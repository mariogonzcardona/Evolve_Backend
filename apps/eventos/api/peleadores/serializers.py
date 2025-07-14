from rest_framework import serializers
from apps.eventos.models import Peleador, Nacionalidad, Direccion, Evento
from apps.eventos.api.serializers import DireccionSerializer
from datetime import date

class NacionalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nacionalidad
        fields = ['id', 'nombre', 'codigo_iso']

class EventoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['id', 'nombre', 'fecha_evento']

class PeleadorSerializer(serializers.ModelSerializer):
    nacionalidad = NacionalidadSerializer(read_only=True)
    direccion = DireccionSerializer(read_only=True)
    evento = EventoSimpleSerializer(read_only=True)

    nacionalidad_id = serializers.PrimaryKeyRelatedField(
        queryset=Nacionalidad.objects.filter(activo=True),
        write_only=True,
        source='nacionalidad'
    )
    direccion_id = serializers.PrimaryKeyRelatedField(
        queryset=Direccion.objects.all(),
        write_only=True,
        source='direccion'
    )
    evento_id = serializers.PrimaryKeyRelatedField(
        queryset=Evento.objects.filter(esta_activo=True),
        write_only=True,
        source='evento'
    )

    class Meta:
        model = Peleador
        fields = [
            'id',
            'nombre',
            'apellido',
            'apodo',
            'email',
            'telefono',
            'nacionalidad', 'nacionalidad_id',
            'direccion', 'direccion_id',
            'fecha_nacimiento',
            'genero',
            'evento', 'evento_id',
            'peso_kg',
            'preferencia_combate',
            'cinta',
            'equipo',
            'foto',
            'trayectoria',
            'categoria',
            'racha',
            'firma_contrato',
            'es_estelar',
            'confirmado',
            'activo',
            'facebook', 'instagram', 'twitter', 'youtube',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'confirmado', 'activo', 'fecha_creacion', 'fecha_actualizacion']

class PeleadorPublicoSerializer(serializers.ModelSerializer):
    nacionalidad = serializers.CharField(source="nacionalidad.codigo_iso")
    edad = serializers.SerializerMethodField()
    class Meta:
        model = Peleador
        fields = [
            "foto",
            "nombre",
            "apellido",
            "apodo",
            "nacionalidad",
            "edad",
            "cinta",
            "equipo",
            "racha",
            "youtube",
            "facebook",
            "instagram",
            "twitter"
        ]
    
    def get_edad(self, obj):
        if not obj.fecha_nacimiento:
            return None
        today = date.today()
        return (
            today.year - obj.fecha_nacimiento.year - ((today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day))
        )