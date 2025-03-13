"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
# Lấy biến môi trường DJANGO_ENV (mặc định là "dev")
env = os.getenv("DJANGO_ENV", "prod")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{env}")

application = get_wsgi_application()
