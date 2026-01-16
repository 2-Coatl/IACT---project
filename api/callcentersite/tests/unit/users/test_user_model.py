"""
Tests para User model extendido.

Cobertura:
- Campos: avatar, phone, position, employee_id
- Metodos RBAC: get_functions(), has_function(), etc.
- Metodos avatar: get_avatar_url(), delete_avatar()
- user_avatar_path()
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import Mock, patch
import os

User = get_user_model()


@pytest.mark.django_db
class TestUserModelFields:
    """Tests para campos adicionales del User model."""
    
    def test_create_user_with_avatar(self):
        """Test crear usuario con avatar."""
        # Crear imagen fake
        avatar = SimpleUploadedFile(
            name='test_avatar.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            avatar=avatar
        )
        
        assert user.avatar is not None
        assert 'test_avatar' in user.avatar.name
    
    def test_create_user_with_phone(self):
        """Test crear usuario con telefono."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            phone='+56912345678'
        )
        
        assert user.phone == '+56912345678'
    
    def test_create_user_with_position(self):
        """Test crear usuario con cargo."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            position='Administrador de Sistema'
        )
        
        assert user.position == 'Administrador de Sistema'
    
    def test_create_user_with_employee_id(self):
        """Test crear usuario con ID de empleado."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            employee_id='EMP-001'
        )
        
        assert user.employee_id == 'EMP-001'
    
    def test_employee_id_unique(self):
        """Test que employee_id es unico."""
        User.objects.create_user(
            username='user1',
            password='pass123',
            employee_id='EMP-001'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            User.objects.create_user(
                username='user2',
                password='pass123',
                employee_id='EMP-001'  # Duplicado
            )
    
    def test_user_str_with_full_name(self):
        """Test __str__ con nombre completo."""
        user = User.objects.create_user(
            username='jperez',
            password='pass123',
            first_name='Juan',
            last_name='Perez'
        )
        
        assert str(user) == 'Juan Perez (jperez)'
    
    def test_user_str_without_full_name(self):
        """Test __str__ sin nombre completo."""
        user = User.objects.create_user(
            username='admin',
            password='pass123'
        )
        
        assert str(user) == 'admin'


@pytest.mark.django_db
class TestUserAvatarMethods:
    """Tests para metodos de avatar."""
    
    def test_get_avatar_url_with_avatar(self):
        """Test get_avatar_url() cuando usuario tiene avatar."""
        avatar = SimpleUploadedFile(
            name='avatar.jpg',
            content=b'fake',
            content_type='image/jpeg'
        )
        
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            avatar=avatar
        )
        
        url = user.get_avatar_url()
        assert url is not None
        assert '/media/profiles/' in url or url.startswith('/media/')
    
    def test_get_avatar_url_without_avatar(self):
        """Test get_avatar_url() cuando usuario NO tiene avatar."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        
        url = user.get_avatar_url()
        assert url == '/static/icons/defaults/avatar_default.png'
    
    @patch('os.path.exists')
    @patch('os.remove')
    def test_delete_avatar_success(self, mock_remove, mock_exists):
        """Test delete_avatar() exitoso."""
        mock_exists.return_value = True
        
        avatar = SimpleUploadedFile(
            name='avatar.jpg',
            content=b'fake',
            content_type='image/jpeg'
        )
        
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            avatar=avatar
        )
        
        result = user.delete_avatar()
        
        assert result is True
        assert user.avatar is None or not user.avatar
    
    def test_delete_avatar_no_avatar(self):
        """Test delete_avatar() cuando no hay avatar."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        
        result = user.delete_avatar()
        assert result is False
    
    def test_user_avatar_path_function(self):
        """Test funcion user_avatar_path()."""
        from apps.users.models import user_avatar_path
        
        user_mock = Mock()
        user_mock.id = 123
        
        path = user_avatar_path(user_mock, 'photo.jpg')
        
        assert path == 'profiles/user_123/avatar.jpg'
    
    def test_user_avatar_path_preserves_extension(self):
        """Test que user_avatar_path preserva extension."""
        from apps.users.models import user_avatar_path
        
        user_mock = Mock()
        user_mock.id = 456
        
        # JPG
        path_jpg = user_avatar_path(user_mock, 'image.jpg')
        assert path_jpg.endswith('.jpg')
        
        # PNG
        path_png = user_avatar_path(user_mock, 'image.png')
        assert path_png.endswith('.png')
        
        # GIF
        path_gif = user_avatar_path(user_mock, 'image.gif')
        assert path_gif.endswith('.gif')


@pytest.mark.django_db
class TestUserRBACMethods:
    """Tests para metodos RBAC."""
    
    @pytest.fixture
    def user_with_functions(self):
        """Usuario con funciones mock."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        
        # Mock get_functions para retornar lista
        with patch.object(user, 'get_functions', return_value=[
            'RPT-001: view_reports',
            'RPT-002: view_dashboard',
            'USR-001: create_users',
        ]):
            yield user
    
    def test_get_functions_returns_list(self):
        """Test que get_functions() retorna lista."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        
        functions = user.get_functions()
        assert isinstance(functions, list)
    
    def test_get_functions_empty_for_new_user(self):
        """Test que nuevo usuario no tiene funciones."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        
        functions = user.get_functions()
        assert functions == []
    
    def test_has_function_true(self, user_with_functions):
        """Test has_function() cuando usuario tiene la funcion."""
        assert user_with_functions.has_function('RPT-001: view_reports') is True
        assert user_with_functions.has_function('RPT-002: view_dashboard') is True
    
    def test_has_function_false(self, user_with_functions):
        """Test has_function() cuando usuario NO tiene la funcion."""
        assert user_with_functions.has_function('ACC-001: assign_functions') is False
        assert user_with_functions.has_function('nonexistent') is False
    
    def test_has_any_function_true(self, user_with_functions):
        """Test has_any_function() cuando tiene al menos una."""
        functions = [
            'RPT-001: view_reports',
            'ACC-001: assign_functions',  # No tiene esta
        ]
        
        assert user_with_functions.has_any_function(functions) is True
    
    def test_has_any_function_false(self, user_with_functions):
        """Test has_any_function() cuando no tiene ninguna."""
        functions = [
            'ACC-001: assign_functions',
            'ACC-002: revoke_functions',
        ]
        
        assert user_with_functions.has_any_function(functions) is False
    
    def test_has_all_functions_true(self, user_with_functions):
        """Test has_all_functions() cuando tiene todas."""
        functions = [
            'RPT-001: view_reports',
            'RPT-002: view_dashboard',
        ]
        
        assert user_with_functions.has_all_functions(functions) is True
    
    def test_has_all_functions_false(self, user_with_functions):
        """Test has_all_functions() cuando no tiene todas."""
        functions = [
            'RPT-001: view_reports',
            'ACC-001: assign_functions',  # No tiene esta
        ]
        
        assert user_with_functions.has_all_functions(functions) is False
    
    def test_has_all_functions_empty_list(self, user_with_functions):
        """Test has_all_functions() con lista vacia."""
        assert user_with_functions.has_all_functions([]) is True


@pytest.mark.django_db
class TestUserModelMeta:
    """Tests para Meta del modelo."""
    
    def test_db_table_name(self):
        """Test que db_table es 'users'."""
        assert User._meta.db_table == 'users'
    
    def test_verbose_name(self):
        """Test verbose_name."""
        assert User._meta.verbose_name == 'Usuario'
    
    def test_verbose_name_plural(self):
        """Test verbose_name_plural."""
        assert User._meta.verbose_name_plural == 'Usuarios'
    
    def test_ordering(self):
        """Test que ordering es por username."""
        assert User._meta.ordering == ['username']
    
    def test_has_username_index(self):
        """Test que existe index en username."""
        indexes = User._meta.indexes
        index_fields = [idx.fields for idx in indexes]
        
        assert ['username'] in index_fields
    
    def test_has_email_index(self):
        """Test que existe index en email."""
        indexes = User._meta.indexes
        index_fields = [idx.fields for idx in indexes]
        
        assert ['email'] in index_fields
    
    def test_has_employee_id_index(self):
        """Test que existe index en employee_id."""
        indexes = User._meta.indexes
        index_fields = [idx.fields for idx in indexes]
        
        assert ['employee_id'] in index_fields


@pytest.mark.django_db
class TestGetFullName:
    """Tests para get_full_name()."""
    
    def test_get_full_name_with_first_and_last(self):
        """Test get_full_name() con nombre y apellido."""
        user = User.objects.create_user(
            username='jperez',
            password='pass123',
            first_name='Juan',
            last_name='Perez'
        )
        
        assert user.get_full_name() == 'Juan Perez'
    
    def test_get_full_name_only_first_name(self):
        """Test get_full_name() solo con nombre."""
        user = User.objects.create_user(
            username='juan',
            password='pass123',
            first_name='Juan'
        )
        
        assert user.get_full_name() == 'Juan'
    
    def test_get_full_name_empty_returns_username(self):
        """Test get_full_name() vacio retorna username."""
        user = User.objects.create_user(
            username='admin',
            password='pass123'
        )
        
        assert user.get_full_name() == 'admin'
    
    def test_get_full_name_whitespace_returns_username(self):
        """Test get_full_name() con espacios retorna username."""
        user = User.objects.create_user(
            username='admin',
            password='pass123',
            first_name='   ',
            last_name='   '
        )
        
        assert user.get_full_name() == 'admin'
