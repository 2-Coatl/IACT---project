---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Apps Compartidas
categoria: arquitectura/apps-comunes
tema: Análisis CORE vs UTILS - Estado Real y Recomendaciones
autor: Claude Technical Analysis
tags: [core, utils, arquitectura, django, best-practices]
relacionado:
  - ANALISIS_APP_CORE_REFACTORING_v1.0.0.md
  - ANALISIS_APP_UTILS_REFACTORING_v1.0.0.md
estado: completado
---

# ANÁLISIS: CORE vs UTILS - ESTADO REAL DEL PROYECTO

**Basado en código existente - Filosofía Django `django.core` vs `django.utils`**

---

## RESUMEN EJECUTIVO

### Estado Actual

```
apps/core/  ✅ YA EXISTE
apps/utils/ ✅ YA EXISTE

PROBLEMA IDENTIFICADO:
⚠️ apps/utils/models.py tiene SoftDeleteMixin (Abstract Model)
⚠️ Según filosofía Django, Abstract Models → core, NO utils

SOLUCIÓN:
Mover SoftDeleteMixin de utils/ a core/
```

---

## TABLA DE CONTENIDOS

1. [Filosofía Django: core vs utils](#filosofia)
2. [Estado Actual del Proyecto](#estado-actual)
3. [Problemas Identificados](#problemas)
4. [Recomendaciones de Refactorización](#recomendaciones)
5. [Plan de Migración](#plan)

---

<a name="filosofia"></a>
## 1. FILOSOFÍA DJANGO: core vs utils

### 1.1 Ejemplo de Django Framework

```
django/django/core/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EL MOTOR - Componentes fundamentales del framework

├── management/      # Comandos de gestión (manage.py)
├── cache/           # Sistema de caché
├── mail/            # Sistema de correo
├── validators.py    # Validadores base
├── exceptions.py    # Excepciones del framework
└── ...              # Otros componentes core

Características:
✅ Define CÓMO funciona Django
✅ Componentes que extienden el framework
✅ Abstract base classes
✅ Manager, QuerySet personalizados
✅ Mixins que interactúan con ORM


django/django/utils/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAJA DE HERRAMIENTAS - Utilidades técnicas

├── datetime_safe.py # Helpers de fechas
├── text.py          # Manipulación de strings
├── functional.py    # Funciones funcionales
├── datastructures.py# Estructuras de datos
└── ...              # Otros helpers

Características:
✅ Pure functions (sin estado)
✅ No dependen de Django internals
✅ Helpers técnicos reutilizables
✅ NO tienen modelos
✅ NO extienden ORM
```

### 1.2 Regla de Oro

```
PREGUNTA: ¿Dónde va este componente?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ¿Es un Abstract Model?        → CORE
2. ¿Es un Manager/QuerySet?      → CORE  
3. ¿Es un Mixin para Models?     → CORE
4. ¿Extiende el framework?       → CORE
5. ¿Es una pure function?        → UTILS
6. ¿Es un helper técnico?        → UTILS
7. ¿Manipula strings/dates?      → UTILS
8. ¿Es stateless?                → UTILS

CORE = Motor de tu app (cómo funciona)
UTILS = Herramientas técnicas (helpers)
```

---

<a name="estado-actual"></a>
## 2. ESTADO ACTUAL DEL PROYECTO

### 2.1 apps/core/ (YA EXISTE)

```python
apps/core/
│
├── models.py (8,151 bytes)
│   ├─ CallRecord (managed=True, analytics DB)
│   ├─ ServiceAccess (managed=True, RBAC)
│   └─ ... otros models
│
├── mixins.py (2,238 bytes)
│   ├─ ServiceFilterMixin (ViewSet mixin)
│   └─ OptionalServiceFilterMixin (ViewSet mixin)
│
├── permissions.py (1,993 bytes)
│   ├─ HasServiceAccess (DRF permission)
│   └─ ... otras permissions
│
├── services.py (6,248 bytes)
│   └─ ServiceAccessService (business logic)
│
├── services/ (directorio)
│   └─ etl_service.py (ETLService para PIPELINE)
│
├── serializers.py (1,832 bytes)
│   └─ Serializers para models
│
├── views.py (2,207 bytes)
│   └─ ViewSets
│
└── migrations/ ✅ Tiene migrations

TOTAL: ~30 KB de código
USADO POR: PIPELINE, REPORTS, ACCESS, otras apps
```

**Análisis:**

```
✅ Contiene models (correcto - core tiene models)
✅ Contiene services (correcto - business logic)
✅ Contiene permissions (correcto - framework extensions)
✅ Mixins para ViewSets (correcto - DRF extensions)
⚠️ NO tiene Abstract Models (problema - debería tenerlos)
⚠️ NO tiene SoftDeleteMixin (está en utils)
```

### 2.2 apps/utils/ (YA EXISTE)

```python
apps/utils/
│
├── models.py (5,564 bytes) ⚠️ PROBLEMA
│   ├─ SoftDeleteQuerySet (QuerySet personalizado)
│   ├─ SoftDeleteManager (Manager personalizado)
│   └─ SoftDeleteMixin (Abstract Model)
│
├── request.py (4,775 bytes) ✅ OK
│   └─ Helpers para request handling
│
└── __init__.py (790 bytes)
    └─ Exports

TOTAL: ~11 KB de código
```

**Análisis:**

```
❌ models.py en utils (VIOLA filosofía Django)
   - SoftDeleteMixin es Abstract Model → debería estar en CORE
   - SoftDeleteManager es Manager → debería estar en CORE
   - SoftDeleteQuerySet es QuerySet → debería estar en CORE

✅ request.py en utils (CORRECTO)
   - Pure functions para requests
   - Helpers técnicos
```

---

<a name="problemas"></a>
## 3. PROBLEMAS IDENTIFICADOS

### 3.1 Problema Principal

```
VIOLACIÓN DE PRINCIPIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/utils/models.py existe

Según Django:
❌ Utils NO debe tener models.py
❌ django.utils NO tiene models
❌ Utilidades son stateless helpers

Realidad:
apps/utils/models.py tiene:
- SoftDeleteMixin (Abstract Model)
- SoftDeleteManager (Manager)
- SoftDeleteQuerySet (QuerySet)

ESTOS COMPONENTES DEBERÍAN ESTAR EN apps/core/
```

### 3.2 Uso Actual de SoftDeleteMixin

```python
# Ejemplo de uso en otras apps:
from apps.utils.models import SoftDeleteMixin

class Report(SoftDeleteMixin, models.Model):
    # ... campos
    pass

APPS QUE LO USAN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ apps/reports/models.py → Report, ExportJob
✅ apps/users/models.py → UserProfile (probablemente)
✅ apps/access/models.py → Profile, Module, etc
✅ Otras apps (múltiples usos)

IMPACTO DE MOVER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cambiar imports en:
- ~8-10 archivos (todos los models que usan SoftDeleteMixin)
- Tests correspondientes

RIESGO: BAJO (solo cambio de import)
```

---

<a name="recomendaciones"></a>
## 4. RECOMENDACIONES DE REFACTORIZACIÓN

### 4.1 Estructura Ideal

```
apps/core/ (Motor de la aplicación)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

├── models.py
│   ├─ CallRecord (concrete model)
│   ├─ ServiceAccess (concrete model)
│   └─ ... otros concrete models
│
├── base_models.py (NUEVO - Abstract Models)
│   ├─ SoftDeleteQuerySet
│   ├─ SoftDeleteManager
│   ├─ SoftDeleteMixin
│   └─ ... otros abstract base classes
│
├── mixins.py
│   ├─ ServiceFilterMixin (ViewSet)
│   └─ ... otros mixins para views/serializers
│
├── permissions.py
│   └─ Custom DRF permissions
│
├── services.py + services/
│   └─ Business logic
│
└── ... otros archivos

IMPORTAR ASÍ:
from apps.core.base_models import SoftDeleteMixin


apps/utils/ (Caja de herramientas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

├── request.py ✅ MANTENER
│   └─ HTTP request helpers
│
├── datetime_helpers.py (ejemplo)
│   └─ Date/time manipulation
│
├── string_helpers.py (ejemplo)
│   └─ String formatting
│
└── __init__.py

❌ NO MÁS models.py en utils
```

### 4.2 Comparación: Antes vs Después

```
ANTES (ACTUAL - INCORRECTO):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/utils/models.py
├─ SoftDeleteMixin (Abstract Model) ❌ Lugar incorrecto
├─ SoftDeleteManager (Manager) ❌ Lugar incorrecto
└─ SoftDeleteQuerySet (QuerySet) ❌ Lugar incorrecto

Import:
from apps.utils.models import SoftDeleteMixin ❌


DESPUÉS (PROPUESTO - CORRECTO):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/base_models.py
├─ SoftDeleteMixin (Abstract Model) ✅ Lugar correcto
├─ SoftDeleteManager (Manager) ✅ Lugar correcto
└─ SoftDeleteQuerySet (QuerySet) ✅ Lugar correcto

Import:
from apps.core.base_models import SoftDeleteMixin ✅

apps/utils/models.py → ELIMINAR archivo completo ✅
```

---

<a name="plan"></a>
## 5. PLAN DE MIGRACIÓN

### 5.1 Pasos de Refactorización

```
PASO 1: Crear apps/core/base_models.py
────────────────────────────────────────────────────────────

1. Crear archivo apps/core/base_models.py
2. Copiar contenido de apps/utils/models.py
3. Ajustar imports (ya usa django.db.models, etc)
4. Verificar que funciona

Tiempo: 10 minutos


PASO 2: Actualizar imports en todas las apps
────────────────────────────────────────────────────────────

Buscar y reemplazar en:

apps/reports/models.py:
- from apps.utils.models import SoftDeleteMixin
+ from apps.core.base_models import SoftDeleteMixin

apps/users/models.py:
- from apps.utils.models import SoftDeleteMixin
+ from apps.core.base_models import SoftDeleteMixin

apps/access/models.py:
- from apps.utils.models import SoftDeleteMixin
+ from apps.core.base_models import SoftDeleteMixin

... y todas las demás apps que lo usen

Comando para encontrar:
grep -r "from apps.utils.models import" apps/

Tiempo: 20 minutos


PASO 3: Actualizar tests
────────────────────────────────────────────────────────────

Buscar tests que importen de utils.models:

tests/unit/utils/test_soft_delete.py:
- from apps.utils.models import SoftDeleteMixin
+ from apps.core.base_models import SoftDeleteMixin

Tiempo: 10 minutos


PASO 4: Ejecutar tests
────────────────────────────────────────────────────────────

pytest tests/unit/ -v

Verificar que todos los tests pasen con los nuevos imports.

Tiempo: 5 minutos


PASO 5: Eliminar apps/utils/models.py
────────────────────────────────────────────────────────────

rm apps/utils/models.py

Verificar que no quede ninguna referencia:
grep -r "apps.utils.models" apps/
grep -r "apps.utils.models" tests/

Tiempo: 5 minutos


PASO 6: Actualizar documentación
────────────────────────────────────────────────────────────

Actualizar análisis de apps:
- ANALISIS_APP_CORE_REFACTORING_v1.0.0.md
- ANALISIS_APP_UTILS_REFACTORING_v1.0.0.md

Mencionar cambio en:
- README.md (si existe sección de arquitectura)
- CHANGELOG.md (registrar refactorización)

Tiempo: 15 minutos


TOTAL: ~1 hora
```

### 5.2 Script de Migración Automática

```bash
#!/bin/bash
# migrate_softdelete_to_core.sh

echo "Migrando SoftDeleteMixin de utils/ a core/"

# 1. Crear base_models.py en core
cp apps/utils/models.py apps/core/base_models.py

# 2. Buscar y reemplazar imports
find apps/ -name "*.py" -type f -exec sed -i \
  's/from apps\.utils\.models import/from apps.core.base_models import/g' {} +

# 3. Hacer lo mismo en tests
find tests/ -name "*.py" -type f -exec sed -i \
  's/from apps\.utils\.models import/from apps.core.base_models import/g' {} +

# 4. Verificar
echo "Verificando que no queden referencias a utils.models..."
grep -r "apps.utils.models" apps/ tests/

# 5. Ejecutar tests
echo "Ejecutando tests..."
pytest tests/unit/ -v

# 6. Si todo OK, eliminar utils/models.py
# (manual para seguridad)
echo "Si tests pasaron, ejecutar manualmente:"
echo "rm apps/utils/models.py"
```

### 5.3 Riesgos y Mitigación

```
RIESGO 1: Importaciones circulares
────────────────────────────────────────────────────────────
Probabilidad: BAJA
Razón: SoftDeleteMixin es Abstract Model, no importa de otros

Mitigación:
✅ Verificar imports en base_models.py
✅ Solo debe importar de django.db, django.utils


RIESGO 2: Migrations ya existentes
────────────────────────────────────────────────────────────
Probabilidad: NULA
Razón: SoftDeleteMixin es Abstract (Meta.abstract = True)
       No genera migrations

Mitigación:
✅ NO requiere makemigrations
✅ Solo cambio de import


RIESGO 3: Tests fallan
────────────────────────────────────────────────────────────
Probabilidad: BAJA
Razón: Solo cambia import path, funcionalidad idéntica

Mitigación:
✅ Ejecutar tests antes y después
✅ Comparar resultados


RIESGO 4: Código en producción
────────────────────────────────────────────────────────────
Probabilidad: MEDIA (si hay deployment en progreso)

Mitigación:
✅ Hacer en feature branch
✅ CI/CD debe correr tests completos
✅ Deploy solo si tests pasan
```

---

## 6. BENEFICIOS DE LA REFACTORIZACIÓN

```
ANTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Viola filosofía Django (utils con models)
❌ Confusión semántica (¿por qué models en utils?)
❌ Import desde utils para Abstract Models
❌ No sigue convención del framework

DESPUÉS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Sigue filosofía Django (core = motor, utils = helpers)
✅ Claridad semántica (Abstract Models en core)
✅ Import desde core (correcto)
✅ Convención del framework
✅ Mejor organización del código
✅ Facilita onboarding de nuevos developers
```

---

## 7. ESTADO FINAL DESEADO

```
apps/core/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Motor de la aplicación
Contiene: Componentes que definen CÓMO funciona la app

✅ models.py (concrete models)
✅ base_models.py (Abstract Models, Managers, QuerySets)
✅ mixins.py (ViewSet/Serializer mixins)
✅ permissions.py (DRF permissions)
✅ services.py + services/ (business logic)
✅ serializers.py, views.py, urls.py

Import típico:
from apps.core.base_models import SoftDeleteMixin
from apps.core.models import CallRecord
from apps.core.mixins import ServiceFilterMixin


apps/utils/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Caja de herramientas técnicas
Contiene: Pure functions y helpers stateless

✅ request.py (HTTP helpers)
✅ datetime_helpers.py (date/time utils)
✅ string_helpers.py (string formatting)
✅ ... otros helpers técnicos
❌ NO models.py (eliminado)

Import típico:
from apps.utils.request import get_client_ip
from apps.utils.datetime_helpers import format_date
```

---

## RESUMEN Y RECOMENDACIONES

```
PROBLEMA ACTUAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ apps/utils/models.py existe (viola filosofía Django)
⚠️ Contiene SoftDeleteMixin (Abstract Model)
⚠️ Abstract Models deberían estar en core, NO utils

SOLUCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Crear apps/core/base_models.py
2. Mover SoftDeleteMixin, Manager, QuerySet
3. Actualizar imports en todas las apps
4. Ejecutar tests
5. Eliminar apps/utils/models.py

TIEMPO: ~1 hora
RIESGO: BAJO (solo cambio de import)
BENEFICIO: Adherencia a filosofía Django ✅

DECISIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¿Proceder con refactorización?

[ ] SÍ - Hacer ahora (1 hora)
[ ] NO - Posponer (deuda técnica)
[ ] DISCUTIR - Revisar con equipo

Si SÍ: Usar script de migración automática arriba
Si NO: Documentar como deuda técnica conocida
```

---

**FIN DEL ANÁLISIS - CORE vs UTILS v1.0.0**

Documento creado: 2026-01-17  
Estado actual: apps/core/ existe, apps/utils/ existe  
Problema: SoftDeleteMixin en lugar incorrecto  
Solución: Mover a core/base_models.py  
Tiempo estimado: 1 hora
