"""
Serializers para sistema de acceso y módulos.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Module, UserModuleAccess, Function, UserFunctionAssignment

User = get_user_model()


class ModuleSerializer(serializers.ModelSerializer):
    """
    Serializer para módulos.
    
    Incluye información de jerarquía y estado.
    """
    
    level = serializers.IntegerField(read_only=True, source='get_level')
    is_root = serializers.BooleanField(read_only=True)
    parent_code = serializers.CharField(source='parent.code', read_only=True, allow_null=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = [
            'id',
            'code',
            'name',
            'description',
            'parent',
            'parent_code',
            'parent_name',
            'order',
            'icon',
            'url_path',
            'is_active',
            'level',
            'is_root',
            'children_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        """Contar hijos directos activos."""
        return obj.children.filter(is_active=True).count()


class ModuleTreeSerializer(serializers.ModelSerializer):
    """
    Serializer para módulos en estructura de árbol.
    
    Incluye hijos anidados recursivamente.
    """
    
    children = serializers.SerializerMethodField()
    level = serializers.IntegerField(read_only=True, source='get_level')
    
    class Meta:
        model = Module
        fields = [
            'id',
            'code',
            'name',
            'description',
            'icon',
            'url_path',
            'order',
            'is_active',
            'level',
            'children',
        ]
    
    def get_children(self, obj):
        """Obtener hijos recursivamente."""
        children = obj.children.filter(is_active=True).order_by('order', 'code')
        return ModuleTreeSerializer(children, many=True).data


class UserModuleAccessSerializer(serializers.ModelSerializer):
    """
    Serializer para accesos de usuarios a módulos.
    """
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)
    granted_by_username = serializers.CharField(
        source='granted_by.username',
        read_only=True,
        allow_null=True
    )
    revoked_by_username = serializers.CharField(
        source='revoked_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = UserModuleAccess
        fields = [
            'id',
            'user',
            'user_username',
            'module',
            'module_code',
            'module_name',
            'granted_at',
            'granted_by',
            'granted_by_username',
            'reason',
            'is_active',
            'revoked_at',
            'revoked_by',
            'revoked_by_username',
        ]
        read_only_fields = [
            'id',
            'granted_at',
            'granted_by',
            'revoked_at',
            'revoked_by',
        ]


class MyModulesSerializer(serializers.Serializer):
    """
    Serializer para respuesta de /my-modules/.
    
    Retorna módulos accesibles por el usuario en estructura de árbol.
    """
    
    modules = ModuleTreeSerializer(many=True, read_only=True)
    total_count = serializers.IntegerField(read_only=True)
    root_count = serializers.IntegerField(read_only=True)
