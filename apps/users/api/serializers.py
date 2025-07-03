from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from ..utils.email_utils import send_password_reset_email
from ..models import UsuarioBase, Cliente, Empleado,UserInvitation
from datetime import date
from django.conf import settings
import re
from drf_yasg.utils import swagger_auto_schema
from apps.users.enums import UserRoles

UsuarioBase = get_user_model()

# -----------------------------
# 1. Autenticación y acceso
# -----------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(request=self.context.get('request'), email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Credenciales incorrectas")
        if not user.is_active:
            raise serializers.ValidationError("La cuenta está inactiva")
        return user

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = UsuarioBase.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UsuarioBase.DoesNotExist):
            raise serializers.ValidationError("Enlace inválido")

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Token inválido o expirado")

        # ✅ Guarda el usuario en el contexto
        self.context['user'] = user
        return data

    def save(self):
        # ✅ Recupera el usuario del contexto (no de self.user)
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])  # <- aquí se aplica el hash
        user.is_active = True
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual no es correcta")
        return value

    def validate_new_password(self, value):
        validate_password(value)  # usa las reglas definidas en settings.py
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


# -----------------------------
# 2. Invitacion
# -----------------------------
class UserInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInvitation
        fields = [
            'id', 'email', 'telefono', 'medio_envio', 'fecha_expiracion',
            'observaciones', 'role', 'filial'
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        if UsuarioBase.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario registrado con este correo.")
        return value

    def validate(self, data):
        medio = data.get('medio_envio')
        telefono = data.get('telefono')

        if medio in ['whatsapp', 'ambos'] and not telefono:
            raise serializers.ValidationError({
                'telefono': "Debe proporcionar un número de teléfono si va a enviar por WhatsApp."
            })

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        enviado_por = request.user if request else None

        return UserInvitation.objects.create(
            enviado_por=enviado_por,
            **validated_data
        )

class CompleteInvitationSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    nombre = serializers.CharField(max_length=50)
    apellido = serializers.CharField(max_length=50)
    alias = serializers.CharField(max_length=50, required=False, allow_blank=True)
    fecha_nacimiento = serializers.DateField()
    genero = serializers.ChoiceField(choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')])
    padecimientos_medicos = serializers.CharField(allow_blank=True, required=False)
    telefono_personal = serializers.CharField(max_length=20)
    telefono_emergencia = serializers.CharField(max_length=20)
    estado = serializers.CharField(max_length=50)
    ciudad = serializers.CharField(max_length=50)
    colonia = serializers.CharField(max_length=100)
    calle = serializers.CharField(max_length=100)
    numero = serializers.CharField(max_length=10)
    codigo_postal = serializers.CharField(max_length=10)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_token(self, value):
        try:
            invitacion = UserInvitation.objects.get(token=value, fue_usado=False)
        except UserInvitation.DoesNotExist:
            raise serializers.ValidationError("El token es inválido o ya fue utilizado.")
        if invitacion.is_expired():
            raise serializers.ValidationError("El token ha expirado.")
        self.context['invitacion'] = invitacion
        return value

    def create(self, validated_data):
        invitacion = self.context['invitacion']

        if UsuarioBase.objects.filter(email=invitacion.email).exists():
            raise serializers.ValidationError("Ya existe un usuario con este correo.")

        # Crear usuario base
        usuario = UsuarioBase.objects.create_user(
            email=invitacion.email,
            password=validated_data.pop('password'),
            role=invitacion.role,
            is_active=True,
            **validated_data
        )

        # Marcar invitación como usada
        invitacion.fue_usado = True
        invitacion.save()

        # Crear entrada según el rol
        if invitacion.role == UserRoles.ATHLETE:
            Cliente.objects.create(usuario=usuario, filial=invitacion.filial)
        elif invitacion.role in [UserRoles.ADMIN, UserRoles.COACH]:
            Empleado.objects.create(usuario=usuario, filial=invitacion.filial, fecha_contratacion=date.today())

        return usuario