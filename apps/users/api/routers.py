from django.urls import path, include
from .admin.router import router as admin_router
from .coach.router import router as coach_router
from .cliente.router import router as cliente_router

urlpatterns = [
    # path('admins/', include(admin_router.urls)),
    # path('coaches/', include(coach_router.urls)),
    # path('clientes/', include(cliente_router.urls)),
]
