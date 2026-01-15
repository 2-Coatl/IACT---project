import pytest
from django.contrib.auth.models import User
from apps.access.models import Function, UserFunctionAssignment


@pytest.mark.unit
@pytest.mark.django_db
class TestFunction:
    """Tests modelo Function (RBAC atomico)."""
    
    def test_create_function(self):
        """Crear funcion atomica."""
        func = Function.objects.create(
            code='ve_reportes',
            module='MOD_Reports',
            name='Ver Reportes',
            description='Consultar reportes del sistema',
        )
        
        assert func.id is not None
        assert func.code == 've_reportes'
        assert func.module == 'MOD_Reports'
        assert func.is_active is True
    
    def test_function_str(self):
        """__str__ muestra code y module."""
        func = Function.objects.create(
            code='crea_usuarios',
            module='MOD_Users',
            name='Crear Usuarios',
        )
        
        assert str(func) == 'crea_usuarios (MOD_Users)'
    
    def test_function_code_unique(self):
        """Code debe ser unico."""
        Function.objects.create(
            code='test_func',
            module='MOD_Test',
            name='Test'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            Function.objects.create(
                code='test_func',
                module='MOD_Test',
                name='Test2'
            )
    
    def test_function_ordering(self):
        """Funciones ordenadas por module, code."""
        Function.objects.create(code='zz', module='MOD_Z', name='Z')
        Function.objects.create(code='aa', module='MOD_A', name='A')
        Function.objects.create(code='bb', module='MOD_A', name='B')
        
        funcs = list(Function.objects.all())
        
        # Primero MOD_A (aa, bb), luego MOD_Z (zz)
        assert funcs[0].code == 'aa'
        assert funcs[1].code == 'bb'
        assert funcs[2].code == 'zz'


@pytest.mark.unit
@pytest.mark.django_db
class TestUserFunctionAssignment:
    """Tests asignacion funciones a usuarios."""
    
    def test_assign_function_to_user(self):
        """Asignar funcion a usuario."""
        user = User.objects.create_user('testuser')
        admin = User.objects.create_user('admin')
        func = Function.objects.create(
            code='crea_usuarios',
            module='MOD_Users',
            name='Crear Usuarios',
        )
        
        assignment = UserFunctionAssignment.objects.create(
            user=user,
            function=func,
            assigned_by=admin,
            reason='Permisos iniciales',
        )
        
        assert assignment.user == user
        assert assignment.function == func
        assert assignment.is_active is True
        assert assignment.assigned_by == admin
        assert assignment.reason == 'Permisos iniciales'
    
    def test_assignment_str(self):
        """__str__ muestra username -> function_code."""
        user = User.objects.create_user('testuser')
        admin = User.objects.create_user('admin')
        func = Function.objects.create(
            code='test_func',
            module='MOD_Test',
            name='Test'
        )
        
        assignment = UserFunctionAssignment.objects.create(
            user=user,
            function=func,
            assigned_by=admin,
            reason='Test'
        )
        
        assert str(assignment) == 'testuser -> test_func'
    
    def test_get_user_functions(self):
        """Obtener funciones activas de usuario."""
        user = User.objects.create_user('testuser')
        admin = User.objects.create_user('admin')
        
        func1 = Function.objects.create(code='func1', module='MOD1', name='F1')
        func2 = Function.objects.create(code='func2', module='MOD2', name='F2')
        func3 = Function.objects.create(code='func3', module='MOD3', name='F3')
        
        # Asignar func1 y func2 (activas)
        UserFunctionAssignment.objects.create(
            user=user,
            function=func1,
            assigned_by=admin,
            reason='test'
        )
        UserFunctionAssignment.objects.create(
            user=user,
            function=func2,
            assigned_by=admin,
            reason='test'
        )
        
        # func3 inactiva
        UserFunctionAssignment.objects.create(
            user=user,
            function=func3,
            assigned_by=admin,
            reason='test',
            is_active=False
        )
        
        active_funcs = UserFunctionAssignment.get_user_functions(user)
        
        assert active_funcs.count() == 2
        codes = [a.function.code for a in active_funcs]
        assert 'func1' in codes
        assert 'func2' in codes
        assert 'func3' not in codes
    
    def test_unique_together_user_function(self):
        """Usuario no puede tener misma funcion asignada 2 veces."""
        user = User.objects.create_user('testuser')
        admin = User.objects.create_user('admin')
        func = Function.objects.create(
            code='test',
            module='MOD',
            name='Test'
        )
        
        UserFunctionAssignment.objects.create(
            user=user,
            function=func,
            assigned_by=admin,
            reason='first'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            UserFunctionAssignment.objects.create(
                user=user,
                function=func,
                assigned_by=admin,
                reason='second'
            )
