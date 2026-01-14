"""Configuracion de la app configuration."""

from django.apps import AppConfig


class ConfigurationConfig(AppConfig):
    """Configuracion de la app de configuracion del sistema."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'callcentersite.apps.configuration'
    verbose_name = 'Configuracion del Sistema'
