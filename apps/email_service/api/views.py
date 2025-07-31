from rest_framework.generics import CreateAPIView
from apps.users.api.permissions import HasAnyRole
from apps.users.enums import UserRoles
from apps.email_service.tasks import send_email_in_thread
from decouple import config
from .serializers import ContactoSerializer
from django_ratelimit.decorators import ratelimit
from rest_framework.exceptions import Throttled
from django.utils.decorators import method_decorator

@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=False), name='post')
class ContactoCreateView(CreateAPIView):
    serializer_class = ContactoSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]

    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            raise Throttled(detail="Has realizado demasiadas solicitudes. Intenta de nuevo más tarde.")
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        data = serializer.validated_data
        send_email_in_thread({
            'to_email': [config('EMAIL_HOST_USER')],
            'email_subject': data['asunto'],
            'nombre': data['nombre'],
            'correo': data['correo'],
            'mensaje': data['mensaje'],
            'template': 'contacto'  # Specify the template to use
        })