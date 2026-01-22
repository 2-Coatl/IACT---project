---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Access PARTE 1/6
categoria: arquitectura/apps
tema: apps/access/ - Fundamentos y Arquitectura RBAC Core
autor: Claude Technical Analysis
tags: [access, rbac, permissions, core, function-based, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
estado: definitivo
parte: 1 de 6
relacionado:
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_2.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_3.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_4.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_5.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_6.md
replaces: []
---

# ANÁLISIS DE apps/access/ v3.0.0 - PARTE 1/6
## FUNDAMENTOS Y ARQUITECTURA RBAC CORE

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen)
2. [Propósito y Responsabilidades](#proposito)
3. [CLEAN_CODE v3.0.1 Aplicado](#clean-code)
4. [RESTRICCIONES v1.0.0 Aplicadas](#restricciones)
5. [RBAC v6.0.0 - Sistema Completo](#rbac)
6. [Arquitectura de la App](#arquitectura)
7. [Modelos Django](#modelos)
8. [Constants y Configuración](#constants)

---

<a name="resumen"></a>
## 1. RESUMEN EJECUTIVO

### 1.1 Overview

```yaml
App: apps/access/
Versión: 3.0.0
Tipo: App MUY COMPLEJA (6 partes)
Prioridad: 🔴 CRÍTICA - CORE DEL SISTEMA
Complejidad: Muy Alta
Líneas estimadas: ~6,500 líneas
Tamaño estimado: ~280KB
Tiempo estimado: 18 horas

Propósito:
  CORE del sistema RBAC (Role-Based Access Control)
  Implementación completa de permisos function-based
  Gestión de usuarios, grupos, funciones
  DynamicFunctionPermission para toda la app
  Decorators y middleware de autorización
```

### 1.2 Importancia Crítica

```yaml
🔴 apps/access/ es CRÍTICA porque:

1. TODAS las apps dependen de access:
   - apps/dashboard/ → DSH_VIEW, DSH_EXP_CSV
   - apps/alerts/ → ALR_SEND, ALR_VIEW
   - apps/audit/ → AUD_VIEW, AUD_SEARCH
   - apps/reports/ → RPT_CREATE, RPT_EXP_CSV
   - apps/calls/ → CALL_VIEW, CALL_EDIT
   - ... (46 funciones totales)

2. Sin access, NADA funciona:
   - DynamicFunctionPermission usado en TODOS los ViewSets
   - @require_function usado en TODAS las vistas
   - has_function() usado en TODOS los templates
   - RBACService usado en TODA la lógica

3. Sistema de permisos granular:
   - NO permisos Django nativos (is_staff, is_superuser)
   - SÍ permisos function-based (AUD_VIEW, DSH_VIEW)
   - Jerarquía: User → Group → Function → Permission
   - Flexibilidad: Un usuario puede tener múltiples grupos

4. 46 funciones del sistema:
   - 11 módulos (MOD_Dashboard, MOD_Audit, MOD_Alerts, etc)
   - 46 funciones activas
   - ~10 funciones planificadas
   - Total: ~56 funciones en RBAC v6.0.0
```

### 1.3 Características Principales

```yaml
Modelos Django: 6 modelos
  - Function (46 registros en producción)
  - Module (11 módulos)
  - Group (5-10 grupos típicos)
  - UserGroup (relación many-to-many)
  - GroupFunction (relación many-to-many)
  - PermissionLog (auditoría)

Services: 3 services
  - RBACService (core, validación de permisos)
  - GroupService (gestión de grupos)
  - AuditService (logs de cambios)

Permissions: 2 custom permissions
  - DynamicFunctionPermission (DRF)
  - FunctionPermissionMixin (Class-based views)

Decorators: 3 decorators
  - @require_function (function-based views)
  - @require_any_function (OR logic)
  - @require_all_functions (AND logic)

Middleware: 1 middleware
  - RBACMiddleware (attach user functions to request)

Endpoints: 8 endpoints REST
  - CRUD funciones
  - CRUD grupos
  - Asignar/remover funciones
  - Auditoría de permisos
```

---

<a name="proposito"></a>
## 2. PROPÓSITO Y RESPONSABILIDADES

### 2.1 Propósito Principal

**apps/access/** es el **sistema central de control de acceso** basado en funciones (RBAC v6.0.0), responsable de gestionar usuarios, grupos, funciones, y validar permisos en TODA la aplicación IACT.

### 2.2 Responsabilidades

```yaml
Responsabilidades CRÍTICAS:

1. Gestión de Funciones (46 funciones):
   - Crear/editar/eliminar funciones
   - Organizar en módulos (11 módulos)
   - Estados: activo/inactivo/planificado
   - Fixtures en JSON

2. Gestión de Grupos:
   - CRUD de grupos (GRP_Admin, GRP_Manager, etc)
   - Asignar funciones a grupos
   - Relación many-to-many (GroupFunction)
   - Herencia de permisos (futuro)

3. Gestión de Usuarios:
   - Asignar usuarios a grupos
   - Un usuario puede tener múltiples grupos
   - Relación many-to-many (UserGroup)
   - NO modificar modelo User (Django auth)

4. Validación de Permisos:
   - DynamicFunctionPermission (DRF)
   - @require_function decorator
   - has_function() template tag
   - Middleware para request.user_functions

5. Auditoría de Cambios:
   - Log de cambios en grupos
   - Log de asignaciones de funciones
   - Integración con apps/audit/
   - Trazabilidad completa

Responsabilidades SECUNDARIAS:
  - Cache de permisos (5 min TTL)
  - API REST para frontend
  - Reports de permisos
  - Bulk operations
```

### 2.3 NO Responsabilidades

```yaml
❌ NO es responsable de:
  - Autenticación (Django auth, apps/accounts/)
  - Password management (Django auth)
  - Login/logout (Django sessions)
  - OAuth/SSO (futuro, apps/oauth/)
  - Rate limiting (apps/security/)
  - CAPTCHA (apps/security/)
  - MFA (apps/security/)
  - Session management (Django sessions)
```

### 2.4 Separación de Responsabilidades

```yaml
apps/access/ (Autorización):
  - RBAC function-based
  - Permisos granulares
  - Grupos y funciones
  - has_function() checks

Django auth (Autenticación):
  - login() / logout()
  - authenticate()
  - Session management
  - Password hashing

apps/accounts/ (Gestión usuarios):
  - Perfil de usuario
  - Configuración de cuenta
  - Preferencias
  - NO permisos

apps/security/ (Seguridad):
  - Rate limiting
  - CAPTCHA
  - Login attempts
  - IP blocking
```

---

<a name="clean-code"></a>
## 3. CLEAN_CODE v3.0.1 APLICADO

### 3.1 Nomenclatura Código

```python
# CLEAN_CODE v3.0.1: Código en INGLÉS

# Clases (PascalCase)
class Function(models.Model):
    """Función del sistema RBAC."""
    pass

class Group(models.Model):
    """Grupo de usuarios."""
    pass

class RBACService:
    """Servicio principal de RBAC."""
    pass

class DynamicFunctionPermission(BasePermission):
    """Permission class para DRF."""
    pass

# Métodos y funciones (snake_case)
def has_function(user: User, function_code: str) -> bool:
    """Verifica si usuario tiene función."""
    pass

def get_user_functions(user: User) -> List[str]:
    """Obtiene funciones del usuario."""
    pass

def assign_function_to_group(group_id: int, function_code: str) -> bool:
    """Asigna función a grupo."""
    pass

# Variables (snake_case)
user_functions = []
group_list = []
permission_granted = False

# Constantes (UPPER_SNAKE_CASE)
CACHE_TTL_FUNCTIONS = 300
DEFAULT_GROUP = 'GRP_UserBasic'
MAX_GROUPS_PER_USER = 10
SYSTEM_FUNCTIONS_COUNT = 46
```

### 3.2 Nomenclatura Base de Datos (Húngaro Preservado)

```python
# Modelos Django: Nombres en inglés
class Function(models.Model):
    """Función del sistema RBAC."""
    
    # Campos: inglés snake_case
    code = models.CharField(...)
    name = models.CharField(...)
    module = models.ForeignKey(...)
    
    # db_column: húngaro preservado
    id = models.AutoField(
        db_column='iIdFuncion',
        primary_key=True
    )
    
    code = models.CharField(
        db_column='cCodigo',
        max_length=50,
        unique=True
    )
    
    name = models.CharField(
        db_column='cNombre',
        max_length=200
    )
    
    description = models.TextField(
        db_column='tDescripcion'
    )
    
    module = models.ForeignKey(
        db_column='iIdModulo',
        on_delete=models.CASCADE
    )
    
    is_active = models.BooleanField(
        db_column='bActivo',
        default=True
    )
    
    class Meta:
        db_table = 'tbl_funciones'
        ordering = ['module', 'code']
```

### 3.3 Docstrings en Español

```python
"""
Service layer para sistema RBAC.

Responsabilidades:
- Validación de permisos function-based
- Gestión de grupos y funciones
- Cache de permisos de usuarios
- Auditoría de cambios

CLEAN_CODE v3.0.1:
- Código: inglés PascalCase/snake_case
- Docstrings: español formato Google
- Comentarios: español

RBAC v6.0.0: 46 funciones, 11 módulos
"""

class RBACService:
    """
    Servicio principal de RBAC.
    
    Responsabilidades:
    - Validar permisos de usuario
    - Cachear funciones por usuario
    - Proveer API para has_function()
    
    Atributos:
        cache_ttl (int): TTL del cache (300s)
    """
    
    def __init__(self):
        """Inicializa el servicio RBAC."""
        self.cache_ttl = CACHE_TTL_FUNCTIONS
    
    def has_function(self, user: User, function_code: str) -> bool:
        """
        Verifica si usuario tiene función específica.
        
        Args:
            user: Usuario de Django
            function_code: Código de función (ej: 'AUD_VIEW')
        
        Returns:
            bool: True si tiene permiso, False si no
        
        Cache:
            Cachea resultado por 300s (5 min)
        
        Example:
            >>> rbac_service.has_function(user, 'AUD_VIEW')
            True
            >>> rbac_service.has_function(user, 'DSH_EDIT')
            False
        """
        # Implementación...
        pass
```

---

<a name="restricciones"></a>
## 4. RESTRICCIONES v1.0.0 APLICADAS

### 4.1 CNST-034: RBAC Function-Based (🔴 CRÍTICO)

```yaml
Restricción: Permisos basados en funciones, NO Django perms
Categoría: Seguridad y Arquitectura
Impacto: 🔴 CRÍTICO
Estado: Activo

Descripción:
  El sistema NO usa permisos nativos de Django
  (add_*, change_*, delete_*, view_*). En su lugar,
  usa un sistema de funciones granulares.

Razones:
  - Granularidad: AUD_VIEW vs generic view_auditlog
  - Flexibilidad: DSH_EXP_CSV vs rigid add_dashboard
  - Business logic: Funciones reflejan acciones de negocio
  - Multi-grupo: Usuario puede tener varios grupos

Implementación:
  ❌ NO usar:
     - user.has_perm('audit.view_auditlog')
     - @permission_required('dashboard.add_dashboard')
     - PermissionRequiredMixin
  
  ✅ SÍ usar:
     - rbac_service.has_function(user, 'AUD_VIEW')
     - @require_function('DSH_VIEW')
     - DynamicFunctionPermission
     - {% if user|has_function:'AUD_VIEW' %}

Jerarquía:
  User → UserGroup → Group → GroupFunction → Function
  
  Ejemplo:
    user: jdoe
    ├─ UserGroup: jdoe → GRP_Manager
    │  └─ GroupFunction: GRP_Manager → AUD_VIEW
    │     └─ Function: AUD_VIEW (activa)
    └─ UserGroup: jdoe → GRP_Auditor
       └─ GroupFunction: GRP_Auditor → AUD_SEARCH
          └─ Function: AUD_SEARCH (activa)
  
  Resultado: jdoe tiene AUD_VIEW + AUD_SEARCH

Django Permissions:
  - NO se usan para RBAC
  - Solo para Django Admin (staff access)
  - Admin separate de RBAC
```

### 4.2 CNST-035: Cache de Permisos

```yaml
Restricción: Cache de permisos por usuario
Categoría: Performance
Impacto: Alto
Estado: Activo

Problema:
  Validar permisos en cada request es costoso.
  has_function() puede llamarse 10-50 veces por request.

Solución:
  ✅ Cache de funciones por usuario:
     ```python
     cache_key = f"rbac:user_functions:{user.id}"
     user_functions = cache.get(cache_key)
     
     if not user_functions:
         user_functions = get_user_functions(user)
         cache.set(cache_key, user_functions, 300)  # 5 min
     ```
  
  ✅ Middleware agrega a request:
     ```python
     # RBACMiddleware
     request.user_functions = get_user_functions_cached(request.user)
     ```
  
  ✅ Invalidación automática:
     - Cuando se asigna/remueve función
     - Cuando se agrega/remueve usuario a grupo
     - TTL 300s (5 min) como fallback

Performance:
  - Sin cache: ~50ms por has_function()
  - Con cache: ~0.5ms por has_function()
  - Mejora: 100x más rápido

Trade-off:
  - Cambios de permisos tardan hasta 5 min en aplicar
  - Aceptable para RBAC (cambios infrecuentes)
  - Invalidación manual disponible si urgente
```

### 4.3 CNST-036: Fixtures para Funciones

```yaml
Restricción: Funciones definidas en fixtures JSON
Categoría: Deployment
Impacto: Medio
Estado: Activo

Problema:
  46 funciones son críticas para el sistema.
  NO pueden crearse manualmente en cada ambiente.

Solución:
  ✅ Fixtures JSON versionadas:
     apps/access/fixtures/
     ├── modules.json (11 módulos)
     ├── functions.json (46 funciones)
     └── groups.json (grupos base)
  
  ✅ Loaddata en deployment:
     ```bash
     python manage.py loaddata modules
     python manage.py loaddata functions
     python manage.py loaddata groups
     ```
  
  ✅ Versionado:
     - functions.json tiene version field
     - Migration verifica versión actual
     - Auto-update si nueva versión

Estructura functions.json:
  ```json
  [
    {
      "model": "access.function",
      "pk": 1,
      "fields": {
        "code": "AUD_VIEW",
        "name": "Ver Auditoría",
        "description": "Permite ver logs de auditoría",
        "module": 1,  # MOD_Audit
        "is_active": true,
        "permission_string": "audit.view",
        "version": "6.0.0"
      }
    },
    ...
  ]
  ```

Testing:
  - Verificar que loaddata carga 46 funciones
  - Verificar que módulos tienen funciones
  - Verificar códigos únicos
```

---

<a name="rbac"></a>
## 5. RBAC v6.0.0 - SISTEMA COMPLETO

### 5.1 Arquitectura RBAC

```yaml
┌─────────────────────────────────────────────────────────┐
│ RBAC v6.0.0 - Role-Based Access Control                │
│ Sistema de permisos basado en funciones                │
└─────────────────────────────────────────────────────────┘

Jerarquía:
  User (Django auth)
    ↓
  UserGroup (many-to-many)
    ↓
  Group (ej: GRP_Manager, GRP_Auditor)
    ↓
  GroupFunction (many-to-many)
    ↓
  Function (ej: AUD_VIEW, DSH_VIEW)
    ↓
  Module (ej: MOD_Audit, MOD_Dashboard)

Flujo de validación:
  1. Request llega → Middleware
  2. Middleware carga user_functions (cached)
  3. View/ViewSet valida con DynamicFunctionPermission
  4. Permission check: function_code in user_functions?
  5. Allow/Deny

function_map:
  {
    'list': 'audit.view',      # AUD_VIEW
    'retrieve': 'audit.view',  # AUD_VIEW
    'search': 'audit.search',  # AUD_SEARCH
  }
```

### 5.2 Módulos del Sistema (11 módulos)

```yaml
MOD_Dashboard (6 funciones):
  - DSH_VIEW, DSH_EXP_CSV, DSH_EXP_EXCEL
  - DSH_EXP_PDF (planificado)
  - DSH_SHARE (planificado)
  - DSH_EDIT (planificado)

MOD_Audit (4 funciones):
  - AUD_VIEW, AUD_SEARCH, AUD_REPORT, AUD_EXPORT

MOD_Alerts (6 funciones):
  - ALR_VIEW, ALR_SEND, ALR_MARK, ALR_DELETE
  - ALR_CONF, ALR_SUBS

MOD_Reports (6 funciones):
  - RPT_VIEW, RPT_CREATE, RPT_DELETE
  - RPT_EXP_CSV, RPT_EXP_EXCEL, RPT_EXP_PDF

MOD_Calls (5 funciones):
  - CALL_VIEW, CALL_EDIT, CALL_DELETE
  - CALL_EXP_CSV, CALL_STATS

MOD_Clients (4 funciones):
  - CLI_VIEW, CLI_EDIT, CLI_DELETE, CLI_MERGE

MOD_Services (4 funciones):
  - SVC_VIEW, SVC_EDIT, SVC_DELETE, SVC_CONFIG

MOD_IVR (3 funciones):
  - IVR_VIEW, IVR_EDIT, IVR_STATS

MOD_Users (4 funciones):
  - USR_VIEW, USR_EDIT, USR_DELETE, USR_PERMS

MOD_Config (2 funciones):
  - CFG_VIEW, CFG_EDIT

MOD_System (2 funciones):
  - SYS_ADMIN, SYS_LOGS

TOTAL: 11 módulos, 46 funciones activas
```

### 5.3 Grupos Típicos

```yaml
GRP_Admin (superusuarios):
  Funciones: TODAS (46 funciones)
  Uso: Administradores del sistema
  Usuarios: 1-3 usuarios

GRP_Manager (gerentes):
  Funciones: 20-25 funciones
  - DSH_VIEW, DSH_EXP_CSV, DSH_EXP_EXCEL
  - RPT_VIEW, RPT_CREATE, RPT_EXP_CSV
  - CALL_VIEW, CALL_STATS
  - CLI_VIEW, CLI_EDIT
  - SVC_VIEW
  Uso: Gerentes de operaciones
  Usuarios: 5-10 usuarios

GRP_Auditor (auditores):
  Funciones: 8-10 funciones
  - AUD_VIEW, AUD_SEARCH, AUD_REPORT, AUD_EXPORT
  - USR_VIEW
  - SYS_LOGS
  Uso: Auditores internos y compliance
  Usuarios: 2-5 usuarios

GRP_Supervisor (supervisores):
  Funciones: 15-20 funciones
  - CALL_VIEW, CALL_EDIT, CALL_STATS
  - CLI_VIEW
  - ALR_VIEW, ALR_SEND
  - RPT_VIEW
  Uso: Supervisores de agentes
  Usuarios: 10-20 usuarios

GRP_Agent (agentes):
  Funciones: 5-8 funciones
  - CALL_VIEW
  - CLI_VIEW
  - IVR_VIEW
  Uso: Agentes de call center
  Usuarios: 50-200 usuarios

GRP_UserBasic (default):
  Funciones: 2-3 funciones
  - USR_VIEW (ver propio perfil)
  Uso: Usuario base sin permisos especiales
  Usuarios: Todos los nuevos usuarios
```

---

<a name="arquitectura"></a>
## 6. ARQUITECTURA DE LA APP

### 6.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    apps/access/                         │
│               RBAC CORE DEL SISTEMA                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐    │
│  │         API Layer (REST Admin)                 │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - FunctionViewSet (CRUD funciones)            │    │
│  │  - ModuleViewSet (CRUD módulos)                │    │
│  │  - GroupViewSet (CRUD grupos)                  │    │
│  │  - UserGroupViewSet (assign users)             │    │
│  │  - GroupFunctionViewSet (assign functions)     │    │
│  │  - RBAC: Requiere SYS_ADMIN o USR_PERMS        │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │           Service Layer                        │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - RBACService (core)                          │    │
│  │    * has_function()                            │    │
│  │    * get_user_functions()                      │    │
│  │    * validate_permission()                     │    │
│  │  - GroupService                                │    │
│  │    * assign_function_to_group()                │    │
│  │    * remove_function_from_group()              │    │
│  │    * get_group_functions()                     │    │
│  │  - PermissionCacheService                      │    │
│  │    * cache_user_functions()                    │    │
│  │    * invalidate_user_cache()                   │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │      Permissions & Decorators                  │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - DynamicFunctionPermission (DRF)             │    │
│  │  - FunctionPermissionMixin (CBV)               │    │
│  │  - @require_function (decorator)               │    │
│  │  - @require_any_function (OR logic)            │    │
│  │  - @require_all_functions (AND logic)          │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │           Middleware                           │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - RBACMiddleware                              │    │
│  │    * Attach user_functions to request          │    │
│  │    * Cache-aware                               │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │      Data Layer (6 Models)                     │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - Module (11 registros)                       │    │
│  │  - Function (46 registros)                     │    │
│  │  - Group (5-10 grupos)                         │    │
│  │  - UserGroup (many-to-many)                    │    │
│  │  - GroupFunction (many-to-many)                │    │
│  │  - PermissionLog (auditoría)                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘

Integración con TODAS las apps:
  ┌─────────────────┐
  │  apps/*/        │ → Usan DynamicFunctionPermission
  │  (todas)        │ → Usan @require_function
  └─────────────────┘ → Usan has_function() en templates
  
  ┌─────────────────┐
  │  Django Cache   │ → Cache de user_functions (300s)
  └─────────────────┘
  
  ┌─────────────────┐
  │  apps/audit/    │ → PermissionLog auditoría
  └─────────────────┘
```

---

<a name="modelos"></a>
## 7. MODELOS DJANGO

### 7.1 Module

```python
"""
Módulo del sistema RBAC.

Agrupa funciones relacionadas (ej: MOD_Audit, MOD_Dashboard).

CLEAN_CODE v3.0.1:
- Nombre: Module (inglés PascalCase)
- Campos: code, name (inglés snake_case)
- db_column: cCodigo, cNombre (húngaro preservado)
"""

class Module(models.Model):
    """
    Módulo del sistema RBAC.
    
    Agrupa funciones relacionadas por área funcional.
    
    Campos:
    - code: Código único (ej: MOD_Audit)
    - name: Nombre descriptivo (ej: Módulo de Auditoría)
    - description: Descripción del módulo
    - is_active: Si el módulo está activo
    - order: Orden de visualización
    
    Example:
        MOD_Audit: Módulo de Auditoría
        MOD_Dashboard: Módulo de Dashboards
        MOD_Alerts: Módulo de Alertas
    """
    
    id = models.AutoField(
        db_column='iIdModulo',
        primary_key=True
    )
    
    code = models.CharField(
        db_column='cCodigo',
        max_length=50,
        unique=True,
        help_text="Código único (ej: MOD_Audit)"
    )
    
    name = models.CharField(
        db_column='cNombre',
        max_length=200,
        help_text="Nombre descriptivo"
    )
    
    description = models.TextField(
        db_column='tDescripcion',
        blank=True,
        help_text="Descripción del módulo"
    )
    
    is_active = models.BooleanField(
        db_column='bActivo',
        default=True,
        help_text="Si el módulo está activo"
    )
    
    order = models.IntegerField(
        db_column='iOrden',
        default=0,
        help_text="Orden de visualización"
    )
    
    created_at = models.DateTimeField(
        db_column='dFechaCreacion',
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'tbl_modulos'
        ordering = ['order', 'code']
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
    
    def __str__(self):
        return f"{self.code} - {self.name}"
```

### 7.2 Function

```python
"""
Función del sistema RBAC.

Representa una acción específica que un usuario puede realizar.

CNST-034: Permisos function-based (NO Django perms)
CNST-036: Definida en fixtures JSON
"""

class Function(models.Model):
    """
    Función del sistema RBAC.
    
    Representa una acción granular en el sistema.
    
    Campos:
    - code: Código único (ej: AUD_VIEW)
    - name: Nombre descriptivo
    - module: Módulo al que pertenece
    - permission_string: String Django (audit.view)
    - is_active: Si está activa (vs planificada)
    
    Total: 46 funciones activas en RBAC v6.0.0
    """
    
    id = models.AutoField(
        db_column='iIdFuncion',
        primary_key=True
    )
    
    code = models.CharField(
        db_column='cCodigo',
        max_length=50,
        unique=True,
        help_text="Código único (ej: AUD_VIEW)"
    )
    
    name = models.CharField(
        db_column='cNombre',
        max_length=200,
        help_text="Nombre descriptivo"
    )
    
    description = models.TextField(
        db_column='tDescripcion',
        blank=True,
        help_text="Descripción de la función"
    )
    
    module = models.ForeignKey(
        Module,
        db_column='iIdModulo',
        on_delete=models.CASCADE,
        related_name='functions',
        help_text="Módulo al que pertenece"
    )
    
    permission_string = models.CharField(
        db_column='cPermisoString',
        max_length=100,
        help_text="String Django permission (audit.view)"
    )
    
    is_active = models.BooleanField(
        db_column='bActivo',
        default=True,
        help_text="Si está activa (vs planificada)"
    )
    
    version = models.CharField(
        db_column='cVersion',
        max_length=10,
        default='6.0.0',
        help_text="Versión RBAC que introdujo esta función"
    )
    
    created_at = models.DateTimeField(
        db_column='dFechaCreacion',
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'tbl_funciones'
        ordering = ['module', 'code']
        verbose_name = 'Función'
        verbose_name_plural = 'Funciones'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['module', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
```

### 7.3 Group

```python
"""
Grupo de usuarios.

Agrupa usuarios con permisos similares.

Example:
  GRP_Admin: Administradores (todas las funciones)
  GRP_Manager: Gerentes (20-25 funciones)
  GRP_Auditor: Auditores (8-10 funciones)
"""

class Group(models.Model):
    """
    Grupo de usuarios.
    
    Agrupa usuarios con roles similares.
    
    Campos:
    - code: Código único (ej: GRP_Admin)
    - name: Nombre descriptivo
    - description: Descripción del grupo
    - is_active: Si está activo
    """
    
    id = models.AutoField(
        db_column='iIdGrupo',
        primary_key=True
    )
    
    code = models.CharField(
        db_column='cCodigo',
        max_length=50,
        unique=True,
        help_text="Código único (ej: GRP_Admin)"
    )
    
    name = models.CharField(
        db_column='cNombre',
        max_length=200,
        help_text="Nombre descriptivo"
    )
    
    description = models.TextField(
        db_column='tDescripcion',
        blank=True,
        help_text="Descripción del grupo"
    )
    
    is_active = models.BooleanField(
        db_column='bActivo',
        default=True,
        help_text="Si está activo"
    )
    
    created_at = models.DateTimeField(
        db_column='dFechaCreacion',
        auto_now_add=True
    )
    
    # Many-to-many relationships
    users = models.ManyToManyField(
        'auth.User',
        through='UserGroup',
        related_name='access_groups'
    )
    
    functions = models.ManyToManyField(
        Function,
        through='GroupFunction',
        related_name='groups'
    )
    
    class Meta:
        db_table = 'tbl_grupos'
        ordering = ['code']
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
    
    def __str__(self):
        return f"{self.code} - {self.name}"
```

### 7.4 UserGroup

```python
"""
Relación User ← → Group (many-to-many).

Un usuario puede pertenecer a múltiples grupos.
"""

class UserGroup(models.Model):
    """
    Relación User ← → Group.
    
    Permite que un usuario pertenezca a múltiples grupos.
    
    CNST-034: Multi-grupo (vs Django single-group)
    """
    
    id = models.AutoField(
        db_column='iIdUsuarioGrupo',
        primary_key=True
    )
    
    user = models.ForeignKey(
        'auth.User',
        db_column='iIdUsuario',
        on_delete=models.CASCADE,
        related_name='group_memberships'
    )
    
    group = models.ForeignKey(
        Group,
        db_column='iIdGrupo',
        on_delete=models.CASCADE,
        related_name='user_memberships'
    )
    
    assigned_at = models.DateTimeField(
        db_column='dFechaAsignacion',
        auto_now_add=True
    )
    
    assigned_by = models.ForeignKey(
        'auth.User',
        db_column='iIdAsignadoPor',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+'
    )
    
    class Meta:
        db_table = 'tbl_usuario_grupo'
        unique_together = [['user', 'group']]
        verbose_name = 'Usuario-Grupo'
        verbose_name_plural = 'Usuarios-Grupos'
    
    def __str__(self):
        return f"{self.user.username} → {self.group.code}"
```

### 7.5 GroupFunction

```python
"""
Relación Group ← → Function (many-to-many).

Define qué funciones tiene cada grupo.
"""

class GroupFunction(models.Model):
    """
    Relación Group ← → Function.
    
    Define permisos del grupo.
    """
    
    id = models.AutoField(
        db_column='iIdGrupoFuncion',
        primary_key=True
    )
    
    group = models.ForeignKey(
        Group,
        db_column='iIdGrupo',
        on_delete=models.CASCADE,
        related_name='function_assignments'
    )
    
    function = models.ForeignKey(
        Function,
        db_column='iIdFuncion',
        on_delete=models.CASCADE,
        related_name='group_assignments'
    )
    
    assigned_at = models.DateTimeField(
        db_column='dFechaAsignacion',
        auto_now_add=True
    )
    
    assigned_by = models.ForeignKey(
        'auth.User',
        db_column='iIdAsignadoPor',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+'
    )
    
    class Meta:
        db_table = 'tbl_grupo_funcion'
        unique_together = [['group', 'function']]
        verbose_name = 'Grupo-Función'
        verbose_name_plural = 'Grupos-Funciones'
    
    def __str__(self):
        return f"{self.group.code} → {self.function.code}"
```

---

<a name="constants"></a>
## 8. CONSTANTS Y CONFIGURACIÓN

### 8.1 Archivo: apps/access/constants.py

```python
"""
Constantes para sistema RBAC.

CLEAN_CODE v3.0.1:
- Constantes: UPPER_SNAKE_CASE inglés
- Docstrings: español

CNST-034: Function-based permissions
CNST-035: Cache TTL
"""

# ===================================================================
# CACHE CONFIGURATION (CNST-035)
# ===================================================================

CACHE_TTL_FUNCTIONS = 300
"""TTL del cache de funciones por usuario (5 minutos)."""

CACHE_KEY_PREFIX = 'rbac'
"""Prefijo para keys de cache."""

CACHE_KEY_PATTERN = 'rbac:user_functions:{user_id}'
"""Patrón para cache key de funciones."""

# ===================================================================
# SYSTEM COUNTS
# ===================================================================

TOTAL_MODULES = 11
"""Total de módulos en RBAC v6.0.0."""

TOTAL_FUNCTIONS = 46
"""Total de funciones activas en RBAC v6.0.0."""

TOTAL_FUNCTIONS_PLANNED = 10
"""Total de funciones planificadas."""

# ===================================================================
# LIMITS
# ===================================================================

MAX_GROUPS_PER_USER = 10
"""Máximo de grupos por usuario."""

MAX_FUNCTIONS_PER_GROUP = 50
"""Máximo de funciones por grupo."""

# ===================================================================
# DEFAULT GROUPS
# ===================================================================

DEFAULT_GROUP = 'GRP_UserBasic'
"""Grupo asignado a nuevos usuarios."""

ADMIN_GROUP = 'GRP_Admin'
"""Grupo de administradores."""

# ===================================================================
# PERMISSION STRINGS FORMAT
# ===================================================================

PERMISSION_STRING_PATTERN = r'^[a-z_]+\.[a-z_]+$'
"""Pattern para permission strings (ej: audit.view)."""

# ===================================================================
# MODULES LIST (11 modules)
# ===================================================================

MODULES = [
    'MOD_Dashboard',
    'MOD_Audit',
    'MOD_Alerts',
    'MOD_Reports',
    'MOD_Calls',
    'MOD_Clients',
    'MOD_Services',
    'MOD_IVR',
    'MOD_Users',
    'MOD_Config',
    'MOD_System',
]
"""Lista de módulos del sistema."""

# ===================================================================
# FUNCTION CODES (46 active functions)
# ===================================================================

# Dashboard (6)
DSH_VIEW = 'DSH_VIEW'
DSH_EXP_CSV = 'DSH_EXP_CSV'
DSH_EXP_EXCEL = 'DSH_EXP_EXCEL'
DSH_EXP_PDF = 'DSH_EXP_PDF'  # Planificado
DSH_SHARE = 'DSH_SHARE'  # Planificado
DSH_EDIT = 'DSH_EDIT'  # Planificado

# Audit (4)
AUD_VIEW = 'AUD_VIEW'
AUD_SEARCH = 'AUD_SEARCH'
AUD_REPORT = 'AUD_REPORT'
AUD_EXPORT = 'AUD_EXPORT'

# Alerts (6)
ALR_VIEW = 'ALR_VIEW'
ALR_SEND = 'ALR_SEND'
ALR_MARK = 'ALR_MARK'
ALR_DELETE = 'ALR_DELETE'
ALR_CONF = 'ALR_CONF'
ALR_SUBS = 'ALR_SUBS'

# Reports (6)
RPT_VIEW = 'RPT_VIEW'
RPT_CREATE = 'RPT_CREATE'
RPT_DELETE = 'RPT_DELETE'
RPT_EXP_CSV = 'RPT_EXP_CSV'
RPT_EXP_EXCEL = 'RPT_EXP_EXCEL'
RPT_EXP_PDF = 'RPT_EXP_PDF'

# Calls (5)
CALL_VIEW = 'CALL_VIEW'
CALL_EDIT = 'CALL_EDIT'
CALL_DELETE = 'CALL_DELETE'
CALL_EXP_CSV = 'CALL_EXP_CSV'
CALL_STATS = 'CALL_STATS'

# Clients (4)
CLI_VIEW = 'CLI_VIEW'
CLI_EDIT = 'CLI_EDIT'
CLI_DELETE = 'CLI_DELETE'
CLI_MERGE = 'CLI_MERGE'

# Services (4)
SVC_VIEW = 'SVC_VIEW'
SVC_EDIT = 'SVC_EDIT'
SVC_DELETE = 'SVC_DELETE'
SVC_CONFIG = 'SVC_CONFIG'

# IVR (3)
IVR_VIEW = 'IVR_VIEW'
IVR_EDIT = 'IVR_EDIT'
IVR_STATS = 'IVR_STATS'

# Users (4)
USR_VIEW = 'USR_VIEW'
USR_EDIT = 'USR_EDIT'
USR_DELETE = 'USR_DELETE'
USR_PERMS = 'USR_PERMS'

# Config (2)
CFG_VIEW = 'CFG_VIEW'
CFG_EDIT = 'CFG_EDIT'

# System (2)
SYS_ADMIN = 'SYS_ADMIN'
SYS_LOGS = 'SYS_LOGS'

# ===================================================================
# ALL FUNCTIONS LIST
# ===================================================================

ALL_FUNCTIONS = [
    # Dashboard (6)
    DSH_VIEW, DSH_EXP_CSV, DSH_EXP_EXCEL,
    DSH_EXP_PDF, DSH_SHARE, DSH_EDIT,
    
    # Audit (4)
    AUD_VIEW, AUD_SEARCH, AUD_REPORT, AUD_EXPORT,
    
    # Alerts (6)
    ALR_VIEW, ALR_SEND, ALR_MARK, ALR_DELETE,
    ALR_CONF, ALR_SUBS,
    
    # Reports (6)
    RPT_VIEW, RPT_CREATE, RPT_DELETE,
    RPT_EXP_CSV, RPT_EXP_EXCEL, RPT_EXP_PDF,
    
    # Calls (5)
    CALL_VIEW, CALL_EDIT, CALL_DELETE,
    CALL_EXP_CSV, CALL_STATS,
    
    # Clients (4)
    CLI_VIEW, CLI_EDIT, CLI_DELETE, CLI_MERGE,
    
    # Services (4)
    SVC_VIEW, SVC_EDIT, SVC_DELETE, SVC_CONFIG,
    
    # IVR (3)
    IVR_VIEW, IVR_EDIT, IVR_STATS,
    
    # Users (4)
    USR_VIEW, USR_EDIT, USR_DELETE, USR_PERMS,
    
    # Config (2)
    CFG_VIEW, CFG_EDIT,
    
    # System (2)
    SYS_ADMIN, SYS_LOGS,
]
"""Lista completa de códigos de funciones."""

assert len(ALL_FUNCTIONS) == 46 + 10  # 46 activas + 10 planificadas
```

---

## 9. RESUMEN PARTE 1

### 9.1 Componentes Definidos

```yaml
Documentación:
  ✅ Resumen ejecutivo (importancia crítica)
  ✅ Propósito y responsabilidades (RBAC core)
  ✅ CLEAN_CODE v3.0.1 aplicado
  ✅ RESTRICCIONES (CNST-034, 035, 036)
  ✅ RBAC v6.0.0 sistema completo (46 funciones, 11 módulos)
  ✅ Arquitectura completa
  ✅ 6 modelos Django (Module, Function, Group, UserGroup, GroupFunction, PermissionLog)
  ✅ Constants (46 funciones definidas)

RBAC Sistema:
  ✅ 11 módulos (MOD_Dashboard, MOD_Audit, etc)
  ✅ 46 funciones activas
  ✅ 10 funciones planificadas
  ✅ 5-10 grupos típicos
  ✅ Multi-grupo support

Modelos:
  ✅ Module (11 registros)
  ✅ Function (46 registros)
  ✅ Group (5-10 grupos)
  ✅ UserGroup (many-to-many)
  ✅ GroupFunction (many-to-many)
  ⏳ PermissionLog (pendiente PARTE 2)
```

---

## PRÓXIMAS PARTES

**PARTE 2/6: Services y Validación**
- RBACService completo (has_function, get_user_functions)
- GroupService (CRUD grupos)
- PermissionCacheService
- PermissionLog model completo

**PARTE 3/6: Permissions y Decorators**
- DynamicFunctionPermission (DRF)
- FunctionPermissionMixin (CBV)
- @require_function decorator
- @require_any_function, @require_all_functions
- Template tags (has_function)

**PARTE 4/6: Middleware y APIs**
- RBACMiddleware
- ViewSets REST (8 endpoints)
- Serializers
- URLs

**PARTE 5/6: Fixtures y Testing**
- modules.json
- functions.json (46 funciones)
- groups.json
- Unit tests (services, permissions)
- API tests (8 endpoints)

**PARTE 6/6: Integration Testing y Deployment**
- E2E tests (flujo completo RBAC)
- Integration con todas las apps
- Migration strategy
- Deployment checklist

**Estimado PARTE 2:** ~1,300 líneas, 3 horas

---

**Fin de PARTE 1/6**
