"""Transformadores de datos."""

from __future__ import annotations

from typing import Iterable, List

from callcentersite.apps.analytics.models import CallAnalytics


class CallDataTransformer:
    """Normaliza los datos provenientes del IVR."""

    def transform(self, raw_calls: Iterable) -> List[CallAnalytics]:
        cleaned: List[CallAnalytics] = []
        for call in raw_calls:
            cleaned.append(
                CallAnalytics(
                    call_id=call.call_id,
                    client_id=call.client_id,
                    call_date=call.call_date,
                    duration_seconds=getattr(call, "duration_seconds", 0),
                    call_type=getattr(call, "call_type", "unknown"),
                    result=getattr(call, "result", "unknown"),
                    center_id=getattr(call, "center_id", 0),
                    service_id=getattr(call, "service_id", 0),
                    agent_id=getattr(call, "agent_id", None),
                    queue_time_seconds=getattr(call, "queue_time_seconds", 0),
                    talk_time_seconds=getattr(call, "talk_time_seconds", 0),
                    hold_time_seconds=getattr(call, "hold_time_seconds", 0),
                    transfer_count=getattr(call, "transfer_count", 0),
                    satisfaction_score=getattr(call, "satisfaction_score", None),
                    metadata=getattr(call, "metadata", {}),
                )
            )
        return cleaned
