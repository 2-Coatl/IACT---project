"""
Fixtures RBAC (funciones, asignaciones).
"""
import pytest


@pytest.fixture
def function_create_user(db):
    """Función crear usuario."""
    from apps.access.models import Function
    return Function.objects.create(
        code='create_user',
        name='Crear Usuario',
        description='Permite crear nuevos usuarios'
    )


@pytest.fixture
def function_delete_user(db):
    """Función eliminar usuario."""
    from apps.access.models import Function
    return Function.objects.create(
        code='delete_user',
        name='Eliminar Usuario',
        description='Permite eliminar usuarios'
    )


@pytest.fixture
def user_with_function(db, basic_user, function_create_user):
    """Usuario con función asignada."""
    from apps.access.models import UserFunctionAssignment
    
    assignment = UserFunctionAssignment.objects.create(
        user=basic_user,
        function=function_create_user
    )
    return basic_user
