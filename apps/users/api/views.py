from django.contrib.auth.models import update_last_login
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.permissions import OR
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from ..utils.email_utils import send_password_reset_email, send_invitation_email
from rest_framework.pagination import PageNumberPagination
from apps.users.models import CustomUser,UserInvitation, Empleado
from .permissions import IsAdminOrReadOnly, IsSelfOrAdmin, IsCoachOrAdmin
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserListSerializer,
    UserUpdateAdminSerializer,
    UserUpdateCoachSerializer,
    UserProfileSerializer,
    UserDeactivateSerializer,
    UserBaseSerializer,
    UserMinimalSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserInvitationSerializer,
    CompleteInvitationSerializer,
    EmpleadoSerializer,
)
from apps.users.api import serializers
from drf_yasg.utils import swagger_auto_schema
from decouple import config

# -----------------------------
# 1. Autenticación y acceso
# -----------------------------
class UserLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserMinimalSerializer(user).data
        })

class LogoutView(TokenBlacklistView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = LogoutSerializer

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
            send_password_reset_email(user, request, tipo='reset')
            return Response({"message": "Correo enviado con éxito"})
        except CustomUser.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Contraseña actualizada correctamente."})

class ChangePasswordView(generics.UpdateAPIView):
    http_method_names = ['put']
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save() 
        
        return Response({"detail": "Contraseña actualizada correctamente."})

# -----------------------------
# 2. Extras
# -----------------------------
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

# -----------------------------
# 3. Gestión de Usuarios
# -----------------------------
class CustomUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.filter(is_superuser=False)
    http_method_names = ['get', 'post', 'put','patch']
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['nombre', 'apellido', 'email']
    ordering_fields = ['nombre', 'apellido', 'email', 'role']
    ordering = ['nombre']  # por defecto

    def get_permissions(self):
        if self.action == 'list':
            return [IsCoachOrAdmin()]
        elif self.action == 'retrieve':
            return [IsSelfOrAdmin()]
        elif self.action == 'partial_update':
            return [OR(IsSelfOrAdmin(), IsCoachOrAdmin())]
        elif self.action == 'desactivar':
            return [IsCoachOrAdmin()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'partial_update':
            if self.request.user.role == 'admin':
                return UserUpdateAdminSerializer
            elif self.request.user.role == 'coach':
                return UserUpdateCoachSerializer
            else:
                return UserProfileSerializer
        elif self.action == 'desactivar':
            return UserDeactivateSerializer
        return UserBaseSerializer

    @action(detail=True, methods=['patch'], url_path='desactivar')
    def desactivar(self, request, pk=None):
        user = self.get_object()
        
        # Protegemos a admins de ser desactivados por coaches
        if request.user.role == 'coach' and user.role == 'admin':
            return Response(
                {"detail": "No tienes permiso para desactivar a un administrador."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # No permitir desactivar superusuarios
        if user.is_superuser:
            return Response(
                {"detail": "No se puede desactivar a un superusuario."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(instance=user, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Usuario desactivado correctamente."})

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Reglas extra: coach no puede editar admins
        if request.user.role == 'coach' and instance.role == 'admin':
            return Response(
                {"detail": "No puedes editar a un administrador."},
                status=status.HTTP_403_FORBIDDEN,
            )
        

        return super().partial_update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        requested_role = request.data.get("role")
        current_user_role = request.user.role

        if current_user_role == "admin":
            # puede crear cualquier rol
            pass
        elif current_user_role == "coach":
            if requested_role != "athlete":
                return Response(
                    {"detail": "Los coaches solo pueden registrar usuarios tipo clientes."},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {"detail": "No tienes permiso para crear usuarios."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Asegurar que el serializer reciba el request para enviar correo
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return self.queryset.filter(role__in=['admin', 'coach'])
        elif user.role == 'coach':
            return self.queryset.filter(role='athlete')
        return self.queryset.filter(id=user.id)

# Gestion de Empleados
class EmpleadoListView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsCoachOrAdmin]
    serializer_class = EmpleadoSerializer

    def get_queryset(self):
        user = self.request.user
        base_qs = Empleado.objects.select_related('usuario')
        if user.role == 'admin':
            return base_qs.filter(usuario__role__in=['admin', 'coach'])
        elif user.role == 'coach':
            return base_qs.filter(usuario__role='athlete')
        return base_qs.none()

class UserUpdateCoachSerializer(UserProfileSerializer):
    def validate(self, data):
        if 'role' in data and data['role'] != 'athlete':
            raise serializers.ValidationError("Los coaches solo pueden modificar clientes.")
        return data


class UserInvitationCreateView(APIView):
    permission_classes = [IsAuthenticated,IsCoachOrAdmin]
    serializer_class=UserInvitationSerializer

    @swagger_auto_schema(request_body=UserInvitationSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            invitacion = serializer.save()
            return Response({
                'message': 'Invitación creada correctamente.',
                'token': str(invitacion.token),
                'email': invitacion.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserInvitationCreateView(APIView):
    permission_classes = [IsAuthenticated]  # + tu permiso personalizado
    serializer_class = UserInvitationSerializer

    @swagger_auto_schema(request_body=UserInvitationSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            invitacion = serializer.save()

            # 👉 Enlace para WhatsApp (opcional)
            link_registro = f"{config('FRONTEND_BASE_URL')}/registro-cliente/{invitacion.token}"
            link_whatsapp = None

            if invitacion.medio_envio in ['email', 'ambos']:
                send_invitation_email(invitacion, request)

            if invitacion.medio_envio in ['whatsapp', 'ambos'] and invitacion.telefono:
                numero = invitacion.telefono
                mensaje = f"Hola! Haz clic para registrarte en Evolve: {link_registro}"
                link_whatsapp = f"https://wa.me/52{numero}?text={mensaje.replace(' ', '%20')}"

            return Response({
                'message': 'Invitación creada correctamente.',
                'token': str(invitacion.token),
                'email': invitacion.email,
                'whatsapp_link': link_whatsapp
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompleteInvitationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CompleteInvitationSerializer
    
    @swagger_auto_schema(request_body=CompleteInvitationSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Registro completado exitosamente.',
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)