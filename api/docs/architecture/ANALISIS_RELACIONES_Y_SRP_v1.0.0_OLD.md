# ANÁLISIS DE RELACIONES Y SRP - Sistema IACT

**Documento:** Análisis de arquitectura para FASE 3  
**Fecha:** 2026-01-21  
**Versión:** 1.0.0  

---

## 📋 ÍNDICE

1. [Inventario de Apps](#inventario-de-apps)
2. [Análisis SRP por App](#análisis-srp-por-app)
3. [Mapa de Dependencias](#mapa-de-dependencias)
4. [apps/core - Análisis Detallado](#appscore---análisis-detallado)
5. [apps/utils - Análisis Detallado](#appsutils---análisis-detallado)
6. [Problemas Detectados](#problemas-detectados)
7. [Recomendaciones FASE 3](#recomendaciones-fase-3)

---

## 1. INVENTARIO DE APPS

### Apps de Negocio (Business Logic)

```yaml
apps/users/ (✅ FASE 2 COMPLETADA):
  Responsabilidad: Gestión de usuarios
  Estado: Producción ready
  Líneas: ~5,000
  Tests: 94+ (~95% coverage)
  
apps/access/:
  Responsabilidad: RBAC (Roles, Permissions, Functions, Modules)
  Estado: Parcial (FASE 1)
  Modelos: Function, Module, UserFunctionAssignment, UserServiceAccess
  
apps/authentication/:
  Responsabilidad: Login, logout, password reset, MFA
  Estado: Parcial (FASE 1)
  Modelos: SecurityQuestion, UserSecurityAnswer
  
apps/pipeline/:
  Responsabilidad: ETL de datos IVR
  Estado: FASE 1
  Modelos: Center, Service, CallRecord, ETLJob
  
apps/reports/:
  Responsabilidad: Generación de reportes
  Estado: FASE 1
  Modelos: Report, Schedule, Export
  
apps/alerts/:
  Responsabilidad: Sistema de alertas
  Estado: FASE 1
  Modelos: Alert, Notification
  
apps/audit/:
  Responsabilidad: Auditoría de acciones
  Estado: FASE 1
  Modelos: AuditLog
  
apps/ivr/:
  Responsabilidad: Integración con IVR legacy
  Estado: FASE 1
  Modelos: Legacy tables (readonly)
```

### Apps de Infraestructura (Foundation)

```yaml
apps/core/:
  Responsabilidad: Componentes compartidos
  Tipo: Fundacional
  Contenido:
    - Abstract models (TimeStampedModel, SoftDeleteMixin)
    - Permissions (RequiresFunctionPermission, etc)
    - Mixins (varios)
    - Middleware (healthcheck, logging, security)
    - Services base
    - Navigation
  
apps/utils/:
  Responsabilidad: Utilidades puras (sin DB)
  Tipo: Fundacional
  Contenido:
    - Validators
    - Formatters
    - Date utils
    - String utils
    - Number utils
    - File utils
    - Helpers
    - Decorators
```

---

## 2. ANÁLISIS SRP POR APP

### ✅ apps/users/ - Single Responsibility: User Management

```yaml
Responsabilidad Única: Gestión de usuarios del sistema

INCLUYE (✅ Correcto):
  - User CRUD
  - Profile management
  - Settings personales
  - Avatar upload
  - Password change
  - Session history (auditoría de sesiones)
  - Leer permissions RBAC

NO INCLUYE (✅ Correcto):
  - Gestión de RBAC (apps/access)
  - Login/Logout (apps/authentication)
  - Password reset (apps/authentication)

SRP Score: 10/10 ✅
```

### ⚠️ apps/access/ - Responsabilidad Difusa

```yaml
Responsabilidad Esperada: RBAC Management

INCLUYE (parcialmente):
  - Function, Module (RBAC)
  - UserFunctionAssignment (RBAC)
  - UserServiceAccess (¿Service access o RBAC?)
  
PROBLEMA:
  ❌ Mezcla RBAC con service access
  ❌ UserServiceAccess es un concepto diferente a RBAC
  
DEBERÍA SER:
  ✅ SOLO RBAC (Functions, Modules, Roles, Assignments)
  ❌ Service access FUERA (¿apps/pipeline? ¿apps/core?)

SRP Score: 6/10 ⚠️
Recomendación: Separar service access de RBAC
```

### ✅ apps/authentication/ - Single Responsibility: Authentication

```yaml
Responsabilidad Única: Autenticación y seguridad

INCLUYE (✅ Correcto):
  - Login/Logout
  - Password reset
  - MFA (SecurityQuestion)
  - Token management
  
NO INCLUYE (✅ Correcto):
  - User CRUD (apps/users)
  - Password change (apps/users - usuario autenticado)
  - RBAC (apps/access)

SRP Score: 9/10 ✅
```

### apps/pipeline/ - Single Responsibility: ETL & Data Pipeline

```yaml
Responsabilidad Única: Pipeline de datos IVR

INCLUYE:
  - ETL jobs
  - Center, Service, CallRecord
  - Data transformation
  - IVR integration
  
PROBLEMA POTENCIAL:
  ⚠️ Service (modelo de negocio) vs service access (RBAC)
  ⚠️ ¿Mezcla datos con access control?

SRP Score: 7/10 ⚠️
Recomendación: Revisar si Service access está bien ubicado
```

### apps/reports/ - Single Responsibility: Reporting

```yaml
Responsabilidad Única: Generación de reportes

INCLUYE:
  - Report generation
  - Scheduling
  - Export (Excel, PDF)
  - Templates

SRP Score: 8/10 ✅
```

### apps/alerts/ - Single Responsibility: Alerting

```yaml
Responsabilidad Única: Sistema de alertas

INCLUYE:
  - Alert definitions
  - Notifications
  - Triggers
  - Email/SMS sending

SRP Score: 8/10 ✅
```

### apps/audit/ - Single Responsibility: Auditing

```yaml
Responsabilidad Única: Auditoría de acciones

INCLUYE:
  - Audit logs
  - User actions tracking
  - Change history

SRP Score: 9/10 ✅
```

---

## 3. MAPA DE DEPENDENCIAS

### Nivel 1: Fundación (No dependen de nadie)

```yaml
apps/utils/:
  Depende de: NADA
  Dependientes: TODOS
  Tipo: Utilidades puras
  Estado: ✅ Bien diseñado
  
  Contenido:
    - validators.py (phone, email, etc)
    - formatters.py
    - date_utils.py
    - string_utils.py
    - helpers.py
    - decorators.py
```

### Nivel 2: Core Infrastructure

```yaml
apps/core/:
  Depende de: apps/utils
  Dependientes: TODOS
  Tipo: Infraestructura compartida
  Estado: ⚠️ Necesita refactor
  
  Contenido:
    - Abstract models (TimeStampedModel, SoftDeleteMixin)
    - Permissions DRF
    - Mixins
    - Middleware
    - Base services (?)
    
  PROBLEMA:
    ❌ Tiene services específicos (callrecord_service, center_service)
    ❌ Mezcla infraestructura con lógica de negocio
```

### Nivel 3: Autenticación & Acceso

```yaml
apps/authentication/:
  Depende de: core, utils, users
  Dependientes: Todos los endpoints protegidos
  Tipo: Seguridad
  
apps/access/:
  Depende de: core, utils, users, pipeline (?)
  Dependientes: Todos con RBAC
  Tipo: RBAC
  
  PROBLEMA:
    ⚠️ Dependencia circular potencial con pipeline
    ⚠️ UserServiceAccess mezclado con RBAC
```

### Nivel 4: Business Logic

```yaml
apps/users/:
  Depende de: core, utils, access (read-only)
  Dependientes: access, authentication, reports, audit
  Tipo: Negocio
  Estado: ✅ FASE 2 completa
  
apps/pipeline/:
  Depende de: core, utils, ivr, access (?)
  Dependientes: reports, alerts
  Tipo: Negocio
  
apps/reports/:
  Depende de: core, utils, users, pipeline
  Dependientes: alerts (?)
  Tipo: Negocio
  
apps/alerts/:
  Depende de: core, utils, users, pipeline, reports
  Dependientes: NADIE
  Tipo: Negocio
  
apps/audit/:
  Depende de: core, utils, users
  Dependientes: NADIE
  Tipo: Negocio
```

### Nivel 5: Legacy Integration

```yaml
apps/ivr/:
  Depende de: core, utils
  Dependientes: pipeline
  Tipo: Legacy readonly
```

---

## 4. apps/core - ANÁLISIS DETALLADO

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
  - ¿Qué mixins tiene?
  - ¿Son genéricos o específicos?
  
Middleware (✅ Correcto):
  - healthcheck.py
  - logging.py
  - security.py
  - timezone.py
  
Navigation (⚠️ ¿Por qué en core?):
  - builders.py
  - urls.py
  - views.py
  - ¿Es esto infraestructura o negocio?
  
Services (❌ PROBLEMA):
  - base_service.py (✅ Correcto)
  - callrecord_service.py (❌ Debería estar en apps/pipeline)
  - center_service.py (❌ Debería estar en apps/pipeline)
  - etl_service.py (❌ Debería estar en apps/pipeline)
  - service_service.py (❌ Debería estar en apps/pipeline)
  
Validators (⚠️ Revisar):
  - ¿Qué validators tiene?
  - ¿Son genéricos?
  
Exceptions (✅ Correcto):
  - Custom exceptions base
  
Context Processors (✅ Correcto):
  - Compartidos
```

### Problemas Detectados en apps/core/

```yaml
1. Services específicos de negocio:
   ❌ callrecord_service.py → apps/pipeline/services/
   ❌ center_service.py → apps/pipeline/services/
   ❌ etl_service.py → apps/pipeline/services/
   ❌ service_service.py → apps/pipeline/services/
   
2. Navigation:
   ⚠️ ¿Es esto infraestructura compartida?
   ⚠️ ¿O debería estar en apps/reports o apps/dashboard?
   
3. Validators:
   ⚠️ ¿Son genéricos o específicos?
   ⚠️ Los genéricos deberían estar en apps/utils
```

### Lo que DEBE estar en apps/core/

```yaml
✅ Abstract models:
   - TimeStampedModel
   - SoftDeleteMixin
   
✅ Permissions DRF genéricas:
   - RequiresFunctionPermission
   - IsOwnerOrReadOnly
   - Etc.
   
✅ Middleware:
   - Healthcheck
   - Logging
   - Security
   - Timezone
   
✅ Base services:
   - BaseService
   
✅ Exceptions base:
   - BusinessRuleError
   - ValidationError
   
✅ Context processors:
   - Compartidos
   
✅ Management commands genéricos:
   - create_modules
```

### Lo que NO debe estar en apps/core/

```yaml
❌ Services específicos de negocio
❌ Models concretos
❌ Serializers específicos
❌ ViewSets específicos
❌ Validators específicos de un dominio
❌ Navigation (a menos que sea genérico)
```

---

## 5. apps/utils - ANÁLISIS DETALLADO

### Contenido Actual

```yaml
Validators (✅ Correcto):
  - validators.py
  - validate_phone_number
  - validate_email
  - Etc.
  
Date Utils (✅ Correcto):
  - date_utils.py
  - Funciones de fechas
  
String Utils (✅ Correcto):
  - string_utils.py
  - Slugify, sanitize, etc.
  
Number Utils (✅ Correcto):
  - number_utils.py
  - Format, parse
  
File Utils (✅ Correcto):
  - file_utils.py
  - Upload, validate
  
Formatters (✅ Correcto):
  - formatters.py
  - Format phone, currency, etc.
  
Helpers (⚠️ Revisar):
  - helpers.py
  - get_client_ip
  - ¿Otros?
  
Decorators (✅ Correcto):
  - decorators.py
  
Constants (✅ Correcto):
  - constants.py
```

### Principios apps/utils/

```yaml
✅ SOLO funciones puras (sin DB)
✅ SOLO utilidades reutilizables
✅ NO lógica de negocio
✅ NO models
✅ NO services
✅ NO dependencias de otras apps
```

### Estado apps/utils/

```yaml
Estado: ✅ Bien diseñado

Características:
  ✅ No depende de otras apps
  ✅ Solo funciones puras
  ✅ Reutilizable
  ✅ Testing fácil
  
Recomendación: Mantener así
```

---

## 6. PROBLEMAS DETECTADOS

### 🔴 CRÍTICO

```yaml
1. apps/core/ tiene services de negocio:
   Problema: Mezcla infraestructura con lógica de negocio
   Impacto: Alto - Viola SRP
   Solución: Mover services a apps/pipeline/services/
   
2. apps/access/ mezcla RBAC con service access:
   Problema: UserServiceAccess no es RBAC
   Impacto: Medio - Confusión conceptual
   Solución: Separar o mover a apps/pipeline
```

### ⚠️ ADVERTENCIA

```yaml
3. Navigation en apps/core/:
   Problema: ¿Es infraestructura o negocio?
   Impacto: Bajo - Ubicación cuestionable
   Solución: Evaluar si mover a app específica
   
4. Dependencias circulares potenciales:
   Problema: apps/access ↔ apps/pipeline
   Impacto: Medio - Dificulta testing
   Solución: Revisar y eliminar
```

### ℹ️ MEJORA

```yaml
5. Validators duplicados:
   Problema: ¿Validators en core Y utils?
   Impacto: Bajo - Posible duplicación
   Solución: Consolidar en apps/utils
   
6. Testing de apps/core y apps/utils:
   Problema: Coverage desconocido
   Impacto: Medio - No sabemos calidad
   Solución: Crear tests (FASE 3)
```

---

## 7. RECOMENDACIONES FASE 3

### Objetivos FASE 3

```yaml
1. Refactorizar apps/core/:
   - Mover services específicos a apps apropiadas
   - Limpiar responsabilidades
   - Mejorar SRP
   
2. Crear tests para apps/core/:
   - Unit tests para permissions
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
   - API documentation
   
5. Documentar apps/utils/:
   - README.md
   - Guía de uso
   
6. Resolver dependencias:
   - Eliminar circulares
   - Clarificar flujos
   - Diagrama de dependencias
```

### Prioridades FASE 3

```yaml
Alta Prioridad:
  1. Tests apps/core/ (crítico para estabilidad)
  2. Tests apps/utils/ (crítico para estabilidad)
  3. Mover services de core a pipeline
  4. Documentación apps/core/
  
Media Prioridad:
  5. Refactor apps/access/ (separar service access)
  6. Documentación apps/utils/
  7. Resolver dependencias circulares
  
Baja Prioridad:
  8. Evaluar navigation location
  9. Consolidar validators
```

### Estimación FASE 3

```yaml
PARTE 1: Análisis + Refactor apps/core/ (3h)
  - Mover services
  - Limpiar responsabilidades
  - Actualizar imports
  
PARTE 2: Tests apps/core/ (4h)
  - Permissions tests (15+)
  - Abstract models tests (10+)
  - Middleware tests (10+)
  - Coverage 90%+
  
PARTE 3: Tests apps/utils/ (3h)
  - Validators tests (20+)
  - Helpers tests (15+)
  - Utils tests (15+)
  - Coverage 95%+
  
PARTE 4: Documentación (2h)
  - README.md apps/core/
  - README.md apps/utils/
  - INTEGRATION_GUIDE_CORE.md
  
Total estimado: 12h
```

---

## 8. DIAGRAMA DE DEPENDENCIAS

```
┌─────────────────────────────────────────────────────────────┐
│                      Nivel 1: Fundación                      │
│                                                              │
│  ┌──────────────┐                                           │
│  │ apps/utils/  │  (validators, formatters, helpers)        │
│  └──────────────┘                                           │
└──────────────────────────────────┬───────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────┐
│                 Nivel 2: Core Infrastructure                 │
│                                                              │
│  ┌──────────────┐                                           │
│  │ apps/core/   │  (abstract models, permissions, middleware)│
│  └──────────────┘                                           │
└──────────────────┬───────────────────────┬───────────────────┘
                   │                       │
        ┌──────────▼──────────┐   ┌───────▼────────┐
        │ apps/authentication │   │  apps/access   │
        └──────────┬──────────┘   └───────┬────────┘
                   │                       │
┌──────────────────▼───────────────────────▼───────────────────┐
│                  Nivel 4: Business Logic                     │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌────────┐       │
│  │ users/  │  │ pipeline/│  │ reports/│  │ alerts/│       │
│  └─────────┘  └──────────┘  └─────────┘  └────────┘       │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. CONCLUSIONES

### Estado Actual

```yaml
✅ Bueno:
  - apps/users/ bien diseñado (FASE 2)
  - apps/utils/ cumple SRP
  - Permissions bien organizadas
  
⚠️ Mejorable:
  - apps/core/ tiene services de negocio
  - apps/access/ mezcla conceptos
  - Testing insuficiente en core/utils
  
❌ Problemas:
  - SRP violado en apps/core/
  - Dependencias circulares potenciales
  - Falta documentación
```

### Valor de FASE 3

```yaml
Beneficios:
  ✅ Estabilidad de infraestructura
  ✅ Tests de fundación (90%+ coverage)
  ✅ SRP mejorado
  ✅ Documentación completa
  ✅ Mantenibilidad mejorada
  
Riesgos si NO se hace:
  ❌ Infraestructura frágil
  ❌ Bugs en componentes base
  ❌ Dificultad para mantener
  ❌ Confusión en arquitectura
```

### Recomendación

```yaml
Proceder con FASE 3:
  Prioridad: ALTA
  Complejidad: Media
  Tiempo: 12h estimado
  ROI: Alto (fundación del sistema)
```

---

**Última actualización:** 2026-01-21  
**Autor:** IACT Development Team  
**Próximo paso:** Crear PLAN_FASE_3_v1.0.0.md
