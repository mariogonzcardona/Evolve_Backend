from rest_framework import serializers
from apps.eventos.models import TipoBoleto, TipoBoletoBeneficio

class BeneficioPorTipoSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    activo = serializers.BooleanField()

class TipoBoletoPublicSerializer(serializers.ModelSerializer):
    beneficios = serializers.SerializerMethodField()

    class Meta:
        model = TipoBoleto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'beneficios', 'orden',"destacado","mensaje_promocional"]

    def get_beneficios(self, obj):
        detalles = TipoBoletoBeneficio.objects.filter(tipo_boleto=obj).select_related('beneficio').order_by('id')
        return [
            {"nombre": detalle.beneficio.nombre,"activo": detalle.activo} for detalle in detalles
        ]

class BoletosEventoActivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoBoleto
        fields = ['id', 'nombre','precio']