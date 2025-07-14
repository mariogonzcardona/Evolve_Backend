from rest_framework import serializers
from apps.eventos.models import Direccion

# Serializador global para peleadores y eventos
class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ['estado','ciudad','calle','numero','colonia','codigo_postal']