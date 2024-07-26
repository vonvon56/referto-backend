from rest_framework import serializers
from .models import Memo

class MemoSerializer(serializers.ModelSerializer):
    paper_id = serializers.IntegerField(source='paper.paper_id', read_only=True)
    content = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Memo
        fields = ['paper_id', 'content']
