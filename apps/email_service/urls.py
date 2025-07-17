from django.urls import path
from apps.email_service.api.views import ContactoCreateView

urlpatterns = [
    path('contacto/', ContactoCreateView.as_view(), name='enviar-contacto'),
]