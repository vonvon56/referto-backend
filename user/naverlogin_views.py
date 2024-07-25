from django.shortcuts import redirect
import os
from json import JSONDecodeError
from django.http import JsonResponse
import requests
from rest_framework import status
from .models import *
from allauth.socialaccount.models import SocialAccount

# 네이버 소셜로그인 변수 설정
state = os.environ.get("STATE")
BASE_URL = 'http://127.0.0.1:8000/'
NAVER_CALLBACK_URI = BASE_URL + 'api/user/naver/callback/'

# 네이버 로그인
def naver_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    redirect_uri = NAVER_CALLBACK_URI
    state = os.environ.get("STATE")
    return redirect(f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&state={state}")

def naver_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_NAVER_SECRET")
    code = request.GET.get('code')
    state = request.GET.get('state')

    # 1. 받은 코드로 네이버에 access token 요청
    token_req = requests.post(f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&state={state}")
  
    # 1-1. json으로 변환 & 에러 부분 파싱
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    # 1-2. 에러 발생 시 종료
    if error is not None:
        raise JSONDecodeError(error)

    # 1-3. 성공 시 access_token 가져오기
    access_token = token_req_json.get('access_token')

    # 2. 가져온 access_token으로 사용자 정보 요청
    user_info_req = requests.get("https://openapi.naver.com/v1/nid/me", headers={"Authorization": f"Bearer {access_token}"})
    user_info_req_status = user_info_req.status_code

    # 2-1. 에러 발생 시 400 에러 반환
    if user_info_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get user info'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 2-2. 성공 시 사용자 정보 가져오기
    user_info_req_json = user_info_req.json()
    email = user_info_req_json.get('response').get('email')
    print('email: ', email)
    # 3. 전달받은 이메일로 회원가입/로그인
    try:
        user = User.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)

        if social_user.provider != 'naver':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        data = {'access_token': access_token, 'code': code}
        print('data: ', access_token, code)
        accept = requests.post("http://127.0.0.1:8000/api/user/naver/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except User.DoesNotExist:
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/user/naver/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except SocialAccount.DoesNotExist:
        return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.naver import views as naver_view

class NaverLogin(SocialLoginView):
    adapter_class = naver_view.NaverOAuth2Adapter
    callback_url = 'http://127.0.0.1:8000/api/user/naver/callback/'
    client_class = OAuth2Client
