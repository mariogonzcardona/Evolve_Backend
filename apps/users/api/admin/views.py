from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from apps.users.models import UsuarioBase
from apps.users.enums import UserRoles
from apps.users.api.admin.serializers import (
    AdminCreateSerializer,
    AdminDetailSerializer,
    AdminListSerializer,
    AdminUpdateSerializer,
    AdminStatusSerializer,
)
from apps.users.api.permissions import HasAnyRole

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

class AdminViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    queryset = UsuarioBase.objects.filter(role=UserRoles.ADMIN).order_by('nombre')
    permission_classes = [IsAuthenticated, HasAnyRole]
    allowed_roles = [UserRoles.BUSINESS_OWNER, UserRoles.ADMIN]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'empleado__filial', 'empleado__status']
    search_fields = ['nombre', 'apellido', 'email']
    ordering_fields = ['nombre', 'apellido', 'email']
    
    def get_queryset(self):
        user = self.request.user

        # Validar que tenga relación con Empleado antes de acceder a su filial
        if not hasattr(user, 'empleado'):
            return self.queryset.none()  # o lanzar 403

        filial = user.empleado.filial
        return self.queryset.filter(empleado__filial=filial)

    def get_serializer_class(self):
        if self.action == 'list':
            return AdminListSerializer
        elif self.action == 'retrieve':
            return AdminDetailSerializer
        elif self.action == 'create':
            return AdminCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AdminUpdateSerializer
        elif self.action == 'update_status':
            return AdminStatusSerializer
        return AdminListSerializer

    def create(self, request, *args, **kwargs):
        if request.user.role != UserRoles.BUSINESS_OWNER:
            return Response({"detail": "No tienes permiso para crear administradores."}, status=403)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.role != UserRoles.BUSINESS_OWNER:
            return Response({"detail": "No tienes permiso para modificar administradores."}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Eliminación directa no permitida."}, status=405)

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
        permission_classes=[IsAuthenticated, HasAnyRole],  # Verificamos rol permitido abajo
    )
    def update_status(self, request, pk=None):
        admin = self.get_object()
        user = request.user

        # Verificamos explícitamente si el usuario tiene permiso
        if user.role != UserRoles.BUSINESS_OWNER:
            return Response(
                {"detail": "No tienes permiso para cambiar el estado de este usuario."},
                status=403
            )

        serializer = AdminStatusSerializer(admin.empleado, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": "Estado actualizado correctamente."}, status=200)
