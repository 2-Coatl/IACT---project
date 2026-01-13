"""Tareas programadas para autenticación y sesiones."""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from callcentersite.apps.audit.models import AuditLog
from callcentersite.apps.notifications.models import InternalMessage
from callcentersite.apps.users.models import UserSession

INACTIVITY_TIMEOUT_MINUTES = 30


def close_inactive_sessions() -> dict:
    """Cierra sesiones inactivas y registra auditoría y notificaciones."""

    threshold = timezone.now() - timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES)
    inactive_sessions = (
        UserSession.objects.filter(is_active=True, last_activity_at__lte=threshold)
        .select_related('user')
    )

    closed_sessions = 0

    for session in inactive_sessions:
        session.close(reason='INACTIVITY_TIMEOUT')
        closed_sessions += 1

        AuditLog.objects.create(
            user=session.user,
            event_type='SESSION_TIMEOUT',
            result='SUCCESS',
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            details={
                'reason': 'INACTIVITY_TIMEOUT',
                'session_key': session.session_key,
                'closed_at': session.logged_out_at.isoformat() if session.logged_out_at else None,
            },
        )

        InternalMessage.objects.create(
            recipient=session.user,
            sender=None,
            subject='Sesión cerrada por inactividad',
            body='Tu sesión fue cerrada después de 30 minutos de inactividad.',
            message_type='system',
            priority='medium',
            created_by_system=True,
            metadata={'session_key': session.session_key},
        )

    return {
        'closed_sessions': closed_sessions,
        'threshold_minutes': INACTIVITY_TIMEOUT_MINUTES,
    }
