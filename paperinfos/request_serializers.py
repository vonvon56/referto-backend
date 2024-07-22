from rest_framework import serializers

class PaperInfoChangeSerializer(serializers.Serializer):
    reference_type = serializers.CharField()
    new_reference = serializers.CharField()