# -------------- 구글 로그인 --------------------
import os


from django.shortcuts import redirect
import os
from json import JSONDecodeError
from django.http import JsonResponse
import requests
import os
from rest_framework import status
from .models import *
from allauth.socialaccount.models import SocialAccount
from .views import *
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# 구글 소셜로그인 변수 설정
state = os.environ.get("STATE")

# 환경 변수나 설정에 따라 BASE_URL 결정
BASE_URL = settings.BACKEND_URL
GOOGLE_CALLBACK_URI = settings.GOOGLE_CALLBACK_URI

# 구글 로그인
def google_login(request):
    try:
        scope = "https://www.googleapis.com/auth/userinfo.email"
        client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        callback_uri = settings.GOOGLE_CALLBACK_URI
        
        # 디버그 로깅 추가
        logger.info(f"Debug mode: {settings.DEBUG}")
        logger.info(f"Client ID: {client_id}")
        logger.info(f"Callback URI: {callback_uri}")
        
        if not client_id:
            logger.error("Missing Google client ID")
            return JsonResponse({
                "error": "Missing Google client ID",
                "detail": "SOCIAL_AUTH_GOOGLE_CLIENT_ID environment variable is not set"
            }, status=400)
            
        if not callback_uri:
            logger.error("Missing callback URI")
            return JsonResponse({
                "error": "Missing callback URI",
                "detail": "GOOGLE_CALLBACK_URI is not configured in settings"
            }, status=400)
        
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            "response_type=code&"
            f"redirect_uri={callback_uri}&"
            f"scope={scope}"
        )
        
        logger.info(f"Redirecting to Google auth URL: {auth_url}")
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"Error in google_login: {str(e)}")
        return JsonResponse({
            "error": "Failed to initialize Google login",
            "detail": str(e)
        }, status=500)


import json
import os
import requests
from django.http import JsonResponse
from requests.exceptions import JSONDecodeError
from django.http import JsonResponse
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

@csrf_exempt
def google_callback(request):    
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')
    
    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    # 1. Token Request - state 파라미터 제거
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token",
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_CALLBACK_URI
        }
    )
    
    try:
        token_req_json = token_req.json()
        error = token_req_json.get("error")
        if error is not None:
            return JsonResponse({"error": error}, status=400)
    except JSONDecodeError as e:
        return JsonResponse({"error": "Failed to parse JSON from token response", "details": str(e)}, status=400)

    # 1-3. 성공 시 access_token 가져오기
    access_token = token_req_json.get('access_token')

    # 2. 가져온 access_token으로 이메일값을 구글에 요청
    email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code

    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=400)

    try:
        email_req_json = email_req.json()
        email = email_req_json.get('email')
    except JSONDecodeError as e:
        return JsonResponse({"error": "Failed to parse JSON from email response", "details": str(e)}, status=400)

    # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인

    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색, 없다면 Exception 발생
        user = User.objects.get(email=email)
        token = RefreshToken.for_user(user)  # 자체 jwt 발급
        refresh_token = str(token)
        access_token = str(token.access_token)

        # 유저가 활성화된 경우
        if user.is_active:
            # 프론트엔드 URL 설정
            redirect_url = f"{settings.FRONTEND_URL}/google/callback?access_token={access_token}&refresh_token={refresh_token}"
            return HttpResponseRedirect(redirect_url)
        else:
            # 활성화되지 않은 회원, Exception 발생
            raise Exception('Signup Required')

    except ObjectDoesNotExist:
        # 유저가 존재하지 않는 경우 - 회원가입 프로세스 호출
        data = {'email': email, 'username': email.split('@')[0], 'password': 'auto_generated_password'}  # 간단한 초기 데이터
        serializer = UserSerializer(data=data)
        
        if serializer.is_valid():
            user = serializer.save()
            token = RefreshToken.for_user(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            
            # 응답 반환
            return JsonResponse({
                'user': serializer.data,
                'message': 'User registered successfully',
                'token': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # 활성화되지 않은 유저 혹은 다른 에러를 처리
        try:
            # FK로 연결된 socialaccount 테이블에서 해당 이메일의 유저 확인
            social_user = SocialAccount.objects.get(user=user)
            
            # Google 계정이 아닌 경우 에러 반환
            if social_user.provider != 'google':
                return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Google 로그인으로 연결
            data = {'access_token': access_token, 'code': code}
            accept = requests.post(f"{BASE_URL}api/user/google/login/finish/", data=data)
            
            # 최종 응답 반환
            return JsonResponse({'msg': 'Login successful'}, status=accept.status_code)
        
        except ObjectDoesNotExist:
            # 유저가 존재하지 않는 경우 - 회원가입 프로세스 호출
            data = {'email': email, 'username': email.split('@')[0], 'password': 'auto_generated_password'}  # 간단한 초기 데이터
            serializer = UserSerializer(data=data)
            
            if serializer.is_valid():
                user = serializer.save()
                token = RefreshToken.for_user(user)
                refresh_token = str(token)
                access_token = str(token.access_token)
                
                # 응답 반환
                return JsonResponse({
                    'user': serializer.data,
                    'message': 'User registered successfully',
                    'token': {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            # 기타 예외 처리
            return JsonResponse({'err_msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
import json
# from allauth.socialaccount.views import SocialLoginView
import json
from django.http import JsonResponse

    
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_CALLBACK_URI
    client_class = OAuth2Client

