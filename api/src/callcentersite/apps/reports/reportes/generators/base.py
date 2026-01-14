"""Clases base para generación de reportes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from django.db.models import QuerySet


class BaseReportGenerator(ABC):
    """Interfaz para generadores de reportes."""

    @abstractmethod
    def generate(self, queryset: QuerySet, parameters: dict) -> str:
        """Genera un archivo y retorna la ruta resultante."""


class InlineGenerator(BaseReportGenerator):
    """Generador simple que devuelve datos en memoria."""

    def generate(self, queryset: QuerySet, parameters: dict) -> str:  # type: ignore[override]
        return ""
