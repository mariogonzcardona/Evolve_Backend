from django.contrib import admin
from .models import (
    Direccion,
    Evento,
    Peleador,
    Patrocinador,
    TipoBoleto,
    Comprador,
    CompraBoleto,
    Nacionalidad,
    TipoPatrocinio,
    TipoBoletoBeneficio,
    Beneficio,
    TransaccionStripe,
    AsignacionToken,
    AsignacionBoletos
)

@admin.register(Nacionalidad)
class NacionalidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'codigo_iso','activo')
    search_fields = ('nombre', 'codigo_iso')
    ordering = ('nombre',)
    list_filter = ('nombre',)
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'codigo_iso', 'activo')
        }),
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('id','calle', 'numero', 'colonia', 'ciudad', 'estado', 'codigo_postal')
    search_fields = ('calle', 'colonia', 'ciudad', 'estado', 'codigo_postal')
    list_filter = ('estado', 'ciudad')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('id','nombre', 'tipo_evento', 'fecha_evento', 'hora_inicio', 'esta_activo')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('tipo_evento', 'esta_activo', 'fecha_evento')
    date_hierarchy = 'fecha_evento'
    ordering = ('-fecha_evento',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

@admin.register(Peleador)
class PeleadorAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo','edad', 'preferencia_combate', 'cinta', 'firma_contrato','es_estelar','confirmado','activo')
    search_fields = ('nombre', 'apellido', 'email', 'equipo', 'cinta')
    list_filter = ('genero', 'preferencia_combate', 'evento', 'cinta', 'confirmado')
    ordering = ('apellido', 'nombre')
    
    # Nombre completo
    def nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"
    nombre_completo.short_description = 'Nombre Completo'
    
    def edad(self, obj):
        from datetime import date
        if obj.fecha_nacimiento:
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - ((today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day))
        return None
    
    fieldsets = (
        ('Información personal', {
            # Nombre Completo
            'fields': (
                'nombre', 
                'apellido',
                'email',
                'telefono', 
                'nacionalidad',
                'direccion',
                'fecha_nacimiento', 
                'genero',
                'activo'
            )
        }),
        ('Detalles de combate', {
            'fields': (
                'evento',
                'peso_kg',
                'preferencia_combate',
                'cinta',
                'equipo',
                'foto',
                'trayectoria',
                'categoria',
                'racha',
                'firma_contrato',
                'es_estelar',
                'confirmado',
            )
        }),
        ('Redes sociales', {
            'fields': (
                'youtube',
                'facebook',
                'instagram',
                'twitter',
            )}),
        ('Fechas automaticas', {'fields': ('fecha_creacion','fecha_actualizacion',)}),
    )
    # No editables
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

@admin.register(TipoPatrocinio)
class TipoPatrocinioAdmin(admin.ModelAdmin):
    list_display = ('id', 'clave', 'descripcion', 'activo')
    search_fields = ('clave', 'descripcion')
    list_filter = ('activo',)
    ordering = ('id',)

@admin.register(Patrocinador)
class PatrocinadorAdmin(admin.ModelAdmin):
    list_display = ('nombre_marca', 'nombre_completo','email','telefono','confirmado','activo')
    search_fields = ('nombre_completo', 'nombre_marca', 'email', 'giro')
    list_filter = ('tipos_patrocinio', 'estado', 'ciudad', 'confirmado')
    ordering = ('-fecha_creacion',)
    filter_horizontal = ('tipos_patrocinio',)
    # def get_tipos_patrocinio(self, obj):
    #     return ", ".join([tp.descripcion for tp in obj.tipos_patrocinio.all()])
    # get_tipos_patrocinio.short_description = 'Tipos de patrocinio'

    fieldsets = (
        ('Representante', {
            'fields': (
                'nombre_completo', 
                'puesto',
                'email',
                'telefono', 
            )
        }),
        ('Datos de Empresa', {
            'fields': (
                'nombre_marca',
                'giro',
                'estado',
                'ciudad',
                'sitio_web',
                'activo',
                'confirmado',
            )
        }),
        ('Interes', {
            'fields': (
                'tipos_patrocinio',
                'ha_patrocinado_antes',
                'mensaje',
                'logo',
            )
        }),
        ('Redes sociales', {
            'fields': (
                'youtube',
                'facebook',
                'instagram',
                'twitter',
            )}),
        ('Fechas automáticas', {'fields': ('fecha_creacion','fecha_actualizacion',)}),
    )

    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

# Inline para gestionar beneficios por tipo de boleto
class TipoBoletoBeneficioInline(admin.TabularInline):
    model = TipoBoletoBeneficio
    extra = 0

# Admin para TipoBoleto (ya con beneficios integrados)
@admin.register(TipoBoleto)
class TipoBoletoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'evento', 'precio', 'cupo', 'orden', 'activo')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('evento', 'activo')
    ordering = ('orden', 'nombre')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    inlines = [TipoBoletoBeneficioInline]

    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'evento')
        }),
        ('Detalles del boleto', {
            'fields': ('precio', 'cupo', 'orden', 'activo','destacado','mensaje_promocional')
        }),
        ('Fechas automáticas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )

# Admin para Beneficio (catálogo)
@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    ordering = ('nombre',)

# (Opcional) Admin directo para ver relaciones (solo si lo necesitas aparte)
@admin.register(TipoBoletoBeneficio)
class TipoBoletoBeneficioAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_boleto', 'beneficio', 'activo')
    list_filter = ('tipo_boleto', 'activo')
    search_fields = ('tipo_boleto__nombre', 'beneficio__nombre')

@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ('id','nombre_completo', 'email', 'es_asistente')
    search_fields = ('nombre', 'apellido', 'email')
    list_filter = ('es_asistente',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"
    nombre_completo.short_description = 'Nombre Completo'


@admin.register(CompraBoleto)
class CompraBoletoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "evento", "tipo_boleto", "comprador", "cantidad",
        "status_pago", "total_pagado", "fecha_compra"
    )
    list_filter = ("evento", "status_pago", "tipo_boleto")
    search_fields = ("comprador__nombre", "comprador__apellido", "evento__nombre")
    readonly_fields = ("fecha_compra", "fecha_creacion", "fecha_actualizacion")
    ordering = ("-fecha_compra",)
    date_hierarchy = "fecha_compra"

@admin.register(TransaccionStripe)
class TransaccionStripeAdmin(admin.ModelAdmin):
    list_display = (
        "payment_intent_id", "compra", "estatus", "metodo_pago", 
        "monto", "moneda", "pagado_en", "cancelado_en"
    )
    search_fields = ("payment_intent_id", "compra__comprador__email", "compra__comprador__nombre")
    list_filter = ("estatus", "metodo_pago", "moneda")
    readonly_fields = ("raw_data", "fecha_creacion")
    ordering = ("-fecha_creacion",)

@admin.register(AsignacionToken)
class AsignacionTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "compra__id","token", "usado", "fecha_creacion")
    search_fields = ("compra__comprador__email", "token")
    list_filter = ("usado",)
    readonly_fields = ("fecha_creacion",)
    ordering = ("-fecha_creacion",)

@admin.register(AsignacionBoletos)
class AsignacionBoletosAdmin(admin.ModelAdmin):
    list_display = ("id", "compra__id", "nombre_asistente", "confirmado")
    search_fields = ("compra__comprador__email", "nombre_asistente")
    list_filter = ("confirmado",)