from .views import *
from .kakaologin_views import *
from .naverlogin_views import *
from .googlelogin_views import google_login, google_callback, GoogleLogin
from django.urls import path, include
#from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterAPIView.as_view()), # post - 회원가입
    path("auth/", AuthAPIView.as_view()), # post - 로그인, delete - 로그아웃, get - 유저정보
    path("auth/refresh/", TokenRefreshView.as_view()), # jwt 토큰 재발급

    # 구글 소셜로그인
    path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    path('google/login/finish/', GoogleLogin.as_view(), name='google_login_todjango'),

     # 네이버 소셜로그인
    # path('naver/login/', naver_login, name='naver_login'),
    # path('naver/callback/', naver_callback, name='naver_callback'),
    # path('naver/login/finish/', NaverLogin.as_view(), name='naver_login_todjango'),

    # 카카오 소셜로그인
    # path('kakao/login/', kakao_login, name='kakao_login'),
    # path('kakao/callback/', kakao_callback, name='kakao_callback'),
]
