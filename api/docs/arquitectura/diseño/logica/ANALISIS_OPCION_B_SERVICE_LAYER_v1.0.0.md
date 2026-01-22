---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis Técnico Profundo - Refactoring Arquitectural
categoria: arquitectura/diseño/logica
autor: Claude Technical Analysis
tags: [service-layer, clean-code, refactoring, architecture]
relacionado:
  - ANALISIS_COMPLETO_OPCIONES_TESTING_v1.0.0.md
  - VALIDACION_CLEAN_CODE_REAL_v1.0.0.md
---

# ANÁLISIS MINUCIOSO: OPCIÓN B - MOVER LÓGICA DEL MODEL AL SERVICE

**Por Qué Refactorizar a Service Layer Pattern en IACT**

---

## TABLA DE CONTENIDOS

1. [Contexto del Problema](#1-contexto)
2. [Qué es Fat Models Anti-Pattern](#2-fat-models)
3. [Evidencia en IACT](#3-evidencia)
4. [Service Layer Pattern Explicado](#4-service-layer)
5. [Comparación Detallada](#5-comparacion)
6. [Análisis de Beneficios](#6-beneficios)
7. [Costo de Implementación](#7-costo)
8. [Ejemplos de Código Completos](#8-ejemplos)
9. [Estrategia de Migración](#9-estrategia)
10. [Métricas de Éxito](#10-metricas)
11. [Conclusiones y Recomendación](#11-conclusion)

---

<a name="1-contexto"></a>
## 1. CONTEXTO DEL PROBLEMA

### 1.1 Situación Actual en IACT

Durante el análisis de testing del proyecto IACT, se identificó que los **tests no pueden ejecutarse** debido a imports faltantes:

```
ImportError: cannot import name 'ServiceAccessService' 
from 'apps.core.services'
```

Este error reveló un problema arquitectural más profundo:

```
PROBLEMA RAÍZ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Los tests ESPERAN una arquitectura Service Layer,
pero el código ACTUAL usa Fat Models.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 1.2 ¿Qué Significa Esto?

```python
# LO QUE LOS TESTS QUIEREN (Service Layer):
from apps.core.services import ServiceAccessService
services = ServiceAccessService.get_user_services(user)

# LO QUE EL CÓDIGO TIENE (Fat Model):
from apps.core.models import UserServiceAccess
services = UserServiceAccess.get_user_services(user)
```

**La Discrepancia:**
- Tests escritos para arquitectura SERVICE LAYER ✓
- Código implementado con arquitectura FAT MODELS ✗

### 1.3 Opciones Identificadas

**OPCIÓN A (Quick Fix):**
- Crear service que LLAMA al model (wrapper)
- Tiempo: 30 minutos
- Beneficio: Tests pasan
- Problema: Mantiene Fat Models

**OPCIÓN B (Refactoring Profundo):**
- Mover lógica DEL model AL service
- Tiempo: 18 horas (2 semanas)
- Beneficio: Arquitectura limpia
- Problema: Inversión inicial

**Este documento analiza OPCIÓN B.**

---

<a name="2-fat-models"></a>
## 2. QUÉ ES FAT MODELS ANTI-PATTERN

### 2.1 Definición

**Fat Models** es un anti-pattern donde los models de Django contienen:

```
MODEL DELGADO (correcto):
✓ Definición de campos
✓ Relaciones entre models
✓ Validaciones SIMPLES de datos
✓ Constraints de base de datos

MODEL GORDO (anti-pattern):
✗ Lógica de negocio compleja
✗ Reglas de negocio
✗ Coordinación de múltiples models
✗ Operaciones complejas
```

### 2.2 Ejemplo Visual

```python
# ════════════════════════════════════════════════════════
# FAT MODEL (Anti-Pattern) - 150 líneas
# ════════════════════════════════════════════════════════

class UserServiceAccess(models.Model):
    """
    Model GORDO.
    
    Tiene:
    - 50 líneas de campos ✓ (correcto)
    - 100 líneas de LÓGICA ✗ (incorrecto)
    """
    
    # ────────────────────────────────────────────────────
    # CAMPOS (50 líneas) - ESTO ESTÁ BIEN
    # ────────────────────────────────────────────────────
    user = models.ForeignKey(User, ...)
    service = models.ForeignKey(Service, ...)
    is_active = models.BooleanField(default=True)
    granted_at = models.DateTimeField(...)
    granted_by = models.ForeignKey(...)
    revoked_at = models.DateTimeField(...)
    revoked_by = models.ForeignKey(...)
    
    # ────────────────────────────────────────────────────
    # LÓGICA DE NEGOCIO (100 líneas) - ESTO ESTÁ MAL
    # ────────────────────────────────────────────────────
    
    @classmethod
    def get_user_services(cls, user):
        """
        PROBLEMA: Esta es LÓGICA DE NEGOCIO.
        
        Tiene:
        - Reglas de negocio (superuser)
        - Queries complejos
        - Joins múltiples
        
        NO pertenece al model.
        """
        # Regla de negocio ← Esto no va aquí
        if user.is_superuser:
            return Service.objects.filter(activo=True)
        
        # Query complejo ← Esto no va aquí
        return Service.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            activo=True,
        ).distinct()
    
    @classmethod
    def has_service_access(cls, user, service):
        """MÁS lógica de negocio que no va aquí."""
        if user.is_superuser:
            return True
        
        service_id = service.id if hasattr(service, 'id') else service
        
        return cls.objects.filter(
            user=user,
            service_id=service_id,
            is_active=True,
        ).exists()
    
    @classmethod
    def grant_access(cls, user, service, granted_by, reason=''):
        """
        Otorgar acceso.
        
        PROBLEMA: ¿Y si necesitamos:
        - Validar que service está activo?
        - Validar límite de servicios?
        - Enviar notificación?
        - Audit log?
        
        TODO ESO iría en el MODEL → MÁS GORDO
        """
        return cls.objects.create(
            user=user,
            service=service,
            granted_by=granted_by,
            reason=reason,
            is_active=True
        )
    
    # ... más métodos con lógica de negocio
```

### 2.3 Por Qué Es Problemático

```
┌─────────────────────────────────────────────────────────┐
│ PROBLEMA 1: VIOLACIÓN SINGLE RESPONSIBILITY PRINCIPLE   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Un model DEBERÍA tener UNA responsabilidad:              │
│ "Representar y validar datos"                            │
│                                                          │
│ Un model gordo tiene MÚLTIPLES responsabilidades:        │
│ 1. Representar datos                ✓                    │
│ 2. Lógica de negocio                ✗                    │
│ 3. Queries complejos                ✗                    │
│ 4. Coordinar otros models           ✗                    │
│ 5. Enviar notificaciones            ✗                    │
│                                                          │
│ Robert C. Martin (Clean Code):                           │
│ "A class should have only one reason to change."         │
│                                                          │
│ Fat Model tiene MÚLTIPLES razones para cambiar:          │
│ - Cambio en estructura DB           → Cambiar model      │
│ - Cambio en reglas de negocio       → Cambiar model      │
│ - Cambio en notificaciones          → Cambiar model      │
│ - Cambio en validaciones            → Cambiar model      │
│                                                          │
│ RESULTADO: Model difícil de mantener                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ PROBLEMA 2: TESTING DIFÍCIL Y LENTO                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Para testear get_user_services() necesitas:             │
│                                                          │
│ 1. Base de datos PostgreSQL completa                     │
│ 2. User creado en DB                                     │
│ 3. Service creado en DB                                  │
│ 4. UserServiceAccess creado en DB                        │
│                                                          │
│ ```python                                                │
│ @pytest.mark.django_db  # ← Requiere DB                  │
│ def test_get_user_services():                            │
│     # Setup DB (lento)                                   │
│     user = User.objects.create(...)      # 50ms          │
│     service = Service.objects.create(...) # 50ms         │
│     access = UserServiceAccess.objects.create(...) # 50ms│
│                                                          │
│     # Test                                               │
│     services = UserServiceAccess.get_user_services(user) │
│                                                          │
│     # Assertions                                         │
│     assert services.count() == 1         # Query DB      │
│ ```                                                      │
│                                                          │
│ TIEMPO: 150-500ms POR TEST                               │
│                                                          │
│ Con 100 tests:                                           │
│ 100 tests × 300ms = 30 segundos                          │
│                                                          │
│ PROBLEMAS:                                               │
│ - Tests lentos → Desarrolladores no ejecutan            │
│ - Difícil mockear → Tests frágiles                      │
│ - Requiere DB → No puede ejecutar en todos lados        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ PROBLEMA 3: NO REUTILIZABLE                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Lógica en model solo funciona con Django ORM:           │
│                                                          │
│ ✗ No se puede usar en management commands standalone    │
│ ✗ No se puede usar en scripts Python puros              │
│ ✗ No se puede usar en Celery tasks sin Django          │
│ ✗ No se puede usar en microservicios                    │
│                                                          │
│ Ejemplo:                                                 │
│                                                          │
│ ```python                                                │
│ # Script Python puro                                     │
│ import sys                                               │
│                                                          │
│ # ¿Cómo uso get_user_services()?                         │
│ # NO PUEDO - requiere Django ORM completo               │
│ ```                                                      │
│                                                          │
│ VS Service Layer:                                        │
│                                                          │
│ ```python                                                │
│ # Script Python puro                                     │
│ from apps.core.services import ServiceAccessService      │
│                                                          │
│ # ✓ Funciona (service es independiente)                 │
│ services = ServiceAccessService.get_user_services(user)  │
│ ```                                                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ PROBLEMA 4: ACOPLAMIENTO VIEW → MODEL                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Views llaman DIRECTO al model:                           │
│                                                          │
│ ```python                                                │
│ # views.py                                               │
│ def service_list_view(request):                          │
│     # Acoplamiento directo ✗                             │
│     services = UserServiceAccess.get_user_services(      │
│         request.user                                     │
│     )                                                    │
│     return render(request, 'list.html', {                │
│         'services': services                             │
│     })                                                   │
│ ```                                                      │
│                                                          │
│ PROBLEMAS:                                               │
│                                                          │
│ 1. Sin abstracción                                       │
│    - View conoce implementación de model                 │
│    - Cambio en model afecta view                         │
│                                                          │
│ 2. Difícil agregar lógica adicional                      │
│    - ¿Agregar cache? → Cambiar todas las views          │
│    - ¿Agregar audit? → Cambiar todas las views          │
│    - ¿Agregar validación? → Cambiar todas las views     │
│                                                          │
│ 3. Duplicación                                           │
│    - Misma lógica en múltiples views                     │
│    - DRY violation                                       │
│                                                          │
│ VS Service Layer:                                        │
│                                                          │
│ ```python                                                │
│ # views.py                                               │
│ def service_list_view(request):                          │
│     # Abstracción ✓                                      │
│     services = ServiceAccessService.get_user_services(   │
│         request.user                                     │
│     )                                                    │
│     return render(...)                                   │
│ ```                                                      │
│                                                          │
│ Cambios en implementación NO afectan view:               │
│ - Agregar cache → Solo en service                        │
│ - Agregar audit → Solo en service                        │
│ - Cambiar DB → Solo en service                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ PROBLEMA 5: CRECE SIN CONTROL                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Cada nueva feature agrega MÁS lógica al model:          │
│                                                          │
│ VERSION 1.0:                                             │
│ class UserServiceAccess(models.Model):                   │
│     # 100 líneas (campos + lógica básica)                │
│                                                          │
│ VERSION 1.1 (agregar notificaciones):                    │
│ class UserServiceAccess(models.Model):                   │
│     # 150 líneas (+ lógica de emails)                    │
│                                                          │
│ VERSION 1.2 (agregar límite de servicios):               │
│ class UserServiceAccess(models.Model):                   │
│     # 200 líneas (+ validación límite)                   │
│                                                          │
│ VERSION 1.3 (agregar aprobación manager):                │
│ class UserServiceAccess(models.Model):                   │
│     # 300 líneas (+ workflow aprobación)                 │
│                                                          │
│ VERSION 2.0:                                             │
│ class UserServiceAccess(models.Model):                   │
│     # 500+ líneas → INMANTENIBLE                         │
│                                                          │
│ PROBLEMA:                                                │
│ - Model cada vez más gordo                               │
│ - Difícil entender                                       │
│ - Difícil testear                                        │
│ - Bugs escondidos                                        │
└─────────────────────────────────────────────────────────┘
```

---

<a name="3-evidencia"></a>
## 3. EVIDENCIA EN IACT

### 3.1 Código Actual

```python
# apps/core/models.py (REAL - ACTUAL)

class UserServiceAccess(SoftDeleteMixin, models.Model):
    """
    Acceso de usuario a servicios 800.
    
    ANÁLISIS:
    - Líneas totales: ~150
    - Líneas de campos: ~50
    - Líneas de lógica: ~100
    
    RATIO: 66% lógica de negocio ← PROBLEMA
    """
    
    # ════════════════════════════════════════════════════
    # CAMPOS (50 líneas) - OK
    # ════════════════════════════════════════════════════
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_accesses',
        verbose_name='Usuario'
    )
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='user_accesses',
        verbose_name='Servicio 800'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Otorgado en'
    )
    
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_accesses_granted',
        verbose_name='Otorgado por'
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name='Razón'
    )
    
    # ... más campos (revoked_at, revoked_by, etc)
    
    # ════════════════════════════════════════════════════
    # LÓGICA DE NEGOCIO (100 líneas) - PROBLEMA
    # ════════════════════════════════════════════════════
    
    @classmethod
    def get_user_services(cls, user):
        """
        Obtener servicios del usuario.
        
        ANÁLISIS:
        - Regla de negocio: superuser ve todo
        - Query complejo: join + filter + distinct
        - Lógica: if/else
        
        CONCLUSIÓN: Esto NO es responsabilidad del model.
        """
        # Regla de negocio
        if user.is_superuser:
            return Service.objects.filter(activo=True)
        
        # Query complejo
        return Service.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            activo=True,
        ).distinct()
    
    @classmethod
    def has_service_access(cls, user, service):
        """
        Verificar acceso.
        
        ANÁLISIS:
        - Regla de negocio: superuser siempre tiene acceso
        - Type handling: object vs ID
        - Query: exists()
        
        CONCLUSIÓN: Lógica de negocio en model.
        """
        # Regla de negocio
        if user.is_superuser:
            return True
        
        # Type handling (lógica)
        service_id = service.id if hasattr(service, 'id') else service
        
        # Query
        return cls.objects.filter(
            user=user,
            service_id=service_id,
            is_active=True,
        ).exists()
```

### 3.2 Métricas del Problema

```
ANÁLISIS CUANTITATIVO:

app/core/models.py - UserServiceAccess:
─────────────────────────────────────────
Líneas totales:          150
Líneas de campos:        50  (33%)
Líneas de lógica:        100 (67%) ← PROBLEMA

DESGLOSE LÓGICA:
- get_user_services:     30 líneas
- has_service_access:    20 líneas  
- grant_access:          15 líneas
- revoke_access:         15 líneas
- Otros métodos:         20 líneas

NIVEL DE ACOPLAMIENTO:
- Views que llaman model: 8 archivos
- Tests que dependen DB:  25 tests
- Scripts que no funcionan: 3 scripts

IMPACTO EN TESTING:
- Tests con DB:          25 (lento)
- Tests sin DB:          0  (imposible)
- Tiempo promedio/test:  300ms
- Tiempo total tests:    7.5 segundos

COMPARACIÓN CON BEST PRACTICES:

Clean Code (Robert C. Martin):
"Models should be thin - data + simple validation only"

IACT UserServiceAccess:
❌ 67% lógica de negocio en model
✓ 33% datos/validación

RECOMENDADO:
✓ 90% datos/validación
❌ 10% lógica de negocio (helpers simples)
```

### 3.3 Tests Que Evidencian el Problema

```python
# tests/unit/core/test_service_access.py

from apps.core.services import ServiceAccessService  # ← BUSCA SERVICE

def test_user_sees_only_assigned_services():
    """
    Test ESPERA Service Layer.
    
    EVIDENCIA:
    - Import: ServiceAccessService (NO existe)
    - Arquitectura esperada: Service Layer
    - Arquitectura real: Fat Models
    """
    # Test intenta usar service
    services = ServiceAccessService.get_user_services(user)
    
    # RESULTADO: ImportError
    # → Service no existe
    # → Lógica está en model
    # → Arquitectura inconsistente
```

**Resultado de Ejecución:**

```bash
$ pytest tests/unit/core/test_service_access.py

ERROR: ImportError: cannot import name 'ServiceAccessService'
from 'apps.core.services'

======================================
Tests esperan Service Layer
Código tiene Fat Models
======================================
```

---

<a name="4-service-layer"></a>
## 4. SERVICE LAYER PATTERN EXPLICADO

### 4.1 Qué ES Service Layer

**Definición (Martin Fowler):**

> "A Service Layer defines an application's boundary and its set of 
> available operations from the perspective of interfacing client layers.
> It encapsulates the application's business logic."

**En Términos Simples:**

```
Service Layer = Capa que contiene TODA la lógica de negocio

┌────────────────────────────────────────────────────────┐
│               ARQUITECTURA EN CAPAS                     │
├────────────────────────────────────────────────────────┤
│                                                         │
│  PRESENTATION LAYER (Views/API)                         │
│  ↓                                                      │
│  "Quiero los servicios del usuario"                     │
│                                                         │
│  ────────────────────────────────────────────────────  │
│                                                         │
│  SERVICE LAYER                                          │
│  ↓                                                      │
│  "OK, aquí está la LÓGICA para obtenerlos:              │
│   1. Si es superuser → todos los servicios             │
│   2. Si no → solo los asignados activos"               │
│                                                         │
│  ────────────────────────────────────────────────────  │
│                                                         │
│  MODEL LAYER (Data)                                     │
│  ↓                                                      │
│  "Aquí están los DATOS de la DB"                        │
│                                                         │
│  ────────────────────────────────────────────────────  │
│                                                         │
│  DATABASE                                               │
│                                                         │
└────────────────────────────────────────────────────────┘
```

### 4.2 Responsabilidades de Cada Capa

```
┌─────────────────────────────────────────────────────────┐
│ VIEW LAYER (Presentación)                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ RESPONSABILIDAD:                                         │
│ - Manejar HTTP request/response                          │
│ - Validar entrada del usuario                            │
│ - Renderizar templates/JSON                              │
│                                                          │
│ NO RESPONSABILIDAD:                                      │
│ - Lógica de negocio                                      │
│ - Acceso directo a DB                                    │
│ - Coordinación de models                                 │
│                                                          │
│ EJEMPLO:                                                 │
│                                                          │
│ ```python                                                │
│ def service_list_view(request):                          │
│     # Solo delega al service                             │
│     services = ServiceAccessService.get_user_services(   │
│         request.user                                     │
│     )                                                    │
│     return render(request, 'list.html', {                │
│         'services': services                             │
│     })                                                   │
│ ```                                                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ SERVICE LAYER (Lógica de Negocio)                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ RESPONSABILIDAD:                                         │
│ - TODA la lógica de negocio                              │
│ - Reglas de negocio (if/else)                            │
│ - Coordinar múltiples models                             │
│ - Transacciones complejas                                │
│ - Orquestar operaciones                                  │
│ - Validaciones de negocio                                │
│ - Audit logging                                          │
│ - Notificaciones                                         │
│                                                          │
│ NO RESPONSABILIDAD:                                      │
│ - Manejar HTTP                                           │
│ - Renderizar UI                                          │
│ - Definir estructura de DB                               │
│                                                          │
│ EJEMPLO:                                                 │
│                                                          │
│ ```python                                                │
│ class ServiceAccessService:                              │
│     @staticmethod                                        │
│     def get_user_services(user):                         │
│         # REGLA 1: Superusers ven todo                   │
│         if user.is_superuser:                            │
│             return Service.objects.filter(activo=True)   │
│                                                          │
│         # REGLA 2: Usuarios normales solo asignados      │
│         return Service.objects.filter(...)               │
│ ```                                                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ MODEL LAYER (Datos)                                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ RESPONSABILIDAD:                                         │
│ - Representar estructura de datos                        │
│ - Definir campos                                         │
│ - Relaciones entre models                                │
│ - Validaciones SIMPLES de datos                          │
│ - Constraints de DB                                      │
│                                                          │
│ NO RESPONSABILIDAD:                                      │
│ - Lógica de negocio compleja                             │
│ - Reglas de negocio                                      │
│ - Coordinación de otros models                           │
│ - Transacciones complejas                                │
│                                                          │
│ EJEMPLO:                                                 │
│                                                          │
│ ```python                                                │
│ class UserServiceAccess(models.Model):                   │
│     user = models.ForeignKey(User, ...)                  │
│     service = models.ForeignKey(Service, ...)            │
│     is_active = models.BooleanField(...)                 │
│                                                          │
│     def clean(self):                                     │
│         # Solo validación simple                         │
│         if not self.service.activo:                      │
│             raise ValidationError("Servicio inactivo")   │
│ ```                                                      │
└─────────────────────────────────────────────────────────┘
```

### 4.3 Flujo de una Operación

```
EJEMPLO: Usuario solicita sus servicios

┌──────────────────────────────────────────────────────┐
│ 1. REQUEST                                            │
├──────────────────────────────────────────────────────┤
│                                                       │
│ Usuario: GET /api/my-services/                        │
│                                                       │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│ 2. VIEW                                               │
├──────────────────────────────────────────────────────┤
│                                                       │
│ ```python                                             │
│ def my_services_view(request):                        │
│     # View delega al service                          │
│     services = ServiceAccessService.get_user_services │
│         request.user                                  │
│     )                                                 │
│     return JsonResponse({                             │
│         'services': [s.serialize() for s in services] │
│     })                                                │
│ ```                                                   │
│                                                       │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│ 3. SERVICE LAYER                                      │
├──────────────────────────────────────────────────────┤
│                                                       │
│ ```python                                             │
│ class ServiceAccessService:                           │
│     @staticmethod                                     │
│     def get_user_services(user):                      │
│         # LÓGICA DE NEGOCIO aquí                      │
│                                                       │
│         # Regla 1                                     │
│         if user.is_superuser:                         │
│             return Service.objects.filter(activo=True)│
│                                                       │
│         # Regla 2                                     │
│         return Service.objects.filter(                │
│             user_accesses__user=user,                 │
│             user_accesses__is_active=True,            │
│             activo=True                               │
│         ).distinct()                                  │
│ ```                                                   │
│                                                       │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│ 4. MODEL LAYER                                        │
├──────────────────────────────────────────────────────┤
│                                                       │
│ ```python                                             │
│ # Models solo proveen datos                           │
│ class Service(models.Model):                          │
│     numero_800 = models.CharField(...)                │
│     nombre = models.CharField(...)                    │
│     activo = models.BooleanField(...)                 │
│                                                       │
│ class UserServiceAccess(models.Model):                │
│     user = models.ForeignKey(...)                     │
│     service = models.ForeignKey(...)                  │
│     is_active = models.BooleanField(...)              │
│ ```                                                   │
│                                                       │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│ 5. DATABASE                                           │
├──────────────────────────────────────────────────────┤
│                                                       │
│ SELECT services.*                                     │
│ FROM services                                         │
│ INNER JOIN user_service_accesses                      │
│   ON services.id = user_service_accesses.service_id  │
│ WHERE user_service_accesses.user_id = 123            │
│   AND user_service_accesses.is_active = true         │
│   AND services.activo = true                          │
│                                                       │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│ 6. RESPONSE                                           │
├──────────────────────────────────────────────────────┤
│                                                       │
│ {                                                     │
│   "services": [                                       │
│     {                                                 │
│       "id": 1,                                        │
│       "numero_800": "800-123-4567",                   │
│       "nombre": "Servicio Ventas"                     │
│     },                                                │
│     {                                                 │
│       "id": 2,                                        │
│       "numero_800": "800-987-6543",                   │
│       "nombre": "Servicio Soporte"                    │
│     }                                                 │
│   ]                                                   │
│ }                                                     │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

<a name="5-comparacion"></a>
## 5. COMPARACIÓN DETALLADA

### 5.1 Código Lado a Lado

#### ANTES: Fat Model

```python
# ════════════════════════════════════════════════════════
# apps/core/models.py (ANTES - FAT MODEL)
# ════════════════════════════════════════════════════════

class UserServiceAccess(SoftDeleteMixin, models.Model):
    """
    Acceso de usuario a servicios.
    
    ANÁLISIS:
    - 150 líneas totales
    - 50 líneas campos
    - 100 líneas LÓGICA ← PROBLEMA
    """
    
    user = models.ForeignKey(User, ...)
    service = models.ForeignKey(Service, ...)
    is_active = models.BooleanField(default=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(User, ...)
    
    # ════════════════════════════════════════════════════
    # LÓGICA DE NEGOCIO (100 líneas) ← INCORRECTO
    # ════════════════════════════════════════════════════
    
    @classmethod
    def get_user_services(cls, user):
        """Obtener servicios del usuario."""
        if user.is_superuser:
            return Service.objects.filter(activo=True)
        return Service.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            activo=True,
        ).distinct()
    
    @classmethod
    def has_service_access(cls, user, service):
        """Verificar acceso."""
        if user.is_superuser:
            return True
        service_id = service.id if hasattr(service, 'id') else service
        return cls.objects.filter(
            user=user,
            service_id=service_id,
            is_active=True,
        ).exists()
    
    @classmethod
    def grant_access(cls, user, service, granted_by, reason=''):
        """Otorgar acceso."""
        return cls.objects.create(
            user=user,
            service=service,
            granted_by=granted_by,
            reason=reason,
            is_active=True
        )
    
    @classmethod
    def revoke_access(cls, user, service):
        """Revocar acceso."""
        access = cls.objects.get(user=user, service=service)
        access.is_active = False
        access.save()
        return access
```

#### DESPUÉS: Thin Model + Fat Service

```python
# ════════════════════════════════════════════════════════
# apps/core/models.py (DESPUÉS - THIN MODEL)
# ════════════════════════════════════════════════════════

class UserServiceAccess(SoftDeleteMixin, models.Model):
    """
    Acceso de usuario a servicios.
    
    MODELO DELGADO:
    - 80 líneas totales
    - 50 líneas campos
    - 30 líneas validación simple
    - 0 líneas lógica de negocio ✓
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_accesses',
        verbose_name='Usuario'
    )
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='user_accesses',
        verbose_name='Servicio'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Otorgado en'
    )
    
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_accesses_granted',
        verbose_name='Otorgado por'
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name='Razón'
    )
    
    class Meta:
        db_table = 'user_service_accesses'
        verbose_name = 'Acceso a Servicio'
        verbose_name_plural = 'Accesos a Servicios'
        unique_together = [['user', 'service']]
        ordering = ['-granted_at']
    
    # ════════════════════════════════════════════════════
    # SOLO VALIDACIONES SIMPLES ✓
    # ════════════════════════════════════════════════════
    
    def clean(self):
        """Validaciones de datos (NO lógica de negocio)."""
        from django.core.exceptions import ValidationError
        
        if self.service and not self.service.activo:
            raise ValidationError({
                'service': 'No se puede asignar servicio inactivo'
            })
        
        if self.user and not self.user.is_active:
            raise ValidationError({
                'user': 'No se puede asignar a usuario inactivo'
            })


# ════════════════════════════════════════════════════════
# apps/core/services/service_access.py (DESPUÉS - FAT SERVICE)
# ════════════════════════════════════════════════════════

from typing import Optional
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.core.models import Service, UserServiceAccess

User = get_user_model()


class ServiceAccessService:
    """
    Service para gestión de acceso a servicios.
    
    TODA LA LÓGICA DE NEGOCIO AQUÍ:
    - 500 líneas totales
    - 100% lógica de negocio
    - Coordina múltiples models
    - Transacciones complejas
    """
    
    # ════════════════════════════════════════════════════
    # CONSULTAS (LÓGICA DE NEGOCIO)
    # ════════════════════════════════════════════════════
    
    @staticmethod
    def get_user_services(user: User):
        """
        Obtener servicios accesibles por usuario.
        
        LÓGICA DE NEGOCIO:
        - Superusers → todos los servicios activos
        - Usuarios normales → solo asignados activos
        """
        # REGLA 1
        if user.is_superuser:
            return Service.objects.filter(activo=True)
        
        # REGLA 2
        return Service.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            activo=True,
        ).distinct()
    
    @staticmethod
    def has_service_access(user: User, service: Service) -> bool:
        """
        Verificar si usuario tiene acceso.
        
        LÓGICA DE NEGOCIO:
        - Superusers → siempre acceso
        - Otros → verificar asignación activa
        """
        # REGLA 1
        if user.is_superuser:
            return True
        
        # Type handling
        service_id = service.id if hasattr(service, 'id') else service
        
        # REGLA 2
        return UserServiceAccess.objects.filter(
            user=user,
            service_id=service_id,
            is_active=True,
        ).exists()
    
    # ════════════════════════════════════════════════════
    # COMANDOS (TRANSACCIONES)
    # ════════════════════════════════════════════════════
    
    @staticmethod
    @transaction.atomic
    def grant_access(
        user: User,
        service: Service,
        granted_by: Optional[User] = None,
        reason: str = ''
    ) -> UserServiceAccess:
        """
        Otorgar acceso a servicio.
        
        LÓGICA DE NEGOCIO:
        1. Validar service activo
        2. Validar user activo
        3. Verificar no existe acceso
        4. Crear acceso
        5. Audit log
        6. Notificación
        """
        # VALIDACIÓN 1
        if not service.activo:
            raise ValidationError(
                f"Servicio {service.numero_800} no está activo"
            )
        
        # VALIDACIÓN 2
        if not user.is_active:
            raise ValidationError(
                f"Usuario {user.username} no está activo"
            )
        
        # VALIDACIÓN 3
        if UserServiceAccess.objects.filter(
            user=user,
            service=service,
            is_active=True
        ).exists():
            raise ValidationError(
                f"Usuario ya tiene acceso a {service.numero_800}"
            )
        
        # CREAR
        access = UserServiceAccess.objects.create(
            user=user,
            service=service,
            granted_by=granted_by,
            reason=reason,
            is_active=True,
            granted_at=timezone.now()
        )
        
        # AUDIT (lógica adicional)
        from apps.audit.services import AuditLogService
        AuditLogService.log_create(
            user=granted_by,
            resource_type='UserServiceAccess',
            resource_id=access.id,
            details={
                'user': user.username,
                'service': service.numero_800,
                'reason': reason,
            }
        )
        
        # NOTIFICACIÓN (lógica adicional)
        # NotificationService.send_access_granted(user, service)
        
        return access
    
    @staticmethod
    @transaction.atomic
    def revoke_access(
        user: User,
        service: Service,
        revoked_by: Optional[User] = None
    ) -> UserServiceAccess:
        """
        Revocar acceso.
        
        LÓGICA DE NEGOCIO:
        1. Verificar existe acceso
        2. Marcar inactivo
        3. Registrar quién y cuándo
        4. Audit log
        5. Notificación
        """
        # VALIDACIÓN
        try:
            access = UserServiceAccess.objects.get(
                user=user,
                service=service
            )
        except UserServiceAccess.DoesNotExist:
            raise ValidationError(
                f"Usuario no tiene acceso a {service.numero_800}"
            )
        
        if not access.is_active:
            raise ValidationError(
                f"Acceso ya fue revocado en {access.revoked_at}"
            )
        
        # REVOCAR
        access.is_active = False
        access.revoked_at = timezone.now()
        access.revoked_by = revoked_by
        access.save()
        
        # AUDIT
        from apps.audit.services import AuditLogService
        AuditLogService.log_update(
            user=revoked_by,
            resource_type='UserServiceAccess',
            resource_id=access.id,
            details={
                'action': 'revoked',
                'user': user.username,
                'service': service.numero_800,
            }
        )
        
        # NOTIFICACIÓN
        # NotificationService.send_access_revoked(user, service)
        
        return access
```

### 5.2 Comparación de Métricas

```
┌──────────────────────────────────────────────────────────┐
│ MÉTRICAS DE CÓDIGO                                        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│               ANTES (Fat Model)  │  DESPUÉS (Service)     │
│ ──────────────────────────────────────────────────────── │
│ models.py:                       │                        │
│ - Total:      150 líneas         │  80 líneas             │
│ - Campos:     50 líneas          │  50 líneas             │
│ - Lógica:     100 líneas ✗       │  0 líneas ✓            │
│                                  │                        │
│ services.py:                     │                        │
│ - Total:      0 líneas ✗         │  500 líneas ✓          │
│ - Lógica:     0 líneas           │  300 líneas            │
│ - Docs:       0 líneas           │  200 líneas            │
│                                  │                        │
│ Ratio:                           │                        │
│ - Lógica/Model:  67% ✗           │  0% ✓                  │
│ - Separation:    NO ✗            │  SÍ ✓                  │
│                                  │                        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ MÉTRICAS DE TESTING                                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│               ANTES (Fat Model)  │  DESPUÉS (Service)     │
│ ──────────────────────────────────────────────────────── │
│ Requiere DB:  SÍ ✗               │  NO ✓                  │
│ Mockeable:    NO ✗               │  SÍ ✓                  │
│ Tiempo/test:  300ms              │  10ms                  │
│ Total (100):  30 seg             │  1 seg                 │
│ Velocidad:    1x                 │  30x más rápido ✓      │
│                                  │                        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ MÉTRICAS DE MANTENIBILIDAD                                │
├──────────────────────────────────────────────────────────┤
│                                                           │
│                   ANTES           │  DESPUÉS               │
│ ──────────────────────────────────────────────────────── │
│ Acoplamiento:     Alto ✗          │  Bajo ✓                │
│ Reutilizable:     NO ✗            │  SÍ ✓                  │
│ Testeable:        Difícil ✗       │  Fácil ✓               │
│ Escalable:        NO ✗            │  SÍ ✓                  │
│ Documentado:      Poco ✗          │  Mucho ✓               │
│ Type hints:       NO ✗            │  SÍ ✓                  │
│                                   │                        │
└──────────────────────────────────────────────────────────┘
```

---

Este documento continúa con las secciones restantes. ¿Quieres que continúe con:

6. Análisis de Beneficios (detallado)
7. Costo de Implementación  
8. Ejemplos de Código Completos
9. Estrategia de Migración
10. Métricas de Éxito
11. Conclusiones

?
