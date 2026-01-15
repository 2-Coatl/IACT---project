import pytest
from django.contrib.auth.models import User
from apps.users.serializers import UserSerializer, UserCreateSerializer
from apps.access.models import Function, UserFunctionAssignment


@pytest.mark.unit
@pytest.mark.django_db
class TestUserSerializer:
    """Tests UserSerializer."""
    
    def test_serialize_user(self):
        """Serializar usuario con funciones."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Asignar funcion
        func = Function.objects.create(
            code='TEST_FUNC',
            module='MOD_Test',
            name='Test Function'
        )
        admin = User.objects.create_user('admin')
        UserFunctionAssignment.objects.create(
            user=user,
            function=func,
            assigned_by=admin,
            reason='test assignment'
        )
        
        serializer = UserSerializer(user)
        
        assert 'id' in serializer.data
        assert serializer.data['username'] == 'testuser'
        assert serializer.data['email'] == 'test@example.com'
        assert serializer.data['first_name'] == 'Test'
        assert serializer.data['last_name'] == 'User'
        assert 'functions' in serializer.data
        assert 'TEST_FUNC' in serializer.data['functions']
    
    def test_user_serializer_fields_explicit(self):
        """Verificar fields explicitos (CNST-005)."""
        user = User.objects.create_user('testuser')
        serializer = UserSerializer(user)
        
        # Fields esperados (NO __all__)
        expected_fields = {
            'id', 'username', 'email', 'first_name', 
            'last_name', 'is_active', 'date_joined', 'functions'
        }
        assert set(serializer.data.keys()) == expected_fields
    
    def test_user_serializer_readonly_fields(self):
        """id, date_joined y functions son readonly."""
        user = User.objects.create_user('testuser')
        serializer = UserSerializer(user)
        
        # Verificar readonly_fields
        assert 'id' in serializer.Meta.read_only_fields
        assert 'date_joined' in serializer.Meta.read_only_fields
        assert 'functions' in serializer.Meta.read_only_fields
    
    def test_functions_field_empty_when_no_assignments(self):
        """Campo functions vacio cuando usuario no tiene funciones."""
        user = User.objects.create_user('testuser')
        serializer = UserSerializer(user)
        
        assert serializer.data['functions'] == []


@pytest.mark.unit
@pytest.mark.django_db
class TestUserCreateSerializer:
    """Tests UserCreateSerializer."""
    
    def test_create_user_hashes_password(self):
        """Crear usuario hashea password."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'testpass123'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid()
        
        user = serializer.save()
        
        # Password debe estar hasheado
        assert user.password != 'testpass123'
        assert user.check_password('testpass123')
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
    
    def test_password_write_only(self):
        """Password es write_only."""
        user = User.objects.create_user(
            'testuser',
            password='test123'
        )
        serializer = UserCreateSerializer(user)
        
        # password NO debe aparecer en data
        assert 'password' not in serializer.data
    
    def test_password_min_length(self):
        """Password requiere minimo 8 caracteres."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'short'  # Solo 5 caracteres
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_create_serializer_fields_explicit(self):
        """Fields explicitos (CNST-005)."""
        serializer = UserCreateSerializer()
        
        expected_fields = {
            'username', 'email', 'first_name', 'last_name', 'password'
        }
        assert set(serializer.fields.keys()) == expected_fields
