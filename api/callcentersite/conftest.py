"""
Pytest fixtures globales - IACT Call Center System.

Fixtures compartidos por todos los tests.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """
    API Client para tests REST.
    
    Returns:
        APIClient: Cliente DRF
    
    Usage:
        def test_endpoint(api_client):
            response = api_client.get('/api/v1/calls/')
            assert response.status_code == 200
    """
    return APIClient()


@pytest.fixture
def authenticated_client(db, api_client):
    """
    API Client autenticado.
    
    Returns:
        tuple: (APIClient, User)
    
    Usage:
        def test_protected(authenticated_client):
            client, user = authenticated_client
            response = client.get('/api/v1/protected/')
            assert response.status_code == 200
    """
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def admin_client(db, api_client):
    """
    API Client autenticado como admin.
    
    Returns:
        tuple: (APIClient, User)
    """
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def sample_call_data():
    """
    Datos sample para CallRecord.
    
    Returns:
        dict: Datos llamada
    
    Usage:
        def test_create_call(sample_call_data):
            call = CallRecord.objects.create(**sample_call_data)
            assert call.total_llamadas == 100
    """
    return {
        'fecha': '2024-01-15',
        'telefono': '5551234567',
        'servicio_800': '8001234567',
        'total_llamadas': 100,
        'llamadas_contestadas': 85,
        'llamadas_abandonadas': 15,
    }


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    """
    Override MEDIA_ROOT para tests.
    
    Evita crear archivos en media/ real.
    """
    settings.MEDIA_ROOT = tmpdir.strpath
