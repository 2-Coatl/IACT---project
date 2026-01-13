"""Servicios para buzon interno (notifications)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from .models import InternalMessage

User = get_user_model()


class NotificationService:
    """Servicio para manejo de mensajes internos."""

    @staticmethod
    def enviar_mensaje(
        sender_id: int,
        recipient_id: int,
        subject: str,
        body: str,
        message_type: str = "info",
        priority: str = "medium",
        expires_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> InternalMessage:
        """
        Enviar mensaje interno a usuario.

        Args:
            sender_id: ID del usuario remitente
            recipient_id: ID del usuario destinatario
            subject: Asunto del mensaje
            body: Cuerpo del mensaje
            message_type: Tipo de mensaje (info, warning, alert, system)
            priority: Prioridad (low, medium, high, critical)
            expires_at: Fecha de expiracion (opcional)
            metadata: Metadata adicional (opcional)

        Returns:
            InternalMessage creado
        """
        sender = User.objects.get(id=sender_id)
        recipient = User.objects.get(id=recipient_id)

        mensaje = InternalMessage.objects.create(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            message_type=message_type,
            priority=priority,
            expires_at=expires_at,
            metadata=metadata or {},
            created_by_system=False,
        )

        return mensaje

    @staticmethod
    def crear_mensaje_sistema(
        recipient_id: int,
        subject: str,
        body: str,
        message_type: str = "system",
        priority: str = "medium",
        expires_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> InternalMessage:
        """
        Crear mensaje generado automaticamente por el sistema.

        Args:
            recipient_id: ID del usuario destinatario
            subject: Asunto del mensaje
            body: Cuerpo del mensaje
            message_type: Tipo de mensaje (por defecto: system)
            priority: Prioridad del mensaje
            expires_at: Fecha de expiracion (opcional)
            metadata: Metadata adicional (opcional)

        Returns:
            InternalMessage creado con created_by_system=True
        """
        recipient = User.objects.get(id=recipient_id)

        mensaje = InternalMessage.objects.create(
            sender=None,  # Mensajes del sistema no tienen remitente
            recipient=recipient,
            subject=subject,
            body=body,
            message_type=message_type,
            priority=priority,
            expires_at=expires_at,
            metadata=metadata or {},
            created_by_system=True,
        )

        return mensaje

    @staticmethod
    def listar_mensajes(
        user_id: int,
        is_read: bool | None = None,
        priority: str | None = None,
        message_type: str | None = None,
    ) -> list[InternalMessage]:
        """
        Listar mensajes recibidos por usuario con filtros opcionales.

        Args:
            user_id: ID del usuario
            is_read: Filtrar por leido/no leido
            priority: Filtrar por prioridad
            message_type: Filtrar por tipo de mensaje

        Returns:
            Lista de mensajes filtrados
        """
        queryset = InternalMessage.objects.filter(recipient_id=user_id)

        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)

        if priority:
            queryset = queryset.filter(priority=priority)

        if message_type:
            queryset = queryset.filter(message_type=message_type)

        return list(queryset.order_by("-created_at"))

    @staticmethod
    def marcar_como_leido(mensaje_id: int) -> InternalMessage:
        """
        Marcar mensaje como leido.

        Args:
            mensaje_id: ID del mensaje

        Returns:
            Mensaje actualizado
        """
        mensaje = InternalMessage.objects.get(id=mensaje_id)
        mensaje.mark_as_read()
        return mensaje

    @staticmethod
    def eliminar_mensaje(mensaje_id: int) -> None:
        """
        Eliminar mensaje.

        Args:
            mensaje_id: ID del mensaje a eliminar
        """
        InternalMessage.objects.filter(id=mensaje_id).delete()

    @staticmethod
    def contar_no_leidos(user_id: int) -> int:
        """
        Contar mensajes no leidos de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Cantidad de mensajes no leidos
        """
        return InternalMessage.objects.filter(
            recipient_id=user_id, is_read=False
        ).count()
