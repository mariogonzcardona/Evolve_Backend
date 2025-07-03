from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

schema_view = get_schema_view(
    openapi.Info(
        title="Api Evolve",
        default_version='v1',
        description="API Evolve Training Center System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="mariogonzcardona@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Paths del Core
    path("", include("apps.core.urls")),
    
    # Paths de la API
    path('api/v1/', include(('apps.users.urls', 'users'), namespace='users')),  # Incluir todas las rutas de users
    # path('api/v1/', include('apps.inscriptions.urls')), 
    
    # Paths de la API
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    urlpatterns += [
        # Swagger documentation URLs
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('swagger/api/v1/user/login/', schema_view.with_ui('swagger', cache_timeout=0), name='rest_framework_login'),
        path('swagger/api/v1/user/logout/', schema_view.with_ui('swagger', cache_timeout=0), name='rest_framework_logout'),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    