"""Carga de datos transformados."""

from __future__ import annotations

from typing import Iterable

from django.db import transaction

from callcentersite.apps.analytics.models import CallAnalytics


class AnalyticsDataLoader:
    """Persistencia de datos analíticos."""

    def load(self, transformed_calls: Iterable[CallAnalytics]) -> None:
        with transaction.atomic():
            CallAnalytics.objects.bulk_create(
                list(transformed_calls), ignore_conflicts=True
            )
