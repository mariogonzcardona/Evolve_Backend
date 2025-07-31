from decouple import config
from apps.email_service.tasks import send_email_in_thread
from apps.eventos.models import CompraBoleto, BoletoAsignado, TokenAsignacion
from apps.eventos.utils.qr_gen import generar_qr_personalizado as generar_qr
from decouple import config

def procesar_post_compra(compra: CompraBoleto):
    comprador = compra.comprador
    cantidad = compra.cantidad
    asistira = comprador.es_asistente
    cantidad_restante = cantidad
    frontend_url = config("FRONTEND_BASE_URL")

    # 📌 Crear o recuperar token
    token_obj, _ = TokenAsignacion.objects.get_or_create(compra=compra)
    token = str(token_obj.token)

    # 🎫 Asignar boleto directo si asistirá
    # Si el comprador asistirá y no tiene un boleto asignado, se genera un QR y se asigna el boleto.
    # Si ya tiene un boleto asignado, no se asigna otro.
    if asistira and not BoletoAsignado.objects.filter(compra=compra, email_asistente=comprador.email).exists():
        qr_url = generar_qr(compra.id, comprador.email)
        BoletoAsignado.objects.create(
            compra=compra,
            nombre_asistente=comprador.nombre,
            email_asistente=comprador.email,
            fecha_nacimiento_asistente=comprador.fecha_nacimiento,
            qr_code=qr_url,
            confirmado=True,
        )
        cantidad_restante -= 1
    else:
        qr_url = None

    # 🔗 Link de asignación si hay boletos restantes
    formulario_url = (
        f"{frontend_url}/asignar-boletos/{token}/"
        if cantidad_restante > 0 else None
    )

    context = {
        "nombre_completo": f"{comprador.nombre} {comprador.apellido}".strip(),
        "nombre_evento": compra.evento.nombre,
        "qr_url": qr_url,
        "formulario_url": formulario_url,
        # Fecha en formato largo 
        "fecha_evento": compra.evento.fecha_evento.strftime("%d de %B de %Y"),
        # Hora en formato de 12 horas
        "hora_evento": compra.evento.hora_inicio.strftime("%I:%M %p")
    }
    print(f"Contexto para el correo: {context}")

    data = {
        "email_subject": "🎟️ Tu boleto para Evolve Grappling Pro",
        "to_email": [comprador.email],
        "template": "boleto_qr",
        "correo": config("EMAIL_HOST_USER"),
        **context,
    }
    print(f"Datos para enviar el correo: {data}")
    send_email_in_thread(data)
