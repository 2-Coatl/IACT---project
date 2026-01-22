---
version: 1.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Relaciones Completo
categoria: arquitectura/analisis
tema: Matriz de Relaciones - Todos los ANALISIS_APP v3.0.0 vs Código Real
autor: Claude Technical Analysis
tags: [analisis, relaciones, modelos, dependencies, refactoring]
documentos_base:
  - TODOS los ANALISIS_APP_*_v3_0_0.md (12 apps)
  - Código real de apps/*/models.py
  - PLAN_IMPLEMENTACION_v2_0_0.md
estado: analisis-completo
---

# ANÁLISIS COMPLETO DE RELACIONES - CÓDIGO REAL vs ANALISIS
## MATRIZ DE MODELOS Y DEPENDENCIAS

---

## 🎯 OBJETIVO

Analizar **TODAS las relaciones** entre modelos considerando:
1. ✅ Modelos en **código REAL**
2. ✅ Modelos en **ANALISIS_APP v3.0.0**
3. ✅ Relaciones **FK / ForeignKey**
4. ✅ Dependencias **circulares**
5. ✅ Plan **refactoring TDD**

---

## 📊 RESUMEN EJECUTIVO

```yaml
Apps Totales Analizadas: 12
Apps Implementadas: 9
Apps Solo en Análisis: 3

Modelos en Código Real: 15
Modelos en Análisis: 40+
Divergencias Detectadas: 7 críticas

Relaciones FK Identificadas: 25+
Dependencias Circulares: 3
Apps con Modelos Concretos: 8
```

---

## 1. APPS EXISTENTES vs ANÁLISIS

### 1.1 Apps Implementadas (9)

```yaml
✅ apps/access/
   Código Real:
     - Function
     - UserFunctionAssignment
     - Module
     - UserModuleAccess
   
   Análisis v3.0.0:
     - Function
     - Group (❌ NO en código)
     - GroupFunction (❌ NO en código)
     - Module
     - UserGroup (❌ NO en código)
   
   Divergencia: 3 modelos faltan
   Estado: Implementación parcial

✅ apps/audit/
   Código Real:
     - AuditLog
   
   Análisis v3.0.0:
     - AuditLog
     - LoginLog (❌ NO en código)
   
   Divergencia: LoginLog falta
   Estado: Implementación parcial

✅ apps/authentication/
   Código Real:
     - SecurityQuestion
     - UserSecurityAnswer
   
   Análisis v3.0.0:
     - LoginAttempt (❌ NO en código)
     - SecurityQuestion
     - SessionLog (❌ NO en código)
     - UserSecurityAnswer
   
   Divergencia: LoginAttempt, SessionLog faltan
   Estado: Implementación parcial

✅ apps/core/
   Código Real:
     - Center (🔴 CONCRETO, debería ser abstract)
     - Service (🔴 CONCRETO, debería ser abstract)
     - CallRecord (🔴 CONCRETO, debería ser abstract)
     - UserServiceAccess (🔴 CONCRETO, debería ser abstract)
   
   Análisis v3.0.0:
     - TimeStampedModel (abstract=True)
     - SoftDeleteMixin (abstract=True)
     - AuditedModel (abstract=True)
     - (NO modelos concretos)
   
   Divergencia: 4 modelos concretos en código
   Estado: 🔴 CRÍTICO - Violación arquitectura

✅ apps/ivr_legacy/
   Código Real:
     - CallLog (readonly MariaDB)
     - (otros modelos IVR)
   
   Análisis v3.0.0:
     - QuarterlyReport
     - TransferReport
     - AbandonedReport
     - CallRecord (Q1, Q2, Q3)
   
   Estado: Readonly, correcto

✅ apps/pipeline/
   Código Real:
     - ETLExecution
   
   Análisis v3.0.0:
     - Job
     - JobExecution
     - Execution
     - JobLog
     - ScheduledJob
   
   Divergencia: Solo 1 modelo implementado
   Estado: Implementación mínima

✅ apps/reports/
   Código Real:
     - Report
     - ExportJob
   
   Análisis v3.0.0:
     - Report
     - ReportExecution (❌ NO en código)
     - ReportTemplate (❌ NO en código)
   
   Divergencia: 2 modelos faltan
   Estado: Implementación parcial

✅ apps/users/
   Código Real:
     - CustomUser
   
   Análisis v3.0.0:
     - (CustomUser mencionado pero como User de Django)
     - UserProfile (❌ NO en código)
     - UserSettings (❌ NO en código)
     - SessionHistory (❌ NO en código)
   
   Divergencia: 3 modelos faltan
   Estado: Implementación mínima

✅ apps/utils/
   Código Real:
     - SoftDeleteMixin (reutilizable)
     - SoftDeleteQuerySet
     - SoftDeleteManager
   
   Análisis v3.0.0:
     - (Solo helpers, NO modelos)
   
   Estado: ✅ Correcto
```

---

### 1.2 Apps Solo en Análisis (3)

```yaml
❌ apps/alerts/ (NO EXISTE)
   Análisis v3.0.0:
     - InternalMessage
     - AlertConfiguration
     - AlertSubscription
     - MessageRecipient
   
   Estado: Futuro, no implementada

❌ apps/calls/ (NO EXISTE)
   Análisis v3.0.0:
     - Call
     - CallStatus
     - CallType
     - CallRecording
     - CallNote
     - CallMetrics
   
   Estado: Futuro, no implementada
   Nota: CallRecord ESTÁ en apps/core/ ⚠️

❌ apps/dashboard/ (NO EXISTE)
   Análisis v3.0.0:
     - DashboardConfig
     - WidgetConfig
     - (Otros configs)
   
   Estado: Futuro, no implementada
```

---

## 2. RELACIONES ENTRE MODELOS (FK)

### 2.1 Relaciones en Código Real

```python
# =============================================================================
# MODELOS CON FK - CÓDIGO REAL
# =============================================================================

# apps/core/models.py
class Service(models.Model):
    center = ForeignKey(Center, on_delete=PROTECT)
    # Relación: Service → Center

class UserServiceAccess(models.Model):
    user = ForeignKey(User, on_delete=CASCADE)
    service = ForeignKey(Service, on_delete=CASCADE)
    granted_by = ForeignKey(User, on_delete=SET_NULL, null=True)
    revoked_by = ForeignKey(User, on_delete=SET_NULL, null=True)
    # Relaciones:
    # UserServiceAccess → User (3 veces: user, granted_by, revoked_by)
    # UserServiceAccess → Service

# apps/access/models.py
class UserFunctionAssignment(models.Model):
    user = ForeignKey(User, on_delete=CASCADE)
    function = ForeignKey(Function, on_delete=CASCADE)
    assigned_by = ForeignKey(User, on_delete=SET_NULL, null=True)
    # Relaciones:
    # UserFunctionAssignment → User (2 veces)
    # UserFunctionAssignment → Function

class UserModuleAccess(models.Model):
    user = ForeignKey(User, on_delete=CASCADE)
    module = ForeignKey(Module, on_delete=CASCADE)
    # Relaciones:
    # UserModuleAccess → User
    # UserModuleAccess → Module

class Function(models.Model):
    module = ForeignKey(Module, on_delete=PROTECT)
    # Relación: Function → Module

# apps/authentication/models.py
class UserSecurityAnswer(models.Model):
    user = ForeignKey(User, on_delete=CASCADE)
    question = ForeignKey(SecurityQuestion, on_delete=PROTECT)
    # Relaciones:
    # UserSecurityAnswer → User
    # UserSecurityAnswer → SecurityQuestion

# apps/reports/models.py
class Report(models.Model):
    created_by = ForeignKey(User, on_delete=SET_NULL, null=True)
    # Relación: Report → User

class ExportJob(models.Model):
    report = ForeignKey(Report, on_delete=CASCADE)
    requested_by = ForeignKey(User, on_delete=SET_NULL, null=True)
    # Relaciones:
    # ExportJob → Report
    # ExportJob → User

# apps/audit/models.py
class AuditLog(models.Model):
    user = ForeignKey(User, on_delete=SET_NULL, null=True)
    # Relación: AuditLog → User
```

---

### 2.2 Mapa de Dependencias

```
┌─────────────────────────────────────────────────────┐
│              MAPA DE DEPENDENCIAS FK                │
└─────────────────────────────────────────────────────┘

apps/users/
  └── CustomUser (User)
       ↑
       ├── apps/core/UserServiceAccess (user, granted_by, revoked_by)
       ├── apps/access/UserFunctionAssignment (user, assigned_by)
       ├── apps/access/UserModuleAccess (user)
       ├── apps/authentication/UserSecurityAnswer (user)
       ├── apps/reports/Report (created_by)
       ├── apps/reports/ExportJob (requested_by)
       └── apps/audit/AuditLog (user)

apps/core/
  ├── Center
  │    ↑
  │    └── Service (center)
  │         ↑
  │         └── UserServiceAccess (service)
  │
  ├── Service
  │    ↑
  │    └── UserServiceAccess (service)
  │
  └── CallRecord (sin FK)

apps/access/
  ├── Module
  │    ↑
  │    ├── Function (module)
  │    └── UserModuleAccess (module)
  │
  └── Function
       ↑
       └── UserFunctionAssignment (function)

apps/authentication/
  └── SecurityQuestion
       ↑
       └── UserSecurityAnswer (question)

apps/reports/
  └── Report
       ↑
       └── ExportJob (report)
```

---

## 3. DEPENDENCIAS CIRCULARES DETECTADAS

```yaml
🔴 CIRCULAR 1: Service.grant_access_to_user()
   apps/core/models.py Service → import UserServiceAccess
   apps/core/models.py UserServiceAccess → ForeignKey(Service)
   
   Solución Actual: Import dentro del método ✅
   
   Código:
     def grant_access_to_user(self, user, granted_by=None):
         from apps.core.models import UserServiceAccess  # ✅ Import local
         ...

🔴 CIRCULAR 2: apps/core/ modelos entre sí
   Service → ForeignKey(Center)
   UserServiceAccess → ForeignKey(Service)
   UserServiceAccess → ForeignKey(User)
   
   Solución: Todos en mismo archivo ✅
   Estado: Sin problemas

⚠️ POTENCIAL CIRCULAR 3: User en múltiples apps
   apps/users/CustomUser usado por:
     - apps/core/ (4 FK)
     - apps/access/ (3 FK)
     - apps/authentication/ (1 FK)
     - apps/reports/ (2 FK)
     - apps/audit/ (1 FK)
   
   Solución: get_user_model() ✅
   Estado: Sin problemas
```

---

## 4. DIVERGENCIAS CRÍTICAS

### 4.1 apps/core/ - VIOLACIÓN ARQUITECTURA

```yaml
🔴 PROBLEMA CRÍTICO:

Análisis v3.0.0 dice:
  ✅ apps/core/models.py SOLO abstract=True
  ✅ TimeStampedModel, SoftDeleteMixin, AuditedModel
  ❌ NINGÚN modelo concreto

Código Real tiene:
  ❌ Center (concreto, db_table='core_centers')
  ❌ Service (concreto, db_table='core_services')
  ❌ CallRecord (concreto, db_table='core_call_records')
  ❌ UserServiceAccess (concreto, db_table='core_user_service_access')

Impacto:
  - 4 modelos violan arquitectura
  - Tablas BD ya creadas (core_*)
  - Services Layer implementado
  - API REST implementada (serializers, filters, permissions)
```

---

### 4.2 Modelos Faltantes en Código

```yaml
ALTA PRIORIDAD (mencionados en análisis, no implementados):

apps/access/:
  ❌ Group (grupos de usuarios)
  ❌ GroupFunction (funciones por grupo)
  ❌ UserGroup (usuarios en grupos)

apps/authentication/:
  ❌ LoginAttempt (intentos de login)
  ❌ SessionLog (log de sesiones)

apps/audit/:
  ❌ LoginLog (log de login/logout)

apps/reports/:
  ❌ ReportExecution (ejecuciones de reportes)
  ❌ ReportTemplate (plantillas de reportes)

apps/users/:
  ❌ UserProfile (perfil extendido)
  ❌ UserSettings (configuraciones)
  ❌ SessionHistory (historial sesiones)

apps/pipeline/:
  ❌ Job (trabajos ETL)
  ❌ JobExecution (ejecuciones)
  ❌ JobLog (logs)
  ❌ ScheduledJob (trabajos programados)
```

---

## 5. APPS FUTURAS (Solo en Análisis)

```yaml
apps/calls/ (❌ NO EXISTE):
  Propósito: Gestión de llamadas del call center
  Modelos: Call, CallStatus, CallType, CallRecording, CallNote, CallMetrics
  Conflicto: CallRecord ya está en apps/core/ ⚠️
  
  Decisión Requerida:
    A) Mover CallRecord a apps/calls/ cuando se cree
    B) Mantener CallRecord en apps/core/
    C) Crear Call diferente de CallRecord

apps/alerts/ (❌ NO EXISTE):
  Propósito: Sistema de alertas y mensajería interna
  Modelos: InternalMessage, AlertConfiguration, AlertSubscription
  Estado: Futuro

apps/dashboard/ (❌ NO EXISTE):
  Propósito: Dashboards configurables
  Modelos: DashboardConfig, WidgetConfig
  Estado: Futuro
```

---

## 6. PLAN REFACTORING TDD

### 6.1 Estrategia General

```yaml
Enfoque: TDD (Test-Driven Development)
Orden: Por dependencias (menos → más dependientes)

Fases:
  1. Abstract Models (apps/core/)
  2. User Models (apps/users/)
  3. Independent Models (Module, SecurityQuestion)
  4. Dependent Models (Function, Service, etc)
  5. Join Tables (UserServiceAccess, UserFunctionAssignment)
```

---

### 6.2 Fase 1: Abstract Models (apps/core/)

```yaml
Objetivo: Crear SOLO modelos abstract en apps/core/

TDD Steps:
  1. Escribir tests para TimeStampedModel
  2. Implementar TimeStampedModel (abstract=True)
  3. Tests para SoftDeleteMixin
  4. Implementar SoftDeleteMixin (abstract=True)
  5. Tests para AuditedModel
  6. Implementar AuditedModel (abstract=True)

Verificación:
  ✅ TODOS abstract=True
  ✅ NINGÚN db_table
  ✅ Tests pasando (>90% coverage)

Estado:
  ⚠️ SoftDeleteMixin ya está en apps/utils/
  ⏳ TimeStampedModel no existe
  ⏳ AuditedModel no existe
```

---

### 6.3 Fase 2: Mover Modelos Concretos

```yaml
🔴 DECISIÓN CRÍTICA REQUERIDA:

¿Qué hacer con Center, Service, CallRecord, UserServiceAccess?

OPCIÓN A: Crear apps nuevas AHORA
  [ ] Crear apps/centers/ → Center, Service
  [ ] Crear apps/calls/ → CallRecord
  [ ] Mover UserServiceAccess → apps/access/
  [ ] Migration SeparateDatabaseAndState
  [ ] Actualizar imports (~50 archivos)
  
  Tiempo: 3-4 días
  Riesgo: Alto (cambios masivos)
  Beneficio: Arquitectura limpia

OPCIÓN B: Mantener en apps/core/ TEMPORAL
  [ ] Documentar como temporal
  [ ] Completar funcionalidad (viewsets, tests)
  [ ] Refactorizar en FASE 10
  
  Tiempo: Continuar sin pausa
  Riesgo: Bajo (deuda técnica controlada)
  Beneficio: Progreso inmediato

OPCIÓN C: Híbrido (Recomendado)
  [ ] Mantener en apps/core/ temporalmente
  [ ] Agregar abstract models a apps/core/
  [ ] Documentar plan refactoring
  [ ] Completar testing primero
  [ ] FASE 10: Refactoring con tests funcionando
  
  Tiempo: Sin pausa + refactoring planificado
  Riesgo: Medio (deuda documentada)
  Beneficio: Testing + Arquitectura limpia
```

---

## 7. MATRIZ DE MODELOS COMPLETA

```yaml
════════════════════════════════════════════════════════
                    MATRIZ COMPLETA
════════════════════════════════════════════════════════

apps/users/ (1 modelo):
  ✅ CustomUser

apps/core/ (4 modelos) 🔴:
  ✅ Center (concreto, debería mover)
  ✅ Service (concreto, debería mover)
  ✅ CallRecord (concreto, debería mover)
  ✅ UserServiceAccess (concreto, debería mover)
  ⏳ TimeStampedModel (falta, abstract)
  ⏳ SoftDeleteMixin (está en utils)
  ⏳ AuditedModel (falta, abstract)

apps/access/ (4 modelos):
  ✅ Function
  ✅ UserFunctionAssignment
  ✅ Module
  ✅ UserModuleAccess
  ⏳ Group (falta)
  ⏳ GroupFunction (falta)
  ⏳ UserGroup (falta)

apps/authentication/ (2 modelos):
  ✅ SecurityQuestion
  ✅ UserSecurityAnswer
  ⏳ LoginAttempt (falta)
  ⏳ SessionLog (falta)

apps/audit/ (1 modelo):
  ✅ AuditLog
  ⏳ LoginLog (falta)

apps/reports/ (2 modelos):
  ✅ Report
  ✅ ExportJob
  ⏳ ReportExecution (falta)
  ⏳ ReportTemplate (falta)

apps/pipeline/ (1 modelo):
  ✅ ETLExecution
  ⏳ Job, JobExecution, JobLog, ScheduledJob (faltan)

apps/ivr_legacy/ (5+ modelos):
  ✅ CallLog (readonly)
  ✅ QuarterlyReport (readonly)
  ✅ etc (readonly MariaDB)

apps/utils/ (helpers):
  ✅ SoftDeleteMixin (debería estar en core/)
  ✅ SoftDeleteQuerySet
  ✅ SoftDeleteManager

apps/alerts/ (❌ NO EXISTE):
  ⏳ InternalMessage
  ⏳ AlertConfiguration
  ⏳ AlertSubscription

apps/calls/ (❌ NO EXISTE):
  ⏳ Call, CallStatus, CallType, etc

apps/dashboard/ (❌ NO EXISTE):
  ⏳ DashboardConfig, WidgetConfig
```

---

## 8. RECOMENDACIONES

```yaml
INMEDIATAS (HOY):
  1. Decidir estrategia: A, B o C (sección 6.3)
  2. Si Opción C:
     [ ] Agregar abstract models a apps/core/
     [ ] Documentar TODOs en código
     [ ] Continuar con viewsets.py
     [ ] TDD para nuevos modelos

CORTO PLAZO (Semana actual):
  3. Completar FASE 2 (apps/core/)
  4. Tests de modelos existentes
  5. Documentar relaciones FK
  6. Coverage >85%

MEDIO PLAZO (Próximas 2 semanas):
  7. Implementar modelos faltantes prioritarios
  8. apps/access/: Group, GroupFunction, UserGroup
  9. apps/authentication/: LoginAttempt, SessionLog
  10. TDD approach

LARGO PLAZO (FASE 10):
  11. Refactoring arquitectónico
  12. Crear apps/centers/, apps/calls/ si necesario
  13. Mover modelos concretos de apps/core/
  14. Migrations SeparateDatabaseAndState
```

---

## 9. CONCLUSIONES

```yaml
Situación Actual:
  ✅ 15 modelos implementados
  ✅ Relaciones FK funcionando
  ✅ Services Layer completo
  ⚠️ Arquitectura diverge de análisis
  ⏳ 25+ modelos faltan

Riesgos:
  🔴 apps/core/ con modelos concretos
  ⚠️ Deuda técnica acumulada
  ⚠️ Apps futuras sin planificar

Oportunidades:
  ✅ TDD desde ahora
  ✅ Testing infrastructure lista
  ✅ Refactoring planificado
  ✅ Arquitectura mejorará

Decisión Crítica:
  ❓ Usuario debe elegir: Opción A, B o C
```

---

**FIN DEL ANÁLISIS**

**Estado:** Completo - Decisión Requerida  
**Próximo Paso:** Usuario elige estrategia de refactoring  
**Documento Base para:** TDD Implementation Plan
