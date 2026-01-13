"""Configuracion de Django Admin para configuration."""

from django.contrib import admin

from .models import Configuracion, ConfiguracionHistorial


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    """Admin para modelo Configuracion."""

    list_display = [
        'clave',
        'categoria',
        'valor',
        'tipo_dato',
        'activa',
        'updated_at',
        'updated_by',
    ]
    list_filter = ['categoria', 'tipo_dato', 'activa']
    search_fields = ['clave', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (
            'Informacion Basica',
            {
                'fields': ['categoria', 'clave', 'descripcion'],
            },
        ),
        (
            'Valor',
            {
                'fields': ['tipo_dato', 'valor', 'valor_default'],
            },
        ),
        (
            'Estado',
            {
                'fields': ['activa'],
            },
        ),
        (
            'Auditoria',
            {
                'fields': ['created_at', 'updated_at', 'updated_by'],
                'classes': ['collapse'],
            },
        ),
    ]


@admin.register(ConfiguracionHistorial)
class ConfiguracionHistorialAdmin(admin.ModelAdmin):
    """Admin para modelo ConfiguracionHistorial."""

    list_display = [
        'clave',
        'valor_anterior',
        'valor_nuevo',
        'modificado_por',
        'timestamp',
    ]
    list_filter = ['timestamp', 'modificado_por']
    search_fields = ['clave']
    readonly_fields = [
        'configuracion',
        'clave',
        'valor_anterior',
        'valor_nuevo',
        'modificado_por',
        'timestamp',
        'ip_address',
        'user_agent',
    ]

    def has_add_permission(self, request):
        """No permitir agregar registros manualmente."""
        return False

    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar registros de auditoria."""
        return False
