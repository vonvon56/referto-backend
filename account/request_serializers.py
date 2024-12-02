from rest_framework import serializers

class SignUpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class SignInRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()