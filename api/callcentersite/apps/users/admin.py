from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.access.models import UserFunctionAssignment


class FunctionAssignmentInline(admin.TabularInline):
    """
    Inline para mostrar funciones asignadas.
    
    Permite ver y editar funciones desde admin de usuarios.
    """
    model = UserFunctionAssignment
    fk_name = 'user'  # Especificar FK porque hay 2 a User
    extra = 0
    readonly_fields = ('assigned_at', 'assigned_by')
    fields = (
        'function',
        'is_active',
        'assigned_at',
        'assigned_by',
        'reason'
    )
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar asignaciones."""
        return True


class UserAdmin(BaseUserAdmin):
    """
    Admin extendido para User.
    
    Incluye:
    - Funciones asignadas (inline)
    - Filtros mejorados
    - Busqueda por username/email
    """
    
    inlines = [FunctionAssignmentInline]
    
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
    )
    
    list_filter = (
        'is_staff',
        'is_active',
        'is_superuser',
        'date_joined',
    )
    
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    
    ordering = ('-date_joined',)


# Registrar User con admin personalizado
admin.site.register(User, UserAdmin)
