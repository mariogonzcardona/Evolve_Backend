from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from apps.eventos.models import Peleador
from apps.eventos.api.peleadores.serializers import PeleadorSerializer
from apps.users.api.permissions import HasAnyRole
from apps.users.enums import UserRoles
from rest_framework.generics import ListAPIView
from apps.eventos.api.peleadores.serializers import PeleadorPublicoSerializer

class PeleadorViewSet(viewsets.ModelViewSet):
    """
    Vista para (business_owner) con CRUD completo sobre peleadores.
    La eliminación es lógica (activo = False).
    """
    queryset = Peleador.objects.all()
    serializer_class = PeleadorSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.BUSINESS_OWNER]

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save()

class PeleadorPublicoListView(ListAPIView):
    """
    Vista pública de EGPro para mostrar peleadores estelares confirmados.
    """
    serializer_class = PeleadorPublicoSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]

    def get_queryset(self):
        return (
            Peleador.objects.select_related("nacionalidad")
            .filter(es_estelar=True, confirmado=True, activo=True)
            .order_by("fecha_nacimiento")[:6]  # fecha_nacimiento más antigua → mayor edad
        )