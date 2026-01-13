"""Views para ETL."""

from __future__ import annotations

from django.db.models import Avg, Count, Q, Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ETLJob, ETLValidationError
from .serializers import (
    ETLJobSerializer,
    ETLStatsSerializer,
    ETLValidationErrorSerializer,
)
from .services import ETLService


class ETLJobViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para jobs ETL - solo lectura para monitoreo."""

    queryset = ETLJob.objects.all()
    serializer_class = ETLJobSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "job_name"]
    search_fields = ["job_name", "error_message"]
    ordering_fields = ["created_at", "started_at", "completed_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Obtener estadisticas de un job especifico."""
        job = self.get_object()
        stats = ETLService.obtener_estadisticas_job(job_id=job.id)
        return Response(stats)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Obtener resumen general de jobs."""
        total = ETLJob.objects.count()
        completed = ETLJob.objects.filter(status="completed").count()
        failed = ETLJob.objects.filter(status="failed").count()
        running = ETLJob.objects.filter(status="running").count()

        total_records = ETLJob.objects.filter(status="completed").aggregate(
            total=Sum("records_loaded")
        )["total"] or 0

        avg_time = ETLJob.objects.filter(
            status="completed", execution_time_seconds__isnull=False
        ).aggregate(avg=Avg("execution_time_seconds"))["avg"]

        data = {
            "total_jobs": total,
            "completed_jobs": completed,
            "failed_jobs": failed,
            "running_jobs": running,
            "total_records_processed": total_records,
            "average_execution_time": avg_time or 0,
        }

        serializer = ETLStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def recent_failures(self, request):
        """Listar jobs fallidos recientes."""
        failures = ETLJob.objects.filter(status="failed").order_by("-created_at")[:20]
        serializer = self.get_serializer(failures, many=True)
        return Response(serializer.data)


class ETLValidationErrorViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para errores de validacion ETL."""

    queryset = ETLValidationError.objects.all()
    serializer_class = ETLValidationErrorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["job", "error_type", "severity"]
    search_fields = ["error_message", "error_type"]
    ordering_fields = ["created_at", "severity"]
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"])
    def by_severity(self, request):
        """Agrupar errores por severidad."""
        errors_by_severity = (
            ETLValidationError.objects.values("severity")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        return Response(errors_by_severity)
