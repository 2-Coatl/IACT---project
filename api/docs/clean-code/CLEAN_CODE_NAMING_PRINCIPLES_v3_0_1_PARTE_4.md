---
version: 3.0.1
date: 2026-01-18
project: IACT (Sistema Call Center)
base: Clean Code (Robert Martin) + Clean Architecture
changelog: |
  v3.0.1 - PARTE 4/5 - Arquitectura corregida
  - CORRECCIÓN: apps/core/ NO deprecado (modelos abstractos)
  - CORRECCIÓN: TimeStampedModel y SoftDeleteMixin en apps/core/
  - CORRECCIÓN: SoftDeleteViewSetMixin en apps/core/
  - apps/utils/ solo funciones (pagination OK)
  - apps/dashboard/ incluido correctamente
  - Service Layer Pattern válido
partes: 4/5
estado: completo
revision: v3.0.1 (arquitectura correcta)
replaces: CLEAN_CODE_NAMING_PRINCIPLES_v2_3_1_PARTE_4.md
---

# CLEAN CODE NAMING PRINCIPLES v3.0.1

**PARTE 4/5: IACT ESPECÍFICO**

---

## 📋 CONTENIDO DE ESTA PARTE

24. [DRF: Renderers, Parsers, Pagination](#24-drf-renderers-parsers-pagination)
25. [IACT: Arquitectura apps/core/ vs apps/utils/](#25-iact-arquitectura-core-utils)
26. [IACT: Service Layer Pattern](#26-iact-service-layer-pattern)
27. [IACT: Modelos y Herencia](#27-iact-modelos-herencia)

---

## ⚠️ CAMBIOS EN v3.0.1

```
ARQUITECTURA CORREGIDA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ v2.3.1 (INCORRECTO):
├─ apps/core/ "DEPRECADO" → ❌ Error conceptual
├─ apps/utils/models.py → TimeStampedModel (clase)
├─ apps/utils/mixins.py → SoftDeleteViewSetMixin (clase)
└─ Confusión arquitectónica

✅ v3.0.1 (CORRECTO):
├─ apps/core/ fundamental (modelos abstractos + mixins ViewSet)
├─ apps/core/models.py → TimeStampedModel, SoftDeleteMixin
├─ apps/core/mixins.py → SoftDeleteViewSetMixin
└─ apps/utils/ solo funciones

MODELOS CORREGIDOS (desde v2.3.1):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CallRecord (antes HistoricoT1)
✅ QuarterlyReport (antes ReporteTrimestral)
✅ IVRMenu (antes Menu2)
✅ AbandonedCall (antes LlamadasAbandonadas)
✅ UniqueClient (antes ClientesUnicos)
✅ apps/ivr/ (antes ivr_legacy)

APPS CONFIRMADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ apps/dashboard/ (visualización con widgets)
✅ apps/core/ (modelos abstractos + mixins ViewSet)
✅ apps/utils/ (solo funciones)
```

---

<a name="24-drf-renderers-parsers-pagination"></a>
## 24. DRF: RENDERERS, PARSERS, PAGINATION

### 24.1 Renderers

```python
# config/settings/base.py

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        # BrowsableAPIRenderer solo en desarrollo
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}


# config/settings/production.py

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        # ❌ NO BrowsableAPIRenderer en producción (seguridad)
    ],
}
```

---

### 24.2 Parsers

```python
# config/settings/base.py

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',  # Para file uploads
    ],
}


# ViewSet específico con parser personalizado:
from rest_framework.parsers import FileUploadParser

class FileUploadViewSet(viewsets.ViewSet):
    """ViewSet para upload de archivos."""  # ← Español
    
    parser_classes = [FileUploadParser]
    
    def create(self, request):
        """Procesa archivo subido."""  # ← Español
        file_obj = request.data['file']
        # Procesar archivo...
        return Response({"filename": file_obj.name})
```

---

### 24.3 Pagination

```python
# apps/utils/pagination.py  ← FUNCIONES/CLASES HELPER OK en utils/

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# ✅ StandardPagination (2 palabras - balance perfecto)
class StandardPagination(PageNumberPagination):
    """
    Paginación estándar de IACT.
    
    Configuración:
    - page_size: 25 (por defecto)
    - page_size_query_param: 'page_size' (usuario puede cambiar)
    - max_page_size: 100 (máximo permitido)
    
    Uso:
        GET /reports/?page=2&page_size=50
    
    Respuesta:
        {
            "count": 150,
            "total_pages": 6,
            "current_page": 2,
            "page_size": 25,
            "next": "http://.../reports/?page=3",
            "previous": "http://.../reports/?page=1",
            "results": [...]
        }
    """  # ← Español
    
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Respuesta paginada con metadata adicional.
        
        Agrega información útil para el frontend:
        - total_pages: número total de páginas
        - current_page: página actual
        """  # ← Español
        
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


# ✅ LargePagination (2 palabras - balance perfecto)
class LargePagination(PageNumberPagination):
    """
    Paginación para listados grandes (admin).
    
    Usado en endpoints administrativos que pueden
    retornar más resultados por página.
    
    Configuración:
    - page_size: 100
    - max_page_size: 500
    """  # ← Español
    
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500


# ❌ INCORRECTO - Nombres confusos
class CustomPagination(PageNumberPagination):
    """❌ ¿Custom cómo? No descriptivo."""
    pass

class Pagination1(PageNumberPagination):
    """❌ Número sin significado."""
    pass
```

**NOTA v3.0.1:**
```
Pagination classes OK en apps/utils/:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ StandardPagination es clase helper (OK en utils/)
✅ LargePagination es clase helper (OK en utils/)

DIFERENCIA:
- Clases de lógica base → apps/core/
- Clases helper/utilidad → apps/utils/ (OK)
```

---

### 24.4 Configuración en Settings

```python
# config/settings/base.py

REST_FRAMEWORK = {
    # Paginación por defecto
    'DEFAULT_PAGINATION_CLASS': 'apps.utils.pagination.StandardPagination',
    'PAGE_SIZE': 25,
}


# Uso en ViewSet específico:
class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet con paginación personalizada."""  # ← Español
    
    # Override paginación para este ViewSet
    pagination_class = LargePagination
    
    queryset = Report.objects.filter(is_deleted=False)
    serializer_class = ReportSerializer


# ViewSet sin paginación (casos especiales):
class StatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """Estadísticas sin paginación."""  # ← Español
    
    pagination_class = None  # Sin paginación
    
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
```

---

<a name="25-iact-arquitectura-core-utils"></a>
## 25. IACT: ARQUITECTURA apps/core/ vs apps/utils/

### 25.1 Arquitectura Correcta (v3.0.1)

```
ARQUITECTURA IACT v3.0.1:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/
├── core/           ✅ MODELOS ABSTRACTOS + MIXINS VIEWSET
├── utils/          ✅ FUNCIONES HELPER + CLASES HELPER
├── access/         ✅ ÚNICO sistema de control de acceso (RBAC)
├── reports/        ✅ Consumo de datos (reportes tabulares)
├── dashboard/      ✅ Visualización con widgets
├── pipeline/       ✅ Monitoreo ETL
└── ivr/            ✅ Adaptador READ-ONLY a datos IVR
```

---

### 25.2 Responsabilidades por App

```python
# ════════════════════════════════════════════════════════════
# apps/core/ - MODELOS ABSTRACTOS + MIXINS VIEWSET
# ════════════════════════════════════════════════════════════

apps/core/
├── models.py
│   ├── TimeStampedModel      # Modelo abstracto (created_at, updated_at)
│   ├── SoftDeleteMixin       # Modelo abstracto (is_deleted, etc.)
│   ├── SoftDeleteManager     # Manager para soft delete
│   └── SoftDeleteQuerySet    # QuerySet para soft delete
│
└── mixins.py
    └── SoftDeleteViewSetMixin  # Mixin para ViewSets DRF


# ════════════════════════════════════════════════════════════
# apps/utils/ - FUNCIONES HELPER + CLASES HELPER
# ════════════════════════════════════════════════════════════

apps/utils/
├── pagination.py
│   ├── StandardPagination    # Clase helper (OK)
│   └── LargePagination       # Clase helper (OK)
│
├── exceptions.py
│   ├── custom_exception_handler()  # Función
│   ├── ExportLimitExceeded   # Exception (OK)
│   └── SeparationOfDutiesViolation
│
├── request.py
│   └── get_client_ip()       # Función
│
└── formatters.py
    ├── format_phone()        # Función
    └── format_nit()          # Función


# ════════════════════════════════════════════════════════════
# apps/access/ - RBAC ÚNICO
# ════════════════════════════════════════════════════════════

apps/access/
├── models.py
│   ├── Function              # Funciones RBAC (reports.view, etc.)
│   ├── FunctionGroup         # Grupos de funciones
│   ├── UserFunctionAssignment  # Asignaciones usuario-función
│   ├── SeparationOfDuties    # Reglas SoD
│   └── AccessLog             # Auditoría de accesos
│
├── services.py
│   └── AccessService         # Lógica RBAC
│       ├── check_user_has_function()
│       ├── assign_function()
│       ├── revoke_function()
│       └── get_user_effective_functions()
│
├── permissions.py
│   ├── RequiresFunction      # Permission class DRF
│   └── IsOwnerOrReadOnly
│
├── decorators.py
│   └── require_function      # Decorator para vistas Django
│
└── middleware.py
    └── AccessAuditMiddleware  # Auditoría de requests


# ════════════════════════════════════════════════════════════
# apps/reports/ - CONSUMO DE DATOS (REPORTES TABULARES)
# ════════════════════════════════════════════════════════════

apps/reports/
├── models.py
│   ├── Report                # Configuración de reporte
│   └── ReportConfig          # Settings de reporte
│
├── services.py
│   ├── ReportService         # Lógica de negocio
│   │   ├── get_quarterly_report()
│   │   ├── calculate_metrics()
│   │   └── validate_date_range()
│   │
│   └── ExportService         # Exportación
│       ├── export_to_excel()
│       └── export_to_csv()
│
└── views.py
    └── ReportViewSet
        └── permission_classes = [RequiresFunction]  # RBAC


# ════════════════════════════════════════════════════════════
# apps/dashboard/ - VISUALIZACIÓN CON WIDGETS
# ════════════════════════════════════════════════════════════

apps/dashboard/
├── models.py
│   ├── Dashboard             # Dashboard personalizado
│   ├── Widget                # Widget individual
│   └── WidgetConfig          # Configuración de widget
│
├── services.py
│   ├── DashboardService      # Lógica de negocio
│   │   ├── get_quarterly_metrics()
│   │   ├── get_client_analysis()
│   │   └── get_ivr_performance()
│   │
│   └── WidgetService         # Generación de widgets
│       ├── generate_kpi_widget()
│       ├── generate_chart_widget()
│       └── generate_table_widget()
│
└── views.py
    └── DashboardViewSet
        └── permission_classes = [RequiresFunction]


# ════════════════════════════════════════════════════════════
# apps/ivr/ - ADAPTADOR A DATOS IVR (READ-ONLY)
# ════════════════════════════════════════════════════════════

apps/ivr/
├── models.py
│   ├── CallRecord            # Registro de llamada (historico_t1)
│   ├── QuarterlyReport       # Reporte trimestral agregado
│   ├── IVRMenu               # Menú del IVR (menu2)
│   ├── AbandonedCall         # Llamadas abandonadas
│   ├── UniqueClient          # Clientes únicos
│   └── AverageClientPerMenu  # Promedio clientes por menú
│
└── services.py
    └── IVRDataService        # Consultas READ-ONLY
        ├── get_call_records()
        └── get_quarterly_data()


# ════════════════════════════════════════════════════════════
# apps/pipeline/ - MONITOREO ETL
# ════════════════════════════════════════════════════════════

apps/pipeline/
├── models.py
│   └── JobExecutionLog       # Log de ejecuciones ETL
│
└── services.py
    └── ETLMonitoringService
        ├── check_execution_status()
        ├── get_last_execution()
        └── request_manual_retry()
```

---

### 25.3 Reglas de Arquitectura

```
REGLA CORE vs UTILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/ (Lógica base reutilizable):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Modelos abstractos (abstract=True)
✅ Mixins para ViewSets DRF
✅ Managers personalizados
✅ QuerySets personalizados

Ejemplos:
- TimeStampedModel → Herencia para TODOS los modelos
- SoftDeleteMixin → Herencia para TODOS los modelos
- SoftDeleteViewSetMixin → Herencia para ViewSets

apps/utils/ (Funciones + Clases helper):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Funciones helper (sin estado)
✅ Clases helper/utilidad (pagination, parsers, etc.)
✅ Excepciones personalizadas
✅ Decoradores

Ejemplos:
- get_client_ip() → Función helper
- format_phone() → Función helper
- StandardPagination → Clase helper
- ExportLimitExceeded → Exception

PREGUNTA CLAVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"¿Otros modelos HEREDAN de esto?"
  SÍ  → apps/core/
  NO  → apps/utils/ (si es función/helper)
```

---

### 25.4 Flujo de Datos IACT

```
ARQUITECTURA IACT v3.0.1:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ETL (Fuera de Django)
   ↓
   MariaDB (Tablas agregadas)
   ├─ historico_t1
   ├─ tbl_reporte_trimestral
   ├─ menu2
   ├─ tbl_reporte_llamadas_abandonadas
   └─ tbl_reporte_clientes_unicos

2. apps/ivr/ (READ-ONLY)
   ↓
   Modelos Django (managed=False):
   ├─ CallRecord → historico_t1
   ├─ QuarterlyReport → tbl_reporte_trimestral
   ├─ IVRMenu → menu2
   ├─ AbandonedCall → tbl_reporte_llamadas_abandonadas
   └─ UniqueClient → tbl_reporte_clientes_unicos

3. apps/reports/ (LÓGICA DE NEGOCIO)
   ↓
   ReportService:
   ├─ Consulta modelos de apps/ivr/
   ├─ Aplica validaciones (CNST-006, CNST-007)
   ├─ Calcula métricas
   └─ Sin filtros por usuario

4. apps/dashboard/ (VISUALIZACIÓN)
   ↓
   DashboardService:
   ├─ Agrega datos de múltiples fuentes
   ├─ Genera KPIs
   ├─ Crea widgets (Chart, KPI, Table)
   └─ Sin filtros por usuario

5. API REST (DRF)
   ↓
   ├─ ReportViewSet (/api/v1/reports/)
   ├─ DashboardViewSet (/api/v1/dashboard/)
   └─ RBAC controla ACCIONES (view, export, etc.)

REGLA CLAVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Todos los usuarios ven TODOS los datos
✅ RBAC controla QUÉ pueden HACER (view, export, delete)
❌ NO hay segmentación de datos por usuario/service
```

---

<a name="26-iact-service-layer-pattern"></a>
## 26. IACT: SERVICE LAYER PATTERN

### 26.1 Propósito del Service Layer

```
VIEW (Controller)
    ↓ Coordina
SERVICE (Lógica de Negocio)
    ↓ Usa
MODEL (Datos)

Responsabilidades:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View:
✅ Validar request (authentication, permissions)
✅ Serializar/deserializar datos
✅ Retornar response HTTP
❌ NO lógica de negocio
❌ NO queries complejas
❌ NO validaciones de negocio

Service:
✅ Lógica de negocio
✅ Validaciones de dominio
✅ Transacciones complejas
✅ Agregaciones de datos
✅ Interacción entre modelos
❌ NO conoce HTTP
❌ NO conoce serializers

Model:
✅ Estructura de datos
✅ Validaciones de campo
✅ Relaciones
❌ NO lógica compleja
❌ NO queries complejas
```

---

### 26.2 Nomenclatura de Services

```python
# ✅ CORRECTO - Service por app
# apps/reports/services.py

from apps.ivr.models import CallRecord, QuarterlyReport


class ReportService:
    """
    Servicio de lógica de negocio para reportes.
    
    Responsabilidades:
    - Obtener datos de reportes con filtros
    - Validar parámetros de fecha (CNST-006)
    - Generar archivos de exportación
    - Calcular métricas agregadas
    
    NO responsabilidades:
    - Serialización (lo hace el ViewSet)
    - Permisos RBAC (lo hace RequiresFunction)
    - Response HTTP (lo hace el ViewSet)
    """  # ← Español
    
    @staticmethod
    def get_quarterly_calls(quarter: str, did: str):
        """
        Obtiene llamadas trimestrales.
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3, Q4)
            did: DID a consultar
            
        Returns:
            QuerySet de CallRecord
            
        Raises:
            ValidationError: Si parámetros inválidos
        """  # ← Español
        
        # Validar parámetros
        ReportService._validate_quarter(quarter)
        ReportService._validate_did(did)
        
        # Query
        return CallRecord.objects.filter(
            quarter=quarter,
            did=did
        )
    
    @staticmethod
    def _validate_quarter(quarter: str):
        """
        Valida trimestre.
        
        Args:
            quarter: Trimestre a validar
            
        Raises:
            ValidationError: Si inválido
        """  # ← Español
        valid_quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        
        if quarter not in valid_quarters:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                f"Trimestre debe ser uno de: {', '.join(valid_quarters)}"
            )
    
    @staticmethod
    def _validate_did(did: str):
        """Valida DID."""  # ← Español
        valid_dids = ['Puebla', 'Nacional']
        
        if did not in valid_dids:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                f"DID debe ser uno de: {', '.join(valid_dids)}"
            )
    
    @staticmethod
    def calculate_abandonment_rate(total: int, abandoned: int) -> float:
        """
        Calcula tasa de abandono.
        
        Formula: (abandonadas / total) * 100
        
        Args:
            total: Total de llamadas
            abandoned: Llamadas abandonadas
            
        Returns:
            Tasa de abandono (0-100)
        """  # ← Español
        
        if total == 0:
            return 0.0
        
        rate = (abandoned / total) * 100
        return round(rate, 2)
    
    @staticmethod
    def get_quarterly_metrics(quarter: str, did: str):
        """
        Obtiene métricas trimestrales.
        
        Calcula:
        - Total de llamadas
        - Llamadas abandonadas
        - Tasa de abandono
        - Clientes únicos
        
        Returns:
            Dict con métricas
        """  # ← Español
        
        from apps.ivr.models import AbandonedCall, UniqueClient
        
        # Obtener datos
        calls = ReportService.get_quarterly_calls(quarter, did)
        total_calls = calls.count()
        
        abandoned = AbandonedCall.objects.filter(
            quarter=quarter,
            did=did
        ).count()
        
        unique_clients = UniqueClient.objects.filter(
            quarter=quarter,
            did=did
        ).count()
        
        # Calcular tasa
        rate = ReportService.calculate_abandonment_rate(
            total_calls,
            abandoned
        )
        
        return {
            'total_calls': total_calls,
            'abandoned_calls': abandoned,
            'abandonment_rate': rate,
            'unique_clients': unique_clients
        }


# ❌ INCORRECTO - Lógica en View
class ReportViewSet(viewsets.ModelViewSet):
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        # ❌ Lógica de negocio en View
        quarter = request.query_params.get('quarter')
        did = request.query_params.get('did')
        
        # ❌ Validaciones en View
        if quarter not in ['Q1', 'Q2', 'Q3', 'Q4']:
            return Response({"error": "..."}, status=400)
        
        # ❌ Queries complejas en View
        calls = CallRecord.objects.filter(...)
        # 50 líneas de lógica...
        
        return Response(data)
```

---

### 26.3 Uso del Service en ViewSet

```python
# apps/reports/views.py

from apps.reports.services import ReportService


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet delgado que delega a Service.
    
    Responsabilidades:
    - Validar permisos RBAC
    - Extraer parámetros de request
    - Llamar service
    - Serializar respuesta
    """  # ← Español
    
    permission_classes = [IsAuthenticated, RequiresFunction]
    required_function = 'reports.view'
    
    @action(detail=False, methods=['get'])
    def quarterly_metrics(self, request):
        """
        Obtiene métricas trimestrales.
        
        GET /reports/quarterly-metrics/?quarter=Q1&did=Puebla
        
        Returns:
            {
                "total_calls": 10000,
                "abandoned_calls": 800,
                "abandonment_rate": 8.0,
                "unique_clients": 4500
            }
        """  # ← Español
        
        # 1. Extraer parámetros
        quarter = request.query_params.get('quarter')
        did = request.query_params.get('did')
        
        if not quarter or not did:
            return Response(
                {"error": "Se requiere quarter y did"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Llamar service (toda la lógica está aquí)
        try:
            metrics = ReportService.get_quarterly_metrics(
                quarter=quarter,
                did=did
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Retornar (sin serializer porque es dict)
        return Response(metrics)
    
    @action(detail=False, methods=['post'])
    def export_excel(self, request):
        """Exporta datos a Excel."""  # ← Español
        
        # Extraer parámetros
        quarter = request.data.get('quarter')
        did = request.data.get('did')
        
        # Obtener datos via service
        calls = ReportService.get_quarterly_calls(quarter, did)
        
        # Validar límite (CNST-007)
        if calls.count() > 100000:
            raise ExportLimitExceeded(calls.count())
        
        # Generar archivo
        from apps.reports.services import ExportService
        file_url = ExportService.export_to_excel(calls)
        
        return Response({"file_url": file_url})
```

---

### 26.4 Service con Transacciones

```python
# apps/access/services.py

from django.db import transaction
from apps.access.models import UserFunctionAssignment, AccessLog
from apps.utils.exceptions import SeparationOfDutiesViolation


class AccessService:
    """Servicio de gestión de accesos RBAC."""  # ← Español
    
    @staticmethod
    @transaction.atomic
    def assign_function_to_user(
        user,
        function,
        assigned_by,
        justification
    ):
        """
        Asigna función a usuario (transacción).
        
        Pasos:
        1. Validar reglas SoD
        2. Crear asignación
        3. Registrar en log de auditoría
        
        Args:
            user: Usuario a asignar
            function: Función a asignar
            assigned_by: Usuario que asigna
            justification: Justificación
            
        Returns:
            UserFunctionAssignment creado
            
        Raises:
            SeparationOfDutiesViolation: Si viola SoD
        """  # ← Español
        
        # 1. Validar SoD
        violations = AccessService._check_sod_violations(user, function)
        if violations:
            raise SeparationOfDutiesViolation(
                function.function_id,
                violations
            )
        
        # 2. Crear asignación
        assignment = UserFunctionAssignment.objects.create(
            user=user,
            function=function,
            assigned_by=assigned_by,
            justification=justification,
            is_active=True
        )
        
        # 3. Auditar
        AccessLog.objects.create(
            user=assigned_by,
            action='ASSIGN_FUNCTION',
            target_user=user,
            function=function,
            details=justification
        )
        
        return assignment
    
    @staticmethod
    def _check_sod_violations(user, new_function):
        """
        Verifica violaciones de SoD.
        
        Returns:
            List de funciones en conflicto (vacía si no hay)
        """  # ← Español
        
        from apps.access.models import SeparationOfDuties
        from django.db.models import Q
        
        # Funciones actuales del usuario
        current_functions = UserFunctionAssignment.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False
        ).values_list('function__function_id', flat=True)
        
        # Reglas SoD que involucren la nueva función
        sod_rules = SeparationOfDuties.objects.filter(
            is_active=True,
            is_deleted=False
        ).filter(
            Q(function_1=new_function) | Q(function_2=new_function)
        )
        
        violations = []
        for rule in sod_rules:
            conflicting_id = (
                rule.function_2.function_id 
                if rule.function_1 == new_function 
                else rule.function_1.function_id
            )
            
            if conflicting_id in current_functions:
                violations.append(conflicting_id)
        
        return violations
```

---

### 26.5 DashboardService

```python
# apps/dashboard/services.py

from apps.ivr.models import CallRecord, AbandonedCall, UniqueClient
from apps.reports.services import ReportService


class DashboardService:
    """
    Servicio de lógica de negocio para dashboards.
    
    Responsabilidades:
    - Agregar datos de múltiples fuentes
    - Calcular KPIs
    - Generar datos para widgets
    """  # ← Español
    
    @staticmethod
    def get_quarterly_dashboard(quarter: str):
        """
        Obtiene datos de dashboard trimestral.
        
        Agrega datos de:
        - Puebla
        - Nacional
        - Top menús
        - Tendencias
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3, Q4)
            
        Returns:
            Dict con datos completos del dashboard
        """  # ← Español
        
        # Métricas por DID
        puebla_metrics = ReportService.get_quarterly_metrics(
            quarter=quarter,
            did='Puebla'
        )
        
        nacional_metrics = ReportService.get_quarterly_metrics(
            quarter=quarter,
            did='Nacional'
        )
        
        # Top menús
        top_menus = DashboardService._get_top_menus(quarter)
        
        return {
            'quarter': quarter,
            'kpis': {
                'total_calls': (
                    puebla_metrics['total_calls'] + 
                    nacional_metrics['total_calls']
                ),
                'abandonment_rate': (
                    (puebla_metrics['abandonment_rate'] + 
                     nacional_metrics['abandonment_rate']) / 2
                ),
                'unique_clients': (
                    puebla_metrics['unique_clients'] + 
                    nacional_metrics['unique_clients']
                )
            },
            'by_did': {
                'puebla': puebla_metrics,
                'nacional': nacional_metrics
            },
            'top_menus': top_menus
        }
    
    @staticmethod
    def _get_top_menus(quarter: str, limit: int = 10):
        """
        Obtiene top menús por número de llamadas.
        
        Args:
            quarter: Trimestre
            limit: Cantidad de menús (default: 10)
        """  # ← Español
        
        from django.db.models import Count
        
        top = CallRecord.objects.filter(
            quarter=quarter
        ).values('menu').annotate(
            call_count=Count('call_id')
        ).order_by('-call_count')[:limit]
        
        return list(top)


class WidgetService:
    """
    Servicio para generación de widgets.
    
    Widgets soportados:
    - KPI: Valor único con cambio %
    - Chart: Gráfica (bar, line, pie)
    - Table: Tabla de datos
    """  # ← Español
    
    @staticmethod
    def generate_kpi_widget(title: str, value, change: float = None):
        """
        Genera widget de KPI.
        
        Args:
            title: Título del KPI
            value: Valor actual
            change: Cambio porcentual vs periodo anterior
            
        Returns:
            Dict con datos del widget
        """  # ← Español
        
        return {
            'type': 'kpi',
            'title': title,
            'value': value,
            'change': change
        }
    
    @staticmethod
    def generate_chart_widget(
        title: str,
        chart_type: str,
        data: list,
        labels: list = None
    ):
        """
        Genera widget de gráfica.
        
        Args:
            title: Título de la gráfica
            chart_type: Tipo (bar, line, pie)
            data: Datos a graficar
            labels: Etiquetas (opcional)
        """  # ← Español
        
        return {
            'type': 'chart',
            'chart_type': chart_type,
            'title': title,
            'data': data,
            'labels': labels or []
        }
```

---

<a name="27-iact-modelos-herencia"></a>
## 27. IACT: MODELOS Y HERENCIA

### 27.1 Patrón de Herencia Estándar

```python
# ✅ CORRECTO - Herencia múltiple con orden correcto

from django.db import models
from apps.core.models import SoftDeleteMixin, TimeStampedModel  # ← De core/


class Report(SoftDeleteMixin, TimeStampedModel, models.Model):
    """
    Modelo de reporte.
    
    Orden de herencia (IMPORTANTE):
    1. SoftDeleteMixin (primero)
    2. TimeStampedModel (segundo)
    3. models.Model (último)
    
    Campos heredados:
    - SoftDeleteMixin: is_deleted, deleted_at, deleted_by
    - TimeStampedModel: created_at, updated_at
    
    CNST-005: TODOS los modelos IACT heredan estos mixins.
    """  # ← Español
    
    # Campos específicos
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='reports',
        verbose_name="Propietario"
    )
    
    class Meta:
        db_table = 'reports'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['is_deleted', '-created_at']),
        ]
    
    def __str__(self):
        return self.name


# ❌ INCORRECTO - Sin mixins
class Report(models.Model):
    name = models.CharField()
    created_at = models.DateTimeField()  # ❌ Duplica TimeStampedModel
    updated_at = models.DateTimeField()  # ❌ Duplica TimeStampedModel
    # ❌ Falta soft delete (viola CNST-005)


# ❌ INCORRECTO - Orden invertido
class Report(models.Model, TimeStampedModel, SoftDeleteMixin):
    # ❌ models.Model debe ir AL FINAL
    pass
```

---

### 27.2 Modelos IVR con db_table (READ-ONLY)

```python
# apps/ivr/models.py

from django.db import models


# ✅ CallRecord - Nombre en inglés, mapea a tabla legacy
class CallRecord(models.Model):
    """
    Registro histórico de llamadas del IVR.
    
    Mapea a tabla: historico_t1 (creada por ETL)
    
    Cada registro representa una llamada procesada
    por el sistema IVR con metadata completa.
    
    IMPORTANTE:
    - managed=False: Django NO maneja esta tabla
    - Tabla creada y mantenida por ETL
    - Solo lectura desde Django
    """  # ← Español
    
    call_id = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='id_llamada',  # ← Columna en DB
        verbose_name="ID de llamada"
    )
    
    did = models.CharField(
        max_length=20,
        db_column='did',
        verbose_name="DID"
    )
    
    menu = models.CharField(
        max_length=100,
        db_column='menu',
        verbose_name="Menú navegado"
    )
    
    timestamp = models.DateTimeField(
        db_column='fecha_hora',
        verbose_name="Fecha y hora"
    )
    
    duration = models.IntegerField(
        db_column='duracion',
        verbose_name="Duración (segundos)"
    )
    
    class Meta:
        db_table = 'historico_t1'  # ← Tabla real en MariaDB
        managed = False  # ← Django NO maneja
        verbose_name = 'Registro de llamada'
        verbose_name_plural = 'Registros de llamadas'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Call {self.call_id}"


# ✅ QuarterlyReport - Nombre en inglés, mapea a tabla legacy
class QuarterlyReport(models.Model):
    """
    Reporte trimestral agregado.
    
    Mapea a: tbl_reporte_trimestral (creada por ETL)
    
    Contiene datos agregados por trimestre y DID
    calculados por el ETL en MariaDB.
    """  # ← Español
    
    report_id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    
    quarter = models.CharField(
        max_length=10,
        db_column='trimestre',
        verbose_name="Trimestre"
    )
    
    did = models.CharField(
        max_length=50,
        db_column='did',
        verbose_name="DID"
    )
    
    total_calls = models.IntegerField(
        db_column='total_llamadas',
        verbose_name="Total de llamadas"
    )
    
    abandoned_calls = models.IntegerField(
        db_column='llamadas_abandonadas',
        verbose_name="Llamadas abandonadas"
    )
    
    class Meta:
        db_table = 'tbl_reporte_trimestral'
        managed = False
        verbose_name = 'Reporte trimestral'
        verbose_name_plural = 'Reportes trimestrales'
        ordering = ['-quarter']
    
    def __str__(self):
        return f"{self.quarter} - {self.did}"


# ✅ IVRMenu - Prefijo "IVR" porque "Menu" es genérico
class IVRMenu(models.Model):
    """
    Menú del sistema IVR.
    
    Mapea a: menu2 (creada por ETL)
    
    Prefijo "IVR" para evitar confusión con otros
    tipos de menús en el sistema.
    """  # ← Español
    
    menu_id = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='id_menu',
        verbose_name="ID de menú"
    )
    
    name = models.CharField(
        max_length=200,
        db_column='nombre',
        verbose_name="Nombre"
    )
    
    description = models.TextField(
        db_column='descripcion',
        verbose_name="Descripción"
    )
    
    class Meta:
        db_table = 'menu2'  # ← Tabla real
        managed = False
        verbose_name = 'Menú IVR'
        verbose_name_plural = 'Menús IVR'
    
    def __str__(self):
        return self.name
```

---

### 27.3 Manager Personalizado

```python
# apps/reports/models.py

from django.db import models
from apps.core.models import SoftDeleteMixin, TimeStampedModel


class ReportManager(models.Manager):
    """Manager con métodos convenientes."""  # ← Español
    
    def active(self):
        """Reportes activos (no eliminados)."""
        return self.filter(is_deleted=False)
    
    def deleted(self):
        """Reportes eliminados."""
        return self.filter(is_deleted=True)
    
    def by_owner(self, user):
        """Reportes de un usuario específico."""
        return self.active().filter(owner=user)
    
    def recent(self, days=7):
        """Reportes creados en últimos N días."""
        from django.utils import timezone
        from datetime import timedelta
        
        threshold = timezone.now() - timedelta(days=days)
        return self.active().filter(created_at__gte=threshold)


class Report(SoftDeleteMixin, TimeStampedModel, models.Model):
    """Modelo con manager personalizado."""  # ← Español
    
    name = models.CharField(max_length=200)
    owner = models.ForeignKey('users.User', on_delete=models.PROTECT)
    
    # Manager personalizado
    objects = ReportManager()
    
    class Meta:
        db_table = 'reports'


# Uso:
Report.objects.active()           # Solo activos
Report.objects.deleted()          # Solo eliminados
Report.objects.by_owner(user)     # De un usuario
Report.objects.recent(days=30)    # Últimos 30 días
```

---

### 27.4 Modelo con Choices

```python
class Report(SoftDeleteMixin, TimeStampedModel, models.Model):
    """Modelo con choices."""  # ← Español
    
    # ✅ CORRECTO - Choices con TextChoices
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'          # key inglés, label español
        PENDING = 'pending', 'Pendiente'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Baja'
        MEDIUM = 'medium', 'Media'
        HIGH = 'high', 'Alta'
        URGENT = 'urgent', 'Urgente'
    
    name = models.CharField(max_length=200)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado"
    )
    
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Prioridad"
    )
    
    class Meta:
        db_table = 'reports'


# ❌ INCORRECTO - Choices en español (keys)
class Status(models.TextChoices):
    BORRADOR = 'borrador', 'Borrador'  # ❌ Key debe ser inglés
    PENDIENTE = 'pendiente', 'Pendiente'
```

---

### 27.5 Modelo con Validaciones Custom

```python
from django.core.exceptions import ValidationError


class Report(SoftDeleteMixin, TimeStampedModel, models.Model):
    """Modelo con validaciones custom."""  # ← Español
    
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    
    class Meta:
        db_table = 'reports'
    
    def clean(self):
        """
        Validación a nivel de modelo.
        
        Llamado automáticamente por forms y admin.
        También puede llamarse manualmente: instance.clean()
        
        Raises:
            ValidationError: Si datos inválidos
        """  # ← Español
        super().clean()
        
        # Validar fechas
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'Fecha fin debe ser posterior a fecha inicio'
                })
            
            # Validar rango máximo (CNST-006)
            days_diff = (self.end_date - self.start_date).days
            if days_diff > 730:
                raise ValidationError(
                    f"Rango máximo 2 años (CNST-006). "
                    f"Rango: {days_diff} días"
                )
    
    def save(self, *args, **kwargs):
        """
        Override save para ejecutar validaciones.
        
        IMPORTANTE: clean() NO se ejecuta automáticamente.
        Debemos llamarlo explícitamente.
        """  # ← Español
        
        # Ejecutar validaciones
        self.full_clean()
        
        super().save(*args, **kwargs)
```

---

**FIN DE PARTE 4/5**

**Continúa en:** CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_5.md

---

## ✅ RESUMEN PARTE 4

**Secciones completadas:**
- ✅ 24. DRF: Renderers, Parsers, Pagination
  - StandardPagination, LargePagination (OK en utils/)
- ✅ 25. IACT: Arquitectura apps/core/ vs apps/utils/
  - apps/core/ modelos abstractos + mixins ViewSet (CORRECTO)
  - apps/utils/ funciones + clases helper (CORRECTO)
  - apps/dashboard/ incluido
- ✅ 26. IACT: Service Layer Pattern
  - ReportService completo
  - DashboardService
  - WidgetService
  - AccessService con transacciones
- ✅ 27. IACT: Modelos y Herencia
  - CallRecord, QuarterlyReport, IVRMenu con db_table
  - Managers personalizados
  - Choices, validaciones

**Correcciones arquitectónicas v3.0.1:**
- ✅ apps/core/ NO deprecado (fundamental)
- ✅ TimeStampedModel en apps/core/ (antes en utils/)
- ✅ SoftDeleteMixin en apps/core/ (antes en utils/)
- ✅ SoftDeleteViewSetMixin en apps/core/ (antes en utils/)
- ✅ Pagination classes OK en apps/utils/ (helper)

**Modelos corregidos aplicados:**
- ✅ CallRecord (antes HistoricoT1)
- ✅ QuarterlyReport (antes ReporteTrimestral)
- ✅ IVRMenu (antes Menu2)
- ✅ AbandonedCall, UniqueClient
- ✅ apps/ivr/ (antes ivr_legacy)
- ✅ apps/dashboard/ (nueva app)

**Próxima parte:** Anti-patterns, Tabla Resumen, Referencias, Changelog v3.0.1
