"""
Permissions para app reports.

Control de acceso basado en RBAC.
"""
from rest_framework.permissions import BasePermission


class CanViewReports(BasePermission):
    """
    Permiso para ver reportes.
    
    Requiere función 'reports.view_report'.
    """
    
    def has_permission(self, request, view):
        """Verificar si usuario puede ver reportes."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser siempre puede
        if request.user.is_superuser:
            return True
        
        # Verificar función RBAC
        return request.user.has_function('reports.view_report')


class CanCreateReports(BasePermission):
    """
    Permiso para crear reportes.
    
    Requiere función 'reports.create_report'.
    """
    
    def has_permission(self, request, view):
        """Verificar si usuario puede crear reportes."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser siempre puede
        if request.user.is_superuser:
            return True
        
        # Verificar función RBAC
        return request.user.has_function('reports.create_report')


class CanExportReports(BasePermission):
    """
    Permiso para exportar reportes.
    
    Requiere función 'reports.export_report'.
    CNST-007: Valida límite de exportación.
    """
    
    def has_permission(self, request, view):
        """Verificar si usuario puede exportar reportes."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser siempre puede
        if request.user.is_superuser:
            return True
        
        # Verificar función RBAC
        return request.user.has_function('reports.export_report')


class IsReportOwner(BasePermission):
    """
    Permiso para acceder solo a reportes propios.
    
    Solo el creador puede ver/modificar su reporte.
    """
    
    def has_object_permission(self, request, view, obj):
        """Verificar si usuario es dueño del reporte."""
        # Superuser siempre puede
        if request.user.is_superuser:
            return True
        
        # Verificar ownership
        return obj.created_by == request.user
