import os
from decouple import config
from django.core.wsgi import get_wsgi_application

# Lee el entorno desde .env y selecciona settings
env = config('ENVIRONMENT', default='local').lower()

if env == 'prod' or env == 'production':
    settings_module = 'config.settings.prod'
else:
    settings_module = 'config.settings.local'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
