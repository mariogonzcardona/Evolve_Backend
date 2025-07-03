from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path, include
from .api.routers import urlpatterns as user_api_urls
from .api.views import (
    UserLoginView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
    UserInvitationCreateView,
    CompleteInvitationView,
)

app_name = 'users_app'

urlpatterns = [

    # --- Autenticación JWT ---
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', LogoutView.as_view(), name='user-logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # --- Contraseña ---
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('auth/password/change/', ChangePasswordView.as_view(), name='password-change'),

    # --- Invitación y registro ---
    path('invitaciones/', UserInvitationCreateView.as_view(), name='crear-invitacion'),
    path('invitaciones/registro/', CompleteInvitationView.as_view(), name='registro-invitado'),

    # --- CRUD por rol ---
    path('', include(user_api_urls)),
]
