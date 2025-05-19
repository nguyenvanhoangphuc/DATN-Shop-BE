from rest_framework import serializers
from users.serializers import UserSerializer
from app.models import StatusEnum

class LoginSerializer(serializers.Serializer):
    usernameOrEmail = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

class LoginResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255)

class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=255)
    status = serializers.BooleanField(default=True)

class ValidateSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=255)

class ValidateResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    status = serializers.BooleanField(default=True)

class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255)
    gender = serializers.BooleanField(allow_null=True)
    phone = serializers.CharField(max_length=15, allow_null=True)
    address = serializers.CharField(max_length=255, allow_null=True)
    birthday = serializers.DateField(allow_null=True)
    avatar = serializers.ImageField(allow_null= True)
    status_enum = serializers.IntegerField(default=StatusEnum.ACTIVE.value)

class RegisterResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()