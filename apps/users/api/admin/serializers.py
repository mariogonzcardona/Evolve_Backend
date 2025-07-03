from rest_framework import serializers
from apps.users.models import UsuarioBase, Empleado
from apps.users.enums import UserRoles, UserStatus
from apps.filiales.models import Filial
from datetime import date
import re


class EmpleadoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = [
            'filial',
            'fecha_contratacion',
            'especialidad',
            'salario',
            'certificaciones',
            'tipo_contrato',
            'status'
        ]


class AdminCreateSerializer(serializers.ModelSerializer):
    empleado = EmpleadoDataSerializer()

    class Meta:
        model = UsuarioBase
        fields = [
            'email', 'nombre', 'apellido', 'alias', 'fecha_nacimiento', 'genero',
            'padecimientos_medicos', 'telefono_personal', 'telefono_emergencia',
            'estado', 'ciudad', 'colonia', 'calle', 'numero', 'codigo_postal',
            'empleado'
        ]

    def validate_email(self, value):
        if UsuarioBase.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate_fecha_nacimiento(self, value):
        # Validación de formato de fecha
        if value > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede estar en el futuro.")
        # Validación de edad mínima (18 años)
        if (date.today() - value).days < 18 * 365:
            raise serializers.ValidationError("El usuario debe tener al menos 18 años.")
        return value

    def create(self, validated_data):
        empleado_data = validated_data.pop('empleado')

        # Forzamos rol como 'admin' y activamos cuenta
        usuario = UsuarioBase.objects.create_user(
            role=UserRoles.ADMIN,
            is_active=True,
            **validated_data
        )

        # Crea relación con Empleado
        Empleado.objects.create(usuario=usuario, **empleado_data)

        return usuario


class AdminDetailSerializer(serializers.ModelSerializer):
    empleado = EmpleadoDataSerializer(read_only=True)

    class Meta:
        model = UsuarioBase
        fields = [
            'id', 'email', 'nombre', 'apellido', 'alias', 'fecha_nacimiento', 'genero',
            'padecimientos_medicos', 'telefono_personal', 'telefono_emergencia',
            'estado', 'ciudad', 'colonia', 'calle', 'numero', 'codigo_postal',
            'is_active', 'role', 'empleado'
        ]


class AdminListSerializer(serializers.ModelSerializer):
    filial = serializers.SerializerMethodField()

    class Meta:
        model = UsuarioBase
        fields = ['id', 'nombre', 'apellido', 'email', 'is_active', 'filial']

    def get_filial(self, obj):
        return getattr(obj.empleado.filial, 'nombre', None)

class EmpleadoDataUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = [
            'filial',
            'fecha_contratacion',
            'especialidad',
            'salario',
            'certificaciones',
            'tipo_contrato',
            'status'
        ]

class AdminUpdateSerializer(serializers.ModelSerializer):
    empleado = EmpleadoDataUpdateSerializer()

    class Meta:
        model = UsuarioBase
        fields = [
            'nombre', 'apellido', 'alias', 'fecha_nacimiento', 'genero',
            'padecimientos_medicos', 'telefono_personal', 'telefono_emergencia',
            'estado', 'ciudad', 'colonia', 'calle', 'numero', 'codigo_postal',
            'is_active', 'empleado'
        ]

    def update(self, instance, validated_data):
        empleado_data = validated_data.pop('empleado', {})
        # Actualiza usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualiza empleado
        empleado = instance.empleado
        for attr, value in empleado_data.items():
            setattr(empleado, attr, value)
        empleado.save()

        return instance

class AdminStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=UserStatus.CHOICES)

    class Meta:
        model = Empleado
        fields = ['status']

    def validate_status(self, value):
        if value not in dict(UserStatus.CHOICES):
            raise serializers.ValidationError("Estado no válido.")
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.save()

        # Opcional: desactivar cuenta automáticamente si status = inactive
        if instance.status == UserStatus.INACTIVE:
            instance.usuario.is_active = False
            instance.usuario.save()
        elif instance.status == UserStatus.ACTIVE:
            instance.usuario.is_active = True
            instance.usuario.save()

        return instance
