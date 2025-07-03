from rest_framework.routers import DefaultRouter
from .views import TipoInscripcionViewSet, MetodoPagoViewSet, MembresiaViewSet, PagoRecurrenteViewSet

router = DefaultRouter()
# router.register(r'tipos', TipoInscripcionViewSet, basename='tipos-inscripcion')
# router.register(r'metodos-pago', MetodoPagoViewSet, basename='metodos-pago')
# router.register(r'membresias', MembresiaViewSet, basename='membresias')
# router.register(r'pagos', PagoRecurrenteViewSet, basename='pagos-recurrentes')