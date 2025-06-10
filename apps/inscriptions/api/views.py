from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    TipoInscripcionSerializer,
    MetodoPagoSerializer,
    MembresiaSerializer,
    PagoRecurrenteSerializer,
    TipoInscripcionDeactivateSerializer,
    MetodoPagoDeactivateSerializer,
    MembresiaDeactivateSerializer,
)
from ..models import TipoInscripcion, MetodoPago, Membresia, PagoRecurrente
from ...users.api.permissions import IsAdminOrReadOnly, IsCoachOrAdmin
from .permissions import IsOwnerOrCoachOrAdmin

# ---------------------------------------------
# Tipo de Inscripción
# Solo lectura o admin puede editar
# ---------------------------------------------
class TipoInscripcionViewSet(viewsets.ModelViewSet):
    queryset = TipoInscripcion.objects.all()
    serializer_class = TipoInscripcionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'patch']  # Removemos delete

    def get_serializer_class(self):
        if self.action == 'desactivar':
            return TipoInscripcionDeactivateSerializer
        return self.serializer_class

    @action(detail=True, methods=['patch'], url_path='desactivar')
    def desactivar(self, request, pk=None):
        tipo = self.get_object()
        serializer = self.get_serializer(instance=tipo, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Tipo de inscripción desactivado correctamente."})


# ---------------------------------------------
# Método de Pago
# Solo lectura o admin puede editar
# ---------------------------------------------
class MetodoPagoViewSet(viewsets.ModelViewSet):
    queryset = MetodoPago.objects.all()
    serializer_class = MetodoPagoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'patch']  # Removemos delete

    def get_serializer_class(self):
        if self.action == 'desactivar':
            return MetodoPagoDeactivateSerializer
        return self.serializer_class

    @action(detail=True, methods=['patch'], url_path='desactivar')
    def desactivar(self, request, pk=None):
        metodo = self.get_object()
        serializer = self.get_serializer(instance=metodo, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Método de pago desactivado correctamente."})


# ---------------------------------------------
# Membresía (relación entre usuario y plan)
# Crear/editar solo coach o admin
# Cliente solo ve sus membresías
# ---------------------------------------------
class MembresiaViewSet(viewsets.ModelViewSet):
    queryset = Membresia.objects.select_related('usuario', 'tipo_inscripcion', 'metodo_pago').all()
    serializer_class = MembresiaSerializer
    http_method_names = ['get', 'post', 'put', 'patch']  # Removemos delete

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'desactivar']:
            return [IsAuthenticated(), IsCoachOrAdmin()]
        elif self.action == 'retrieve':
            return [IsAuthenticated(), IsOwnerOrCoachOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.role == 'coach':
            return self.queryset
        return self.queryset.filter(usuario=user)

    def get_serializer_class(self):
        if self.action == 'desactivar':
            return MembresiaDeactivateSerializer
        return self.serializer_class

    @action(detail=True, methods=['patch'], url_path='desactivar')
    def desactivar(self, request, pk=None):
        membresia = self.get_object()
        serializer = self.get_serializer(instance=membresia, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Membresía desactivada correctamente."})


# ---------------------------------------------
# Pago recurrente
# Crear solo coach o admin
# Cliente solo ve sus pagos
# ---------------------------------------------
class PagoRecurrenteViewSet(viewsets.ModelViewSet):
    queryset = PagoRecurrente.objects.select_related('membresia', 'membresia__usuario', 'pagado_por').all()
    serializer_class = PagoRecurrenteSerializer
    http_method_names = ['get', 'post', 'put', 'patch']  # Removemos delete

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), IsCoachOrAdmin()]
        elif self.action == 'retrieve':
            return [IsAuthenticated(), IsOwnerOrCoachOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.role == 'coach':
            return self.queryset
        return self.queryset.filter(membresia__usuario=user)
