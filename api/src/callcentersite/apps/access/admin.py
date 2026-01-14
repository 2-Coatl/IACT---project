"""
Admin para Sistema de Permisos Granular.

Registra todos los modelos en Django Admin para gestion.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Funcion,
    Capacidad,
    FuncionCapacidad,
    GrupoPermisos,
    GrupoCapacidad,
    UsuarioGrupo,
    PermisoExcepcional,
    AuditoriaPermiso
)


@admin.register(Funcion)
class FuncionAdmin(admin.ModelAdmin):
    """Admin para Funcion."""

    list_display = [
        'nombre',
        'nombre_completo',
        'dominio',
        'categoria',
        'orden_menu',
        'activa_badge',
        'created_at'
    ]
    list_filter = ['dominio', 'categoria', 'activa']
    search_fields = ['nombre', 'nombre_completo', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['orden_menu', 'nombre']

    fieldsets = [
        ('Informacion Basica', {
            'fields': ('nombre', 'nombre_completo', 'descripcion')
        }),
        ('Clasificacion', {
            'fields': ('dominio', 'categoria', 'icono')
        }),
        ('Configuracion', {
            'fields': ('orden_menu', 'activa')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    def activa_badge(self, obj):
        """Badge para campo activa."""
        if obj.activa:
            return format_html('<span style="color: green;">ACTIVA</span>')
        return format_html('<span style="color: red;">INACTIVA</span>')
    activa_badge.short_description = 'Estado'


@admin.register(Capacidad)
class CapacidadAdmin(admin.ModelAdmin):
    """Admin para Capacidad."""

    list_display = [
        'nombre_completo',
        'accion',
        'recurso',
        'dominio',
        'nivel_sensibilidad_badge',
        'requiere_auditoria_badge',
        'activa_badge'
    ]
    list_filter = ['dominio', 'nivel_sensibilidad', 'requiere_auditoria', 'activa']
    search_fields = ['nombre_completo', 'descripcion', 'accion', 'recurso']
    readonly_fields = ['created_at']
    ordering = ['nombre_completo']

    fieldsets = [
        ('Identificacion', {
            'fields': ('nombre_completo', 'descripcion')
        }),
        ('Componentes', {
            'fields': ('accion', 'recurso', 'dominio')
        }),
        ('Seguridad', {
            'fields': ('nivel_sensibilidad', 'requiere_auditoria')
        }),
        ('Estado', {
            'fields': ('activa', 'created_at')
        }),
    ]

    def nivel_sensibilidad_badge(self, obj):
        """Badge para nivel de sensibilidad."""
        colors = {
            'bajo': 'green',
            'normal': 'blue',
            'alto': 'orange',
            'critico': 'red'
        }
        color = colors.get(obj.nivel_sensibilidad, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_nivel_sensibilidad_display()
        )
    nivel_sensibilidad_badge.short_description = 'Sensibilidad'

    def requiere_auditoria_badge(self, obj):
        """Badge para requiere_auditoria."""
        if obj.requiere_auditoria:
            return format_html('<span style="color: red;">SI</span>')
        return format_html('<span style="color: gray;">NO</span>')
    requiere_auditoria_badge.short_description = 'Auditoria'

    def activa_badge(self, obj):
        """Badge para activa."""
        if obj.activa:
            return format_html('<span style="color: green;">SI</span>')
        return format_html('<span style="color: gray;">NO</span>')
    activa_badge.short_description = 'Activa'


@admin.register(FuncionCapacidad)
class FuncionCapacidadAdmin(admin.ModelAdmin):
    """Admin para FuncionCapacidad."""

    list_display = [
        'funcion',
        'capacidad',
        'requerida_badge',
        'visible_en_ui_badge',
        'created_at'
    ]
    list_filter = ['requerida', 'visible_en_ui']
    search_fields = ['funcion__nombre', 'capacidad__nombre_completo']
    autocomplete_fields = ['funcion', 'capacidad']
    readonly_fields = ['created_at']

    def requerida_badge(self, obj):
        """Badge para requerida."""
        if obj.requerida:
            return format_html('<span style="color: red;">OBLIGATORIA</span>')
        return format_html('<span style="color: gray;">OPCIONAL</span>')
    requerida_badge.short_description = 'Requerida'

    def visible_en_ui_badge(self, obj):
        """Badge para visible_en_ui."""
        if obj.visible_en_ui:
            return format_html('<span style="color: green;">SI</span>')
        return format_html('<span style="color: gray;">NO</span>')
    visible_en_ui_badge.short_description = 'Visible UI'


@admin.register(GrupoPermisos)
class GrupoPermisosAdmin(admin.ModelAdmin):
    """Admin para GrupoPermisos."""

    list_display = [
        'nombre_display',
        'codigo',
        'tipo_acceso',
        'num_capacidades',
        'num_usuarios',
        'activo_badge',
        'created_at'
    ]
    list_filter = ['tipo_acceso', 'activo']
    search_fields = ['codigo', 'nombre_display', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['nombre_display']

    fieldsets = [
        ('Informacion Basica', {
            'fields': ('codigo', 'nombre_display', 'descripcion')
        }),
        ('Clasificacion', {
            'fields': ('tipo_acceso',)
        }),
        ('Estado', {
            'fields': ('activo', 'created_at', 'updated_at')
        }),
    ]

    def num_capacidades(self, obj):
        """Numero de capacidades del grupo."""
        return obj.capacidades.count()
    num_capacidades.short_description = 'Capacidades'

    def num_usuarios(self, obj):
        """Numero de usuarios asignados al grupo."""
        return obj.usuarios.filter(activo=True).count()
    num_usuarios.short_description = 'Usuarios'

    def activo_badge(self, obj):
        """Badge para activo."""
        if obj.activo:
            return format_html('<span style="color: green;">ACTIVO</span>')
        return format_html('<span style="color: red;">INACTIVO</span>')
    activo_badge.short_description = 'Estado'


@admin.register(GrupoCapacidad)
class GrupoCapacidadAdmin(admin.ModelAdmin):
    """Admin para GrupoCapacidad."""

    list_display = ['grupo', 'capacidad', 'created_at']
    list_filter = ['grupo']
    search_fields = ['grupo__codigo', 'capacidad__nombre_completo']
    autocomplete_fields = ['grupo', 'capacidad']
    readonly_fields = ['created_at']


@admin.register(UsuarioGrupo)
class UsuarioGrupoAdmin(admin.ModelAdmin):
    """Admin para UsuarioGrupo."""

    list_display = [
        'usuario',
        'grupo',
        'fecha_asignacion',
        'expiracion_badge',
        'asignado_por',
        'activo_badge'
    ]
    list_filter = ['activo', 'grupo']
    search_fields = ['usuario__username', 'grupo__codigo']
    autocomplete_fields = ['usuario', 'grupo', 'asignado_por']
    readonly_fields = ['fecha_asignacion']
    date_hierarchy = 'fecha_asignacion'

    fieldsets = [
        ('Asignacion', {
            'fields': ('usuario', 'grupo')
        }),
        ('Fechas', {
            'fields': ('fecha_asignacion', 'fecha_expiracion')
        }),
        ('Auditoria', {
            'fields': ('asignado_por', 'activo')
        }),
    ]

    def expiracion_badge(self, obj):
        """Badge para fecha_expiracion."""
        if obj.fecha_expiracion is None:
            return format_html('<span style="color: blue;">PERMANENTE</span>')
        if obj.is_expired():
            return format_html(
                '<span style="color: red;">EXPIRADO: {}</span>',
                obj.fecha_expiracion.strftime('%Y-%m-%d')
            )
        return format_html(
            '<span style="color: green;">Expira: {}</span>',
            obj.fecha_expiracion.strftime('%Y-%m-%d')
        )
    expiracion_badge.short_description = 'Expiracion'

    def activo_badge(self, obj):
        """Badge para activo."""
        if obj.activo and not obj.is_expired():
            return format_html('<span style="color: green;">ACTIVO</span>')
        return format_html('<span style="color: red;">INACTIVO</span>')
    activo_badge.short_description = 'Estado'


@admin.register(PermisoExcepcional)
class PermisoExcepcionalAdmin(admin.ModelAdmin):
    """Admin para PermisoExcepcional."""

    list_display = [
        'usuario',
        'capacidad',
        'tipo_badge',
        'fecha_inicio',
        'fecha_fin',
        'autorizado_por',
        'estado_badge'
    ]
    list_filter = ['tipo', 'activo']
    search_fields = ['usuario__username', 'capacidad__nombre_completo', 'motivo']
    autocomplete_fields = ['usuario', 'capacidad', 'autorizado_por']
    readonly_fields = ['created_at']
    date_hierarchy = 'fecha_inicio'

    fieldsets = [
        ('Permiso', {
            'fields': ('usuario', 'capacidad', 'tipo')
        }),
        ('Periodo', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Justificacion', {
            'fields': ('motivo', 'autorizado_por')
        }),
        ('Estado', {
            'fields': ('activo', 'created_at')
        }),
    ]

    def tipo_badge(self, obj):
        """Badge para tipo."""
        if obj.tipo == 'conceder':
            return format_html('<span style="color: green;">CONCEDER</span>')
        return format_html('<span style="color: red;">REVOCAR</span>')
    tipo_badge.short_description = 'Tipo'

    def estado_badge(self, obj):
        """Badge para estado actual."""
        if obj.is_active_now():
            return format_html('<span style="color: green;">ACTIVO AHORA</span>')
        return format_html('<span style="color: gray;">INACTIVO</span>')
    estado_badge.short_description = 'Estado'


@admin.register(AuditoriaPermiso)
class AuditoriaPermisoAdmin(admin.ModelAdmin):
    """Admin para AuditoriaPermiso."""

    list_display = [
        'timestamp',
        'usuario',
        'capacidad',
        'accion_badge',
        'recurso_accedido',
        'ip_address'
    ]
    list_filter = ['accion_realizada', 'timestamp']
    search_fields = ['usuario__username', 'capacidad', 'recurso_accedido', 'ip_address']
    readonly_fields = ['timestamp', 'metadata']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    fieldsets = [
        ('Acceso', {
            'fields': ('usuario', 'capacidad', 'accion_realizada', 'recurso_accedido')
        }),
        ('Contexto', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Metadata', {
            'fields': ('metadata', 'timestamp'),
            'classes': ('collapse',)
        }),
    ]

    def has_add_permission(self, request):
        """No permitir agregar registros de auditoria manualmente."""
        return False

    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar registros de auditoria."""
        return False

    def accion_badge(self, obj):
        """Badge para accion_realizada."""
        if obj.accion_realizada == 'acceso_concedido':
            return format_html('<span style="color: green;">CONCEDIDO</span>')
        return format_html('<span style="color: red;">DENEGADO</span>')
    accion_badge.short_description = 'Accion'
