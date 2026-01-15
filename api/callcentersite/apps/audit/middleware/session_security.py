from django.utils.deprecation import MiddlewareMixin
from apps.audit.models import AuditLog


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware de seguridad de sesion.
    
    - Registra todas las peticiones API en auditoria
    - Captura IP y User-Agent
    - Excluye paths admin/static/schema
    """
    
    EXCLUDED_PATHS = [
        '/admin/jsi18n/',
        '/static/',
        '/media/',
        '/api/schema/',
        '/__debug__/',
    ]
    
    def process_request(self, request):
        """
        Procesar peticion entrante.
        
        Registra en auditoria si:
        - Usuario autenticado
        - Path NO excluido
        - Metodo relevante (GET, POST, PUT, DELETE, PATCH)
        """
        # Verificar si path debe ser excluido
        if self._is_excluded_path(request.path):
            return None
        
        # Solo registrar si hay usuario autenticado
        if not request.user or not request.user.is_authenticated:
            return None
        
        # Capturar contexto
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Registrar en auditoria
        try:
            AuditLog.record(
                user=request.user,
                action='API_REQUEST',
                resource=request.path,
                result='SUCCESS',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'method': request.method,
                    'path': request.path,
                }
            )
        except Exception:
            # No fallar si auditoria falla
            pass
        
        return None
    
    def _is_excluded_path(self, path):
        """
        Verificar si path esta excluido.
        
        Args:
            path: Path de la peticion
            
        Returns:
            bool: True si debe excluirse
        """
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return True
        return False
    
    def get_client_ip(self, request):
        """
        Obtener IP del cliente.
        
        Prioriza X-Forwarded-For (proxies/load balancers).
        
        Args:
            request: HttpRequest
            
        Returns:
            str: IP address o None
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Tomar la primera IP (cliente real)
            ip = x_forwarded_for.split(',')[0].strip()
            return ip
        
        return request.META.get('REMOTE_ADDR')
