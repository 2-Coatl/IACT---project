"""Configuración de la app ivr."""

from django.apps import AppConfig


class IVRLegacyConfig(AppConfig):
    """App que representa datos read-only del IVR."""

    name = "callcentersite.apps.ivr"
    verbose_name = "IVR"
