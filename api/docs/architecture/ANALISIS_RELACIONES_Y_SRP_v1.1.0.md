# ANÁLISIS DE RELACIONES Y SRP - Sistema IACT

**Documento:** Análisis de arquitectura para FASE 3  
**Versión:** 1.1.0  
**Fecha:** 2026-01-21  
**Cambios:** Análisis más profundo de dependencias directas e indirectas  

---

## 📋 CAMBIOS EN v1.1.0

```yaml
v1.0.0 → v1.1.0:
  ✅ Corregido: Niveles de dependencia más precisos
  ✅ Agregado: Análisis de dependencias directas vs indirectas
  ✅ Mejorado: Explicación de por qué apps están en niveles específicos
  ✅ Agregado: Análisis de flujo de datos
  ✅ Corregido: apps/authentication NO está al mismo nivel que apps/access
```

---

## 📋 ÍNDICE

1. [Inventario de Apps](#inventario-de-apps)
2. [Tipos de Dependencias](#tipos-de-dependencias)
3. [Análisis de Dependencias Detallado](#análisis-de-dependencias-detallado)
4. [Mapa de Dependencias Corregido](#mapa-de-dependencias-corregido)
5. [Análisis SRP por App](#análisis-srp-por-app)
6. [apps/core - Análisis Detallado](#appscore---análisis-detallado)
7. [apps/utils - Análisis Detallado](#appsutils---análisis-detallado)
8. [Problemas Detectados](#problemas-detectados)
9. [Recomendaciones FASE 3](#recomendaciones-fase-3)

---

## 1. INVENTARIO DE APPS

### Apps de Negocio (Business Logic)

```yaml
apps/users/ (✅ FASE 2 COMPLETADA):
  Responsabilidad: Gestión de usuarios
  Estado: Producción ready
  Líneas: ~5,000
  Tests: 94+ (~95% coverage)
  Dependencias directas: core, utils
  Dependencias indirectas: access (vía has_function)
  
apps/access/:
  Responsabilidad: RBAC (Roles, Permissions, Functions, Modules)
  Estado: Parcial (FASE 1)
  Modelos: Function, Module, UserFunctionAssignment, UserServiceAccess
  Dependencias directas: core
  Dependencias indirectas: users (User model vía ForeignKey)
  
apps/authentication/:
  Responsabilidad: Login, logout, password reset, MFA
  Estado: Parcial (FASE 1)
  Modelos: SecurityQuestion, UserSecurityAnswer, SessionLog
  Dependencias directas: core
  Dependencias indirectas: users, access (vía RBAC permissions)
  
apps/pipeline/:
  Responsabilidad: ETL de datos IVR
  Estado: FASE 1
  Modelos: Center, Service, CallRecord, ETLJob
  Dependencias directas: core, utils, ivr, access (UserServiceAccess)
  
apps/reports/:
  Responsabilidad: Generación de reportes
  Estado: FASE 1
  Modelos: Report, Schedule, Export
  Dependencias directas: core, utils, users, pipeline
  
apps/alerts/:
  Responsabilidad: Sistema de alertas
  Estado: FASE 1
  Modelos: Alert, Notification
  Dependencias directas: core, utils, users, pipeline, reports
  
apps/audit/:
  Responsabilidad: Auditoría de acciones
  Estado: FASE 1
  Modelos: AuditLog
  Dependencias directas: core, utils, users
  
apps/ivr/:
  Responsabilidad: Integración con IVR legacy
  Estado: FASE 1
  Modelos: Legacy tables (readonly)
  Dependencias directas: core, utils
```

### Apps de Infraestructura (Foundation)

```yaml
apps/core/:
  Responsabilidad: Componentes compartidos
  Tipo: Fundacional
  Dependencias directas: utils
  Contenido:
    - Abstract models (TimeStampedModel, SoftDeleteMixin)
    - Permissions DRF (RequiresFunctionPermission, etc)
    - Mixins
    - Middleware
    - Base services
    - Navigation
  
apps/utils/:
  Responsabilidad: Utilidades puras (sin DB)
  Tipo: Fundacional
  Dependencias directas: NINGUNA
  Contenido:
    - Validators
    - Formatters
    - Date/String/Number utils
    - Helpers
    - Decorators
```

---

## 2. TIPOS DE DEPENDENCIAS

### Dependencia Directa

```yaml
Definición: Import explícito en el código
Ejemplo: from apps.core.models import TimeStampedModel
Impacto: Alto - Rompe si falta el módulo
```

### Dependencia Indirecta

```yaml
Definición: Uso vía referencia, signal, o método
Ejemplo: 
  - user.has_function() llama a apps.access (import lazy)
  - ForeignKey a User (usa settings.AUTH_USER_MODEL)
  - Permission que verifica RBAC (usa access vía users)
Impacto: Medio - Más flexible pero menos visible
```

### Dependencia Circular

```yaml
Definición: A depende de B, B depende de A
Ejemplo: apps.users ↔ apps.access (potencial)
Impacto: Crítico - Dificulta testing y puede causar errores
```

---

## 3. ANÁLISIS DE DEPENDENCIAS DETALLADO

### apps/utils/ - Nivel 1: Fundación Pura

```yaml
Depende de: NADA
Dependientes: TODOS

Característica: Funciones puras sin dependencias
Estado: ✅ Perfecto
```

### apps/core/ - Nivel 2: Infraestructura Base

```yaml
Depende de:
  ✅ apps/utils (directa - validators, helpers)

Dependientes: TODOS

Característica: Infraestructura compartida
Estado: ⚠️ Tiene services de negocio (PROBLEMA)
```

### apps/users/ - Nivel 3: User Model Base

```yaml
Depende de:
  ✅ apps/core (directa - TimeStampedModel, SoftDeleteMixin)
  ✅ apps/utils (directa - validate_phone_number)
  ⚠️ apps/access (indirecta - vía has_function con import lazy)

Dependientes: access, authentication, pipeline, reports, alerts, audit

Característica: Define User model que otros usan
Estado: ✅ Bien diseñado (FASE 2)

IMPORTANTE: User.has_function() tiene import lazy:
  def has_function(self, function_id):
      from apps.access.models import UserFunctionAssignment  # ← Import lazy
      return UserFunctionAssignment.objects.filter(...)
```

### apps/access/ - Nivel 4: RBAC Management

```yaml
Depende de:
  ✅ apps/core (directa - SoftDeleteMixin)
  ⚠️ apps/users (indirecta - User vía ForeignKey con settings.AUTH_USER_MODEL)

Dependientes: authentication (vía RBAC), pipeline (UserServiceAccess), users (vía has_function)

Característica: Gestiona RBAC
Estado: ⚠️ Mezcla RBAC con service access

POR QUÉ NIVEL 4:
  - apps/users define User model (nivel 3)
  - apps/access usa User vía ForeignKey (nivel 4)
  - UserFunctionAssignment.user = FK(User)
```

### apps/authentication/ - Nivel 5: Authentication Layer

```yaml
Depende de:
  ✅ apps/core (directa - RequiresFunctionPermission, AuditMixin)
  ⚠️ apps/users (indirecta - User vía get_user_model)
  ⚠️ apps/access (indirecta - vía RequiresFunctionPermission)

Dependientes: NINGUNO (capa superior)

Característica: Login, logout, MFA
Estado: ✅ Bien separado

POR QUÉ NIVEL 5 (NO nivel 4):
  - USA RequiresFunctionPermission con function_map
  - function_map = {'change_password': 'authentication.change_password'}
  - RequiresFunctionPermission → user.has_function() → apps.access
  - Por lo tanto: authentication → access (indirecta)

FLUJO:
  1. POST /auth/change-password/
  2. RequiresFunctionPermission verifica
  3. user.has_function('authentication.change_password')
  4. Consulta UserFunctionAssignment (apps/access)
```

### apps/pipeline/ - Nivel 5: Data Pipeline

```yaml
Depende de:
  ✅ apps/core (directa - services, mixins)
  ✅ apps/utils (directa - validators, formatters)
  ✅ apps/ivr (directa - legacy data)
  ✅ apps/access (directa - UserServiceAccess)

Dependientes: reports, alerts

Característica: ETL, CallRecords
Estado: ⚠️ Tiene services en apps/core (PROBLEMA)

POR QUÉ NIVEL 5:
  - USA apps/access.UserServiceAccess (nivel 4)
  - Import directo: from apps.access.models import UserServiceAccess
```

### apps/reports/ - Nivel 6: Reporting

```yaml
Depende de:
  ✅ apps/core, apps/utils
  ✅ apps/users (ForeignKey a User)
  ✅ apps/pipeline (datos para reportes)

Dependientes: alerts

POR QUÉ NIVEL 6:
  - USA apps/pipeline (nivel 5)
```

### apps/alerts/ - Nivel 7: Alerting

```yaml
Depende de:
  ✅ apps/core, apps/utils
  ✅ apps/users
  ✅ apps/pipeline
  ✅ apps/reports

Dependientes: NINGUNO

POR QUÉ NIVEL 7:
  - USA apps/reports (nivel 6)
  - Capa más alta de negocio
```

### apps/audit/ - Nivel 5: Auditing (paralelo)

```yaml
Depende de:
  ✅ apps/core, apps/utils
  ✅ apps/users

Dependientes: NINGUNO

POR QUÉ NIVEL 5:
  - NO depende de access, authentication, pipeline
  - Solo usa users
  - Paralelo e independiente
```

---

## 4. MAPA DE DEPENDENCIAS CORREGIDO

### Versión v1.1.0 - CORREGIDA

```
┌─────────────────────────────────────────────────────────────┐
│                  Nivel 1: Fundación Pura                     │
│                                                              │
│  ┌──────────────┐                                           │
│  │ apps/utils/  │  (validators, formatters, helpers)        │
│  └──────────────┘  NO depende de nadie                      │
└──────────────────────────────────┬───────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────┐
│             Nivel 2: Core Infrastructure                     │
│                                                              │
│  ┌──────────────┐                                           │
│  │ apps/core/   │  (abstract models, permissions, middleware)│
│  └──────────────┘  Depende: utils                           │
└──────────────────────────────────┬───────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────┐
│                 Nivel 3: User Model Base                     │
│                                                              │
│  ┌──────────────┐                                           │
│  │ apps/users/  │  (User model + Profile + Settings)        │
│  └──────────────┘  Depende: core, utils, access (lazy)      │
└──────────────────────────────────┬───────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────┐
│                  Nivel 4: RBAC Layer                         │
│                                                              │
│  ┌──────────────┐                                           │
│  │ apps/access/ │  (RBAC: Functions, Modules, Assignments)  │
│  └──────────────┘  Depende: core, users (FK)                │
└─────────┬────────────────────────────────┬───────────────────┘
          │                                │
┌─────────▼────────────────────────────────▼───────────────────┐
│        Nivel 5: Auth + Business Logic (paralelo)             │
│                                                              │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────┐     │
│  │apps/authentication│  │apps/pipeline │  │apps/audit  │     │
│  └─────────────────┘  └──────────────┘  └────────────┘     │
│  Depende: core,       Depende: core,    Depende: core,     │
│  users, access (vía   utils, ivr,       utils, users       │
│  RBAC permissions)    access                                │
└─────────┬──────────────────────┬───────────────────────────┘
          │                      │
┌─────────▼──────────────────────▼───────────────────────────┐
│              Nivel 6: Reporting Layer                       │
│                                                             │
│  ┌──────────────┐                                          │
│  │apps/reports/ │                                          │
│  └──────────────┘  Depende: core, utils, users, pipeline  │
└─────────┬───────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────┐
│              Nivel 7: Alerting Layer                        │
│                                                             │
│  ┌─────────────┐                                           │
│  │apps/alerts/ │                                           │
│  └─────────────┘  Depende: core, utils, users, pipeline,  │
│                   reports                                  │
└─────────────────────────────────────────────────────────────┘
```

### Comparación v1.0.0 vs v1.1.0

```yaml
v1.0.0 (INCORRECTO):
  Nivel 3: apps/authentication, apps/access (mismo nivel)
  
v1.1.0 (CORRECTO):
  Nivel 3: apps/users/
  Nivel 4: apps/access/
  Nivel 5: apps/authentication/ (depende de access vía RBAC)

RAZÓN DEL CAMBIO:
  - apps/authentication USA RequiresFunctionPermission
  - RequiresFunctionPermission verifica user.has_function()
  - has_function() consulta apps/access
  - Por lo tanto: authentication → access (dependencia indirecta)
```

---

## 5. ANÁLISIS SRP POR APP

### ✅ apps/users/ - Single Responsibility: User Management

```yaml
Responsabilidad Única: Gestión de usuarios del sistema

INCLUYE (✅ Correcto):
  - User CRUD
  - Profile management
  - Settings personales
  - Avatar upload
  - Password change
  - Session history
  - Leer permissions RBAC (has_function con import lazy)

NO INCLUYE (✅ Correcto):
  - Gestión de RBAC (apps/access)
  - Login/Logout (apps/authentication)
  - Password reset (apps/authentication)

SRP Score: 10/10 ✅
```

### ⚠️ apps/access/ - Responsabilidad Difusa

```yaml
Responsabilidad Esperada: RBAC Management

INCLUYE:
  - Function, Module (RBAC) ✅
  - UserFunctionAssignment (RBAC) ✅
  - UserServiceAccess (Service access) ⚠️
  
PROBLEMA:
  ❌ Mezcla RBAC con service access
  ❌ UserServiceAccess NO es RBAC puro
  
DEBERÍA SER:
  ✅ SOLO RBAC (Functions, Modules, Assignments)
  ❌ Service access podría estar en apps/pipeline
  
PERO:
  ⚠️ UserServiceAccess es similar a UserFunctionAssignment
  ⚠️ Ambos son "permisos" (función vs servicio)
  ⚠️ Podría argumentarse que es parte de "access control"

SRP Score: 7/10 ⚠️
Recomendación: Evaluar si separar, pero no urgente
```

### ✅ apps/authentication/ - Single Responsibility: Authentication

```yaml
Responsabilidad Única: Autenticación y seguridad

INCLUYE (✅ Correcto):
  - Login/Logout
  - Password reset
  - MFA (SecurityQuestion)
  - Token management
  - Session tracking
  
USA (✅ Correcto):
  - RBAC permissions vía RequiresFunctionPermission
  - Ejemplo: change_password requiere 'authentication.change_password'
  
NO INCLUYE (✅ Correcto):
  - User CRUD (apps/users)
  - Password change (apps/users - usuario autenticado sin reset)
  - RBAC management (apps/access)

SRP Score: 9/10 ✅
```

### Otros Apps (sin cambios)

```yaml
apps/pipeline/: 7/10 ⚠️
apps/reports/: 8/10 ✅
apps/alerts/: 8/10 ✅
apps/audit/: 9/10 ✅
apps/ivr/: 9/10 ✅
```

---

## 6. apps/core - ANÁLISIS DETALLADO

*(Sin cambios respecto a v1.0.0)*

### Contenido Actual

```yaml
Abstract Models (✅ Correcto):
  - TimeStampedModel
  - SoftDeleteMixin
  - SoftDeleteManager
  
Permissions DRF (✅ Correcto):
  - RequiresFunctionPermission (RBAC)
  - IsOwnerOrReadOnly
  - IsSuperUserOrReadOnly
  - IsStaffOrReadOnly
  - HasServiceAccess
  - AllowOptionsAuthentication
  
Mixins (⚠️ Revisar):
  - AuditMixin
  - Otros mixins
  
Middleware (✅ Correcto):
  - healthcheck.py
  - logging.py
  - security.py
  - timezone.py
  
Navigation (⚠️ Cuestionable):
  - builders.py
  - urls.py
  - views.py
  
Services (❌ PROBLEMA):
  - base_service.py (✅ Correcto)
  - callrecord_service.py (❌ → apps/pipeline)
  - center_service.py (❌ → apps/pipeline)
  - etl_service.py (❌ → apps/pipeline)
  - service_service.py (❌ → apps/pipeline)
```

### Problemas (sin cambios)

```yaml
1. Services específicos de negocio:
   ❌ callrecord_service.py → apps/pipeline/services/
   ❌ center_service.py → apps/pipeline/services/
   ❌ etl_service.py → apps/pipeline/services/
   ❌ service_service.py → apps/pipeline/services/
   
2. Navigation:
   ⚠️ ¿Es infraestructura o negocio?
```

---

## 7. apps/utils - ANÁLISIS DETALLADO

*(Sin cambios respecto a v1.0.0)*

---

## 8. PROBLEMAS DETECTADOS

### 🔴 CRÍTICO

```yaml
1. apps/core/ tiene services de negocio:
   Problema: Mezcla infraestructura con lógica de negocio
   Impacto: Alto - Viola SRP
   Solución: Mover services a apps/pipeline/services/
   
2. apps/core/ y apps/utils/ sin tests:
   Problema: Coverage desconocido
   Impacto: Alto - Riesgo de regresiones
   Solución: Crear tests (FASE 3)
```

### ⚠️ ADVERTENCIA

```yaml
3. apps/access/ mezcla RBAC con service access:
   Problema: UserServiceAccess no es RBAC puro
   Impacto: Medio - Confusión conceptual
   Solución: Evaluar si separar (no urgente)
   
4. Navigation en apps/core/:
   Problema: ¿Es infraestructura o negocio?
   Impacto: Bajo - Ubicación cuestionable
   Solución: Evaluar si mover
   
5. Dependencias indirectas complejas:
   Problema: authentication → access vía RBAC no es obvio
   Impacto: Medio - Dificulta entendimiento
   Solución: Documentar bien (FASE 3)
```

### ℹ️ MEJORA

```yaml
6. Documentación de dependencias:
   Problema: No está documentado el flujo
   Impacto: Bajo - Onboarding más lento
   Solución: Crear diagramas y docs (FASE 3)
```

---

## 9. RECOMENDACIONES FASE 3

*(Actualizadas para v1.1.0)*

### Objetivos FASE 3

```yaml
1. Refactorizar apps/core/:
   - Mover services específicos a apps/pipeline/
   - Limpiar responsabilidades
   - Mejorar SRP
   
2. Crear tests para apps/core/:
   - Unit tests para permissions (incluir RequiresFunctionPermission)
   - Unit tests para abstract models
   - Unit tests para middleware
   - Coverage objetivo: 90%+
   
3. Crear tests para apps/utils/:
   - Unit tests para validators
   - Unit tests para helpers
   - Unit tests para utils
   - Coverage objetivo: 95%+
   
4. Documentar apps/core/:
   - README.md
   - INTEGRATION_GUIDE_CORE.md
   - Diagrama de dependencias
   - Flujo de RBAC permissions
   
5. Documentar apps/utils/:
   - README.md
   - Guía de uso
   
6. Documentar flujo de dependencias:
   - Dependencias directas vs indirectas
   - Por qué authentication está en nivel 5
   - Flujo de RequiresFunctionPermission
```

### Prioridades FASE 3 (actualizadas)

```yaml
Alta Prioridad:
  1. Tests apps/core/ (crítico - incluir permissions)
  2. Tests apps/utils/ (crítico)
  3. Mover services de core a pipeline
  4. Documentar flujo RBAC (authentication → access)
  
Media Prioridad:
  5. Documentación apps/core/
  6. Documentación apps/utils/
  7. Diagrama de dependencias detallado
  
Baja Prioridad:
  8. Evaluar navigation location
  9. Evaluar separar UserServiceAccess
```

---

## 10. DIAGRAMA DE FLUJO RBAC

### Nuevo en v1.1.0

```
┌─────────────────────────────────────────────────────────────┐
│         Flujo: Usuario hace request protegido               │
└─────────────────────────────────────────────────────────────┘

1. Request: POST /auth/change-password/
   ↓
2. DRF ViewSet (apps/authentication/viewsets.py)
   - permission_classes = [IsAuthenticated, RequiresFunctionPermission]
   - function_map = {'change_password': 'authentication.change_password'}
   ↓
3. RequiresFunctionPermission (apps/core/permissions.py)
   - Obtiene action = 'change_password'
   - Obtiene function_id = 'authentication.change_password'
   - Llama: user.has_function(function_id)
   ↓
4. User.has_function() (apps/users/models.py)
   - Import lazy: from apps.access.models import UserFunctionAssignment
   - Query: UserFunctionAssignment.objects.filter(user=self, function__code=function_id)
   ↓
5. UserFunctionAssignment (apps/access/models.py)
   - Verifica en DB si user tiene la función
   - Retorna True/False
   ↓
6. Response:
   - True → 200 OK (ejecuta change_password)
   - False → 403 Forbidden

DEPENDENCIAS:
  apps/authentication (ViewSet)
    ↓ usa
  apps/core (RequiresFunctionPermission)
    ↓ llama
  apps/users (User.has_function)
    ↓ consulta
  apps/access (UserFunctionAssignment)
```

---

## 11. CONCLUSIONES v1.1.0

### Correcciones Realizadas

```yaml
✅ Corregido: Mapa de dependencias
  - apps/authentication NIVEL 5 (no 3)
  - apps/access NIVEL 4 (no 3)
  - Razón: authentication usa RBAC de access

✅ Agregado: Análisis de dependencias directas vs indirectas
  - Directas: imports explícitos
  - Indirectas: vía métodos, ForeignKey, permissions

✅ Agregado: Flujo de RBAC
  - Documenta cómo RequiresFunctionPermission funciona
  - Explica cadena de dependencias

✅ Mejorado: Explicación de niveles
  - Por qué cada app está donde está
  - Qué dependencias tiene cada una
```

### Estado Actual

```yaml
✅ Bueno:
  - apps/users/ bien diseñado (FASE 2)
  - apps/utils/ cumple SRP
  - Dependencias ahora claras
  
⚠️ Mejorable:
  - apps/core/ tiene services de negocio
  - Testing insuficiente en core/utils
  - Documentación faltante
  
❌ Problemas:
  - SRP violado en apps/core/
  - Coverage desconocido
```

### Próximos Pasos

```yaml
FASE 3 (12h estimado):
  PARTE 1: Refactor apps/core/ (3h)
  PARTE 2: Tests apps/core/ (4h)
  PARTE 3: Tests apps/utils/ (3h)
  PARTE 4: Documentación (2h)

Post-FASE 3:
  - Diagramas de dependencias visuales
  - Docs de integración entre apps
  - Guía de arquitectura completa
```

---

**Última actualización:** 2026-01-21  
**Versión:** 1.1.0  
**Cambios:** Análisis más profundo de dependencias, niveles corregidos  
**Próximo paso:** Actualizar PLAN_FASE_3 a v1.1.0
