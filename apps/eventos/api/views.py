# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decouple import config
from rest_framework.permissions import AllowAny
import stripe

stripe.api_key = config("STRIPE_SECRET_KEY")

class CrearIntentoPagoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            datos = request.data

            # Validaciones mínimas
            required_fields = ["amount", "currency", "tipo_boleto", "cantidad", "email"]
            for field in required_fields:
                if not datos.get(field):
                    return Response(
                        {"error": f"El campo '{field}' es obligatorio."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            amount = int(datos["amount"])
            currency = datos.get("currency", "mxn")
            email = datos.get("email")
            tipo_boleto = datos.get("tipo_boleto")
            cantidad = datos.get("cantidad")

            # Puedes agregar más campos como metadata opcional
            metadata = {
                "email": email,
                "tipo_boleto": tipo_boleto,
                "cantidad": str(cantidad),
                "nombre": datos.get("nombre", ""),
                "apellido": datos.get("apellido", ""),
                "evento": datos.get("evento", "EvolveGP2025"),
            }

            # Crear el PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata,
            )

            return Response({
                "clientSecret": intent.client_secret,
                "paymentIntentId": intent.id  # Puedes guardarlo después
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RegistrarCompraView(APIView):
    # Permitir cualqueir origen
    
    permission_classes=[AllowAny]
    def post(self, request):
        try:
            datos = request.data
            print(datos)
            # Aquí guardarás la compra (puedes modelar esto en tu modelo CompraBoleto)
            # Ejemplo:
            # CompraBoleto.objects.create(
            #     nombre=datos["nombre"],
            #     email=datos["email"],
            #     tipo_boleto=datos["tipo_boleto"],
            #     cantidad=datos["cantidad"],
            #     ...
            # )
            return Response({"mensaje": "Compra registrada correctamente"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)