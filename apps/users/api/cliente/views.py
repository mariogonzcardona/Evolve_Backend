from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from apps.users.models import UsuarioBase
from apps.users.enums import UserRoles
from apps.users.api.cliente.serializers import (
    ClienteCreateSerializer,
    ClienteDetailSerializer,
    ClienteListSerializer,
    ClienteUpdateSerializer,
    ClienteStatusSerializer
)
from apps.users.api.permissions import HasAnyRole


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasAnyRole]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'cliente__filial', 'cliente__status']
    search_fields = ['nombre', 'apellido', 'email']
    ordering_fields = ['nombre', 'apellido', 'email']
    ordering = ['nombre']

    allowed_roles = [UserRoles.BUSINESS_OWNER, UserRoles.ADMIN, UserRoles.COACH, UserRoles.ATHLETE]

    def get_queryset(self):
        user = self.request.user

        if user.role == UserRoles.BUSINESS_OWNER:
            return UsuarioBase.objects.filter(role=UserRoles.ATHLETE)

        elif user.role in [UserRoles.ADMIN, UserRoles.COACH]:
            if hasattr(user, 'empleado') and user.empleado.filial:
                return UsuarioBase.objects.filter(
                    role=UserRoles.ATHLETE,
                    cliente__filial=user.empleado.filial
                )

        elif user.role == UserRoles.ATHLETE:
            return UsuarioBase.objects.filter(pk=user.pk)

        return UsuarioBase.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return ClienteListSerializer
        elif self.action == 'retrieve':
            return ClienteDetailSerializer
        elif self.action == 'create':
            return ClienteCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClienteUpdateSerializer
        elif self.action == 'update_status':
            return ClienteStatusSerializer
        return ClienteListSerializer

    def update(self, request, *args, **kwargs):
        cliente = self.get_object()
        user = request.user

        if user.role == UserRoles.ATHLETE and cliente.pk != user.pk:
            return Response({"detail": "No puedes modificar otro perfil."}, status=403)

        if user.role in [UserRoles.ADMIN, UserRoles.COACH]:
            if not hasattr(user, 'empleado') or user.empleado.filial != cliente.cliente.filial:
                return Response({"detail": "No puedes modificar clientes de otra filial."}, status=403)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Eliminación directa no permitida."}, status=405)

    @action(detail=True, methods=["patch"], url_path="status", permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        cliente = self.get_object()
        user = request.user

        if user.role == UserRoles.ATHLETE:
            return Response({"detail": "No tienes permiso para modificar tu estado."}, status=403)

        if user.role in [UserRoles.ADMIN, UserRoles.COACH]:
            if not hasattr(user, 'empleado') or user.empleado.filial != cliente.cliente.filial:
                return Response({"detail": "No puedes modificar clientes de otra filial."}, status=403)

        serializer = ClienteStatusSerializer(cliente.cliente, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": "Estado actualizado correctamente."}, status=200)
