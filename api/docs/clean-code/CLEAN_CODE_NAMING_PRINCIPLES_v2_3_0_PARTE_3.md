---
version: 2.3.0
date: 2026-01-18
project: IACT (Sistema Call Center)
base: Clean Code (Robert Martin) + Clean Architecture  
changelog: PARTE 3/5 - DRF Avanzado (Permissions, Decorators, Middleware, Mixins, Response)
partes: 3/5
estado: completo
---

# CLEAN CODE NAMING PRINCIPLES v2.3.0

**PARTE 3/5: DRF AVANZADO**

---

## 📋 CONTENIDO DE ESTA PARTE

19. [DRF: Permissions y Authentication](#19-drf-permissions-authentication)
20. [DRF: Decorators](#20-drf-decorators)  
21. [Django: Middleware](#21-django-middleware)
22. [DRF: Mixins](#22-drf-mixins)
23. [DRF: Response y Exception Handling](#23-drf-response-exception-handling)

---

## RECORDATORIO: REGLA DE IDIOMA

```
✅ CÓDIGO: Siempre en INGLÉS
✅ COMENTARIOS/DOCSTRINGS: Siempre en ESPAÑOL
✅ NOMBRES DE DOMINIO: Depende del contexto

Function ID RBAC: reports.view (inglés)
Display name: ve_reportes (español)
Error messages: español
```

---

<a name="19-drf-permissions-authentication"></a>
## 19. DRF: PERMISSIONS Y AUTHENTICATION

### 19.1 Permission Classes Estándar

```python
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
    IsAuthenticatedOrReadOnly
)

# ✅ CORRECTO - Usar permissions estándar
class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet con permisos estándar."""  # ← Español
    
    permission_classes = [IsAuthenticated]
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
```

### 19.2 Custom Permission Class IACT

```python
# apps/access/permissions.py

from rest_framework.permissions import BasePermission


class RequiresFunction(BasePermission):
    """
    Permission que verifica función RBAC.
    
    Uso:
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, RequiresFunction]
            required_function = 'reports.view'
    
    El ViewSet debe definir atributo 'required_function'.
    """  # ← Español
    
    def has_permission(self, request, view):
        """
        Verifica si usuario tiene función requerida.
        
        Returns:
            True si tiene la función
        """  # ← Español
        
        # Obtener función requerida del view
        required_function = getattr(view, 'required_function', None)
        
        if not required_function:
            # Sin función requerida = denegar
            return False
        
        # Verificar si usuario tiene la función
        from apps.access.services import AccessService
        
        return AccessService.user_has_function(
            user=request.user,
            function_id=required_function
        )
    
    def has_object_permission(self, request, view, obj):
        """
        Verifica permisos a nivel de objeto.
        
        Por defecto, delega a has_permission.
        Override si necesitas lógica específica por objeto.
        """  # ← Español
        return self.has_permission(request, view)


# ✅ USO
class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet con RBAC."""  # ← Español
    
    permission_classes = [IsAuthenticated, RequiresFunction]
    required_function = 'reports.view'
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
```

### 19.3 Permission por Acción

```python
# apps/reports/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.access.permissions import RequiresFunction


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet con permisos diferentes por acción.
    
    - list/retrieve: reports.view
    - create: reports.create
    - update/partial_update: reports.update
    - destroy: reports.delete
    """  # ← Español
    
    queryset = Report.objects.filter(is_deleted=False)
    serializer_class = ReportSerializer
    
    def get_permissions(self):
        """
        Retorna permisos según acción.
        
        DRF llama este método para cada request.
        """  # ← Español
        
        # Mapa de acción → función requerida
        function_map = {
            'list': 'reports.view',
            'retrieve': 'reports.view',
            'create': 'reports.create',
            'update': 'reports.update',
            'partial_update': 'reports.update',
            'destroy': 'reports.delete',
        }
        
        # Obtener función requerida
        self.required_function = function_map.get(
            self.action,
            'reports.view'  # Default
        )
        
        return [IsAuthenticated(), RequiresFunction()]
```

---

<a name="20-drf-decorators"></a>
## 20. DRF: DECORATORS

### 20.1 @action Decorator

```python
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet con custom actions."""  # ← Español
    
    # ✅ CORRECTO - @action con detail=False
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """
        Obtiene métricas generales.
        
        GET /api/v1/reports/metrics/
        
        No requiere ID (detail=False).
        """  # ← Español
        data = ReportService.get_metrics()
        return Response(data)
    
    # ✅ CORRECTO - @action con detail=True
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """
        Exporta reporte específico.
        
        POST /api/v1/reports/{id}/export/
        
        Requiere ID (detail=True).
        """  # ← Español
        report = self.get_object()
        file_url = ReportService.export_to_excel(report)
        return Response({'file_url': file_url})
    
    # ✅ CORRECTO - @action con múltiples métodos
    @action(detail=True, methods=['post', 'delete'])
    def share(self, request, pk=None):
        """
        Comparte o descomparte reporte.
        
        POST /api/v1/reports/{id}/share/   - Compartir
        DELETE /api/v1/reports/{id}/share/ - Descompartir
        """  # ← Español
        report = self.get_object()
        
        if request.method == 'POST':
            # Compartir
            shared_with = request.data.get('user_ids', [])
            ReportService.share_with_users(report, shared_with)
            return Response({'message': 'Reporte compartido'})
        
        elif request.method == 'DELETE':
            # Descompartir
            ReportService.unshare(report)
            return Response(status=status.HTTP_204_NO_CONTENT)
```

### 20.2 URL Naming en @action

```python
# ✅ CORRECTO - url_path personalizado
@action(
    detail=True,
    methods=['post'],
    url_path='generate-excel'  # URL: /reports/{id}/generate-excel/
)
def generate_excel(self, request, pk=None):
    """Genera Excel del reporte."""  # ← Español
    pass


# ✅ CORRECTO - url_name para reverse()
@action(
    detail=False,
    methods=['get'],
    url_name='top-reports'  # name para reverse: 'report-top-reports'
)
def top_reports(self, request):
    """Top 10 reportes más usados."""  # ← Español
    pass


# Uso de url_name:
from django.urls import reverse
url = reverse('report-top-reports')  # /api/v1/reports/top_reports/
```

---

<a name="21-django-middleware"></a>
## 21. DJANGO: MIDDLEWARE

### 21.1 Nomenclatura de Middleware

```python
# apps/access/middleware.py

# ✅ CORRECTO - Sufijo "Middleware"
class AccessAuditMiddleware:
    """
    Middleware de auditoría de accesos.
    
    Registra cada request autenticado para auditoría RBAC.
    """  # ← Español
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """Procesa request."""  # ← Español
        
        # Before view
        if request.user.is_authenticated:
            self._log_access(request)
        
        # View execution
        response = self.get_response(request)
        
        # After view
        return response
    
    def _log_access(self, request):
        """Registra acceso en audit log."""  # ← Español
        from apps.audit.models import AccessLog
        
        AccessLog.objects.create(
            user=request.user,
            path=request.path,
            method=request.method,
            ip_address=self._get_client_ip(request)
        )
    
    def _get_client_ip(self, request):
        """Obtiene IP del cliente."""  # ← Español
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip


# ❌ INCORRECTO - Sin sufijo
class AccessAudit:  # ❌ Falta "Middleware"
    pass

# ❌ INCORRECTO - Nombre genérico
class AuditMiddleware:  # ❌ No indica QUÉ audita
    pass
```

### 21.2 Orden de Middleware

```python
# config/settings/base.py

MIDDLEWARE = [
    # 1. Security
    'django.middleware.security.SecurityMiddleware',
    
    # 2. Session
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # 3. CORS (si aplica)
    'corsheaders.middleware.CorsMiddleware',
    
    # 4. Common
    'django.middleware.common.CommonMiddleware',
    
    # 5. CSRF
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # 6. Authentication
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # 7. Messages
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # 8. Clickjacking
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # 9. Custom - Access Audit
    'apps.access.middleware.AccessAuditMiddleware',
    
    # 10. Custom - Session Security
    'apps.authentication.middleware.SessionSecurityMiddleware',
]

# ❌ INCORRECTO - Orden incorrecto
MIDDLEWARE = [
    'apps.access.middleware.AccessAuditMiddleware',  # ❌ Muy temprano
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # AccessAuditMiddleware necesita request.user (de AuthenticationMiddleware)
]
```

---

<a name="22-drf-mixins"></a>
## 22. DRF: MIXINS

### 22.1 Mixins Estándar de DRF

```python
from rest_framework import mixins, viewsets


# ✅ CORRECTO - Solo lectura (list + retrieve)
class ReportViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    API de solo lectura para reportes.
    
    Endpoints disponibles:
    - GET /reports/         - Lista reportes
    - GET /reports/{id}/    - Obtiene reporte específico
    
    NO permite:
    - POST (create)
    - PUT/PATCH (update)
    - DELETE (destroy)
    """  # ← Español
    
    queryset = Report.objects.filter(is_deleted=False)
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]


# ✅ CORRECTO - Crear y listar (no modificar)
class LogViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    API para logs del sistema.
    
    Endpoints:
    - GET  /logs/   - Lista logs
    - POST /logs/   - Crea nuevo log
    
    NO permite:
    - GET /logs/{id}/      (retrieve)
    - PUT/PATCH (update)
    - DELETE (destroy)
    
    Razón: Logs son append-only, no se modifican ni eliminan.
    """  # ← Español
    
    queryset = SystemLog.objects.all()
    serializer_class = LogSerializer
```

### 22.2 Custom Mixins IACT

```python
# apps/utils/mixins.py

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class SoftDeleteViewSetMixin:
    """
    Mixin para ViewSets con soft delete.
    
    Agrega endpoints estándar de soft delete:
    - DELETE /{id}/ → soft delete
    - POST /{id}/restore/ → restore
    - GET /deleted/ → list deleted
    
    Requisitos:
    - Modelo debe heredar de SoftDeleteMixin
    - ViewSet debe tener permission_classes configurado
    
    Uso:
        class MyViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
            queryset = MyModel.objects.filter(is_deleted=False)
            ...
    """  # ← Español
    
    def get_queryset(self):
        """
        Filtra solo registros activos por defecto.
        
        Override si necesitas comportamiento diferente.
        """  # ← Español
        queryset = super().get_queryset()
        return queryset.filter(is_deleted=False)
    
    def destroy(self, request, pk=None):
        """
        Soft delete en lugar de DELETE físico.
        
        DELETE /{resource}/{id}/
        
        CNST-005: IACT prohibe DELETE físico en producción.
        """  # ← Español
        instance = self.get_object()
        instance.soft_delete(deleted_by=request.user)
        
        return Response(
            {"message": f"{instance._meta.verbose_name} eliminado exitosamente"},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Restaura registro eliminado.
        
        POST /{resource}/{id}/restore/
        """  # ← Español
        model_class = self.get_queryset().model
        
        try:
            instance = model_class.objects.get(pk=pk)
        except model_class.DoesNotExist:
            return Response(
                {"error": "Registro no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not instance.is_deleted:
            return Response(
                {"error": "El registro no está eliminado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.restore()
        serializer = self.get_serializer(instance)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """
        Lista registros eliminados.
        
        GET /{resource}/deleted/
        """  # ← Español
        model_class = self.get_queryset().model
        queryset = model_class.objects.filter(is_deleted=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ✅ USO del mixin
class ReportViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet de reportes con soft delete automático.
    
    Hereda de SoftDeleteViewSetMixin para obtener:
    - destroy() con soft delete
    - POST /restore/
    - GET /deleted/
    """  # ← Español
    
    queryset = Report.objects.all()  # Mixin filtra is_deleted=False
    serializer_class = ReportSerializer
```

---

<a name="23-drf-response-exception-handling"></a>
## 23. DRF: RESPONSE Y EXCEPTION HANDLING

### 23.1 Response Estándar

```python
from rest_framework.response import Response
from rest_framework import status


# ✅ CORRECTO - Usar Response de DRF
class ReportViewSet(viewsets.ModelViewSet):
    
    def create(self, request):
        """Crea nuevo reporte."""  # ← Español
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Obtiene métricas."""  # ← Español
        data = ReportService.get_metrics()
        
        return Response({
            'count': len(data),
            'metrics': data
        })
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Exporta reporte."""  # ← Español
        report = self.get_object()
        
        try:
            file_url = ReportService.export_to_excel(report)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'file_url': file_url,
            'report_id': report.id
        })


# ❌ INCORRECTO - Usar JsonResponse en DRF
from django.http import JsonResponse

class ReportViewSet(viewsets.ModelViewSet):
    
    def create(self, request):
        """❌ JsonResponse pierde features de DRF."""
        report = Report.objects.create(name=request.data['name'])
        return JsonResponse({"id": report.id}, status=201)  # ❌
```

### 23.2 Custom Exception Handler

```python
# apps/utils/exceptions.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError


def custom_exception_handler(exc, context):
    """
    Handler de excepciones personalizado para IACT.
    
    Maneja:
    - Excepciones de DRF (estándar)
    - ValidationError de Django
    - Excepciones custom de IACT
    
    Retorna respuestas consistentes con estructura:
    {
        "error": "mensaje",
        "code": "ERROR_CODE",
        "details": {...}
    }
    """  # ← Español
    
    # Llamar handler estándar de DRF
    response = exception_handler(exc, context)
    
    if response is not None:
        # DRF ya manejó la excepción
        # Personalizar formato de respuesta
        custom_response = {
            'error': response.data.get('detail', 'Error en la solicitud'),
            'code': _get_error_code(exc),
            'status_code': response.status_code
        }
        
        # Agregar detalles si hay validación
        if hasattr(exc, 'get_full_details'):
            custom_response['details'] = exc.get_full_details()
        
        return Response(custom_response, status=response.status_code)
    
    # Manejar ValidationError de Django
    if isinstance(exc, DjangoValidationError):
        return Response(
            {
                'error': 'Error de validación',
                'code': 'VALIDATION_ERROR',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Manejar excepciones custom IACT
    if hasattr(exc, 'error_code'):
        return Response(
            {
                'error': str(exc),
                'code': exc.error_code,
                'details': getattr(exc, 'details', None)
            },
            status=getattr(exc, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
        )
    
    # Excepción no manejada - retornar None para handler default
    return None


def _get_error_code(exc):
    """Obtiene código de error según tipo de excepción."""  # ← Español
    error_code_map = {
        'NotAuthenticated': 'AUTHENTICATION_REQUIRED',
        'PermissionDenied': 'PERMISSION_DENIED',
        'NotFound': 'NOT_FOUND',
        'ValidationError': 'VALIDATION_ERROR',
    }
    
    exc_class_name = exc.__class__.__name__
    return error_code_map.get(exc_class_name, 'UNKNOWN_ERROR')


# config/settings/base.py
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.utils.exceptions.custom_exception_handler',
}
```

### 23.3 Excepciones Custom IACT

```python
# apps/utils/exceptions.py

class IACTException(Exception):
    """Base exception para IACT."""  # ← Español
    
    error_code = 'IACT_ERROR'
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details


class ExportLimitExceeded(IACTException):
    """
    Excepción cuando export excede CNST-007.
    
    Raised cuando se intenta exportar > 100k registros.
    """  # ← Español
    
    error_code = 'EXPORT_LIMIT_EXCEEDED'
    status_code = status.HTTP_400_BAD_REQUEST


class DateRangeExceeded(IACTException):
    """
    Excepción cuando rango de fechas excede CNST-006.
    
    Raised cuando rango > 730 días.
    """  # ← Español
    
    error_code = 'DATE_RANGE_EXCEEDED'
    status_code = status.HTTP_400_BAD_REQUEST


class ETLDataNotAvailable(IACTException):
    """
    Excepción cuando datos ETL no están disponibles.
    
    Raised cuando se solicitan datos de fecha sin procesar.
    """  # ← Español
    
    error_code = 'ETL_DATA_NOT_AVAILABLE'
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class SeparationOfDutiesViolation(IACTException):
    """
    Excepción cuando se viola regla de separación de funciones.
    
    Raised cuando usuario intenta tener funciones conflictivas.
    """  # ← Español
    
    error_code = 'SOD_VIOLATION'
    status_code = status.HTTP_403_FORBIDDEN


# ✅ USO
class ReportService:
    
    @staticmethod
    def export_to_excel(start_date, end_date):
        """
        Exporta reporte a Excel.
        
        Raises:
            DateRangeExceeded: Si rango > 730 días
            ExportLimitExceeded: Si registros > 100k
        """  # ← Español
        
        # Validar rango
        days = (end_date - start_date).days
        if days > 730:
            raise DateRangeExceeded(
                f"Rango máximo es 730 días. Rango solicitado: {days} días",
                details={'max_days': 730, 'requested_days': days}
            )
        
        # Validar límite de registros
        count = ReporteTrimestral.objects.filter(
            fecha__gte=start_date,
            fecha__lte=end_date
        ).count()
        
        if count > 100000:
            raise ExportLimitExceeded(
                f"Límite de exportación es 100k registros (CNST-007). "
                f"Registros encontrados: {count:,}",
                details={'max_records': 100000, 'found_records': count}
            )
        
        # Generar Excel...
        return file_url
```

### 23.4 Renderers y Parsers

```python
# config/settings/base.py

REST_FRAMEWORK = {
    # Renderers
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Solo en dev
    ],
    
    # Parsers
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}


# Custom renderer
# apps/utils/renderers.py

from rest_framework.renderers import JSONRenderer


class IACTJSONRenderer(JSONRenderer):
    """
    Renderer JSON personalizado para IACT.
    
    Agrega metadata a todas las respuestas:
    - timestamp
    - version
    """  # ← Español
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Renderiza respuesta con metadata."""  # ← Español
        
        if renderer_context and 'response' in renderer_context:
            response = renderer_context['response']
            
            # Solo agregar metadata en success (2xx)
            if response.status_code >= 200 and response.status_code < 300:
                wrapped_data = {
                    'data': data,
                    'meta': {
                        'timestamp': timezone.now().isoformat(),
                        'version': 'v1',
                    }
                }
                return super().render(
                    wrapped_data,
                    accepted_media_type,
                    renderer_context
                )
        
        return super().render(data, accepted_media_type, renderer_context)
```

### 23.5 Pagination

```python
# apps/utils/pagination.py

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Paginación estándar de IACT.
    
    - page_size: 50 registros por defecto
    - max_page_size: 100 máximo
    - page_size_query_param: permite personalizar tamaño
    """  # ← Español
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """Response con metadata de paginación."""  # ← Español
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'results': data
        })


class LargePagination(PageNumberPagination):
    """
    Paginación para grandes volúmenes.
    
    - page_size: 1000 registros
    - Para exports, logs, etc
    """  # ← Español
    
    page_size = 1000
    max_page_size = 5000


# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'apps.utils.pagination.StandardPagination',
}
```

---

**FIN DE PARTE 3/5**

**Continúa en:** CLEAN_CODE_NAMING_PRINCIPLES_v2_3_0_PARTE_4.md

---

**Resumen Parte 3:**
- ✅ Sección 19: DRF Permissions (RequiresFunction, permission por acción)
- ✅ Sección 20: DRF Decorators (@action, url_path, url_name)
- ✅ Sección 21: Django Middleware (AccessAuditMiddleware, orden correcto)
- ✅ Sección 22: DRF Mixins (estándar + SoftDeleteViewSetMixin custom)
- ✅ Sección 23: Response y Exception Handling (excepciones IACT custom)

**Próxima parte:** IACT Específico (secciones 24-27)