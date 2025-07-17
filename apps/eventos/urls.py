from django.urls import path, include
from .api.views import CrearIntentoPagoView, RegistrarCompraView
from apps.eventos.api import routers
from apps.eventos.api.eventos.views import EventoActivoAPIView
from apps.eventos.api.peleadores.views import PeleadorPublicoListView
from apps.eventos.api.patrocinadores.views import PatrocinadorPublicoListView

urlpatterns = [
    path('eventos/stripe/pago', CrearIntentoPagoView.as_view(), name='stripe-pago'),
    path('eventos/registro/compra', RegistrarCompraView.as_view(), name='registro-compra'),
    
    path('eventos/activo/', EventoActivoAPIView.as_view(), name='evento-activo'),
    path('peleadores/estelares/', PeleadorPublicoListView.as_view(), name='peleadores-estelares'),
    path('patrocinadores/', PatrocinadorPublicoListView.as_view(), name='patrocinadores'),
    path('', include(routers)),  # incluir todos los viewsets
]