from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from apps.eventos.models import Patrocinador
from apps.eventos.api.patrocinadores.serializers import PatrocinadorPublicSerializer
from apps.users.api.permissions import HasAnyRole
from apps.users.enums import UserRoles
from rest_framework.generics import ListAPIView


class PatrocinadorPublicoListView(ListAPIView):
    """
    Vista pública de EGPro para mostrar patrocinadores confirmados.
    """
    queryset = Patrocinador.objects.filter(activo=True, confirmado=True).order_by('id')
    serializer_class = PatrocinadorPublicSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]