"""
Permisos personalizados para apps/pipeline/.

Django REST Framework custom permissions.

Movido desde apps/core/ - FASE 2 PARTE 2.
CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

from rest_framework import permissions
# TODO PARTE 7: Mover UserServiceAccess a apps.access
from apps.access.models import UserServiceAccess


class IsCenterManager(permissions.BasePermission):
    """
    Permiso: Solo administradores de centros pueden modificar.
    
    Permite:
        - GET, HEAD, OPTIONS: Todos los usuarios autenticados
        - POST, PUT, PATCH, DELETE: Solo superusers o staff
    """
    
    message = 'Solo administradores pueden gestionar centros.'
    
    def has_permission(self, request, view):
        """Verificar permiso a nivel de vista."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_superuser or request.user.is_staff


class IsServiceManager(permissions.BasePermission):
    """Permiso: Solo administradores de servicios pueden modificar."""
    
    message = 'Solo administradores pueden gestionar servicios.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_superuser or request.user.is_staff

# ====================================================================================
# REMOVED - FASE A DT-002 (2026-01-21)
# ====================================================================================
#
# Permissions eliminadas:
#   - HasServiceAccess: Verificaba UserServiceAccess
#   - CanGrantAccess: Otorgar accesos a servicios
#   - CanRevokeAccess: Revocar accesos a servicios
#
# Razón: UserServiceAccess eliminado, reemplazado por RBAC puro
# Reemplazo: Usar RequiresFunctionPermission con functions apropiadas
# ====================================================================================


class IsActiveUser(permissions.BasePermission):
    """Permiso: Usuario está activo."""
    
    message = 'Su cuenta está inactiva.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_active
