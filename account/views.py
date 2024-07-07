from django.contrib.auth.models import User
from django.contrib import auth
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from account.request_serializers import SignInRequestSerializer, SignUpRequestSerializer

from .serializers import (
    UserSerializer,
    UserProfileSerializer,
)
from .models import UserProfile


class SignUpView(APIView):
    @swagger_auto_schema(
        operation_id="회원가입",
        operation_description="회원가입을 진행합니다.",
        request_body=SignUpRequestSerializer,
        responses={201: UserProfileSerializer, 400: "Bad Request"},
    )
    def post(self, request):

        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            user.set_password(user.password)
            user.save()

        email = request.data.get("email")

        user_profile = UserProfile.objects.create(
            user=user, email=email
        )
        user_profile_serializer = UserProfileSerializer(instance=user_profile)
        return Response(user_profile_serializer.data, status=status.HTTP_201_CREATED)


class SignInView(APIView):
    @swagger_auto_schema(
        operation_id="로그인",
        operation_description="로그인을 진행합니다.",
        request_body=SignInRequestSerializer,
        responses={200: UserSerializer, 404: "Not Found", 400: "Bad Request"},
    )
    def post(self, request):
        # query_params 에서 username, password를 가져온다.
        email = request.data.get("email")
        password = request.data.get("password")
        if email is None or password is None:
            return Response(
                {"message": "missing fields ['email', 'password'] in query_params"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                return Response(
                    {"message": "Password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_profile = UserProfile.objects.get(user=user)
            user_profile_serializer = UserProfileSerializer(instance=user_profile)
            return Response(user_profile_serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
