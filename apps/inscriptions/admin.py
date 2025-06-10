from django.contrib import admin
from .models import TipoInscripcion, MetodoPago, Membresia, PagoRecurrente

# --------------------------------------------------------
# Tipo de Inscripción
# --------------------------------------------------------
@admin.register(TipoInscripcion)
class TipoInscripcionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'esta_activo', 'fecha_creacion', 'fecha_actualizacion')
    list_filter = ('esta_activo',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('esta_activo',)
    ordering = ('id',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'esta_activo')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

# --------------------------------------------------------
# Método de Pago
# --------------------------------------------------------
@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_integracion', 'requiere_confirmacion_manual', 'esta_activo', 'fecha_creacion')
    list_filter = ('esta_activo', 'requiere_confirmacion_manual')
    search_fields = ('nombre', 'descripcion', 'codigo_integracion')
    list_editable = ('esta_activo', 'requiere_confirmacion_manual')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'esta_activo')
        }),
        ('Integración externa', {
            'fields': ('codigo_integracion', 'requiere_confirmacion_manual'),
            'description': 'Código opcional para integraciones como Stripe, PayPal, etc.'
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

# --------------------------------------------------------
# Membresía
# --------------------------------------------------------
@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    list_display = (
        'get_usuario_nombre',
        'tipo_inscripcion',
        'metodo_pago',
        'fecha_inicio',
        'fecha_fin',
        'costo_inscripcion',
        'duracion_meses',
        'esta_activa',
    )
    list_filter = ('esta_activa', 'tipo_inscripcion', 'metodo_pago')
    search_fields = ('usuario__nombre', 'usuario__apellido', 'usuario__email')
    list_editable = ('esta_activa',)
    ordering = ('-fecha_inicio',)
    date_hierarchy = 'fecha_inicio'
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Detalles de la Membresía', {
            'fields': (
                'tipo_inscripcion',
                'metodo_pago',
                'fecha_inicio',
                'fecha_fin',
                'costo_inscripcion',
                'duracion_meses',
                'esta_activa'
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    raw_id_fields = ('usuario',)
    autocomplete_fields = ['tipo_inscripcion', 'metodo_pago']

    def get_usuario_nombre(self, obj):
        return f"{obj.usuario.nombre} {obj.usuario.apellido}"
    get_usuario_nombre.short_description = 'Usuario'
    get_usuario_nombre.admin_order_field = 'usuario__nombre'

# --------------------------------------------------------
# Pago Recurrente
# --------------------------------------------------------
@admin.register(PagoRecurrente)
class PagoRecurrenteAdmin(admin.ModelAdmin):
    list_display = (
        'get_usuario_nombre',
        'frecuencia',
        'periodo_inicio',
        'monto_recurrente',
        'fecha_pago',
        'dia_limite_pago',
        'estado',
        'pagado_por'
    )
    list_filter = ('estado', 'frecuencia', 'fecha_pago')
    search_fields = (
        'membresia__usuario__nombre',
        'membresia__usuario__apellido',
        'pagado_por__nombre',
        'membresia__tipo_inscripcion__nombre'
    )
    list_editable = ('estado',)
    ordering = ('-periodo_inicio',)
    autocomplete_fields = ['membresia', 'pagado_por']
    date_hierarchy = 'periodo_inicio'

    fieldsets = (
        ('Membresía Asociada', {
            'fields': ('membresia',)
        }),
        ('Detalles del Pago', {
            'fields': (
                'frecuencia',
                'periodo_inicio',
                'monto_recurrente',
                'fecha_pago',
                'dia_limite_pago',
                'estado'
            )
        }),
        ('Información Adicional', {
            'fields': ('pagado_por', 'observaciones'),
            'classes': ('collapse',)
        }),
    )

    def get_usuario_nombre(self, obj):
        return f"{obj.membresia.usuario.nombre} {obj.membresia.usuario.apellido}"
    get_usuario_nombre.short_description = 'Usuario'
    get_usuario_nombre.admin_order_field = 'membresia__usuario__nombre'
