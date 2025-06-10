from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path, include
from .api.routers import router
from .api.views import *

app_name = 'users_app'

urlpatterns = [
        
    # Autenticación
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', LogoutView.as_view(), name='user-logout'),
    
    # Gestión de contraseñas
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('auth/password/change/', ChangePasswordView.as_view(), name='password-change'),
    
    # JWT Token refresh
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Invitaciones y Registro
    path('invitaciones/', UserInvitationCreateView.as_view(), name='crear-invitacion'),
    path('invitaciones/registro/', CompleteInvitationView.as_view(), name='registro-invitado'),
    
    # Incluir las URLs del router
    path('', include(router.urls)),
]