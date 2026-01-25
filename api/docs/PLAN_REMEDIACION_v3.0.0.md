# PLAN DE REMEDIACIÓN COMPLETO v3.0.0 (REVISADO)

**Versión:** 3.0.0-rev1  
**Fecha:** 2026-01-21  
**Origen:** Post-FASE 3 + ANÁLISIS apps/access/ (PARTE 1-6) + DT-002  
**Estado:** PLANIFICACIÓN  
**Basado en:** 11 módulos reales del sistema + 46 funciones  

---

## 📋 RESUMEN EJECUTIVO

### Contexto

Este plan integra:
- ✅ **DT-002 (DECISIÓN TOMADA):** Eliminar UserServiceAccess
- ✅ **ANÁLISIS apps/access/ v3.0.0:** 6 partes documentadas
- ✅ **11 módulos reales:** MOD_Dashboard, MOD_Audit, MOD_Alerts, MOD_Reports, MOD_Calls, MOD_Clients, MOD_Services, MOD_IVR, MOD_Users, MOD_Config, MOD_System
- ✅ **46 funciones activas** en producción
- ✅ **Arquitectura RBAC v6.0.0** con Groups

### Decisión Clave (DT-002)

```yaml
UserServiceAccess: ELIMINAR ❌
  Razón:
    - RBAC puro: Function-based ✅
    - Service Access: Servicios 800 ❌
    - Mezcla conceptos
  
  Reemplazo:
    - Functions genéricas para pipeline/services
    - RequiresFunctionPermission en ViewSets
```

---

## 📊 ARQUITECTURA REAL (Según Análisis v3.0.0)

### Modelos apps/access/ (REAL)

```yaml
Modelos documentados en ANÁLISIS v3.0.0:
  1. Function (46 registros activos)
     - Funciones atómicas RBAC
     - Ejemplo: AUD_VIEW, DSH_EXP_CSV, RPT_CREATE
  
  2. Module (11 módulos)
     - Agrupa functions
     - Ejemplo: MOD_Audit, MOD_Dashboard
  
  3. Group (5-10 grupos típicos)
     - Grupos de usuarios
     - Ejemplo: GRP_Admin, GRP_Manager
  
  4. UserGroup (many-to-many)
     - User ↔ Group
  
  5. GroupFunction (many-to-many)
     - Group ↔ Function
  
  6. PermissionLog (auditoría)
     - Log de cambios permisos

Modelos NO documentados (agregados después):
  ❌ UserServiceAccess → A ELIMINAR (DT-002)
  ⚠️ UserModuleAccess → Revisar si mantener
```

### 11 Módulos Reales del Sistema

```yaml
MOD_Dashboard (6 funciones):
  ✅ DSH_VIEW, DSH_EXP_CSV, DSH_EXP_EXCEL
  ⏳ DSH_EXP_PDF, DSH_SHARE, DSH_EDIT (planificados)

MOD_Audit (4 funciones):
  ✅ AUD_VIEW, AUD_SEARCH, AUD_REPORT, AUD_EXPORT

MOD_Alerts (6 funciones):
  ✅ ALR_VIEW, ALR_SEND, ALR_MARK, ALR_DELETE
  ✅ ALR_CONF, ALR_SUBS

MOD_Reports (6 funciones):
  ✅ RPT_VIEW, RPT_CREATE, RPT_DELETE
  ✅ RPT_EXP_CSV, RPT_EXP_EXCEL, RPT_EXP_PDF

MOD_Calls (5 funciones):
  ✅ CALL_VIEW, CALL_EDIT, CALL_DELETE
  ✅ CALL_EXP_CSV, CALL_STATS

MOD_Clients (4 funciones):
  ✅ CLI_VIEW, CLI_EDIT, CLI_DELETE, CLI_MERGE

MOD_Services (4 funciones):
  ✅ SVC_VIEW, SVC_EDIT, SVC_DELETE, SVC_CONFIG

MOD_IVR (3 funciones):
  ✅ IVR_VIEW, IVR_EDIT, IVR_STATS

MOD_Users (4 funciones):
  ✅ USR_VIEW, USR_EDIT, USR_DELETE, USR_PERMS

MOD_Config (2 funciones):
  ✅ CFG_VIEW, CFG_EDIT

MOD_System (2 funciones):
  ✅ SYS_ADMIN, SYS_LOGS

TOTAL: 11 módulos, 46 funciones activas
```

### Flujo RBAC v6.0.0 (REAL)

```
1. Usuario pertenece a Group(s)
   User → UserGroup → Group

2. Group tiene Function(s)
   Group → GroupFunction → Function

3. Usuario hereda Functions de sus Groups
   User.functions = Union de todos Group.functions

4. Permission check en ViewSet:
   RequiresFunctionPermission → user.has_function('AUD_VIEW')

5. has_function() query:
   UserGroup → GroupFunction → Function
   Verifica si user tiene función vía grupos
```

---

## 🚨 PROBLEMA PRINCIPAL (DT-002)

### UserServiceAccess - ELIMINAR

**Estado:** Decisión tomada, pendiente ejecución

**Descripción:**
```yaml
UserServiceAccess NO aparece en:
  ❌ ANALISIS_APP_ACCESS_v3_0_0 (6 partes)
  ❌ MODELO_RBAC_IACT_v6_0_0
  ❌ Arquitectura documentada

Aparece en:
  ✅ apps/access/models.py (código real)
  ✅ apps/core/permissions.py (HasServiceAccess)
  ✅ apps/pipeline/ (uso)

Conclusión:
  - Agregado fuera de arquitectura
  - Mezcla RBAC con servicios 800
  - Debe eliminarse (DT-002 decidido)
```

**Impacto:**
```yaml
SRP violado:
  - apps/access/ debe ser RBAC puro
  - Services 800 no son parte de RBAC
  - SRP actual: 7/10 → Después: 9/10

Código afectado:
  - apps/access/models.py (UserServiceAccess)
  - apps/core/permissions.py (HasServiceAccess)
  - apps/pipeline/views.py (uso)
  - tests/unit/core/test_permissions.py
```

---

## 🛠️ PLAN DE REMEDIACIÓN (Basado en DT-002)

### FASE A: Eliminación UserServiceAccess (3-4h)

**Ejecuta DT-002 completo**

#### A.1: Análisis de Impacto (30 min)

```bash
# Identificar usos
grep -r "UserServiceAccess" apps/
grep -r "HasServiceAccess" apps/
grep -r "service.*800" apps/pipeline/

# Verificar data
python manage.py shell
>>> from apps.access.models import UserServiceAccess
>>> UserServiceAccess.objects.count()
```

#### A.2: Crear Functions para Services (30 min)

**Usar módulo real MOD_Services:**

```python
# Script: create_service_functions.py

from apps.access.models import Function, Module

# MOD_Services ya existe con 4 funciones:
# - SVC_VIEW, SVC_EDIT, SVC_DELETE, SVC_CONFIG

# Verificar si SVC_VIEW cubre servicios 800
service_module = Module.objects.get(code='MOD_Services')
functions = Function.objects.filter(module=service_module)

print("Funciones existentes en MOD_Services:")
for func in functions:
    print(f"  - {func.code}: {func.name}")

# Si SVC_VIEW no cubre servicios 800, agregar:
Function.objects.get_or_create(
    code='SVC_VIEW_800',
    defaults={
        'name': 'Ver Servicios 800',
        'description': 'Permiso para ver servicios 800',
        'module': service_module,
        'is_active': True,
    }
)
```

**IMPORTANTE:** Usar funciones reales del sistema, NO inventar.

#### A.3: Actualizar ViewSets (1h)

```python
# apps/pipeline/views.py

# ANTES (con HasServiceAccess)
class ServiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasServiceAccess]
    # Lógica UserServiceAccess

# DESPUÉS (con RBAC puro)
from apps.core.permissions import RequiresFunctionPermission

class ServiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    function_map = {
        'list': 'SVC_VIEW',      # Ya existe en MOD_Services
        'retrieve': 'SVC_VIEW',
        'create': 'SVC_EDIT',    # Ya existe
        'update': 'SVC_EDIT',
        'partial_update': 'SVC_EDIT',
        'destroy': 'SVC_DELETE', # Ya existe
        'configure': 'SVC_CONFIG', # Ya existe
    }
```

#### A.4: Eliminar Código (30 min)

```yaml
Eliminar:
  ✅ apps/access/models.py:
     - class UserServiceAccess
     - Migrations relacionadas
  
  ✅ apps/core/permissions.py:
     - class HasServiceAccess
     - Export en __init__.py
  
  ✅ apps/access/serializers.py:
     - UserServiceAccessSerializer (si existe)
  
  ✅ apps/access/filters.py:
     - UserServiceAccessFilter (si existe)
  
  ✅ tests/unit/core/test_permissions.py:
     - TestHasServiceAccess (5 tests)
```

#### A.5: Migración DB (30 min)

```bash
# Crear migración
python manage.py makemigrations access -n "remove_user_service_access"

# Revisar migración
cat apps/access/migrations/000X_remove_user_service_access.py

# Aplicar
python manage.py migrate access
```

#### A.6: Testing (1h)

```bash
# Tests unitarios
pytest tests/unit/access/ -v
pytest tests/unit/core/test_permissions.py -v

# Tests integración
pytest tests/integration/pipeline/ -v

# Verificación manual
# Login como usuario con SVC_VIEW
# GET /api/pipeline/services/ → 200 OK
```

---

### FASE B: Clarificar UserModuleAccess (1h)

**Objetivo:** Decidir si mantener o eliminar UserModuleAccess.

**Contexto:**
```yaml
UserModuleAccess:
  - NO aparece en ANALISIS v3.0.0
  - SÍ aparece en código (apps/access/models.py)
  - Diferente de arquitectura RBAC v6.0.0

Arquitectura v6.0.0 usa:
  - User → UserGroup → Group
  - Group → GroupFunction → Function
  - NO menciona UserModuleAccess
```

**Opciones:**

```yaml
Opción 1: Eliminar UserModuleAccess
  Razón:
    - NO está en arquitectura documentada
    - Groups ya agrupan functions por módulo
    - Redundante con Groups
  
  Proceso:
    - Similar a UserServiceAccess
    - Migrar a Groups si necesario

Opción 2: Mantener UserModuleAccess
  Razón:
    - Controla visibilidad UI (qué ve en menú)
    - Separado de permisos (qué puede hacer)
    - Útil para UX
  
  Requisito:
    - Documentar claramente
    - Diferencia Module access vs Function permissions

Opción 3: Audit completo
  Razón:
    - Verificar uso real en código
    - Decidir basado en evidencia
```

**Tareas:**

```yaml
☐ Tarea 1: Audit uso UserModuleAccess (30 min)
  grep -r "UserModuleAccess" apps/
  grep -r "module.*access" apps/
  Revisar ViewSets que usan

☐ Tarea 2: Decisión (15 min)
  Si usa mucho → Mantener y documentar
  Si usa poco → Eliminar
  Si no usa → Eliminar

☐ Tarea 3: Ejecutar decisión (15 min)
  Mantener: Agregar a docs
  Eliminar: Similar a UserServiceAccess
```

---

### FASE C: Documentación (2h)

**Objetivo:** Documentar arquitectura REAL basada en ANÁLISIS v3.0.0.

#### C.1: apps/access/README.md (1h)

```markdown
# apps/access/ - RBAC Sistema v6.0.0

## 🎯 Arquitectura RBAC

### Modelos (6)

```yaml
Function (46 activas):
  - Funciones atómicas del sistema
  - Ejemplos: AUD_VIEW, DSH_EXP_CSV, RPT_CREATE
  - Organizadas en 11 módulos

Module (11 módulos):
  - Agrupación lógica de functions
  - MOD_Dashboard, MOD_Audit, MOD_Alerts, etc.

Group (5-10 grupos):
  - Grupos de usuarios
  - GRP_Admin, GRP_Manager, GRP_Analyst, etc.

UserGroup (many-to-many):
  - Asigna usuarios a grupos
  - User ↔ Group

GroupFunction (many-to-many):
  - Asigna functions a grupos
  - Group ↔ Function

PermissionLog (auditoría):
  - Log de cambios en permisos
```

### Flujo RBAC

```
1. Admin crea Group:
   GRP_ReportsAdmin

2. Admin asigna Functions a Group:
   GRP_ReportsAdmin ← RPT_VIEW
   GRP_ReportsAdmin ← RPT_CREATE
   GRP_ReportsAdmin ← RPT_EXP_CSV

3. Admin asigna User a Group:
   Usuario "juan" → GRP_ReportsAdmin

4. Usuario hereda Functions:
   juan.functions = {RPT_VIEW, RPT_CREATE, RPT_EXP_CSV}

5. Permission check en API:
   RequiresFunctionPermission('RPT_VIEW')
   → juan.has_function('RPT_VIEW')
   → Query: UserGroup → GroupFunction
   → Result: True ✅
```

### Ejemplo Completo

```python
from apps.access.models import Function, Group, GroupFunction, UserGroup

# 1. Crear Group
reports_admin = Group.objects.create(
    code='GRP_ReportsAdmin',
    name='Administradores de Reportes',
    description='Acceso completo a módulo reportes',
)

# 2. Obtener Functions de MOD_Reports
report_functions = Function.objects.filter(
    code__startswith='RPT_'
)

# 3. Asignar Functions a Group
for function in report_functions:
    GroupFunction.objects.create(
        group=reports_admin,
        function=function,
        assigned_by=admin_user,
    )

# 4. Asignar User a Group
UserGroup.objects.create(
    user=juan,
    group=reports_admin,
    assigned_by=admin_user,
)

# 5. Verificar permisos
juan.has_function('RPT_VIEW')  # → True
juan.has_function('AUD_VIEW')  # → False (no en grupo)
```

### ViewSet Implementation

```python
from apps.core.permissions import RequiresFunctionPermission

class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    function_map = {
        'list': 'RPT_VIEW',
        'retrieve': 'RPT_VIEW',
        'create': 'RPT_CREATE',
        'update': 'RPT_CREATE',  # O RPT_EDIT si existe
        'destroy': 'RPT_DELETE',
        'export_csv': 'RPT_EXP_CSV',
    }
```

## 📋 Módulos y Functions

### MOD_Dashboard (6 funciones)
- DSH_VIEW: Ver dashboard
- DSH_EXP_CSV: Exportar CSV
- DSH_EXP_EXCEL: Exportar Excel

### MOD_Audit (4 funciones)
- AUD_VIEW: Ver auditoría
- AUD_SEARCH: Buscar en auditoría
- AUD_REPORT: Generar reportes
- AUD_EXPORT: Exportar auditoría

### MOD_Alerts (6 funciones)
- ALR_VIEW: Ver alertas
- ALR_SEND: Enviar alertas
- ALR_MARK: Marcar alertas
- ALR_DELETE: Eliminar alertas
- ALR_CONF: Configurar alertas
- ALR_SUBS: Suscripciones alertas

### MOD_Reports (6 funciones)
- RPT_VIEW: Ver reportes
- RPT_CREATE: Crear reportes
- RPT_DELETE: Eliminar reportes
- RPT_EXP_CSV: Exportar CSV
- RPT_EXP_EXCEL: Exportar Excel
- RPT_EXP_PDF: Exportar PDF

### MOD_Calls (5 funciones)
- CALL_VIEW: Ver llamadas
- CALL_EDIT: Editar llamadas
- CALL_DELETE: Eliminar llamadas
- CALL_EXP_CSV: Exportar llamadas
- CALL_STATS: Estadísticas llamadas

### MOD_Clients (4 funciones)
- CLI_VIEW: Ver clientes
- CLI_EDIT: Editar clientes
- CLI_DELETE: Eliminar clientes
- CLI_MERGE: Fusionar clientes

### MOD_Services (4 funciones)
- SVC_VIEW: Ver servicios
- SVC_EDIT: Editar servicios
- SVC_DELETE: Eliminar servicios
- SVC_CONFIG: Configurar servicios

### MOD_IVR (3 funciones)
- IVR_VIEW: Ver IVR
- IVR_EDIT: Editar IVR
- IVR_STATS: Estadísticas IVR

### MOD_Users (4 funciones)
- USR_VIEW: Ver usuarios
- USR_EDIT: Editar usuarios
- USR_DELETE: Eliminar usuarios
- USR_PERMS: Gestionar permisos

### MOD_Config (2 funciones)
- CFG_VIEW: Ver configuración
- CFG_EDIT: Editar configuración

### MOD_System (2 funciones)
- SYS_ADMIN: Administración sistema
- SYS_LOGS: Ver logs sistema

## 🚫 Eliminado

### UserServiceAccess ❌

**Razón:** No parte de arquitectura RBAC v6.0.0
**Fecha eliminación:** 2026-01-21
**DT-002:** Decisión tomada

Reemplazado por:
- Usar SVC_VIEW, SVC_EDIT, etc. (MOD_Services)
- RBAC puro con Groups y Functions
```
```

#### C.2: INTEGRATION_GUIDE_ACCESS.md (1h)

Basado en módulos y funciones REALES (no Facturación).

---

## 📅 CRONOGRAMA

```yaml
Semana 1 (CRÍTICO):
  Día 1: FASE A (UserServiceAccess) - 3-4h
     ✅ Ejecuta DT-002 completo
     ✅ Usa MOD_Services existente
  
  Día 2: FASE B (UserModuleAccess audit) - 1h
     ⚠️ Decidir si mantener o eliminar
  
  Día 3: FASE C (Documentación) - 2h
     ✅ Basada en ANÁLISIS v3.0.0
     ✅ Módulos reales del sistema

Total: 6-7h
```

---

## ✅ CRITERIOS DE ACEPTACIÓN

```yaml
FASE A (DT-002):
  ✅ UserServiceAccess eliminado
  ✅ HasServiceAccess eliminado
  ✅ ViewSets usan RequiresFunctionPermission
  ✅ Functions MOD_Services usadas
  ✅ Tests pasando
  ✅ SRP mejorado a 9/10

FASE B (UserModuleAccess):
  ✅ Audit completo
  ✅ Decisión tomada (mantener o eliminar)
  ✅ Documentado o eliminado

FASE C (Docs):
  ✅ README basado en ANÁLISIS v3.0.0
  ✅ 11 módulos reales documentados
  ✅ 46 funciones documentadas
  ✅ Ejemplos con módulos reales (no inventados)
```

---

## 📊 DIFERENCIAS CON ARQUITECTURA

### Modelos en ANÁLISIS v3.0.0

```yaml
Documentados:
  ✅ Function
  ✅ Module
  ✅ Group
  ✅ UserGroup
  ✅ GroupFunction
  ✅ PermissionLog
```

### Modelos en Código Real

```yaml
Encontrados:
  ✅ Function
  ✅ Module
  ⚠️ UserModuleAccess (NO documentado)
  ❌ UserServiceAccess (A eliminar)
  ⚠️ Group (verificar)
  ⚠️ UserGroup (verificar)
  ⚠️ GroupFunction (verificar)
```

### Acción Requerida

```yaml
FASE B debe verificar:
  - ¿Group, UserGroup, GroupFunction existen?
  - ¿O solo Function y UserFunctionAssignment?
  - ¿UserModuleAccess es necesario?
```

---

**Versión:** 3.0.0-rev1  
**Basado en:** ANÁLISIS v3.0.0 (6 partes) + DT-002  
**Módulos:** 11 reales del sistema  
**Funciones:** 46 activas documentadas  
**Estado:** REVISADO - Listo para ejecutar  
**Próximo paso:** Ejecutar FASE A (DT-002)

**Versión:** 3.0.0  
**Fecha:** 2026-01-21  
**Origen:** Post-FASE 3 - Análisis arquitectura apps/access/  
**Estado:** PLANIFICACIÓN  

---

## 📋 ÍNDICE

1. [Estado Actual](#estado-actual)
2. [Problemas Identificados](#problemas-identificados)
3. [Estado Deseado](#estado-deseado)
4. [Plan de Remediación](#plan-de-remediación)
5. [Cronograma y Estimaciones](#cronograma-y-estimaciones)
6. [Criterios de Aceptación](#criterios-de-aceptación)

---

## 📊 ESTADO ACTUAL

### Arquitectura apps/access/ (Actual)

```yaml
Modelos (5):
  1. Module:
     - Módulos jerárquicos (parent/children)
     - Visibilidad en UI
     - Jerarquía: MOD_Dashboard > MOD_Dashboard_View
  
  2. UserModuleAccess:
     - Acceso de usuarios a módulos
     - Herencia: acceso a padre = acceso a hijos
     - Controla VISIBILIDAD
  
  3. Function:
     - Funciones atómicas RBAC
     - 46 funciones en 11 módulos
     - Permisos granulares
  
  4. UserFunctionAssignment:
     - Asignación MANUAL de funciones
     - Controla PERMISOS (qué puede hacer)
     - NO automático desde módulo
  
  5. UserServiceAccess: ❌ A ELIMINAR
     - Acceso a servicios 800
     - Conceptualmente diferente de RBAC
     - Mezcla conceptos

Flujo RBAC Actual:
  1. UserModuleAccess → Usuario tiene acceso a módulo (VISIBILIDAD)
  2. UserFunctionAssignment → Usuario tiene permisos en módulo (ACCIONES)
  3. Separados: Tener acceso ≠ Tener permisos
```

### Relación Module ↔ Function (Actual)

```yaml
Module:
  - code: "MOD_Reports"
  - name: "Reportes"
  - Visibilidad en menú

Function:
  - code: "reports.view"
  - module: "MOD_Reports"  # ← String reference, NO FK
  - Permiso para ver reportes

Relación: DÉBIL (string reference)
  - Function.module es CharField, NO ForeignKey
  - No hay integridad referencial
  - Propenso a inconsistencias
```

### Permission System Flow (Actual)

```
1. Usuario hace request:
   GET /api/reports/

2. RequiresFunctionPermission:
   - Verifica user.has_function('reports.view')
   - UserFunctionAssignment.objects.filter(
       user=user,
       function__code='reports.view',
       is_active=True
     ).exists()

3. SI has_function() = True:
   → 200 OK

4. UserModuleAccess:
   - NO interviene en permisos
   - Solo controla visibilidad en UI
   - Frontend: if (user.hasModuleAccess('MOD_Reports')) { showMenuItem() }
```

### HasServiceAccess Permission (Actual) ❌

```python
# apps/core/permissions.py
class HasServiceAccess(permissions.BasePermission):
    """
    Permission para acceso a servicios 800.
    
    ❌ PROBLEMA: Conceptualmente diferente de RBAC
    ❌ A ELIMINAR
    """
    
    def has_permission(self, request, view):
        # Lógica específica de servicios 800
        # NO alineado con RBAC
        pass
```

---

## 🚨 PROBLEMAS IDENTIFICADOS

### PROBLEMA 1: UserServiceAccess (CRÍTICO)

**Descripción:**
```yaml
UserServiceAccess mezcla dos conceptos:
  - RBAC: Permisos basados en funciones/módulos ✅
  - Service Access: Permisos basados en servicios 800 ❌

Impacto:
  - Confusión arquitectural
  - Código duplicado (HasServiceAccess vs RequiresFunctionPermission)
  - Inconsistencia en control de acceso
  - SRP violado en apps/access/ (7/10)

Usado en:
  - apps/pipeline/views.py
  - apps/core/permissions.py (HasServiceAccess)
  - apps/access/models.py (UserServiceAccess model)
```

**Evidencia:**
```python
# UserServiceAccess (A ELIMINAR)
class UserServiceAccess(SoftDeleteMixin, models.Model):
    user = models.ForeignKey(User, ...)
    servicio_800 = models.CharField(max_length=20)  # ← Específico, no RBAC
    # ...
```

**Solución:** Reemplazar con RBAC puro usando Functions.

---

### PROBLEMA 2: Module-Function Relación Débil (MEDIO)

**Descripción:**
```yaml
Function.module es CharField, NO ForeignKey:
  - No hay integridad referencial
  - Inconsistencias posibles (module="MOD_Reporst" - typo)
  - Cambios en Module.code NO se propagan
  - Queries lentos (sin JOIN, solo string matching)

Actual:
  class Function(models.Model):
      module = models.CharField(max_length=50)  # ← String

Ideal:
  class Function(models.Model):
      module = models.ForeignKey(Module, ...)   # ← FK
```

**Impacto:**
```yaml
Medio:
  - Funciona pero frágil
  - Requiere cuidado manual
  - Propenso a errores humanos

Ejemplos de riesgo:
  - Admin cambia Module.code: "MOD_Reports" → "MOD_Reportes"
  - 15 Functions quedan huérfanas (module="MOD_Reports" old)
  - Permissions rotos hasta actualizar manualmente
```

**Solución:** Migrar module a ForeignKey (opcional, mejora calidad).

---

### PROBLEMA 3: Documentación Confusa (BAJO)

**Descripción:**
```yaml
Relación Module ↔ Function NO está clara:
  - Docs no explican que son sistemas separados
  - Onboarding confuso: "¿Dar acceso a módulo da permisos?"
  - Respuesta: NO, pero no está documentado

Falta claridad en:
  - Module = VISIBILIDAD (UI)
  - Function = PERMISOS (acciones)
  - Asignación MANUAL
```

**Impacto:**
```yaml
Bajo:
  - Confusión inicial
  - Errores de uso
  - Preguntas repetidas

No bloquea desarrollo pero:
  - Reduce eficiencia
  - Aumenta errores
```

**Solución:** Documentar claramente en README y guía de integración.

---

### PROBLEMA 4: Arquitectura 4 Apps (BAJO-MEDIO)

**Descripción:**
```yaml
La arquitectura mencionada difiere del código:

Arquitectura mencionada:
  apps/users/ → Sin has_function() ❌
  apps/authentication/ → Sin SessionHistory ❌
  apps/access/ → Con Group, GroupFunction, PermissionLog ❌
  apps/alerts/ → OK

Código real:
  apps/users/ → CON has_function() ✅
  apps/authentication/ → ¿SessionHistory? (revisar)
  apps/access/ → Sin Group, Sin GroupFunction ✅
  apps/alerts/ → (revisar)

Inconsistencia:
  - Docs vs código
  - Puede haber features faltantes o sobras
```

**Impacto:**
```yaml
Medio:
  - Confusión en arquitectura
  - ¿Qué es real vs planeado?
  - Requiere audit completo
```

**Solución:** Audit de 4 apps vs arquitectura documentada.

---

## 🎯 ESTADO DESEADO

### Arquitectura apps/access/ (Deseado)

```yaml
Modelos (4) - Sin UserServiceAccess:
  1. Module:
     - Jerárquico (parent/children)
     - Controla VISIBILIDAD en UI
     - FK desde Function
  
  2. UserModuleAccess:
     - Acceso a módulos
     - Herencia padre→hijos
     - Solo VISIBILIDAD
  
  3. Function:
     - Funciones atómicas RBAC
     - module = ForeignKey(Module) ← FK
     - Controla PERMISOS
  
  4. UserFunctionAssignment:
     - Asignación MANUAL funciones
     - NO automático desde módulo
     - Controla ACCIONES

Eliminados:
  ❌ UserServiceAccess
  ❌ HasServiceAccess permission

Agregados:
  ✅ Functions específicas para servicios 800 (si necesario)
  ✅ FK Module en Function (opcional)
```

### Permission System Flow (Deseado)

```
1. Usuario hace request:
   GET /api/pipeline/services/

2. RequiresFunctionPermission:
   function_map = {
       'list': 'pipeline.view_services',  # ← Function genérica
   }
   
   Verifica: user.has_function('pipeline.view_services')

3. UserFunctionAssignment:
   - Asignado manualmente a usuario
   - Controla permiso de VER servicios

4. UserModuleAccess:
   - Controla si ve menú "Pipeline" en UI
   - NO interviene en API permissions

5. NO HAY HasServiceAccess ni UserServiceAccess
```

### RBAC Puro con Servicios 800

**Opción A: Functions genéricas (Recomendado)**

```yaml
Functions creadas:
  - pipeline.view_services
  - pipeline.create_service
  - pipeline.edit_service
  - pipeline.delete_service

Permisos:
  - Usuario con pipeline.view_services → Ve TODOS los servicios
  - Sin filtrado por servicio 800 específico
  - Más simple, RBAC puro
```

**Opción B: Functions específicas por servicio (Si necesario)**

```yaml
Si realmente se requiere control por servicio 800:

Functions creadas dinámicamente:
  - pipeline.view_service_800123456
  - pipeline.view_service_800999999

Permisos:
  - Usuario con pipeline.view_service_800123456 → Solo ve ese servicio
  - Granular pero complejo
  - 46+ funciones → 100+ funciones

Recomendación: NO hacer esto
  - Demasiado granular
  - Difícil de mantener
  - Usar filtros en queries mejor
```

### Documentación Clara (Deseado)

```yaml
README apps/access/:
  Sección: Module vs Function
  
  Claridad:
    ✅ Module = VISIBILIDAD
       - Controla qué ve en UI
       - Herencia padre→hijos
       - UserModuleAccess
    
    ✅ Function = PERMISOS
       - Controla qué puede hacer
       - Asignación MANUAL
       - UserFunctionAssignment
    
    ✅ Workflow:
       1. Admin da acceso a módulo → Usuario ve menú
       2. Admin asigna funciones → Usuario puede hacer acciones
       3. NO automático: Módulo ≠ Funciones
```

---

## 🛠️ PLAN DE REMEDIACIÓN

### FASE A: Eliminación UserServiceAccess (3-4h)

**Objetivo:** Eliminar UserServiceAccess y HasServiceAccess, migrar a RBAC puro.

#### A.1: Análisis de Impacto (30 min)

**Tareas:**
```yaml
☐ Identificar todos los usos de UserServiceAccess:
  grep -r "UserServiceAccess" apps/
  grep -r "HasServiceAccess" apps/

☐ Listar ViewSets afectados:
  - apps/pipeline/views.py
  - apps/core/permissions.py

☐ Verificar data en DB:
  UserServiceAccess.objects.count()
  
☐ Decisión: ¿Migrar data o eliminar?
  - Si <100 registros → Reasignar manualmente
  - Si >100 registros → Script de migración
```

#### A.2: Crear Functions para Servicios (30 min)

**Opción A: Functions genéricas (Recomendado)**

```python
# Script: create_pipeline_functions.py

from apps.access.models import Function, Module

# Obtener módulo Pipeline
pipeline_module = Module.objects.get(code='MOD_Pipeline')

# Crear functions genéricas
functions = [
    {
        'code': 'pipeline.view_services',
        'name': 'Ver Servicios',
        'description': 'Permiso para ver todos los servicios',
        'module': 'MOD_Pipeline',  # String o FK
    },
    {
        'code': 'pipeline.create_service',
        'name': 'Crear Servicio',
        'description': 'Permiso para crear servicios',
        'module': 'MOD_Pipeline',
    },
    {
        'code': 'pipeline.edit_service',
        'name': 'Editar Servicio',
        'description': 'Permiso para editar servicios',
        'module': 'MOD_Pipeline',
    },
    {
        'code': 'pipeline.delete_service',
        'name': 'Eliminar Servicio',
        'description': 'Permiso para eliminar servicios',
        'module': 'MOD_Pipeline',
    },
]

for func_data in functions:
    Function.objects.get_or_create(
        code=func_data['code'],
        defaults=func_data
    )
```

**Opción B: Migrar UserServiceAccess → UserFunctionAssignment (Si data importante)**

```python
# Script: migrate_service_access_to_rbac.py

from apps.access.models import (
    UserServiceAccess,
    UserFunctionAssignment,
    Function,
)

# Función genérica para ver servicios
view_services_func = Function.objects.get(code='pipeline.view_services')

# Migrar cada UserServiceAccess
for service_access in UserServiceAccess.objects.filter(is_active=True):
    # Crear UserFunctionAssignment si no existe
    UserFunctionAssignment.objects.get_or_create(
        user=service_access.user,
        function=view_services_func,
        defaults={
            'assigned_by': service_access.granted_by,
            'reason': f'Migrado de UserServiceAccess (servicio: {service_access.servicio_800})',
        }
    )

print(f'Migrados {count} registros')
```

#### A.3: Actualizar ViewSets a RBAC (1h)

**Antes:**
```python
# apps/pipeline/views.py (ANTES)
from apps.core.permissions import HasServiceAccess

class ServiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasServiceAccess]
    # Lógica específica de servicio 800
```

**Después:**
```python
# apps/pipeline/views.py (DESPUÉS)
from apps.core.permissions import RequiresFunctionPermission

class ServiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    function_map = {
        'list': 'pipeline.view_services',
        'retrieve': 'pipeline.view_services',
        'create': 'pipeline.create_service',
        'update': 'pipeline.edit_service',
        'partial_update': 'pipeline.edit_service',
        'destroy': 'pipeline.delete_service',
    }
```

#### A.4: Eliminar Código (30 min)

```yaml
☐ Eliminar UserServiceAccess model:
  - apps/access/models.py

☐ Eliminar HasServiceAccess permission:
  - apps/core/permissions.py
  - apps/core/__init__.py (export)

☐ Eliminar serializers relacionados:
  - apps/access/serializers.py (UserServiceAccessSerializer)

☐ Eliminar filters:
  - apps/access/filters.py

☐ Eliminar tests:
  - tests/unit/core/test_permissions.py (TestHasServiceAccess)
```

#### A.5: Migración DB (30 min)

```bash
# Crear migración
python manage.py makemigrations access -n "remove_user_service_access"

# Revisar migración generada
cat apps/access/migrations/000X_remove_user_service_access.py

# Aplicar migración
python manage.py migrate access
```

#### A.6: Testing y Verificación (1h)

```yaml
☐ Tests unitarios:
  pytest tests/unit/access/ -v
  pytest tests/unit/core/test_permissions.py -v

☐ Tests de integración:
  - Verificar endpoints pipeline/ funcionan
  - Verificar permissions con usuario normal
  - Verificar permissions con superuser

☐ Verificación manual:
  - Login como usuario con pipeline.view_services
  - GET /api/pipeline/services/ → 200 OK
  - POST /api/pipeline/services/ → 403 (sin create)
```

---

### FASE B: Module-Function FK (Opcional, 2-3h)

**Objetivo:** Mejorar integridad referencial Module ↔ Function.

**Nota:** Esta fase es OPCIONAL. El sistema funciona con CharField.

#### B.1: Análisis Pre-Migración (30 min)

```yaml
☐ Verificar consistencia actual:
  SELECT DISTINCT module FROM functions;
  SELECT code FROM modules;
  
☐ Identificar inconsistencias:
  - Functions con module que no existe
  - Typos en module names

☐ Limpiar data antes de migrar:
  UPDATE functions SET module='MOD_Reports' WHERE module='MOD_Reporst';
```

#### B.2: Migración module CharField → FK (1h)

```python
# Migration: apps/access/migrations/000X_function_module_fk.py

from django.db import migrations, models

class Migration(migrations.Migration):
    
    dependencies = [
        ('access', '000X_previous'),
    ]
    
    operations = [
        # Paso 1: Agregar nuevo field module_fk (nullable)
        migrations.AddField(
            model_name='function',
            name='module_fk',
            field=models.ForeignKey(
                'Module',
                on_delete=models.CASCADE,
                null=True,
                blank=True,
                related_name='functions',
            ),
        ),
        
        # Paso 2: Migrar data (RunPython)
        migrations.RunPython(
            migrate_module_to_fk,
            reverse_code=migrations.RunPython.noop,
        ),
        
        # Paso 3: Eliminar old field module (CharField)
        migrations.RemoveField(
            model_name='function',
            name='module',
        ),
        
        # Paso 4: Renombrar module_fk → module
        migrations.RenameField(
            model_name='function',
            old_name='module_fk',
            new_name='module',
        ),
        
        # Paso 5: Hacer NOT NULL
        migrations.AlterField(
            model_name='function',
            name='module',
            field=models.ForeignKey(
                'Module',
                on_delete=models.CASCADE,
                related_name='functions',
            ),
        ),
    ]

def migrate_module_to_fk(apps, schema_editor):
    """Migrar module CharField → FK."""
    Function = apps.get_model('access', 'Function')
    Module = apps.get_model('access', 'Module')
    
    for function in Function.objects.all():
        module_code = function.module  # CharField
        try:
            module = Module.objects.get(code=module_code)
            function.module_fk = module
            function.save()
        except Module.DoesNotExist:
            # Log error
            print(f'ERROR: Module {module_code} no existe para Function {function.code}')
```

#### B.3: Actualizar Código (30 min)

```python
# Antes
class Function(models.Model):
    module = models.CharField(max_length=50)  # String

# Después
class Function(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='functions',
    )

# Queries mejorados
# Antes: Function.objects.filter(module='MOD_Reports')
# Después: Function.objects.filter(module__code='MOD_Reports')
# O mejor: Function.objects.filter(module=module_instance)
```

#### B.4: Testing (1h)

```yaml
☐ Verificar migración:
  - Todos los Functions tienen module FK
  - No hay funciones huérfanas
  
☐ Tests actualizados:
  - Queries con module__code
  
☐ Performance:
  - JOINs automáticos más rápidos
```

---

### FASE C: Documentación (2h)

**Objetivo:** Documentar claramente Module vs Function.

#### C.1: apps/access/README.md (1h)

```markdown
# apps/access/ - RBAC Sistema

## 🎯 Conceptos Clave

### Module vs Function

**IMPORTANTE:** Module y Function son sistemas SEPARADOS que trabajan juntos.

#### Module = VISIBILIDAD

```yaml
¿Qué controla?
  - Qué ve el usuario en UI (menús, secciones)
  - Jerarquía de navegación
  - Acceso hereda de padre a hijos

¿Cómo se asigna?
  - UserModuleAccess
  - Admin → Usuarios → Módulos → Asignar

¿Da permisos?
  - NO ❌
  - Solo visibilidad
```

#### Function = PERMISOS

```yaml
¿Qué controla?
  - Qué puede HACER el usuario (ver, crear, editar, eliminar)
  - Permisos granulares por acción
  - API endpoints permissions

¿Cómo se asigna?
  - UserFunctionAssignment
  - Admin → Usuarios → Funciones → Asignar MANUALMENTE
  - NO automático desde módulo

¿Requiere Module?
  - NO para permisos API
  - SÍ para ver opción en UI
```

#### Workflow Completo

```
1. Admin asigna Module "MOD_Reports" a Usuario:
   → Usuario VE menú "Reportes" en UI
   → Pero NO puede hacer nada aún

2. Admin asigna Functions a Usuario:
   - reports.view → Puede VER reportes
   - reports.export → Puede EXPORTAR reportes
   → Ahora usuario puede usar funciones

3. Usuario usa sistema:
   - Frontend: if (hasModuleAccess('MOD_Reports')) { showMenu() }
   - API: RequiresFunctionPermission verifica reports.view
   - Ambos necesarios para UX completa
```

## 📋 Modelos

### Module

Jerarquía:
- MOD_Dashboard (root)
  - MOD_Dashboard_Analytics (child)

### Function

Granular:
- reports.view
- reports.create
- reports.export

### UserModuleAccess

Asignación:
- user + module + granted_by + reason

### UserFunctionAssignment

Asignación:
- user + function + assigned_by + reason
- MANUAL, NO automático
```

#### C.2: INTEGRATION_GUIDE_ACCESS.md (1h)

```markdown
# INTEGRATION GUIDE - apps/access/

## Caso de Uso: Nuevo Módulo con Permisos

### Escenario

Crear módulo "Facturación" con permisos CRUD.

### Pasos

#### 1. Crear Module

```python
from apps.access.models import Module

module = Module.objects.create(
    code='MOD_Billing',
    name='Facturación',
    description='Gestión de facturas',
    url_path='/billing',
    icon='invoice',
)
```

#### 2. Crear Functions

```python
from apps.access.models import Function

functions = [
    {
        'code': 'billing.view',
        'name': 'Ver Facturas',
        'module': module,  # FK o 'MOD_Billing' si CharField
    },
    {
        'code': 'billing.create',
        'name': 'Crear Factura',
        'module': module,
    },
    {
        'code': 'billing.edit',
        'name': 'Editar Factura',
        'module': module,
    },
    {
        'code': 'billing.delete',
        'name': 'Eliminar Factura',
        'module': module,
    },
]

for func_data in functions:
    Function.objects.create(**func_data)
```

#### 3. Asignar Module a Usuario

```python
from apps.access.models import UserModuleAccess

UserModuleAccess.objects.create(
    user=usuario,
    module=module,
    granted_by=admin,
    reason='Usuario necesita ver módulo Facturación',
)

# Ahora usuario VE "Facturación" en menú
```

#### 4. Asignar Functions a Usuario

```python
from apps.access.models import UserFunctionAssignment, Function

# Asignar solo view y create
functions_to_assign = Function.objects.filter(
    code__in=['billing.view', 'billing.create']
)

for function in functions_to_assign:
    UserFunctionAssignment.objects.create(
        user=usuario,
        function=function,
        assigned_by=admin,
        reason='Usuario puede ver y crear facturas',
    )

# Ahora usuario PUEDE ver y crear facturas
# NO puede editar ni eliminar (no asignadas)
```

#### 5. Implementar ViewSet

```python
from apps.core.permissions import RequiresFunctionPermission

class BillingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    function_map = {
        'list': 'billing.view',
        'retrieve': 'billing.view',
        'create': 'billing.create',
        'update': 'billing.edit',
        'partial_update': 'billing.edit',
        'destroy': 'billing.delete',
    }
```

### Resultado

```yaml
Usuario con Module + Functions:
  GET /api/billing/ → 200 OK (tiene billing.view)
  POST /api/billing/ → 200 OK (tiene billing.create)
  PUT /api/billing/1/ → 403 Forbidden (NO tiene billing.edit)
  DELETE /api/billing/1/ → 403 Forbidden (NO tiene billing.delete)

UI:
  - Ve menú "Facturación" (UserModuleAccess)
  - Ve botón "Crear" (tiene billing.create)
  - NO ve botón "Editar" (NO tiene billing.edit)
```
```

---

### FASE D: Audit 4 Apps (Opcional, 3-4h)

**Objetivo:** Verificar arquitectura mencionada vs código real.

#### D.1: apps/users/ Audit (1h)

```yaml
Revisar:
  ☐ User.has_function() existe? (✅ confirmado)
  ☐ SessionHistory en users o authentication?
  ☐ UserProfile, UserSettings presentes?
  ☐ Endpoints: 9 (CRUD, profile, settings)?

Resultado esperado:
  - Documento: AUDIT_USERS.md
  - Inconsistencias identificadas
  - Plan corrección si necesario
```

#### D.2: apps/authentication/ Audit (1h)

```yaml
Revisar:
  ☐ LoginAttempt, SecurityQuestion, UserSecurityAnswer?
  ☐ SessionLog vs SessionHistory?
  ☐ 5 preguntas seguridad predefinidas?
  ☐ Endpoints: 9 (login, logout, etc)?
  ☐ Email disabled (CNST-001)?

Resultado esperado:
  - Documento: AUDIT_AUTHENTICATION.md
  - Verificar si SessionHistory está aquí o en users
```

#### D.3: apps/access/ Audit (1h)

```yaml
Revisar:
  ☐ Group model existe? (mencionado pero no visto)
  ☐ GroupFunction existe?
  ☐ PermissionLog existe?
  ☐ Endpoints: 10?
  ☐ PermissionService vs RBACService?

Resultado esperado:
  - Documento: AUDIT_ACCESS.md
  - Si faltan models, ¿crear o eliminar de docs?
```

#### D.4: apps/alerts/ Audit (30 min)

```yaml
Revisar:
  ☐ 5 modelos presentes?
  ☐ Endpoints: 14?
  ☐ Rate limiting implementado?
  ☐ Auto-archivado 90 días?
  ☐ Email disabled (CNST-001)?

Resultado esperado:
  - Documento: AUDIT_ALERTS.md
```

---

## 📅 CRONOGRAMA Y ESTIMACIONES

### Resumen

```yaml
Total estimado: 10-13h

FASE A: UserServiceAccess (3-4h) - CRÍTICO:
  A.1: Análisis impacto (30 min)
  A.2: Crear functions (30 min)
  A.3: Actualizar ViewSets (1h)
  A.4: Eliminar código (30 min)
  A.5: Migración DB (30 min)
  A.6: Testing (1h)

FASE B: Module-Function FK (2-3h) - OPCIONAL:
  B.1: Análisis (30 min)
  B.2: Migración (1h)
  B.3: Actualizar código (30 min)
  B.4: Testing (1h)

FASE C: Documentación (2h) - IMPORTANTE:
  C.1: apps/access/README.md (1h)
  C.2: INTEGRATION_GUIDE_ACCESS.md (1h)

FASE D: Audit 4 Apps (3-4h) - OPCIONAL:
  D.1: apps/users/ (1h)
  D.2: apps/authentication/ (1h)
  D.3: apps/access/ (1h)
  D.4: apps/alerts/ (30 min)
```

### Prioridades

```yaml
CRÍTICO (Hacer ya):
  ✅ FASE A: UserServiceAccess (3-4h)
     Razón: Inconsistencia arquitectural, SRP violado

IMPORTANTE (Hacer pronto):
  ✅ FASE C: Documentación (2h)
     Razón: Confusión actual, onboarding difícil

OPCIONAL (Nice to have):
  ⚠️ FASE B: Module-Function FK (2-3h)
     Razón: Mejora calidad, no urgente
  
  ⚠️ FASE D: Audit 4 Apps (3-4h)
     Razón: Verificar arquitectura, claridad
```

### Cronograma Recomendado

```yaml
Semana 1:
  Día 1-2: FASE A (UserServiceAccess) - 3-4h
  Día 3: FASE C (Documentación) - 2h

Semana 2 (Opcional):
  Día 1: FASE D (Audit) - 3-4h
  Día 2: FASE B (FK Migration) - 2-3h
```

---

## ✅ CRITERIOS DE ACEPTACIÓN

### FASE A: UserServiceAccess

```yaml
✅ UserServiceAccess eliminado de models
✅ HasServiceAccess eliminado de permissions
✅ Functions pipeline.* creadas
✅ ViewSets actualizados a RequiresFunctionPermission
✅ Data migrada (si aplicable)
✅ Migración DB aplicada
✅ Tests pasando
✅ SRP apps/access/ mejorado a 9/10
✅ Documentación actualizada
```

### FASE B: Module-Function FK

```yaml
✅ Function.module es ForeignKey
✅ Migración data completa
✅ No funciones huérfanas
✅ Tests actualizados
✅ Queries optimizados (JOINs)
```

### FASE C: Documentación

```yaml
✅ apps/access/README.md completo
✅ INTEGRATION_GUIDE_ACCESS.md creado
✅ Sección Module vs Function clara
✅ Ejemplos funcionales
✅ Workflow documentado
✅ DO/DON'T patterns
```

### FASE D: Audit 4 Apps

```yaml
✅ AUDIT_USERS.md creado
✅ AUDIT_AUTHENTICATION.md creado
✅ AUDIT_ACCESS.md creado
✅ AUDIT_ALERTS.md creado
✅ Inconsistencias identificadas
✅ Plan de corrección (si necesario)
```

---

## 📊 IMPACTO ESPERADO

### Antes Remediación

```yaml
Problemas:
  ❌ UserServiceAccess mezcla conceptos
  ❌ HasServiceAccess vs RequiresFunctionPermission
  ❌ SRP violado (7/10)
  ❌ Confusión Module vs Function
  ❌ Module-Function relación débil (CharField)
  ❌ Arquitectura docs vs código unclear

Impacto:
  - Confusión arquitectural
  - Código duplicado
  - Onboarding difícil
  - Inconsistencias posibles
```

### Después Remediación

```yaml
Mejoras:
  ✅ Solo RBAC puro (RequiresFunctionPermission)
  ✅ SRP mejorado (9/10)
  ✅ Module vs Function documentado
  ✅ FK Module-Function (opcional)
  ✅ Arquitectura clara
  ✅ Onboarding fácil

Beneficios:
  ✅ Consistencia arquitectural
  ✅ Sin código duplicado
  ✅ Mantenibilidad mejorada
  ✅ Menos errores
  ✅ Escalabilidad garantizada
```

---

## 🔗 RELACIONADO

### Deuda Técnica

```yaml
Este plan resuelve:
  - DT-002: Eliminar UserServiceAccess (FASE A)
  - DT-004: Navigation Location (parte de Audit)

Crea nueva deuda:
  - DT-006: Module-Function FK (FASE B) - Opcional
  - DT-007: Audit 4 Apps (FASE D) - Opcional
```

### Documentos

```yaml
Pre-requisitos:
  - ANALISIS_RELACIONES_Y_SRP_v1.1.0.md
  - DEUDA_TECNICA.md
  - apps/core/README.md
  - INTEGRATION_GUIDE_CORE.md

Genera:
  - apps/access/README.md
  - INTEGRATION_GUIDE_ACCESS.md
  - AUDIT_*.md (4 docs)
```

---

## 📝 NOTAS

### Decisiones Clave

```yaml
1. UserServiceAccess → ELIMINAR
   - RBAC puro con Functions
   - No control por servicio 800 específico
   - Functions genéricas (pipeline.view_services)

2. Module-Function FK → OPCIONAL
   - Mejora calidad pero no urgente
   - Sistema funciona con CharField
   - Hacer si tiempo disponible

3. Module ≠ Function
   - Sistemas SEPARADOS
   - Module = VISIBILIDAD
   - Function = PERMISOS
   - Asignación MANUAL
```

### Riesgos

```yaml
FASE A (UserServiceAccess):
  Riesgo: Perder data de servicios 800
  Mitigación: Script de migración a Functions
  
FASE B (FK Migration):
  Riesgo: Functions huérfanas
  Mitigación: Análisis pre-migración, cleanup

FASE D (Audit):
  Riesgo: Descubrir features faltantes
  Mitigación: Plan de implementación post-audit
```

---

**Versión:** 3.0.0  
**Estado:** Planificación  
**Próximo paso:** Ejecutar FASE A (UserServiceAccess)  
**Aprobación:** Pendiente  
**Última actualización:** 2026-01-21
