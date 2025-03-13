from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DEV_DB_NAME", "dev_db"),
        "USER": os.getenv("DEV_DB_USER", "root"),
        "PASSWORD": os.getenv("DEV_DB_PASSWORD", "abc23102002"),
        "HOST": os.getenv("DEV_DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DEV_DB_PORT", "3306"),
    }
}
