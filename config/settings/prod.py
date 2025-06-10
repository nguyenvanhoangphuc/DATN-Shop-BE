from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("PROD_DB_NAME", "prod_db"),
        "USER": os.getenv("PROD_DB_USER", "root"),
        "PASSWORD": os.getenv("PROD_DB_PASSWORD", "abc23102002"),
        "HOST": os.getenv("PROD_DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("PROD_DB_PORT", "3306"),
    }
}

# Cấu hình bảo mật cho production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
