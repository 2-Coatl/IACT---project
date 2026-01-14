"""Modelos del dashboard."""

from django.conf import settings
from django.db import models


class DashboardConfiguracion(models.Model):
    """Configuracion personalizada de dashboard por usuario.

    Almacena las preferencias de widgets y visualizacion
    de cada usuario para su dashboard personalizado.
    """

    id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_configuracion',
        help_text='Usuario dueno de la configuracion'
    )
    configuracion = models.JSONField(
        default=dict,
        help_text='Configuracion de widgets y layout en formato JSON'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Fecha de ultima actualizacion'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creacion'
    )

    class Meta:
        db_table = 'dashboard_configuracion'
        verbose_name = 'Configuracion de Dashboard'
        verbose_name_plural = 'Configuraciones de Dashboards'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Dashboard de {self.usuario.email}"
