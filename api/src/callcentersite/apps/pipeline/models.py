"""Modelos para ETL y job execution."""

from __future__ import annotations

from django.db import models
from django.utils import timezone

from callcentersite.apps.common.models import TimeStampedModel


class ETLJob(TimeStampedModel):
    """Job ETL ejecutado."""

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("running", "En ejecucion"),
        ("completed", "Completado"),
        ("failed", "Fallido"),
        ("cancelled", "Cancelado"),
    ]

    job_name = models.CharField(max_length=200, help_text="Nombre del job")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", help_text="Estado"
    )
    started_at = models.DateTimeField(null=True, blank=True, help_text="Inicio")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Fin")
    records_extracted = models.IntegerField(
        default=0, help_text="Registros extraidos"
    )
    records_transformed = models.IntegerField(
        default=0, help_text="Registros transformados"
    )
    records_loaded = models.IntegerField(default=0, help_text="Registros cargados")
    records_failed = models.IntegerField(default=0, help_text="Registros fallidos")
    error_message = models.TextField(null=True, blank=True, help_text="Mensaje error")
    error_details = models.JSONField(
        default=dict, blank=True, help_text="Detalles del error"
    )
    execution_time_seconds = models.FloatField(
        null=True, blank=True, help_text="Tiempo de ejecucion en segundos"
    )
    metadata = models.JSONField(
        default=dict, blank=True, help_text="Metadata adicional"
    )

    class Meta:
        verbose_name = "ETL Job"
        verbose_name_plural = "ETL Jobs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["job_name", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.job_name} - {self.status}"

    def mark_as_running(self) -> None:
        """Marcar job como en ejecucion."""
        self.status = "running"
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at"])

    def mark_as_completed(
        self,
        extracted: int = 0,
        transformed: int = 0,
        loaded: int = 0,
        failed: int = 0,
    ) -> None:
        """Marcar job como completado."""
        self.status = "completed"
        self.completed_at = timezone.now()
        self.records_extracted = extracted
        self.records_transformed = transformed
        self.records_loaded = loaded
        self.records_failed = failed

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.execution_time_seconds = delta.total_seconds()

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "records_extracted",
                "records_transformed",
                "records_loaded",
                "records_failed",
                "execution_time_seconds",
            ]
        )

    def mark_as_failed(self, error_message: str, error_details: dict = None) -> None:
        """Marcar job como fallido."""
        self.status = "failed"
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.error_details = error_details or {}

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.execution_time_seconds = delta.total_seconds()

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "error_message",
                "error_details",
                "execution_time_seconds",
            ]
        )


class ETLValidationError(TimeStampedModel):
    """Error de validacion durante ETL."""

    job = models.ForeignKey(
        ETLJob,
        on_delete=models.CASCADE,
        related_name="validation_errors",
        help_text="Job relacionado",
    )
    error_type = models.CharField(max_length=100, help_text="Tipo de error")
    error_message = models.TextField(help_text="Mensaje de error")
    record_data = models.JSONField(default=dict, help_text="Datos del registro")
    field_name = models.CharField(
        max_length=100, null=True, blank=True, help_text="Campo con error"
    )
    severity = models.CharField(
        max_length=20,
        choices=[
            ("warning", "Advertencia"),
            ("error", "Error"),
            ("critical", "Critico"),
        ],
        default="error",
        help_text="Severidad",
    )

    class Meta:
        verbose_name = "Error de validacion ETL"
        verbose_name_plural = "Errores de validacion ETL"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.error_type} - {self.job.job_name}"
