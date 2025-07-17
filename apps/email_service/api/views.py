from rest_framework.generics import CreateAPIView
from apps.users.api.permissions import HasAnyRole
from apps.users.enums import UserRoles
from apps.email_service.tasks import send_email_in_thread
from decouple import config
from .serializers import ContactoSerializer

class ContactoCreateView(CreateAPIView):
    serializer_class = ContactoSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]

    def perform_create(self, serializer):
        data = serializer.validated_data
        send_email_in_thread({
            'to_email': [config('EMAIL_HOST_USER')],
            'email_subject': data['asunto'],
            'nombre': data['nombre'],
            'correo': data['correo'],
            'mensaje': data['mensaje'],
        })