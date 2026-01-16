"""
Tests para API de perfil de usuario.

Cobertura:
- GET /api/v1/users/profile/
- PUT /api/v1/users/profile/update/
- Datos retornados
- Actualizacion de campos
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

User = get_user_model()


@pytest.mark.django_db
class TestGetUserProfileAPI:
    """Tests para GET /api/v1/users/profile/"""
    
    @pytest.fixture
    def api_client(self):
        """Cliente API."""
        return APIClient()
    
    @pytest.fixture
    def user(self):
        """Usuario de prueba."""
        return User.objects.create_user(
            username='testuser',
            password='pass123',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone='+56912345678',
            position='Developer',
            employee_id='EMP-001'
        )
    
    def test_get_profile_requires_authentication(self, api_client):
        """Test que endpoint requiere autenticacion."""
        url = reverse('users:user-profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_profile_success(self, api_client, user):
        """Test obtener perfil exitosamente."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:user-profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar campos
        data = response.data
        assert data['id'] == user.id
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert data['first_name'] == 'Test'
        assert data['last_name'] == 'User'
        assert data['full_name'] == 'Test User'
        assert data['phone'] == '+56912345678'
        assert data['position'] == 'Developer'
        assert data['employee_id'] == 'EMP-001'
        assert data['is_active'] is True
    
    def test_get_profile_includes_avatar_url(self, api_client, user):
        """Test que perfil incluye avatar_url."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:user-profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'avatar_url' in response.data
        # Sin avatar debe retornar default
        assert response.data['avatar_url'] == '/static/icons/defaults/avatar_default.png'
    
    @patch.object(User, 'get_functions')
    def test_get_profile_includes_functions(self, mock_get_functions, api_client, user):
        """Test que perfil incluye funciones RBAC."""
        mock_get_functions.return_value = [
            'RPT-001: view_reports',
            'USR-001: create_users'
        ]
        
        api_client.force_authenticate(user=user)
        
        url = reverse('users:user-profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'functions' in response.data
        assert len(response.data['functions']) == 2
        assert 'RPT-001: view_reports' in response.data['functions']
    
    def test_get_profile_with_minimal_user(self, api_client):
        """Test perfil con usuario minimo (solo username)."""
        minimal_user = User.objects.create_user(
            username='admin',
            password='pass123'
        )
        
        api_client.force_authenticate(user=minimal_user)
        
        url = reverse('users:user-profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'admin'
        assert response.data['full_name'] == 'admin'
        assert response.data['phone'] is None
        assert response.data['position'] is None
        assert response.data['employee_id'] is None
    
    def test_get_profile_includes_created_at(self, api_client, user):
        """Test que perfil incluye created_at."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:user-profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'created_at' in response.data
        assert response.data['created_at'] is not None
    
    def test_get_profile_handles_error(self, api_client, user):
        """Test manejo de error al obtener perfil."""
        api_client.force_authenticate(user=user)
        
        with patch.object(User, 'get_functions', side_effect=Exception('Error')):
            url = reverse('users:user-profile')
            response = api_client.get(url)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data


@pytest.mark.django_db
class TestUpdateUserProfileAPI:
    """Tests para PUT /api/v1/users/profile/update/"""
    
    @pytest.fixture
    def api_client(self):
        """Cliente API."""
        return APIClient()
    
    @pytest.fixture
    def user(self):
        """Usuario de prueba."""
        return User.objects.create_user(
            username='testuser',
            password='pass123',
            first_name='Old',
            last_name='Name'
        )
    
    def test_update_profile_requires_authentication(self, api_client):
        """Test que endpoint requiere autenticacion."""
        url = reverse('users:update-profile')
        response = api_client.put(url, {})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile_first_name(self, api_client, user):
        """Test actualizar first_name."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:update-profile')
        response = api_client.put(
            url, 
            {'first_name': 'New'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'first_name' in response.data['message']
        
        # Verificar en BD
        user.refresh_from_db()
        assert user.first_name == 'New'
    
    def test_update_profile_last_name(self, api_client, user):
        """Test actualizar last_name."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:update-profile')
        response = api_client.put(
            url, 
            {'last_name': 'NewLastName'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.last_name == 'NewLastName'
    
    def test_update_profile_phone(self, api_client, user):
        """Test actualizar phone."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:update-profile')
        response = api_client.put(
            url, 
            {'phone': '+56987654321'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.phone == '+56987654321'
    
    def test_update_profile_position(self, api_client, user):
        """Test actualizar position."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:update-profile')
        response = api_client.put(
            url, 
            {'position': 'Senior Developer'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.position == 'Senior Developer'
    
    def test_update_profile_multiple_fields(self, api_client, user):
        """Test actualizar multiples campos."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:update-profile')
        response = api_client.put(
            url,
            {
                'first_name': 'Juan',
                'last_name': 'Perez',
                'phone': '+56912345678',
                'position': 'Tech Lead'
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        
        # Verificar que mensaje incluye todos los campos
        message = response.data['message']
        assert 'first_name' in message
        assert 'last_name' in message
        assert 'phone' in message
        assert 'position' in message
        
        # Verificar en BD
        user.refresh_from_db()
        assert user.first_name == 'Juan'
        assert user.last_name == 'Perez'
        assert user.phone == '+56912345678'
        assert user.position == 'Tech Lead'
    
    def test_update_profile_no_fields(self, api_client, user):
        """Test update sin campos."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:update-profile')
        response = api_client.put(url, {}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'No se enviaron campos' in response.data['message']
    
    def test_update_profile_ignores_non_allowed_fields(self, api_client, user):
        """Test que campos no permitidos se ignoran."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:update-profile')
        response = api_client.put(
            url,
            {
                'first_name': 'Juan',
                'username': 'hacker',  # No permitido
                'email': 'hacker@evil.com',  # No permitido
                'is_staff': True,  # No permitido
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Solo first_name deberia cambiar
        user.refresh_from_db()
        assert user.first_name == 'Juan'
        assert user.username == 'testuser'  # No cambio
        assert user.email != 'hacker@evil.com'  # No cambio
        assert user.is_staff is False  # No cambio
    
    def test_update_profile_returns_updated_profile(self, api_client, user):
        """Test que update retorna perfil actualizado."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:update-profile')
        response = api_client.put(
            url,
            {'first_name': 'Updated'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'profile' in response.data
        
        profile = response.data['profile']
        assert profile['first_name'] == 'Updated'
        assert profile['full_name'] == 'Updated Name'
    
    def test_update_profile_handles_error(self, api_client, user):
        """Test manejo de error al actualizar."""
        api_client.force_authenticate(user=user)
        
        with patch.object(User, 'save', side_effect=Exception('Error DB')):
            url = reverse('users:update-profile')
            response = api_client.put(
                url,
                {'first_name': 'Test'},
                format='json'
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data


@pytest.mark.django_db
class TestProfileURLsIntegration:
    """Tests de integracion para URLs de perfil."""
    
    def test_profile_url_resolves(self):
        """Test que URL de profile resuelve."""
        url = reverse('users:user-profile')
        assert url == '/api/v1/users/profile/'
    
    def test_update_profile_url_resolves(self):
        """Test que URL de update resuelve."""
        url = reverse('users:update-profile')
        assert url == '/api/v1/users/profile/update/'
    
    def test_urls_are_different(self):
        """Test que URLs son diferentes."""
        get_url = reverse('users:user-profile')
        update_url = reverse('users:update-profile')
        
        assert get_url != update_url
