from rest_framework import serializers
from .models import Assignment

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['assignment_id', 'name', 'user_id', 'reference_type', 'number']

class AssignmentModifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['assignment_id']