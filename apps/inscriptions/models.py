from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

Usuario = get_user_model()

# ----------------------------
# Tipos de inscripción
# ----------------------------
class TipoInscripcion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    esta_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inscripciones_tipo'
        verbose_name = 'Tipo de Inscripción'
        verbose_name_plural = 'Tipos de Inscripción'
        ordering = ['id']

    def __str__(self):
        return self.nombre

# ----------------------------
# Métodos de pago
# ----------------------------
class MetodoPago(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    esta_activo = models.BooleanField(default=True)
    codigo_integracion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Código para integración con servicios de pago (ej. 'stripe', 'paypal')"
    )
    requiere_confirmacion_manual = models.BooleanField(
        default=False,
        help_text="Indica si este método de pago requiere confirmación manual por parte del staff"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'inscripciones_metodo_pago'
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        ordering = ['id']

    def __str__(self):
        return self.nombre

# ----------------------------
# Membresía activa del usuario
# ----------------------------
class Membresia(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='membresias'
    )
    tipo_inscripcion = models.ForeignKey(
        TipoInscripcion,
        on_delete=models.PROTECT
    )
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    fecha_inicio = models.DateField(
        auto_now_add=False,
        help_text="Fecha en que inicia formalmente la membresía"
    )
    fecha_fin = models.DateField(blank=True, null=True)
    costo_inscripcion = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text="Costo total acordado para esta membresía"
    )
    esta_activa = models.BooleanField(default=True)
    observaciones = models.TextField(
            blank=True,
            null=True,
            help_text="Comentarios o notas sobre este pago, si aplica"
        )
    duracion_meses = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Duración planeada en meses (usado como referencia para cálculos)"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inscripciones_membresias'
        verbose_name = 'Membresía'
        verbose_name_plural = 'Membresías'
        ordering = ['-fecha_inicio']

    def clean(self):
        if self.esta_activa:
            existe_activa = Membresia.objects.filter(
                usuario=self.usuario,
                esta_activa=True
            ).exclude(pk=self.pk).exists()
            if existe_activa:
                raise ValidationError("El usuario ya tiene una membresía activa.")

    def __str__(self):
        return f"{self.usuario} - {self.tipo_inscripcion.nombre}"
    
# ----------------------------
# Pagos mensuales asociados a una membresía
# ----------------------------
class PagoRecurrente(models.Model):
    FRECUENCIA_CHOICES = [
        ('mensual', 'Mensual'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('retrasado', 'Retrasado'),
        ('cancelado', 'Cancelado'),
    ]

    membresia = models.ForeignKey(
        'Membresia',
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    frecuencia = models.CharField(
        max_length=20,
        choices=FRECUENCIA_CHOICES,
        default='mensual',
        help_text="Frecuencia con la que se realiza este pago"
    )
    periodo_inicio = models.DateField(
        help_text="Fecha de inicio del periodo que cubre este pago (ej. 2025-05-01)"
    )
    monto_recurrente = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Monto total pagado en ese periodo"
    )
    fecha_pago = models.DateField(
        help_text="Fecha real en que se realizó el pago",
        null=True,
        blank=True
    )
    dia_limite_pago = models.PositiveSmallIntegerField(
        default=5,
        help_text="Día del mes en que vence el pago (ej: día 5)"
    )
    pagado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos_realizados'
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='confirmado',
        help_text="Estado actual del pago"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text="Comentarios o notas como promociones, retrasos, acuerdos especiales, etc."
    )

    class Meta:
        db_table = 'inscripciones_pago_recurrente'
        ordering = ['-periodo_inicio']
        constraints = [
            models.UniqueConstraint(fields=['membresia', 'periodo_inicio'], name='unique_pago_por_periodo')
        ]
        verbose_name = 'Pago recurrente'
        verbose_name_plural = 'Pagos recurrentes'

    def __str__(self):
        return f"{self.membresia.usuario} - {self.periodo_inicio.strftime('%B %Y')}"
