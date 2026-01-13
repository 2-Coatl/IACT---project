"""
Configuracion de la app access.

Sistema de Permisos Granular - Prioridad 1
"""

from django.apps import AppConfig


class AccessConfig(AppConfig):
    """Configuracion de la app access."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'callcentersite.apps.access'
    verbose_name = 'Sistema de Permisos Granular'

    def ready(self):
        """
        Ejecutado cuando la app esta lista.

        Aqui se pueden registrar signals, cargar datos iniciales, etc.
        """
        # Importar signals si existen
        # from . import signals  # noqa: F401
        pass
