from django.template.loader import render_to_string 
from django.core.mail import EmailMessage
from decouple import config
import threading

def send_email(data):
    if len(data['to_email']) >= 1:
        from_email = config('EMAIL_HOST_USER')
        html_template = 'emails/contacto.html'  # Puedes mover la plantilla a templates/email/contacto.html
        html_message = render_to_string(html_template, data)

        message = EmailMessage(
            subject=data['email_subject'],
            body=html_message,
            from_email=from_email,
            to=data['to_email'],
            reply_to=[data['correo']]  # esto permite responder directo al cliente
        )
        message.content_subtype = 'html'
        message.send()
        print('Email sent successfully')
    else:
        print('Email not sent – Missing recipient')

def send_email_in_thread(data):
    thread = threading.Thread(target=send_email, args=(data,))
    thread.start()
