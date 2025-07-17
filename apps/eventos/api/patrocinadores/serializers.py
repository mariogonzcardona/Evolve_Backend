from rest_framework import serializers
from apps.eventos.models import Patrocinador

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
