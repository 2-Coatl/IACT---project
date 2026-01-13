"""
Serializers para el sistema de permisos granular.

Sistema de Permisos Granular - Prioridad 2: API Layer
REF: ADR-012-sistema-permisos-sin-roles-jerarquicos.md
"""

from __future__ import annotations

from rest_framework import serializers

from callcentersite.apps.access.models import (
    Funcion,
    Capacidad,
    FuncionCapacidad,
    GrupoPermisos,
    GrupoCapacidad,
    UsuarioGrupo,
    PermisoExcepcional,
    AuditoriaPermiso,
)


class FuncionSerializer(serializers.ModelSerializer):
    """Serializer para Funcion del sistema."""

    class Meta:
        model = Funcion
        fields = [
            'id',
            'nombre',
            'nombre_completo',
            'descripcion',
            'dominio',
            'categoria',
            'icono',
            'orden_menu',
            'activa',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CapacidadSerializer(serializers.ModelSerializer):
    """Serializer para Capacidad."""

    class Meta:
        model = Capacidad
        fields = [
            'id',
            'nombre_completo',
            'descripcion',
            'accion',
            'recurso',
            'dominio',
            'nivel_sensibilidad',
            'requiere_auditoria',
            'activa',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class FuncionCapacidadSerializer(serializers.ModelSerializer):
    """Serializer para relacion Funcion-Capacidad."""

    funcion_nombre = serializers.CharField(source='funcion.nombre_completo', read_only=True)
    capacidad_nombre = serializers.CharField(source='capacidad.nombre_completo', read_only=True)

    class Meta:
        model = FuncionCapacidad
        fields = [
            'id',
            'funcion',
            'capacidad',
            'funcion_nombre',
            'capacidad_nombre',
            'requerida',
            'visible_en_ui',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class GrupoPermisosSerializer(serializers.ModelSerializer):
    """Serializer para GrupoPermisos."""

    capacidades_count = serializers.SerializerMethodField()

    class Meta:
        model = GrupoPermisos
        fields = [
            'id',
            'codigo',
            'nombre_display',
            'descripcion',
            'tipo_acceso',
            'activo',
            'created_at',
            'updated_at',
            'capacidades_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_capacidades_count(self, obj) -> int:
        """Retorna cantidad de capacidades del grupo."""
        return obj.grupo_capacidades.count()


class GrupoPermisosDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para GrupoPermisos con capacidades incluidas."""

    capacidades = serializers.SerializerMethodField()

    class Meta:
        model = GrupoPermisos
        fields = [
            'id',
            'codigo',
            'nombre_display',
            'descripcion',
            'tipo_acceso',
            'activo',
            'created_at',
            'updated_at',
            'capacidades',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_capacidades(self, obj) -> list[dict]:
        """Retorna capacidades del grupo."""
        grupo_caps = obj.grupo_capacidades.select_related('capacidad').all()
        return [
            {
                'id': gc.capacidad.id,
                'nombre_completo': gc.capacidad.nombre_completo,
                'nivel_sensibilidad': gc.capacidad.nivel_sensibilidad,
            }
            for gc in grupo_caps
        ]


class GrupoCapacidadSerializer(serializers.ModelSerializer):
    """Serializer para relacion Grupo-Capacidad."""

    grupo_nombre = serializers.CharField(source='grupo.nombre_display', read_only=True)
    capacidad_nombre = serializers.CharField(source='capacidad.nombre_completo', read_only=True)

    class Meta:
        model = GrupoCapacidad
        fields = [
            'id',
            'grupo',
            'capacidad',
            'grupo_nombre',
            'capacidad_nombre',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class UsuarioGrupoSerializer(serializers.ModelSerializer):
    """Serializer para UsuarioGrupo (asignaciones)."""

    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    grupo_nombre = serializers.CharField(source='grupo.nombre_display', read_only=True)

    class Meta:
        model = UsuarioGrupo
        fields = [
            'id',
            'usuario',
            'grupo',
            'fecha_asignacion',
            'fecha_expiracion',
            'asignado_por',
            'activo',
            'usuario_username',
            'grupo_nombre',
        ]
        read_only_fields = ['id', 'fecha_asignacion']


class UsuarioGrupoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear asignaciones Usuario-Grupo."""

    class Meta:
        model = UsuarioGrupo
        fields = [
            'usuario',
            'grupo',
            'fecha_expiracion',
            'asignado_por',
            'activo',
        ]

    def validate(self, attrs):
        """Valida que no exista asignacion duplicada activa."""
        usuario = attrs.get('usuario')
        grupo = attrs.get('grupo')

        # Verificar si ya existe asignacion activa
        if UsuarioGrupo.objects.filter(
            usuario=usuario,
            grupo=grupo
        ).exists():
            raise serializers.ValidationError({
                'non_field_errors': [
                    f'Usuario {usuario.username} ya esta asignado al grupo {grupo.nombre_display}'
                ]
            })

        return attrs


class PermisoExcepcionalSerializer(serializers.ModelSerializer):
    """Serializer para PermisoExcepcional."""

    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    capacidad_nombre = serializers.CharField(source='capacidad.nombre_completo', read_only=True)
    autorizado_por_username = serializers.CharField(
        source='autorizado_por.username',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = PermisoExcepcional
        fields = [
            'id',
            'usuario',
            'capacidad',
            'tipo',
            'fecha_inicio',
            'fecha_fin',
            'motivo',
            'autorizado_por',
            'activo',
            'created_at',
            'usuario_username',
            'capacidad_nombre',
            'autorizado_por_username',
        ]
        read_only_fields = ['id', 'created_at']


class PermisoExcepcionalCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear permisos excepcionales."""

    class Meta:
        model = PermisoExcepcional
        fields = [
            'usuario',
            'capacidad',
            'tipo',
            'fecha_inicio',
            'fecha_fin',
            'motivo',
            'autorizado_por',
            'activo',
        ]

    def validate(self, attrs):
        """Validaciones adicionales."""
        fecha_inicio = attrs.get('fecha_inicio')
        fecha_fin = attrs.get('fecha_fin')

        if fecha_fin and fecha_inicio and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError({
                'fecha_fin': 'Fecha de fin debe ser posterior a fecha de inicio'
            })

        return attrs


class AuditoriaPermisoSerializer(serializers.ModelSerializer):
    """Serializer para AuditoriaPermiso (solo lectura)."""

    usuario_username = serializers.CharField(
        source='usuario.username',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = AuditoriaPermiso
        fields = [
            'id',
            'usuario',
            'capacidad',
            'accion_realizada',
            'recurso_accedido',
            'ip_address',
            'user_agent',
            'metadata',
            'timestamp',
            'usuario_username',
        ]
        read_only_fields = fields  # Todos read-only (auditoria no se modifica)
