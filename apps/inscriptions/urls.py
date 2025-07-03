from django.urls import path, include
from .api.routers import router

app_name = 'inscripciones'

urlpatterns = [
    # Incluir todas las URLs del router
    # path('', include((router.urls, 'inscripciones'))),
]  