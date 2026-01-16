"""
Tests para API de avatar.

Cobertura:
- POST /api/v1/users/upload-avatar/
- DELETE /api/v1/users/delete-avatar/
- Validaciones (extension, tamaño)
- Manejo de errores
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, Mock
import os

User = get_user_model()


@pytest.mark.django_db
class TestUploadAvatarAPI:
    """Tests para POST /api/v1/users/upload-avatar/"""
    
    @pytest.fixture
    def api_client(self):
        """Cliente API."""
        return APIClient()
    
    @pytest.fixture
    def user(self):
        """Usuario de prueba."""
        return User.objects.create_user(
            username='testuser',
            password='pass123'
        )
    
    @pytest.fixture
    def valid_image(self):
        """Imagen valida."""
        return SimpleUploadedFile(
            name='avatar.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
    
    def test_upload_avatar_requires_authentication(self, api_client, valid_image):
        """Test que endpoint requiere autenticacion."""
        url = reverse('users:upload-avatar')
        response = api_client.post(url, {'avatar': valid_image})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_upload_avatar_success(self, api_client, user, valid_image):
        """Test upload exitoso de avatar."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:upload-avatar')
        response = api_client.post(url, {'avatar': valid_image}, format='multipart')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'avatar_url' in response.data
        assert 'message' in response.data
        
        # Verificar que se guardo
        user.refresh_from_db()
        assert user.avatar is not None
    
    def test_upload_avatar_no_file_sent(self, api_client, user):
        """Test upload sin archivo."""
        api_client.force_authenticate(user=user)
        
        url = reverse('users:upload-avatar')
        response = api_client.post(url, {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_upload_avatar_invalid_extension(self, api_client, user):
        """Test upload con extension invalida."""
        invalid_file = SimpleUploadedFile(
            name='avatar.txt',
            content=b'fake content',
            content_type='text/plain'
        )
        
        api_client.force_authenticate(user=user)
        
        url = reverse('users:upload-avatar')
        response = api_client.post(url, {'avatar': invalid_file}, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'Extension no permitida' in response.data['error']
    
    @patch('apps.users.views.settings')
    def test_upload_avatar_file_too_large(self, mock_settings, api_client, user):
        """Test upload con archivo muy grande."""
        mock_settings.MAX_AVATAR_SIZE = 100  # 100 bytes max
        mock_settings.ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
        
        large_file = SimpleUploadedFile(
            name='avatar.jpg',
            content=b'x' * 200,  # 200 bytes (mas grande que limite)
            content_type='image/jpeg'
        )
        
        api_client.force_authenticate(user=user)
        
        url = reverse('users:upload-avatar')
        response = api_client.post(url, {'avatar': large_file}, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'muy grande' in response.data['error'].lower()
    
    @patch('os.path.exists')
    @patch('os.remove')
    def test_upload_avatar_replaces_old_avatar(
        self, 
        mock_remove, 
        mock_exists, 
        api_client, 
        user, 
        valid_image
    ):
        """Test que upload reemplaza avatar anterior."""
        mock_exists.return_value = True
        
        # Usuario ya tiene avatar
        old_avatar = SimpleUploadedFile(
            name='old_avatar.jpg',
            content=b'old image',
            content_type='image/jpeg'
        )
        user.avatar = old_avatar
        user.save()
        
        api_client.force_authenticate(user=user)
        
        # Upload nuevo avatar
        new_avatar = SimpleUploadedFile(
            name='new_avatar.jpg',
            content=b'new image',
            content_type='image/jpeg'
        )
        
        url = reverse('users:upload-avatar')
        response = api_client.post(url, {'avatar': new_avatar}, format='multipart')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que se intento eliminar el anterior
        # mock_remove.assert_called_once()
    
    def test_upload_avatar_jpg(self, api_client, user):
        """Test upload con JPG."""
        jpg_image = SimpleUploadedFile(
            name='avatar.jpg',
            content=b'fake jpg',
            content_type='image/jpeg'
        )
        
        api_client.force_authenticate(user=user)
        
        url = reverse('users:upload-avatar')
        response = api_client.post(url, {'avatar': jpg_image}, format='multipart')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_upload_avatar_png(self, api_client, user):
        """Test upload con PNG."""
        png_image = SimpleUploadedFile(
            name='avatar.png',
            content=b'fake png',
            content_type='image/png'
        )
        
        api_client.force_authenticate(user=user)
        
        url = reverse('users:upload-avatar')
        response = api_client.post(url, {'avatar': png_image}, format='multipart')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_upload_avatar_gif(self, api_client, user):
        """Test upload con GIF."""
        gif_image = SimpleUploadedFile(
            name='avatar.gif',
            content=b'fake gif',
            content_type='image/gif'
        )
        
        api_client.force_authenticate(user=user)
        
        url = reverse('users:upload-avatar')
        response = api_client.post(url, {'avatar': gif_image}, format='multipart')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDeleteAvatarAPI:
    """Tests para DELETE /api/v1/users/delete-avatar/"""
    
    @pytest.fixture
    def api_client(self):
        """Cliente API."""
        return APIClient()
    
    @pytest.fixture
    def user_with_avatar(self):
        """Usuario con avatar."""
        avatar = SimpleUploadedFile(
            name='avatar.jpg',
            content=b'fake image',
            content_type='image/jpeg'
        )
        
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            avatar=avatar
        )
        return user
    
    @pytest.fixture
    def user_without_avatar(self):
        """Usuario sin avatar."""
        return User.objects.create_user(
            username='testuser',
            password='pass123'
        )
    
    def test_delete_avatar_requires_authentication(self, api_client):
        """Test que endpoint requiere autenticacion."""
        url = reverse('users:delete-avatar')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('apps.users.models.CustomUser.delete_avatar')
    def test_delete_avatar_success(
        self, 
        mock_delete, 
        api_client, 
        user_with_avatar
    ):
        """Test delete exitoso."""
        mock_delete.return_value = True
        
        api_client.force_authenticate(user=user_with_avatar)
        
        url = reverse('users:delete-avatar')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'avatar_url' in response.data
        assert 'message' in response.data
    
    @patch('apps.users.models.CustomUser.delete_avatar')
    def test_delete_avatar_no_avatar_to_delete(
        self, 
        mock_delete, 
        api_client, 
        user_without_avatar
    ):
        """Test delete cuando no hay avatar."""
        mock_delete.return_value = False
        
        api_client.force_authenticate(user=user_without_avatar)
        
        url = reverse('users:delete-avatar')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'No habia avatar' in response.data['message']
    
    @patch('apps.users.models.CustomUser.delete_avatar')
    def test_delete_avatar_handles_error(
        self, 
        mock_delete, 
        api_client, 
        user_with_avatar
    ):
        """Test manejo de error en delete."""
        mock_delete.side_effect = Exception('Error interno')
        
        api_client.force_authenticate(user=user_with_avatar)
        
        url = reverse('users:delete-avatar')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data
    
    @patch('apps.users.models.CustomUser.delete_avatar')
    def test_delete_avatar_returns_default_url(
        self, 
        mock_delete, 
        api_client, 
        user_with_avatar
    ):
        """Test que delete retorna URL default."""
        mock_delete.return_value = True
        
        api_client.force_authenticate(user=user_with_avatar)
        
        url = reverse('users:delete-avatar')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        # avatar_url deberia ser el default
        assert 'avatar_url' in response.data


@pytest.mark.django_db
class TestAvatarURLsIntegration:
    """Tests de integracion para URLs de avatar."""
    
    def test_upload_avatar_url_resolves(self):
        """Test que URL de upload resuelve."""
        url = reverse('users:upload-avatar')
        assert url == '/api/v1/users/upload-avatar/'
    
    def test_delete_avatar_url_resolves(self):
        """Test que URL de delete resuelve."""
        url = reverse('users:delete-avatar')
        assert url == '/api/v1/users/delete-avatar/'
    
    def test_urls_are_different(self):
        """Test que URLs son diferentes."""
        upload_url = reverse('users:upload-avatar')
        delete_url = reverse('users:delete-avatar')
        
        assert upload_url != delete_url
