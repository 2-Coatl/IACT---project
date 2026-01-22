---
version: 1.0.0
date: 2026-01-20
project: IACT Call Center System
type: Guía Completa Testing
categoria: testing
tema: Testing con Mocks - SQLite, Factories, Service Layer
autor: Claude Technical Analysis
tags: [testing, mocks, sqlite, factories, service-layer]
estado: completo
---

# GUÍA COMPLETA: TESTING CON MOCKS Y SERVICE LAYER

**Contexto:** Trabajamos con **SQLite** en tests (NO tenemos IPs de MySQL/PostgreSQL reales).

---

## 📊 ESTADO ACTUAL

```yaml
Base de Datos Tests:
  ✅ SQLite (en memoria) - CORRECTO
  ❌ NO MySQL connection
  ❌ NO PostgreSQL connection
  ✅ Mocks para simular BD externas

Estructura Actual:
  ✅ tests/factories/     # factory_boy
  ✅ tests/fixtures/      # pytest fixtures
  ✅ tests/unit/          # tests por app
  ✅ tests/integration/   # tests multi-app
  ✅ tests/api/           # tests endpoints

Patrón Arquitectónico:
  ✅ Service Layer Pattern
  ✅ Lógica en services (NO en models)
  ✅ Models = solo estructura
  ✅ Services = lógica de negocio
```

---

## 1. FACTORIES COMPLETAS (factory_boy)

### 1.1 Factories para TODAS las apps

**Archivo:** `tests/factories/__init__.py`

```python
"""
Factories completas para TODAS las apps.

PATTERN: factory_boy para crear objetos de test.
"""

# Import all factories for easy access
from .user_factory import UserFactory, AdminUserFactory
from .access_factories import (
    ModuleFactory,
    FunctionFactory,
    RoleFactory,
    UserModuleAccessFactory,
    UserFunctionAssignmentFactory,
)
from .audit_factories import (
    AuditLogFactory,
    SessionLogFactory,
)
from .ivr_factories import (
    QuarterlyReportFactory,
    TransferReportFactory,
    AbandonedReportFactory,
    CallRecordQ1Factory,
)
from .pipeline_factories import (
    ETLJobFactory,
    ETLErrorFactory,
    SchedulerConfigFactory,
)
from .report_factories import (
    ReportFactory,
    ReportExecutionFactory,
    ReportTemplateFactory,
)
from .dashboard_factories import (
    DashboardConfigFactory,
    WidgetConfigFactory,
)
from .alert_factories import (
    AlertRuleFactory,
    AlertFactory,
    AlertNotificationFactory,
)

__all__ = [
    # Users
    'UserFactory',
    'AdminUserFactory',
    
    # Access/RBAC
    'ModuleFactory',
    'FunctionFactory',
    'RoleFactory',
    'UserModuleAccessFactory',
    'UserFunctionAssignmentFactory',
    
    # Audit
    'AuditLogFactory',
    'SessionLogFactory',
    
    # IVR
    'QuarterlyReportFactory',
    'TransferReportFactory',
    'AbandonedReportFactory',
    'CallRecordQ1Factory',
    
    # Pipeline
    'ETLJobFactory',
    'ETLErrorFactory',
    'SchedulerConfigFactory',
    
    # Reports
    'ReportFactory',
    'ReportExecutionFactory',
    'ReportTemplateFactory',
    
    # Dashboard
    'DashboardConfigFactory',
    'WidgetConfigFactory',
    
    # Alerts
    'AlertRuleFactory',
    'AlertFactory',
    'AlertNotificationFactory',
]
```

---

### 1.2 Access Factories

**Archivo:** `tests/factories/access_factories.py`

```python
"""
Factories para apps/access/ (RBAC).
"""

import factory
from factory.django import DjangoModelFactory
from apps.access.models import (
    Module,
    Function,
    Role,
    UserModuleAccess,
    UserFunctionAssignment,
    UserRoleAssignment,
)
from .user_factory import UserFactory


class ModuleFactory(DjangoModelFactory):
    """Factory para Module."""
    
    class Meta:
        model = Module
    
    module_id = factory.Sequence(lambda n: f'MODULE_{n:03d}')
    name = factory.Faker('word')
    parent = None  # Override si necesitas jerarquía
    is_active = True


class FunctionFactory(DjangoModelFactory):
    """Factory para Function."""
    
    class Meta:
        model = Function
    
    function_id = factory.Sequence(lambda n: f'function.{n}')
    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=200)
    module = factory.SubFactory(ModuleFactory)


class RoleFactory(DjangoModelFactory):
    """Factory para Role."""
    
    class Meta:
        model = Role
    
    role_id = factory.Sequence(lambda n: f'ROLE_{n:03d}')
    name = factory.Faker('job')
    description = factory.Faker('text', max_nb_chars=200)


class UserModuleAccessFactory(DjangoModelFactory):
    """Factory para UserModuleAccess."""
    
    class Meta:
        model = UserModuleAccess
    
    user = factory.SubFactory(UserFactory)
    module = factory.SubFactory(ModuleFactory)


class UserFunctionAssignmentFactory(DjangoModelFactory):
    """Factory para UserFunctionAssignment."""
    
    class Meta:
        model = UserFunctionAssignment
    
    user = factory.SubFactory(UserFactory)
    function = factory.SubFactory(FunctionFactory)
```

---

### 1.3 IVR Factories (MOCK - SQLite)

**CRÍTICO:** IVR usa MariaDB en producción, pero en tests **simulamos con SQLite**.

**Archivo:** `tests/factories/ivr_factories.py`

```python
"""
Factories para apps/ivr/ (ETL).

IMPORTANTE: En tests usamos SQLite (NO MariaDB).
Los datos son MOCK, simulan lo que vendría de BD IVR real.
"""

import factory
from factory.django import DjangoModelFactory
from datetime import date
from apps.ivr.models import (
    QuarterlyReport,
    TransferReport,
    AbandonedReport,
    ClientReport,
    CallRecordQ1,
)


class QuarterlyReportFactory(DjangoModelFactory):
    """
    Factory para QuarterlyReport.
    
    Simula datos de BD IVR (MariaDB en prod, SQLite en tests).
    """
    
    class Meta:
        model = QuarterlyReport
    
    year = 2025
    quarter = 1
    total_calls = factory.Faker('pyint', min_value=1000, max_value=50000)
    unique_clients = factory.Faker('pyint', min_value=500, max_value=10000)
    avg_duration_seconds = factory.Faker('pyint', min_value=60, max_value=600)


class TransferReportFactory(DjangoModelFactory):
    """Factory para TransferReport."""
    
    class Meta:
        model = TransferReport
    
    year = 2025
    quarter = 1
    menu_option = factory.Iterator(['1', '2', '3', '4', '5'])
    total_transfers = factory.Faker('pyint', min_value=10, max_value=1000)
    avg_wait_time_seconds = factory.Faker('pyint', min_value=5, max_value=120)


class AbandonedReportFactory(DjangoModelFactory):
    """Factory para AbandonedReport."""
    
    class Meta:
        model = AbandonedReport
    
    year = 2025
    quarter = 1
    did = factory.Sequence(lambda n: f'80012345{n}')
    total_abandoned = factory.Faker('pyint', min_value=0, max_value=500)
    abandonment_rate = factory.Faker('pyfloat', min_value=0, max_value=0.3)


class ClientReportFactory(DjangoModelFactory):
    """Factory para ClientReport."""
    
    class Meta:
        model = ClientReport
    
    year = 2025
    quarter = 1
    client_id = factory.Sequence(lambda n: f'CLIENT_{n:05d}')
    total_calls = factory.Faker('pyint', min_value=1, max_value=100)
    total_duration_seconds = factory.Faker('pyint', min_value=60, max_value=3600)


class CallRecordQ1Factory(DjangoModelFactory):
    """Factory para CallRecordQ1."""
    
    class Meta:
        model = CallRecordQ1
    
    fecha = factory.LazyFunction(lambda: date(2025, 1, 15))
    telefono = factory.Sequence(lambda n: f'80012{n:05d}')
    duracion_segundos = factory.Faker('pyint', min_value=30, max_value=600)
    estado = factory.Iterator(['COMPLETED', 'ABANDONED', 'FAILED'])
```

---

### 1.4 Reports Factories

**Archivo:** `tests/factories/report_factories.py`

```python
"""Factories para apps/reports/."""

import factory
from factory.django import DjangoModelFactory
from apps.reports.models import Report, ReportExecution, ReportTemplate
from .user_factory import UserFactory


class ReportFactory(DjangoModelFactory):
    """Factory para Report."""
    
    class Meta:
        model = Report
    
    report_type = factory.Iterator(['quarterly', 'transfers', 'abandoned', 'clients'])
    report_name = factory.Faker('sentence', nb_words=4)
    generated_by = factory.SubFactory(UserFactory)
    file_format = factory.Iterator(['xlsx', 'csv', 'pdf'])
    file_url = factory.Faker('url')
    file_size_bytes = factory.Faker('pyint', min_value=1024, max_value=1024000)
    row_count = factory.Faker('pyint', min_value=10, max_value=10000)
    parameters = factory.LazyFunction(lambda: {'year': 2025, 'quarter': 1})
    generation_time_seconds = factory.Faker('pyfloat', min_value=0.5, max_value=30.0)
    is_cached = False


class ReportExecutionFactory(DjangoModelFactory):
    """Factory para ReportExecution."""
    
    class Meta:
        model = ReportExecution
    
    report = factory.SubFactory(ReportFactory)
    execution_status = factory.Iterator(['SUCCESS', 'FAILED', 'PENDING'])
    started_at = factory.Faker('date_time_this_month')
    finished_at = factory.Faker('date_time_this_month')


class ReportTemplateFactory(DjangoModelFactory):
    """Factory para ReportTemplate."""
    
    class Meta:
        model = ReportTemplate
    
    template_name = factory.Faker('sentence', nb_words=3)
    report_type = factory.Iterator(['quarterly', 'transfers'])
    default_parameters = factory.LazyFunction(lambda: {'year': 2025, 'quarter': 1})
    is_active = True
```

---

## 2. MOCKS COMPLETOS

### 2.1 Mock de Database IVR (MariaDB)

**Archivo:** `tests/mocks/database_mocks.py`

```python
"""
Mocks para conexiones de BD.

CONTEXTO: No tenemos IPs de MySQL/PostgreSQL reales.
Simulamos respuestas de BD usando mocks.
"""

from unittest.mock import Mock, MagicMock
import pytest


@pytest.fixture
def mock_ivr_connection(mocker):
    """
    Mock de conexión a BD IVR (MariaDB).
    
    En producción: MariaDB readonly
    En tests: Mock que simula respuestas
    
    Uso:
        def test_etl(mock_ivr_connection):
            # BD IVR mockeada
            pass
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Simular cursor
    mock_conn.cursor.return_value = mock_cursor
    
    # Simular fetchall() con datos fake
    mock_cursor.fetchall.return_value = [
        (2025, 1, 10000, 5000, 180),  # year, quarter, calls, clients, duration
        (2025, 2, 12000, 6000, 190),
    ]
    
    # Mockear django.db.connections
    mocker.patch(
        'django.db.connections.__getitem__',
        return_value=mock_conn
    )
    
    return mock_conn


@pytest.fixture
def mock_postgresql_connection(mocker):
    """
    Mock de conexión a PostgreSQL.
    
    Similar a IVR, pero para BD principal.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    
    mocker.patch(
        'django.db.connections.databases.default',
        return_value=mock_conn
    )
    
    return mock_conn


@pytest.fixture
def mock_database_router(mocker):
    """
    Mock del Database Router.
    
    CNST-002: IVRRouter decide qué BD usar.
    En tests, siempre usa SQLite (default).
    """
    mock_router = MagicMock()
    
    # db_for_read siempre retorna 'default' (SQLite)
    mock_router.db_for_read.return_value = 'default'
    
    # db_for_write retorna None para IVR (readonly)
    def mock_db_for_write(model, **hints):
        if model._meta.app_label == 'ivr':
            return None  # IVR readonly
        return 'default'
    
    mock_router.db_for_write.side_effect = mock_db_for_write
    
    mocker.patch(
        'apps.ivr.routers.IVRRouter',
        return_value=mock_router
    )
    
    return mock_router
```

---

### 2.2 Mock de ETL Service

**Archivo:** `tests/mocks/service_mocks.py`

```python
"""
Mocks para Services.

Service Layer Pattern: Lógica en services, NO en models.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_etl_service(mocker):
    """
    Mock de ETLService.
    
    Simula extracción de datos sin tocar BD IVR real.
    
    Uso:
        def test_report_generation(mock_etl_service):
            mock_etl_service.extract_quarterly_data.return_value = [...]
            # Test usa datos mock
    """
    from apps.pipeline.services import ETLService
    
    mock_service = MagicMock(spec=ETLService)
    
    # Mock extract_quarterly_data
    mock_service.extract_quarterly_data.return_value = [
        {'year': 2025, 'quarter': 1, 'total_calls': 10000},
        {'year': 2025, 'quarter': 2, 'total_calls': 12000},
    ]
    
    # Mock extract_transfer_data
    mock_service.extract_transfer_data.return_value = [
        {'menu_option': '1', 'total_transfers': 500},
        {'menu_option': '2', 'total_transfers': 300},
    ]
    
    mocker.patch(
        'apps.pipeline.services.ETLService',
        return_value=mock_service
    )
    
    return mock_service


@pytest.fixture
def mock_report_generator_service(mocker):
    """
    Mock de ReportGeneratorService.
    
    Simula generación de reportes sin generar archivos reales.
    """
    from apps.reports.services import ReportGeneratorService
    
    mock_service = MagicMock(spec=ReportGeneratorService)
    
    # Mock generate_report
    mock_service.generate_report.return_value = {
        'report_id': 123,
        'file_url': 'http://example.com/test.xlsx',
        'status': 'SUCCESS'
    }
    
    mocker.patch(
        'apps.reports.services.ReportGeneratorService',
        return_value=mock_service
    )
    
    return mock_service


@pytest.fixture
def mock_access_service(mocker):
    """
    Mock de AccessService (RBAC).
    
    Simula verificación de permisos.
    """
    from apps.access.services import AccessService
    
    mock_service = MagicMock(spec=AccessService)
    
    # Por defecto, usuario tiene acceso
    mock_service.user_has_function.return_value = True
    mock_service.user_has_module.return_value = True
    
    mocker.patch(
        'apps.access.services.AccessService',
        return_value=mock_service
    )
    
    return mock_service
```

---

### 2.3 Mock de File Generation

**Archivo:** `tests/mocks/file_mocks.py`

```python
"""
Mocks para generación de archivos.
"""

import pytest
from unittest.mock import MagicMock, mock_open


@pytest.fixture
def mock_excel_exporter(mocker):
    """
    Mock de ExcelExporter.
    
    Simula export a Excel sin crear archivo real.
    """
    from apps.reports.exporters import ExcelExporter
    
    mock_exporter = MagicMock(spec=ExcelExporter)
    
    # export() retorna path fake
    mock_exporter.export.return_value = '/fake/path/report.xlsx'
    
    mocker.patch(
        'apps.reports.exporters.ExcelExporter',
        return_value=mock_exporter
    )
    
    return mock_exporter


@pytest.fixture
def mock_file_storage(mocker):
    """
    Mock de file storage.
    
    Simula guardado de archivos sin escribir disco.
    """
    mock_storage = MagicMock()
    
    # save() retorna path fake
    mock_storage.save.return_value = '/fake/path/file.xlsx'
    mock_storage.url.return_value = 'http://example.com/file.xlsx'
    
    mocker.patch(
        'django.core.files.storage.default_storage',
        mock_storage
    )
    
    return mock_storage


@pytest.fixture
def mock_open_file(mocker):
    """
    Mock de open() para archivos.
    
    Simula lectura/escritura sin tocar disco.
    """
    m = mock_open(read_data=b'fake file content')
    mocker.patch('builtins.open', m)
    return m
```

---

## 3. SERVICE LAYER PATTERN

### 3.1 Guía: Mover lógica de Model → Service

**ANTES (Lógica en Model - ❌ INCORRECTO):**

```python
# apps/reports/models.py

class Report(models.Model):
    """❌ INCORRECTO: Lógica de negocio en model"""
    
    report_type = models.CharField(max_length=50)
    file_url = models.URLField()
    
    def generate_quarterly_report(self, year, quarter):
        """❌ Lógica de negocio aquí"""
        # Consultar BD IVR
        data = QuarterlyReport.objects.filter(year=year, quarter=quarter)
        
        # Generar Excel
        exporter = ExcelExporter()
        file_path = exporter.export(data)
        
        # Guardar
        self.file_url = file_path
        self.save()
        
        return self
```

**DESPUÉS (Lógica en Service - ✅ CORRECTO):**

```python
# apps/reports/models.py

class Report(models.Model):
    """✅ CORRECTO: Solo estructura, NO lógica"""
    
    report_type = models.CharField(max_length=50)
    file_url = models.URLField()
    # ... solo fields


# apps/reports/services.py

class ReportGeneratorService:
    """✅ CORRECTO: Lógica de negocio en service"""
    
    @staticmethod
    def generate_quarterly_report(year, quarter, generated_by):
        """
        Genera reporte trimestral.
        
        Returns:
            Report: Reporte generado
        """
        # 1. Consultar datos
        data = QuarterlyReport.objects.filter(year=year, quarter=quarter)
        
        # 2. Generar Excel
        exporter = ExcelExporter()
        file_path = exporter.export(data)
        
        # 3. Crear registro
        report = Report.objects.create(
            report_type='quarterly',
            file_url=file_path,
            generated_by=generated_by,
            parameters={'year': year, 'quarter': quarter}
        )
        
        return report
```

---

### 3.2 Test de Service (con Mocks)

```python
# tests/unit/reports/test_services.py

import pytest
from apps.reports.services import ReportGeneratorService
from tests.factories import UserFactory, QuarterlyReportFactory


@pytest.mark.django_db
class TestReportGeneratorService:
    """Tests para ReportGeneratorService."""
    
    def test_generate_quarterly_report_with_mocks(
        self,
        mock_etl_service,
        mock_excel_exporter
    ):
        """
        Test: Genera reporte usando mocks (SIN BD IVR real).
        
        Given: Datos de BD IVR mockeados
        When: Generamos reporte trimestral
        Then: Reporte se crea exitosamente
        """
        # Arrange
        user = UserFactory()
        
        # Mock de datos IVR
        mock_etl_service.extract_quarterly_data.return_value = [
            {'year': 2025, 'quarter': 1, 'total_calls': 10000}
        ]
        
        # Mock de export
        mock_excel_exporter.export.return_value = '/fake/report.xlsx'
        
        # Act
        report = ReportGeneratorService.generate_quarterly_report(
            year=2025,
            quarter=1,
            generated_by=user
        )
        
        # Assert
        assert report is not None
        assert report.report_type == 'quarterly'
        assert report.file_url == '/fake/report.xlsx'
        
        # Verificar mocks llamados
        mock_etl_service.extract_quarterly_data.assert_called_once()
        mock_excel_exporter.export.assert_called_once()
```

---

## 4. EJEMPLOS COMPLETOS DE TESTS

### 4.1 Test Unitario con Factories

```python
# tests/unit/access/test_models.py

import pytest
from tests.factories import ModuleFactory, UserFactory, UserModuleAccessFactory


@pytest.mark.django_db
class TestModuleModel:
    """Tests para Module model."""
    
    def test_create_module_with_factory(self):
        """Test: Crear módulo usando factory."""
        # Arrange & Act
        module = ModuleFactory(
            module_id='MODULE_TEST',
            name='Test Module'
        )
        
        # Assert
        assert module.module_id == 'MODULE_TEST'
        assert module.name == 'Test Module'
        assert module.is_active is True
    
    def test_module_hierarchy_with_factories(self):
        """Test: Jerarquía de módulos con factories."""
        # Arrange
        parent = ModuleFactory(name='Parent')
        child = ModuleFactory(name='Child', parent=parent)
        
        # Assert
        assert child.parent == parent
        assert parent in child.get_ancestors()
```

---

### 4.2 Test de Service con Mocks

```python
# tests/unit/pipeline/test_services.py

import pytest
from apps.pipeline.services import ETLService
from tests.factories import ETLJobFactory


@pytest.mark.django_db
class TestETLService:
    """Tests para ETLService."""
    
    def test_extract_data_with_mock_db(self, mock_ivr_connection):
        """
        Test: Extraer datos con BD IVR mockeada.
        
        Given: Conexión IVR mockeada
        When: Ejecutamos ETL
        Then: Datos se extraen correctamente
        """
        # Arrange
        mock_cursor = mock_ivr_connection.cursor.return_value
        mock_cursor.fetchall.return_value = [
            (2025, 1, 10000, 5000, 180),
        ]
        
        # Act
        data = ETLService.extract_quarterly_data(year=2025, quarter=1)
        
        # Assert
        assert len(data) == 1
        assert data[0]['year'] == 2025
        assert data[0]['total_calls'] == 10000
```

---

### 4.3 Test de API con Factories

```python
# tests/api/test_reports_api.py

import pytest
from tests.factories import UserFactory, ReportFactory


@pytest.mark.django_db
class TestReportAPI:
    """Tests para Report API."""
    
    def test_list_reports(self, authenticated_client):
        """Test: Listar reportes."""
        # Arrange
        ReportFactory.create_batch(5)  # Crear 5 reportes
        
        # Act
        response = authenticated_client.get('/api/v1/reports/')
        
        # Assert
        assert response.status_code == 200
        assert len(response.data['results']) == 5
    
    def test_generate_report_with_mocks(
        self,
        authenticated_client,
        mock_report_generator_service
    ):
        """Test: Generar reporte con service mockeado."""
        # Arrange
        mock_report_generator_service.generate_report.return_value = {
            'report_id': 123,
            'file_url': 'http://example.com/test.xlsx'
        }
        
        # Act
        response = authenticated_client.post('/api/v1/reports/generate/', {
            'report_type': 'quarterly',
            'year': 2025,
            'quarter': 1
        })
        
        # Assert
        assert response.status_code == 201
        assert 'file_url' in response.data
```

---

## 5. INTEGRACIÓN: conftest.py ACTUALIZADO

**Archivo:** `tests/conftest.py`

```python
"""
Configuración pytest COMPLETA.

Integra:
- Factories (factory_boy)
- Fixtures pytest
- Mocks (unittest.mock)
"""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Import factories
from tests.factories import (
    UserFactory,
    AdminUserFactory,
    ModuleFactory,
    FunctionFactory,
    ReportFactory,
)

# Import fixtures adicionales
pytest_plugins = [
    'tests.fixtures.users',
    'tests.fixtures.rbac',
    'tests.mocks.database_mocks',
    'tests.mocks.service_mocks',
    'tests.mocks.file_mocks',
]


# ============================================================================
# API CLIENTS
# ============================================================================

@pytest.fixture
def api_client():
    """Cliente REST sin autenticación."""
    return APIClient()


@pytest.fixture
def authenticated_client(db, sample_user):
    """Cliente REST autenticado."""
    client = APIClient()
    refresh = RefreshToken.for_user(sample_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


# ============================================================================
# USERS (usando Factories)
# ============================================================================

@pytest.fixture
def sample_user(db):
    """Usuario estándar usando factory."""
    return UserFactory()


@pytest.fixture
def sample_admin(db):
    """Admin usando factory."""
    return AdminUserFactory()


# ============================================================================
# ACCESS/RBAC (usando Factories)
# ============================================================================

@pytest.fixture
def sample_module(db):
    """Módulo usando factory."""
    return ModuleFactory()


@pytest.fixture
def sample_function(db, sample_module):
    """Función usando factory."""
    return FunctionFactory(module=sample_module)


# ============================================================================
# DATABASE SETTINGS (SQLite)
# ============================================================================

@pytest.fixture(scope='session')
def django_db_setup():
    """
    Configuración BD para tests.
    
    IMPORTANTE: Usa SQLite (NO MySQL/PostgreSQL).
    """
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
```

---

## 6. CHECKLIST DE IMPLEMENTACIÓN

```yaml
Factories:
  [ ] Crear factories para 11 apps
  [ ] UserFactory, AdminUserFactory
  [ ] AccessFactories (Module, Function, Role)
  [ ] IVRFactories (QuarterlyReport, etc)
  [ ] ReportFactories
  [ ] Dashboard, Alerts, Pipeline factories

Mocks:
  [ ] mock_ivr_connection (BD IVR)
  [ ] mock_postgresql_connection
  [ ] mock_database_router
  [ ] mock_etl_service
  [ ] mock_report_generator_service
  [ ] mock_excel_exporter
  [ ] mock_file_storage

Service Layer:
  [ ] Mover lógica de models → services
  [ ] Crear services para cada app
  [ ] Models solo estructura
  [ ] Services con lógica de negocio

Tests:
  [ ] Tests unitarios con factories
  [ ] Tests de services con mocks
  [ ] Tests de API con factories + mocks
  [ ] >85% coverage

conftest.py:
  [ ] Integrar factories
  [ ] Integrar mocks
  [ ] SQLite configurado
  [ ] pytest_plugins actualizado
```

---

## 7. COMANDOS ÚTILES

```bash
# Ejecutar tests
pytest

# Con mocks verbose
pytest -vv -s

# Solo tests unitarios
pytest tests/unit/

# Solo tests de access
pytest tests/unit/access/

# Con coverage
pytest --cov=apps --cov-report=html

# Ver mocks llamados (debug)
pytest -vv --tb=short
```

---

## RESUMEN

```yaml
✅ SQLite en tests (NO MySQL/PostgreSQL)
✅ Factories (factory_boy) para crear objetos
✅ Mocks para BD, services, files
✅ Service Layer Pattern (lógica en services)
✅ Tests con factories + mocks
✅ >85% coverage objetivo

Estructura Final:
  tests/
  ├── factories/         # factory_boy
  ├── fixtures/          # pytest fixtures
  ├── mocks/             # mocks BD, services
  ├── unit/              # tests unitarios
  ├── integration/       # tests multi-app
  └── api/               # tests endpoints
```

---

**FIN DE LA GUÍA COMPLETA**

**Próximo paso:** Implementar factories y mocks para las 11 apps.
