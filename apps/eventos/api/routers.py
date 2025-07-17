from rest_framework.routers import DefaultRouter
from apps.eventos.api.eventos.views import EventoViewSet
from apps.eventos.api.peleadores.views import PeleadorViewSet
from apps.eventos.api.boletos.views import TipoBoletoPublicViewSet

router = DefaultRouter()
router.register(r'eventos', EventoViewSet, basename='eventos')
router.register(r'peleadores', PeleadorViewSet, basename='peleadores')
router.register(r'tipos-boletos', TipoBoletoPublicViewSet, basename='tipos-boletos')

urlpatterns = router.urls