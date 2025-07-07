from django.db import models
from apps.eventos.enums import TipoEvento, Genero, PreferenciaCombate, EstatusPago, TipoPatrocinio

# Modelo abstracto para redes sociales (opcional)
class RedesSociales(models.Model):
    youtube = models.URLField(blank=True, null=True, help_text="Enlace al canal de YouTube")
    facebook = models.URLField(blank=True, null=True, help_text="Enlace al perfil de Facebook")
    instagram = models.URLField(blank=True, null=True, help_text="Enlace al perfil de Instagram")
    twitter = models.URLField(blank=True, null=True, help_text="Enlace al perfil de Twitter")

    class Meta:
        abstract = True

# Modelo para direcciones
# Este modelo puede ser reutilizado por otros modelos que necesiten una dirección
class Direccion(models.Model):
    estado = models.CharField(max_length=100, help_text="Estado o provincia")
    ciudad = models.CharField(max_length=100, help_text="Ciudad o localidad")
    calle = models.CharField(max_length=100, help_text="Nombre de la calle")
    numero = models.CharField(max_length=10, help_text="Número exterior o interior")
    colonia = models.CharField(max_length=100, help_text="Colonia o barrio")
    codigo_postal = models.CharField(max_length=10, help_text="Código postal")

    class Meta:
        db_table = 'eventos_direccion'
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        ordering = ['estado', 'ciudad', 'colonia']

    def __str__(self):
        return f"{self.calle} #{self.numero}, {self.colonia}, {self.ciudad}, {self.estado}"

# Modelo principal para eventos
# Este modelo representa un evento deportivo, como un torneo o seminario
class Evento(models.Model):
    nombre = models.CharField(max_length=255, help_text="Nombre del evento")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción general del evento")
    tipo_evento = models.CharField(max_length=20, choices=TipoEvento.CHOICES, default=TipoEvento.TORNEO, help_text="Tipo de evento")
    video_promocional_url = models.URLField(blank=True, null=True, help_text="Enlace a video promocional")
    fecha_evento = models.DateField(help_text="Fecha principal del evento")
    hora_inicio = models.TimeField(help_text="Hora de inicio del evento")
    hora_fin = models.TimeField(blank=True, null=True, help_text="Hora de finalización del evento (opcional)")
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, related_name='eventos', help_text="Ubicación donde se llevará a cabo el evento")
    fecha_pesaje = models.DateField(blank=True, null=True, help_text="Fecha del pesaje (opcional)")
    hora_pesaje = models.TimeField(blank=True, null=True, help_text="Hora del pesaje (opcional)")
    esta_activo = models.BooleanField(default=True, help_text="Define si el evento está publicado")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'eventos_evento'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha_evento']

    def __str__(self):
        return self.nombre

# Modelo para peleadores
# Este modelo representa a los atletas que participan en los eventos
class Peleador(RedesSociales,models.Model):
    # Datos personales
    nombre = models.CharField(max_length=50, help_text="Nombre del peleador")
    apellido = models.CharField(max_length=50, help_text="Apellido del peleador")
    email = models.EmailField(unique=True, help_text="Correo electrónico de contacto")
    telefono = models.CharField(max_length=20, help_text="Número telefónico de contacto")
    nacionalidad = models.CharField(max_length=50, help_text="País de nacionalidad")
    direccion = models.OneToOneField(Direccion, on_delete=models.CASCADE, help_text="Dirección actual del peleador")
    fecha_nacimiento = models.DateField(help_text="Fecha de nacimiento")
    genero = models.CharField(max_length=1, choices=Genero.CHOICES, help_text="Género del peleador")

    evento= models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='peleadores', help_text="Evento al que está inscrito el peleador")
    
    # Datos deportivos
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, help_text="Peso en kilogramos")
    preferencia_combate = models.CharField(max_length=20, choices=PreferenciaCombate.CHOICES, help_text="Tipo de combate preferido")
    cinta = models.CharField(max_length=50, help_text="Grado de cinta actual")
    equipo = models.CharField(max_length=100, help_text="Academia o equipo al que pertenece")
    foto = models.ImageField(upload_to='peleadores/', blank=True, null=True, help_text="Foto de perfil del peleador")

    categoria = models.CharField(max_length=50, help_text="Categoría competitiva (ej. Lightweight, Heavyweight)")
    racha = models.CharField(max_length=100, blank=True, null=True, help_text="Historial de combates (ej. 3W-1L)")
    firma_contrato = models.BooleanField(default=False, help_text="¿Tiene contrato firmado con la organización?")
    es_estelar = models.BooleanField(default=False, help_text="¿Es un peleador estelar?")
    confirmado = models.BooleanField(default=False, help_text="¿Ha sido aceptado oficialmente por la organización?")

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'eventos_peleador'
        verbose_name = 'Peleador'
        verbose_name_plural = 'Peleadores'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Modelo para patrocinadores
# Este modelo representa a las empresas o marcas que patrocinan eventos
class Patrocinador(RedesSociales,models.Model):
    # Datos personales del representante
    nombre_completo = models.CharField(max_length=150, help_text="Nombre completo del representante")
    puesto = models.CharField(max_length=100, help_text="Puesto o cargo dentro de la empresa")
    email = models.EmailField(help_text="Correo electrónico de contacto")
    telefono = models.CharField(max_length=20, help_text="Número telefónico de contacto")

    # Datos de la empresa o marca
    nombre_marca = models.CharField(max_length=150, help_text="Nombre de la empresa o marca")
    giro = models.CharField(max_length=100, help_text="Sector o giro del negocio")
    estado = models.CharField(max_length=100, help_text="Estado donde opera la marca")
    ciudad = models.CharField(max_length=100, help_text="Ciudad donde opera la marca")
    sitio_web = models.URLField(blank=True, null=True, help_text="Sitio web oficial de la marca (opcional)")

    tipo_patrocinio = models.CharField(max_length=20, choices=TipoPatrocinio.CHOICES, help_text="Tipo de patrocinio ofrecido")
    ha_patrocinado_antes = models.BooleanField(default=False, help_text="¿Ha patrocinado eventos anteriormente?")
    mensaje = models.TextField(blank=True, null=True, help_text="Comentarios u observaciones adicionales")
    logo = models.ImageField(upload_to='patrocinadores/', blank=True, null=True, help_text="Logo de la marca patrocinadora")
    confirmado = models.BooleanField(default=False, help_text="¿El patrocinio ha sido confirmado por la organización?")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'eventos_patrocinador'
        verbose_name = 'Patrocinador'
        verbose_name_plural = 'Patrocinadores'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre_completo} - {self.nombre_marca}"

# Modelo para tipos de boletos
# Este modelo define los diferentes tipos de boletos disponibles para un evento
class TipoBoleto(models.Model):
    nombre = models.CharField(max_length=100, help_text="Nombre identificador del tipo de boleto")
    descripcion = models.TextField(blank=True, help_text="Descripción general del boleto")
    precio = models.DecimalField(max_digits=8, decimal_places=2, help_text="Precio en pesos mexicanos")
    incluye = models.TextField(help_text="Lista de beneficios o accesos incluidos", blank=True)
    cupo = models.IntegerField(null=True, blank=True, help_text="Cantidad máxima disponible (opcional)")
    orden = models.IntegerField(default=0, help_text="Orden de aparición en el frontend")
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='tipos_boleto', help_text="Evento al que pertenece este tipo de boleto")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'eventos_tipo_boleto'
        verbose_name = 'Tipo de boleto'
        verbose_name_plural = 'Tipos de boletos'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

# Modelo para compradores
# Este modelo representa a las personas que compran boletos para los eventos
class Comprador(models.Model):
    nombre = models.CharField(max_length=100, help_text="Nombre del comprador")
    apellido = models.CharField(max_length=100, help_text="Apellido del comprador")
    email = models.EmailField(unique=True, help_text="Correo electrónico de contacto")
    telefono = models.CharField(max_length=20, blank=True, help_text="Número telefónico (opcional)")
    direccion = models.ForeignKey(Direccion, on_delete=models.PROTECT, related_name='compradores', help_text="Dirección actual del comprador")
    es_asistente = models.BooleanField(default=True, help_text="¿El comprador también asistirá al evento?")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'eventos_comprador'
        verbose_name = 'Comprador'
        verbose_name_plural = 'Compradores'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Modelo para compras de boletos
# Este modelo registra las transacciones de compra de boletos para eventos
class CompraBoleto(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='compras', help_text="Evento al que corresponde la compra")
    tipo_boleto = models.ForeignKey(TipoBoleto, on_delete=models.CASCADE, related_name='compras', help_text="Tipo de boleto adquirido")
    peleador = models.ForeignKey(Peleador, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras', help_text="Peleador asociado (opcional)")
    comprador = models.ForeignKey(Comprador, on_delete=models.CASCADE, related_name='compras', help_text="Comprador que realiza la transacción")
    cantidad = models.PositiveIntegerField(default=1, help_text="Número de boletos comprados")
    fecha_compra = models.DateTimeField(auto_now_add=True)
    status_pago = models.CharField(max_length=20, choices=EstatusPago.CHOICES, default=EstatusPago.PENDIENTE, help_text="Estado del pago")
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto total pagado")
    referencia_pago = models.CharField(max_length=100, blank=True, null=True, help_text="ID de transacción en Conekta (opcional)")
    terminos_aceptados = models.BooleanField(default=False, help_text="¿Se aceptaron los términos y condiciones?")

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'eventos_compra_boleto'
        verbose_name = 'Compra de boleto'
        verbose_name_plural = 'Compras de boletos'
        ordering = ['-fecha_compra']

    def __str__(self):
        return f"Compra de {self.cantidad} boleto(s) para {self.evento.nombre} por {self.comprador.nombre} {self.comprador.apellido}"


class TransaccionConekta(models.Model):
    compra = models.OneToOneField('CompraBoleto',on_delete=models.CASCADE,related_name='transaccion_conekta',help_text="Compra asociada a esta transacción")
    id_conekta = models.CharField(max_length=100,unique=True,help_text="ID de la transacción en Conekta")
    estatus = models.CharField(max_length=50,help_text="Estatus actual del cargo (ej. paid, failed, refunded)")
    metodo_pago = models.CharField(max_length=50,help_text="Método de pago usado (ej. card, cash, spei)")
    monto = models.DecimalField(max_digits=10,decimal_places=2,help_text="Monto procesado en la transacción")
    moneda = models.CharField(max_length=10,default='MXN',help_text="Moneda de la transacción")
    autorizado_en = models.DateTimeField(blank=True,null=True,help_text="Fecha y hora en que fue autorizado el pago")
    pagado_en = models.DateTimeField(blank=True,null=True,help_text="Fecha y hora en que fue pagado (si aplica)")
    fallido_en = models.DateTimeField(blank=True,null=True,help_text="Fecha y hora del fallo (si aplica)")
    mensaje_error = models.TextField(blank=True,null=True,help_text="Mensaje de error devuelto por Conekta (si aplica)")
    raw_data = models.JSONField(help_text="Payload completo recibido de Conekta",blank=True,null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pagos_transacciones_conekta'
        verbose_name = 'Transacción con Conekta'
        verbose_name_plural = 'Transacciones con Conekta'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"TXN {self.id_conekta} - {self.estatus}"
