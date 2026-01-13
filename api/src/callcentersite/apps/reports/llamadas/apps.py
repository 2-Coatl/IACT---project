"""Django app configuration para Llamadas."""

from django.apps import AppConfig


class LlamadasConfig(AppConfig):
    """Configuracion de la app Llamadas."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'callcentersite.apps.llamadas'
    verbose_name = 'Llamadas'
