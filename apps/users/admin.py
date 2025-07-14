from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioBase, Empleado, Cliente

@admin.register(UsuarioBase)
class UsuarioBaseAdmin(UserAdmin):
    model = UsuarioBase
    list_display = ('id', 'email', 'nombre', 'apellido', 'role', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'nombre', 'apellido')
    list_filter = ('is_active', 'role', 'estado', 'ciudad')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {
            'fields': (
                'nombre', 'apellido', 'fecha_nacimiento', 'genero',
                'padecimientos_medicos', 'telefono_personal', 'telefono_emergencia',
                'foto_perfil',
                'estado', 'ciudad', 'colonia', 'calle', 'numero', 'codigo_postal'
            )
        }),
        ('Permisos', {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Fechas importantes', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'nombre', 'apellido', 'password1', 'password2',
                'role', 'is_active', 'is_staff', 'is_superuser','fecha_nacimiento'
            )
        }),
    )

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_contratacion', 'especialidad', 'salario')
    search_fields = ('usuario__nombre', 'usuario__apellido', 'especialidad')
    fields = (
        'usuario', 'filial', 'fecha_contratacion', 'especialidad', 'salario',
        'certificaciones', 'tipo_contrato', 'status'
    )

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'filial', 'status')
    search_fields = ('usuario__nombre', 'usuario__apellido', 'filial__nombre')
    list_filter = ('filial', 'status')
    fields = ('usuario', 'filial', 'status')
