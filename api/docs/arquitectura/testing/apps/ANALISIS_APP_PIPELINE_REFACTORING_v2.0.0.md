---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Refactorización - App PIPELINE
categoria: arquitectura/testing/apps
tema: App PIPELINE - Monitoreo de ETL (NO ejecución)
autor: Claude Technical Analysis
tags: [pipeline, etl-monitoring, tracking, dashboard]
replaces: ANALISIS_APP_PIPELINE_REFACTORING_v1.0.0.md
relacionado:
  - FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md (flujo correcto)
  - ANALISIS_APP_REPORTS_REFACTORING_v2.0.0.md
estado: corregido-definitivo
---

# ANÁLISIS APP PIPELINE v2.0.0 - CORRECCIÓN DEFINITIVA

**🔴 ACTUALIZADO: ETL es JOB en DB, Pipeline solo MONITOREA**

---

## ⚠️ AVISO DE ACTUALIZACIÓN

```
VERSIÓN ANTERIOR (v1.0.0): CONTENÍA SUPUESTOS INCORRECTOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Asumía que ETLService ejecuta ETL en Python
❌ Describía extract(), transform(), load() methods
❌ APScheduler ejecutando ETL cada 12h
❌ Pipeline guardando en CallRecord

ESTA VERSIÓN (v2.0.0): CORREGIDA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ETL es JOB en DB (stored procedure/cron)
✅ Pipeline solo MONITOREA ejecución de ETL
✅ ETLExecution solo tracking
✅ Dashboard de estado, NO ejecución
```

---

## TABLA DE CONTENIDOS

1. [Propósito Real de la App](#proposito)
2. [Componentes Correctos](#componentes)
3. [Modelos](#modelos)
4. [Services (Monitoring)](#services)
5. [Views (Dashboard)](#views)
6. [Tests](#tests)
7. [Flujo de Datos Real](#flujo)
8. [Comparación v1 vs v2](#comparacion)

---

<a name="proposito"></a>
## 1. PROPÓSITO REAL DE LA APP

### 1.1 Descripción

```
apps/pipeline/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: MONITOREAR ejecución de ETL (NO ejecutar)

Responsabilidades:
✅ Verificar que ETL corrió para una fecha
✅ Dashboard de estado de ETLs
✅ Tracking de ejecuciones (ETLExecution model)
✅ Alertas si ETL no corrió o falló
✅ API endpoints para consultar estado

NO es responsable de:
❌ Ejecutar ETL
❌ Extract/Transform/Load
❌ Scheduling de ETL
❌ Procesamiento de datos

ETL REAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El ETL corre como:
- Stored Procedure en MySQL/Postgres
- Cron job en servidor de DB
- Script Python externo (fuera de Django)

Ejecuta: 2:00 AM diario (día vencido)
Escribe: default DB (misma de Django)
Registra: ETLExecution (para tracking)
```

### 1.2 Arquitectura Real

```
┌─────────────────────────────────────────────────────────────┐
│ ETL JOB (Fuera de Django)                                   │
│                                                             │
│ - Stored procedure en DB                                   │
│ - O cron job ejecutando script                             │
│ - Corre 2 AM diario                                        │
│                                                             │
│ Proceso:                                                    │
│ 1. Extract de IVR_LEGACY                                   │
│ 2. Transform (limpiar, agregar)                            │
│ 3. Load en default DB                                      │
│ 4. INSERT en ETLExecution (tracking)                       │
└────────────┬────────────────────────────────────────────────┘
             │
             │ ETLExecution record created
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ apps/pipeline/ (Django - MONITORING)                        │
│                                                             │
│ - Query ETLExecution (tracking)                            │
│ - Verificar estado                                         │
│ - Dashboard API                                            │
│ - Alertas si falla                                         │
└─────────────────────────────────────────────────────────────┘
```

---

<a name="componentes"></a>
## 2. COMPONENTES CORRECTOS

### 2.1 Estructura de Archivos

```python
apps/pipeline/
│
├── __init__.py
├── apps.py
│
├── models.py ✅
│   └── ETLExecution (tracking de ejecuciones)
│
├── services.py ✅
│   └── ETLMonitoringService (verificar estado)
│
├── views.py ✅
│   └── ETLMonitoringViewSet (dashboard API)
│
├── serializers.py ✅
│   └── ETLExecutionSerializer
│
├── urls.py
└── migrations/
    └── 0001_initial.py (create ETLExecution table)

NO tiene:
❌ scheduler.py (ETL corre fuera de Django)
❌ etl_service.py (procesamiento fuera de Django)
❌ adapters/ (IVRAdapter en apps/ivr_legacy/)
```

---

<a name="modelos"></a>
## 3. MODELOS

### 3.1 ETLExecution (ÚNICO modelo)

```python
# ════════════════════════════════════════════════════════════
# apps/pipeline/models.py
# ════════════════════════════════════════════════════════════

from django.db import models
from apps.core.base_models import SoftDeleteMixin


class ETLExecution(SoftDeleteMixin, models.Model):
    """
    Tracking de ejecuciones de ETL.
    
    IMPORTANTE:
    - Registrado POR el ETL JOB (no por Django)
    - Django solo CONSULTA para monitoreo
    - Tabla en default DB
    """
    
    # Identificación
    etl_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Nombre del ETL (ej: 'cmenu_diario', 'llamadas_diarias')"
    )
    
    # Fecha procesada
    fecha_procesada = models.DateField(
        db_index=True,
        help_text="Fecha de los datos procesados"
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('success', 'Success'),
            ('failed', 'Failed')
        ],
        default='pending',
        db_index=True
    )
    
    # Métricas
    records_processed = models.IntegerField(
        default=0,
        help_text="Cantidad de registros procesados"
    )
    
    # Error info
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Mensaje de error si status='failed'"
    )
    
    # Timestamps
    started_at = models.DateTimeField(
        help_text="Cuándo empezó la ejecución"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Cuándo terminó (success o failed)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True  # Django gestiona tabla
        db_table = 'pipeline_etlexecution'
        ordering = ['-started_at']
        unique_together = [
            ('etl_name', 'fecha_procesada', 'started_at')
        ]
        indexes = [
            models.Index(fields=['etl_name', '-fecha_procesada']),
            models.Index(fields=['status', '-started_at']),
        ]
        verbose_name = 'ETL Execution'
        verbose_name_plural = 'ETL Executions'
    
    def __str__(self):
        return f"{self.etl_name} - {self.fecha_procesada} ({self.status})"
    
    @property
    def duration_seconds(self):
        """Duración de ejecución en segundos."""
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds()
        return None


# ════════════════════════════════════════════════════════════
# ANÁLISIS DEL MODELO
# ════════════════════════════════════════════════════════════

CARACTERÍSTICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ SoftDeleteMixin (hereda de core)
✅ managed=True (Django crea tabla)
✅ unique_together (evita duplicados)
✅ Indexes optimizados (etl_name + fecha_procesada)
✅ 1 property (duration_seconds)
✅ 0 métodos de negocio (modelo delgado)

LÓGICA DE NEGOCIO: 0 líneas ✅
- Solo 1 property (computed field)
- NO hay save() override
- NO hay métodos complejos
```

---

<a name="services"></a>
## 4. SERVICES (MONITORING)

### 4.1 ETLMonitoringService

```python
# ════════════════════════════════════════════════════════════
# apps/pipeline/services.py
# ════════════════════════════════════════════════════════════

from datetime import date, datetime
from typing import Dict, Optional
from apps.pipeline.models import ETLExecution


class ETLMonitoringService:
    """
    Servicio para monitorear estado de ETLs.
    
    NO ejecuta ETL.
    Solo verifica si corrió correctamente.
    """
    
    @staticmethod
    def check_etl_status(etl_name: str, fecha: date) -> Dict:
        """
        Verificar si ETL corrió para una fecha.
        
        Args:
            etl_name: Nombre del ETL ('cmenu_diario', etc)
            fecha: Fecha a verificar
        
        Returns:
            {
                'executed': bool,
                'status': str,
                'records_processed': int,
                'last_run': datetime,
                'duration_seconds': float
            }
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
            date o None
        """
        execution = ETLExecution.objects.filter(
            etl_name=etl_name,
            status='success'
        ).first()  # Ya ordenado por -started_at
        
        return execution.fecha_procesada if execution else None
    
    @staticmethod
    def get_etl_dashboard() -> Dict:
        """
        Dashboard de estado de todos los ETLs.
        
        Returns:
            {
                'cmenu_diario': {...},
                'llamadas_diarias': {...},
                ...
            }
        """
        # ETLs conocidos del sistema
        etls = [
            'cmenu_diario',
            'llamadas_diarias',
            'metricas_semanales'
        ]
        
        dashboard = {}
        
        for etl_name in etls:
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
                    'error': latest.error_message
                }
            else:
                dashboard[etl_name] = {
                    'last_run': None,
                    'status': 'never_run',
                    'last_processed_date': None,
                    'records_processed': 0,
                    'error': None
                }
        
        return dashboard
    
    @staticmethod
    def get_failed_executions(days: int = 7) -> list:
        """
        Obtener ejecuciones fallidas en últimos N días.
        
        Útil para alertas.
        """
        from datetime import timedelta
        
        since = datetime.now() - timedelta(days=days)
        
        failed = ETLExecution.objects.filter(
            status='failed',
            started_at__gte=since
        ).select_related(None)
        
        return list(failed.values(
            'etl_name',
            'fecha_procesada',
            'error_message',
            'started_at'
        ))


# ════════════════════════════════════════════════════════════
# ANÁLISIS DEL SERVICE
# ════════════════════════════════════════════════════════════

MÉTODOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ check_etl_status() - Verificar ejecución
✅ get_latest_processed_date() - Última fecha procesada
✅ get_etl_dashboard() - Dashboard completo
✅ get_failed_executions() - Alertas de fallos

NO tiene:
❌ extract() - ETL corre fuera de Django
❌ transform() - ETL corre fuera de Django
❌ load() - ETL corre fuera de Django
❌ run_etl() - ETL corre fuera de Django

TOTAL: 4 métodos (solo monitoring) ✅
```

---

<a name="views"></a>
## 5. VIEWS (DASHBOARD)

```python
# ════════════════════════════════════════════════════════════
# apps/pipeline/views.py
# ════════════════════════════════════════════════════════════

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.access.permissions import IsSuperuser
from apps.pipeline.services import ETLMonitoringService
from datetime import datetime


class ETLMonitoringViewSet(viewsets.ViewSet):
    """
    ViewSet para monitorear ETLs.
    
    Solo superusuarios pueden acceder.
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
                "records_processed": 5234
            },
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
        
        Response:
        {
            "executed": true,
            "status": "success",
            "records_processed": 5234,
            "last_run": "2025-08-18T02:15:30Z",
            "duration_seconds": 45.2
        }
        """
        etl_name = request.query_params.get('etl')
        fecha_str = request.query_params.get('fecha')
        
        if not etl_name or not fecha_str:
            return Response({
                "error": "Parámetros 'etl' y 'fecha' requeridos"
            }, status=400)
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                "error": "Formato de fecha inválido. Usar YYYY-MM-DD"
            }, status=400)
        
        status = ETLMonitoringService.check_etl_status(etl_name, fecha)
        return Response(status)
    
    @action(detail=False, methods=['get'])
    def failed_executions(self, request):
        """
        Listar ejecuciones fallidas recientes.
        
        GET /api/v1/pipeline/failed-executions/?days=7
        
        Response:
        [
            {
                "etl_name": "cmenu_diario",
                "fecha_procesada": "2025-08-15",
                "error_message": "Connection timeout",
                "started_at": "2025-08-16T02:00:00Z"
            },
            ...
        ]
        """
        days = int(request.query_params.get('days', 7))
        failed = ETLMonitoringService.get_failed_executions(days)
        return Response(failed)
```

---

<a name="tests"></a>
## 6. TESTS

### 6.1 Test Coverage

```python
# ════════════════════════════════════════════════════════════
# tests/unit/pipeline/test_etlexecution_model.py
# ════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestETLExecutionModel:
    def test_create_etlexecution(self):
        """Crear ETLExecution básico."""
        execution = ETLExecution.objects.create(
            etl_name='cmenu_diario',
            fecha_procesada=date(2025, 8, 17),
            status='success',
            records_processed=5234,
            started_at=datetime(2025, 8, 18, 2, 0),
            completed_at=datetime(2025, 8, 18, 2, 15)
        )
        
        assert execution.etl_name == 'cmenu_diario'
        assert execution.status == 'success'
    
    def test_duration_seconds_property(self):
        """Calcular duración de ejecución."""
        execution = ETLExecution.objects.create(
            etl_name='test',
            fecha_procesada=date.today(),
            started_at=datetime(2025, 8, 18, 2, 0, 0),
            completed_at=datetime(2025, 8, 18, 2, 0, 45)
        )
        
        assert execution.duration_seconds == 45.0


# ════════════════════════════════════════════════════════════
# tests/unit/pipeline/test_monitoring_service.py
# ════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestETLMonitoringService:
    def test_check_etl_status_executed(self, etlexecution_success):
        """Verificar ETL que corrió exitosamente."""
        status = ETLMonitoringService.check_etl_status(
            'cmenu_diario',
            date(2025, 8, 17)
        )
        
        assert status['executed'] is True
        assert status['status'] == 'success'
        assert status['records_processed'] > 0
    
    def test_check_etl_status_not_run(self):
        """Verificar ETL que no corrió."""
        status = ETLMonitoringService.check_etl_status(
            'cmenu_diario',
            date(2025, 12, 31)  # Fecha futura
        )
        
        assert status['executed'] is False
        assert status['status'] == 'not_run'
    
    def test_get_etl_dashboard(self, etlexecution_success):
        """Dashboard de todos los ETLs."""
        dashboard = ETLMonitoringService.get_etl_dashboard()
        
        assert 'cmenu_diario' in dashboard
        assert dashboard['cmenu_diario']['status'] == 'success'


TOTAL TESTS: ~10-15 tests
COVERAGE ESPERADO: >90%
```

---

<a name="flujo"></a>
## 7. FLUJO DE DATOS REAL

### 7.1 Flujo Completo

```
┌──────────────┐
│  IVR_LEGACY  │  MariaDB - call_logs (RAW)
└──────┬───────┘
       │
       │ 2:00 AM - ETL JOB ejecuta
       │ (Stored procedure o cron)
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ ETL JOB PROCESS (Fuera de Django)                       │
│                                                          │
│ 1. EXTRACT                                              │
│    SELECT * FROM ivr_legacy.call_logs                   │
│    WHERE DATE(call_timestamp) = YESTERDAY                │
│                                                          │
│ 2. TRANSFORM                                            │
│    - Limpiar datos                                      │
│    - Agregar (GROUP BY)                                 │
│    - Validar                                            │
│                                                          │
│ 3. LOAD                                                 │
│    INSERT INTO reporte_cmenu_agregado (...)            │
│                                                          │
│ 4. REGISTRO                                             │
│    INSERT INTO pipeline_etlexecution (                  │
│        etl_name='cmenu_diario',                        │
│        fecha_procesada='2025-08-17',                   │
│        status='success',                               │
│        records_processed=5234                          │
│    )                                                    │
└──────────────┬───────────────────────────────────────────┘
               │
               │ ETLExecution creado
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│ DEFAULT DB (Postgres/SQLite)                            │
│                                                          │
│ Tables:                                                  │
│ ├─ pipeline_etlexecution (tracking)                    │
│ ├─ reporte_cmenu_agregado (datos)                      │
│ └─ ...                                                  │
└──────────────┬───────────────────────────────────────────┘
               │
               │ Django query
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│ apps/pipeline/ (Django - MONITORING)                    │
│                                                          │
│ ETLMonitoringService.check_etl_status()                │
│   → Query pipeline_etlexecution                         │
│   → Return status info                                  │
│                                                          │
│ Dashboard:                                              │
│   ✅ cmenu_diario: success (5234 records)               │
│   ✅ llamadas_diarias: success (12450 records)          │
│   ❌ metricas_semanales: failed (timeout error)         │
└──────────────────────────────────────────────────────────┘
```

### 7.2 Uso desde REPORTS

```python
# ════════════════════════════════════════════════════════════
# apps/reports/views.py
# ════════════════════════════════════════════════════════════

@action(detail=False, methods=['post'])
def generate(self, request):
    """Generar reporte cMenu."""
    
    fecha = request.data.get('fecha')
    
    # VERIFICAR QUE ETL CORRIÓ ✅
    from apps.pipeline.services import ETLMonitoringService
    
    etl_status = ETLMonitoringService.check_etl_status(
        'cmenu_diario',
        fecha
    )
    
    if not etl_status['executed']:
        return Response({
            "error": "ETL no ha corrido para esta fecha",
            "fecha": fecha,
            "suggestion": "El ETL corre diariamente a las 2 AM"
        }, status=400)
    
    if etl_status['status'] != 'success':
        return Response({
            "error": "ETL falló para esta fecha",
            "etl_status": etl_status
        }, status=400)
    
    # ETL corrió OK → proceder con reporte
    # ...
```

---

<a name="comparacion"></a>
## 8. COMPARACIÓN v1 vs v2

### 8.1 Cambios Principales

```
COMPONENTE: ETLService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

v1.0.0 (INCORRECTO):
class ETLService:
    def extract():
        # Query IVR_LEGACY
    def transform():
        # Limpiar datos
    def load():
        # Guardar en CallRecord
    def run_etl():
        # Ejecutar pipeline completo

v2.0.0 (CORRECTO):
❌ ETLService NO EXISTE
✅ ETL corre fuera de Django
✅ Stored procedure en DB
✅ O script Python externo


COMPONENTE: Scheduling
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

v1.0.0 (INCORRECTO):
class ETLScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_etl, trigger='interval', hours=12)

v2.0.0 (CORRECTO):
❌ ETLScheduler NO EXISTE
✅ Cron job en servidor DB
✅ MySQL Event o pg_cron
✅ Schedule: 2:00 AM diario


COMPONENTE: Monitoring
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

v1.0.0 (INCORRECTO):
No existía concepto de monitoring

v2.0.0 (CORRECTO):
✅ ETLMonitoringService
✅ check_etl_status()
✅ get_etl_dashboard()
✅ Dashboard API


COMPONENTE: Modelos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

v1.0.0 (INCORRECTO):
class CallRecord(models.Model):
    # Analytics data
    # En apps/core/

class ETLExecution(models.Model):
    # Tracking

v2.0.0 (CORRECTO):
❌ CallRecord NO EXISTE
✅ Solo ETLExecution (tracking)
✅ Datos van directo a CMenuAgregado (apps/reports/)
```

### 8.2 Tabla Comparativa

```
┌─────────────────────────┬──────────────────┬──────────────────┐
│ Aspecto                 │ v1.0.0 ❌        │ v2.0.0 ✅        │
├─────────────────────────┼──────────────────┼──────────────────┤
│ ¿Quién ejecuta ETL?     │ Django/Python    │ DB JOB/Cron      │
│ ETLService existe?      │ Sí               │ No               │
│ Scheduling              │ APScheduler      │ DB cron/event    │
│ Frecuencia              │ 12 horas         │ 2 AM diario      │
│ Pipeline responsable de │ Ejecución        │ Monitoring       │
│ CallRecord existe?      │ Sí (apps/core/)  │ No               │
│ Datos van a             │ CallRecord       │ CMenuAgregado    │
│ Database                │ analytics_db     │ default DB       │
│ managed                 │ True/False       │ True             │
│ Propósito apps/pipeline │ ETL execution    │ ETL monitoring   │
└─────────────────────────┴──────────────────┴──────────────────┘
```

---

## RESUMEN Y CONCLUSIONES

```
CORRECCIONES APLICADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ETL es JOB en DB (NO Python)
✅ Pipeline solo MONITOREA (NO ejecuta)
✅ ETLExecution solo tracking
✅ ETLMonitoringService para verificar estado
✅ Dashboard de estado de ETLs
✅ CallRecord NO existe
✅ Datos en default DB (managed=True)

PROPÓSITO REAL apps/pipeline/:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Monitorear que ETL corrió
- Dashboard de estado
- Tracking de ejecuciones
- Alertas si falla

NO:
- Ejecutar ETL
- Procesar datos
- Scheduling

TODO CORRECTO ✅
```

---

**FIN DEL ANÁLISIS - PIPELINE v2.0.0**

Documento creado: 2026-01-17  
Versión: 2.0.0 - CORREGIDA  
Reemplaza: v1.0.0 (supuestos incorrectos)  
Basado en: FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md  
Estado: Definitivo
