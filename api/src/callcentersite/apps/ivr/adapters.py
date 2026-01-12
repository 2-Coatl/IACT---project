"""Adaptadores para acceder a la base de datos legacy."""

from __future__ import annotations

from datetime import datetime

from . import models


class IVRDataAdapter:
    """Encapsula la lectura de datos de la BD IVR en modo read-only."""

    def get_calls(self, start_date: datetime, end_date: datetime):
        return models.IVRCall.objects.using("ivr_readonly").filter(
            call_date__range=(start_date, end_date)
        )

    def get_client(self, client_id: str):
        return models.IVRClient.objects.using("ivr_readonly").get(client_id=client_id)
