from rest_framework import serializers
from ..models import TipoInscripcion, MetodoPago, Membresia, PagoRecurrente
from ...users.api.serializers import UserMinimalSerializer

# ---------------------------------------
# Tipo de Inscripción
# ---------------------------------------
class TipoInscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoInscripcion
        fields = ['id', 'nombre', 'descripcion', 'esta_activo', 'fecha_creacion','fecha_actualizacion']


# ---------------------------------------
# Método de Pago
# ---------------------------------------
class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = ['id', 'nombre', 'descripcion', 'esta_activo', 'codigo_integracion','requiere_confirmacion_manual']


# ---------------------------------------
# Membresía
# ---------------------------------------
class MembresiaSerializer(serializers.ModelSerializer):
    usuario = UserMinimalSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Membresia._meta.get_field('usuario').remote_field.model.objects.all(),
        source='usuario',
        write_only=True
    )
    tipo_inscripcion = TipoInscripcionSerializer(read_only=True)
    tipo_inscripcion_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoInscripcion.objects.all(),
        source='tipo_inscripcion',
        write_only=True
    )
    metodo_pago = MetodoPagoSerializer(read_only=True)
    metodo_pago_id = serializers.PrimaryKeyRelatedField(
        queryset=MetodoPago.objects.all(),
        source='metodo_pago',
        write_only=True
    )
    fecha_creacion = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    
    class Meta:
        model = Membresia
        fields = [
            'id',
            'usuario',
            'usuario_id',
            'tipo_inscripcion',
            'tipo_inscripcion_id',
            'metodo_pago',
            'metodo_pago_id',
            'fecha_inicio',
            'fecha_fin',
            'costo_inscripcion',
            'esta_activa',
            'observaciones',
            'fecha_creacion'
        ]
        read_only_fields = ['id']


# ---------------------------------------
# Pago Recurrente
# ---------------------------------------
class PagoRecurrenteSerializer(serializers.ModelSerializer):
    membresia = MembresiaSerializer(read_only=True)
    membresia_id = serializers.PrimaryKeyRelatedField(
        queryset=Membresia.objects.all(),
        source='membresia',
        write_only=True
    )
    pagado_por = UserMinimalSerializer(read_only=True)
    pagado_por_id = serializers.PrimaryKeyRelatedField(
        queryset=PagoRecurrente._meta.get_field('pagado_por').remote_field.model.objects.all(),
        source='pagado_por',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = PagoRecurrente
        fields = [
            'id', 
            'membresia', 
            'membresia_id',
            'frecuencia',
            'periodo_inicio',
            'monto_recurrente',
            'fecha_pago', 
            'dia_limite_pago',
            'pagado_por', 
            'pagado_por_id',
            'observaciones'
        ]
        read_only_fields = ['id']


# ---------------------------------------
# Desactivación
# ---------------------------------------
class TipoInscripcionDeactivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoInscripcion
        fields = []

    def validate(self, data):
        if not self.instance.esta_activo:
            raise serializers.ValidationError("Este tipo de inscripción ya está desactivado.")
        return data

    def update(self, instance, validated_data):
        instance.esta_activo = False
        instance.save()
        return instance

class MetodoPagoDeactivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = []

    def validate(self, data):
        if not self.instance.esta_activo:
            raise serializers.ValidationError("Este método de pago ya está desactivado.")
        return data

    def update(self, instance, validated_data):
        instance.esta_activo = False
        instance.save()
        return instance

class MembresiaDeactivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membresia
        fields = []

    def validate(self, data):
        if not self.instance.esta_activa:
            raise serializers.ValidationError("Esta membresía ya está desactivada.")
        return data

    def update(self, instance, validated_data):
        instance.esta_activa = False
        instance.save()
        return instance
