import os
from decouple import config
from django.core.wsgi import get_wsgi_application

# Lee el entorno desde .env y selecciona settings
env = config('ENVIRONMENT', default='local').lower()
if env in ('prod','production'):
    settings_module = 'config.settings.prod'
elif env in ('dev','development'):
    settings_module = 'config.settings.dev'
else:
    settings_module = 'config.settings.local'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
