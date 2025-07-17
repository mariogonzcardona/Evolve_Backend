from rest_framework import viewsets
from apps.eventos.models import TipoBoleto
from .serializers import TipoBoletoPublicSerializer
from apps.users.api.permissions import HasAnyRole
from apps.users.enums import UserRoles

class TipoBoletoPublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TipoBoleto.objects.filter(activo=True).order_by('orden')
    serializer_class = TipoBoletoPublicSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]