"""
User Timezone Middleware.

CLEAN_CODE v3.0.1: Nombre auto-documentado.
"""

import pytz
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone


class UserTimezoneMiddleware(MiddlewareMixin):
    """
    Middleware para timezone del usuario.
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    
    Activa timezone según preferencia del usuario.
    Todas las fechas se muestran en el timezone del usuario.
    
    Fallback: America/Santiago si no hay preferencia.
    
    Instalación:
        # settings.py
        MIDDLEWARE = [
            ...
            'apps.core.middleware.timezone.UserTimezoneMiddleware',
        ]
    
    Uso:
        # El timezone se activa automáticamente
        # Todas las fechas se muestran en timezone del usuario
        
        # En views/templates:
        {{ order.created_at }}  # Se muestra en timezone del usuario
    
    Examples:
        # Usuario con timezone 'America/New_York':
        # created_at: 2025-01-20 10:00 UTC
        # Se muestra: 2025-01-20 05:00 EST
    """
    
    def process_request(self, request):
        """
        Activa timezone del usuario.
        
        Args:
            request: HttpRequest
        
        Returns:
            None
        """
        if request.user.is_authenticated:
            # Obtener timezone del perfil del usuario
            # Default: America/Santiago
            user_timezone = self._get_user_timezone(request.user)
            
            try:
                timezone.activate(pytz.timezone(user_timezone))
            except pytz.UnknownTimeZoneError:
                # Fallback a Santiago si timezone inválido
                timezone.activate(pytz.timezone('America/Santiago'))
        else:
            # Usuario anónimo: usar timezone por defecto
            timezone.activate(pytz.timezone('America/Santiago'))
        
        return None
    
    def _get_user_timezone(self, user):
        """
        Obtiene timezone del usuario.
        
        Intenta obtener de:
        1. user.profile.timezone
        2. Fallback: America/Santiago
        
        Args:
            user: User object
        
        Returns:
            str: Timezone (ej: 'America/Santiago')
        """
        # Intentar obtener de profile
        if hasattr(user, 'profile'):
            return getattr(user.profile, 'timezone', 'America/Santiago')
        
        # Fallback
        return 'America/Santiago'


# ============================================================================
# RESUMEN MIDDLEWARE TIMEZONE
# 
# Middleware: UserTimezoneMiddleware
# Propósito: Activar timezone del usuario automáticamente
# 
# Comportamiento:
#   ✅ Usuario autenticado → usa user.profile.timezone
#   ✅ Usuario anónimo → America/Santiago
#   ✅ Timezone inválido → fallback a America/Santiago
# 
# Benefit:
#   - Todas las fechas se muestran en timezone del usuario
#   - No necesita conversión manual en views/templates
# 
# Instalación: Agregar a MIDDLEWARE en settings
# ============================================================================
