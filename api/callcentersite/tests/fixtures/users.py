"""
Fixtures de usuarios para el modelo CustomUser.
Este archivo centraliza la creación de usuarios para evitar duplicidad de código
en tests de Modelos, APIs, Serializadores y Vistas.
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

# Obtenemos el CustomUser definido en AUTH_USER_MODEL
User = get_user_model()

@pytest.fixture
def user_factory(db):
    """
    Factory universal para crear usuarios con cualquier atributo.
    Cubre: test_user_model.py y test_views.py (múltiples usuarios).
    """
    def _make_user(username='testuser', **kwargs):
        if 'email' not in kwargs:
            kwargs['email'] = f'{username}@example.com'
        
        password = kwargs.pop('password', 'testpass123')
        
        # .create_user funcionará con CustomUser y sus campos extra
        user = User.objects.create_user(username=username, **kwargs)
        user.set_password(password)
        user.save()
        return user
    return _make_user

@pytest.fixture
def user_data():
    """
    Datos planos para pruebas de serializadores.
    Cubre: test_serializers.py.
    """
    return {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
    }

@pytest.fixture
def basic_user(user_factory):
    """Usuario estándar sin atributos adicionales."""
    return user_factory(username='basicuser')

@pytest.fixture
def sample_admin(user_factory):
    """
    Superusuario para pruebas de administración.
    Reemplaza la creación manual en todos los archivos.
    """
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )

@pytest.fixture
def user_with_profile(user_factory):
    """
    Usuario con el perfil completo según el modelo CustomUser.
    Cubre: test_profile_api.py.
    """
    return user_factory(
        username='profileuser',
        first_name='Juan',
        last_name='Perez',
        phone='+56912345678',
        position='Developer',
        employee_id='EMP-001'
    )

@pytest.fixture
def valid_avatar_file():
    """
    Archivo de imagen mínimo válido en memoria.
    Cubre: test_avatar_api.py y test_user_model.py.
    """
    return SimpleUploadedFile(
        name='test_avatar.jpg',
        content=(
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
            b'\x01\x00\x3b'
        ),
        content_type='image/jpeg'
    )

@pytest.fixture
def user_with_avatar(user_factory, valid_avatar_file):
    """
    Usuario que ya tiene un avatar asignado.
    Cubre: test_avatar_api.py.
    """
    return user_factory(username='avataruser', avatar=valid_avatar_file)

@pytest.fixture
def other_user(user_factory):
    """
    Segundo usuario para pruebas de permisos o listados.
    Cubre: test_views.py.
    """
    return user_factory(username='otheruser')