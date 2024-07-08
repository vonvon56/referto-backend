from rest_framework import serializers
from .models import Paper

class PaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = ['paper_id', 'pdf', 'assignment', 'created_at']
        read_only_fields = ['paper_id', 'created_at']
