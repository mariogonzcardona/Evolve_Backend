from rest_framework import serializers
from apps.eventos.models import Patrocinador,TipoPatrocinio

class PatrocinadorPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patrocinador
        fields = [
            'nombre_marca',
            'logo',
            'sitio_web',
            "youtube",
            "facebook",
            "instagram",
            "twitter",
        ]

# class LogoUploadSerializer(serializers.Serializer):
#     archivo = serializers.ImageField()

#     def validate_archivo(self, value):
#         # Validación opcional extra
#         max_size_mb = 5
#         if value.size > max_size_mb * 1024 * 1024:
#             raise serializers.ValidationError(f"La imagen supera los {max_size_mb}MB.")
#         return value

class TipoPatrociniosSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPatrocinio
        fields = ['id', 'descripcion']
    

class PatrocinadorSerializer(serializers.ModelSerializer):
    tipos_patrocinio = serializers.PrimaryKeyRelatedField(
        queryset=TipoPatrocinio.objects.all(),
        many=True
    )
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Patrocinador
        fields = [
            "nombre_completo",
            "puesto",
            "email",
            "telefono",
            "nombre_marca",
            "giro",
            "estado",
            "ciudad",
            "sitio_web",
            "youtube",
            "facebook",
            "instagram",
            "twitter",
            "tipos_patrocinio",
            "ha_patrocinado_antes",
            "mensaje",
            "logo"
        ]

    def validate_logo(self, value):
        if value:
            max_size_mb = 5
            if value.size > max_size_mb * 1024 * 1024:
                raise serializers.ValidationError(f"La imagen supera los {max_size_mb} MB.")
            if value.image.format.lower() not in ["jpeg", "png", "jpg"]:
                raise serializers.ValidationError("Formato no válido. Usa JPG o PNG.")
        return value