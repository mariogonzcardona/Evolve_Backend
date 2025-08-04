import uuid
import io
from PIL import Image, ImageDraw, ImageOps
import qrcode
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def generar_qr_personalizado(compra_id, email):
    # Datos del QR
    qr_data = f"compra:{compra_id}|email:{email}|uuid:{uuid.uuid4()}"

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
    qr_img = qr.make_image(fill_color="#2f6bc5", back_color="white").convert("RGB")
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
    filename = f"boletos_qr/qr_{compra_id}_{uuid.uuid4().hex[:6]}.png"

    # Usar default_storage (django-storages → S3)
    file_content = ContentFile(in_mem_file.read())
    default_storage.save(filename, file_content)

    # Retornar URL pública desde default_storage
    return default_storage.url(filename)
