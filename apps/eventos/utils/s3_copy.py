import boto3
from decouple import config
from botocore.exceptions import BotoCoreError, ClientError

def mover_archivo_s3(bucket, origen, destino):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
        region_name=config("AWS_S3_REGION_NAME"),
    )

    try:
        s3.copy_object(
            Bucket=bucket,
            CopySource=f"{bucket}/{origen}",
            Key=destino
        )
        s3.delete_object(Bucket=bucket, Key=origen)
        print("✔️ Copiado y eliminado correctamente.")
        return True
    except (BotoCoreError, ClientError) as e:
        print("❌ Error moviendo archivo S3:", str(e))
        return False
