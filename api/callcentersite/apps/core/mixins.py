"""
Mixins para ViewSets con filtrado automático por servicio.
"""
from .services import ServiceAccessService


class ServiceFilterMixin:
    """
    Mixin para auto-filtrar queryset por servicios del usuario.
    
    Uso en ViewSet:
        class CallRecordViewSet(ServiceFilterMixin, viewsets.ModelViewSet):
            service_field = 'servicio_800'  # Campo que contiene el servicio
            ...
    
    Características:
    - Superusuarios ven todos los registros
    - Usuarios normales solo ven registros de sus servicios
    - Si no se especifica service_field, usa 'service' por defecto
    """
    
    service_field = 'service'  # Override en subclases
    
    def get_queryset(self):
        """
        Filtrar queryset por servicios del usuario automáticamente.
        
        Returns:
            QuerySet filtrado
        """
        queryset = super().get_queryset()
        
        # Si no hay usuario autenticado, retornar vacío
        if not self.request.user or not self.request.user.is_authenticated:
            return queryset.none()
        
        # Filtrar por servicios del usuario
        return ServiceAccessService.filter_by_user_services(
            queryset,
            self.request.user,
            self.service_field
        )


class OptionalServiceFilterMixin:
    """
    Mixin que filtra por servicio solo si el usuario NO es superusuario.
    
    Útil cuando quieres que superusuarios vean todo sin filtro,
    pero usuarios normales solo sus servicios.
    """
    
    service_field = 'service'
    
    def get_queryset(self):
        """
        Filtrar queryset opcionalmente por servicios.
        
        Returns:
            QuerySet filtrado o completo (si superuser)
        """
        queryset = super().get_queryset()
        
        if not self.request.user or not self.request.user.is_authenticated:
            return queryset.none()
        
        # Superusuarios ven todo sin filtro
        if self.request.user.is_superuser:
            return queryset
        
        # Otros filtran por servicios
        return ServiceAccessService.filter_by_user_services(
            queryset,
            self.request.user,
            self.service_field
        )
