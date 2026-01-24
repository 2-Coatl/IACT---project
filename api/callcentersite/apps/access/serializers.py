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


# ====================================================================================
# RBAC v6.0.0 - Function Serializers
# ====================================================================================

class FunctionSerializer(serializers.ModelSerializer):
    """
    Serializer para funciones RBAC v6.0.0.
    
    RBAC v6.0.0: Usa permission_django (namespaces) como identificador.
    
    Read-only fields:
    - id, created_at, updated_at
    
    Fields:
    - permission_django: Namespace Django (PK funcional)
    - code: Código legacy (para compatibilidad)
    - module: Módulo al que pertenece
    - name: Nombre descriptivo
    - description: Descripción de la función
    - status: activo, planificado, deprecado
    - is_active: Activo/inactivo
    
    Examples:
        >>> func = Function.objects.get(permission_django='users.view')
        >>> serializer = FunctionSerializer(func)
        >>> serializer.data['permission_django']
        'users.view'
        >>> serializer.data['status']
        'activo'
    """
    
    class Meta:
        model = Function
        fields = [
            'id',
            'permission_django',
            'code',
            'module',
            'name',
            'description',
            'status',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FunctionListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de funciones.
    
    Solo incluye campos esenciales para listas.
    """
    
    class Meta:
        model = Function
        # CLEAN CODE: Explicit is better than implicit (PEP 20)
        fields = (
            'id',
            'permission_django',
            'code',
            'name',
            'module',
            'status',
            'is_active',
        )
        # List views are typically read-only
        read_only_fields = fields


class UserFunctionAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer para asignaciones de funciones a usuarios.
    
    RBAC v6.0.0: Gestión de asignaciones con namespaces.
    
    Incluye información enriquecida:
    - user_username: Username del usuario
    - function_namespace: Namespace de la función
    - function_name: Nombre de la función
    - assigned_by_username: Username de quien asignó
    
    Read-only fields:
    - id, assigned_at
    - Relaciones enriched (user_username, etc)
    
    Examples:
        >>> assignment = UserFunctionAssignment.objects.first()
        >>> serializer = UserFunctionAssignmentSerializer(assignment)
        >>> serializer.data['function_namespace']
        'users.view'
        >>> serializer.data['is_active']
        True
    """
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    function_namespace = serializers.CharField(
        source='function.permission_django',
        read_only=True
    )
    function_name = serializers.CharField(source='function.name', read_only=True)
    function_module = serializers.CharField(source='function.module', read_only=True)
    assigned_by_username = serializers.CharField(
        source='assigned_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = UserFunctionAssignment
        fields = [
            'id',
            'user',
            'user_username',
            'user_full_name',
            'function',
            'function_namespace',
            'function_name',
            'function_module',
            'assigned_at',
            'assigned_by',
            'assigned_by_username',
            'reason',
            'is_active',
        ]
        read_only_fields = [
            'id',
            'assigned_at',
            'assigned_by',
        ]


class AssignFunctionSerializer(serializers.Serializer):
    """
    Serializer para asignar función a usuario.
    
    Input:
    - user: ID del usuario (required)
    - function: ID de la función (required)
    - reason: Razón de la asignación (optional)
    
    Process:
    - Valida que user existe
    - Valida que function existe y está activa
    - Crea UserFunctionAssignment
    - assigned_by se obtiene del request.user
    
    Examples:
        >>> data = {
        ...     'user': 1,
        ...     'function': 2,
        ...     'reason': 'Usuario de soporte'
        ... }
        >>> serializer = AssignFunctionSerializer(data=data)
        >>> serializer.is_valid()
        True
    """
    
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
        help_text='ID del usuario'
    )
    function = serializers.PrimaryKeyRelatedField(
        queryset=Function.objects.filter(is_active=True, status='activo'),
        required=True,
        help_text='ID de la función'
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        help_text='Razón de la asignación'
    )
    
    def validate(self, attrs):
        """Valida que no exista asignación activa duplicada."""
        user = attrs['user']
        function = attrs['function']
        
        # Verificar si ya existe asignación activa
        exists = UserFunctionAssignment.objects.filter(
            user=user,
            function=function,
            is_active=True
        ).exists()
        
        if exists:
            raise serializers.ValidationError({
                'function': f'Usuario ya tiene asignada la función {function.permission_django}'
            })
        
        return attrs


class RevokeFunctionSerializer(serializers.Serializer):
    """
    Serializer para revocar función de usuario.
    
    Input:
    - assignment: ID de la asignación (required)
    
    Process:
    - Valida que assignment existe y está activa
    - Marca is_active=False
    
    Examples:
        >>> data = {'assignment': 1}
        >>> serializer = RevokeFunctionSerializer(data=data)
        >>> serializer.is_valid()
        True
    """
    
    assignment = serializers.PrimaryKeyRelatedField(
        queryset=UserFunctionAssignment.objects.filter(is_active=True),
        required=True,
        help_text='ID de la asignación a revocar'
    )


class MyFunctionsSerializer(serializers.Serializer):
    """
    Serializer para respuesta de /my-functions/.
    
    Retorna funciones del usuario autenticado.
    
    Fields:
    - functions: Lista de namespaces
    - count: Total de funciones
    - user: Datos del usuario
    
    Examples:
        >>> data = {
        ...     'functions': ['users.view', 'calls.view'],
        ...     'count': 2,
        ...     'user': {'id': 1, 'username': 'john'}
        ... }
        >>> serializer = MyFunctionsSerializer(data)
    """
    
    functions = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text='Lista de namespaces de funciones'
    )
    count = serializers.IntegerField(
        read_only=True,
        help_text='Total de funciones activas'
    )
    user = serializers.DictField(
        read_only=True,
        help_text='Datos básicos del usuario'
    )


# ====================================================================================
# REMOVED - FASE A DT-002
# ====================================================================================
#
# UserServiceAccess Serializers (eliminados 2026-01-21):
#   - UserServiceAccessSerializer
#   - UserServiceAccessListSerializer
#   - GrantAccessSerializer
#   - BulkGrantAccessSerializer
#   - RevokeAccessSerializer
#
# Razón: UserServiceAccess eliminado, reemplazado por RBAC puro
# Ver: apps/access/models.py (comentario REMOVED)
# ====================================================================================


# ====================================================================================
# RESUMEN SERIALIZERS
# 
# Total Serializers: 15
# 
# Módulos (sistema jerárquico):
#   ✅ ModuleSerializer - Módulo con info de jerarquía
#   ✅ ModuleTreeSerializer - Módulo en estructura de árbol
#   ✅ UserModuleAccessSerializer - Accesos de usuarios a módulos
#   ✅ MyModulesSerializer - Respuesta /my-modules/
# 
# RBAC v6.0.0 (funciones con namespaces):
#   ✅ FunctionSerializer - Función completa
#   ✅ FunctionListSerializer - Función simplificada (listas)
#   ✅ UserFunctionAssignmentSerializer - Asignación de función
#   ✅ AssignFunctionSerializer - Input para asignar función
#   ✅ RevokeFunctionSerializer - Input para revocar función
#   ✅ MyFunctionsSerializer - Respuesta /my-functions/
# 
# RBAC v6.0.0 Características:
#   ✅ Usa permission_django (namespaces)
#   ✅ Campos enriched (user_username, function_namespace)
#   ✅ Validaciones de duplicados
#   ✅ Status filtering (solo activas)
#   ✅ Documentación completa
# 
# Principios:
#   ✅ DRY: Validaciones reutilizables
#   ✅ SRP: Cada serializer una responsabilidad
#   ✅ Clean Code: Nombres descriptivos
#   ✅ RBAC v6.0.0: Namespaces Django
# 
# Líneas: ~400
# ====================================================================================
