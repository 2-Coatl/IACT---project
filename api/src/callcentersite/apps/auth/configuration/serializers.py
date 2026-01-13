"""
Serializers para API REST de configuraciones del sistema.

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (FASE 3)
"""

from __future__ import annotations

from rest_framework import serializers

from .models import Configuracion, ConfiguracionHistorial


class ConfiguracionSerializer(serializers.ModelSerializer):
    """Serializer para configuraciones del sistema."""

    class Meta:
        model = Configuracion
        fields = [
            'id',
            'categoria',
            'clave',
            'valor',
            'tipo_dato',
            'valor_default',
            'descripcion',
            'activa',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = ['id', 'updated_at', 'updated_by']


class EditarConfiguracionSerializer(serializers.Serializer):
    """Serializer para editar una configuracion."""

    nuevo_valor = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=1000,
        help_text='Nuevo valor para la configuracion',
    )


class ImportarConfiguracionSerializer(serializers.Serializer):
    """Serializer para importar configuraciones desde JSON."""

    configuraciones_json = serializers.JSONField(
        required=True,
        help_text='Diccionario con configuraciones a importar',
    )

    def validate_configuraciones_json(self, value):
        """Valida que sea un dict valido."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                'configuraciones_json debe ser un objeto JSON'
            )
        return value


class ConfiguracionHistorialSerializer(serializers.ModelSerializer):
    """Serializer para historial de cambios."""

    class Meta:
        model = ConfiguracionHistorial
        fields = [
            'id',
            'configuracion',
            'clave',
            'valor_anterior',
            'valor_nuevo',
            'modificado_por',
            'timestamp',
            'ip_address',
        ]
        read_only_fields = fields
