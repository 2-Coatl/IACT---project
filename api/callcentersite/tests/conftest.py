"""
Configuración pytest compartida.

Fixtures disponibles para todos los tests.
"""
import pytest
from rest_framework.test import APIClient


# NOTA: django_db_setup removido - testing.py ya configura SQLite correctamente
# El fixture causaba conflictos con pytest-django impidiendo la creación de tablas


@pytest.fixture
def api_client():
    """
    REST API client.
    
    Usage:
        def test_endpoint(api_client):
            response = api_client.get('/api/v1/calls/')
            assert response.status_code == 200
    """
    return APIClient()


@pytest.fixture
def authenticated_client(db):
    """
    API client autenticado.
    
    Crea usuario y autentica automáticamente.
    
    Usage:
        def test_protected(authenticated_client):
            response = authenticated_client.get('/api/v1/calls/')
            assert response.status_code == 200
    """
    from django.contrib.auth import get_user_model
    from rest_framework_simplejwt.tokens import RefreshToken
    
    User = get_user_model()
    user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )
    
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return client


@pytest.fixture
def sample_date():
    """
    Fecha de ejemplo para tests.
    
    Siempre la misma para reproducibilidad.
    """
    from datetime import date
    return date(2024, 1, 15)


# Importar fixtures adicionales
pytest_plugins = [
    'tests.fixtures.users',
    'tests.fixtures.rbac',
]
