"""URLs para reportes IVR."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExportarReporteViewSet,
    ReporteClientesUnicosViewSet,
    ReporteLlamadasDiaViewSet,
    ReporteMenuProblemasViewSet,
    ReporteTransferenciasViewSet,
    ReporteTrimestralViewSet,
)

router = DefaultRouter()
router.register(r"trimestral", ReporteTrimestralViewSet, basename="reporte-trimestral")
router.register(
    r"transferencias", ReporteTransferenciasViewSet, basename="reporte-transferencias"
)
router.register(
    r"menus-problematicos",
    ReporteMenuProblemasViewSet,
    basename="reporte-menus-problematicos",
)
router.register(
    r"llamadas-dia", ReporteLlamadasDiaViewSet, basename="reporte-llamadas-dia"
)
router.register(
    r"clientes-unicos",
    ReporteClientesUnicosViewSet,
    basename="reporte-clientes-unicos",
)
router.register(r"exportar", ExportarReporteViewSet, basename="exportar-reporte")

urlpatterns = [
    path("", include(router.urls)),
]
