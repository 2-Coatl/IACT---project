"""Generador CSV."""

from __future__ import annotations

import csv
import tempfile

from django.db.models import QuerySet

from .base import BaseReportGenerator


class CSVReportGenerator(BaseReportGenerator):
    """Genera un archivo CSV temporal."""

    def generate(self, queryset: QuerySet, parameters: dict) -> str:  # type: ignore[override]
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".csv", mode="w", newline=""
        ) as tmp:
            writer = csv.writer(tmp)
            model = queryset.model
            headers = [field.name for field in model._meta.fields]
            writer.writerow(headers)
            for obj in queryset.iterator():
                writer.writerow([getattr(obj, field) for field in headers])
        return tmp.name
