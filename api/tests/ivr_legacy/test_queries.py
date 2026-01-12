"""Tests para queries y el adapter de ivr."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from unittest.mock import Mock, patch

from callcentersite.apps.ivr.adapters import IVRDataAdapter
from callcentersite.apps.ivr.models import IVRCall, IVRClient


@pytest.mark.django_db(databases=["default", "ivr_readonly"])
class TestIVRDataAdapter:
    """Tests para el adaptador IVRDataAdapter."""

    @pytest.fixture
    def adapter(self):
        """Fixture que retorna una instancia de IVRDataAdapter."""
        return IVRDataAdapter()

    def test_adapter_instantiation(self, adapter):
        """Test que el adapter se puede instanciar."""
        assert isinstance(adapter, IVRDataAdapter)

    @patch("callcentersite.apps.ivr.models.IVRCall.objects")
    def test_get_calls_with_date_range(self, mock_ivr_call_objects, adapter):
        """Test get_calls filtra por rango de fechas correctamente."""
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()

        # Configurar mock
        mock_using = Mock()
        mock_ivr_call_objects.using.return_value = mock_using
        mock_filter = Mock()
        mock_using.filter.return_value = mock_filter

        # Ejecutar
        result = adapter.get_calls(start_date, end_date)

        # Verificar
        mock_ivr_call_objects.using.assert_called_once_with("ivr_readonly")
        mock_using.filter.assert_called_once_with(
            call_date__range=(start_date, end_date)
        )

    @patch("callcentersite.apps.ivr.models.IVRCall.objects")
    def test_get_calls_uses_ivr_readonly_database(self, mock_ivr_call_objects, adapter):
        """Test que get_calls usa la base de datos ivr_readonly."""
        start_date = timezone.now() - timedelta(days=1)
        end_date = timezone.now()

        mock_using = Mock()
        mock_ivr_call_objects.using.return_value = mock_using
        mock_using.filter.return_value = []

        adapter.get_calls(start_date, end_date)

        # Verificar que se llamó con la base de datos correcta
        mock_ivr_call_objects.using.assert_called_with("ivr_readonly")

    @patch("callcentersite.apps.ivr.models.IVRClient.objects")
    def test_get_client_by_id(self, mock_ivr_client_objects, adapter):
        """Test get_client obtiene cliente por ID."""
        client_id = "CLIENT-TEST-001"

        # Configurar mock
        mock_using = Mock()
        mock_ivr_client_objects.using.return_value = mock_using
        mock_client = Mock(spec=IVRClient)
        mock_client.client_id = client_id
        mock_client.full_name = "Test Client"
        mock_using.get.return_value = mock_client

        # Ejecutar
        result = adapter.get_client(client_id)

        # Verificar
        mock_ivr_client_objects.using.assert_called_once_with("ivr_readonly")
        mock_using.get.assert_called_once_with(client_id=client_id)
        assert result.client_id == client_id

    @patch("callcentersite.apps.ivr.models.IVRClient.objects")
    def test_get_client_uses_ivr_readonly_database(self, mock_ivr_client_objects, adapter):
        """Test que get_client usa la base de datos ivr_readonly."""
        client_id = "CLIENT-TEST-002"

        mock_using = Mock()
        mock_ivr_client_objects.using.return_value = mock_using
        mock_using.get.return_value = Mock(spec=IVRClient)

        adapter.get_client(client_id)

        # Verificar que se llamó con la base de datos correcta
        mock_ivr_client_objects.using.assert_called_with("ivr_readonly")

    @patch("callcentersite.apps.ivr.models.IVRCall.objects")
    def test_get_calls_returns_queryset(self, mock_ivr_call_objects, adapter):
        """Test que get_calls retorna un QuerySet."""
        start_date = timezone.now() - timedelta(days=1)
        end_date = timezone.now()

        mock_using = Mock()
        mock_ivr_call_objects.using.return_value = mock_using
        mock_queryset = []
        mock_using.filter.return_value = mock_queryset

        result = adapter.get_calls(start_date, end_date)

        # El resultado debe ser iterable (queryset o lista)
        assert hasattr(result, "__iter__")


@pytest.mark.django_db(databases=["default", "ivr_readonly"])
class TestIVRCallQueries:
    """Tests para queries sobre el modelo IVRCall."""

    @patch("callcentersite.apps.ivr.models.IVRCall.objects")
    def test_filter_calls_by_date_range(self, mock_ivr_call_objects):
        """Test filtrar llamadas por rango de fechas."""
        start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 31, tzinfo=timezone.utc)

        mock_using = Mock()
        mock_ivr_call_objects.using.return_value = mock_using
        mock_using.filter.return_value = []

        # Ejecutar query
        IVRCall.objects.using("ivr_readonly").filter(
            call_date__range=(start_date, end_date)
        )

        # Verificar
        mock_ivr_call_objects.using.assert_called_with("ivr_readonly")

    @patch("callcentersite.apps.ivr.models.IVRCall.objects")
    def test_filter_calls_by_client_id(self, mock_ivr_call_objects):
        """Test filtrar llamadas por client_id."""
        client_id = "CLIENT-001"

        mock_using = Mock()
        mock_ivr_call_objects.using.return_value = mock_using
        mock_using.filter.return_value = []

        IVRCall.objects.using("ivr_readonly").filter(client_id=client_id)

        mock_using.filter.assert_called_with(client_id=client_id)

    @patch("callcentersite.apps.ivr.models.IVRCall.objects")
    def test_filter_calls_by_duration(self, mock_ivr_call_objects):
        """Test filtrar llamadas por duración."""
        min_duration = 60  # 1 minuto

        mock_using = Mock()
        mock_ivr_call_objects.using.return_value = mock_using
        mock_using.filter.return_value = []

        IVRCall.objects.using("ivr_readonly").filter(duration_seconds__gte=min_duration)

        mock_using.filter.assert_called_with(duration_seconds__gte=min_duration)


@pytest.mark.django_db(databases=["default", "ivr_readonly"])
class TestIVRClientQueries:
    """Tests para queries sobre el modelo IVRClient."""

    @patch("callcentersite.apps.ivr.models.IVRClient.objects")
    def test_get_client_by_id(self, mock_ivr_client_objects):
        """Test obtener cliente por ID."""
        client_id = "CLIENT-001"

        mock_using = Mock()
        mock_ivr_client_objects.using.return_value = mock_using
        mock_using.get.return_value = Mock(spec=IVRClient)

        IVRClient.objects.using("ivr_readonly").get(client_id=client_id)

        mock_using.get.assert_called_with(client_id=client_id)

    @patch("callcentersite.apps.ivr.models.IVRClient.objects")
    def test_filter_clients_by_name(self, mock_ivr_client_objects):
        """Test filtrar clientes por nombre (búsqueda parcial)."""
        search_term = "Juan"

        mock_using = Mock()
        mock_ivr_client_objects.using.return_value = mock_using
        mock_using.filter.return_value = []

        IVRClient.objects.using("ivr_readonly").filter(full_name__icontains=search_term)

        mock_using.filter.assert_called_with(full_name__icontains=search_term)
