"""Modelos de autenticación y seguridad."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class SecurityQuestion(models.Model):
    """Preguntas de seguridad asociadas a un usuario."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security_questions",
    )
    question = models.TextField("pregunta")
    answer_hash = models.CharField("respuesta cifrada", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "pregunta de seguridad"
        verbose_name_plural = "preguntas de seguridad"
        unique_together = ("user", "question")

    def set_answer(self, answer: str) -> None:
        """Guarda la respuesta cifrada."""

        self.answer_hash = make_password(answer)
        self.save(update_fields=["answer_hash"])

    def verify_answer(self, answer: str) -> bool:
        """Verifica si la respuesta proporcionada coincide."""

        return check_password(answer, self.answer_hash)


class LoginAttempt(models.Model):
    """Intentos de inicio de sesión para auditoría."""

    ip_address = models.GenericIPAddressField("IP")
    username = models.CharField("usuario", max_length=150)
    success = models.BooleanField("éxito")
    timestamp = models.DateTimeField("fecha", default=timezone.now)
    user_agent = models.TextField("user agent")
    reason = models.CharField("razón", max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "intento de inicio de sesión"
        verbose_name_plural = "intentos de inicio de sesión"
        ordering = ("-timestamp",)
