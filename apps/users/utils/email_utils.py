from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from decouple import config

def send_password_reset_email(user, request, tipo='reset'):
    print(f"Enviando correo a {user.email}")

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_url = f"{request.scheme}://{request.get_host()}/reset-password/?uidb64={uid}&token={token}"

    context = {
        'user': user,
        'reset_url': reset_url,
    }

    if tipo == 'welcome':
        subject = "¡Bienvenido a Evolve!"
        template_name = "emails/welcome_email.html"
        text_body = f"¡Bienvenido a Evolve! Establece tu contraseña aquí: {reset_url}"
    else:
        subject = "Recuperación de contraseña - Evolve"
        template_name = "emails/password_reset_email.html"
        text_body = f"Recupera tu contraseña aquí: {reset_url}"

    from_email = "Evolve <no-reply@evolve.com>"
    recipient_list = [user.email]

    html_body = render_to_string(template_name, context)

    email = EmailMultiAlternatives(subject, text_body, from_email, recipient_list)
    email.attach_alternative(html_body, "text/html")
    email.send()

def send_invitation_email(invitacion, request):
    print(f"Enviando invitación a {invitacion.email}")

    registro_url = f"{config('FRONTEND_BASE_URL')}/registro-cliente/{invitacion.token}"

    context = {
        'invitacion': invitacion,
        'registro_url': registro_url,
    }

    subject = "¡Te han invitado a Evolve!"
    template_name = "emails/invitation_email.html"
    text_body = f"Completa tu registro en Evolve aquí: {registro_url}"

    from_email = "Evolve <no-reply@evolve.com>"
    recipient_list = [invitacion.email]

    html_body = render_to_string(template_name, context)

    email = EmailMultiAlternatives(subject, text_body, from_email, recipient_list)
    email.attach_alternative(html_body, "text/html")
    email.send()