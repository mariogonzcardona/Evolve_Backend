import os
from django.core.wsgi import get_wsgi_application
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
if config('ENVIRONMENT') == 'local':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.local'

application = get_wsgi_application()
