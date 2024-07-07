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
from account.views import SignInView, SignUpView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('api/users/', SignUpView.as_view(), name='create-user'),
    # path('api/users/<str:user_id>/', UserDeleteView.as_view(), name='delete-user'),

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
