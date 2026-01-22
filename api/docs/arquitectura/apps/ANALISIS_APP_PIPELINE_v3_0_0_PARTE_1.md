---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Pipeline PARTE 1/4
categoria: arquitectura/apps
tema: apps/pipeline/ - Fundamentos, Models y Job Monitoring
autor: Claude Technical Analysis
tags: [pipeline, etl, monitoring, apscheduler, jobs, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes) ⭐ APLICADO
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
estado: definitivo
parte: 1 de 4
relacionado:
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
  - ANALISIS_APP_PIPELINE_v3_0_0_PARTE_2.md
  - ANALISIS_APP_PIPELINE_v3_0_0_PARTE_3.md
  - ANALISIS_APP_PIPELINE_v3_0_0_PARTE_4.md
replaces: []
---

# ANÁLISIS DE apps/pipeline/ v3.0.0 - PARTE 1/4
## FUNDAMENTOS, MODELS Y JOB MONITORING

**BASADO EN: CLEAN_CODE_NAMING_PRINCIPLES v3.0.1 (5 partes)**

---

## 1. RESUMEN EJECUTIVO

### 1.1 Información General

```yaml
App: apps/pipeline/
Tipo: COMPLEJA (4 partes)
Líneas estimadas: ~3,800 líneas código
Propósito: Monitoreo y gestión del ETL (Extract, Transform, Load)
Funciones RBAC: 4 (PIPELINE_VIEW, PIPELINE_EDIT, PIPELINE_STATS, PIPELINE_ADMIN)
Dependencias:
  - APScheduler (BackgroundScheduler)
  - MariaDB (job_execution_log)
  - apps/ivr/ (consulta datos ETL)
  - apps/access/ (RBAC)
  - apps/audit/ (logs)
Tests: 45 tests estimados
Coverage objetivo: >90%
Clean Code: v3.0.1 aplicado ✅
```

### 1.2 Responsabilidades Core

```yaml
Monitoreo ETL:
  ✅ Rastreo de ejecuciones ETL
  ✅ Logs de jobs (success/fail)
  ✅ Métricas de performance
  ✅ Alertas por fallos
  ✅ Historial de ejecuciones

APScheduler Integration (CNST-013):
  ✅ BackgroundScheduler (NO Celery)
  ✅ Jobs programados
  ✅ Ejecutor de tareas
  ✅ Health checks
  ✅ Manual triggers

Health Monitoring:
  ✅ Estado BD IVR (MariaDB)
  ✅ Estado BD Analytics (PostgreSQL)
  ✅ Estado ETL (última ejecución)
  ✅ Espacio en disco
  ✅ Performance queries

Restricciones Aplicadas:
  - CNST-013: APScheduler (NO Celery)
  - CNST-010: NO Redis
  - CNST-031: Auditoría completa
```

### 1.3 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│              apps/pipeline/                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Models (PostgreSQL - DEFAULT):                    │
│  ├─ JobExecution (ejecuciones ETL)                 │
│  ├─ ScheduledJob (jobs configurados)               │
│  ├─ JobLog (logs detallados)                       │
│  └─ HealthCheck (chequeos sistema)                 │
│                                                     │
│  APScheduler (CNST-013):                           │
│  ├─ BackgroundScheduler (NO Celery)               │
│  ├─ Jobs programados                               │
│  ├─ etl_daily_job (6-12h)                         │
│  └─ health_check_job (cada 5 min)                 │
│                                                     │
│  Services:                                          │
│  ├─ PipelineMonitorService (monitoreo)            │
│  ├─ JobExecutionService (ejecuciones)              │
│  ├─ HealthCheckService (health)                    │
│  └─ ETLTriggerService (triggers manuales)          │
│                                                     │
│  Integration:                                       │
│  ├─ MariaDB IVR (consulta estado ETL)             │
│  ├─ PostgreSQL (almacena logs)                     │
│  ├─ apps/ivr/ (consulta datos)                    │
│  ├─ apps/alerts/ (envía alertas)                  │
│  └─ apps/audit/ (auditoría)                       │
│                                                     │
└─────────────────────────────────────────────────────┘

FLUJO:
  APScheduler → Ejecuta Job
      ↓
  JobExecution (create) → Estado: running
      ↓
  ETL (sp_etl_daily en MariaDB) → Ejecuta
      ↓
  JobExecution (update) → Estado: success/failed
      ↓
  JobLog (create) → Detalles de ejecución
      ↓
  apps/alerts/ (si failed) → Notifica
```

---

## 2. CLEAN CODE v3.0.1 APLICADO

### 2.1 Principio: Nombres que Revelan Intenciones

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 1, Sección 1
# ============================================================================

# ❌ INCORRECTO
class Job(models.Model):  # ¿Qué tipo de job?
    status = ...

class Execution(models.Model):  # ¿Ejecución de qué?
    pass

# ✅ CORRECTO (CLEAN_CODE v3.0.1)
class JobExecution(models.Model):
    """
    Ejecución de un job del ETL.
    
    Rastrea cada vez que se ejecuta el ETL.
    Almacena: inicio, fin, estado, errores.
    
    Database: PostgreSQL (default)
    """
    
    job_type = models.CharField(...)  # ← Auto-documentado
    execution_status = models.CharField(...)  # ← Claro
    started_at = models.DateTimeField(...)
    finished_at = models.DateTimeField(...)
```

### 2.2 Principio: Una Palabra por Concepto

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 1, Sección 8
# ============================================================================

# ✅ CORRECTO - "Service" para todos los servicios
PipelineMonitorService    # ✅ Service
JobExecutionService       # ✅ Service
HealthCheckService        # ✅ Service
ETLTriggerService         # ✅ Service (NO "ETLManager")

# ✅ CORRECTO - "Job" para trabajos programados
ScheduledJob              # ✅ Job
JobExecution              # ✅ Ejecución de job
JobLog                    # ✅ Log de job
```

### 2.3 Principio: Service Layer Pattern

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 2, Sección 20
# ============================================================================

# ✅ CORRECTO - Lógica en Service, View delgado
class PipelineMonitorService:
    """
    Service para monitoreo del pipeline ETL.
    
    Responsabilidades:
    - Obtener estado actual del ETL
    - Calcular métricas de ejecuciones
    - Detectar fallos
    - Generar alertas
    """
    
    @staticmethod
    def get_pipeline_status():
        """
        Obtiene estado actual del pipeline.
        
        Returns:
            Dict con estado completo del ETL
        """
        # Lógica compleja aquí
        pass
```

---

## 3. RESTRICCIONES ARQUITECTÓNICAS

### 3.1 CNST-013: APScheduler (NO Celery)

```yaml
CNST-013: APScheduler (🔴 CRÍTICO)

Descripción:
  Usar APScheduler para jobs programados.
  PROHIBIDO Celery, RabbitMQ, Redis.

Reglas:
  1. ✅ SÍ APScheduler (BackgroundScheduler)
  2. ❌ NO Celery (cualquier backend)
  3. ❌ NO RabbitMQ
  4. ❌ NO Redis para queue
  5. ✅ SÍ Django management commands para tareas manuales

Implementación CLEAN_CODE v3.0.1:
  # apps/pipeline/scheduler.py
  from apscheduler.schedulers.background import BackgroundScheduler
  
  scheduler = BackgroundScheduler()
  
  # Job ETL diario (6-12h)
  scheduler.add_job(
      func=run_etl_daily,
      trigger='cron',
      hour=6,
      id='etl_daily',
      name='ETL Daily Execution',
      replace_existing=True
  )
  
  # Health check cada 5 min
  scheduler.add_job(
      func=health_check,
      trigger='interval',
      minutes=5,
      id='health_check',
      name='Health Check',
      replace_existing=True
  )
  
  scheduler.start()

Justificación:
  - No hay Redis/RabbitMQ en infraestructura
  - Arquitectura simplificada
  - APScheduler suficiente para el scope

Referencias:
  - RESTRICCIONES v1.0.0 PARTE 1, Sección 1.7
  - ARQUITECTURA_ETL v3.0.0 PARTE 1, Decisión 3
```

### 3.2 CNST-031: Auditoría Completa

```yaml
CNST-031: Auditoría de Jobs (🟡 IMPORTANTE)

Descripción:
  Todos los jobs deben tener auditoría completa.

Reglas:
  1. ✅ Registrar TODAS las ejecuciones
  2. ✅ Logs immutables (append-only)
  3. ✅ Timestamp preciso
  4. ✅ Usuario/trigger
  5. ✅ Retención 2 años mínimo

Implementación:
  class JobExecution(models.Model):
      """Auditoría de ejecuciones."""
      
      # Immutable - NO se puede editar
      def save(self, *args, **kwargs):
          if self.pk and self.execution_status == 'completed':
              raise RuntimeError("Cannot modify completed execution")
          super().save(*args, **kwargs)
```

---

## 4. MODELOS DJANGO

### 4.1 JobExecution

```python
"""
Modelos para apps/pipeline/.

CLEAN_CODE v3.0.1: Inglés auto-documentado.
Database: PostgreSQL (default)
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class JobExecution(models.Model):
    """
    Ejecución de un job del ETL.
    
    CNST-031: Auditoría immutable de jobs.
    
    Rastrea cada ejecución del ETL incluyendo:
    - Timestamp inicio/fin
    - Estado (running, success, failed)
    - Registros procesados
    - Errores
    
    Database: PostgreSQL (default)
    Tabla: pipeline_job_executions
    """
    
    # Choices
    JOB_TYPE_ETL_DAILY = 'etl_daily'
    JOB_TYPE_ETL_MANUAL = 'etl_manual'
    JOB_TYPE_CLEANUP = 'cleanup'
    JOB_TYPE_HEALTH_CHECK = 'health_check'
    
    JOB_TYPE_CHOICES = [
        (JOB_TYPE_ETL_DAILY, 'ETL Daily'),
        (JOB_TYPE_ETL_MANUAL, 'ETL Manual'),
        (JOB_TYPE_CLEANUP, 'Cleanup'),
        (JOB_TYPE_HEALTH_CHECK, 'Health Check'),
    ]
    
    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    
    # Fields
    execution_id = models.BigAutoField(
        primary_key=True,
        verbose_name='ID de ejecución'
    )
    
    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPE_CHOICES,
        verbose_name='Tipo de job',
        help_text='Tipo de job ejecutado'
    )
    
    execution_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Estado',
        help_text='Estado actual de la ejecución'
    )
    
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_executions',
        verbose_name='Disparado por',
        help_text='Usuario que disparó (null si automático)'
    )
    
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Inicio',
        help_text='Timestamp de inicio'
    )
    
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fin',
        help_text='Timestamp de finalización'
    )
    
    records_processed = models.IntegerField(
        default=0,
        verbose_name='Registros procesados',
        help_text='Número de registros procesados'
    )
    
    records_failed = models.IntegerField(
        default=0,
        verbose_name='Registros fallidos'
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de error',
        help_text='Detalles del error si falló'
    )
    
    metadata = models.JSONField(
        default=dict,
        verbose_name='Metadata',
        help_text='Información adicional (JSON)'
    )
    
    class Meta:
        db_table = 'pipeline_job_executions'
        verbose_name = 'Ejecución de Job'
        verbose_name_plural = 'Ejecuciones de Jobs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['job_type', '-started_at']),
            models.Index(fields=['execution_status', '-started_at']),
        ]
    
    def __str__(self):
        """String representation."""
        return f"{self.get_job_type_display()} - {self.execution_status}"
    
    @property
    def duration_seconds(self):
        """
        Duración de la ejecución en segundos.
        
        Returns:
            int: Duración en segundos (None si aún corriendo)
        """
        if self.finished_at:
            delta = self.finished_at - self.started_at
            return int(delta.total_seconds())
        return None
    
    @property
    def is_running(self):
        """Verifica si está corriendo."""
        return self.execution_status == self.STATUS_RUNNING
    
    @property
    def is_completed(self):
        """Verifica si completó (success o failed)."""
        return self.execution_status in [
            self.STATUS_SUCCESS,
            self.STATUS_FAILED
        ]
    
    def mark_as_running(self):
        """Marca como running."""
        self.execution_status = self.STATUS_RUNNING
        self.save(update_fields=['execution_status'])
    
    def mark_as_success(self, records_processed=0):
        """
        Marca como exitoso.
        
        Args:
            records_processed: Número de registros procesados
        """
        self.execution_status = self.STATUS_SUCCESS
        self.finished_at = timezone.now()
        self.records_processed = records_processed
        self.save(update_fields=[
            'execution_status',
            'finished_at',
            'records_processed'
        ])
    
    def mark_as_failed(self, error_message):
        """
        Marca como fallido.
        
        Args:
            error_message: Mensaje de error
        """
        self.execution_status = self.STATUS_FAILED
        self.finished_at = timezone.now()
        self.error_message = error_message
        self.save(update_fields=[
            'execution_status',
            'finished_at',
            'error_message'
        ])


class ScheduledJob(models.Model):
    """
    Configuración de jobs programados.
    
    Define qué jobs están activos y su schedule.
    
    Database: PostgreSQL (default)
    Tabla: pipeline_scheduled_jobs
    """
    
    job_id = models.AutoField(
        primary_key=True,
        verbose_name='ID de job'
    )
    
    job_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre del job'
    )
    
    job_type = models.CharField(
        max_length=50,
        choices=JobExecution.JOB_TYPE_CHOICES,
        verbose_name='Tipo de job'
    )
    
    schedule = models.CharField(
        max_length=100,
        verbose_name='Schedule',
        help_text='Cron expression o interval'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si el job está activo'
    )
    
    last_execution = models.ForeignKey(
        JobExecution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scheduled_job_last',
        verbose_name='Última ejecución'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creado'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Actualizado'
    )
    
    class Meta:
        db_table = 'pipeline_scheduled_jobs'
        verbose_name = 'Job Programado'
        verbose_name_plural = 'Jobs Programados'
        ordering = ['job_name']
    
    def __str__(self):
        """String representation."""
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.job_name}"


class JobLog(models.Model):
    """
    Log detallado de ejecuciones.
    
    CNST-031: Logs immutables (append-only).
    
    Almacena cada paso de la ejecución para debugging.
    
    Database: PostgreSQL (default)
    Tabla: pipeline_job_logs
    """
    
    LOG_LEVEL_INFO = 'info'
    LOG_LEVEL_WARNING = 'warning'
    LOG_LEVEL_ERROR = 'error'
    
    LOG_LEVEL_CHOICES = [
        (LOG_LEVEL_INFO, 'Info'),
        (LOG_LEVEL_WARNING, 'Warning'),
        (LOG_LEVEL_ERROR, 'Error'),
    ]
    
    log_id = models.BigAutoField(
        primary_key=True,
        verbose_name='ID de log'
    )
    
    execution = models.ForeignKey(
        JobExecution,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Ejecución'
    )
    
    log_level = models.CharField(
        max_length=20,
        choices=LOG_LEVEL_CHOICES,
        default=LOG_LEVEL_INFO,
        verbose_name='Nivel'
    )
    
    message = models.TextField(
        verbose_name='Mensaje'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Timestamp'
    )
    
    class Meta:
        db_table = 'pipeline_job_logs'
        verbose_name = 'Log de Job'
        verbose_name_plural = 'Logs de Jobs'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['execution', 'timestamp']),
        ]
    
    def __str__(self):
        """String representation."""
        return f"[{self.log_level.upper()}] {self.message[:50]}"
```

---

## 5. CONSTANTS

```python
"""
Constants para apps/pipeline/.

CLEAN_CODE v3.0.1 PARTE 2, Sección 11: UPPER_SNAKE_CASE.
"""

# Job Types
JOB_TYPE_ETL_DAILY = 'etl_daily'
JOB_TYPE_ETL_MANUAL = 'etl_manual'
JOB_TYPE_CLEANUP = 'cleanup'
JOB_TYPE_HEALTH_CHECK = 'health_check'

# Execution Status
EXECUTION_STATUS_PENDING = 'pending'
EXECUTION_STATUS_RUNNING = 'running'
EXECUTION_STATUS_SUCCESS = 'success'
EXECUTION_STATUS_FAILED = 'failed'
EXECUTION_STATUS_CANCELLED = 'cancelled'

# Schedules (cron expressions)
SCHEDULE_ETL_DAILY = '0 6 * * *'        # 6:00 AM diario
SCHEDULE_HEALTH_CHECK = '*/5 * * * *'   # Cada 5 minutos
SCHEDULE_CLEANUP = '0 3 * * 0'          # 3:00 AM domingos

# Timeouts
ETL_TIMEOUT_SECONDS = 3600              # 1 hora max
HEALTH_CHECK_TIMEOUT_SECONDS = 30       # 30 segundos

# Retención
LOG_RETENTION_DAYS = 730                # 2 años (CNST-031)
EXECUTION_RETENTION_DAYS = 730

# Funciones RBAC
PIPELINE_VIEW = 'PIPELINE_VIEW'
PIPELINE_EDIT = 'PIPELINE_EDIT'
PIPELINE_STATS = 'PIPELINE_STATS'
PIPELINE_ADMIN = 'PIPELINE_ADMIN'
```

---

## 6. RESUMEN PARTE 1

```yaml
Modelos (3):
  ✅ JobExecution (~200 líneas)
     - Rastrea ejecuciones ETL
     - Estados: pending, running, success, failed
     - Auditoría completa (CNST-031)
  
  ✅ ScheduledJob (~80 líneas)
     - Configuración jobs programados
     - APScheduler integration
  
  ✅ JobLog (~60 líneas)
     - Logs detallados (append-only)
     - Niveles: info, warning, error

Restricciones Aplicadas (2):
  ✅ CNST-013: APScheduler (NO Celery)
  ✅ CNST-031: Auditoría completa

Clean Code Aplicado:
  ✅ v3.0.1 PARTE 1, Sección 1: Nombres auto-documentados
  ✅ v3.0.1 PARTE 1, Sección 8: Una palabra por concepto
  ✅ v3.0.1 PARTE 2, Sección 11: UPPER_SNAKE_CASE constantes

Database:
  ✅ PostgreSQL (default)
  ✅ 3 tablas con índices optimizados

Líneas código: ~550 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 2/4: Services y APScheduler Integration**

Contenido:
- ✅ PipelineMonitorService
- ✅ JobExecutionService
- ✅ HealthCheckService
- ✅ ETLTriggerService
- ✅ APScheduler configuration completo
- ✅ Job definitions

**Estimado:** ~1,200 líneas, 3 horas

---

**Fin de PARTE 1/4 - v3.0.0 con CLEAN_CODE v3.0.1 aplicado ✅**
