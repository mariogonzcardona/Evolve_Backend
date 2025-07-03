from uuid import uuid4
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers.UsuarioBaseManager import UsuarioBaseManager
from apps.users.enums import UserRoles, UserGender,InvitationMethod,UserStatus
from apps.filiales.models import Filial

class Persona(models.Model):
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    alias = models.CharField(max_length=50, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=UserGender.CHOICES, default=UserGender.Hombre)
    padecimientos_medicos = models.TextField(blank=True, null=True)
    telefono_personal = models.CharField(max_length=20)
    telefono_emergencia = models.CharField(max_length=20)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True, default='perfiles/default.jpg')

    # Dirección
    estado = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    colonia = models.CharField(max_length=100)
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    codigo_postal = models.CharField(max_length=10)

    # Permisos y rol general
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Solo superadmin será staff
    role = models.CharField(max_length=20, choices=UserRoles.CHOICES, default=UserRoles.ATHLETE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UsuarioBase(AbstractBaseUser, PermissionsMixin, Persona):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    objects = UsuarioBaseManager()

    class Meta:
        db_table = 'usuarios_usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nombre', 'apellido']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Cliente(models.Model):
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.CASCADE, related_name='cliente')
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20,choices=UserStatus.CHOICES,default=UserStatus.ACTIVE,help_text="Estado comercial del cliente")
    
    class Meta:
        db_table = 'usuarios_cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['usuario__nombre']

    def __str__(self):
        return f"Cliente: {self.usuario.nombre} {self.usuario.apellido}"

class Empleado(models.Model):
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.CASCADE, related_name='empleado')
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_contratacion = models.DateField()
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    certificaciones = models.TextField(blank=True, null=True)
    tipo_contrato = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20,choices=UserStatus.CHOICES,default=UserStatus.ACTIVE,help_text="Estado comercial del empleado")
    
    class Meta:
        db_table = 'usuarios_empleado'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['usuario__nombre']

    def __str__(self):
        return f"Empleado: {self.usuario.nombre} {self.usuario.apellido}"

class UserInvitation(models.Model):
    email = models.EmailField(unique=True)
    token = models.UUIDField(default=uuid4, unique=True, editable=False)

    enviado_por = models.ForeignKey(UsuarioBase,on_delete=models.SET_NULL,null=True,blank=True,related_name='invitaciones_enviadas')
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    fue_usado = models.BooleanField(default=False)
    medio_envio= models.CharField(max_length=20,choices=InvitationMethod.CHOICES,default=InvitationMethod.EMAIL)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    role = models.CharField(max_length=20, choices=UserRoles.CHOICES, default=UserRoles.ATHLETE)
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'usuarios_invitacion'
        verbose_name = 'Invitación de usuario'
        verbose_name_plural = 'Invitaciones de usuarios'
        ordering = ['-fecha_envio']

    def __str__(self):
        estado = "usada" if self.fue_usado else "pendiente"
        return f"Invitación a {self.email} ({estado})"

    def is_expired(self):
        return timezone.now() > self.fecha_expiracion
