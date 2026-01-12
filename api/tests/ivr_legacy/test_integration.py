"""Tests de integración para ivr con base de datos legacy."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import connection, connections
from unittest.mock import Mock, patch

from callcentersite.apps.ivr.adapters import IVRDataAdapter
from callcentersite.apps.ivr.models import IVRCall, IVRClient


@pytest.mark.django_db(databases=["default", "ivr_readonly"])
class TestIVRDatabaseConnection:
    """Tests de conexión a la base de datos legacy IVR."""

    def test_ivr_readonly_database_configured(self, settings):
        """Test que la base de datos ivr_readonly está configurada."""
        assert "ivr_readonly" in settings.DATABASES

    def test_ivr_readonly_database_accessible(self):
        """Test que la base de datos ivr_readonly es accesible."""
        # Verificar que la conexión existe
        assert "ivr_readonly" in connections

        # Intentar obtener conexión (no necesariamente conectarse realmente)
        ivr_conn = connections["ivr_readonly"]
        assert ivr_conn is not None

    @pytest.mark.skip(reason="Requiere BD IVR real disponible")
    def test_ivr_database_tables_exist(self):
        """Test que las tablas 'calls' y 'clients' existen en BD legacy."""
        # Este test solo funciona si la BD IVR legacy está realmente disponible
        with connections["ivr_readonly"].cursor() as cursor:
            # Verificar tabla calls
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_name = 'calls'"
            )
            calls_exists = cursor.fetchone()[0] > 0
            assert calls_exists

            # Verificar tabla clients
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_name = 'clients'"
            )
            clients_exists = cursor.fetchone()[0] > 0
            assert clients_exists


@pytest.mark.django_db(databases=["default", "ivr_readonly"])
class TestIVRDataAdapterIntegration:
    """Tests de integración para IVRDataAdapter."""

    @pytest.fixture
    def adapter(self):
        """Fixture que retorna una instancia de IVRDataAdapter."""
        return IVRDataAdapter()

    @pytest.mark.skip(reason="Requiere BD IVR con datos de prueba")
    def test_get_calls_integration_with_real_data(self, adapter):
        """Test get_calls con datos reales en BD legacy."""
        # Este test requiere BD IVR con datos de prueba poblados
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()

        calls = adapter.get_calls(start_date, end_date)

        # Verificar que retorna un queryset
        assert hasattr(calls, "count")

        # Verificar que todas las llamadas están en el rango
        for call in calls:
            assert start_date <= call.call_date <= end_date

    @pytest.mark.skip(reason="Requiere BD IVR con datos de prueba")
    def test_get_client_integration_with_real_data(self, adapter):
        """Test get_client con datos reales en BD legacy."""
        # Este test requiere un cliente conocido en BD de prueba
        client_id = "TEST-CLIENT-001"

        client = adapter.get_client(client_id)

        assert client.client_id == client_id
        assert client.full_name is not None
        assert len(client.full_name) > 0

    @patch("callcentersite.apps.ivr.models.IVRCall.objects")
    def test_get_calls_handles_empty_results(self, mock_ivr_call_objects, adapter):
        """Test get_calls maneja correctamente resultados vacíos."""
        start_date = timezone.now() - timedelta(days=1)
        end_date = timezone.now()

        # Configurar mock para retornar lista vacía
        mock_using = Mock()
        mock_ivr_call_objects.using.return_value = mock_using
        mock_using.filter.return_value = []

        calls = adapter.get_calls(start_date, end_date)

        # Verificar que retorna lista vacía (no None, no error)
        assert calls is not None
        assert len(calls) == 0

    @patch("callcentersite.apps.ivr.models.IVRClient.objects")
    def test_get_client_raises_does_not_exist(self, mock_ivr_client_objects, adapter):
        """Test get_client levanta excepción si cliente no existe."""
        from django.core.exceptions import ObjectDoesNotExist

        client_id = "NONEXISTENT-CLIENT"

        # Configurar mock para levantar DoesNotExist
        mock_using = Mock()
        mock_ivr_client_objects.using.return_value = mock_using
        mock_using.get.side_effect = IVRClient.DoesNotExist

        with pytest.raises(IVRClient.DoesNotExist):
            adapter.get_client(client_id)


@pytest.mark.django_db(databases=["default", "ivr_readonly"])
class TestIVRReadOnlyConstraint:
    """Tests para verificar que la BD IVR es realmente read-only."""

    @pytest.mark.skip(reason="Requiere BD IVR real configurada como read-only")
    def test_cannot_insert_into_ivr_calls(self):
        """Test que no se puede insertar en tabla calls de BD legacy."""
        call = IVRCall(
            call_id="CALL-NEW-001",
            client_id="CLIENT-001",
            call_date=timezone.now(),
            duration_seconds=60,
        )

        # Intentar guardar debe fallar porque managed=False y BD es read-only
        with pytest.raises(Exception):  # Puede ser OperationalError o similar
            call.save(using="ivr_readonly")

    @pytest.mark.skip(reason="Requiere BD IVR real configurada como read-only")
    def test_cannot_delete_from_ivr_calls(self):
        """Test que no se puede eliminar de tabla calls de BD legacy."""
        # Asumiendo que existe una llamada con este ID
        call_id = "EXISTING-CALL-001"

        with pytest.raises(Exception):
            IVRCall.objects.using("ivr_readonly").filter(call_id=call_id).delete()

    @pytest.mark.skip(reason="Requiere BD IVR real configurada como read-only")
    def test_cannot_update_ivr_calls(self):
        """Test que no se puede actualizar registros en tabla calls."""
        call_id = "EXISTING-CALL-001"

        with pytest.raises(Exception):
            IVRCall.objects.using("ivr_readonly").filter(call_id=call_id).update(
                duration_seconds=999
            )


@pytest.mark.django_db(databases=["default", "ivr_readonly"])
class TestIVRDataConsistency:
    """Tests para verificar consistencia de datos en BD legacy."""

    @pytest.mark.skip(reason="Requiere BD IVR con datos de prueba")
    def test_all_calls_have_valid_client_ids(self):
        """Test que todas las llamadas tienen client_id válidos."""
        # Obtener todas las llamadas recientes
        start_date = timezone.now() - timedelta(days=30)
        end_date = timezone.now()

        calls = IVRCall.objects.using("ivr_readonly").filter(
            call_date__range=(start_date, end_date)
        )

        for call in calls:
            # Verificar que client_id no es None ni vacío
            assert call.client_id is not None
            assert len(call.client_id) > 0

    @pytest.mark.skip(reason="Requiere BD IVR con datos de prueba")
    def test_call_durations_are_reasonable(self):
        """Test que las duraciones de llamadas son razonables."""
        calls = IVRCall.objects.using("ivr_readonly").all()[:100]  # Muestra

        for call in calls:
            # Duración debe ser >= 0
            assert call.duration_seconds >= 0
            # Duración razonable (menos de 24 horas = 86400 segundos)
            assert call.duration_seconds < 86400


# Fixture para tests de integración con datos mockeados
@pytest.fixture
def mock_ivr_call_data():
    """Fixture que retorna datos de prueba de llamadas IVR."""
    return [
        {
            "call_id": "CALL-TEST-001",
            "client_id": "CLIENT-TEST-001",
            "call_date": timezone.now() - timedelta(days=1),
            "duration_seconds": 120,
        },
        {
            "call_id": "CALL-TEST-002",
            "client_id": "CLIENT-TEST-002",
            "call_date": timezone.now() - timedelta(days=2),
            "duration_seconds": 90,
        },
        {
            "call_id": "CALL-TEST-003",
            "client_id": "CLIENT-TEST-001",  # Mismo cliente
            "call_date": timezone.now() - timedelta(days=3),
            "duration_seconds": 150,
        },
    ]


@pytest.fixture
def mock_ivr_client_data():
    """Fixture que retorna datos de prueba de clientes IVR."""
    return [
        {
            "client_id": "CLIENT-TEST-001",
            "full_name": "Juan Pérez Test",
        },
        {
            "client_id": "CLIENT-TEST-002",
            "full_name": "María García Test",
        },
    ]
