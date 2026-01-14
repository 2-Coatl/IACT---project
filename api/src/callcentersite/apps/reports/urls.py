"""Rutas del dashboard."""

from django.urls import path

from .views import (
    DashboardCompartirView,
    DashboardExportarView,
    DashboardOverviewView,
    DashboardPersonalizarView,
)

app_name = "dashboard"

urlpatterns = [
    path("overview/", DashboardOverviewView.as_view(), name="overview"),
    path("exportar/", DashboardExportarView.as_view(), name="exportar"),
    path("personalizar/", DashboardPersonalizarView.as_view(), name="personalizar"),
    path("compartir/", DashboardCompartirView.as_view(), name="compartir"),
]
