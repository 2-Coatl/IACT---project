---
version: 1.0.0
date: 2026-01-20
project: IACT Call Center System
type: Plan de Implementación
categoria: implementacion
tema: Plan Completo de Implementación - 11 Módulos Analizados
autor: Claude Technical Analysis
tags: [implementacion, plan, roadmap, clean-code]
documentos_base:
  - 43 partes de análisis arquitectónico
  - 11 módulos completos
  - ~30,870 líneas de código
  - 452 tests
estado: plan
---

# PLAN DE IMPLEMENTACIÓN COMPLETO - IACT v3.0.0
## BASADO EN 43 PARTES DE ANÁLISIS ARQUITECTÓNICO

---

## 📊 RESUMEN EJECUTIVO

```yaml
Análisis completado:
  - Documentación: 43 partes (~1,700KB)
  - Módulos: 11/11 (100%)
  - Líneas código: ~30,870 líneas
  - Tests: 452 tests estimados
  - Endpoints: 95 endpoints REST
  - Funciones RBAC: 57 documentadas
  - Clean Code: v3.0.1 aplicado

Tiempo estimado total: 12-16 semanas
Complejidad: ALTA
Riesgo: MEDIO-ALTO
```

---

## 🎯 OBJETIVOS DEL PLAN

1. Implementar las 11 apps analizadas
2. Migrar de estado actual a arquitectura definitiva
3. Aplicar CLEAN_CODE v3.0.1 en TODO el código
4. Alcanzar >85% coverage
5. Zero downtime en producción

---

## 📋 ÍNDICE

1. [Análisis de Estado Actual](#fase-0)
2. [Fase 1: Fundamentos](#fase-1)
3. [Fase 2: Core & Utils](#fase-2)
4. [Fase 3: Authentication & Users](#fase-3)
5. [Fase 4: Access (RBAC)](#fase-4)
6. [Fase 5: Audit](#fase-5)
7. [Fase 6: IVR & Pipeline](#fase-6)
8. [Fase 7: Reports](#fase-7)
9. [Fase 8: Dashboard & Alerts](#fase-8)
10. [Fase 9: Testing & QA](#fase-9)
11. [Fase 10: Deployment](#fase-10)

---

<a name="fase-0"></a>
## FASE 0: ANÁLISIS DE ESTADO ACTUAL (Semana 1)

### 0.1 Auditoría del Código Existente

**Objetivo:** Entender qué ya existe vs qué hay que crear.

```bash
# 1. Verificar estructura actual
ls -R apps/

# 2. Contar líneas de código existentes
find apps/ -name "*.py" | xargs wc -l

# 3. Ejecutar tests actuales
pytest --collect-only
pytest -v

# 4. Verificar coverage actual
pytest --cov=apps --cov-report=html

# 5. Análisis de BD
python manage.py showmigrations
python manage.py dbshell
```

### 0.2 Documentar Estado Actual

**Deliverables:**
- `ESTADO_ACTUAL.md`: Inventario de código existente
- `GAPS_ANALYSIS.md`: Qué falta vs análisis
- `MIGRATION_PLAN.md`: Plan de migración específico

**Tiempo:** 3-5 días

---

<a name="fase-1"></a>
## FASE 1: FUNDAMENTOS (Semana 2)

### 1.1 Configuración Base

**Tareas:**
1. Actualizar `requirements.txt` con TODAS las dependencias
2. Configurar settings (base, dev, prod, testing)
3. Configurar logging
4. Configurar dual database (PostgreSQL + MariaDB)
5. Configurar cache (locmem - CNST-010)

**Archivos:**
```
config/
├── settings/
│   ├── base.py          # Settings base
│   ├── development.py   # Dev
│   ├── production.py    # Prod
│   └── testing.py       # Tests
├── urls.py              # URLs root
├── wsgi.py
└── asgi.py
```

**Checklist:**
- [ ] PostgreSQL configurado (DEFAULT)
- [ ] MariaDB configurado (IVR_LEGACY - readonly)
- [ ] Database Router creado
- [ ] Logging a archivo + console
- [ ] Cache locmem configurado
- [ ] Settings por ambiente

**Tiempo:** 3-4 días

---

### 1.2 Tests Infrastructure

**Tareas:**
1. Mover TODOS los tests a `/tests/`
2. Actualizar `conftest.py` con 60+ fixtures
3. Configurar pytest.ini
4. Crear factories con factory_boy

**Estructura final:**
```
tests/
├── conftest.py          # 60+ fixtures
├── unit/               # Tests por app
│   ├── access/
│   ├── users/
│   └── ...
├── integration/        # Tests multi-app
├── api/                # Tests endpoints
└── e2e/                # Tests E2E
```

**Checklist:**
- [ ] conftest.py con 60+ fixtures
- [ ] pytest.ini configurado
- [ ] Factories creados
- [ ] README.md actualizado
- [ ] Tests básicos pasando

**Tiempo:** 2-3 días

---

<a name="fase-2"></a>
## FASE 2: CORE & UTILS (Semanas 3-4)

### 2.1 apps/core/ (SOLO Abstract Models)

**CRÍTICO:** `apps/core/models.py` SOLO puede tener `abstract=True`.

**Tareas:**
1. Crear abstract models:
   - TimeStampedModel
   - SoftDeleteMixin
   - AuditedModel
   - SoftDeleteManager/QuerySet

2. Crear exceptions:
   - IACTBaseException
   - ValidationError
   - BusinessRuleError
   - PermissionDeniedError
   - ResourceNotFoundError

3. Crear validators (clases):
   - PhoneValidator
   - EmailValidator
   - NITValidator

4. Crear middleware:
   - RequestLoggingMiddleware (CNST-031)
   - SecurityHeadersMiddleware
   - UserTimezoneMiddleware

5. Crear permissions DRF:
   - RequiresFunctionPermission
   - IsOwnerOrReadOnly

6. Crear mixins:
   - SoftDeleteViewSetMixin
   - ServiceFilterMixin
   - AuditCreateMixin

**Archivos:**
```
apps/core/
├── models.py             # SOLO abstract=True
├── exceptions.py
├── validators.py
├── middleware/
│   ├── logging.py
│   └── security.py
├── permissions.py
├── mixins.py
└── services.py
```

**Tests:**
- 25+ tests en `tests/unit/core/`

**Checklist:**
- [ ] Todos los models con abstract=True
- [ ] NINGÚN modelo concreto en core/
- [ ] 7 exceptions creadas
- [ ] 3 validators (clases)
- [ ] 4 middleware
- [ ] 4 permissions DRF
- [ ] 5 mixins
- [ ] Tests pasando (>90% coverage)

**Tiempo:** 5-6 días

---

### 2.2 apps/utils/ (SOLO Funciones)

**CRÍTICO:** `apps/utils/` NO debe tener `models.py`.

**Tareas:**
1. Crear validators (funciones):
   - validate_email()
   - validate_phone_cl()
   - validate_rut()
   - validate_date_range()

2. Crear formatters:
   - format_phone_cl()
   - format_rut()
   - format_currency()
   - format_percentage()

3. Crear date_utils:
   - get_quarter_from_date()
   - get_quarter_date_range()
   - format_datetime_cl()

4. Crear string_utils:
   - slugify()
   - normalize_text()
   - truncate()

5. Crear decorators:
   - @cache_result
   - @log_execution
   - @retry_on_failure

**Archivos:**
```
apps/utils/
├── validators.py        # Funciones validación
├── formatters.py        # Funciones formato
├── date_utils.py        # Funciones fechas
├── string_utils.py      # Funciones strings
├── number_utils.py      # Funciones números
├── decorators.py        # Decoradores
├── exceptions.py        # Exceptions utils
└── constants.py         # Constantes globales
```

**Tests:**
- 40+ tests en `tests/unit/utils/`

**Checklist:**
- [ ] NO models.py en utils/
- [ ] 6 validators (funciones)
- [ ] 8 formatters
- [ ] 10 date utils
- [ ] 8 string utils
- [ ] 3 decorators
- [ ] Tests pasando (>95% coverage)

**Tiempo:** 4-5 días

---

<a name="fase-3"></a>
## FASE 3: AUTHENTICATION & USERS (Semanas 5-6)

### 3.1 apps/users/

**Tareas:**
1. Crear User model (si no existe)
2. Crear UserProfile model
3. Crear services:
   - UserService (CRUD)
4. Crear serializers:
   - UserSerializer
   - UserCreateSerializer
   - UserUpdateSerializer
5. Crear ViewSets:
   - UserViewSet
6. Crear endpoints REST

**Estructura:**
```
apps/users/
├── models.py            # User, UserProfile
├── services.py          # UserService
├── serializers.py       # 3 serializers
├── views.py             # UserViewSet
├── urls.py
└── permissions.py
```

**Endpoints:**
- GET /api/v1/users/
- POST /api/v1/users/
- GET /api/v1/users/{id}/
- PUT /api/v1/users/{id}/
- DELETE /api/v1/users/{id}/
- GET /api/v1/users/me/

**Tests:**
- 20+ tests en `tests/unit/users/`
- 10+ tests en `tests/api/test_users_api.py`

**Checklist:**
- [ ] Modelos creados
- [ ] Service layer implementado
- [ ] 3 serializers
- [ ] ViewSet con RBAC
- [ ] 6 endpoints REST
- [ ] Tests pasando (>85% coverage)

**Tiempo:** 5-6 días

---

### 3.2 apps/authentication/

**Tareas:**
1. Configurar JWT (rest_framework_simplejwt)
2. Crear LoginView
3. Crear LogoutView
4. Crear PasswordChangeView
5. Crear services:
   - AuthenticationService
   - SessionService
6. Configurar sessions DB (CNST-010)

**Estructura:**
```
apps/authentication/
├── models.py            # Session (si necesario)
├── services.py          # AuthService, SessionService
├── serializers.py       # LoginSerializer, TokenSerializer
├── views.py             # LoginView, LogoutView
└── urls.py
```

**Endpoints:**
- POST /api/v1/auth/login/
- POST /api/v1/auth/logout/
- POST /api/v1/auth/refresh/
- POST /api/v1/auth/password-change/

**Tests:**
- 20+ tests en `tests/unit/authentication/`
- 10+ tests en `tests/integration/test_auth_flow.py`

**Checklist:**
- [ ] JWT configurado
- [ ] Login/Logout funcionando
- [ ] Sessions DB configurado
- [ ] Service layer
- [ ] 4 endpoints REST
- [ ] Tests pasando (>85% coverage)

**Tiempo:** 4-5 días

---

<a name="fase-4"></a>
## FASE 4: ACCESS (RBAC) (Semanas 7-9)

**CRÍTICO:** Esta es la app CORE del sistema. Máxima prioridad.

### 4.1 Modelos RBAC

**Tareas:**
1. Crear modelos:
   - Module (jerarquía)
   - Function
   - Role
   - UserModuleAccess
   - UserFunctionAssignment
   - UserRoleAssignment
   - RoleFunctionAssignment

**Relaciones:**
```
Module → Function (1:N)
User → Module (N:N via UserModuleAccess)
User → Function (N:N via UserFunctionAssignment)
User → Role (N:N via UserRoleAssignment)
Role → Function (N:N via RoleFunctionAssignment)
```

**Checklist:**
- [ ] 7 modelos creados
- [ ] Jerarquía Module con MPTT o similar
- [ ] Unique constraints
- [ ] Soft delete en todos
- [ ] Tests models (>90% coverage)

**Tiempo:** 6-7 días

---

### 4.2 Services RBAC

**Tareas:**
1. ModuleService:
   - get_user_modules()
   - get_module_tree()
   - grant_module_access()

2. FunctionService:
   - get_user_functions()
   - user_has_function()
   - assign_function_to_user()

3. RoleService:
   - get_user_roles()
   - assign_role_to_user()
   - get_role_functions()

4. AccessService (central):
   - check_access()
   - check_function()
   - get_accessible_resources()

**Estructura:**
```
apps/access/
├── models.py            # 7 modelos
├── services/
│   ├── module_service.py
│   ├── function_service.py
│   ├── role_service.py
│   └── access_service.py
├── serializers.py       # 7+ serializers
├── views.py             # 5 ViewSets
└── urls.py
```

**Checklist:**
- [ ] 4 services implementados
- [ ] Queries optimizadas (select_related, prefetch_related)
- [ ] Cache en queries repetitivos
- [ ] Tests services (>90% coverage)

**Tiempo:** 7-8 días

---

### 4.3 API REST RBAC

**Endpoints (17):**
```
Modules (5):
  GET  /api/v1/access/modules/
  GET  /api/v1/access/modules/{id}/
  POST /api/v1/access/modules/
  GET  /api/v1/access/my-modules/
  GET  /api/v1/access/module-tree/

Functions (7):
  GET    /api/v1/access/functions/
  GET    /api/v1/access/functions/{id}/
  POST   /api/v1/access/functions/
  PUT    /api/v1/access/functions/{id}/
  DELETE /api/v1/access/functions/{id}/
  GET    /api/v1/access/my-functions/
  POST   /api/v1/access/check-function/

Roles (5):
  GET    /api/v1/access/roles/
  POST   /api/v1/access/roles/
  GET    /api/v1/access/roles/{id}/
  GET    /api/v1/access/my-roles/
  POST   /api/v1/access/assign-role/
```

**Checklist:**
- [ ] 17 endpoints implementados
- [ ] Serializers optimizados
- [ ] Paginación en list endpoints
- [ ] Filtros (module, role, user)
- [ ] Permisos RBAC en cada endpoint
- [ ] Tests API (>85% coverage)

**Tiempo:** 6-7 días

---

### 4.4 Fixtures Iniciales RBAC

**Tareas:**
1. Crear 57 funciones documentadas
2. Crear módulos básicos
3. Crear roles predefinidos:
   - ADMIN
   - MANAGER
   - ANALYST
   - VIEWER

**Archivos:**
```
apps/access/fixtures/
├── modules.json         # Módulos base
├── functions.json       # 57 funciones
└── roles.json          # Roles predefinidos
```

**Comando:**
```bash
python manage.py loaddata modules functions roles
```

**Checklist:**
- [ ] 57 funciones creadas
- [ ] Módulos base creados
- [ ] 4 roles predefinidos
- [ ] Fixture loadable

**Tiempo:** 3-4 días

---

<a name="fase-5"></a>
## FASE 5: AUDIT (Semanas 10)

### 5.1 Modelos Audit

**Tareas:**
1. Crear modelos:
   - AuditLog (immutable)
   - SessionLog
   - RequestLog

**CNST-031:** Auditoría completa de acciones.

**Estructura:**
```
apps/audit/
├── models.py            # AuditLog, SessionLog, RequestLog
├── services.py          # AuditService
├── middleware.py        # AuditMiddleware
├── decorators.py        # @audit_action
├── serializers.py       # 3 serializers
├── views.py             # 3 ViewSets
└── urls.py
```

**Checklist:**
- [ ] AuditLog immutable (no update/delete)
- [ ] Logs append-only
- [ ] Middleware captura requests
- [ ] Decorator @audit_action
- [ ] Retención 7 días (configurable)
- [ ] Tests (>90% coverage)

**Tiempo:** 5-6 días

---

<a name="fase-6"></a>
## FASE 6: IVR & PIPELINE (Semanas 11-12)

### 6.1 apps/ivr/ (BD Readonly)

**CRÍTICO:** CNST-002 - BD IVR readonly.

**Tareas:**
1. Configurar Database Router (IVRRouter)
2. Crear modelos ETL:
   - QuarterlyReport
   - TransferReport
   - AbandonedReport
   - ClientReport
   - CallRecordQ1

3. Verificar SOLO queries SELECT

**IVRRouter:**
```python
class IVRRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'ivr':
            return 'ivr_legacy'
        return None
    
    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'ivr':
            return None  # ❌ Prohibido escribir
        return None
```

**Checklist:**
- [ ] Router configurado
- [ ] 11 modelos ETL (readonly)
- [ ] SOLO SELECT permitido
- [ ] Tests de readonly
- [ ] Conexión MariaDB estable

**Tiempo:** 5-6 días

---

### 6.2 apps/pipeline/ (APScheduler)

**CRÍTICO:** CNST-013 - APScheduler (NO Celery).

**Tareas:**
1. Configurar APScheduler
2. Crear jobs:
   - cleanup_sessions (diario 3:00 AM)
   - etl_monitor (cada 6h)
   - health_check (cada 5 min)

3. Crear modelos:
   - ETLJob
   - ETLError
   - SchedulerConfig

4. Crear services:
   - ETLService
   - MonitorService
   - HealthCheckService

**Estructura:**
```
apps/pipeline/
├── models.py            # ETLJob, ETLError, SchedulerConfig
├── services/
│   ├── etl_service.py
│   ├── monitor_service.py
│   └── health_check_service.py
├── jobs.py              # Definición de jobs
├── scheduler.py         # Configuración APScheduler
└── management/commands/
    └── run_scheduler.py
```

**Checklist:**
- [ ] APScheduler configurado
- [ ] 4 jobs programados
- [ ] Logging de jobs
- [ ] Retry automático
- [ ] Tests (>85% coverage)

**Tiempo:** 6-7 días

---

<a name="fase-7"></a>
## FASE 7: REPORTS (Semanas 13-14)

### 7.1 Report Generators

**Tareas:**
1. Crear modelos:
   - Report
   - ReportExecution
   - ReportTemplate

2. Crear generators:
   - QuarterlySummaryReport
   - TransferAnalysisReport
   - AbandonedCallsReport
   - ClientActivityReport
   - CustomReport

3. Crear exporters:
   - ExcelExporter (openpyxl)
   - CSVExporter (pandas)
   - PDFExporter (reportlab)

**Estructura:**
```
apps/reports/
├── models.py            # Report, ReportExecution, ReportTemplate
├── generators/
│   ├── base_generator.py
│   ├── quarterly_summary.py
│   ├── transfer_analysis.py
│   ├── abandoned_calls.py
│   ├── client_activity.py
│   └── custom_report.py
├── exporters/
│   ├── excel_exporter.py
│   ├── csv_exporter.py
│   └── pdf_exporter.py
├── services/
│   ├── report_generator_service.py
│   ├── export_service.py
│   └── query_builder_service.py
├── serializers.py       # 6 serializers
├── views.py             # 2 ViewSets
└── urls.py
```

**CNST-007:** Export máximo 100K filas.

**Checklist:**
- [ ] 5 tipos de reportes
- [ ] 3 formatos export
- [ ] Limit 100K rows
- [ ] Cache de reportes
- [ ] File cleanup job
- [ ] Tests (>90% coverage)

**Tiempo:** 7-8 días

---

### 7.2 Report API

**Endpoints (15):**
```
Reports (5):
  GET  /api/v1/reports/
  GET  /api/v1/reports/{id}/
  POST /api/v1/reports/generate/
  GET  /api/v1/reports/stats/
  GET  /api/v1/reports/my-reports/

Templates (7):
  GET    /api/v1/report-templates/
  POST   /api/v1/report-templates/
  GET    /api/v1/report-templates/{id}/
  PUT    /api/v1/report-templates/{id}/
  DELETE /api/v1/report-templates/{id}/
  POST   /api/v1/report-templates/{id}/generate/
```

**Checklist:**
- [ ] 15 endpoints implementados
- [ ] Async generation (si >10s)
- [ ] Download links
- [ ] RBAC en endpoints
- [ ] Tests API (>85% coverage)

**Tiempo:** 5-6 días

---

<a name="fase-8"></a>
## FASE 8: DASHBOARD & ALERTS (Semanas 15-16)

### 8.1 apps/dashboard/

**Tareas:**
1. Crear modelos:
   - DashboardConfig
   - WidgetConfig
   - SavedFilter

2. Crear services:
   - DashboardService
   - WidgetService
   - MetricsService

3. Crear widgets:
   - CallsChartWidget
   - TransfersWidget
   - AbandonmentsWidget
   - Top5ClientsWidget

**Estructura:**
```
apps/dashboard/
├── models.py            # DashboardConfig, WidgetConfig
├── services/
│   ├── dashboard_service.py
│   ├── widget_service.py
│   └── metrics_service.py
├── widgets/
│   ├── calls_chart.py
│   ├── transfers.py
│   └── abandonments.py
├── serializers.py       # 4 serializers
├── views.py             # 2 ViewSets
└── urls.py
```

**Checklist:**
- [ ] 3 modelos
- [ ] 3 services
- [ ] 4 widgets
- [ ] API REST (10 endpoints)
- [ ] Tests (>85% coverage)

**Tiempo:** 6-7 días

---

### 8.2 apps/alerts/

**Tareas:**
1. Crear modelos:
   - AlertRule
   - Alert
   - AlertNotification

2. Crear services:
   - AlertService
   - RuleEvaluatorService
   - NotificationService

3. Crear types:
   - THRESHOLD
   - TREND
   - ANOMALY

**Estructura:**
```
apps/alerts/
├── models.py            # AlertRule, Alert, AlertNotification
├── services/
│   ├── alert_service.py
│   ├── rule_evaluator_service.py
│   └── notification_service.py
├── evaluators/
│   ├── threshold_evaluator.py
│   ├── trend_evaluator.py
│   └── anomaly_evaluator.py
├── notifiers/
│   └── email_notifier.py
├── serializers.py       # 5 serializers
├── views.py             # 3 ViewSets
└── urls.py
```

**Checklist:**
- [ ] 3 modelos
- [ ] 3 services
- [ ] 3 evaluators
- [ ] Email notifications
- [ ] API REST (13 endpoints)
- [ ] Tests (>85% coverage)

**Tiempo:** 6-7 días

---

<a name="fase-9"></a>
## FASE 9: TESTING & QA (Semana 17)

### 9.1 Testing Completo

**Tareas:**
1. Completar tests unitarios (unit/)
2. Crear tests integración (integration/)
3. Crear tests API (api/)
4. Crear tests E2E (e2e/)
5. Alcanzar >85% coverage

**Estructura:**
```
tests/
├── unit/               # 300+ tests
│   ├── access/        # 50 tests
│   ├── users/         # 30 tests
│   ├── reports/       # 57 tests
│   └── ...
├── integration/        # 50+ tests
│   ├── test_auth_flow.py
│   ├── test_rbac_flow.py
│   └── test_etl_pipeline.py
├── api/                # 100+ tests
│   ├── test_access_api.py
│   ├── test_reports_api.py
│   └── ...
└── e2e/                # 10+ tests
    └── test_user_journey.py
```

**Checklist:**
- [ ] >85% coverage total
- [ ] Todos los endpoints testeados
- [ ] Tests integración pasando
- [ ] Tests E2E pasando
- [ ] CI/CD configurado

**Tiempo:** 7-10 días

---

### 9.2 Code Quality

**Tareas:**
1. Aplicar CLEAN_CODE v3.0.1
2. Refactorizar nombres
3. Eliminar code smells
4. Optimizar queries N+1

**Tools:**
- pylint
- flake8
- black (formatter)
- isort (imports)
- bandit (security)

**Checklist:**
- [ ] pylint score >8.5
- [ ] flake8 sin errores
- [ ] black aplicado
- [ ] isort aplicado
- [ ] bandit sin issues críticos

**Tiempo:** 5-7 días

---

<a name="fase-10"></a>
## FASE 10: DEPLOYMENT (Semana 18)

### 10.1 Pre-Deployment

**Tareas:**
1. Crear migrations finales
2. Crear fixtures producción
3. Configurar entorno producción
4. Crear scripts deployment
5. Configurar monitoring

**Checklist:**
- [ ] Migrations probadas en staging
- [ ] Fixtures cargados
- [ ] Settings producción OK
- [ ] Scripts deployment listos
- [ ] Monitoring configurado

**Tiempo:** 3-4 días

---

### 10.2 Deployment Staging

**Tareas:**
1. Deploy a staging
2. Smoke tests
3. Performance tests
4. Security audit
5. UAT (User Acceptance Testing)

**Checklist:**
- [ ] Deploy exitoso
- [ ] Smoke tests pasando
- [ ] Performance OK
- [ ] Security OK
- [ ] UAT aprobado

**Tiempo:** 4-5 días

---

### 10.3 Deployment Producción

**Tareas:**
1. Backup BD producción
2. Deploy zero-downtime
3. Migrate BD
4. Smoke tests producción
5. Rollback plan ready

**Checklist:**
- [ ] Backup completo
- [ ] Deploy exitoso
- [ ] Migrations OK
- [ ] Smoke tests OK
- [ ] Rollback plan tested

**Tiempo:** 2-3 días

---

## 📊 CRONOGRAMA CONSOLIDADO

```
Semana 1:  Fase 0 - Análisis Estado Actual
Semana 2:  Fase 1 - Fundamentos
Semanas 3-4:  Fase 2 - Core & Utils
Semanas 5-6:  Fase 3 - Auth & Users
Semanas 7-9:  Fase 4 - Access (RBAC) ⭐ CRÍTICO
Semana 10: Fase 5 - Audit
Semanas 11-12: Fase 6 - IVR & Pipeline
Semanas 13-14: Fase 7 - Reports
Semanas 15-16: Fase 8 - Dashboard & Alerts
Semana 17: Fase 9 - Testing & QA
Semana 18: Fase 10 - Deployment

TOTAL: 18 semanas (~4.5 meses)
```

---

## 🎯 PRIORIZACIÓN

### P0 (CRÍTICO - Primero):
1. Fundamentos (Semana 2)
2. Core & Utils (Semanas 3-4)
3. Access/RBAC (Semanas 7-9) ⭐ **MÁS IMPORTANTE**
4. Authentication (Semanas 5-6)

### P1 (ALTO - Segundo):
5. Users (Semanas 5-6)
6. Audit (Semana 10)
7. IVR (Semanas 11-12)

### P2 (MEDIO - Tercero):
8. Pipeline (Semanas 11-12)
9. Reports (Semanas 13-14)

### P3 (BAJO - Último):
10. Dashboard (Semanas 15-16)
11. Alerts (Semanas 15-16)

---

## ⚠️ RIESGOS Y MITIGACIÓN

### Riesgo 1: Dual Database Complejo
**Probabilidad:** ALTA  
**Impacto:** ALTO  
**Mitigación:**
- Probar Database Router extensivamente
- Tests específicos de readonly
- Monitoring de queries

### Riesgo 2: Migración RBAC Complejo
**Probabilidad:** MEDIA  
**Impacto:** CRÍTICO  
**Mitigación:**
- Plan de migración detallado
- Staging environment
- Rollback plan

### Riesgo 3: Performance Queries
**Probabilidad:** MEDIA  
**Impacto:** ALTO  
**Mitigación:**
- Optimizar queries desde inicio
- Profiling frecuente
- Índices BD correctos

### Riesgo 4: Testing Incompleto
**Probabilidad:** MEDIA  
**Impacto:** ALTO  
**Mitigación:**
- Coverage >85% obligatorio
- CI/CD automático
- Code review estricto

---

## ✅ CHECKLIST MAESTRO

```yaml
Análisis:
  ✅ 43 partes completadas
  ✅ 11 módulos analizados
  ✅ Clean Code v3.0.1 definido

Fundamentos:
  [ ] Settings configurados
  [ ] Dual DB funcionando
  [ ] Tests infrastructure OK

Core Modules:
  [ ] apps/core/ completo (SOLO abstract)
  [ ] apps/utils/ completo (SOLO funciones)
  [ ] apps/users/ completo
  [ ] apps/authentication/ completo

RBAC (CRÍTICO):
  [ ] apps/access/ completo
  [ ] 57 funciones cargadas
  [ ] Roles predefinidos
  [ ] Permissions funcionando

Data & ETL:
  [ ] apps/ivr/ completo (readonly)
  [ ] apps/pipeline/ completo
  [ ] APScheduler configurado

Reports & Viz:
  [ ] apps/reports/ completo
  [ ] apps/dashboard/ completo
  [ ] apps/alerts/ completo

Audit:
  [ ] apps/audit/ completo
  [ ] Middleware funcionando
  [ ] Logs immutables

Testing:
  [ ] 452+ tests escritos
  [ ] >85% coverage
  [ ] CI/CD configurado

Deployment:
  [ ] Staging OK
  [ ] Producción OK
  [ ] Monitoring activo
```

---

## 📚 RECURSOS NECESARIOS

### Equipo:
- 1-2 Senior Django Developers
- 1 Frontend Developer (si hay UI)
- 1 QA Engineer
- 1 DevOps Engineer

### Herramientas:
- GitHub/GitLab
- Jira/Trello
- Slack/Discord
- Sentry (monitoring)
- New Relic (APM)

### Ambientes:
- Development (local)
- Staging
- Production

---

**FIN DEL PLAN DE IMPLEMENTACIÓN**

**Próximos pasos:**
1. Revisar y aprobar este plan
2. Asignar recursos
3. Iniciar Fase 0 (Análisis Estado Actual)

**Tiempo total estimado:** 18 semanas (4.5 meses)  
**Complejidad:** ALTA  
**Riesgo:** MEDIO-ALTO  
**Prioridad:** apps/access/ (RBAC) es CRÍTICA
