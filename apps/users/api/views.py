from django.contrib.auth.models import update_last_login
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from decouple import config

from apps.users.models import UsuarioBase, UserInvitation, Cliente, Empleado
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserInvitationSerializer,
    CompleteInvitationSerializer,
)
from ..utils.email_utils import send_password_reset_email, send_invitation_email


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
            'user': {
                'id': user.id,
                'email': user.email,
                'nombre': user.nombre,
                'apellido': user.apellido,
                'role': user.role
            }
        })


class LogoutView(TokenBlacklistView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = LogoutSerializer


# -----------------------------
# 2. Gestión de contraseñas
# -----------------------------
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = UsuarioBase.objects.get(email=email)
            send_password_reset_email(user, request, tipo='reset')
            return Response({"message": "Correo enviado con éxito"})
        except UsuarioBase.DoesNotExist:
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
# 3. Invitaciones
# -----------------------------
class UserInvitationCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserInvitationSerializer

    @swagger_auto_schema(request_body=UserInvitationSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            invitacion = serializer.save()

            link_registro = f"{config('FRONTEND_BASE_URL')}/registro-cliente/{invitacion.token}"
            link_whatsapp = None

            if invitacion.medio_envio in ['email', 'ambos']:
                send_invitation_email(invitacion, request)

            if invitacion.medio_envio in ['whatsapp', 'ambos'] and invitacion.telefono:
                mensaje = f"Hola! Haz clic para registrarte en Evolve: {link_registro}"
                link_whatsapp = f"https://wa.me/52{invitacion.telefono}?text={mensaje.replace(' ', '%20')}"

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
