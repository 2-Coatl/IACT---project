"""
Serializers para API REST de dashboards.

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (FASE 3)
"""

from __future__ import annotations

from rest_framework import serializers

from .models import DashboardConfiguracion


class DashboardConfiguracionSerializer(serializers.ModelSerializer):
    """Serializer para configuracion de dashboard."""

    class Meta:
        model = DashboardConfiguracion
        fields = ['id', 'usuario', 'configuracion', 'updated_at', 'created_at']
        read_only_fields = ['id', 'usuario', 'updated_at', 'created_at']

    def validate_configuracion(self, value):
        """Valida que configuracion sea un dict valido."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                'La configuracion debe ser un objeto JSON'
            )
        return value


class ExportarDashboardSerializer(serializers.Serializer):
    """Serializer para exportar dashboard."""

    formato = serializers.ChoiceField(
        choices=['pdf', 'excel'],
        default='pdf',
        help_text='Formato de exportacion',
    )


class PersonalizarDashboardSerializer(serializers.Serializer):
    """Serializer para personalizar dashboard."""

    configuracion = serializers.JSONField(
        required=True,
        help_text='Configuracion de widgets y layout',
    )

    def validate_configuracion(self, value):
        """Valida que configuracion sea un dict valido."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                'La configuracion debe ser un objeto JSON'
            )
        return value


class CompartirDashboardSerializer(serializers.Serializer):
    """Serializer para compartir dashboard."""

    compartir_con_usuario_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text='ID del usuario con quien compartir',
    )
    compartir_con_grupo_codigo = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=100,
        help_text='Codigo del grupo con quien compartir',
    )

    def validate(self, data):
        """Valida que se especifique al menos un receptor."""
        if not data.get('compartir_con_usuario_id') and not data.get('compartir_con_grupo_codigo'):
            raise serializers.ValidationError(
                'Debe especificar compartir_con_usuario_id o compartir_con_grupo_codigo'
            )
        return data
