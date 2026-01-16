"""
Configuración pytest compartida.
Fixtures globales disponibles para todos los módulos del proyecto.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

# Importar fixtures adicionales de otros archivos para mantener este limpio
# Asegúrate de que las rutas 'tests.fixtures.users' y 'tests.fixtures.rbac' existan
pytest_plugins = [
    'tests.fixtures.users',
    'tests.fixtures.rbac',
]

# --- Fixtures de Cliente API ---

@pytest.fixture
def api_client():
    """Cliente REST API básico sin autenticación."""
    return APIClient()

@pytest.fixture
def authenticated_client(db, sample_user):
    """
    API client autenticado con un usuario regular.
    Reutiliza la fixture 'sample_user' para consistencia.
    """
    client = APIClient()
    refresh = RefreshToken.for_user(sample_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client

@pytest.fixture
def admin_client(db, sample_admin):
    """
    API client autenticado como superusuario.
    Reutiliza la fixture 'sample_admin'.
    """
    client = APIClient()
    refresh = RefreshToken.for_user(sample_admin)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client

# --- Fixtures de Usuarios (Entidades Core) ---

@pytest.fixture
def sample_user(db):
    """Usuario estándar para pruebas de permisos."""
    User = get_user_model()
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )

@pytest.fixture
def sample_admin(db):
    """Superusuario para pruebas de administración."""
    User = get_user_model()
    return User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='adminpass123'
    )

# --- Fixtures de Negocio (Core Models) ---

@pytest.fixture
def sample_center(db):
    """Centro de ejemplo."""
    from apps.core.models import Center
    return Center.objects.get_or_create(
        codigo='CT01',
        defaults={'nombre': 'Centro Test'}
    )[0]

@pytest.fixture
def sample_service(db, sample_center):
    """Servicio asociado a un centro."""
    from apps.core.models import Service
    return Service.objects.create(
        numero_800='800-123-4567',
        nombre='Servicio Test',
        center=sample_center,
        activo=True
    )

# --- Helpers ---

@pytest.fixture
def sample_date():
    """Fecha estática para evitar errores por cambios de zona horaria en tests."""
    from datetime import date
    return date(2024, 1, 15)