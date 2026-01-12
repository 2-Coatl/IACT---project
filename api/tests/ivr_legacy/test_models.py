"""Tests para los modelos de ivr."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from django.utils import timezone

from callcentersite.apps.ivr.models import IVRCall, IVRClient


@pytest.mark.django_db(databases=["default", "ivr_readonly"])
class TestIVRCallModel:
    """Tests para el modelo IVRCall."""

    def test_ivr_call_creation(self):
        """Test que se puede crear una instancia de IVRCall."""
        call = IVRCall(
            call_id="CALL-001",
            client_id="CLIENT-001",
            call_date=timezone.now(),
            duration_seconds=120,
        )
        assert call.call_id == "CALL-001"
        assert call.client_id == "CLIENT-001"
        assert call.duration_seconds == 120

    def test_ivr_call_str_representation(self):
        """Test representación string de IVRCall."""
        call = IVRCall(
            call_id="CALL-002",
            client_id="CLIENT-002",
            call_date=timezone.now(),
            duration_seconds=90,
        )
        # Verificar que el objeto se puede convertir a string sin errores
        str_repr = str(call)
        assert "IVRCall" in str_repr or "CALL-002" in str_repr

    def test_ivr_call_meta_configuration(self):
        """Test configuración del modelo (managed=False, db_table, etc.)."""
        assert IVRCall._meta.managed is False
        assert IVRCall._meta.db_table == "calls"
        assert IVRCall._meta.app_label == "ivr"

    def test_ivr_call_primary_key(self):
        """Test que call_id es la primary key."""
        pk_field = IVRCall._meta.pk
        assert pk_field.name == "call_id"

    def test_ivr_call_fields(self):
        """Test que todos los campos esperados existen."""
        field_names = [f.name for f in IVRCall._meta.get_fields()]
        assert "call_id" in field_names
        assert "client_id" in field_names
        assert "call_date" in field_names
        assert "duration_seconds" in field_names

    def test_ivr_call_duration_positive(self):
        """Test que duration_seconds puede ser positivo."""
        call = IVRCall(
            call_id="CALL-003",
            client_id="CLIENT-003",
            call_date=timezone.now(),
            duration_seconds=300,
        )
        assert call.duration_seconds > 0

    def test_ivr_call_duration_zero(self):
        """Test que duration_seconds puede ser cero (llamada sin contestar)."""
        call = IVRCall(
            call_id="CALL-004",
            client_id="CLIENT-004",
            call_date=timezone.now(),
            duration_seconds=0,
        )
        assert call.duration_seconds == 0


@pytest.mark.django_db(databases=["default", "ivr_readonly"])
class TestIVRClientModel:
    """Tests para el modelo IVRClient."""

    def test_ivr_client_creation(self):
        """Test que se puede crear una instancia de IVRClient."""
        client = IVRClient(
            client_id="CLIENT-001",
            full_name="Juan Pérez",
        )
        assert client.client_id == "CLIENT-001"
        assert client.full_name == "Juan Pérez"

    def test_ivr_client_str_representation(self):
        """Test representación string de IVRClient."""
        client = IVRClient(
            client_id="CLIENT-002",
            full_name="María García",
        )
        str_repr = str(client)
        assert "IVRClient" in str_repr or "CLIENT-002" in str_repr or "María García" in str_repr

    def test_ivr_client_meta_configuration(self):
        """Test configuración del modelo (managed=False, db_table, etc.)."""
        assert IVRClient._meta.managed is False
        assert IVRClient._meta.db_table == "clients"
        assert IVRClient._meta.app_label == "ivr"

    def test_ivr_client_primary_key(self):
        """Test que client_id es la primary key."""
        pk_field = IVRClient._meta.pk
        assert pk_field.name == "client_id"

    def test_ivr_client_fields(self):
        """Test que todos los campos esperados existen."""
        field_names = [f.name for f in IVRClient._meta.get_fields()]
        assert "client_id" in field_names
        assert "full_name" in field_names

    def test_ivr_client_full_name_length(self):
        """Test que full_name puede almacenar nombres largos."""
        long_name = "A" * 255  # Máximo según modelo
        client = IVRClient(
            client_id="CLIENT-003",
            full_name=long_name,
        )
        assert len(client.full_name) == 255


@pytest.mark.django_db(databases=["default", "ivr_readonly"])
class TestIVRModelsRelationship:
    """Tests para relaciones entre modelos de IVR."""

    def test_call_and_client_same_id(self):
        """Test que call y client pueden compartir client_id conceptualmente."""
        client_id = "CLIENT-SHARED-001"

        client = IVRClient(
            client_id=client_id,
            full_name="Cliente Compartido",
        )

        call = IVRCall(
            call_id="CALL-SHARED-001",
            client_id=client_id,
            call_date=timezone.now(),
            duration_seconds=60,
        )

        # Verificar que el client_id coincide
        assert call.client_id == client.client_id
