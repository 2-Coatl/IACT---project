# 📋 ADDENDUM: Sistema de Permissions

**Plan:** v2.2.0  
**Fecha:** 2026-01-21  
**Tema:** Corrección del sistema de permissions

---

## ✅ SISTEMA CORRECTO DE PERMISSIONS

### Django Permissions con Namespaces (NO códigos)

```yaml
Formato correcto:
  ✅ 'reports.view' (namespace Django)
  ✅ 'dashboard.export.csv'
  ✅ 'users.create'
  ✅ 'users.edit'

Códigos referenciales (solo documentación):
  📝 RPT_VIEW → 'reports.view' (referencia)
  📝 DSH_EXP_CSV → 'dashboard.export.csv' (referencia)
  📝 USR_CREATE → 'users.create' (referencia)
```

---

## 🏗️ PATRÓN DE IMPLEMENTACIÓN

### 1. Permission Class (apps/core/permissions.py)

```python
class RequiresFunctionPermission(permissions.BasePermission):
    """
    Ya existe en apps/core/permissions.py
    
    Verifica función RBAC usando function_map del ViewSet.
    """
    
    def has_permission(self, request, view):
        # 1. Obtener action
        action = getattr(view, 'action', None)
        
        # 2. Obtener function_map del view
        function_map = getattr(view, 'function_map', {})
        
        # 3. Obtener permission namespace
        function_id = function_map[action]  # ej: 'users.view'
        
        # 4. Verificar usando User.has_function()
        return request.user.has_function(function_id)
```

### 2. ViewSet con function_map

```python
class UserViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios con RBAC."""
    
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    # ✅ function_map con namespaces Django
    function_map = {
        'list': 'users.view',          # ← namespace Django
        'retrieve': 'users.view',
        'create': 'users.create',
        'update': 'users.edit',
        'partial_update': 'users.edit',
        'destroy': 'users.delete',
        'activate': 'users.edit',      # Custom action
        'deactivate': 'users.edit',
    }
```

### 3. User.has_function() - Por implementar

```python
class User(AbstractUser, SoftDeleteMixin):
    
    def has_function(self, function_id):
        """
        Verifica si usuario tiene permiso.
        
        Args:
            function_id: Namespace Django (ej: 'users.view')
            
        Returns:
            bool: True si tiene el permiso
            
        Example:
            user.has_function('reports.view')  # ← namespace
            user.has_function('dashboard.export.csv')
        """
        # Superuser siempre tiene acceso
        if self.is_superuser:
            return True
        
        # Verificar en apps/access/
        from apps.access.models import UserFunctionAssignment
        
        return UserFunctionAssignment.objects.filter(
            user=self,
            function__code=function_id,  # ← 'users.view'
            is_active=True
        ).exists()
```

---

## 📋 CORRECCIONES EN PARTE 4 (Serializers)

### UserDetailSerializer - OPCIONAL mostrar permissions

```python
class UserDetailSerializer(serializers.ModelSerializer):
    """Detalle de usuario."""
    
    # OPCIONAL: Mostrar permissions (read-only)
    permissions = serializers.SerializerMethodField()
    
    def get_permissions(self, obj):
        """
        Lista de permissions del usuario.
        
        Returns:
            list: Namespaces Django ['users.view', 'reports.edit']
        """
        from apps.access.models import UserFunctionAssignment
        
        assignments = UserFunctionAssignment.objects.filter(
            user=obj,
            is_active=True
        ).select_related('function')
        
        # Retornar namespaces Django
        return [a.function.code for a in assignments]
        # Ejemplo: ['users.view', 'users.edit', 'reports.view']
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'position', 'avatar',
            'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login',
            'profile', 'settings',
            'permissions',  # ← OPCIONAL
        ]
```

---

## 📋 CORRECCIONES EN PARTE 5 (ViewSets)

### 1. UserViewSet

```python
class UserViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios."""
    
    queryset = User.objects.active()
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    # ✅ CORRECTO: namespaces Django
    function_map = {
        'list': 'users.view',
        'retrieve': 'users.view',
        'create': 'users.create',
        'update': 'users.edit',
        'partial_update': 'users.edit',
        'destroy': 'users.delete',
        'activate': 'users.edit',
        'deactivate': 'users.edit',
    }
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        else:
            return UserDetailSerializer
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activar usuario."""
        user = self.get_object()
        # Delegar a UserService
        UserService().activate_user(user.id)
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Desactivar usuario."""
        user = self.get_object()
        # Delegar a UserService
        UserService().deactivate_user(user.id)
        return Response({'status': 'deactivated'})
```

### 2. ProfileViewSet

```python
class ProfileViewSet(viewsets.GenericViewSet):
    """Gestión de perfil propio."""
    
    permission_classes = [IsAuthenticated]
    # NO necesita function_map (solo perfil propio)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Ver/actualizar perfil."""
        pass
    
    @action(detail=False, methods=['post'], url_path='me/avatar')
    def upload_avatar(self, request):
        """Subir avatar."""
        pass
```

### 3. AuthViewSet

```python
class AuthViewSet(viewsets.GenericViewSet):
    """Autenticación."""
    
    permission_classes = [AllowAny]  # Login es público
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login (público)."""
        pass
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout (requiere autenticación)."""
        self.permission_classes = [IsAuthenticated]
        pass
```

### 4. SessionHistoryViewSet

```python
class SessionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Auditoría de sesiones."""
    
    serializer_class = SessionHistorySerializer
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    # ✅ CORRECTO: namespace Django
    function_map = {
        'list': 'sessions.view',
        'retrieve': 'sessions.view',
    }
    
    def get_queryset(self):
        """Usuarios ven solo sus sesiones, staff ve todas."""
        if self.request.user.is_staff:
            return SessionHistory.objects.all()
        return SessionHistory.objects.filter(user=self.request.user)
```

---

## 📊 NAMESPACES PARA apps/users/

### Permissions requeridos

```python
# apps/users/constants.py (REFERENCIA)

# Namespaces Django (lo que se usa en código)
PERM_USERS_VIEW = 'users.view'
PERM_USERS_CREATE = 'users.create'
PERM_USERS_EDIT = 'users.edit'
PERM_USERS_DELETE = 'users.delete'
PERM_SESSIONS_VIEW = 'sessions.view'

# Códigos referenciales (solo documentación)
# USR_VIEW → 'users.view'
# USR_CREATE → 'users.create'
# USR_EDIT → 'users.edit'
# USR_DELETE → 'users.delete'
# SESS_VIEW → 'sessions.view'
```

---

## ✅ RESUMEN DE CAMBIOS

```yaml
ANTES (v2.1.0 - INCORRECTO):
  ❌ HasFunction('USR_VIEW') - códigos duros
  ❌ Confusión entre códigos y namespaces

AHORA (v2.2.0 - CORRECTO):
  ✅ RequiresFunctionPermission + function_map
  ✅ function_map = {'list': 'users.view'} - namespaces
  ✅ user.has_function('users.view') - namespace Django
  ✅ Códigos solo en constants (referencia)
  
Patrón existente:
  ✅ Ya usado en apps/core/permissions.py
  ✅ Consistente con sistema actual
  ✅ Namespaces Django estándar
```

---

## 🎯 IMPLEMENTACIÓN EN PARTE 5

### Archivos a crear

```
apps/users/viewsets/
├── __init__.py
├── user_viewset.py
│   └── function_map = {'list': 'users.view', ...}
├── profile_viewset.py
│   └── Sin function_map (perfil propio)
├── auth_viewset.py
│   └── AllowAny (login público)
└── session_viewset.py
    └── function_map = {'list': 'sessions.view'}

apps/users/permissions.py
└── Reutilizar RequiresFunctionPermission de core

apps/users/constants.py
└── Agregar PERM_* con namespaces
```

---

**Corrección:** Sistema de permissions con namespaces Django  
**Patrón:** RequiresFunctionPermission + function_map  
**Namespaces:** 'users.view', 'users.create', etc.  
**Códigos:** Solo referencia en constants
