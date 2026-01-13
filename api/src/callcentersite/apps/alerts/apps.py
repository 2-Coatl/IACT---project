"""Configuración de la app de notificaciones."""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Configura el módulo de mensajería interna."""

    name = "callcentersite.apps.notifications"
    verbose_name = "Notificaciones"
