from django.db import models


class ETLExecution(models.Model):
    """
    Registro de ejecucion ETL.
    
    CNST-004: ETL programado cada 6-12 horas (NO real-time).
    
    Tracking de:
    - Rango de fechas procesadas
    - Status de ejecucion
    - Registros procesados
    - Errores si ocurrieron
    """
    
    # Rango de datos procesados
    start_date = models.DateField(
        verbose_name='Fecha inicio'
    )
    end_date = models.DateField(
        verbose_name='Fecha fin'
    )
    
    # Status ejecucion
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pendiente'),
            ('RUNNING', 'Ejecutando'),
            ('SUCCESS', 'Exitoso'),
            ('FAILED', 'Fallido'),
        ],
        default='PENDING',
        verbose_name='Estado',
    )
    
    # Metricas
    records_extracted = models.IntegerField(
        default=0,
        verbose_name='Registros extraidos',
        help_text='Cantidad de registros extraidos de IVR',
    )
    records_loaded = models.IntegerField(
        default=0,
        verbose_name='Registros cargados',
        help_text='Cantidad de registros cargados en Analytics',
    )
    
    # Timestamps
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Iniciado',
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Completado',
    )
    
    # Error tracking
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de error',
    )
    
    class Meta:
        db_table = 'etl_executions'
        verbose_name = 'Ejecucion ETL'
        verbose_name_plural = 'Ejecuciones ETL'
        # Añadimos -id para desempatar tiempos idénticos
        ordering = ['-started_at', '-id']
        indexes = [
            models.Index(fields=['-started_at', '-id']), # Ajustamos el índice
            models.Index(fields=['status', '-started_at']),
        ]
    
    def __str__(self):
        return f"ETL {self.start_date} to {self.end_date} - {self.status}"
