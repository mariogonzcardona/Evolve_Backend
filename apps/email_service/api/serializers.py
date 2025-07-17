from rest_framework import serializers

class ContactoSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    correo = serializers.EmailField()
    asunto = serializers.CharField(max_length=150)
    mensaje = serializers.CharField()