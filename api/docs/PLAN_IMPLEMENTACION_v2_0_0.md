---
version: 2.0.0
date: 2026-01-20
project: IACT Call Center System
type: Plan de Implementación
categoria: implementacion
tema: Plan v2.0.0 - SQLite, Factories, Mocks y Service Layer
autor: Claude Technical Analysis
tags: [implementacion, plan, sqlite, factories, mocks, service-layer]
replaces: PLAN_IMPLEMENTACION_COMPLETO_v1_0_0.md
estado: plan
---

# PLAN DE IMPLEMENTACIÓN v2.0.0 - IACT
## CON SQLITE, FACTORIES, MOCKS Y SERVICE LAYER

**CAMBIOS CRÍTICOS desde v1.0.0:**
```yaml
✅ SQLite para desarrollo/tests (NO MySQL/PostgreSQL IPs)
✅ Factories completas (factory_boy) para TODAS las apps
✅ Mocks para BD externas, servicios, archivos
✅ Service Layer Pattern desde el inicio
✅ TDD approach (tests primero)
✅ Implementación incremental validada con tests
```

---

## 📊 CONTEXTO REAL DEL PROYECTO

```yaml
Base de Datos:
  Desarrollo: SQLite (NO tenemos IPs de MySQL/PostgreSQL)
  Tests: SQLite en memoria
  Producción: PostgreSQL + MariaDB (IVR readonly)

Testing Actual:
  ✅ tests/factories/ (factory_boy) - PARCIAL
  ✅ tests/fixtures/ (pytest) - PARCIAL
  ✅ tests/unit/ - Por app
  ✅ tests/integration/ - Multi-app
  ✅ tests/api/ - Endpoints REST
  ✅ 294 tests colectados, 291 OK

Arquitectura:
  ✅ Service Layer Pattern (lógica en services)
  ✅ Models = solo estructura
  ✅ Services = lógica de negocio
  ✅ Mocks para servicios externos

Estado Actual:
  ✅ Análisis completo (43 partes, 11 apps)
  ✅ Fixtures básicas creadas
  ⏳ Factories incompletas (solo users, partial access)
  ⏳ Mocks incompletos
  ⏳ Service layer parcial
```

---

## 🎯 OBJETIVOS DEL PLAN v2.0.0

1. **Completar infrastructure de testing** (factories + mocks)
2. **Implementar Service Layer completo** para todas las apps
3. **Desarrollar con SQLite**, deploy con PostgreSQL
4. **TDD approach**: Tests primero, luego implementación
5. **>85% coverage** en cada fase

---

## 📋 NUEVO CRONOGRAMA (14 SEMANAS)

```
Semana 1-2:   FASE 1 - Testing Infrastructure ⭐
Semana 3:     FASE 2 - Core & Utils
Semana 4:     FASE 3 - Authentication
Semanas 5-7:  FASE 4 - Access (RBAC) 🔴 CRÍTICO
Semana 8:     FASE 5 - Users & Audit
Semanas 9-10: FASE 6 - IVR & Pipeline
Semanas 11-12: FASE 7 - Reports
Semana 13:    FASE 8 - Dashboard & Alerts
Semana 14:    FASE 9 - QA & Deployment

TOTAL: 14 semanas (~3.5 meses)
```

---

## FASE 1: TESTING INFRASTRUCTURE (Semanas 1-2)

**Objetivo:** Completar toda la infraestructura de testing ANTES de implementar apps.

### Semana 1: Factories Completas

**Día 1-2: Factories Base**
```bash
tests/factories/
├── __init__.py                    # ✅ Ya existe
├── user_factory.py               # ✅ Ya existe
├── access_factories.py           # ⏳ CREAR
├── audit_factories.py            # ⏳ CREAR
├── ivr_factories.py              # ⏳ CREAR
├── pipeline_factories.py         # ⏳ CREAR
├── report_factories.py           # ⏳ CREAR
├── dashboard_factories.py        # ⏳ CREAR
└── alert_factories.py            # ⏳ CREAR
```

**Tareas:**
1. Crear AccessFactories (Module, Function, Role, UserModuleAccess, UserFunctionAssignment)
2. Crear AuditFactories (AuditLog, SessionLog)
3. Crear IVRFactories (QuarterlyReport, TransferReport, AbandonedReport, etc)
4. Crear PipelineFactories (ETLJob, ETLError, SchedulerConfig)
5. Crear ReportFactories (Report, ReportExecution, ReportTemplate)
6. Crear DashboardFactories (DashboardConfig, WidgetConfig)
7. Crear AlertFactories (AlertRule, Alert, AlertNotification)

**Deliverables:**
- [ ] 8 archivos de factories (50+ factories totales)
- [ ] Tests de factories (`test_factories.py`)
- [ ] Documentación de uso

**Checklist:**
```yaml
Factories Access (5):
  [ ] ModuleFactory
  [ ] FunctionFactory
  [ ] RoleFactory
  [ ] UserModuleAccessFactory
  [ ] UserFunctionAssignmentFactory

Factories IVR (5):
  [ ] QuarterlyReportFactory
  [ ] TransferReportFactory
  [ ] AbandonedReportFactory
  [ ] ClientReportFactory
  [ ] CallRecordQ1Factory

Factories Reports (3):
  [ ] ReportFactory
  [ ] ReportExecutionFactory
  [ ] ReportTemplateFactory

Factories Pipeline (3):
  [ ] ETLJobFactory
  [ ] ETLErrorFactory
  [ ] SchedulerConfigFactory

Factories Dashboard (2):
  [ ] DashboardConfigFactory
  [ ] WidgetConfigFactory

Factories Alerts (3):
  [ ] AlertRuleFactory
  [ ] AlertFactory
  [ ] AlertNotificationFactory

Factories Audit (2):
  [ ] AuditLogFactory
  [ ] SessionLogFactory
```

**Tiempo:** 2-3 días

---

**Día 3-4: Mocks Completos**

```bash
tests/mocks/
├── __init__.py                   # ⏳ CREAR
├── database_mocks.py            # ⏳ CREAR
├── service_mocks.py             # ⏳ CREAR
├── file_mocks.py                # ⏳ CREAR
├── scheduler_mocks.py           # ⏳ CREAR
└── external_mocks.py            # ⏳ CREAR
```

**Tareas:**
1. Mock BD IVR (MariaDB → SQLite mock)
2. Mock PostgreSQL connection
3. Mock Database Router
4. Mock ETLService
5. Mock ReportGeneratorService
6. Mock AccessService (RBAC)
7. Mock ExcelExporter, CSVExporter, PDFExporter
8. Mock File Storage
9. Mock APScheduler
10. Mock Email backend

**Deliverables:**
- [ ] 5 archivos de mocks
- [ ] Tests de mocks
- [ ] Documentación de uso

**Checklist:**
```yaml
Database Mocks (3):
  [ ] mock_ivr_connection (MariaDB)
  [ ] mock_postgresql_connection
  [ ] mock_database_router (IVRRouter)

Service Mocks (4):
  [ ] mock_etl_service
  [ ] mock_report_generator_service
  [ ] mock_access_service (RBAC)
  [ ] mock_audit_service

File Mocks (4):
  [ ] mock_excel_exporter
  [ ] mock_csv_exporter
  [ ] mock_pdf_exporter
  [ ] mock_file_storage

External Mocks (3):
  [ ] mock_apscheduler
  [ ] mock_email_backend
  [ ] mock_cache
```

**Tiempo:** 2 días

---

**Día 5: Actualizar conftest.py**

**Tareas:**
1. Integrar todas las factories
2. Integrar todos los mocks
3. Actualizar pytest_plugins
4. Configurar SQLite para tests
5. Crear fixtures híbridas (factory + fixture)

**Archivo:** `tests/conftest.py`

```python
"""
conftest.py v2.0.0

Integra:
- Factories (50+)
- Mocks (14+)
- Fixtures pytest (60+)
- SQLite configuración
"""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Import ALL factories
from tests.factories import (
    UserFactory,
    AdminUserFactory,
    ModuleFactory,
    FunctionFactory,
    RoleFactory,
    ReportFactory,
    QuarterlyReportFactory,
    ETLJobFactory,
    AlertRuleFactory,
    # ... todos los demás
)

# Import pytest plugins
pytest_plugins = [
    'tests.fixtures.users',
    'tests.fixtures.rbac',
    'tests.mocks.database_mocks',
    'tests.mocks.service_mocks',
    'tests.mocks.file_mocks',
    'tests.mocks.scheduler_mocks',
    'tests.mocks.external_mocks',
]

# ============================================================================
# DATABASE CONFIGURATION (SQLite)
# ============================================================================

@pytest.fixture(scope='session')
def django_db_setup():
    """Configurar SQLite para tests."""
    from django.conf import settings
    
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
        'ivr_legacy': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }


# ============================================================================
# API CLIENTS
# ============================================================================

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(db):
    """Cliente autenticado usando factory."""
    user = UserFactory()
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def admin_client(db):
    """Cliente admin usando factory."""
    admin = AdminUserFactory()
    client = APIClient()
    refresh = RefreshToken.for_user(admin)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


# ============================================================================
# USERS (Hybrid: factory + fixture)
# ============================================================================

@pytest.fixture
def sample_user(db):
    """Usuario estándar usando factory."""
    return UserFactory(username='testuser', email='test@example.com')


@pytest.fixture
def sample_admin(db):
    """Admin usando factory."""
    return AdminUserFactory(username='admin', email='admin@example.com')


# ============================================================================
# ACCESS/RBAC (Hybrid)
# ============================================================================

@pytest.fixture
def sample_module(db):
    return ModuleFactory(module_id='MODULE_001', name='Test Module')


@pytest.fixture
def sample_function(db, sample_module):
    return FunctionFactory(
        function_id='test.function',
        name='Test Function',
        module=sample_module
    )


@pytest.fixture
def sample_role(db):
    return RoleFactory(role_id='ROLE_TEST', name='Test Role')


# ... más fixtures híbridas
```

**Checklist:**
- [ ] Imports de factories
- [ ] Imports de mocks
- [ ] pytest_plugins actualizado
- [ ] SQLite configurado
- [ ] Fixtures híbridas (60+)
- [ ] Tests de conftest.py

**Tiempo:** 1 día

---

### Semana 2: Tests Base y Validación

**Día 1-2: Tests de Infrastructure**

**Tareas:**
1. Tests de factories (`tests/unit/test_factories.py`)
2. Tests de mocks (`tests/unit/test_mocks.py`)
3. Tests de conftest.py
4. Verificar >90% coverage de infrastructure

**Tests:**
```python
# tests/unit/test_factories.py

import pytest
from tests.factories import UserFactory, ModuleFactory, ReportFactory


@pytest.mark.django_db
class TestFactories:
    """Validar que todas las factories funcionan."""
    
    def test_user_factory(self):
        user = UserFactory()
        assert user.username is not None
        assert user.email is not None
    
    def test_module_factory(self):
        module = ModuleFactory()
        assert module.module_id is not None
    
    def test_report_factory(self):
        report = ReportFactory()
        assert report.report_type is not None
    
    # ... tests para TODAS las factories
```

**Checklist:**
- [ ] 50+ tests de factories
- [ ] 14+ tests de mocks
- [ ] Tests de conftest.py
- [ ] >90% coverage infrastructure

**Tiempo:** 2 días

---

**Día 3-5: Documentation**

**Tareas:**
1. Documentar todas las factories
2. Documentar todos los mocks
3. Crear ejemplos de uso
4. Actualizar README.md de tests

**Deliverables:**
- [ ] FACTORY_GUIDE.md (guía factories)
- [ ] MOCK_GUIDE.md (guía mocks)
- [ ] TESTING_EXAMPLES.md (ejemplos)
- [ ] README.md actualizado

**Tiempo:** 3 días

---

### Resumen Fase 1

```yaml
Duración: 2 semanas (10 días hábiles)

Día 1-2:   Factories completas (8 archivos)
Día 3-4:   Mocks completos (5 archivos)
Día 5:     conftest.py actualizado
Día 6-7:   Tests infrastructure
Día 8-10:  Documentation

Deliverables:
  ✅ 50+ factories (8 archivos)
  ✅ 14+ mocks (5 archivos)
  ✅ conftest.py v2.0.0
  ✅ 64+ tests infrastructure
  ✅ Documentation completa
  ✅ >90% coverage infrastructure

Checklist Final:
  [ ] 50+ factories creadas y testeadas
  [ ] 14+ mocks creados y testeados
  [ ] conftest.py integrado
  [ ] SQLite configurado
  [ ] Tests pasando (>90% coverage)
  [ ] Documentation completa
```

---

## FASE 2: CORE & UTILS (Semana 3)

**Objetivo:** Implementar componentes base usando TDD.

### apps/core/ (3 días)

**CRÍTICO:** `apps/core/models.py` SOLO abstract=True.

**Día 1: Models + Tests**

**TDD Approach:**
1. Escribir tests primero
2. Implementar para pasar tests
3. Refactorizar

```python
# tests/unit/core/test_models.py (PRIMERO)

import pytest
from apps.core.models import TimeStampedModel, SoftDeleteMixin


@pytest.mark.django_db
class TestTimeStampedModel:
    """Tests para TimeStampedModel."""
    
    def test_auto_timestamps(self):
        """Test: created_at y updated_at se setean automáticamente."""
        # Este test FALLA porque model no existe aún
        # LUEGO implementamos model para pasar test
        pass
```

```python
# apps/core/models.py (DESPUÉS)

class TimeStampedModel(models.Model):
    """Modelo base con timestamps."""
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # ✅ OBLIGATORIO
```

**Tareas:**
- [ ] Tests de TimeStampedModel
- [ ] Tests de SoftDeleteMixin
- [ ] Tests de AuditedModel
- [ ] Implementar models para pasar tests
- [ ] Tests de SoftDeleteManager/QuerySet

**Checklist:**
```yaml
Abstract Models (5):
  [ ] TimeStampedModel + tests
  [ ] SoftDeleteMixin + tests
  [ ] SoftDeleteQuerySet + tests
  [ ] SoftDeleteManager + tests
  [ ] AuditedModel + tests

Verificación:
  [ ] TODOS con abstract=True
  [ ] NINGÚN db_table
  [ ] Tests pasando (>90% coverage)
```

**Tiempo:** 1 día

---

**Día 2: Exceptions, Validators + Tests**

```python
# tests/unit/core/test_exceptions.py (PRIMERO)

from apps.core.exceptions import ValidationError, PermissionDeniedError


def test_validation_error_with_field():
    """Test: ValidationError con field."""
    error = ValidationError(message="Invalid", field="email")
    assert error.field == "email"


# apps/core/exceptions.py (DESPUÉS)

class ValidationError(IACTBaseException):
    def __init__(self, message: str, field: str = None):
        self.field = field
        self.message = message
        super().__init__(message)
```

**Tareas:**
- [ ] Tests de 7 exceptions
- [ ] Implementar exceptions
- [ ] Tests de 3 validators (clases)
- [ ] Implementar validators

**Tiempo:** 1 día

---

**Día 3: Middleware, Permissions + Tests**

**Tareas:**
- [ ] Tests de RequestLoggingMiddleware
- [ ] Implementar middleware
- [ ] Tests de RequiresFunctionPermission (DRF)
- [ ] Implementar permissions
- [ ] Tests de mixins (SoftDeleteViewSetMixin, etc)
- [ ] Implementar mixins

**Tiempo:** 1 día

---

### apps/utils/ (2 días)

**CRÍTICO:** Solo funciones (NO clases, NO models.py).

**Día 1: Validators, Formatters + Tests**

```python
# tests/unit/utils/test_validators.py (PRIMERO)

from apps.utils.validators import validate_phone_cl, validate_rut


def test_validate_phone_cl_valid():
    """Test: Teléfono válido."""
    assert validate_phone_cl('+56912345678') is True


def test_validate_phone_cl_invalid():
    """Test: Teléfono inválido."""
    assert validate_phone_cl('123') is False
```

**Tareas:**
- [ ] Tests de 6 validators (funciones)
- [ ] Implementar validators
- [ ] Tests de 8 formatters
- [ ] Implementar formatters

**Tiempo:** 1 día

---

**Día 2: Date Utils, Decorators + Tests**

**Tareas:**
- [ ] Tests de date_utils (10 funciones)
- [ ] Implementar date_utils
- [ ] Tests de decorators (@cache_result, @retry_on_failure)
- [ ] Implementar decorators

**Tiempo:** 1 día

---

### Resumen Fase 2

```yaml
Duración: 1 semana (5 días)

apps/core/ (3 días):
  Día 1: Abstract Models + Tests
  Día 2: Exceptions, Validators + Tests
  Día 3: Middleware, Permissions + Tests

apps/utils/ (2 días):
  Día 4: Validators, Formatters + Tests
  Día 5: Date Utils, Decorators + Tests

Deliverables:
  ✅ apps/core/ completo (SOLO abstract)
  ✅ apps/utils/ completo (SOLO funciones)
  ✅ 25+ tests core/
  ✅ 40+ tests utils/
  ✅ >90% coverage

Checklist:
  [ ] core/models.py SOLO abstract=True
  [ ] utils/ SOLO funciones (NO models.py)
  [ ] 7 exceptions
  [ ] 3 validators (clases)
  [ ] 4 middleware
  [ ] 5 mixins
  [ ] 6 validators (funciones)
  [ ] 8 formatters
  [ ] 10 date utils
  [ ] Tests pasando (>90%)
```

---

## FASE 3: AUTHENTICATION (Semana 4)

**Objetivo:** Sistema de autenticación con JWT.

### apps/authentication/ (5 días)

**Día 1: Models + Tests**

**TDD:**
```python
# tests/unit/authentication/test_services.py (PRIMERO)

from apps.authentication.services import AuthenticationService
from tests.factories import UserFactory


@pytest.mark.django_db
def test_login_success():
    """Test: Login exitoso retorna tokens."""
    user = UserFactory(username='test', password='pass123')
    
    tokens = AuthenticationService.login(
        username='test',
        password='pass123'
    )
    
    assert 'access' in tokens
    assert 'refresh' in tokens
```

**Tareas:**
- [ ] Tests de AuthenticationService
- [ ] Implementar AuthenticationService
- [ ] Tests de SessionService
- [ ] Implementar SessionService

**Tiempo:** 1 día

---

**Día 2-3: API + Tests**

**Tareas:**
- [ ] Tests de LoginView
- [ ] Implementar LoginView
- [ ] Tests de LogoutView
- [ ] Implementar LogoutView
- [ ] Tests de RefreshTokenView
- [ ] Implementar RefreshTokenView

**Endpoints:**
```yaml
POST /api/v1/auth/login/
POST /api/v1/auth/logout/
POST /api/v1/auth/refresh/
POST /api/v1/auth/password-change/
```

**Tiempo:** 2 días

---

**Día 4-5: Integration Tests + JWT Config**

**Tareas:**
- [ ] Configurar JWT (rest_framework_simplejwt)
- [ ] Tests de integración (login → obtener módulos)
- [ ] Tests de sessions DB (CNST-010)
- [ ] Performance tests (login <100ms)

**Tiempo:** 2 días

---

### Resumen Fase 3

```yaml
Duración: 1 semana (5 días)

apps/authentication/:
  Día 1:   Models + Services + Tests
  Día 2-3: API Views + Tests
  Día 4-5: Integration + JWT Config

Deliverables:
  ✅ AuthenticationService
  ✅ SessionService
  ✅ 4 endpoints REST
  ✅ JWT configurado
  ✅ 20+ tests
  ✅ >85% coverage

Endpoints:
  [ ] POST /api/v1/auth/login/
  [ ] POST /api/v1/auth/logout/
  [ ] POST /api/v1/auth/refresh/
  [ ] POST /api/v1/auth/password-change/

Checklist:
  [ ] JWT funcionando
  [ ] Sessions DB configurado
  [ ] Tests de integración
  [ ] Performance tests
  [ ] >85% coverage
```

---

## FASE 4: ACCESS (RBAC) 🔴 CRÍTICO (Semanas 5-7)

**Objetivo:** Sistema completo de RBAC (CORE del sistema).

### Semana 5: Models + Services

**Día 1-2: Models + Tests**

**TDD:**
```python
# tests/unit/access/test_models.py (PRIMERO)

from tests.factories import ModuleFactory, FunctionFactory


@pytest.mark.django_db
def test_module_hierarchy():
    """Test: Jerarquía de módulos."""
    parent = ModuleFactory(name='Parent')
    child = ModuleFactory(name='Child', parent=parent)
    
    assert child.parent == parent
    assert parent in child.get_ancestors()
```

**Tareas:**
- [ ] Tests de Module (jerarquía, soft delete)
- [ ] Implementar Module
- [ ] Tests de Function (unique constraints)
- [ ] Implementar Function
- [ ] Tests de Role
- [ ] Implementar Role
- [ ] Tests de UserModuleAccess
- [ ] Tests de UserFunctionAssignment
- [ ] Tests de UserRoleAssignment

**Tiempo:** 2 días

---

**Día 3-5: Services + Tests**

**TDD:**
```python
# tests/unit/access/test_services.py (PRIMERO)

from apps.access.services import AccessService
from tests.factories import UserFactory, FunctionFactory


@pytest.mark.django_db
def test_user_has_function():
    """Test: Verificar si usuario tiene función."""
    user = UserFactory()
    function = FunctionFactory(function_id='test.function')
    
    # Sin asignar
    assert AccessService.user_has_function(user, 'test.function') is False
    
    # Asignar
    UserFunctionAssignmentFactory(user=user, function=function)
    
    # Con asignación
    assert AccessService.user_has_function(user, 'test.function') is True
```

**Tareas:**
- [ ] Tests de ModuleService
- [ ] Implementar ModuleService
- [ ] Tests de FunctionService
- [ ] Implementar FunctionService
- [ ] Tests de RoleService
- [ ] Implementar RoleService
- [ ] Tests de AccessService (central)
- [ ] Implementar AccessService

**Tiempo:** 3 días

---

### Semana 6: API REST

**Día 1-3: Endpoints + Tests**

**17 endpoints:**
```yaml
Modules (5):
  [ ] GET  /api/v1/access/modules/
  [ ] POST /api/v1/access/modules/
  [ ] GET  /api/v1/access/modules/{id}/
  [ ] GET  /api/v1/access/my-modules/
  [ ] GET  /api/v1/access/module-tree/

Functions (7):
  [ ] GET    /api/v1/access/functions/
  [ ] POST   /api/v1/access/functions/
  [ ] GET    /api/v1/access/functions/{id}/
  [ ] PUT    /api/v1/access/functions/{id}/
  [ ] DELETE /api/v1/access/functions/{id}/
  [ ] GET    /api/v1/access/my-functions/
  [ ] POST   /api/v1/access/check-function/

Roles (5):
  [ ] GET  /api/v1/access/roles/
  [ ] POST /api/v1/access/roles/
  [ ] GET  /api/v1/access/roles/{id}/
  [ ] GET  /api/v1/access/my-roles/
  [ ] POST /api/v1/access/assign-role/
```

**TDD:**
```python
# tests/api/test_access_api.py (PRIMERO)

@pytest.mark.django_db
def test_my_modules_endpoint(authenticated_client):
    """Test: Obtener módulos del usuario."""
    # Arrange
    user = authenticated_client.user
    module = ModuleFactory()
    UserModuleAccessFactory(user=user, module=module)
    
    # Act
    response = authenticated_client.get('/api/v1/access/my-modules/')
    
    # Assert
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['module_id'] == module.module_id
```

**Tiempo:** 3 días

---

**Día 4-5: Integration Tests**

**Tareas:**
- [ ] Test: Login → Obtener módulos → Verificar función
- [ ] Test: Asignar rol → Usuario hereda funciones
- [ ] Test: RBAC en endpoint (permission denied)
- [ ] Performance tests (verificación RBAC <50ms)

**Tiempo:** 2 días

---

### Semana 7: Fixtures y Docs

**Día 1-3: Fixtures Iniciales**

**57 funciones RBAC:**
```python
# apps/access/fixtures/functions.json

[
  {
    "function_id": "dashboard.view",
    "name": "Ver Dashboard",
    "module": "MODULE_DASHBOARD"
  },
  {
    "function_id": "reports.create",
    "name": "Crear Reportes",
    "module": "MODULE_REPORTS"
  },
  # ... 55 más
]
```

**Tareas:**
- [ ] Crear 57 funciones documentadas
- [ ] Crear módulos base (11 módulos)
- [ ] Crear roles predefinidos (4 roles)
- [ ] Tests de fixtures (loaddata)

**Tiempo:** 3 días

---

**Día 4-5: Documentation**

**Tareas:**
- [ ] RBAC_GUIDE.md (guía completa RBAC)
- [ ] FUNCTION_REFERENCE.md (57 funciones)
- [ ] API_REFERENCE.md (17 endpoints)
- [ ] Integration examples

**Tiempo:** 2 días

---

### Resumen Fase 4

```yaml
Duración: 3 semanas (15 días)

Semana 5: Models + Services
  Día 1-2:   Models + Tests
  Día 3-5:   Services + Tests

Semana 6: API REST
  Día 1-3:   17 endpoints + Tests
  Día 4-5:   Integration Tests

Semana 7: Fixtures + Docs
  Día 1-3:   57 funciones, módulos, roles
  Día 4-5:   Documentation completa

Deliverables:
  ✅ 7 modelos RBAC
  ✅ 4 services
  ✅ 17 endpoints REST
  ✅ 57 funciones documentadas
  ✅ 4 roles predefinidos
  ✅ 50+ tests
  ✅ >90% coverage
  ✅ Documentation completa

Checklist Final:
  [ ] Module hierarchy funcionando
  [ ] Function assignment funcionando
  [ ] Role-based access funcionando
  [ ] 17 endpoints REST
  [ ] 57 funciones cargadas
  [ ] Roles predefinidos (ADMIN, MANAGER, ANALYST, VIEWER)
  [ ] Tests de integración
  [ ] Performance <50ms
  [ ] >90% coverage
```

---

## FASE 5: USERS & AUDIT (Semana 8)

### apps/users/ (2.5 días)

**TDD:**
```python
# tests/unit/users/test_services.py

from apps.users.services import UserService
from tests.factories import UserFactory


@pytest.mark.django_db
def test_create_user_service():
    """Test: Crear usuario con service."""
    user_data = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'pass123'
    }
    
    user = UserService.create_user(user_data)
    
    assert user.username == 'newuser'
    assert user.check_password('pass123')
```

**Tareas:**
- [ ] Tests de UserService
- [ ] Implementar UserService
- [ ] Tests de UserViewSet (6 endpoints)
- [ ] Implementar ViewSet
- [ ] Tests API

**Endpoints:**
```yaml
[ ] GET    /api/v1/users/
[ ] POST   /api/v1/users/
[ ] GET    /api/v1/users/{id}/
[ ] PUT    /api/v1/users/{id}/
[ ] DELETE /api/v1/users/{id}/
[ ] GET    /api/v1/users/me/
```

**Tiempo:** 2.5 días

---

### apps/audit/ (2.5 días)

**CNST-031:** Auditoría completa.

**TDD:**
```python
# tests/unit/audit/test_middleware.py

from apps.audit.middleware import AuditMiddleware


@pytest.mark.django_db
def test_audit_middleware_logs_request(rf, sample_user):
    """Test: Middleware loggea request."""
    request = rf.get('/api/v1/test/')
    request.user = sample_user
    
    middleware = AuditMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    
    # Verificar log creado
    from apps.audit.models import AuditLog
    assert AuditLog.objects.filter(user=sample_user).exists()
```

**Tareas:**
- [ ] Tests de AuditLog (immutable)
- [ ] Implementar AuditLog
- [ ] Tests de AuditMiddleware
- [ ] Implementar middleware
- [ ] Tests de @audit_action decorator
- [ ] Implementar decorator

**Tiempo:** 2.5 días

---

### Resumen Fase 5

```yaml
Duración: 1 semana (5 días)

apps/users/ (2.5 días):
  ✅ UserService
  ✅ 6 endpoints REST
  ✅ 20+ tests

apps/audit/ (2.5 días):
  ✅ AuditLog (immutable)
  ✅ AuditMiddleware
  ✅ @audit_action decorator
  ✅ 15+ tests

Checklist:
  [ ] UserService funcionando
  [ ] 6 endpoints users
  [ ] AuditLog immutable
  [ ] Middleware captura requests
  [ ] Decorator @audit_action
  [ ] >85% coverage
```

---

## FASE 6: IVR & PIPELINE (Semanas 9-10)

### Semana 9: apps/ivr/ (BD Readonly)

**CRÍTICO:** IVR usa MariaDB en prod, SQLite en tests.

**Día 1-2: Database Router + Tests**

```python
# tests/unit/ivr/test_router.py

from apps.ivr.routers import IVRRouter
from apps.ivr.models import QuarterlyReport


def test_router_read_ivr_legacy():
    """Test: Router usa 'ivr_legacy' para read."""
    router = IVRRouter()
    
    db = router.db_for_read(QuarterlyReport)
    assert db == 'ivr_legacy'


def test_router_write_returns_none():
    """Test: Router prohíbe writes en IVR."""
    router = IVRRouter()
    
    db = router.db_for_write(QuarterlyReport)
    assert db is None  # ✅ Readonly
```

**Tareas:**
- [ ] Tests de IVRRouter
- [ ] Implementar IVRRouter
- [ ] Tests de models readonly
- [ ] Implementar 11 models ETL

**Tiempo:** 2 días

---

**Día 3-5: Mocks + Integration**

**TDD:**
```python
# tests/unit/ivr/test_queries.py

from apps.ivr.models import QuarterlyReport


@pytest.mark.django_db
def test_query_quarterly_report_with_mock(mock_ivr_connection):
    """Test: Query con BD IVR mockeada."""
    # BD IVR retorna datos mock
    data = QuarterlyReport.objects.filter(year=2025, quarter=1)
    
    assert len(data) > 0
```

**Tareas:**
- [ ] Tests con mock_ivr_connection
- [ ] Verificar SOLO queries SELECT
- [ ] Tests de performance (<200ms)
- [ ] Integration con pipeline

**Tiempo:** 3 días

---

### Semana 10: apps/pipeline/ (APScheduler)

**CNST-013:** APScheduler (NO Celery).

**Día 1-3: ETL Service + Tests**

```python
# tests/unit/pipeline/test_services.py

from apps.pipeline.services import ETLService
from tests.factories import ETLJobFactory


@pytest.mark.django_db
def test_extract_quarterly_data_with_mock(mock_etl_service):
    """Test: ETL con service mockeado."""
    mock_etl_service.extract_quarterly_data.return_value = [
        {'year': 2025, 'quarter': 1, 'total_calls': 10000}
    ]
    
    job = ETLService.run_quarterly_etl(year=2025, quarter=1)
    
    assert job.status == 'SUCCESS'
    assert job.records_processed > 0
```

**Tareas:**
- [ ] Tests de ETLService
- [ ] Implementar ETLService
- [ ] Tests de MonitorService
- [ ] Implementar MonitorService
- [ ] Tests de HealthCheckService

**Tiempo:** 3 días

---

**Día 4-5: APScheduler + Jobs**

```python
# apps/pipeline/jobs.py

from apscheduler.schedulers.background import BackgroundScheduler


def setup_scheduler():
    """Configurar jobs APScheduler."""
    scheduler = BackgroundScheduler()
    
    # Cleanup sessions (diario 3:00 AM)
    scheduler.add_job(
        cleanup_sessions,
        'cron',
        hour=3,
        id='cleanup_sessions'
    )
    
    # ETL monitor (cada 6h)
    scheduler.add_job(
        etl_monitor,
        'interval',
        hours=6,
        id='etl_monitor'
    )
    
    scheduler.start()
    return scheduler
```

**Tareas:**
- [ ] Configurar APScheduler
- [ ] Tests de jobs con mock_apscheduler
- [ ] 4 jobs programados
- [ ] Tests de retry automático

**Tiempo:** 2 días

---

### Resumen Fase 6

```yaml
Duración: 2 semanas (10 días)

Semana 9: apps/ivr/
  Día 1-2:   Router + Tests
  Día 3-5:   Mocks + Integration

Semana 10: apps/pipeline/
  Día 1-3:   ETL Service + Tests
  Día 4-5:   APScheduler + Jobs

Deliverables:
  ✅ IVRRouter (readonly)
  ✅ 11 models ETL
  ✅ ETLService
  ✅ MonitorService
  ✅ APScheduler configurado
  ✅ 4 jobs programados
  ✅ 30+ tests
  ✅ >85% coverage

Checklist:
  [ ] IVR readonly funcionando
  [ ] Mocks BD IVR
  [ ] ETL Service
  [ ] APScheduler configurado
  [ ] Jobs funcionando
  [ ] Retry automático
  [ ] >85% coverage
```

---

## FASE 7: REPORTS (Semanas 11-12)

### Semana 11: Generators + Exporters

**Día 1-3: Report Generators + Tests**

```python
# tests/unit/reports/test_generators.py

from apps.reports.generators import QuarterlySummaryReport
from tests.factories import QuarterlyReportFactory


@pytest.mark.django_db
def test_quarterly_summary_generator(mock_etl_service):
    """Test: Generar reporte trimestral con mock."""
    # Mock datos IVR
    mock_etl_service.extract_quarterly_data.return_value = [
        {'year': 2025, 'quarter': 1, 'total_calls': 10000}
    ]
    
    generator = QuarterlySummaryReport(year=2025, quarter=1)
    data = generator.generate()
    
    assert len(data) > 0
    assert data[0]['total_calls'] == 10000
```

**Tareas:**
- [ ] Tests de QuarterlySummaryReport
- [ ] Implementar QuarterlySummaryReport
- [ ] Tests de TransferAnalysisReport
- [ ] Tests de AbandonedCallsReport
- [ ] Tests de ClientActivityReport
- [ ] Implementar 4 generadores

**Tiempo:** 3 días

---

**Día 4-5: Exporters + Tests**

```python
# tests/unit/reports/test_exporters.py

from apps.reports.exporters import ExcelExporter


def test_excel_exporter_with_mock(mock_excel_exporter, tmp_path):
    """Test: Export Excel con mock."""
    data = [
        {'year': 2025, 'quarter': 1, 'calls': 10000}
    ]
    
    mock_excel_exporter.export.return_value = str(tmp_path / 'test.xlsx')
    
    exporter = ExcelExporter()
    file_path = exporter.export(data)
    
    assert file_path.endswith('.xlsx')
    mock_excel_exporter.export.assert_called_once()
```

**Tareas:**
- [ ] Tests de ExcelExporter
- [ ] Implementar ExcelExporter
- [ ] Tests de CSVExporter
- [ ] Tests de PDFExporter
- [ ] Implementar 3 exporters

**Tiempo:** 2 días

---

### Semana 12: API + Services

**Día 1-3: Report API + Tests**

**15 endpoints:**
```yaml
Reports (5):
  [ ] GET  /api/v1/reports/
  [ ] POST /api/v1/reports/generate/
  [ ] GET  /api/v1/reports/{id}/
  [ ] GET  /api/v1/reports/stats/
  [ ] GET  /api/v1/reports/my-reports/

Templates (10):
  [ ] GET    /api/v1/report-templates/
  [ ] POST   /api/v1/report-templates/
  [ ] GET    /api/v1/report-templates/{id}/
  [ ] PUT    /api/v1/report-templates/{id}/
  [ ] DELETE /api/v1/report-templates/{id}/
  [ ] POST   /api/v1/report-templates/{id}/generate/
  # ... más endpoints
```

**Tiempo:** 3 días

---

**Día 4-5: Integration + Limits**

**CNST-007:** Export máximo 100K rows.

**Tareas:**
- [ ] Test limit 100K rows
- [ ] Test cache reportes
- [ ] Test file cleanup job
- [ ] Integration tests (ETL → Report → Export)

**Tiempo:** 2 días

---

### Resumen Fase 7

```yaml
Duración: 2 semanas (10 días)

Semana 11: Generators + Exporters
  Día 1-3:   5 generadores + Tests
  Día 4-5:   3 exporters + Tests

Semana 12: API + Integration
  Día 1-3:   15 endpoints + Tests
  Día 4-5:   Integration + Limits

Deliverables:
  ✅ 5 report generators
  ✅ 3 exporters (Excel, CSV, PDF)
  ✅ 15 endpoints REST
  ✅ CNST-007 implementado (100K limit)
  ✅ Cache reportes
  ✅ File cleanup job
  ✅ 57+ tests
  ✅ >90% coverage

Checklist:
  [ ] 5 generators funcionando
  [ ] 3 exporters funcionando
  [ ] 15 endpoints REST
  [ ] Limit 100K rows
  [ ] Cache implementado
  [ ] File cleanup
  [ ] >90% coverage
```

---

## FASE 8: DASHBOARD & ALERTS (Semana 13)

### apps/dashboard/ (2.5 días)

**TDD:**
```python
# tests/unit/dashboard/test_services.py

from apps.dashboard.services import DashboardService
from tests.factories import DashboardConfigFactory


@pytest.mark.django_db
def test_get_user_dashboard(sample_user):
    """Test: Obtener dashboard del usuario."""
    config = DashboardConfigFactory(user=sample_user)
    
    dashboard = DashboardService.get_user_dashboard(sample_user)
    
    assert dashboard is not None
    assert dashboard.config_name == config.config_name
```

**Tareas:**
- [ ] Tests de DashboardService
- [ ] Tests de WidgetService
- [ ] Tests de MetricsService
- [ ] Implementar 3 services
- [ ] Tests de 10 endpoints
- [ ] Implementar ViewSets

**Tiempo:** 2.5 días

---

### apps/alerts/ (2.5 días)

**TDD:**
```python
# tests/unit/alerts/test_evaluators.py

from apps.alerts.evaluators import ThresholdEvaluator
from tests.factories import AlertRuleFactory


@pytest.mark.django_db
def test_threshold_evaluator():
    """Test: Evaluar regla de umbral."""
    rule = AlertRuleFactory(
        metric='abandonment_rate',
        threshold_value=0.15,
        comparison_operator='>'
    )
    
    evaluator = ThresholdEvaluator(rule)
    
    # Debajo del umbral
    assert evaluator.evaluate(0.10) is False
    
    # Por encima del umbral
    assert evaluator.evaluate(0.20) is True
```

**Tareas:**
- [ ] Tests de ThresholdEvaluator
- [ ] Tests de TrendEvaluator
- [ ] Tests de AnomalyEvaluator
- [ ] Implementar 3 evaluators
- [ ] Tests de 13 endpoints
- [ ] Implementar ViewSets

**Tiempo:** 2.5 días

---

### Resumen Fase 8

```yaml
Duración: 1 semana (5 días)

apps/dashboard/ (2.5 días):
  ✅ DashboardService, WidgetService, MetricsService
  ✅ 10 endpoints REST
  ✅ 20+ tests

apps/alerts/ (2.5 días):
  ✅ 3 evaluators (Threshold, Trend, Anomaly)
  ✅ AlertService, NotificationService
  ✅ 13 endpoints REST
  ✅ 25+ tests

Checklist:
  [ ] Dashboard funcionando
  [ ] Widgets configurables
  [ ] Alertas funcionando
  [ ] 3 tipos evaluadores
  [ ] Notificaciones email
  [ ] >85% coverage
```

---

## FASE 9: QA & DEPLOYMENT (Semana 14)

### QA (3 días)

**Tareas:**
- [ ] Completar tests faltantes
- [ ] Alcanzar >85% coverage total
- [ ] Code quality (pylint, flake8, black)
- [ ] Security audit (bandit)
- [ ] Performance tests
- [ ] Load tests

**Tiempo:** 3 días

---

### Deployment (2 días)

**Tareas:**
- [ ] Configurar PostgreSQL (producción)
- [ ] Configurar MariaDB IVR (readonly)
- [ ] Migrations finales
- [ ] Deploy staging
- [ ] Smoke tests staging
- [ ] Deploy producción

**Tiempo:** 2 días

---

## 📊 CHECKLIST MAESTRO

```yaml
FASE 1: Testing Infrastructure ✅
  [ ] 50+ factories creadas
  [ ] 14+ mocks creados
  [ ] conftest.py v2.0.0
  [ ] SQLite configurado
  [ ] Documentation completa

FASE 2: Core & Utils ✅
  [ ] apps/core/ (SOLO abstract)
  [ ] apps/utils/ (SOLO funciones)
  [ ] >90% coverage

FASE 3: Authentication ✅
  [ ] JWT funcionando
  [ ] 4 endpoints REST
  [ ] >85% coverage

FASE 4: Access (RBAC) ✅ 🔴
  [ ] 7 modelos
  [ ] 4 services
  [ ] 17 endpoints REST
  [ ] 57 funciones cargadas
  [ ] 4 roles predefinidos
  [ ] >90% coverage

FASE 5: Users & Audit ✅
  [ ] UserService
  [ ] AuditLog immutable
  [ ] Middleware captura requests
  [ ] >85% coverage

FASE 6: IVR & Pipeline ✅
  [ ] IVR readonly
  [ ] APScheduler
  [ ] 4 jobs programados
  [ ] >85% coverage

FASE 7: Reports ✅
  [ ] 5 generators
  [ ] 3 exporters
  [ ] 15 endpoints REST
  [ ] Limit 100K rows
  [ ] >90% coverage

FASE 8: Dashboard & Alerts ✅
  [ ] Dashboard configurable
  [ ] 3 tipos alertas
  [ ] >85% coverage

FASE 9: QA & Deployment ✅
  [ ] >85% coverage total
  [ ] Code quality
  [ ] Security audit
  [ ] Deployed staging
  [ ] Deployed producción
```

---

## 🎯 PRIORIZACIÓN v2.0.0

```yaml
P0 (CRÍTICO - Semanas 1-7):
  1. Testing Infrastructure (Semanas 1-2) ⭐
  2. Core & Utils (Semana 3)
  3. Authentication (Semana 4)
  4. Access/RBAC (Semanas 5-7) 🔴 MÁS CRÍTICO

P1 (ALTO - Semanas 8-10):
  5. Users & Audit (Semana 8)
  6. IVR & Pipeline (Semanas 9-10)

P2 (MEDIO - Semanas 11-12):
  7. Reports (Semanas 11-12)

P3 (BAJO - Semana 13):
  8. Dashboard & Alerts (Semana 13)

P4 (FINAL - Semana 14):
  9. QA & Deployment (Semana 14)
```

---

## ⚡ DIFERENCIAS vs v1.0.0

```yaml
v1.0.0 (18 semanas):
  ❌ Asumía MySQL/PostgreSQL desde inicio
  ❌ Factories parciales
  ❌ Sin mocks completos
  ❌ Service layer no priorizado
  ❌ Testing al final

v2.0.0 (14 semanas): ✅
  ✅ SQLite para desarrollo/tests
  ✅ Factories completas PRIMERO
  ✅ Mocks completos PRIMERO
  ✅ Service Layer desde inicio
  ✅ TDD approach (tests primero)
  ✅ 4 semanas más rápido
  ✅ Más realista y ejecutable
```

---

## 📚 RECURSOS v2.0.0

```yaml
Equipo:
  - 1-2 Senior Django Developers
  - 1 QA Engineer (part-time)
  - 1 DevOps Engineer (para deployment)

Herramientas:
  - factory_boy (factories)
  - pytest-mock (mocks)
  - pytest-django (testing Django)
  - pytest-cov (coverage)
  - SQLite (desarrollo/tests)
  - PostgreSQL (producción)
  - MariaDB (IVR readonly)

Ambientes:
  - Development (SQLite)
  - Testing (SQLite in-memory)
  - Staging (PostgreSQL + MariaDB)
  - Production (PostgreSQL + MariaDB)
```

---

## 🎉 RESUMEN EJECUTIVO

```yaml
Plan v2.0.0:
  Duración: 14 semanas (~3.5 meses)
  Fases: 9 fases
  Enfoque: TDD + Service Layer + Mocks
  Coverage objetivo: >85%
  
Fase Crítica:
  FASE 1: Testing Infrastructure (Semanas 1-2)
  - Sin esto, NO se puede avanzar
  - 50+ factories
  - 14+ mocks
  - SQLite configurado

Fase Más Importante:
  FASE 4: Access/RBAC (Semanas 5-7)
  - CORE del sistema
  - Sin RBAC, apps no pueden controlar permisos
  - 3 semanas dedicadas

Innovaciones:
  ✅ SQLite para desarrollo (más rápido)
  ✅ Factories ANTES de implementar
  ✅ Mocks ANTES de implementar
  ✅ TDD desde inicio
  ✅ Service Layer desde inicio
  
Riesgos Mitigados:
  ✅ NO depender de BD externas para desarrollo
  ✅ Tests completos ANTES de implementar
  ✅ Mocks para todo lo externo
  ✅ Validación continua con tests
```

---

**FIN DEL PLAN v2.0.0**

**Próximo paso:** Iniciar FASE 1 - Testing Infrastructure

**Tiempo total:** 14 semanas (3.5 meses)  
**Complejidad:** ALTA  
**Riesgo:** MEDIO (reducido vs v1.0.0)  
**Prioridad #1:** Testing Infrastructure + RBAC
