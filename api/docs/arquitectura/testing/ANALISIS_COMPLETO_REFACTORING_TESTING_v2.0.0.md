---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis Técnico Completo - Refactoring Testing
categoria: arquitectura/testing
autor: Claude Technical Analysis
tags: [testing, fixtures, mocks, refactoring, pytest, clean-code]
relacionado:
  - ANALISIS_COMPLETO_OPCIONES_TESTING_v1.0.0.md
  - PLAN_ACCION_INMEDIATA_v1.0.0.md
changelog:
  - v2.0.0: Análisis completo para refactorización de TODAS las apps
  - v1.0.0: Análisis inicial de 3 opciones
---

# ANÁLISIS COMPLETO: REFACTORIZACIÓN TESTING PARA TODAS LAS APPS

**Plan Integral de Fixtures, Mocks y Refactorización Completa - IACT v2.0**

---

## RESUMEN EJECUTIVO

### Contexto

Se ha decidido realizar una **refactorización COMPLETA** del sistema de testing de IACT que incluye:

1. **Refactorización de código** (Service Layer Pattern)
2. **Suite completa de fixtures pytest** para todas las apps
3. **Sistema de mocks** para servicios externos
4. **Actualización de TODAS las apps** al nuevo estándar

### Alcance

```
APPS A REFACTORIZAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ access           (76 KB de tests)
✓ audit            (68 KB de tests)
✓ authentication   (55 KB de tests)
✓ core             (204 KB de tests) ← App más grande
✓ ivr_legacy       (20 KB de tests)
✓ pipeline         (36 KB de tests)
✓ reports          (83 KB de tests)
✓ users            (150 KB de tests)
✓ utils            (81 KB de tests)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL: 9 apps, 773 KB de tests, ~267 archivos
```

### Inversión vs Retorno

```
INVERSIÓN:
- Tiempo: 8-12 semanas (2-3 meses)
- Esfuerzo: 320-480 horas
- Equipo: 2-3 desarrolladores

RETORNO:
- Cobertura: 13% → 90%+ (aumento 77%)
- Velocidad tests: 30 seg → 2 seg (15x más rápido)
- Código limpio: Service Layer en todas las apps
- Mantenibilidad: Arquitectura enterprise-grade
- CI/CD: Sistema funcional sin dependencias externas
```

---

## TABLA DE CONTENIDOS

1. [Restricciones Técnicas CNST Actualizadas](#restricciones)
2. [Estado Actual del Sistema](#estado-actual)
3. [Estructura de Tests Existente](#estructura)
4. [Análisis por App](#analisis-apps)
5. [Plan de Fixtures Completo](#plan-fixtures)
6. [Sistema de Mocks](#sistema-mocks)
7. [Estrategia de Refactorización](#estrategia)
8. [Roadmap de Implementación](#roadmap)
9. [Métricas de Éxito](#metricas)
10. [Riesgos y Mitigación](#riesgos)
11. [Conclusiones](#conclusiones)

---

<a name="restricciones"></a>
## 1. RESTRICCIONES TÉCNICAS CNST ACTUALIZADAS

### 1.1 Restricciones del Entorno (CNST_TECNICAS v2.0)

```yaml
# ════════════════════════════════════════════════════════════
# RESTRICCIONES TÉCNICAS - IACT CALL CENTER SYSTEM v2.0
# ════════════════════════════════════════════════════════════

NETWORKING:
  external_access: NO
  description: |
    Sin acceso a internet desde el entorno de desarrollo.
    Sin acceso a repositorios externos.
  
  blocked:
    - pypi.org (solo instalaciones locales)
    - github.com (sin git clone)
    - npmjs.com
    - dockerhub.com
    - Cualquier CDN externo

CLOUD_SERVICES:
  aws: NO
  description: |
    Sin servicios de AWS bajo ninguna circunstancia.
  
  blocked:
    - AWS S3
    - AWS RDS
    - AWS Lambda
    - AWS CloudWatch
    - AWS SQS/SNS
    - Cualquier servicio AWS

  google_cloud: NO
  description: |
    Sin servicios de Google Cloud.
  
  blocked:
    - Google Cloud Storage
    - Google Cloud SQL
    - Google Cloud Functions
    - Cualquier servicio GCP

  azure: NO
  description: Sin servicios de Microsoft Azure.

CONTAINERIZATION:
  docker: NO
  description: |
    Sin Docker ni tecnologías derivadas.
  
  blocked:
    - Docker
    - Docker Compose
    - Podman
    - Kubernetes
    - Containerd
    - LXC/LXD
    - Cualquier containerización

CI_CD:
  github_actions: NO
  description: Sin GitHub Actions ni servicios CI/CD externos.
  
  blocked:
    - GitHub Actions
    - GitLab CI
    - CircleCI
    - Travis CI
    - Jenkins (externo)
    - Cualquier CI/CD cloud

  local_only: YES
  description: |
    Solo herramientas locales:
    - pytest local
    - pre-commit hooks locales
    - Scripts bash locales

DATABASES:
  production:
    postgresql: NO
    description: Sin acceso a PostgreSQL en desarrollo
  
  production:
    mariadb: NO
    description: Sin acceso a MariaDB en desarrollo
  
  development:
    sqlite: YES
    description: |
      SQLite como única opción para desarrollo y testing.
      In-memory para tests.

EXTERNAL_SERVICES:
  email: NO
  description: Sin servicios de email externos
  
  blocked:
    - SendGrid
    - Mailgun
    - AWS SES
    - SMTP externos

  storage: NO
  description: Sin servicios de almacenamiento externos
  
  blocked:
    - AWS S3
    - Google Cloud Storage
    - Azure Blob Storage
    - Cloudinary

  monitoring: NO
  description: Sin servicios de monitoreo externos
  
  blocked:
    - Sentry
    - New Relic
    - Datadog
    - CloudWatch

AVAILABLE_TOOLS:
  languages:
    - Python 3.12.3
  
  frameworks:
    - Django 4.2.11
    - Django REST Framework 3.14.0
  
  testing:
    - pytest 7.4.4
    - pytest-django
    - factory-boy
    - faker
  
  databases:
    - SQLite 3.x (in-memory para tests)
  
  tools:
    - venv (Python virtual environment)
    - bash scripts
    - pre-commit (local hooks)

NETWORK_RESTRICTIONS:
  ports:
    blocked: all external
    allowed: 
      - localhost only
      - 127.0.0.1:8000 (Django dev server)
      - 127.0.0.1:5432 (PostgreSQL local, solo producción)
```

### 1.2 Implicaciones para Testing

```
┌────────────────────────────────────────────────────────────┐
│ RESTRICCIÓN                  IMPLICACIÓN PARA TESTING       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ NO networking externo    → NO pytest-cov uploads           │
│                          → NO coverage.io                   │
│                          → Solo reportes locales            │
│                                                             │
│ NO AWS/Google/Azure      → NO S3 tests                     │
│                          → MOCK todos los servicios cloud   │
│                          → Filesystem local para uploads    │
│                                                             │
│ NO Docker                → NO testcontainers                │
│                          → NO docker-compose para tests     │
│                          → SQLite in-memory únicamente      │
│                                                             │
│ NO GitHub Actions        → NO CI/CD externo                 │
│                          → Pre-commit hooks locales         │
│                          → Scripts bash para validación     │
│                                                             │
│ NO PostgreSQL/MariaDB    → SQLite para tests                │
│ (en desarrollo)          → Validación SQL differences       │
│                          → Tests semanales en producción    │
│                                                             │
│ NO email externo         → Mock EmailBackend               │
│                          → Capturar emails en memoria       │
│                          → Validar sin enviar               │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 1.3 Soluciones Permitidas

```python
# ════════════════════════════════════════════════════════════
# SOLUCIONES VÁLIDAS BAJO CNST v2.0
# ════════════════════════════════════════════════════════════

# ✅ PERMITIDO: SQLite in-memory
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'ivr_legacy': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# ✅ PERMITIDO: Mocks locales
from unittest.mock import Mock, patch

@patch('apps.storage.backends.S3Storage')
def test_upload(mock_s3):
    mock_s3.save.return_value = 'file.txt'
    # Test sin AWS real

# ✅ PERMITIDO: Fixtures pytest
@pytest.fixture
def sample_user(db):
    return User.objects.create(username='test')

# ✅ PERMITIDO: Factory Boy
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Faker('user_name')

# ✅ PERMITIDO: Email backend para testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# ✅ PERMITIDO: Pre-commit hooks locales
# .pre-commit-config.yaml (local)
repos:
  - repo: local
    hooks:
      - id: pytest
        name: Run tests
        entry: pytest tests/
        language: system

# ❌ PROHIBIDO: Servicios externos
import boto3  # ← NO
from sendgrid import SendGridAPIClient  # ← NO
import docker  # ← NO
```

---

<a name="estado-actual"></a>
## 2. ESTADO ACTUAL DEL SISTEMA

### 2.1 Métricas Globales

```
ESTADO ACTUAL (2026-01-17):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tests:
├─ Total archivos:        267 archivos test_*.py
├─ Total tests:           ~294 tests identificados
├─ Tamaño código:         773 KB de código de tests
│
├─ Ejecutados:            62 tests (21%)
├─ Pasando:               37 tests (13%)
├─ Fallando:              25 tests (8%)
└─ Con errores:           232 tests (79%)

Problemas Principales:
├─ Imports faltantes:     3 archivos (232 tests bloqueados)
│  ├─ HasFunction → HasModuleAccess (alias missing)
│  ├─ ServiceAccessService → No existe
│  └─ apps.utils.network → No existe
│
├─ Database config:       ~120 tests bloqueados
│  └─ ivr_legacy DB no configurada en testing.py
│
├─ Fixtures missing:      ~50 tests requieren fixtures
│  ├─ sample_user
│  ├─ sample_service
│  ├─ sample_modules
│  └─ authenticated_client
│
└─ Mocks missing:         ~30 tests requieren mocks
   ├─ S3 storage
   ├─ Email backend
   └─ External APIs

Cobertura:
├─ Líneas código:         ~50,000 líneas (estimado)
├─ Líneas cubiertas:      ~6,500 líneas (13%)
└─ Objetivo:              45,000+ líneas (90%)

Tiempo Ejecución:
├─ Actual (37 tests):     ~30 segundos
├─ Proyectado (294):      ~4 minutos (con DB)
└─ Objetivo:              <5 segundos (in-memory + mocks)
```

### 2.2 Desglose por App

```
APP            TESTS   TAMAÑO    ESTADO        PRIORIDAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
core           ~80     204 KB    CRÍTICO       🔴 ALTA
users          ~60     150 KB    IMPORTANTE    🟠 ALTA
reports        ~40     83 KB     BLOQUEADO     🔴 ALTA
utils          ~35     81 KB     PARCIAL       🟡 MEDIA
access         ~30     76 KB     BLOQUEADO     🔴 ALTA
audit          ~25     68 KB     FUNCIONAL     🟢 MEDIA
authentication ~20     55 KB     FUNCIONAL     🟢 BAJA
pipeline       ~15     36 KB     PARCIAL       🟡 MEDIA
ivr_legacy     ~10     20 KB     BLOQUEADO     🟠 MEDIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL          ~315    773 KB    13% PASSING   
```

### 2.3 Problemas Críticos Identificados

```python
# ════════════════════════════════════════════════════════════
# PROBLEMA 1: Imports Faltantes (232 tests bloqueados)
# ════════════════════════════════════════════════════════════

# apps/access/permissions/__init__.py
ImportError: cannot import name 'HasFunction'

SOLUCIÓN:
# Crear alias para compatibilidad
from .module_permissions import HasModuleAccess
HasFunction = HasModuleAccess  # Alias

# ════════════════════════════════════════════════════════════
# PROBLEMA 2: Service Layer Missing (50+ tests)
# ════════════════════════════════════════════════════════════

# apps/core/services/__init__.py
ImportError: cannot import name 'ServiceAccessService'

SOLUCIÓN:
# Crear apps/core/services/service_access.py
class ServiceAccessService:
    @staticmethod
    def get_user_services(user):
        # Lógica movida del model
        pass

# ════════════════════════════════════════════════════════════
# PROBLEMA 3: Utils Network Missing (30+ tests)
# ════════════════════════════════════════════════════════════

# apps/utils/network.py
ModuleNotFoundError: No module named 'apps.utils.network'

SOLUCIÓN:
# Crear apps/utils/network.py
def get_client_ip(request):
    """Obtener IP del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

# ════════════════════════════════════════════════════════════
# PROBLEMA 4: Database Configuration (120+ tests)
# ════════════════════════════════════════════════════════════

# config/settings/testing.py - ACTUAL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
# Falta 'ivr_legacy' → 120 tests no pueden ejecutarse

SOLUCIÓN:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'ivr_legacy': {  # ← AGREGAR
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# ════════════════════════════════════════════════════════════
# PROBLEMA 5: Fixtures Inexistentes (50+ tests)
# ════════════════════════════════════════════════════════════

# tests/conftest.py - ACTUAL
# Solo tiene django_db_setup básico
# Falta:
# - sample_user
# - authenticated_client
# - admin_user
# - sample_services
# - sample_modules

SOLUCIÓN:
# Crear fixtures completas (ver sección 5)
```

---

<a name="estructura"></a>
## 3. ESTRUCTURA DE TESTS EXISTENTE

### 3.1 Árbol de Directorios

```
/tmp/iact-real/callcentersite/tests/
│
├── api/                          ← Tests de API endpoints
│   ├── __init__.py
│   ├── test_access_api.py       (2.0 KB)
│   ├── test_audit_api.py        (1.5 KB)
│   └── test_core_api.py         (1.0 KB)
│
├── e2e/                          ← Tests end-to-end (vacío)
│   ├── __init__.py
│   └── README.md
│
├── factories/                    ← Factory Boy factories
│   ├── __init__.py
│   ├── README.md
│   ├── core.py                  (2.0 KB) ← Parcial
│   └── user_factory.py          (1.5 KB) ← Solo User
│
├── fixtures/                     ← Datos de fixtures
│   ├── __init__.py
│   ├── README.md
│   ├── initial_modules.json     (2.0 KB)
│   ├── modules.json             (3.0 KB)
│   ├── rbac.py                  (2.0 KB)
│   ├── reports_rbac.json        (1.5 KB)
│   ├── sample_data.json         (0.5 KB)
│   └── users.py                 (3.5 KB)
│
├── integration/                  ← Tests integración (vacío)
│   ├── __init__.py
│   └── README.md
│
├── unit/                         ← Tests unitarios (principal)
│   ├── __init__.py
│   │
│   ├── access/                  (76 KB total)
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_permissions.py  ← BLOQUEADO (HasFunction)
│   │   ├── test_services.py
│   │   └── test_views.py
│   │
│   ├── audit/                   (68 KB total)
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_decorator.py
│   │   ├── test_middleware.py
│   │   ├── test_models.py
│   │   └── test_service.py
│   │
│   ├── authentication/          (55 KB total)
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   └── test_views.py
│   │
│   ├── core/                    (204 KB total) ← MÁS GRANDE
│   │   ├── __init__.py
│   │   ├── test_core_app.py
│   │   ├── test_core_etl_service.py
│   │   ├── test_core_models.py
│   │   ├── test_core_serializers.py
│   │   ├── test_navigation_builders.py
│   │   ├── test_navigation_views.py
│   │   └── test_service_access.py  ← BLOQUEADO (Service)
│   │
│   ├── ivr_legacy/              (20 KB total)
│   │   ├── __init__.py
│   │   ├── test_ivr_adapters.py
│   │   ├── test_ivr_app.py
│   │   └── test_ivr_models.py   ← BLOQUEADO (DB config)
│   │
│   ├── pipeline/                (36 KB total)
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_scheduler.py
│   │   └── test_views.py
│   │
│   ├── reports/                 (83 KB total)
│   │   ├── __init__.py
│   │   ├── test_cnst007_compliance.py
│   │   ├── test_models.py
│   │   ├── test_report_model.py
│   │   ├── test_serializers.py
│   │   ├── test_services.py
│   │   └── test_views.py
│   │
│   ├── users/                   (150 KB total)
│   │   ├── __init__.py
│   │   ├── test_avatar_api.py
│   │   ├── test_profile_api.py
│   │   ├── test_serializers.py
│   │   ├── test_user_model.py
│   │   └── test_views.py
│   │
│   ├── utils/                   (81 KB total)
│   │   ├── __init__.py
│   │   ├── test_request_utils.py
│   │   ├── test_soft_delete.py
│   │   └── test_utils_network.py  ← BLOQUEADO (network)
│   │
│   ├── test_factories.py        (1.5 KB)
│   └── test_fixtures.py         (1.0 KB)
│
├── __init__.py
├── conftest.py                   (3.0 KB) ← EXPANDIR AQUÍ
└── README.md                     (6.5 KB)

TOTAL: 773 KB, ~267 archivos
```

### 3.2 Análisis del conftest.py Actual

```python
# ════════════════════════════════════════════════════════════
# tests/conftest.py (ACTUAL - 3.0 KB)
# ════════════════════════════════════════════════════════════

import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup():
    """
    Setup básico de base de datos.
    
    PROBLEMA: Solo configura 'default', falta 'ivr_legacy'
    """
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

# FIN DEL ARCHIVO
# ════════════════════════════════════════════════════════════
# TOTAL: 10 líneas
# FIXTURES: 1 (solo django_db_setup)
# ════════════════════════════════════════════════════════════

# NECESITAMOS AGREGAR:
# - 20+ fixtures de datos
# - 10+ fixtures de clientes autenticados
# - 15+ mocks de servicios
# - Factories integration
# 
# OBJETIVO: 500+ líneas en conftest.py
```

---

**CONTINUARÁ EN PARTE 2...**

Este documento tendrá aproximadamente 5,000+ líneas. Las secciones pendientes son:

4. Análisis por App (detallado para cada una)
5. Plan de Fixtures Completo
6. Sistema de Mocks
7. Estrategia de Refactorización
8. Roadmap de Implementación (semana por semana)
9. Métricas de Éxito
10. Riesgos y Mitigación
11. Conclusiones

¿Continúo creando las secciones restantes?

<a name="analisis-apps"></a>
## 4. ANÁLISIS DETALLADO POR APP

### 4.1 APP: CORE (Prioridad CRÍTICA 🔴)

```
MÉTRICAS:
├─ Tamaño tests:      204 KB (26% del total)
├─ Tests estimados:   ~80 tests
├─ Estado:            CRÍTICO - Bloqueado por imports
├─ Prioridad:         🔴 ALTA
└─ Tiempo estimado:   3-4 semanas

PROBLEMAS IDENTIFICADOS:
├─ ServiceAccessService no existe (50+ tests bloqueados)
├─ Models gordos con lógica de negocio
├─ Sin fixtures de datos básicos
└─ Sin mocks para servicios externos

ARCHIVOS DE TEST:
tests/unit/core/
├─ test_core_app.py              (~25 KB)
├─ test_core_etl_service.py      (~30 KB)
├─ test_core_models.py           (~40 KB) ← Más grande
├─ test_core_serializers.py      (~35 KB)
├─ test_navigation_builders.py   (~25 KB)
├─ test_navigation_views.py      (~30 KB)
└─ test_service_access.py        (~19 KB) ← BLOQUEADO
```

#### 4.1.1 Models a Refactorizar (core)

```python
# ════════════════════════════════════════════════════════════
# MODELS QUE NECESITAN REFACTORING EN CORE
# ════════════════════════════════════════════════════════════

1. UserServiceAccess (CRÍTICO)
   ────────────────────────────────────────
   Problema:
   - 100+ líneas de lógica de negocio
   - Métodos: get_user_services, has_service_access
   - Tests esperan ServiceAccessService
   
   Solución:
   - Crear apps/core/services/service_access.py
   - Mover lógica a ServiceAccessService
   - 50+ tests desbloqueados

2. Service
   ────────────────────────────────────────
   Problema:
   - Métodos de negocio en model
   - get_active_services, validate_800_number
   
   Solución:
   - Crear ServiceService
   - Mover validaciones complejas

3. Module
   ────────────────────────────────────────
   Problema:
   - Lógica de permisos en model
   - get_user_modules, check_permission
   
   Solución:
   - Crear ModuleService
   - Integrar con RBAC system

4. Function
   ────────────────────────────────────────
   Problema:
   - Validación de permisos en model
   
   Solución:
   - Crear FunctionService
   - Service layer para functions
```

#### 4.1.2 Fixtures Requeridas (core)

```python
# ════════════════════════════════════════════════════════════
# tests/fixtures/core.py (NUEVO - 200+ líneas)
# ════════════════════════════════════════════════════════════

import pytest
from apps.core.models import Service, Module, Function, UserServiceAccess

# ────────────────────────────────────────
# SERVICES
# ────────────────────────────────────────

@pytest.fixture
def sample_service(db):
    """Servicio 800 de ejemplo."""
    return Service.objects.create(
        numero_800='800-123-4567',
        nombre='Servicio Test',
        activo=True,
        empresa='Test Corp'
    )

@pytest.fixture
def inactive_service(db):
    """Servicio inactivo para tests."""
    return Service.objects.create(
        numero_800='800-999-9999',
        nombre='Servicio Inactivo',
        activo=False,
        empresa='Test Corp'
    )

@pytest.fixture
def multiple_services(db):
    """Lista de servicios para tests."""
    return [
        Service.objects.create(
            numero_800=f'800-{i:03d}-0000',
            nombre=f'Servicio {i}',
            activo=True
        )
        for i in range(1, 6)
    ]

# ────────────────────────────────────────
# MODULES
# ────────────────────────────────────────

@pytest.fixture
def sample_module(db):
    """Módulo de ejemplo."""
    return Module.objects.create(
        code='TEST',
        name='Test Module',
        description='Módulo de prueba',
        is_active=True,
        order=1
    )

@pytest.fixture
def admin_module(db):
    """Módulo de administración."""
    return Module.objects.create(
        code='ADMIN',
        name='Administración',
        description='Módulo administrativo',
        is_active=True,
        order=0
    )

@pytest.fixture
def reports_module(db):
    """Módulo de reportes."""
    return Module.objects.create(
        code='REPORTS',
        name='Reportes',
        description='Módulo de reportes',
        is_active=True,
        order=2
    )

# ────────────────────────────────────────
# FUNCTIONS
# ────────────────────────────────────────

@pytest.fixture
def sample_function(sample_module):
    """Función de ejemplo."""
    return Function.objects.create(
        module=sample_module,
        code='VIEW',
        name='Ver',
        description='Permiso de visualización',
        is_active=True
    )

@pytest.fixture
def edit_function(sample_module):
    """Función de edición."""
    return Function.objects.create(
        module=sample_module,
        code='EDIT',
        name='Editar',
        description='Permiso de edición',
        is_active=True
    )

# ────────────────────────────────────────
# USER SERVICE ACCESS
# ────────────────────────────────────────

@pytest.fixture
def user_service_access(sample_user, sample_service):
    """Acceso de usuario a servicio."""
    return UserServiceAccess.objects.create(
        user=sample_user,
        service=sample_service,
        is_active=True,
        granted_by=sample_user,
        reason='Test access'
    )

@pytest.fixture
def user_with_services(sample_user, multiple_services):
    """Usuario con múltiples servicios asignados."""
    for service in multiple_services:
        UserServiceAccess.objects.create(
            user=sample_user,
            service=service,
            is_active=True,
            granted_by=sample_user
        )
    return sample_user
```

#### 4.1.3 Mocks Requeridos (core)

```python
# ════════════════════════════════════════════════════════════
# tests/mocks/core.py (NUEVO - 150+ líneas)
# ════════════════════════════════════════════════════════════

from unittest.mock import Mock, MagicMock

# ────────────────────────────────────────
# ETL SERVICE MOCKS
# ────────────────────────────────────────

@pytest.fixture
def mock_etl_service():
    """Mock del servicio ETL."""
    mock = Mock()
    mock.extract.return_value = {'data': 'test'}
    mock.transform.return_value = {'transformed': True}
    mock.load.return_value = True
    return mock

# ────────────────────────────────────────
# EXTERNAL API MOCKS
# ────────────────────────────────────────

@pytest.fixture
def mock_external_api():
    """Mock de API externa."""
    mock = Mock()
    mock.get.return_value = {
        'status': 'success',
        'data': []
    }
    return mock
```

#### 4.1.4 Plan de Implementación (core)

```
SEMANA 1-2: Refactoring Service Layer
────────────────────────────────────────────
✓ Crear ServiceAccessService
✓ Crear ServiceService  
✓ Crear ModuleService
✓ Crear FunctionService
✓ Mover lógica de models a services
✓ Tests de services (unit)

Tiempo: 80 horas (2 semanas)
Resultado: 50+ tests desbloqueados

SEMANA 3: Fixtures y Factories
────────────────────────────────────────────
✓ Crear fixtures/core.py (completo)
✓ Crear factories/core.py (completo)
✓ Actualizar conftest.py
✓ Tests de fixtures

Tiempo: 40 horas (1 semana)
Resultado: Fixtures disponibles

SEMANA 4: Mocks y Tests
────────────────────────────────────────────
✓ Crear mocks/core.py
✓ Actualizar tests existentes
✓ Agregar tests faltantes
✓ Coverage 80%+

Tiempo: 40 horas (1 semana)
Resultado: Core app completa

TOTAL CORE: 160 horas (4 semanas)
```

---

### 4.2 APP: USERS (Prioridad ALTA 🟠)

```
MÉTRICAS:
├─ Tamaño tests:      150 KB (19% del total)
├─ Tests estimados:   ~60 tests
├─ Estado:            IMPORTANTE - Algunos tests pasan
├─ Prioridad:         🟠 ALTA
└─ Tiempo estimado:   2-3 semanas

PROBLEMAS IDENTIFICADOS:
├─ Avatar upload sin mock de storage
├─ Profile update tests incompletos
├─ Sin fixtures de usuarios con roles
└─ Email tests sin mock backend

ARCHIVOS DE TEST:
tests/unit/users/
├─ test_avatar_api.py        (~30 KB)
├─ test_profile_api.py       (~35 KB)
├─ test_serializers.py       (~25 KB)
├─ test_user_model.py        (~35 KB)
└─ test_views.py             (~25 KB)
```

#### 4.2.1 Fixtures Requeridas (users)

```python
# ════════════════════════════════════════════════════════════
# tests/fixtures/users.py (EXPANDIR - actual: 3.5 KB → 150 KB)
# ════════════════════════════════════════════════════════════

import pytest
from django.contrib.auth import get_user_model
from apps.core.models import Module, Function

User = get_user_model()

# ────────────────────────────────────────
# BASIC USERS
# ────────────────────────────────────────

@pytest.fixture
def sample_user(db):
    """Usuario básico para tests."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
        is_active=True
    )

@pytest.fixture
def admin_user(db):
    """Usuario administrador."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )

@pytest.fixture
def staff_user(db):
    """Usuario staff."""
    return User.objects.create_user(
        username='staff',
        email='staff@example.com',
        password='staffpass123',
        first_name='Staff',
        last_name='User',
        is_staff=True,
        is_active=True
    )

@pytest.fixture
def inactive_user(db):
    """Usuario inactivo."""
    return User.objects.create_user(
        username='inactive',
        email='inactive@example.com',
        password='pass123',
        is_active=False
    )

# ────────────────────────────────────────
# USERS WITH MODULES
# ────────────────────────────────────────

@pytest.fixture
def user_with_modules(sample_user, sample_module, admin_module):
    """Usuario con módulos asignados."""
    sample_user.modules.add(sample_module)
    sample_user.modules.add(admin_module)
    return sample_user

@pytest.fixture
def user_with_all_permissions(sample_user, sample_module):
    """Usuario con todos los permisos de un módulo."""
    # Agregar todas las functions del módulo
    for function in sample_module.functions.all():
        sample_user.user_functions.create(
            function=function,
            is_active=True
        )
    return sample_user

# ────────────────────────────────────────
# USERS WITH SERVICES
# ────────────────────────────────────────

@pytest.fixture
def user_with_one_service(sample_user, sample_service):
    """Usuario con un servicio asignado."""
    from apps.core.models import UserServiceAccess
    UserServiceAccess.objects.create(
        user=sample_user,
        service=sample_service,
        is_active=True,
        granted_by=sample_user
    )
    return sample_user

@pytest.fixture
def user_with_multiple_services(sample_user, multiple_services):
    """Usuario con múltiples servicios."""
    from apps.core.models import UserServiceAccess
    for service in multiple_services:
        UserServiceAccess.objects.create(
            user=sample_user,
            service=service,
            is_active=True,
            granted_by=sample_user
        )
    return sample_user

# ────────────────────────────────────────
# USERS FOR SPECIFIC SCENARIOS
# ────────────────────────────────────────

@pytest.fixture
def supervisor_user(db, sample_user):
    """Usuario supervisor."""
    supervisor = User.objects.create_user(
        username='supervisor',
        email='supervisor@example.com',
        password='super123',
        is_supervisor=True
    )
    supervisor.supervised_users.add(sample_user)
    return supervisor

@pytest.fixture
def multiple_users(db):
    """Lista de usuarios para tests."""
    users = []
    for i in range(1, 11):
        user = User.objects.create_user(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password='pass123'
        )
        users.append(user)
    return users
```

#### 4.2.2 Mocks Requeridos (users)

```python
# ════════════════════════════════════════════════════════════
# tests/mocks/users.py (NUEVO - 100+ líneas)
# ════════════════════════════════════════════════════════════

from unittest.mock import Mock, patch
import pytest

# ────────────────────────────────────────
# STORAGE MOCKS (para avatars)
# ────────────────────────────────────────

@pytest.fixture
def mock_storage():
    """
    Mock del storage backend (sin AWS).
    
    CNST: NO AWS, usar filesystem local.
    """
    with patch('django.core.files.storage.default_storage') as mock:
        mock.save.return_value = 'avatars/test.jpg'
        mock.url.return_value = '/media/avatars/test.jpg'
        mock.exists.return_value = True
        mock.delete.return_value = True
        yield mock

# ────────────────────────────────────────
# EMAIL MOCKS
# ────────────────────────────────────────

@pytest.fixture
def mock_email_backend():
    """
    Mock del email backend.
    
    CNST: NO external email services.
    """
    from django.core import mail
    # Django ya tiene locmem backend, solo verificar configuración
    yield mail.outbox

# ────────────────────────────────────────
# PASSWORD RESET MOCKS
# ────────────────────────────────────────

@pytest.fixture
def mock_password_reset():
    """Mock del sistema de reset de password."""
    with patch('django.contrib.auth.tokens.default_token_generator') as mock:
        mock.make_token.return_value = 'test-token-123'
        mock.check_token.return_value = True
        yield mock
```

#### 4.2.3 Plan de Implementación (users)

```
SEMANA 1: Service Layer
────────────────────────────────────────────
✓ Crear UserProfileService
✓ Crear AvatarService
✓ Mover lógica de models

Tiempo: 40 horas

SEMANA 2: Fixtures y Mocks
────────────────────────────────────────────
✓ Expandir fixtures/users.py
✓ Crear mocks/users.py
✓ Actualizar conftest.py

Tiempo: 40 horas

SEMANA 3: Tests
────────────────────────────────────────────
✓ Actualizar tests existentes
✓ Agregar tests faltantes
✓ Coverage 85%+

Tiempo: 40 horas

TOTAL USERS: 120 horas (3 semanas)
```

---

### 4.3 APP: REPORTS (Prioridad ALTA 🔴)

```
MÉTRICAS:
├─ Tamaño tests:      83 KB (11% del total)
├─ Tests estimados:   ~40 tests
├─ Estado:            BLOQUEADO - Múltiples problemas
├─ Prioridad:         🔴 ALTA
└─ Tiempo estimado:   2 semanas

PROBLEMAS IDENTIFICADOS:
├─ CNST007 compliance tests sin mocks
├─ Report generation sin fixtures
├─ Sin mocks para servicios externos
└─ Database queries complejos

ARCHIVOS DE TEST:
tests/unit/reports/
├─ test_cnst007_compliance.py    (~20 KB) ← IMPORTANTE
├─ test_models.py                (~15 KB)
├─ test_report_model.py          (~18 KB)
├─ test_serializers.py           (~10 KB)
├─ test_services.py              (~12 KB)
└─ test_views.py                 (~8 KB)
```

#### 4.3.1 Fixtures Requeridas (reports)

```python
# ════════════════════════════════════════════════════════════
# tests/fixtures/reports.py (NUEVO - 200+ líneas)
# ════════════════════════════════════════════════════════════

import pytest
from datetime import datetime, timedelta
from apps.reports.models import Report, ReportType, ReportSchedule

# ────────────────────────────────────────
# REPORT TYPES
# ────────────────────────────────────────

@pytest.fixture
def cnst007_report_type(db):
    """Tipo de reporte CNST007."""
    return ReportType.objects.create(
        code='CNST007',
        name='Reporte CNST-007',
        description='Cumplimiento normativo',
        is_active=True,
        requires_approval=True
    )

@pytest.fixture
def daily_report_type(db):
    """Tipo de reporte diario."""
    return ReportType.objects.create(
        code='DAILY',
        name='Reporte Diario',
        description='Reporte diario de operaciones',
        is_active=True,
        requires_approval=False
    )

# ────────────────────────────────────────
# REPORTS
# ────────────────────────────────────────

@pytest.fixture
def sample_report(db, cnst007_report_type, sample_user):
    """Reporte de ejemplo."""
    return Report.objects.create(
        report_type=cnst007_report_type,
        title='Reporte Test',
        generated_by=sample_user,
        generated_at=datetime.now(),
        status='COMPLETED',
        data={'test': True}
    )

@pytest.fixture
def pending_report(db, daily_report_type, sample_user):
    """Reporte pendiente."""
    return Report.objects.create(
        report_type=daily_report_type,
        title='Reporte Pendiente',
        generated_by=sample_user,
        status='PENDING'
    )

# ────────────────────────────────────────
# REPORT DATA (para tests CNST007)
# ────────────────────────────────────────

@pytest.fixture
def cnst007_sample_data():
    """Datos de ejemplo para CNST007."""
    return {
        'period': '2024-01',
        'services': [
            {
                'numero_800': '800-123-4567',
                'llamadas_recibidas': 1000,
                'llamadas_atendidas': 950,
                'tiempo_promedio': 120,
                'nivel_servicio': 95.0
            }
        ],
        'compliance': {
            'nivel_servicio_80_20': True,
            'tiempo_respuesta_cumple': True,
            'registros_completos': True
        }
    }

@pytest.fixture
def cnst007_non_compliant_data():
    """Datos que NO cumplen CNST007."""
    return {
        'period': '2024-01',
        'services': [
            {
                'numero_800': '800-999-9999',
                'llamadas_recibidas': 1000,
                'llamadas_atendidas': 700,  # < 80% ← NO CUMPLE
                'tiempo_promedio': 300,     # > 20 seg ← NO CUMPLE
                'nivel_servicio': 70.0
            }
        ],
        'compliance': {
            'nivel_servicio_80_20': False,
            'tiempo_respuesta_cumple': False,
            'registros_completos': True
        }
    }
```

#### 4.3.2 Mocks Requeridos (reports)

```python
# ════════════════════════════════════════════════════════════
# tests/mocks/reports.py (NUEVO - 150+ líneas)
# ════════════════════════════════════════════════════════════

import pytest
from unittest.mock import Mock, patch

# ────────────────────────────────────────
# REPORT GENERATION MOCKS
# ────────────────────────────────────────

@pytest.fixture
def mock_report_generator():
    """Mock del generador de reportes."""
    mock = Mock()
    mock.generate.return_value = {
        'status': 'success',
        'report_id': 123,
        'file_path': '/tmp/report.pdf'
    }
    return mock

# ────────────────────────────────────────
# CNST007 VALIDATION MOCKS
# ────────────────────────────────────────

@pytest.fixture
def mock_cnst007_validator():
    """Mock del validador CNST007."""
    mock = Mock()
    mock.validate.return_value = {
        'compliant': True,
        'issues': [],
        'score': 100.0
    }
    return mock

# ────────────────────────────────────────
# PDF GENERATION MOCKS
# ────────────────────────────────────────

@pytest.fixture
def mock_pdf_generator():
    """
    Mock del generador de PDFs.
    
    CNST: Sin servicios externos de PDF.
    """
    with patch('apps.reports.utils.PDFGenerator') as mock:
        mock.return_value.generate.return_value = b'%PDF-1.4 fake pdf'
        yield mock
```

#### 4.3.3 Plan de Implementación (reports)

```
SEMANA 1: Service Layer + Fixtures
────────────────────────────────────────────
✓ Crear ReportService
✓ Crear CNST007ComplianceService
✓ Crear fixtures/reports.py
✓ Crear mocks/reports.py

Tiempo: 40 horas

SEMANA 2: Tests
────────────────────────────────────────────
✓ Tests CNST007 completos
✓ Tests de generación
✓ Tests de validación
✓ Coverage 80%+

Tiempo: 40 horas

TOTAL REPORTS: 80 horas (2 semanas)
```

---

### 4.4 RESUMEN DE OTRAS APPS

```
APP: ACCESS (76 KB, ~30 tests)
──────────────────────────────────────────────────────────────
Problema Principal: HasFunction import missing
Tiempo: 1.5 semanas (60 horas)
Fixtures: access.py (100+ líneas)
Prioridad: 🔴 ALTA

APP: AUDIT (68 KB, ~25 tests)
──────────────────────────────────────────────────────────────
Estado: Mayormente funcional
Tiempo: 1 semana (40 horas)
Fixtures: audit.py (80+ líneas)
Prioridad: 🟢 MEDIA

APP: AUTHENTICATION (55 KB, ~20 tests)
──────────────────────────────────────────────────────────────
Estado: Funcional
Tiempo: 1 semana (40 horas)
Mocks: JWT, OAuth backends
Prioridad: 🟢 BAJA

APP: PIPELINE (36 KB, ~15 tests)
──────────────────────────────────────────────────────────────
Problema: Scheduler tests sin mocks
Tiempo: 1.5 semanas (60 horas)
Mocks: Celery, Schedule tasks
Prioridad: 🟡 MEDIA

APP: IVR_LEGACY (20 KB, ~10 tests)
──────────────────────────────────────────────────────────────
Problema: Database ivr_legacy no configurada
Tiempo: 1 semana (40 horas)
Fixtures: IVR data
Prioridad: 🟠 MEDIA

APP: UTILS (81 KB, ~35 tests)
──────────────────────────────────────────────────────────────
Problema: network.py missing
Tiempo: 1 semana (40 horas)
Fixtures: Request utils
Prioridad: 🟡 MEDIA
```

---

**CONTINÚA EN PARTE 3...**

Secciones pendientes:
5. Plan de Fixtures Completo (conftest.py expandido)
6. Sistema de Mocks (arquitectura completa)
7. Estrategia de Refactorización (orden de implementación)
8. Roadmap semana por semana
9. Métricas de éxito
10. Riesgos
11. Conclusiones

¿Continúo con la Parte 3?

<a name="plan-fixtures"></a>
## 5. PLAN DE FIXTURES COMPLETO

### 5.1 Arquitectura de Fixtures

```
tests/
├── conftest.py                    ← Central hub (500+ líneas)
│
├── fixtures/                      ← Datos estáticos
│   ├── __init__.py
│   ├── users.py                  (150+ líneas) ← EXPANDIR
│   ├── core.py                   (200+ líneas) ← NUEVO
│   ├── reports.py                (200+ líneas) ← NUEVO
│   ├── access.py                 (100+ líneas) ← NUEVO
│   ├── audit.py                  (80+ líneas)  ← NUEVO
│   ├── pipeline.py               (100+ líneas) ← NUEVO
│   ├── ivr_legacy.py             (120+ líneas) ← NUEVO
│   └── authentication.py         (60+ líneas)  ← NUEVO
│
├── factories/                     ← Factories dinámicas
│   ├── __init__.py
│   ├── user_factory.py           (expandir)
│   ├── core.py                   (expandir)
│   ├── reports.py                ← NUEVO
│   └── ivr_legacy.py             ← NUEVO
│
└── mocks/                         ← NUEVO directorio
    ├── __init__.py
    ├── storage.py                 (sin AWS/Google)
    ├── email.py                   (sin servicios externos)
    ├── external_apis.py
    └── schedulers.py

TOTAL ESTIMADO: 2,000+ líneas de código de fixtures/mocks
```

### 5.2 conftest.py Central (Expandido)

```python
# ════════════════════════════════════════════════════════════
# tests/conftest.py (EXPANDIDO - 500+ líneas)
# ════════════════════════════════════════════════════════════

import pytest
from django.conf import settings
from django.core.management import call_command
from rest_framework.test import APIClient

# ────────────────────────────────────────────────────────────
# DATABASE SETUP
# ────────────────────────────────────────────────────────────

@pytest.fixture(scope='session')
def django_db_setup():
    """
    Setup completo de bases de datos.
    
    CNST: Solo SQLite in-memory (NO PostgreSQL/MariaDB).
    """
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'ATOMIC_REQUESTS': False,
            'CONN_MAX_AGE': 0,
        },
        'ivr_legacy': {  # ← AGREGAR para IVR tests
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'ATOMIC_REQUESTS': False,
            'CONN_MAX_AGE': 0,
        }
    }
    
    # Ejecutar migraciones
    call_command('migrate', '--database=default', verbosity=0)
    call_command('migrate', '--database=ivr_legacy', verbosity=0)

@pytest.fixture(scope='function')
def db_with_data(db):
    """
    Database con datos iniciales para cada test.
    
    Ejecuta después de crear la DB pero antes del test.
    """
    # Cargar datos iniciales si es necesario
    # call_command('loaddata', 'initial_data.json', verbosity=0)
    yield

# ────────────────────────────────────────────────────────────
# API CLIENTS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """Cliente API sin autenticación."""
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, sample_user):
    """Cliente API autenticado con usuario normal."""
    api_client.force_authenticate(user=sample_user)
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    """Cliente API autenticado como admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.fixture
def staff_client(api_client, staff_user):
    """Cliente API autenticado como staff."""
    api_client.force_authenticate(user=staff_user)
    return api_client

# ────────────────────────────────────────────────────────────
# REQUEST FACTORIES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def request_factory():
    """Factory para crear requests de Django."""
    from django.test import RequestFactory
    return RequestFactory()

@pytest.fixture
def authenticated_request(request_factory, sample_user):
    """Request autenticado."""
    request = request_factory.get('/')
    request.user = sample_user
    return request

@pytest.fixture
def admin_request(request_factory, admin_user):
    """Request de admin."""
    request = request_factory.get('/')
    request.user = admin_user
    return request

# ────────────────────────────────────────────────────────────
# FILE UPLOADS (sin AWS/Google)
# ────────────────────────────────────────────────────────────

@pytest.fixture
def sample_file():
    """
    Archivo de prueba en memoria.
    
    CNST: NO usar AWS S3, NO usar Google Cloud Storage.
    Usar filesystem local o in-memory.
    """
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    return SimpleUploadedFile(
        "test.txt",
        b"test file content",
        content_type="text/plain"
    )

@pytest.fixture
def sample_image():
    """Imagen de prueba."""
    from PIL import Image
    from io import BytesIO
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    # Crear imagen 100x100
    image = Image.new('RGB', (100, 100), color='red')
    image_io = BytesIO()
    image.save(image_io, format='JPEG')
    image_io.seek(0)
    
    return SimpleUploadedFile(
        "test.jpg",
        image_io.getvalue(),
        content_type="image/jpeg"
    )

@pytest.fixture
def sample_csv():
    """CSV de prueba."""
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    csv_content = b"header1,header2\nvalue1,value2\nvalue3,value4"
    
    return SimpleUploadedFile(
        "test.csv",
        csv_content,
        content_type="text/csv"
    )

# ────────────────────────────────────────────────────────────
# EMAIL TESTING (sin servicios externos)
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mailoutbox(settings):
    """
    Buzón de email para testing.
    
    CNST: NO SendGrid, NO AWS SES, NO Mailgun.
    Usar locmem backend de Django.
    """
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    from django.core import mail
    mail.outbox = []
    yield mail.outbox
    mail.outbox = []

# ────────────────────────────────────────────────────────────
# DATETIME FIXTURES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def freeze_time():
    """Congelar tiempo para tests determinísticos."""
    from freezegun import freeze_time as _freeze_time
    with _freeze_time('2024-01-15 10:00:00'):
        yield

@pytest.fixture
def today():
    """Fecha de hoy."""
    from datetime import date
    return date.today()

@pytest.fixture
def now():
    """Datetime ahora."""
    from datetime.datetime import now
    return now()

# ────────────────────────────────────────────────────────────
# LOGGING CAPTURE
# ────────────────────────────────────────────────────────────

@pytest.fixture
def captured_logs(caplog):
    """Capturar logs durante tests."""
    import logging
    caplog.set_level(logging.INFO)
    return caplog

# ────────────────────────────────────────────────────────────
# CACHE FIXTURES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def cache(settings):
    """
    Cache local para testing.
    
    CNST: NO Redis externo, NO Memcached externo.
    Usar cache local en memoria.
    """
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-cache',
        }
    }
    from django.core.cache import cache
    cache.clear()
    yield cache
    cache.clear()

# ────────────────────────────────────────────────────────────
# CELERY MOCKS (sin servicios externos)
# ────────────────────────────────────────────────────────────

@pytest.fixture
def celery_app(settings):
    """
    Celery app para testing.
    
    CNST: NO usar RabbitMQ externo, NO usar Redis externo.
    Usar ALWAYS_EAGER para tests síncronos.
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    
    from celery import current_app
    return current_app

# ────────────────────────────────────────────────────────────
# IMPORTS DE FIXTURES ESPECÍFICAS
# ────────────────────────────────────────────────────────────

# Importar fixtures de cada app
pytest_plugins = [
    'tests.fixtures.users',
    'tests.fixtures.core',
    'tests.fixtures.reports',
    'tests.fixtures.access',
    'tests.fixtures.audit',
    'tests.fixtures.pipeline',
    'tests.fixtures.ivr_legacy',
    'tests.fixtures.authentication',
]

# FIN conftest.py
# TOTAL: ~500 líneas
```

---

<a name="sistema-mocks"></a>
## 6. SISTEMA DE MOCKS

### 6.1 Arquitectura de Mocks

```
PRINCIPIO: Mock TODOS los servicios externos
CNST: NO AWS, NO Google, NO servicios cloud, NO Docker

tests/mocks/
├── __init__.py
├── storage.py              ← Mock storage (NO S3/GCS)
├── email.py                ← Mock email (NO SendGrid/SES)
├── external_apis.py        ← Mock APIs externas
├── schedulers.py           ← Mock Celery/Schedule
├── payment_gateways.py     ← Mock gateways de pago
└── monitoring.py           ← Mock Sentry/New Relic
```

### 6.2 Storage Mocks (sin AWS/Google)

```python
# ════════════════════════════════════════════════════════════
# tests/mocks/storage.py (200+ líneas)
# ════════════════════════════════════════════════════════════

"""
Mocks de storage sin servicios cloud.

CNST COMPLIANCE:
✗ NO AWS S3
✗ NO Google Cloud Storage
✗ NO Azure Blob Storage
✓ SÍ filesystem local
✓ SÍ in-memory storage
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
import os

# ────────────────────────────────────────────────────────────
# FILESYSTEM STORAGE MOCK
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_file_storage():
    """
    Mock del filesystem storage (NO cloud).
    
    Simula almacenamiento local sin usar AWS/Google.
    """
    mock = Mock()
    
    # Simular archivos guardados en memoria
    mock._files = {}
    
    def save(name, content, max_length=None):
        """Guardar archivo en memoria."""
        mock._files[name] = content.read()
        return name
    
    def open(name, mode='rb'):
        """Abrir archivo desde memoria."""
        if name not in mock._files:
            raise FileNotFoundError(f"File {name} not found")
        return BytesIO(mock._files[name])
    
    def exists(name):
        """Verificar si existe."""
        return name in mock._files
    
    def delete(name):
        """Eliminar archivo."""
        if name in mock._files:
            del mock._files[name]
    
    def url(name):
        """URL local (NO cloud)."""
        return f'/media/{name}'
    
    def size(name):
        """Tamaño del archivo."""
        if name in mock._files:
            return len(mock._files[name])
        return 0
    
    mock.save = save
    mock.open = open
    mock.exists = exists
    mock.delete = delete
    mock.url = url
    mock.size = size
    
    return mock

@pytest.fixture
def patch_default_storage(mock_file_storage):
    """Patch del default storage de Django."""
    with patch('django.core.files.storage.default_storage', mock_file_storage):
        yield mock_file_storage

# ────────────────────────────────────────────────────────────
# IMAGE PROCESSING MOCKS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_image_processor():
    """
    Mock de procesamiento de imágenes.
    
    Para tests de avatares, thumbnails, etc.
    """
    mock = Mock()
    
    def resize(image, size):
        """Simular resize."""
        return Mock(size=size)
    
    def crop(image, box):
        """Simular crop."""
        return Mock()
    
    def save(image, format='JPEG', quality=85):
        """Simular save."""
        return BytesIO(b'fake image data')
    
    mock.resize = resize
    mock.crop = crop
    mock.save = save
    
    return mock

# ────────────────────────────────────────────────────────────
# MEDIA FILES CLEANUP
# ────────────────────────────────────────────────────────────

@pytest.fixture
def cleanup_media(settings):
    """
    Limpiar archivos de media después de tests.
    
    IMPORTANTE: Limpiar para no dejar basura.
    """
    # Setup
    import tempfile
    media_root = tempfile.mkdtemp()
    settings.MEDIA_ROOT = media_root
    
    yield
    
    # Cleanup
    import shutil
    if os.path.exists(media_root):
        shutil.rmtree(media_root)
```

### 6.3 Email Mocks (sin servicios externos)

```python
# ════════════════════════════════════════════════════════════
# tests/mocks/email.py (150+ líneas)
# ════════════════════════════════════════════════════════════

"""
Mocks de email sin servicios externos.

CNST COMPLIANCE:
✗ NO SendGrid
✗ NO AWS SES
✗ NO Mailgun
✗ NO servicios SMTP externos
✓ SÍ locmem backend de Django
"""

import pytest
from unittest.mock import Mock, patch
from django.core import mail

# ────────────────────────────────────────────────────────────
# EMAIL BACKEND MOCK
# ────────────────────────────────────────────────────────────

@pytest.fixture
def email_outbox(settings):
    """
    Buzón de email en memoria.
    
    CNST: Usar locmem backend (NO servicios externos).
    """
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    mail.outbox = []
    yield mail.outbox
    mail.outbox = []

@pytest.fixture
def email_helpers(email_outbox):
    """Helpers para validar emails."""
    
    class EmailHelpers:
        @staticmethod
        def get_by_subject(subject):
            """Obtener email por subject."""
            for email in email_outbox:
                if subject in email.subject:
                    return email
            return None
        
        @staticmethod
        def get_by_recipient(email_address):
            """Obtener emails por destinatario."""
            return [
                email for email in email_outbox
                if email_address in email.to
            ]
        
        @staticmethod
        def count():
            """Contar emails enviados."""
            return len(email_outbox)
        
        @staticmethod
        def clear():
            """Limpiar outbox."""
            mail.outbox = []
        
        @staticmethod
        def last():
            """Último email enviado."""
            return email_outbox[-1] if email_outbox else None
    
    return EmailHelpers()

# ────────────────────────────────────────────────────────────
# EMAIL TEMPLATES MOCK
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_email_template():
    """Mock de templates de email."""
    mock = Mock()
    mock.render.return_value = '<html>Test Email</html>'
    return mock

# ────────────────────────────────────────────────────────────
# MASS EMAIL MOCK
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_mass_email():
    """
    Mock para envío masivo de emails.
    
    CNST: Sin rate limits de servicios externos.
    """
    with patch('django.core.mail.send_mass_mail') as mock:
        mock.return_value = 100  # Número de emails "enviados"
        yield mock
```

### 6.4 External APIs Mocks

```python
# ════════════════════════════════════════════════════════════
# tests/mocks/external_apis.py (200+ líneas)
# ════════════════════════════════════════════════════════════

"""
Mocks de APIs externas.

CNST COMPLIANCE:
✗ NO llamadas HTTP reales
✗ NO dependencias de servicios externos
✓ SÍ mocks completamente locales
"""

import pytest
from unittest.mock import Mock, patch
import requests_mock

# ────────────────────────────────────────────────────────────
# HTTP CLIENT MOCKS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_requests():
    """
    Mock de requests HTTP.
    
    Para testear integraciones con APIs externas sin llamadas reales.
    """
    with requests_mock.Mocker() as m:
        # Mock de API externa genérica
        m.get(
            'https://api.example.com/data',
            json={'status': 'success', 'data': []}
        )
        
        m.post(
            'https://api.example.com/data',
            json={'status': 'success', 'id': 123}
        )
        
        # Mock de error
        m.get(
            'https://api.example.com/error',
            status_code=500,
            json={'error': 'Internal Server Error'}
        )
        
        yield m

# ────────────────────────────────────────────────────────────
# THIRD PARTY SERVICE MOCKS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_payment_gateway():
    """Mock de gateway de pago."""
    mock = Mock()
    mock.charge.return_value = {
        'transaction_id': 'txn_123',
        'status': 'approved',
        'amount': 100.00
    }
    return mock

@pytest.fixture
def mock_sms_service():
    """
    Mock de servicio SMS.
    
    CNST: NO Twilio, NO servicios SMS externos.
    """
    mock = Mock()
    mock.send.return_value = {
        'message_id': 'msg_123',
        'status': 'sent'
    }
    return mock
```

### 6.5 Scheduler Mocks (sin Celery externo)

```python
# ════════════════════════════════════════════════════════════
# tests/mocks/schedulers.py (150+ líneas)
# ════════════════════════════════════════════════════════════

"""
Mocks de schedulers y tasks.

CNST COMPLIANCE:
✗ NO RabbitMQ externo
✗ NO Redis externo como broker
✓ SÍ Celery ALWAYS_EAGER mode
✓ SÍ ejecución síncrona en tests
"""

import pytest
from unittest.mock import Mock, patch
from celery import current_app

# ────────────────────────────────────────────────────────────
# CELERY TASK MOCKS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def celery_eager(settings):
    """
    Celery en modo eager (síncrono).
    
    CNST: NO usar broker externo, ejecutar tasks síncronamente.
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    settings.CELERY_BROKER_URL = 'memory://'
    settings.CELERY_RESULT_BACKEND = 'cache+memory://'
    
    yield current_app

@pytest.fixture
def mock_async_task():
    """Mock de task asíncrona."""
    mock = Mock()
    mock.delay.return_value = Mock(id='task-123', state='PENDING')
    mock.apply_async.return_value = Mock(id='task-456', state='PENDING')
    return mock

# ────────────────────────────────────────────────────────────
# SCHEDULED TASKS MOCKS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_scheduler():
    """Mock del scheduler (celery beat)."""
    mock = Mock()
    mock.schedule.return_value = {
        'task_id': 'scheduled-123',
        'next_run': '2024-01-15 10:00:00'
    }
    return mock
```

### 6.6 Monitoring Mocks (sin Sentry/New Relic)

```python
# ════════════════════════════════════════════════════════════
# tests/mocks/monitoring.py (100+ líneas)
# ════════════════════════════════════════════════════════════

"""
Mocks de servicios de monitoreo.

CNST COMPLIANCE:
✗ NO Sentry
✗ NO New Relic
✗ NO Datadog
✓ SÍ logging local
"""

import pytest
from unittest.mock import Mock, patch

# ────────────────────────────────────────────────────────────
# SENTRY MOCK
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_sentry():
    """
    Mock de Sentry.
    
    CNST: NO enviar a Sentry real.
    """
    with patch('sentry_sdk.capture_exception') as mock:
        yield mock

@pytest.fixture
def mock_sentry_init():
    """Mock de inicialización de Sentry."""
    with patch('sentry_sdk.init') as mock:
        yield mock

# ────────────────────────────────────────────────────────────
# METRICS MOCK
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_metrics():
    """Mock de métricas."""
    mock = Mock()
    mock.increment.return_value = None
    mock.gauge.return_value = None
    mock.histogram.return_value = None
    return mock
```

---

**CONTINÚA EN PARTE 4...**

Secciones pendientes:
7. Estrategia de Refactorización (orden y metodología)
8. Roadmap semana por semana (12 semanas)
9. Métricas de éxito
10. Riesgos y mitigación
11. Conclusiones

¿Continúo con la Parte 4?

<a name="estrategia"></a>
## 7. ESTRATEGIA DE REFACTORIZACIÓN

### 7.1 Principios Guía

```
PRINCIPIOS DE IMPLEMENTACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. INCREMENTAL
   ✓ Una app a la vez
   ✓ No romper funcionalidad existente
   ✓ Tests verdes en cada paso

2. SERVICE LAYER FIRST
   ✓ Refactorizar código antes de tests
   ✓ Crear services antes de fixtures
   ✓ Models delgados, services gordos

3. FIXTURES DESPUÉS
   ✓ Crear fixtures una vez que service existe
   ✓ Usar factories para datos dinámicos
   ✓ Fixtures para datos estáticos

4. TESTS AL FINAL
   ✓ Actualizar tests existentes
   ✓ Agregar tests faltantes
   ✓ Validar cobertura >80%

5. DOCUMENTAR TODO
   ✓ Docstrings en todos los services
   ✓ Type hints everywhere
   ✓ Ejemplos de uso

6. CNST COMPLIANCE
   ✓ Sin servicios externos
   ✓ Sin Docker
   ✓ Solo SQLite
   ✓ Mocks locales
```

### 7.2 Orden de Implementación

```
ORDEN ESTRATÉGICO (por dependencias):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FASE 1: FUNDAMENTOS (Semanas 1-2)
├─ 1. UTILS              (base para todas)
│  └─ network.py, request_utils, etc
│
├─ 2. AUTHENTICATION     (auth base)
│  └─ JWT, sessions, permissions
│
└─ 3. USERS              (usuarios base)
   └─ Profile, avatars, preferences

FASE 2: CORE (Semanas 3-6)
├─ 4. CORE               (crítico)
│  ├─ ServiceAccessService
│  ├─ ModuleService
│  └─ FunctionService
│
└─ 5. ACCESS             (depende de core)
   └─ Permissions, RBAC

FASE 3: FEATURES (Semanas 7-10)
├─ 6. REPORTS            (independiente)
│  └─ CNST007, generators
│
├─ 7. AUDIT              (logging)
│  └─ Audit trails, logs
│
├─ 8. PIPELINE           (procesos)
│  └─ ETL, schedulers
│
└─ 9. IVR_LEGACY         (legacy)
   └─ IVR adapters

FASE 4: POLISH (Semanas 11-12)
├─ Coverage final >90%
├─ Documentación completa
├─ Performance tuning
└─ Code review final
```

### 7.3 Metodología por App

```python
# ════════════════════════════════════════════════════════════
# TEMPLATE DE REFACTORIZACIÓN POR APP
# ════════════════════════════════════════════════════════════

def refactor_app(app_name):
    """
    Proceso estándar para refactorizar una app.
    
    Duración: 1-4 semanas dependiendo tamaño.
    """
    
    # ────────────────────────────────────────────────────────
    # PASO 1: ANÁLISIS (0.5 días)
    # ────────────────────────────────────────────────────────
    analyze(app_name)
    # - Identificar models con lógica
    # - Listar tests existentes
    # - Identificar dependencias
    
    # ────────────────────────────────────────────────────────
    # PASO 2: SERVICE LAYER (3-5 días)
    # ────────────────────────────────────────────────────────
    create_services(app_name)
    # - Crear apps/{app}/services/
    # - Mover lógica de models a services
    # - Type hints + docstrings
    # - Tests unitarios de services
    
    # ────────────────────────────────────────────────────────
    # PASO 3: FIXTURES (1-2 días)
    # ────────────────────────────────────────────────────────
    create_fixtures(app_name)
    # - Crear tests/fixtures/{app}.py
    # - Fixtures para cada model
    # - Fixtures para escenarios comunes
    
    # ────────────────────────────────────────────────────────
    # PASO 4: FACTORIES (1 día)
    # ────────────────────────────────────────────────────────
    create_factories(app_name)
    # - Crear tests/factories/{app}.py
    # - Factory para cada model
    # - SubFactories para relaciones
    
    # ────────────────────────────────────────────────────────
    # PASO 5: MOCKS (1-2 días)
    # ────────────────────────────────────────────────────────
    create_mocks(app_name)
    # - Crear tests/mocks/{app}.py
    # - Mock servicios externos
    # - Mock APIs
    
    # ────────────────────────────────────────────────────────
    # PASO 6: ACTUALIZAR TESTS (2-3 días)
    # ────────────────────────────────────────────────────────
    update_tests(app_name)
    # - Actualizar tests existentes
    # - Usar nuevos services
    # - Usar fixtures/mocks
    
    # ────────────────────────────────────────────────────────
    # PASO 7: TESTS FALTANTES (2-3 días)
    # ────────────────────────────────────────────────────────
    add_missing_tests(app_name)
    # - Identificar casos no cubiertos
    # - Crear tests faltantes
    # - Coverage >80%
    
    # ────────────────────────────────────────────────────────
    # PASO 8: DOCUMENTACIÓN (1 día)
    # ────────────────────────────────────────────────────────
    document(app_name)
    # - README de la app
    # - Docstrings completos
    # - Ejemplos de uso
    
    # ────────────────────────────────────────────────────────
    # PASO 9: CODE REVIEW (0.5 día)
    # ────────────────────────────────────────────────────────
    code_review(app_name)
    # - Revisar código
    # - Validar estándares
    # - Aprobar merge
    
    # ────────────────────────────────────────────────────────
    # TOTAL: 12-19 días por app (promedio: 15 días = 3 semanas)
    # ────────────────────────────────────────────────────────
```

---

<a name="roadmap"></a>
## 8. ROADMAP DE IMPLEMENTACIÓN

### 8.1 Timeline General (12 semanas)

```
ROADMAP COMPLETO - 12 SEMANAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MES 1: FUNDAMENTOS + CORE
├─ Semana 1:  UTILS + AUTHENTICATION
├─ Semana 2:  USERS
├─ Semana 3:  CORE (parte 1)
└─ Semana 4:  CORE (parte 2)

MES 2: FEATURES PRINCIPALES
├─ Semana 5:  ACCESS
├─ Semana 6:  REPORTS (parte 1)
├─ Semana 7:  REPORTS (parte 2)
└─ Semana 8:  AUDIT

MES 3: FEATURES RESTANTES + POLISH
├─ Semana 9:  PIPELINE + IVR_LEGACY
├─ Semana 10: Coverage final
├─ Semana 11: Documentación completa
└─ Semana 12: Code review + deploy

RESULTADO FINAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 9 apps refactorizadas
✓ ~294 tests funcionando
✓ Cobertura 90%+
✓ Service Layer completo
✓ 2,000+ líneas de fixtures/mocks
✓ Arquitectura enterprise-grade
```

### 8.2 Semana por Semana (Detallado)

```
┌────────────────────────────────────────────────────────────┐
│ SEMANA 1: UTILS + AUTHENTICATION                           │
├────────────────────────────────────────────────────────────┤
│ Objetivo: Bases fundamentales                              │
│                                                             │
│ Lunes-Martes: UTILS                                         │
│ ├─ Crear apps/utils/network.py                             │
│ ├─ Crear apps/utils/request_utils.py                       │
│ ├─ Tests unitarios                                          │
│ └─ 35 tests desbloqueados                                   │
│                                                             │
│ Miércoles-Viernes: AUTHENTICATION                           │
│ ├─ Crear AuthenticationService                              │
│ ├─ Fixtures/mocks JWT                                       │
│ ├─ Actualizar tests                                         │
│ └─ 20 tests funcionando                                     │
│                                                             │
│ Resultado: 55 tests ✓ (19%)                                 │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ SEMANA 2: USERS                                             │
├────────────────────────────────────────────────────────────┤
│ Objetivo: Sistema de usuarios completo                      │
│                                                             │
│ Lunes-Martes: Service Layer                                 │
│ ├─ Crear UserProfileService                                 │
│ ├─ Crear AvatarService                                      │
│ └─ Tests unitarios services                                 │
│                                                             │
│ Miércoles: Fixtures                                         │
│ ├─ Expandir fixtures/users.py                               │
│ ├─ Crear factories/users.py                                 │
│ └─ 15+ fixtures disponibles                                 │
│                                                             │
│ Jueves-Viernes: Tests                                       │
│ ├─ Actualizar tests existentes                              │
│ ├─ Agregar tests faltantes                                  │
│ ├─ Mocks de storage (avatars)                               │
│ └─ 60 tests funcionando                                     │
│                                                             │
│ Resultado: 115 tests ✓ (39%)                                │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ SEMANAS 3-4: CORE (CRÍTICO)                                 │
├────────────────────────────────────────────────────────────┤
│ Objetivo: App más grande, base del sistema                  │
│                                                             │
│ Semana 3:                                                   │
│ Lunes-Martes: ServiceAccessService                          │
│ ├─ Crear apps/core/services/service_access.py               │
│ ├─ 500+ líneas de código                                    │
│ ├─ Mover lógica de UserServiceAccess                        │
│ └─ 50+ tests desbloqueados                                  │
│                                                             │
│ Miércoles: ModuleService                                    │
│ ├─ Crear apps/core/services/module.py                       │
│ └─ Lógica de módulos                                        │
│                                                             │
│ Jueves-Viernes: FunctionService + Fixtures                   │
│ ├─ Crear apps/core/services/function.py                     │
│ ├─ Crear fixtures/core.py (200+ líneas)                     │
│ └─ Factories completas                                       │
│                                                             │
│ Semana 4:                                                   │
│ Lunes-Miércoles: Tests                                      │
│ ├─ Actualizar test_service_access.py                        │
│ ├─ Actualizar test_core_models.py                           │
│ ├─ Actualizar test_core_serializers.py                      │
│ └─ Agregar tests faltantes                                  │
│                                                             │
│ Jueves-Viernes: Coverage + Polish                           │
│ ├─ Completar coverage >85%                                  │
│ ├─ Documentación                                             │
│ └─ 80 tests funcionando                                     │
│                                                             │
│ Resultado: 195 tests ✓ (66%)                                │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ SEMANA 5: ACCESS                                            │
├────────────────────────────────────────────────────────────┤
│ Objetivo: Sistema de permisos completo                       │
│                                                             │
│ Lunes: Fix Imports                                          │
│ ├─ Crear alias HasFunction = HasModuleAccess                │
│ └─ 30 tests desbloqueados                                   │
│                                                             │
│ Martes-Miércoles: Service Layer                             │
│ ├─ Crear AccessControlService                               │
│ └─ PermissionService                                         │
│                                                             │
│ Jueves-Viernes: Fixtures + Tests                            │
│ ├─ Crear fixtures/access.py                                 │
│ ├─ Actualizar tests                                         │
│ └─ 30 tests funcionando                                     │
│                                                             │
│ Resultado: 225 tests ✓ (76%)                                │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ SEMANAS 6-7: REPORTS                                        │
├────────────────────────────────────────────────────────────┤
│ Objetivo: Sistema de reportes CNST007 completo              │
│                                                             │
│ Semana 6:                                                   │
│ Lunes-Martes: Service Layer                                 │
│ ├─ Crear ReportService                                      │
│ ├─ Crear CNST007ComplianceService                           │
│ └─ Lógica de validación                                     │
│                                                             │
│ Miércoles-Viernes: Fixtures + Mocks                         │
│ ├─ Crear fixtures/reports.py (200+ líneas)                  │
│ ├─ Crear mocks/reports.py                                   │
│ ├─ Mock PDF generator                                       │
│ └─ Mock validadores                                         │
│                                                             │
│ Semana 7:                                                   │
│ Lunes-Jueves: Tests                                         │
│ ├─ test_cnst007_compliance.py completo                       │
│ ├─ test_report_model.py                                     │
│ ├─ test_services.py                                         │
│ └─ 40 tests funcionando                                     │
│                                                             │
│ Viernes: Coverage                                           │
│ └─ Coverage >80%                                            │
│                                                             │
│ Resultado: 265 tests ✓ (90%)                                │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ SEMANA 8: AUDIT                                             │
├────────────────────────────────────────────────────────────┤
│ Objetivo: Sistema de auditoría completo                      │
│                                                             │
│ Lunes-Martes: Service Layer                                 │
│ ├─ Crear AuditLogService (si falta)                         │
│ └─ Mejorar servicios existentes                             │
│                                                             │
│ Miércoles-Viernes: Fixtures + Tests                         │
│ ├─ Crear fixtures/audit.py                                  │
│ ├─ Actualizar tests                                         │
│ └─ 25 tests funcionando                                     │
│                                                             │
│ Resultado: 290 tests ✓ (98%)                                │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ SEMANA 9: PIPELINE + IVR_LEGACY                             │
├────────────────────────────────────────────────────────────┤
│ Objetivo: Features restantes                                │
│                                                             │
│ Lunes-Miércoles: PIPELINE                                   │
│ ├─ Fix DB config ivr_legacy                                 │
│ ├─ Crear fixtures/ivr_legacy.py                             │
│ └─ 10 tests funcionando                                     │
│                                                             │
│ Jueves-Viernes: IVR_LEGACY                                  │
│ ├─ Mocks de scheduler                                       │
│ ├─ Fixtures pipeline                                        │
│ └─ 15 tests funcionando                                     │
│                                                             │
│ Resultado: 315 tests ✓ (107% - más que estimado)            │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ SEMANA 10: COVERAGE FINAL                                   │
├────────────────────────────────────────────────────────────┤
│ Objetivo: 90%+ cobertura en todas las apps                  │
│                                                             │
│ Lunes-Miércoles: Tests faltantes                            │
│ ├─ Identificar gaps de cobertura                            │
│ ├─ Crear tests faltantes                                    │
│ └─ Edge cases                                               │
│                                                             │
│ Jueves-Viernes: Integration tests                           │
│ ├─ Tests de integración entre apps                          │
│ ├─ tests/integration/ (nuevo)                               │
│ └─ Flujos completos                                         │
│                                                             │
│ Resultado: 350+ tests ✓, Coverage 90%+                      │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ SEMANA 11: DOCUMENTACIÓN COMPLETA                           │
├────────────────────────────────────────────────────────────┤
│ Objetivo: Documentación enterprise-grade                     │
│                                                             │
│ Lunes-Martes: READMEs                                       │
│ ├─ README principal                                         │
│ ├─ README por app                                           │
│ └─ README de tests                                          │
│                                                             │
│ Miércoles: Docstrings                                       │
│ ├─ Completar docstrings faltantes                           │
│ ├─ Google style                                             │
│ └─ Type hints everywhere                                    │
│                                                             │
│ Jueves-Viernes: Guías                                       │
│ ├─ Guía de testing                                          │
│ ├─ Guía de fixtures                                         │
│ ├─ Guía de service layer                                    │
│ └─ Best practices                                           │
│                                                             │
│ Resultado: Documentación completa                           │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ SEMANA 12: CODE REVIEW + POLISH                             │
├────────────────────────────────────────────────────────────┤
│ Objetivo: Validación final y deploy                         │
│                                                             │
│ Lunes-Martes: Code Review                                   │
│ ├─ Revisar TODO el código refactorizado                     │
│ ├─ Validar estándares                                       │
│ └─ Corregir issues                                          │
│                                                             │
│ Miércoles: Performance                                      │
│ ├─ Optimizar queries lentos                                 │
│ ├─ Optimizar fixtures                                       │
│ └─ Tests <5 segundos                                        │
│                                                             │
│ Jueves: Pre-commit hooks                                    │
│ ├─ Configurar pre-commit local                              │
│ ├─ pytest hook                                              │
│ ├─ coverage hook                                            │
│ └─ flake8/black hooks                                       │
│                                                             │
│ Viernes: Deploy + Celebración                               │
│ ├─ Merge a main                                             │
│ ├─ Deploy a staging                                         │
│ └─ 🎉 PROYECTO COMPLETO 🎉                                  │
│                                                             │
│ Resultado: Sistema en producción                            │
└────────────────────────────────────────────────────────────┘
```

---

<a name="metricas"></a>
## 9. MÉTRICAS DE ÉXITO

### 9.1 KPIs Cuantitativos

```
ANTES (Actual)          DESPUÉS (Objetivo)         GANANCIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TESTS:
37 tests pasando        294+ tests pasando         +257 tests
13% pasando             100% pasando               +87%
232 tests bloqueados    0 tests bloqueados         -232 tests

COBERTURA:
~13% líneas             90%+ líneas                +77%
~6,500 líneas           45,000+ líneas             +38,500 líneas

TIEMPO EJECUCIÓN:
~30 segundos            <5 segundos                6x más rápido
(solo 37 tests)         (todos los tests)

VELOCIDAD DE DESARROLLO:
Bug fix: 2-4 horas     Bug fix: 30 min             4-8x más rápido
Feature: 1-2 semanas   Feature: 3-5 días           2-3x más rápido

CALIDAD DE CÓDIGO:
Models gordos           Models delgados            ✓ Service Layer
Sin services            Services completos          ✓ Clean Code
Sin type hints          Type hints everywhere       ✓ Type safety
Docs parciales          Docs completas              ✓ Mantenible
```

### 9.2 KPIs Cualitativos

```
MÉTRICA                 ANTES       DESPUÉS      IMPACTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquitectura            ❌ Fat      ✅ Service   Clean Code
                        Models      Layer

Testabilidad            ❌ Difícil  ✅ Fácil     Mocks simples
                        (DB always) (in-memory)

Reutilización           ❌ Baja     ✅ Alta      DRY total

Mantenibilidad          ❌ Difícil  ✅ Fácil     12x más rápido

Onboarding              2-3 meses   2 semanas    6x más rápido
(nuevo dev)

CI/CD                   ❌ No       ✅ Sí        Deployments
                        funciona    funciona     automáticos

Confianza del equipo    ❌ Baja     ✅ Alta      Menos bugs
                        (sin tests) (tests ok)   en producción

Deuda técnica           ❌ Alta     ✅ Baja      Sostenible
```

### 9.3 Validación de Éxito

```python
# ════════════════════════════════════════════════════════════
# CRITERIOS DE ÉXITO - CHECKLIST
# ════════════════════════════════════════════════════════════

✓ TESTS
  [✓] 294+ tests ejecutándose
  [✓] 0 tests bloqueados
  [✓] 100% tests pasando
  [✓] <5 segundos tiempo total
  [✓] 0 dependencias externas

✓ COBERTURA
  [✓] >90% líneas de código
  [✓] >85% por app
  [✓] >95% en código crítico (services)

✓ ARQUITECTURA
  [✓] Service Layer en 9 apps
  [✓] Models delgados (<100 líneas)
  [✓] Services documentados
  [✓] Type hints everywhere

✓ FIXTURES
  [✓] 2,000+ líneas de fixtures
  [✓] 50+ fixtures disponibles
  [✓] Factories para todos los models
  [✓] Mocks para servicios externos

✓ DOCUMENTACIÓN
  [✓] README principal completo
  [✓] README por app
  [✓] Guía de testing
  [✓] Docstrings Google style

✓ CI/CD
  [✓] Pre-commit hooks funcionando
  [✓] Tests ejecutables localmente
  [✓] Sin dependencias externas (CNST ok)

✓ EQUIPO
  [✓] 2+ devs capacitados
  [✓] Knowledge transfer completo
  [✓] Documentación entregada
```

---

<a name="riesgos"></a>
## 10. RIESGOS Y MITIGACIÓN

### 10.1 Riesgos Técnicos

```
RIESGO 1: PostgreSQL vs SQLite Incompatibilidades
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Probabilidad: MEDIA
Impacto: BAJO

Descripción:
SQLite y PostgreSQL tienen diferencias SQL que pueden
causar tests que pasan en SQLite pero fallan en producción.

Mitigación:
✓ Usar SQL estándar cuando sea posible
✓ Tests semanales en PostgreSQL staging
✓ Documentar diferencias conocidas
✓ Dual-database strategy (ver v1.0.0)

Contingencia:
- Si falla en producción: rollback inmediato
- Agregar tests específicos para PostgreSQL
- Considerar pytest-django-queries para validar SQL
```

```
RIESGO 2: Refactoring Rompe Funcionalidad
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Probabilidad: MEDIA
Impacto: ALTO

Descripción:
Al mover lógica de models a services, podemos
introducir bugs sutiles en producción.

Mitigación:
✓ Hacer refactoring incremental (una app a la vez)
✓ Tests verdes en cada paso
✓ Code review obligatorio
✓ Deploy gradual (staging → production)
✓ Backward compatibility temporal

Contingencia:
- Feature flags para rollback rápido
- Monitoring exhaustivo post-deploy
- Plan de rollback en <15 minutos
```

```
RIESGO 3: Tiempo de Implementación Excede Estimado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Probabilidad: MEDIA
Impacto: MEDIO

Descripción:
12 semanas puede ser insuficiente si encontramos
problemas no anticipados.

Mitigación:
✓ Buffer de 2 semanas (semanas 13-14)
✓ Priorizar apps críticas primero (core, users)
✓ Parallelizar trabajo cuando posible
✓ Daily standups para detectar bloqueos

Contingencia:
- Reducir scope: postponer apps menos críticas
- Extender timeline a 16 semanas
- Agregar desarrollador adicional
```

### 10.2 Riesgos de Equipo

```
RIESGO 4: Falta de Buy-in del Equipo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Probabilidad: BAJA
Impacto: ALTO

Descripción:
El equipo puede resistirse al cambio o no ver el valor.

Mitigación:
✓ Sesiones de capacitación
✓ Mostrar beneficios concretos (tests más rápidos)
✓ Involucrar en decisiones técnicas
✓ Pair programming durante refactoring

Contingencia:
- 1-on-1s para entender resistencia
- Ajustar approach según feedback
- Champion interno del proyecto
```

### 10.3 Matriz de Riesgos

```
RIESGO                          PROB    IMP    PRIORIDAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PostgreSQL incompatibilidades   MEDIA   BAJO   🟡 MEDIA
Romper funcionalidad            MEDIA   ALTO   🔴 ALTA
Tiempo excede estimado          MEDIA   MEDIO  🟡 MEDIA
Falta de buy-in                 BAJA    ALTO   🟠 MEDIA
Bugs en producción              BAJA    ALTO   🟠 MEDIA
P�rdida de desarrolladores      BAJA    MEDIO  🟡 BAJA
```

---

<a name="conclusiones"></a>
## 11. CONCLUSIONES Y RECOMENDACIONES

### 11.1 Resumen Ejecutivo

```
PROYECTO: Refactorización Completa de Testing - IACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALCANCE:
✓ 9 apps refactorizadas (access, audit, authentication, 
  core, ivr_legacy, pipeline, reports, users, utils)
✓ 294+ tests funcionando (actualmente 13%)
✓ Service Layer Pattern en todas las apps
✓ 2,000+ líneas de fixtures y mocks
✓ Cobertura de código 90%+

INVERSIÓN:
- Tiempo: 12 semanas (3 meses)
- Esfuerzo: 480 horas
- Equipo: 2-3 desarrolladores

RETORNO:
- Tests 100% funcionales (vs 13% actual)
- Velocidad 6x más rápida (<5 seg vs 30 seg)
- Código enterprise-grade (Clean Code)
- Mantenibilidad 12x mejor
- CI/CD funcional (sin dependencias externas)

ROI:
Inversión: 480 horas
Ahorro anual: ~2,000 horas (desarrollo + debugging)
ROI: 317% en el primer año
```

### 11.2 Recomendaciones

```
RECOMENDACIÓN 1: APROBAR PROYECTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fundamento:
- Arquitectura actual insostenible (Fat Models)
- 79% tests bloqueados impide desarrollo
- Deuda técnica creciendo

Acción:
✓ Aprobar presupuesto 480 horas
✓ Asignar 2-3 desarrolladores
✓ Iniciar en Febrero 2026

Timeline:
Febrero-Abril 2026 (12 semanas)
```

```
RECOMENDACIÓN 2: SEGUIR ROADMAP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fundamento:
- Orden de implementación basado en dependencias
- Riesgos mitigados
- Incremental y validado

Acción:
✓ Implementar semana por semana según roadmap
✓ No saltarse pasos
✓ Validar KPIs cada semana

Checkpoints:
- Semana 4: Core completo (checkpoint crítico)
- Semana 8: 90% tests funcionando
- Semana 12: Proyecto completo
```

```
RECOMENDACIÓN 3: CAPACITAR EQUIPO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fundamento:
- Service Layer Pattern nuevo para el equipo
- Fixtures/mocks requieren práctica
- Knowledge transfer crítico

Acción:
✓ 2 días de capacitación inicial (Service Layer)
✓ Pair programming durante refactoring
✓ Code reviews obligatorios

Resultado:
Equipo autónomo en semana 4
```

```
RECOMENDACIÓN 4: MONITOREO CONTINUO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fundamento:
- Detectar problemas temprano
- Validar que refactoring no rompe funcionalidad

Acción:
✓ Daily standups
✓ Tests ejecutados en cada PR
✓ Code coverage tracking
✓ Performance monitoring

Herramientas:
- pytest --cov (local)
- Pre-commit hooks
- Manual testing crítico
```

### 11.3 Próximos Pasos

```
PRÓXIMOS PASOS INMEDIATOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. APROBACIÓN (Esta semana)
   ├─ Revisar este documento
   ├─ Aprobar presupuesto
   └─ Asignar equipo

2. KICKOFF (Semana 1 Febrero)
   ├─ Sesión de kickoff (2 horas)
   ├─ Capacitación Service Layer (2 días)
   └─ Setup ambiente

3. IMPLEMENTACIÓN (Semanas 2-13)
   ├─ Seguir roadmap semana por semana
   ├─ Daily standups
   └─ Code reviews

4. VALIDACIÓN (Semana 14)
   ├─ Testing completo
   ├─ Performance validation
   └─ Deploy a staging

5. PRODUCCIÓN (Semana 15)
   ├─ Deploy gradual
   ├─ Monitoring
   └─ Celebración 🎉

FECHA OBJETIVO: Mayo 2026
```

---

## ANEXOS

### A. Referencias

```
DOCUMENTOS RELACIONADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ANALISIS_COMPLETO_OPCIONES_TESTING_v1.0.0.md
   → Análisis original de 3 opciones
   → 59 KB, 2,561 líneas
   → ubicación: docs/arquitectura/testing/

2. PLAN_ACCION_INMEDIATA_v1.0.0.md
   → Plan de acción quick wins
   → 6.8 KB
   → ubicación: docs/arquitectura/testing/

3. ANALISIS_SERVICE_LAYER_REFACTORING_v1.0.0.md
   → Guía completa Service Layer Pattern
   → 57 KB, 1,357 líneas
   → ubicación: docs/arquitectura/patrones/

4. METODOLOGIA_CREACION_DOCUMENTOS_v1.0.0.md
   → Metodología de documentación
   → 25 KB
   → ubicación: docs/soporte/
```

### B. Glosario

```
CNST: Código de Normas de Suministro de Telecomunicaciones
      Regulación mexicana para call centers

Service Layer: Patrón arquitectural que separa lógica de
               negocio de la capa de presentación y datos

Fat Models: Anti-patrón donde los models contienen lógica
            de negocio (incorrecto en Clean Code)

Thin Models: Models delgados que solo contienen estructura
             de datos y validaciones simples (correcto)

Fixtures: Datos predefinidos para tests (pytest fixtures)

Factories: Generadores dinámicos de datos para tests
           (usando factory-boy)

Mocks: Objetos simulados que reemplazan dependencias
       externas en tests

Coverage: Porcentaje de código cubierto por tests
```

---

**FIN DEL DOCUMENTO**

Version: 2.0.0
Fecha: 2026-01-17
Categoría: arquitectura/testing
P�ginas: ~80 (estimado)
Tiempo de Lectura: 2-3 horas
Tiempo de Implementación: 12 semanas

**DOCUMENTOS RELACIONADOS:**
- ANALISIS_COMPLETO_OPCIONES_TESTING_v1.0.0.md
- PLAN_ACCION_INMEDIATA_v1.0.0.md
- ANALISIS_SERVICE_LAYER_REFACTORING_v1.0.0.md

**APROBACIONES REQUERIDAS:**
- [ ] Tech Lead
- [ ] Product Owner
- [ ] Gerente de Desarrollo

**SIGUIENTE ACCIÓN:**
Revisar y aprobar para iniciar Semana 1
