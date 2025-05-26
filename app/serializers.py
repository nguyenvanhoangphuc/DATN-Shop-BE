# upload/serializers.py
from rest_framework import serializers

class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField()


class ResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=255)
    status = serializers.BooleanField(default=True)