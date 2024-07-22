from .views import *
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view

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
)

urlpatterns = [
    path('<int:paper_id>/', ProcessPaperInfo.as_view(), name='process_paper_info'), 
    path('assignment/<int:assignment_id>/', PaperInfoListView.as_view(), name='paperinfo_list')
]