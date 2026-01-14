"""
Modelos core - IACT Call Center System.

CNST-003: Modelos analytics (PostgreSQL default DB).
"""
from django.db import models
from decimal import Decimal


class CallRecord(models.Model):
    """
    Registro de llamadas procesado.
    
    Almacena datos agregados por fecha/telefono/servicio.
    Base de datos: default (PostgreSQL analytics).
    
    CNST-003: Este modelo usa 'default' DB (PostgreSQL).
    NO usa 'ivr_legacy' (MariaDB READ-ONLY).
    """
    
    fecha = models.DateField(
        db_index=True,
        help_text='Fecha de las llamadas'
    )
    
    telefono = models.CharField(
        max_length=20,
        db_index=True,
        help_text='Numero telefonico que realizo llamadas'
    )
    
    servicio_800 = models.CharField(
        max_length=20,
        db_index=True,
        help_text='Numero servicio 800 destino'
    )
    
    total_llamadas = models.IntegerField(
        default=0,
        help_text='Total de llamadas realizadas'
    )
    
    llamadas_contestadas = models.IntegerField(
        default=0,
        help_text='Llamadas contestadas por agente'
    )
    
    llamadas_abandonadas = models.IntegerField(
        default=0,
        help_text='Llamadas abandonadas (colgadas antes de contestar)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp creacion registro'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp ultima actualizacion'
    )
    
    class Meta:
        db_table = 'core_call_records'
        ordering = ['-fecha', '-created_at']
        unique_together = [['fecha', 'telefono', 'servicio_800']]
        indexes = [
            models.Index(fields=['fecha', 'servicio_800']),
            models.Index(fields=['fecha', 'telefono']),
        ]
        verbose_name = 'Registro de Llamada'
        verbose_name_plural = 'Registros de Llamadas'
    
    def __str__(self):
        """Representacion string."""
        return f"{self.fecha} - {self.telefono} -> {self.servicio_800}"
    
    def answer_rate(self):
        """
        Calcular porcentaje de respuesta.
        
        Returns:
            Decimal: Porcentaje (0-100)
        """
        if self.total_llamadas == 0:
            return Decimal('0.00')
        
        rate = (Decimal(self.llamadas_contestadas) / 
                Decimal(self.total_llamadas)) * 100
        return rate.quantize(Decimal('0.01'))


class Center(models.Model):
    """
    Centro de atencion.
    
    Representa un centro fisico de call center.
    """
    
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre del centro'
    )
    
    codigo = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Codigo unico del centro'
    )
    
    activo = models.BooleanField(
        default=True,
        help_text='Centro activo'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_centers'
        ordering = ['nombre']
        verbose_name = 'Centro'
        verbose_name_plural = 'Centros'
    
    def __str__(self):
        return self.nombre



class Service(models.Model):
    """
    Servicio 800.
    
    Representa un numero de servicio 800 asociado a un centro.
    """
    
    numero_800 = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Numero servicio 800'
    )
    
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre del servicio'
    )
    
    center = models.ForeignKey(
        Center,
        on_delete=models.PROTECT,
        related_name='services',
        help_text='Centro al que pertenece'
    )
    
    activo = models.BooleanField(
        default=True,
        help_text='Servicio activo'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_services'
        ordering = ['numero_800']
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
    
    def __str__(self):
        return f"{self.numero_800} - {self.nombre}"
