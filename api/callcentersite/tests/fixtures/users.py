"""
Fixtures usuarios para tests.
"""
import pytest
from django.contrib.auth.models import User


@pytest.fixture
def user_data():
    """Datos básicos usuario."""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
    }


@pytest.fixture
def basic_user(django_user_model):
    """Usuario básico sin permisos."""
    return django_user_model.objects.create_user(
        username='basicuser',
        password='basic123'
    )


@pytest.fixture
def admin_user(django_user_model):
    """Usuario admin."""
    return django_user_model.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
