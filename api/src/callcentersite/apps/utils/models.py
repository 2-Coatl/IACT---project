"""Modelos compartidos."""

from __future__ import annotations

from django.db import models


class TimeStampedModel(models.Model):
    """Modelo abstracto con fechas de creación y actualización."""

    created_at = models.DateTimeField("fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("fecha de actualización", auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Modelo abstracto con soft delete controlado por bandera."""

    is_deleted = models.BooleanField("eliminado", default=False)
    deleted_at = models.DateTimeField("fecha de eliminación", blank=True, null=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """Base para modelos de negocio con campos comunes."""

    class Meta:
        abstract = True
