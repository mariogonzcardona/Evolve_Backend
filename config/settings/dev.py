# dev.py
from .base import *
from decouple import config, Csv

DEBUG = False  # en AWS dev normalmente HTTPS real; si quieres True, súbelo solo para debug puntual.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# CORS / CSRF
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv(), default=[])
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv(), default=[])

# DB (mismo patrón que base/local/prod)
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

# ===== AWS S3 - DEV =====
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')

STORAGES = {
    "default": {  # Media
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "location": "media",
        },
    },
    "staticfiles": {  # Static
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "location": "static",
        },
    },
}

STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/"
MEDIA_URL  = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/"

# Seguridad razonable en dev (HTTPS con Caddy/LE):
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
