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
def admin_client(db):
    """
    API client autenticado como superusuario.
    
    Usage:
        def test_admin_endpoint(admin_client):
            response = admin_client.get('/api/v1/admin/users/')
            assert response.status_code == 200
    """
    from django.contrib.auth import get_user_model
    from rest_framework_simplejwt.tokens import RefreshToken
    
    User = get_user_model()
    admin = User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='adminpass123'
    )
    
    client = APIClient()
    refresh = RefreshToken.for_user(admin)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return client


@pytest.fixture
def sample_user(db):
    """
    Usuario de ejemplo para tests.
    
    Usage:
        def test_user_model(sample_user):
            assert sample_user.username == 'testuser'
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )


@pytest.fixture
def sample_admin(db):
    """
    Superusuario de ejemplo para tests.
    
    Usage:
        def test_admin_permission(sample_admin):
            assert sample_admin.is_superuser
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='adminpass123'
    )


@pytest.fixture
def sample_date():
    """
    Fecha de ejemplo para tests.
    
    Siempre la misma para reproducibilidad.
    """
    from datetime import date
    return date(2024, 1, 15)


@pytest.fixture
def sample_center(db):
    """
    Centro de ejemplo para tests.
    
    Usage:
        def test_center(sample_center):
            assert sample_center.nombre == 'Centro Test'
    """
    from apps.core.models import Center
    return Center.objects.create(
        nombre='Centro Test',
        codigo='CT01'
    )


@pytest.fixture
def sample_service(db, sample_center):
    """
    Servicio 800 de ejemplo para tests.
    
    Usage:
        def test_service(sample_service):
            assert sample_service.numero_800 == '800-123-4567'
    """
    from apps.core.models import Service
    return Service.objects.create(
        numero_800='800-123-4567',
        nombre='Servicio Test',
        center=sample_center,
        activo=True
    )


# Importar fixtures adicionales
pytest_plugins = [
    'tests.fixtures.users',
    'tests.fixtures.rbac',
]
