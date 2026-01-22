---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Relaciones entre Apps
categoria: arquitectura/relaciones
tema: PIPELINE (Monitoring) y REPORTS (Consumption)
autor: Claude Technical Analysis
tags: [pipeline, reports, monitoring, consumption, exporters, dashboards]
relacionado:
  - ANALISIS_RELACIONES_v2.0.0_PARTE_1.md
  - ANALISIS_RELACIONES_v2.0.0_PARTE_2.md
  - ANALISIS_APP_PIPELINE_REFACTORING_v2.0.0.md
estado: completo-definitivo
partes: 3/6
---

# ANÁLISIS DE RELACIONES v2.0.0 - PARTE 3/6

**PIPELINE (Monitoring) y REPORTS (Consumption)**

---

## TABLA DE CONTENIDOS (PARTE 3)

1. [apps/pipeline/ - Monitoring de ETL](#pipeline)
2. [apps/reports/ - Consumption de Datos](#reports)
3. [Relación PIPELINE ↔ REPORTS](#pipeline-reports)
4. [Exporters (Excel/CSV/PDF)](#exporters)
5. [Dashboards en Tiempo Real](#dashboards)

---

<a name="pipeline"></a>
## 1. apps/pipeline/ - MONITORING DE ETL

### 1.1 Propósito y Alcance

```
apps/pipeline/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROPÓSITO:
  Monitorear que ETL JOB corre correctamente

RESPONSABILIDADES:
  ✅ Verificar que ETL ejecutó para una fecha
  ✅ Dashboard de estado de todos los ETLs
  ✅ Tracking de ejecuciones (ETLExecution model)
  ✅ Alertas si ETL falla
  ✅ API endpoints para consultar estado

NO ES RESPONSABLE DE:
  ❌ Ejecutar ETL (corre fuera de Django)
  ❌ Procesamiento de datos
  ❌ Scheduling de ETL
  ❌ Extract/Transform/Load

USUARIOS:
  - Administradores del sistema
  - Apps que necesitan verificar datos (REPORTS)
  - Monitoring tools (Prometheus, Grafana, etc)
```

### 1.2 Arquitectura de PIPELINE

```
┌─────────────────────────────────────────────────────────────┐
│ apps/pipeline/                                              │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ models.py                                               ││
│ │                                                          ││
│ │ class ETLExecution(models.Model):                       ││
│ │     """Tracking de ejecuciones de ETL."""              ││
│ │                                                          ││
│ │     etl_name = CharField()                              ││
│ │     fecha_procesada = DateField()                       ││
│ │     status = CharField(choices=['success', 'failed'])   ││
│ │     records_processed = IntegerField()                  ││
│ │     error_message = TextField()                         ││
│ │     started_at = DateTimeField()                        ││
│ │     completed_at = DateTimeField()                      ││
│ │                                                          ││
│ │     Meta:                                               ││
│ │         managed = True  # Django crea tabla             ││
│ │         db_table = 'pipeline_etlexecution'              ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ services.py                                             ││
│ │                                                          ││
│ │ class ETLMonitoringService:                             ││
│ │     """Servicios para monitorear ETL."""               ││
│ │                                                          ││
│ │     @staticmethod                                       ││
│ │     def check_etl_status(etl_name, fecha):              ││
│ │         """Verificar si ETL corrió."""                 ││
│ │         # Query ETLExecution                            ││
│ │         # Return status info                            ││
│ │                                                          ││
│ │     @staticmethod                                       ││
│ │     def get_latest_processed_date(etl_name):            ││
│ │         """Última fecha procesada exitosamente."""     ││
│ │                                                          ││
│ │     @staticmethod                                       ││
│ │     def get_etl_dashboard():                            ││
│ │         """Dashboard de estado de todos los ETLs."""   ││
│ │                                                          ││
│ │     @staticmethod                                       ││
│ │     def get_failed_executions(days=7):                  ││
│ │         """Ejecuciones fallidas recientes."""          ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ views.py                                                ││
│ │                                                          ││
│ │ class ETLMonitoringViewSet(viewsets.ViewSet):           ││
│ │     """API endpoints para monitoring."""               ││
│ │                                                          ││
│ │     @action(detail=False, methods=['get'])              ││
│ │     def dashboard(self, request):                       ││
│ │         """GET /api/v1/pipeline/dashboard/"""          ││
│ │                                                          ││
│ │     @action(detail=False, methods=['get'])              ││
│ │     def check_status(self, request):                    ││
│ │         """GET /api/v1/pipeline/check-status/          ││
│ │            ?etl=cmenu_diario&fecha=2025-08-17"""       ││
│ │                                                          ││
│ │     @action(detail=False, methods=['get'])              ││
│ │     def failed_executions(self, request):               ││
│ │         """GET /api/v1/pipeline/failed-executions/     ││
│ │            ?days=7"""                                   ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ serializers.py                                          ││
│ │                                                          ││
│ │ class ETLExecutionSerializer(serializers.ModelSerializer):││
│ │     duration_seconds = serializers.FloatField()         ││
│ │     class Meta:                                         ││
│ │         model = ETLExecution                            ││
│ │         fields = '__all__'                              ││
│ └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 1.3 ETLMonitoringService - Código Completo

```python
# ════════════════════════════════════════════════════════════
# apps/pipeline/services.py
# ════════════════════════════════════════════════════════════

from datetime import date, datetime, timedelta
from typing import Dict, Optional, List
from django.db.models import Q
from apps.pipeline.models import ETLExecution


class ETLMonitoringService:
    """
    Servicio para monitorear estado de ETLs.
    
    NO ejecuta ETL - solo verifica que corrió correctamente.
    """
    
    # ETLs conocidos del sistema
    KNOWN_ETLS = [
        'cmenu_diario',
        'llamadas_diarias',
        'metricas_semanales',
        'dashboard_agentes',
        'reporte_sucursales'
        # ... agregar más según necesidad
    ]
    
    @staticmethod
    def check_etl_status(etl_name: str, fecha: date) -> Dict:
        """
        Verificar si ETL corrió para una fecha específica.
        
        Args:
            etl_name: Nombre del ETL (ej: 'cmenu_diario')
            fecha: Fecha a verificar
        
        Returns:
            {
                'executed': bool,
                'status': str ('success', 'failed', 'not_run'),
                'records_processed': int,
                'last_run': datetime,
                'duration_seconds': float,
                'error_message': str
            }
        
        Example:
            >>> status = ETLMonitoringService.check_etl_status(
            ...     'cmenu_diario',
            ...     date(2025, 8, 17)
            ... )
            >>> print(status['status'])
            'success'
        """
        try:
            # Buscar última ejecución para esta fecha
            execution = ETLExecution.objects.filter(
                etl_name=etl_name,
                fecha_procesada=fecha
            ).latest('started_at')
            
            return {
                'executed': True,
                'status': execution.status,
                'records_processed': execution.records_processed,
                'last_run': execution.completed_at or execution.started_at,
                'duration_seconds': execution.duration_seconds,
                'error_message': execution.error_message
            }
        
        except ETLExecution.DoesNotExist:
            return {
                'executed': False,
                'status': 'not_run',
                'records_processed': 0,
                'last_run': None,
                'duration_seconds': None,
                'error_message': None
            }
    
    @staticmethod
    def get_latest_processed_date(etl_name: str) -> Optional[date]:
        """
        Obtener última fecha procesada exitosamente.
        
        Args:
            etl_name: Nombre del ETL
        
        Returns:
            date o None si nunca corrió
        
        Example:
            >>> latest = ETLMonitoringService.get_latest_processed_date(
            ...     'cmenu_diario'
            ... )
            >>> print(latest)
            datetime.date(2025, 8, 17)
        """
        execution = ETLExecution.objects.filter(
            etl_name=etl_name,
            status='success'
        ).first()  # Ya ordenado por -started_at
        
        return execution.fecha_procesada if execution else None
    
    @staticmethod
    def get_etl_dashboard() -> Dict[str, Dict]:
        """
        Dashboard completo de estado de todos los ETLs.
        
        Returns:
            {
                'cmenu_diario': {
                    'last_run': datetime,
                    'status': str,
                    'last_processed_date': date,
                    'records_processed': int,
                    'error': str,
                    'is_current': bool  # ¿Procesó datos de ayer?
                },
                ...
            }
        
        Example:
            >>> dashboard = ETLMonitoringService.get_etl_dashboard()
            >>> for etl, info in dashboard.items():
            ...     print(f"{etl}: {info['status']}")
            cmenu_diario: success
            llamadas_diarias: success
        """
        dashboard = {}
        yesterday = date.today() - timedelta(days=1)
        
        for etl_name in ETLMonitoringService.KNOWN_ETLS:
            # Última ejecución de cada ETL
            latest = ETLExecution.objects.filter(
                etl_name=etl_name
            ).first()
            
            if latest:
                dashboard[etl_name] = {
                    'last_run': latest.completed_at or latest.started_at,
                    'status': latest.status,
                    'last_processed_date': latest.fecha_procesada,
                    'records_processed': latest.records_processed,
                    'error': latest.error_message,
                    'is_current': latest.fecha_procesada == yesterday
                }
            else:
                dashboard[etl_name] = {
                    'last_run': None,
                    'status': 'never_run',
                    'last_processed_date': None,
                    'records_processed': 0,
                    'error': None,
                    'is_current': False
                }
        
        return dashboard
    
    @staticmethod
    def get_failed_executions(days: int = 7) -> List[Dict]:
        """
        Obtener ejecuciones fallidas en últimos N días.
        
        Útil para alertas y debugging.
        
        Args:
            days: Número de días hacia atrás
        
        Returns:
            List[{
                'etl_name': str,
                'fecha_procesada': date,
                'error_message': str,
                'started_at': datetime
            }]
        
        Example:
            >>> failed = ETLMonitoringService.get_failed_executions(7)
            >>> for fail in failed:
            ...     print(f"{fail['etl_name']}: {fail['error_message']}")
        """
        since = datetime.now() - timedelta(days=days)
        
        failed = ETLExecution.objects.filter(
            status='failed',
            started_at__gte=since
        ).order_by('-started_at')
        
        return list(failed.values(
            'etl_name',
            'fecha_procesada',
            'error_message',
            'started_at',
            'records_processed'
        ))
    
    @staticmethod
    def verify_data_freshness(etl_name: str, max_age_hours: int = 26) -> Dict:
        """
        Verificar que datos están frescos (no muy viejos).
        
        Args:
            etl_name: Nombre del ETL
            max_age_hours: Máximo de horas desde última ejecución
        
        Returns:
            {
                'is_fresh': bool,
                'age_hours': float,
                'last_run': datetime,
                'warning': str
            }
        
        Example:
            >>> freshness = ETLMonitoringService.verify_data_freshness(
            ...     'cmenu_diario',
            ...     max_age_hours=26
            ... )
            >>> if not freshness['is_fresh']:
            ...     print(f"Warning: {freshness['warning']}")
        """
        execution = ETLExecution.objects.filter(
            etl_name=etl_name,
            status='success'
        ).first()
        
        if not execution:
            return {
                'is_fresh': False,
                'age_hours': None,
                'last_run': None,
                'warning': f"ETL '{etl_name}' nunca ha corrido"
            }
        
        last_run = execution.completed_at or execution.started_at
        age = datetime.now() - last_run
        age_hours = age.total_seconds() / 3600
        
        is_fresh = age_hours <= max_age_hours
        
        warning = None
        if not is_fresh:
            warning = (
                f"Datos tienen {age_hours:.1f} horas de antigüedad "
                f"(límite: {max_age_hours}h)"
            )
        
        return {
            'is_fresh': is_fresh,
            'age_hours': age_hours,
            'last_run': last_run,
            'warning': warning
        }
```

### 1.4 ETLMonitoringViewSet - API Endpoints

```python
# ════════════════════════════════════════════════════════════
# apps/pipeline/views.py
# ════════════════════════════════════════════════════════════

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.access.permissions import IsSuperuser
from apps.pipeline.services import ETLMonitoringService
from apps.pipeline.serializers import ETLExecutionSerializer
from datetime import datetime, date


class ETLMonitoringViewSet(viewsets.ViewSet):
    """
    ViewSet para monitorear ETLs.
    
    Endpoints:
    - GET /api/v1/pipeline/dashboard/
    - GET /api/v1/pipeline/check-status/?etl=X&fecha=Y
    - GET /api/v1/pipeline/failed-executions/?days=7
    - GET /api/v1/pipeline/freshness/?etl=X
    
    Permissions:
    - Solo superusuarios pueden acceder
    """
    
    permission_classes = [IsAuthenticated, IsSuperuser]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Dashboard de estado de todos los ETLs.
        
        GET /api/v1/pipeline/dashboard/
        
        Response:
        {
            "cmenu_diario": {
                "last_run": "2025-08-18T02:15:30Z",
                "status": "success",
                "last_processed_date": "2025-08-17",
                "records_processed": 485,
                "error": null,
                "is_current": true
            },
            "llamadas_diarias": { ... },
            ...
        }
        """
        dashboard = ETLMonitoringService.get_etl_dashboard()
        return Response(dashboard)
    
    @action(detail=False, methods=['get'])
    def check_status(self, request):
        """
        Verificar estado de un ETL específico.
        
        GET /api/v1/pipeline/check-status/?etl=cmenu_diario&fecha=2025-08-17
        
        Query Params:
        - etl: Nombre del ETL (required)
        - fecha: Fecha en formato YYYY-MM-DD (required)
        
        Response:
        {
            "executed": true,
            "status": "success",
            "records_processed": 485,
            "last_run": "2025-08-18T02:15:30Z",
            "duration_seconds": 15.3,
            "error_message": null
        }
        """
        etl_name = request.query_params.get('etl')
        fecha_str = request.query_params.get('fecha')
        
        # Validar parámetros
        if not etl_name or not fecha_str:
            return Response({
                "error": "Parámetros 'etl' y 'fecha' son requeridos"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parsear fecha
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                "error": "Formato de fecha inválido. Usar YYYY-MM-DD"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar estado
        etl_status = ETLMonitoringService.check_etl_status(etl_name, fecha)
        
        return Response(etl_status)
    
    @action(detail=False, methods=['get'])
    def failed_executions(self, request):
        """
        Listar ejecuciones fallidas recientes.
        
        GET /api/v1/pipeline/failed-executions/?days=7
        
        Query Params:
        - days: Número de días hacia atrás (default: 7)
        
        Response:
        [
            {
                "etl_name": "cmenu_diario",
                "fecha_procesada": "2025-08-15",
                "error_message": "Connection timeout to IVR_LEGACY",
                "started_at": "2025-08-16T02:00:00Z",
                "records_processed": 0
            },
            ...
        ]
        """
        days = int(request.query_params.get('days', 7))
        
        # Validar días
        if days < 1 or days > 90:
            return Response({
                "error": "Parámetro 'days' debe estar entre 1 y 90"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        failed = ETLMonitoringService.get_failed_executions(days)
        
        return Response({
            "count": len(failed),
            "days": days,
            "failures": failed
        })
    
    @action(detail=False, methods=['get'])
    def freshness(self, request):
        """
        Verificar frescura de datos de un ETL.
        
        GET /api/v1/pipeline/freshness/?etl=cmenu_diario&max_age=26
        
        Query Params:
        - etl: Nombre del ETL (required)
        - max_age: Máximo de horas (default: 26)
        
        Response:
        {
            "is_fresh": true,
            "age_hours": 6.5,
            "last_run": "2025-08-18T02:15:30Z",
            "warning": null
        }
        """
        etl_name = request.query_params.get('etl')
        max_age = int(request.query_params.get('max_age', 26))
        
        if not etl_name:
            return Response({
                "error": "Parámetro 'etl' es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        freshness = ETLMonitoringService.verify_data_freshness(
            etl_name,
            max_age
        )
        
        return Response(freshness)
```

---

<a name="reports"></a>
## 2. apps/reports/ - CONSUMPTION DE DATOS

### 2.1 Propósito y Alcance

```
apps/reports/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROPÓSITO:
  Consumir datos procesados por ETL y generar reportes

RESPONSABILIDADES:
  ✅ Query datos de tablas agregadas
  ✅ Generar reportes (Excel, CSV, PDF)
  ✅ API endpoints para solicitar reportes
  ✅ Dashboards con métricas
  ✅ Validar disponibilidad de datos (vía PIPELINE)
  ✅ RBAC (vía ACCESS)
  ✅ Soportar N tipos de reportes

NO ES RESPONSABLE DE:
  ❌ ETL (corre fuera de Django)
  ❌ Procesamiento de datos RAW
  ❌ Transformación de datos
  ❌ Agregaciones pesadas (ya hechas por ETL)

USUARIOS:
  - Usuarios finales (reportes)
  - Managers (dashboards)
  - Analistas (exports masivos)
```

### 2.2 Arquitectura de REPORTS

```
┌─────────────────────────────────────────────────────────────┐
│ apps/reports/                                               │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ models.py                                               ││
│ │                                                          ││
│ │ # Modelos de datos agregados (managed=True)             ││
│ │ class CMenuAgregado(models.Model):                      ││
│ │     fecha = DateField()                                 ││
│ │     sucursal = CharField()                              ││
│ │     cmenu_opcion = CharField()                          ││
│ │     total_llamadas = IntegerField()                     ││
│ │     ...                                                 ││
│ │                                                          ││
│ │ class LlamadasDiarias(models.Model):                    ││
│ │     fecha = DateField()                                 ││
│ │     sucursal = CharField()                              ││
│ │     total_llamadas = IntegerField()                     ││
│ │     ...                                                 ││
│ │                                                          ││
│ │ # Metadata de reportes                                  ││
│ │ class Report(SoftDeleteMixin, models.Model):            ││
│ │     """Tracking de reportes generados."""              ││
│ │     user = ForeignKey(User)                             ││
│ │     report_type = CharField()                           ││
│ │     fecha_inicio = DateField()                          ││
│ │     fecha_fin = DateField()                             ││
│ │     file_path = CharField()                             ││
│ │     ...                                                 ││
│ │                                                          ││
│ │ class ExportJob(models.Model):                          ││
│ │     """Jobs de exportación."""                         ││
│ │     status = CharField()                                ││
│ │     ...                                                 ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ services.py                                             ││
│ │                                                          ││
│ │ class CMenuReportService:                               ││
│ │     @staticmethod                                       ││
│ │     def get_cmenu_data(fecha_inicio, fecha_fin,         ││
│ │                        sucursal):                       ││
│ │         """Query datos agregados."""                   ││
│ │                                                          ││
│ │     @staticmethod                                       ││
│ │     def verify_data_availability(fecha):                ││
│ │         """Verificar que ETL corrió."""                ││
│ │                                                          ││
│ │ class DashboardService:                                 ││
│ │     @staticmethod                                       ││
│ │     def get_kpis_diarios():                             ││
│ │         """KPIs para dashboard."""                     ││
│ │                                                          ││
│ │ class ExportService:                                    ││
│ │     @staticmethod                                       ││
│ │     def create_export_job(report_type, params):         ││
│ │         """Crear job de exportación."""                ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ exporters.py                                            ││
│ │                                                          ││
│ │ class ExcelExporter:                                    ││
│ │     @staticmethod                                       ││
│ │     def generate_cmenu_excel(data, sucursal, total):    ││
│ │         """Generar Excel estilo Reporte_cMenu."""      ││
│ │                                                          ││
│ │ class CSVExporter:                                      ││
│ │     @staticmethod                                       ││
│ │     def generate_csv(data, filename):                   ││
│ │         """Generar CSV."""                             ││
│ │                                                          ││
│ │ class PDFExporter:                                      ││
│ │     @staticmethod                                       ││
│ │     def generate_pdf(data, template):                   ││
│ │         """Generar PDF."""                             ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ views.py                                                ││
│ │                                                          ││
│ │ class CMenuReportViewSet(viewsets.ViewSet):             ││
│ │     @action(detail=False, methods=['post'])             ││
│ │     def generate(self, request):                        ││
│ │         """POST /api/v1/reports/cmenu/generate/"""     ││
│ │                                                          ││
│ │ class DashboardViewSet(viewsets.ViewSet):               ││
│ │     @action(detail=False, methods=['get'])              ││
│ │     def kpis(self, request):                            ││
│ │         """GET /api/v1/reports/dashboard/kpis/"""      ││
│ └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 2.3 CMenuReportService - Ejemplo Completo

```python
# ════════════════════════════════════════════════════════════
# apps/reports/services.py
# ════════════════════════════════════════════════════════════

from datetime import date
from typing import List, Dict, Optional
from django.db.models import Sum, Avg, Count
from apps.reports.models import CMenuAgregado
from apps.pipeline.services import ETLMonitoringService


class CMenuReportService:
    """
    Servicio para reportes cMenu.
    
    Consume datos de CMenuAgregado (creados por ETL).
    """
    
    @staticmethod
    def get_cmenu_data(
        fecha_inicio: date,
        fecha_fin: date,
        sucursal: str = 'todas'
    ) -> List[Dict]:
        """
        Query datos agregados de cMenu.
        
        Args:
            fecha_inicio: Fecha inicial
            fecha_fin: Fecha final
            sucursal: 'puebla', 'nacional', 'todas'
        
        Returns:
            List[{
                'fecha': date,
                'sucursal': str,
                'cmenu_opcion': str,
                'total_llamadas': int,
                'duracion_promedio': float
            }]
        
        Example:
            >>> data = CMenuReportService.get_cmenu_data(
            ...     date(2025, 8, 17),
            ...     date(2025, 8, 17),
            ...     'puebla'
            ... )
            >>> len(data)
            25
        """
        queryset = CMenuAgregado.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        )
        
        # Filtrar por sucursal si no es 'todas'
        if sucursal != 'todas':
            queryset = queryset.filter(sucursal=sucursal)
        
        # Ordenar por total descendente
        queryset = queryset.order_by('-total_llamadas')
        
        return list(queryset.values(
            'fecha',
            'sucursal',
            'cmenu_opcion',
            'total_llamadas',
            'duracion_promedio'
        ))
    
    @staticmethod
    def get_total_llamadas(
        fecha_inicio: date,
        fecha_fin: date,
        sucursal: str = 'todas'
    ) -> int:
        """
        Calcular total general de llamadas.
        
        Args:
            fecha_inicio: Fecha inicial
            fecha_fin: Fecha final
            sucursal: Filtro por sucursal
        
        Returns:
            int: Total de llamadas
        
        Example:
            >>> total = CMenuReportService.get_total_llamadas(
            ...     date(2025, 8, 17),
            ...     date(2025, 8, 17),
            ...     'puebla'
            ... )
            >>> print(total)
            132473
        """
        queryset = CMenuAgregado.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        )
        
        if sucursal != 'todas':
            queryset = queryset.filter(sucursal=sucursal)
        
        result = queryset.aggregate(total=Sum('total_llamadas'))
        return result['total'] or 0
    
    @staticmethod
    def verify_data_availability(fecha: date) -> Dict:
        """
        Verificar si datos están disponibles para una fecha.
        
        Usa PIPELINE para verificar que ETL corrió.
        
        Args:
            fecha: Fecha a verificar
        
        Returns:
            {
                'available': bool,
                'etl_status': str,
                'records_count': int,
                'message': str
            }
        
        Example:
            >>> avail = CMenuReportService.verify_data_availability(
            ...     date(2025, 8, 17)
            ... )
            >>> if not avail['available']:
            ...     print(avail['message'])
        """
        # 1. Verificar que ETL corrió
        etl_status = ETLMonitoringService.check_etl_status(
            'cmenu_diario',
            fecha
        )
        
        if not etl_status['executed']:
            return {
                'available': False,
                'etl_status': 'not_run',
                'records_count': 0,
                'message': (
                    f"ETL no ha corrido para {fecha}. "
                    f"El ETL corre diariamente a las 2 AM."
                )
            }
        
        if etl_status['status'] != 'success':
            return {
                'available': False,
                'etl_status': 'failed',
                'records_count': 0,
                'message': (
                    f"ETL falló para {fecha}: "
                    f"{etl_status['error_message']}"
                )
            }
        
        # 2. Verificar que existan datos en la tabla
        count = CMenuAgregado.objects.filter(fecha=fecha).count()
        
        if count == 0:
            return {
                'available': False,
                'etl_status': 'success',
                'records_count': 0,
                'message': (
                    f"ETL corrió exitosamente pero no hay datos "
                    f"para {fecha}"
                )
            }
        
        # 3. Todo OK
        return {
            'available': True,
            'etl_status': 'success',
            'records_count': count,
            'message': f"Datos disponibles ({count} registros)"
        }
    
    @staticmethod
    def get_top_opciones(
        fecha_inicio: date,
        fecha_fin: date,
        limit: int = 10
    ) -> List[Dict]:
        """
        Top N opciones de menú por volumen.
        
        Args:
            fecha_inicio: Fecha inicial
            fecha_fin: Fecha final
            limit: Número de opciones a retornar
        
        Returns:
            List[{
                'cmenu_opcion': str,
                'total_llamadas': int,
                'porcentaje': float
            }]
        """
        # Total general
        total_general = CMenuReportService.get_total_llamadas(
            fecha_inicio,
            fecha_fin
        )
        
        # Top opciones
        top = CMenuAgregado.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        ).values('cmenu_opcion').annotate(
            total=Sum('total_llamadas')
        ).order_by('-total')[:limit]
        
        # Calcular porcentajes
        result = []
        for item in top:
            porcentaje = (
                (item['total'] / total_general * 100)
                if total_general > 0 else 0
            )
            result.append({
                'cmenu_opcion': item['cmenu_opcion'],
                'total_llamadas': item['total'],
                'porcentaje': round(porcentaje, 2)
            })
        
        return result
```

---

<a name="pipeline-reports"></a>
## 3. RELACIÓN PIPELINE ↔ REPORTS

### 3.1 Flujo de Integración

```
┌─────────────────────────────────────────────────────────────┐
│ Usuario solicita reporte                                    │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ apps/reports/ - CMenuReportViewSet.generate()               │
│                                                             │
│ 1. Validar parámetros                                       │
│ 2. Verificar permisos RBAC (via ACCESS)                    │
│ 3. Verificar que ETL corrió (via PIPELINE) ◄─────┐         │
└────────────┬────────────────────────────────────────┼────────┘
             │                                        │
             │                                        │
             ▼                                        │
┌─────────────────────────────────────────────────────────────┐
│ CMenuReportService.verify_data_availability()              │
│                                                             │
│ Llama a:                                                    │
│ ETLMonitoringService.check_etl_status() ─────────────────┐ │
└────────────┬─────────────────────────────────────────────┼──┘
             │                                             │
             │                                             │
             │ ┌───────────────────────────────────────────┘
             │ │
             │ ▼
             │ ┌──────────────────────────────────────────┐
             │ │ apps/pipeline/ - ETLMonitoringService     │
             │ │                                           │
             │ │ Query: ETLExecution                      │
             │ │ WHERE etl_name='cmenu_diario'            │
             │ │ AND fecha_procesada='2025-08-17'         │
             │ │                                           │
             │ │ Return: {                                 │
             │ │   'executed': True,                      │
             │ │   'status': 'success',                   │
             │ │   'records_processed': 485               │
             │ │ }                                         │
             │ └──────────────────┬───────────────────────┘
             │                    │
             │ ◄──────────────────┘
             │
             ▼ Si ETL OK
┌─────────────────────────────────────────────────────────────┐
│ 4. Query datos                                              │
│    CMenuReportService.get_cmenu_data()                      │
│                                                             │
│    SELECT * FROM reporte_cmenu_agregado                     │
│    WHERE fecha='2025-08-17' AND sucursal='puebla'           │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Generar Excel                                            │
│    ExcelExporter.generate_cmenu_excel(data)                 │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Response con archivo                                     │
│    {                                                        │
│      "status": "completed",                                 │
│      "file_url": "/media/reports/cmenu_puebla_170825.xlsx", │
│      "etl_info": { ... }                                    │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Ejemplo de Integración en ViewSet

```python
# ════════════════════════════════════════════════════════════
# apps/reports/views.py - Integración PIPELINE + REPORTS
# ════════════════════════════════════════════════════════════

class CMenuReportViewSet(viewsets.ViewSet):
    """ViewSet para reportes cMenu."""
    
    permission_classes = [IsAuthenticated, CanViewCMenuReport]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generar reporte cMenu.
        
        POST /api/v1/reports/cmenu/generate/
        
        Body:
        {
            "fecha_inicio": "2025-08-17",
            "fecha_fin": "2025-08-17",
            "sucursal": "puebla",
            "formato": "excel"
        }
        
        Response:
        {
            "status": "completed",
            "file_url": "/media/reports/...",
            "etl_info": { ... }
        }
        """
        # ────────────────────────────────────────────────────
        # 1. Validar input
        # ────────────────────────────────────────────────────
        
        serializer = CMenuReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated = serializer.validated_data
        fecha = validated['fecha_inicio']  # Asumimos mismo día
        
        # ────────────────────────────────────────────────────
        # 2. Verificar permisos RBAC (via ACCESS)
        # ────────────────────────────────────────────────────
        
        if not request.user.has_function('reports.view_cmenu_report'):
            return Response({
                "error": "No tiene permiso para ver reportes cMenu"
            }, status=403)
        
        # ────────────────────────────────────────────────────
        # 3. Verificar que ETL corrió (via PIPELINE) ⚡
        # ────────────────────────────────────────────────────
        
        availability = CMenuReportService.verify_data_availability(fecha)
        
        if not availability['available']:
            return Response({
                "error": "Datos no disponibles",
                "message": availability['message'],
                "etl_status": availability['etl_status'],
                "fecha": fecha
            }, status=400)
        
        # ────────────────────────────────────────────────────
        # 4. Query datos
        # ────────────────────────────────────────────────────
        
        data = CMenuReportService.get_cmenu_data(
            fecha_inicio=validated['fecha_inicio'],
            fecha_fin=validated['fecha_fin'],
            sucursal=validated['sucursal']
        )
        
        total = CMenuReportService.get_total_llamadas(
            fecha_inicio=validated['fecha_inicio'],
            fecha_fin=validated['fecha_fin'],
            sucursal=validated['sucursal']
        )
        
        # ────────────────────────────────────────────────────
        # 5. Generar archivo según formato
        # ────────────────────────────────────────────────────
        
        if validated['formato'] == 'excel':
            filepath = ExcelExporter.generate_cmenu_excel(
                data=data,
                sucursal=validated['sucursal'],
                total=total
            )
        elif validated['formato'] == 'csv':
            filepath = CSVExporter.generate_csv(
                data=data,
                filename=f"cmenu_{validated['sucursal']}"
            )
        else:
            return Response({
                "error": "Formato no soportado"
            }, status=400)
        
        # ────────────────────────────────────────────────────
        # 6. Registrar reporte generado (metadata)
        # ────────────────────────────────────────────────────
        
        from apps.reports.models import Report
        
        Report.objects.create(
            user=request.user,
            report_type='cmenu',
            fecha_inicio=validated['fecha_inicio'],
            fecha_fin=validated['fecha_fin'],
            file_path=filepath,
            parameters={'sucursal': validated['sucursal']}
        )
        
        # ────────────────────────────────────────────────────
        # 7. Response
        # ────────────────────────────────────────────────────
        
        file_url = filepath.replace(settings.MEDIA_ROOT, '/media')
        
        return Response({
            "status": "completed",
            "file_url": file_url,
            "total_records": len(data),
            "total_llamadas": total,
            "etl_info": {
                "etl_status": availability['etl_status'],
                "records_count": availability['records_count']
            }
        })
```

---

<a name="exporters"></a>
## 4. EXPORTERS (EXCEL/CSV/PDF)

### 4.1 ExcelExporter - Implementación Completa

```python
# ════════════════════════════════════════════════════════════
# apps/reports/exporters.py
# ════════════════════════════════════════════════════════════

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime
from django.conf import settings
import os


class ExcelExporter:
    """Generador de archivos Excel."""
    
    @staticmethod
    def generate_cmenu_excel(
        data: list,
        sucursal: str,
        total: int
    ) -> str:
        """
        Generar Excel estilo Reporte_cMenu_180825.xlsx
        
        Args:
            data: List[Dict] con datos de cMenu
            sucursal: Nombre de sucursal
            total: Total general de llamadas
        
        Returns:
            str: Filepath del Excel generado
        
        Example:
            >>> data = [
            ...     {'cmenu_opcion': 'ANI', 'total_llamadas': 2181},
            ...     ...
            ... ]
            >>> filepath = ExcelExporter.generate_cmenu_excel(
            ...     data, 'puebla', 132473
            ... )
            >>> print(filepath)
            '/media/reports/cmenu_puebla_170825.xlsx'
        """
        # Crear workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = sucursal.capitalize()
        
        # ────────────────────────────────────────────────────
        # Headers
        # ────────────────────────────────────────────────────
        
        ws['A1'] = 'cMenu'
        ws['B1'] = 'Numero'
        ws['D1'] = 'Total'
        ws['E1'] = total
        
        # Styling headers
        header_font = Font(bold=True, size=12)
        header_fill = PatternFill(
            start_color='4472C4',
            end_color='4472C4',
            fill_type='solid'
        )
        
        for cell in ['A1', 'B1', 'D1', 'E1']:
            ws[cell].font = header_font
            ws[cell].alignment = Alignment(horizontal='center')
        
        # ────────────────────────────────────────────────────
        # Datos
        # ────────────────────────────────────────────────────
        
        row_num = 2
        for item in data:
            ws[f'A{row_num}'] = item['cmenu_opcion']
            ws[f'B{row_num}'] = item['total_llamadas']
            row_num += 1
        
        # ────────────────────────────────────────────────────
        # Ajustar anchos de columna
        # ────────────────────────────────────────────────────
        
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['D'].width = 10
        ws.column_dimensions['E'].width = 15
        
        # ────────────────────────────────────────────────────
        # Guardar archivo
        # ────────────────────────────────────────────────────
        
        # Crear directorio si no existe
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Nombre de archivo
        fecha_str = datetime.now().strftime('%d%m%y')
        filename = f"cmenu_{sucursal}_{fecha_str}.xlsx"
        filepath = os.path.join(reports_dir, filename)
        
        # Guardar
        wb.save(filepath)
        
        return filepath


class CSVExporter:
    """Generador de archivos CSV."""
    
    @staticmethod
    def generate_csv(data: list, filename: str) -> str:
        """
        Generar archivo CSV.
        
        Args:
            data: List[Dict] con datos
            filename: Nombre base del archivo
        
        Returns:
            str: Filepath del CSV generado
        """
        import csv
        
        # Crear directorio
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Filepath
        fecha_str = datetime.now().strftime('%d%m%y')
        filepath = os.path.join(
            reports_dir,
            f"{filename}_{fecha_str}.csv"
        )
        
        # Escribir CSV
        if data:
            keys = data[0].keys()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
        
        return filepath
```

---

<a name="dashboards"></a>
## 5. DASHBOARDS EN TIEMPO REAL

### 5.1 DashboardService

```python
# ════════════════════════════════════════════════════════════
# apps/reports/services.py - DashboardService
# ════════════════════════════════════════════════════════════

class DashboardService:
    """Servicio para dashboards con métricas."""
    
    @staticmethod
    def get_kpis_diarios(fecha: date = None) -> Dict:
        """
        KPIs diarios para dashboard.
        
        Args:
            fecha: Fecha a consultar (default: ayer)
        
        Returns:
            {
                'total_llamadas': int,
                'llamadas_atendidas': int,
                'llamadas_abandonadas': int,
                'duracion_promedio': float,
                'tasa_abandono': float,
                'top_opciones': List[Dict]
            }
        """
        from datetime import timedelta
        
        if fecha is None:
            fecha = date.today() - timedelta(days=1)
        
        # Query CMenuAgregado
        datos_cmenu = CMenuAgregado.objects.filter(fecha=fecha)
        
        total_llamadas = datos_cmenu.aggregate(
            total=Sum('total_llamadas')
        )['total'] or 0
        
        duracion_promedio = datos_cmenu.aggregate(
            promedio=Avg('duracion_promedio')
        )['promedio'] or 0
        
        # Top 5 opciones
        top_opciones = list(
            datos_cmenu.values('cmenu_opcion').annotate(
                total=Sum('total_llamadas')
            ).order_by('-total')[:5]
        )
        
        return {
            'fecha': fecha,
            'total_llamadas': total_llamadas,
            'duracion_promedio': round(duracion_promedio, 2),
            'top_opciones': top_opciones
        }
```

---

## RESUMEN PARTE 3

```
CONTENIDO CUBIERTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ apps/pipeline/ (Monitoring)
   - ETLExecution model
   - ETLMonitoringService (4 métodos)
   - ETLMonitoringViewSet (4 endpoints)
   - Dashboard de estado

✅ apps/reports/ (Consumption)
   - CMenuAgregado, LlamadasDiarias models
   - CMenuReportService
   - DashboardService
   - Integración PIPELINE ↔ REPORTS

✅ Exporters
   - ExcelExporter (openpyxl)
   - CSVExporter
   - Ejemplo completo de generación

✅ Dashboards
   - KPIs diarios
   - Métricas en tiempo real

PRÓXIMA PARTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PARTE 4/6: ACCESS (RBAC)
- Control de permisos granular
- user.has_function()
- Permisos por reporte
```

---

**FIN DE PARTE 3/6**

Documento: ANALISIS_RELACIONES v2.0.0 - PARTE 3/6  
Fecha: 2026-01-17  
Estado: Completo  
Siguiente: PARTE 4/6 - ACCESS (RBAC)
