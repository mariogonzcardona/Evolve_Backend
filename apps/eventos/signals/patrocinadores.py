from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.eventos.models import Patrocinador
from apps.email_service.tasks import send_email_in_thread
from decouple import config

@receiver(post_save, sender=Patrocinador)
def enviar_correo_bienvenida_patrocinador(sender, instance, created, **kwargs):
    if created:
        try:
            data = {
                'email_subject': 'Gracias por registrarte como patrocinador',
                'to_email': [instance.email],
                'template': 'registro_patrocinador',  # templates/emails/registro_patrocinador.html
                'nombre': instance.nombre_completo,
                'empresa': instance.nombre_marca,
                'correo': config('EMAIL_HOST_USER')  # usado en reply_to
            }
            send_email_in_thread(data)
        except Exception as e:
            print(f"❌ Error enviando correo de bienvenida: {e}")


# Variable global temporal (puede mejorar con un middleware si crece)
_old_confirmado = {}

@receiver(pre_save, sender=Patrocinador)
def guardar_estado_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Patrocinador.objects.get(pk=instance.pk)
            _old_confirmado[instance.pk] = old.confirmado
        except Patrocinador.DoesNotExist:
            _old_confirmado[instance.pk] = None

@receiver(post_save, sender=Patrocinador)
def enviar_correo_confirmacion_patrocinador(sender, instance, created, **kwargs):
    if not created and instance.pk in _old_confirmado:
        if not _old_confirmado[instance.pk] and instance.confirmado:
            data = {
                'email_subject': 'Gracias por registrarte como patrocinador',
                'to_email': [instance.email],
                'template': 'patrocinador_confirmado',  # templates/emails/registro_patrocinador.html
                'nombre': instance.nombre_completo,
                'empresa': instance.nombre_marca,
                'correo': config('EMAIL_HOST_USER')  # usado en reply_to
            }
            send_email_in_thread(data)
        # Limpieza
        del _old_confirmado[instance.pk]