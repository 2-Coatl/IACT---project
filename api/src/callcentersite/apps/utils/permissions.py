"""Permisos compartidos."""

from rest_framework.permissions import BasePermission


class IsStaffOrReadOnly(BasePermission):
    """Permite acceso de escritura solo a personal interno."""

    def has_permission(self, request, view):  # type: ignore[override]
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(request.user and request.user.is_staff)
