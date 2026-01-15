from django.contrib import admin
from apps.access.models import Function, UserFunctionAssignment


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    """
    Admin para funciones RBAC.
    
    Permite crear/editar funciones atomicas del sistema.
    """
    
    list_display = ('code', 'module', 'name', 'is_active', 'created_at')
    list_filter = ('module', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informacion', {
            'fields': ('code', 'module', 'name', 'description')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserFunctionAssignment)
class UserFunctionAssignmentAdmin(admin.ModelAdmin):
    """
    Admin para asignaciones funciones.
    
    Muestra quien asigno que funcion a quien y cuando.
    """
    
    list_display = (
        'user',
        'function',
        'is_active',
        'assigned_by',
        'assigned_at'
    )
    list_filter = (
        'is_active',
        'function__module',
        'assigned_at'
    )
    search_fields = (
        'user__username',
        'function__code',
        'function__name'
    )
    readonly_fields = (
        'assigned_at',
        'assigned_by',
        'revoked_at',
        'revoked_by'
    )
    
    fieldsets = (
        ('Asignacion', {
            'fields': ('user', 'function', 'reason')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Auditoria Asignacion', {
            'fields': ('assigned_at', 'assigned_by'),
            'classes': ('collapse',)
        }),
        ('Auditoria Revocacion', {
            'fields': ('revoked_at', 'revoked_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Guardar quien asigna la funcion."""
        if not change:  # Si es nuevo
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)
