import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers.CustomUserManager import CustomUserManager

GENERO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]
ROLE_CHOICES = [('admin', 'Administrador'), ('coach', 'Coach'), ('athlete', 'Atleta')]

class Persona(models.Model):
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    alias = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Nombre con el que la persona prefiere ser llamada"
    )
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    padecimientos_medicos = models.TextField(blank=True, null=True)
    telefono_personal = models.CharField(max_length=20)
    telefono_emergencia = models.CharField(max_length=20)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True,default='perfiles/default.jpg')

    # Dirección
    estado = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    colonia = models.CharField(max_length=100)
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    codigo_postal = models.CharField(max_length=10)

    # Permisos y rol general
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='athlete')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CustomUser(AbstractBaseUser, PermissionsMixin, Persona):
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    objects = CustomUserManager()

    class Meta:
        db_table = 'users_customuser'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nombre', 'apellido']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def save(self, *args, **kwargs):
        if self.role == 'admin':
            self.is_staff = True
        super().save(*args, **kwargs)

class Cliente(models.Model):
    usuario = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cliente')

    class Meta:
        db_table = 'usuarios_cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['usuario__nombre']

    def __str__(self):
        return f"Cliente: {self.usuario.nombre} {self.usuario.apellido}"

class Empleado(models.Model):
    usuario = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='empleado')
    fecha_contratacion = models.DateField()
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    certificaciones = models.TextField(blank=True, null=True, help_text="Certificaciones relevantes del empleado")
    tipo_contrato = models.CharField(max_length=50, blank=True, null=True, help_text="Ej. Tiempo completo, medio tiempo")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuarios_empleado'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['usuario__nombre']

    def __str__(self):
        return f"Empleado: {self.usuario.nombre} {self.usuario.apellido}"

class UserInvitation(models.Model):
    email = models.EmailField(unique=True, help_text="Correo electrónico del invitado")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    enviado_por = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invitaciones_enviadas',
        help_text="Admin o coach que envió la invitación"
    )

    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(
        help_text="Fecha límite para que la persona complete el registro"
    )

    fue_usado = models.BooleanField(default=False)

    medio_envio = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Correo electrónico'),
            ('whatsapp', 'WhatsApp'),
            ('ambos', 'Ambos')
        ],
        default='email',
        help_text="Medio por el cual se envió la invitación"
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Número de teléfono si se envió vía WhatsApp"
    )

    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'users_invitaciones'
        verbose_name = 'Invitación de usuario'
        verbose_name_plural = 'Invitaciones de usuarios'
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"Invitación a {self.email} ({'usada' if self.fue_usado else 'pendiente'})"

    def is_expired(self):
        return timezone.now() > self.fecha_expiracion