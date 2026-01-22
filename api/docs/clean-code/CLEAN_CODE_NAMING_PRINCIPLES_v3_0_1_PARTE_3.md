---
version: 3.0.1
date: 2026-01-18
project: IACT (Sistema Call Center)
base: Clean Code (Robert Martin) + Clean Architecture
changelog: |
  v3.0.1 - PARTE 3/5 - Arquitectura corregida
  - CORRECCIÓN: SoftDeleteViewSetMixin en apps/core/ (no utils/)
  - apps/utils/ SOLO funciones (exceptions.py OK)
  - apps/dashboard/ incluido correctamente
  - Mantiene DRF Avanzado (válido)
partes: 3/5
estado: completo
revision: v3.0.1 (arquitectura correcta)
replaces: CLEAN_CODE_NAMING_PRINCIPLES_v2_3_1_PARTE_3.md
---

# CLEAN CODE NAMING PRINCIPLES v3.0.1

**PARTE 3/5: DRF AVANZADO**

---

## 📋 CONTENIDO DE ESTA PARTE

19. [DRF: Permissions y Authentication](#19-drf-permissions-y-authentication)
20. [DRF: Decorators](#20-drf-decorators)
21. [Django: Middleware](#21-django-middleware)
22. [DRF: Mixins](#22-drf-mixins)
23. [DRF: Response y Exception Handling](#23-drf-response-exception-handling)

---

## ⚠️ CAMBIOS EN v3.0.1

```
ARQUITECTURA CORREGIDA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ v2.3.1 (INCORRECTO):
├─ apps/utils/mixins.py → SoftDeleteViewSetMixin (CLASE)
└─ Mixins en utils/ (incorrecto)

✅ v3.0.1 (CORRECTO):
├─ apps/core/mixins.py → SoftDeleteViewSetMixin (CLASE)
├─ apps/utils/exceptions.py → Funciones (OK)
└─ Arquitectura apps/core/ vs apps/utils/ correcta

MODELOS CORREGIDOS (desde v2.3.1):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CallRecord (antes HistoricoT1)
✅ QuarterlyReport (antes ReporteTrimestral)
✅ IVRMenu (antes Menu2)
✅ apps/ivr/ (antes ivr_legacy)

APPS CONFIRMADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ apps/dashboard/ (visualización con widgets)
✅ apps/core/ (modelos abstractos + mixins ViewSet)
✅ apps/utils/ (solo funciones)
```

---

<a name="19-drf-permissions-y-authentication"></a>
## 19. DRF: PERMISSIONS Y AUTHENTICATION

### 19.1 Permission Classes

```python
# apps/access/permissions.py

from rest_framework import permissions


# ✅ CORRECTO - RequiresFunction (2 palabras)
class RequiresFunction(permissions.BasePermission):
    """
    Requiere función RBAC específica.
    
    Verifica que usuario tenga función asignada
    especificada en atributo required_function del ViewSet.
    
    Uso en ViewSet:
        class ReportViewSet(viewsets.ModelViewSet):
            permission_classes = [RequiresFunction]
            required_function = 'reports.view'
    
    Uso en @action:
        @action(...)
        @require_function('reports.export')  # Decorator
        def export(self, request):
            pass
    """  # ← Español
    
    message = "No tienes permiso para realizar esta acción"  # ← Español
    
    def has_permission(self, request, view):
        """
        Verifica permiso a nivel de vista.
        
        Args:
            request: HttpRequest
            view: ViewSet o APIView
            
        Returns:
            True si usuario tiene función requerida
        """  # ← Español
        
        # Obtener función requerida del ViewSet
        required_function = getattr(view, 'required_function', None)
        
        if not required_function:
            return True  # Sin función = permitir
        
        # Verificar que usuario tenga la función
        return self.check_user_has_function(
            request.user,
            required_function
        )
    
    def check_user_has_function(self, user, function_id):
        """
        Verifica si usuario tiene función asignada.
        
        Args:
            user: Usuario a verificar
            function_id: ID namespace (ej: 'reports.view')
            
        Returns:
            True si tiene función activa
        """  # ← Español
        
        if not user or not user.is_authenticated:
            return False
        
        # Superusuarios tienen todas las funciones
        if user.is_superuser:
            return True
        
        from apps.access.models import UserFunctionAssignment
        
        return UserFunctionAssignment.objects.filter(
            user=user,
            function__function_id=function_id,
            is_active=True,
            is_deleted=False
        ).exists()


# ✅ CORRECTO - IsOwnerOrReadOnly (4 palabras)
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permite edición solo al dueño, lectura a todos.
    
    Métodos seguros (GET, HEAD, OPTIONS): todos
    Métodos escritura (POST, PUT, PATCH, DELETE): solo dueño
    
    Uso:
        permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    """  # ← Español
    
    message = "Solo el propietario puede modificar este recurso"  # ← Español
    
    def has_object_permission(self, request, view, obj):
        """
        Verifica permiso a nivel de objeto.
        
        Args:
            request: HttpRequest
            view: ViewSet
            obj: Instancia del modelo
        """  # ← Español
        
        # Lectura permitida para todos autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para dueño
        return obj.owner == request.user


# ❌ INCORRECTO - Nombres genéricos
class CustomPermission(permissions.BasePermission):
    """❌ ¿Qué permiso? No descriptivo."""
    pass

class Permission1(permissions.BasePermission):
    """❌ Número sin significado."""
    pass
```

---

### 19.2 Uso en ViewSets

```python
# apps/reports/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.access.permissions import RequiresFunction, IsOwnerOrReadOnly
from apps.reports.models import Report
from apps.reports.serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    """
    API de reportes con RBAC.
    
    Permisos base:
    - IsAuthenticated: Usuario autenticado
    - RequiresFunction: Función RBAC específica
    
    Endpoints:
    - GET /reports/ - Lista reportes (reports.view)
    - POST /reports/ - Crea reporte (reports.create)
    - GET /reports/{id}/ - Detalle (reports.view)
    - PUT /reports/{id}/ - Actualiza (reports.update)
    - DELETE /reports/{id}/ - Soft delete (reports.delete)
    """  # ← Español
    
    queryset = Report.objects.filter(is_deleted=False)
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, RequiresFunction]
    required_function = 'reports.view'  # ← Función base
    
    def get_permissions(self):
        """
        Permisos dinámicos según acción.
        
        Permite especificar diferentes permisos
        para diferentes acciones del ViewSet.
        """  # ← Español
        
        # destroy requiere ser dueño O tener permiso especial
        if self.action == 'destroy':
            return [
                IsAuthenticated(),
                RequiresFunction(),
                IsOwnerOrReadOnly()
            ]
        
        # update/partial_update requieren ser dueño
        if self.action in ['update', 'partial_update']:
            return [
                IsAuthenticated(),
                RequiresFunction(),
                IsOwnerOrReadOnly()
            ]
        
        # Por defecto: autenticado + función
        return super().get_permissions()


# ❌ INCORRECTO - Usar decorator en ViewSet DRF
from apps.access.decorators import require_function  # ← Para vistas Django

class ReportViewSet(viewsets.ModelViewSet):
    
    @require_function('reports.export')  # ❌ NO en DRF ViewSets
    def export_csv(self, request):
        """❌ Decorators para vistas Django, NO DRF."""
        pass
```

**Por qué es incorrecto usar decorators en ViewSets:**
```
Decoradores (@require_function):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Para: Vistas Django tradicionales (function-based)
✅ Patrón: Funcional/procedural
✅ Ejemplo: def my_view(request): ...

Permission Classes:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Para: DRF ViewSets y APIView (class-based)
✅ Patrón: Orientado a objetos
✅ Ejemplo: permission_classes = [RequiresFunction]

❌ NO mezclar: Usar decoradores en ViewSets rompe patrón DRF
```

---

### 19.3 Authentication

```python
# config/settings/base.py

REST_FRAMEWORK = {
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # JWT para API (producción)
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # Session para Browsable API (desarrollo)
        'rest_framework.authentication.SessionAuthentication',
    ],
    
    # Permissions
    'DEFAULT_PERMISSION_CLASSES': [
        # ⭐ Por defecto requiere autenticación (seguro)
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'apps.utils.pagination.StandardPagination',
    'PAGE_SIZE': 25,
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}


# ❌ INCORRECTO - AllowAny por defecto (INSEGURO)
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # ❌ Permite sin auth
    ],
}
```

---

<a name="20-drf-decorators"></a>
## 20. DRF: DECORATORS

### 20.1 @action

```python
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from apps.reports.services import ReportService


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet con custom actions."""  # ← Español
    
    # ✅ CORRECTO: detail=False para colección
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Estadísticas globales de reportes.
        
        GET /reports/statistics/
        
        Solo reportes activos (no eliminados).
        """  # ← Español
        
        from apps.ivr.models import CallRecord
        
        active_count = CallRecord.objects.filter(
            is_deleted=False
        ).count()
        
        total_calls = CallRecord.objects.aggregate(
            total=models.Sum('total_calls')
        )['total']
        
        return Response({
            "active_reports": active_count,
            "total_calls": total_calls
        })
    
    # ✅ CORRECTO: detail=True para instancia específica
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminUser]  # Solo admin
    )
    def force_delete(self, request, pk=None):
        """
        Elimina físicamente un reporte (SOLO ADMIN).
        
        POST /reports/{id}/force-delete/
        
        ⚠️ PELIGROSO: Eliminación física permanente.
        Solo para emergencias por admin.
        """  # ← Español
        
        report = self.get_object()
        report.delete()  # DELETE físico
        
        return Response(
            {"message": "Reporte eliminado permanentemente"},
            status=status.HTTP_204_NO_CONTENT
        )
    
    # ✅ CORRECTO: url_path personalizado
    @action(
        detail=False,
        methods=['post'],
        url_path='export-excel'
    )
    def export_excel(self, request):
        """
        Exporta reportes a Excel.
        
        POST /reports/export-excel/
        
        Body:
            {
                "quarter": "Q1",
                "did": "Puebla"
            }
        """  # ← Español
        
        quarter = request.data.get('quarter')
        did = request.data.get('did')
        
        file_url = ReportService.export_to_excel(quarter, did)
        
        return Response({"file_url": file_url})
```

---

### 20.2 @api_view (function-based views)

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# ✅ CORRECTO - Function-based view simple
@api_view(['GET'])
def health_check(request):
    """
    Verifica salud del sistema.
    
    GET /health/
    
    Returns:
        {"status": "healthy", "timestamp": ...}
    """  # ← Español
    
    from django.utils import timezone
    
    return Response({
        "status": "healthy",
        "timestamp": timezone.now().isoformat()
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def version(request):
    """
    Información de versión de la API.
    
    GET  /version/ - Obtiene versión
    POST /version/ - Valida compatibilidad
    """  # ← Español
    
    version_info = {
        "version": "2.0.0",
        "build": "2026-01-18",
        "api": "v1"
    }
    
    if request.method == 'GET':
        return Response(version_info)
    
    elif request.method == 'POST':
        client_version = request.data.get('version')
        compatible = client_version == version_info['version']
        
        return Response({
            **version_info,
            "compatible": compatible
        })
```

---

<a name="21-django-middleware"></a>
## 21. DJANGO: MIDDLEWARE

### 21.1 Nomenclatura

```python
# apps/access/middleware.py

import logging
from django.utils import timezone
from apps.access.models import AccessLog

logger = logging.getLogger(__name__)


# ✅ CORRECTO - AccessAuditMiddleware (3 palabras)
class AccessAuditMiddleware:
    """
    Middleware de auditoría de accesos.
    
    Registra cada request autenticado con:
    - Usuario
    - Endpoint accedido
    - Método HTTP
    - IP de origen
    - Timestamp
    - Response status
    
    Solo audita requests autenticados.
    Logs se guardan con soft delete.
    """  # ← Español
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Procesa request y audita acceso.
        
        Args:
            request: HttpRequest de Django
            
        Returns:
            HttpResponse
        """  # ← Español
        
        # Procesar request
        response = self.get_response(request)
        
        # Auditar si autenticado
        if request.user.is_authenticated:
            self.log_access(request, response)
        
        return response
    
    def log_access(self, request, response):
        """
        Registra acceso en log de auditoría.
        
        Args:
            request: HttpRequest
            response: HttpResponse
        """  # ← Español
        
        try:
            AccessLog.objects.create(
                user=request.user,
                path=request.path,
                method=request.method,
                ip_address=self.get_client_ip(request),
                status_code=response.status_code,
                timestamp=timezone.now()
            )
        except Exception as e:
            # No fallar request si falla log
            logger.error(
                f"Error al auditar acceso: {e}",
                exc_info=True
            )
    
    @staticmethod
    def get_client_ip(request):
        """
        Obtiene IP real del cliente.
        
        Considera headers de proxy/load balancer.
        """  # ← Español
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        
        if x_forwarded_for:
            # Primera IP es del cliente
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip


# ❌ INCORRECTO - Nombres confusos
class CustomMiddleware:  # ❌ NO descriptivo
    pass

class Middleware1:  # ❌ Número sin significado
    pass

class PermissionAuditMiddleware:  # ❌ Confuso (sugiere permissions/)
    """❌ Está en access/, no permissions/."""
    pass
```

---

### 21.2 Orden de Middleware (CRÍTICO)

```python
# config/settings/base.py

MIDDLEWARE = [
    # 1. Security (PRIMERO)
    'django.middleware.security.SecurityMiddleware',
    
    # 2. Sessions (necesario para SessionSecurity)
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # 3. ⭐ IACT: Validar sesión única (DESPUÉS de Session)
    'apps.authentication.middleware.SessionSecurityMiddleware',
    
    # 4. Common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # 5. Authentication (identifica request.user)
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # 6. ⭐ IACT: Auditar accesos (DESPUÉS de Auth)
    'apps.access.middleware.AccessAuditMiddleware',
    
    # 7. Messages
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # 8. Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**Reglas de orden:**

```
ORDEN CRÍTICO (NO cambiar):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ SecurityMiddleware → PRIMERO (headers seguridad)
✅ SessionMiddleware → ANTES de SessionSecurity
✅ SessionSecurityMiddleware → DESPUÉS de Session
✅ AuthenticationMiddleware → ANTES de AccessAudit
✅ AccessAuditMiddleware → DESPUÉS de Auth

❌ SI CAMBIAS ORDEN:
- AccessAudit antes de Auth → ❌ request.user no existe
- SessionSecurity antes de Session → ❌ session no existe
- CSRF antes de Session → ❌ CSRF no funciona
```

---

<a name="22-drf-mixins"></a>
## 22. DRF: MIXINS

### 22.1 Mixins Estándar de DRF

Django REST Framework proporciona mixins para composición de ViewSets.

**Mixins disponibles:**
```python
from rest_framework import mixins

mixins.ListModelMixin       # list()
mixins.CreateModelMixin     # create()
mixins.RetrieveModelMixin   # retrieve()
mixins.UpdateModelMixin     # update() + partial_update()
mixins.DestroyModelMixin    # destroy()
```

---

### 22.2 Composición de ViewSets

```python
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated


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
    - GET /reports/{id}/    - Obtiene reporte
    
    NO permite:
    - POST (create)
    - PUT/PATCH (update)
    - DELETE (destroy)
    
    Uso: Reportes que no deben modificarse vía API.
    """  # ← Español
    
    queryset = Report.objects.filter(is_deleted=False)
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]


# ✅ CORRECTO - Crear y listar (append-only)
class LogViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    API para logs del sistema.
    
    Endpoints:
    - GET  /logs/   - Lista logs
    - POST /logs/   - Crea log
    
    NO permite:
    - GET /logs/{id}/      (retrieve)
    - PUT/PATCH (update)
    - DELETE (destroy)
    
    Razón: Logs son append-only, no se modifican.
    """  # ← Español
    
    queryset = SystemLog.objects.all()
    serializer_class = LogSerializer


# ❌ INCORRECTO - ModelViewSet cuando solo necesitas lectura
class ReportViewSet(viewsets.ModelViewSet):
    """❌ Da create, update, destroy que NO queremos."""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

# ✅ MEJOR - ReadOnlyModelViewSet
class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    """✅ Solo list() y retrieve()."""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
```

---

### 22.3 Custom Mixins IACT

```python
# apps/core/mixins.py  ← CORRECCIÓN v3.0.1

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


# ✅ SoftDeleteViewSetMixin (4 palabras - descriptivo)
class SoftDeleteViewSetMixin:
    """
    Mixin para ViewSets con soft delete.
    
    Agrega endpoints estándar:
    - DELETE /{id}/ → soft delete
    - POST /{id}/restore/ → restore
    - GET /deleted/ → list deleted
    
    Requisitos:
    - Modelo debe heredar SoftDeleteMixin
    - ViewSet debe tener permission_classes
    
    Uso:
        class ReportViewSet(
            SoftDeleteViewSetMixin,
            viewsets.ModelViewSet
        ):
            queryset = Report.objects.all()
    """  # ← Español
    
    def get_queryset(self):
        """
        Filtra solo activos por defecto.
        
        Override si necesitas otro comportamiento.
        """  # ← Español
        queryset = super().get_queryset()
        return queryset.filter(is_deleted=False)
    
    def destroy(self, request, pk=None):
        """
        Soft delete en lugar de DELETE físico.
        
        DELETE /{resource}/{id}/
        
        NO elimina físicamente el registro.
        Solo marca is_deleted=True.
        
        CNST-005: IACT prohibe DELETE físico.
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
        
        Revierte soft delete.
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
        
        Requiere permiso especial.
        """  # ← Español
        model_class = self.get_queryset().model
        queryset = model_class.objects.filter(is_deleted=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# Uso del mixin:
from apps.core.mixins import SoftDeleteViewSetMixin  # ← Importar de core/

class ReportViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet con soft delete automático.
    
    Hereda de SoftDeleteViewSetMixin para obtener:
    - destroy() con soft delete
    - POST /restore/
    - GET /deleted/
    """  # ← Español
    
    queryset = Report.objects.all()  # Mixin filtra is_deleted=False
    serializer_class = ReportSerializer
```

**CORRECCIÓN v3.0.1:**
```
❌ v2.3.1: apps/utils/mixins.py (INCORRECTO)
✅ v3.0.1: apps/core/mixins.py (CORRECTO)

RAZÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/  → Clases reutilizables (abstractos + mixins)
apps/utils/ → Solo funciones helper

SoftDeleteViewSetMixin es una CLASE → va en core/
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
    
    def list(self, request):
        """Lista reportes activos."""  # ← Español
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })


# ❌ INCORRECTO - Usar JsonResponse (pierde features DRF)
from django.http import JsonResponse

class ReportViewSet(viewsets.ModelViewSet):
    
    def create(self, request):
        return JsonResponse({"id": 1}, status=201)  # ❌ Pierde DRF
```

**Por qué es malo usar JsonResponse:**
```
JsonResponse:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Pierde renderers de DRF (JSON, Browsable API, XML)
❌ Pierde content negotiation
❌ Pierde throttling y caching
❌ Inconsistente con resto de DRF

Response de DRF:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Soporta múltiples formatos (JSON, Browsable API)
✅ Content negotiation automático
✅ Integra con throttling, caching, permissions
✅ Consistente en toda la API
```

---

### 23.2 Exception Handler Personalizado

```python
# apps/utils/exceptions.py  ← FUNCIONES OK en utils/

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Exception handler personalizado para IACT.
    
    Extiende handler de DRF para:
    1. Logging estructurado de errores
    2. Mensajes en español
    3. Formato consistente de respuesta
    4. Tracking de errores por usuario
    
    Args:
        exc: Excepción lanzada
        context: Contexto de request
        
    Returns:
        Response con error formateado
    """  # ← Español
    
    # Llamar handler por defecto
    response = exception_handler(exc, context)
    
    if response is not None:
        # Personalizar respuesta
        custom_response_data = {
            'error': True,
            'message': get_spanish_error_message(exc),
            'detail': response.data,
            'status_code': response.status_code
        }
        
        # Log estructurado
        log_exception(exc, context, response.status_code)
        
        response.data = custom_response_data
    
    else:
        # Error no manejado por DRF
        logger.error(
            f"Error no manejado: {exc}",
            exc_info=True,
            extra={
                'view': context.get('view'),
                'request': context.get('request')
            }
        )
        
        response = Response(
            {
                'error': True,
                'message': 'Error interno del servidor',
                'detail': str(exc)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response


def get_spanish_error_message(exc):
    """
    Traduce mensajes de error a español.
    
    Args:
        exc: Excepción
        
    Returns:
        Mensaje en español
    """  # ← Español
    
    error_messages = {
        'NotFound': 'Recurso no encontrado',
        'PermissionDenied': 'No tienes permiso para esta acción',
        'NotAuthenticated': 'Autenticación requerida',
        'AuthenticationFailed': 'Credenciales inválidas',
        'ValidationError': 'Error de validación',
        'MethodNotAllowed': 'Método no permitido',
    }
    
    exc_type = type(exc).__name__
    return error_messages.get(exc_type, 'Error en la solicitud')


def log_exception(exc, context, status_code):
    """
    Registra excepción en logs.
    
    Args:
        exc: Excepción
        context: Contexto de request
        status_code: Código HTTP
    """  # ← Español
    
    request = context.get('request')
    view = context.get('view')
    
    logger.warning(
        f"API Error: {type(exc).__name__}",
        extra={
            'exception': str(exc),
            'status_code': status_code,
            'path': request.path if request else None,
            'method': request.method if request else None,
            'user': request.user.username if request and request.user.is_authenticated else 'Anonymous',
            'view': view.__class__.__name__ if view else None
        }
    )
```

---

### 23.3 Configuración en Settings

```python
# config/settings/base.py

REST_FRAMEWORK = {
    # Exception handler personalizado
    'EXCEPTION_HANDLER': 'apps.utils.exceptions.custom_exception_handler',
    
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    # Permissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# ❌ INCORRECTO - Exception handler como middleware
MIDDLEWARE = [
    'apps.utils.middleware.ExceptionHandlerMiddleware',  # ❌ NO
]

# ✅ CORRECTO - En REST_FRAMEWORK
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.utils.exceptions.custom_exception_handler',
}
```

**Por qué no usar middleware:**
```
Middleware:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Se ejecuta ANTES de DRF
❌ No tiene contexto de ViewSet
❌ No puede usar serializers
❌ Orden de ejecución incorrecto

Exception Handler:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Se ejecuta DENTRO de DRF
✅ Tiene contexto completo
✅ Acceso a serializers
✅ Orden correcto
```

---

### 23.4 Excepciones Personalizadas

```python
# apps/utils/exceptions.py

from rest_framework.exceptions import APIException
from rest_framework import status


# ✅ ExportLimitExceeded (3 palabras - descriptivo)
class ExportLimitExceeded(APIException):
    """
    Excepción cuando se excede límite de exportación.
    
    CNST-007: Máximo 100,000 registros por exportación.
    
    Uso:
        if record_count > 100000:
            raise ExportLimitExceeded(record_count)
    """  # ← Español
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Se excedió el límite de exportación'
    default_code = 'export_limit_exceeded'
    
    def __init__(self, record_count=None):
        if record_count:
            detail = (
                f"Se excedió el límite de 100,000 registros. "
                f"Intentaste exportar {record_count:,} registros."
            )
        else:
            detail = self.default_detail
        
        super().__init__(detail)


# ✅ SeparationOfDutiesViolation (4 palabras)
class SeparationOfDutiesViolation(APIException):
    """
    Excepción cuando se viola regla de separación de funciones.
    
    Uso:
        if AccessService.check_sod_violation(user, function):
            raise SeparationOfDutiesViolation(
                function,
                conflicting_functions
            )
    """  # ← Español
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Viola reglas de separación de funciones'
    default_code = 'sod_violation'
    
    def __init__(self, function_id=None, conflicting_functions=None):
        if function_id and conflicting_functions:
            detail = (
                f"No se puede asignar '{function_id}' "
                f"porque viola SoD con: {', '.join(conflicting_functions)}"
            )
        else:
            detail = self.default_detail
        
        super().__init__(detail)


# ✅ ETLNotExecuted (3 palabras)
class ETLNotExecuted(APIException):
    """
    Excepción cuando ETL no se ha ejecutado.
    
    Uso:
        if not ETLService.is_executed_today():
            raise ETLNotExecuted(date.today())
    """  # ← Español
    
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'ETL no ejecutado'
    default_code = 'etl_not_executed'
    
    def __init__(self, date=None):
        if date:
            detail = (
                f"ETL no ejecutado para {date}. "
                f"Datos pueden estar desactualizados."
            )
        else:
            detail = self.default_detail
        
        super().__init__(detail)


# Uso en ViewSet:
class ReportViewSet(viewsets.ModelViewSet):
    
    @action(detail=False, methods=['post'])
    def export_excel(self, request):
        """Exporta reportes a Excel."""  # ← Español
        
        queryset = self.get_queryset()
        record_count = queryset.count()
        
        # Validar CNST-007
        if record_count > 100000:
            raise ExportLimitExceeded(record_count)
        
        # Generar archivo
        file_url = ExcelExporter.export(queryset)
        
        return Response({"file_url": file_url})
```

---

**FIN DE PARTE 3/5**

**Continúa en:** CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_4.md

---

## ✅ RESUMEN PARTE 3

**Secciones completadas:**
- ✅ 19. DRF: Permissions y Authentication
  - RequiresFunction
  - IsOwnerOrReadOnly
  - JWT configuration
- ✅ 20. DRF: Decorators
  - @action (detail=True/False)
  - @api_view
- ✅ 21. Django: Middleware
  - AccessAuditMiddleware
  - Orden crítico de middleware
- ✅ 22. DRF: Mixins
  - Composición de ViewSets
  - SoftDeleteViewSetMixin custom (en core/)
- ✅ 23. DRF: Response y Exception Handling
  - custom_exception_handler
  - Excepciones personalizadas IACT

**Correcciones arquitectónicas v3.0.1:**
- ✅ SoftDeleteViewSetMixin en apps/core/mixins.py (antes en utils/)
- ✅ Funciones en apps/utils/exceptions.py (correcto)
- ✅ apps/dashboard/ incluido correctamente

**Modelos corregidos aplicados:**
- ✅ CallRecord (antes HistoricoT1)
- ✅ QuarterlyReport (antes ReporteTrimestral)
- ✅ apps/ivr/ (antes ivr_legacy)
- ✅ apps/dashboard/ (nueva app)

**Próxima parte:** IACT Específico (Renderers, Parsers, Pagination, Service Layer, Modelos)
