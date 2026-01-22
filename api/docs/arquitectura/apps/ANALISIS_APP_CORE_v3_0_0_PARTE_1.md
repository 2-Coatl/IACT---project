---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Core PARTE 1/3
categoria: arquitectura/apps
tema: apps/core/ - Abstract Models, Exceptions y Validators
autor: Claude Technical Analysis
tags: [core, abstract-models, exceptions, validators, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes) ⭐ APLICADO
  - GUIA_CORE_VS_UTILS_v2_0_0.md ⭐ APLICADO
  - ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v3_0_0.md ⭐ APLICADO
estado: definitivo
parte: 1 de 3
relacionado:
  - ANALISIS_APP_CORE_v3_0_0_PARTE_2.md
  - ANALISIS_APP_CORE_v3_0_0_PARTE_3.md
replaces: []
---

# ANÁLISIS DE apps/core/ v3.0.0 - PARTE 1/3
## ABSTRACT MODELS, EXCEPTIONS Y VALIDATORS

**BASADO EN: CLEAN_CODE v3.0.1 + GUIA_CORE_VS_UTILS v2.0.0**

---

## 1. RESUMEN EJECUTIVO

### 1.1 Información General

```yaml
App: apps/core/
Tipo: CORE MODULE (3 partes)
Líneas estimadas: ~1,500 líneas código
Propósito: Componentes base y clases abstractas (NO modelos concretos)
Estructura:
  - models.py (SOLO abstract=True) 🔴 CRÍTICO
  - exceptions.py (excepciones base)
  - validators.py (clases validadoras)
  - middleware.py (middleware custom)
  - permissions.py (DRF permissions)
  - mixins.py (view/serializer mixins)
  - services.py (base service classes)
Tests: 25 tests estimados
Coverage objetivo: >90%
Clean Code: v3.0.1 aplicado ✅

🚨 CRÍTICO - NO TIENE:
  ❌ NO settings/ (settings van en config/)
  ❌ NO modelos concretos (van en apps de negocio)
  ❌ NO funciones sueltas (van en apps/utils/)
```

### 1.2 Responsabilidades Core

```yaml
Abstract Models (SOLO abstract=True):
  ✅ TimeStampedModel (created_at, updated_at)
  ✅ SoftDeleteMixin (is_deleted, deleted_at)
  ✅ AuditedModel (created_by, updated_by)
  ✅ SoftDeleteManager/QuerySet
  ❌ NINGÚN modelo concreto

Exceptions Base:
  ✅ IACTBaseException
  ✅ ValidationError
  ✅ BusinessRuleError
  ✅ PermissionDeniedError
  ✅ ResourceNotFoundError

Validators (Clases):
  ✅ PhoneValidator
  ✅ EmailValidator
  ✅ NITValidator
  ✅ DateRangeValidator
```

### 1.3 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                apps/core/                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  models.py (SOLO abstract=True)          🔴 CRÍTICO│
│  ├─ TimeStampedModel                               │
│  ├─ SoftDeleteMixin                                │
│  ├─ AuditedModel                                   │
│  ├─ SoftDeleteManager                              │
│  └─ SoftDeleteQuerySet                             │
│                                                     │
│  ❌ CallRecord → apps/analytics/models.py          │
│  ❌ Center → apps/centers/models.py                │
│  ❌ Service → apps/centers/models.py               │
│                                                     │
│  exceptions.py:                                     │
│  ├─ IACTBaseException                              │
│  ├─ ValidationError                                │
│  ├─ BusinessRuleError                              │
│  └─ PermissionDeniedError                          │
│                                                     │
│  validators.py:                                     │
│  ├─ PhoneValidator                                 │
│  ├─ EmailValidator                                 │
│  └─ NITValidator                                   │
│                                                     │
└─────────────────────────────────────────────────────┘

🔴 REGLA DE ORO:
  apps/core/models.py SOLO puede tener:
  ✅ class Meta: abstract = True
  ❌ NINGÚN db_table
```

---

## 2. CLEAN CODE v3.0.1 APLICADO

### 2.1 Principio: SOLO Abstract Models

```python
# ============================================================================
# REGLA CRÍTICA: apps/core/models.py SOLO abstract=True
# ============================================================================

# ❌ INCORRECTO - Modelo concreto en core/
# apps/core/models.py
class CallRecord(models.Model):
    fecha = models.DateField()
    
    class Meta:
        db_table = 'core_call_records'  # ❌ Crea tabla
        # ❌ NO tiene abstract=True

# ✅ CORRECTO - Modelo abstracto en core/
# apps/core/models.py
class TimeStampedModel(models.Model):
    """
    Modelo base con timestamps automáticos.
    
    CLEAN_CODE v3.0.1: Nombre auto-documentado.
    
    Todos los modelos que hereden tendrán:
    - created_at (auto)
    - updated_at (auto)
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creado'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Actualizado'
    )
    
    class Meta:
        abstract = True  # ✅ OBLIGATORIO
```

---

## 3. ABSTRACT MODELS

### 3.1 models.py (SOLO abstract=True)

```python
"""
Abstract Models base para IACT.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
CRÍTICO: SOLO modelos con abstract=True.

Modelos concretos van en apps de negocio:
- CallRecord → apps/analytics/models.py
- Center, Service → apps/centers/models.py
- UserServiceAccess → apps/access/models.py
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo base con timestamps automáticos.
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    
    Provee campos automáticos:
    - created_at: Se setea al crear
    - updated_at: Se actualiza al guardar
    
    Uso:
        class MiModelo(TimeStampedModel):
            # Automáticamente tiene created_at y updated_at
            pass
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creado',
        help_text='Fecha y hora de creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Actualizado',
        help_text='Fecha y hora de última actualización'
    )
    
    class Meta:
        abstract = True  # ✅ OBLIGATORIO


class SoftDeleteMixin(models.Model):
    """
    Mixin para soft delete (borrado lógico).
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    
    Permite marcar registros como eliminados sin
    borrarlos físicamente de la BD.
    
    Provee:
    - is_deleted (flag)
    - deleted_at (timestamp)
    - delete() override (soft)
    - hard_delete() (real)
    
    Uso:
        class MiModelo(SoftDeleteMixin, models.Model):
            pass
        
        # Soft delete
        obj.delete()  # Marca is_deleted=True
        
        # Hard delete
        obj.hard_delete()  # Elimina de BD
        
        # Query solo no eliminados
        MiModelo.objects.active()
    """
    
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Eliminado',
        help_text='Marca si el registro fue eliminado'
    )
    
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Eliminado en',
        help_text='Fecha y hora de eliminación'
    )
    
    class Meta:
        abstract = True  # ✅ OBLIGATORIO
    
    objects = models.Manager()  # Manager default
    # active_objects agregado por SoftDeleteManager
    
    def delete(self, using=None, keep_parents=False):
        """
        Soft delete: marca como eliminado.
        
        NO elimina físicamente de la BD.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def hard_delete(self, using=None, keep_parents=False):
        """
        Hard delete: elimina físicamente.
        
        Usa delete() de Django directamente.
        """
        super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restaura registro eliminado."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class SoftDeleteQuerySet(models.QuerySet):
    """
    QuerySet para soft delete.
    
    CLEAN_CODE v3.0.1: Nombre auto-documentado.
    
    Provee métodos:
    - active(): Solo no eliminados
    - deleted(): Solo eliminados
    - with_deleted(): Todos
    """
    
    def active(self):
        """Retorna solo registros no eliminados."""
        return self.filter(is_deleted=False)
    
    def deleted(self):
        """Retorna solo registros eliminados."""
        return self.filter(is_deleted=True)
    
    def with_deleted(self):
        """Retorna todos los registros."""
        return self


class SoftDeleteManager(models.Manager):
    """
    Manager para soft delete.
    
    CLEAN_CODE v3.0.1: Nombre auto-documentado.
    
    Por defecto retorna solo registros activos.
    
    Uso:
        class MiModelo(SoftDeleteMixin, models.Model):
            objects = SoftDeleteManager()
        
        # Solo activos (default)
        MiModelo.objects.all()
        
        # Incluir eliminados
        MiModelo.objects.with_deleted()
    """
    
    def get_queryset(self):
        """Retorna QuerySet con soft delete."""
        return SoftDeleteQuerySet(self.model, using=self._db)
    
    def active(self):
        """Retorna solo no eliminados."""
        return self.get_queryset().active()
    
    def deleted(self):
        """Retorna solo eliminados."""
        return self.get_queryset().deleted()
    
    def with_deleted(self):
        """Retorna todos."""
        return self.get_queryset().with_deleted()


class AuditedModel(models.Model):
    """
    Modelo base con auditoría de usuario.
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    
    Rastrea qué usuario creó/modificó el registro.
    
    Provee:
    - created_by (User FK)
    - updated_by (User FK)
    
    Uso:
        class MiModelo(AuditedModel):
            pass
        
        # Al crear
        obj = MiModelo.objects.create(
            created_by=request.user,
            ...
        )
        
        # Al actualizar
        obj.updated_by = request.user
        obj.save()
    """
    
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_created',
        verbose_name='Creado por',
        help_text='Usuario que creó el registro'
    )
    
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_updated',
        verbose_name='Actualizado por',
        help_text='Usuario que actualizó el registro'
    )
    
    class Meta:
        abstract = True  # ✅ OBLIGATORIO
```

---

## 4. EXCEPTIONS

### 4.1 exceptions.py

```python
"""
Exceptions base para IACT.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""


class IACTBaseException(Exception):
    """
    Exception base para todo el proyecto IACT.
    
    CLEAN_CODE v3.0.1: Prefijo IACT indica origen.
    
    Todas las exceptions custom deben heredar de esta.
    """
    pass


class ValidationError(IACTBaseException):
    """
    Error de validación de datos.
    
    Se lanza cuando validación de datos falla.
    
    Attributes:
        field: Campo que falló (opcional)
        message: Mensaje de error
    
    Example:
        raise ValidationError(
            message="Email inválido",
            field="email"
        )
    """
    
    def __init__(self, message: str, field: str = None):
        """
        Args:
            message: Mensaje de error
            field: Campo que falló (opcional)
        """
        self.field = field
        self.message = message
        super().__init__(message)


class BusinessRuleError(IACTBaseException):
    """
    Error de regla de negocio.
    
    Se lanza cuando se viola una regla de negocio.
    
    Example:
        raise BusinessRuleError(
            "No se puede eliminar un reporte en uso"
        )
    """
    pass


class PermissionDeniedError(IACTBaseException):
    """
    Error de permisos RBAC.
    
    Se lanza cuando usuario no tiene permiso.
    
    Attributes:
        function_id: ID de función requerida
        user_id: ID del usuario
    
    Example:
        raise PermissionDeniedError(
            function_id='reports.create',
            user_id=request.user.id
        )
    """
    
    def __init__(self, function_id: str, user_id: int = None):
        """
        Args:
            function_id: ID de función RBAC requerida
            user_id: ID del usuario (opcional)
        """
        self.function_id = function_id
        self.user_id = user_id
        
        message = f"Permission denied for function: {function_id}"
        if user_id:
            message += f" (user: {user_id})"
        
        super().__init__(message)


class ResourceNotFoundError(IACTBaseException):
    """
    Recurso no encontrado.
    
    Attributes:
        resource_type: Tipo de recurso
        resource_id: ID del recurso
    
    Example:
        raise ResourceNotFoundError(
            resource_type='Report',
            resource_id=123
        )
    """
    
    def __init__(self, resource_type: str, resource_id: any):
        """
        Args:
            resource_type: Tipo de recurso (str)
            resource_id: ID del recurso
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        
        super().__init__(
            f"{resource_type} not found: {resource_id}"
        )


class ConfigurationError(IACTBaseException):
    """Error de configuración del sistema."""
    pass


class ExternalServiceError(IACTBaseException):
    """
    Error al comunicarse con servicio externo.
    
    Attributes:
        service_name: Nombre del servicio
        error_message: Mensaje de error
    
    Example:
        raise ExternalServiceError(
            service_name='IVR Database',
            error_message='Connection timeout'
        )
    """
    
    def __init__(self, service_name: str, error_message: str):
        """
        Args:
            service_name: Nombre del servicio
            error_message: Mensaje de error
        """
        self.service_name = service_name
        
        super().__init__(
            f"External service error ({service_name}): {error_message}"
        )
```

---

## 5. VALIDATORS (Clases)

### 5.1 validators.py

```python
"""
Validators (clases) para IACT.

CLEAN_CODE v3.0.1: Nombres auto-documentados.

NOTA: Funciones de validación van en apps/utils/validators.py
      Clases de validación van aquí (apps/core/validators.py)
"""

import re
from django.core.exceptions import ValidationError as DjangoValidationError


class PhoneValidator:
    """
    Validador de teléfonos.
    
    CLEAN_CODE v3.0.1: Clase validadora (va en core/).
    
    Uso:
        class MiModelo(models.Model):
            phone = models.CharField(
                max_length=20,
                validators=[PhoneValidator()]
            )
    """
    
    message = "Número de teléfono inválido"
    code = "invalid_phone"
    
    def __call__(self, value):
        """Valida teléfono."""
        # Remover espacios, guiones, paréntesis
        clean = re.sub(r'[\s\-\(\)\+]', '', value)
        
        # Validar solo dígitos y longitud
        if not clean.isdigit() or not (10 <= len(clean) <= 15):
            raise DjangoValidationError(
                self.message,
                code=self.code
            )


class EmailValidator:
    """
    Validador de emails.
    
    Uso:
        class MiModelo(models.Model):
            email = models.EmailField(
                validators=[EmailValidator()]
            )
    """
    
    message = "Email inválido"
    code = "invalid_email"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def __call__(self, value):
        """Valida email."""
        if not re.match(self.pattern, value):
            raise DjangoValidationError(
                self.message,
                code=self.code
            )


class NITValidator:
    """
    Validador de NIT colombiano.
    
    Uso:
        class MiModelo(models.Model):
            nit = models.CharField(
                max_length=20,
                validators=[NITValidator()]
            )
    """
    
    message = "NIT inválido"
    code = "invalid_nit"
    
    def __call__(self, value):
        """Valida NIT."""
        # Limpiar
        clean = value.replace('.', '').replace('-', '')
        
        # Validar formato
        if not re.match(r'^\d{9,10}$', clean):
            raise DjangoValidationError(
                self.message,
                code=self.code
            )
```

---

## 6. RESUMEN PARTE 1

```yaml
Abstract Models (SOLO abstract=True):
  ✅ TimeStampedModel (~40 líneas)
  ✅ SoftDeleteMixin (~60 líneas)
  ✅ SoftDeleteQuerySet (~20 líneas)
  ✅ SoftDeleteManager (~30 líneas)
  ✅ AuditedModel (~50 líneas)

🔴 REGLA CRÍTICA:
  - TODOS con abstract=True
  - NINGUNO con db_table
  - Modelos concretos en apps de negocio

Exceptions (6):
  ✅ IACTBaseException
  ✅ ValidationError
  ✅ BusinessRuleError
  ✅ PermissionDeniedError
  ✅ ResourceNotFoundError
  ✅ ConfigurationError
  ✅ ExternalServiceError

Validators (3 clases):
  ✅ PhoneValidator
  ✅ EmailValidator
  ✅ NITValidator

Clean Code Aplicado:
  ✅ v3.0.1 PARTE 1: Nombres auto-documentados
  ✅ GUIA_CORE_VS_UTILS v2.0.0: SOLO abstractos
  ✅ Docstrings Google Style

Total: ~600 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 2/3: Middleware, Permissions y Mixins**

Contenido:
- ✅ Middleware custom (3-4 middleware)
- ✅ DRF Permissions (4 permissions)
- ✅ View/Serializer Mixins (5 mixins)
- ✅ Context processors

**Estimado:** ~600 líneas, 2 horas

---

**Fin de PARTE 1/3 - v3.0.0 con CLEAN_CODE v3.0.1 aplicado ✅**
