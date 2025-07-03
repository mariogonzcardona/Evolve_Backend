from rest_framework import serializers
from apps.users.models import UsuarioBase, Cliente
from apps.users.enums import UserRoles, UserStatus
from datetime import date


class ClienteDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['filial', 'status']


class ClienteCreateSerializer(serializers.ModelSerializer):
    cliente = ClienteDataSerializer()

    class Meta:
        model = UsuarioBase
        fields = [
            'email', 'nombre', 'apellido', 'alias', 'fecha_nacimiento', 'genero',
            'padecimientos_medicos', 'telefono_personal', 'telefono_emergencia',
            'estado', 'ciudad', 'colonia', 'calle', 'numero', 'codigo_postal',
            'cliente'
        ]

    def validate_email(self, value):
        if UsuarioBase.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate_fecha_nacimiento(self, value):
        if value > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede estar en el futuro.")
        if (date.today() - value).days < 2 * 365:
            raise serializers.ValidationError("El cliente debe tener al menos 2 años.")
        return value

    def create(self, validated_data):
        cliente_data = validated_data.pop('cliente')

        usuario = UsuarioBase.objects.create_user(
            role=UserRoles.ATHLETE,
            is_active=True,
            **validated_data
        )
        Cliente.objects.create(usuario=usuario, **cliente_data)
        return usuario


class ClienteDetailSerializer(serializers.ModelSerializer):
    cliente = ClienteDataSerializer(read_only=True)

    class Meta:
        model = UsuarioBase
        fields = [
            'id', 'email', 'nombre', 'apellido', 'alias', 'fecha_nacimiento', 'genero',
            'padecimientos_medicos', 'telefono_personal', 'telefono_emergencia',
            'estado', 'ciudad', 'colonia', 'calle', 'numero', 'codigo_postal',
            'is_active', 'role', 'cliente'
        ]


class ClienteListSerializer(serializers.ModelSerializer):
    filial = serializers.SerializerMethodField()

    class Meta:
        model = UsuarioBase
        fields = ['id', 'nombre', 'apellido', 'email', 'is_active', 'filial']

    def get_filial(self, obj):
        return getattr(obj.cliente.filial, 'nombre', None)


class ClienteUpdateSerializer(serializers.ModelSerializer):
    cliente = ClienteDataSerializer()

    class Meta:
        model = UsuarioBase
        fields = [
            'nombre', 'apellido', 'alias', 'fecha_nacimiento', 'genero',
            'padecimientos_medicos', 'telefono_personal', 'telefono_emergencia',
            'estado', 'ciudad', 'colonia', 'calle', 'numero', 'codigo_postal',
            'is_active', 'cliente'
        ]

    def update(self, instance, validated_data):
        cliente_data = validated_data.pop('cliente', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        cliente = instance.cliente
        for attr, value in cliente_data.items():
            setattr(cliente, attr, value)
        cliente.save()

        return instance


class ClienteStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=UserStatus.CHOICES)

    class Meta:
        model = Cliente
        fields = ['status']

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.save()

        # Si el status es INACTIVE, desactiva el acceso
        if instance.status == UserStatus.INACTIVE:
            instance.usuario.is_active = False
            instance.usuario.save()
        elif instance.status == UserStatus.ACTIVE:
            instance.usuario.is_active = True
            instance.usuario.save()

        return instance
