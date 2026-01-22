"""
Serializers para User model.

CLEAN_CODE v3.0.1: Serializers separados por responsabilidad.
SOLID SRP: Cada serializer un propósito específico.

FASE 2 PARTE 4: Serializers de apps/users/
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.users.validators import validate_password_strength

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer básico de User.
    
    Para uso general en relaciones y listados básicos.
    
    Fields:
    - Info básica: id, username, email, nombres
    - Contacto: phone
    - Trabajo: position
    - Avatar: avatar, avatar_url
    - Estado: is_active, is_staff
    - Fechas: date_joined, last_login
    
    Example:
        user = User.objects.get(id=1)
        serializer = UserSerializer(user)
        data = serializer.data
        # {'id': 1, 'username': 'jdoe', 'full_name': 'John Doe', ...}
    """
    
    full_name = serializers.CharField(
        source='get_full_name',
        read_only=True,
        help_text='Nombre completo del usuario'
    )
    
    avatar_url = serializers.SerializerMethodField(
        help_text='URL del avatar o default'
    )
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'position',
            'avatar',
            'avatar_url',
            'is_active',
            'is_staff',
            'date_joined',
            'last_login',
        ]
        read_only_fields = [
            'id',
            'date_joined',
            'last_login',
        ]
    
    def get_avatar_url(self, obj):
        """
        Obtiene URL del avatar.
        
        Returns:
            str: URL del avatar o None
        """
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.avatar_url
        return None


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer para listado de usuarios (lightweight).
    
    Optimizado para listados con muchos registros.
    Solo campos esenciales.
    
    Fields:
    - Identificación: id, username, email
    - Nombre: full_name
    - Trabajo: position
    - Estado: is_active
    - Última actividad: last_login
    
    Example:
        users = User.objects.active()
        serializer = UserListSerializer(users, many=True)
        # [{'id': 1, 'username': 'jdoe', ...}, ...]
    """
    
    full_name = serializers.CharField(
        source='get_full_name',
        read_only=True
    )
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'full_name',
            'position',
            'is_active',
            'last_login',
        ]
        read_only_fields = '__all__'




    
    def get_permissions(self, obj):
        """
        Obtiene permissions del usuario.
        
        Lee de apps/access (NO gestiona).
        
        Returns:
            list: Namespaces Django ['users.view', 'reports.edit']
        """
        try:
            from apps.access.models import UserFunctionAssignment
            
            assignments = UserFunctionAssignment.objects.filter(
                user=obj,
                is_active=True
            ).select_related('function')
            
            # Retornar namespaces Django
            return [a.function.code for a in assignments]
        except Exception:
            # Si apps/access no disponible, retornar vacío
            return []


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear nuevo usuario.
    
    Incluye validación de password y confirmación.
    Delega creación a UserService.
    
    Fields:
    - Requeridos: username, email, password
    - Confirmación: password_confirm
    - Opcionales: first_name, last_name, phone, position
    
    Validations:
    - Passwords coinciden
    - Password fuerte (8 chars, mayús/minús/número/especial)
    - Username único
    - Email único
    
    Example:
        data = {
            'username': 'jdoe',
            'email': 'jdoe@company.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
        }
        serializer = UserCreateSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Password del usuario (min 8 chars, mayús/minús/número/especial)'
    )
    
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Confirmación de password'
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone',
            'position',
        ]
    
    def validate(self, data):
        """
        Validar passwords coinciden y fortaleza.
        
        Args:
            data: Datos validados
            
        Returns:
            dict: Datos validados
            
        Raises:
            ValidationError: Si passwords no coinciden o débil
        """
        # Validar passwords coinciden
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden'
            })
        
        # Validar fortaleza de password
        try:
            validate_password_strength(data['password'])
        except Exception as e:
            raise serializers.ValidationError({
                'password': str(e)
            })
        
        return data
    
    def create(self, validated_data):
        """
        Crear usuario.
        
        Delega a UserService para lógica de negocio.
        
        Args:
            validated_data: Datos validados
            
        Returns:
            User: Usuario creado
        """
        # Remover password_confirm
        validated_data.pop('password_confirm')
        
        # Delegar a UserService
        from apps.users.services.user_service import UserService
        
        user = UserService().create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone'),
            position=validated_data.get('position'),
        )
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar usuario existente.
    
    Solo campos editables (NO username, email, password).
    
    Fields editables:
    - Nombres: first_name, last_name
    - Contacto: phone
    - Trabajo: position
    
    Para cambiar password: usar PasswordChangeSerializer
    Para cambiar email/username: requiere proceso especial
    
    Example:
        user = User.objects.get(id=1)
        data = {'first_name': 'Jane', 'position': 'MANAGER'}
        serializer = UserUpdateSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
    """
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone',
            'position',
        ]
    
    def update(self, instance, validated_data):
        """
        Actualizar usuario.
        
        Delega a UserService para lógica de negocio.
        
        Args:
            instance: Usuario existente
            validated_data: Datos validados
            
        Returns:
            User: Usuario actualizado
        """
        from apps.users.services.user_service import UserService
        
        user = UserService().update_user(
            user_id=instance.id,
            **validated_data
        )
        
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para usuario con todas sus relaciones.

    Serializer completo que incluye toda la información del usuario
    y sus relaciones, incluyendo permisos y funciones asignadas.

    Ideal para endpoints de detalle y profiles.

    Fields:
    - Info básica: id, username, email, nombres
    - Contacto: phone
    - Trabajo: position
    - Avatar: avatar, avatar_url
    - Estado: is_active, is_staff
    - Fechas: date_joined, last_login
    - Relaciones: permissions (readonly desde apps/access)

    Example:
        user = User.objects.get(id=1)
        serializer = UserDetailSerializer(user)
        data = serializer.data
        # {
        #     'id': 1,
        #     'username': 'jdoe',
        #     'email': 'jdoe@company.com',
        #     'full_name': 'John Doe',
        #     'phone': '+1234567890',
        #     'position': 'AGENT',
        #     'avatar': 'https://...',
        #     'avatar_url': 'https://...',
        #     'is_active': True,
        #     'is_staff': False,
        #     'date_joined': '2024-01-15T10:30:00Z',
        #     'last_login': '2024-01-20T15:45:30Z',
        #     'permissions': ['users.view', 'reports.view']
        # }
    """

    full_name = serializers.CharField(
        source='get_full_name',
        read_only=True,
        help_text='Nombre completo del usuario'
    )

    avatar_url = serializers.SerializerMethodField(
        help_text='URL del avatar o default'
    )

    permissions = serializers.SerializerMethodField(
        help_text='Permisos/funciones asignados (desde apps/access)'
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'position',
            'avatar',
            'avatar_url',
            'is_active',
            'is_staff',
            'date_joined',
            'last_login',
            'permissions',
        ]
        read_only_fields = [
            'id',
            'date_joined',
            'last_login',
            'permissions',
        ]

    def get_avatar_url(self, obj):
        """
        Obtiene URL del avatar.

        Returns:
            str: URL del avatar o None
        """
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.avatar_url
        return None

    def get_permissions(self, obj):
        """
        Obtiene permissions/funciones del usuario.

        Lee de apps/access (NO gestiona).

        Returns:
            list: Códigos de funciones asignadas ['users.view', 'reports.edit']
        """
        try:
            from apps.access.models import UserFunctionAssignment

            assignments = UserFunctionAssignment.objects.filter(
                user=obj,
                is_active=True
            ).select_related('function')

            # Retornar códigos de funciones
            return [a.function.code for a in assignments]
        except Exception:
            # Si apps/access no disponible, retornar vacío
            return []


# ============================================================================
# RESUMEN USER SERIALIZERS
#
# Total: 5 serializers
#
# Serializers:
#   ✅ UserSerializer - Básico para uso general
#   ✅ UserListSerializer - Lightweight para listados
#   ✅ UserDetailSerializer - Completo con relaciones
#   ✅ UserCreateSerializer - Crear con validación password
#   ✅ UserUpdateSerializer - Actualizar campos editables
#
# Responsabilidades:
#   ✅ Validación de datos
#   ✅ Serialización/Deserialización
#   ✅ Delegación a services
#
# NO incluye:
#   ❌ Gestión de RBAC (apps/access)
#   ❌ Cambio de password (auth_serializer.py)
#   ❌ Gestión de avatar (profile_serializer.py)
#
# Principios:
#   ✅ SRP: Cada serializer un propósito
#   ✅ DRY: Delegar a services
#   ✅ Clean Code: Nombres auto-documentados
# ============================================================================