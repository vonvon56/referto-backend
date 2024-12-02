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
# 구글 소셜로그인 변수 설정
state = os.environ.get("STATE")

# BASE_URL = 'http://127.0.0.1:8000/'
BASE_URL = 'https://www.referto.site/'

# GOOGLE_CALLBACK_URI = "http://127.0.0.1:8000/api/user/google/callback/"
GOOGLE_CALLBACK_URI = 'https://www.referto.site/api/user/google/callback/'
# 구글 로그인
def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    print(client_id)
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


import json
import os
import requests
from django.http import JsonResponse
from requests.exceptions import JSONDecodeError
from django.http import JsonResponse
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

@csrf_exempt
def google_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')
    state = request.GET.get('state')
    print("code: ", code)
    print("state: ", state)

    # 1. 받은 코드로 구글에 access token 요청
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}"
    )
    print('token_req:', token_req)
    # JSON 변환 시도 및 오류 처리
    try:
        token_req_json = token_req.json()
        print('token_req_json: ', token_req_json)
        error = token_req_json.get("error")
        if error is not None:
            return JsonResponse({"error": error}, status=400)
    except JSONDecodeError as e:
        # JSON 파싱 실패 시 에러 메시지 반환
        return JsonResponse({"error": "Failed to parse JSON from token response", "details": str(e)}, status=400)

    # 1-3. 성공 시 access_token 가져오기
    access_token = token_req_json.get('access_token')

    # 2. 가져온 access_token으로 이메일값을 구글에 요청
    email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code

    # 2-1. 에러 발생 시 400 에러 반환
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=400)

    # 이메일 요청 JSON 변환 시도 및 오류 처리
    try:
        email_req_json = email_req.json()
        email = email_req_json.get('email')
        print('email: ', email)
        print('')
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
            return JsonResponse({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
        else:
            # 활성화되지 않은 회원, Exception 발생
            raise Exception('Signup Required')

    except ObjectDoesNotExist:
        # 유저가 존재하지 않는 경우 - 회원가입 프로세스 호출
        data = {'email': email, 'username': email.split('@')[0], 'password': 'auto_generated_password'}  # 간단한 초기 데이터
        print('signupdata: ', data)
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
    callback_url = 'http://127.0.0.1:8000/api/user/google/callback/'
    client_class = OAuth2Client