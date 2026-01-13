"""Extractores de datos."""

from __future__ import annotations

from datetime import datetime

from callcentersite.apps.ivr.adapters import IVRDataAdapter


class IVRDataExtractor:
    """Extrae llamadas desde la BD IVR."""

    def __init__(self) -> None:
        self.adapter = IVRDataAdapter()

    def extract_calls(self, start_date: datetime, end_date: datetime):
        return self.adapter.get_calls(start_date, end_date)
