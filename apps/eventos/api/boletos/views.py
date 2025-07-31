import stripe
from rest_framework import viewsets
from apps.eventos.api.boletos.serializers import TipoBoletoPublicSerializer,BoletosEventoActivoSerializer
from apps.users.api.permissions import HasAnyRole
from apps.users.enums import UserRoles
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decouple import config
from rest_framework.permissions import AllowAny
from decimal import Decimal
from stripe.error import CardError, InvalidRequestError, AuthenticationError, APIConnectionError, StripeError
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.exceptions import Throttled
from apps.eventos.models import CompraBoleto, TransaccionStripe, Comprador, Direccion, TipoBoleto, Evento, Peleador
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from apps.eventos.services.post_compra import procesar_post_compra
from datetime import datetime

stripe.api_key = config("STRIPE_SECRET_KEY")
endpoint_secret = config("STRIPE_WEBHOOK_SECRET")

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("📩 Webhook recibido")
        payload = request.body
        print(f"📦 Payload recibido: {payload}")
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        print(f"🔐 Firma Stripe: {sig_header}")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            print(f"✅ Evento construido correctamente: {event['type']}")
        except stripe.error.SignatureVerificationError:
            print("❌ Firma inválida")
            return Response({"error": "Firma inválida"}, status=400)
        except Exception as e:
            print(f"❌ Error general construyendo evento: {e}")
            return Response({"error": str(e)}, status=400)

        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            print(f"💳 PaymentIntent exitoso recibido: {intent['id']}")

            try:
                metadata = intent.get("metadata", {})
                print(f"🧾 Metadata recibida: {metadata}")
                
                fecha_nacimiento_str = metadata.get("fecha_nacimiento", "")
                fecha_nacimiento = None
                if fecha_nacimiento_str:
                    try:
                        fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
                    except ValueError:
                        print("❌ Fecha inválida en metadata:", fecha_nacimiento_str)
                        return Response({"error": "Formato de fecha inválido. Debe ser YYYY-MM-DD."}, status=400)
                
                email = metadata.get("email")
                tipo_boleto_nombre = metadata.get("tipo_boleto")
                cantidad = int(metadata.get("cantidad", 1))
                nombre = metadata.get("nombre", "")
                apellido = metadata.get("apellido", "")
                telefono = metadata.get("telefono", "")
                id_peleador = int(metadata.get("id_peleador"))
                peleador = None
                if id_peleador:
                    try:
                        peleador = Peleador.objects.get(id=id_peleador, activo=True)
                    except Peleador.DoesNotExist:
                        print(f"⚠️ Peleador con ID {id_peleador} no encontrado o inactivo")
                print(f"📌 Datos procesados — Email: {email}, Boleto: {tipo_boleto_nombre}, Cantidad: {cantidad}")

                direccion_data = {
                    "estado": metadata.get("estado", ""),
                    "ciudad": metadata.get("ciudad", ""),
                    "calle": metadata.get("calle", ""),
                    "numero": metadata.get("numero", ""),
                    "colonia": metadata.get("colonia", ""),
                    "codigo_postal": metadata.get("codigo_postal", ""),
                }

                print(f"📦 Dirección recibida: {direccion_data}")

                if not all(direccion_data.values()):
                    print("❌ Dirección incompleta")
                    return Response({"error": "Datos de dirección incompletos"}, status=400)

                direccion = Direccion.objects.create(**direccion_data)
                print(f"🏠 Dirección creada con ID: {direccion.id}")

                tipo_boleto = TipoBoleto.objects.get(nombre=tipo_boleto_nombre)
                print(f"🎟️ Tipo de boleto encontrado: {tipo_boleto.nombre}")

                evento = tipo_boleto.evento
                print(f"📅 Evento vinculado: {evento.nombre}")
                
                asistira_str = metadata.get("esAsistente", "true")
                asistira = asistira_str.lower() == "true"

                comprador, creado = Comprador.objects.get_or_create(
                    email=email,
                    defaults={
                        "nombre": nombre,
                        "apellido": apellido,
                        "fecha_nacimiento": fecha_nacimiento,
                        "telefono": telefono,
                        "direccion": direccion,
                        "es_asistente": asistira,
                    }
                )
                if creado:
                    print(f"🙋‍♂️ Comprador creado con ID: {comprador.id}")
                else:
                    print(f"🙋‍♂️ Comprador existente usado: {comprador.id}")
                    comprador.es_asistente = asistira
                    comprador.save()

                compra = CompraBoleto.objects.create(
                    evento=evento,
                    tipo_boleto=tipo_boleto,
                    comprador=comprador,
                    cantidad=cantidad,
                    status_pago="pagado",
                    total_pagado=Decimal(intent["amount"]) / 100,
                    terminos_aceptados=True,
                    peleador=peleador,
                )
                print(f"🧾 Compra registrada con ID: {compra.id}")

                TransaccionStripe.objects.create(
                    compra=compra,
                    payment_intent_id=intent["id"],
                    client_secret=intent.get("client_secret"),
                    estatus=intent["status"],
                    metodo_pago=intent["payment_method_types"][0],
                    monto=Decimal(intent["amount"]) / 100,
                    moneda=intent["currency"].upper(),
                    pagado_en=timezone.now(),
                    raw_data=intent
                )
                print("💰 Transacción Stripe registrada exitosamente")
                try:
                    procesar_post_compra(compra)
                except Exception as e:
                    print(f"⚠️ Error post-compra: {e}")
                return Response({"mensaje": "Compra registrada vía webhook"}, status=200)

            except Exception as e:
                print(f"❌ Error procesando el intent: {e}")
                return Response({"error": str(e)}, status=400)

        print("ℹ️ Tipo de evento no manejado, ignorado")
        return Response({"mensaje": "Evento ignorado"}, status=200)


class TipoBoletoPublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TipoBoleto.objects.filter(activo=True).order_by('orden')
    serializer_class = TipoBoletoPublicSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]

class BoletosEventoActivoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TipoBoleto.objects.filter(activo=True).order_by('orden')
    serializer_class = BoletosEventoActivoSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]

@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=False), name='dispatch')
class CrearIntentoPagoView(APIView):
    
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]

    def post(self, request):
        if getattr(request, 'limited', False):
            raise Throttled(detail="Demasiadas solicitudes de pago. Intenta más tarde.")
        try:
            datos = request.data

            # Validaciones mínimas
            required_fields = ["currency", "tipo_boleto", "cantidad", "email"]
            for field in required_fields:
                if not datos.get(field):
                    return Response(
                        {"error": f"El campo '{field}' es obligatorio."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            # Aquí deberías calcular el monto basado en el tipo de boleto y cantidad
            # Por ejemplo, si tienes un modelo TipoBoleto con un campo 'precio':
            precio_unitario = TipoBoleto.objects.get(nombre=datos["tipo_boleto"]).precio
            cantidad = int(datos["cantidad"])
            amount = int(Decimal(precio_unitario) * cantidad * 100)  # Stripe espera el monto en centavos
            currency = datos.get("currency", "mxn")
            email = datos.get("email")
            tipo_boleto = datos.get("tipo_boleto")
            cantidad = datos.get("cantidad")

            # Puedes agregar más campos como metadata opcional
            metadata={
                "tipo_boleto": tipo_boleto,
                "cantidad": str(cantidad),
                "nombre": datos.get("nombre", ""),
                "apellido": datos.get("apellido", ""),
                "fecha_nacimiento": datos.get("fecha_nacimiento", ""),
                "email": email,
                "telefono": datos.get("telefono", ""),
                "estado": datos.get("estado", ""),
                "ciudad": datos.get("ciudad", ""),
                "calle": datos.get("calle", ""),
                "numero": datos.get("numero", ""),
                "colonia": datos.get("colonia", ""),
                "codigo_postal": datos.get("codigo_postal", ""),
                "evento": datos.get("evento", "EvolveGP2025"),
                "id_peleador": str(datos.get("id_peleador", "")),
                "esAsistente": str(datos.get("esAsistente", "true")).lower(),
                
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

        except CardError as e:
            return Response({"error": f"Error de tarjeta: {e.user_message}"}, status=400)
        except InvalidRequestError as e:
            return Response({"error": "Error de solicitud a Stripe. Verifica los datos."}, status=400)
        except AuthenticationError:
            return Response({"error": "Error de autenticación con Stripe."}, status=500)
        except APIConnectionError:
            return Response({"error": "Error de conexión con Stripe. Intenta más tarde."}, status=500)
        except StripeError:
            return Response({"error": "Error general de Stripe. Intenta con otra tarjeta."}, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
