"""Tests para modelos Module y UserModuleAccess."""
import pytest
from django.contrib.auth import get_user_model
from apps.access.models import Module, UserModuleAccess

User = get_user_model()


@pytest.mark.django_db
class TestModuleModel:
    """Tests para Module model."""
    
    def test_create_root_module(self):
        """Test crear módulo raíz."""
        module = Module.objects.create(
            code='MOD_Test',
            name='Test Module',
            description='Test',
        )
        assert module.is_root() is True
        assert module.get_level() == 0
    
    def test_create_child_module(self):
        """Test crear módulo hijo."""
        parent = Module.objects.create(code='MOD_Parent', name='Parent')
        child = Module.objects.create(
            code='MOD_Child',
            name='Child',
            parent=parent,
        )
        assert child.is_root() is False
        assert child.get_level() == 1
        assert child.parent == parent
    
    def test_get_ancestors(self):
        """Test obtener ancestros."""
        root = Module.objects.create(code='ROOT', name='Root')
        child1 = Module.objects.create(code='CHILD1', name='Child1', parent=root)
        child2 = Module.objects.create(code='CHILD2', name='Child2', parent=child1)
        
        ancestors = child2.get_ancestors()
        assert len(ancestors) == 2
        assert child1 in ancestors
        assert root in ancestors
    
    def test_soft_delete_module(self):
        """Test soft delete de módulo."""
        module = Module.objects.create(code='MOD_Delete', name='Delete')
        module.delete()
        
        assert module.is_deleted is True
        assert Module.objects.count() == 0
        assert Module.objects.all_with_deleted().count() == 1


@pytest.mark.django_db
class TestUserModuleAccessModel:
    """Tests para UserModuleAccess model."""
    
    def test_grant_access(self):
        """Test otorgar acceso a módulo."""
        user = User.objects.create_user(username='test')
        module = Module.objects.create(code='MOD_Test', name='Test')
        
        access = UserModuleAccess.objects.create(
            user=user,
            module=module,
        )
        
        assert access.is_active is True
        assert access.user == user
        assert access.module == module
    
    def test_get_user_modules(self):
        """Test obtener módulos de usuario."""
        user = User.objects.create_user(username='test')
        parent = Module.objects.create(code='PARENT', name='Parent')
        child = Module.objects.create(code='CHILD', name='Child', parent=parent)
        
        # Acceso al padre
        UserModuleAccess.objects.create(user=user, module=parent)
        
        # Debe incluir hijo automáticamente
        modules = UserModuleAccess.get_user_modules(user)
        assert parent in modules
        assert child in modules
