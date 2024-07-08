from rest_framework import serializers
from .models import Paper

# class PaperCreateSerializer(serializers.ModelSerializer):
class PaperCreateSerializer(serializers.Serializer):
    pdf = serializers.FileField()
    assignment = serializers.IntegerField()