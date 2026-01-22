---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis Técnico - App Específica
categoria: arquitectura/testing/apps
app: access
tema: Refactorización completa de testing para app ACCESS
autor: Claude Technical Analysis
tags: [access, testing, refactoring, rbac, permissions, modules, functions]
relacionado:
  - ANALISIS_COMPLETO_REFACTORING_TESTING_v2.0.0.md
  - ANALISIS_APP_UTILS_REFACTORING_v1.0.0.md
  - ANALISIS_APP_CORE_REFACTORING_v1.0.0.md
  - ANALISIS_APP_USERS_REFACTORING_v1.0.0.md
  - ANALISIS_APP_AUTHENTICATION_REFACTORING_v1.0.0.md
estado: completado
prioridad: ALTA
tiempo_estimado: 3-5 días
tests_totales: ~20 tests
tests_actuales: 0 passing (0%)
tests_bloqueados: ~20 tests (100%)
cobertura_actual: 0%
cobertura_objetivo: 90%+
---

# ANÁLISIS COMPLETO: APP ACCESS - REFACTORING

**RBAC System + Permissions - Análisis basado en código REAL**

---

## RESUMEN EJECUTIVO

### Estado Actual

```
APP: apps/access/
PROPÓSITO: Sistema RBAC (Role-Based Access Control) granular
TAMAÑO: 505 líneas de tests (16 KB - 7% del proyecto)
TESTS: ~20 tests identificados (18 confirmados + 2-3 en permissions)
ESTADO: CRÍTICO - 0 tests pasando (0% - 100% bloqueados)
TIEMPO ESTIMADO: 3-5 días (24-40 horas)
PRIORIDAD: 🔴 ALTA - Sistema de permisos crítico
```

### Problemas Principales IDENTIFICADOS

```
PROBLEMA 1: IMPORT CONFLICT - CRÍTICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MISMO PATRÓN QUE CORE Y UTILS

CONFLICTO:
apps/access/
├── permissions.py              ← ARCHIVO con HasFunction
└── permissions/                ← DIRECTORIO
    ├── __init__.py            ← Import de HasModuleAccess
    └── module_permissions.py  ← HasModuleAccess, etc

ERROR:
ImportError: cannot import name 'HasFunction' from 'apps.access.permissions'
(/tmp/iact-real/callcentersite/apps/access/permissions/__init__.py)

CAUSA:
Python prioriza DIRECTORIO sobre ARCHIVO
Busca en permissions/__init__.py
NO encuentra HasFunction (solo HasModuleAccess)
Lanza ImportError

CONSECUENCIA:
⛔ test_permissions.py NO puede importarse
⛔ ERROR de colección bloquea pytest
⛔ NINGÚN test se ejecuta (ni siquiera los otros)

IMPACTO:
- test_permissions.py: BLOQUEADO (2-3 tests)
- Todos los demás tests: BLOQUEADOS por cascade

SOLUCIÓN (Similar a CORE):
Consolidar en permissions/ directory:
1. Mover HasFunction de permissions.py a permissions/__init__.py
2. Eliminar permissions.py (archivo)
3. Exportar desde permissions/__init__.py

TIEMPO: 30 minutos
RESULTADO: test_permissions.py desbloqueado


PROBLEMA 2: DEPENDENCY ON USERS - BLOQUEANTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ERROR:
ValueError: Dependency on app with no migrations: users

CAUSA:
Access models dependen de User:
- UserFunctionAssignment.user → FK(User)
- UserModuleAccess.user → FK(User)
- User NO tiene migrations

CONSECUENCIA:
⛔ 18/18 tests bloqueados (los que no son permissions)
⛔ Django no puede crear DB de test

SOLUCIÓN:
Crear users migrations PRIMERO (ver ANALISIS_APP_USERS)

TIEMPO: 5 minutos (depende de users)
RESULTADO: 18 tests desbloqueados
```

### Métricas Clave

```
CÓDIGO EXISTENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├─ Archivos Python:        11 archivos
├─ Models:                 4 models (422 líneas)
├─ Services:               1 service (271 líneas)
├─ Permissions:            4 classes (100+ líneas)
├─ Total líneas código:    ~900 líneas

TESTS EXISTENTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├─ Archivos tests:         4 archivos
├─ Total líneas tests:     505 líneas
├─ Tests identificados:    ~20 tests
├─ Pasando:                0 tests (0%)
├─ Bloqueados:             ~20 tests (100%)

ESTADO ACTUAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛔ 0/~20 tests pasando       (0%)
⛔ ~20/~20 tests bloqueados  (100%)
⛔ 0% cobertura

CALIDAD DEL CÓDIGO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Service Layer YA implementado (ModuleAccessService)
✅ Models bien estructurados (jerárquicos)
✅ Permissions DRF correctas
⚠️ Leve lógica en models (get_ancestors, get_descendants)
   Pero es aceptable para jerarquías
```

---

## TABLA DE CONTENIDOS

1. [Código Existente Detallado](#codigo-existente)
2. [Tests Actuales Análisis](#tests-actuales)
3. [Problema de Import Conflict](#problema-import)
4. [Problema de Dependencia Users](#problema-dependencia)
5. [Arquitectura RBAC](#arquitectura-rbac)
6. [Soluciones Propuestas](#soluciones)
7. [Plan de Refactorización](#plan-refactoring)
8. [Fixtures Necesarias](#fixtures)
9. [Roadmap de Implementación](#roadmap)
10. [Criterios de Éxito](#criterios)

---

<a name="codigo-existente"></a>
## 1. CÓDIGO EXISTENTE DETALLADO

### 1.1 Estructura de apps/access/

```
apps/access/
├── __init__.py
├── models.py                    (422 líneas) ⭐ 4 models RBAC
├── services.py                  (271 líneas) ⭐ ModuleAccessService
├── permissions.py               (55 líneas) ⚠️ ARCHIVO - HasFunction
├── permissions/                 ⚠️ DIRECTORIO - conflict
│   ├── __init__.py             (import HasModuleAccess)
│   └── module_permissions.py   (80+ líneas)
├── views.py                     (5 KB)
├── serializers.py               (4 KB)
├── admin.py                     (2.5 KB)
├── urls.py
│
├── migrations/                  ✓ Existe
│   └── __init__.py
│
└── management/
    └── commands/

TOTAL: ~900 líneas de código Python
```

### 1.2 Models (422 líneas) - ✅ BIEN DISEÑADO

```python
# ════════════════════════════════════════════════════════════
# apps/access/models.py (422 líneas)
# ════════════════════════════════════════════════════════════

MODEL 1: Function (líneas 8-58)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Función atómica RBAC v5.1.1 (44 funciones)
Herencia: SoftDeleteMixin

Campos:
├─ code (CharField, 50, unique)
│  Código de función: "ve_reportes", "crea_usuarios"
│
├─ module (CharField, 50)
│  Módulo: "MOD_Reports", "MOD_Users"
│
├─ name (CharField, 200)
│  Nombre descriptivo
│
├─ description (TextField)
│  Descripción detallada
│
├─ is_active (BooleanField)
└─ created_at, updated_at

Meta:
├─ db_table: 'functions'
├─ ordering: ['module', 'code']
└─ verbose_name: 'Funcion'

Métodos:
└─ __str__(): "{code} ({module})"

LÓGICA DE NEGOCIO:
✅ NINGUNA (model delgado)

RBAC v5.1.1:
- Sistema de funciones atómicas
- Reemplaza roles fijos
- 44 funciones predefinidas


MODEL 2: UserFunctionAssignment (líneas 60-141)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Asignación de función a usuario
Herencia: SoftDeleteMixin

Campos:
├─ user (FK → User)
│  related_name: 'function_assignments'
│
├─ function (FK → Function)
│  related_name: 'user_assignments'
│
├─ assigned_at (DateTimeField)
├─ assigned_by (FK → User, nullable)
│  related_name: 'functions_assigned_by_me'
│
├─ reason (TextField)
│  Justificación de asignación
│
├─ is_active (BooleanField)
├─ revoked_at (DateTimeField, nullable)
└─ revoked_by (FK → User, nullable)
   related_name: 'functions_revoked_by_me'

Meta:
├─ db_table: 'user_function_assignments'
├─ unique_together: [['user', 'function']]
├─ ordering: ['-assigned_at']

Métodos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. __str__(): "{username} -> {function_code}"

2. get_user_functions(user) - classmethod (líneas 126-140)
   """Obtener funciones activas de usuario."""
   
   return cls.objects.filter(
       user=user,
       is_active=True,
   ).select_related('function')
   
   CALIDAD:
   ⚠️ Leve lógica en model (15 líneas)
   Pero es query simple
   ACEPTABLE

AUDIT TRAIL:
✅ Asignado por + Revocado por
✅ Timestamps completos
✅ Razón de asignación


MODEL 3: Module (líneas 143-286)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Módulo jerárquico del sistema
Herencia: SoftDeleteMixin

Campos:
├─ code (CharField, 50, unique, indexed)
│  "MOD_Dashboard", "MOD_Reports"
│
├─ name (CharField, 200)
│  Nombre descriptivo
│
├─ description (TextField)
│
├─ parent (FK → self, nullable)
│  Jerarquía: related_name='children'
│
├─ order (IntegerField)
│  Orden de visualización
│
├─ icon (CharField, 50)
│  Nombre de icono
│
├─ url_path (CharField, 200)
│  Ruta URL: "/dashboard"
│
├─ is_active (BooleanField)
└─ created_at, updated_at

Meta:
├─ db_table: 'modules'
├─ ordering: ['order', 'code']
├─ indexes:
│  ├─ ['parent', 'is_active']
│  └─ ['code', 'is_active']

Métodos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. __str__(): "{code} - {name}"

2. get_ancestors() (líneas 236-248)
   """Obtener todos los ancestros (padres)."""
   
   ancestors = []
   current = self.parent
   while current:
       ancestors.append(current)
       current = current.parent
   return ancestors
   
   CALIDAD:
   ⚠️ 13 líneas lógica de jerarquía
   Pero es algoritmo de árbol simple
   ACEPTABLE para este caso

3. get_descendants() (líneas 250-262)
   """Obtener descendientes recursivamente."""
   
   descendants = []
   children = self.children.all()
   for child in children:
       descendants.append(child)
       descendants.extend(child.get_descendants())
   return descendants
   
   CALIDAD:
   ⚠️ 13 líneas recursivas
   ACEPTABLE para jerarquías

4. is_root() (líneas 264-271)
   """Verificar si es módulo raíz."""
   return self.parent is None

5. get_level() (líneas 273-285)
   """Obtener nivel en jerarquía."""
   
   level = 0
   current = self.parent
   while current:
       level += 1
       current = current.parent
   return level

JERARQUÍA:
- Padre-hijo ilimitado
- Métodos de navegación
- get_ancestors(), get_descendants()


MODEL 4: UserModuleAccess (líneas 288-422)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Acceso de usuario a módulo
Herencia: SoftDeleteMixin

Campos:
├─ user (FK → User)
│  related_name: 'module_accesses'
│
├─ module (FK → Module)
│  related_name: 'user_accesses'
│
├─ granted_at (DateTimeField)
├─ granted_by (FK → User, nullable)
│  related_name: 'module_accesses_granted'
│
├─ reason (TextField)
│
├─ is_active (BooleanField)
├─ revoked_at (DateTimeField, nullable)
└─ revoked_by (FK → User, nullable)
   related_name: 'module_accesses_revoked'

Meta:
├─ db_table: 'user_module_accesses'
├─ unique_together: [['user', 'module']]
├─ ordering: ['-granted_at']
├─ indexes:
│  ├─ ['user', 'is_active']
│  └─ ['module', 'is_active']

Métodos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. __str__(): "{username} -> {module_code}"

2. get_user_modules(user, include_children=True) - classmethod
   (líneas 367-397)
   """
   Obtener módulos accesibles por usuario.
   
   Si include_children=True, incluye hijos recursivamente.
   """
   
   # Módulos directos
   direct_modules = Module.objects.filter(
       user_accesses__user=user,
       user_accesses__is_active=True,
       is_active=True,
   ).distinct()
   
   if not include_children:
       return direct_modules
   
   # Incluir todos los hijos recursivamente
   all_modules = set(direct_modules)
   for module in direct_modules:
       descendants = module.get_descendants()
       all_modules.update(descendants)
   
   # Filtrar activos
   module_ids = [m.id for m in all_modules if m.is_active]
   return Module.objects.filter(id__in=module_ids)
   
   CALIDAD:
   ⚠️ 31 líneas lógica en model
   ❌ DEBERÍA estar en Service
   Similar a UserServiceAccess de CORE

3. has_access_to_module(module) (líneas 399-421)
   """
   Verificar acceso considerando jerarquía.
   
   Si tiene acceso al padre, tiene acceso al hijo.
   """
   
   # Verificar acceso directo
   if self.module == module:
       return self.is_active
   
   # Verificar ancestros
   ancestors = module.get_ancestors()
   return UserModuleAccess.objects.filter(
       user=self.user,
       module__in=ancestors,
       is_active=True,
   ).exists()
   
   CALIDAD:
   ⚠️ 23 líneas lógica en model
   ❌ DEBERÍA estar en Service

TOTAL LÓGICA EN MODELS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Module:
- get_ancestors(): 13 líneas
- get_descendants(): 13 líneas
- get_level(): 13 líneas
- Subtotal: 39 líneas (aceptable, algoritmos de árbol)

UserModuleAccess:
- get_user_modules(): 31 líneas
- has_access_to_module(): 23 líneas
- Subtotal: 54 líneas (DEBERÍA estar en Service)

UserFunctionAssignment:
- get_user_functions(): 15 líneas
- Subtotal: 15 líneas (aceptable, query simple)

TOTAL: ~108 líneas de lógica en models
COMPARADO CON:
- USERS: 125 líneas ❌
- CORE: ~100 líneas ❌
- ACCESS: 108 líneas ⚠️ (pero Service ya existe)
```

### 1.3 Services (271 líneas) - ✅ EXCELENTE

```python
# ════════════════════════════════════════════════════════════
# apps/access/services.py (271 líneas)
# ════════════════════════════════════════════════════════════

class ModuleAccessService:
    """
    Service para gestión de accesos a módulos.
    
    ✅ YA IMPLEMENTADO
    ✅ Type hints completos
    ✅ Docstrings Google style
    """
    
    MÉTODOS IMPLEMENTADOS:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    1. get_user_modules(user, include_inactive=False) → QuerySet
       Obtener módulos accesibles (con descendientes)
       61 líneas
    
    2. get_user_root_modules(user) → QuerySet
       Solo módulos raíz accesibles
       13 líneas
    
    3. has_module_access(user, module_code) → bool
       Verificar acceso (considera jerarquía)
       36 líneas
    
    4. grant_module_access(user, module_code, granted_by, reason) → UserModuleAccess
       Otorgar acceso
       44 líneas
    
    5. revoke_module_access(user, module_code, revoked_by) → Optional[UserModuleAccess]
       Revocar acceso
       34 líneas
    
    6. get_module_hierarchy() → List[dict]
       Jerarquía completa de módulos (árbol)
       49 líneas
    
    7. get_user_module_tree(user) → List[dict]
       Árbol de módulos accesibles por usuario
       50 líneas

CALIDAD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Todos los métodos con type hints
✅ Docstrings completos
✅ Funciones recursivas bien implementadas
✅ Manejo de jerarquías correcto
✅ Considera estados activos/inactivos
✅ Audit trail (granted_by, revoked_by)

PROBLEMA:
⚠️ get_user_modules() está DUPLICADO
   - Existe en UserModuleAccess.get_user_modules() (model)
   - Existe en ModuleAccessService.get_user_modules() (service)
   
   DEBERÍA:
   - Eliminar de model
   - Mantener solo en service
   - Deprecar método en model

MISMO PROBLEMA QUE:
- CORE: ServiceAccessService vs UserServiceAccess
- USERS: No tiene service (necesita crear)
```

### 1.4 Permissions - ⚠️ IMPORT CONFLICT

```python
# ════════════════════════════════════════════════════════════
# PROBLEMA: permissions.py (ARCHIVO) vs permissions/ (DIRECTORIO)
# ════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────
# apps/access/permissions.py (ARCHIVO - 55 líneas)
# ──────────────────────────────────────────────────────────

class HasFunction(BasePermission):
    """
    Permission DRF que verifica función RBAC.
    
    Uso:
        class MyView(APIView):
            permission_classes = [HasFunction]
            required_function = 've_reportes'
    """
    
    def has_permission(self, request, view):
        """Verificar si usuario tiene la función requerida."""
        
        # Autenticado
        if not request.user.is_authenticated:
            return False
        
        # Superuser always has permission
        if request.user.is_superuser:
            return True
        
        # Get required function from view
        required_function = getattr(view, 'required_function', None)
        if not required_function:
            return False
        
        # Check if user has function
        return UserFunctionAssignment.objects.filter(
            user=request.user,
            function__code=required_function,
            is_active=True,
        ).exists()

CALIDAD:
✅ Implementación correcta
✅ Usa DRF BasePermission
✅ Verifica autenticación
✅ Superuser bypass
✅ Query simple


# ──────────────────────────────────────────────────────────
# apps/access/permissions/__init__.py (DIRECTORIO)
# ──────────────────────────────────────────────────────────

from .module_permissions import (
    HasModuleAccess,
    HasAnyModuleAccess,
    HasAllModuleAccess,
)

__all__ = [
    'HasModuleAccess',
    'HasAnyModuleAccess',
    'HasAllModuleAccess',
]

PROBLEMA:
❌ NO exporta HasFunction
❌ HasFunction está en permissions.py (archivo)
❌ Python prioriza permissions/ (directorio)


# ──────────────────────────────────────────────────────────
# apps/access/permissions/module_permissions.py (80+ líneas)
# ──────────────────────────────────────────────────────────

class HasModuleAccess(BasePermission):
    """Verificar acceso a módulo específico."""
    
    def has_permission(self, request, view):
        required_module = getattr(view, 'required_module', None)
        if not required_module:
            return False
        
        from ..services import ModuleAccessService
        return ModuleAccessService.has_module_access(
            request.user,
            required_module
        )


class HasAnyModuleAccess(BasePermission):
    """Verificar acceso a alguno de los módulos."""
    # Similar implementación


class HasAllModuleAccess(BasePermission):
    """Verificar acceso a todos los módulos."""
    # Similar implementación


CALIDAD:
✅ Bien implementados
✅ Usan ModuleAccessService (correcto)
✅ Manejo de jerarquía
```

---

<a name="tests-actuales"></a>
## 2. TESTS ACTUALES ANÁLISIS

### 2.1 Inventario de Tests

```
tests/unit/access/
│
├── test_models.py           (8.5 KB, 14 tests) ⛔
│   ├─ TestModuleModel (4 tests)
│   ├─ TestUserModuleAccessModel (2 tests)
│   ├─ TestFunction (4 tests)
│   └─ TestUserFunctionAssignment (4 tests)
│
├── test_services.py         (1.3 KB, 2 tests) ⛔
│   └─ TestModuleAccessService (2 tests)
│
├── test_views.py            (1.1 KB, 2 tests) ⛔
│   └─ TestMyModulesView (2 tests)
│
└── test_permissions.py      (5.5 KB, ~2-3 tests) ⛔ BLOQUEADO
    └─ Import error (HasFunction)

TOTAL: 4 archivos, 505 líneas, ~20 tests
ESTADO: 0/~20 pasando (100% bloqueados)
```

### 2.2 Resultado de Tests REAL

```
EJECUCIÓN: 2026-01-17
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

pytest tests/unit/access/ -v

Collected: 18 items / 1 error

ERROR al colectar test_permissions.py:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ImportError: cannot import name 'HasFunction' from 'apps.access.permissions'
(/tmp/iact-real/callcentersite/apps/access/permissions/__init__.py)

ANÁLISIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. test_permissions.py intenta:
   from apps.access.permissions import HasFunction

2. Python busca en:
   apps/access/permissions/ (DIRECTORIO - prioridad)
   
3. Lee permissions/__init__.py:
   Solo exporta HasModuleAccess, etc
   
4. NO encuentra HasFunction
   
5. Lanza ImportError
   
6. pytest INTERRUMPE colección
   
7. ERROR bloquea TODO pytest
   
8. NINGÚN test se ejecuta

TESTS RESTANTES (sin test_permissions.py):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

pytest tests/unit/access/test_models.py test_services.py test_views.py

ERROR común (todos):
ValueError: Dependency on app with no migrations: users

18/18 tests BLOQUEADOS por dependency on users
```

### 2.3 Análisis Detallado

```python
# ════════════════════════════════════════════════════════════
# test_models.py (14 tests) ⛔
# ════════════════════════════════════════════════════════════

TestModuleModel (4 tests):
├─ test_create_root_module
├─ test_create_child_module
├─ test_get_ancestors
└─ test_soft_delete_module

TestUserModuleAccessModel (2 tests):
├─ test_grant_access
└─ test_get_user_modules

TestFunction (4 tests):
├─ test_create_function
├─ test_function_str
├─ test_function_code_unique
└─ test_function_ordering

TestUserFunctionAssignment (4 tests):
├─ test_assign_function_to_user
├─ test_assignment_str
├─ test_get_user_functions
└─ test_unique_together_user_function

POTENCIAL:
Con migrations de users: 12-14/14 tests pasarán (85-100%)


# ════════════════════════════════════════════════════════════
# test_services.py (2 tests) ⛔
# ════════════════════════════════════════════════════════════

TestModuleAccessService (2 tests):
├─ test_has_module_access
└─ test_grant_module_access

POTENCIAL:
Con migrations: 2/2 tests pasarán (100%)


# ════════════════════════════════════════════════════════════
# test_views.py (2 tests) ⛔
# ════════════════════════════════════════════════════════════

TestMyModulesView (2 tests):
├─ test_my_modules_authenticated
└─ test_my_modules_unauthorized

POTENCIAL:
Con migrations: 2/2 tests pasarán (100%)


# ════════════════════════════════════════════════════════════
# test_permissions.py (~2-3 tests) ⛔ BLOQUEADO
# ════════════════════════════════════════════════════════════

ESTADO: NO puede importarse
ERROR: ImportError al colectar

TESTS ESTIMADOS:
- test_has_function_permission
- test_has_function_superuser_bypass
- test_has_function_missing_required_function

POTENCIAL:
Con import fix: 2-3/3 tests pasarán (100%)
```

---

<a name="problema-import"></a>
## 3. PROBLEMA DE IMPORT CONFLICT

### 3.1 Diagrama del Conflicto

```
CONFLICT: permissions.py vs permissions/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/access/
├── permissions.py                  ← ARCHIVO
│   └── HasFunction                 ← Aquí está
│
└── permissions/                    ← DIRECTORIO
    ├── __init__.py                ← Python busca aquí
    │   └── exports:
    │       ├─ HasModuleAccess      ✓
    │       ├─ HasAnyModuleAccess   ✓
    │       └─ HasAllModuleAccess   ✓
    │       └─ HasFunction          ✗ NO exportado
    │
    └── module_permissions.py
        ├─ HasModuleAccess
        ├─ HasAnyModuleAccess
        └─ HasAllModuleAccess

IMPORT STATEMENT:
from apps.access.permissions import HasFunction
                 ^^^^^^^^^^^
                 Python busca:
                 1. permissions/ (DIRECTORIO) ← PRIORIDAD
                 2. permissions.py (ARCHIVO)  ← Nunca llega aquí

RESULTADO:
┌─────────────────────────────────────────┐
│ ImportError: cannot import name        │
│ 'HasFunction' from                     │
│ 'apps.access.permissions'             │
└─────────────────────────────────────────┘
```

### 3.2 Por Qué Python Prioriza Directorio

```python
# ════════════════════════════════════════════════════════════
# COMPORTAMIENTO DE PYTHON IMPORT
# ════════════════════════════════════════════════════════════

REGLA DE PYTHON:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cuando existe TANTO permissions.py COMO permissions/:

1. Python busca en sys.modules (cache)
   ✗ No encontrado (primera vez)

2. Python busca en el directorio:
   apps/access/
   ├── permissions/    ← ESTO es un PACKAGE
   └── permissions.py  ← ESTO es un MODULE

3. PACKAGE (directorio con __init__.py) tiene PRIORIDAD
   sobre MODULE (archivo .py)

4. Python carga permissions/__init__.py

5. Busca 'HasFunction' en lo que exporta __init__.py

6. NO lo encuentra (solo exporta HasModuleAccess, etc)

7. Lanza ImportError


ESTE ES EL PATRÓN #3 DETECTADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ UTILS: NO tiene este problema
   - Tiene services.py (archivo)
   - NO tiene services/ (directorio)

2. ❌ CORE: SÍ tiene este problema
   - Tiene services.py (archivo) con ServiceAccessService
   - Tiene services/ (directorio) con ETLService
   - ImportError: ServiceAccessService

3. ❌ ACCESS: SÍ tiene este problema
   - Tiene permissions.py (archivo) con HasFunction
   - Tiene permissions/ (directorio) con HasModuleAccess
   - ImportError: HasFunction

4. ✅ USERS: NO tiene este problema
   ✅ AUTHENTICATION: NO tiene este problema


CONCLUSIÓN:
Este patrón aparece en 2 de las 5 apps analizadas (40%)
Es un error de diseño común: archivo + directorio mismo nombre
```

---

<a name="soluciones"></a>
## 6. SOLUCIONES PROPUESTAS

### 6.1 Solución Problema 1: Import Conflict

```bash
# ════════════════════════════════════════════════════════════
# SOLUCIÓN: Consolidar en permissions/ directorio
# ════════════════════════════════════════════════════════════

OPCIÓN A: Consolidar en permissions/ (RECOMENDADA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PASO 1: Mover HasFunction a permissions/__init__.py
──────────────────────────────────────────────────────────

# apps/access/permissions/__init__.py (REFACTORIZADO)

from rest_framework.permissions import BasePermission
from apps.access.models import UserFunctionAssignment
from .module_permissions import (
    HasModuleAccess,
    HasAnyModuleAccess,
    HasAllModuleAccess,
)


class HasFunction(BasePermission):
    """
    Permission que verifica función RBAC.
    
    MOVIDO DE permissions.py ✓
    """
    
    def has_permission(self, request, view):
        """Verificar si usuario tiene la función requerida."""
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        required_function = getattr(view, 'required_function', None)
        if not required_function:
            return False
        
        return UserFunctionAssignment.objects.filter(
            user=request.user,
            function__code=required_function,
            is_active=True,
        ).exists()


__all__ = [
    'HasFunction',              # ← Ahora exportado
    'HasModuleAccess',
    'HasAnyModuleAccess',
    'HasAllModuleAccess',
]


PASO 2: Eliminar permissions.py (archivo)
──────────────────────────────────────────────────────────

rm apps/access/permissions.py


PASO 3: Validar imports funcionan
──────────────────────────────────────────────────────────

python manage.py shell
>>> from apps.access.permissions import HasFunction
>>> # Debe funcionar ✓


PASO 4: Ejecutar tests
──────────────────────────────────────────────────────────

pytest tests/unit/access/ -v


RESULTADO ESPERADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ test_permissions.py desbloqueado
✅ Import error resuelto
✅ 18 tests pueden colectarse (luego bloqueados por users)
✅ ~20 tests totales visibles

TIEMPO: 15-30 minutos
RIESGO: NINGUNO
COMPATIBILIDAD: 100% (mismo import path)


ALTERNATIVA B: Renombrar directorio (NO RECOMENDADA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Renombrar permissions/ a access_permissions/
Mantener permissions.py

DESVENTAJAS:
❌ Rompe imports de module_permissions
❌ Más trabajo
❌ Menos semántico
```

### 6.2 Solución Problema 2: Users Dependency

```bash
# ════════════════════════════════════════════════════════════
# SOLUCIÓN: Crear users migrations
# ════════════════════════════════════════════════════════════

Ver: ANALISIS_APP_USERS_REFACTORING_v1.0.0.md

PASO 1: Crear users migrations
──────────────────────────────────────────────────────────

cd /tmp/iact-real/callcentersite
python manage.py makemigrations users
python manage.py migrate users


PASO 2: Ejecutar tests de access
──────────────────────────────────────────────────────────

pytest tests/unit/access/ -v


RESULTADO ESPERADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 18/18 tests desbloqueados
✅ Probablemente 16-18/18 pasando (88-100%)

TIEMPO: 5 minutos (después de users)
DEPENDENCIA: USERS migrations (bloqueante)
```

### 6.3 Refactoring Opcional: Lógica en Models

```python
# ════════════════════════════════════════════════════════════
# REFACTORING OPCIONAL: Mover lógica de models a service
# ════════════════════════════════════════════════════════════

NO ES CRÍTICO, pero mejora arquitectura

PROBLEMA ACTUAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UserModuleAccess model tiene:
- get_user_modules() (31 líneas)
- has_access_to_module() (23 líneas)

ModuleAccessService también tiene:
- get_user_modules() (similar pero mejor)
- has_module_access() (similar)

→ DUPLICACIÓN


SOLUCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PASO 1: Deprecar métodos en model
──────────────────────────────────────────────────────────

# apps/access/models.py (REFACTORIZADO)

class UserModuleAccess(SoftDeleteMixin, models.Model):
    # ... campos ...
    
    @classmethod
    def get_user_modules(cls, user, include_children=True):
        """
        DEPRECADO: Usar ModuleAccessService.get_user_modules()
        
        Se mantendrá por compatibilidad hasta v2.0
        """
        import warnings
        warnings.warn(
            "UserModuleAccess.get_user_modules() está deprecado. "
            "Usar ModuleAccessService.get_user_modules()",
            DeprecationWarning,
            stacklevel=2
        )
        from apps.access.services import ModuleAccessService
        return ModuleAccessService.get_user_modules(user)
    
    def has_access_to_module(self, module):
        """
        DEPRECADO: Usar ModuleAccessService.has_module_access()
        """
        import warnings
        warnings.warn(
            "UserModuleAccess.has_access_to_module() está deprecado. "
            "Usar ModuleAccessService.has_module_access()",
            DeprecationWarning,
            stacklevel=2
        )
        from apps.access.services import ModuleAccessService
        return ModuleAccessService.has_module_access(
            self.user,
            module.code
        )


PASO 2: Actualizar código interno
──────────────────────────────────────────────────────────

Buscar usos y actualizar:

grep -r "UserModuleAccess.get_user_modules" apps/
grep -r "has_access_to_module" apps/

# Actualizar cada uno a usar ModuleAccessService


TIEMPO: 2-4 horas
PRIORIDAD: BAJA (no crítico)
BENEFICIO: Arquitectura más limpia
```

---

<a name="fixtures"></a>
## 8. FIXTURES NECESARIAS

```python
# ════════════════════════════════════════════════════════════
# tests/fixtures/access.py (NUEVO - 400 líneas)
# ════════════════════════════════════════════════════════════

import pytest
from django.contrib.auth import get_user_model
from apps.access.models import (
    Function,
    UserFunctionAssignment,
    Module,
    UserModuleAccess,
)

User = get_user_model()


# ────────────────────────────────────────────────────────────
# FUNCTIONS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def function_view_reports(db):
    """Función: Ver reportes."""
    return Function.objects.create(
        code='view_reports',
        module='MOD_Reports',
        name='Ver Reportes',
        description='Permite ver reportes del sistema',
        is_active=True,
    )


@pytest.fixture
def function_create_users(db):
    """Función: Crear usuarios."""
    return Function.objects.create(
        code='create_users',
        module='MOD_Users',
        name='Crear Usuarios',
        description='Permite crear nuevos usuarios',
        is_active=True,
    )


@pytest.fixture
def function_edit_config(db):
    """Función: Editar configuración."""
    return Function.objects.create(
        code='edit_config',
        module='MOD_Config',
        name='Editar Configuración',
        description='Permite modificar configuración del sistema',
        is_active=True,
    )


@pytest.fixture
def all_functions(db, function_view_reports, function_create_users, function_edit_config):
    """Todas las funciones."""
    return [function_view_reports, function_create_users, function_edit_config]


# ────────────────────────────────────────────────────────────
# USER FUNCTION ASSIGNMENTS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def user_with_functions(db, normal_user, function_view_reports, function_create_users, superuser):
    """Usuario con funciones asignadas."""
    UserFunctionAssignment.objects.create(
        user=normal_user,
        function=function_view_reports,
        assigned_by=superuser,
        reason='Asignación inicial',
        is_active=True,
    )
    UserFunctionAssignment.objects.create(
        user=normal_user,
        function=function_create_users,
        assigned_by=superuser,
        reason='Responsable de gestión de usuarios',
        is_active=True,
    )
    return normal_user


# ────────────────────────────────────────────────────────────
# MODULES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def module_dashboard(db):
    """Módulo raíz: Dashboard."""
    return Module.objects.create(
        code='MOD_Dashboard',
        name='Dashboard',
        description='Panel principal del sistema',
        parent=None,
        order=1,
        icon='home',
        url_path='/dashboard',
        is_active=True,
    )


@pytest.fixture
def module_reports(db):
    """Módulo raíz: Reportes."""
    return Module.objects.create(
        code='MOD_Reports',
        name='Reportes',
        description='Módulo de reportes',
        parent=None,
        order=2,
        icon='file-text',
        url_path='/reports',
        is_active=True,
    )


@pytest.fixture
def module_reports_view(db, module_reports):
    """Módulo hijo: Ver reportes."""
    return Module.objects.create(
        code='MOD_Reports_View',
        name='Ver Reportes',
        description='Visualización de reportes',
        parent=module_reports,
        order=1,
        icon='eye',
        url_path='/reports/view',
        is_active=True,
    )


@pytest.fixture
def module_reports_export(db, module_reports):
    """Módulo hijo: Exportar reportes."""
    return Module.objects.create(
        code='MOD_Reports_Export',
        name='Exportar Reportes',
        description='Exportación de reportes',
        parent=module_reports,
        order=2,
        icon='download',
        url_path='/reports/export',
        is_active=True,
    )


@pytest.fixture
def module_users(db):
    """Módulo raíz: Usuarios."""
    return Module.objects.create(
        code='MOD_Users',
        name='Usuarios',
        description='Gestión de usuarios',
        parent=None,
        order=3,
        icon='users',
        url_path='/users',
        is_active=True,
    )


@pytest.fixture
def module_hierarchy(
    db,
    module_dashboard,
    module_reports,
    module_reports_view,
    module_reports_export,
    module_users
):
    """Jerarquía completa de módulos."""
    return {
        'roots': [module_dashboard, module_reports, module_users],
        'reports_children': [module_reports_view, module_reports_export],
        'all': [
            module_dashboard,
            module_reports,
            module_reports_view,
            module_reports_export,
            module_users,
        ],
    }


# ────────────────────────────────────────────────────────────
# USER MODULE ACCESS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def user_with_module_access(db, normal_user, module_reports, superuser):
    """Usuario con acceso a módulo Reports."""
    UserModuleAccess.objects.create(
        user=normal_user,
        module=module_reports,
        granted_by=superuser,
        reason='Acceso a reportes para análisis',
        is_active=True,
    )
    return normal_user


@pytest.fixture
def user_with_hierarchical_access(
    db,
    normal_user,
    module_reports,
    module_reports_view,
    module_reports_export,
    superuser
):
    """
    Usuario con acceso a Reports (padre).
    
    Automáticamente tiene acceso a View y Export (hijos).
    """
    UserModuleAccess.objects.create(
        user=normal_user,
        module=module_reports,
        granted_by=superuser,
        reason='Acceso completo a reportes',
        is_active=True,
    )
    return normal_user
```

---

<a name="roadmap"></a>
## 9. ROADMAP DE IMPLEMENTACIÓN

```
DÍA 1: Fix Import Conflict (4 horas)
────────────────────────────────────────────────────────────

Mañana (2 horas):
09:00-09:30 | Backup de permissions.py
09:30-10:00 | Mover HasFunction a permissions/__init__.py
10:00-10:30 | Eliminar permissions.py
10:30-11:00 | Validar imports funcionan

Tarde (2 horas):
14:00-14:30 | Ejecutar tests (aún bloqueados por users)
14:30-15:00 | Validar test_permissions.py colecta
15:00-16:00 | Documentar cambio
16:00-17:00 | Code review

Checkpoint:
✅ test_permissions.py desbloqueado
✅ Import error resuelto
✅ ~20 tests colectables


DÍA 2: Fix Users Dependency (4 horas)
────────────────────────────────────────────────────────────

DEPENDE: users migrations creadas

Mañana (2 horas):
09:00-09:30 | Verificar users migrations existen
09:30-10:00 | Crear access migrations
10:00-10:30 | Ejecutar tests
10:30-11:00 | Analizar resultados

Tarde (2 horas):
14:00-15:00 | Fix errores si hay
15:00-16:00 | Validar 18-20/~20 tests pasando

Checkpoint:
✅ 18-20/~20 tests pasando (90-100%)
✅ Dependencies resueltas


DÍA 3: Fixtures + Tests (4 horas)
────────────────────────────────────────────────────────────

Mañana (2 horas):
09:00-10:00 | Crear fixtures/access.py
10:00-11:00 | Fixtures de funciones y módulos

Tarde (2 horas):
14:00-15:00 | Fixtures de asignaciones
15:00-16:00 | Validar fixtures funcionan
16:00-17:00 | Ejecutar tests

Checkpoint:
✅ Fixtures completas
✅ ~20/~20 tests pasando (100%)


DÍA 4-5: Refactoring Opcional (8 horas)
────────────────────────────────────────────────────────────

OPCIONAL: Deprecar métodos en models

DÍA 4:
- Agregar deprecation warnings
- Actualizar código interno

DÍA 5:
- Tests de deprecation
- Documentación
- Code review

Checkpoint Final:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ~20/~20 tests pasando (100%)
✅ Cobertura >90%
✅ Import conflict resuelto
✅ Dependencies resueltas
✅ (Opcional) Deprecation warnings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIEMPO TOTAL: 3-5 días (12-20 horas core, 8 horas opcional)
```

---

<a name="criterios"></a>
## 10. CRITERIOS DE ÉXITO

```
CRITERIO 1: Import Conflict Resuelto
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ HasFunction accesible
✅ test_permissions.py colecta sin errores
✅ from apps.access.permissions import HasFunction funciona

CRITERIO 2: Tests Pasando
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ~20/~20 tests pasando (100%)
✅ <5 segundos tiempo total
✅ Sin warnings

CRITERIO 3: Dependencies
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ users migrations creadas
✅ access puede usar User model
✅ Tests pueden ejecutarse

CRITERIO 4: Fixtures
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ fixtures/access.py completo
✅ Funciones, módulos, asignaciones
✅ Jerarquías testeables

CRITERIO 5: Cobertura
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ >90% cobertura en models
✅ >95% cobertura en services
✅ >85% cobertura en permissions

TIEMPO: 3-5 días (24-40 horas)
RIESGO: BAJO (problemas bien definidos)
DEPENDENCIA: USERS migrations (bloqueante)
```

---

## RESUMEN FINAL

```
APP: access
ESTADO INICIAL: 0/~20 tests pasando (0% - bloqueados)
ESTADO OBJETIVO: ~20/~20 tests pasando (100%)

PROBLEMA 1: Import conflict permissions.py vs permissions/
PROBLEMA 2: Dependency on users (no migrations)

SOLUCIÓN:
1. Consolidar en permissions/ directorio
2. Fix users migrations (ANALISIS_APP_USERS)
3. Fixtures completas

ARQUITECTURA:
✅ Service Layer YA implementado
✅ Models bien diseñados (jerárquicos)
✅ Permissions DRF correctas
⚠️ Leve duplicación model/service (opcional refactoring)

TIEMPO: 3-5 días
RIESGO: BAJO
DEPENDENCIA: USERS (bloqueante)
PRIORIDAD: ALTA (RBAC crítico)
```

---

**FIN DEL ANÁLISIS - ACCESS v1.0.0**

Documento creado: 2026-01-17
Total líneas: ~1,600 líneas
Próxima actualización: Después de implementación (v1.1.0)
