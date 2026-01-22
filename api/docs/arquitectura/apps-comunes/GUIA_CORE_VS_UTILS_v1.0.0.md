---
version: 1.0.0
date: 2026-01-18
project: IACT Call Center System
type: Guía Práctica - Apps Compartidas
categoria: arquitectura/apps-comunes
tema: Guía Práctica CORE vs UTILS - Referencia Rápida
autor: Claude Technical Analysis
tags: [core, utils, guia, referencia-rapida, best-practices]
relacionado:
  - ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v2.0.0.md
estado: completado
---

# GUÍA PRÁCTICA: CORE vs UTILS

**Referencia rápida para desarrolladores - 5 minutos**

---

## ⚡ REGLA DE ORO

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ¿Qué estoy escribiendo?                              │
│                                                         │
│   def mi_funcion():     →  apps/utils/                 │
│   class MiClase:        →  apps/core/                  │
│                                                         │
│   ¡ASÍ DE SIMPLE!                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 CHECKLIST DE DECISIÓN (30 SEGUNDOS)

```
1. ¿Es una función (def)?
   └─ SÍ → apps/utils/
   └─ NO → Ir a 2

2. ¿Es una clase (class)?
   └─ SÍ → apps/core/
   └─ NO → ¿Qué es? 🤔

3. ¿Importa desde django.db.models?
   └─ SÍ → apps/core/ (modelo/mixin/manager)
   └─ NO → Ir a 4

4. ¿Tiene estado (self.xxx)?
   └─ SÍ → apps/core/ (clase)
   └─ NO → apps/utils/ (función)
```

---

## ✅ vs ❌ EJEMPLOS VISUALES

### Ejemplo 1: Abstract Model

```python
# ❌ INCORRECTO
# apps/utils/models.py
class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    class Meta:
        abstract = True

# ✅ CORRECTO
# apps/core/base_models.py
class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    class Meta:
        abstract = True
```

**Por qué:** Es una **CLASE** → core/

---

### Ejemplo 2: Helper de Request

```python
# ❌ INCORRECTO
# apps/core/request_helpers.py
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

# ✅ CORRECTO
# apps/utils/request.py
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
```

**Por qué:** Es una **FUNCIÓN** → utils/

---

### Ejemplo 3: Validador

```python
# ❌ INCORRECTO
# apps/utils/validators.py
class PhoneValidator:
    def __call__(self, value):
        if not value.isdigit():
            raise ValidationError('Teléfono inválido')

# ✅ CORRECTO
# apps/core/validators.py
class PhoneValidator:
    def __call__(self, value):
        if not value.isdigit():
            raise ValidationError('Teléfono inválido')
```

**Por qué:** Es una **CLASE** → core/

---

### Ejemplo 4: Helper de Formato

```python
# ❌ INCORRECTO
# apps/core/formatters.py
def format_phone(phone):
    return f"{phone[:3]} {phone[3:6]} {phone[6:]}"

# ✅ CORRECTO
# apps/utils/formatters.py
def format_phone(phone):
    return f"{phone[:3]} {phone[3:6]} {phone[6:]}"
```

**Por qué:** Es una **FUNCIÓN** → utils/

---

### Ejemplo 5: Manager Personalizado

```python
# ❌ INCORRECTO
# apps/utils/managers.py
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

# ✅ CORRECTO
# apps/core/base_models.py
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
```

**Por qué:** Es una **CLASE** → core/

---

### Ejemplo 6: Exception Personalizada

```python
# ❌ INCORRECTO
# apps/utils/exceptions.py
class BusinessException(Exception):
    pass

# ✅ CORRECTO
# apps/core/exceptions.py
class BusinessException(Exception):
    pass
```

**Por qué:** Es una **CLASE** → core/

---

## 📁 apps/core/ - QUÉ VA AQUÍ

### Contenido de apps/core/

```
apps/core/
│
├── models.py                    ✅ Modelos concretos de negocio
│   └── class CallRecord(models.Model)
│       class Center(models.Model)
│       class Service(models.Model)
│
├── base_models.py               ✅ Modelos abstractos
│   └── class TimeStampedModel(models.Model)
│       class SoftDeleteMixin(models.Model)
│       class AuditedModel(models.Model)
│       class SoftDeleteManager(models.Manager)
│       class SoftDeleteQuerySet(models.QuerySet)
│
├── exceptions.py                ✅ Excepciones del sistema
│   └── class BusinessException(Exception)
│       class InsufficientFundsException(BusinessException)
│       class ETLNotExecutedException(Exception)
│
├── validators.py                ✅ Validadores (clases)
│   └── class PhoneValidator
│       class NITValidator
│       class EmailValidator
│
├── middleware.py                ✅ Middleware (clases)
│   └── class RequestLoggingMiddleware
│       class TenantMiddleware
│       class AccessAuditMiddleware
│
├── permissions.py               ✅ Permissions DRF (clases)
│   └── class RequiresFunction(permissions.BasePermission)
│       class IsOwnerOrReadOnly(permissions.BasePermission)
│
├── mixins.py                    ✅ Mixins para Views/Serializers
│   └── class ServiceFilterMixin
│       class SoftDeleteViewSetMixin
│
├── services.py                  ✅ Services (clases)
│   └── class ServiceAccessService
│       class ReportService
│       class DashboardService
│
└── serializers.py               ✅ Serializers (clases)
    └── class ReportSerializer
```

### Reglas para apps/core/

```
✅ SIEMPRE va en core/:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. class ... (models.Model)          → Cualquier modelo
2. class ... (models.Manager)        → Cualquier manager
3. class ... (models.QuerySet)       → Cualquier queryset
4. class ... (Exception)             → Cualquier excepción
5. class ... (BasePermission)        → Cualquier permission
6. class ... Middleware              → Cualquier middleware
7. class ... Service                 → Cualquier service
8. class ... Serializer              → Cualquier serializer
9. class ... Mixin                   → Cualquier mixin para views
10. class ... Validator              → Cualquier validador

PATRÓN:
Si empieza con "class" → core/
```

---

## 📁 apps/utils/ - QUÉ VA AQUÍ

### Contenido de apps/utils/

```
apps/utils/
│
├── request.py                   ✅ Helpers de request
│   └── def get_client_ip(request)
│       def get_user_agent(request)
│       def parse_query_params(request)
│
├── formatters.py                ✅ Formateo de datos
│   └── def format_phone(phone)
│       def format_currency(amount)
│       def format_date_spanish(date)
│
├── validators_helpers.py        ✅ Helpers de validación
│   └── def is_valid_phone(phone)
│       def is_valid_nit(nit)
│       def sanitize_input(text)
│
├── string_helpers.py            ✅ Manipulación de strings
│   └── def slugify_spanish(text)
│       def truncate_smart(text, length)
│       def capitalize_each_word(text)
│
├── datetime_helpers.py          ✅ Helpers de fecha/hora
│   └── def parse_spanish_date(text)
│       def format_time_ago(datetime)
│       def get_quarter_from_date(date)
│
└── calculations.py              ✅ Cálculos genéricos
    └── def calculate_percentage(part, total)
        def round_currency(amount)
        def calculate_growth_rate(old, new)
```

### Reglas para apps/utils/

```
✅ SIEMPRE va en utils/:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. def nombre()                      → Cualquier función
2. Sin estado (stateless)            → Pure functions
3. No importa de django.db.models    → No usa ORM
4. Reutilizable en cualquier app     → Genérico

PATRÓN:
Si empieza con "def" → utils/

❌ NUNCA va en utils/:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. class ...                         → Va en core/
2. Cualquier cosa con estado         → Va en core/
3. models.py                         → NO debe existir
```

---

## 🎯 CASOS COMUNES

### Caso 1: Necesito soft delete

```python
# ✅ CORRECTO
# apps/core/base_models.py
class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

# Uso:
from apps.core.base_models import SoftDeleteMixin

class Report(SoftDeleteMixin, models.Model):
    # ...
    pass
```

**Por qué core/:** Es una CLASE (Mixin)

---

### Caso 2: Necesito obtener IP del cliente

```python
# ✅ CORRECTO
# apps/utils/request.py
def get_client_ip(request):
    """Obtiene IP del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

# Uso:
from apps.utils.request import get_client_ip

def my_view(request):
    ip = get_client_ip(request)
    # ...
```

**Por qué utils/:** Es una FUNCIÓN

---

### Caso 3: Necesito validar teléfono

```python
# OPCIÓN A: Validación simple (función) → utils/
# apps/utils/validators_helpers.py
def is_valid_phone(phone):
    """Verifica si teléfono es válido."""
    return len(phone) == 10 and phone.isdigit()

# Uso:
from apps.utils.validators_helpers import is_valid_phone
if is_valid_phone(phone):
    # ...


# OPCIÓN B: Validador Django (clase) → core/
# apps/core/validators.py
class PhoneValidator:
    """Validador de teléfono para Django."""
    
    def __call__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValidationError('Teléfono inválido')

# Uso:
from apps.core.validators import PhoneValidator

class User(models.Model):
    phone = models.CharField(
        validators=[PhoneValidator()]
    )
```

**Por qué:**
- Función helper → utils/
- Clase validador → core/

---

### Caso 4: Necesito formatear moneda

```python
# ✅ CORRECTO
# apps/utils/formatters.py
def format_currency(amount):
    """Formatea cantidad como moneda colombiana."""
    return f"${amount:,.0f}".replace(',', '.')

# Uso:
from apps.utils.formatters import format_currency

total = format_currency(1234567)  # "$1.234.567"
```

**Por qué utils/:** Es una FUNCIÓN

---

### Caso 5: Necesito timestamps en todos los modelos

```python
# ✅ CORRECTO
# apps/core/base_models.py
class TimeStampedModel(models.Model):
    """Modelo base con timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

# Uso:
from apps.core.base_models import TimeStampedModel

class Report(TimeStampedModel):
    # Automáticamente tiene created_at y updated_at
    name = models.CharField(max_length=200)
```

**Por qué core/:** Es una CLASE (Abstract Model)

---

### Caso 6: Necesito custom exception

```python
# ✅ CORRECTO
# apps/core/exceptions.py
class BusinessException(Exception):
    """Excepción base de negocio."""
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class ExportLimitExceeded(BusinessException):
    """Se excedió límite de exportación."""
    pass

# Uso:
from apps.core.exceptions import ExportLimitExceeded

if count > 100000:
    raise ExportLimitExceeded("Máximo 100,000 registros")
```

**Por qué core/:** Es una CLASE (Exception)

---

## 🤔 FAQ

### P: ¿Puede utils/ tener un archivo models.py?

```
R: ❌ NO

utils/ NO debe tener models.py porque models.py
contiene CLASES, y utils/ solo debe tener FUNCIONES.

Si tienes models.py en utils/, es un error.
```

---

### P: ¿Dónde van los Abstract Models?

```
R: apps/core/base_models.py

Razón: Son CLASES, aunque sean abstract.
La diferencia NO es abstract vs concrete.
La diferencia ES función vs clase.
```

---

### P: ¿Dónde van los Managers personalizados?

```
R: apps/core/base_models.py (junto con los mixins)

Razón: class SoftDeleteManager(models.Manager) → CLASE
```

---

### P: ¿Dónde van los QuerySets personalizados?

```
R: apps/core/base_models.py (junto con managers)

Razón: class SoftDeleteQuerySet(models.QuerySet) → CLASE
```

---

### P: ¿Dónde van las funciones de validación simples?

```
R: apps/utils/validators_helpers.py

Razón: def is_valid_phone() → FUNCIÓN

Pero si es un validador Django (clase):
apps/core/validators.py

Razón: class PhoneValidator → CLASE
```

---

### P: ¿Puede core/ tener funciones?

```
R: ⚠️ Técnicamente sí, pero NO es recomendado

core/ debe ser principalmente CLASES.
Si tienes una función, probablemente va en utils/.

Excepción:
Si la función está dentro de una clase (método),
entonces sí está bien.
```

---

### P: ¿Qué pasa si tengo un archivo con funciones Y clases?

```
R: Dividir en dos archivos

Ejemplo:
validators.py con clases Y funciones

Dividir en:
- core/validators.py → CLASES
- utils/validators_helpers.py → FUNCIONES
```

---

### P: ¿Los Mixins para ViewSets van en core/ o utils/?

```
R: apps/core/mixins.py

Razón: class ServiceFilterMixin → CLASE

Aunque sean "mixins", siguen siendo CLASES.
```

---

### P: ¿Las Permissions de DRF van en core/ o utils/?

```
R: apps/core/permissions.py

Razón: class RequiresFunction(permissions.BasePermission) → CLASE
```

---

### P: ¿El Middleware va en core/ o utils/?

```
R: apps/core/middleware.py

Razón: class AccessAuditMiddleware → CLASE
```

---

## 📊 REFERENCIA RÁPIDA

```
┌───────────────────────────────────────────────────────────────────┐
│                     REFERENCIA RÁPIDA                             │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  TIPO                           UBICACIÓN         ARCHIVO         │
│  ────────────────────────────   ─────────────────────────────────│
│                                                                   │
│  def mi_funcion()               apps/utils/       *.py           │
│  class MiModelo                 apps/core/        base_models.py │
│  class MiManager                apps/core/        base_models.py │
│  class MiQuerySet               apps/core/        base_models.py │
│  class MiException              apps/core/        exceptions.py  │
│  class MiValidator              apps/core/        validators.py  │
│  class MiMiddleware             apps/core/        middleware.py  │
│  class MiPermission             apps/core/        permissions.py │
│  class MiMixin (ViewSet)        apps/core/        mixins.py      │
│  class MiService                apps/core/        services.py    │
│  class MiSerializer             apps/core/        serializers.py │
│                                                                   │
│  Helpers de request             apps/utils/       request.py     │
│  Formateo de datos              apps/utils/       formatters.py  │
│  Validación simple              apps/utils/       validators_    │
│                                                   helpers.py     │
│  String helpers                 apps/utils/       string_        │
│                                                   helpers.py     │
│  Date/time helpers              apps/utils/       datetime_      │
│                                                   helpers.py     │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🎬 EJEMPLOS DE IMPORTS

### ✅ Imports Correctos

```python
# En models.py de cualquier app:
from apps.core.base_models import SoftDeleteMixin, TimeStampedModel
from apps.utils.formatters import format_phone, format_currency

class Report(SoftDeleteMixin, TimeStampedModel):
    phone = models.CharField(max_length=20)
    
    def formatted_phone(self):
        return format_phone(self.phone)


# En views.py:
from apps.core.permissions import RequiresFunction
from apps.utils.request import get_client_ip

class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [RequiresFunction]
    
    def create(self, request):
        ip = get_client_ip(request)
        # ...


# En services.py:
from apps.core.exceptions import ExportLimitExceeded
from apps.utils.calculations import calculate_percentage

class ReportService:
    @staticmethod
    def export(queryset):
        count = queryset.count()
        if count > 100000:
            raise ExportLimitExceeded()
        
        progress = calculate_percentage(current, total)
        # ...
```

---

## 🚫 ANTI-PATTERNS COMUNES

### ❌ Anti-pattern 1: Clase en utils/

```python
# ❌ INCORRECTO
# apps/utils/models.py
class SoftDeleteMixin(models.Model):
    # ...

# ✅ CORRECTO
# apps/core/base_models.py
class SoftDeleteMixin(models.Model):
    # ...
```

---

### ❌ Anti-pattern 2: Función en core/ (sin ser método)

```python
# ❌ INCORRECTO
# apps/core/formatters.py
def format_phone(phone):
    # ...

# ✅ CORRECTO
# apps/utils/formatters.py
def format_phone(phone):
    # ...
```

---

### ❌ Anti-pattern 3: models.py en utils/

```python
# ❌ INCORRECTO
apps/utils/
└── models.py  # ← NO debe existir

# ✅ CORRECTO
apps/utils/
├── request.py
├── formatters.py
└── validators_helpers.py
```

---

### ❌ Anti-pattern 4: Import incorrecto

```python
# ❌ INCORRECTO
from apps.utils.models import SoftDeleteMixin

# ✅ CORRECTO
from apps.core.base_models import SoftDeleteMixin
```

---

## 📝 CHECKLIST DE REVISIÓN

```
Al crear un nuevo archivo, verifica:

[ ] ¿El archivo está en la ubicación correcta?
    - ¿Tiene clases? → core/
    - ¿Tiene funciones? → utils/

[ ] ¿El nombre del archivo es descriptivo?
    - base_models.py (no models_base.py)
    - formatters.py (no format_utils.py)

[ ] ¿Los imports son correctos?
    - from apps.core.xxx import MiClase
    - from apps.utils.xxx import mi_funcion

[ ] ¿No hay duplicación con archivos existentes?
    - Verificar que no exista utils/models.py
    - Verificar imports en otras apps

[ ] ¿El código sigue la filosofía Django?
    - core/ = motor (clases)
    - utils/ = herramientas (funciones)
```

---

## 🎯 RESUMEN EJECUTIVO

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              LA REGLA MÁS IMPORTANTE                    │
│                                                         │
│   class ...  →  apps/core/                             │
│   def ...    →  apps/utils/                            │
│                                                         │
│   ¡No hay excepción a esta regla!                      │
│                                                         │
└─────────────────────────────────────────────────────────┘

PATRÓN DJANGO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

django/core/  → Componentes del framework (clases)
django/utils/ → Herramientas técnicas (funciones)

PATRÓN IACT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/  → Componentes del sistema (clases)
apps/utils/ → Herramientas técnicas (funciones)

MIGRACIÓN PENDIENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ apps/utils/models.py → MOVER a apps/core/base_models.py
⚠️ Actualizar imports en todas las apps
⚠️ Eliminar apps/utils/models.py

Ver: ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v2.0.0.md
```

---

**FIN DE LA GUÍA PRÁCTICA**

Tiempo de lectura: 5 minutos  
Tiempo de consulta: 30 segundos (usa el checklist)  
Documento complementario: ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v2.0.0.md
