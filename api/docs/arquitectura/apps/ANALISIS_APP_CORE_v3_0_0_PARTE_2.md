---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Core PARTE 2/3
categoria: arquitectura/apps
tema: apps/core/ - Middleware, Permissions y Mixins
autor: Claude Technical Analysis
tags: [core, middleware, permissions, mixins, clean-code]
estado: definitivo
parte: 2 de 3
relacionado:
  - ANALISIS_APP_CORE_v3_0_0_PARTE_1.md
  - ANALISIS_APP_CORE_v3_0_0_PARTE_3.md
replaces: []
---

# ANÁLISIS DE apps/core/ v3.0.0 - PARTE 2/3
## MIDDLEWARE, PERMISSIONS Y MIXINS

---

## 1. MIDDLEWARE

### 1.1 middleware/logging.py

```python
"""
Request Logging Middleware.

CNST-031: Auditoría completa de requests HTTP.
CLEAN_CODE v3.0.1: Nombre auto-documentado.
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para loggear requests HTTP.
    
    CNST-031: Auditoría de todos los requests.
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    
    Loggea:
    - URL, method, user
    - Timestamp inicio/fin
    - Duration
    - Response status code
    - IP del cliente
    
    Instalación:
        # settings.py
        MIDDLEWARE = [
            ...
            'apps.core.middleware.logging.RequestLoggingMiddleware',
        ]
    """
    
    def process_request(self, request):
        """Procesa request (inicio)."""
        # Timestamp inicio
        request.start_time = time.time()
        
        # IP del cliente
        from apps.utils.helpers import get_client_ip
        request.client_ip = get_client_ip(request)
        
        return None
    
    def process_response(self, request, response):
        """Procesa response y loggea."""
        # Calcular duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
        else:
            duration = 0
        
        # Usuario
        user = request.user if hasattr(request, 'user') else None
        username = user.username if user and user.is_authenticated else 'anonymous'
        
        # Log
        logger.info(
            f"[REQUEST] {request.method} {request.path} | "
            f"User: {username} | "
            f"IP: {request.client_ip} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f}s"
        )
        
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware para headers de seguridad.
    
    Agrega headers de seguridad a todas las responses.
    
    Headers agregados:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: same-origin
    """
    
    def process_response(self, request, response):
        """Agrega headers de seguridad."""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'same-origin'
        
        return response


class UserTimezoneMiddleware(MiddlewareMixin):
    """
    Middleware para timezone del usuario.
    
    Activa timezone según preferencia del usuario.
    
    Uso:
        # El timezone se activa automáticamente
        # Todas las fechas se muestran en timezone del usuario
    """
    
    def process_request(self, request):
        """Activa timezone del usuario."""
        import pytz
        from django.utils import timezone
        
        if request.user.is_authenticated:
            # Obtener timezone del perfil
            user_timezone = getattr(
                request.user.profile,
                'timezone',
                'America/Santiago'
            )
            
            try:
                timezone.activate(pytz.timezone(user_timezone))
            except pytz.UnknownTimeZoneError:
                timezone.activate(pytz.timezone('America/Santiago'))
        
        return None


class HealthCheckMiddleware(MiddlewareMixin):
    """
    Middleware para health check.
    
    Responde a /health/ sin autenticación.
    
    Uso:
        GET /health/
        → 200 OK {"status": "healthy"}
    """
    
    def process_request(self, request):
        """Procesa health check."""
        if request.path == '/health/':
            from django.http import JsonResponse
            return JsonResponse({'status': 'healthy'})
        
        return None
```

---

## 2. PERMISSIONS (DRF)

### 2.1 permissions.py

```python
"""
DRF Permissions custom para IACT.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

from rest_framework import permissions


class RequiresFunctionPermission(permissions.BasePermission):
    """
    Permission que requiere función RBAC.
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    
    Uso en ViewSet:
        class MiViewSet(viewsets.ModelViewSet):
            permission_classes = [RequiresFunctionPermission]
            
            function_map = {
                'list': 'reports.view',
                'create': 'reports.create',
                'destroy': 'reports.delete',
            }
    """
    
    def has_permission(self, request, view):
        """Verifica permiso."""
        # Usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Obtener function_id del view
        action = getattr(view, 'action', None)
        function_map = getattr(view, 'function_map', {})
        
        if action not in function_map:
            # Sin function_map, denegar
            return False
        
        function_id = function_map[action]
        
        # Verificar permiso RBAC
        from apps.access.services import AccessService
        return AccessService.user_has_function(
            request.user,
            function_id
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission: Owner puede edit, otros solo read.
    
    Uso:
        class ReportViewSet(viewsets.ModelViewSet):
            permission_classes = [IsOwnerOrReadOnly]
    """
    
    def has_object_permission(self, request, view, obj):
        """Verifica permiso sobre objeto."""
        # Lectura permitida para todos (autenticados)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para owner
        return obj.created_by == request.user


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Permission: Superuser puede edit, otros solo read.
    
    Uso:
        class ConfigViewSet(viewsets.ModelViewSet):
            permission_classes = [IsSuperUserOrReadOnly]
    """
    
    def has_permission(self, request, view):
        """Verifica permiso."""
        # Lectura permitida para todos (autenticados)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para superuser
        return request.user and request.user.is_superuser


class AllowOptionsAuthentication(permissions.BasePermission):
    """
    Permission: Permite OPTIONS sin autenticación.
    
    Para CORS preflight requests.
    
    Uso:
        class MiViewSet(viewsets.ModelViewSet):
            permission_classes = [
                AllowOptionsAuthentication,
                IsAuthenticated
            ]
    """
    
    def has_permission(self, request, view):
        """Permite OPTIONS."""
        if request.method == 'OPTIONS':
            return True
        
        # Delegar a siguiente permission
        return True
```

---

## 3. MIXINS

### 3.1 mixins.py

```python
"""
Mixins para Views y Serializers.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class SoftDeleteViewSetMixin:
    """
    Mixin para ViewSets con soft delete.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    
    Agrega acciones:
    - /restore/ (POST) - Restaura eliminado
    - /hard-delete/ (DELETE) - Elimina físicamente
    
    Uso:
        class MiViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
            pass
        
        # Endpoints adicionales:
        POST /api/resource/{id}/restore/
        DELETE /api/resource/{id}/hard-delete/
    """
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaura registro eliminado."""
        obj = self.get_object()
        
        if not hasattr(obj, 'is_deleted'):
            return Response(
                {'error': 'Model does not support soft delete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not obj.is_deleted:
            return Response(
                {'error': 'Object is not deleted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        obj.restore()
        
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'])
    def hard_delete(self, request, pk=None):
        """Elimina físicamente."""
        obj = self.get_object()
        
        if hasattr(obj, 'hard_delete'):
            obj.hard_delete()
        else:
            obj.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class ServiceFilterMixin:
    """
    Mixin para filtrar por servicio del usuario.
    
    CLEAN_CODE v3.0.1: Nombre auto-documentado.
    
    Filtra queryset según servicios asignados al usuario.
    
    Uso:
        class ReportViewSet(ServiceFilterMixin, viewsets.ModelViewSet):
            service_field = 'service'  # Campo FK a Service
    """
    
    service_field = 'service'  # Override en subclass
    
    def get_queryset(self):
        """Filtra por servicios del usuario."""
        queryset = super().get_queryset()
        
        # Si superuser, retornar todo
        if self.request.user.is_superuser:
            return queryset
        
        # Obtener servicios del usuario
        from apps.access.models import UserServiceAccess
        user_services = UserServiceAccess.objects.filter(
            user=self.request.user,
            is_deleted=False
        ).values_list('service_id', flat=True)
        
        # Filtrar
        filter_kwargs = {f'{self.service_field}__in': user_services}
        return queryset.filter(**filter_kwargs)


class AuditCreateMixin:
    """
    Mixin para setear created_by al crear.
    
    Uso:
        class ReportViewSet(AuditCreateMixin, viewsets.ModelViewSet):
            pass
    """
    
    def perform_create(self, serializer):
        """Setea created_by."""
        serializer.save(created_by=self.request.user)


class AuditUpdateMixin:
    """
    Mixin para setear updated_by al actualizar.
    
    Uso:
        class ReportViewSet(AuditUpdateMixin, viewsets.ModelViewSet):
            pass
    """
    
    def perform_update(self, serializer):
        """Setea updated_by."""
        serializer.save(updated_by=self.request.user)


class PaginationControlMixin:
    """
    Mixin para controlar paginación.
    
    Permite al cliente desactivar paginación con ?paginate=false.
    
    Uso:
        class ReportViewSet(PaginationControlMixin, viewsets.ModelViewSet):
            pass
        
        # Sin paginación:
        GET /api/reports/?paginate=false
    """
    
    def paginate_queryset(self, queryset):
        """Pagina solo si ?paginate=true (default)."""
        paginate = self.request.query_params.get('paginate', 'true')
        
        if paginate.lower() == 'false':
            return None
        
        return super().paginate_queryset(queryset)
```

---

## 4. CONTEXT PROCESSORS

### 4.1 context_processors.py

```python
"""
Context processors para templates.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

from django.conf import settings


def site_settings(request):
    """
    Agrega settings del sitio al context.
    
    Disponible en templates:
    {{ SITE_NAME }}
    {{ VERSION }}
    {{ DEBUG }}
    
    Instalación:
        # settings.py
        TEMPLATES = [{
            'OPTIONS': {
                'context_processors': [
                    ...
                    'apps.core.context_processors.site_settings',
                ],
            },
        }]
    """
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'IACT'),
        'VERSION': getattr(settings, 'VERSION', '1.0.0'),
        'DEBUG': settings.DEBUG,
    }


def user_permissions(request):
    """
    Agrega funciones RBAC del usuario al context.
    
    Disponible en templates:
    {% if 'reports.create' in user_functions %}
    
    Instalación:
        TEMPLATES = [{
            'OPTIONS': {
                'context_processors': [
                    ...
                    'apps.core.context_processors.user_permissions',
                ],
            },
        }]
    """
    user_functions = []
    
    if request.user.is_authenticated:
        from apps.access.services import AccessService
        user_functions = AccessService.get_user_functions(request.user)
    
    return {
        'user_functions': user_functions,
    }


def request_meta(request):
    """
    Agrega metadata del request al context.
    
    Disponible en templates:
    {{ client_ip }}
    {{ user_agent }}
    """
    from apps.utils.helpers import get_client_ip, get_user_agent
    
    return {
        'client_ip': get_client_ip(request),
        'user_agent': get_user_agent(request),
    }
```

---

## 5. RESUMEN PARTE 2

```yaml
Middleware (4):
  ✅ RequestLoggingMiddleware (CNST-031)
  ✅ SecurityHeadersMiddleware
  ✅ UserTimezoneMiddleware
  ✅ HealthCheckMiddleware

Permissions DRF (4):
  ✅ RequiresFunctionPermission (RBAC)
  ✅ IsOwnerOrReadOnly
  ✅ IsSuperUserOrReadOnly
  ✅ AllowOptionsAuthentication

Mixins (5):
  ✅ SoftDeleteViewSetMixin
  ✅ ServiceFilterMixin
  ✅ AuditCreateMixin
  ✅ AuditUpdateMixin
  ✅ PaginationControlMixin

Context Processors (3):
  ✅ site_settings
  ✅ user_permissions
  ✅ request_meta

Clean Code Aplicado:
  ✅ v3.0.1 PARTE 1: Nombres auto-documentados
  ✅ Docstrings Google Style
  ✅ Clases (van en core/, NO en utils/)

Total: ~600 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 3/3: Testing, Base Services y Resumen Final**

Contenido:
- ✅ Base Services (service classes abstractas)
- ✅ Tests (25 tests)
- ✅ Usage examples
- ✅ Resumen ejecutivo final

**Estimado:** ~300 líneas

---

**Fin de PARTE 2/3**
