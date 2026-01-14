"""Modelos de reportes."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from callcentersite.apps.common.models import TimeStampedModel


class ReportTemplate(TimeStampedModel):
    """Plantilla de reporte configurable."""

    FORMAT_CHOICES = [
        ("csv", "CSV"),
        ("excel", "Excel"),
        ("pdf", "PDF"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    query_config = models.JSONField(default=dict)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="report_templates",
    )

    class Meta:
        verbose_name = "plantilla de reporte"
        verbose_name_plural = "plantillas de reporte"
        ordering = ("name",)


class GeneratedReport(TimeStampedModel):
    """Reporte generado listo para descarga."""

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("completed", "Completado"),
        ("failed", "Fallido"),
    ]

    template = models.ForeignKey(
        ReportTemplate, on_delete=models.CASCADE, related_name="generated_reports"
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="generated_reports",
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to="reports/")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    parameters = models.JSONField(default=dict)
    file_size = models.BigIntegerField(default=0)
    record_count = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "reporte generado"
        verbose_name_plural = "reportes generados"
        ordering = ("-generated_at",)


# Modelos para reportes IVR - Datos agregados extraídos desde BD IVR


class ReporteTrimestral(TimeStampedModel):
    """Reporte agregado trimestral de llamadas IVR."""

    TRIMESTRE_CHOICES = [
        ("Q1", "Primer Trimestre"),
        ("Q2", "Segundo Trimestre"),
        ("Q3", "Tercer Trimestre"),
        ("Q4", "Cuarto Trimestre"),
    ]

    trimestre = models.CharField(
        max_length=2, choices=TRIMESTRE_CHOICES, help_text="Trimestre del reporte"
    )
    anio = models.IntegerField(help_text="Anio del reporte")
    total_llamadas = models.IntegerField(
        default=0, help_text="Total de llamadas en el trimestre"
    )
    llamadas_atendidas = models.IntegerField(
        default=0, help_text="Llamadas atendidas exitosamente"
    )
    llamadas_abandonadas = models.IntegerField(
        default=0, help_text="Llamadas abandonadas"
    )
    tiempo_promedio_espera = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tiempo promedio de espera en segundos",
    )
    tiempo_promedio_atencion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tiempo promedio de atención en segundos",
    )
    nivel_servicio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Nivel de servicio en porcentaje",
    )
    tasa_abandono = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Tasa de abandono en porcentaje",
    )

    class Meta:
        verbose_name = "reporte trimestral"
        verbose_name_plural = "reportes trimestrales"
        ordering = ("-anio", "-trimestre")
        unique_together = [["trimestre", "anio"]]

    def __str__(self):
        return f"Reporte {self.trimestre} {self.anio}"


class ReporteTransferencias(TimeStampedModel):
    """Reporte de transferencias entre centros de atención."""

    fecha = models.DateField(help_text="Fecha del reporte")
    centro_origen = models.CharField(
        max_length=100, help_text="Centro de atención origen"
    )
    centro_destino = models.CharField(
        max_length=100, help_text="Centro de atención destino"
    )
    total_transferencias = models.IntegerField(
        default=0, help_text="Total de transferencias"
    )
    transferencias_exitosas = models.IntegerField(
        default=0, help_text="Transferencias completadas exitosamente"
    )
    transferencias_fallidas = models.IntegerField(
        default=0, help_text="Transferencias fallidas"
    )
    tiempo_promedio_transferencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tiempo promedio de transferencia en segundos",
    )
    tasa_exito = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Tasa de éxito en porcentaje",
    )

    class Meta:
        verbose_name = "reporte de transferencias"
        verbose_name_plural = "reportes de transferencias"
        ordering = ("-fecha", "centro_origen")
        unique_together = [["fecha", "centro_origen", "centro_destino"]]

    def __str__(self):
        return f"Transferencias {self.fecha}: {self.centro_origen} → {self.centro_destino}"


class ReporteMenuProblemas(TimeStampedModel):
    """Reporte de menús problemáticos del IVR."""

    fecha = models.DateField(help_text="Fecha del reporte")
    menu_id = models.CharField(max_length=50, help_text="ID del menú IVR")
    menu_nombre = models.CharField(max_length=200, help_text="Nombre del menú")
    veces_accedido = models.IntegerField(
        default=0, help_text="Veces que se accedió al menú"
    )
    abandonos = models.IntegerField(default=0, help_text="Abandonos en el menú")
    timeout = models.IntegerField(default=0, help_text="Timeout en el menú")
    errores = models.IntegerField(default=0, help_text="Errores en el menú")
    tasa_abandono = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Tasa de abandono (%)"
    )
    tiempo_promedio_permanencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tiempo promedio en el menú (segundos)",
    )

    class Meta:
        verbose_name = "reporte de menú problemático"
        verbose_name_plural = "reportes de menús problemáticos"
        ordering = ("-fecha", "-abandonos")
        unique_together = [["fecha", "menu_id"]]

    def __str__(self):
        return f"Menú {self.menu_nombre} - {self.fecha}"


class ReporteLlamadasDia(TimeStampedModel):
    """Reporte de llamadas por día y hora."""

    fecha = models.DateField(help_text="Fecha del reporte")
    hora = models.IntegerField(help_text="Hora del día (0-23)")
    total_llamadas = models.IntegerField(default=0, help_text="Total de llamadas")
    llamadas_atendidas = models.IntegerField(
        default=0, help_text="Llamadas atendidas"
    )
    llamadas_abandonadas = models.IntegerField(
        default=0, help_text="Llamadas abandonadas"
    )
    tiempo_promedio_espera = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tiempo promedio de espera (segundos)",
    )
    tiempo_promedio_atencion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tiempo promedio de atención (segundos)",
    )
    nivel_servicio = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Nivel de servicio (%)"
    )

    class Meta:
        verbose_name = "reporte de llamadas por día"
        verbose_name_plural = "reportes de llamadas por día"
        ordering = ("-fecha", "hora")
        unique_together = [["fecha", "hora"]]

    def __str__(self):
        return f"Llamadas {self.fecha} {self.hora}:00"


class ReporteClientesUnicos(TimeStampedModel):
    """Reporte de clientes únicos que llamaron al IVR."""

    fecha_inicio = models.DateField(help_text="Fecha de inicio del período")
    fecha_fin = models.DateField(help_text="Fecha de fin del período")
    total_clientes_unicos = models.IntegerField(
        default=0, help_text="Total de clientes únicos"
    )
    nuevos_clientes = models.IntegerField(
        default=0, help_text="Clientes que llamaron por primera vez"
    )
    clientes_recurrentes = models.IntegerField(
        default=0, help_text="Clientes que ya habían llamado antes"
    )
    promedio_llamadas_cliente = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Promedio de llamadas por cliente",
    )

    class Meta:
        verbose_name = "reporte de clientes únicos"
        verbose_name_plural = "reportes de clientes únicos"
        ordering = ("-fecha_inicio",)
        unique_together = [["fecha_inicio", "fecha_fin"]]

    def __str__(self):
        return f"Clientes únicos {self.fecha_inicio} - {self.fecha_fin}"
