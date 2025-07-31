from PIL import Image, ImageDraw, ImageOps
import uuid
import io
import boto3
import qrcode

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

    # Crear máscara con bordes redondeados
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, size[0], size[1]], radius=50, fill=255)

    # Aplicar máscara
    qr_img = ImageOps.fit(qr_img, size)
    qr_img.putalpha(mask)

    # Convertir a RGB con fondo blanco
    final_img = Image.new("RGB", size, (255, 255, 255))
    final_img.paste(qr_img, mask=qr_img.split()[3])

    # Subir a S3
    in_mem_file = io.BytesIO()
    final_img.save(in_mem_file, format="PNG")
    in_mem_file.seek(0)

    s3 = boto3.client("s3")
    bucket = "evolve-backend"
    object_key = f"boletos_qr/qr_{compra_id}_{uuid.uuid4().hex[:6]}.png"
    s3.upload_fileobj(
        in_mem_file,
        bucket,
        object_key,
        ExtraArgs={"ContentType": "image/png"}
    )

    return f"https://{bucket}.s3.amazonaws.com/{object_key}"
