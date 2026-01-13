"""Configuración de la app reportes."""

from django.apps import AppConfig


class ReportesConfig(AppConfig):
    """Configuración de la app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'callcentersite.apps.reportes'
    verbose_name = 'Sistema de Reportes'
