# 🧹 CLEAN CODE v3.0.1 - Corrección de Nomenclatura

## INFORMACIÓN

| Atributo | Valor |
|---|---|
| **Fecha** | 2026-01-21 |
| **Tipo** | CORRECCIÓN CLEAN CODE |
| **Base** | CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1 |

---

## 🚨 VIOLACIONES IDENTIFICADAS

### 1. Acrónimos en Nombres de Clases

```python
# ❌ INCORRECTO - Usa acrónimo RBAC
class RBACService:
    """Servicio de control de acceso basado en funciones."""
    pass

# ❌ Problemas:
# - RBAC es un acrónimo técnico
# - No es universalmente conocido
# - Reduce legibilidad
# - Viola CLEAN_CODE v3.0.1
```

### 2. Sufijo "Service" Genérico

```python
# ⚠️ MEJORABLE - "Service" es muy genérico
class SomethingService:
    pass

# ✅ MEJOR - Describe la acción
class SomethingManager:      # Gestiona algo
class SomethingValidator:    # Valida algo
class SomethingChecker:      # Verifica algo
class SomethingProvider:     # Provee algo
```

---

## ✅ NOMBRES CORRECTOS

### Principios CLEAN_CODE v3.0.1

```yaml
Reglas para nombres de clases:
  1. PascalCase (CapitalizedWords)
  2. Nombres descriptivos, no acrónimos
  3. Describen responsabilidad clara
  4. Sustantivos (entities) o sustantivo+verbo (services)
  5. Evitar prefijos/sufijos genéricos cuando hay mejor opción
  6. Inglés técnico

Ejemplos buenos:
  ✅ PermissionService         # Gestiona permisos
  ✅ AccessControlService      # Control de acceso
  ✅ UserAuthenticator         # Autentica usuarios
  ✅ PasswordValidator         # Valida passwords
  ✅ SessionManager            # Gestiona sesiones

Ejemplos malos:
  ❌ RBACService              # Acrónimo
  ❌ ACLManager               # Acrónimo
  ❌ UMService                # Acrónimo + genérico
  ❌ DataService              # Muy genérico
  ❌ HelperService            # No dice qué hace
```

---

## 🔧 CORRECCIONES APLICADAS

### apps/access/ - Sistema de Permisos

```python
# ❌ ANTES (incorrecto)
class RBACService:
    """Servicio principal de RBAC."""
    
    def has_function(self, user, permission):
        ...

# ✅ DESPUÉS (correcto)
class PermissionService:
    """
    Servicio de validación de permisos basados en funciones.
    
    Responsabilidades:
    - Validar permisos de usuario
    - Gestionar cache de permisos
    - Proveer API has_function()
    """
    
    def has_function(self, user: User, permission: str) -> bool:
        """Verifica si usuario tiene permiso específico."""
        ...
    
    def get_user_permissions(self, user: User) -> Set[str]:
        """Obtiene set de permisos del usuario."""
        ...
    
    def invalidate_user_cache(self, user: User) -> None:
        """Invalida cache de permisos."""
        ...
```

**Razón:** `PermissionService` es claro, descriptivo, sin acrónimos.

---

### apps/access/ - Otros Services

```python
# ✅ GroupService - CORRECTO (ya estaba bien)
class GroupService:
    """Servicio de gestión de grupos de funciones."""
    
    def assign_user_to_group(self, user, group):
        ...
    
    def remove_user_from_group(self, user, group):
        ...

# ✅ PermissionCacheService - CORRECTO (descriptivo)
class PermissionCacheService:
    """Servicio de cache de permisos."""
    
    def cache_user_permissions(self, user):
        ...
    
    def invalidate_cache(self, user):
        ...
```

---

### apps/authentication/ - Services

```python
# ✅ AuthenticationService - CORRECTO
class AuthenticationService:
    """Servicio de autenticación de usuarios."""
    
    def login_user(self, request, username, password):
        ...
    
    def logout_user(self, request):
        ...

# ✅ RecoveryService - CORRECTO
class RecoveryService:
    """Servicio de recuperación de contraseñas."""
    
    def verify_security_answers(self, user, answers):
        ...
    
    def reset_password_by_questions(self, user, new_password):
        ...

# ✅ LockoutService - CORRECTO
class LockoutService:
    """Servicio de bloqueo de cuentas."""
    
    def is_locked(self, username):
        ...
    
    def record_failed_attempt(self, username):
        ...

# ✅ SessionService - CORRECTO
class SessionService:
    """Servicio de gestión de sesiones."""
    
    def get_active_sessions(self, user):
        ...
    
    def invalidate_session(self, session_key):
        ...
```

---

### apps/users/ - Services

```python
# ✅ UserService - CORRECTO
class UserService:
    """Servicio de gestión de usuarios."""
    
    def create_user(self, data):
        ...
    
    def update_user(self, user_id, data):
        ...
    
    def delete_user(self, user_id):
        ...

# ✅ ProfileService - CORRECTO
class ProfileService:
    """Servicio de gestión de perfiles."""
    
    def update_profile(self, user, data):
        ...
    
    def upload_avatar(self, user, file):
        ...

# ✅ PasswordService - CORRECTO
class PasswordService:
    """Servicio de gestión de contraseñas."""
    
    def change_password(self, user, old_password, new_password):
        ...
    
    def validate_password_strength(self, password):
        ...
```

---

### apps/alerts/ - Services

```python
# ✅ AlertService - CORRECTO
class AlertService:
    """Servicio de gestión de alertas internas."""
    
    def send_message(self, sender, recipients, subject, body):
        ...
    
    def mark_as_read(self, message_id, user):
        ...
    
    def auto_archive_old_messages(self):
        ...

# ✅ ConfigurationService - CORRECTO
class ConfigurationService:
    """Servicio de configuración de alertas."""
    
    def create_alert_rule(self, event_type, condition):
        ...
    
    def trigger_alert(self, configuration, data):
        ...

# ✅ SubscriptionService - CORRECTO
class SubscriptionService:
    """Servicio de gestión de suscripciones."""
    
    def subscribe_user(self, user, configuration):
        ...
    
    def get_subscribers(self, configuration):
        ...
```

---

## 📝 PATRÓN DE NOMENCLATURA

### Services - Naming Pattern

```python
# PATRÓN: [Entidad/Dominio] + Service
# Donde Service describe: gestión, validación, procesamiento

# Domain Services (entidad + Service)
class UserService:           # Gestiona usuarios
class GroupService:          # Gestiona grupos  
class AlertService:          # Gestiona alertas
class SessionService:        # Gestiona sesiones

# Specialized Services (acción + Service)
class AuthenticationService: # Autentica
class RecoveryService:       # Recupera
class LockoutService:        # Bloquea
class PermissionService:     # Valida permisos
class SubscriptionService:   # Gestiona suscripciones
class ConfigurationService:  # Configura

# Cache Services
class PermissionCacheService:  # Cache de permisos
# O alternativamente:
class PermissionCache:         # Más conciso
```

---

## 🔄 CAMBIOS EN IMPORTS

### Antes (incorrecto)

```python
# apps/access/services/__init__.py
from apps.access.services.rbac import RBACService
from apps.access.services.group import GroupService

__all__ = ['RBACService', 'GroupService']
```

```python
# apps/dashboard/viewsets.py
from apps.access.services import RBACService

class DashboardViewSet(viewsets.ViewSet):
    def list(self, request):
        rbac = RBACService()
        if not rbac.has_function(request.user, 'dashboard.view'):
            raise PermissionDenied()
```

### Después (correcto)

```python
# apps/access/services/__init__.py
from apps.access.services.permission import PermissionService
from apps.access.services.group import GroupService

__all__ = ['PermissionService', 'GroupService']
```

```python
# apps/dashboard/viewsets.py
from apps.access.services import PermissionService

class DashboardViewSet(viewsets.ViewSet):
    def list(self, request):
        permission_service = PermissionService()
        if not permission_service.has_function(request.user, 'dashboard.view'):
            raise PermissionDenied()
```

---

## 🔧 DECORATORS Y HELPERS

```python
# apps/access/decorators.py

# ✅ CORRECTO - Funciones descriptivas
def require_permission(permission: str):
    """
    Decorator que requiere permiso específico.
    
    Args:
        permission: Permission Django (reports.view, audit.export)
    
    Example:
        @require_permission('reports.view')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            service = PermissionService()
            
            if not service.has_function(request.user, permission):
                raise PermissionDenied()
            
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def require_any_permission(*permissions):
    """Requiere al menos uno de los permisos (OR)."""
    ...


def require_all_permissions(*permissions):
    """Requiere todos los permisos (AND)."""
    ...
```

---

## 📋 RESUMEN DE CAMBIOS

```yaml
CAMBIOS PRINCIPALES:

1. Renombrar clase:
   ❌ RBACService → ✅ PermissionService

2. Actualizar imports:
   - apps/access/services/__init__.py
   - apps/access/services/rbac.py → permission.py
   - Todos los archivos que importan RBACService

3. Actualizar instancias:
   - rbac = RBACService() → permission_service = PermissionService()
   - O usar nombre corto: permissions = PermissionService()

4. Mantener API pública:
   - has_function(user, permission) ✅ sin cambios
   - get_user_permissions(user) ✅ sin cambios
   - invalidate_user_cache(user) ✅ sin cambios

SERVICIOS VALIDADOS (ya correctos):
   ✅ UserService
   ✅ ProfileService
   ✅ PasswordService
   ✅ AuthenticationService
   ✅ RecoveryService
   ✅ LockoutService
   ✅ SessionService
   ✅ GroupService
   ✅ AlertService
   ✅ ConfigurationService
   ✅ SubscriptionService
   ✅ PermissionCacheService
```

---

## ✅ CLEAN CODE COMPLIANCE

```python
# ANTES (violaciones)
class RBACService:              # ❌ Acrónimo
class ACLManager:               # ❌ Acrónimo
class UMService:                # ❌ Acrónimo
class ETLPipeline:              # ❌ Acrónimo

# DESPUÉS (clean)
class PermissionService:        # ✅ Descriptivo
class AccessControlService:     # ✅ Descriptivo
class UserManagementService:    # ✅ Descriptivo
class DataPipelineService:      # ✅ Descriptivo
```

---

**Documento generado:** 2026-01-21  
**Tipo:** CORRECCIÓN CLEAN CODE  
**Estado:** LISTO para aplicar en código  
**Impacto:** Cambio de nombre en 1 clase + imports
