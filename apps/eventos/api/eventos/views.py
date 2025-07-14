from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.eventos.models import Evento
from .serializers import EventoSerializer
from apps.users.api.permissions import HasAnyRole
from apps.users.enums import UserRoles


class EventoViewSet(viewsets.ModelViewSet):
    """
    Vista para Armando (business_owner) que permite CRUD completo de eventos.
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.BUSINESS_OWNER]

    def destroy(self, request, *args, **kwargs):
        evento = self.get_object()
        evento.esta_activo = False
        evento.save()
        return Response(
            {"detail": "El evento fue desactivado correctamente."},
            status=status.HTTP_200_OK
        )


class EventoActivoAPIView(generics.RetrieveAPIView):
    """
    Vista para el frontend público (EGPro) que obtiene el evento activo más reciente.
    """
    serializer_class = EventoSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]  # solo egpro puede hacer esta petición

    def get_object(self):
        return Evento.objects.filter(esta_activo=True).order_by('-fecha_evento').first()
