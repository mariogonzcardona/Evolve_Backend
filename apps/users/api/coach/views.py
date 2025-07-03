from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from apps.users.models import UsuarioBase
from apps.users.enums import UserRoles
from apps.users.api.coach.serializers import (
    CoachCreateSerializer,
    CoachDetailSerializer,
    CoachListSerializer,
    CoachUpdateSerializer,
    CoachStatusSerializer,
)
from apps.users.api.permissions import HasAnyRole

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

class CoachViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasAnyRole]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'empleado__filial', 'empleado__status']
    search_fields = ['nombre', 'apellido', 'email']
    ordering_fields = ['nombre', 'apellido', 'email']
    ordering = ['nombre']

    # ✅ Permitimos solo a business_owner y admin
    allowed_roles = [UserRoles.BUSINESS_OWNER, UserRoles.ADMIN]

    def get_queryset(self):
        user = self.request.user

        if user.role == UserRoles.BUSINESS_OWNER:
            return UsuarioBase.objects.filter(role=UserRoles.COACH)

        if user.role == UserRoles.ADMIN and hasattr(user, 'empleado') and user.empleado.filial:
            return UsuarioBase.objects.filter(
                role=UserRoles.COACH,
                empleado__filial=user.empleado.filial
            )

        return UsuarioBase.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return CoachListSerializer
        elif self.action == 'retrieve':
            return CoachDetailSerializer
        elif self.action == 'create':
            return CoachCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CoachUpdateSerializer
        elif self.action == 'update_status':
            return CoachStatusSerializer
        return CoachListSerializer

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        coach = self.get_object()
        user = request.user

        if user.role == UserRoles.ADMIN:
            if not hasattr(user, 'empleado') or user.empleado.filial != coach.empleado.filial:
                return Response({"detail": "No puedes modificar coaches de otra filial."}, status=403)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Eliminación directa no permitida."}, status=405)

    @action(detail=True, methods=['patch'], url_path='status', permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        coach = self.get_object()
        user = request.user

        if user.role == UserRoles.ADMIN:
            if not hasattr(user, 'empleado') or user.empleado.filial != coach.empleado.filial:
                return Response({"detail": "No puedes cambiar el estado de un coach de otra filial."}, status=403)

        if user.role not in [UserRoles.BUSINESS_OWNER, UserRoles.ADMIN]:
            return Response({"detail": "No tienes permiso para cambiar el estado de este usuario."}, status=403)

        serializer = CoachStatusSerializer(coach.empleado, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": "Estado actualizado correctamente."}, status=200)
