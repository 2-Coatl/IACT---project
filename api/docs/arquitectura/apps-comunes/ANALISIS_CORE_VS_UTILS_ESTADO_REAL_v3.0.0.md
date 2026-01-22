---
version: 3.0.0
date: 2026-01-18
project: IACT Call Center System
type: Análisis de Arquitectura - Apps Compartidas
categoria: arquitectura/apps-comunes
tema: Análisis CORE vs UTILS - Estado Real y Recomendaciones
autor: Claude Technical Analysis
tags: [core, utils, arquitectura, django, best-practices, abstract-models-only]
relacionado:
  - ANALISIS_APP_CORE_v2.0.0.md
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_0.md
estado: completado
replaces: ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v2.0.0.md
changelog: |
  v3.0.0 (2026-01-18):
  - CORRECCIÓN CRÍTICA: apps/core/models.py debe tener SOLO abstract=True
  - CallRecord, Center, Service en core/ es ERROR (son concretos)
  - Modelos concretos deben ir en apps de negocio
  - Actualiza plan de migración completo
  - Ejemplos corregidos con abstract=True
  v2.0.0 (2026-01-18):
  - Enfatiza diferencia: utils/ = FUNCIONES, core/ = CLASES
  v1.0.0 (2026-01-17):
  - Versión inicial
---

# ANÁLISIS: CORE vs UTILS - ESTADO REAL DEL PROYECTO v3.0.0

**Basado en código existente - Filosofía Django `django.core` vs `django.utils`**

---

## 🚨 CORRECCIÓN CRÍTICA v3.0.0

```
ERROR IDENTIFICADO EN v2.0.0:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

v2.0.0 decía:
"apps/core/models.py puede tener modelos concretos"

ESTO ES INCORRECTO ❌

CORRECCIÓN v3.0.0:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/models.py debe tener SOLO:
✅ Modelos con abstract=True
✅ Managers/QuerySets para abstractos
❌ NINGÚN modelo concreto (sin abstract=True)

CallRecord, Center, Service en core/models.py → ERROR
Deben moverse a apps de negocio.
```

---

## RESUMEN EJECUTIVO

### Estado Actual

```
apps/core/  ✅ YA EXISTE
apps/utils/ ✅ YA EXISTE

PROBLEMAS IDENTIFICADOS v3.0.0:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ apps/utils/models.py tiene CLASES (deben ir en core/)
⚠️ apps/core/models.py tiene modelos CONCRETOS (deben ir en apps de negocio)

SOLUCIÓN:
1. Mover SoftDeleteMixin de utils/ → core/ (CLASES)
2. Mover CallRecord, Center, Service de core/ → apps de negocio (CONCRETOS)
3. core/models.py solo debe tener abstract=True
```

---

## TABLA DE CONTENIDOS

1. [Filosofía Django: core vs utils](#filosofia)
2. [CRÍTICO: apps/core/ SOLO Abstractos](#core-solo-abstractos)
3. [Estado Actual del Proyecto](#estado-actual)
4. [Problemas Identificados](#problemas)
5. [Recomendaciones de Refactorización](#recomendaciones)
6. [Plan de Migración](#plan)

---

<a name="filosofia"></a>
## 1. FILOSOFÍA DJANGO: core vs utils

### 1.1 django/utils/ - Solo FUNCIONES

```python
# django/utils/text.py
def slugify(value):                    # ✅ FUNCIÓN
    return slug

def truncate_words(text, num):         # ✅ FUNCIÓN
    return truncated

# django/utils/timezone.py
def now():                             # ✅ FUNCIÓN
    return datetime.now()

# ❌ NO HAY CLASES en django/utils/
```

### 1.2 django/core/ - Solo CLASES

```python
# django/core/validators.py
class EmailValidator:                  # ✅ CLASE
    def __call__(self, value):
        # lógica

# django/core/paginator.py
class Paginator:                       # ✅ CLASE
    def __init__(self, object_list, per_page):
        # lógica

# ❌ NO HAY FUNCIONES sueltas en django/core/
```

### 1.3 Regla Simple

```
PREGUNTA: ¿Qué estoy escribiendo?

def mi_funcion():        → apps/utils/
class MiClase:           → apps/core/
```

---

<a name="core-solo-abstractos"></a>
## 2. CRÍTICO: apps/core/ SOLO ABSTRACTOS

### 2.1 apps/core/models.py - REGLA DE ORO

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   apps/core/models.py SOLO puede tener:                │
│                                                         │
│   ✅ class MiModelo(models.Model):                     │
│         class Meta:                                     │
│             abstract = True  ← OBLIGATORIO             │
│                                                         │
│   ✅ class MiManager(models.Manager)                   │
│   ✅ class MiQuerySet(models.QuerySet)                 │
│                                                         │
│   ❌ class MiModelo(models.Model):                     │
│         class Meta:                                     │
│             db_table = 'tabla'  ← PROHIBIDO            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 ¿Por qué SOLO abstractos?

```
FILOSOFÍA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/ = Componentes FUNDAMENTALES del framework
           = Base classes que OTROS heredan
           = NO es una app de negocio

Modelos abstractos:
✅ Son base classes (como TimeStampedModel)
✅ Definen comportamiento compartido
✅ NO crean tablas en DB
✅ Otros modelos los heredan

Modelos concretos:
❌ Son lógica de negocio específica
❌ Crean tablas en DB
❌ Van en apps de negocio (analytics, centers, etc)
```

### 2.3 Comparación Django Framework

```python
# ════════════════════════════════════════════════════════════
# django.contrib.contenttypes (ejemplo Django oficial)
# ════════════════════════════════════════════════════════════

# django/contrib/contenttypes/models.py
class ContentType(models.Model):
    """
    ¿Esto viola la regla?
    
    NO, porque django.contrib.contenttypes ES una APP,
    NO es django/core/
    
    django/core/ NO tiene models.py
    """
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'django_content_type'  # ← Tabla concreta


# ════════════════════════════════════════════════════════════
# django/core/ - NO TIENE MODELS
# ════════════════════════════════════════════════════════════

django/core/
├── validators.py    ✅ Validadores (clases)
├── paginator.py     ✅ Paginador (clase)
├── exceptions.py    ✅ Excepciones (clases)
└── ❌ NO HAY models.py


# ════════════════════════════════════════════════════════════
# PATRÓN IACT CORRECTO
# ════════════════════════════════════════════════════════════

apps/core/
├── models.py        ✅ SOLO abstract=True
├── validators.py    ✅ Validadores
├── exceptions.py    ✅ Excepciones
└── middleware.py    ✅ Middleware

apps/analytics/      ← APP de negocio
└── models.py        ✅ Modelos concretos (CallRecord)

apps/centers/        ← APP de negocio
└── models.py        ✅ Modelos concretos (Center, Service)
```

---

<a name="estado-actual"></a>
## 3. ESTADO ACTUAL DEL PROYECTO

### 3.1 apps/core/models.py (INCORRECTO)

```python
# Estado actual: apps/core/models.py

from django.db import models
from apps.utils import SoftDeleteMixin  # ❌ Import incorrecto


class CallRecord(SoftDeleteMixin, models.Model):
    """
    ❌ PROBLEMA: Modelo CONCRETO en core/
    
    Este modelo crea tabla en DB (db_table='core_call_records')
    NO tiene abstract=True
    
    DEBE IR EN: apps/analytics/models.py
    """
    fecha = models.DateField()
    telefono = models.CharField(max_length=20)
    servicio_800 = models.CharField(max_length=20)
    total_llamadas = models.IntegerField()
    
    class Meta:
        db_table = 'core_call_records'  # ❌ Crea tabla
        ordering = ['-fecha']
        # ❌ NO tiene abstract=True


class Center(SoftDeleteMixin, models.Model):
    """
    ❌ PROBLEMA: Modelo CONCRETO en core/
    
    DEBE IR EN: apps/centers/models.py
    """
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'core_centers'  # ❌ Crea tabla
        # ❌ NO tiene abstract=True


class Service(SoftDeleteMixin, models.Model):
    """
    ❌ PROBLEMA: Modelo CONCRETO en core/
    
    DEBE IR EN: apps/centers/models.py
    """
    numero_800 = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    center = models.ForeignKey(Center, on_delete=models.PROTECT)
    
    class Meta:
        db_table = 'core_services'  # ❌ Crea tabla
        # ❌ NO tiene abstract=True


class UserServiceAccess(SoftDeleteMixin, models.Model):
    """
    ❌ PROBLEMA: Modelo CONCRETO en core/
    
    DEBE IR EN: apps/access/models.py
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'user_service_accesses'  # ❌ Crea tabla
        # ❌ NO tiene abstract=True


# ANÁLISIS:
# ========
# ❌ 4 modelos concretos en core/ (INCORRECTO)
# ❌ Todos crean tablas en DB
# ❌ Ninguno tiene abstract=True
# ❌ Son lógica de negocio, NO base classes
```

### 3.2 apps/utils/models.py (INCORRECTO)

```python
# Estado actual: apps/utils/models.py

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """
    ❌ PROBLEMA: CLASE en utils/
    
    DEBE IR EN: apps/core/models.py
    """
    def delete(self):
        return self.update(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """
    ❌ PROBLEMA: CLASE en utils/
    
    DEBE IR EN: apps/core/models.py
    """
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteMixin(models.Model):
    """
    ❌ PROBLEMA: CLASE en utils/
    
    DEBE IR EN: apps/core/models.py
    
    Aunque es abstract=True, sigue siendo CLASE.
    utils/ solo debe tener FUNCIONES.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    
    class Meta:
        abstract = True  # ✅ Es abstract, pero...
                         # ❌ ...está en utils/ (incorrecto)


# ANÁLISIS:
# ========
# ❌ 3 CLASES en utils/ (INCORRECTO)
# ✅ SoftDeleteMixin tiene abstract=True (correcto)
# ❌ Pero está en utils/ en vez de core/
```

---

<a name="problemas"></a>
## 4. PROBLEMAS IDENTIFICADOS

### 4.1 Problema 1: Modelos Concretos en core/

```
VIOLACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/models.py tiene 4 modelos CONCRETOS:
- CallRecord      → Crea tabla 'core_call_records'
- Center          → Crea tabla 'core_centers'
- Service         → Crea tabla 'core_services'
- UserServiceAccess → Crea tabla 'user_service_accesses'

Todos tienen:
❌ db_table definido (crean tabla)
❌ NO tienen abstract=True

SOLUCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mover a apps de negocio:
- CallRecord → apps/analytics/models.py
- Center, Service → apps/centers/models.py
- UserServiceAccess → apps/access/models.py
```

### 4.2 Problema 2: Clases en utils/

```
VIOLACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/utils/models.py tiene 3 CLASES:
- SoftDeleteQuerySet
- SoftDeleteManager
- SoftDeleteMixin

utils/ solo debe tener FUNCIONES, NO clases.

SOLUCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mover a core/:
apps/utils/models.py → apps/core/models.py
```

### 4.3 Problema 3: core/ Sin Abstractos

```
AUSENCIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/models.py NO tiene modelos abstractos propios.

Debería tener:
- TimeStampedModel (abstract=True)
- AuditedModel (abstract=True)
- SoftDeleteMixin (abstract=True, movido de utils)

SOLUCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agregar modelos abstractos base a core/models.py
```

---

<a name="recomendaciones"></a>
## 5. RECOMENDACIONES DE REFACTORIZACIÓN

### 5.1 Estructura Ideal

```python
# ════════════════════════════════════════════════════════════
# apps/core/models.py - SOLO ABSTRACTOS
# ════════════════════════════════════════════════════════════

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo base con timestamps.
    
    TODOS los modelos IACT heredan esto.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # ✅ OBLIGATORIO


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
    
    CNST-005: TODOS los modelos IACT deben heredar esto.
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
        abstract = True  # ✅ OBLIGATORIO
    
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
        abstract = True  # ✅ OBLIGATORIO


# ════════════════════════════════════════════════════════════
# apps/analytics/models.py - NUEVO (modelos concretos)
# ════════════════════════════════════════════════════════════

from apps.core.models import SoftDeleteMixin, TimeStampedModel


class CallRecord(SoftDeleteMixin, TimeStampedModel):
    """
    Registro de llamadas agregado.
    
    Almacena datos procesados por fecha/teléfono/servicio.
    """
    fecha = models.DateField(db_index=True)
    telefono = models.CharField(max_length=20, db_index=True)
    servicio_800 = models.CharField(max_length=20, db_index=True)
    total_llamadas = models.IntegerField(default=0)
    llamadas_contestadas = models.IntegerField(default=0)
    llamadas_abandonadas = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'analytics_call_records'  # ✅ Tabla concreta
        ordering = ['-fecha', '-created_at']
        unique_together = [['fecha', 'telefono', 'servicio_800']]
        # ✅ NO tiene abstract=True


# ════════════════════════════════════════════════════════════
# apps/centers/models.py - NUEVO (modelos concretos)
# ════════════════════════════════════════════════════════════

from apps.core.models import SoftDeleteMixin, TimeStampedModel


class Center(SoftDeleteMixin, TimeStampedModel):
    """Centro de atención."""
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=20, unique=True, db_index=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'centers'  # ✅ Tabla concreta
        ordering = ['nombre']


class Service(SoftDeleteMixin, TimeStampedModel):
    """Servicio 800."""
    numero_800 = models.CharField(max_length=20, unique=True, db_index=True)
    nombre = models.CharField(max_length=200)
    center = models.ForeignKey(
        Center,
        on_delete=models.PROTECT,
        related_name='services'
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'services'  # ✅ Tabla concreta
        ordering = ['numero_800']


# ════════════════════════════════════════════════════════════
# apps/access/models.py - ACTUALIZADO (modelo movido)
# ════════════════════════════════════════════════════════════

from apps.core.models import SoftDeleteMixin, TimeStampedModel
from apps.centers.models import Service


class UserServiceAccess(SoftDeleteMixin, TimeStampedModel):
    """
    Acceso de usuario a servicios 800.
    
    Define qué servicios puede ver/gestionar cada usuario.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='service_accesses'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='user_accesses'
    )
    granted_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='service_accesses_granted'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_service_accesses'  # ✅ Tabla concreta
        unique_together = [['user', 'service']]


# ════════════════════════════════════════════════════════════
# apps/utils/ - SOLO FUNCIONES
# ════════════════════════════════════════════════════════════

# apps/utils/request.py
def get_client_ip(request):
    """Obtiene IP del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# apps/utils/formatters.py
def format_phone(phone):
    """Formatea teléfono colombiano."""
    if not phone or len(phone) != 10:
        return phone
    return f"{phone[:3]} {phone[3:6]} {phone[6:]}"


# ❌ apps/utils/models.py - ELIMINADO COMPLETAMENTE
```

---

<a name="plan"></a>
## 6. PLAN DE MIGRACIÓN

### 6.1 Pasos Detallados

```
FASE 1: Crear apps de negocio necesarias
────────────────────────────────────────────────────────────

1. Crear apps/analytics/ (si no existe)
   python manage.py startapp analytics apps/analytics

2. Crear apps/centers/ (si no existe)
   python manage.py startapp centers apps/centers

3. Registrar en INSTALLED_APPS


FASE 2: Preparar apps/core/models.py con abstractos
────────────────────────────────────────────────────────────

1. Copiar contenido de apps/utils/models.py
2. Pegar en apps/core/models.py (al inicio)
3. Agregar TimeStampedModel, AuditedModel
4. Verificar que TODOS tienen abstract=True


FASE 3: Mover modelos concretos
────────────────────────────────────────────────────────────

1. Crear apps/analytics/models.py
   - Mover CallRecord de core/
   - Cambiar import a: from apps.core.models import ...
   - Cambiar db_table a 'analytics_call_records'

2. Crear apps/centers/models.py
   - Mover Center de core/
   - Mover Service de core/
   - Actualizar ForeignKey de Service → Center
   - Cambiar db_tables a 'centers', 'services'

3. Actualizar apps/access/models.py
   - Mover UserServiceAccess de core/
   - Actualizar import: from apps.centers.models import Service
   - Mantener db_table 'user_service_accesses'


FASE 4: Actualizar imports en todo el proyecto
────────────────────────────────────────────────────────────

Buscar y reemplazar:

# CallRecord
from apps.core.models import CallRecord
→ from apps.analytics.models import CallRecord

# Center, Service
from apps.core.models import Center, Service
→ from apps.centers.models import Center, Service

# UserServiceAccess
from apps.core.models import UserServiceAccess
→ from apps.access.models import UserServiceAccess

# SoftDeleteMixin
from apps.utils.models import SoftDeleteMixin
→ from apps.core.models import SoftDeleteMixin

Comando:
grep -r "from apps.core.models import" apps/
grep -r "from apps.utils.models import" apps/


FASE 5: Crear migrations
────────────────────────────────────────────────────────────

1. python manage.py makemigrations analytics
2. python manage.py makemigrations centers
3. python manage.py makemigrations access

Las migrations deben ser solo de cambio de app,
NO de cambio de tabla (db_table no cambia).


FASE 6: Actualizar apps/core/models.py final
────────────────────────────────────────────────────────────

Eliminar modelos concretos de core/models.py:
- CallRecord → eliminado (ahora en analytics)
- Center → eliminado (ahora en centers)
- Service → eliminado (ahora en centers)
- UserServiceAccess → eliminado (ahora en access)

Dejar solo:
- TimeStampedModel
- SoftDeleteMixin
- SoftDeleteManager
- SoftDeleteQuerySet
- AuditedModel

Verificar: TODOS con abstract=True


FASE 7: Eliminar apps/utils/models.py
────────────────────────────────────────────────────────────

rm apps/utils/models.py

Verificar no quedan referencias:
grep -r "apps.utils.models" apps/


FASE 8: Ejecutar migrations
────────────────────────────────────────────────────────────

python manage.py migrate

Como no cambiamos db_table, no hay ALTER TABLE.
Solo actualiza django_content_type.


FASE 9: Tests
────────────────────────────────────────────────────────────

pytest tests/unit/ -v
pytest tests/integration/ -v


TOTAL: ~3-4 horas
```

### 6.2 Checklist de Verificación

```
ANTES DE EJECUTAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] Git commit actual (punto de retorno)
[ ] Rama nueva (feature/refactor-core-models)
[ ] Tests pasando
[ ] Backup de apps/core/models.py
[ ] Backup de apps/utils/models.py

DURANTE MIGRACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] apps/analytics/ creada
[ ] apps/centers/ creada
[ ] apps/core/models.py solo tiene abstract=True
[ ] CallRecord en apps/analytics/
[ ] Center, Service en apps/centers/
[ ] UserServiceAccess en apps/access/
[ ] Todos los imports actualizados
[ ] apps/utils/models.py eliminado

DESPUÉS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] Migrations creadas
[ ] Migrations ejecutadas sin errores
[ ] Tests pasan
[ ] Aplicación corre
[ ] Verificar django_content_type actualizado
```

---

## 7. ESTADO FINAL DESEADO

```
apps/core/models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Modelos BASE abstractos
Contiene: SOLO modelos con abstract=True

✅ class TimeStampedModel          (abstract=True)
✅ class SoftDeleteMixin            (abstract=True)
✅ class SoftDeleteManager          (helper)
✅ class SoftDeleteQuerySet         (helper)
✅ class AuditedModel               (abstract=True)

❌ NINGÚN modelo concreto
❌ NINGÚN db_table


apps/analytics/models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Analytics de llamadas
Contiene: Modelos de análisis

✅ class CallRecord                 (concreto)
   - db_table='analytics_call_records'
   - Hereda SoftDeleteMixin, TimeStampedModel


apps/centers/models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Gestión de centros y servicios
Contiene: Centros y servicios 800

✅ class Center                     (concreto)
   - db_table='centers'
   - Hereda SoftDeleteMixin, TimeStampedModel

✅ class Service                    (concreto)
   - db_table='services'
   - Hereda SoftDeleteMixin, TimeStampedModel


apps/access/models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Control de acceso
Contiene: RBAC + Service Access

✅ class UserServiceAccess          (concreto)
   - db_table='user_service_accesses'
   - Hereda SoftDeleteMixin, TimeStampedModel


apps/utils/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Funciones helper
Contiene: SOLO funciones

✅ request.py → get_client_ip()
✅ formatters.py → format_phone()
✅ validators_helpers.py → is_valid_phone()

❌ NO models.py (eliminado)
```

---

## RESUMEN Y DECISIÓN

```
PROBLEMAS IDENTIFICADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ⚠️ apps/core/models.py tiene modelos CONCRETOS
   - CallRecord, Center, Service, UserServiceAccess
   - NO tienen abstract=True
   - Crean tablas en DB
   
2. ⚠️ apps/utils/models.py tiene CLASES
   - SoftDeleteMixin, Manager, QuerySet
   - Deben ir en core/

SOLUCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Crear apps de negocio:
   - apps/analytics/
   - apps/centers/

2. Mover modelos concretos de core/ a apps de negocio

3. Mover clases de utils/ a core/

4. core/models.py solo debe tener abstract=True

TIEMPO ESTIMADO: 3-4 horas
RIESGO: MEDIO (cambios de estructura)
BENEFICIO: Arquitectura correcta ✅

REGLA FINAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/models.py:
✅ SOLO abstract=True
❌ NINGÚN modelo concreto

apps/{negocio}/models.py:
✅ Modelos concretos
❌ NO abstract=True
```

---

**FIN DEL ANÁLISIS - CORE vs UTILS v3.0.0**

Documento actualizado: 2026-01-18  
Cambios críticos desde v2.0.0: apps/core/ SOLO abstractos  
Estado actual: apps/core/ con concretos (incorrecto)  
Solución: Mover concretos a apps de negocio  
Tiempo estimado: 3-4 horas
