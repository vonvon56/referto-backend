from rest_framework import serializers
from .models import PaperInfo

class PaperInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperInfo
        fields = ['paperInfo_id', 'mla_reference', 'apa_reference', 'chicago_reference', 'vancouver_reference', 'paper']
        read_only_fields = ['paper']
