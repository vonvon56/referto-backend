import requests
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.db import IntegrityError

User = get_user_model()

def kakao_login(request):
    kakao_auth_url = (
        f"{settings.KAKAO_AUTH_URL}?response_type=code"
        f"&client_id={settings.KAKAO_REST_API_KEY}"
        f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
    )
    return HttpResponseRedirect(kakao_auth_url)

def kakao_callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "Authorization code not provided."}, status=400)

    # Request access token
    token_data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_REST_API_KEY,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "code": code,
    }
    token_response = requests.post(settings.KAKAO_TOKEN_URL, data=token_data)
    token_json = token_response.json()

    if "access_token" not in token_json:
        return JsonResponse({"error": "Failed to get access token.", "details": token_json}, status=400)

    access_token = token_json["access_token"]

    # Request user information
    user_info_response = requests.get(
        settings.KAKAO_USER_INFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info_json = user_info_response.json()

    if user_info_response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch user info.", "details": user_info_json}, status=400)

    kakao_id = user_info_json.get("id")
    nickname = user_info_json.get("properties", {}).get("nickname", "Unknown")
    email = user_info_json.get("kakao_account", {}).get("email")

    if not email:
        email = f"kakao_{kakao_id}@kakao.com"

    if not kakao_id:
        return JsonResponse({"error": "Failed to fetch Kakao ID."}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        try:
            user = User.objects.create_user(
                email=email,
                nickname=nickname,  # Adjust this field name to match your model
                password=None,  # Password can be left blank for social login
            )
        except IntegrityError:
            return JsonResponse({"error": "Failed to create user. Please try again later."}, status=500)

    # Add backend attribute to user
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)

    return JsonResponse({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": getattr(user, "nickname", "Unknown"),  # Adjust field name here as well
        }
    })
