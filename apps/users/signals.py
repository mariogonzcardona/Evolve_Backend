import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import UsuarioBase

@receiver(pre_save, sender=UsuarioBase)
def delete_old_profile_picture(sender, instance, **kwargs):
    if not instance.pk:
        return  # Usuario nuevo

    try:
        old_instance = UsuarioBase.objects.get(pk=instance.pk)
    except UsuarioBase.DoesNotExist:
        return

    old_file = old_instance.foto_perfil
    new_file = instance.foto_perfil

    if old_file and old_file != new_file:
        try:
            if old_file.name != 'perfiles/default.jpg' and os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except Exception:
            pass

@receiver(post_delete, sender=UsuarioBase)
def delete_profile_picture_on_delete(sender, instance, **kwargs):
    file = instance.foto_perfil
    if file:
        try:
            if file.name != 'perfiles/default.jpg' and os.path.isfile(file.path):
                os.remove(file.path)
        except Exception:
            pass
