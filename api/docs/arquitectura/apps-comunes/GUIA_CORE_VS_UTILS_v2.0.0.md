---
version: 2.0.0
date: 2026-01-18
project: IACT Call Center System
type: Guía Práctica - Apps Compartidas
categoria: arquitectura/apps-comunes
tema: Guía Práctica CORE vs UTILS - Referencia Rápida
autor: Claude Technical Analysis
tags: [core, utils, guia, referencia-rapida, best-practices, abstract-only]
relacionado:
  - ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v3.0.0.md
estado: completado
replaces: GUIA_CORE_VS_UTILS_v1.0.0.md
changelog: |
  v2.0.0 (2026-01-18):
  - CORRECCIÓN CRÍTICA: apps/core/models.py SOLO abstract=True
  - Modelos concretos van en apps de negocio (analytics, centers, etc)
  - Actualiza todos los ejemplos con abstract=True obligatorio
  - Agrega sección "CRÍTICO: core/ SOLO Abstractos"
  v1.0.0 (2026-01-18):
  - Versión inicial
---

# GUÍA PRÁCTICA: CORE vs UTILS v2.0.0

**Referencia rápida para desarrolladores - 5 minutos**

---

## 🚨 CORRECCIÓN CRÍTICA v2.0.0

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ERROR EN v1.0.0:                                     │
│   "apps/core/models.py puede tener concretos"         │
│                                                         │
│   CORRECCIÓN v2.0.0:                                   │
│   apps/core/models.py SOLO puede tener:                │
│                                                         │
│   class MiModelo(models.Model):                        │
│       class Meta:                                       │
│           abstract = True  ← OBLIGATORIO               │
│                                                         │
│   CallRecord, Center en core/ → ERROR                  │
│   Deben ir en apps de negocio                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ⚡ REGLA DE ORO

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ¿Qué estoy escribiendo?                              │
│                                                         │
│   def mi_funcion():              →  apps/utils/        │
│                                                         │
│   class MiModelo(models.Model):  →  ¿Es abstracto?     │
│       class Meta:                                       │
│           abstract = True        →  apps/core/         │
│                                                         │
│   class MiModelo(models.Model):  →  ¿Es concreto?      │
│       class Meta:                                       │
│           db_table = 'tabla'     →  apps/negocio/      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 CHECKLIST DE DECISIÓN (30 SEGUNDOS)

```
1. ¿Es una función (def)?
   └─ SÍ → apps/utils/
   └─ NO → Ir a 2

2. ¿Es una clase de modelo (models.Model)?
   └─ SÍ → Ir a 3
   └─ NO → Ir a 5

3. ¿Tiene abstract=True?
   └─ SÍ → apps/core/models.py
   └─ NO → Ir a 4

4. ¿Crea tabla en DB (db_table)?
   └─ SÍ → apps/{negocio}/models.py
   └─ NO → ERROR (debe tener abstract=True)

5. ¿Es otra clase (Exception, Validator, etc)?
   └─ SÍ → apps/core/{exceptions,validators,etc}.py
```

---

## 🎯 CRÍTICO: apps/core/models.py SOLO ABSTRACTOS

### Regla Absoluta

```python
# ✅ CORRECTO - apps/core/models.py
class TimeStampedModel(models.Model):
    """Modelo base con timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # ← OBLIGATORIO


class SoftDeleteMixin(models.Model):
    """Modelo base con soft delete."""
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        abstract = True  # ← OBLIGATORIO


# ❌ INCORRECTO - apps/core/models.py
class CallRecord(models.Model):
    """❌ NO debe estar en core/"""
    fecha = models.DateField()
    
    class Meta:
        db_table = 'core_call_records'  # ← Crea tabla
        # ❌ NO tiene abstract=True
```

**Por qué:**
- core/ = Base classes (abstractas)
- Modelos concretos = Lógica de negocio
- Lógica de negocio → apps de negocio

---

## ✅ vs ❌ EJEMPLOS VISUALES

### Ejemplo 1: Soft Delete Mixin

```python
# ❌ INCORRECTO (v1.0.0)
# apps/utils/models.py
class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    class Meta:
        abstract = True

# ❌ TAMBIÉN INCORRECTO
# apps/core/models.py
class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    # ❌ Falta abstract=True


# ✅ CORRECTO (v2.0.0)
# apps/core/models.py
class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    class Meta:
        abstract = True  # ← OBLIGATORIO
```

**Por qué core/:**
1. Es una CLASE (no va en utils/)
2. Tiene abstract=True (va en core/)

---

### Ejemplo 2: Modelo de Negocio (CallRecord)

```python
# ❌ INCORRECTO (ESTADO ACTUAL)
# apps/core/models.py
class CallRecord(SoftDeleteMixin, models.Model):
    """❌ Modelo CONCRETO en core/"""
    fecha = models.DateField()
    telefono = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'core_call_records'  # ❌ Crea tabla
        # ❌ NO tiene abstract=True


# ✅ CORRECTO (v2.0.0)
# apps/analytics/models.py
from apps.core.models import SoftDeleteMixin, TimeStampedModel

class CallRecord(SoftDeleteMixin, TimeStampedModel):
    """✅ Modelo CONCRETO en app de negocio"""
    fecha = models.DateField()
    telefono = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'analytics_call_records'  # ✅ Tabla real
        # ✅ NO tiene abstract (es concreto)
```

**Por qué analytics/:**
1. Es CONCRETO (crea tabla en DB)
2. Es lógica de negocio (analytics de llamadas)
3. core/ SOLO para abstractos

---

### Ejemplo 3: Timestamps Base

```python
# ❌ INCORRECTO
# apps/utils/timestamps.py
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True


# ✅ CORRECTO
# apps/core/models.py
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # ← OBLIGATORIO
```

**Por qué core/:**
1. Es una CLASE (no va en utils/)
2. Tiene abstract=True (va en core/)

---

### Ejemplo 4: Helper de Formato (función)

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

**Por qué utils/:**
1. Es una FUNCIÓN
2. utils/ = solo funciones

---

## 📁 apps/core/ - QUÉ VA AQUÍ

### Contenido de apps/core/

```
apps/core/
│
├── models.py                    ✅ SOLO modelos con abstract=True
│   └── class TimeStampedModel(models.Model)
│           class Meta: abstract = True
│       class SoftDeleteMixin(models.Model)
│           class Meta: abstract = True
│       class AuditedModel(models.Model)
│           class Meta: abstract = True
│       class SoftDeleteManager(models.Manager)
│       class SoftDeleteQuerySet(models.QuerySet)
│
├── exceptions.py                ✅ Excepciones del sistema
│   └── class BusinessException(Exception)
│       class ExportLimitExceeded(BusinessException)
│
├── validators.py                ✅ Validadores (clases)
│   └── class PhoneValidator
│       class NITValidator
│
├── middleware.py                ✅ Middleware (clases)
│   └── class RequestLoggingMiddleware
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
└── services.py                  ✅ Services base (si aplica)
    └── class BaseService
```

### CRÍTICO: apps/core/models.py

```python
# apps/core/models.py - PLANTILLA

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # ← OBLIGATORIO


class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    
    class Meta:
        abstract = True  # ← OBLIGATORIO


class AuditedModel(models.Model):
    created_by = models.ForeignKey(...)
    updated_by = models.ForeignKey(...)
    
    class Meta:
        abstract = True  # ← OBLIGATORIO


# ❌ NUNCA ESTO:
class MiModelo(models.Model):
    campo = models.CharField(...)
    
    class Meta:
        db_table = 'tabla'  # ← PROHIBIDO en core/
```

---

## 📁 apps/{negocio}/ - MODELOS CONCRETOS

### apps/analytics/models.py

```python
from apps.core.models import SoftDeleteMixin, TimeStampedModel


class CallRecord(SoftDeleteMixin, TimeStampedModel):
    """
    Registro de llamadas agregado.
    
    ✅ CONCRETO - va en app de negocio
    ✅ Hereda de core/ abstractos
    ✅ Crea tabla en DB
    """
    fecha = models.DateField()
    telefono = models.CharField(max_length=20)
    servicio_800 = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'analytics_call_records'  # ✅ Tabla real
        ordering = ['-fecha']
        # ✅ NO tiene abstract=True
```

### apps/centers/models.py

```python
from apps.core.models import SoftDeleteMixin, TimeStampedModel


class Center(SoftDeleteMixin, TimeStampedModel):
    """Centro de atención."""
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=20, unique=True)
    
    class Meta:
        db_table = 'centers'  # ✅ Tabla real


class Service(SoftDeleteMixin, TimeStampedModel):
    """Servicio 800."""
    numero_800 = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    center = models.ForeignKey(Center, on_delete=models.PROTECT)
    
    class Meta:
        db_table = 'services'  # ✅ Tabla real
```

---

## 📁 apps/utils/ - QUÉ VA AQUÍ

```
apps/utils/
│
├── request.py                   ✅ Helpers de request (funciones)
│   └── def get_client_ip(request)
│       def get_user_agent(request)
│
├── formatters.py                ✅ Formateo de datos (funciones)
│   └── def format_phone(phone)
│       def format_currency(amount)
│
├── validators_helpers.py        ✅ Helpers de validación (funciones)
│   └── def is_valid_phone(phone)
│       def is_valid_nit(nit)
│
└── string_helpers.py            ✅ Manipulación strings (funciones)
    └── def slugify_spanish(text)
        def truncate_smart(text, length)


❌ NO models.py - PROHIBIDO
❌ NO CLASES
```

---

## 🤔 FAQ

### P: ¿Puede core/models.py tener modelos concretos?

```
R: ❌ NO

core/models.py SOLO puede tener:
✅ Modelos con abstract=True
✅ Managers (para abstractos)
✅ QuerySets (para abstractos)

❌ NUNCA modelos concretos
❌ NUNCA db_table (indica concreto)
```

---

### P: ¿Dónde van CallRecord, Center, Service actualmente en core/?

```
R: DEBEN MOVERSE a apps de negocio

Estado actual (INCORRECTO):
apps/core/models.py
├── CallRecord        ❌ Concreto en core/
├── Center            ❌ Concreto en core/
└── Service           ❌ Concreto en core/

Estado correcto:
apps/analytics/models.py
└── CallRecord        ✅ Concreto en app negocio

apps/centers/models.py
├── Center            ✅ Concreto en app negocio
└── Service           ✅ Concreto en app negocio
```

---

### P: ¿Cómo sé si mi modelo debe ir en core/?

```
R: Checklist de 3 preguntas:

1. ¿Tiene abstract=True?
   └─ NO → NO va en core/

2. ¿Otros modelos heredan de este?
   └─ NO → NO va en core/

3. ¿Crea tabla en DB (db_table)?
   └─ SÍ → NO va en core/

SOLO va en core/ si:
✅ Tiene abstract=True
✅ Es base class
✅ NO crea tabla
```

---

### P: ¿Puede utils/ tener models.py?

```
R: ❌ NO

utils/ NO debe tener models.py porque:
1. models.py contiene CLASES
2. utils/ solo debe tener FUNCIONES
3. Las clases de models van en core/ (si abstract) o apps de negocio (si concretos)
```

---

### P: ¿Dónde va SoftDeleteMixin?

```
R: apps/core/models.py

Estado actual (INCORRECTO):
apps/utils/models.py
└── SoftDeleteMixin   ❌ Clase en utils/

Estado correcto:
apps/core/models.py
└── SoftDeleteMixin   ✅ Clase abstracta en core/
    class Meta:
        abstract = True
```

---

### P: Si mi modelo hereda de SoftDeleteMixin, ¿va en core/?

```
R: ❌ NO necesariamente

Depende de si ES abstracto:

✅ SÍ va en core/:
class MiBaseModel(SoftDeleteMixin):
    class Meta:
        abstract = True  ← Tiene abstract

❌ NO va en core/:
class MiModelo(SoftDeleteMixin):
    class Meta:
        db_table = 'tabla'  ← Es concreto
        
Va en: apps/negocio/models.py
```

---

## 📊 REFERENCIA RÁPIDA

```
┌───────────────────────────────────────────────────────────────┐
│                     REFERENCIA RÁPIDA                         │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  TIPO                        UBICACIÓN         ABSTRACT?      │
│  ─────────────────────────   ──────────────────────────────  │
│                                                               │
│  def mi_funcion()            apps/utils/       N/A           │
│                                                               │
│  class MiModelo:                                              │
│    Meta: abstract=True       apps/core/        ✅ SÍ         │
│                                                               │
│  class MiModelo:                                              │
│    Meta: db_table='...'      apps/negocio/     ❌ NO         │
│                                                               │
│  class MiManager             apps/core/        N/A           │
│  class MiQuerySet            apps/core/        N/A           │
│  class MiException           apps/core/        N/A           │
│  class MiValidator           apps/core/        N/A           │
│  class MiMiddleware          apps/core/        N/A           │
│  class MiPermission          apps/core/        N/A           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 🎯 CASOS COMUNES IACT

### Caso 1: Crear modelo de reportes

```python
# ✅ CORRECTO
# apps/reports/models.py
from apps.core.models import SoftDeleteMixin, TimeStampedModel

class Report(SoftDeleteMixin, TimeStampedModel):
    """Reporte generado."""
    name = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'reports'  # ✅ Concreto, va en app negocio


# ❌ INCORRECTO
# apps/core/models.py
class Report(SoftDeleteMixin, TimeStampedModel):
    """❌ NO va en core/ (es concreto)"""
    name = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'reports'  # ❌ Crea tabla
```

---

### Caso 2: Crear base model para auditoría

```python
# ✅ CORRECTO
# apps/core/models.py
class AuditedModel(models.Model):
    """Base para modelos con auditoría."""
    created_by = models.ForeignKey('users.User', ...)
    updated_by = models.ForeignKey('users.User', ...)
    
    class Meta:
        abstract = True  # ✅ Abstract, va en core/


# Uso en app de negocio:
# apps/reports/models.py
from apps.core.models import AuditedModel

class Report(AuditedModel):
    name = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'reports'  # ✅ Concreto
```

---

### Caso 3: Agregar timestamps a todos los modelos

```python
# ✅ CORRECTO
# apps/core/models.py
class TimeStampedModel(models.Model):
    """Base con timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # ✅ OBLIGATORIO
```

---

## 🚫 ANTI-PATTERNS COMUNES

### ❌ Anti-pattern 1: Concreto en core/

```python
# ❌ INCORRECTO
# apps/core/models.py
class CallRecord(models.Model):
    fecha = models.DateField()
    
    class Meta:
        db_table = 'core_call_records'  # ❌ Crea tabla

# ✅ CORRECTO
# apps/analytics/models.py
class CallRecord(SoftDeleteMixin, TimeStampedModel):
    fecha = models.DateField()
    
    class Meta:
        db_table = 'analytics_call_records'
```

---

### ❌ Anti-pattern 2: Clase en utils/

```python
# ❌ INCORRECTO
# apps/utils/models.py
class SoftDeleteMixin(models.Model):
    class Meta:
        abstract = True

# ✅ CORRECTO
# apps/core/models.py
class SoftDeleteMixin(models.Model):
    class Meta:
        abstract = True
```

---

### ❌ Anti-pattern 3: Abstracto sin abstract=True

```python
# ❌ INCORRECTO
# apps/core/models.py
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # ❌ Falta abstract=True

# ✅ CORRECTO
# apps/core/models.py
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True  # ✅ OBLIGATORIO
```

---

## 📝 CHECKLIST DE REVISIÓN

```
Al crear un modelo, verifica:

[ ] ¿El modelo tiene abstract=True?
    └─ SÍ → Debe ir en apps/core/models.py
    └─ NO → Ir a siguiente

[ ] ¿El modelo crea tabla (db_table)?
    └─ SÍ → Debe ir en apps/{negocio}/models.py
    └─ NO → ERROR (falta abstract=True)

[ ] ¿El modelo está en core/models.py?
    └─ SÍ → Verificar que tiene abstract=True
    └─ NO → OK

[ ] ¿apps/utils/ tiene archivos con clases?
    └─ SÍ → ERROR (mover a core/)
    └─ NO → OK
```

---

## 🎯 RESUMEN EJECUTIVO

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              LA REGLA MÁS IMPORTANTE                    │
│                                                         │
│   apps/core/models.py:                                 │
│   ✅ SOLO abstract=True                                │
│   ❌ NINGÚN db_table                                   │
│                                                         │
│   apps/{negocio}/models.py:                            │
│   ✅ Modelos concretos                                 │
│   ✅ db_table (crea tabla)                             │
│   ❌ NO abstract=True                                  │
│                                                         │
│   apps/utils/:                                         │
│   ✅ SOLO funciones                                    │
│   ❌ NO clases                                         │
│   ❌ NO models.py                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘

MIGRACIÓN PENDIENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Mover SoftDeleteMixin:
   apps/utils/models.py → apps/core/models.py

2. Mover modelos concretos de core/:
   CallRecord → apps/analytics/models.py
   Center, Service → apps/centers/models.py
   UserServiceAccess → apps/access/models.py

3. Eliminar:
   apps/utils/models.py

Ver: ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v3.0.0.md
```

---

**FIN DE LA GUÍA PRÁCTICA v2.0.0**

Tiempo de lectura: 5 minutos  
Tiempo de consulta: 30 segundos (usa el checklist)  
Documento complementario: ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v3.0.0.md  
Cambio crítico desde v1.0.0: core/ SOLO abstractos
