"""Funciones utilitarias compartidas."""

from __future__ import annotations

from typing import Any, Dict


def merge_metadata(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    """Combina diccionarios de metadatos priorizando valores adicionales."""

    result = {**base}
    result.update(extra)
    return result
