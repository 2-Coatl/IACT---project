# 📋 PLAN FASE 2 v2.2.0 - User Management (CORREGIDO)

**Versión:** 2.2.0  
**Fecha:** 2026-01-21  
**País:** México 🇲🇽  
**App:** apps/users/ ÚNICAMENTE

---

## 🔍 CORRECCIÓN vs v2.1.0

```yaml
PROBLEMA v2.1.0:
  ❌ Mezclaba responsabilidades de apps/users/ y apps/access/
  ❌ Incluía serializers de RBAC (Function, Module assignments)
  ❌ Incluía endpoints de gestión RBAC

SOLUCIÓN v2.2.0:
  ✅ apps/users/ SOLO gestión de usuarios
  ✅ apps/access/ maneja RBAC (ya existe)
  ✅ Separación clara de responsabilidades
```

---

## 🏗️ ARQUITECTURA - SCOPE DE apps/users/

```
┌─────────────────────────────────────────────────────┐
│                  apps/users/                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Models:                                            │
│  ├─ User (CustomUser)                              │
│  ├─ UserProfile (1-to-1)                           │
│  ├─ SessionHistory (auditoría)                     │
│  └─ UserSettings (preferencias)                    │
│                                                     │
│  Services: ✅ YA EXISTEN (1,511 líneas)            │
│  ├─ UserService (CRUD, activation)                 │
│  ├─ AuthenticationService (login, logout)          │
│  ├─ ProfileService (gestión de perfiles)           │
│  └─ PasswordService (cambio, reset)                │
│                                                     │
│  API: ⏳ POR IMPLEMENTAR                           │
│  ├─ UserViewSet (CRUD users)                       │
│  ├─ ProfileViewSet (gestión perfil)                │
│  ├─ AuthViewSet (login, logout, cambio pass)       │
│  └─ SessionHistoryViewSet (auditoría)              │
│                                                     │
│  Integration:                                       │
│  ├─ apps/access/ (RBAC) → Lee, NO gestiona         │
│  ├─ apps/audit/ (logs) → Usa para logging          │
│  └─ Django auth backend                            │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              apps/access/ (SEPARADO)                │
├─────────────────────────────────────────────────────┤
│  ✅ Ya existe - NO es parte de esta FASE           │
│                                                     │
│  Models:                                            │
│  ├─ Function (funciones atómicas)                  │
│  ├─ Module (módulos jerárquicos)                   │
│  ├─ UserFunctionAssignment                         │
│  └─ UserModuleAccess                               │
│                                                     │
│  API: (apps/access/ lo maneja)                     │
│  ├─ FunctionViewSet                                │
│  ├─ ModuleViewSet                                  │
│  └─ AssignmentViewSets                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 📋 PARTES (5 TOTAL - CORREGIDAS)

### ✅ PARTE 1: Models + Validators - COMPLETADA

```yaml
Estado: ✅ COMPLETADA
Tiempo: 1h
```

### ✅ PARTE 2: Correcciones - COMPLETADA

```yaml
Estado: ✅ COMPLETADA
Tiempo: 30 min
```

### ❌ PARTE 3: Services - OMITIDA

```yaml
Estado: ✅ YA EXISTEN (1,511 líneas)
```

---

### ⏳ PARTE 4: Serializers (1.5h) - CORREGIDA

**Objetivo:** Serializers SOLO para apps/users/

**11 Serializers:**

1. **UserSerializer** - Básico
   ```python
   class UserSerializer(serializers.ModelSerializer):
       full_name = serializers.CharField(source='get_full_name', read_only=True)
       avatar_url = serializers.SerializerMethodField()
       
       class Meta:
           model = User
           fields = [
               'id', 'username', 'email', 'first_name', 'last_name',
               'full_name', 'phone', 'position', 'avatar', 'avatar_url',
               'is_active', 'is_staff', 'date_joined', 'last_login',
           ]
           # ❌ NO incluir: functions, modules (eso es de apps/access)
   ```

2. **UserCreateSerializer**
   ```python
   class UserCreateSerializer(serializers.ModelSerializer):
       password = serializers.CharField(write_only=True)
       password_confirm = serializers.CharField(write_only=True)
       
       def create(self, validated_data):
           # Delega a UserService
           return UserService().create_user(**validated_data)
   ```

3. **UserUpdateSerializer**
   ```python
   class UserUpdateSerializer(serializers.ModelSerializer):
       class Meta:
           model = User
           fields = ['first_name', 'last_name', 'phone', 'position']
   ```

4. **UserListSerializer** - Lightweight
   ```python
   class UserListSerializer(serializers.ModelSerializer):
       full_name = serializers.CharField(source='get_full_name')
       
       class Meta:
           model = User
           fields = ['id', 'username', 'email', 'full_name', 
                    'position', 'is_active', 'last_login']
   ```

5. **UserDetailSerializer** - Completo
   ```python
   class UserDetailSerializer(serializers.ModelSerializer):
       profile = ProfileSerializer(read_only=True)
       settings = UserSettingsSerializer(read_only=True)
       
       class Meta:
           model = User
           fields = [
               'id', 'username', 'email', 'first_name', 'last_name',
               'phone', 'position', 'avatar',
               'is_active', 'is_staff', 'is_superuser',
               'date_joined', 'last_login',
               'profile', 'settings',
           ]
           # ❌ NO function_assignments, module_accesses
   ```

6. **ProfileSerializer**
   ```python
   class ProfileSerializer(serializers.ModelSerializer):
       avatar_url = serializers.CharField(read_only=True)
       
       class Meta:
           model = UserProfile
           fields = ['bio', 'department', 'avatar_url']
   ```

7. **UserSettingsSerializer**
   ```python
   class UserSettingsSerializer(serializers.ModelSerializer):
       class Meta:
           model = UserSettings
           fields = ['language', 'notifications_enabled']
   ```

8. **AvatarUploadSerializer**
   ```python
   class AvatarUploadSerializer(serializers.Serializer):
       avatar = serializers.ImageField()
       
       def update(self, instance, validated_data):
           return ProfileService().upload_avatar(
               instance, validated_data['avatar']
           )
   ```

9. **PasswordChangeSerializer**
   ```python
   class PasswordChangeSerializer(serializers.Serializer):
       old_password = serializers.CharField()
       new_password = serializers.CharField()
       new_password_confirm = serializers.CharField()
   ```

10. **UserActivationSerializer**
    ```python
    class UserActivationSerializer(serializers.Serializer):
        is_active = serializers.BooleanField()
        reason = serializers.CharField(required=False)
    ```

11. **SessionHistorySerializer** ← FALTABA
    ```python
    class SessionHistorySerializer(serializers.ModelSerializer):
        username = serializers.CharField(source='user.username')
        
        class Meta:
            model = SessionHistory
            fields = [
                'id', 'username', 'login_at', 'logout_at',
                'ip_address', 'user_agent', 'is_active',
            ]
            read_only_fields = '__all__'
    ```

**Archivos:**
```
apps/users/serializers/
├── __init__.py
├── user_serializer.py (1-5)
├── profile_serializer.py (6-8)
├── auth_serializer.py (9-10)
└── session_serializer.py (11)
```

**❌ NO CREAR (van en apps/access/):**
- UserFunctionAssignmentSerializer
- UserModuleAccessSerializer
- Endpoints de asignar/revocar funciones
- Endpoints de otorgar/revocar módulos

---

### ⏳ PARTE 5: ViewSets (2h) - CORREGIDA

**Objetivo:** API REST SOLO para apps/users/

**4 ViewSets:**

1. **UserViewSet**
   ```python
   class UserViewSet(viewsets.ModelViewSet):
       """
       CRUD de usuarios.
       
       Permissions:
       - USR_VIEW: list, retrieve
       - USR_CREATE: create
       - USR_EDIT: update, partial_update
       - USR_DELETE: destroy
       """
       queryset = User.objects.active()
       permission_classes = [IsAuthenticated, HasFunction]
       
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
           """Activar usuario (requiere USR_EDIT)."""
           pass
           
       @action(detail=True, methods=['post'])
       def deactivate(self, request, pk=None):
           """Desactivar usuario (requiere USR_EDIT)."""
           pass
   ```

2. **ProfileViewSet**
   ```python
   class ProfileViewSet(viewsets.GenericViewSet):
       """
       Gestión de perfil del usuario autenticado.
       
       Solo /me/ endpoints.
       """
       permission_classes = [IsAuthenticated]
       
       @action(detail=False, methods=['get', 'put', 'patch'])
       def me(self, request):
           """Ver/actualizar perfil propio."""
           pass
           
       @action(detail=False, methods=['post'], url_path='me/avatar')
       def upload_avatar(self, request):
           """Subir avatar."""
           pass
           
       @action(detail=False, methods=['delete'], url_path='me/avatar')
       def remove_avatar(self, request):
           """Eliminar avatar."""
           pass
   ```

3. **AuthViewSet**
   ```python
   class AuthViewSet(viewsets.GenericViewSet):
       """
       Autenticación y gestión de password.
       
       No requiere autenticación para login.
       """
       @action(detail=False, methods=['post'])
       def login(self, request):
           """Login (público)."""
           pass
           
       @action(detail=False, methods=['post'])
       def logout(self, request):
           """Logout (requiere autenticación)."""
           pass
           
       @action(detail=False, methods=['post'])
       def change_password(self, request):
           """Cambiar password (requiere autenticación)."""
           pass
           
       @action(detail=False, methods=['post'])
       def reset_password(self, request):
           """Reset password (público)."""
           pass
   ```

4. **SessionHistoryViewSet**
   ```python
   class SessionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
       """
       Auditoría de sesiones.
       
       Read-only, usuarios ven solo sus sesiones.
       Admins ven todas.
       """
       serializer_class = SessionHistorySerializer
       permission_classes = [IsAuthenticated]
       
       def get_queryset(self):
           if self.request.user.is_staff:
               return SessionHistory.objects.all()
           return SessionHistory.objects.filter(user=self.request.user)
   ```

**Endpoints resultantes:**
```
/api/users/
  GET    - Listar usuarios (USR_VIEW)
  POST   - Crear usuario (USR_CREATE)

/api/users/{id}/
  GET    - Detalle (USR_VIEW)
  PUT    - Actualizar (USR_EDIT)
  DELETE - Soft delete (USR_DELETE)

/api/users/{id}/activate/
  POST - Activar (USR_EDIT)

/api/users/{id}/deactivate/
  POST - Desactivar (USR_EDIT)

/api/profile/me/
  GET/PUT - Ver/actualizar perfil

/api/profile/me/avatar/
  POST/DELETE - Gestión avatar

/api/auth/login/
  POST - Login (público)

/api/auth/logout/
  POST - Logout

/api/auth/change_password/
  POST - Cambiar password

/api/sessions/
  GET - Mis sesiones (o todas si admin)

/api/sessions/{id}/
  GET - Detalle sesión
```

**Archivos:**
```
apps/users/viewsets/
├── __init__.py
├── user_viewset.py
├── profile_viewset.py
├── auth_viewset.py
└── session_viewset.py

apps/users/permissions.py (HasFunction)
apps/users/urls.py
```

**❌ NO CREAR (van en apps/access/):**
- /api/users/{id}/functions/ → apps/access/
- /api/users/{id}/assign_function/ → apps/access/
- /api/users/{id}/modules/ → apps/access/
- /api/users/{id}/grant_module/ → apps/access/

---

### ⏳ PARTE 6: Tests Unit (2h)

```yaml
Archivos:
  - test_models.py (User, Profile, Settings, Sessions)
  - test_validators.py (3 validators)
  - test_managers.py (CustomUserManager)
  - test_services.py (User, Profile, Password, Auth services)
  - test_serializers.py (11 serializers)
```

---

### ⏳ PARTE 7: Tests Int + Docs (1.5h)

```yaml
Archivos:
  - test_user_api.py (CRUD users)
  - test_profile_api.py (gestión perfil)
  - test_auth_api.py (login, logout, password)
  - test_sessions_api.py (auditoría)
  - docs/API_USERS.md
```

---

## 📊 RESUMEN

```yaml
Scope: apps/users/ ÚNICAMENTE
Partes: 5 (2 completadas, 3 pendientes)

✅ PARTE 1: Models + Validators (1h)
✅ PARTE 2: Correcciones (30 min)
❌ PARTE 3: Services (omitida - existen)
⏳ PARTE 4: Serializers (1.5h) - 11 serializers
⏳ PARTE 5: ViewSets (2h) - 4 viewsets
⏳ PARTE 6: Tests Unit (2h)
⏳ PARTE 7: Tests Int + Docs (1.5h)

Total: 9.5h
Progreso: 40% (2/5)
Restante: 8h

Responsabilidades claras:
  ✅ apps/users/ → Gestión de usuarios
  ✅ apps/access/ → RBAC (ya existe)
  ✅ apps/authentication/ → Login/lockout (ya existe)
  ✅ apps/audit/ → Auditoría (ya existe)
```

---

## 🎯 INTEGRACIÓN CON apps/access/

### Cómo apps/users/ usa RBAC (sin gestionarlo)

```python
# En permissions.py
class HasFunction(BasePermission):
    """Lee funciones, NO las gestiona."""
    def __init__(self, function_code):
        self.function_code = function_code
    
    def has_permission(self, request, view):
        # Lee de apps/access/
        from apps.access.models import UserFunctionAssignment
        
        return UserFunctionAssignment.objects.filter(
            user=request.user,
            function__code=self.function_code,
            is_active=True
        ).exists()
```

```python
# En serializers.py (OPCIONAL - solo lectura)
class UserDetailSerializer(serializers.ModelSerializer):
    # Puede MOSTRAR funciones (read-only)
    functions = serializers.SerializerMethodField()
    
    def get_functions(self, obj):
        """Solo lectura, NO gestión."""
        from apps.access.models import UserFunctionAssignment
        assignments = UserFunctionAssignment.objects.filter(
            user=obj, is_active=True
        )
        return [a.function.code for a in assignments]
    
    # Pero NO incluir métodos para asignar/revocar
```

**Gestión de RBAC:**
- Asignar funciones → apps/access/viewsets/
- Otorgar módulos → apps/access/viewsets/
- Listar funciones → apps/access/viewsets/

---

## 📄 CAMBIOS vs v2.1.0

```yaml
ELIMINADO de apps/users/:
  ❌ UserFunctionAssignmentSerializer
  ❌ UserModuleAccessSerializer
  ❌ /users/{id}/assign_function/ endpoint
  ❌ /users/{id}/revoke_function/ endpoint
  ❌ /users/{id}/grant_module/ endpoint
  ❌ /users/{id}/revoke_module/ endpoint

AGREGADO a apps/users/:
  ✅ SessionHistorySerializer (faltaba)
  ✅ SessionHistoryViewSet (faltaba)
  ✅ AuthViewSet (faltaba explícito)

CLARIFICADO:
  ✅ Separación de responsabilidades
  ✅ apps/users/ NO gestiona RBAC
  ✅ apps/access/ maneja RBAC completo
```

---

**Versión:** 2.2.0  
**Estado:** Corregido - Scope claro  
**Próximo:** PARTE 4 - Serializers (solo apps/users)
