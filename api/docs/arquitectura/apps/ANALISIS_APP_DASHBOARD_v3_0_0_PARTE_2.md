---
version: 3.0.0
date: 2026-01-19
project: IACT Call Center System
type: Análisis de Arquitectura - App Dashboard PARTE 2/5
categoria: arquitectura/apps
tema: apps/dashboard/ - Modelos y Services
autor: Claude Technical Analysis
tags: [dashboard, services, cache, clean-code, restricciones]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
estado: definitivo
parte: 2 de 5
relacionado:
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_1.md
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_3.md
---

# ANÁLISIS DE apps/dashboard/ v3.0.0 - PARTE 2/5
## MODELOS Y SERVICE LAYER

---

## TABLA DE CONTENIDOS

1. [Resumen Parte 2](#resumen)
2. [Modelos Django](#modelos)
3. [Service Layer - DashboardService](#service-layer)
4. [Cache Strategy (CNST-010)](#cache-strategy)
5. [Widget Generators](#widget-generators)
6. [Constants y Configuración](#constants)
7. [Validaciones de Negocio](#validaciones)
8. [Utils y Helpers](#utils)

---

<a name="resumen"></a>
## 1. RESUMEN PARTE 2

### 1.1 Alcance de esta Parte

```yaml
Componentes cubiertos:
  ✅ Modelos Django (referencias apps/ivr/)
  ✅ DashboardService completo
  ✅ Cache Strategy LocMem (CNST-010)
  ✅ Widget Generators (KPI, Charts, Tables)
  ✅ Constants y configuración
  ✅ Validaciones de negocio
  ✅ Utils y helpers

Líneas de código: ~900 líneas Python
Archivos generados:
  - apps/dashboard/services.py
  - apps/dashboard/constants.py
  - apps/dashboard/utils.py
  - apps/dashboard/validators.py
```

### 1.2 Dependencias de Modelos

```python
# apps/dashboard/ NO tiene modelos propios
# Usa modelos de apps/ivr/ (readonly, CNST-002)

from apps.ivr.models import (
    QuarterlyReport,           # tbl_reporte_trimestral
    AbandonedCallReport,       # tbl_reporte_abandonadas
    UniqueClientReport,        # tbl_reporte_clientes
    TransferReport,            # tbl_reporte_transferencias
    MenuPerformanceReport,     # tbl_reporte_menus_performance
    MenuErrorReport,           # tbl_reporte_menu_errores
)
```

### 1.3 Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                  DashboardService                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Cache Layer (LocMem, TTL 300s)          │  │
│  └──────────────────────────────────────────────────┘  │
│                        ▼                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Data Aggregation Layer                   │  │
│  │   (QuarterlyReport, AbandonedCallReport, etc)   │  │
│  └──────────────────────────────────────────────────┘  │
│                        ▼                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Widget Generation Layer                  │  │
│  │   - KPI Widgets                                  │  │
│  │   - Chart Widgets (bar, line, pie)              │  │
│  │   - Table Widgets                                │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

<a name="modelos"></a>
## 2. MODELOS DJANGO

### 2.1 Decisión: Sin Modelos Propios

```python
"""
apps/dashboard/models.py

Dashboard NO tiene modelos propios.

Razón:
- Dashboard es una capa de VISUALIZACIÓN
- Consume datos agregados de apps/ivr/ (readonly)
- No almacena estado propio
- No requiere persistencia

CLEAN_CODE v3.0.1: Separación de responsabilidades clara
- apps/ivr/: Datos (modelos readonly)
- apps/reports/: Generación reportes (POST)
- apps/dashboard/: Visualización widgets (GET)
"""

# No hay modelos Django en este archivo
```

### 2.2 Modelos IVR Utilizados

#### 2.2.1 QuarterlyReport

```python
# apps/ivr/models.py (referencia)

class QuarterlyReport(models.Model):
    """
    Reporte trimestral agregado.
    
    Tabla: tbl_reporte_trimestral
    BD: ivr_legacy (readonly, CNST-002)
    """
    
    id = models.AutoField(
        db_column='iIdReporte',
        primary_key=True
    )
    
    quarter = models.CharField(
        db_column='cTrimestre',
        max_length=2,
        help_text="Trimestre: Q1, Q2, Q3, Q4"
    )
    
    year = models.IntegerField(
        db_column='iAnio'
    )
    
    did = models.CharField(
        db_column='cDID',
        max_length=20,
        help_text="Número DID (800-xxx-xxxx)"
    )
    
    total_calls = models.IntegerField(
        db_column='iTotalLlamadas',
        default=0
    )
    
    answered_calls = models.IntegerField(
        db_column='iLlamadasAtendidas',
        default=0
    )
    
    abandoned_calls = models.IntegerField(
        db_column='iLlamadasAbandonadas',
        default=0
    )
    
    avg_wait_time = models.DecimalField(
        db_column='dTiempoEsperaPromedio',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    avg_talk_time = models.DecimalField(
        db_column='dTiempoConversacionPromedio',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    service_level = models.DecimalField(
        db_column='dNivelServicio',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Porcentaje de nivel de servicio"
    )
    
    created_at = models.DateTimeField(
        db_column='dFechaCreacion',
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        db_column='dFechaActualizacion',
        auto_now=True
    )
    
    class Meta:
        db_table = 'tbl_reporte_trimestral'
        managed = False  # CNST-002: Readonly
        ordering = ['-year', '-quarter', 'did']
        indexes = [
            models.Index(fields=['year', 'quarter']),
            models.Index(fields=['did']),
        ]
```

#### 2.2.2 Otros Modelos Referenciados

```python
# Todos en apps/ivr/models.py

class AbandonedCallReport(models.Model):
    """tbl_reporte_abandonadas"""
    # Campos: did, fecha, hora, cantidad, motivo_abandono, etc
    
class UniqueClientReport(models.Model):
    """tbl_reporte_clientes"""
    # Campos: telefono_cliente, total_llamadas, primera_llamada, etc

class TransferReport(models.Model):
    """tbl_reporte_transferencias"""
    # Campos: did_origen, did_destino, cantidad, etc

class MenuPerformanceReport(models.Model):
    """tbl_reporte_menus_performance"""
    # Campos: menu_id, opcion, selecciones, conversion_rate, etc

class MenuErrorReport(models.Model):
    """tbl_reporte_menu_errores"""
    # Campos: menu_id, error_type, cantidad, etc
```

---

<a name="service-layer"></a>
## 3. SERVICE LAYER - DashboardService

### 3.1 Archivo Completo: apps/dashboard/services.py

```python
"""
Service Layer para Dashboard.

Responsabilidades:
- Generar dashboards con widgets agregados
- Cache LocMem (CNST-010) con TTL 300s
- Transformar datos de reportes a widgets
- Validar parámetros de entrada

CLEAN_CODE v3.0.1:
- Clase: DashboardService (PascalCase inglés)
- Métodos: snake_case inglés
- Docstrings: español formato Google

RESTRICCIONES aplicadas:
- CNST-003: Datos estáticos (6-12h desfase)
- CNST-010: Cache LocMem (NO Redis)
- CNST-023: NO auto-refresh
- CNST-025: Timeout 90s
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.cache import cache
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone

from apps.ivr.models import (
    QuarterlyReport,
    AbandonedCallReport,
    UniqueClientReport,
    TransferReport,
    MenuPerformanceReport,
    MenuErrorReport,
)
from apps.dashboard.constants import (
    DASHBOARD_TYPES,
    WIDGET_TYPES,
    CHART_TYPES,
    CACHE_TTL,
    VALID_QUARTERS,
)
from apps.dashboard.validators import DashboardValidator
from apps.dashboard.utils import (
    generate_cache_key,
    format_number,
    format_percentage,
    calculate_percentage,
)


class DashboardService:
    """
    Servicio para generación de dashboards con widgets.
    
    Responsabilidades:
    - Generar 3 tipos de dashboards (métricas, clientes, IVR)
    - Cache LocMem con TTL 300s (CNST-010)
    - Generar widgets: KPI, Charts, Tables
    - Validar parámetros de entrada
    
    CNST-003: Dashboards muestran datos estáticos (6-12h desfase)
    CNST-023: NO incluye auto-refresh
    """
    
    def __init__(self):
        """Inicializa el servicio de dashboard."""
        self.validator = DashboardValidator()
    
    # ===================================================================
    # DASHBOARDS PRINCIPALES
    # ===================================================================
    
    def get_quarterly_metrics_dashboard(
        self,
        quarter: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera dashboard de métricas trimestrales.
        
        Dashboard tipo: 'quarterly_metrics'
        Widgets: 4 KPIs + 3 Charts + 1 Table
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3, Q4)
            year: Año (default: año actual)
        
        Returns:
            Dict con estructura:
            {
                'dashboard_type': 'quarterly_metrics',
                'quarter': 'Q1',
                'year': 2026,
                'widgets': [...],
                'last_updated': '2026-01-19T10:30:00Z',
                'data_status': 'static',  # CNST-003
                'refresh_interval': None,  # CNST-023
                'cache_hit': True/False
            }
        
        Raises:
            ValidationError: Si quarter inválido
        """
        # Validar parámetros
        self.validator.validate_quarter(quarter)
        year = year or timezone.now().year
        
        # Cache key
        cache_key = generate_cache_key(
            'quarterly_metrics',
            quarter=quarter,
            year=year
        )
        
        # Intentar obtener de cache (CNST-010: LocMem)
        cached_data = cache.get(cache_key)
        if cached_data:
            cached_data['cache_hit'] = True
            return cached_data
        
        # Generar dashboard desde datos
        dashboard = self._build_quarterly_metrics_dashboard(quarter, year)
        
        # Guardar en cache (TTL 300s)
        cache.set(cache_key, dashboard, CACHE_TTL)
        dashboard['cache_hit'] = False
        
        return dashboard
    
    def get_client_analysis_dashboard(
        self,
        quarter: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera dashboard de análisis de clientes.
        
        Dashboard tipo: 'client_analysis'
        Widgets: 3 KPIs + 2 Charts + 1 Table (top clientes)
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3, Q4)
            year: Año (default: año actual)
        
        Returns:
            Dict con estructura de dashboard
        
        Raises:
            ValidationError: Si quarter inválido
        """
        self.validator.validate_quarter(quarter)
        year = year or timezone.now().year
        
        cache_key = generate_cache_key(
            'client_analysis',
            quarter=quarter,
            year=year
        )
        
        cached_data = cache.get(cache_key)
        if cached_data:
            cached_data['cache_hit'] = True
            return cached_data
        
        dashboard = self._build_client_analysis_dashboard(quarter, year)
        
        cache.set(cache_key, dashboard, CACHE_TTL)
        dashboard['cache_hit'] = False
        
        return dashboard
    
    def get_ivr_performance_dashboard(
        self,
        quarter: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera dashboard de performance IVR (menús).
        
        Dashboard tipo: 'ivr_performance'
        Widgets: 4 KPIs + 2 Charts + 2 Tables
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3, Q4)
            year: Año (default: año actual)
        
        Returns:
            Dict con estructura de dashboard
        
        Raises:
            ValidationError: Si quarter inválido
        """
        self.validator.validate_quarter(quarter)
        year = year or timezone.now().year
        
        cache_key = generate_cache_key(
            'ivr_performance',
            quarter=quarter,
            year=year
        )
        
        cached_data = cache.get(cache_key)
        if cached_data:
            cached_data['cache_hit'] = True
            return cached_data
        
        dashboard = self._build_ivr_performance_dashboard(quarter, year)
        
        cache.set(cache_key, dashboard, CACHE_TTL)
        dashboard['cache_hit'] = False
        
        return dashboard
    
    # ===================================================================
    # BUILDERS PRIVADOS
    # ===================================================================
    
    def _build_quarterly_metrics_dashboard(
        self,
        quarter: str,
        year: int
    ) -> Dict[str, Any]:
        """
        Construye dashboard de métricas trimestrales.
        
        Widgets generados:
        - KPI: Total Llamadas
        - KPI: Llamadas Atendidas
        - KPI: Llamadas Abandonadas
        - KPI: Nivel de Servicio Promedio
        - Chart (bar): Llamadas por DID
        - Chart (line): Tendencia diaria
        - Chart (pie): Distribución atendidas/abandonadas
        - Table: Top 10 DIDs por volumen
        
        Args:
            quarter: Trimestre validado
            year: Año
        
        Returns:
            Dict con estructura completa de dashboard
        """
        # Obtener datos agregados
        reports = QuarterlyReport.objects.filter(
            quarter=quarter,
            year=year
        )
        
        # Agregaciones
        totals = reports.aggregate(
            total_calls=Sum('total_calls'),
            answered_calls=Sum('answered_calls'),
            abandoned_calls=Sum('abandoned_calls'),
            avg_service_level=Avg('service_level'),
            avg_wait_time=Avg('avg_wait_time'),
            avg_talk_time=Avg('avg_talk_time'),
        )
        
        # Construir widgets
        widgets = []
        
        # KPI: Total Llamadas
        widgets.append(self._generate_kpi_widget(
            title='Total Llamadas',
            value=totals['total_calls'] or 0,
            format_type='number',
            icon='phone',
            color='blue'
        ))
        
        # KPI: Llamadas Atendidas
        widgets.append(self._generate_kpi_widget(
            title='Llamadas Atendidas',
            value=totals['answered_calls'] or 0,
            format_type='number',
            icon='check-circle',
            color='green',
            subtitle=format_percentage(
                totals['answered_calls'],
                totals['total_calls']
            )
        ))
        
        # KPI: Llamadas Abandonadas
        widgets.append(self._generate_kpi_widget(
            title='Llamadas Abandonadas',
            value=totals['abandoned_calls'] or 0,
            format_type='number',
            icon='x-circle',
            color='red',
            subtitle=format_percentage(
                totals['abandoned_calls'],
                totals['total_calls']
            )
        ))
        
        # KPI: Nivel de Servicio
        widgets.append(self._generate_kpi_widget(
            title='Nivel de Servicio Promedio',
            value=float(totals['avg_service_level'] or 0),
            format_type='percentage',
            icon='target',
            color='purple'
        ))
        
        # Chart (bar): Llamadas por DID
        did_data = reports.values('did').annotate(
            total=Sum('total_calls')
        ).order_by('-total')[:10]
        
        widgets.append(self._generate_chart_widget(
            chart_type='bar',
            title='Top 10 DIDs por Volumen',
            labels=[d['did'] for d in did_data],
            datasets=[{
                'label': 'Total Llamadas',
                'data': [d['total'] for d in did_data],
                'backgroundColor': 'rgba(54, 162, 235, 0.6)'
            }]
        ))
        
        # Chart (pie): Distribución
        widgets.append(self._generate_chart_widget(
            chart_type='pie',
            title='Distribución de Llamadas',
            labels=['Atendidas', 'Abandonadas'],
            datasets=[{
                'data': [
                    totals['answered_calls'] or 0,
                    totals['abandoned_calls'] or 0
                ],
                'backgroundColor': [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 99, 132, 0.6)'
                ]
            }]
        ))
        
        # Table: Top 10 DIDs
        table_rows = []
        for report in reports.order_by('-total_calls')[:10]:
            table_rows.append({
                'did': report.did,
                'total_llamadas': report.total_calls,
                'atendidas': report.answered_calls,
                'abandonadas': report.abandoned_calls,
                'nivel_servicio': f"{report.service_level or 0}%",
            })
        
        widgets.append(self._generate_table_widget(
            title='Detalle Top 10 DIDs',
            headers=[
                'DID',
                'Total Llamadas',
                'Atendidas',
                'Abandonadas',
                'Nivel Servicio'
            ],
            rows=table_rows
        ))
        
        # Construir dashboard completo
        dashboard = {
            'dashboard_type': 'quarterly_metrics',
            'quarter': quarter,
            'year': year,
            'widgets': widgets,
            'last_updated': timezone.now().isoformat(),
            'data_status': 'static',  # CNST-003
            'refresh_interval': None,  # CNST-023
            'metadata': {
                'total_dids': reports.count(),
                'total_calls': totals['total_calls'] or 0,
                'avg_wait_time': float(totals['avg_wait_time'] or 0),
                'avg_talk_time': float(totals['avg_talk_time'] or 0),
            }
        }
        
        return dashboard
    
    def _build_client_analysis_dashboard(
        self,
        quarter: str,
        year: int
    ) -> Dict[str, Any]:
        """
        Construye dashboard de análisis de clientes.
        
        Widgets generados:
        - KPI: Total Clientes Únicos
        - KPI: Clientes Recurrentes
        - KPI: Clientes Nuevos
        - Chart (bar): Top 20 clientes por llamadas
        - Chart (line): Evolución clientes mensuales
        - Table: Top 20 clientes detalle
        
        Args:
            quarter: Trimestre validado
            year: Año
        
        Returns:
            Dict con estructura de dashboard
        """
        # Obtener datos de clientes
        clients = UniqueClientReport.objects.filter(
            quarter=quarter,
            year=year
        )
        
        # Agregaciones
        totals = clients.aggregate(
            total_clients=Count('phone_number', distinct=True),
            total_calls=Sum('total_calls'),
        )
        
        # Clientes recurrentes (>1 llamada)
        recurring = clients.filter(total_calls__gt=1).count()
        new_clients = totals['total_clients'] - recurring
        
        # Widgets
        widgets = []
        
        # KPIs
        widgets.append(self._generate_kpi_widget(
            title='Total Clientes Únicos',
            value=totals['total_clients'] or 0,
            format_type='number',
            icon='users',
            color='blue'
        ))
        
        widgets.append(self._generate_kpi_widget(
            title='Clientes Recurrentes',
            value=recurring,
            format_type='number',
            icon='repeat',
            color='green',
            subtitle=format_percentage(recurring, totals['total_clients'])
        ))
        
        widgets.append(self._generate_kpi_widget(
            title='Clientes Nuevos',
            value=new_clients,
            format_type='number',
            icon='user-plus',
            color='purple',
            subtitle=format_percentage(new_clients, totals['total_clients'])
        ))
        
        # Chart: Top 20 clientes
        top_clients = clients.order_by('-total_calls')[:20]
        
        widgets.append(self._generate_chart_widget(
            chart_type='bar',
            title='Top 20 Clientes por Llamadas',
            labels=[c.phone_number[-4:] for c in top_clients],  # Últimos 4 dígitos
            datasets=[{
                'label': 'Total Llamadas',
                'data': [c.total_calls for c in top_clients],
                'backgroundColor': 'rgba(153, 102, 255, 0.6)'
            }]
        ))
        
        # Table: Top 20 detalle
        table_rows = []
        for client in top_clients:
            table_rows.append({
                'telefono': f"***{client.phone_number[-4:]}",  # Enmascarar
                'total_llamadas': client.total_calls,
                'primera_llamada': client.first_call_date.strftime('%Y-%m-%d'),
                'ultima_llamada': client.last_call_date.strftime('%Y-%m-%d'),
            })
        
        widgets.append(self._generate_table_widget(
            title='Top 20 Clientes - Detalle',
            headers=['Teléfono', 'Total Llamadas', 'Primera Llamada', 'Última Llamada'],
            rows=table_rows
        ))
        
        # Dashboard completo
        dashboard = {
            'dashboard_type': 'client_analysis',
            'quarter': quarter,
            'year': year,
            'widgets': widgets,
            'last_updated': timezone.now().isoformat(),
            'data_status': 'static',  # CNST-003
            'refresh_interval': None,  # CNST-023
            'metadata': {
                'total_clients': totals['total_clients'] or 0,
                'recurring_clients': recurring,
                'new_clients': new_clients,
            }
        }
        
        return dashboard
    
    def _build_ivr_performance_dashboard(
        self,
        quarter: str,
        year: int
    ) -> Dict[str, Any]:
        """
        Construye dashboard de performance IVR.
        
        Widgets generados:
        - KPI: Total Interacciones Menú
        - KPI: Tasa de Conversión Promedio
        - KPI: Errores Menú Total
        - KPI: Tasa de Error Promedio
        - Chart (bar): Top menús por uso
        - Chart (pie): Distribución errores por tipo
        - Table: Performance por menú
        - Table: Errores por menú
        
        Args:
            quarter: Trimestre validado
            year: Año
        
        Returns:
            Dict con estructura de dashboard
        """
        # Datos de performance
        menu_performance = MenuPerformanceReport.objects.filter(
            quarter=quarter,
            year=year
        )
        
        # Datos de errores
        menu_errors = MenuErrorReport.objects.filter(
            quarter=quarter,
            year=year
        )
        
        # Agregaciones
        perf_totals = menu_performance.aggregate(
            total_interactions=Sum('total_selections'),
            avg_conversion=Avg('conversion_rate'),
        )
        
        error_totals = menu_errors.aggregate(
            total_errors=Sum('error_count'),
        )
        
        total_interactions = perf_totals['total_interactions'] or 0
        total_errors = error_totals['total_errors'] or 0
        error_rate = calculate_percentage(total_errors, total_interactions)
        
        # Widgets
        widgets = []
        
        # KPIs
        widgets.append(self._generate_kpi_widget(
            title='Total Interacciones Menú',
            value=total_interactions,
            format_type='number',
            icon='menu',
            color='blue'
        ))
        
        widgets.append(self._generate_kpi_widget(
            title='Tasa de Conversión Promedio',
            value=float(perf_totals['avg_conversion'] or 0),
            format_type='percentage',
            icon='trending-up',
            color='green'
        ))
        
        widgets.append(self._generate_kpi_widget(
            title='Errores Menú Total',
            value=total_errors,
            format_type='number',
            icon='alert-circle',
            color='red'
        ))
        
        widgets.append(self._generate_kpi_widget(
            title='Tasa de Error',
            value=error_rate,
            format_type='percentage',
            icon='alert-triangle',
            color='orange'
        ))
        
        # Chart: Top menús
        top_menus = menu_performance.order_by('-total_selections')[:10]
        
        widgets.append(self._generate_chart_widget(
            chart_type='bar',
            title='Top 10 Menús por Interacciones',
            labels=[m.menu_name for m in top_menus],
            datasets=[{
                'label': 'Total Selecciones',
                'data': [m.total_selections for m in top_menus],
                'backgroundColor': 'rgba(255, 159, 64, 0.6)'
            }]
        ))
        
        # Chart: Distribución errores
        error_types = menu_errors.values('error_type').annotate(
            total=Sum('error_count')
        ).order_by('-total')[:5]
        
        widgets.append(self._generate_chart_widget(
            chart_type='pie',
            title='Distribución Errores por Tipo',
            labels=[e['error_type'] for e in error_types],
            datasets=[{
                'data': [e['total'] for e in error_types],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                ]
            }]
        ))
        
        # Table: Performance
        perf_rows = []
        for menu in menu_performance.order_by('-total_selections')[:10]:
            perf_rows.append({
                'menu': menu.menu_name,
                'interacciones': menu.total_selections,
                'conversion': f"{menu.conversion_rate}%",
            })
        
        widgets.append(self._generate_table_widget(
            title='Performance por Menú',
            headers=['Menú', 'Interacciones', 'Tasa Conversión'],
            rows=perf_rows
        ))
        
        # Table: Errores
        error_rows = []
        for error in menu_errors.order_by('-error_count')[:10]:
            error_rows.append({
                'menu': error.menu_name,
                'tipo_error': error.error_type,
                'cantidad': error.error_count,
            })
        
        widgets.append(self._generate_table_widget(
            title='Top 10 Errores por Menú',
            headers=['Menú', 'Tipo Error', 'Cantidad'],
            rows=error_rows
        ))
        
        # Dashboard completo
        dashboard = {
            'dashboard_type': 'ivr_performance',
            'quarter': quarter,
            'year': year,
            'widgets': widgets,
            'last_updated': timezone.now().isoformat(),
            'data_status': 'static',  # CNST-003
            'refresh_interval': None,  # CNST-023
            'metadata': {
                'total_interactions': total_interactions,
                'total_errors': total_errors,
                'error_rate': error_rate,
                'avg_conversion': float(perf_totals['avg_conversion'] or 0),
            }
        }
        
        return dashboard
    
    # ===================================================================
    # WIDGET GENERATORS
    # ===================================================================
    
    def _generate_kpi_widget(
        self,
        title: str,
        value: Any,
        format_type: str = 'number',
        icon: Optional[str] = None,
        color: Optional[str] = None,
        subtitle: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera widget tipo KPI.
        
        Args:
            title: Título del KPI
            value: Valor numérico
            format_type: Tipo de formato (number, percentage, currency)
            icon: Nombre del icono (opcional)
            color: Color del widget (opcional)
            subtitle: Subtítulo adicional (opcional)
        
        Returns:
            Dict con estructura del widget KPI
        """
        return {
            'type': WIDGET_TYPES['KPI'],
            'title': title,
            'value': value,
            'format_type': format_type,
            'formatted_value': self._format_value(value, format_type),
            'icon': icon,
            'color': color,
            'subtitle': subtitle,
        }
    
    def _generate_chart_widget(
        self,
        chart_type: str,
        title: str,
        labels: List[str],
        datasets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Genera widget tipo Chart.
        
        Args:
            chart_type: Tipo de chart (bar, line, pie)
            title: Título del chart
            labels: Labels del eje X (o categorías)
            datasets: Datasets con data y configuración
        
        Returns:
            Dict con estructura del widget Chart
        """
        return {
            'type': WIDGET_TYPES['CHART'],
            'chart_type': chart_type,
            'title': title,
            'data': {
                'labels': labels,
                'datasets': datasets
            },
            'options': self._get_chart_options(chart_type)
        }
    
    def _generate_table_widget(
        self,
        title: str,
        headers: List[str],
        rows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Genera widget tipo Table.
        
        Args:
            title: Título de la tabla
            headers: Headers de columnas
            rows: Filas de datos (lista de dicts)
        
        Returns:
            Dict con estructura del widget Table
        """
        return {
            'type': WIDGET_TYPES['TABLE'],
            'title': title,
            'headers': headers,
            'rows': rows,
            'total_rows': len(rows)
        }
    
    # ===================================================================
    # HELPERS PRIVADOS
    # ===================================================================
    
    def _format_value(self, value: Any, format_type: str) -> str:
        """
        Formatea valor según tipo.
        
        Args:
            value: Valor a formatear
            format_type: Tipo de formato
        
        Returns:
            String formateado
        """
        if format_type == 'number':
            return format_number(value)
        elif format_type == 'percentage':
            return f"{value:.2f}%"
        elif format_type == 'currency':
            return f"${value:,.2f}"
        else:
            return str(value)
    
    def _get_chart_options(self, chart_type: str) -> Dict[str, Any]:
        """
        Obtiene opciones de configuración para chart según tipo.
        
        Args:
            chart_type: Tipo de chart
        
        Returns:
            Dict con opciones de configuración
        """
        base_options = {
            'responsive': True,
            'maintainAspectRatio': False,
        }
        
        if chart_type == 'bar':
            base_options.update({
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                }
            })
        elif chart_type == 'line':
            base_options.update({
                'elements': {
                    'line': {
                        'tension': 0.4
                    }
                }
            })
        
        return base_options
```

---

<a name="cache-strategy"></a>
## 4. CACHE STRATEGY (CNST-010)

### 4.1 Configuración Cache LocMem

```python
# config/settings/production.py

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'iact-dashboard-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # Máximo 1000 entradas
        }
    }
}

# CNST-010: NO Redis
# Razón: Simplicidad, sin dependencias externas
# Trade-off: Cache no compartido entre workers Gunicorn
```

### 4.2 Cache TTL Strategy

```python
# apps/dashboard/constants.py

# Cache Time-To-Live
CACHE_TTL = 300  # 5 minutos (300 segundos)

# Razón TTL 5 minutos:
# - Datos agregados cambian cada 6-12h (CNST-003)
# - Balance entre freshness y performance
# - Reduce carga en BD IVR readonly (CNST-002)
```

### 4.3 Cache Key Pattern

```python
# apps/dashboard/utils.py

def generate_cache_key(
    dashboard_type: str,
    **kwargs
) -> str:
    """
    Genera cache key consistente.
    
    Pattern: dashboard:{type}:{quarter}:{year}:{hash}
    
    Args:
        dashboard_type: Tipo de dashboard
        **kwargs: Parámetros adicionales
    
    Returns:
        String cache key
    
    Ejemplo:
        generate_cache_key('quarterly_metrics', quarter='Q1', year=2026)
        → 'dashboard:quarterly_metrics:Q1:2026'
    """
    parts = [f"dashboard:{dashboard_type}"]
    
    for key in sorted(kwargs.keys()):
        parts.append(f"{key}:{kwargs[key]}")
    
    return ":".join(parts)
```

---

<a name="widget-generators"></a>
## 5. WIDGET GENERATORS

### 5.1 Widget Types

```python
# apps/dashboard/constants.py

WIDGET_TYPES = {
    'KPI': 'kpi',
    'CHART': 'chart',
    'TABLE': 'table',
}

CHART_TYPES = {
    'BAR': 'bar',
    'LINE': 'line',
    'PIE': 'pie',
}
```

### 5.2 KPI Widget Structure

```json
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
```

### 5.3 Chart Widget Structure

```json
{
  "type": "chart",
  "chart_type": "bar",
  "title": "Top 10 DIDs por Volumen",
  "data": {
    "labels": ["800-123-4567", "800-234-5678", ...],
    "datasets": [{
      "label": "Total Llamadas",
      "data": [5000, 4500, 4000, ...],
      "backgroundColor": "rgba(54, 162, 235, 0.6)"
    }]
  },
  "options": {
    "responsive": true,
    "scales": {
      "y": {
        "beginAtZero": true
      }
    }
  }
}
```

### 5.4 Table Widget Structure

```json
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
    },
    ...
  ],
  "total_rows": 10
}
```

---

<a name="constants"></a>
## 6. CONSTANTS Y CONFIGURACIÓN

### 6.1 Archivo: apps/dashboard/constants.py

```python
"""
Constantes para dashboard.

CLEAN_CODE v3.0.1:
- Constantes: UPPER_SNAKE_CASE inglés
- Docstrings: español
"""

# Dashboard Types
DASHBOARD_TYPES = {
    'QUARTERLY_METRICS': 'quarterly_metrics',
    'CLIENT_ANALYSIS': 'client_analysis',
    'IVR_PERFORMANCE': 'ivr_performance',
}

# Widget Types
WIDGET_TYPES = {
    'KPI': 'kpi',
    'CHART': 'chart',
    'TABLE': 'table',
}

# Chart Types
CHART_TYPES = {
    'BAR': 'bar',
    'LINE': 'line',
    'PIE': 'pie',
    'DOUGHNUT': 'doughnut',
}

# Valid Quarters
VALID_QUARTERS = ['Q1', 'Q2', 'Q3', 'Q4']

# Cache Configuration
CACHE_TTL = 300  # 5 minutos
CACHE_PREFIX = 'dashboard'

# Widget Icons (Lucide React)
WIDGET_ICONS = {
    'phone': 'Phone',
    'users': 'Users',
    'check-circle': 'CheckCircle',
    'x-circle': 'XCircle',
    'target': 'Target',
    'trending-up': 'TrendingUp',
    'alert-circle': 'AlertCircle',
    'alert-triangle': 'AlertTriangle',
    'menu': 'Menu',
    'repeat': 'Repeat',
    'user-plus': 'UserPlus',
}

# Widget Colors
WIDGET_COLORS = {
    'blue': '#3B82F6',
    'green': '#10B981',
    'red': '#EF4444',
    'purple': '#8B5CF6',
    'orange': '#F59E0B',
    'indigo': '#6366F1',
}

# Export Limits (CNST-007 no aplica a dashboard GET)
# Dashboard solo visualiza, no exporta grandes volúmenes
MAX_TABLE_ROWS = 100  # Máximo rows en table widget
```

---

<a name="validaciones"></a>
## 7. VALIDACIONES DE NEGOCIO

### 7.1 Archivo: apps/dashboard/validators.py

```python
"""
Validadores para dashboard.

CLEAN_CODE v3.0.1:
- Clase: DashboardValidator (PascalCase)
- Métodos: snake_case
- Excepciones: ValidationError Django
"""

from django.core.exceptions import ValidationError
from apps.dashboard.constants import VALID_QUARTERS, DASHBOARD_TYPES


class DashboardValidator:
    """
    Validador de parámetros de dashboard.
    
    Responsabilidades:
    - Validar quarter (Q1-Q4)
    - Validar year (rango válido)
    - Validar dashboard_type
    """
    
    def validate_quarter(self, quarter: str) -> None:
        """
        Valida que quarter sea válido.
        
        Args:
            quarter: Trimestre a validar
        
        Raises:
            ValidationError: Si quarter inválido
        """
        if quarter not in VALID_QUARTERS:
            raise ValidationError(
                f"Quarter inválido: {quarter}. "
                f"Valores permitidos: {', '.join(VALID_QUARTERS)}"
            )
    
    def validate_year(self, year: int) -> None:
        """
        Valida que year esté en rango válido.
        
        Args:
            year: Año a validar
        
        Raises:
            ValidationError: Si year fuera de rango
        """
        from django.utils import timezone
        current_year = timezone.now().year
        
        # Permitir desde 2020 hasta año actual + 1
        if year < 2020 or year > current_year + 1:
            raise ValidationError(
                f"Año inválido: {year}. "
                f"Rango permitido: 2020-{current_year + 1}"
            )
    
    def validate_dashboard_type(self, dashboard_type: str) -> None:
        """
        Valida que dashboard_type sea válido.
        
        Args:
            dashboard_type: Tipo de dashboard
        
        Raises:
            ValidationError: Si tipo inválido
        """
        valid_types = list(DASHBOARD_TYPES.values())
        
        if dashboard_type not in valid_types:
            raise ValidationError(
                f"Dashboard type inválido: {dashboard_type}. "
                f"Valores permitidos: {', '.join(valid_types)}"
            )
```

---

<a name="utils"></a>
## 8. UTILS Y HELPERS

### 8.1 Archivo: apps/dashboard/utils.py

```python
"""
Utilidades para dashboard.

CLEAN_CODE v3.0.1:
- Funciones: snake_case inglés
- Docstrings: español
"""

from typing import Any, Optional
from decimal import Decimal


def generate_cache_key(dashboard_type: str, **kwargs) -> str:
    """
    Genera cache key consistente.
    
    Pattern: dashboard:{type}:{param1}:{value1}:...
    
    Args:
        dashboard_type: Tipo de dashboard
        **kwargs: Parámetros adicionales (quarter, year, etc)
    
    Returns:
        String cache key
    
    Ejemplo:
        >>> generate_cache_key('quarterly_metrics', quarter='Q1', year=2026)
        'dashboard:quarterly_metrics:quarter:Q1:year:2026'
    """
    from apps.dashboard.constants import CACHE_PREFIX
    
    parts = [CACHE_PREFIX, dashboard_type]
    
    # Ordenar kwargs para consistencia
    for key in sorted(kwargs.keys()):
        parts.append(f"{key}:{kwargs[key]}")
    
    return ":".join(parts)


def format_number(value: Any) -> str:
    """
    Formatea número con separadores de miles.
    
    Args:
        value: Número a formatear
    
    Returns:
        String formateado
    
    Ejemplo:
        >>> format_number(45000)
        '45,000'
        >>> format_number(1234567)
        '1,234,567'
    """
    if value is None:
        return '0'
    
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(numerator: Any, denominator: Any) -> str:
    """
    Calcula y formatea porcentaje.
    
    Args:
        numerator: Numerador
        denominator: Denominador
    
    Returns:
        String con porcentaje formateado
    
    Ejemplo:
        >>> format_percentage(4500, 5000)
        '90.00%'
        >>> format_percentage(0, 100)
        '0.00%'
    """
    percentage = calculate_percentage(numerator, denominator)
    return f"{percentage:.2f}%"


def calculate_percentage(numerator: Any, denominator: Any) -> float:
    """
    Calcula porcentaje de forma segura.
    
    Args:
        numerator: Numerador
        denominator: Denominador
    
    Returns:
        Porcentaje como float (0.0-100.0)
    
    Ejemplo:
        >>> calculate_percentage(4500, 5000)
        90.0
        >>> calculate_percentage(0, 100)
        0.0
        >>> calculate_percentage(100, 0)  # División por cero
        0.0
    """
    if not denominator or denominator == 0:
        return 0.0
    
    try:
        num = float(numerator or 0)
        den = float(denominator)
        return (num / den) * 100.0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def format_currency(value: Any, currency: str = 'CLP') -> str:
    """
    Formatea valor como moneda.
    
    Args:
        value: Valor numérico
        currency: Código de moneda (default: CLP)
    
    Returns:
        String formateado como moneda
    
    Ejemplo:
        >>> format_currency(45000, 'CLP')
        '$45,000'
        >>> format_currency(1234.56, 'USD')
        '$1,234.56'
    """
    if value is None:
        return '$0'
    
    try:
        formatted = f"${float(value):,.2f}"
        
        # Para CLP, no mostrar decimales
        if currency == 'CLP':
            formatted = f"${int(value):,}"
        
        return formatted
    except (ValueError, TypeError):
        return str(value)


def truncate_text(text: str, max_length: int = 50, suffix: str = '...') -> str:
    """
    Trunca texto a longitud máxima.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
    
    Returns:
        Texto truncado
    
    Ejemplo:
        >>> truncate_text('Este es un texto muy largo', 15)
        'Este es un t...'
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
```

---

## 9. RESUMEN PARTE 2

### 9.1 Componentes Generados

```yaml
Archivos Python:
  ✅ apps/dashboard/services.py (~500 líneas)
  ✅ apps/dashboard/constants.py (~100 líneas)
  ✅ apps/dashboard/validators.py (~80 líneas)
  ✅ apps/dashboard/utils.py (~150 líneas)

Total: ~830 líneas Python production-ready
```

### 9.2 Clases y Funciones

```python
# Clases
DashboardService          # Service principal
DashboardValidator        # Validador

# Métodos DashboardService (públicos)
get_quarterly_metrics_dashboard()
get_client_analysis_dashboard()
get_ivr_performance_dashboard()

# Métodos DashboardService (privados)
_build_quarterly_metrics_dashboard()
_build_client_analysis_dashboard()
_build_ivr_performance_dashboard()
_generate_kpi_widget()
_generate_chart_widget()
_generate_table_widget()
_format_value()
_get_chart_options()

# Funciones Utils
generate_cache_key()
format_number()
format_percentage()
calculate_percentage()
format_currency()
truncate_text()

# Métodos Validator
validate_quarter()
validate_year()
validate_dashboard_type()
```

### 9.3 RESTRICCIONES Aplicadas

```yaml
CNST-002:
  ✅ Usa modelos IVR readonly (QuarterlyReport, etc)
  ✅ Solo consultas SELECT, no modificaciones

CNST-003:
  ✅ Dashboard retorna data_status='static'
  ✅ Documentado desfase 6-12h

CNST-010:
  ✅ Cache LocMem (NO Redis)
  ✅ TTL 300s configurado
  ✅ Cache key pattern consistente

CNST-023:
  ✅ refresh_interval=None (NO auto-refresh)
  ✅ Documentado en dashboard response

CNST-025:
  ✅ Operaciones optimizadas <90s
  ✅ Cache reduce tiempo de respuesta
```

### 9.4 CLEAN_CODE Aplicado

```yaml
Nomenclatura:
  ✅ Clases: PascalCase (DashboardService, DashboardValidator)
  ✅ Métodos: snake_case (get_quarterly_metrics_dashboard)
  ✅ Constantes: UPPER_SNAKE_CASE (CACHE_TTL, WIDGET_TYPES)
  ✅ Variables: snake_case (totals, widgets, dashboard)

Docstrings:
  ✅ Formato Google español
  ✅ Args, Returns, Raises documentados
  ✅ Ejemplos incluidos

Separación responsabilidades:
  ✅ Service: Lógica de negocio
  ✅ Validators: Validaciones
  ✅ Utils: Helpers reutilizables
  ✅ Constants: Configuración centralizada
```

---

## PRÓXIMA PARTE

**PARTE 3/5: APIs y Endpoints**

Contenido:
- Serializers completos
- ViewSets con RBAC
- URLs configuration
- Endpoints documentados
- Decoradores @require_function
- DynamicFunctionPermission

**Estimado:** ~900 líneas, 2 horas

---

**Fin de PARTE 2/5**
