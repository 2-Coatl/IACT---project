"""Generador Excel basado en openpyxl."""

from __future__ import annotations

import tempfile

try:  # pragma: no cover - dependencia opcional
    from openpyxl import Workbook
except ImportError:  # pragma: no cover
    Workbook = None

from django.db.models import QuerySet

from .base import BaseReportGenerator


class ExcelReportGenerator(BaseReportGenerator):
    """Genera un archivo XLSX temporal."""

    def generate(self, queryset: QuerySet, parameters: dict) -> str:  # type: ignore[override]
        if Workbook is None:
            raise RuntimeError("openpyxl no está instalado")

        workbook = Workbook()
        sheet = workbook.active
        headers = [field.name for field in queryset.model._meta.fields]
        sheet.append(headers)
        for obj in queryset.iterator():
            sheet.append([getattr(obj, field) for field in headers])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
        return tmp.name
