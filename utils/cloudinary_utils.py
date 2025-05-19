import cloudinary
import cloudinary.uploader
from django.conf import settings

# Khởi tạo Cloudinary config từ Django settings
cloudinary.config(
    cloud_name=settings.CLOUDINARY['cloud_name'],
    api_key=settings.CLOUDINARY['api_key'],
    api_secret=settings.CLOUDINARY['api_secret'],
    secure=True
)

def upload_image(file):
    """
    Upload file ảnh lên Cloudinary và trả về URL ảnh.
    file: file object từ Django (request.FILES['xxx'])
    """
    try:
        result = cloudinary.uploader.upload(file)
        return result.get('secure_url')
    except Exception as e:
        # Có thể log lỗi ở đây
        raise e
