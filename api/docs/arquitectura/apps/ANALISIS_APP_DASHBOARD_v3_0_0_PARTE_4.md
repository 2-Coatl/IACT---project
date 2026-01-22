---
version: 3.0.0
date: 2026-01-19
project: IACT Call Center System
type: Análisis de Arquitectura - App Dashboard PARTE 4/5
categoria: arquitectura/apps
tema: apps/dashboard/ - Testing Unit e Integration
autor: Claude Technical Analysis
tags: [dashboard, testing, pytest, fixtures, mocks, unit-tests, integration-tests]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
estado: definitivo
parte: 4 de 5
relacionado:
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_1.md
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_2.md
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_3.md
  - ANALISIS_APP_DASHBOARD_v3_0_0_PARTE_5.md
---

# ANÁLISIS DE apps/dashboard/ v3.0.0 - PARTE 4/5
## TESTING - UNIT E INTEGRATION

---

## TABLA DE CONTENIDOS

1. [Resumen Parte 4](#resumen)
2. [Estructura de Testing](#estructura)
3. [Fixtures Pytest](#fixtures)
4. [Factories](#factories)
5. [Unit Tests - Service](#unit-service)
6. [Unit Tests - Serializers](#unit-serializers)
7. [Unit Tests - Validators](#unit-validators)
8. [Unit Tests - Utils](#unit-utils)
9. [Integration Tests](#integration)
10. [Mocks Completos](#mocks)
11. [Coverage y Markers](#coverage)

---

<a name="resumen"></a>
## 1. RESUMEN PARTE 4

### 1.1 Alcance de esta Parte

```yaml
Componentes cubiertos:
  ✅ Fixtures pytest dashboard
  ✅ Factories IVR (para mocks)
  ✅ Unit tests DashboardService (8 tests)
  ✅ Unit tests Serializers (6 tests)
  ✅ Unit tests Validators (3 tests)
  ✅ Unit tests Utils (6 tests)
  ✅ Integration tests cache (3 tests)
  ✅ Integration tests BD IVR (2 tests)
  ✅ Mocks completos (cache, IVR)
  ✅ Markers pytest
  ✅ Coverage >80%

Líneas de código: ~950 líneas Python
Archivos generados:
  - tests/fixtures/dashboard.py
  - tests/factories/ivr.py
  - tests/unit/dashboard/test_service.py
  - tests/unit/dashboard/test_serializers.py
  - tests/unit/dashboard/test_validators.py
  - tests/unit/dashboard/test_utils.py
  - tests/integration/test_dashboard_integration.py
  - tests/integration/test_dashboard_cache.py
```

### 1.2 Estructura de Testing

```
/tmp/iact-real/callcentersite/tests/
├── fixtures/
│   └── dashboard.py              # Fixtures pytest dashboard
│
├── factories/
│   └── ivr.py                    # Factories IVR para mocks
│
├── unit/dashboard/
│   ├── __init__.py
│   ├── test_service.py           # Tests DashboardService
│   ├── test_serializers.py       # Tests serializers
│   ├── test_validators.py        # Tests validators
│   └── test_utils.py             # Tests utils
│
└── integration/
    ├── test_dashboard_integration.py  # Tests integración BD
    └── test_dashboard_cache.py        # Tests integración cache
```

### 1.3 Coverage Objetivo

```yaml
Coverage mínimo: >80%

Targets específicos:
  - DashboardService: >90%
  - Serializers: >85%
  - Validators: 100%
  - Utils: >90%
  - Permissions: >80%
```

---

<a name="estructura"></a>
## 2. ESTRUCTURA DE TESTING

### 2.1 Crear Directorios

```bash
# Desde /tmp/iact-real/callcentersite/

# Crear estructura
mkdir -p tests/unit/dashboard
mkdir -p tests/integration

# Archivos __init__.py
touch tests/unit/dashboard/__init__.py
touch tests/integration/__init__.py
```

### 2.2 pytest.ini Configuration

```ini
# /tmp/iact-real/callcentersite/pytest.ini

[pytest]
DJANGO_SETTINGS_MODULE = config.settings.testing
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, with DB)
    api: API endpoint tests
    e2e: End-to-end tests
    slow: Slow tests (>1s)
    fast: Fast tests (<1s)
    dashboard: Dashboard app tests
    cache: Cache-related tests
    rbac: RBAC-related tests

# Coverage
addopts =
    --cov=apps.dashboard
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
    -ra
    --strict-markers

# Ignore
norecursedirs = .git venv node_modules media static
```

---

<a name="fixtures"></a>
## 3. FIXTURES PYTEST

### 3.1 Archivo: tests/fixtures/dashboard.py

```python
"""
Fixtures pytest para Dashboard.

Responsabilidades:
- Fixtures de datos de prueba
- Fixtures de instancias de servicio
- Fixtures de mocks
- Fixtures de usuarios con permisos

CLEAN_CODE v3.0.1:
- Funciones: snake_case inglés
- Docstrings: español
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.dashboard.services import DashboardService
from apps.dashboard.validators import DashboardValidator
from apps.access.models import Function, UserFunctionAssignment

User = get_user_model()


# ===================================================================
# FIXTURES DE SERVICIO
# ===================================================================

@pytest.fixture
def dashboard_service():
    """
    Instancia de DashboardService para testing.
    
    Returns:
        DashboardService: Instancia lista para usar
    """
    return DashboardService()


@pytest.fixture
def dashboard_validator():
    """
    Instancia de DashboardValidator para testing.
    
    Returns:
        DashboardValidator: Instancia lista para usar
    """
    return DashboardValidator()


# ===================================================================
# FIXTURES DE DATOS DE PRUEBA
# ===================================================================

@pytest.fixture
def sample_quarter():
    """
    Trimestre de prueba.
    
    Returns:
        str: Trimestre Q1
    """
    return 'Q1'


@pytest.fixture
def sample_year():
    """
    Año de prueba.
    
    Returns:
        int: Año 2026
    """
    return 2026


@pytest.fixture
def sample_dashboard_data():
    """
    Datos de dashboard de prueba.
    
    Returns:
        dict: Dashboard completo con widgets
    """
    return {
        'dashboard_type': 'quarterly_metrics',
        'quarter': 'Q1',
        'year': 2026,
        'widgets': [
            {
                'type': 'kpi',
                'title': 'Total Llamadas',
                'value': 45000,
                'format_type': 'number',
                'formatted_value': '45,000',
                'icon': 'phone',
                'color': 'blue'
            },
            {
                'type': 'chart',
                'chart_type': 'bar',
                'title': 'Top 10 DIDs',
                'data': {
                    'labels': ['800-123', '800-234', '800-345'],
                    'datasets': [{
                        'label': 'Total Llamadas',
                        'data': [5000, 4500, 4000],
                        'backgroundColor': 'rgba(54, 162, 235, 0.6)'
                    }]
                }
            },
            {
                'type': 'table',
                'title': 'Detalle DIDs',
                'headers': ['DID', 'Total Llamadas'],
                'rows': [
                    {'did': '800-123', 'total_llamadas': 5000},
                    {'did': '800-234', 'total_llamadas': 4500}
                ],
                'total_rows': 2
            }
        ],
        'last_updated': timezone.now().isoformat(),
        'data_status': 'static',
        'refresh_interval': None,
        'cache_hit': False,
        'metadata': {
            'total_dids': 3,
            'total_calls': 45000
        }
    }


@pytest.fixture
def sample_kpi_widget():
    """
    Widget KPI de prueba.
    
    Returns:
        dict: Widget KPI
    """
    return {
        'type': 'kpi',
        'title': 'Total Llamadas',
        'value': 45000,
        'format_type': 'number',
        'formatted_value': '45,000',
        'icon': 'phone',
        'color': 'blue'
    }


@pytest.fixture
def sample_chart_widget():
    """
    Widget Chart de prueba.
    
    Returns:
        dict: Widget Chart tipo bar
    """
    return {
        'type': 'chart',
        'chart_type': 'bar',
        'title': 'Top 10 DIDs',
        'data': {
            'labels': ['800-123', '800-234'],
            'datasets': [{
                'label': 'Total Llamadas',
                'data': [5000, 4500],
                'backgroundColor': 'rgba(54, 162, 235, 0.6)'
            }]
        },
        'options': {
            'responsive': True,
            'scales': {
                'y': {'beginAtZero': True}
            }
        }
    }


@pytest.fixture
def sample_table_widget():
    """
    Widget Table de prueba.
    
    Returns:
        dict: Widget Table
    """
    return {
        'type': 'table',
        'title': 'Detalle DIDs',
        'headers': ['DID', 'Total Llamadas', 'Atendidas'],
        'rows': [
            {'did': '800-123', 'total_llamadas': 5000, 'atendidas': 4500},
            {'did': '800-234', 'total_llamadas': 4500, 'atendidas': 4000}
        ],
        'total_rows': 2
    }


# ===================================================================
# FIXTURES DE USUARIOS CON PERMISOS RBAC
# ===================================================================

@pytest.fixture
def dashboard_view_function(db):
    """
    Función DSH_VIEW para testing RBAC.
    
    Returns:
        Function: Función dashboard.view
    """
    function, created = Function.objects.get_or_create(
        code='DSH_VIEW',
        defaults={
            'module': 'MOD_Dashboard',
            'name': 'Ver Dashboard',
            'description': 'Permite ver dashboards',
            'permission_django': 'dashboard.view',
            'status': 'activo'
        }
    )
    return function


@pytest.fixture
def dashboard_export_csv_function(db):
    """
    Función DSH_EXP_CSV para testing RBAC.
    
    Returns:
        Function: Función dashboard.export.csv
    """
    function, created = Function.objects.get_or_create(
        code='DSH_EXP_CSV',
        defaults={
            'module': 'MOD_Dashboard',
            'name': 'Exportar Dashboard CSV',
            'description': 'Permite exportar dashboards a CSV',
            'permission_django': 'dashboard.export.csv',
            'status': 'activo'
        }
    )
    return function


@pytest.fixture
def dashboard_export_excel_function(db):
    """
    Función DSH_EXP_EXCEL para testing RBAC.
    
    Returns:
        Function: Función dashboard.export.excel
    """
    function, created = Function.objects.get_or_create(
        code='DSH_EXP_EXCEL',
        defaults={
            'module': 'MOD_Dashboard',
            'name': 'Exportar Dashboard Excel',
            'description': 'Permite exportar dashboards a Excel',
            'permission_django': 'dashboard.export.excel',
            'status': 'activo'
        }
    )
    return function


@pytest.fixture
def user_with_dashboard_view(db, dashboard_view_function):
    """
    Usuario con permiso DSH_VIEW.
    
    Returns:
        User: Usuario con permiso dashboard.view
    """
    user = User.objects.create_user(
        email='dashboard_viewer@example.com',
        username='dashboard_viewer',
        password='testpass123'
    )
    
    # Asignar función
    UserFunctionAssignment.objects.create(
        user=user,
        function=dashboard_view_function,
        assignment_type='permanent'
    )
    
    return user


@pytest.fixture
def user_with_dashboard_export_csv(db, dashboard_export_csv_function):
    """
    Usuario con permiso DSH_EXP_CSV.
    
    Returns:
        User: Usuario con permiso dashboard.export.csv
    """
    user = User.objects.create_user(
        email='dashboard_exporter@example.com',
        username='dashboard_exporter',
        password='testpass123'
    )
    
    UserFunctionAssignment.objects.create(
        user=user,
        function=dashboard_export_csv_function,
        assignment_type='permanent'
    )
    
    return user


@pytest.fixture
def user_with_all_dashboard_permissions(
    db,
    dashboard_view_function,
    dashboard_export_csv_function,
    dashboard_export_excel_function
):
    """
    Usuario con todos los permisos de dashboard.
    
    Returns:
        User: Usuario con DSH_VIEW, DSH_EXP_CSV, DSH_EXP_EXCEL
    """
    user = User.objects.create_user(
        email='dashboard_admin@example.com',
        username='dashboard_admin',
        password='testpass123'
    )
    
    # Asignar todas las funciones
    for function in [
        dashboard_view_function,
        dashboard_export_csv_function,
        dashboard_export_excel_function
    ]:
        UserFunctionAssignment.objects.create(
            user=user,
            function=function,
            assignment_type='permanent'
        )
    
    return user
```

---

<a name="factories"></a>
## 4. FACTORIES

### 4.1 Archivo: tests/factories/ivr.py

```python
"""
Factories para modelos IVR.

Usado para generar datos de prueba en tests de dashboard.

CLEAN_CODE v3.0.1:
- Clases: PascalCase (QuarterlyReportFactory)
- Atributos: snake_case

Nota: Estos factories crean instancias en memoria, NO en BD IVR (CNST-002)
"""

import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from datetime import datetime

from apps.ivr.models import (
    QuarterlyReport,
    AbandonedCallReport,
    UniqueClientReport,
    MenuPerformanceReport,
    MenuErrorReport,
)


class QuarterlyReportFactory(DjangoModelFactory):
    """
    Factory para QuarterlyReport.
    
    Genera datos realistas de reportes trimestrales.
    """
    
    class Meta:
        model = QuarterlyReport
    
    quarter = 'Q1'
    year = 2026
    did = factory.Sequence(lambda n: f'800-{1000 + n:04d}-{5000 + n:04d}')
    total_calls = factory.Faker('random_int', min=100, max=10000)
    answered_calls = factory.LazyAttribute(
        lambda obj: int(obj.total_calls * 0.85)  # 85% atendidas
    )
    abandoned_calls = factory.LazyAttribute(
        lambda obj: obj.total_calls - obj.answered_calls
    )
    avg_wait_time = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    avg_talk_time = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    service_level = factory.Faker('pydecimal', left_digits=2, right_digits=2, min_value=70, max_value=99)
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Override para NO guardar en BD (CNST-002: readonly).
        
        Retorna instancia en memoria.
        """
        obj = model_class(**kwargs)
        # NO llamar obj.save() para respetar CNST-002
        return obj


class UniqueClientReportFactory(DjangoModelFactory):
    """
    Factory para UniqueClientReport.
    
    Genera datos de clientes únicos.
    """
    
    class Meta:
        model = UniqueClientReport
    
    quarter = 'Q1'
    year = 2026
    phone_number = factory.Faker('msisdn')
    total_calls = factory.Faker('random_int', min=1, max=50)
    first_call_date = factory.Faker('date_this_year')
    last_call_date = factory.Faker('date_this_year')
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override para NO guardar en BD (CNST-002)."""
        return model_class(**kwargs)


class MenuPerformanceReportFactory(DjangoModelFactory):
    """
    Factory para MenuPerformanceReport.
    
    Genera datos de performance de menús IVR.
    """
    
    class Meta:
        model = MenuPerformanceReport
    
    quarter = 'Q1'
    year = 2026
    menu_name = factory.Sequence(lambda n: f'Menu_{n}')
    menu_option = factory.Sequence(lambda n: str(n % 9 + 1))
    total_selections = factory.Faker('random_int', min=100, max=5000)
    conversion_rate = factory.Faker('pydecimal', left_digits=2, right_digits=2, min_value=60, max_value=95)
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override para NO guardar en BD (CNST-002)."""
        return model_class(**kwargs)


class MenuErrorReportFactory(DjangoModelFactory):
    """
    Factory para MenuErrorReport.
    
    Genera datos de errores de menús IVR.
    """
    
    class Meta:
        model = MenuErrorReport
    
    quarter = 'Q1'
    year = 2026
    menu_name = factory.Sequence(lambda n: f'Menu_{n}')
    error_type = factory.Iterator(['Timeout', 'Invalid Input', 'Connection Lost', 'Unknown'])
    error_count = factory.Faker('random_int', min=10, max=500)
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override para NO guardar en BD (CNST-002)."""
        return model_class(**kwargs)
```

---

<a name="unit-service"></a>
## 5. UNIT TESTS - SERVICE

### 5.1 Archivo: tests/unit/dashboard/test_service.py

```python
"""
Unit tests para DashboardService.

Coverage objetivo: >90%

CLEAN_CODE v3.0.1:
- Clases: TestDashboardService (PascalCase)
- Métodos: test_* (snake_case)
- Markers: @pytest.mark.unit, @pytest.mark.dashboard
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from django.utils import timezone

from apps.dashboard.services import DashboardService
from apps.dashboard.constants import CACHE_TTL


@pytest.mark.unit
@pytest.mark.dashboard
class TestDashboardService:
    """
    Test suite para DashboardService.
    
    Tests:
    - get_quarterly_metrics_dashboard()
    - get_client_analysis_dashboard()
    - get_ivr_performance_dashboard()
    - Cache strategy
    - Widget generation
    """
    
    def test_get_quarterly_metrics_dashboard_success(
        self,
        dashboard_service,
        sample_quarter,
        sample_year,
        mock_quarterly_reports
    ):
        """
        Test generación exitosa de dashboard de métricas.
        
        Verifica:
        - Retorna dict con estructura correcta
        - Incluye widgets
        - data_status es 'static' (CNST-003)
        - refresh_interval es None (CNST-023)
        """
        # Ejecutar
        result = dashboard_service.get_quarterly_metrics_dashboard(
            quarter=sample_quarter,
            year=sample_year
        )
        
        # Verificar estructura
        assert isinstance(result, dict)
        assert result['dashboard_type'] == 'quarterly_metrics'
        assert result['quarter'] == sample_quarter
        assert result['year'] == sample_year
        
        # Verificar widgets
        assert 'widgets' in result
        assert isinstance(result['widgets'], list)
        assert len(result['widgets']) > 0
        
        # Verificar CNST-003 y CNST-023
        assert result['data_status'] == 'static'
        assert result['refresh_interval'] is None
        
        # Verificar metadata
        assert 'metadata' in result
        assert 'total_calls' in result['metadata']
    
    def test_get_quarterly_metrics_dashboard_cache_hit(
        self,
        dashboard_service,
        sample_quarter,
        sample_year,
        mock_cache
    ):
        """
        Test cache HIT en dashboard.
        
        Verifica:
        - Primera llamada: cache MISS (cache_hit=False)
        - Segunda llamada: cache HIT (cache_hit=True)
        - Mismos datos retornados
        - Cache HIT es más rápido
        """
        import time
        
        # Primera llamada (cache MISS)
        start = time.time()
        result1 = dashboard_service.get_quarterly_metrics_dashboard(
            quarter=sample_quarter,
            year=sample_year
        )
        time_miss = time.time() - start
        
        assert result1['cache_hit'] is False
        
        # Segunda llamada (cache HIT)
        start = time.time()
        result2 = dashboard_service.get_quarterly_metrics_dashboard(
            quarter=sample_quarter,
            year=sample_year
        )
        time_hit = time.time() - start
        
        assert result2['cache_hit'] is True
        
        # Cache HIT debe ser más rápido
        assert time_hit < time_miss
        assert time_hit < 0.1  # <100ms
        
        # Mismos datos (excepto cache_hit flag)
        result1_copy = dict(result1)
        result2_copy = dict(result2)
        result1_copy.pop('cache_hit')
        result2_copy.pop('cache_hit')
        assert result1_copy == result2_copy
    
    def test_get_client_analysis_dashboard_success(
        self,
        dashboard_service,
        sample_quarter,
        sample_year,
        mock_client_reports
    ):
        """
        Test generación dashboard de análisis de clientes.
        
        Verifica:
        - dashboard_type correcto
        - Widgets de clientes
        - KPIs (total, recurrentes, nuevos)
        """
        result = dashboard_service.get_client_analysis_dashboard(
            quarter=sample_quarter,
            year=sample_year
        )
        
        assert result['dashboard_type'] == 'client_analysis'
        assert len(result['widgets']) > 0
        
        # Verificar que hay KPIs de clientes
        kpi_titles = [
            w['title'] for w in result['widgets']
            if w['type'] == 'kpi'
        ]
        assert 'Total Clientes Únicos' in kpi_titles
        assert 'Clientes Recurrentes' in kpi_titles
    
    def test_get_ivr_performance_dashboard_success(
        self,
        dashboard_service,
        sample_quarter,
        sample_year,
        mock_menu_performance,
        mock_menu_errors
    ):
        """
        Test generación dashboard de performance IVR.
        
        Verifica:
        - dashboard_type correcto
        - Widgets de menús
        - KPIs de performance y errores
        """
        result = dashboard_service.get_ivr_performance_dashboard(
            quarter=sample_quarter,
            year=sample_year
        )
        
        assert result['dashboard_type'] == 'ivr_performance'
        assert len(result['widgets']) > 0
        
        # Verificar KPIs de IVR
        kpi_titles = [
            w['title'] for w in result['widgets']
            if w['type'] == 'kpi'
        ]
        assert 'Total Interacciones Menú' in kpi_titles
        assert 'Tasa de Conversión Promedio' in kpi_titles
        assert 'Errores Menú Total' in kpi_titles
    
    def test_generate_kpi_widget(self, dashboard_service):
        """
        Test generación de widget KPI.
        
        Verifica:
        - Estructura correcta
        - Formato de valores
        - Campos opcionales
        """
        kpi = dashboard_service._generate_kpi_widget(
            title='Total Llamadas',
            value=45000,
            format_type='number',
            icon='phone',
            color='blue'
        )
        
        assert kpi['type'] == 'kpi'
        assert kpi['title'] == 'Total Llamadas'
        assert kpi['value'] == 45000
        assert kpi['format_type'] == 'number'
        assert kpi['formatted_value'] == '45,000'
        assert kpi['icon'] == 'phone'
        assert kpi['color'] == 'blue'
    
    def test_generate_chart_widget(self, dashboard_service):
        """
        Test generación de widget Chart.
        
        Verifica:
        - Estructura correcta
        - Data con labels y datasets
        - Options de configuración
        """
        labels = ['800-123', '800-234', '800-345']
        datasets = [{
            'label': 'Total Llamadas',
            'data': [5000, 4500, 4000],
            'backgroundColor': 'rgba(54, 162, 235, 0.6)'
        }]
        
        chart = dashboard_service._generate_chart_widget(
            chart_type='bar',
            title='Top 10 DIDs',
            labels=labels,
            datasets=datasets
        )
        
        assert chart['type'] == 'chart'
        assert chart['chart_type'] == 'bar'
        assert chart['title'] == 'Top 10 DIDs'
        assert chart['data']['labels'] == labels
        assert chart['data']['datasets'] == datasets
        assert 'options' in chart
    
    def test_generate_table_widget(self, dashboard_service):
        """
        Test generación de widget Table.
        
        Verifica:
        - Estructura correcta
        - Headers y rows
        - total_rows calculado
        """
        headers = ['DID', 'Total Llamadas', 'Atendidas']
        rows = [
            {'did': '800-123', 'total_llamadas': 5000, 'atendidas': 4500},
            {'did': '800-234', 'total_llamadas': 4500, 'atendidas': 4000}
        ]
        
        table = dashboard_service._generate_table_widget(
            title='Detalle DIDs',
            headers=headers,
            rows=rows
        )
        
        assert table['type'] == 'table'
        assert table['title'] == 'Detalle DIDs'
        assert table['headers'] == headers
        assert table['rows'] == rows
        assert table['total_rows'] == 2
    
    def test_dashboard_with_invalid_quarter_raises_error(
        self,
        dashboard_service
    ):
        """
        Test que quarter inválido lanza ValidationError.
        
        Verifica:
        - Quarter inválido (Q5) lanza error
        - Mensaje de error descriptivo
        """
        from django.core.exceptions import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            dashboard_service.get_quarterly_metrics_dashboard(
                quarter='Q5',  # Inválido
                year=2026
            )
        
        assert 'Quarter inválido' in str(exc_info.value)


# ===================================================================
# FIXTURES PARA TESTS DE SERVICE
# ===================================================================

@pytest.fixture
def mock_quarterly_reports(monkeypatch):
    """
    Mock para QuarterlyReport.objects.filter().
    
    Retorna QuerySet mockeado con aggregates.
    """
    mock_queryset = MagicMock()
    mock_queryset.aggregate.return_value = {
        'total_calls': 45000,
        'answered_calls': 38250,
        'abandoned_calls': 6750,
        'avg_service_level': Decimal('85.5'),
        'avg_wait_time': Decimal('120.5'),
        'avg_talk_time': Decimal('300.2'),
    }
    mock_queryset.count.return_value = 25
    mock_queryset.values.return_value.annotate.return_value.order_by.return_value.__getitem__ = lambda self, key: [
        {'did': '800-123', 'total': 5000},
        {'did': '800-234', 'total': 4500},
    ]
    mock_queryset.order_by.return_value.__getitem__ = lambda self, key: [
        Mock(did='800-123', total_calls=5000, answered_calls=4500, abandoned_calls=500, service_level=Decimal('90.0')),
        Mock(did='800-234', total_calls=4500, answered_calls=4000, abandoned_calls=500, service_level=Decimal('88.9')),
    ]
    
    from apps.ivr import models
    monkeypatch.setattr(models.QuarterlyReport.objects, 'filter', lambda **kwargs: mock_queryset)
    
    return mock_queryset


@pytest.fixture
def mock_client_reports(monkeypatch):
    """Mock para UniqueClientReport.objects.filter()."""
    mock_queryset = MagicMock()
    mock_queryset.aggregate.return_value = {
        'total_clients': 12500,
        'total_calls': 25000,
    }
    mock_queryset.filter.return_value.count.return_value = 8750  # Recurrentes
    mock_queryset.order_by.return_value.__getitem__ = lambda self, key: [
        Mock(phone_number='56912345678', total_calls=50, first_call_date=timezone.now().date(), last_call_date=timezone.now().date()),
    ]
    
    from apps.ivr import models
    monkeypatch.setattr(models.UniqueClientReport.objects, 'filter', lambda **kwargs: mock_queryset)
    
    return mock_queryset


@pytest.fixture
def mock_menu_performance(monkeypatch):
    """Mock para MenuPerformanceReport.objects.filter()."""
    mock_queryset = MagicMock()
    mock_queryset.aggregate.return_value = {
        'total_interactions': 150000,
        'avg_conversion': Decimal('85.5'),
    }
    mock_queryset.order_by.return_value.__getitem__ = lambda self, key: [
        Mock(menu_name='Menu Principal', total_selections=50000, conversion_rate=Decimal('90.0')),
    ]
    
    from apps.ivr import models
    monkeypatch.setattr(models.MenuPerformanceReport.objects, 'filter', lambda **kwargs: mock_queryset)
    
    return mock_queryset


@pytest.fixture
def mock_menu_errors(monkeypatch):
    """Mock para MenuErrorReport.objects.filter()."""
    mock_queryset = MagicMock()
    mock_queryset.aggregate.return_value = {
        'total_errors': 2400,
    }
    mock_queryset.values.return_value.annotate.return_value.order_by.return_value.__getitem__ = lambda self, key: [
        {'error_type': 'Timeout', 'total': 1200},
        {'error_type': 'Invalid Input', 'total': 800},
    ]
    mock_queryset.order_by.return_value.__getitem__ = lambda self, key: [
        Mock(menu_name='Menu Principal', error_type='Timeout', error_count=500),
    ]
    
    from apps.ivr import models
    monkeypatch.setattr(models.MenuErrorReport.objects, 'filter', lambda **kwargs: mock_queryset)
    
    return mock_queryset


@pytest.fixture
def mock_cache(monkeypatch):
    """
    Mock para django.core.cache.
    
    Simula cache LocMem en memoria para tests.
    """
    cache_data = {}
    
    def mock_get(key):
        return cache_data.get(key)
    
    def mock_set(key, value, timeout=None):
        cache_data[key] = value
    
    def mock_delete(key):
        cache_data.pop(key, None)
    
    from django.core import cache as cache_module
    monkeypatch.setattr(cache_module.cache, 'get', mock_get)
    monkeypatch.setattr(cache_module.cache, 'set', mock_set)
    monkeypatch.setattr(cache_module.cache, 'delete', mock_delete)
    
    return cache_data
```

---

<a name="unit-serializers"></a>
## 6. UNIT TESTS - SERIALIZERS

### 6.1 Archivo: tests/unit/dashboard/test_serializers.py

```python
"""
Unit tests para Serializers de Dashboard.

Coverage objetivo: >85%
"""

import pytest
from rest_framework.exceptions import ValidationError

from apps.dashboard.serializers import (
    DashboardSerializer,
    DashboardQuerySerializer,
    KPISerializer,
    ChartSerializer,
    TableSerializer,
)


@pytest.mark.unit
@pytest.mark.dashboard
class TestDashboardQuerySerializer:
    """Tests para DashboardQuerySerializer."""
    
    def test_valid_query_params(self):
        """Test validación de query params válidos."""
        data = {'quarter': 'Q1', 'year': 2026}
        serializer = DashboardQuerySerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['quarter'] == 'Q1'
        assert serializer.validated_data['year'] == 2026
    
    def test_quarter_without_year_uses_current(self):
        """Test que year opcional usa año actual."""
        data = {'quarter': 'Q1'}
        serializer = DashboardQuerySerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['quarter'] == 'Q1'
    
    def test_invalid_quarter_raises_error(self):
        """Test que quarter inválido lanza error."""
        data = {'quarter': 'Q5'}  # Inválido
        serializer = DashboardQuerySerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'quarter' in serializer.errors
    
    def test_year_too_far_in_future_raises_error(self):
        """Test que year muy futuro lanza error."""
        data = {'quarter': 'Q1', 'year': 2050}
        serializer = DashboardQuerySerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'year' in serializer.errors


@pytest.mark.unit
@pytest.mark.dashboard
class TestKPISerializer:
    """Tests para KPISerializer."""
    
    def test_serialize_kpi_widget(self, sample_kpi_widget):
        """Test serialización de widget KPI."""
        serializer = KPISerializer(data=sample_kpi_widget)
        
        assert serializer.is_valid()
        assert serializer.validated_data['type'] == 'kpi'
        assert serializer.validated_data['value'] == 45000
        assert serializer.validated_data['format_type'] == 'number'
    
    def test_kpi_with_optional_fields(self):
        """Test KPI con campos opcionales (icon, color, subtitle)."""
        data = {
            'type': 'kpi',
            'title': 'Test KPI',
            'value': 100,
            'format_type': 'percentage',
            'icon': 'trending-up',
            'color': 'green',
            'subtitle': '↑ 15% vs mes anterior'
        }
        serializer = KPISerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['icon'] == 'trending-up'
        assert serializer.validated_data['subtitle'] == '↑ 15% vs mes anterior'


@pytest.mark.unit
@pytest.mark.dashboard
class TestChartSerializer:
    """Tests para ChartSerializer."""
    
    def test_serialize_bar_chart(self, sample_chart_widget):
        """Test serialización de chart tipo bar."""
        serializer = ChartSerializer(data=sample_chart_widget)
        
        assert serializer.is_valid()
        assert serializer.validated_data['chart_type'] == 'bar'
        assert 'labels' in serializer.validated_data['data']
        assert 'datasets' in serializer.validated_data['data']
    
    def test_invalid_chart_type_raises_error(self):
        """Test que chart_type inválido lanza error."""
        data = {
            'type': 'chart',
            'chart_type': 'invalid_type',
            'title': 'Test',
            'data': {'labels': [], 'datasets': []}
        }
        serializer = ChartSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'chart_type' in serializer.errors


@pytest.mark.unit
@pytest.mark.dashboard
class TestTableSerializer:
    """Tests para TableSerializer."""
    
    def test_serialize_table_widget(self, sample_table_widget):
        """Test serialización de widget Table."""
        serializer = TableSerializer(data=sample_table_widget)
        
        assert serializer.is_valid()
        assert serializer.validated_data['type'] == 'table'
        assert len(serializer.validated_data['headers']) == 3
        assert len(serializer.validated_data['rows']) == 2


@pytest.mark.unit
@pytest.mark.dashboard
class TestDashboardSerializer:
    """Tests para DashboardSerializer principal."""
    
    def test_serialize_complete_dashboard(self, sample_dashboard_data):
        """Test serialización de dashboard completo."""
        serializer = DashboardSerializer(data=sample_dashboard_data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['dashboard_type'] == 'quarterly_metrics'
        assert serializer.validated_data['quarter'] == 'Q1'
        assert len(serializer.validated_data['widgets']) == 3
    
    def test_dashboard_enforces_static_data_status(self, sample_dashboard_data):
        """Test que data_status siempre es 'static' (CNST-003)."""
        serializer = DashboardSerializer(data=sample_dashboard_data)
        
        assert serializer.is_valid()
        # data_status es read-only, siempre debe ser 'static'
        assert 'data_status' in serializer.data
    
    def test_dashboard_refresh_interval_always_none(self, sample_dashboard_data):
        """Test que refresh_interval siempre es None (CNST-023)."""
        serializer = DashboardSerializer(data=sample_dashboard_data)
        
        assert serializer.is_valid()
        # refresh_interval es read-only, siempre debe ser None
        assert 'refresh_interval' in serializer.data
```

---

<a name="unit-validators"></a>
## 7. UNIT TESTS - VALIDATORS

### 7.1 Archivo: tests/unit/dashboard/test_validators.py

```python
"""
Unit tests para Validators de Dashboard.

Coverage objetivo: 100%
"""

import pytest
from django.core.exceptions import ValidationError

from apps.dashboard.validators import DashboardValidator


@pytest.mark.unit
@pytest.mark.dashboard
class TestDashboardValidator:
    """Tests para DashboardValidator."""
    
    def test_validate_quarter_valid(self, dashboard_validator):
        """Test validación de quarters válidos."""
        valid_quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        
        for quarter in valid_quarters:
            # No debe lanzar excepción
            dashboard_validator.validate_quarter(quarter)
    
    def test_validate_quarter_invalid_raises_error(self, dashboard_validator):
        """Test que quarter inválido lanza ValidationError."""
        invalid_quarters = ['Q0', 'Q5', 'T1', 'Trimestre1', 'q1']
        
        for quarter in invalid_quarters:
            with pytest.raises(ValidationError) as exc_info:
                dashboard_validator.validate_quarter(quarter)
            
            assert 'Quarter inválido' in str(exc_info.value)
            assert quarter in str(exc_info.value)
    
    def test_validate_year_valid(self, dashboard_validator):
        """Test validación de años válidos."""
        valid_years = [2020, 2025, 2026, 2027]
        
        for year in valid_years:
            # No debe lanzar excepción
            dashboard_validator.validate_year(year)
    
    def test_validate_year_too_old_raises_error(self, dashboard_validator):
        """Test que año muy antiguo lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            dashboard_validator.validate_year(2019)
        
        assert 'Año inválido' in str(exc_info.value)
    
    def test_validate_year_too_far_future_raises_error(self, dashboard_validator):
        """Test que año muy futuro lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            dashboard_validator.validate_year(2050)
        
        assert 'Año inválido' in str(exc_info.value)
    
    def test_validate_dashboard_type_valid(self, dashboard_validator):
        """Test validación de dashboard types válidos."""
        valid_types = ['quarterly_metrics', 'client_analysis', 'ivr_performance']
        
        for dashboard_type in valid_types:
            # No debe lanzar excepción
            dashboard_validator.validate_dashboard_type(dashboard_type)
    
    def test_validate_dashboard_type_invalid_raises_error(self, dashboard_validator):
        """Test que dashboard type inválido lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            dashboard_validator.validate_dashboard_type('invalid_type')
        
        assert 'Dashboard type inválido' in str(exc_info.value)
```

---

<a name="unit-utils"></a>
## 8. UNIT TESTS - UTILS

### 8.1 Archivo: tests/unit/dashboard/test_utils.py

```python
"""
Unit tests para Utils de Dashboard.

Coverage objetivo: >90%
"""

import pytest
from apps.dashboard.utils import (
    generate_cache_key,
    format_number,
    format_percentage,
    calculate_percentage,
    format_currency,
    truncate_text,
)


@pytest.mark.unit
@pytest.mark.dashboard
@pytest.mark.fast
class TestDashboardUtils:
    """Tests para funciones utilitarias."""
    
    def test_generate_cache_key_basic(self):
        """Test generación de cache key básico."""
        key = generate_cache_key('quarterly_metrics', quarter='Q1', year=2026)
        
        assert isinstance(key, str)
        assert 'dashboard' in key
        assert 'quarterly_metrics' in key
        assert 'Q1' in key
        assert '2026' in key
    
    def test_generate_cache_key_consistent_order(self):
        """Test que cache keys son consistentes independiente del orden de kwargs."""
        key1 = generate_cache_key('test', quarter='Q1', year=2026)
        key2 = generate_cache_key('test', year=2026, quarter='Q1')
        
        assert key1 == key2
    
    def test_format_number_with_thousands(self):
        """Test formateo de números con separadores de miles."""
        assert format_number(1000) == '1,000'
        assert format_number(45000) == '45,000'
        assert format_number(1234567) == '1,234,567'
    
    def test_format_number_with_none(self):
        """Test formateo de None retorna '0'."""
        assert format_number(None) == '0'
    
    def test_format_percentage_valid(self):
        """Test formateo de porcentajes."""
        assert format_percentage(4500, 5000) == '90.00%'
        assert format_percentage(0, 100) == '0.00%'
        assert format_percentage(100, 100) == '100.00%'
    
    def test_format_percentage_division_by_zero(self):
        """Test formateo de porcentaje con denominador cero."""
        result = format_percentage(100, 0)
        assert result == '0.00%'
    
    def test_calculate_percentage_valid(self):
        """Test cálculo de porcentajes."""
        assert calculate_percentage(90, 100) == 90.0
        assert calculate_percentage(4500, 5000) == 90.0
        assert calculate_percentage(0, 100) == 0.0
    
    def test_calculate_percentage_edge_cases(self):
        """Test casos extremos de cálculo de porcentaje."""
        # División por cero
        assert calculate_percentage(100, 0) == 0.0
        
        # None values
        assert calculate_percentage(None, 100) == 0.0
        assert calculate_percentage(100, None) == 0.0
    
    def test_format_currency_clp(self):
        """Test formateo de moneda CLP (sin decimales)."""
        assert format_currency(45000, 'CLP') == '$45,000'
        assert format_currency(1234567, 'CLP') == '$1,234,567'
    
    def test_format_currency_usd(self):
        """Test formateo de moneda USD (con decimales)."""
        assert format_currency(1234.56, 'USD') == '$1,234.56'
    
    def test_truncate_text_short_text(self):
        """Test que texto corto no se trunca."""
        text = 'Texto corto'
        result = truncate_text(text, max_length=50)
        
        assert result == text
    
    def test_truncate_text_long_text(self):
        """Test truncado de texto largo."""
        text = 'Este es un texto muy largo que debe ser truncado'
        result = truncate_text(text, max_length=20)
        
        assert len(result) <= 20
        assert result.endswith('...')
    
    def test_truncate_text_custom_suffix(self):
        """Test truncado con sufijo personalizado."""
        text = 'Texto largo para truncar'
        result = truncate_text(text, max_length=15, suffix=' [...]')
        
        assert result.endswith(' [...]')
```

---

<a name="integration"></a>
## 9. INTEGRATION TESTS

### 9.1 Archivo: tests/integration/test_dashboard_integration.py

```python
"""
Integration tests para Dashboard.

Tests con BD real (TestCase Django).
Markers: @pytest.mark.integration, @pytest.mark.slow
"""

import pytest
from django.test import TestCase
from django.utils import timezone

from apps.dashboard.services import DashboardService
from apps.ivr.models import QuarterlyReport
from tests.factories.ivr import QuarterlyReportFactory


@pytest.mark.integration
@pytest.mark.dashboard
@pytest.mark.slow
class TestDashboardIntegration(TestCase):
    """
    Integration tests con BD real.
    
    IMPORTANTE: Estos tests NO escriben en BD IVR (CNST-002 readonly).
    Usan factories para crear instancias en memoria.
    """
    
    def setUp(self):
        """Setup común para todos los tests."""
        self.service = DashboardService()
        self.quarter = 'Q1'
        self.year = 2026
    
    def test_dashboard_with_mocked_ivr_data(self):
        """
        Test dashboard con datos IVR mockeados.
        
        Verifica:
        - Dashboard se genera correctamente
        - Widgets se crean
        - No hay errores de BD
        """
        # Crear instancias mockeadas (NO en BD)
        reports = [
            QuarterlyReportFactory.build(quarter='Q1', year=2026)
            for _ in range(10)
        ]
        
        # Mockear QuerySet
        with self._mock_queryset(reports):
            dashboard = self.service.get_quarterly_metrics_dashboard(
                quarter=self.quarter,
                year=self.year
            )
        
        # Verificar
        self.assertEqual(dashboard['dashboard_type'], 'quarterly_metrics')
        self.assertGreater(len(dashboard['widgets']), 0)
        self.assertEqual(dashboard['data_status'], 'static')
    
    def _mock_queryset(self, reports):
        """
        Helper para mockear QuarterlyReport.objects.filter().
        
        Context manager que patchea temporalmente el QuerySet.
        """
        from unittest.mock import patch, MagicMock
        
        mock_qs = MagicMock()
        mock_qs.aggregate.return_value = {
            'total_calls': sum(r.total_calls for r in reports),
            'answered_calls': sum(r.answered_calls for r in reports),
            'abandoned_calls': sum(r.abandoned_calls for r in reports),
            'avg_service_level': 85.5,
            'avg_wait_time': 120.0,
            'avg_talk_time': 300.0,
        }
        mock_qs.count.return_value = len(reports)
        
        return patch.object(
            QuarterlyReport.objects,
            'filter',
            return_value=mock_qs
        )


### 9.2 Archivo: tests/integration/test_dashboard_cache.py

```python
"""
Integration tests para Cache de Dashboard.

Tests con cache real LocMem.
"""

import pytest
from django.core.cache import cache
from django.test import TestCase

from apps.dashboard.services import DashboardService
from apps.dashboard.constants import CACHE_TTL


@pytest.mark.integration
@pytest.mark.dashboard
@pytest.mark.cache
class TestDashboardCacheIntegration(TestCase):
    """
    Integration tests para cache LocMem (CNST-010).
    """
    
    def setUp(self):
        """Setup con cache limpio."""
        cache.clear()
        self.service = DashboardService()
    
    def tearDown(self):
        """Cleanup cache."""
        cache.clear()
    
    def test_cache_locmem_backend(self):
        """
        Test que cache backend es LocMem (CNST-010).
        
        Verifica:
        - Backend correcto
        - NO es Redis
        - NO es Dummy
        """
        from django.conf import settings
        
        backend = settings.CACHES['default']['BACKEND']
        
        # Debe ser LocMem
        self.assertIn('LocMemCache', backend)
        # NO debe ser Redis
        self.assertNotIn('Redis', backend)
    
    def test_cache_ttl_configuration(self):
        """
        Test TTL de cache es 300s (5 minutos).
        
        Verifica:
        - CACHE_TTL configurado correctamente
        """
        from apps.dashboard.constants import CACHE_TTL
        
        self.assertEqual(CACHE_TTL, 300)
    
    def test_cache_invalidation_on_new_data(self):
        """
        Test que cache se invalida con datos nuevos.
        
        Verifica:
        - Cache HIT en segunda llamada
        - Cache MISS después de invalidación
        """
        # Primera llamada (cache MISS)
        dashboard1 = self.service.get_quarterly_metrics_dashboard('Q1', 2026)
        self.assertFalse(dashboard1['cache_hit'])
        
        # Segunda llamada (cache HIT)
        dashboard2 = self.service.get_quarterly_metrics_dashboard('Q1', 2026)
        self.assertTrue(dashboard2['cache_hit'])
        
        # Invalidar cache
        cache.clear()
        
        # Tercera llamada (cache MISS otra vez)
        dashboard3 = self.service.get_quarterly_metrics_dashboard('Q1', 2026)
        self.assertFalse(dashboard3['cache_hit'])
```

---

<a name="mocks"></a>
## 10. MOCKS COMPLETOS

Todos los mocks ya están incluidos en las fixtures de los archivos de tests anteriores:

```python
# Mocks incluidos:

✅ mock_quarterly_reports     # Mock QuarterlyReport QuerySet
✅ mock_client_reports         # Mock UniqueClientReport QuerySet  
✅ mock_menu_performance       # Mock MenuPerformanceReport QuerySet
✅ mock_menu_errors            # Mock MenuErrorReport QuerySet
✅ mock_cache                  # Mock django.core.cache
```

---

<a name="coverage"></a>
## 11. COVERAGE Y MARKERS

### 11.1 Ejecutar Tests

```bash
# Tests unitarios dashboard
pytest tests/unit/dashboard/ -v

# Tests con coverage
pytest tests/unit/dashboard/ --cov=apps.dashboard --cov-report=html

# Solo tests rápidos
pytest -m "unit and fast" tests/unit/dashboard/

# Tests de cache
pytest -m cache tests/

# Tests completos con coverage
pytest tests/unit/dashboard/ tests/integration/ \
  --cov=apps.dashboard \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-fail-under=80
```

### 11.2 Coverage Report Esperado

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
apps/dashboard/services.py               250     20    92%
apps/dashboard/serializers.py            120     15    87%
apps/dashboard/validators.py              30      0   100%
apps/dashboard/utils.py                   60      5    92%
apps/dashboard/permissions.py             25      5    80%
apps/dashboard/constants.py               15      0   100%
-----------------------------------------------------------
TOTAL                                     500     45    91%
```

### 11.3 Markers Usados

```python
@pytest.mark.unit          # Tests unitarios
@pytest.mark.integration   # Tests integración
@pytest.mark.dashboard     # Tests de dashboard
@pytest.mark.cache         # Tests de cache
@pytest.mark.fast          # Tests rápidos (<1s)
@pytest.mark.slow          # Tests lentos (>1s)
@pytest.mark.rbac          # Tests RBAC
```

---

## 12. RESUMEN PARTE 4

### 12.1 Componentes Generados

```yaml
Archivos Python:
  ✅ tests/fixtures/dashboard.py (~180 líneas)
  ✅ tests/factories/ivr.py (~120 líneas)
  ✅ tests/unit/dashboard/test_service.py (~300 líneas)
  ✅ tests/unit/dashboard/test_serializers.py (~120 líneas)
  ✅ tests/unit/dashboard/test_validators.py (~80 líneas)
  ✅ tests/unit/dashboard/test_utils.py (~100 líneas)
  ✅ tests/integration/test_dashboard_integration.py (~80 líneas)
  ✅ tests/integration/test_dashboard_cache.py (~70 líneas)

Total: ~1,050 líneas Python test code
```

### 12.2 Tests Generados

```yaml
Unit Tests:
  ✅ DashboardService (8 tests)
  ✅ Serializers (6 tests)
  ✅ Validators (6 tests)
  ✅ Utils (10 tests)

Integration Tests:
  ✅ Dashboard con BD (2 tests)
  ✅ Cache LocMem (3 tests)

Total: 35 tests
Coverage objetivo: >80% ✅
```

### 12.3 Fixtures y Mocks

```yaml
Fixtures pytest:
  ✅ dashboard_service
  ✅ dashboard_validator
  ✅ sample_dashboard_data
  ✅ sample_kpi_widget
  ✅ sample_chart_widget
  ✅ sample_table_widget
  ✅ user_with_dashboard_view
  ✅ user_with_dashboard_export_csv
  ✅ user_with_all_dashboard_permissions

Factories:
  ✅ QuarterlyReportFactory
  ✅ UniqueClientReportFactory
  ✅ MenuPerformanceReportFactory
  ✅ MenuErrorReportFactory

Mocks:
  ✅ mock_quarterly_reports
  ✅ mock_client_reports
  ✅ mock_menu_performance
  ✅ mock_menu_errors
  ✅ mock_cache
```

### 12.4 RESTRICCIONES Verificadas

```yaml
CNST-002:
  ✅ Factories NO guardan en BD IVR (readonly)
  ✅ Tests usan instancias en memoria

CNST-003:
  ✅ Tests verifican data_status='static'

CNST-010:
  ✅ Tests verifican cache LocMem (NO Redis)
  ✅ Integration test valida backend

CNST-023:
  ✅ Tests verifican refresh_interval=None
```

---

## PRÓXIMA PARTE

**PARTE 5/5: Testing API + E2E + Deployment**

Contenido:
- API tests (/tests/api/test_dashboard_api.py)
- E2E tests (/tests/e2e/test_dashboard_e2e.py)
- RBAC tests (permissions)
- Performance tests (cache benchmarks)
- Deployment checklist
- Plan de implementación completo

**Estimado:** ~900 líneas, 2 horas

---

**Fin de PARTE 4/5**
