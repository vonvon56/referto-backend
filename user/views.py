from rest_framework.views import APIView
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
import jwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from django.shortcuts import render, get_object_or_404
from referto.settings import SECRET_KEY
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .request_serializers import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt

# 회원가입
class RegisterAPIView(APIView):
    @swagger_auto_schema(
        operation_id="회원가입",
        operation_description="회원가입을 진행합니다.",
        request_body=SignUpRequestSerializer,
        responses={201: UserSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "register successs",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            
            # jwt 토큰 => 쿠키에 저장
            res.set_cookie("access_token", access_token)
            res.set_cookie("refresh_token", refresh_token)
            
            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 유저 정보 확인, 로그인, 로그아웃
class AuthAPIView(APIView):
    # 유저 정보 확인
    @swagger_auto_schema(
        operation_id="사용자 정보 조회",
        operation_description="현재 로그인한 사용자의 정보를 조회합니다.",
        responses={200: UserSerializer, 401: "Unauthorized"},
    )
    def get(self, request):
        try:
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            access = request.COOKIES['access_token']
            payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
            pk = payload.get('user_id')
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            data = {'refresh_token': request.COOKIES.get('refresh_token', None)}
            serializer = TokenRefreshSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                access = serializer.data.get('access_token', None)
                refresh = serializer.data.get('refresh_token', None)
                payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
                pk = payload.get('user_id')
                user = get_object_or_404(User, pk=pk)
                serializer = UserSerializer(instance=user)
                res = Response(serializer.data, status=status.HTTP_200_OK)
                res.set_cookie('access_token', access)
                res.set_cookie('refresh_token', refresh)
                return res
            raise jwt.exceptions.InvalidTokenError

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # 로그인
    @swagger_auto_schema(
        operation_id="로그인",
        operation_description="로그인을 진행합니다.",
        request_body=SignInRequestSerializer,
        responses={200: UserSerializer, 404: "Not Found", 400: "Bad Request"},
    )
    def post(self, request):
    	# 유저 인증
        print(request)
        print(request.data)
        user = authenticate(
            email=request.data.get("email"), password=request.data.get("password")
        )
        # 이미 회원가입 된 유저일 때
        if user is not None:
            serializer = UserSerializer(user)
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "login success",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            # jwt 토큰 => 쿠키에 저장
            res.set_cookie("access_token", access_token)
            res.set_cookie("refresh_token", refresh_token)
            return res
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # 로그아웃
    @swagger_auto_schema(
        operation_id="로그아웃",
        operation_description="로그아웃을 진행합니다.",
        responses={204: "No Content"},
    )
    def delete(self, request):
        # 쿠키에 저장된 토큰 삭제 => 로그아웃 처리
        if not request.user.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "no refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )
        RefreshToken(refresh_token).blacklist()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
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

# 구글 소셜로그인 변수 설정
state = os.environ.get("STATE")
# 로컬의 base url
# BASE_URL = 'http://127.0.0.1:8000/'
# 실제 서버의 base url
BASE_URL = 'https://www.referto.site/'
GOOGLE_CALLBACK_URI = BASE_URL + 'api/user/google/callback/'
# GOOGLE_CALLBACK_URI = "http://127.0.0.1:8000/api/user/google/callback/"
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

# -------------- Access Token Refresh --------------------

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_id="토큰 재발급",
        operation_description="access 토큰을 재발급 받습니다.",
        request_body=TokenRefreshRequestSerializer,
        responses={200: UserSerializer},
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        
        #Get user's refresh_token
        if not refresh_token:
            return Response(
                {"detail": "no refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
        #Check if refresh_token is valid
        #if invalid -- means user has to sign in again.
            RefreshToken(refresh_token).verify()
        except:
            return Response(
                {"detail": "please signin again."}, status=status.HTTP_401_UNAUTHORIZED
            )
            
        #Since refresh_token is valid, create new access_token, embed into a cookie and send it over
        new_access_token = str(RefreshToken(refresh_token).access_token)
        response = Response({"access": new_access_token}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", new_access_token)
        return response

