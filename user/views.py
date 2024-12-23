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
            # Try to get token from Authorization header first
            auth_header = request.headers.get('Authorization', '')
            print(f"[Auth] Headers: {dict(request.headers)}")
            print(f"[Auth] Authorization header: {auth_header}")
            
            access = None
            if auth_header and auth_header.startswith('Bearer '):
                access = auth_header.split(' ')[1]
                print(f"[Auth] Token from Authorization header: {access}")
            
            # If no token in header, try cookies
            if not access:
                access = request.COOKIES.get('access_token')
                print(f"[Auth] Token from cookies: {access}")
                print(f"[Auth] All cookies: {request.COOKIES}")

            if not access:
                return Response({'error': 'No access token provided'}, status=status.HTTP_401_UNAUTHORIZED)

            print(f"[Auth] Final token being used: {access}")
            
            try:
                payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
                pk = payload.get('user_id')
                if not pk:
                    return Response({'error': 'Invalid token: no user_id'}, status=status.HTTP_401_UNAUTHORIZED)
                    
                user = get_object_or_404(User, pk=pk)
                serializer = UserSerializer(instance=user)
                return Response(serializer.data, status=status.HTTP_200_OK)
                
            except jwt.InvalidTokenError:
                return Response({'error': 'Invalid token format'}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.ExpiredSignatureError:
                return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print(f"[Auth] Error in get: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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


