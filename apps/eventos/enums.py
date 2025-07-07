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
    HOMBRE = "M"
    MUJER = "F"

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