import os
from decouple import config
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
if config('ENVIRONMENT') == 'local':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.local'

application = get_asgi_application()