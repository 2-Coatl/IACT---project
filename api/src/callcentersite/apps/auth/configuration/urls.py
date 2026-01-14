"""URLs para API REST de configuraciones."""

from django.urls import path

from .views import (
    ConfiguracionAuditoriaView,
    ConfiguracionEditarView,
    ConfiguracionExportarView,
    ConfiguracionImportarView,
    ConfiguracionListView,
    ConfiguracionHistorialView,
    ConfiguracionRestaurarView,
)

app_name = "configuration"

urlpatterns = [
    path("", ConfiguracionListView.as_view(), name="list"),
    path("<str:clave>/", ConfiguracionEditarView.as_view(), name="editar"),
    path("<str:clave>/historial/", ConfiguracionHistorialView.as_view(), name="historial"),
    path("exportar/", ConfiguracionExportarView.as_view(), name="exportar"),
    path("importar/", ConfiguracionImportarView.as_view(), name="importar"),
    path("auditar/", ConfiguracionAuditoriaView.as_view(), name="auditar"),
    path("<str:clave>/restaurar/", ConfiguracionRestaurarView.as_view(), name="restaurar"),
]
