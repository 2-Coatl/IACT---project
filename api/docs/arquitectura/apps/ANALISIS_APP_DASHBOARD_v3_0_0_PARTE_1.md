---
version: 3.0.0
date: 2026-01-19
project: IACT Call Center System
type: Análisis de Arquitectura - App Dashboard PARTE 1/5
categoria: arquitectura/apps
tema: apps/dashboard/ - Fundamentos y Arquitectura
autor: Claude Technical Analysis
tags: [dashboard, analytics, reporting, cache, rbac, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
estado: definitivo
parte: 1 de 5
relacionado:
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_2.md
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_3.md
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_4.md
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_5.md
replaces: []
---

# ANÁLISIS DE apps/dashboard/ v3.0.0 - PARTE 1/5
## FUNDAMENTOS Y ARQUITECTURA

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen)
2. [Propósito y Responsabilidades](#proposito)
3. [CLEAN_CODE v3.0.1 Aplicado](#clean-code)
4. [RESTRICCIONES v1.0.0 Aplicadas](#restricciones)
5. [RBAC v6.0.0 - MOD_Dashboard](#rbac)
6. [Arquitectura de la App](#arquitectura)
7. [Fuentes de Datos](#fuentes-datos)
8. [Constants y Configuración](#constants)

---

<a name="resumen"></a>
## 1. RESUMEN EJECUTIVO

### 1.1 Overview

```yaml
App: apps/dashboard/
Versión: 3.0.0
Tipo: App COMPLEJA (5 partes)
Complejidad: Alta
Líneas estimadas: ~4,700 líneas
Tamaño estimado: ~200KB
Tiempo estimado: 12 horas

Propósito:
  Sistema de dashboards analíticos con métricas agregadas
  Visualización de KPIs de call center
  Reportes gerenciales con múltiples fuentes
  Exportación de datos en múltiples formatos
```

### 1.2 Características Principales

```yaml
Dashboards disponibles:
  1. Quarterly Metrics Dashboard
     - Métricas trimestrales consolidadas
     - Comparación Q1/Q2/Q3/Q4
     - 15+ KPIs de negocio
  
  2. Client Reports Dashboard
     - Reportes por cliente
     - Análisis de llamadas por cliente
     - Tendencias de satisfacción
  
  3. Menu Performance Dashboard
     - Performance de IVRs
     - Opciones más usadas
     - Tiempos de navegación

Capacidades:
  - Agregación de datos multi-tabla
  - Cache inteligente (CNST-010)
  - Exportación CSV/Excel (CNST-023)
  - Timeout control (CNST-025)
  - Permisos granulares RBAC (6 funciones)
```

---

<a name="proposito"></a>
## 2. PROPÓSITO Y RESPONSABILIDADES

### 2.1 Propósito Principal

**Sistema de dashboards analíticos** para visualización de métricas de negocio del call center, con agregaciones complejas de múltiples fuentes de datos y capacidades de exportación.

### 2.2 Responsabilidades

```yaml
Responsabilidades Principales:
  1. Generación de dashboards ejecutivos
     - Quarterly Metrics (trimestral)
     - Client Reports (por cliente)
     - Menu Performance (IVR analytics)
  
  2. Agregación de datos multi-fuente
     - calls (llamadas)
     - service_levels (niveles de servicio)
     - client_satisfaction (satisfacción)
     - ivr_navigation (navegación IVR)
  
  3. Cálculo de KPIs de negocio
     - Service Level (SL)
     - Average Speed of Answer (ASA)
     - Abandonment Rate
     - First Call Resolution (FCR)
     - Customer Satisfaction (CSAT)
     - Net Promoter Score (NPS)
  
  4. Exportación de datos
     - CSV para análisis externo
     - Excel con formato
     - Validación de permisos RBAC
  
  5. Cache de resultados
     - Cache por trimestre/cliente/menu
     - Invalidación automática
     - TTL 300s (5 minutos)

Responsabilidades Secundarias:
  - Integración con apps/reports/ (reportes históricos)
  - Métricas para apps/monitoring/
  - Datos para alertas en apps/alerts/
```

### 2.3 NO Responsabilidades

```yaml
❌ NO es responsable de:
  - Almacenamiento de métricas (responsabilidad de apps/etl/)
  - Alertas sobre KPIs (responsabilidad de apps/alerts/)
  - Reportes históricos detallados (apps/reports/)
  - Configuración de thresholds (apps/config/)
  - Procesamiento ETL (apps/etl/)
  - Monitoreo en tiempo real (apps/monitoring/)
```

### 2.4 Separación de Responsabilidades

```yaml
apps/dashboard/:
  - Visualización de métricas agregadas
  - Dashboards ejecutivos
  - Exportación de datos agregados

apps/reports/:
  - Reportes históricos detallados
  - Drill-down a nivel de llamada
  - Reportes programados

apps/etl/:
  - Procesamiento de datos crudos
  - Agregaciones pre-calculadas
  - Materialización de métricas

apps/alerts/:
  - Alertas sobre KPIs
  - Notificaciones automáticas
  - Thresholds configurables
```

---

<a name="clean-code"></a>
## 3. CLEAN_CODE v3.0.1 APLICADO

### 3.1 Nomenclatura Código

```python
# CLEAN_CODE v3.0.1: Código en INGLÉS

# Clases (PascalCase)
class QuarterlyMetricsDashboard:
    """Dashboard de métricas trimestrales."""
    pass

class ClientReportsDashboard:
    """Dashboard de reportes por cliente."""
    pass

class DashboardService:
    """Servicio de generación de dashboards."""
    pass

class DashboardCache:
    """Servicio de cache para dashboards."""
    pass

# Métodos y funciones (snake_case)
def get_quarterly_metrics(quarter: str, year: int) -> Dict[str, Any]:
    """Obtiene métricas trimestrales."""
    pass

def calculate_service_level(total_calls: int, answered_in_time: int) -> float:
    """Calcula Service Level (%)."""
    return (answered_in_time / total_calls) * 100

def export_to_csv(data: List[Dict], filename: str) -> str:
    """Exporta datos a CSV."""
    pass

# Variables (snake_case)
quarterly_data = []
service_level = 0.0
cache_key = "dashboard:Q1:2026"

# Constantes (UPPER_SNAKE_CASE)
CACHE_TTL_SECONDS = 300
DEFAULT_QUARTER = 'Q1'
MAX_EXPORT_ROWS = 10000
SERVICE_LEVEL_THRESHOLD = 80.0
```

### 3.2 Nomenclatura Base de Datos

```python
# Dashboard NO tiene modelos propios Django
# Usa modelos de otras apps:
# - apps/calls/models.py (Call, CallDetail)
# - apps/clients/models.py (Client)
# - apps/services/models.py (Service)
# - apps/ivr/models.py (MenuNavigation)

# Queries usan nombres de tablas existentes:
from apps.calls.models import Call
from apps.clients.models import Client

# Agregaciones usan nombres inglés
quarterly_stats = Call.objects.filter(
    created_at__year=year,
    quarter=quarter
).aggregate(
    total_calls=Count('id'),
    avg_duration=Avg('duration'),
    max_wait_time=Max('wait_time')
)
```

### 3.3 Docstrings en Español

```python
"""
Service layer para generación de dashboards.

Responsabilidades:
- Generar dashboards con métricas agregadas
- Cache de resultados (CNST-010)
- Exportación de datos (CNST-023)
- Control de timeouts (CNST-025)

CLEAN_CODE v3.0.1:
- Código: inglés PascalCase/snake_case
- Docstrings: español formato Google
- Comentarios: español

CNST-002: Agregaciones optimizadas
CNST-010: Cache LocMem
CNST-023: Exportación CSV/Excel
"""

class DashboardService:
    """
    Servicio principal de dashboards.
    
    Responsabilidades:
    - Generación de dashboards
    - Cálculo de KPIs
    - Integración con cache
    
    Atributos:
        cache: Instancia de DashboardCache
        export_service: Servicio de exportación
    """
    
    def __init__(self):
        """Inicializa el servicio de dashboards."""
        self.cache = DashboardCache()
        self.export_service = ExportService()
    
    def get_quarterly_dashboard(
        self,
        quarter: str,
        year: int,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Obtiene dashboard de métricas trimestrales.
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3, Q4)
            year: Año (ej: 2026)
            use_cache: Si usar cache (default: True)
        
        Returns:
            Dict con métricas del trimestre
        
        CNST-002: Agregaciones optimizadas con índices
        CNST-010: Cache LocMem con TTL 300s
        CNST-025: Timeout máximo 90s
        
        Example:
            >>> service.get_quarterly_dashboard('Q1', 2026)
            {
                'quarter': 'Q1',
                'year': 2026,
                'total_calls': 125000,
                'service_level': 85.2,
                'asa': 45.8,
                'abandonment_rate': 3.5,
                ...
            }
        """
        # Implementación...
        pass
```

---

<a name="restricciones"></a>
## 4. RESTRICCIONES v1.0.0 APLICADAS

### 4.1 CNST-002: Agregaciones Optimizadas

```yaml
Restricción: Queries de agregación optimizadas
Categoría: Performance
Impacto: Alto
Estado: Activo

Problema:
  Dashboards ejecutan queries pesadas con agregaciones
  multi-tabla. Queries no optimizadas causan timeouts.

Implementación:
  ✅ Índices en campos de agregación:
     - idx_call_created_quarter (created_at, quarter)
     - idx_call_client (client_id, created_at)
     - idx_service_level (service_id, date)
  
  ✅ Agregaciones con annotate/aggregate:
     ```python
     Call.objects.filter(
         quarter='Q1', year=2026
     ).aggregate(
         total=Count('id'),
         avg_duration=Avg('duration'),
         service_level=Avg('service_level_pct')
     )
     ```
  
  ✅ Prefetch related para evitar N+1:
     ```python
     Client.objects.prefetch_related(
         'calls', 'services'
     )
     ```
  
  ✅ EXPLAIN ANALYZE para queries críticas
  ✅ select_related para foreign keys
  ✅ only() para limitar campos

Testing:
  - Verificar EXPLAIN ANALYZE usa índices
  - Verificar queries <5s en producción
  - Verificar N+1 detectado por django-debug-toolbar
```

### 4.2 CNST-003: Datos ETL Pre-calculados

```yaml
Restricción: Usar datos ETL cuando sea posible
Categoría: Performance
Impacto: Alto
Estado: Activo

Problema:
  Calcular métricas en tiempo real es costoso.
  Dashboards deben ser rápidos (<5s).

Solución:
  ✅ Usar tablas ETL para métricas agregadas:
     - tbl_metricas_diarias (daily_metrics)
     - tbl_metricas_semanales (weekly_metrics)
     - tbl_metricas_trimestrales (quarterly_metrics)
  
  ✅ Queries a tablas pre-calculadas:
     ```python
     QuarterlyMetric.objects.filter(
         quarter='Q1',
         year=2026
     ).first()
     ```
  
  ✅ Fallback a cálculo en vivo si ETL no disponible
  ✅ Cache de resultados (CNST-010)

Integración:
  - apps/etl/ genera métricas diariamente
  - apps/dashboard/ consume métricas
  - Si ETL falla, calcular en vivo con warning
```

### 4.3 CNST-010: Cache LocMem

```yaml
Restricción: Cache LocMem (NO Redis)
Categoría: Infraestructura
Impacto: Medio
Estado: Activo

Implementación:
  ✅ settings.py:
     ```python
     CACHES = {
         'default': {
             'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
             'LOCATION': 'iact-dashboard-cache',
             'OPTIONS': {
                 'MAX_ENTRIES': 1000
             }
         }
     }
     ```
  
  ✅ Cache keys con namespace:
     ```python
     cache_key = f"dashboard:quarterly:{quarter}:{year}"
     cache_key = f"dashboard:client:{client_id}:{date}"
     ```
  
  ✅ TTL corto (300s = 5 minutos):
     ```python
     cache.set(cache_key, data, timeout=300)
     ```

Trade-off:
  - Cache NO compartido entre workers Gunicorn
  - Cada worker tiene su propio cache
  - TTL corto minimiza inconsistencias
  - Aceptable para dashboards (datos agregados)

Invalidación:
  - Automática por TTL
  - Manual con cache.delete(key)
  - NO invalidación proactiva (complejidad)
```

### 4.4 CNST-023: Exportación de Datos

```yaml
Restricción: Exportación solo CSV/Excel
Categoría: Funcional
Impacto: Medio
Estado: Activo

Formatos soportados:
  ✅ CSV (pandas, openpyxl)
  ✅ Excel (openpyxl)
  ❌ PDF (CNST-023: NO implementado aún)

Límites:
  - Max 10,000 filas por exportación
  - Max 5MB tamaño archivo
  - Timeout 90s (CNST-025)

Implementación:
  ✅ ExportService:
     ```python
     def export_to_csv(data: List[Dict]) -> str:
         df = pd.DataFrame(data)
         filename = f"dashboard_{timestamp}.csv"
         df.to_csv(filename, index=False)
         return filename
     ```
  
  ✅ RBAC validation:
     - DSH_EXP_CSV (audit.export + 'csv')
     - DSH_EXP_EXCEL (audit.export + 'excel')

Download:
  - Archivos guardados en /media/exports/
  - URL firmada con token temporal
  - Auto-delete después de 24 horas
```

### 4.5 CNST-025: Timeout 90s

```yaml
Restricción: Timeout máximo 90 segundos
Categoría: Performance
Impacto: Alto
Estado: Activo

Aplicación:
  ✅ Queries de dashboard:
     ```python
     from django.db import connection
     
     with connection.cursor() as cursor:
         cursor.execute("SET statement_timeout = 90000")  # 90s
         # query pesada
     ```
  
  ✅ Exportaciones:
     - Async tasks para >1000 filas
     - Celery task con timeout 90s
  
  ✅ Gunicorn timeout:
     ```python
     # gunicorn.conf.py
     timeout = 90
     ```
  
  ✅ Nginx proxy_read_timeout:
     ```nginx
     location /api/v1/dashboard/ {
         proxy_read_timeout 90s;
     }
     ```

Testing:
  - Verificar queries <90s en producción
  - Test con datos máximos (Q4 completo)
  - Monitoreo de slow queries
```

---

<a name="rbac"></a>
## 5. RBAC v6.0.0 - MOD_Dashboard

### 5.1 Módulo MOD_Dashboard

```yaml
Código: MOD_Dashboard
Nombre: Módulo de Dashboards
Descripción: Dashboards ejecutivos y reportes gerenciales
Estado: Activo
Funciones: 6 (3 activas + 3 planificadas)
Grupos asociados: GRP_Manager, GRP_Executive, GRP_Admin

Nota:
  Funciones DSH_EXP_PDF, DSH_SHARE, DSH_EDIT están
  planificadas pero NO implementadas (CNST-023)
```

### 5.2 Funciones Activas (3)

#### 5.2.1 DSH_VIEW

```yaml
Código: DSH_VIEW
Nombre: Ver Dashboards
Descripción: Permite visualizar dashboards del sistema
Permission Django: dashboard.view
Estado: Activo
Asignación típica:
  - GRP_Manager (gerentes de operaciones)
  - GRP_Executive (directivos)
  - GRP_Admin

Permite:
  - GET /api/v1/dashboard/quarterly/
  - GET /api/v1/dashboard/client-reports/
  - GET /api/v1/dashboard/menu-performance/
  - Ver todos los dashboards disponibles
  - Filtrar por trimestre/cliente/menú

Restricciones:
  - Solo dashboards del período actual (default)
  - Histórico requiere filtros explícitos
  - Límite 10,000 filas por vista

No permite:
  - Exportar datos (requiere DSH_EXP_*)
  - Compartir dashboards (DSH_SHARE planificado)
  - Editar configuración (DSH_EDIT planificado)
```

#### 5.2.2 DSH_EXP_CSV

```yaml
Código: DSH_EXP_CSV
Nombre: Exportar a CSV
Descripción: Permite exportar dashboards a formato CSV
Permission Django: dashboard.export_csv
Estado: Activo
Asignación típica:
  - GRP_Manager
  - GRP_Executive
  - GRP_Admin

Permite:
  - POST /api/v1/dashboard/export/csv/
  - Exportar cualquier dashboard a CSV
  - Max 10,000 filas
  - Download con URL firmada

Formato CSV:
  - Encoding: UTF-8
  - Delimiter: coma (,)
  - Headers: nombres de columnas
  - Sin formato (datos crudos)

Límites:
  - Max 10,000 filas (CNST-023)
  - Max 5MB archivo
  - Timeout 90s (CNST-025)
  - Auto-delete 24h después

Validaciones:
  - Usuario debe tener DSH_VIEW + DSH_EXP_CSV
  - Dashboard debe existir
  - Parámetros válidos (trimestre, cliente, etc)
```

#### 5.2.3 DSH_EXP_EXCEL

```yaml
Código: DSH_EXP_EXCEL
Nombre: Exportar a Excel
Descripción: Permite exportar dashboards a formato Excel
Permission Django: dashboard.export_excel
Estado: Activo
Asignación típica:
  - GRP_Executive (prefieren Excel)
  - GRP_Admin

Permite:
  - POST /api/v1/dashboard/export/excel/
  - Exportar con formato (colores, bordes)
  - Múltiples hojas (sheets)
  - Gráficos embebidos (futuro)

Formato Excel:
  - Librería: openpyxl
  - Formato: .xlsx (NO .xls)
  - Headers con formato
  - Auto-width columns
  - Freeze panes

Características:
  - Hoja 1: Datos completos
  - Hoja 2: Resumen ejecutivo
  - Hoja 3: Gráficos (futuro)

Límites:
  - Max 10,000 filas (CNST-023)
  - Max 5MB archivo
  - Timeout 90s (CNST-025)
```

### 5.3 Funciones Planificadas (3)

#### 5.3.1 DSH_EXP_PDF

```yaml
Código: DSH_EXP_PDF
Nombre: Exportar a PDF
Descripción: Permite exportar dashboards a formato PDF
Permission Django: dashboard.export_pdf
Estado: Planificado (NO implementado)
Razón: CNST-023 (complejidad alta, prioridad media)

Cuando se implemente:
  - POST /api/v1/dashboard/export/pdf/
  - Formato profesional con logo
  - Gráficos embebidos
  - Múltiples páginas
  - Librería: reportlab o weasyprint

Prioridad: Media
Estimado: Sprint 3-4
```

#### 5.3.2 DSH_SHARE

```yaml
Código: DSH_SHARE
Nombre: Compartir Dashboard
Descripción: Permite compartir dashboards con otros usuarios
Permission Django: dashboard.share
Estado: Planificado (NO implementado)

Cuando se implemente:
  - POST /api/v1/dashboard/share/
  - Link compartido con token
  - Expira en 7 días
  - Control de permisos

Prioridad: Baja
Estimado: Sprint 5-6
```

#### 5.3.3 DSH_EDIT

```yaml
Código: DSH_EDIT
Nombre: Editar Dashboard
Descripción: Permite personalizar configuración de dashboards
Permission Django: dashboard.edit
Estado: Planificado (NO implementado)

Cuando se implemente:
  - PUT /api/v1/dashboard/{id}/config/
  - Personalizar KPIs mostrados
  - Cambiar colores/temas
  - Guardar vistas favoritas

Prioridad: Baja
Estimado: Sprint 6-7
```

### 5.4 function_map en ViewSets

```python
# apps/dashboard/views.py

class QuarterlyDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para dashboard trimestral.
    
    RBAC v6.0.0: DynamicFunctionPermission
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    # function_map para RBAC
    function_map = {
        'get_dashboard': 'dashboard.view',         # DSH_VIEW
        'export_csv': 'dashboard.export_csv',      # DSH_EXP_CSV
        'export_excel': 'dashboard.export_excel',  # DSH_EXP_EXCEL
        # 'export_pdf': 'dashboard.export_pdf',    # Planificado
        # 'share': 'dashboard.share',              # Planificado
    }


class ClientReportsDashboardViewSet(viewsets.ViewSet):
    """ViewSet para dashboard de clientes."""
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'get_dashboard': 'dashboard.view',         # DSH_VIEW
        'export_csv': 'dashboard.export_csv',      # DSH_EXP_CSV
        'export_excel': 'dashboard.export_excel',  # DSH_EXP_EXCEL
    }
```

### 5.5 Grupos y Asignaciones

```yaml
GRP_Manager:
  Funciones asignadas:
    - DSH_VIEW (ver dashboards)
    - DSH_EXP_CSV (exportar CSV)
    - DSH_EXP_EXCEL (exportar Excel)

GRP_Executive:
  Funciones asignadas:
    - DSH_VIEW (dashboards ejecutivos)
    - DSH_EXP_EXCEL (preferencia Excel)

GRP_Admin:
  Funciones asignadas:
    - Todas de GRP_Manager +
    - Acceso sin restricciones
    - Futura DSH_EDIT

GRP_UserBasic:
  Funciones asignadas:
    - Ninguna (dashboards solo gerenciales)
```

---

<a name="arquitectura"></a>
## 6. ARQUITECTURA DE LA APP

### 6.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                  apps/dashboard/                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐    │
│  │              API Layer (REST)                  │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - QuarterlyDashboardViewSet                   │    │
│  │  - ClientReportsDashboardViewSet               │    │
│  │  - MenuPerformanceDashboardViewSet             │    │
│  │  - RBAC: DynamicFunctionPermission             │    │
│  │  - Timeout 90s (CNST-025)                      │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │           Service Layer                        │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - DashboardService                            │    │
│  │    * get_quarterly_dashboard()                 │    │
│  │    * get_client_reports()                      │    │
│  │    * get_menu_performance()                    │    │
│  │  - ExportService                               │    │
│  │    * export_to_csv()                           │    │
│  │    * export_to_excel()                         │    │
│  │  - DashboardCache (CNST-010)                   │    │
│  │    * get_cached()                              │    │
│  │    * set_cache()                               │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │      Data Aggregation Layer                    │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - QuarterlyMetricsAggregator                  │    │
│  │  - ClientMetricsAggregator                     │    │
│  │  - MenuMetricsAggregator                       │    │
│  │  - CNST-002: Queries optimizadas               │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │       Data Sources (Multi-App)                 │    │
│  │  - apps/calls/ (Call, CallDetail)              │    │
│  │  - apps/clients/ (Client)                      │    │
│  │  - apps/services/ (Service)                    │    │
│  │  - apps/ivr/ (MenuNavigation)                  │    │
│  │  - apps/etl/ (QuarterlyMetric) CNST-003        │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘

Integraciones:
  ┌─────────────────┐
  │  apps/etl/      │ → Métricas pre-calculadas (CNST-003)
  └─────────────────┘
  
  ┌─────────────────┐
  │  apps/reports/  │ → Reportes históricos
  └─────────────────┘
  
  ┌─────────────────┐
  │  apps/access/   │ → RBAC validation (6 funciones)
  └─────────────────┘
```

---

<a name="fuentes-datos"></a>
## 7. FUENTES DE DATOS

### 7.1 Modelos de Otras Apps

```python
# Dashboard NO tiene modelos propios
# Consume modelos de múltiples apps

from apps.calls.models import Call, CallDetail
from apps.clients.models import Client
from apps.services.models import Service, ServiceLevel
from apps.ivr.models import MenuNavigation
from apps.etl.models import QuarterlyMetric, DailyMetric

# Ejemplo de query multi-tabla
quarterly_data = Call.objects.filter(
    created_at__year=2026,
    quarter='Q1'
).select_related(
    'client', 'service'
).prefetch_related(
    'call_details'
).aggregate(
    total_calls=Count('id'),
    avg_duration=Avg('duration'),
    service_level=Avg('service_level_pct')
)
```

---

<a name="constants"></a>
## 8. CONSTANTS Y CONFIGURACIÓN

### 8.1 Archivo: apps/dashboard/constants.py

```python
"""
Constantes para sistema de dashboards.

CLEAN_CODE v3.0.1:
- Constantes: UPPER_SNAKE_CASE inglés
- Docstrings: español

CNST-010: Cache settings
CNST-023: Export limits
CNST-025: Timeout settings
"""

# Cache
CACHE_TTL_SECONDS = 300
CACHE_KEY_PREFIX = 'dashboard'
CACHE_MAX_ENTRIES = 1000

# Quarters
QUARTERS = ['Q1', 'Q2', 'Q3', 'Q4']
QUARTER_MONTHS = {
    'Q1': [1, 2, 3],
    'Q2': [4, 5, 6],
    'Q3': [7, 8, 9],
    'Q4': [10, 11, 12],
}
DEFAULT_QUARTER = 'Q1'

# Export
MAX_EXPORT_ROWS = 10000
MAX_EXPORT_SIZE_MB = 5
EXPORT_FILE_RETENTION_HOURS = 24
EXPORT_FORMATS = ['csv', 'excel']

# Timeout
QUERY_TIMEOUT_SECONDS = 90
EXPORT_TIMEOUT_SECONDS = 90

# KPI Thresholds
SERVICE_LEVEL_THRESHOLD = 80.0
ASA_THRESHOLD = 60.0
ABANDONMENT_THRESHOLD = 5.0
FCR_THRESHOLD = 75.0
CSAT_THRESHOLD = 4.0

# Dashboard Types
DASHBOARD_TYPES = [
    'quarterly_metrics',
    'client_reports',
    'menu_performance',
]

# KPI Fields
KPI_FIELDS = [
    'total_calls',
    'answered_calls',
    'abandoned_calls',
    'service_level',
    'asa',
    'abandonment_rate',
    'avg_duration',
    'max_wait_time',
    'fcr',
    'csat',
    'nps',
]
```

---

## RESUMEN PARTE 1

```yaml
Completado:
  ✅ Resumen ejecutivo
  ✅ Propósito y responsabilidades
  ✅ CLEAN_CODE v3.0.1
  ✅ RESTRICCIONES (CNST-002, 003, 010, 023, 025)
  ✅ RBAC v6.0.0 (6 funciones: 3 activas + 3 planificadas)
  ✅ Arquitectura completa
  ✅ Fuentes de datos
  ✅ Constants

Próximas partes:
  ✅ PARTE 2/5: Services y Cache (YA GENERADA)
  ✅ PARTE 3/5: APIs y Serializers (YA GENERADA)
  ✅ PARTE 4/5: Testing Unit+Integration (YA GENERADA)
  ✅ PARTE 5/5: Testing API+E2E+Deployment (YA GENERADA)
```

---

**FIN DE PARTE 1/5**
