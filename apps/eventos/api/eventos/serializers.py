from rest_framework import serializers
from apps.eventos.models import Evento, Direccion
from apps.eventos.api.serializers import DireccionSerializer

class EventoSerializer(serializers.ModelSerializer):
    direccion = DireccionSerializer()

    class Meta:
        model = Evento
        fields = ['nombre','descripcion','tipo_evento','video_promocional_url','fecha_evento','hora_inicio','hora_fin','direccion','fecha_pesaje','hora_pesaje','esta_activo',]