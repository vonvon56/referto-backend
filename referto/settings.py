"""
Django settings for referto project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os, environ
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    DEBUG=(bool, True)
)


environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)
# Kakao API configuration
KAKAO_REST_API_KEY = os.environ.get("KAKAO_SECRET_KEY")
KAKAO_REDIRECT_URI = os.environ.get("KAKAO_REDIRECT_URI")

# Kakao API URLs (fixed and public information)
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
import pymysql
pymysql.install_as_MySQLdb()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =env('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['referto-backend', '127.0.0.1:8000', '127.0.0.1', 'referto-backend.fly.dev', 'https://referto-backend.fly.dev','localhost', '*']

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:3000',
    "http://localhost:3000",
    'https://referto-backend.fly.dev',
    "https://referto.site",
    'http://43.201.56.176:8000',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)
# Application definition
CSRF_TRUSTED_ORIGINS = [
   'http://127.0.0.1:3000', 
   'http://localhost:3000',
   'https://referto-backend.fly.dev',
   'http://43.201.56.176:8000',
]
CORS_ORIGIN_ALLOW_ALL = False 
# SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Ensure that cookies are only sent via HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CORS_ORIGIN_WHITELIST = ['http://43.201.56.176:8000', 'http://127.0.0.1:3000' ,'http://localhost:3000', 'https://referto-backend.fly.dev','http://referto-backend.fly.dev']
INSTALLED_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.naver',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'user',
    'assignments',
    'papers',
    'paperinfos',
    'memos',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'drf_yasg',
    'corsheaders',
    'whitenoise.runserver_nostatic', 
]

# SECURE_SSL_REDIRECT = True  # HTTP 요청을 HTTPS로 리다이렉트

SITE_ID = 1
AUTH_USER_MODEL = 'user.User'

REST_USE_JWT = True

ACCOUNT_USER_MODEL_USERNAME_FIELD = None # username 필드 사용 x
ACCOUNT_EMAIL_REQUIRED = True            # email 필드 사용 o
ACCOUNT_USERNAME_REQUIRED = False        # username 필드 사용 x
ACCOUNT_AUTHENTICATION_METHOD = 'email'

REST_USE_JWT = True

ACCOUNT_USER_MODEL_USERNAME_FIELD = None # username 필드 사용 x
ACCOUNT_EMAIL_REQUIRED = True            # email 필드 사용 o
ACCOUNT_USERNAME_REQUIRED = False        # username 필드 사용 x
ACCOUNT_AUTHENTICATION_METHOD = 'email'

# jwt 토큰은 simplejwt의 JWTAuthentication으로 인증한다.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ), 
    # 'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated', # 인증된 사용자만 접근
        # 'rest_framework.permissions.IsAdminUser', # 관리자만 접근
        # 'rest_framework.permissions.AllowAny', # 누구나 접근
    # )
        # 'rest_framework.permissions.AllowAny', # 누구나 접근
    # )
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'allauth.account.middleware.AccountMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
]

AUTHENTICATION_BACKENDS = (
    # 'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'PROVIDER': 'allauth.socialaccount.providers.google.GoogleProvider',
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID"),
            'secret': os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET"),
            'key': ''
        },
        'METHOD': 'oauth2',
    }, 
    'naver': {
        'APP': {
            'client_id': os.environ.get('SOCIAL_AUTH_NAVER_CLIENT_ID'),
            'secret': os.environ.get('SOCIAL_AUTH_NAVER_SECRET'),
            'key': ''
        }
    } 
}

    


AUTHENTICATION_BACKENDS = (
    # 'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID"),
            'secret': os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET"),
            'key': ''
        }
    }
}

ROOT_URLCONF = 'referto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'referto.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # engine: mysql
        'NAME' : 'referto_db', # DB Name
        'USER' : 'admin', # DB User
        'PASSWORD' : 'refertodb', # Password
        'HOST': 'referto-db.cfsecok4g34k.ap-northeast-2.rds.amazonaws.com', # 생성한 데이터베이스 엔드포인트
        'PORT': '3306', # 데이터베이스 포트
        'OPTIONS':{
            'init_command' : "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 추가적인 JWT 설정, 다 쓸 필요는 없지만 혹시 몰라서 다 넣었다.
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # <-- Updated!
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # <-- Updated!
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'