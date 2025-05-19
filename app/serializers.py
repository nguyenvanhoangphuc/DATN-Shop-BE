# upload/serializers.py
from rest_framework import serializers

class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField()
