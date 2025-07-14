class TipoEvento:
    TORNEO = "torneo"
    SEMINARIO = "seminario"
    OTRO = "otro"

    CHOICES = [
        (TORNEO, "Torneo"),
        (SEMINARIO, "Seminario"),
        (OTRO, "Otro"),
    ]

class Genero:
    HOMBRE = "H"
    MUJER = "M"

    CHOICES = [
        (HOMBRE, "Hombre"),
        (MUJER, "Mujer"),
    ]

class PreferenciaCombate:
    GI = "gi"
    NO_GI = "no_gi"
    AMBOS = "gi_y_no_gi"

    CHOICES = [
        (GI, "Gi"),
        (NO_GI, "No Gi"),
        (AMBOS, "Gi y No Gi"),
    ]

class EstatusPago:
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    CANCELADO = "cancelado"

    CHOICES = [
        (PENDIENTE, "Pendiente"),
        (PAGADO, "Pagado"),
        (CANCELADO, "Cancelado"),
    ]

class TipoPatrocinio:
    ECONOMICO = 'economico'
    DONACION = 'donacion'
    PUBLICIDAD = 'publicidad'
    STAND = 'stand'

    CHOICES = [
        (ECONOMICO, 'Patrocinio económico'),
        (DONACION, 'Donación de productos o servicios'),
        (PUBLICIDAD, 'Publicidad en redes sociales'),
        (STAND, 'Stand de marca en el evento'),
    ]

class CintaBJJ:
    BLANCA = "blanca"
    AZUL = "azul"
    MORADA = "morada"
    CAFE = "cafe"
    NEGRA = "negra"
    BLANCA_AMARILLA = "blanca_amarilla"
    AMARILLA = "amarilla"
    AMARILLA_NARANJA = "amarilla_naranja"
    NARANJA = "naranja"
    NARANJA_VERDE = "naranja_verde"
    VERDE = "verde"

    CHOICES = [
        (BLANCA, "Blanca"),
        (AZUL, "Azul"),
        (MORADA, "Morada"),
        (CAFE, "Café"),
        (NEGRA, "Negra"),
        (BLANCA_AMARILLA, "Blanca-Amarilla"),
        (AMARILLA, "Amarilla"),
        (AMARILLA_NARANJA, "Amarilla-Naranja"),
        (NARANJA, "Naranja"),
        (NARANJA_VERDE, "Naranja-Verde"),
        (VERDE, "Verde"),
    ]