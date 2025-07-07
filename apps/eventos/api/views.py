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
            amount = request.data.get("amount")
            currency = request.data.get("currency", "mxn")

            intent = stripe.PaymentIntent.create(
                amount=int(amount),  # en centavos
                currency=currency,
                metadata={"integration_check": "accept_a_payment"},
            )

            return Response({"clientSecret": intent.client_secret})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegistrarCompraView(APIView):
    # Permitir cualqueir origen
    
    permission_classes=[AllowAny]
    def post(self, request):
        try:
            datos = request.data
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