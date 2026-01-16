"""Tests para permissions de módulos."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from apps.access.models import Module, UserModuleAccess
from apps.access.permissions import HasModuleAccess

User = get_user_model()


@pytest.mark.django_db
class TestHasModuleAccess:
    """Tests para HasModuleAccess permission."""
    
    def test_permission_with_access(self):
        """Test permiso con acceso."""
        user = User.objects.create_user(username='test')
        module = Module.objects.create(code='MOD_Test', name='Test')
        UserModuleAccess.objects.create(user=user, module=module)
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        class MockView:
            required_module = 'MOD_Test'
        
        permission = HasModuleAccess()
        assert permission.has_permission(request, MockView()) is True
    
    def test_permission_without_access(self):
        """Test permiso sin acceso."""
        user = User.objects.create_user(username='test')
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        class MockView:
            required_module = 'MOD_Test'
        
        permission = HasModuleAccess()
        assert permission.has_permission(request, MockView()) is False
