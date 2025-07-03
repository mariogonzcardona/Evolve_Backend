from rest_framework.routers import DefaultRouter
from .views import CoachViewSet

router = DefaultRouter()
router.register(r'', CoachViewSet, basename='coaches')
