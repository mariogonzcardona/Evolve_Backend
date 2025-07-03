from django.contrib import admin
from apps.filiales.models import Filial

@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa', 'telefono', 'email_contacto']
    search_fields = ['nombre', 'email_contacto']
    list_filter = ['activa']
    ordering = ['nombre']