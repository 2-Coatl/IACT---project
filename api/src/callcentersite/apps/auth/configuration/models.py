"""Modelos de configuracion del sistema."""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Configuracion(models.Model):
    """Parametros de configuracion del sistema.

    Almacena configuraciones tecnicas del sistema que pueden
    ser modificadas en tiempo de ejecución por usuarios autorizados.
    """

    TIPO_DATO_CHOICES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('float', 'Float'),
        ('json', 'JSON'),
        ('email', 'Email'),
        ('url', 'URL'),
    ]

    CATEGORIA_CHOICES = [
        ('general', 'General'),
        ('seguridad', 'Seguridad'),
        ('notificaciones', 'Notificaciones'),
        ('integraciones', 'Integraciones'),
        ('llamadas', 'Llamadas'),
        ('tickets', 'Tickets'),
        ('reportes', 'Reportes'),
        ('sistema', 'Sistema'),
    ]

    id = models.AutoField(primary_key=True)
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIA_CHOICES,
        db_index=True,
        help_text='Categoria de la configuracion'
    )
    clave = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='Clave unica de la configuracion'
    )
    valor = models.TextField(
        help_text='Valor actual de la configuracion'
    )
    tipo_dato = models.CharField(
        max_length=20,
        choices=TIPO_DATO_CHOICES,
        help_text='Tipo de dato del valor'
    )
    valor_default = models.TextField(
        help_text='Valor por defecto de la configuracion'
    )
    descripcion = models.TextField(
        blank=True,
        help_text='Descripcion de la configuracion'
    )
    activa = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Indica si la configuracion esta activa'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Fecha de ultima actualizacion'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='configuraciones_actualizadas',
        help_text='Usuario que realizo la ultima modificacion'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creacion'
    )

    class Meta:
        db_table = 'configuracion'
        verbose_name = 'Configuracion'
        verbose_name_plural = 'Configuraciones'
        ordering = ['categoria', 'clave']
        indexes = [
            models.Index(fields=['categoria', 'activa']),
            models.Index(fields=['clave']),
        ]

    def __str__(self):
        return f"{self.categoria}.{self.clave}"

    def get_valor_typed(self):
        """Retorna el valor convertido a su tipo de dato correspondiente."""
        if self.tipo_dato == 'integer':
            return int(self.valor)
        elif self.tipo_dato == 'boolean':
            return self.valor.lower() in ['true', '1', 'yes']
        elif self.tipo_dato == 'float':
            return float(self.valor)
        elif self.tipo_dato == 'json':
            import json
            return json.loads(self.valor)
        else:
            return self.valor

    def resetear_a_default(self):
        """Resetea el valor a su valor por defecto."""
        self.valor = self.valor_default
        self.save()


class ConfiguracionHistorial(models.Model):
    """Historial de cambios en configuraciones del sistema.

    Registra todas las modificaciones realizadas a las configuraciones
    para auditoria y trazabilidad.
    """

    id = models.AutoField(primary_key=True)
    configuracion = models.ForeignKey(
        Configuracion,
        on_delete=models.CASCADE,
        related_name='historial',
        help_text='Configuracion modificada'
    )
    clave = models.CharField(
        max_length=100,
        db_index=True,
        help_text='Clave de la configuracion (desnormalizado para historico)'
    )
    valor_anterior = models.TextField(
        help_text='Valor antes del cambio'
    )
    valor_nuevo = models.TextField(
        help_text='Valor despues del cambio'
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modificaciones_configuracion',
        help_text='Usuario que realizo el cambio'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Fecha y hora del cambio'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='Direccion IP desde donde se realizo el cambio'
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        help_text='User agent del navegador'
    )

    class Meta:
        db_table = 'configuracion_historial'
        verbose_name = 'Historial de Configuracion'
        verbose_name_plural = 'Historial de Configuraciones'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['clave', '-timestamp']),
            models.Index(fields=['modificado_por', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.clave} - {self.timestamp}"
