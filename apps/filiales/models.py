from django.db import models

class Filial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email_contacto = models.EmailField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'filiales_filial'
        verbose_name = 'Filial'
        verbose_name_plural = 'Filiales'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

