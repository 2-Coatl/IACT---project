# 🔧 CORRECCIÓN CRÍTICA - Nomenclatura RBAC

## INFORMACIÓN

| Atributo | Valor |
|---|---|
| **Fecha** | 2026-01-21 |
| **Tipo** | CORRECCIÓN CRÍTICA |
| **Base** | MODELO_RBAC_IACT_v6_0_0 (2 partes) |

---

## 🚨 ERROR IDENTIFICADO

### Estaba usando INCORRECTAMENTE:

```python
# ❌ INCORRECTO - Usando 'code' (solo referencia humana)
rbac.has_function(user, 'AUD_VIEW')
rbac.has_function(user, 'DSH_VIEW')
rbac.has_function(user, 'RPT_EXP_CSV')

function_map = {
    'list': 'AUD_VIEW',
    'create': 'AUD_CREATE',
}

@require_function('RPT_VIEW')
def my_view(request):
    ...
```

### Debe usar CORRECTAMENTE:

```python
# ✅ CORRECTO - Usando 'permission_django' (PRIMARY KEY)
rbac.has_function(user, 'audit.view')
rbac.has_function(user, 'dashboard.view')
rbac.has_function(user, 'reports.export.csv')

function_map = {
    'list': 'audit.view',
    'create': 'audit.add',
}

@require_function('reports.view')
def my_view(request):
    ...
```

---

## 📊 MODELO FUNCTION (RBAC v6.0.0)

```python
class Function(models.Model):
    """Función atómica del sistema RBAC."""
    
    # Código referencial (solo para humanos)
    code = models.CharField(
        max_length=30,
        unique=True,
        help_text="Código: RPT_VIEW, DSH_EXP_CSV, AUD_VIEW"
    )
    
    # Permission Django - PRIMARY KEY ⭐ ESTE ES EL QUE SE USA
    permission_django = models.CharField(
        max_length=100,
        primary_key=True,  # ← PRIMARY KEY
        help_text="reports.view, dashboard.export.csv, audit.view"
    )
    
    # UI en español
    display_name = models.CharField(
        max_length=200,
        help_text="Ve Reportes, Exporta CSV, Ve Auditoría"
    )
    
    module = models.CharField(max_length=50)
    status = models.CharField(max_length=20)  # activo/planificado/deprecado
    description = models.TextField()
```

---

## 🔄 MAPEO code ↔ permission_django

### MOD_Audit (6 funciones)

| code | permission_django ✅ | display_name |
|------|---------------------|--------------|
| AUD_VIEW | `audit.view` | Ve Auditoría |
| AUD_SEARCH | `audit.search` | Busca en Auditoría |
| AUD_EXP | `audit.export` | Exporta Auditoría |
| AUD_REPORT | `audit.report` | Genera Reporte Auditoría |
| AUD_COMPLIANCE | `audit.compliance` | Ve Cumplimiento |
| AUD_PURGE | `audit.purge` | Purga Logs Antiguos |

### MOD_Dashboard (6 funciones)

| code | permission_django ✅ | display_name |
|------|---------------------|--------------|
| DSH_VIEW | `dashboard.view` | Ve Dashboard |
| DSH_EXP_CSV | `dashboard.export.csv` | Exporta Dashboard CSV |
| DSH_EXP_EXCEL | `dashboard.export.excel` | Exporta Dashboard Excel |
| DSH_EXP_PDF | `dashboard.export.pdf` | Exporta Dashboard PDF |
| DSH_SHARE | `dashboard.share` | Comparte Dashboard |
| DSH_EDIT | `dashboard.edit` | Edita Dashboard |

### MOD_Alerts (6 funciones)

| code | permission_django ✅ | display_name |
|------|---------------------|--------------|
| ALR_VIEW | `alerts.view` | Ve Alertas |
| ALR_SEND | `alerts.send` | Envía Alertas |
| ALR_CONF | `alerts.configure` | Configura Alertas |
| ALR_SUBS | `alerts.subscribe` | Gestiona Suscripciones |
| ALR_MARK | `alerts.mark` | Marca Leído/No Leído |
| ALR_DELETE | `alerts.delete` | Elimina Alertas |

### MOD_Reports (6 funciones)

| code | permission_django ✅ | display_name |
|------|---------------------|--------------|
| RPT_VIEW | `reports.view` | Ve Reportes |
| RPT_CREATE | `reports.create` | Crea Reporte |
| RPT_DELETE | `reports.delete` | Elimina Reporte |
| RPT_EXP_CSV | `reports.export.csv` | Exporta CSV |
| RPT_EXP_EXCEL | `reports.export.excel` | Exporta Excel |
| RPT_EXP_PDF | `reports.export.pdf` | Exporta PDF |

### MOD_Users (9 funciones)

| code | permission_django ✅ | display_name |
|------|---------------------|--------------|
| USR_VIEW | `users.view_user` | Ve Usuarios |
| USR_CREATE | `users.add_user` | Crea Usuarios |
| USR_EDIT | `users.change_user` | Edita Usuarios |
| USR_DELETE | `users.delete_user` | Elimina Usuarios |
| USR_PASS | `users.change_password` | Cambia Contraseña |
| USR_RESET | `users.reset_password` | Resetea Contraseña |
| USR_LOCK | `users.lock_user` | Bloquea Usuario |
| USR_UNLOCK | `users.unlock_user` | Desbloquea Usuario |
| USR_PROFILE | `users.view_profile` | Ve Perfil |

### MOD_Access (5 funciones)

| code | permission_django ✅ | display_name |
|------|---------------------|--------------|
| ACC_ASSIGN | `access.assign_functions` | Asigna Funciones |
| ACC_REVOKE | `access.revoke_functions` | Revoca Funciones |
| ACC_VIEW_PERM | `access.view_permissions` | Ve Permisos |
| ACC_GROUPS | `access.manage_groups` | Gestiona Grupos |
| ACC_SOD | `access.view_separation` | Ve Reglas SoD |

### MOD_Auth (4 funciones)

| code | permission_django ✅ | display_name |
|------|---------------------|--------------|
| AUTH_LOGIN | `auth.login` | Iniciar Sesión |
| AUTH_LOGOUT | `auth.logout` | Cerrar Sesión |
| AUTH_RECOVER | `auth.recover_password` | Recuperar Contraseña |
| AUTH_SESSIONS | `auth.view_sessions` | Ve Sesiones |

---

## 🔧 IMPLEMENTACIÓN CORRECTA

### 1. RBACService

```python
# apps/access/services/rbac.py

class RBACService:
    """Servicio RBAC usando permission_django."""
    
    def has_function(
        self, 
        user: User, 
        permission_django: str  # ✅ NO 'code'
    ) -> bool:
        """
        Verifica si usuario tiene función.
        
        Args:
            user: Usuario
            permission_django: 'reports.view', 'dashboard.export.csv', etc
        
        Returns:
            bool
        """
        if not user or not user.is_authenticated:
            return False
        
        if user.is_superuser:
            return True
        
        # Obtener funciones del usuario (cached)
        user_functions = self.get_user_functions(user)
        
        return permission_django in user_functions  # ✅ permission_django
    
    def get_user_functions(self, user: User) -> Set[str]:
        """
        Obtiene set de permission_django del usuario.
        
        Returns:
            Set[str]: {'reports.view', 'audit.view', 'dashboard.export.csv'}
        """
        # Cache key
        cache_key = f"rbac:user_functions:{user.id}"
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        # Query con permission_django (NO code)
        functions = UserFunctionAssignment.objects.filter(
            user=user,
            function__status='activo',
            function__is_active=True
        ).values_list(
            'function__permission_django',  # ✅ permission_django
            flat=True
        )
        
        functions_set = set(functions)
        
        # Cache 300s
        cache.set(cache_key, functions_set, 300)
        
        return functions_set
```

### 2. DynamicFunctionPermission (DRF)

```python
# apps/access/permissions.py

class DynamicFunctionPermission(BasePermission):
    """
    Permission class para DRF usando permission_django.
    """
    
    def has_permission(self, request, view):
        """Verifica permiso usando function_map del ViewSet."""
        
        # Obtener action actual
        action = view.action or getattr(view, 'action_map', {}).get(
            request.method.lower()
        )
        
        # Buscar en function_map
        function_map = getattr(view, 'function_map', {})
        required_permission = function_map.get(action)
        
        if not required_permission:
            return True  # No requiere permiso específico
        
        # Validar con RBACService usando permission_django
        rbac = RBACService()
        return rbac.has_function(
            request.user, 
            required_permission  # ✅ 'reports.view', NO 'RPT_VIEW'
        )
```

### 3. @require_function Decorator

```python
# apps/access/decorators.py

from functools import wraps
from django.core.exceptions import PermissionDenied

def require_function(permission_django: str):  # ✅ permission_django
    """
    Decorator para function-based views.
    
    Args:
        permission_django: 'reports.view', 'audit.export', etc
    
    Example:
        @require_function('reports.view')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            rbac = RBACService()
            
            if not rbac.has_function(request.user, permission_django):
                raise PermissionDenied(
                    f"Permiso requerido: {permission_django}"
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapped
    return decorator


def require_any_function(*permissions):
    """OR logic - cualquier permiso."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            rbac = RBACService()
            
            has_any = any(
                rbac.has_function(request.user, perm)
                for perm in permissions
            )
            
            if not has_any:
                raise PermissionDenied(
                    f"Se requiere al menos uno de: {', '.join(permissions)}"
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapped
    return decorator
```

### 4. ViewSet Example

```python
# apps/audit/views.py

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de auditoría con RBAC."""
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    # ✅ CORRECTO - Usa permission_django
    function_map = {
        'list': 'audit.view',
        'retrieve': 'audit.view',
        'export': 'audit.export',
        'search': 'audit.search',
    }
    
    @action(detail=False, methods=['post'])
    def export(self, request):
        """Exporta auditoría (requiere audit.export)."""
        # DynamicFunctionPermission valida automáticamente
        ...
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Busca en auditoría (requiere audit.search)."""
        ...


# apps/dashboard/views.py

class DashboardViewSet(viewsets.ViewSet):
    """ViewSet de dashboards con RBAC."""
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    # ✅ CORRECTO - Usa permission_django
    function_map = {
        'retrieve': 'dashboard.view',
        'export_csv': 'dashboard.export.csv',
        'export_excel': 'dashboard.export.excel',
    }
    
    @action(detail=True, methods=['post'])
    def export_csv(self, request, pk=None):
        """Exporta dashboard a CSV."""
        # Requiere 'dashboard.export.csv'
        ...


# apps/users/views.py

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet de usuarios con RBAC."""
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    # ✅ CORRECTO - Usa permission_django
    function_map = {
        'list': 'users.view_user',
        'retrieve': 'users.view_user',
        'create': 'users.add_user',
        'update': 'users.change_user',
        'partial_update': 'users.change_user',
        'destroy': 'users.delete_user',
        'reset_password': 'users.reset_password',
        'lock': 'users.lock_user',
        'unlock': 'users.unlock_user',
    }
```

### 5. Template Tag

```python
# apps/access/templatetags/rbac_tags.py

from django import template
from apps.access.services import RBACService

register = template.Library()

@register.simple_tag(takes_context=True)
def has_function(context, permission_django: str):  # ✅ permission_django
    """
    Template tag para verificar permisos.
    
    Usage:
        {% load rbac_tags %}
        {% has_function 'reports.view' as can_view_reports %}
        {% if can_view_reports %}
            ...
        {% endif %}
    """
    user = context.get('user')
    if not user:
        return False
    
    rbac = RBACService()
    return rbac.has_function(user, permission_django)
```

---

## 📋 FIXTURES CORRECTOS

```json
// apps/access/fixtures/functions.json

[
  {
    "model": "access.function",
    "pk": "audit.view",  // ← PRIMARY KEY (permission_django)
    "fields": {
      "code": "AUD_VIEW",
      "display_name": "Ve Auditoría",
      "module": "audit",
      "status": "activo",
      "description": "Ve logs de auditoría del sistema",
      "is_active": true
    }
  },
  {
    "model": "access.function",
    "pk": "reports.view",
    "fields": {
      "code": "RPT_VIEW",
      "display_name": "Ve Reportes",
      "module": "reports",
      "status": "activo",
      "description": "Ve reportes tabulares",
      "is_active": true
    }
  },
  {
    "model": "access.function",
    "pk": "dashboard.export.csv",
    "fields": {
      "code": "DSH_EXP_CSV",
      "display_name": "Exporta Dashboard CSV",
      "module": "dashboard",
      "status": "activo",
      "description": "Exporta snapshot dashboard a CSV",
      "is_active": true
    }
  }
]
```

---

## ✅ RESUMEN DE CAMBIOS

```yaml
LO QUE ESTABA HACIENDO MAL:
  ❌ has_function(user, 'AUD_VIEW')
  ❌ function_map = {'list': 'RPT_VIEW'}
  ❌ @require_function('DSH_VIEW')
  ❌ code como identificador principal

LO QUE DEBO HACER:
  ✅ has_function(user, 'audit.view')
  ✅ function_map = {'list': 'reports.view'}
  ✅ @require_function('dashboard.view')
  ✅ permission_django como PRIMARY KEY
  ✅ code solo como referencia humana
```

---

**Documento generado:** 2026-01-21  
**Tipo:** CORRECCIÓN CRÍTICA  
**Estado:** LISTO para actualizar plan de remediación
