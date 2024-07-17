# 만들어둔 모델, serializer (User, UserProfile) import
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer,UserProfileSerializer, EmailUsernameSerializer


# APIView, JWT token, 비밀번호 해싱을 위해 필요한 class import
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from account.request_serializers import (
    SignInRequestSerializer,
    SignUpRequestSerializer,
)


def generate_token_in_serialized_data(user, user_profile):
    token = RefreshToken.for_user(user)
    refresh_token, access_token = str(token), str(token.access_token)
    serialized_data = UserProfileSerializer(user_profile).data
    serialized_data["token"] = {"access": access_token, "refresh": refresh_token}
    return serialized_data

def set_token_on_response_cookie(user, status_code) -> Response:
    token = RefreshToken.for_user(user)
    user_profile = UserProfile.objects.get(user=user)
    serialized_data = UserProfileSerializer(user_profile).data
    res = Response(serialized_data, status=status_code)
    res.set_cookie("refresh_token", value=str(token), httponly=False)
    res.set_cookie("access_token", value=str(token.access_token), httponly=False)
    return res

#### view
class SignupView(APIView):
    @swagger_auto_schema(
        operation_id="회원가입",
        operation_description="회원가입을 진행합니다.",
        request_body=SignUpRequestSerializer,
        responses={201: UserProfileSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        data = request.data.copy()
        email = data.get('email')

        # email을 username으로 사용
        data['username'] = email

        user_serializer = UserSerializer(data=data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            user.set_password(user.password)
            user.save()
                
        user_profile = UserProfile.objects.create(
            user=user,
            email=email
        )

        return set_token_on_response_cookie(user, status_code=status.HTTP_201_CREATED)
        #     serialized_data = generate_token_in_serialized_data(user, user_profile )
        #     # 생성된 token, UserProfile 정보를 Response에 담아서 반환
        #     return Response(serialized_data, status=status.HTTP_201_CREATED)
        # return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SigninView(APIView):
    @swagger_auto_schema(
        operation_id="로그인",
        operation_description="로그인을 진행합니다.",
        request_body=SignInRequestSerializer,
        responses={200: UserSerializer, 404: "Not Found", 400: "Bad Request"},
    )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                return Response(
                    {"message": "Password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return set_token_on_response_cookie(user, status_code=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class SignOutView(APIView):
    @swagger_auto_schema(
        operation_id="로그아웃",
        operation_description="로그아웃을 진행합니다.",
        responses={204: "No Content"},
    )
    def post(self, request):

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
    

class UserInfoView(APIView):

    @swagger_auto_schema(
        operation_id="사용자 정보 조회",
        operation_description="현재 로그인한 사용자의 정보를 조회합니다.",
        responses={200: EmailUsernameSerializer, 401: "Unauthorized"},
    )

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "로그인 후 다시 시도해주세요"}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        serializer = EmailUsernameSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

# views.py
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import UserProfile
from django.http import HttpResponse
from rest_framework.decorators import api_view
import secrets
import logging

# account/views.py
logger = logging.getLogger(__name__)

def generate_state():
    return secrets.token_urlsafe(16)

@swagger_auto_schema(method='get', operation_description="네이버 로그인 시작")
@api_view(['GET'])
def naver_login(request):
    client_id = settings.NAVER_CLIENT_ID
    redirect_uri = settings.NAVER_REDIRECT_URI
    state = generate_state()
    request.session['naver_auth_state'] = state
    logger.debug(f'Generated state: {state}')
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&state={state}"
    )

@swagger_auto_schema(method='get', operation_description="네이버 로그인 콜백")
@api_view(['GET'])
def naver_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    session_state = request.session.pop('naver_auth_state', None)

    logger.debug(f'Received state: {state}, Session state: {session_state}')

    if state != session_state:
        return HttpResponse('State mismatch error.', status=400)

    client_id = settings.NAVER_CLIENT_ID
    client_secret = settings.NAVER_CLIENT_SECRET
    redirect_uri = settings.NAVER_REDIRECT_URI

    token_request = requests.post(
        'https://nid.naver.com/oauth2.0/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'state': state,
        }
    )
    token_response_json = token_request.json()
    access_token = token_response_json['access_token']

    profile_request = requests.get(
        'https://openapi.naver.com/v1/nid/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    profile_response_json = profile_request.json()
    logger.debug(f'Profile response: {profile_response_json}')

    response = profile_response_json['response']
    naver_id = response.get('id')
    # nickname = response.get('nickname')
    # profile_image = response.get('profile_image')

    if not naver_id:
        return HttpResponse('Naver ID not provided.', status=400)

    # 네이버 아이디를 이메일 형식으로 변환 (예: naver_id@naver.com)
    email = f"{naver_id}@naver.com"

    # 사용자 정보를 User 및 UserProfile에 저장하거나 업데이트
    user, created = User.objects.get_or_create(username=email)
    if created:
        user.set_unusable_password()
        user.save()
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile.email = email
    # user_profile.nickname = nickname
    # user_profile.profile_image = profile_image
    user_profile.save()

    login(request, user)
    return redirect(settings.LOGIN_REDIRECT_URL)