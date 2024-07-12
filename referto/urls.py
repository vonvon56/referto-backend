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
from django.contrib import admin
from django.urls import path, include
from account.views import SigninView, SignupView
from papers.views import PaperUploadView
from memos.views import MemoDetailView
from assignments.views import AssignmentListView, AssignmentDetailView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from paperinfos.views import ProcessPaperInfo
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# swagger settings
schema_view = get_schema_view(
    openapi.Info(
        title="LIKELION Blog API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourdomain.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('api/account/signup', SignupView.as_view(), name='signup'),
    path('api/account/signin', SigninView.as_view(), name='signin'),

    path('api/assignments/', AssignmentListView.as_view(), name='assignment-list'),
    path('api/assignments/<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),

    path('api/papers/', PaperUploadView.as_view(), name='paper-upload'),

    path('api/papers/<int:pk>/memo', MemoDetailView.as_view(), name='memo'),

    path('api/paperinfo/<int:paper_id>/', ProcessPaperInfo.as_view(), name='process_paper_info'), 

    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/social/', include('allauth.socialaccount.urls')),
    path('api/assignments/', include('assignments.urls'))
]



# import React from 'react';
# import { GoogleLogin } from 'react-google-login';
# import axios from 'axios';

# const App = () => {
#   const responseGoogle = (response) => {
#     axios.post('http://localhost:8000/api/auth/social/google/', {
#       access_token: response.tokenId,  // Google에서 반환된 access token
#     })
#     .then((res) => {
#       console.log(res.data);
#       // 여기서 받은 데이터를 통해 사용자 인증 처리를 할 수 있습니다.
#     })
#     .catch((err) => {
#       console.error(err);
#     });
#   };

#   return (
#     <div>
#       <GoogleLogin
#         clientId="<your-client-id>"  // Google 클라이언트 ID
#         buttonText="Login with Google"
#         onSuccess={responseGoogle}
#         onFailure={responseGoogle}
#         cookiePolicy={'single_host_origin'}
#       />
#     </div>
#   );
# };

# export default App;
