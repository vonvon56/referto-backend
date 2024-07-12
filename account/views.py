# 만들어둔 모델, serializer (User, UserProfile) import
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer,UserProfileSerializer,EmailUsernameSerializer

# APIView, JWT token, 비밀번호 해싱을 위해 필요한 class import
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
    res.set_cookie("refresh_token", value=str(token))
    res.set_cookie("access_token", value=str(token.access_token))
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
