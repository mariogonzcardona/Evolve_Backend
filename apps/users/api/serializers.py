from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from ..utils.email_utils import send_password_reset_email
from ..models import CustomUser, Cliente, Empleado,UserInvitation
from datetime import date
from django.conf import settings
import re
from drf_yasg.utils import swagger_auto_schema

CustomUser = get_user_model()

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
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
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
# 2. Registro
# -----------------------------

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'nombre', 'apellido')

class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ['password', 'user_permissions', 'groups', 'is_superuser', 'is_staff', 'last_login']  # ocultamos lo que no se necesita

class UserCreateSerializer(serializers.ModelSerializer):
    foto_perfil = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = [
            'email', 'nombre', 'apellido', 'alias', 'fecha_nacimiento', 'genero',
            'padecimientos_medicos', 'telefono_personal', 'telefono_emergencia',
            'foto_perfil', 'estado', 'ciudad', 'colonia', 'calle', 'numero',
            'codigo_postal', 'role'
        ]
        
    def get_foto_perfil(self, obj):
        request = self.context.get('request')
        if obj.foto_perfil and hasattr(obj.foto_perfil, 'url'):
            return request.build_absolute_uri(obj.foto_perfil.url) if request else obj.foto_perfil.url
        return None

    def validate_fecha_nacimiento(self, value):
        if value > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser en el futuro")
        if value < date.today().replace(year=date.today().year - 100):
            raise serializers.ValidationError("La fecha de nacimiento no puede tener más de 100 años")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado")
        return value

    def validate_telefono_personal(self, value):
        if not re.fullmatch(r'\d{10,}', value):
            raise serializers.ValidationError("El teléfono personal debe contener al menos 10 dígitos numéricos")
        return value

    def validate_telefono_emergencia(self, value):
        if not re.fullmatch(r'\d{10,}', value):
            raise serializers.ValidationError("El teléfono de emergencia debe contener al menos 10 dígitos numéricos")
        return value

    def validate_nombre(self, value):
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", value):
            raise serializers.ValidationError("El nombre solo debe contener letras y espacios")
        return value

    def validate_apellido(self, value):
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", value):
            raise serializers.ValidationError("El apellido solo debe contener letras y espacios")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        user = CustomUser(**validated_data)
        user.set_unusable_password()  # 🔐 sin contraseña de inicio
        user.save()

        if request:
            send_password_reset_email(user, request, tipo='welcome')

        return user

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['usuario']

class EmpleadoSerializer(serializers.ModelSerializer):
    usuario = UserMinimalSerializer(read_only=True)
    foto_perfil = serializers.SerializerMethodField()
    
    def get_foto_perfil(self, obj):
        request = self.context.get('request')
        if obj.usuario.foto_perfil and hasattr(obj.usuario.foto_perfil, 'url'):
            return request.build_absolute_uri(obj.usuario.foto_perfil.url) if request else obj.usuario.foto_perfil.url
        return None
    
    class Meta:
        model = Empleado
        fields = ['usuario', 'fecha_contratacion', 'especialidad', 'salario', 'certificaciones', 'tipo_contrato', 'activo', 'fecha_creacion', 'fecha_actualizacion','foto_perfil']
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']

# -----------------------------
# 3. Listar
# -----------------------------
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'nombre', 'apellido', 'email', 'role', 'is_active']

class UserDetailSerializer(serializers.ModelSerializer):
    foto_perfil = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'nombre', 'apellido', 'alias', 'fecha_nacimiento', 'genero',
            'padecimientos_medicos', 'telefono_personal', 'telefono_emergencia',
            'foto_perfil', 'estado', 'ciudad', 'colonia', 'calle', 'numero',
            'codigo_postal', 'role'
        ]

    def get_foto_perfil(self, obj):
        request = self.context.get('request')
        if obj.foto_perfil and hasattr(obj.foto_perfil, 'url'):
            return request.build_absolute_uri(obj.foto_perfil.url) if request else obj.foto_perfil.url
        return None

# -----------------------------
# 4. Actualizar
# -----------------------------
class UserValidationMixin:
        def validate_nombre(self, value):
            if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", value):
                raise serializers.ValidationError("El nombre solo debe contener letras y espacios")
            return value

        def validate_apellido(self, value):
            if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", value):
                raise serializers.ValidationError("El apellido solo debe contener letras y espacios")
            return value

        def validate_telefono_personal(self, value):
            if not re.fullmatch(r'\d{10,}', value):
                raise serializers.ValidationError("El teléfono personal debe contener al menos 10 dígitos")
            return value

        def validate_telefono_emergencia(self, value):
            if not re.fullmatch(r'\d{10,}', value):
                raise serializers.ValidationError("El teléfono de emergencia debe contener al menos 10 dígitos")
            return value

        def validate_fecha_nacimiento(self, value):
            if value > date.today():
                raise serializers.ValidationError("La fecha de nacimiento no puede ser en el futuro")
            if value < date.today().replace(year=date.today().year - 100):
                raise serializers.ValidationError("La fecha de nacimiento no puede tener más de 100 años")
            return value

class UserProfileSerializer(UserValidationMixin,serializers.ModelSerializer):
    foto_perfil = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = [
            'nombre', 'apellido', 'alias', 'fecha_nacimiento', 'genero',
            'padecimientos_medicos', 'telefono_personal', 'telefono_emergencia',
            'foto_perfil', 'estado', 'ciudad', 'colonia', 'calle', 'numero', 'codigo_postal'
        ]
        
    def get_foto_perfil(self, obj):
        request = self.context.get('request')
        if obj.foto_perfil and hasattr(obj.foto_perfil, 'url'):
            return request.build_absolute_uri(obj.foto_perfil.url) if request else obj.foto_perfil.url
        return None
    
class UserUpdateAdminSerializer(UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + ['role', 'is_active']
        read_only_fields = ['is_superuser', 'is_staff', 'last_login']

class EmpleadoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = ['fecha_contratacion', 'especialidad', 'salario', 'certificaciones', 'tipo_contrato', 'activo']

class UserUpdateCoachSerializer(UserProfileSerializer):
    empleado = EmpleadoDataSerializer()

    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + ['empleado']
        read_only_fields = ['is_superuser', 'is_staff', 'last_login']

    def update(self, instance, validated_data):
        empleado_data = validated_data.pop('empleado', {})
        instance = super().update(instance, validated_data)

        empleado = instance.empleado  # relación OneToOne
        for attr, value in empleado_data.items():
            setattr(empleado, attr, value)
        empleado.save()

        return instance

# -----------------------------
# 5. Desactivar
# -----------------------------
class UserDeactivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = []  # No necesitamos campos ya que solo desactivamos

    def validate(self, data):
        if not self.instance.is_active:
            raise serializers.ValidationError("El usuario ya está desactivado.")
        return data

    def update(self, instance, validated_data):
        instance.is_active = False
        instance.save()
        return instance

# -----------------------------
# 6. Utilitario
# -----------------------------


# -----------------------------
# 7. Invitacion
# -----------------------------
class UserInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInvitation
        fields = [
            'id',
            'email',
            'telefono',
            'medio_envio',
            'fecha_expiracion',
            'observaciones'
        ]
        # `enviado_por` no se expone al cliente directamente
        read_only_fields = ['id']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario registrado con este correo.")
        return value

    def validate(self, data):
        medio = data.get('medio_envio')
        telefono = data.get('telefono')

        if medio in ['whatsapp', 'ambos'] and not telefono:
            raise serializers.ValidationError({
                'telefono': "Debe proporcionar un número de teléfono si va a enviar la invitación por WhatsApp."
            })

        return data

    def create(self, validated_data):
        # Asignamos el usuario autenticado como quien envió la invitación
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
        return value

    def create(self, validated_data):
        token = validated_data.pop('token')
        invitacion = UserInvitation.objects.get(token=token)
        
        if CustomUser.objects.filter(email=invitacion.email).exists():
            raise serializers.ValidationError("Ya existe un usuario con este correo.")
        
        # Crear el usuario
        usuario = CustomUser.objects.create_user(
            email=invitacion.email,
            password=validated_data.pop('password'),
            role='athlete',
            is_active=True,
            **validated_data
        )

        # Marcar la invitación como usada
        invitacion.fue_usado = True
        invitacion.save()

        # Crear entrada en Cliente
        Cliente.objects.create(usuario=usuario)

        return usuario