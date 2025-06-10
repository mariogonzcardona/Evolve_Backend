from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'empleados', EmpleadoListView, basename='empleados-list')