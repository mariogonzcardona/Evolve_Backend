# prod.py
from .base import *

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Base de datos (sin cambios)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
    }
}

# ===== AWS S3 - PROD =====
AWS_STORAGE_BUCKET_NAME = "evolve-backend-prod"
AWS_S3_REGION_NAME = "us-east-1"  # ajusta si usas otra región
AWS_QUERYSTRING_AUTH = False

# Archivos estáticos en S3
STATICFILES_STORAGE = "config.settings.storage_backends.StaticStorage"
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/"

# Archivos subidos (media) en S3
DEFAULT_FILE_STORAGE = "config.settings.storage_backends.MediaStorage"
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/"

# Seguridad extra
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
