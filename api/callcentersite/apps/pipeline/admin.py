from django.contrib import admin
from apps.pipeline.models import ETLExecution


@admin.register(ETLExecution)
class ETLExecutionAdmin(admin.ModelAdmin):
    """
    Admin para ETLExecution.
    
    Solo lectura - las ejecuciones se crean automaticamente.
    """
    
    list_display = (
        'id',
        'start_date',
        'end_date',
        'status',
        'records_extracted',
        'records_loaded',
        'started_at',
        'completed_at',
    )
    
    list_filter = ('status', 'started_at')
    
    search_fields = ('error_message',)
    
    readonly_fields = (
        'start_date',
        'end_date',
        'status',
        'records_extracted',
        'records_loaded',
        'started_at',
        'completed_at',
        'error_message',
    )
    
    date_hierarchy = 'started_at'
    
    def has_add_permission(self, request):
        """NO permitir crear manualmente."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """NO permitir modificar."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar (limpiar logs viejos)."""
        return True
