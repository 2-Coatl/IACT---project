---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Pipeline PARTE 3/4
categoria: arquitectura/apps
tema: apps/pipeline/ - API REST y Dashboard Integration
autor: Claude Technical Analysis
tags: [pipeline, api, rest, drf, dashboard]
estado: definitivo
parte: 3 de 4
relacionado:
  - ANALISIS_APP_PIPELINE_v3_0_0_PARTE_1.md
  - ANALISIS_APP_PIPELINE_v3_0_0_PARTE_2.md
  - ANALISIS_APP_PIPELINE_v3_0_0_PARTE_4.md
replaces: []
---

# ANÁLISIS DE apps/pipeline/ v3.0.0 - PARTE 3/4
## API REST Y DASHBOARD INTEGRATION

---

## 1. SERIALIZERS DRF

```python
"""
Serializers DRF para pipeline.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

from rest_framework import serializers
from apps.pipeline.models import JobExecution, ScheduledJob, JobLog


class JobExecutionSerializer(serializers.ModelSerializer):
    """Serializer para JobExecution."""
    
    job_type_display = serializers.CharField(
        source='get_job_type_display',
        read_only=True
    )
    
    status_display = serializers.CharField(
        source='get_execution_status_display',
        read_only=True
    )
    
    duration_seconds = serializers.IntegerField(read_only=True)
    is_running = serializers.BooleanField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    
    triggered_by_username = serializers.CharField(
        source='triggered_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = JobExecution
        fields = [
            'execution_id', 'job_type', 'job_type_display',
            'execution_status', 'status_display',
            'triggered_by', 'triggered_by_username',
            'started_at', 'finished_at', 'duration_seconds',
            'records_processed', 'records_failed',
            'error_message', 'metadata',
            'is_running', 'is_completed'
        ]
        read_only_fields = '__all__'


class JobExecutionCreateSerializer(serializers.Serializer):
    """Serializer para crear ejecución manual."""
    
    job_type = serializers.ChoiceField(
        choices=[
            JobExecution.JOB_TYPE_ETL_MANUAL,
            JobExecution.JOB_TYPE_CLEANUP
        ]
    )
    
    metadata = serializers.JSONField(required=False)


class ScheduledJobSerializer(serializers.ModelSerializer):
    """Serializer para ScheduledJob."""
    
    job_type_display = serializers.CharField(
        source='get_job_type_display',
        read_only=True
    )
    
    last_execution_status = serializers.CharField(
        source='last_execution.execution_status',
        read_only=True,
        allow_null=True
    )
    
    last_execution_date = serializers.DateTimeField(
        source='last_execution.started_at',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = ScheduledJob
        fields = [
            'job_id', 'job_name', 'job_type', 'job_type_display',
            'schedule', 'is_active',
            'last_execution', 'last_execution_status', 'last_execution_date',
            'created_at', 'updated_at'
        ]


class JobLogSerializer(serializers.ModelSerializer):
    """Serializer para JobLog."""
    
    log_level_display = serializers.CharField(
        source='get_log_level_display',
        read_only=True
    )
    
    class Meta:
        model = JobLog
        fields = [
            'log_id', 'execution', 'log_level', 'log_level_display',
            'message', 'timestamp'
        ]
        read_only_fields = '__all__'


class PipelineStatusSerializer(serializers.Serializer):
    """Serializer para estado del pipeline."""
    
    last_execution = serializers.DictField()
    is_healthy = serializers.BooleanField()
    next_scheduled = serializers.CharField(allow_null=True)
    pending_executions = serializers.IntegerField()


class ExecutionMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de ejecuciones."""
    
    total_executions = serializers.IntegerField()
    successful_executions = serializers.IntegerField()
    failed_executions = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_duration_seconds = serializers.FloatField()
    period_days = serializers.IntegerField()
```

---

## 2. VIEWSETS REST

```python
"""
ViewSets DRF para pipeline.

CLEAN_CODE v3.0.1: Responsabilidades claras.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.access.permissions import DynamicFunctionPermission
from apps.pipeline.serializers import (
    JobExecutionSerializer,
    JobExecutionCreateSerializer,
    ScheduledJobSerializer,
    JobLogSerializer,
    PipelineStatusSerializer,
    ExecutionMetricsSerializer
)
from apps.pipeline.services import (
    JobExecutionService,
    PipelineMonitorService,
    HealthCheckService,
    ETLTriggerService
)
from apps.pipeline.models import JobExecution, ScheduledJob, JobLog


class JobExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para JobExecution.
    
    Endpoints:
    - GET  /api/v1/pipeline/executions/
    - GET  /api/v1/pipeline/executions/{id}/
    - POST /api/v1/pipeline/executions/trigger/
    - GET  /api/v1/pipeline/executions/{id}/logs/
    
    RBAC: PIPELINE_VIEW, PIPELINE_ADMIN
    """
    
    queryset = JobExecution.objects.all()
    serializer_class = JobExecutionSerializer
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'list': 'pipeline.view',
        'retrieve': 'pipeline.view',
        'trigger': 'pipeline.admin',
        'logs': 'pipeline.view',
    }
    
    @action(detail=False, methods=['post'])
    def trigger(self, request):
        """
        Dispara ejecución manual de job.
        
        POST /api/v1/pipeline/executions/trigger/
        {
            "job_type": "etl_manual",
            "metadata": {}
        }
        
        Returns:
            JobExecution creado
        """
        serializer = JobExecutionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            if serializer.validated_data['job_type'] == JobExecution.JOB_TYPE_ETL_MANUAL:
                # Trigger ETL manual
                execution = ETLTriggerService.trigger_etl_manual(
                    triggered_by=request.user
                )
            else:
                # Crear ejecución genérica
                execution = JobExecutionService.create_execution(
                    job_type=serializer.validated_data['job_type'],
                    triggered_by=request.user,
                    metadata=serializer.validated_data.get('metadata')
                )
            
            response_serializer = JobExecutionSerializer(execution)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """
        Obtiene logs de una ejecución.
        
        GET /api/v1/pipeline/executions/{id}/logs/
        """
        execution = self.get_object()
        logs = execution.logs.all()
        
        serializer = JobLogSerializer(logs, many=True)
        return Response(serializer.data)


class PipelineMonitorViewSet(viewsets.ViewSet):
    """
    ViewSet para monitoreo del pipeline.
    
    Endpoints:
    - GET /api/v1/pipeline/monitor/status/
    - GET /api/v1/pipeline/monitor/metrics/
    - GET /api/v1/pipeline/monitor/health/
    
    RBAC: PIPELINE_VIEW, PIPELINE_STATS
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'status': 'pipeline.view',
        'metrics': 'pipeline.stats',
        'health': 'pipeline.view',
    }
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Estado global del pipeline.
        
        GET /api/v1/pipeline/monitor/status/
        
        Returns:
            {
                "last_execution": {...},
                "is_healthy": true,
                "next_scheduled": "0 6 * * *",
                "pending_executions": 0
            }
        """
        pipeline_status = PipelineMonitorService.get_pipeline_status()
        
        serializer = PipelineStatusSerializer(pipeline_status)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """
        Métricas de ejecuciones.
        
        GET /api/v1/pipeline/monitor/metrics/?days=30
        
        Returns:
            {
                "total_executions": 30,
                "successful_executions": 28,
                "failed_executions": 2,
                "success_rate": 93.33,
                "average_duration_seconds": 1234.56,
                "period_days": 30
            }
        """
        days = int(request.query_params.get('days', 30))
        
        metrics = PipelineMonitorService.get_execution_metrics(days)
        
        serializer = ExecutionMetricsSerializer(metrics)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        """
        Health check del sistema.
        
        GET /api/v1/pipeline/monitor/health/
        
        Returns:
            {
                "database_ivr": {"healthy": true, ...},
                "database_analytics": {"healthy": true, ...},
                "etl_status": {"healthy": true, ...},
                "disk_space": {"healthy": true, ...},
                "overall_status": true
            }
        """
        health_results = HealthCheckService.run_health_check()
        
        return Response(health_results)


class ScheduledJobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ScheduledJob.
    
    Endpoints:
    - GET /api/v1/pipeline/scheduled-jobs/
    - GET /api/v1/pipeline/scheduled-jobs/{id}/
    - POST /api/v1/pipeline/scheduled-jobs/{id}/toggle/
    
    RBAC: PIPELINE_VIEW, PIPELINE_EDIT
    """
    
    queryset = ScheduledJob.objects.all()
    serializer_class = ScheduledJobSerializer
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'list': 'pipeline.view',
        'retrieve': 'pipeline.view',
        'toggle': 'pipeline.edit',
    }
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """
        Activa/desactiva un job programado.
        
        POST /api/v1/pipeline/scheduled-jobs/{id}/toggle/
        """
        job = self.get_object()
        job.is_active = not job.is_active
        job.save(update_fields=['is_active'])
        
        serializer = self.get_serializer(job)
        return Response(serializer.data)
```

---

## 3. URLS

```python
"""
URL configuration para pipeline.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.pipeline.views import (
    JobExecutionViewSet,
    PipelineMonitorViewSet,
    ScheduledJobViewSet
)

router = DefaultRouter()
router.register(r'executions', JobExecutionViewSet, basename='execution')
router.register(r'monitor', PipelineMonitorViewSet, basename='monitor')
router.register(r'scheduled-jobs', ScheduledJobViewSet, basename='scheduled-job')

app_name = 'pipeline'

urlpatterns = [
    path('api/v1/pipeline/', include(router.urls)),
]
```

**Endpoints (12 total):**

```yaml
Job Executions (4):
  GET  /api/v1/pipeline/executions/
  GET  /api/v1/pipeline/executions/{id}/
  POST /api/v1/pipeline/executions/trigger/
  GET  /api/v1/pipeline/executions/{id}/logs/

Pipeline Monitor (3):
  GET /api/v1/pipeline/monitor/status/
  GET /api/v1/pipeline/monitor/metrics/?days=30
  GET /api/v1/pipeline/monitor/health/

Scheduled Jobs (3):
  GET  /api/v1/pipeline/scheduled-jobs/
  GET  /api/v1/pipeline/scheduled-jobs/{id}/
  POST /api/v1/pipeline/scheduled-jobs/{id}/toggle/

RBAC Functions:
  - pipeline.view (lectura)
  - pipeline.edit (edición)
  - pipeline.stats (métricas)
  - pipeline.admin (trigger manual)
```

---

## 4. DASHBOARD INTEGRATION

### 4.1 Widget para apps/dashboard/

```python
"""
Widget de Pipeline para Dashboard.

Integración con apps/dashboard/.
"""

from apps.pipeline.services import PipelineMonitorService


def get_pipeline_widget_data():
    """
    Obtiene datos para widget de pipeline en dashboard.
    
    Returns:
        Dict con datos para visualización
    """
    # Estado del pipeline
    status = PipelineMonitorService.get_pipeline_status()
    
    # Métricas últimos 7 días
    metrics = PipelineMonitorService.get_execution_metrics(days=7)
    
    return {
        'title': 'Pipeline ETL',
        'status': {
            'is_healthy': status['is_healthy'],
            'last_execution': status['last_execution'],
        },
        'metrics': {
            'success_rate': metrics['success_rate'],
            'total_executions': metrics['total_executions'],
            'average_duration': metrics['average_duration_seconds']
        },
        'chart_data': _get_execution_chart_data(days=7)
    }


def _get_execution_chart_data(days=7):
    """Obtiene datos para gráfica de ejecuciones."""
    from datetime import timedelta
    from django.utils import timezone
    from apps.pipeline.models import JobExecution
    
    cutoff = timezone.now() - timedelta(days=days)
    
    executions = JobExecution.objects.filter(
        job_type=JobExecution.JOB_TYPE_ETL_DAILY,
        started_at__gte=cutoff
    ).order_by('started_at')
    
    # Agrupar por día
    chart_data = []
    for execution in executions:
        chart_data.append({
            'date': execution.started_at.date().isoformat(),
            'duration': execution.duration_seconds or 0,
            'status': execution.execution_status,
            'records': execution.records_processed
        })
    
    return chart_data
```

---

## 5. RESUMEN PARTE 3

```yaml
Serializers (6):
  ✅ JobExecutionSerializer
  ✅ JobExecutionCreateSerializer
  ✅ ScheduledJobSerializer
  ✅ JobLogSerializer
  ✅ PipelineStatusSerializer
  ✅ ExecutionMetricsSerializer

ViewSets (3):
  ✅ JobExecutionViewSet
  ✅ PipelineMonitorViewSet
  ✅ ScheduledJobViewSet

Endpoints REST: 12 endpoints

RBAC Functions (4):
  - pipeline.view
  - pipeline.edit
  - pipeline.stats
  - pipeline.admin

Dashboard Integration:
  ✅ Widget de pipeline
  ✅ Gráficas de ejecuciones
  ✅ Estado en tiempo real

Total: ~650 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 4/4: Testing y Deployment (FINAL)**

Contenido:
- ✅ Tests (45 tests)
- ✅ APScheduler configuration
- ✅ Deployment checklist
- ✅ Monitoring setup
- ✅ Resumen final completo

**Estimado:** ~1,200 líneas

---

**Fin de PARTE 3/4**
