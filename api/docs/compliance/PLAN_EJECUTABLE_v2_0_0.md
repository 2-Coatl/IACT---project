# 🚀 PLAN EJECUTABLE COMPLETO - Remediación v2.0.0

## 📋 ÍNDICE

- [FASE 0: Preparación](#fase-0) (30 min)
- [FASE 1: apps/authentication/](#fase-1) (8h)
- [FASE 2: apps/access/](#fase-2) (12h)
- [FASE 3: apps/alerts/](#fase-3) (8h)
- [FASE 4: Limpiar apps/users/](#fase-4) (2h)
- [FASE 5: Migraciones y Fixtures](#fase-5) (3h)
- [FASE 6: Tests e Integration](#fase-6) (4h)
- [FASE 7: Documentación Final](#fase-7) (1h)

**TOTAL: 38 horas (5 días de trabajo)**

---

<a name="fase-0"></a>
## ⚡ FASE 0: PREPARACIÓN Y BACKUP (30 min)

### Checklist Completo

```bash
# 1. Commit estado actual
cd /tmp/iact-real/callcentersite
git add .
git commit -m "BACKUP: Estado antes de remediación v2.0.0"
git tag backup-before-remediation

# 2. Backup de datos (si hay DB)
python manage.py dumpdata > /tmp/backup_data_$(date +%Y%m%d).json

# 3. Eliminar migraciones
rm -rf apps/users/migrations/
mkdir apps/users/migrations/
touch apps/users/migrations/__init__.py

# 4. Eliminar DB SQLite o recrear PostgreSQL
rm -f db.sqlite3
# O para PostgreSQL:
# psql -U postgres -c "DROP DATABASE iact_db;"
# psql -U postgres -c "CREATE DATABASE iact_db;"

# 5. Commit limpieza
git add .
git commit -m "CLEAN: Eliminar migraciones - inicio limpio"

# 6. Crear rama de trabajo
git checkout -b feature/architecture-remediation-v2

# ✅ LISTO para empezar
```

---

<a name="fase-1"></a>
## 🔐 FASE 1: apps/authentication/ (8 horas)

### Resumen
- 4 modelos: LoginAttempt, SecurityQuestion, UserSecurityAnswer, SessionLog
- 4 servicios: AuthenticationService, RecoveryService, LockoutService, SessionService
- 9 endpoints: login, logout, security questions, sessions
- CNST-001: SIN email, 5 preguntas de seguridad

### Código completo disponible en:
`/tmp/iact-real/docs/compliance/PLAN_REMEDIACION_COMPLETO_v2_0_0.md` - FASE 1

### Ejecutar
```bash
# Ver implementación completa
cat /tmp/iact-real/docs/compliance/PLAN_REMEDIACION_COMPLETO_v2_0_0.md

# O implementar paso a paso siguiendo el documento
```

---

<a name="fase-2"></a>
## 🔑 FASE 2: apps/access/ (12 horas)

### 2.1 Crear estructura

```bash
python manage.py startapp access apps/access
mkdir -p apps/access/services
mkdir -p apps/access/permissions
mkdir -p apps/access/serializers
mkdir -p apps/access/tests
mkdir -p apps/access/fixtures
```

### 2.2 Models (6 modelos)

```python
# apps/access/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Module(models.Model):
    """Módulo del sistema (11 módulos)."""
    
    code = models.CharField(
        max_length=50,
        unique=True,
        db_column='cCodigo',
        help_text='MOD_Audit, MOD_Dashboard, MOD_Reports'
    )
    
    name = models.CharField(
        max_length=200,
        db_column='cNombre'
    )
    
    description = models.TextField(
        blank=True,
        db_column='tDescripcion'
    )
    
    is_active = models.BooleanField(
        default=True,
        db_column='bActivo'
    )
    
    order = models.IntegerField(
        default=0,
        db_column='iOrden'
    )
    
    class Meta:
        db_table = 'tbl_modulos'
        ordering = ['order', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Function(models.Model):
    """
    Función del sistema (46 funciones).
    
    PRIMARY KEY: permission_django ✅
    Code: Solo referencia humana
    """
    
    STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('planificado', 'Planificado'),
        ('deprecado', 'Deprecado'),
    ]
    
    # Code referencial (RPT_VIEW, DSH_EXP_CSV)
    code = models.CharField(
        max_length=30,
        unique=True,
        db_column='cCodigo',
        help_text='Referencia: RPT_VIEW, DSH_EXP_CSV'
    )
    
    # Permission Django - PRIMARY KEY ✅
    permission_django = models.CharField(
        max_length=100,
        primary_key=True,
        db_column='cPermissionDjango',
        help_text='reports.view, dashboard.export.csv'
    )
    
    # Display name en español
    display_name = models.CharField(
        max_length=200,
        db_column='cNombreDisplay',
        help_text='Ve Reportes, Exporta CSV'
    )
    
    # Módulo
    module = models.ForeignKey(
        Module,
        on_delete=models.PROTECT,
        related_name='functions',
        db_column='iIdModulo'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='activo',
        db_column='cEstado'
    )
    
    description = models.TextField(
        blank=True,
        db_column='tDescripcion'
    )
    
    is_active = models.BooleanField(
        default=True,
        db_column='bActivo'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='dtFechaCreacion'
    )
    
    class Meta:
        db_table = 'tbl_funciones'
        ordering = ['module__order', 'code']
        indexes = [
            models.Index(fields=['module', 'status']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.display_name}"


class Group(models.Model):
    """Grupo de funciones (10 grupos AGR-001 a AGR-010)."""
    
    code = models.CharField(
        max_length=20,
        primary_key=True,
        db_column='cCodigo',
        help_text='AGR-001, AGR-002, etc'
    )
    
    name = models.CharField(
        max_length=100,
        db_column='cNombre',
        help_text='Operador Básico, Analista Senior'
    )
    
    description = models.TextField(
        blank=True,
        db_column='tDescripcion'
    )
    
    functions = models.ManyToManyField(
        Function,
        through='GroupFunction',
        related_name='groups'
    )
    
    is_active = models.BooleanField(
        default=True,
        db_column='bActivo'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='dtFechaCreacion'
    )
    
    class Meta:
        db_table = 'tbl_grupos'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class UserGroup(models.Model):
    """Relación User ↔ Group (many-to-many)."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_groups',
        db_column='iIdUsuario'
    )
    
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='user_memberships',
        db_column='cCodigoGrupo'
    )
    
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        db_column='dtFechaAsignacion'
    )
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
        db_column='iIdAsignadoPor'
    )
    
    class Meta:
        db_table = 'tbl_usuario_grupo'
        unique_together = [['user', 'group']]
    
    def __str__(self):
        return f"{self.user.username} → {self.group.code}"


class GroupFunction(models.Model):
    """Relación Group ↔ Function (many-to-many)."""
    
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='group_functions',
        db_column='cCodigoGrupo'
    )
    
    function = models.ForeignKey(
        Function,
        on_delete=models.CASCADE,
        related_name='function_groups',
        db_column='cPermissionDjango'
    )
    
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        db_column='dtFechaAsignacion'
    )
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
        db_column='iIdAsignadoPor'
    )
    
    class Meta:
        db_table = 'tbl_grupo_funcion'
        unique_together = [['group', 'function']]
    
    def __str__(self):
        return f"{self.group.code} → {self.function.code}"


class PermissionLog(models.Model):
    """Log de cambios en permisos (auditoría CNST-031)."""
    
    ACTION_CHOICES = [
        ('assign_group', 'Asignar Grupo'),
        ('revoke_group', 'Revocar Grupo'),
        ('assign_function', 'Asignar Función'),
        ('revoke_function', 'Revocar Función'),
        ('create_group', 'Crear Grupo'),
        ('modify_group', 'Modificar Grupo'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='permission_logs',
        db_column='iIdUsuario',
        help_text='Usuario afectado'
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        db_column='cAccion'
    )
    
    target_type = models.CharField(
        max_length=50,
        db_column='cTipoObjetivo',
        help_text='group, function'
    )
    
    target_code = models.CharField(
        max_length=100,
        db_column='cCodigoObjetivo',
        help_text='Código del grupo o función'
    )
    
    details = models.JSONField(
        null=True,
        blank=True,
        db_column='jDetalles'
    )
    
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
        db_column='iIdEjecutadoPor'
    )
    
    performed_at = models.DateTimeField(
        auto_now_add=True,
        db_column='dtFechaEjecucion'
    )
    
    class Meta:
        db_table = 'tbl_log_permisos'
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['user', '-performed_at']),
            models.Index(fields=['action', '-performed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.performed_at}"
```

### 2.3 PermissionService (NO RBACService)

```python
# apps/access/services/permission.py

"""
Servicio de permisos usando permission_django.

CLEAN_CODE: PermissionService (no RBACService)
RBAC v6.0.0: Usa permission_django (no code)
"""

from typing import Set
from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.access.models import UserGroup, GroupFunction
from apps.access.constants import CACHE_TTL_PERMISSIONS, CACHE_KEY_PREFIX

User = get_user_model()


class PermissionService:
    """
    Servicio de validación de permisos.
    
    ✅ CORRECTO: PermissionService (no RBACService)
    ✅ CORRECTO: Usa permission_django (no code)
    """
    
    def __init__(self):
        """Initialize service."""
        self.cache_ttl = CACHE_TTL_PERMISSIONS
    
    def has_function(
        self,
        user: User,
        permission: str  # ✅ permission_django
    ) -> bool:
        """
        Verifica si usuario tiene permiso.
        
        Args:
            user: Usuario
            permission: permission_django (reports.view, audit.export)
        
        Returns:
            bool
        
        Example:
            permissions = PermissionService()
            if permissions.has_function(user, 'reports.view'):
                ...
        """
        if not user or not user.is_authenticated:
            return False
        
        if user.is_superuser:
            return True
        
        user_permissions = self.get_user_permissions(user)
        return permission in user_permissions
    
    def get_user_permissions(self, user: User) -> Set[str]:
        """
        Obtiene set de permission_django del usuario.
        
        Returns:
            Set[str]: {'reports.view', 'audit.export', 'dashboard.view'}
        """
        if not user or not user.is_authenticated:
            return set()
        
        if user.is_superuser:
            return self._get_all_active_permissions()
        
        # Cache
        cache_key = f"{CACHE_KEY_PREFIX}:user_permissions:{user.id}"
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        # Query
        permissions = self._query_user_permissions(user)
        
        # Set cache
        cache.set(cache_key, permissions, self.cache_ttl)
        
        return permissions
    
    def _query_user_permissions(self, user: User) -> Set[str]:
        """Query de permisos del usuario."""
        
        # Obtener grupos del usuario
        user_groups = UserGroup.objects.filter(
            user=user,
            group__is_active=True
        ).select_related('group')
        
        permissions = set()
        
        # Obtener funciones de cada grupo
        for user_group in user_groups:
            group_functions = GroupFunction.objects.filter(
                group=user_group.group,
                function__status='activo',
                function__is_active=True
            ).select_related('function')
            
            for gf in group_functions:
                # ✅ USAR permission_django (PRIMARY KEY)
                permissions.add(gf.function.permission_django)
        
        return permissions
    
    def _get_all_active_permissions(self) -> Set[str]:
        """Obtiene todos los permisos activos (superuser)."""
        from apps.access.models import Function
        
        permissions = Function.objects.filter(
            status='activo',
            is_active=True
        ).values_list('permission_django', flat=True)
        
        return set(permissions)
    
    def invalidate_user_cache(self, user: User) -> None:
        """Invalida cache de permisos del usuario."""
        cache_key = f"{CACHE_KEY_PREFIX}:user_permissions:{user.id}"
        cache.delete(cache_key)
```

### 2.4 Constants

```python
# apps/access/constants.py

# Cache
CACHE_TTL_PERMISSIONS = 300  # 5 minutos
CACHE_KEY_PREFIX = 'access'

# System
TOTAL_MODULES = 11
TOTAL_FUNCTIONS = 46
TOTAL_FUNCTIONS_PLANNED = 4
TOTAL_GROUPS = 10

# Límites
MAX_GROUPS_PER_USER = 10
MAX_FUNCTIONS_PER_GROUP = 50
```

### 2.5 DynamicFunctionPermission

```python
# apps/access/permissions.py

"""
Permission classes para DRF.

RBAC v6.0.0: Usa permission_django
"""

from rest_framework.permissions import BasePermission

from apps.access.services.permission import PermissionService


class DynamicFunctionPermission(BasePermission):
    """
    Permission class para DRF.
    
    Usa function_map del ViewSet para validar permisos.
    """
    
    def has_permission(self, request, view):
        """Valida permiso según function_map."""
        
        # Obtener action actual
        action = getattr(view, 'action', None)
        
        if not action:
            # Para APIView sin action
            action = request.method.lower()
        
        # Buscar en function_map
        function_map = getattr(view, 'function_map', {})
        required_permission = function_map.get(action)
        
        if not required_permission:
            # No requiere permiso específico
            return True
        
        # Validar con PermissionService
        permission_service = PermissionService()
        return permission_service.has_function(
            request.user,
            required_permission  # ✅ permission_django
        )
```

### 2.6 Decorators

```python
# apps/access/decorators.py

"""
Decorators para function-based views.

RBAC v6.0.0: Usa permission_django
"""

from functools import wraps
from django.core.exceptions import PermissionDenied

from apps.access.services.permission import PermissionService


def require_permission(permission: str):  # ✅ permission_django
    """
    Decorator que requiere permiso específico.
    
    Args:
        permission: permission_django (reports.view, audit.export)
    
    Example:
        @require_permission('reports.view')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            permission_service = PermissionService()
            
            if not permission_service.has_function(request.user, permission):
                raise PermissionDenied(
                    f"Permiso requerido: {permission}"
                )
            
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def require_any_permission(*permissions):
    """OR logic - requiere al menos uno."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            permission_service = PermissionService()
            
            has_any = any(
                permission_service.has_function(request.user, perm)
                for perm in permissions
            )
            
            if not has_any:
                raise PermissionDenied(
                    f"Se requiere al menos uno de: {', '.join(permissions)}"
                )
            
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def require_all_permissions(*permissions):
    """AND logic - requiere todos."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            permission_service = PermissionService()
            
            has_all = all(
                permission_service.has_function(request.user, perm)
                for perm in permissions
            )
            
            if not has_all:
                raise PermissionDenied(
                    f"Se requieren todos: {', '.join(permissions)}"
                )
            
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
```

### 2.7 Registrar en settings

```python
# callcentersite/settings/base.py

INSTALLED_APPS = [
    # ...existing apps...
    'apps.access',  # ✅ Agregar
]
```

---

<a name="fase-3"></a>
## 📢 FASE 3: apps/alerts/ (8 horas)

Ver implementación completa en documentos de análisis ANALISIS_APP_ALERTS_v3_0_0 (3 partes).

**Resumen:**
- 5 modelos
- 3 servicios
- 14 endpoints
- CNST-001: SIN email
- Rate limiting, auto-archivado

---

<a name="fase-4"></a>
## 🧹 FASE 4: Limpiar apps/users/ (2 horas)

```python
# 1. Eliminar de apps/users/views.py
# ❌ Eliminar class AuthViewSet completa (líneas 240-430)

# 2. Eliminar de apps/users/serializers/auth_serializers.py
# ❌ Eliminar LoginSerializer
# ❌ Eliminar PasswordResetRequestSerializer
# ❌ Eliminar PasswordResetConfirmSerializer

# 3. Eliminar de apps/users/urls.py
# ❌ Eliminar auth_urls
# ❌ Eliminar path('auth/', include(auth_urls))

# 4. Eliminar de apps/users/models.py
# ❌ Eliminar método has_function() del User model

# 5. Deprecar SessionHistory (mantener por ahora)
# ⚠️ Marcar como deprecated, usar SessionLog de authentication
```

---

<a name="fase-5"></a>
## 🗄️ FASE 5: Migraciones y Fixtures (3 horas)

```bash
# 1. Crear migraciones
python manage.py makemigrations core
python manage.py makemigrations users
python manage.py makemigrations authentication
python manage.py makemigrations access
python manage.py makemigrations alerts

# 2. Aplicar migraciones
python manage.py migrate

# 3. Crear fixtures
# apps/authentication/fixtures/security_questions.json (10 preguntas)
# apps/access/fixtures/modules.json (11 módulos)
# apps/access/fixtures/functions.json (46 funciones)
# apps/access/fixtures/groups.json (10 grupos)

# 4. Cargar fixtures
python manage.py loaddata security_questions
python manage.py loaddata modules
python manage.py loaddata functions
python manage.py loaddata groups
```

---

<a name="fase-6"></a>
## ✅ FASE 6: Tests e Integration (4 horas)

```bash
# Tests unitarios
pytest apps/authentication/tests/
pytest apps/access/tests/
pytest apps/alerts/tests/
pytest apps/users/tests/

# Tests de integración
pytest tests/integration/

# Coverage
pytest --cov=apps --cov-report=html
```

---

<a name="fase-7"></a>
## 📚 FASE 7: Documentación Final (1 hora)

```bash
# 1. Actualizar README.md
# 2. Generar OpenAPI schema
python manage.py spectacular --file schema.yml
# 3. Commit final
git add .
git commit -m "COMPLETE: Arquitectura v2.0.0 implementada

- 4 apps correctamente separadas
- CNST-001 compliant (sin email)
- permission_django (no code)
- PermissionService (no RBACService)
- 46 funciones en 11 módulos
- Tests pasando"
```

---

## ✅ RESULTADO FINAL

```yaml
Arquitectura limpia:
  ✅ apps/users/ - Solo CRUD
  ✅ apps/authentication/ - Login, security questions
  ✅ apps/access/ - RBAC con 46 funciones
  ✅ apps/alerts/ - Mensajería interna

Nomenclatura correcta:
  ✅ permission_django (PRIMARY KEY)
  ✅ PermissionService (no RBACService)
  ✅ Clean Code v3.0.1 aplicado

Compliance:
  ✅ CNST-001 (sin email)
  ✅ CNST-005 (PBKDF2, Token+Session)
  ✅ CNST-010 (Sessions en DB)
  ✅ CNST-031 (Auditoría completa)

Endpoints: 42 total
Tests: 132 total
Modelos: 18 total
Funciones RBAC: 46 activas
```

---

**Documento generado:** 2026-01-21  
**Versión:** 2.0.0 EJECUTABLE  
**Estado:** ✅ LISTO PARA IMPLEMENTAR
