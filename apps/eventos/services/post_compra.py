from decouple import config
from apps.email_service.tasks import send_email_in_thread
from apps.eventos.models import CompraBoleto, AsignacionBoletos, AsignacionToken
from apps.eventos.utils.qr_gen import generar_qr_personalizado
from decouple import config

def procesar_post_compra(compra: CompraBoleto):
    comprador = compra.comprador
    cantidad = compra.cantidad
    asistira = comprador.es_asistente
    cantidad_restante = cantidad
    frontend_url = config("FRONTEND_BASE_URL")

    # 📌 Crear o recuperar token
    token_obj, _ = AsignacionToken.objects.get_or_create(compra=compra)
    token = str(token_obj.token)

    # 🎫 Asignar boleto directo si asistirá
    # Si el comprador asistirá y no tiene un boleto asignado, se genera un QR y se asigna el boleto.
    # Si ya tiene un boleto asignado, no se asigna otro.
    qr_url=None
    if asistira and not AsignacionBoletos.objects.filter(compra=compra, email_asistente=comprador.email).exists():
        # qr_url = generar_qr_personalizado(compra.id, comprador.email)
        qr_url = generar_qr_personalizado(token_obj,comprador.nombre,comprador.email)
        AsignacionBoletos.objects.create(
            compra=compra,
            nombre_asistente=comprador.nombre,
            email_asistente=comprador.email,
            fecha_nacimiento_asistente=comprador.fecha_nacimiento,
            qr_code=str(qr_url) if qr_url else None,
            token_formulario=token,
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
        "fecha_evento": compra.evento.fecha_evento.strftime("%d de %B de %Y"),
        "hora_evento": compra.evento.hora_inicio.strftime("%I:%M %p"),
        "direccion_evento": compra.evento.direccion,
        "qr_url": qr_url,
        "formulario_url": str(formulario_url) if formulario_url else None,
        "cantidad_boletos": cantidad,
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
