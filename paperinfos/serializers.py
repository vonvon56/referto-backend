from rest_framework import serializers
from .models import PaperInfo

class PaperInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperInfo
        fields = ['paperInfo_id', 'reference', 'paper_id', 'created_at']
        read_only_fields = ['paper_id', 'created_at']
