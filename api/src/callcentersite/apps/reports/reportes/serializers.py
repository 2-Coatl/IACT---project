"""Serializers para reportes IVR."""

from __future__ import annotations

from rest_framework import serializers

from .models import (
    ReporteClientesUnicos,
    ReporteLlamadasDia,
    ReporteMenuProblemas,
    ReporteTransferencias,
    ReporteTrimestral,
)


class ReporteTrimestralSerializer(serializers.ModelSerializer):
    """Serializer para reportes trimestrales."""

    class Meta:
        model = ReporteTrimestral
        fields = [
            "id",
            "trimestre",
            "anio",
            "total_llamadas",
            "llamadas_atendidas",
            "llamadas_abandonadas",
            "tiempo_promedio_espera",
            "tiempo_promedio_atencion",
            "nivel_servicio",
            "tasa_abandono",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReporteTransferenciasSerializer(serializers.ModelSerializer):
    """Serializer para reportes de transferencias."""

    class Meta:
        model = ReporteTransferencias
        fields = [
            "id",
            "fecha",
            "centro_origen",
            "centro_destino",
            "total_transferencias",
            "transferencias_exitosas",
            "transferencias_fallidas",
            "tiempo_promedio_transferencia",
            "tasa_exito",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReporteMenuProblemasSerializer(serializers.ModelSerializer):
    """Serializer para reportes de menus problematicos."""

    class Meta:
        model = ReporteMenuProblemas
        fields = [
            "id",
            "fecha",
            "menu_id",
            "menu_nombre",
            "veces_accedido",
            "abandonos",
            "timeout",
            "errores",
            "tasa_abandono",
            "tiempo_promedio_permanencia",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReporteLlamadasDiaSerializer(serializers.ModelSerializer):
    """Serializer para reportes de llamadas por dia."""

    class Meta:
        model = ReporteLlamadasDia
        fields = [
            "id",
            "fecha",
            "hora",
            "total_llamadas",
            "llamadas_atendidas",
            "llamadas_abandonadas",
            "tiempo_promedio_espera",
            "tiempo_promedio_atencion",
            "nivel_servicio",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReporteClientesUnicosSerializer(serializers.ModelSerializer):
    """Serializer para reportes de clientes unicos."""

    class Meta:
        model = ReporteClientesUnicos
        fields = [
            "id",
            "fecha_inicio",
            "fecha_fin",
            "total_clientes_unicos",
            "nuevos_clientes",
            "clientes_recurrentes",
            "promedio_llamadas_cliente",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ExportarReporteSerializer(serializers.Serializer):
    """Serializer para solicitud de exportacion de reportes."""

    tipo_reporte = serializers.ChoiceField(
        choices=[
            ("trimestral", "Trimestral"),
            ("transferencias", "Transferencias"),
            ("menus_problematicos", "Menus Problematicos"),
            ("llamadas_dia", "Llamadas por Dia"),
            ("clientes_unicos", "Clientes Unicos"),
        ],
        help_text="Tipo de reporte a exportar",
    )
    formato = serializers.ChoiceField(
        choices=[("csv", "CSV"), ("excel", "Excel"), ("pdf", "PDF")],
        default="csv",
        help_text="Formato de exportacion",
    )
    filtros = serializers.JSONField(
        required=False,
        help_text="Filtros a aplicar al reporte (JSON)",
    )

    def validate_filtros(self, value):
        """Validar estructura de filtros."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            msg = "Los filtros deben ser un objeto JSON"
            raise serializers.ValidationError(msg)
        return value
