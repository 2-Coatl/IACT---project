import pytest
from django.contrib.auth.models import User, AnonymousUser
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from apps.access.models import Function, UserFunctionAssignment
from apps.access.permissions import HasFunction


class DummyView(APIView):
    """View dummy para tests."""
    permission_classes = [HasFunction]
    required_function = 've_reportes'


@pytest.mark.unit
@pytest.mark.django_db
class TestHasFunctionPermission:
    """Tests para permission HasFunction."""
    
    def test_unauthenticated_user_denied(self):
        """Usuario no autenticado es denegado."""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()  # Usuario anonimo (no autenticado)
        
        view = DummyView()
        permission = HasFunction()
        
        assert permission.has_permission(request, view) is False
    
    def test_superuser_always_allowed(self):
        """Superuser siempre tiene permiso."""
        user = User.objects.create_user(
            username='admin',
            is_superuser=True
        )
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        view = DummyView()
        permission = HasFunction()
        
        assert permission.has_permission(request, view) is True
    
    def test_user_with_function_allowed(self):
        """Usuario con la funcion es permitido."""
        user = User.objects.create_user('testuser')
        admin = User.objects.create_user('admin')
        
        func = Function.objects.create(
            code='ve_reportes',
            module='MOD_Reports',
            name='Ver Reportes'
        )
        
        UserFunctionAssignment.objects.create(
            user=user,
            function=func,
            assigned_by=admin,
            reason='Test',
            is_active=True
        )
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        view = DummyView()
        permission = HasFunction()
        
        assert permission.has_permission(request, view) is True
    
    def test_user_without_function_denied(self):
        """Usuario sin la funcion es denegado."""
        user = User.objects.create_user('testuser')
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        view = DummyView()
        permission = HasFunction()
        
        assert permission.has_permission(request, view) is False
    
    def test_user_with_inactive_function_denied(self):
        """Usuario con funcion inactiva es denegado."""
        user = User.objects.create_user('testuser')
        admin = User.objects.create_user('admin')
        
        func = Function.objects.create(
            code='ve_reportes',
            module='MOD_Reports',
            name='Ver Reportes'
        )
        
        UserFunctionAssignment.objects.create(
            user=user,
            function=func,
            assigned_by=admin,
            reason='Test',
            is_active=False  # INACTIVA
        )
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        view = DummyView()
        permission = HasFunction()
        
        assert permission.has_permission(request, view) is False
    
    def test_view_without_required_function_denied(self):
        """View sin required_function definido deniega acceso."""
        user = User.objects.create_user('testuser')
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        # View sin required_function
        class ViewWithoutFunction(APIView):
            permission_classes = [HasFunction]
        
        view = ViewWithoutFunction()
        permission = HasFunction()
        
        assert permission.has_permission(request, view) is False
