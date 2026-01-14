"""Jobs ETL."""

from __future__ import annotations

import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .extractors import IVRDataExtractor
from .loaders import AnalyticsDataLoader
from .transformers import CallDataTransformer

logger = logging.getLogger(__name__)


def run_etl() -> None:
    """Ejecuta el flujo ETL completo."""

    end = timezone.now()
    start = end - timedelta(hours=getattr(settings, "ETL_FREQUENCY_HOURS", 6))

    extractor = IVRDataExtractor()
    raw_calls = extractor.extract_calls(start, end)

    transformer = CallDataTransformer()
    transformed = transformer.transform(raw_calls)

    loader = AnalyticsDataLoader()
    loader.load(transformed)

    logger.info("ETL finalizado", extra={"registros": len(transformed)})
