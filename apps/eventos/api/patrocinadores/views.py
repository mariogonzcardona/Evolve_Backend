import boto3
import uuid
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from apps.eventos.models import Patrocinador,TipoPatrocinio
from apps.eventos.api.patrocinadores.serializers import PatrocinadorPublicSerializer,TipoPatrociniosSerializer,PatrocinadorSerializer
from apps.users.api.permissions import HasAnyRole
from apps.users.enums import UserRoles
from rest_framework.generics import ListAPIView,CreateAPIView
from botocore.exceptions import BotoCoreError, ClientError
from decouple import config
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from urllib.parse import urlparse
from copy import deepcopy
from apps.eventos.utils.s3_copy import mover_archivo_s3
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.exceptions import Throttled

class TiposPatrocinioListView(ListAPIView):
    """Vista publica para obtener los tipos de patrocinio activos."""
    queryset=TipoPatrocinio.objects.filter(activo=True)
    serializer_class= TipoPatrociniosSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]

class PatrocinadorPublicoListView(ListAPIView):
    """
    Vista pública de EGPro para mostrar patrocinadores confirmados.
    """
    queryset = Patrocinador.objects.filter(activo=True, confirmado=True).order_by('id')
    serializer_class = PatrocinadorPublicSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]

@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=False), name='post')
class CrearPatrocinadorView(CreateAPIView):
    queryset = Patrocinador.objects.all()
    serializer_class = PatrocinadorSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]
    parser_classes = [
        MultiPartParser,
        FormParser
    ]

    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            raise Throttled(detail="Has realizado demasiados registros. Intenta de nuevo más tarde.")
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Guardado automático en S3 usando el ImageField del modelo
        patrocinador = serializer.save()

        return Response({"id": patrocinador.id}, status=status.HTTP_201_CREATED)
    
# class LogoUploadView(APIView):
#     parser_classes = [MultiPartParser, FormParser]

#     @swagger_auto_schema(
#         operation_description="Subir logo a S3 (versión final, sin carpeta temporal)",
#         manual_parameters=[
#             openapi.Parameter(
#                 name="archivo",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_FILE,
#                 required=True,
#                 description="Archivo de imagen (JPG, PNG)",
#             )
#         ],
#         responses={201: openapi.Response("URL del archivo subido")},
#     )
#     def post(self, request):
#         serializer = LogoUploadSerializer(data=request.data)
#         if serializer.is_valid():
#             archivo = serializer.validated_data["archivo"]

#             s3 = boto3.client(
#                 "s3",
#                 aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
#                 aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
#                 region_name=config("AWS_S3_REGION_NAME"),
#             )

#             bucket = config("AWS_STORAGE_BUCKET_NAME")
#             filename = f"patrocinadores/logos/{uuid.uuid4()}_{archivo.name}"
#             region = config("AWS_S3_REGION_NAME")
#             try:
#                 s3.upload_fileobj(
#                     archivo,
#                     bucket,
#                     filename,
#                     ExtraArgs={"ContentType": archivo.content_type}
#                 )

#                 s3_url = f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"
#                 # Agregar print con emojis
#                 print("🚀 Archivo subido exitosamente a S3!")
#                 print(f"📂 URL del archivo: {s3_url}")
#                 return Response({"url": s3_url}, status=status.HTTP_201_CREATED)

#             except (BotoCoreError, ClientError) as e:
#                 return Response(
#                     {"error": "No se pudo subir el archivo", "detalle": str(e)},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)