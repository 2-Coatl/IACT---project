"""
Permissions para control de acceso a servicios.
"""
from rest_framework import permissions
from .services import ServiceAccessService


class HasServiceAccess(permissions.BasePermission):
    """
    Permission que verifica acceso a servicio.
    
    Uso en views:
        permission_classes = [IsAuthenticated, HasServiceAccess]
        service_field = 'service'  # Campo del objeto que tiene el servicio
    
    El campo puede ser:
    - 'service': FK directa a Service
    - 'servicio_800': CharField con número
    - Custom con get_service_for_permission()
    """
    
    message = 'No tienes acceso a este servicio.'
    
    def has_permission(self, request, view):
        """
        Verificar permiso a nivel de vista.
        
        Superusuarios siempre pasan.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Permitir por defecto, verificar en has_object_permission
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Verificar permiso a nivel de objeto.
        
        Verifica si el usuario tiene acceso al servicio del objeto.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Determinar campo de servicio
        service_field = getattr(view, 'service_field', 'service')
        
        # Método custom para obtener servicio
        if hasattr(obj, 'get_service_for_permission'):
            service = obj.get_service_for_permission()
        elif hasattr(obj, service_field):
            service = getattr(obj, service_field)
        else:
            # Sin campo de servicio, permitir
            return True
        
        # Verificar acceso
        return ServiceAccessService.has_service_access(request.user, service)
