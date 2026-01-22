---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Pipeline PARTE 2/4
categoria: arquitectura/apps
tema: apps/pipeline/ - Services y APScheduler Integration
autor: Claude Technical Analysis
tags: [pipeline, services, apscheduler, etl, monitoring]
estado: definitivo
parte: 2 de 4
relacionado:
  - ANALISIS_APP_PIPELINE_v3_0_0_PARTE_1.md
  - ANALISIS_APP_PIPELINE_v3_0_0_PARTE_3.md
  - ANALISIS_APP_PIPELINE_v3_0_0_PARTE_4.md
replaces: []
---

# ANÁLISIS DE apps/pipeline/ v3.0.0 - PARTE 2/4
## SERVICES Y APSCHEDULER INTEGRATION

---

## 1. SERVICES

### 1.1 JobExecutionService

```python
"""
Services para apps/pipeline/.

CLEAN_CODE v3.0.1 PARTE 2, Sección 20: Service Layer Pattern.
CNST-013: APScheduler (NO Celery).
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction

from apps.pipeline.models import JobExecution, JobLog, ScheduledJob
from apps.pipeline.exceptions import JobAlreadyRunningError, JobExecutionError


class JobExecutionService:
    """
    Service para gestión de ejecuciones de jobs.
    
    Responsabilidades:
    - Crear ejecuciones
    - Actualizar estado
    - Registrar logs
    - Validar ejecuciones concurrentes
    """
    
    @staticmethod
    @transaction.atomic
    def create_execution(
        job_type: str,
        triggered_by=None,
        metadata: dict = None
    ) -> JobExecution:
        """
        Crea una nueva ejecución de job.
        
        Args:
            job_type: Tipo de job (JOB_TYPE_*)
            triggered_by: Usuario que disparó (None si automático)
            metadata: Metadata adicional (dict)
        
        Returns:
            JobExecution creado
        
        Raises:
            JobAlreadyRunningError: Si ya hay ejecución corriendo
        """
        # Validar que no haya ejecución corriendo
        running = JobExecution.objects.filter(
            job_type=job_type,
            execution_status=JobExecution.STATUS_RUNNING
        ).exists()
        
        if running:
            raise JobAlreadyRunningError(
                f"Job {job_type} already running"
            )
        
        # Crear ejecución
        execution = JobExecution.objects.create(
            job_type=job_type,
            triggered_by=triggered_by,
            metadata=metadata or {}
        )
        
        # Log inicial
        JobExecutionService.log_execution(
            execution,
            'info',
            f'Job {job_type} created'
        )
        
        return execution
    
    @staticmethod
    def start_execution(execution: JobExecution):
        """
        Marca ejecución como running.
        
        Args:
            execution: JobExecution a iniciar
        """
        execution.mark_as_running()
        
        JobExecutionService.log_execution(
            execution,
            'info',
            f'Job {execution.job_type} started'
        )
    
    @staticmethod
    @transaction.atomic
    def complete_execution_success(
        execution: JobExecution,
        records_processed: int = 0,
        metadata: dict = None
    ):
        """
        Marca ejecución como exitosa.
        
        Args:
            execution: JobExecution a completar
            records_processed: Número de registros procesados
            metadata: Metadata adicional
        """
        execution.mark_as_success(records_processed)
        
        # Actualizar metadata si se proporcionó
        if metadata:
            execution.metadata.update(metadata)
            execution.save(update_fields=['metadata'])
        
        JobExecutionService.log_execution(
            execution,
            'info',
            f'Job {execution.job_type} completed successfully. '
            f'Records processed: {records_processed}'
        )
    
    @staticmethod
    @transaction.atomic
    def complete_execution_failed(
        execution: JobExecution,
        error_message: str,
        records_processed: int = 0
    ):
        """
        Marca ejecución como fallida.
        
        Args:
            execution: JobExecution a marcar
            error_message: Mensaje de error
            records_processed: Registros procesados antes del fallo
        """
        execution.records_processed = records_processed
        execution.mark_as_failed(error_message)
        
        JobExecutionService.log_execution(
            execution,
            'error',
            f'Job {execution.job_type} failed: {error_message}'
        )
        
        # Enviar alerta
        JobExecutionService._send_failure_alert(execution)
    
    @staticmethod
    def log_execution(
        execution: JobExecution,
        level: str,
        message: str
    ):
        """
        Registra log de ejecución.
        
        Args:
            execution: JobExecution
            level: Nivel (info, warning, error)
            message: Mensaje
        """
        JobLog.objects.create(
            execution=execution,
            log_level=level,
            message=message
        )
    
    @staticmethod
    def get_execution_history(
        job_type: str = None,
        days: int = 30
    ) -> List[JobExecution]:
        """
        Obtiene historial de ejecuciones.
        
        Args:
            job_type: Tipo de job (opcional)
            days: Días hacia atrás
        
        Returns:
            List[JobExecution]
        """
        cutoff = timezone.now() - timedelta(days=days)
        
        qs = JobExecution.objects.filter(started_at__gte=cutoff)
        
        if job_type:
            qs = qs.filter(job_type=job_type)
        
        return list(qs.order_by('-started_at'))
    
    @staticmethod
    def _send_failure_alert(execution: JobExecution):
        """Envía alerta por fallo de job."""
        from apps.alerts.services import AlertService
        
        AlertService.create_alert(
            alert_type='job_failed',
            severity='high',
            title=f'Job Failed: {execution.get_job_type_display()}',
            message=execution.error_message,
            related_object=execution
        )


class PipelineMonitorService:
    """
    Service para monitoreo del pipeline.
    
    Responsabilidades:
    - Estado global del pipeline
    - Métricas de ejecuciones
    - Detección de problemas
    """
    
    @staticmethod
    def get_pipeline_status() -> Dict:
        """
        Obtiene estado global del pipeline.
        
        Returns:
            Dict con:
            - last_execution: Última ejecución ETL
            - is_healthy: Boolean
            - next_scheduled: Próxima ejecución programada
            - pending_executions: Ejecuciones pendientes
        """
        # Última ejecución ETL
        last_etl = JobExecution.objects.filter(
            job_type=JobExecution.JOB_TYPE_ETL_DAILY
        ).order_by('-started_at').first()
        
        # Próxima ejecución programada
        scheduled_job = ScheduledJob.objects.filter(
            job_type=JobExecution.JOB_TYPE_ETL_DAILY,
            is_active=True
        ).first()
        
        # Health check
        is_healthy = PipelineMonitorService._check_pipeline_health()
        
        return {
            'last_execution': {
                'status': last_etl.execution_status if last_etl else None,
                'started_at': last_etl.started_at if last_etl else None,
                'finished_at': last_etl.finished_at if last_etl else None,
                'records_processed': last_etl.records_processed if last_etl else 0,
            },
            'is_healthy': is_healthy,
            'next_scheduled': scheduled_job.schedule if scheduled_job else None,
            'pending_executions': JobExecution.objects.filter(
                execution_status=JobExecution.STATUS_PENDING
            ).count()
        }
    
    @staticmethod
    def get_execution_metrics(days: int = 30) -> Dict:
        """
        Calcula métricas de ejecuciones.
        
        Args:
            days: Período en días
        
        Returns:
            Dict con métricas
        """
        from django.db.models import Count, Avg
        
        cutoff = timezone.now() - timedelta(days=days)
        
        executions = JobExecution.objects.filter(
            started_at__gte=cutoff,
            job_type=JobExecution.JOB_TYPE_ETL_DAILY
        )
        
        # Métricas
        total = executions.count()
        success = executions.filter(
            execution_status=JobExecution.STATUS_SUCCESS
        ).count()
        failed = executions.filter(
            execution_status=JobExecution.STATUS_FAILED
        ).count()
        
        # Duración promedio (solo completados)
        completed = executions.filter(
            execution_status__in=[
                JobExecution.STATUS_SUCCESS,
                JobExecution.STATUS_FAILED
            ]
        ).exclude(finished_at__isnull=True)
        
        durations = [e.duration_seconds for e in completed if e.duration_seconds]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'total_executions': total,
            'successful_executions': success,
            'failed_executions': failed,
            'success_rate': round((success / total * 100), 2) if total > 0 else 0,
            'average_duration_seconds': round(avg_duration, 2),
            'period_days': days
        }
    
    @staticmethod
    def _check_pipeline_health() -> bool:
        """
        Verifica salud del pipeline.
        
        Returns:
            bool: True si saludable
        """
        # Última ejecución debe ser < 24h
        last_execution = JobExecution.objects.filter(
            job_type=JobExecution.JOB_TYPE_ETL_DAILY
        ).order_by('-started_at').first()
        
        if not last_execution:
            return False
        
        # No debe haber pasado más de 24h
        hours_since = (timezone.now() - last_execution.started_at).total_seconds() / 3600
        
        if hours_since > 24:
            return False
        
        # Última ejecución debe ser exitosa
        if last_execution.execution_status != JobExecution.STATUS_SUCCESS:
            return False
        
        return True


class HealthCheckService:
    """
    Service para health checks del sistema.
    
    Responsabilidades:
    - Verificar conectividad DB
    - Verificar espacio en disco
    - Verificar estado ETL
    """
    
    @staticmethod
    def run_health_check() -> Dict:
        """
        Ejecuta health check completo.
        
        Returns:
            Dict con resultados de checks
        """
        results = {}
        
        # Check BD IVR (MariaDB)
        results['database_ivr'] = HealthCheckService._check_database_ivr()
        
        # Check BD Analytics (PostgreSQL)
        results['database_analytics'] = HealthCheckService._check_database_analytics()
        
        # Check ETL status
        results['etl_status'] = HealthCheckService._check_etl_status()
        
        # Check espacio disco
        results['disk_space'] = HealthCheckService._check_disk_space()
        
        # Estado general
        results['overall_status'] = all([
            results['database_ivr']['healthy'],
            results['database_analytics']['healthy'],
            results['etl_status']['healthy']
        ])
        
        return results
    
    @staticmethod
    def _check_database_ivr() -> Dict:
        """Verifica conectividad a BD IVR."""
        try:
            from django.db import connections
            
            with connections['ivr_legacy'].cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            
            return {
                'healthy': True,
                'message': 'IVR database connection OK'
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'IVR database error: {str(e)}'
            }
    
    @staticmethod
    def _check_database_analytics() -> Dict:
        """Verifica conectividad a BD Analytics."""
        try:
            from django.db import connections
            
            with connections['default'].cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            
            return {
                'healthy': True,
                'message': 'Analytics database connection OK'
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Analytics database error: {str(e)}'
            }
    
    @staticmethod
    def _check_etl_status() -> Dict:
        """Verifica estado del ETL."""
        last_execution = JobExecution.objects.filter(
            job_type=JobExecution.JOB_TYPE_ETL_DAILY
        ).order_by('-started_at').first()
        
        if not last_execution:
            return {
                'healthy': False,
                'message': 'No ETL executions found'
            }
        
        # Verificar que no haya pasado más de 24h
        hours_since = (timezone.now() - last_execution.started_at).total_seconds() / 3600
        
        if hours_since > 24:
            return {
                'healthy': False,
                'message': f'Last ETL execution was {hours_since:.1f} hours ago'
            }
        
        if last_execution.execution_status != JobExecution.STATUS_SUCCESS:
            return {
                'healthy': False,
                'message': f'Last ETL execution failed: {last_execution.error_message}'
            }
        
        return {
            'healthy': True,
            'message': f'Last ETL execution: {last_execution.started_at}'
        }
    
    @staticmethod
    def _check_disk_space() -> Dict:
        """Verifica espacio en disco."""
        import shutil
        
        try:
            stat = shutil.disk_usage('/')
            
            # Convertir a GB
            total_gb = stat.total / (1024**3)
            used_gb = stat.used / (1024**3)
            free_gb = stat.free / (1024**3)
            percent_used = (stat.used / stat.total) * 100
            
            # Alerta si > 80% usado
            healthy = percent_used < 80
            
            return {
                'healthy': healthy,
                'total_gb': round(total_gb, 2),
                'used_gb': round(used_gb, 2),
                'free_gb': round(free_gb, 2),
                'percent_used': round(percent_used, 2)
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Disk check error: {str(e)}'
            }


class ETLTriggerService:
    """
    Service para trigger manual del ETL.
    
    Responsabilidades:
    - Ejecutar ETL manualmente
    - Validar condiciones
    - Auditoría
    """
    
    @staticmethod
    @transaction.atomic
    def trigger_etl_manual(triggered_by) -> JobExecution:
        """
        Dispara ETL manualmente.
        
        Args:
            triggered_by: Usuario que dispara
        
        Returns:
            JobExecution creado
        
        Raises:
            JobAlreadyRunningError: Si ETL ya está corriendo
        """
        # Crear ejecución
        execution = JobExecutionService.create_execution(
            job_type=JobExecution.JOB_TYPE_ETL_MANUAL,
            triggered_by=triggered_by,
            metadata={'manual_trigger': True}
        )
        
        # Log en auditoría
        from apps.audit.services import AuditService
        AuditService.log_action(
            action='ETL_MANUAL_TRIGGER',
            user=triggered_by,
            details={
                'execution_id': execution.execution_id
            }
        )
        
        return execution
```

---

## 2. APSCHEDULER INTEGRATION

### 2.1 Archivo: apps/pipeline/scheduler.py

```python
"""
APScheduler configuration para apps/pipeline/.

CNST-013: APScheduler (NO Celery).
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
import logging

from apps.pipeline.jobs import (
    run_etl_daily,
    run_health_check,
    cleanup_old_executions
)

logger = logging.getLogger(__name__)

# Scheduler instance
scheduler = BackgroundScheduler()


def start_scheduler():
    """
    Inicia APScheduler.
    
    CNST-013: APScheduler (NO Celery).
    
    Jobs configurados:
    - ETL Daily: 6:00 AM diario
    - Health Check: cada 5 minutos
    - Cleanup: 3:00 AM domingos
    """
    if not settings.DEBUG:
        # Job 1: ETL Diario
        scheduler.add_job(
            func=run_etl_daily,
            trigger=CronTrigger(hour=6, minute=0),
            id='etl_daily',
            name='ETL Daily Execution',
            replace_existing=True,
            max_instances=1
        )
        logger.info("[APScheduler] ETL Daily job scheduled (6:00 AM)")
        
        # Job 2: Health Check
        scheduler.add_job(
            func=run_health_check,
            trigger=IntervalTrigger(minutes=5),
            id='health_check',
            name='Health Check',
            replace_existing=True,
            max_instances=1
        )
        logger.info("[APScheduler] Health Check job scheduled (every 5 min)")
        
        # Job 3: Cleanup
        scheduler.add_job(
            func=cleanup_old_executions,
            trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
            id='cleanup',
            name='Cleanup Old Executions',
            replace_existing=True,
            max_instances=1
        )
        logger.info("[APScheduler] Cleanup job scheduled (Sundays 3:00 AM)")
        
        # Iniciar scheduler
        scheduler.start()
        logger.info("[APScheduler] Scheduler started successfully")
    else:
        logger.info("[APScheduler] Skipped in DEBUG mode")


def stop_scheduler():
    """Para el scheduler."""
    scheduler.shutdown()
    logger.info("[APScheduler] Scheduler stopped")
```

### 2.2 Archivo: apps/pipeline/jobs.py

```python
"""
Job definitions para APScheduler.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

import logging
from django.db import connection

from apps.pipeline.services import (
    JobExecutionService,
    HealthCheckService
)
from apps.pipeline.models import JobExecution

logger = logging.getLogger(__name__)


def run_etl_daily():
    """
    Job para ejecutar ETL diario.
    
    CNST-013: Ejecutado por APScheduler (NO Celery).
    
    Proceso:
    1. Crear JobExecution
    2. Ejecutar sp_etl_daily en MariaDB
    3. Actualizar JobExecution con resultado
    """
    logger.info("[ETL Daily] Starting ETL execution")
    
    # Crear ejecución
    try:
        execution = JobExecutionService.create_execution(
            job_type=JobExecution.JOB_TYPE_ETL_DAILY,
            triggered_by=None  # Automático
        )
    except Exception as e:
        logger.error(f"[ETL Daily] Error creating execution: {e}")
        return
    
    # Marcar como running
    JobExecutionService.start_execution(execution)
    
    try:
        # Ejecutar SP en MariaDB
        records_processed = _execute_etl_stored_procedure()
        
        # Marcar como exitoso
        JobExecutionService.complete_execution_success(
            execution,
            records_processed=records_processed
        )
        
        logger.info(
            f"[ETL Daily] Completed successfully. "
            f"Records processed: {records_processed}"
        )
    
    except Exception as e:
        # Marcar como fallido
        JobExecutionService.complete_execution_failed(
            execution,
            error_message=str(e)
        )
        
        logger.error(f"[ETL Daily] Failed: {e}")


def _execute_etl_stored_procedure():
    """
    Ejecuta stored procedure sp_etl_daily en MariaDB.
    
    Returns:
        int: Número de registros procesados
    """
    from django.db import connections
    
    with connections['ivr_legacy'].cursor() as cursor:
        # Ejecutar SP
        cursor.execute('CALL sp_etl_daily()')
        
        # Obtener resultado (asumiendo que SP retorna conteo)
        result = cursor.fetchone()
        records_processed = result[0] if result else 0
    
    return records_processed


def run_health_check():
    """
    Job para health check del sistema.
    
    Ejecuta cada 5 minutos.
    """
    logger.debug("[Health Check] Running health check")
    
    # Crear ejecución
    execution = JobExecutionService.create_execution(
        job_type=JobExecution.JOB_TYPE_HEALTH_CHECK
    )
    
    JobExecutionService.start_execution(execution)
    
    try:
        # Ejecutar health check
        results = HealthCheckService.run_health_check()
        
        # Completar
        JobExecutionService.complete_execution_success(
            execution,
            metadata={'health_check_results': results}
        )
        
        if not results['overall_status']:
            logger.warning(f"[Health Check] System unhealthy: {results}")
    
    except Exception as e:
        JobExecutionService.complete_execution_failed(
            execution,
            error_message=str(e)
        )
        logger.error(f"[Health Check] Failed: {e}")


def cleanup_old_executions():
    """
    Job para limpiar ejecuciones antiguas.
    
    CNST-031: Retención 2 años.
    Ejecuta domingos 3:00 AM.
    """
    from datetime import timedelta
    from django.utils import timezone
    from apps.pipeline.constants import EXECUTION_RETENTION_DAYS
    
    logger.info("[Cleanup] Starting cleanup of old executions")
    
    cutoff = timezone.now() - timedelta(days=EXECUTION_RETENTION_DAYS)
    
    # Eliminar ejecuciones antiguas
    deleted, _ = JobExecution.objects.filter(
        started_at__lt=cutoff
    ).delete()
    
    logger.info(f"[Cleanup] Deleted {deleted} old executions")
```

---

## 3. RESUMEN PARTE 2

```yaml
Services (4):
  ✅ JobExecutionService (~350 líneas)
     - Crear/completar ejecuciones
     - Logs detallados
     - Alertas por fallos
  
  ✅ PipelineMonitorService (~200 líneas)
     - Estado global pipeline
     - Métricas de ejecuciones
     - Health check
  
  ✅ HealthCheckService (~200 líneas)
     - Check BD IVR/Analytics
     - Check ETL status
     - Check espacio disco
  
  ✅ ETLTriggerService (~80 líneas)
     - Trigger manual ETL
     - Validaciones
     - Auditoría

APScheduler:
  ✅ scheduler.py (~80 líneas)
     - BackgroundScheduler configurado
     - 3 jobs programados
  
  ✅ jobs.py (~150 líneas)
     - run_etl_daily()
     - run_health_check()
     - cleanup_old_executions()

CNST-013 Aplicada:
  ✅ APScheduler (NO Celery)
  ✅ BackgroundScheduler
  ✅ Jobs programados

Total: ~1,060 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 3/4: API REST y Dashboard Integration**

Contenido:
- ✅ Serializers DRF (5 serializers)
- ✅ ViewSets REST (3 viewsets)
- ✅ URLs configuration
- ✅ Endpoints (12 endpoints)

**Estimado:** ~900 líneas

---

**Fin de PARTE 2/4**
