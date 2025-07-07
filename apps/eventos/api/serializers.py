from rest_framework import serializers
from ..models import Evento, Inscripcion, Direccion, Peleador

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class RedesSocialesSerializer(serializers.Serializer):
    youtube = serializers.URLField(required=False, allow_null=True)
    facebook = serializers.URLField(required=False, allow_null=True)
    instagram = serializers.URLField(required=False, allow_null=True)
    twitter = serializers.URLField(required=False, allow_null=True)


class PeleadorSerializer(serializers.ModelSerializer):
    direccion = DireccionSerializer()

    class Meta:
        model = Peleador
        fields = '__all__'
