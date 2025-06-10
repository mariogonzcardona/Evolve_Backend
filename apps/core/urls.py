from django.urls import path
from .views import *

urlpatterns = [
    # Paths del Core
    path('',home,name='home'),
]