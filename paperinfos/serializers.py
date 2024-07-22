from rest_framework import serializers
from .models import PaperInfo

class PaperInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperInfo
        fields = ['paperInfo_id', 'MLA', 'APA', 'Chicago', 'Vancouver', 'paper']
        read_only_fields = ['paper']
