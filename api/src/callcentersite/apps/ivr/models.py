"""Modelos mapeados a la base de datos legacy del IVR."""

from __future__ import annotations

from django.db import models


class IVRCall(models.Model):
    """Representa un registro de llamada en la BD legacy."""

    call_id = models.CharField(max_length=50, primary_key=True)
    client_id = models.CharField(max_length=100)
    call_date = models.DateTimeField()
    duration_seconds = models.IntegerField()

    class Meta:
        managed = False
        db_table = "calls"
        app_label = "ivr"


class IVRClient(models.Model):
    """Representa un cliente dentro de la BD legacy."""

    client_id = models.CharField(max_length=100, primary_key=True)
    full_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "clients"
        app_label = "ivr"
