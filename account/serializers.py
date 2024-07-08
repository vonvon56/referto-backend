### 🔻 이 부분 추가 🔻 ###
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import UserProfile


class EmailUsernameSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "password", "email", "username"]


class UserProfileSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = "__all__"