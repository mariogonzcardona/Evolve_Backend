from rest_framework import serializers
from apps.eventos.models import Peleador, Nacionalidad, Direccion, Evento
from datetime import date
from django.db import transaction, IntegrityError

class NacionalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nacionalidad
        fields = ['id', 'nombre', 'codigo_iso']

class EventoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['id', 'nombre', 'fecha_evento']

class PeleadorRegistroSerializer(serializers.ModelSerializer):
    nacionalidad = serializers.CharField(write_only=True)
    direccion = serializers.DictField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = Peleador
        fields = [
            "foto",
            "nombre",
            "apellido",
            "apodo",
            "email",
            "telefono",
            "nacionalidad",
            "direccion",
            "fecha_nacimiento",
            "cinta",
            "genero",
            "peso_kg",
            "preferencia_combate",
            "categoria",
            "racha",
            "equipo",
            "trayectoria",
            "youtube",
            "facebook",
            "instagram",
            "twitter",
        ]
        extra_kwargs = {
            "email": {"validators": []},  # Desactiva validadores automáticos
        }

    def validate_email(self, value):
        value = value.strip().lower()
        if Peleador.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado para el evento.")
        return value
    
    def validate_foto(self, value):
        """
        Validación de la imagen subida.
        """
        max_size_mb = 5
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"La imagen supera los {max_size_mb}MB.")
        return value

    def create(self, validated_data):
        codigo = str(validated_data.pop("nacionalidad", "")).lower()
        direccion_data = validated_data.pop("direccion", {})

        try:
            with transaction.atomic():
                # Nacionalidad
                nacionalidad = Nacionalidad.objects.filter(
                    codigo_iso=codigo,
                    activo=True
                ).first()
                if not nacionalidad:
                    raise serializers.ValidationError({"nacionalidad": "No válida o no activa."})

                # Evento activo
                evento = Evento.objects.filter(esta_activo=True).first()
                if not evento:
                    raise serializers.ValidationError({"evento": "No hay evento activo para registrar."})

                # Email normalizado
                validated_data["email"] = validated_data["email"].strip().lower()

                # Dirección
                direccion = Direccion.objects.create(**direccion_data)
                validated_data["nacionalidad"] = nacionalidad
                validated_data["direccion"] = direccion
                validated_data["evento"] = evento

                # Guardar y subir la imagen automáticamente a S3
                peleador = super().create(validated_data)
                return peleador

        except IntegrityError as e:
            raise serializers.ValidationError({
                "email": "Ya existe un peleador registrado con este correo."
                if "email" in str(e) else "Error de integridad en la base de datos.",
                "detalle": str(e),
            })

        except Exception as e:
            raise serializers.ValidationError({
                "detalle": f"Error al crear el peleador: {str(e)}"
            })

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

class PerfilUploadSerializer(serializers.Serializer):
    archivo = serializers.ImageField()

    def validate_archivo(self, value):
        max_size_mb = 5
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"La imagen supera los {max_size_mb}MB.")
        return value

class PeleadoresConfirmadosSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Peleador
        fields = [
            "id",
            "nombre",
            "apellido",
            "apodo",
            'nombre_completo'
        ]
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} ({obj.apodo}) {obj.apellido}" if obj.apodo else f"{obj.nombre} {obj.apellido}"