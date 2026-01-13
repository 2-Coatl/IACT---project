"""Modelo de mensajería interna."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class InternalMessageQuerySet(models.QuerySet):
    """QuerySet que mapea alias de campos usados por legacy tests."""

    @staticmethod
    def _normalize_kwargs(kwargs: dict) -> dict:
        normalized = dict(kwargs)
        if "user_id" in normalized:
            normalized["recipient_id"] = normalized.pop("user_id")
        if "user" in normalized:
            normalized["recipient"] = normalized.pop("user")
        return normalized

    def filter(self, *args, **kwargs):  # type: ignore[override]
        return super().filter(*args, **self._normalize_kwargs(kwargs))

    def get(self, *args, **kwargs):  # type: ignore[override]
        return super().get(*args, **self._normalize_kwargs(kwargs))

    def create(self, **kwargs):  # type: ignore[override]
        return super().create(**self._normalize_kwargs(kwargs))


class InternalMessage(models.Model):
    """Mensaje interno enviado a usuarios del sistema."""

    objects = InternalMessageQuerySet.as_manager()

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="sent_messages",
        null=True,
        blank=True,
    )
    subject = models.CharField("asunto", max_length=255)
    body = models.TextField("cuerpo")
    message_type = models.CharField(
        "tipo",
        max_length=20,
        choices=[
            ("info", "Información"),
            ("warning", "Advertencia"),
            ("alert", "Alerta"),
            ("system", "Sistema"),
        ],
    )
    priority = models.CharField(
        "prioridad",
        max_length=20,
        choices=[
            ("low", "Baja"),
            ("medium", "Media"),
            ("high", "Alta"),
            ("critical", "Crítica"),
        ],
    )
    is_read = models.BooleanField("leído", default=False)
    read_at = models.DateTimeField("fecha lectura", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by_system = models.BooleanField(
        "creado por sistema",
        default=False,
        help_text="Indica si el mensaje fue generado automáticamente por el sistema"
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "mensaje interno"
        verbose_name_plural = "mensajes internos"
        ordering = ("-created_at",)

    @property
    def user_id(self) -> int:
        """Retorna el ID del destinatario para compatibilidad con tests."""
        return self.recipient.id

    def mark_as_read(self) -> None:
        """Marca el mensaje como leído."""

        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
