from django.urls import path
from .api.views import CrearIntentoPagoView, RegistrarCompraView

urlpatterns = [
    path("eventos/stripe/pago", CrearIntentoPagoView.as_view(), name="stripe-pago"),
    path("eventos/registro/compra", RegistrarCompraView.as_view(), name="registro-compra"),
]