"""
URL configuration for referto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from user.views import *
from user.kakaologin_views import *
schema_view = get_schema_view(
    openapi.Info(
        title="Referto API",
        default_version='v1',
        description="API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    # url='https://referto-backend.fly.dev',  # URL을 HTTPS로 설정합니다.
)

# 간단한 테스트 뷰 추가
def home(request):
    return HttpResponse("Hello, Django Server is running!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', home),  # 루트 경로
    # user
    #path('api/user/', include('allauth.urls')),
    path('api/user/', include('user.urls')),
    # assignments
    path('api/assignments/', include('assignments.urls')),
    # papers
    path('api/papers/', include('papers.urls')),
    # paperinfos
    path('api/paperinfo/', include('paperinfos.urls')),
    # memos
    path('api/papers/', include('memos.urls')),
    path('auth', kakao_callback, name='kakao_callback'),
    # notes
    path('api/notes/', include('notes.urls')),
]
