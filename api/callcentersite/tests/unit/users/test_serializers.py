import pytest
from apps.users.serializers import UserSerializer
from apps.access.models import UserFunctionAssignment

@pytest.mark.unit
@pytest.mark.django_db
class TestUserSerializer:
    """
    Tests para UserSerializer (Lectura).
    Valida la transformación de CustomUser a JSON.
    """

    def test_serialize_basic_user_fields(self, basic_user):
        """1. Validar campos estándar de AbstractUser."""
        serializer = UserSerializer(basic_user)
        data = serializer.data
        
        assert data['username'] == basic_user.username
        assert data['email'] == basic_user.email
        assert 'id' in data

    def test_serialize_custom_fields(self, user_with_profile):
        """2. Validar campos específicos de CustomUser (phone, position, employee_id)."""
        serializer = UserSerializer(user_with_profile)
        data = serializer.data
        
        assert data['phone'] == user_with_profile.phone
        assert data['position'] == user_with_profile.position
        assert data['employee_id'] == user_with_profile.employee_id

    def test_serialize_avatar_url(self, user_with_avatar):
        """3. Validar que retorna la URL completa del avatar."""
        serializer = UserSerializer(user_with_avatar)
        # Debe contener la ruta definida en user_avatar_path
        assert 'profiles/user_' in serializer.data['avatar_url']

    def test_serialize_default_avatar(self, basic_user):
        """4. Validar fallback de avatar cuando no existe archivo."""
        serializer = UserSerializer(basic_user)
        assert serializer.data['avatar_url'] == '/static/icons/defaults/avatar_default.png'

    def test_serialize_with_functions(self, user_with_function):
        """5. Validar inclusión de códigos RBAC mediante get_functions()."""
        user = user_with_function.user
        serializer = UserSerializer(user)
        
        assert 'functions' in serializer.data
        assert 'create_user' in serializer.data['functions']

    def test_serialize_empty_functions(self, basic_user):
        """6. Validar que retorna lista vacía si no hay funciones."""
        serializer = UserSerializer(basic_user)
        assert serializer.data['functions'] == []

    def test_fields_explicit_definition(self):
        """7. Cumplimiento CNST-005: No usar __all__."""
        serializer = UserSerializer()
        # Verificamos que los campos estén explícitamente listados en Meta
        assert serializer.Meta.fields != '__all__'
        
        expected_fields = {
            'id', 'username', 'email', 'first_name', 'last_name', 
            'is_active', 'date_joined', 'functions', 'phone', 
            'position', 'employee_id', 'avatar_url'
        }
        assert set(serializer.Meta.fields).issubset(expected_fields)

    def test_readonly_fields_config(self):
        """8. Verificar campos protegidos contra escritura."""
        serializer = UserSerializer()
        readonly = serializer.Meta.read_only_fields
        
        assert 'id' in readonly
        assert 'date_joined' in readonly
        assert 'functions' in readonly

    def test_full_name_calculation(self, user_with_profile):
        """9. Validar que el serializador exponga el método get_full_name()."""
        serializer = UserSerializer(user_with_profile)
        expected_name = f"{user_with_profile.first_name} {user_with_profile.last_name}"
        assert serializer.data['full_name'] == expected_name

    def test_is_active_status(self, basic_user):
        """10. Verificar el estado de activación del usuario."""
        serializer = UserSerializer(basic_user)
        assert serializer.data['is_active'] is True

from apps.users.serializers import UserCreateSerializer

@pytest.mark.unit
@pytest.mark.django_db
class TestUserCreateSerializer:
    """
    Tests para UserCreateSerializer (Escritura).
    Valida la creación de usuarios, seguridad de contraseñas y validaciones.
    """

    def test_create_user_hashes_password(self, user_data):
        """11. Validar que la contraseña se guarda hasheada y no en texto plano."""
        serializer = UserCreateSerializer(data=user_data)
        assert serializer.is_valid(), serializer.errors
        
        user = serializer.save()
        
        # El hash de Django nunca es igual al texto plano
        assert user.password != user_data['password']
        # Pero debe ser verificable
        assert user.check_password(user_data['password'])

    def test_password_write_only(self, user_factory):
        """12. Seguridad: La contraseña debe ser write_only (no aparecer en el JSON de salida)."""
        user = user_factory(username='secure_user', password='secret_password_123')
        serializer = UserCreateSerializer(user)
        
        # El campo 'password' no debe existir en la representación que va al cliente
        assert 'password' not in serializer.data

    def test_password_min_length_validation(self, user_data):
        """13. Validar longitud mínima de contraseña (8 caracteres)."""
        user_data['password'] = 'short'  # 5 caracteres
        serializer = UserCreateSerializer(data=user_data)
        
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_create_with_custom_fields_success(self, user_data):
        """14. Validar que acepte phone y employee_id durante el registro."""
        serializer = UserCreateSerializer(data=user_data)
        assert serializer.is_valid()
        
        user = serializer.save()
        assert user.phone == user_data['phone']
        assert user.employee_id == user_data['employee_id']

    def test_username_uniqueness_validation(self, user_data, basic_user):
        """15. Error de validación si el username ya existe en la DB."""
        # Usamos el username de un usuario que ya existe
        user_data['username'] = basic_user.username
        serializer = UserCreateSerializer(data=user_data)
        
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_email_required_and_format_validation(self, user_data):
        """16. Validar que el email sea obligatorio y tenga formato válido."""
        user_data['email'] = 'not-an-email'
        serializer = UserCreateSerializer(data=user_data)
        
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_create_serializer_fields_explicit(self):
        """17. Cumplimiento CNST-005: Campos explícitos permitidos para creación."""
        serializer = UserCreateSerializer()
        
        # Lista blanca de campos que el serializer permite procesar
        expected_fields = {
            'username', 'email', 'first_name', 'last_name', 
            'password', 'phone', 'position', 'employee_id'
        }
        assert set(serializer.fields.keys()).issubset(expected_fields)

    def test_strip_whitespace_in_credentials(self, user_data):
        """18. Validar limpieza de espacios accidentales en username y email."""
        user_data['username'] = '  cleanuser  '
        user_data['email'] = ' clean@example.com '
        
        serializer = UserCreateSerializer(data=user_data)
        assert serializer.is_valid()
        
        user = serializer.save()
        assert user.username == 'cleanuser'
        assert user.email == 'clean@example.com'

    def test_create_user_is_active_by_default(self, user_data):
        """19. Verificar que los nuevos usuarios se creen con is_active=True."""
        serializer = UserCreateSerializer(data=user_data)
        serializer.is_valid()
        user = serializer.save()
        
        assert user.is_active is True

    def test_employee_id_uniqueness_in_serializer(self, user_data, user_factory):
        """20. Validar que el serializer detecte IDs de empleado duplicados."""
        # Creamos un usuario previo con el mismo ID
        user_factory(username='existing', employee_id=user_data['employee_id'])
        
        serializer = UserCreateSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'employee_id' in serializer.errors

    def test_internal_save_error_handling(self, user_data):
        """21. Simular error de integridad de DB durante el guardado."""
        from django.db import IntegrityError
        from unittest.mock import patch
        
        serializer = UserCreateSerializer(data=user_data)
        serializer.is_valid()
        
        with patch('apps.users.serializers.UserCreateSerializer.save', side_effect=IntegrityError("DB Error")):
            with pytest.raises(IntegrityError):
                serializer.save()