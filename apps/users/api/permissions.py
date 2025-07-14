from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.enums import UserRoles


class HasAnyRole(BasePermission):
    """
    Permite acceso a usuarios autenticados con alguno de los roles permitidos.

    Esta versión permite definir los roles permitidos en la vista usando: `allowed_roles = [...]`
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(view, 'allowed_roles') and
            request.user.role in view.allowed_roles
        )

class IsSelfOrBusinessRole(BasePermission):
    """
    Permite acceso si el usuario es el mismo que el objeto,
    o si tiene un rol operativo en el negocio.
    Excluye superadmin.
    """
    business_roles = [
        UserRoles.BUSINESS_OWNER,
        UserRoles.ADMIN,
        UserRoles.COACH,
    ]

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            obj == request.user or
            request.user.role in self.business_roles
        )

class IsBusinessRoleOrReadOnly(BasePermission):
    """
    Permite lectura a usuarios autenticados,
    y escritura solo a roles del negocio (excluye superadmin).
    El rol athlete también puede acceder a datos públicos si están autenticados.
    """
    business_roles = [
        UserRoles.BUSINESS_OWNER,
        UserRoles.ADMIN,
        UserRoles.COACH,
    ]

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in self.business_roles
        )

class IsSelfOnly(BasePermission):
    """
    Permite modificar solo su propio objeto.
    Ideal para vistas específicas de atletas.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj == request.user
