"""Generador PDF basado en reportlab."""

from __future__ import annotations

import tempfile

try:  # pragma: no cover - dependencia opcional
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except ImportError:  # pragma: no cover
    canvas = None
    A4 = None

from django.db.models import QuerySet

from .base import BaseReportGenerator


class PDFReportGenerator(BaseReportGenerator):
    """Genera un PDF simple con conteo de registros."""

    def generate(self, queryset: QuerySet, parameters: dict) -> str:  # type: ignore[override]
        if canvas is None or A4 is None:
            raise RuntimeError("reportlab no está instalado")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf = canvas.Canvas(tmp.name, pagesize=A4)
            pdf.drawString(100, 800, "Reporte IACT")
            pdf.drawString(100, 780, f"Registros: {queryset.count()}")
            pdf.showPage()
            pdf.save()
        return tmp.name
