"""Configuración de la app común."""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Configura componentes compartidos del monolito."""

    name = "callcentersite.apps.common"
    verbose_name = "Common"
