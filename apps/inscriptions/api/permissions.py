from rest_framework.permissions import BasePermission

class IsOwnerOrCoachOrAdmin(BasePermission):
    """
    Permite acceso si el objeto pertenece al usuario autenticado (cliente),
    o si quien accede es admin o coach.

    Es útil para vistas detalladas de Membresía o PagoRecurrente.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        return (
            user.role in ['admin', 'coach']
            or (hasattr(obj, 'usuario') and obj.usuario == user)
            or (hasattr(obj, 'membresia') and obj.membresia.usuario == user)
        )
