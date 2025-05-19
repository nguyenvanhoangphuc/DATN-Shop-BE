from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from authentication.serializers import *
from users.models import *
from users.serializers import *
from . import utils
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import authentication_classes, permission_classes


# Create LoginView
@authentication_classes([])
class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: LoginResponseSerializer}
    )
    def post(self, request):
        data = request.data.copy()
        usernameOrEmail = data.get("usernameOrEmail", "")
        password = data.get("password", "")
        # Check if username or email is empty
        if usernameOrEmail == "":
            return Response(
                {"detail": "Username or email is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Check is username or email
        isEmail = "@" in usernameOrEmail
        # Check if password is empty
        if password == "":
            return Response(
                {"detail": "Password is empty"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Check if username or email is existed
        if isEmail:
            if not User.objects.filter(email=usernameOrEmail).exists():
                return Response(
                    {"detail": "Email is not existed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            if not User.objects.filter(username=usernameOrEmail).exists():
                return Response(
                    {"detail": "Username is not existed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Get user
        user = (
            User.objects.get(email=usernameOrEmail)
            if isEmail
            else User.objects.get(username=usernameOrEmail)
        )
        # Check if password is correct
        if not utils.check_password(user, password):
            return Response(
                {"detail": "Password is incorrect"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create refresh token
        refresh_token, access_token = utils.generateTokensUser(user)
        # Update refresh token
        utils.updateRefreshToken(user, refresh_token)
        # Return user
        user = UserSerializer(user)
        # Create response
        response = {'user': user.data, 'refresh_token': refresh_token, 'access_token': access_token}
        return Response(response, status=status.HTTP_200_OK)


# Create RegisterView
@authentication_classes([])
class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: RegisterResponseSerializer}
    )
    def post(self, request):
        # Get data from request
        data = request.data.copy()
        # Get username, email, password from data
        username = data.get("username", "")
        email = data.get("email", "")
        password = data.get("password", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        # Check if username is empty
        if username == "":
            return Response(
                {"detail": "Username is empty"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Check if email is empty
        if email == "":
            return Response(
                {"detail": "Email is empty"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Check if password is empty
        if password == "":
            return Response(
                {"detail": "Password is empty"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Check if first_name is empty
        if first_name == "":
            return Response(
                {"detail": "Name is empty"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Check if last_name is empty
        if last_name == "":
            return Response(
                {"detail": "Last name is empty"}, status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if username is existed
        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "Username is existed"}, status=status.HTTP_400_BAD_REQUEST
            )
        data["password_hash"] = utils.hash_password(password)

        # Create refresh token
        refresh_token, access_token = utils.generateTokens(data)
        data["refresh_token"] = refresh_token
        # Create user
        user = UserSerializer(data=data)
        if user.is_valid():
            user.save()
        else:
            return Response(
                {"detail": "User is invalid"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Create response
        response = {
            "user": user.data,
            "refresh_token": refresh_token,
            "access_token": access_token,
        }
        return Response(response, status=status.HTTP_201_CREATED)

authentication_classes = []
class Logout(GenericAPIView):
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        request_body=LogoutSerializer,
        responses={200: LogoutResponseSerializer}
    )
    def post(self, request):
        data = request.data.copy()
        refresh_token = data.get("refresh_token", "")
        if refresh_token == "":
            return Response(
                {"detail": "Refresh token is empty"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            payload = jwt.decode(
                refresh_token, settings.JWT_SECRET_KEY, algorithms="HS256"
            )
            user = User.objects.get(username=payload["username"])
            user.refresh_token = ""
            user.save()
        except jwt.DecodeError as identifier:
            return Response(
                {"detail": "Your token is invalid, login"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {"detail": "Your token is expired, login"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User is not existed"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"detail": "Logout successfully"}, status=status.HTTP_200_OK)


class Validate(GenericAPIView):
    serializer_class = ValidateSerializer

    @swagger_auto_schema(
        request_body=ValidateSerializer,
        responses={200: ValidateResponseSerializer}
    )
    def post(self, request):
        data = request.data.copy()
        access_token = data.get("access_token", "")
        if access_token == "":
            return Response(
                {"detail": "Access token is empty"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            payload = jwt.decode(
                access_token, settings.JWT_SECRET_KEY, algorithms="HS256"
            )
            user = User.objects.get(username=payload["username"])
            user = UserSerializer(user)
        except jwt.DecodeError as identifier:
            return Response(
                {"detail": "Your token is invalid, login"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {"detail": "Your token is expired, login"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User is not existed"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"user": user.data}, status=status.HTTP_200_OK)

authentication_classes = []
class RefreshToken(GenericAPIView):
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        request_body=LogoutSerializer,
        responses={200: LogoutResponseSerializer}
    )
    def post(self, request):
        data = request.data.copy()
        refresh_token = data.get("refresh_token", "")
        if refresh_token == "":
            return Response(
                {"detail": "Refresh token is empty"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            payload = jwt.decode(
                refresh_token, settings.JWT_SECRET_KEY, algorithms="HS256"
            )
            user = User.objects.get(username=payload["username"])
            if user.refresh_token != refresh_token:
                return Response(
                    {"detail": "Refresh token is invalid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            refresh_token, access_token = utils.generateTokensUser(user)
            utils.updateRefreshToken(user, refresh_token)
        except jwt.DecodeError as identifier:
            return Response(
                {"detail": "Your token is invalid, login"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {"detail": "Your token is expired, login"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User is not existed"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"refresh_token": refresh_token, "access_token": access_token},
            status=status.HTTP_200_OK,
        )
