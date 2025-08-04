import boto3
import uuid
from apps.eventos.utils.s3_copy import mover_archivo_s3
from decouple import config
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from apps.eventos.models import Peleador
from apps.users.api.permissions import HasAnyRole
from apps.users.enums import UserRoles
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from botocore.exceptions import BotoCoreError, ClientError
from apps.eventos.api.peleadores.serializers import PeleadorPublicoSerializer, PeleadorRegistroSerializer,PeleadoresConfirmadosSerializer
from django.db import IntegrityError
from urllib.parse import urlparse
from copy import deepcopy
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.exceptions import Throttled

# class PeleadorViewSet(viewsets.ModelViewSet):
#     """
#     Vista para (business_owner) con CRUD completo sobre peleadores.
#     La eliminación es lógica (activo = False).
#     """
#     queryset = Peleador.objects.all()
#     serializer_class = PeleadorSerializer
#     permission_classes = [HasAnyRole]
#     allowed_roles = [UserRoles.BUSINESS_OWNER]

#     def perform_destroy(self, instance):
#         instance.activo = False
#         instance.save()

@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=False), name='post')
class RegistroPeleadorPublicoView(CreateAPIView):
    """
    Endpoint público para registrar un nuevo peleador.
    Ahora maneja la imagen `foto` directamente gracias a ImageField + django-storages.
    """
    serializer_class = PeleadorRegistroSerializer
    queryset = Peleador.objects.all()
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]
    parser_classes = [MultiPartParser, FormParser]  # Permite multipart/form-data

    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            raise Throttled(detail="Has enviado demasiadas solicitudes. Intenta de nuevo más tarde.")
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # data = request.data.copy()  # importante: copia mutable
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            peleador = serializer.save()
        except IntegrityError as e:
            if 'eventos_peleador_email_key' in str(e):
                return Response(
                    {"email": ["Este correo ya está registrado para el evento."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"detalle": "Error inesperado al registrar el peleador."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"id": peleador.id}, status=status.HTTP_201_CREATED)

class PeleadorPublicoListView(ListAPIView):
    """
    Vista de EGPro para mostrar peleadores estelares confirmados.
    """
    serializer_class = PeleadorPublicoSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]

    def get_queryset(self):
        return (
            Peleador.objects.select_related("nacionalidad")
            .filter(es_estelar=True, confirmado=True, activo=True)
            .order_by("fecha_nacimiento")[:6]
        )

# class PerfilUploadView(APIView):
#     parser_classes = [MultiPartParser, FormParser]

#     @swagger_auto_schema(
#         operation_description="Subir imagen de perfil de peleador a S3 (carpeta final)",
#         manual_parameters=[
#             openapi.Parameter(
#                 name="archivo",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_FILE,
#                 required=True,
#                 description="Archivo de imagen (JPG, PNG)",
#             )
#         ],
#         responses={201: openapi.Response("URL del archivo subido")})
#     def post(self, request):
#         serializer = PerfilUploadSerializer(data=request.data)
#         if serializer.is_valid():
#             archivo = serializer.validated_data["archivo"]

#             s3 = boto3.client(
#                 "s3",
#                 aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
#                 aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
#                 region_name=config("AWS_S3_REGION_NAME"),
#             )

#             bucket = config("AWS_STORAGE_BUCKET_NAME")
#             region = config("AWS_S3_REGION_NAME")
#             filename = f"peleadores/foto-perfil/{uuid.uuid4()}_{archivo.name}"

#             try:
#                 s3.upload_fileobj(
#                     archivo,
#                     bucket,
#                     filename,
#                     ExtraArgs={"ContentType": archivo.content_type}
#                 )
                
#                 s3_url = f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"
#                 print("🚀 Archivo subido exitosamente a S3!")
#                 print(f"📂 URL del archivo: {s3_url}")
                
#                 return Response({"url": s3_url}, status=status.HTTP_201_CREATED)

#             except (BotoCoreError, ClientError) as e:
#                 return Response(
#                     {"error": "No se pudo subir el archivo", "detalle": str(e)},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PeleadoresConfirmadosListView(ListAPIView):
    """
    Vista de EGPro para mostrar peleadores confirmados.
    """
    serializer_class = PeleadoresConfirmadosSerializer
    permission_classes = [HasAnyRole]
    allowed_roles = [UserRoles.EGPRO]

    def get_queryset(self):
        return (
            Peleador.objects.filter(confirmado=True, activo=True).order_by("nombre")
        )