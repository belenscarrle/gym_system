from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
    """
    Permite que los administradores accedan a cualquier usuario,
    pero los usuarios normales solo a sí mismos.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.tipo == 'admin' or
            obj.id == request.user.id
        )