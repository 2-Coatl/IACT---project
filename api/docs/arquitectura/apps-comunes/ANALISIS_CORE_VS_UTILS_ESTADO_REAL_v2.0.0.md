---
version: 2.0.0
date: 2026-01-18
project: IACT Call Center System
type: Análisis de Arquitectura - Apps Compartidas
categoria: arquitectura/apps-comunes
tema: Análisis CORE vs UTILS - Estado Real y Recomendaciones
autor: Claude Technical Analysis
tags: [core, utils, arquitectura, django, best-practices, functions-vs-classes]
relacionado:
  - ANALISIS_APP_CORE_v2.0.0.md
  - CLEAN_CODE_NAMING_PRINCIPLES_v2_3_1.md
estado: completado
replaces: ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v1.0.0.md
changelog: |
  v2.0.0 (2026-01-18):
  - Enfatiza diferencia clave: utils/ = FUNCIONES, core/ = CLASES
  - Agrega sección "La Diferencia Fundamental: Funciones vs Clases"
  - Actualiza ejemplos con patrón correcto
  - Clarifica que utils/ NO debe tener ninguna clase, solo funciones
  - Actualiza plan de migración
  v1.0.0 (2026-01-17):
  - Versión inicial
---

# ANÁLISIS: CORE vs UTILS - ESTADO REAL DEL PROYECTO v2.0.0

**Basado en código existente - Filosofía Django `django.core` vs `django.utils`**

---

## RESUMEN EJECUTIVO

### Estado Actual

```
apps/core/  ✅ YA EXISTE
apps/utils/ ✅ YA EXISTE

PROBLEMA IDENTIFICADO v2.0.0:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ apps/utils/models.py tiene CLASES (SoftDeleteMixin, Manager, QuerySet)
⚠️ utils/ debe tener SOLO FUNCIONES
⚠️ CLASES (incluyendo Abstract Models) → core/, NO utils/

SOLUCIÓN:
Mover TODAS las clases de utils/ a core/
Dejar SOLO funciones en utils/
```

### Cambios desde v1.0.0

```
v1.0.0 decía:
❌ "Abstract Models → core"

v2.0.0 ACLARA:
✅ "TODAS LAS CLASES → core/ (incluyendo abstract models)"
✅ "SOLO FUNCIONES → utils/"
✅ La diferencia NO es abstract vs concrete
✅ La diferencia ES función vs clase
```

---

## TABLA DE CONTENIDOS

1. [La Diferencia Fundamental: Funciones vs Clases](#diferencia-fundamental)
2. [Filosofía Django: core vs utils](#filosofia)
3. [Estado Actual del Proyecto](#estado-actual)
4. [Problemas Identificados](#problemas)
5. [Recomendaciones de Refactorización](#recomendaciones)
6. [Plan de Migración](#plan)

---

<a name="diferencia-fundamental"></a>
## 1. LA DIFERENCIA FUNDAMENTAL: FUNCIONES vs CLASES

### 1.1 La Clave para Decidir

```
PREGUNTA ÚNICA QUE LO DECIDE TODO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¿Es una FUNCIÓN o una CLASE?

FUNCIÓN  → utils/
CLASE    → core/

¡ES ASÍ DE SIMPLE!
```

### 1.2 Análisis del Patrón Django

```python
# ════════════════════════════════════════════════════════════
# django/utils/ - SOLO FUNCIONES
# ════════════════════════════════════════════════════════════

# django/utils/text.py
def slugify(value):                    # ✅ FUNCIÓN
    """Convierte a slug."""
    return slug

def truncate_words(text, num):         # ✅ FUNCIÓN
    """Trunca texto."""
    return truncated


# django/utils/timezone.py
def now():                             # ✅ FUNCIÓN
    """Obtiene datetime actual."""
    return datetime.now()

def localtime(value):                  # ✅ FUNCIÓN
    """Convierte a zona local."""
    return local_dt


# django/utils/html.py
def escape(text):                      # ✅ FUNCIÓN
    """Escapa HTML."""
    return escaped


# ════════════════════════════════════════════════════════════
# django/core/ - CLASES
# ════════════════════════════════════════════════════════════

# django/core/validators.py
class EmailValidator:                  # ✅ CLASE
    """Valida emails."""
    def __call__(self, value):
        # lógica


# django/core/paginator.py
class Paginator:                       # ✅ CLASE
    """Paginador."""
    def __init__(self, object_list, per_page):
        # lógica


# django/core/exceptions.py
class ValidationError(Exception):      # ✅ CLASE
    """Excepción de validación."""
    pass
```

### 1.3 Patrón Visual

```
django/utils/              apps/utils/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def slugify()       ✅     def get_client_ip()      ✅
def escape()        ✅     def format_phone()       ✅
def now()           ✅     def parse_date()         ✅
def truncate()      ✅     def sanitize_input()    ✅

❌ NO CLASES               ❌ NO CLASES


django/core/               apps/core/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class EmailValidator ✅    class TimeStampedModel   ✅
class Paginator      ✅    class SoftDeleteMixin    ✅
class Signer         ✅    class BusinessException ✅
                           class RequestMiddleware  ✅

❌ NO FUNCIONES            ❌ NO FUNCIONES
```

---

<a name="filosofia"></a>
## 2. FILOSOFÍA DJANGO: core vs utils

### 2.1 django/utils/ - Caja de Herramientas

```
CARACTERÍSTICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ SOLO funciones (def)
✅ Stateless (sin estado)
✅ Pure functions idealmente
✅ Helpers técnicos
✅ No dependen de Django internals

EJEMPLOS:
text.py          → slugify(), truncate()
timezone.py      → now(), localtime()
html.py          → escape(), strip_tags()
encoding.py      → force_str(), force_bytes()
dateformat.py    → format()

❌ NO HAY models.py
❌ NO HAY clases
```

### 2.2 django/core/ - Motor del Framework

```
CARACTERÍSTICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CLASES (class)
✅ Componentes fundamentales
✅ Extienden el framework
✅ Stateful (con estado)
✅ Subsistemas completos

EJEMPLOS:
validators.py    → EmailValidator, URLValidator (CLASES)
paginator.py     → Paginator (CLASE)
exceptions.py    → ValidationError, ObjectDoesNotExist (CLASES)
mail/            → EmailMessage (CLASE)
management/      → BaseCommand (CLASE)
cache/           → Cache (CLASE)
```

### 2.3 Regla de Oro (v2.0.0)

```
PREGUNTA CLAVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¿Qué estoy escribiendo?

def mi_funcion():        → utils/
class MiClase:           → core/

¡ASÍ DE SIMPLE!

NO IMPORTA SI ES:
- Abstract o Concrete
- Mixin o Manager
- QuerySet o Validator
- Exception o Middleware

SI ES CLASE → core/
SI ES FUNCIÓN → utils/
```

---

<a name="estado-actual"></a>
## 3. ESTADO ACTUAL DEL PROYECTO

### 3.1 apps/utils/ (PROBLEMA)

```python
apps/utils/
│
├── models.py (5,564 bytes) ❌ PROBLEMA: Tiene CLASES
│   │
│   ├─ class SoftDeleteQuerySet(models.QuerySet):    ❌ CLASE
│   │      """QuerySet personalizado."""
│   │
│   ├─ class SoftDeleteManager(models.Manager):      ❌ CLASE
│   │      """Manager personalizado."""
│   │
│   └─ class SoftDeleteMixin(models.Model):          ❌ CLASE
│          """Abstract Model."""
│          class Meta:
│              abstract = True
│
└── request.py (4,775 bytes) ✅ CORRECTO: Solo funciones
    │
    └─ def get_client_ip(request):                   ✅ FUNCIÓN
           """Obtiene IP del cliente."""
           return ip

ANÁLISIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ models.py en utils → VIOLA REGLA (tiene clases)
❌ SoftDeleteQuerySet → CLASE, debe ir en core/
❌ SoftDeleteManager → CLASE, debe ir en core/
❌ SoftDeleteMixin → CLASE, debe ir en core/

✅ request.py → CORRECTO (solo funciones)
```

### 3.2 apps/core/ (INCOMPLETO)

```python
apps/core/
│
├── models.py (8,151 bytes) ✅ Tiene modelos concretos
│   ├─ class CallRecord(SoftDeleteMixin, models.Model):
│   ├─ class Center(SoftDeleteMixin, models.Model):
│   ├─ class Service(SoftDeleteMixin, models.Model):
│   └─ class UserServiceAccess(SoftDeleteMixin, models.Model):
│
├── mixins.py (2,238 bytes) ✅ Tiene mixins para ViewSets
├── permissions.py (1,993 bytes) ✅ Tiene permissions
├── services.py (6,248 bytes) ✅ Tiene services
│
└── ⚠️ FALTA: base_models.py o abstract_models.py
    Debería tener:
    - SoftDeleteQuerySet
    - SoftDeleteManager
    - SoftDeleteMixin
    - TimeStampedModel
    - AuditedModel

ANÁLISIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Tiene modelos concretos (correcto)
✅ Tiene clases de business logic (correcto)
⚠️ NO tiene las clases base que están en utils/
⚠️ Debería tener archivo para abstract models
```

---

<a name="problemas"></a>
## 4. PROBLEMAS IDENTIFICADOS

### 4.1 Violación del Principio

```
PROBLEMA PRINCIPAL (v2.0.0):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/utils/models.py EXISTE y contiene CLASES

Según Django:
❌ utils/ NO debe tener clases
❌ utils/ SOLO debe tener funciones
❌ django.utils NO tiene ningún archivo con clases

Realidad IACT:
apps/utils/models.py tiene 3 CLASES:
- SoftDeleteQuerySet (CLASE)
- SoftDeleteManager (CLASE)
- SoftDeleteMixin (CLASE)

ESTAS 3 CLASES DEBEN IR EN apps/core/
```

### 4.2 Comparación Incorrecta

```
❌ PENSAMIENTO INCORRECTO (v1.0.0):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Abstract Models → core/"
"Concrete Models → pueden estar en cualquier app"

Esto hace pensar:
- SoftDeleteMixin (abstract) → core/
- CallRecord (concrete) → puede estar donde sea

PERO NO ES CORRECTO porque:
- Ambos son CLASES
- La diferencia NO es abstract vs concrete
- La diferencia ES función vs clase


✅ PENSAMIENTO CORRECTO (v2.0.0):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"CLASES → core/"
"FUNCIONES → utils/"

Esto es claro:
- SoftDeleteMixin (CLASE) → core/
- CallRecord (CLASE) → core/ (o app de negocio)
- get_client_ip (FUNCIÓN) → utils/
- slugify (FUNCIÓN) → utils/
```

### 4.3 Impacto Actual

```python
# Uso actual (INCORRECTO):
from apps.utils.models import SoftDeleteMixin  # ❌ utils con clase

class Report(SoftDeleteMixin, models.Model):
    # ...
    pass

APPS QUE IMPORTAN DE utils.models:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ apps/reports/models.py
✅ apps/users/models.py
✅ apps/access/models.py
✅ apps/core/models.py
✅ Otras apps (~8-10 archivos)

IMPACTO DE CORREGIR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cambiar import en:
- ~8-10 archivos models.py
- Tests correspondientes
- Total: ~15-20 archivos

RIESGO: BAJO (solo cambio de import, funcionalidad idéntica)
```

---

<a name="recomendaciones"></a>
## 5. RECOMENDACIONES DE REFACTORIZACIÓN

### 5.1 Estructura Ideal

```
apps/utils/ (SOLO FUNCIONES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

├── request.py ✅
│   └── def get_client_ip(request):
│       def get_user_agent(request):
│
├── formatters.py ✅
│   └── def format_phone(phone):
│       def format_currency(amount):
│       def format_date_spanish(date):
│
├── validators_helpers.py ✅
│   └── def is_valid_phone(phone):
│       def is_valid_nit(nit):
│       def sanitize_input(text):
│
└── string_helpers.py ✅
    └── def slugify_spanish(text):
        def truncate_smart(text, length):

❌ NO models.py (ELIMINAR)
❌ NO CLASES


apps/core/ (CLASES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

├── models.py ✅
│   └── class CallRecord(SoftDeleteMixin, TimeStampedModel):
│       class Center(SoftDeleteMixin, TimeStampedModel):
│       class Service(SoftDeleteMixin, TimeStampedModel):
│
├── base_models.py ✅ NUEVO - Abstract Models
│   └── class TimeStampedModel(models.Model):
│           class Meta:
│               abstract = True
│
│       class SoftDeleteQuerySet(models.QuerySet):
│       class SoftDeleteManager(models.Manager):
│       class SoftDeleteMixin(models.Model):
│           class Meta:
│               abstract = True
│
│       class AuditedModel(models.Model):
│           class Meta:
│               abstract = True
│
├── exceptions.py ✅
│   └── class BusinessException(Exception):
│       class InsufficientFundsException(BusinessException):
│
├── validators.py ✅
│   └── class PhoneValidator:
│       class NITValidator:
│
├── middleware.py ✅
│   └── class RequestLoggingMiddleware:
│       class TenantMiddleware:
│
└── permissions.py ✅
    └── class RequiresFunction(permissions.BasePermission):
        class IsOwnerOrReadOnly(permissions.BasePermission):
```

### 5.2 Imports Correctos

```python
# ════════════════════════════════════════════════════════════
# ANTES (INCORRECTO)
# ════════════════════════════════════════════════════════════

# apps/reports/models.py
from apps.utils.models import SoftDeleteMixin  # ❌ utils con clase


# ════════════════════════════════════════════════════════════
# DESPUÉS (CORRECTO)
# ════════════════════════════════════════════════════════════

# apps/reports/models.py
from apps.core.base_models import SoftDeleteMixin  # ✅ core con clase
from apps.core.base_models import TimeStampedModel
from apps.utils.formatters import format_phone  # ✅ utils con función
from apps.utils.request import get_client_ip  # ✅ utils con función


# ════════════════════════════════════════════════════════════
# REGLA VISUAL
# ════════════════════════════════════════════════════════════

from apps.core.xxx import MiClase      # ✅ Importar CLASES de core
from apps.utils.xxx import mi_funcion  # ✅ Importar FUNCIONES de utils
```

### 5.3 Ejemplo Completo

```python
# ════════════════════════════════════════════════════════════
# apps/core/base_models.py - NUEVO
# ════════════════════════════════════════════════════════════

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo base con timestamps.
    
    Todos los modelos IACT heredan esto.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet con soft delete."""
    
    def delete(self):
        return self.update(
            is_deleted=True,
            deleted_at=timezone.now()
        )
    
    def alive(self):
        return self.filter(is_deleted=False)
    
    def deleted(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """Manager con soft delete."""
    
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            is_deleted=False
        )
    
    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteMixin(models.Model):
    """
    Mixin para soft delete.
    
    CNST-005: TODOS los modelos IACT DEBEN heredar esto.
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted'
    )
    
    objects = SoftDeleteManager()
    
    class Meta:
        abstract = True
    
    def soft_delete(self, deleted_by=None):
        """Soft delete del registro."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.save()
    
    def restore(self):
        """Restaura registro eliminado."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()


class AuditedModel(models.Model):
    """
    Modelo base con auditoría.
    
    Registra quién crea/modifica registros.
    """
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated'
    )
    
    class Meta:
        abstract = True


# ════════════════════════════════════════════════════════════
# apps/utils/request.py - EXISTENTE (CORRECTO)
# ════════════════════════════════════════════════════════════

def get_client_ip(request):
    """
    Obtiene IP del cliente.
    
    Considera headers de proxy/load balancer.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def get_user_agent(request):
    """Obtiene User-Agent del request."""
    return request.META.get('HTTP_USER_AGENT', '')


# ════════════════════════════════════════════════════════════
# apps/utils/formatters.py - NUEVO
# ════════════════════════════════════════════════════════════

def format_phone(phone):
    """
    Formatea número telefónico colombiano.
    
    Args:
        phone: Número sin formato (3001234567)
        
    Returns:
        Número formateado (300 123 4567)
    """
    if not phone:
        return ''
    
    phone = phone.strip().replace(' ', '').replace('-', '')
    
    if len(phone) == 10:
        return f"{phone[:3]} {phone[3:6]} {phone[6:]}"
    
    return phone


def format_currency(amount):
    """
    Formatea cantidad como moneda colombiana.
    
    Args:
        amount: Cantidad numérica
        
    Returns:
        String formateado ($1.234.567)
    """
    return f"${amount:,.0f}".replace(',', '.')
```

---

<a name="plan"></a>
## 6. PLAN DE MIGRACIÓN

### 6.1 Pasos Detallados

```
PASO 1: Crear apps/core/base_models.py
────────────────────────────────────────────────────────────

1. Crear archivo apps/core/base_models.py
2. Copiar contenido de apps/utils/models.py
3. Agregar TimeStampedModel, AuditedModel (nuevos)
4. Verificar imports (solo django.db, django.utils)

Archivos a crear:
- apps/core/base_models.py

Tiempo: 15 minutos


PASO 2: Actualizar imports en models.py
────────────────────────────────────────────────────────────

Buscar y reemplazar:

apps/reports/models.py:
- from apps.utils.models import SoftDeleteMixin
+ from apps.core.base_models import SoftDeleteMixin, TimeStampedModel

apps/users/models.py:
- from apps.utils.models import SoftDeleteMixin
+ from apps.core.base_models import SoftDeleteMixin, TimeStampedModel

apps/access/models.py:
- from apps.utils.models import SoftDeleteMixin
+ from apps.core.base_models import SoftDeleteMixin, TimeStampedModel

apps/core/models.py:
- from apps.utils import SoftDeleteMixin
+ from apps.core.base_models import SoftDeleteMixin, TimeStampedModel

... todos los demás

Comando para encontrar:
grep -r "from apps.utils.models import" apps/
grep -r "from apps.utils import SoftDeleteMixin" apps/

Archivos estimados: ~8-10
Tiempo: 20 minutos


PASO 3: Crear archivos de funciones en utils/
────────────────────────────────────────────────────────────

Crear archivos nuevos para organizar mejor:

apps/utils/formatters.py:
- def format_phone()
- def format_currency()
- def format_date_spanish()

apps/utils/validators_helpers.py:
- def is_valid_phone()
- def is_valid_nit()
- def sanitize_input()

Tiempo: 15 minutos


PASO 4: Actualizar imports en tests
────────────────────────────────────────────────────────────

tests/unit/utils/test_soft_delete.py:
- from apps.utils.models import SoftDeleteMixin
+ from apps.core.base_models import SoftDeleteMixin

tests/unit/reports/test_models.py:
- from apps.utils.models import SoftDeleteMixin
+ from apps.core.base_models import SoftDeleteMixin

Comando:
grep -r "from apps.utils.models" tests/

Tiempo: 15 minutos


PASO 5: Ejecutar tests
────────────────────────────────────────────────────────────

pytest tests/unit/ -v
pytest tests/integration/ -v

Verificar que todo pasa.

Tiempo: 10 minutos


PASO 6: Eliminar apps/utils/models.py
────────────────────────────────────────────────────────────

rm apps/utils/models.py

Verificar que no quede ninguna referencia:
grep -r "apps.utils.models" apps/
grep -r "apps.utils.models" tests/

Debería retornar vacío.

Tiempo: 5 minutos


PASO 7: Actualizar __init__.py si es necesario
────────────────────────────────────────────────────────────

apps/utils/__init__.py:
Remover exports de models si existen.

apps/core/__init__.py:
Agregar exports de base_models.

Tiempo: 5 minutos


TOTAL: ~1.5 horas
```

### 6.2 Script de Migración Automática

```bash
#!/bin/bash
# migrate_classes_to_core.sh
# Migra CLASES de utils/ a core/

echo "════════════════════════════════════════════════════════════"
echo "Migrando CLASES de utils/ a core/"
echo "════════════════════════════════════════════════════════════"
echo ""

# 1. Crear base_models.py en core
echo "1. Creando apps/core/base_models.py..."
cp apps/utils/models.py apps/core/base_models.py
echo "   ✓ Creado"
echo ""

# 2. Buscar y reemplazar imports en apps/
echo "2. Actualizando imports en apps/..."
find apps/ -name "*.py" -type f -exec sed -i \
  's/from apps\.utils\.models import/from apps.core.base_models import/g' {} +
find apps/ -name "*.py" -type f -exec sed -i \
  's/from apps\.utils import SoftDeleteMixin/from apps.core.base_models import SoftDeleteMixin/g' {} +
echo "   ✓ Actualizado"
echo ""

# 3. Buscar y reemplazar imports en tests/
echo "3. Actualizando imports en tests/..."
find tests/ -name "*.py" -type f -exec sed -i \
  's/from apps\.utils\.models import/from apps.core.base_models import/g' {} +
echo "   ✓ Actualizado"
echo ""

# 4. Verificar que no queden referencias
echo "4. Verificando que no queden referencias a utils.models..."
REFS_APPS=$(grep -r "apps.utils.models" apps/ 2>/dev/null | wc -l)
REFS_TESTS=$(grep -r "apps.utils.models" tests/ 2>/dev/null | wc -l)

if [ "$REFS_APPS" -eq 0 ] && [ "$REFS_TESTS" -eq 0 ]; then
    echo "   ✓ No quedan referencias"
else
    echo "   ⚠ Quedan referencias:"
    echo "     - En apps/: $REFS_APPS"
    echo "     - En tests/: $REFS_TESTS"
    echo ""
    echo "   Revisar manualmente:"
    grep -r "apps.utils.models" apps/ tests/ 2>/dev/null
    exit 1
fi
echo ""

# 5. Ejecutar tests
echo "5. Ejecutando tests..."
pytest tests/unit/ -v --tb=short

if [ $? -eq 0 ]; then
    echo "   ✓ Tests pasaron"
else
    echo "   ✗ Tests fallaron"
    echo "   No eliminar utils/models.py hasta resolver"
    exit 1
fi
echo ""

# 6. Eliminar utils/models.py (manual para seguridad)
echo "6. Para eliminar apps/utils/models.py ejecutar:"
echo "   rm apps/utils/models.py"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "Migración completada exitosamente"
echo "════════════════════════════════════════════════════════════"
```

### 6.3 Checklist de Verificación

```
ANTES DE EJECUTAR MIGRACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] Commit actual en git (punto de retorno)
[ ] Rama nueva (feature/refactor-utils-core)
[ ] Tests pasando antes de migración
[ ] Backup de apps/utils/models.py

DURANTE MIGRACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] Crear apps/core/base_models.py
[ ] Actualizar imports en apps/
[ ] Actualizar imports en tests/
[ ] Verificar no quedan referencias a utils.models

DESPUÉS DE MIGRACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] Tests unitarios pasan
[ ] Tests integración pasan
[ ] Aplicación corre sin errores
[ ] Eliminar apps/utils/models.py
[ ] Commit de cambios
[ ] PR para revisión
```

---

## 7. BENEFICIOS DE LA REFACTORIZACIÓN

### 7.1 Adherencia a Filosofía Django

```
ANTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ apps/utils/models.py existe (viola filosofía Django)
❌ utils/ con CLASES (incorrecto)
❌ Confusión: "¿Por qué models en utils?"
❌ No sigue patrón del framework

DESPUÉS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ apps/core/ con CLASES (correcto)
✅ apps/utils/ con FUNCIONES (correcto)
✅ Claridad total: función → utils, clase → core
✅ Sigue filosofía Django
```

### 7.2 Claridad para Desarrolladores

```
ANTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Developer nuevo:
"¿Por qué hay models.py en utils?"
"¿Dónde pongo mi Abstract Model?"
"¿utils o core?"

Confusión semántica.

DESPUÉS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Developer nuevo:
"¿Es una función? → utils/"
"¿Es una clase? → core/"

Regla simple y clara.
```

### 7.3 Mejor Organización

```
ANTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/utils/
├── models.py        ❌ Confuso
└── request.py       ✅ OK

apps/core/
├── models.py        ✅ OK
└── (sin base models) ⚠️ Incompleto


DESPUÉS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/utils/
├── request.py       ✅ Funciones
├── formatters.py    ✅ Funciones
└── validators.py    ✅ Funciones

apps/core/
├── models.py        ✅ Modelos concretos
├── base_models.py   ✅ Modelos abstractos
├── exceptions.py    ✅ Excepciones
├── middleware.py    ✅ Middleware
└── validators.py    ✅ Validadores (clases)
```

---

## 8. ESTADO FINAL DESEADO

```
apps/utils/ (SOLO FUNCIONES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Caja de herramientas técnicas
Contiene: Pure functions y helpers stateless

✅ request.py → get_client_ip(), get_user_agent()
✅ formatters.py → format_phone(), format_currency()
✅ validators_helpers.py → is_valid_phone(), sanitize_input()
✅ string_helpers.py → slugify_spanish(), truncate_smart()

❌ NO models.py (eliminado)
❌ NO clases


apps/core/ (SOLO CLASES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Motor de la aplicación
Contiene: Clases base y componentes fundamentales

✅ models.py → CallRecord, Center, Service (concretos)
✅ base_models.py → SoftDeleteMixin, TimeStampedModel (abstractos)
✅ exceptions.py → BusinessException, etc
✅ validators.py → PhoneValidator, NITValidator (clases)
✅ middleware.py → RequestLoggingMiddleware
✅ permissions.py → RequiresFunction, IsOwnerOrReadOnly
✅ services.py → ServiceAccessService
✅ mixins.py → ServiceFilterMixin

❌ NO funciones (van en utils)
```

---

## RESUMEN Y DECISIÓN FINAL

```
PROBLEMA (v2.0.0):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ apps/utils/models.py contiene CLASES
⚠️ Viola filosofía Django: utils = funciones, core = clases
⚠️ Confusión para desarrolladores

SOLUCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Crear apps/core/base_models.py
2. Mover SoftDeleteMixin, Manager, QuerySet
3. Agregar TimeStampedModel, AuditedModel
4. Actualizar imports en todas las apps
5. Eliminar apps/utils/models.py
6. Crear utils/formatters.py, utils/validators_helpers.py

TIEMPO ESTIMADO: 1.5 horas
RIESGO: BAJO (solo cambios de import)
BENEFICIO: Adherencia total a filosofía Django ✅

REGLA SIMPLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¿Es una FUNCIÓN? → apps/utils/
¿Es una CLASE?    → apps/core/

¡ASÍ DE SIMPLE!

DECISIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] PROCEDER - Ejecutar refactorización
[ ] POSPONER - Registrar como deuda técnica
[ ] DISCUTIR - Revisar con equipo

Recomendación: PROCEDER (1.5 horas bien invertidas)
```

---

**FIN DEL ANÁLISIS - CORE vs UTILS v2.0.0**

Documento actualizado: 2026-01-18  
Cambios desde v1.0.0: Enfatiza función vs clase como diferencia fundamental  
Estado actual: apps/utils/models.py con clases (incorrecto)  
Solución: Mover todas las clases a apps/core/base_models.py  
Tiempo estimado: 1.5 horas  
Regla simple: FUNCIÓN → utils/, CLASE → core/
