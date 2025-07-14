class UserRoles:
    SUPERADMIN = "superadmin"          # Mario - acceso técnico total
    BUSINESS_OWNER = "business_owner"  # Armando - dueño del negocio
    ADMIN = "admin"                    # Admin de filial
    COACH = "coach"                    # Instructor o entrenador
    ATHLETE = "athlete"                # Cliente o usuario final
    EGPRO = "egpro"                    # Usuario bot de EGPRO

    CHOICES = [
        (SUPERADMIN, "Superadmin"),
        (BUSINESS_OWNER, "Business Owner"),
        (ADMIN, "Admin"),
        (COACH, "Coach"),
        (ATHLETE, "Athlete"),
        (EGPRO, "EgPro"),
    ]

class UserStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

    CHOICES = [
        (ACTIVE, "Activo"),
        (INACTIVE, "Inactivo"),
        (SUSPENDED, "Suspendido"),
    ]
    
class UserGender:
    Hombre = "M"
    Mujer = "F"
    Otro = "O"
    CHOICES = [
        (Hombre, "Masculino"),
        (Mujer, "Femenino"),
        (Otro, "Otro"),
    ]

# choices=[('email', 'Correo electrónico'), ('whatsapp', 'WhatsApp'), ('ambos', 'Ambos')],
class InvitationMethod:
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    BOTH = "ambos"

    CHOICES = [
        (EMAIL, "Correo electrónico"),
        (WHATSAPP, "WhatsApp"),
        (BOTH, "Ambos"),
    ]