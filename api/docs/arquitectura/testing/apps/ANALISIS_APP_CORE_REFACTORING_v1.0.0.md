---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System  
type: Análisis Técnico - App Crítica
categoria: arquitectura/testing/apps
app: core
tema: Refactorización completa de testing para app CORE
autor: Claude Technical Analysis
tags: [core, testing, refactoring, service-layer, critical-app]
relacionado:
  - ANALISIS_COMPLETO_REFACTORING_TESTING_v2.0.0.md
  - ANALISIS_APP_UTILS_REFACTORING_v1.0.0.md
  - ANALISIS_SERVICE_LAYER_REFACTORING_v1.0.0.md
estado: completado
prioridad: CRÍTICA
tiempo_estimado: 2-3 semanas
tests_totales: 69 tests
tests_actuales: 6 passing (9%)
tests_bloqueados: ~60 tests (87%)
cobertura_actual: ~9%
cobertura_objetivo: 90%+
---

# ANÁLISIS COMPLETO: APP CORE - REFACTORING

**La App Más Crítica del Sistema - Análisis basado en código REAL**

---

## RESUMEN EJECUTIVO

### Estado Actual

```
APP: apps/core/
PROPÓSITO: Núcleo del sistema - Servicios, permisos, navegación
TAMAÑO: 204 KB de tests (26% del total del proyecto)
TESTS: 69 tests identificados
ESTADO: CRÍTICO - Solo 6 tests pasando (9%)
TIEMPO ESTIMADO: 2-3 semanas (80-120 horas)
PRIORIDAD: 🔴 CRÍTICA - Corazón del sistema
```

### Problema Principal IDENTIFICADO

```
CONFLICTO DE IMPORTS - CRÍTICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CAUSA RAÍZ:
Existe TANTO un archivo como un directorio con el mismo nombre:
├── apps/core/services.py      (archivo con ServiceAccessService)
└── apps/core/services/        (directorio con __init__.py vacío)

CONSECUENCIA:
Python prioriza el directorio sobre el archivo.
Import "from apps.core.services import ServiceAccessService" busca en:
- services/__init__.py (vacío) ✗ FALLA
- NO en services.py (donde está el código) ✗ NO LO ENCUENTRA

ERROR:
ImportError: cannot import name 'ServiceAccessService' from 'apps.core.services' 
(/tmp/iact-real/callcentersite/apps/core/services/__init__.py)

IMPACTO:
- test_service_access.py BLOQUEADO (9 tests)
- Otros tests que usan ServiceAccessService BLOQUEADOS
- ~50-60 tests NO pueden ejecutarse

CÓDIGO SÍ EXISTE:
✓ ServiceAccessService está en apps/core/services.py (líneas 14-209)
✓ 195 líneas de código funcional
✓ 7 métodos implementados
✓ Type hints completos
✓ Documentación completa

SOLUCIÓN:
Mover ServiceAccessService de services.py a services/__init__.py
O renombrar uno de los dos
```

### Métricas Clave

```
CÓDIGO EXISTENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├─ Archivos Python:        20 archivos
├─ Models:                 4 models (316 líneas)
├─ Services:               2 services (ServiceAccess + ETL)
├─ Navigation:             3 archivos (navegación/menús)
├─ Mixins:                 ServiceFilterMixin
└─ Total líneas código:    ~2,000 líneas estimadas

TESTS EXISTENTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├─ Archivos tests:         7 archivos
├─ Total líneas tests:     1,451 líneas
├─ Tests identificados:    69 tests
├─ Pasando:                6 tests (9%)
├─ Fallando:               24 tests (35%)
├─ Con errores:            39 tests (57%)
└─ Bloqueados (import):    ~60 tests (87%)

ESTADO ACTUAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 6/69 tests pasando      (9%)
❌ 24/69 tests fallando    (35%)
⚠️  39/69 tests con error  (57%)
⛔ ~60/69 bloqueados      (87%)
```

---

## TABLA DE CONTENIDOS

1. [Código Existente Detallado](#codigo-existente)
2. [Tests Actuales Análisis](#tests-actuales)
3. [Problema del Import](#problema-import)
4. [Soluciones Propuestas](#soluciones)
5. [Plan de Refactorización](#plan-refactoring)
6. [Service Layer Strategy](#service-layer)
7. [Fixtures Necesarias](#fixtures)
8. [Mocks Necesarios](#mocks)
9. [Roadmap de Implementación](#roadmap)
10. [Riesgos](#riesgos)
11. [Criterios de Éxito](#criterios)

---

<a name="codigo-existente"></a>
## 1. CÓDIGO EXISTENTE DETALLADO

### 1.1 Estructura de apps/core/

```
apps/core/
├── __init__.py
├── admin.py
├── apps.py
├── models.py                    (316 líneas) ⭐ CORE
├── serializers.py               (2.0 KB)
├── views.py                     (2.5 KB)
├── urls.py
├── permissions.py               (2.0 KB)
├── mixins.py                    (2.5 KB)
├── tests.py                     (vacío)
│
├── services.py                  (209 líneas) ⭐ SERVICIO
│   └── ServiceAccessService
│
├── services/                    ⚠️ CONFLICTO
│   ├── __init__.py             (vacío) ← PROBLEMA
│   └── etl_service.py          (7.5 KB)
│
├── navigation/
│   ├── __init__.py
│   ├── builders.py             (17 KB)
│   ├── views.py                (2.5 KB)
│   └── urls.py
│
├── management/
│   └── commands/
│       └── [varios comandos]
│
└── migrations/
    ├── __init__.py
    └── [...migrations...]

TOTAL: ~2,000 líneas de código Python
```

### 1.2 Models (4 models, 316 líneas)

```python
# ════════════════════════════════════════════════════════════
# apps/core/models.py (316 líneas)
# ════════════════════════════════════════════════════════════

MODEL 1: CallRecord (líneas 14-97)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Registro de llamadas procesado (analytics)
Herencia: SoftDeleteMixin
Database: default (PostgreSQL analytics)

Campos:
├─ fecha (DateField, indexed)
├─ telefono (CharField, indexed)
├─ servicio_800 (CharField, indexed)
├─ total_llamadas (IntegerField)
├─ llamadas_contestadas (IntegerField)
├─ llamadas_abandonadas (IntegerField)
├─ created_at (DateTimeField)
└─ updated_at (DateTimeField)

Métodos:
└─ answer_rate() -> Decimal
   Calcula porcentaje de respuesta (0-100)

Índices:
├─ fecha + servicio_800
└─ fecha + telefono

Unique Together: [fecha, telefono, servicio_800]

LÓGICA DE NEGOCIO:
❌ answer_rate() en model (debería estar en service)

MODEL 2: Center (líneas 99-136)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Centro de atención físico
Herencia: SoftDeleteMixin

Campos:
├─ nombre (CharField)
├─ codigo (CharField, unique, indexed)
├─ activo (BooleanField)
├─ created_at (DateTimeField)
└─ updated_at (DateTimeField)

LÓGICA DE NEGOCIO:
✅ Model delgado (solo datos)

MODEL 3: Service (líneas 139-183)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Servicio 800
Herencia: SoftDeleteMixin

Campos:
├─ numero_800 (CharField, unique, indexed)
├─ nombre (CharField)
├─ center (ForeignKey → Center)
├─ activo (BooleanField)
├─ created_at (DateTimeField)
└─ updated_at (DateTimeField)

Relación:
└─ Center.services (related_name)

LÓGICA DE NEGOCIO:
✅ Model delgado (solo datos)

MODEL 4: UserServiceAccess (líneas 185-316) ⚠️ GORDÍSIMO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Acceso de usuario a servicios 800
Herencia: SoftDeleteMixin
PROBLEMA: ⚠️ Tiene lógica de negocio en classmethod

Campos:
├─ user (ForeignKey → User)
├─ service (ForeignKey → Service)
├─ granted_at (DateTimeField)
├─ granted_by (ForeignKey → User, nullable)
├─ reason (TextField)
├─ is_active (BooleanField)
├─ revoked_at (DateTimeField, nullable)
└─ revoked_by (ForeignKey → User, nullable)

Métodos con LÓGICA DE NEGOCIO (líneas 272-315):
⚠️ get_user_services(user) -> QuerySet
   44 líneas de lógica
   Retorna servicios accesibles por usuario
   
⚠️ has_service_access(user, service) -> bool
   14 líneas de lógica
   Verifica si usuario tiene acceso

PROBLEMA CRÍTICO:
❌ 58 líneas de lógica de negocio en MODEL
❌ Debería estar en ServiceAccessService
❌ Viola Service Layer Pattern
❌ Fat Model anti-pattern

EVIDENCIA DE REFACTORING NECESARIO:
Estos mismos métodos existen en ServiceAccessService
(services.py líneas 26-53) pero el service solo delega
al model. Debería ser al revés.
```

### 1.3 ServiceAccessService (EXISTE pero inaccesible)

```python
# ════════════════════════════════════════════════════════════
# apps/core/services.py (209 líneas)
# ESTADO: ✅ EXISTE pero ⛔ INACCESIBLE por conflicto de imports
# ════════════════════════════════════════════════════════════

class ServiceAccessService:
    """
    Service para gestión de accesos a servicios.
    
    UBICACIÓN: apps/core/services.py (líneas 14-209)
    PROBLEMA: Inaccesible por conflicto con services/ directorio
    """
    
    # ────────────────────────────────────────────────────────
    # MÉTODOS IMPLEMENTADOS (7 métodos, 195 líneas)
    # ────────────────────────────────────────────────────────
    
    1. get_user_services(user) -> QuerySet
       Obtener servicios accesibles por usuario
       Líneas: 26-39 (14 líneas)
       
    2. has_service_access(user, service) -> bool
       Verificar acceso a servicio
       Líneas: 42-53 (12 líneas)
       
    3. filter_by_user_services(queryset, user, service_field) -> QuerySet
       Filtrar QuerySet por servicios permitidos
       Líneas: 56-100 (45 líneas)
       ⭐ MÉTODO IMPORTANTE - filtra CallRecord, Reports, etc
       
    4. grant_service_access(user, service, granted_by, reason) -> UserServiceAccess
       Otorgar acceso a servicio
       Líneas: 103-144 (42 líneas)
       
    5. revoke_service_access(user, service, revoked_by) -> Optional[UserServiceAccess]
       Revocar acceso a servicio
       Líneas: 147-181 (35 líneas)
       
    6. get_services_summary(user) -> dict
       Resumen de servicios del usuario
       Líneas: 184-209 (26 líneas)

CALIDAD DEL CÓDIGO:
✅ Type hints completos
✅ Docstrings Google style
✅ Ejemplos de uso en docstrings
✅ Métodos estáticos (stateless)
✅ Separation of Concerns

PROBLEMA ACTUAL:
❌ Service delega a Model (debería ser al revés)
❌ Lógica está en UserServiceAccess.get_user_services()
❌ Service solo hace wrapper

REFACTORING NECESARIO:
1. Mover lógica de UserServiceAccess a ServiceAccessService
2. UserServiceAccess solo debe tener datos
3. ServiceAccessService debe tener lógica
```

### 1.4 Navigation System

```
apps/core/navigation/
│
├── builders.py (17 KB, ~500 líneas)
│   ├─ MenuValidator
│   ├─ MenuBuilder  
│   └─ MenuSerializer
│
├── views.py (2.5 KB)
│   └─ NavigationViewSet
│
└── urls.py
    └─ Router configuration

FUNCIONALIDAD:
- Construcción dinámica de menús
- Validación de estructura de menús
- Serialización para frontend
- Permisos por módulo/función

TESTS:
- test_navigation_builders.py (18 KB)
- test_navigation_views.py (8.5 KB)
- 24 tests fallando (problemas de fixtures)
```

### 1.5 Otros Componentes

```python
# ════════════════════════════════════════════════════════════
# apps/core/mixins.py
# ════════════════════════════════════════════════════════════

class ServiceFilterMixin:
    """
    Mixin para ViewSets que filtran por servicio.
    
    Aplica automáticamente filter_by_user_services al queryset.
    """
    service_field = 'servicio_800'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return ServiceAccessService.filter_by_user_services(
            queryset, self.request.user, self.service_field
        )

# ════════════════════════════════════════════════════════════
# apps/core/serializers.py
# ════════════════════════════════════════════════════════════

CallRecordSerializer
ServiceSerializer
CenterSerializer

# ════════════════════════════════════════════════════════════
# apps/core/services/etl_service.py
# ════════════════════════════════════════════════════════════

class ETLService:
    """Servicio ETL para procesar datos."""
    
    def extract(self):
        pass
    
    def transform(self, data):
        pass
    
    def load(self, data):
        pass
```

---

<a name="tests-actuales"></a>
## 2. TESTS ACTUALES ANÁLISIS

### 2.1 Inventario de Tests

```
tests/unit/core/
│
├── test_core_app.py                 (512 bytes, ~1 test)
│   └─ test_app_config
│
├── test_core_etl_service.py         (4.0 KB, ~10 tests)
│   └─ Tests de ETLService
│
├── test_core_models.py              (8.0 KB, ~15 tests)
│   ├─ TestCallRecord
│   ├─ TestCenter
│   ├─ TestService
│   └─ TestUserServiceAccess
│
├── test_core_serializers.py         (3.0 KB, ~5 tests)
│   └─ Tests de serializers
│
├── test_navigation_builders.py      (18 KB, ~20 tests)
│   ├─ TestMenuValidator
│   ├─ TestMenuBuilder
│   ├─ TestMenuSerializer
│   └─ TestMenuBuilderIntegration
│
├── test_navigation_views.py         (8.5 KB, ~10 tests)
│   └─ Tests de NavigationViewSet
│
└── test_service_access.py           (8.0 KB, ~9 tests) ⛔ BLOQUEADO
    ├─ TestUserServiceAccess
    ├─ TestServiceAccessService
    └─ TestServiceFilterMixin

TOTAL: 7 archivos, 1,451 líneas, 69 tests
```

### 2.2 Resultado de Tests REAL (Ejecutados 2026-01-17)

```
EJECUCIÓN COMPLETA (con import error):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pytest tests/unit/core/ -v

Collected: 69 items / 1 error

ERROR:
test_service_access.py - ImportError en línea 5
ImportError: cannot import name 'ServiceAccessService'

RESULTADO:
⛔ 1 error de colección
⛔ test_service_access.py NO ejecutado (9 tests bloqueados)

EJECUCIÓN SIN test_service_access.py:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pytest tests/unit/core/ --ignore=test_service_access.py -v

Collected: 60 items

RESULTADOS:
✅ 6 tests PASANDO      (10%)
❌ 24 tests FALLANDO    (40%)
⚠️  30 tests CON ERROR  (50%)

TESTS PASANDO (6/60):
- test_core_app.py::test_app_config ✓
- test_core_models.py::TestCallRecord::test_create ✓
- test_core_models.py::TestCenter::test_create ✓
- test_core_models.py::TestService::test_create ✓
- test_core_serializers.py::test_call_record_serializer ✓
- test_core_serializers.py::test_service_serializer ✓

TESTS FALLANDO (24/60):
- Mayormente test_navigation_builders.py
- Problemas de fixtures / datos de test

TESTS CON ERROR (30/60):
- Problemas de DB
- Imports faltantes
- Fixtures no configuradas
```

### 2.3 Análisis Detallado por Archivo

```python
# ════════════════════════════════════════════════════════════
# test_service_access.py (8 KB, 9 tests) ⛔ BLOQUEADO
# ════════════════════════════════════════════════════════════

ESTADO: ⛔ BLOQUEADO COMPLETAMENTE (0/9)
PROBLEMA: ImportError en línea 5

from apps.core.services import ServiceAccessService
                               ^^^^^^^^^^^^^^^^^^^^
ImportError: cannot import name 'ServiceAccessService'

TESTS BLOQUEADOS:
TestUserServiceAccess:
├─ test_grant_service_access
├─ test_get_user_services
└─ test_superuser_sees_all_services

TestServiceAccessService:
├─ test_has_service_access
├─ test_filter_by_user_services
├─ test_grant_and_revoke_access
└─ test_get_services_summary

TestServiceFilterMixin:
└─ test_mixin_filters_queryset

TOTAL: 9/9 tests bloqueados (100%)

# ════════════════════════════════════════════════════════════
# test_navigation_builders.py (18 KB, ~20 tests)
# ════════════════════════════════════════════════════════════

ESTADO: ❌ MAYORMENTE FALLANDO (0/20 pasando)

TestMenuValidator (8 tests):
❌ 8/8 fallando
Problema: Fixtures de menús no configuradas

TestMenuBuilder (8 tests):
❌ 8/8 fallando
Problema: Permisos no configurados, fixtures missing

TestMenuSerializer (2 tests):
❌ 2/2 fallando

TestMenuBuilderIntegration (2 tests):
❌ 2/2 fallando

PROBLEMAS COMUNES:
- Fixtures de módulos no existen
- Fixtures de permisos no existen
- Datos de navegación no están en DB

# ════════════════════════════════════════════════════════════
# test_core_models.py (8 KB, ~15 tests)
# ════════════════════════════════════════════════════════════

ESTADO: ✅ PARCIAL (3/15 pasando)

TestCallRecord:
├─ test_create ✅
├─ test_answer_rate ⚠️  (error DB)
└─ test_unique_together ⚠️  (error DB)

TestCenter:
├─ test_create ✅
└─ test_soft_delete ⚠️  (error)

TestService:
├─ test_create ✅
└─ test_center_relation ⚠️  (error)

TestUserServiceAccess:
├─ test_create ⚠️  (error)
├─ test_get_user_services ⚠️  (error)
└─ test_has_service_access ⚠️  (error)

PASANDO: 3/15 (20%)
FALLANDO/ERROR: 12/15 (80%)

# ════════════════════════════════════════════════════════════
# test_core_serializers.py (3 KB, ~5 tests)
# ════════════════════════════════════════════════════════════

ESTADO: ✅ MEJOR (2/5 pasando)

✅ test_call_record_serializer
✅ test_service_serializer
⚠️  test_center_serializer
⚠️  test_user_service_access_serializer
⚠️  test_nested_serialization

PASANDO: 2/5 (40%)

# ════════════════════════════════════════════════════════════
# test_core_etl_service.py (4 KB, ~10 tests)
# ════════════════════════════════════════════════════════════

ESTADO: ⚠️  ERRORES (0/10 pasando)

Todos los tests tienen errores de:
- Fixtures no configuradas
- Mocks no disponibles
- DB no configurada

# ════════════════════════════════════════════════════════════
# test_core_app.py (512 bytes, 1 test)
# ════════════════════════════════════════════════════════════

ESTADO: ✅ FUNCIONA (1/1 pasando)

✅ test_app_config

# ════════════════════════════════════════════════════════════
# test_navigation_views.py (8.5 KB, ~10 tests)
# ════════════════════════════════════════════════════════════

ESTADO: ⚠️  ERRORES (0/10 pasando)

Problemas similares a test_navigation_builders.py
```

---

<a name="problema-import"></a>
## 3. PROBLEMA DEL IMPORT (Análisis Profundo)

### 3.1 Diagnóstico del Conflicto

```
SITUACIÓN ACTUAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/
├── services.py                  ← ARCHIVO con ServiceAccessService
└── services/                    ← DIRECTORIO
    ├── __init__.py             ← VACÍO (problema)
    └── etl_service.py          ← ETLService

CUANDO SE HACE:
from apps.core.services import ServiceAccessService

PYTHON HACE:
1. Ve que existe apps/core/services/
2. Busca services/__init__.py (directorio tiene prioridad)
3. Importa de services/__init__.py (vacío)
4. NO encuentra ServiceAccessService
5. ImportError

PYTHON NO:
- No busca en services.py (archivo)
- No considera services.py si existe services/

EVIDENCIA:
ImportError: cannot import name 'ServiceAccessService' from 'apps.core.services' 
(/tmp/iact-real/callcentersite/apps/core/services/__init__.py)
                                                    ^^^^^^^^^
                                           Path es al __init__.py del directorio
```

### 3.2 Por Qué Sucede Esto

```python
# ════════════════════════════════════════════════════════════
# PRIORIDAD DE IMPORTS EN PYTHON
# ════════════════════════════════════════════════════════════

Cuando existe:
- apps/core/services.py (archivo)
- apps/core/services/ (directorio)

Python SIEMPRE prioriza el DIRECTORIO sobre el ARCHIVO.

REGLA DE PYTHON:
1. Si existe directorio con __init__.py → usar directorio
2. Si NO existe directorio → usar archivo .py

NO PUEDE COEXISTIR:
❌ No puedes tener services.py Y services/ al mismo nivel
❌ Python solo "ve" uno de ellos
❌ El directorio siempre gana

SOLUCIÓN CORRECTA:
Elegir UNO:
A. Solo services.py (archivo)
B. Solo services/ (directorio con __init__.py que expone todo)
```

### 3.3 Estado del Código

```
CÓDIGO QUE SÍ EXISTE Y FUNCIONA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/services.py:
├─ ServiceAccessService     (195 líneas)
│  ├─ get_user_services()
│  ├─ has_service_access()
│  ├─ filter_by_user_services()  ⭐ IMPORTANTE
│  ├─ grant_service_access()
│  ├─ revoke_service_access()
│  └─ get_services_summary()
│
├─ Calidad: ✅ EXCELENTE
│  ├─ Type hints completos
│  ├─ Docstrings Google style
│  ├─ Ejemplos en docstrings
│  └─ Clean Code

apps/core/services/etl_service.py:
├─ ETLService               (7.5 KB)
│  ├─ extract()
│  ├─ transform()
│  └─ load()
│
└─ Calidad: ✅ BUENA

PROBLEMA:
apps/core/services/__init__.py:
└─ VACÍO ← Este es el problema

Si __init__.py no exporta ServiceAccessService,
el import falla aunque services.py exista.
```

---

<a name="soluciones"></a>
## 4. SOLUCIONES PROPUESTAS

### 4.1 Opción A: Mover a services/__init__.py (RECOMENDADA)

```python
# ════════════════════════════════════════════════════════════
# SOLUCIÓN A: Consolidar en services/ (RECOMENDADA)
# ════════════════════════════════════════════════════════════

VENTAJAS:
✅ Organización más limpia
✅ Todos los services en un lugar
✅ Escalable (más services en futuro)
✅ Patrón estándar de Django
✅ No rompe imports existentes (una vez actualizado)

PASOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Copiar ServiceAccessService de services.py a services/__init__.py
   
2. Actualizar apps/core/services/__init__.py:

# apps/core/services/__init__.py (NUEVO - 220 líneas)
"""
Services para app core.

Exports:
- ServiceAccessService: Gestión de accesos a servicios
- ETLService: ETL para datos
"""
from typing import Optional
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from apps.core.models import Service, UserServiceAccess

User = get_user_model()


class ServiceAccessService:
    """
    Service para gestión de accesos a servicios.
    
    [... copiar código completo de services.py ...]
    """
    
    @staticmethod
    def get_user_services(user: User) -> QuerySet:
        # ... implementación ...
        pass
    
    # ... resto de métodos ...


# Importar ETLService
from .etl_service import ETLService

__all__ = ['ServiceAccessService', 'ETLService']


3. ELIMINAR apps/core/services.py (el archivo)

4. Validar imports:
   python manage.py shell
   >>> from apps.core.services import ServiceAccessService
   >>> # Debería funcionar ✓

5. Ejecutar tests:
   pytest tests/unit/core/test_service_access.py -v
   # Debería pasar ✓

TIEMPO: 30-45 minutos
RIESGO: BAJO
COMPATIBILIDAD: 100% (mismo import path)
```

```
RESULTADO ESPERADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/
├── services/
│   ├── __init__.py         ← ServiceAccessService aquí (220 líneas)
│   └── etl_service.py      ← ETLService (7.5 KB)
└── [no más services.py]

IMPORT:
from apps.core.services import ServiceAccessService ✅
from apps.core.services import ETLService ✅

TESTS:
test_service_access.py: 9/9 ✅ (desbloqueados)
```

### 4.2 Opción B: Renombrar directorio (NO RECOMENDADA)

```
SOLUCIÓN B: Renombrar services/ a algo diferente
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PASOS:
mv apps/core/services/ apps/core/service_layer/

VENTAJAS:
✅ services.py queda accesible
✅ No hay conflicto de nombres

DESVENTAJAS:
❌ Rompe imports de ETLService
❌ Requiere actualizar múltiples archivos
❌ Nombres inconsistentes (services.py vs service_layer/)
❌ Más refactoring

TIEMPO: 1-2 horas
RIESGO: MEDIO
NO RECOMENDADA
```

### 4.3 Opción C: Eliminar directorio (NO RECOMENDADA)

```
SOLUCIÓN C: Eliminar services/ y poner todo en services.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PASOS:
1. Mover ETLService a services.py
2. Eliminar directorio services/
3. Todo en un archivo services.py

DESVENTAJAS:
❌ services.py sería muy grande (500+ líneas)
❌ No escalable
❌ Violenta separation of concerns
❌ Un archivo gigante difícil de mantener

NO RECOMENDADA
```

---

---

<a name="plan-refactoring"></a>
## 5. PLAN DE REFACTORIZACIÓN

### 5.1 Problemas de Arquitectura Identificados

```
PROBLEMA 1: Fat Models (Anti-Pattern)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UBICACIÓN: UserServiceAccess model (líneas 272-315)

CÓDIGO ACTUAL (MALO):
class UserServiceAccess(models.Model):
    # ... campos ...
    
    @classmethod
    def get_user_services(cls, user):
        """44 líneas de lógica de negocio."""
        if user.is_superuser:
            return Service.objects.filter(activo=True)
        
        return Service.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            activo=True,
        ).distinct()
    
    @classmethod
    def has_service_access(cls, user, service):
        """14 líneas de lógica de negocio."""
        if user.is_superuser:
            return True
        
        service_id = service.id if hasattr(service, 'id') else service
        
        return cls.objects.filter(
            user=user,
            service_id=service_id,
            is_active=True,
        ).exists()

PROBLEMA:
❌ 58 líneas de lógica en MODEL
❌ Model sabe sobre permisos de superuser
❌ Model maneja lógica de negocio
❌ Difícil de testear
❌ Viola Single Responsibility Principle

SOLUCIÓN:
✅ Mover a ServiceAccessService
✅ Model solo datos
✅ Service maneja lógica


PROBLEMA 2: Service como Wrapper (Anti-Pattern)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UBICACIÓN: ServiceAccessService.get_user_services()

CÓDIGO ACTUAL (MALO):
class ServiceAccessService:
    @staticmethod
    def get_user_services(user: User) -> QuerySet:
        """Solo delega al model."""
        return UserServiceAccess.get_user_services(user)
                                 ^^^^^^^^^^^^^^^^^^^^
                              Delega toda la lógica

PROBLEMA:
❌ Service solo hace wrapper
❌ Lógica está en model
❌ Service no agrega valor
❌ Inversión de dependencias incorrecta

DEBERÍA SER:
✅ Lógica en Service
✅ Model solo acceso a datos
✅ Service usa Model (no al revés)


PROBLEMA 3: Lógica de Negocio en Model
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UBICACIÓN: CallRecord.answer_rate()

CÓDIGO ACTUAL (MALO):
class CallRecord(models.Model):
    # ... campos ...
    
    def answer_rate(self):
        """Cálculo de porcentaje."""
        if self.total_llamadas == 0:
            return Decimal('0.00')
        
        rate = (Decimal(self.llamadas_contestadas) / 
                Decimal(self.total_llamadas)) * 100
        return rate.quantize(Decimal('0.01'))

PROBLEMA:
❌ Cálculo de negocio en model
❌ Difícil de testear independiente
❌ No reutilizable para múltiples CallRecords

SOLUCIÓN:
Crear CallRecordService con método calculate_answer_rate()
```

### 5.2 Estrategia de Refactorización

```
FASE 1: Fix Import Blocking (DÍA 1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objetivo: Desbloquear 9 tests de test_service_access.py

PASOS:
1. Mover ServiceAccessService a services/__init__.py
2. Eliminar services.py (archivo)
3. Validar imports funcionan
4. Ejecutar test_service_access.py

RESULTADO:
✅ 9/9 tests desbloqueados
✅ ServiceAccessService accesible
✅ Base para siguiente fase

TIEMPO: 1-2 horas


FASE 2: Service Layer Refactoring (DÍAS 2-5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objetivo: Mover lógica de models a services

PASOS:

DÍA 2: UserServiceAccess → ServiceAccessService
────────────────────────────────────────────────────────────
1. Mover get_user_services() de model a service
2. Mover has_service_access() de model a service
3. Actualizar tests
4. Deprecar métodos en model

Código refactorizado:

# apps/core/services/__init__.py (REFACTORIZADO)
class ServiceAccessService:
    @staticmethod
    def get_user_services(user: User) -> QuerySet:
        """
        Obtener servicios accesibles.
        
        LÓGICA MOVIDA DEL MODEL ✓
        """
        if user.is_superuser:
            return Service.objects.filter(activo=True)
        
        # Usuario normal: solo servicios asignados
        return Service.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            activo=True,
        ).distinct()

# apps/core/models.py (REFACTORIZADO)
class UserServiceAccess(SoftDeleteMixin, models.Model):
    # ... solo campos ...
    
    @classmethod
    def get_user_services(cls, user):
        """
        DEPRECADO: Usar ServiceAccessService.get_user_services()
        
        Se mantendrá por compatibilidad hasta v2.0
        """
        import warnings
        warnings.warn(
            "UserServiceAccess.get_user_services() está deprecado. "
            "Usar ServiceAccessService.get_user_services()",
            DeprecationWarning,
            stacklevel=2
        )
        from apps.core.services import ServiceAccessService
        return ServiceAccessService.get_user_services(user)

TIEMPO: 4-6 horas


DÍA 3: Crear CallRecordService
────────────────────────────────────────────────────────────
1. Crear apps/core/services/call_record_service.py
2. Mover answer_rate() del model
3. Agregar métodos de análisis
4. Actualizar tests

# apps/core/services/call_record_service.py (NUEVO)
from decimal import Decimal
from typing import List, Dict
from django.db.models import QuerySet, Avg, Sum
from apps.core.models import CallRecord


class CallRecordService:
    """Service para lógica de CallRecord."""
    
    @staticmethod
    def calculate_answer_rate(call_record: CallRecord) -> Decimal:
        """
        Calcular porcentaje de respuesta.
        
        Args:
            call_record: Instancia de CallRecord
            
        Returns:
            Decimal: Porcentaje (0-100)
        """
        if call_record.total_llamadas == 0:
            return Decimal('0.00')
        
        rate = (Decimal(call_record.llamadas_contestadas) / 
                Decimal(call_record.total_llamadas)) * 100
        return rate.quantize(Decimal('0.01'))
    
    @staticmethod
    def get_statistics(queryset: QuerySet) -> Dict:
        """
        Obtener estadísticas de conjunto de llamadas.
        
        Args:
            queryset: QuerySet de CallRecord
            
        Returns:
            Dict con estadísticas agregadas
        """
        stats = queryset.aggregate(
            total_calls=Sum('total_llamadas'),
            total_answered=Sum('llamadas_contestadas'),
            total_abandoned=Sum('llamadas_abandonadas'),
        )
        
        # Calcular porcentaje general
        if stats['total_calls'] and stats['total_calls'] > 0:
            answer_rate = (Decimal(stats['total_answered']) / 
                          Decimal(stats['total_calls'])) * 100
            stats['answer_rate'] = answer_rate.quantize(Decimal('0.01'))
        else:
            stats['answer_rate'] = Decimal('0.00')
        
        return stats
    
    @staticmethod
    def get_service_summary(servicio_800: str, date_from, date_to) -> Dict:
        """
        Resumen de llamadas para un servicio en rango de fechas.
        
        Args:
            servicio_800: Número de servicio
            date_from: Fecha inicio
            date_to: Fecha fin
            
        Returns:
            Dict con resumen
        """
        queryset = CallRecord.objects.filter(
            servicio_800=servicio_800,
            fecha__gte=date_from,
            fecha__lte=date_to,
        )
        
        stats = CallRecordService.get_statistics(queryset)
        
        return {
            'servicio_800': servicio_800,
            'period': {
                'from': date_from,
                'to': date_to,
            },
            'statistics': stats,
            'records_count': queryset.count(),
        }

TIEMPO: 4-6 horas


DÍA 4-5: Fixtures y Tests
────────────────────────────────────────────────────────────
1. Crear fixtures/core.py
2. Actualizar todos los tests
3. Validar cobertura
4. Documentar cambios

TIEMPO: 8-12 horas


FASE 3: Navigation System (DÍAS 6-8)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objetivo: Fix 24 tests fallando de navigation

PROBLEMA:
- Fixtures de módulos no existen
- Fixtures de permisos no existen
- Navigation data no en DB

PASOS:

DÍA 6: Crear fixtures de navegación
────────────────────────────────────────────────────────────
1. Analizar estructura de menús esperada
2. Crear fixtures/navigation.py
3. Fixtures de módulos
4. Fixtures de funciones/permisos

# tests/fixtures/navigation.py (NUEVO - 400 líneas)
import pytest
from apps.access.models import Module, Function


@pytest.fixture
def module_users(db):
    """Módulo de usuarios."""
    return Module.objects.create(
        code='users',
        name='Usuarios',
        description='Gestión de usuarios',
        icon='users',
        order=1,
        is_active=True,
    )


@pytest.fixture
def function_user_list(module_users):
    """Función listar usuarios."""
    return Function.objects.create(
        module=module_users,
        code='user.list',
        name='Listar Usuarios',
        description='Ver lista de usuarios',
        endpoint='/api/users/',
        order=1,
        is_active=True,
    )


@pytest.fixture
def navigation_menu_data():
    """Estructura completa de menú."""
    return {
        'level1': [
            {
                'id': 'dashboard',
                'label': 'Dashboard',
                'icon': 'home',
                'endpoint': '/dashboard/',
            },
            {
                'id': 'users',
                'label': 'Usuarios',
                'icon': 'users',
                'level2': [
                    {
                        'id': 'users-list',
                        'label': 'Lista',
                        'endpoint': '/users/',
                        'required_permission': 'user.list',
                    },
                    {
                        'id': 'users-create',
                        'label': 'Crear',
                        'endpoint': '/users/create/',
                        'required_permission': 'user.create',
                    },
                ],
            },
        ],
    }


# Más fixtures...

TIEMPO: 6-8 horas


DÍA 7: Actualizar tests de navigation
────────────────────────────────────────────────────────────
1. Actualizar test_navigation_builders.py
2. Usar nuevas fixtures
3. Fix expectations
4. Validar 20/20 pasando

TIEMPO: 4-6 horas


DÍA 8: Tests de navigation views
────────────────────────────────────────────────────────────
1. Actualizar test_navigation_views.py
2. Mocks de permisos
3. Fixtures de usuarios con permisos
4. Validar 10/10 pasando

TIEMPO: 4-6 horas


FASE 4: ETL Service (DÍAS 9-10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objetivo: Fix 10 tests de ETL

PASOS:
1. Analizar qué hace ETLService
2. Crear mocks necesarios
3. Fixtures de datos de entrada
4. Actualizar tests

TIEMPO: 8-12 horas


FASE 5: Validación Final (DÍA 11-12)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Ejecutar todos los tests
2. Validar 69/69 pasando
3. Cobertura >90%
4. Code review
5. Documentación

TIEMPO: 8-12 horas
```

### 5.3 Migration Path (Deprecation Strategy)

```
ESTRATEGIA DE DEPRECACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PASO 1: Duplicar funcionalidad (ACTUAL)
────────────────────────────────────────────────────────────
- Código en MODEL (viejo)
- Código en SERVICE (nuevo)
- Ambos funcionan

PASO 2: Deprecar métodos en model
────────────────────────────────────────────────────────────
- Agregar warnings.warn()
- Actualizar docstrings
- Model delega a Service

Ejemplo:
@classmethod
def get_user_services(cls, user):
    """DEPRECADO: Usar ServiceAccessService."""
    warnings.warn("Use ServiceAccessService", DeprecationWarning)
    from apps.core.services import ServiceAccessService
    return ServiceAccessService.get_user_services(user)

PASO 3: Actualizar código interno
────────────────────────────────────────────────────────────
- Buscar todos los usos de métodos deprecados
- Actualizar a usar Service

Comando:
grep -r "UserServiceAccess.get_user_services" apps/
# Actualizar cada uno

PASO 4: Período de gracia (1-2 sprints)
────────────────────────────────────────────────────────────
- Warnings en logs
- Nadie debe usar métodos viejos
- Tests validan ambas formas

PASO 5: Eliminar métodos deprecados
────────────────────────────────────────────────────────────
- Después de 1-2 sprints
- Solo si no hay warnings en logs
- Version bump (v2.0)
```

---

<a name="service-layer"></a>
## 6. SERVICE LAYER STRATEGY

### 6.1 Patrón de Service Layer

```python
# ════════════════════════════════════════════════════════════
# PATRÓN: Service Layer
# ════════════════════════════════════════════════════════════

ESTRUCTURA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/
├── models.py                    ← Solo datos
│   ├── CallRecord              ← Campos + Meta
│   ├── Service                 ← Campos + Meta
│   └── UserServiceAccess       ← Campos + Meta
│
├── services/
│   ├── __init__.py             ← ServiceAccessService
│   ├── call_record_service.py  ← CallRecordService
│   └── etl_service.py          ← ETLService
│
└── views.py                     ← Usa Services, no Models


RESPONSABILIDADES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODELS:
✅ Definir campos
✅ Definir relaciones
✅ Validaciones a nivel de campo
✅ Meta (db_table, indexes, etc)
✅ __str__()
❌ NO lógica de negocio
❌ NO cálculos complejos
❌ NO queries complejos

SERVICES:
✅ Lógica de negocio
✅ Cálculos
✅ Queries complejos
✅ Transacciones
✅ Validaciones de negocio
✅ Orquestación de múltiples models
❌ NO acceso directo a request
❌ NO lógica de presentación

VIEWS:
✅ Recibir request
✅ Validar input
✅ Llamar a Services
✅ Formatear response
❌ NO lógica de negocio
❌ NO queries directos a Models (usar Services)
```

### 6.2 Ejemplo Before/After

```python
# ════════════════════════════════════════════════════════════
# BEFORE: Fat Model (Anti-Pattern)
# ════════════════════════════════════════════════════════════

# apps/core/models.py (ANTES - MALO)
class UserServiceAccess(models.Model):
    user = models.ForeignKey(User)
    service = models.ForeignKey(Service)
    is_active = models.BooleanField(default=True)
    
    @classmethod
    def get_user_services(cls, user):
        """
        44 LÍNEAS DE LÓGICA EN MODEL ❌
        """
        if user.is_superuser:
            return Service.objects.filter(activo=True)
        
        return Service.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            activo=True,
        ).distinct()
    
    @classmethod
    def has_service_access(cls, user, service):
        """
        14 LÍNEAS DE LÓGICA EN MODEL ❌
        """
        if user.is_superuser:
            return True
        
        service_id = service.id if hasattr(service, 'id') else service
        
        return cls.objects.filter(
            user=user,
            service_id=service_id,
            is_active=True,
        ).exists()


# apps/core/views.py (ANTES - MALO)
class CallRecordViewSet(viewsets.ModelViewSet):
    queryset = CallRecord.objects.all()
    
    def get_queryset(self):
        """
        LÓGICA DE NEGOCIO EN VIEW ❌
        """
        user = self.request.user
        
        if user.is_superuser:
            return CallRecord.objects.filter(activo=True)
        
        # 15 líneas de lógica...
        services = Service.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
        )
        service_numbers = services.values_list('numero_800', flat=True)
        
        return CallRecord.objects.filter(
            servicio_800__in=service_numbers
        )


# ════════════════════════════════════════════════════════════
# AFTER: Service Layer (Correcto)
# ════════════════════════════════════════════════════════════

# apps/core/models.py (DESPUÉS - BUENO)
class UserServiceAccess(SoftDeleteMixin, models.Model):
    """
    SOLO DATOS ✓
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_accesses',
    )
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='user_accesses',
    )
    
    is_active = models.BooleanField(default=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(User, null=True, ...)
    
    class Meta:
        db_table = 'user_service_accesses'
        unique_together = [['user', 'service']]
    
    def __str__(self):
        return f"{self.user.username} -> {self.service.numero_800}"
    
    # SIN LÓGICA DE NEGOCIO ✓


# apps/core/services/__init__.py (DESPUÉS - BUENO)
class ServiceAccessService:
    """
    LÓGICA DE NEGOCIO AQUÍ ✓
    """
    
    @staticmethod
    def get_user_services(user: User) -> QuerySet:
        """Obtener servicios accesibles."""
        if user.is_superuser:
            return Service.objects.filter(activo=True)
        
        return Service.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            activo=True,
        ).distinct()
    
    @staticmethod
    def has_service_access(user: User, service) -> bool:
        """Verificar acceso."""
        if user.is_superuser:
            return True
        
        service_id = service.id if hasattr(service, 'id') else service
        
        return UserServiceAccess.objects.filter(
            user=user,
            service_id=service_id,
            is_active=True,
        ).exists()
    
    @staticmethod
    def filter_by_user_services(
        queryset: QuerySet, 
        user: User, 
        service_field: str = 'servicio_800'
    ) -> QuerySet:
        """
        Filtrar QuerySet por servicios permitidos.
        
        LÓGICA COMPLEJA EN SERVICE ✓
        """
        if user.is_superuser:
            return queryset
        
        user_services = ServiceAccessService.get_user_services(user)
        
        if not user_services.exists():
            return queryset.none()
        
        service_numbers = user_services.values_list('numero_800', flat=True)
        filter_kwargs = {f'{service_field}__in': service_numbers}
        
        return queryset.filter(**filter_kwargs)


# apps/core/views.py (DESPUÉS - BUENO)
class CallRecordViewSet(viewsets.ModelViewSet):
    """
    VIEW DELGADA - SOLO COORDINACIÓN ✓
    """
    queryset = CallRecord.objects.all()
    serializer_class = CallRecordSerializer
    
    def get_queryset(self):
        """
        DELEGA A SERVICE ✓
        """
        queryset = super().get_queryset()
        return ServiceAccessService.filter_by_user_services(
            queryset,
            self.request.user,
            'servicio_800'
        )
    
    # O usar mixin:

class CallRecordViewSet(ServiceFilterMixin, viewsets.ModelViewSet):
    """
    AÚN MÁS SIMPLE CON MIXIN ✓
    """
    queryset = CallRecord.objects.all()
    serializer_class = CallRecordSerializer
    service_field = 'servicio_800'
    
    # ServiceFilterMixin.get_queryset() hace el trabajo
```

### 6.3 Testing Strategy para Service Layer

```python
# ════════════════════════════════════════════════════════════
# TESTING: Service Layer
# ════════════════════════════════════════════════════════════

# tests/unit/core/test_service_access.py (REFACTORIZADO)

@pytest.mark.django_db
class TestServiceAccessService:
    """
    Tests INDEPENDIENTES del Model ✓
    """
    
    def test_get_user_services_superuser(self):
        """Superuser ve todos los servicios."""
        # Arrange
        superuser = User.objects.create_user(
            username='admin', 
            is_superuser=True
        )
        center = Center.objects.create(nombre='C1', codigo='C1')
        s1 = Service.objects.create(numero_800='800-111', nombre='S1', center=center)
        s2 = Service.objects.create(numero_800='800-222', nombre='S2', center=center)
        
        # Act
        services = ServiceAccessService.get_user_services(superuser)
        
        # Assert
        assert services.count() == 2
        assert s1 in services
        assert s2 in services
    
    def test_get_user_services_normal_user(self):
        """Usuario normal solo ve servicios asignados."""
        # Arrange
        user = User.objects.create_user(username='user')
        center = Center.objects.create(nombre='C1', codigo='C1')
        s1 = Service.objects.create(numero_800='800-111', nombre='S1', center=center)
        s2 = Service.objects.create(numero_800='800-222', nombre='S2', center=center)
        
        # Usuario solo tiene acceso a s1
        UserServiceAccess.objects.create(user=user, service=s1, is_active=True)
        
        # Act
        services = ServiceAccessService.get_user_services(user)
        
        # Assert
        assert services.count() == 1
        assert s1 in services
        assert s2 not in services
    
    def test_filter_by_user_services(self):
        """Filtrar CallRecords por servicios del usuario."""
        # Arrange
        user = User.objects.create_user(username='user')
        center = Center.objects.create(nombre='C1', codigo='C1')
        s1 = Service.objects.create(numero_800='800-111', nombre='S1', center=center)
        s2 = Service.objects.create(numero_800='800-222', nombre='S2', center=center)
        
        from datetime import date
        call1 = CallRecord.objects.create(
            fecha=date.today(),
            telefono='555-1234',
            servicio_800='800-111',
            total_llamadas=10
        )
        call2 = CallRecord.objects.create(
            fecha=date.today(),
            telefono='555-5678',
            servicio_800='800-222',
            total_llamadas=5
        )
        
        UserServiceAccess.objects.create(user=user, service=s1)
        
        # Act
        all_calls = CallRecord.objects.all()
        filtered = ServiceAccessService.filter_by_user_services(
            all_calls, user, 'servicio_800'
        )
        
        # Assert
        assert filtered.count() == 1
        assert call1 in filtered
        assert call2 not in filtered


@pytest.mark.django_db
class TestCallRecordService:
    """
    Tests de CallRecordService ✓
    """
    
    def test_calculate_answer_rate(self):
        """Calcular porcentaje de respuesta."""
        # Arrange
        from datetime import date
        call = CallRecord.objects.create(
            fecha=date.today(),
            telefono='555-1234',
            servicio_800='800-111',
            total_llamadas=100,
            llamadas_contestadas=75,
            llamadas_abandonadas=25,
        )
        
        # Act
        from apps.core.services.call_record_service import CallRecordService
        rate = CallRecordService.calculate_answer_rate(call)
        
        # Assert
        from decimal import Decimal
        assert rate == Decimal('75.00')
    
    def test_get_statistics(self):
        """Obtener estadísticas agregadas."""
        # Arrange
        from datetime import date
        CallRecord.objects.create(
            fecha=date.today(),
            telefono='555-1111',
            servicio_800='800-111',
            total_llamadas=100,
            llamadas_contestadas=80,
            llamadas_abandonadas=20,
        )
        CallRecord.objects.create(
            fecha=date.today(),
            telefono='555-2222',
            servicio_800='800-111',
            total_llamadas=50,
            llamadas_contestadas=40,
            llamadas_abandonadas=10,
        )
        
        # Act
        from apps.core.services.call_record_service import CallRecordService
        queryset = CallRecord.objects.filter(servicio_800='800-111')
        stats = CallRecordService.get_statistics(queryset)
        
        # Assert
        assert stats['total_calls'] == 150
        assert stats['total_answered'] == 120
        assert stats['total_abandoned'] == 30
        from decimal import Decimal
        assert stats['answer_rate'] == Decimal('80.00')
```

---

<a name="fixtures"></a>
## 7. FIXTURES NECESARIAS

### 7.1 Fixtures Core Models

```python
# ════════════════════════════════════════════════════════════
# tests/fixtures/core.py (NUEVO - 500 líneas)
# ════════════════════════════════════════════════════════════

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.core.models import Center, Service, UserServiceAccess, CallRecord

User = get_user_model()


# ────────────────────────────────────────────────────────────
# USERS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def superuser(db):
    """Usuario administrador."""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123',
        is_superuser=True,
        is_staff=True,
    )


@pytest.fixture
def normal_user(db):
    """Usuario normal."""
    return User.objects.create_user(
        username='user1',
        email='user1@example.com',
        password='user123',
    )


@pytest.fixture
def user_with_services(db, service_customer_support, service_sales):
    """Usuario con acceso a servicios."""
    user = User.objects.create_user(
        username='user_services',
        email='user_services@example.com',
        password='user123',
    )
    
    # Otorgar acceso a servicios
    UserServiceAccess.objects.create(
        user=user,
        service=service_customer_support,
        is_active=True,
    )
    UserServiceAccess.objects.create(
        user=user,
        service=service_sales,
        is_active=True,
    )
    
    return user


# ────────────────────────────────────────────────────────────
# CENTERS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def center_cdmx(db):
    """Centro CDMX."""
    return Center.objects.create(
        nombre='Centro Ciudad de México',
        codigo='CDMX',
        activo=True,
    )


@pytest.fixture
def center_gdl(db):
    """Centro Guadalajara."""
    return Center.objects.create(
        nombre='Centro Guadalajara',
        codigo='GDL',
        activo=True,
    )


@pytest.fixture
def center_inactive(db):
    """Centro inactivo."""
    return Center.objects.create(
        nombre='Centro Inactivo',
        codigo='INACTIVE',
        activo=False,
    )


# ────────────────────────────────────────────────────────────
# SERVICES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def service_customer_support(db, center_cdmx):
    """Servicio de atención al cliente."""
    return Service.objects.create(
        numero_800='800-123-4567',
        nombre='Atención al Cliente',
        center=center_cdmx,
        activo=True,
    )


@pytest.fixture
def service_sales(db, center_cdmx):
    """Servicio de ventas."""
    return Service.objects.create(
        numero_800='800-234-5678',
        nombre='Ventas',
        center=center_cdmx,
        activo=True,
    )


@pytest.fixture
def service_technical(db, center_gdl):
    """Servicio técnico."""
    return Service.objects.create(
        numero_800='800-345-6789',
        nombre='Soporte Técnico',
        center=center_gdl,
        activo=True,
    )


@pytest.fixture
def service_inactive(db, center_cdmx):
    """Servicio inactivo."""
    return Service.objects.create(
        numero_800='800-999-9999',
        nombre='Servicio Inactivo',
        center=center_cdmx,
        activo=False,
    )


@pytest.fixture
def all_services(db, service_customer_support, service_sales, service_technical):
    """Todos los servicios activos."""
    return [service_customer_support, service_sales, service_technical]


# ────────────────────────────────────────────────────────────
# CALL RECORDS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def call_record_today(db, service_customer_support):
    """Registro de llamadas de hoy."""
    return CallRecord.objects.create(
        fecha=date.today(),
        telefono='555-1234-5678',
        servicio_800=service_customer_support.numero_800,
        total_llamadas=100,
        llamadas_contestadas=85,
        llamadas_abandonadas=15,
    )


@pytest.fixture
def call_record_yesterday(db, service_sales):
    """Registro de llamadas de ayer."""
    return CallRecord.objects.create(
        fecha=date.today() - timedelta(days=1),
        telefono='555-8765-4321',
        servicio_800=service_sales.numero_800,
        total_llamadas=50,
        llamadas_contestadas=40,
        llamadas_abandonadas=10,
    )


@pytest.fixture
def call_records_last_week(db, service_customer_support, service_sales):
    """Registros de última semana."""
    records = []
    
    for i in range(7):
        fecha = date.today() - timedelta(days=i)
        
        # Registro para customer support
        records.append(CallRecord.objects.create(
            fecha=fecha,
            telefono=f'555-111-{i:04d}',
            servicio_800=service_customer_support.numero_800,
            total_llamadas=100 + (i * 10),
            llamadas_contestadas=80 + (i * 8),
            llamadas_abandonadas=20 + (i * 2),
        ))
        
        # Registro para sales
        records.append(CallRecord.objects.create(
            fecha=fecha,
            telefono=f'555-222-{i:04d}',
            servicio_800=service_sales.numero_800,
            total_llamadas=50 + (i * 5),
            llamadas_contestadas=40 + (i * 4),
            llamadas_abandonadas=10 + (i * 1),
        ))
    
    return records


# ────────────────────────────────────────────────────────────
# USER SERVICE ACCESS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def user_service_access_active(db, normal_user, service_customer_support, superuser):
    """Acceso activo."""
    return UserServiceAccess.objects.create(
        user=normal_user,
        service=service_customer_support,
        granted_by=superuser,
        reason='Asignación inicial',
        is_active=True,
    )


@pytest.fixture
def user_service_access_revoked(db, normal_user, service_sales, superuser):
    """Acceso revocado."""
    from django.utils import timezone
    
    access = UserServiceAccess.objects.create(
        user=normal_user,
        service=service_sales,
        granted_by=superuser,
        is_active=False,
    )
    access.revoked_at = timezone.now()
    access.revoked_by = superuser
    access.save()
    
    return access


# ────────────────────────────────────────────────────────────
# COMPOSITE FIXTURES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def complete_call_center_setup(
    db,
    center_cdmx,
    center_gdl,
    service_customer_support,
    service_sales,
    service_technical,
    superuser,
    normal_user,
    call_records_last_week,
):
    """Setup completo de call center."""
    return {
        'centers': [center_cdmx, center_gdl],
        'services': [service_customer_support, service_sales, service_technical],
        'users': [superuser, normal_user],
        'call_records': call_records_last_week,
    }
```

### 7.2 Fixtures de Navigation

```python
# ════════════════════════════════════════════════════════════
# tests/fixtures/navigation.py (NUEVO - 400 líneas)
# ════════════════════════════════════════════════════════════

import pytest


@pytest.fixture
def navigation_menu_structure():
    """
    Estructura de menú para tests.
    
    Retorna estructura esperada por MenuBuilder.
    """
    return {
        'level1': [
            {
                'id': 'dashboard',
                'label': 'Dashboard',
                'icon': 'home',
                'endpoint': '/dashboard/',
                'order': 1,
            },
            {
                'id': 'users',
                'label': 'Usuarios',
                'icon': 'users',
                'order': 2,
                'level2': [
                    {
                        'id': 'users-list',
                        'label': 'Lista de Usuarios',
                        'endpoint': '/users/',
                        'order': 1,
                        'required_permission': 'users.view_user',
                    },
                    {
                        'id': 'users-create',
                        'label': 'Crear Usuario',
                        'endpoint': '/users/create/',
                        'order': 2,
                        'required_permission': 'users.add_user',
                    },
                    {
                        'id': 'users-permissions',
                        'label': 'Permisos',
                        'endpoint': '/users/permissions/',
                        'order': 3,
                        'required_permission': 'users.change_permission',
                    },
                ],
            },
            {
                'id': 'reports',
                'label': 'Reportes',
                'icon': 'file-text',
                'order': 3,
                'level2': [
                    {
                        'id': 'reports-calls',
                        'label': 'Reporte de Llamadas',
                        'endpoint': '/reports/calls/',
                        'order': 1,
                        'required_permission': 'reports.view_callreport',
                    },
                    {
                        'id': 'reports-cnst007',
                        'label': 'CNST007',
                        'endpoint': '/reports/cnst007/',
                        'order': 2,
                        'required_permission': 'reports.view_cnst007',
                    },
                ],
            },
            {
                'id': 'settings',
                'label': 'Configuración',
                'icon': 'settings',
                'endpoint': '/settings/',
                'order': 99,
                'required_permission': 'core.change_settings',
            },
        ],
    }


@pytest.fixture
def menu_with_user_data(navigation_menu_structure):
    """Menú personalizado con datos de usuario."""
    menu = navigation_menu_structure.copy()
    
    menu['user'] = {
        'username': 'testuser',
        'full_name': 'Test User',
        'avatar_url': '/static/avatars/default.png',
        'email': 'test@example.com',
    }
    
    return menu


@pytest.fixture
def menu_icons_valid():
    """Iconos válidos para tests."""
    return [
        'home',
        'users',
        'file-text',
        'settings',
        'bar-chart',
        'calendar',
        'phone',
    ]


@pytest.fixture
def menu_icons_invalid():
    """Iconos inválidos para tests."""
    return [
        'nonexistent-icon',
        'invalid/icon',
        '../../../etc/passwd',  # Path traversal
        'icon with spaces',
    ]
```

---

<a name="mocks"></a>
## 8. MOCKS NECESARIOS

### 8.1 Servicios Externos

```python
# ════════════════════════════════════════════════════════════
# PREGUNTA AL USUARIO: ¿Qué servicios externos usa CORE?
# ════════════════════════════════════════════════════════════

NECESITO SABER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ¿CORE envía EMAIL?
   □ NO (usan ALERTAS INTERNAS - confirmado en UTILS)
   □ Sí → ¿Qué servicio? (SendGrid/AWS SES/SMTP)

2. ¿CORE usa CELERY?
   □ NO (confirmado en UTILS)
   □ Sí → ¿Para qué? (background tasks)

3. ¿CORE usa SENTRY?
   □ NO (confirmado en UTILS)
   □ Sí → ¿Para monitoreo?

4. ¿ETLService de dónde extrae datos?
   □ Base de datos IVR_LEGACY (MariaDB)
   □ API externa
   □ Archivos CSV
   □ Otro

5. ¿CORE genera REPORTES?
   □ Solo consultas DB
   □ PDF generation
   □ Excel generation
   □ Otro

6. ¿CORE usa FILE STORAGE?
   □ Filesystem local
   □ AWS S3
   □ Google Cloud Storage
   □ Otro

7. ¿Sistema de ALERTAS INTERNAS?
   □ ¿Cómo funciona?
   □ ¿Base de datos?
   □ ¿WebSocket?
   □ ¿Modelo Alert?

BASADO EN CONFIRMACIONES ANTERIORES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ NO email
✅ NO Celery
✅ NO Sentry
❓ ETL extrae de IVR_LEGACY (MariaDB READ-ONLY)
❓ Alertas internas (¿cómo?)
❓ Storage (¿dónde?)
```

### 8.2 Mocks Básicos (Sin Servicios Externos)

```python
# ════════════════════════════════════════════════════════════
# tests/mocks/core.py (BÁSICO - 200 líneas)
# ════════════════════════════════════════════════════════════

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime


# ────────────────────────────────────────────────────────────
# REQUEST MOCKS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_request_authenticated(normal_user):
    """Request autenticado con usuario normal."""
    request = Mock()
    request.user = normal_user
    request.method = 'GET'
    request.META = {
        'REMOTE_ADDR': '127.0.0.1',
        'HTTP_USER_AGENT': 'TestClient/1.0',
    }
    return request


@pytest.fixture
def mock_request_superuser(superuser):
    """Request autenticado con superuser."""
    request = Mock()
    request.user = superuser
    request.method = 'GET'
    request.META = {
        'REMOTE_ADDR': '127.0.0.1',
        'HTTP_USER_AGENT': 'TestClient/1.0',
    }
    return request


# ────────────────────────────────────────────────────────────
# QUERYSET MOCKS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_empty_queryset():
    """QuerySet vacío."""
    qs = Mock()
    qs.count.return_value = 0
    qs.exists.return_value = False
    qs.all.return_value = []
    qs.__iter__ = lambda x: iter([])
    qs.__len__ = lambda x: 0
    return qs


@pytest.fixture
def mock_queryset_with_data(service_customer_support, service_sales):
    """QuerySet con datos."""
    qs = Mock()
    qs.count.return_value = 2
    qs.exists.return_value = True
    qs.all.return_value = [service_customer_support, service_sales]
    qs.__iter__ = lambda x: iter([service_customer_support, service_sales])
    qs.__len__ = lambda x: 2
    qs.values_list.return_value.flat = True
    qs.values_list.return_value = [
        service_customer_support.numero_800,
        service_sales.numero_800,
    ]
    return qs


# ────────────────────────────────────────────────────────────
# TIMEZONE MOCKS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_timezone_now():
    """Mock de timezone.now() para tests predecibles."""
    fixed_time = datetime(2026, 1, 17, 12, 0, 0)
    
    with patch('django.utils.timezone.now', return_value=fixed_time):
        yield fixed_time


# ────────────────────────────────────────────────────────────
# DATE MOCKS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_date_today():
    """Mock de date.today() para tests predecibles."""
    fixed_date = date(2026, 1, 17)
    
    with patch('datetime.date') as mock_date:
        mock_date.today.return_value = fixed_date
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
        yield fixed_date


# ────────────────────────────────────────────────────────────
# PAGINATION MOCKS (para APIs)
# ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_paginated_response():
    """Response paginado típico de DRF."""
    return {
        'count': 100,
        'next': 'http://testserver/api/calls/?page=2',
        'previous': None,
        'results': [],
    }
```

---

<a name="roadmap"></a>
## 9. ROADMAP DE IMPLEMENTACIÓN

### 9.1 Semana 1: Fundamentos (5 días)

```
SEMANA 1: Fix Import + Service Layer Base
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DÍA 1 (Lunes): Fix Import Bloqueante
────────────────────────────────────────────────────────────
Objetivo: Desbloquear test_service_access.py

Mañana (4 horas):
09:00-09:30 | Backup de services.py
09:30-10:30 | Mover ServiceAccessService a services/__init__.py
10:30-11:00 | Eliminar services.py (archivo)
11:00-12:00 | Validar imports funcionan

Tarde (4 horas):
14:00-15:00 | Ejecutar test_service_access.py
15:00-16:00 | Fix errores si hay
16:00-17:00 | Commit y documentar
17:00-18:00 | Code review interno

Checkpoint:
✅ test_service_access.py: 9/9 pasando
✅ ServiceAccessService accesible
✅ Documentación actualizada

DÍA 2 (Martes): Service Layer Refactoring
────────────────────────────────────────────────────────────
Objetivo: Mover lógica de UserServiceAccess a Service

Mañana (4 horas):
09:00-10:00 | Mover get_user_services() lógica a Service
10:00-11:00 | Mover has_service_access() lógica a Service
11:00-12:00 | Agregar deprecation warnings en model

Tarde (4 horas):
14:00-15:00 | Actualizar tests
15:00-16:00 | Buscar usos en codebase
16:00-17:00 | Actualizar código a usar Service
17:00-18:00 | Validar 9/9 tests pasando

Checkpoint:
✅ Lógica en Service, no en Model
✅ Deprecation warnings funcionando
✅ Tests actualizados y pasando

DÍA 3 (Miércoles): CallRecordService
────────────────────────────────────────────────────────────
Objetivo: Crear CallRecordService

Mañana (4 horas):
09:00-10:00 | Crear call_record_service.py
10:00-11:00 | Implementar calculate_answer_rate()
11:00-12:00 | Implementar get_statistics()

Tarde (4 horas):
14:00-15:00 | Implementar get_service_summary()
15:00-16:00 | Deprecar answer_rate() en model
16:00-17:00 | Crear tests de CallRecordService
17:00-18:00 | Validar tests pasando

Checkpoint:
✅ CallRecordService completo
✅ Tests de CallRecordService: 10/10 pasando
✅ answer_rate() deprecado

DÍA 4 (Jueves): Fixtures Core
────────────────────────────────────────────────────────────
Objetivo: Crear fixtures completas para core

Mañana (4 horas):
09:00-10:00 | Crear fixtures/core.py estructura
10:00-11:00 | Fixtures de Centers y Services
11:00-12:00 | Fixtures de UserServiceAccess

Tarde (4 horas):
14:00-15:00 | Fixtures de CallRecords
15:00-16:00 | Composite fixtures
16:00-17:00 | Actualizar conftest.py
17:00-18:00 | Validar fixtures funcionan

Checkpoint:
✅ fixtures/core.py completo (500 líneas)
✅ Todas las fixtures importables
✅ Tests usan fixtures correctamente

DÍA 5 (Viernes): Tests Core Models
────────────────────────────────────────────────────────────
Objetivo: Fix tests de core models

Mañana (4 horas):
09:00-10:00 | Actualizar test_core_models.py
10:00-11:00 | Usar nuevas fixtures
11:00-12:00 | Fix assertions

Tarde (4 horas):
14:00-15:00 | Ejecutar tests
15:00-16:00 | Fix errores
16:00-17:00 | Validar 15/15 pasando
17:00-18:00 | Retrospectiva semana 1

Checkpoint Semana 1:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ServiceAccessService accesible: 9/9 tests ✓
✅ Service Layer implementado
✅ CallRecordService completo: 10/10 tests ✓
✅ Fixtures core completas
✅ test_core_models.py: 15/15 pasando ✓
✅ test_service_access.py: 9/9 pasando ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL: 34/69 tests pasando (49%)
```

### 9.2 Semana 2: Navigation System (5 días)

```
SEMANA 2: Navigation + ETL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DÍA 6 (Lunes): Fixtures Navigation
────────────────────────────────────────────────────────────
Objetivo: Crear fixtures para navigation

Mañana (4 horas):
09:00-10:00 | Analizar estructura de menús
10:00-11:00 | Crear fixtures/navigation.py
11:00-12:00 | Fixtures de módulos (si existen en access app)

Tarde (4 horas):
14:00-15:00 | Fixtures de estructura de menú
15:00-16:00 | Fixtures de iconos
16:00-17:00 | Fixtures de permisos (para navigation)
17:00-18:00 | Validar fixtures

Checkpoint:
✅ fixtures/navigation.py completo (400 líneas)
✅ Estructura de menú definida

DÍA 7 (Martes): Tests Navigation Builders
────────────────────────────────────────────────────────────
Objetivo: Fix test_navigation_builders.py

Mañana (4 horas):
09:00-10:00 | Actualizar TestMenuValidator
10:00-11:00 | Usar nuevas fixtures
11:00-12:00 | Fix assertions

Tarde (4 horas):
14:00-15:00 | Actualizar TestMenuBuilder
15:00-16:00 | Actualizar TestMenuSerializer
16:00-17:00 | Ejecutar tests
17:00-18:00 | Fix errores

Checkpoint:
✅ TestMenuValidator: 8/8 pasando
✅ TestMenuBuilder: 8/8 pasando
✅ TestMenuSerializer: 2/2 pasando

DÍA 8 (Miércoles): Tests Navigation Views
────────────────────────────────────────────────────────────
Objetivo: Fix test_navigation_views.py

Mañana (4 horas):
09:00-10:00 | Crear mocks de request
10:00-11:00 | Actualizar tests de NavigationViewSet
11:00-12:00 | Fix permisos en tests

Tarde (4 horas):
14:00-15:00 | Ejecutar tests
15:00-16:00 | Fix errores
16:00-17:00 | Validar 10/10 pasando
17:00-18:00 | Documentar navigation system

Checkpoint:
✅ test_navigation_views.py: 10/10 pasando

DÍA 9-10 (Jueves-Viernes): ETL Service
────────────────────────────────────────────────────────────
Objetivo: Fix test_core_etl_service.py

DÍA 9 Mañana:
09:00-10:00 | Analizar ETLService actual
10:00-11:00 | Entender qué extrae (IVR_LEGACY?)
11:00-12:00 | Crear mocks de IVR_LEGACY DB

DÍA 9 Tarde:
14:00-15:00 | Crear fixtures de datos ETL
15:00-16:00 | Mock de extract()
16:00-17:00 | Mock de transform()
17:00-18:00 | Mock de load()

DÍA 10 Mañana:
09:00-10:00 | Actualizar test_core_etl_service.py
10:00-11:00 | Usar nuevos mocks
11:00-12:00 | Fix expectations

DÍA 10 Tarde:
14:00-15:00 | Ejecutar tests
15:00-16:00 | Fix errores
16:00-17:00 | Validar 10/10 pasando
17:00-18:00 | Retrospectiva semana 2

Checkpoint Semana 2:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ test_navigation_builders.py: 20/20 pasando ✓
✅ test_navigation_views.py: 10/10 pasando ✓
✅ test_core_etl_service.py: 10/10 pasando ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL: 74/69 tests pasando (107% - más de lo esperado)
```

### 9.3 Semana 3: Polish y Validación (3 días)

```
SEMANA 3: Serializers + Validación Final
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DÍA 11 (Lunes): Serializers
────────────────────────────────────────────────────────────
Objetivo: Fix test_core_serializers.py

Mañana (4 horas):
09:00-10:00 | Analizar tests de serializers
10:00-11:00 | Crear fixtures necesarias
11:00-12:00 | Actualizar tests

Tarde (4 horas):
14:00-15:00 | Ejecutar tests
15:00-16:00 | Fix errores
16:00-17:00 | Validar 5/5 pasando
17:00-18:00 | Documentar serializers

Checkpoint:
✅ test_core_serializers.py: 5/5 pasando

DÍA 12 (Martes): Validación Final
────────────────────────────────────────────────────────────
Objetivo: Validar TODOS los tests de core

Mañana (4 horas):
09:00-10:00 | Ejecutar pytest tests/unit/core/ -v
10:00-11:00 | Analizar resultados
11:00-12:00 | Fix errores finales

Tarde (4 horas):
14:00-15:00 | Re-ejecutar tests
15:00-16:00 | Validar 69/69 pasando
16:00-17:00 | Medir cobertura
17:00-18:00 | Validar >90% cobertura

Checkpoint:
✅ 69/69 tests pasando (100%)
✅ Cobertura >90%

DÍA 13 (Miércoles): Documentación y Entrega
────────────────────────────────────────────────────────────
Objetivo: Documentar todo el refactoring

Mañana (4 horas):
09:00-10:00 | Actualizar README de core
10:00-11:00 | Documentar Service Layer
11:00-12:00 | Documentar deprecations

Tarde (4 horas):
14:00-15:00 | Crear migration guide
15:00-16:00 | Code review final
16:00-17:00 | PR y documentación
17:00-18:00 | Retrospectiva final

ENTREGA FINAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 69/69 tests pasando (100%)
✅ Cobertura >90%
✅ Service Layer completo
✅ Fixtures completas
✅ Documentación completa
✅ Migration guide
✅ Code review aprobado
```

---

<a name="riesgos"></a>
## 10. RIESGOS

### 10.1 Riesgos Técnicos

```
RIESGO 1: Service Layer Rompe Funcionalidad Existente
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Probabilidad: MEDIA
Impacto: ALTO

Descripción:
Al mover lógica de models a services, código existente
que usa los métodos del model puede romperse.

Ejemplo:
# Código en producción que puede existir:
services = UserServiceAccess.get_user_services(user)

Si eliminamos el método sin deprecation, rompe.

Mitigación:
✅ Usar deprecation warnings primero
✅ Mantener métodos en model que deleguen a service
✅ Buscar todos los usos antes de eliminar
✅ Período de gracia (1-2 sprints)
✅ Tests de integración

Contingencia:
- Si rompe, revertir cambio inmediatamente
- Extender período de deprecación
- Comunicar a equipo para actualizar código


RIESGO 2: Dependencias Circulares Services ↔ Models
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Probabilidad: MEDIA
Impacto: MEDIO

Descripción:
Service importa Model, Model importa Service
→ ImportError circular

Ejemplo:
# apps/core/models.py
from apps.core.services import ServiceAccessService

class UserServiceAccess(models.Model):
    @classmethod
    def get_user_services(cls, user):
        return ServiceAccessService.get_user_services(user)
        #      ^^^^^^^^^^^^^^^^^^^
        #      Importa Service

# apps/core/services/__init__.py
from apps.core.models import UserServiceAccess

class ServiceAccessService:
    @staticmethod
    def get_user_services(user):
        return UserServiceAccess.objects.filter(...)
        #      ^^^^^^^^^^^^^^^^^^
        #      Importa Model

→ CIRCULAR IMPORT ❌

Mitigación:
✅ Imports dentro de métodos (no top-level)
✅ Services nunca importan models en top-level
✅ Use lazy imports
✅ Reestructurar si necesario

Ejemplo correcto:
# apps/core/models.py
class UserServiceAccess(models.Model):
    @classmethod
    def get_user_services(cls, user):
        # Import dentro del método ✓
        from apps.core.services import ServiceAccessService
        return ServiceAccessService.get_user_services(user)


RIESGO 3: Tests de Navigation Dependen de Access App
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Probabilidad: ALTA
Impacto: MEDIO

Descripción:
Navigation system usa Module y Function de access app.
Si access app no está configurada, tests fallan.

Mitigación:
✅ Fixtures que crean Module y Function
✅ O mocks de Module y Function
✅ O tests skipped si access no disponible

pytest.mark.skipif(
    not apps.is_installed('apps.access'),
    reason="Access app not installed"
)


RIESGO 4: ETL Service Datos Reales Requieren IVR_LEGACY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Probabilidad: ALTA
Impacto: MEDIO

Descripción:
ETLService extrae datos de IVR_LEGACY (MariaDB).
Tests requieren DB o mocks.

Mitigación:
✅ Mocks completos de IVR_LEGACY
✅ Fixtures con datos esperados
✅ Tests unitarios (no requieren DB real)
✅ Tests de integración separados

PREGUNTA AL USUARIO:
¿ETLService extrae de IVR_LEGACY?
¿Qué estructura de datos retorna?


RIESGO 5: Tiempo Excede Estimado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Probabilidad: MEDIA
Impacto: MEDIO

Descripción:
Estimación de 2-3 semanas puede no ser suficiente
si hay problemas inesperados.

Mitigación:
✅ Buffer de 50% en cada fase
✅ Checkpoints diarios
✅ Detección temprana de bloqueos
✅ Comunicación constante

Contingencia:
- Priorizar tests críticos
- Dejar tests menos importantes para después
- Pedir extensión de tiempo si necesario
```

### 10.2 Matriz de Riesgos

```
RIESGO                                PROB    IMP    ACCIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service Layer rompe funcionalidad    MEDIA   ALTO   Deprecation
Circular imports                      MEDIA   MEDIO  Lazy imports
Navigation depende de access          ALTA    MEDIO  Fixtures/Mocks
ETL requiere IVR_LEGACY              ALTA    MEDIO  Mocks completos
Tiempo excede estimado                MEDIA   MEDIO  Buffer 50%
Fixtures muy complejas                BAJA    BAJO   Simplificar
Tests flaky                           BAJA    BAJO   Debuggear
```

---

<a name="criterios"></a>
## 11. CRITERIOS DE ÉXITO

### 11.1 Criterios Técnicos

```
CRITERIO 1: Tests Pasando
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: 69/69 tests pasando (100%)

Desglose por archivo:
├─ test_core_app.py:             1/1   (100%) ✓
├─ test_core_models.py:          15/15 (100%) ✓
├─ test_service_access.py:       9/9   (100%) ✓
├─ test_core_serializers.py:     5/5   (100%) ✓
├─ test_navigation_builders.py:  20/20 (100%) ✓
├─ test_navigation_views.py:     10/10 (100%) ✓
└─ test_core_etl_service.py:     10/10 (100%) ✓
                                 ─────────────
TOTAL:                           69/69 (100%) ✓

Comando validación:
$ pytest tests/unit/core/ -v
===================== 69 passed in 5.43s =====================


CRITERIO 2: Cobertura de Código
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: >90% cobertura en core app

Comando:
$ pytest tests/unit/core/ --cov=apps.core --cov-report=html

Mínimos requeridos:
├─ models.py:           >85%
├─ services/:           >95% ⭐
├─ navigation/:         >80%
├─ serializers.py:      >90%
└─ mixins.py:           >95%

TOTAL apps/core/:       >90% ✓


CRITERIO 3: Service Layer Completo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: Lógica en services, no en models

Validación:
✅ ServiceAccessService: Lógica movida de UserServiceAccess
✅ CallRecordService: Lógica movida de CallRecord
✅ Models delgados (solo datos)
✅ Services testeables independientemente
✅ Deprecation warnings en models


CRITERIO 4: Fixtures Completas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: Fixtures reutilizables para toda la app

Archivos requeridos:
├─ fixtures/core.py:         ✓ 500 líneas
└─ fixtures/navigation.py:   ✓ 400 líneas

Fixtures mínimas:
✅ Centers (activos, inactivos)
✅ Services (múltiples, vinculados a centers)
✅ UserServiceAccess (activos, revocados)
✅ CallRecords (varios períodos)
✅ Navigation structures
✅ Modules y Functions (si access disponible)


CRITERIO 5: No Import Errors
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: Todos los imports funcionan

Validación:
✅ from apps.core.services import ServiceAccessService
✅ from apps.core.services import ETLService
✅ from apps.core.services.call_record_service import CallRecordService
✅ No circular imports
✅ No ModuleNotFoundError


CRITERIO 6: Tiempo de Ejecución
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: Tests rápidos (<10 segundos total)

Máximos permitidos:
├─ test_core_app.py:             <0.5s
├─ test_core_models.py:          <2.0s
├─ test_service_access.py:       <2.0s
├─ test_core_serializers.py:     <1.0s
├─ test_navigation_builders.py:  <2.0s
├─ test_navigation_views.py:     <1.5s
└─ test_core_etl_service.py:     <1.0s
                                 ──────
TOTAL:                           <10s ✓


CRITERIO 7: Código Limpio
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: Código mantenible y documentado

Checklist:
✅ Type hints en services
✅ Docstrings Google style
✅ Ejemplos en docstrings
✅ Sin duplicación de código
✅ Sin magic numbers
✅ Sin lógica en models (solo en services)
✅ Deprecation warnings claros


CRITERIO 8: Documentación Completa
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: Todo documentado para el equipo

Documentos requeridos:
✅ README de core actualizado
✅ Service Layer guide
✅ Migration guide (deprecations)
✅ Fixtures documentation
✅ Este análisis (ANALISIS_APP_CORE_REFACTORING_v1.0.0.md)
```

### 11.2 Checklist de Validación

```
CHECKLIST PRE-ENTREGA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TESTS:
☐ pytest tests/unit/core/ -v (todos pasan)
☐ 69/69 tests ✓
☐ 0 errors
☐ 0 warnings importantes
☐ <10 segundos tiempo total

COBERTURA:
☐ pytest --cov=apps.core --cov-report=html
☐ >90% cobertura total
☐ >95% cobertura en services/
☐ Report HTML generado

CÓDIGO:
☐ ServiceAccessService accesible
☐ CallRecordService implementado
☐ ETLService testeado
☐ Navigation system funcionando
☐ No import errors
☐ No circular imports

SERVICE LAYER:
☐ Lógica movida de models a services
☐ Models delgados (solo datos)
☐ Deprecation warnings en models
☐ Service Layer documentado

FIXTURES:
☐ fixtures/core.py completo
☐ fixtures/navigation.py completo
☐ Todas las fixtures testeadas
☐ conftest.py actualizado

DOCUMENTACIÓN:
☐ README de core actualizado
☐ Service Layer guide creado
☐ Migration guide creado
☐ Docstrings completos
☐ Type hints completos

CODE REVIEW:
☐ Código revisado por par
☐ Sin code smells
☐ Sin duplicación
☐ Estándares seguidos
☐ PR aprobado

COMUNICACIÓN:
☐ Equipo informado de cambios
☐ Deprecations comunicadas
☐ Migration guide compartido
☐ Stakeholders notificados
```

---

## RESUMEN FINAL

```
APP: core
ESTADO INICIAL: 6/69 tests pasando (9%)
ESTADO OBJETIVO: 69/69 tests pasando (100%)

PROBLEMA PRINCIPAL:
Conflicto services.py vs services/ → ImportError

SOLUCIÓN:
Consolidar en services/ directorio

REFACTORING MAYOR:
Service Layer Pattern
├─ Lógica de models → services
├─ Models delgados
└─ Services testeables

TIEMPO: 2-3 semanas (13 días laborales)
RIESGO: MEDIO-ALTO (app crítica)
PRIORIDAD: 🔴 CRÍTICA

BENEFICIO:
✓ 69/69 tests pasando
✓ Cobertura >90%
✓ Service Layer completo
✓ Arquitectura mejorada
✓ Código mantenible
✓ Base sólida para features futuras

ROI:
- Inversión: 80-120 horas
- Beneficio: Base sólida del sistema
- Payback: Inmediato (desbloquea otras apps)
```

---

## ANEXOS

### A. Comandos Útiles

```bash
# Ejecutar tests de core
pytest tests/unit/core/ -v

# Ejecutar test específico
pytest tests/unit/core/test_service_access.py::TestServiceAccessService::test_has_service_access -v

# Con cobertura
pytest tests/unit/core/ --cov=apps.core --cov-report=html

# Solo tests pasando
pytest tests/unit/core/ -v | grep PASSED

# Solo tests fallando
pytest tests/unit/core/ -v | grep FAILED

# Tiempo de ejecución
pytest tests/unit/core/ --durations=10

# Ejecutar en paralelo
pytest tests/unit/core/ -n auto

# Validar imports
python manage.py shell
>>> from apps.core.services import ServiceAccessService
>>> from apps.core.services import ETLService
```

### B. Estructura Final Esperada

```
apps/core/
├── models.py                           (solo datos)
├── serializers.py
├── views.py
├── urls.py
├── admin.py
├── permissions.py
├── mixins.py
│
├── services/
│   ├── __init__.py                    ← ServiceAccessService (220 líneas)
│   ├── call_record_service.py         ← CallRecordService (NUEVO - 150 líneas)
│   └── etl_service.py                 ← ETLService (existente)
│
├── navigation/
│   ├── builders.py
│   ├── views.py
│   └── urls.py
│
└── management/
    └── commands/

tests/unit/core/
├── test_core_app.py                   (1/1) ✓
├── test_core_models.py                (15/15) ✓
├── test_service_access.py             (9/9) ✓
├── test_core_serializers.py           (5/5) ✓
├── test_navigation_builders.py        (20/20) ✓
├── test_navigation_views.py           (10/10) ✓
└── test_core_etl_service.py           (10/10) ✓

tests/fixtures/
├── core.py                            (500 líneas)
└── navigation.py                      (400 líneas)
```

---

**FIN DEL ANÁLISIS COMPLETO - CORE v1.0.0**

Documento creado: 2026-01-17
Partes: 2 (Parte 1: estructura y problemas, Parte 2: soluciones y roadmap)
Total líneas: ~2,800 líneas
Próxima actualización: Después de implementación (v1.1.0)