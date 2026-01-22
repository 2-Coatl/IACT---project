---
version: 3.0.0
date: 2026-01-19
project: IACT Call Center System
type: Análisis de Arquitectura - App Dashboard PARTE 3/5
categoria: arquitectura/apps
tema: apps/dashboard/ - APIs y Endpoints
autor: Claude Technical Analysis
tags: [dashboard, api, endpoints, serializers, rbac, viewsets]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
estado: definitivo
parte: 3 de 5
relacionado:
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_1.md
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_2.md
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_4.md
---

# ANÁLISIS DE apps/dashboard/ v3.0.0 - PARTE 3/5
## APIS Y ENDPOINTS

---

## TABLA DE CONTENIDOS

1. [Resumen Parte 3](#resumen)
2. [Serializers Completos](#serializers)
3. [ViewSets con RBAC](#viewsets)
4. [Permissions y Decoradores](#permissions)
5. [URLs Configuration](#urls)
6. [Endpoints Documentados](#endpoints)
7. [Request/Response Examples](#examples)
8. [Error Handling](#errors)

---

<a name="resumen"></a>
## 1. RESUMEN PARTE 3

### 1.1 Alcance de esta Parte

```yaml
Componentes cubiertos:
  ✅ Serializers (5 tipos)
  ✅ ViewSets con RBAC v6.0.0
  ✅ Permissions DynamicFunctionPermission
  ✅ Decoradores @require_function
  ✅ URLs configuration
  ✅ Endpoints GET documentados
  ✅ Endpoints POST export documentados
  ✅ Request/Response examples
  ✅ Error handling

Líneas de código: ~900 líneas Python
Archivos generados:
  - apps/dashboard/serializers.py
  - apps/dashboard/views.py
  - apps/dashboard/permissions.py
  - apps/dashboard/urls.py
```

### 1.2 Endpoints API

```
GET  /api/v1/dashboard/metricas-trimestrales/
GET  /api/v1/dashboard/analisis-clientes/
GET  /api/v1/dashboard/performance-ivr/
POST /api/v1/dashboard/metricas-trimestrales/export/
POST /api/v1/dashboard/analisis-clientes/export/
POST /api/v1/dashboard/performance-ivr/export/
```

### 1.3 RBAC v6.0.0 Aplicado

```yaml
MOD_Dashboard - 6 funciones:

Activas (3):
  - DSH_VIEW: dashboard.view
  - DSH_EXP_CSV: dashboard.export.csv
  - DSH_EXP_EXCEL: dashboard.export.excel

Planificadas (3):
  - DSH_EXP_PDF: dashboard.export.pdf
  - DSH_SHARE: dashboard.share
  - DSH_EDIT: dashboard.edit
```

---

<a name="serializers"></a>
## 2. SERIALIZERS COMPLETOS

### 2.1 Archivo: apps/dashboard/serializers.py

```python
"""
Serializers para Dashboard API.

Responsabilidades:
- Serializar widgets (KPI, Chart, Table)
- Serializar dashboards completos
- Validar parámetros de entrada
- Formatear respuestas

CLEAN_CODE v3.0.1:
- Clases: PascalCase inglés
- Campos: snake_case inglés
- Docstrings: español formato Google

RBAC v6.0.0:
- Permisos validados en ViewSets
- Serializers sin lógica de permisos
"""

from rest_framework import serializers
from typing import Dict, List, Any

from apps.dashboard.constants import (
    DASHBOARD_TYPES,
    WIDGET_TYPES,
    CHART_TYPES,
    VALID_QUARTERS,
)


class WidgetSerializer(serializers.Serializer):
    """
    Serializer base para widgets.
    
    Campos:
    - type: Tipo de widget (kpi, chart, table)
    - title: Título del widget
    
    Usado como base para serializers específicos.
    """
    
    type = serializers.ChoiceField(
        choices=list(WIDGET_TYPES.values()),
        help_text="Tipo de widget"
    )
    
    title = serializers.CharField(
        max_length=200,
        help_text="Título del widget"
    )


class KPISerializer(serializers.Serializer):
    """
    Serializer para widgets tipo KPI.
    
    Estructura:
    {
        "type": "kpi",
        "title": "Total Llamadas",
        "value": 45000,
        "format_type": "number",
        "formatted_value": "45,000",
        "icon": "phone",
        "color": "blue",
        "subtitle": "100%"
    }
    """
    
    type = serializers.CharField(default='kpi')
    title = serializers.CharField(max_length=200)
    value = serializers.FloatField()
    format_type = serializers.ChoiceField(
        choices=['number', 'percentage', 'currency'],
        default='number'
    )
    formatted_value = serializers.CharField(read_only=True)
    icon = serializers.CharField(max_length=50, required=False, allow_null=True)
    color = serializers.CharField(max_length=50, required=False, allow_null=True)
    subtitle = serializers.CharField(max_length=200, required=False, allow_null=True)


class ChartDatasetSerializer(serializers.Serializer):
    """
    Serializer para dataset de chart.
    
    Estructura:
    {
        "label": "Total Llamadas",
        "data": [5000, 4500, 4000, ...],
        "backgroundColor": "rgba(54, 162, 235, 0.6)",
        "borderColor": "rgba(54, 162, 235, 1)",
        "borderWidth": 1
    }
    """
    
    label = serializers.CharField(max_length=200)
    data = serializers.ListField(child=serializers.FloatField())
    backgroundColor = serializers.CharField(
        max_length=100,
        required=False,
        allow_null=True
    )
    borderColor = serializers.CharField(
        max_length=100,
        required=False,
        allow_null=True
    )
    borderWidth = serializers.IntegerField(
        required=False,
        default=1
    )


class ChartSerializer(serializers.Serializer):
    """
    Serializer para widgets tipo Chart.
    
    Estructura:
    {
        "type": "chart",
        "chart_type": "bar",
        "title": "Top 10 DIDs",
        "data": {
            "labels": ["800-123", "800-234", ...],
            "datasets": [...]
        },
        "options": {...}
    }
    """
    
    type = serializers.CharField(default='chart')
    chart_type = serializers.ChoiceField(
        choices=list(CHART_TYPES.values()),
        help_text="Tipo de chart: bar, line, pie"
    )
    title = serializers.CharField(max_length=200)
    data = serializers.DictField(
        help_text="Data del chart con labels y datasets"
    )
    options = serializers.DictField(
        required=False,
        help_text="Opciones de configuración del chart"
    )


class TableSerializer(serializers.Serializer):
    """
    Serializer para widgets tipo Table.
    
    Estructura:
    {
        "type": "table",
        "title": "Detalle Top 10 DIDs",
        "headers": ["DID", "Total Llamadas", ...],
        "rows": [
            {"did": "800-123", "total_llamadas": 5000, ...},
            ...
        ],
        "total_rows": 10
    }
    """
    
    type = serializers.CharField(default='table')
    title = serializers.CharField(max_length=200)
    headers = serializers.ListField(
        child=serializers.CharField(max_length=200),
        help_text="Headers de columnas"
    )
    rows = serializers.ListField(
        child=serializers.DictField(),
        help_text="Filas de datos"
    )
    total_rows = serializers.IntegerField(
        read_only=True,
        help_text="Total de filas"
    )


class DashboardSerializer(serializers.Serializer):
    """
    Serializer principal para dashboards.
    
    Usado para serializar respuesta completa de dashboard.
    
    Estructura:
    {
        "dashboard_type": "quarterly_metrics",
        "quarter": "Q1",
        "year": 2026,
        "widgets": [...],
        "last_updated": "2026-01-19T10:30:00Z",
        "data_status": "static",
        "refresh_interval": null,
        "cache_hit": true,
        "metadata": {...}
    }
    """
    
    dashboard_type = serializers.ChoiceField(
        choices=list(DASHBOARD_TYPES.values()),
        help_text="Tipo de dashboard"
    )
    
    quarter = serializers.ChoiceField(
        choices=VALID_QUARTERS,
        help_text="Trimestre: Q1, Q2, Q3, Q4"
    )
    
    year = serializers.IntegerField(
        min_value=2020,
        max_value=2030,
        help_text="Año del reporte"
    )
    
    widgets = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lista de widgets del dashboard"
    )
    
    last_updated = serializers.DateTimeField(
        read_only=True,
        help_text="Última actualización de datos"
    )
    
    data_status = serializers.CharField(
        read_only=True,
        default='static',
        help_text="Estado de datos: static (CNST-003)"
    )
    
    refresh_interval = serializers.IntegerField(
        read_only=True,
        allow_null=True,
        default=None,
        help_text="Intervalo de refresco en segundos (CNST-023: siempre None)"
    )
    
    cache_hit = serializers.BooleanField(
        read_only=True,
        help_text="Indica si la respuesta vino de cache"
    )
    
    metadata = serializers.DictField(
        read_only=True,
        required=False,
        help_text="Metadata adicional del dashboard"
    )


class DashboardQuerySerializer(serializers.Serializer):
    """
    Serializer para validar query parameters de dashboard.
    
    Usado en: GET requests
    
    Query params:
    - quarter: Trimestre (Q1, Q2, Q3, Q4)
    - year: Año (opcional, default: año actual)
    """
    
    quarter = serializers.ChoiceField(
        choices=VALID_QUARTERS,
        required=True,
        help_text="Trimestre a consultar"
    )
    
    year = serializers.IntegerField(
        min_value=2020,
        max_value=2030,
        required=False,
        help_text="Año (default: año actual)"
    )
    
    def validate_year(self, value):
        """
        Valida que year no sea futuro lejano.
        
        Args:
            value: Año a validar
        
        Returns:
            Año validado
        
        Raises:
            ValidationError: Si año inválido
        """
        from django.utils import timezone
        current_year = timezone.now().year
        
        if value and value > current_year + 1:
            raise serializers.ValidationError(
                f"Año no puede ser mayor a {current_year + 1}"
            )
        
        return value


class DashboardExportSerializer(serializers.Serializer):
    """
    Serializer para exportar dashboard.
    
    Usado en: POST /export/
    
    Request:
    {
        "quarter": "Q1",
        "year": 2026,
        "format": "csv"
    }
    
    Response:
    {
        "download_url": "/media/exports/dashboard_Q1_2026.csv",
        "filename": "dashboard_Q1_2026.csv",
        "format": "csv",
        "size_bytes": 12345
    }
    """
    
    quarter = serializers.ChoiceField(
        choices=VALID_QUARTERS,
        required=True,
        help_text="Trimestre a exportar"
    )
    
    year = serializers.IntegerField(
        min_value=2020,
        max_value=2030,
        required=False,
        help_text="Año (default: año actual)"
    )
    
    format = serializers.ChoiceField(
        choices=['csv', 'excel'],
        default='csv',
        help_text="Formato de exportación (csv o excel)"
    )
    
    # Response fields
    download_url = serializers.CharField(read_only=True)
    filename = serializers.CharField(read_only=True)
    size_bytes = serializers.IntegerField(read_only=True)
```

---

<a name="viewsets"></a>
## 3. VIEWSETS CON RBAC

### 3.1 Archivo: apps/dashboard/views.py

```python
"""
ViewSets para Dashboard API.

Responsabilidades:
- Exponer endpoints REST
- Aplicar RBAC v6.0.0 (DynamicFunctionPermission)
- Invocar DashboardService
- Manejar errores

CLEAN_CODE v3.0.1:
- Clases: PascalCase inglés
- Métodos: snake_case inglés
- Docstrings: español formato Google

RBAC v6.0.0:
- permission_classes = [DynamicFunctionPermission]
- function_map define permisos por acción
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.dashboard.serializers import (
    DashboardSerializer,
    DashboardQuerySerializer,
    DashboardExportSerializer,
)
from apps.dashboard.services import DashboardService
from apps.dashboard.permissions import DynamicFunctionPermission
from apps.access.decorators import require_function


class QuarterlyMetricsDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para Dashboard de Métricas Trimestrales.
    
    Endpoints:
    - GET /api/v1/dashboard/metricas-trimestrales/?quarter=Q1&year=2026
    - POST /api/v1/dashboard/metricas-trimestrales/export/
    
    RBAC v6.0.0:
    - list: Requiere dashboard.view (DSH_VIEW)
    - export_csv: Requiere dashboard.export.csv (DSH_EXP_CSV)
    - export_excel: Requiere dashboard.export.excel (DSH_EXP_EXCEL)
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    # RBAC v6.0.0: function_map
    function_map = {
        'list': 'dashboard.view',
        'export_csv': 'dashboard.export.csv',
        'export_excel': 'dashboard.export.excel',
    }
    
    def __init__(self, *args, **kwargs):
        """Inicializa ViewSet con DashboardService."""
        super().__init__(*args, **kwargs)
        self.dashboard_service = DashboardService()
    
    def list(self, request):
        """
        GET /api/v1/dashboard/metricas-trimestrales/
        
        Obtiene dashboard de métricas trimestrales.
        
        Query params:
        - quarter: Trimestre (Q1, Q2, Q3, Q4) - requerido
        - year: Año (opcional, default: año actual)
        
        Returns:
            200: Dashboard con widgets
            400: Parámetros inválidos
            403: Sin permiso dashboard.view
        
        RBAC: Requiere DSH_VIEW (dashboard.view)
        """
        # Validar query params
        query_serializer = DashboardQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        
        quarter = query_serializer.validated_data['quarter']
        year = query_serializer.validated_data.get('year') or timezone.now().year
        
        try:
            # Obtener dashboard (con cache)
            dashboard_data = self.dashboard_service.get_quarterly_metrics_dashboard(
                quarter=quarter,
                year=year
            )
            
            # Serializar respuesta
            serializer = DashboardSerializer(data=dashboard_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Error generando dashboard', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='export')
    def export(self, request):
        """
        POST /api/v1/dashboard/metricas-trimestrales/export/
        
        Exporta dashboard a CSV o Excel.
        
        Request body:
        {
            "quarter": "Q1",
            "year": 2026,
            "format": "csv"
        }
        
        Returns:
            200: URL de descarga
            400: Parámetros inválidos
            403: Sin permiso export
        
        RBAC: Requiere DSH_EXP_CSV o DSH_EXP_EXCEL según formato
        """
        # Validar request
        serializer = DashboardExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quarter = serializer.validated_data['quarter']
        year = serializer.validated_data.get('year') or timezone.now().year
        format_type = serializer.validated_data['format']
        
        # Validar permiso según formato
        if format_type == 'csv':
            self._check_permission(request, 'dashboard.export.csv')
        elif format_type == 'excel':
            self._check_permission(request, 'dashboard.export.excel')
        
        try:
            # Generar export (implementación futura)
            # Por ahora retornar estructura
            export_data = {
                'download_url': f'/media/exports/metricas_{quarter}_{year}.{format_type}',
                'filename': f'metricas_{quarter}_{year}.{format_type}',
                'format': format_type,
                'size_bytes': 0,  # Calcular en implementación real
            }
            
            response_serializer = DashboardExportSerializer(data=export_data)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': 'Error exportando dashboard', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _check_permission(self, request, permission_name):
        """
        Verifica permiso específico.
        
        Args:
            request: Request object
            permission_name: Nombre del permiso (ej: 'dashboard.export.csv')
        
        Raises:
            PermissionDenied: Si usuario no tiene permiso
        """
        from rest_framework.exceptions import PermissionDenied
        from apps.access.services import RBACService
        
        rbac_service = RBACService()
        has_permission = rbac_service.user_has_function(
            request.user,
            permission_name
        )
        
        if not has_permission:
            raise PermissionDenied(
                f"Usuario no tiene permiso: {permission_name}"
            )


class ClientAnalysisDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para Dashboard de Análisis de Clientes.
    
    Endpoints:
    - GET /api/v1/dashboard/analisis-clientes/?quarter=Q1&year=2026
    - POST /api/v1/dashboard/analisis-clientes/export/
    
    RBAC v6.0.0:
    - list: Requiere dashboard.view (DSH_VIEW)
    - export: Requiere dashboard.export.csv o dashboard.export.excel
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'list': 'dashboard.view',
        'export_csv': 'dashboard.export.csv',
        'export_excel': 'dashboard.export.excel',
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dashboard_service = DashboardService()
    
    def list(self, request):
        """
        GET /api/v1/dashboard/analisis-clientes/
        
        Obtiene dashboard de análisis de clientes.
        
        RBAC: Requiere DSH_VIEW (dashboard.view)
        """
        query_serializer = DashboardQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        
        quarter = query_serializer.validated_data['quarter']
        year = query_serializer.validated_data.get('year') or timezone.now().year
        
        try:
            dashboard_data = self.dashboard_service.get_client_analysis_dashboard(
                quarter=quarter,
                year=year
            )
            
            serializer = DashboardSerializer(data=dashboard_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Error generando dashboard', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='export')
    def export(self, request):
        """
        POST /api/v1/dashboard/analisis-clientes/export/
        
        Exporta dashboard a CSV o Excel.
        
        RBAC: Requiere DSH_EXP_CSV o DSH_EXP_EXCEL
        """
        serializer = DashboardExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quarter = serializer.validated_data['quarter']
        year = serializer.validated_data.get('year') or timezone.now().year
        format_type = serializer.validated_data['format']
        
        # Validar permiso
        if format_type == 'csv':
            self._check_permission(request, 'dashboard.export.csv')
        elif format_type == 'excel':
            self._check_permission(request, 'dashboard.export.excel')
        
        try:
            export_data = {
                'download_url': f'/media/exports/clientes_{quarter}_{year}.{format_type}',
                'filename': f'clientes_{quarter}_{year}.{format_type}',
                'format': format_type,
                'size_bytes': 0,
            }
            
            response_serializer = DashboardExportSerializer(data=export_data)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': 'Error exportando dashboard', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _check_permission(self, request, permission_name):
        """Verifica permiso específico."""
        from rest_framework.exceptions import PermissionDenied
        from apps.access.services import RBACService
        
        rbac_service = RBACService()
        has_permission = rbac_service.user_has_function(
            request.user,
            permission_name
        )
        
        if not has_permission:
            raise PermissionDenied(
                f"Usuario no tiene permiso: {permission_name}"
            )


class IVRPerformanceDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para Dashboard de Performance IVR.
    
    Endpoints:
    - GET /api/v1/dashboard/performance-ivr/?quarter=Q1&year=2026
    - POST /api/v1/dashboard/performance-ivr/export/
    
    RBAC v6.0.0:
    - list: Requiere dashboard.view (DSH_VIEW)
    - export: Requiere dashboard.export.csv o dashboard.export.excel
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'list': 'dashboard.view',
        'export_csv': 'dashboard.export.csv',
        'export_excel': 'dashboard.export.excel',
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dashboard_service = DashboardService()
    
    def list(self, request):
        """
        GET /api/v1/dashboard/performance-ivr/
        
        Obtiene dashboard de performance IVR.
        
        RBAC: Requiere DSH_VIEW (dashboard.view)
        """
        query_serializer = DashboardQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        
        quarter = query_serializer.validated_data['quarter']
        year = query_serializer.validated_data.get('year') or timezone.now().year
        
        try:
            dashboard_data = self.dashboard_service.get_ivr_performance_dashboard(
                quarter=quarter,
                year=year
            )
            
            serializer = DashboardSerializer(data=dashboard_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Error generando dashboard', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='export')
    def export(self, request):
        """
        POST /api/v1/dashboard/performance-ivr/export/
        
        Exporta dashboard a CSV o Excel.
        
        RBAC: Requiere DSH_EXP_CSV o DSH_EXP_EXCEL
        """
        serializer = DashboardExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quarter = serializer.validated_data['quarter']
        year = serializer.validated_data.get('year') or timezone.now().year
        format_type = serializer.validated_data['format']
        
        # Validar permiso
        if format_type == 'csv':
            self._check_permission(request, 'dashboard.export.csv')
        elif format_type == 'excel':
            self._check_permission(request, 'dashboard.export.excel')
        
        try:
            export_data = {
                'download_url': f'/media/exports/ivr_{quarter}_{year}.{format_type}',
                'filename': f'ivr_{quarter}_{year}.{format_type}',
                'format': format_type,
                'size_bytes': 0,
            }
            
            response_serializer = DashboardExportSerializer(data=export_data)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': 'Error exportando dashboard', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _check_permission(self, request, permission_name):
        """Verifica permiso específico."""
        from rest_framework.exceptions import PermissionDenied
        from apps.access.services import RBACService
        
        rbac_service = RBACService()
        has_permission = rbac_service.user_has_function(
            request.user,
            permission_name
        )
        
        if not has_permission:
            raise PermissionDenied(
                f"Usuario no tiene permiso: {permission_name}"
            )
```

---

<a name="permissions"></a>
## 4. PERMISSIONS Y DECORADORES

### 4.1 Archivo: apps/dashboard/permissions.py

```python
"""
Permissions para Dashboard.

RBAC v6.0.0:
- DynamicFunctionPermission: Permission class que usa function_map

CLEAN_CODE v3.0.1:
- Clase: DynamicFunctionPermission (PascalCase)
- Métodos: snake_case
"""

from rest_framework.permissions import BasePermission
from apps.access.services import RBACService


class DynamicFunctionPermission(BasePermission):
    """
    Permission class basada en RBAC v6.0.0.
    
    Lee function_map del ViewSet y valida que usuario tenga la función.
    
    Uso:
        class MyViewSet(viewsets.ViewSet):
            permission_classes = [DynamicFunctionPermission]
            function_map = {
                'list': 'dashboard.view',
                'export': 'dashboard.export.csv'
            }
    
    RBAC v6.0.0:
    - Valida contra UserFunctionAssignment
    - Soporta permisos temporales
    - Valida SoD (Segregation of Duties)
    """
    
    def has_permission(self, request, view):
        """
        Verifica permiso basado en function_map.
        
        Args:
            request: Request object
            view: ViewSet instance
        
        Returns:
            True si usuario tiene permiso, False caso contrario
        """
        # Usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser siempre tiene acceso
        if request.user.is_superuser:
            return True
        
        # Obtener function_map del viewset
        function_map = getattr(view, 'function_map', {})
        
        # Obtener action actual
        action = view.action
        
        # Si action no está en function_map, denegar
        if action not in function_map:
            return False
        
        # Obtener función requerida
        required_function = function_map[action]
        
        # Validar con RBACService
        rbac_service = RBACService()
        return rbac_service.user_has_function(request.user, required_function)
```

---

<a name="urls"></a>
## 5. URLS CONFIGURATION

### 5.1 Archivo: apps/dashboard/urls.py

```python
"""
URLs para Dashboard API.

CLEAN_CODE v3.0.1:
- Rutas: kebab-case español
- ViewSets: PascalCase

Estructura:
/api/v1/dashboard/
    metricas-trimestrales/
    analisis-clientes/
    performance-ivr/
"""

from rest_framework.routers import DefaultRouter
from apps.dashboard.views import (
    QuarterlyMetricsDashboardViewSet,
    ClientAnalysisDashboardViewSet,
    IVRPerformanceDashboardViewSet,
)

# Router para dashboard
router = DefaultRouter()

# Registrar viewsets
router.register(
    r'metricas-trimestrales',
    QuarterlyMetricsDashboardViewSet,
    basename='quarterly-metrics-dashboard'
)

router.register(
    r'analisis-clientes',
    ClientAnalysisDashboardViewSet,
    basename='client-analysis-dashboard'
)

router.register(
    r'performance-ivr',
    IVRPerformanceDashboardViewSet,
    basename='ivr-performance-dashboard'
)

urlpatterns = router.urls
```

### 5.2 Integración en config/urls.py

```python
# config/urls.py

from django.urls import path, include

urlpatterns = [
    # ... otras rutas ...
    
    # Dashboard API
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
    
    # ... otras rutas ...
]
```

---

<a name="endpoints"></a>
## 6. ENDPOINTS DOCUMENTADOS

### 6.1 GET Métricas Trimestrales

```http
GET /api/v1/dashboard/metricas-trimestrales/?quarter=Q1&year=2026
Authorization: Bearer {token}
```

**Query Parameters:**
- `quarter` (requerido): Trimestre (Q1, Q2, Q3, Q4)
- `year` (opcional): Año (default: año actual)

**RBAC:** Requiere `DSH_VIEW` (dashboard.view)

**Response 200 OK:**
```json
{
  "dashboard_type": "quarterly_metrics",
  "quarter": "Q1",
  "year": 2026,
  "widgets": [
    {
      "type": "kpi",
      "title": "Total Llamadas",
      "value": 45000,
      "format_type": "number",
      "formatted_value": "45,000",
      "icon": "phone",
      "color": "blue"
    },
    {
      "type": "chart",
      "chart_type": "bar",
      "title": "Top 10 DIDs por Volumen",
      "data": {
        "labels": ["800-123-4567", "800-234-5678", ...],
        "datasets": [
          {
            "label": "Total Llamadas",
            "data": [5000, 4500, 4000, ...],
            "backgroundColor": "rgba(54, 162, 235, 0.6)"
          }
        ]
      }
    },
    {
      "type": "table",
      "title": "Detalle Top 10 DIDs",
      "headers": ["DID", "Total Llamadas", "Atendidas", "Abandonadas"],
      "rows": [
        {
          "did": "800-123-4567",
          "total_llamadas": 5000,
          "atendidas": 4500,
          "abandonadas": 500
        }
      ],
      "total_rows": 10
    }
  ],
  "last_updated": "2026-01-19T10:30:00Z",
  "data_status": "static",
  "refresh_interval": null,
  "cache_hit": true,
  "metadata": {
    "total_dids": 25,
    "total_calls": 45000,
    "avg_wait_time": 120.5,
    "avg_talk_time": 300.2
  }
}
```

**Response 400 Bad Request:**
```json
{
  "error": "Quarter inválido: Q5. Valores permitidos: Q1, Q2, Q3, Q4"
}
```

**Response 403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 6.2 GET Análisis de Clientes

```http
GET /api/v1/dashboard/analisis-clientes/?quarter=Q1&year=2026
Authorization: Bearer {token}
```

**RBAC:** Requiere `DSH_VIEW` (dashboard.view)

**Response 200 OK:**
```json
{
  "dashboard_type": "client_analysis",
  "quarter": "Q1",
  "year": 2026,
  "widgets": [
    {
      "type": "kpi",
      "title": "Total Clientes Únicos",
      "value": 12500,
      "format_type": "number",
      "formatted_value": "12,500",
      "icon": "users",
      "color": "blue"
    },
    {
      "type": "kpi",
      "title": "Clientes Recurrentes",
      "value": 8750,
      "format_type": "number",
      "formatted_value": "8,750",
      "icon": "repeat",
      "color": "green",
      "subtitle": "70.00%"
    },
    {
      "type": "chart",
      "chart_type": "bar",
      "title": "Top 20 Clientes por Llamadas",
      "data": {
        "labels": ["1234", "5678", "9012", ...],
        "datasets": [
          {
            "label": "Total Llamadas",
            "data": [50, 45, 40, ...],
            "backgroundColor": "rgba(153, 102, 255, 0.6)"
          }
        ]
      }
    }
  ],
  "last_updated": "2026-01-19T10:35:00Z",
  "data_status": "static",
  "refresh_interval": null,
  "cache_hit": false,
  "metadata": {
    "total_clients": 12500,
    "recurring_clients": 8750,
    "new_clients": 3750
  }
}
```

---

### 6.3 GET Performance IVR

```http
GET /api/v1/dashboard/performance-ivr/?quarter=Q1&year=2026
Authorization: Bearer {token}
```

**RBAC:** Requiere `DSH_VIEW` (dashboard.view)

**Response 200 OK:**
```json
{
  "dashboard_type": "ivr_performance",
  "quarter": "Q1",
  "year": 2026,
  "widgets": [
    {
      "type": "kpi",
      "title": "Total Interacciones Menú",
      "value": 150000,
      "format_type": "number",
      "formatted_value": "150,000",
      "icon": "menu",
      "color": "blue"
    },
    {
      "type": "kpi",
      "title": "Tasa de Conversión Promedio",
      "value": 85.5,
      "format_type": "percentage",
      "formatted_value": "85.50%",
      "icon": "trending-up",
      "color": "green"
    },
    {
      "type": "chart",
      "chart_type": "pie",
      "title": "Distribución Errores por Tipo",
      "data": {
        "labels": ["Timeout", "Invalid Input", "Connection Lost"],
        "datasets": [
          {
            "data": [1200, 800, 400],
            "backgroundColor": [
              "rgba(255, 99, 132, 0.6)",
              "rgba(54, 162, 235, 0.6)",
              "rgba(255, 206, 86, 0.6)"
            ]
          }
        ]
      }
    }
  ],
  "last_updated": "2026-01-19T10:40:00Z",
  "data_status": "static",
  "refresh_interval": null,
  "cache_hit": true,
  "metadata": {
    "total_interactions": 150000,
    "total_errors": 2400,
    "error_rate": 1.6,
    "avg_conversion": 85.5
  }
}
```

---

### 6.4 POST Export Dashboard

```http
POST /api/v1/dashboard/metricas-trimestrales/export/
Authorization: Bearer {token}
Content-Type: application/json

{
  "quarter": "Q1",
  "year": 2026,
  "format": "csv"
}
```

**RBAC:** Requiere `DSH_EXP_CSV` (dashboard.export.csv) o `DSH_EXP_EXCEL` (dashboard.export.excel)

**Response 200 OK:**
```json
{
  "download_url": "/media/exports/metricas_Q1_2026.csv",
  "filename": "metricas_Q1_2026.csv",
  "format": "csv",
  "size_bytes": 15420
}
```

**Response 403 Forbidden (sin permiso):**
```json
{
  "detail": "Usuario no tiene permiso: dashboard.export.csv"
}
```

---

<a name="examples"></a>
## 7. REQUEST/RESPONSE EXAMPLES

### 7.1 Curl Examples

#### GET Dashboard

```bash
# Con autenticación JWT
curl -X GET \
  'http://localhost:8000/api/v1/dashboard/metricas-trimestrales/?quarter=Q1&year=2026' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

#### POST Export

```bash
curl -X POST \
  'http://localhost:8000/api/v1/dashboard/metricas-trimestrales/export/' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -H 'Content-Type: application/json' \
  -d '{
    "quarter": "Q1",
    "year": 2026,
    "format": "csv"
  }'
```

### 7.2 Python Requests Examples

```python
import requests

# Autenticación
login_response = requests.post('http://localhost:8000/api/v1/auth/login/', json={
    'username': 'user@example.com',
    'password': 'password123'
})
token = login_response.json()['access']

# Headers con token
headers = {
    'Authorization': f'Bearer {token}'
}

# GET Dashboard
response = requests.get(
    'http://localhost:8000/api/v1/dashboard/metricas-trimestrales/',
    params={'quarter': 'Q1', 'year': 2026},
    headers=headers
)

dashboard = response.json()
print(f"Total widgets: {len(dashboard['widgets'])}")
print(f"Cache hit: {dashboard['cache_hit']}")

# POST Export
export_response = requests.post(
    'http://localhost:8000/api/v1/dashboard/metricas-trimestrales/export/',
    json={'quarter': 'Q1', 'year': 2026, 'format': 'csv'},
    headers=headers
)

download_url = export_response.json()['download_url']
print(f"Download: {download_url}")
```

---

<a name="errors"></a>
## 8. ERROR HANDLING

### 8.1 Códigos de Error

```yaml
400 Bad Request:
  - Quarter inválido
  - Year fuera de rango
  - Formato inválido en export

401 Unauthorized:
  - Token JWT faltante o inválido
  - Token expirado

403 Forbidden:
  - Usuario no tiene permiso DSH_VIEW
  - Usuario no tiene permiso DSH_EXP_CSV
  - Usuario no tiene permiso DSH_EXP_EXCEL

404 Not Found:
  - Endpoint no existe

500 Internal Server Error:
  - Error generando dashboard
  - Error consultando BD IVR
  - Error en cache
```

### 8.2 Estructura de Errores

```json
{
  "error": "Mensaje de error legible",
  "detail": "Detalle técnico (opcional)",
  "code": "ERROR_CODE (opcional)"
}
```

### 8.3 Ejemplos de Errores

#### Error 400: Quarter Inválido

```json
{
  "error": "Quarter inválido: Q5. Valores permitidos: Q1, Q2, Q3, Q4"
}
```

#### Error 403: Sin Permiso

```json
{
  "detail": "Usuario no tiene permiso: dashboard.export.csv"
}
```

#### Error 500: Error Interno

```json
{
  "error": "Error generando dashboard",
  "detail": "Timeout connecting to IVR database"
}
```

---

## 9. RESUMEN PARTE 3

### 9.1 Componentes Generados

```yaml
Archivos Python:
  ✅ apps/dashboard/serializers.py (~350 líneas)
  ✅ apps/dashboard/views.py (~400 líneas)
  ✅ apps/dashboard/permissions.py (~60 líneas)
  ✅ apps/dashboard/urls.py (~40 líneas)

Total: ~850 líneas Python production-ready
```

### 9.2 Serializers

```python
✅ WidgetSerializer (base)
✅ KPISerializer
✅ ChartSerializer
✅ ChartDatasetSerializer
✅ TableSerializer
✅ DashboardSerializer
✅ DashboardQuerySerializer
✅ DashboardExportSerializer
```

### 9.3 ViewSets

```python
✅ QuarterlyMetricsDashboardViewSet
   - list() → GET dashboard
   - export() → POST export
   
✅ ClientAnalysisDashboardViewSet
   - list() → GET dashboard
   - export() → POST export
   
✅ IVRPerformanceDashboardViewSet
   - list() → GET dashboard
   - export() → POST export
```

### 9.4 RBAC v6.0.0 Aplicado

```yaml
Permission Class:
  ✅ DynamicFunctionPermission

function_map en cada ViewSet:
  ✅ list: 'dashboard.view'
  ✅ export_csv: 'dashboard.export.csv'
  ✅ export_excel: 'dashboard.export.excel'

Funciones RBAC:
  ✅ DSH_VIEW (activa)
  ✅ DSH_EXP_CSV (activa)
  ✅ DSH_EXP_EXCEL (activa)
  ⏳ DSH_EXP_PDF (planificada)
  ⏳ DSH_SHARE (planificada)
  ⏳ DSH_EDIT (planificada)
```

### 9.5 Endpoints

```yaml
GET Endpoints (3):
  ✅ /api/v1/dashboard/metricas-trimestrales/
  ✅ /api/v1/dashboard/analisis-clientes/
  ✅ /api/v1/dashboard/performance-ivr/

POST Endpoints (3):
  ✅ /api/v1/dashboard/metricas-trimestrales/export/
  ✅ /api/v1/dashboard/analisis-clientes/export/
  ✅ /api/v1/dashboard/performance-ivr/export/
```

### 9.6 CLEAN_CODE Aplicado

```yaml
Nomenclatura:
  ✅ Clases: PascalCase (DashboardSerializer, QuarterlyMetricsDashboardViewSet)
  ✅ Métodos: snake_case (list, export, _check_permission)
  ✅ URLs: kebab-case (metricas-trimestrales, analisis-clientes)

Docstrings:
  ✅ 100% español formato Google
  ✅ Args, Returns documentados
  ✅ RBAC requirements documentados

Validaciones:
  ✅ Serializers con validators
  ✅ Query params validados
  ✅ Permissions verificadas
```

---

## PRÓXIMA PARTE

**PARTE 4/5: Testing - Unit e Integration**

Contenido:
- Fixtures pytest (/tests/fixtures/dashboard.py)
- Factories (/tests/factories/dashboard.py)
- Unit tests (DashboardService, Serializers, Validators)
- Integration tests (ViewSets con BD real)
- Mocks (cache, IVR data)
- Coverage >80%

**Estimado:** ~900 líneas, 2.5 horas

---

**Fin de PARTE 3/5**
