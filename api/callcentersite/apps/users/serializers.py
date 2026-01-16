from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()
from apps.access.models import UserFunctionAssignment


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para User.
    
    CNST-005: fields explicitos (NO __all__)
    
    Incluye funciones asignadas via RBAC.
    """
    
    functions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'date_joined',
            'functions',
        ]
        read_only_fields = ['id', 'date_joined', 'functions']
    
    def get_functions(self, obj):
        """
        Obtener funciones asignadas al usuario.
        
        Returns:
            list: Lista de codigos de funciones
        """
        assignments = UserFunctionAssignment.get_user_functions(obj)
        return [a.function.code for a in assignments]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear usuario.
    
    CNST-005: Password hasheado, min_length validado.
    """
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        ]
    
    def create(self, validated_data):
        """
        Crear usuario con password hasheado.
        
        Args:
            validated_data: Datos validados
            
        Returns:
            User: Usuario creado
        """
        return User.objects.create_user(**validated_data)
