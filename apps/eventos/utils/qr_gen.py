from uuid import uuid4
import io
import json
from PIL import Image, ImageDraw, ImageOps
import qrcode
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def generar_qr_personalizado(token_obj,nombre_asistente,email_asistente):
    # Datos del QR
    # qr_data = f"compra:{compra_id}|email:{email}|uuid:{uuid.uuid4()}"
    filename_uid = uuid4().hex
    qr_info = {
        "token": str(token_obj.token),
        "nombre_asistente": nombre_asistente,
        "email_asistente": email_asistente,
        "compra_id": token_obj.compra.id,
    }
    qr_data = json.dumps(qr_info, separators=(',', ':'))
    # Crear QR en color sólido
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Imagen QR con color personalizado
    qr_img = qr.make_image(fill_color="#17142A", back_color="white").convert("RGB")
    size = qr_img.size

    # Máscara con bordes redondeados
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, size[0], size[1]], radius=50, fill=255)

    # Aplicar máscara
    qr_img = ImageOps.fit(qr_img, size)
    qr_img.putalpha(mask)

    # Convertir a RGB con fondo blanco
    final_img = Image.new("RGB", size, (255, 255, 255))
    final_img.paste(qr_img, mask=qr_img.split()[3])

    # Guardar en memoria
    in_mem_file = io.BytesIO()
    final_img.save(in_mem_file, format="PNG")
    in_mem_file.seek(0)

    # Nombre de archivo en el bucket
    filename = f"media/boletos_qr/qr_{filename_uid}_{token_obj.token}.png"

    # Usar default_storage (django-storages → S3)
    file_content = ContentFile(in_mem_file.read())
    default_storage.save(filename, file_content)

    # Retornar URL pública desde default_storage
    return default_storage.url(filename)
