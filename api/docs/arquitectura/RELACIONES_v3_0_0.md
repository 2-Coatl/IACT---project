---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Relaciones entre Apps y Modelos
categoria: arquitectura/relaciones
tema: RELACIONES v3.0.0 - Basado en TODOS los ANALISIS_APP v3.0.0
autor: Claude Technical Analysis
tags: [relaciones, arquitectura, models, apps, analisis-completo]
documentos_base:
  - 56 archivos ANALISIS_APP_*.md v3.0.0
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md
  - MODELO_RBAC_IACT_v6_0_0.md
estado: definitivo
replaces: 
  - RELACIONES_v2_PARTES_1_2_3_4_5_6.md
---

# RELACIONES ENTRE APPS Y MODELOS v3.0.0
## BASADO EN ANÁLISIS ARQUITECTÓNICOS COMPLETOS

**ORIGEN:** Análisis de 56 archivos ANALISIS_APP_*.md v3.0.0

---

## 📋 TABLA DE CONTENIDOS

1. [Apps Existentes y Modelos](#apps-existentes)
2. [Apps Futuras Planificadas](#apps-futuras)
3. [apps/core/ - PROBLEMA CRÍTICO](#core-problema)
4. [Relaciones Entre Apps](#relaciones)
5. [Matriz de Dependencias](#matriz)
6. [Flujos de Datos](#flujos)

---

<a name="apps-existentes"></a>
## 1. APPS EXISTENTES (9 apps)

### 1.1 apps/access/ 🔴 CRÍTICA

```yaml
Estado: ✅ EXISTE en código
Propósito: Sistema RBAC (permisos function-based)
Complejidad: MUY ALTA (6 partes análisis)
Prioridad: 🔴 CRÍTICA - Base del sistema

Modelos (6):
  ✅ Function          - Funciones del sistema (46 funciones)
  ✅ Module            - Módulos funcionales (11 módulos)
  ✅ Group             - Grupos de usuarios
  ✅ UserGroup         - Relación User-Group (M2M)
  ✅ GroupFunction     - Relación Group-Function (M2M)
  ✅ PermissionLog     - Auditoría de permisos

Services (3):
  - RBACService (validación permisos)
  - GroupService (gestión grupos)
  - AuditService (logs)

Relaciones:
  → apps/users/ (User vía Django auth)
  → apps/audit/ (logs de cambios)
  ← TODAS las apps (validación permisos)

Uso por otras apps:
  ✅ DynamicFunctionPermission (DRF)
  ✅ @require_function decorator
  ✅ has_function() template tag
  ✅ RBACMiddleware
```

---

### 1.2 apps/audit/ 

```yaml
Estado: ✅ EXISTE en código
Propósito: Auditoría y logging de acciones
Complejidad: MEDIA (3 partes análisis)

Modelos (2):
  ✅ AuditLog      - Log de acciones (CRUD, cambios)
  ✅ LoginLog      - Log de intentos de login

Services (3):
  - AuditService (logging)
  - ReportService (reportes auditoría)
  - SearchService (búsqueda logs)

Relaciones:
  → apps/users/ (User como actor)
  → apps/access/ (funciones usadas)
  ← TODAS las apps (registran acciones)

CNST-031: Auditoría completa de requests HTTP
```

---

### 1.3 apps/authentication/

```yaml
Estado: ✅ EXISTE en código
Propósito: Autenticación y recuperación de contraseñas
Complejidad: MEDIA (3 partes análisis)

Modelos (4):
  ✅ LoginAttempt         - Intentos de login
  ✅ SecurityQuestion     - Preguntas de seguridad
  ✅ UserSecurityAnswer   - Respuestas de usuario
  ✅ SessionLog           - Historial de sesiones

Services (4):
  - AuthenticationService (login/logout)
  - SessionService (sesiones en DB)
  - RecoveryService (preguntas seguridad)
  - LockoutService (bloqueo cuentas)

Relaciones:
  → apps/users/ (User)
  → apps/audit/ (logs de autenticación)

Restricciones:
  CNST-001: NO email (recuperación por preguntas)
  CNST-010: Sesiones en DB, NO Redis
```

---

### 1.4 apps/users/

```yaml
Estado: ✅ EXISTE en código
Propósito: Gestión de usuarios y perfiles
Complejidad: ALTA (4 partes análisis)

Modelos (4):
  ✅ User (CustomUser)    - Modelo principal (AbstractUser)
  ✅ UserProfile          - Perfil extendido (1-to-1)
  ✅ UserSettings         - Preferencias usuario
  ✅ SessionHistory       - Historial de sesiones

Services (4):
  - UserService (CRUD, activation)
  - AuthenticationService (login, logout)
  - ProfileService (gestión perfiles)
  - PasswordService (cambio, reset)

Relaciones:
  → apps/access/ (UserGroup)
  → apps/authentication/ (login)
  → apps/audit/ (cambios usuario)
  ← TODAS las apps (Foreign Key User)
```

---

### 1.5 apps/ivr_legacy/ (apps/ivr/)

```yaml
Estado: ✅ EXISTE en código como apps/ivr_legacy/
Propósito: Datos IVR legacy readonly (MariaDB)
Complejidad: ALTA (4 partes análisis v3.1.0)

Modelos (11 - TODOS readonly):
  ✅ QuarterlyReport       - Reportes trimestrales
  ✅ TransferReport        - Reportes de transferencias
  ✅ AbandonedReport       - Reportes de abandonadas
  ✅ ClientReport          - Reportes de clientes
  ✅ CallRecordQ1          - Histórico trimestre 1
  ✅ CallRecordQ2          - Histórico trimestre 2
  ✅ CallRecordQ3          - Histórico trimestre 3
  ✅ CallRecordQ4          - Histórico trimestre 4
  ✅ MenuErrorReport       - Errores de menú
  ✅ MenuPerformanceReport - Performance de menú
  ✅ TransferDetailReport  - Detalle transferencias

Database Router:
  ✅ IVRRouter (BLOQUEA escrituras - CNST-002)
  ✅ using='ivr_legacy' (MariaDB readonly)

Relaciones:
  → apps/pipeline/ (ETL consume estos datos)
  → apps/reports/ (reportes usan estos datos)

Restricciones:
  CNST-002: IVR Legacy READONLY (MariaDB)
  CNST-003: PostgreSQL para analytics
```

---

### 1.6 apps/pipeline/

```yaml
Estado: ✅ EXISTE en código
Propósito: ETL jobs y scheduler
Complejidad: ALTA (4 partes análisis)

Modelos (3):
  ✅ JobExecution    - Ejecuciones de jobs
  ✅ JobLog          - Logs de ejecución
  ✅ ScheduledJob    - Jobs programados

Services (4):
  - ETLService (orquestación)
  - SchedulerService (APScheduler)
  - MonitorService (monitoreo jobs)
  - CleanupService (limpieza)

Relaciones:
  → apps/ivr_legacy/ (lee datos)
  → apps/audit/ (logs de ETL)

Restricciones:
  CNST-013: APScheduler (NO Celery)
  CNST-007: Export limits
```

---

### 1.7 apps/reports/

```yaml
Estado: ✅ EXISTE en código
Propósito: Generación de reportes multi-formato
Complejidad: ALTA (5 partes análisis)

Modelos (3):
  ✅ Report           - Definición de reporte
  ✅ ReportExecution  - Ejecuciones de reportes
  ✅ ReportTemplate   - Templates de reportes

Services (5):
  - ReportGeneratorService (generación)
  - ExportService (Excel/CSV/PDF)
  - TemplateService (gestión templates)
  - ScheduleService (reportes programados)
  - CacheService (cache de reportes)

Relaciones:
  → apps/ivr_legacy/ (datos IVR)
  → apps/access/ (permisos RPT_*)
  → apps/users/ (created_by)

Restricciones:
  CNST-007: MAX_EXPORT_ROWS = 100,000
```

---

### 1.8 apps/utils/

```yaml
Estado: ✅ EXISTE en código (NO en INSTALLED_APPS)
Propósito: Helpers, funciones compartidas
Complejidad: BAJA (3 partes análisis)

Modelos: ❌ NINGUNO (solo funciones)

Contenido:
  ✅ SoftDeleteMixin (abstract)
  ✅ SoftDeleteQuerySet
  ✅ SoftDeleteManager
  ✅ validators.py (15 validators)
  ✅ constants.py (100+ constants)
  ✅ helpers.py (funciones helper)
  ✅ decorators.py
  ✅ formatters.py

Relaciones:
  ← TODAS las apps (usan helpers)

NOTA: Debe registrarse en INSTALLED_APPS
```

---

### 1.9 apps/core/ 🔴 PROBLEMA CRÍTICO

```yaml
Estado: ✅ EXISTE en código
Análisis: ANALISIS_APP_CORE_v3_0_0 (3 partes)
Propósito CORRECTO: Solo clases abstractas base
Complejidad: BAJA (3 partes análisis)

Modelos CORRECTOS (abstract=True):
  ✅ TimeStampedModel (abstract)
  ✅ SoftDeleteMixin (abstract) - MOVER a apps/utils/
  ✅ AuditedModel (abstract)
  ✅ SoftDeleteQuerySet - MOVER a apps/utils/
  ✅ SoftDeleteManager - MOVER a apps/utils/

Contenido CORRECTO:
  ✅ exceptions.py (7 excepciones base)
  ✅ validators.py (clases validadoras) - MOVER a apps/utils/
  ✅ middleware.py (4 middlewares)
  ✅ permissions.py (DRF permissions base)
  ✅ mixins.py (5 mixins)
  ✅ services.py (BaseService)

🔴 MODELOS INCORRECTOS (db_table presente):
  ❌ Center              → apps/centers/ (NO EXISTE)
  ❌ Service             → apps/centers/ (NO EXISTE)
  ❌ CallRecord          → apps/analytics/ (NO EXISTE)
  ❌ UserServiceAccess   → apps/access/ (alternativa)

🔴 SERVICES INCORRECTOS:
  ❌ CenterService       → apps/centers/services.py
  ❌ ServiceService      → apps/centers/services.py
  ❌ CallRecordService   → apps/analytics/services.py

🔴 SERIALIZERS/VIEWSETS INCORRECTOS:
  ❌ serializers.py (20 serializers) → apps/centers/ + apps/analytics/
  ❌ filters.py (4 filters)          → apps/centers/ + apps/analytics/
  ❌ permissions.py (6 custom)       → apps/centers/ + apps/analytics/
  ❌ viewsets.py (4 viewsets)        → apps/centers/ + apps/analytics/

Relaciones INCORRECTAS:
  → apps/utils/ (validators) ❌ CIRCULAR
  → apps/access/ (UserServiceAccess) ❌ UBICACIÓN INCORRECTA
  ← Ninguna app debe depender de apps/core/ para modelos concretos

🔴 REGLA DE ORO VIOLADA:
  apps/core/models.py SOLO puede tener:
  ✅ class Meta: abstract = True
  ❌ NINGÚN db_table
```

---

<a name="apps-futuras"></a>
## 2. APPS FUTURAS PLANIFICADAS (3 apps)

### 2.1 apps/calls/ 🔴 CORE BUSINESS

```yaml
Estado: ❌ NO EXISTE (tiene análisis completo)
Análisis: ANALISIS_APP_CALLS_v3_0_0 (1 parte, 4 pendientes)
Propósito: Gestión de llamadas individuales tiempo real
Complejidad: MUY ALTA (4 partes estimadas)
Prioridad: 🔴 CRÍTICA - Core del call center

Modelos (6):
  ⏳ Call             - Llamada individual
  ⏳ CallStatus       - Estados de llamada
  ⏳ CallType         - Tipos de llamada
  ⏳ CallRecording    - Grabaciones
  ⏳ CallNote         - Notas/comentarios
  ⏳ CallMetrics      - Métricas agregadas

Services (4):
  - CallService (CRUD, gestión)
  - CallStatsService (estadísticas)
  - RecordingService (grabaciones)
  - QueueService (colas de espera)

Relaciones FUTURAS:
  → apps/users/ (agentes)
  → apps/access/ (permisos CALL_*)
  → PBX/Asterisk (integración telefonía)

DIFERENCIA CRÍTICA con CallRecord:
  - Call = llamada INDIVIDUAL (tiempo real)
  - CallRecord = datos AGREGADOS (analytics)
  Son COMPLEMENTARIOS, no duplicados
```

---

### 2.2 apps/dashboard/

```yaml
Estado: ❌ NO EXISTE (tiene análisis completo)
Análisis: ANALISIS_APP_DASHBOARD_v3_0_0 (5 partes)
Propósito: Dashboards configurables y widgets
Complejidad: ALTA (5 partes análisis)

Modelos (estimados):
  ⏳ DashboardConfig     - Configuración de dashboards
  ⏳ Widget              - Widgets individuales
  ⏳ WidgetConfig        - Configuración de widgets
  ⏳ UserDashboard       - Dashboards por usuario

Relaciones FUTURAS:
  → apps/users/ (dashboards personalizados)
  → apps/access/ (permisos DSH_*)
  → apps/ivr_legacy/ (datos para widgets)
  → apps/reports/ (integración reportes)
```

---

### 2.3 apps/alerts/

```yaml
Estado: ❌ NO EXISTE (tiene análisis completo)
Análisis: ANALISIS_APP_ALERTS_v3_0_0 (3 partes)
Propósito: Sistema de alertas y notificaciones
Complejidad: MEDIA (3 partes análisis)

Modelos (4):
  ⏳ AlertConfiguration  - Configuración de alertas
  ⏳ AlertSubscription   - Suscripciones de usuarios
  ⏳ InternalMessage     - Mensajes internos
  ⏳ MessageRecipient    - Destinatarios de mensajes

Relaciones FUTURAS:
  → apps/users/ (destinatarios)
  → apps/access/ (permisos ALR_*)
```

---

<a name="core-problema"></a>
## 3. apps/core/ - ANÁLISIS DEL PROBLEMA

### 3.1 Arquitectura CORRECTA según ANALISIS_APP_CORE_v3_0_0

```yaml
apps/core/ DEBE tener SOLO:
  ✅ Abstract Models:
      - TimeStampedModel (abstract=True)
      - SoftDeleteMixin (abstract=True)
      - AuditedModel (abstract=True)
      - SoftDeleteQuerySet
      - SoftDeleteManager
  
  ✅ Exceptions (7):
      - IACTBaseException
      - ValidationError
      - BusinessRuleError
      - PermissionDeniedError
      - ResourceNotFoundError
      - ConfigurationError
      - ExternalServiceError
  
  ✅ Validators (clases):
      - PhoneValidator
      - EmailValidator
      - NITValidator
      - DateRangeValidator
  
  ✅ Middleware (4):
      - RequestLoggingMiddleware
      - SecurityHeadersMiddleware
      - UserTimezoneMiddleware
      - HealthCheckMiddleware
  
  ✅ Permissions DRF (4):
      - RequiresFunctionPermission
      - IsOwnerOrReadOnly
      - IsSuperUserOrReadOnly
      - AllowOptionsAuthentication
  
  ✅ Mixins (5):
      - SoftDeleteViewSetMixin
      - ServiceFilterMixin
      - AuditCreateMixin
      - AuditUpdateMixin
      - PaginationControlMixin
  
  ✅ Services base:
      - BaseService (clase base)

❌ NO DEBE TENER:
  ❌ Modelos concretos (con db_table)
  ❌ Services específicos (CenterService, etc)
  ❌ Serializers específicos
  ❌ ViewSets específicos
  ❌ Filters específicos
```

---

### 3.2 Código REAL Actual (INCORRECTO)

```python
# apps/core/models.py (ACTUAL - INCORRECTO)

✅ CORRECTO - Abstract models:
class TimeStampedModel(models.Model):
    class Meta:
        abstract = True  # ✅

class SoftDeleteMixin(models.Model):
    class Meta:
        abstract = True  # ✅

class AuditedModel(models.Model):
    class Meta:
        abstract = True  # ✅

❌ INCORRECTO - Modelos concretos:
class Center(SoftDeleteMixin, models.Model):
    class Meta:
        db_table = 'core_centers'  # ❌ TIENE db_table

class Service(SoftDeleteMixin, models.Model):
    class Meta:
        db_table = 'core_services'  # ❌ TIENE db_table

class CallRecord(SoftDeleteMixin, models.Model):
    class Meta:
        db_table = 'core_call_records'  # ❌ TIENE db_table

class UserServiceAccess(SoftDeleteMixin, models.Model):
    class Meta:
        db_table = 'core_user_service_access'  # ❌ TIENE db_table
```

---

### 3.3 Ubicación CORRECTA según Análisis

```yaml
Center y Service:
  Ubicación según ANALISIS_APP_CORE_v3_0_0:
    → apps/centers/models.py
  
  Problema:
    ❌ apps/centers/ NO EXISTE
    ❌ apps/centers/ NO TIENE ANALISIS v3.0.0
  
  Opciones:
    A) Crear apps/centers/ (nueva app)
    B) Dejar en apps/core/ temporalmente
    C) Mover a apps/access/ (si son permisos de servicio)

CallRecord:
  Ubicación según ANALISIS_APP_CORE_v3_0_0:
    → apps/analytics/models.py
  
  Problema:
    ❌ apps/analytics/ NO EXISTE
    ❌ apps/analytics/ NO TIENE ANALISIS v3.0.0
  
  Diferencia con apps/calls/:
    - CallRecord = datos AGREGADOS (fecha/teléfono/servicio)
    - Call = llamada INDIVIDUAL (tiempo real)
    - Son COMPLEMENTARIOS
  
  Opciones:
    A) Crear apps/analytics/ (nueva app)
    B) Mover a apps/calls/ (cuando se cree)
    C) Dejar en apps/core/ temporalmente

UserServiceAccess:
  Ubicación NO especificada en análisis
  
  Naturaleza: Relación User-Service (permisos)
  
  Opciones:
    A) apps/access/ (permisos y accesos)
    B) apps/centers/ (junto con Service)
    C) Nueva app apps/service_access/
```

---

### 3.4 Archivos Adicionales INCORRECTOS en apps/core/

```yaml
❌ apps/core/services/:
  - center_service.py (9 métodos)
  - service_service.py (12 métodos)
  - call_record_service.py (11 métodos)
  
  Deben ir a:
    → apps/centers/services/
    → apps/analytics/services/

❌ apps/core/serializers.py (20 serializers):
  - CenterSerializer, CenterListSerializer, CenterDetailSerializer
  - ServiceSerializer, ServiceListSerializer, ServiceDetailSerializer
  - CallRecordSerializer, CallRecordListSerializer
  - UserServiceAccessSerializer
  
  Deben ir a:
    → apps/centers/serializers.py
    → apps/analytics/serializers.py

❌ apps/core/filters.py (4 filters):
  - CenterFilter
  - ServiceFilter
  - CallRecordFilter
  - UserServiceAccessFilter
  
  Deben ir a:
    → apps/centers/filters.py
    → apps/analytics/filters.py

❌ apps/core/permissions.py (6 custom permissions):
  - IsCenterManager
  - IsServiceManager
  - HasServiceAccess
  - CanGrantAccess
  - CanRevokeAccess
  
  Deben ir a:
    → apps/centers/permissions.py

❌ apps/core/viewsets.py (estimado):
  - CenterViewSet
  - ServiceViewSet
  - CallRecordViewSet
  - UserServiceAccessViewSet
  
  Deben ir a:
    → apps/centers/viewsets.py
    → apps/analytics/viewsets.py
```

---

<a name="relaciones"></a>
## 4. RELACIONES ENTRE APPS

### 4.1 Dependencias Core (apps existentes)

```
apps/access/ (RBAC) 🔴 BASE
  ↓
  ├→ apps/users/ (User)
  ├→ apps/audit/ (logs)
  └─→ TODAS las apps (permisos)

apps/users/ (CustomUser)
  ↓
  ├→ apps/authentication/ (login)
  ├→ apps/audit/ (logs)
  └─→ TODAS las apps (FK User)

apps/authentication/
  ↓
  ├→ apps/users/ (User)
  └→ apps/audit/ (logs)

apps/audit/
  ↓
  ├→ apps/users/ (User)
  └→ apps/access/ (funciones)

apps/ivr_legacy/ (readonly MariaDB)
  ↓
  ├→ apps/pipeline/ (ETL)
  └→ apps/reports/ (datos)

apps/pipeline/ (ETL)
  ↓
  ├→ apps/ivr_legacy/ (lee)
  └→ apps/audit/ (logs)

apps/reports/
  ↓
  ├→ apps/ivr_legacy/ (datos)
  ├→ apps/users/ (User)
  └→ apps/access/ (permisos RPT_*)

apps/core/ (SOLO abstract)
  ↓
  └─→ TODAS las apps (heredan TimeStampedModel, etc)

apps/utils/ (helpers)
  ↓
  └─→ TODAS las apps (funciones helper)
```

---

### 4.2 Dependencias Futuras (cuando se creen apps)

```
apps/calls/ (futuro)
  ↓
  ├→ apps/users/ (agentes)
  ├→ apps/access/ (permisos CALL_*)
  └→ PBX/Asterisk (telefonía)

apps/dashboard/ (futuro)
  ↓
  ├→ apps/users/ (User)
  ├→ apps/access/ (permisos DSH_*)
  ├→ apps/ivr_legacy/ (datos)
  └→ apps/reports/ (integración)

apps/alerts/ (futuro)
  ↓
  ├→ apps/users/ (User)
  └→ apps/access/ (permisos ALR_*)

apps/centers/ (futuro - para Center/Service)
  ↓
  ├→ apps/users/ (User)
  └→ apps/access/ (permisos)

apps/analytics/ (futuro - para CallRecord)
  ↓
  ├→ apps/users/ (User)
  ├→ apps/access/ (permisos)
  └→ apps/pipeline/ (ETL)
```

---

<a name="matriz"></a>
## 5. MATRIZ DE DEPENDENCIAS

```
┌─────────────┬────────┬────────┬────────┬────────┬────────┬────────┬────────┬────────┐
│             │ access │ users  │  auth  │ audit  │  ivr   │pipeline│reports │ utils  │
├─────────────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│ apps/access │   -    │   ✅   │        │   ✅   │        │        │        │   ✅   │
│ apps/users  │   ✅   │   -    │   ✅   │   ✅   │        │        │        │   ✅   │
│ apps/auth   │   ✅   │   ✅   │   -    │   ✅   │        │        │        │   ✅   │
│ apps/audit  │   ✅   │   ✅   │        │   -    │        │        │        │   ✅   │
│ apps/ivr    │        │        │        │        │   -    │   ✅   │   ✅   │   ✅   │
│ apps/pipeline│   ✅  │   ✅   │        │   ✅   │   ✅   │   -    │        │   ✅   │
│ apps/reports│   ✅   │   ✅   │        │        │   ✅   │        │   -    │   ✅   │
│ apps/utils  │        │        │        │        │        │        │        │   -    │
│ apps/core   │        │        │        │        │        │        │        │   ✅   │
└─────────────┴────────┴────────┴────────┴────────┴────────┴────────┴────────┴────────┘

Leyenda:
  ✅ = Depende de (import, FK, permisos)
  -  = Self (no aplica)
```

---

<a name="flujos"></a>
## 6. FLUJOS DE DATOS

### 6.1 Flujo ETL (IVR → Analytics)

```
IVR Legacy (MariaDB readonly)
  ↓
apps/ivr_legacy/ (modelos readonly)
  ↓
apps/pipeline/ (ETL jobs)
  ↓
apps/analytics/ (CallRecord - FUTURO)
  ↓
apps/reports/ (reportes)
```

---

### 6.2 Flujo Autenticación y Permisos

```
Usuario ingresa credenciales
  ↓
apps/authentication/ (AuthenticationService)
  ↓
apps/users/ (User lookup)
  ↓
apps/access/ (cargar permisos RBAC)
  ↓
apps/audit/ (registrar login)
  ↓
Request con user_functions disponibles
```

---

### 6.3 Flujo Validación de Permisos

```
Request a endpoint protegido
  ↓
DynamicFunctionPermission (DRF)
  ↓
apps/access/ (RBACService.user_has_function)
  ↓
  ├─ Cache (5 min TTL)
  │  └→ Return True/False
  │
  └─ DB Query (UserGroup → GroupFunction → Function)
     └→ Cache result
     └→ Return True/False
  ↓
Allow/Deny request
```

---

## 7. RESUMEN EJECUTIVO

```yaml
Apps EXISTENTES: 9
  ✅ access (RBAC - CRÍTICA)
  ✅ users (CustomUser)
  ✅ authentication (login/logout)
  ✅ audit (logging)
  ✅ ivr_legacy (readonly MariaDB)
  ✅ pipeline (ETL)
  ✅ reports (generación reportes)
  ✅ utils (helpers)
  ✅ core (SOLO abstract - PROBLEMA: tiene concretos)

Apps FUTURAS: 3
  ⏳ calls (llamadas tiempo real)
  ⏳ dashboard (dashboards configurables)
  ⏳ alerts (alertas y notificaciones)

Apps MENCIONADAS sin análisis: 2
  ❓ centers (Center, Service)
  ❓ analytics (CallRecord)

PROBLEMA CRÍTICO apps/core/:
  ❌ Tiene 4 modelos concretos (deben ser abstract)
  ❌ Tiene services específicos (deben ir a apps de negocio)
  ❌ Tiene serializers/viewsets/filters (deben ir a apps de negocio)
  ❌ Circular dependency con apps/utils/

SOLUCIÓN RECOMENDADA:
  1. Crear apps/centers/ (Center, Service, UserServiceAccess)
  2. Crear apps/analytics/ (CallRecord)
  3. Limpiar apps/core/ (SOLO abstract models)
  4. Mover validators a apps/utils/
  5. Actualizar imports (~50 archivos)
  6. Migrations con SeparateDatabaseAndState

ALTERNATIVA TEMPORAL:
  1. Dejar código actual (funcionando)
  2. Documentar ubicación incorrecta
  3. Crear apps nuevas en FASE 8-9
  4. Refactorizar con tests ya funcionando
```

---

**FIN DEL DOCUMENTO**

**56 archivos ANALISIS_APP_*.md considerados ✅**  
**Arquitectura CORRECTA definida ✅**  
**Problema apps/core/ identificado ✅**  
**Soluciones propuestas ✅**
