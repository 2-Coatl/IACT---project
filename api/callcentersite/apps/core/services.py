"""
Service para control de acceso a servicios 800.

Gestiona qué servicios puede ver/gestionar cada usuario.
"""
from typing import Optional
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q
from .models import Service, UserServiceAccess

User = get_user_model()


class ServiceAccessService:
    """
    Service para gestión de accesos a servicios.
    
    Proporciona métodos para:
    - Obtener servicios de un usuario
    - Verificar acceso a servicio
    - Filtrar queries por servicios permitidos
    - Otorgar/revocar accesos
    """
    
    @staticmethod
    def get_user_services(user: User) -> QuerySet:
        """
        Obtener servicios accesibles por usuario.
        
        Superusuarios ven todos los servicios activos.
        Usuarios normales solo ven servicios asignados.
        
        Args:
            user: Usuario
            
        Returns:
            QuerySet de Service
        """
        return UserServiceAccess.get_user_services(user)
    
    @staticmethod
    def has_service_access(user: User, service) -> bool:
        """
        Verificar si usuario tiene acceso a un servicio.
        
        Args:
            user: Usuario
            service: Instancia de Service o ID
            
        Returns:
            bool: True si tiene acceso
        """
        return UserServiceAccess.has_service_access(user, service)
    
    @staticmethod
    def filter_by_user_services(queryset: QuerySet, user: User, service_field: str = 'servicio_800') -> QuerySet:
        """
        Filtrar QuerySet por servicios permitidos al usuario.
        
        Útil para filtrar CallRecord, Reports, etc por servicio.
        
        Args:
            queryset: QuerySet a filtrar
            user: Usuario
            service_field: Nombre del campo que contiene el servicio
                          Ej: 'servicio_800', 'service', 'service__numero_800'
            
        Returns:
            QuerySet filtrado
            
        Examples:
            >>> # Filtrar CallRecords por servicios del usuario
            >>> calls = CallRecord.objects.all()
            >>> filtered = ServiceAccessService.filter_by_user_services(
            ...     calls, request.user, 'servicio_800'
            ... )
            
            >>> # Con relación FK
            >>> reports = Report.objects.all()
            >>> filtered = ServiceAccessService.filter_by_user_services(
            ...     reports, request.user, 'service__numero_800'
            ... )
        """
        if user.is_superuser:
            # Superusuarios ven todo
            return queryset
        
        # Obtener servicios permitidos
        user_services = ServiceAccessService.get_user_services(user)
        
        if not user_services.exists():
            # Sin servicios asignados = sin datos
            return queryset.none()
        
        # Extraer números de servicio
        service_numbers = user_services.values_list('numero_800', flat=True)
        
        # Filtrar por servicio
        filter_kwargs = {f'{service_field}__in': service_numbers}
        return queryset.filter(**filter_kwargs)
    
    @staticmethod
    def grant_service_access(
        user: User,
        service,
        granted_by: User,
        reason: str = ""
    ) -> UserServiceAccess:
        """
        Otorgar acceso a servicio.
        
        Args:
            user: Usuario a quien se otorga acceso
            service: Instancia de Service o ID
            granted_by: Usuario que otorga el acceso
            reason: Razón del otorgamiento
            
        Returns:
            UserServiceAccess creado o reactivado
        """
        if isinstance(service, int):
            service = Service.objects.get(id=service)
        
        # Crear o reactivar
        access, created = UserServiceAccess.objects.get_or_create(
            user=user,
            service=service,
            defaults={
                'granted_by': granted_by,
                'reason': reason,
                'is_active': True,
            }
        )
        
        if not created and not access.is_active:
            # Reactivar si estaba revocado
            access.is_active = True
            access.granted_by = granted_by
            access.reason = reason
            access.revoked_at = None
            access.revoked_by = None
            access.save()
        
        return access
    
    @staticmethod
    def revoke_service_access(
        user: User,
        service,
        revoked_by: User
    ) -> Optional[UserServiceAccess]:
        """
        Revocar acceso a servicio.
        
        Args:
            user: Usuario a quien se revoca acceso
            service: Instancia de Service o ID
            revoked_by: Usuario que revoca el acceso
            
        Returns:
            UserServiceAccess revocado o None si no existía
        """
        from django.utils import timezone
        
        service_id = service.id if hasattr(service, 'id') else service
        
        try:
            access = UserServiceAccess.objects.get(
                user=user,
                service_id=service_id,
                is_active=True,
            )
            
            access.is_active = False
            access.revoked_at = timezone.now()
            access.revoked_by = revoked_by
            access.save()
            
            return access
        except UserServiceAccess.DoesNotExist:
            return None
    
    @staticmethod
    def get_services_summary(user: User) -> dict:
        """
        Obtener resumen de servicios del usuario.
        
        Args:
            user: Usuario
            
        Returns:
            Dict con estadísticas
        """
        services = ServiceAccessService.get_user_services(user)
        
        return {
            'total_services': services.count(),
            'services': [
                {
                    'id': s.id,
                    'numero_800': s.numero_800,
                    'nombre': s.nombre,
                    'center': s.center.nombre,
                }
                for s in services
            ],
            'is_superuser': user.is_superuser,
        }
