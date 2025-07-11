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
    # Cintas para adultos
    BLANCA_ADULTO = "adulto_blanca"
    AZUL = "adulto_azul"
    MORADA = "adulto_morada"
    CAFE = "adulto_cafe"
    NEGRA = "adulto_negra"

    # Cintas para niños
    BLANCA_NIÑO = "nino_blanca"
    BLANCA_AMARILLA = "nino_blanca_amarilla"
    AMARILLA = "nino_amarilla"
    AMARILLA_NARANJA = "nino_amarilla_naranja"
    NARANJA = "nino_naranja"
    NARANJA_VERDE = "nino_naranja_verde"
    VERDE = "nino_verde"

    CHOICES = [
        # Adultos
        (BLANCA_ADULTO, "Blanca"),
        (AZUL, "Azul"),
        (MORADA, "Morada"),
        (CAFE, "Café"),
        (NEGRA, "Negra"),

        # Niños
        (BLANCA_NIÑO, "Blanca (Niño)"),
        (BLANCA_AMARILLA, "Blanca-Amarilla"),
        (AMARILLA, "Amarilla"),
        (AMARILLA_NARANJA, "Amarilla-Naranja"),
        (NARANJA, "Naranja"),
        (NARANJA_VERDE, "Naranja-Verde"),
        (VERDE, "Verde"),
    ]