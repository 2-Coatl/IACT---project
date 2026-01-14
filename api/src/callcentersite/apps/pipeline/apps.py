"""Configuración del módulo ETL."""

from django.apps import AppConfig


class ETLConfig(AppConfig):
    """Configura los componentes ETL."""

    name = "callcentersite.apps.etl"
    verbose_name = "ETL"
