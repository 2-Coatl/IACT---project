"""
Serializers para Llamadas.

Sistema de Permisos Granular - Prioridad 3: Módulo Operativo Llamadas
"""

from rest_framework import serializers
from callcentersite.apps.llamadas.models import (
    EstadoLlamada,
    TipoLlamada,
    Llamada,
    LlamadaTranscripcion,
    LlamadaGrabacion,
)


class EstadoLlamadaSerializer(serializers.ModelSerializer):
    """Serializer para EstadoLlamada."""

    class Meta:
        model = EstadoLlamada
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'es_final', 'activo', 'created_at']
        read_only_fields = ['id', 'created_at']


class TipoLlamadaSerializer(serializers.ModelSerializer):
    """Serializer para TipoLlamada."""

    class Meta:
        model = TipoLlamada
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'activo', 'created_at']
        read_only_fields = ['id', 'created_at']


class LlamadaSerializer(serializers.ModelSerializer):
    """Serializer para Llamada."""

    duracion = serializers.SerializerMethodField()
    agente_username = serializers.CharField(source='agente.username', read_only=True)
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)

    class Meta:
        model = Llamada
        fields = [
            'id', 'codigo', 'numero_telefono', 'tipo', 'estado', 'agente',
            'cliente_nombre', 'cliente_email', 'cliente_id',
            'fecha_inicio', 'fecha_fin', 'metadata', 'notas',
            'created_at', 'updated_at',
            'duracion', 'agente_username', 'estado_nombre', 'tipo_nombre'
        ]
        read_only_fields = ['id', 'codigo', 'created_at', 'updated_at']

    def get_duracion(self, obj):
        """Obtener duracion calculada."""
        return obj.calcular_duracion()


class LlamadaTranscripcionSerializer(serializers.ModelSerializer):
    """Serializer para LlamadaTranscripcion."""

    class Meta:
        model = LlamadaTranscripcion
        fields = [
            'id', 'llamada', 'texto', 'timestamp_inicio', 'timestamp_fin',
            'hablante', 'confianza', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LlamadaGrabacionSerializer(serializers.ModelSerializer):
    """Serializer para LlamadaGrabacion."""

    class Meta:
        model = LlamadaGrabacion
        fields = [
            'id', 'llamada', 'archivo_url', 'formato', 'duracion_segundos',
            'tamano_bytes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
