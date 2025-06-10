# upload/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authentication.permissions import IsAuthenticatedPermission
from .serializers import UploadImageSerializer
import cloudinary.uploader
from rest_framework.decorators import authentication_classes
from rest_framework.parsers import MultiPartParser, FormParser
# load settings
from django.conf import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY['cloud_name'],
    api_key=settings.CLOUDINARY['api_key'],
    api_secret=settings.CLOUDINARY['api_secret']
)

# @authentication_classes([])
# class UploadImageView(APIView):
#     permission_classes = []

#     def post(self, request):
#         serializer = UploadImageSerializer(data=request.data)
#         if serializer.is_valid():
#             image = serializer.validated_data['image']
#             result = cloudinary.uploader.upload(image)
#             return Response({"image_url": result.get("secure_url")}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadImageView(APIView):
    authentication_classes = []  # nếu bạn muốn bỏ xác thực
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]  # 👈 quan trọng!

    def post(self, request):
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            result = cloudinary.uploader.upload(image)
            return Response({"image_url": result.get("secure_url")}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

