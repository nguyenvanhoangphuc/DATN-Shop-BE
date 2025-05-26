from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'role')

class UserSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'phone', 'address', 'region', 'company', 'address_billing', 'zip_code', 'note', 'image_url', 'role', 'status_enum')
        read_only_fields = ('id', 'created_at', 'role')

class UserUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'phone', 'address', 'region', 'company', 'address_billing', 'zip_code', 'note', 'image')
        read_only_fields = ('id', 'created_at', 'role')
    
class IdsUserSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

