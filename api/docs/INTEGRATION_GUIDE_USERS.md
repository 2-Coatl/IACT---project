# INTEGRATION GUIDE - apps/users

**App:** users  
**Versión:** 2.0.0  
**Fecha:** 2026-01-21  
**FASE 2:** Completada  

---

## 📋 OVERVIEW

Guía de integración para conectar `apps/users/` con otros módulos del sistema.

---

## 🔗 INTEGRACIÓN CON APPS

### 1. apps/access/ - RBAC Management

**Responsabilidades:**
- `apps/access/`: **Gestiona** RBAC (assign/revoke permissions)
- `apps/users/`: **Lee** RBAC (verifica permissions)

#### Leer Permissions desde apps/users/

```python
# apps/users/models.py

class User(AbstractUser):
    def has_function(self, function_id: str) -> bool:
        """
        Verifica si user tiene permission.
        
        Args:
            function_id: Namespace Django (ej: 'users.view')
        
        Returns:
            bool: True si tiene permission
        """
        if self.is_superuser:
            return True
        
        from apps.access.models import UserFunctionAssignment
        
        return UserFunctionAssignment.objects.filter(
            user=self,
            function__code=function_id,  # ← namespace Django
            is_active=True
        ).exists()
```

#### Mostrar Permissions en UserDetailSerializer

```python
# apps/users/serializers/user_serializer.py

class UserDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    
    def get_permissions(self, obj):
        """
        Lista permissions del usuario.
        
        Returns:
            list: ['users.view', 'users.edit', 'reports.view']
        """
        from apps.access.models import UserFunctionAssignment
        
        assignments = UserFunctionAssignment.objects.filter(
            user=obj,
            is_active=True
        ).select_related('function')
        
        return [a.function.code for a in assignments]
```

#### Asignar Permissions (en apps/access/)

```python
# apps/access/ maneja asignación

from apps.access.models import UserFunctionAssignment, Function
from apps.users.models import User

user = User.objects.get(id=1)
function = Function.objects.get(code='users.view')

# Asignar permission
UserFunctionAssignment.objects.create(
    user=user,
    function=function,
    is_active=True,
    granted_by=admin_user
)
```

---

### 2. apps/authentication/ - Login/Logout

**Responsabilidades:**
- `apps/authentication/`: Login, logout, password reset
- `apps/users/`: Password change (usuario autenticado)

#### Login (apps/authentication/)

```python
# apps/authentication/viewsets/auth_viewset.py

@action(detail=False, methods=['post'])
def login(self, request):
    """Login endpoint."""
    from apps.users.services.authentication_service import AuthenticationService
    
    result = AuthenticationService().authenticate_user(
        username=request.data['username'],
        password=request.data['password']
    )
    
    # Crear sesión en SessionHistory
    from apps.users.models import SessionHistory
    SessionHistory.objects.create(
        user=result['user'],
        login_at=timezone.now(),
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        is_active=True
    )
    
    return Response(result)
```

#### Password Change (apps/users/)

```python
# apps/users/viewsets/auth_viewset.py

@action(detail=False, methods=['post'])
def change_password(self, request):
    """Change password (authenticated user)."""
    from apps.users.services.password_service import PasswordService
    
    PasswordService().change_password(
        user=request.user,
        old_password=request.data['old_password'],
        new_password=request.data['new_password']
    )
    
    return Response({'detail': 'Password changed'})
```

---

### 3. apps/core/ - Shared Components

#### Usar RequiresFunctionPermission

```python
# apps/users/viewsets/user_viewset.py

from apps.core.permissions import RequiresFunctionPermission

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    function_map = {
        'list': 'users.view',
        'create': 'users.create',
    }
```

#### Usar SoftDeleteMixin (desde apps/utils/)

```python
# apps/users/models.py

from apps.utils.mixins import SoftDeleteMixin

class User(AbstractUser, SoftDeleteMixin):
    # Heredar soft delete capabilities
    pass

# Uso
user.delete()  # Soft delete (is_deleted=True)
user.hard_delete()  # Hard delete (real DELETE)
```

---

### 4. apps/utils/ - Validators

#### Reutilizar Validators

```python
# apps/users/validators.py

from apps.utils.validators import (
    validate_email,
    validate_phone_number
)

# Reutilizar en models
class User(AbstractUser):
    email = models.EmailField(validators=[validate_email])
    phone = models.CharField(validators=[validate_phone_number])
```

---

## 🔌 INTEGRACIÓN VIA SIGNALS

### Auto-crear Profile y Settings

```python
# apps/users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-crear UserProfile cuando se crea User."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    """Auto-crear UserSettings cuando se crea User."""
    if created:
        UserSettings.objects.create(user=instance)
```

### Registrar en apps.py

```python
# apps/users/apps.py

class UsersConfig(AppConfig):
    name = 'apps.users'
    
    def ready(self):
        import apps.users.signals  # Registrar signals
```

---

## 📡 INTEGRACIÓN VIA API

### Desde Frontend (React/Vue)

#### Listar Usuarios

```javascript
// GET /api/users/
const response = await fetch('/api/users/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  }
});

const users = await response.json();
// { results: [...], count: 100, next: '...', previous: '...' }
```

#### Crear Usuario

```javascript
// POST /api/users/
const response = await fetch('/api/users/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'jdoe',
    email: 'jdoe@company.com',
    password: 'SecurePass123!',
    password_confirm: 'SecurePass123!',
    first_name: 'John',
    last_name: 'Doe',
  })
});

const user = await response.json();
// { id: 1, username: 'jdoe', ... }
```

#### Actualizar Perfil

```javascript
// PATCH /api/profile/me/
const response = await fetch('/api/profile/me/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    bio: 'Python Developer',
    department: 'DEVELOPMENT',
  })
});
```

#### Subir Avatar

```javascript
// POST /api/profile/me/avatar/
const formData = new FormData();
formData.append('avatar', fileInput.files[0]);

const response = await fetch('/api/profile/me/avatar/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
  body: formData
});
```

---

## 🗄️ INTEGRACIÓN CON BASE DE DATOS

### ForeignKeys a User

```python
# Otro modelo que referencia User

from django.conf import settings

class Report(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Usar esto
        on_delete=models.CASCADE,
        related_name='reports'
    )
```

### Queries Optimizadas

```python
# Con select_related para profile/settings
users = User.objects.select_related(
    'profile',
    'settings'
).filter(is_active=True)

# Con prefetch_related para permissions
from apps.access.models import UserFunctionAssignment

users = User.objects.prefetch_related(
    'userfunctionassignment_set__function'
).all()
```

---

## 🧪 INTEGRACIÓN EN TESTS

### Usar Factories

```python
# tests/integration/myapp/test_integration.py

from tests.factories.user_factory import UserFactory

@pytest.mark.django_db
def test_my_integration():
    # Crear usuario de prueba
    user = UserFactory(
        username='testuser',
        email='test@example.com'
    )
    
    # Profile y settings auto-creados
    assert hasattr(user, 'profile')
    assert hasattr(user, 'settings')
```

### Mock Permissions

```python
from unittest.mock import patch
from apps.users.models import User

@pytest.mark.django_db
def test_with_permission(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    
    # Mock permission
    with patch.object(User, 'has_function', return_value=True):
        response = api_client.get('/api/users/')
    
    assert response.status_code == 200
```

---

## 📋 NAMESPACES DE PERMISSIONS

### Definidos en apps/users/

```python
# apps/users/constants.py

PERM_USERS_VIEW = 'users.view'
PERM_USERS_CREATE = 'users.create'
PERM_USERS_EDIT = 'users.edit'
PERM_USERS_DELETE = 'users.delete'
PERM_SESSIONS_VIEW = 'sessions.view'
```

### Crear Functions en apps/access/

```python
# Script para crear functions

from apps.access.models import Function, Module

# Crear módulo Users
module = Module.objects.create(
    code='USERS',
    name='Gestión de Usuarios',
    description='Módulo de administración de usuarios',
    is_active=True
)

# Crear functions
Function.objects.create(
    code='users.view',
    name='Ver Usuarios',
    description='Permite listar y ver detalles de usuarios',
    module=module,
    is_active=True
)

Function.objects.create(
    code='users.create',
    name='Crear Usuarios',
    description='Permite crear nuevos usuarios',
    module=module,
    is_active=True
)

# ... más functions
```

---

## 🔄 FLUJOS DE INTEGRACIÓN

### Flujo: Crear Usuario con Permissions

```
1. POST /api/users/ (apps/users)
   ↓
2. UserCreateSerializer valida
   ↓
3. UserService.create_user()
   ↓
4. User creado → signals auto-crean Profile/Settings
   ↓
5. Admin asigna permissions (apps/access)
   ↓
6. UserFunctionAssignment creado
   ↓
7. User puede usar endpoints protegidos
```

### Flujo: Login → Usar API → Logout

```
1. POST /api/auth/login/ (apps/authentication)
   ↓
2. AuthenticationService valida credentials
   ↓
3. SessionHistory creado (apps/users)
   ↓
4. JWT token retornado
   ↓
5. GET /api/users/ con token
   ↓
6. RequiresFunctionPermission verifica user.has_function()
   ↓
7. UserFunctionAssignment consultado (apps/access)
   ↓
8. Response 200 OK
   ↓
9. POST /api/auth/logout/ (apps/authentication)
   ↓
10. SessionHistory.logout_at actualizado
```

---

## ⚠️ CONSIDERACIONES

### Separación de Responsabilidades

```yaml
✅ HACER:
  - apps/users/ lee permissions vía has_function()
  - apps/users/ muestra permissions en serializers
  - apps/users/ valida permissions en viewsets

❌ NO HACER:
  - apps/users/ NO asigna permissions
  - apps/users/ NO revoca permissions
  - apps/users/ NO crea Functions
  
Responsable RBAC: apps/access/
```

### Circular Imports

```python
# ❌ EVITAR:
# apps/users/models.py
from apps.access.models import UserFunctionAssignment

# ✅ CORRECTO:
def has_function(self, function_id):
    # Import dentro de método
    from apps.access.models import UserFunctionAssignment
    return UserFunctionAssignment.objects...
```

### Performance

```python
# ❌ N+1 queries
for user in User.objects.all():
    print(user.profile.bio)  # Query por cada user

# ✅ select_related
users = User.objects.select_related('profile', 'settings')
for user in users:
    print(user.profile.bio)  # Sin queries adicionales
```

---

## 📚 RECURSOS

### Documentación

- **README:** [apps/users/README.md](../../apps/users/README.md)
- **API Docs:** [API_DOCUMENTATION_USERS.md](./API_DOCUMENTATION_USERS.md)
- **Changelog:** [apps/users/CHANGELOG.md](../../apps/users/CHANGELOG.md)

### Código de Ejemplo

- **Tests Integración:** `tests/integration/users/test_complete_flows.py`
- **Factories:** `tests/factories/user_factory.py`
- **Services:** `apps/users/services/`

---

## ✅ CHECKLIST DE INTEGRACIÓN

### Al integrar apps/users/ en nuevo módulo:

- [ ] Importar User desde `django.contrib.auth.get_user_model()`
- [ ] Usar ForeignKey a `settings.AUTH_USER_MODEL`
- [ ] Verificar permissions con `user.has_function()`
- [ ] Usar factories en tests
- [ ] Mock permissions en tests
- [ ] select_related profile/settings si necesario
- [ ] No gestionar RBAC desde tu módulo

---

**Última actualización:** 2026-01-21  
**Mantenido por:** IACT Development Team  
**App:** users
