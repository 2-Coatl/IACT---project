"""Widgets de dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class Widget:
    """Representación simple de un widget."""

    type: str
    title: str
    value: str
    change: str
    period: str


WIDGET_REGISTRY: Dict[str, Widget] = {
    "total_calls": Widget("total_calls", "Total de llamadas", "0", "0%", "Hoy"),
    "avg_duration": Widget("avg_duration", "Duración promedio", "0", "0%", "Hoy"),
}
