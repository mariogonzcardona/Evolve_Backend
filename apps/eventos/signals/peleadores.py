from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.eventos.models import Peleador
from apps.email_service.tasks import send_email_in_thread
from decouple import config

# 1. Correo al registrarse
@receiver(post_save, sender=Peleador)
def enviar_correo_bienvenida_peleador(sender, instance, created, **kwargs):
    if created:
        try:
            data = {
                'email_subject': 'Gracias por registrarte para Evolve Grappling Pro',
                'to_email': [instance.email],
                'template': 'registro_peleador',  # templates/emails/registro_peleador.html
                'nombre': instance.nombre,
                'apellido': instance.apellido,
                'correo': config('EMAIL_HOST_USER')  # reply_to
            }
            send_email_in_thread(data)
        except Exception as e:
            print(f"❌ Error enviando correo de bienvenida a peleador: {e}")

# 2. Variable para confirmar cambio de estado
_old_confirmado_peleador = {}

@receiver(pre_save, sender=Peleador)
def guardar_estado_anterior_peleador(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Peleador.objects.get(pk=instance.pk)
            _old_confirmado_peleador[instance.pk] = old.confirmado
        except Peleador.DoesNotExist:
            _old_confirmado_peleador[instance.pk] = None

# 3. Correo al ser confirmado
@receiver(post_save, sender=Peleador)
def enviar_correo_confirmacion_peleador(sender, instance, created, **kwargs):
    if not created and instance.pk in _old_confirmado_peleador:
        if not _old_confirmado_peleador[instance.pk] and instance.confirmado:
            try:
                data = {
                    'email_subject': '¡Estás confirmado para Evolve Grappling Pro!',
                    'to_email': [instance.email],
                    'template': 'peleador_confirmado',  # templates/emails/peleador_confirmado.html
                    'nombre': instance.nombre,
                    'apellido': instance.apellido,
                    'evento': instance.evento.nombre,
                    'fecha_evento': instance.evento.fecha_evento.strftime('%d %B %Y'),
                    'correo': config('EMAIL_HOST_USER')
                }
                send_email_in_thread(data)
            except Exception as e:
                print(f"❌ Error enviando correo de confirmación a peleador: {e}")
        del _old_confirmado_peleador[instance.pk]
