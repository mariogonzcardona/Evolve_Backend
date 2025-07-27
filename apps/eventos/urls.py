from django.urls import path, include
from apps.eventos.api import routers
from apps.eventos.api.boletos.views import CrearIntentoPagoView,BoletosEventoActivoViewSet, StripeWebhookView
from apps.eventos.api.eventos.views import EventoActivoAPIView
from apps.eventos.api.peleadores.views import PeleadorPublicoListView
from apps.eventos.api.patrocinadores.views import PatrocinadorPublicoListView,LogoUploadView,TiposPatrocinioListView,CrearPatrocinadorView
from apps.eventos.api.peleadores.views import PerfilUploadView,RegistroPeleadorPublicoView, PeleadoresConfirmadosListView

urlpatterns = [
    path('eventos/activo/', EventoActivoAPIView.as_view(), name='evento-activo'),
    
    # Aqui ira el Webhook de Stripe
    path("boletos/stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path('boletos/stripe/pago', CrearIntentoPagoView.as_view(), name='stripe-pago'),
    path('boletos/activos/', BoletosEventoActivoViewSet.as_view({'get': 'list'}), name='boletos-activos'),
    
    path('peleadores/estelares/', PeleadorPublicoListView.as_view(), name='peleadores-estelares'),
    path('peleadores/activos/', PeleadoresConfirmadosListView.as_view(), name='peleadores-activos'),
    path("peleadores/registro", RegistroPeleadorPublicoView.as_view(), name="registro-peleador"),
    
    path('patrocinadores/', PatrocinadorPublicoListView.as_view(), name='patrocinadores'),
    path('patrocinadores/registro', CrearPatrocinadorView.as_view(), name='patrocinadores'),
    path('patrocinadores/beneficios', TiposPatrocinioListView.as_view(), name='patrocinadores'),
    
    path("subir-logo/", LogoUploadView.as_view(), name="subir-logo"),
    path("subir-imagen-perfil/", PerfilUploadView.as_view(), name="subir-imagen-perfil"),
    path('', include(routers)),  # incluir todos los viewsets
]