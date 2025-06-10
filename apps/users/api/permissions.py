from rest_framework.permissions import BasePermission, SAFE_METHODS

# --------------------------------------------------------
# 🔐 Clase base reutilizable: HasRole
# --------------------------------------------------------
class HasRole(BasePermission):
    """
    Permite acceso solo a usuarios con un rol específico.

    Se debe heredar y definir la lista de roles permitidos en la variable 'allowed_roles'.
    """
    allowed_roles = []

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in self.allowed_roles
        )


# --------------------------------------------------------
# 🔐 Permisos específicos basados en HasRole
# --------------------------------------------------------

class IsAdminUser(HasRole):
    """Permite acceso solo a usuarios con rol 'admin'."""
    allowed_roles = ['admin']

class IsCoachUser(HasRole):
    """Permite acceso solo a usuarios con rol 'coach'."""
    allowed_roles = ['coach']

class IsAthleteUser(HasRole):
    """Permite acceso solo a usuarios con rol 'athlete'."""
    allowed_roles = ['athlete']

class IsCoachOrAdmin(HasRole):
    """Permite acceso a usuarios con rol 'coach' o 'admin'."""
    allowed_roles = ['coach', 'admin']


# --------------------------------------------------------
# 🔐 Permiso combinado: lectura libre, escritura solo admin
# --------------------------------------------------------

class IsAdminOrReadOnly(BasePermission):
    """
    Permite lectura (GET, HEAD, OPTIONS) a cualquier usuario autenticado.
    Solo los usuarios con rol 'admin' pueden crear, actualizar o eliminar.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


# --------------------------------------------------------
# 🔐 Permiso basado en el objeto accedido
# --------------------------------------------------------

class IsSelfOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin' or obj == request.user
