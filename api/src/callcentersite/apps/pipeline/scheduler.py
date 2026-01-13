"""Configuración del scheduler ETL."""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

from .jobs import run_etl

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)


@scheduler.scheduled_job("interval", hours=settings.ETL_FREQUENCY_HOURS)
def scheduled_etl() -> None:
    """Ejecuta el proceso ETL según frecuencia configurada."""

    logger.info("Iniciando job ETL programado")
    run_etl()
