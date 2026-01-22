---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Data Storage
categoria: arquitectura/data-storage
tema: CallRecord - ¿Modelo en DB o solo Serializer? Análisis de necesidad
autor: Claude Technical Analysis
tags: [callrecord, etl, analytics, storage, serializer, model]
relacionado:
  - ANALISIS_APP_CORE_REFACTORING_v1.0.0.md
  - ANALISIS_RELACIONES_REPORTS_ACCESS_IVR_PIPELINE_v1.0.0.md
estado: completado
---

# ANÁLISIS: CallRecord - ¿Modelo en DB o solo Serializer?

**Respondiendo: ¿Es necesario guardar datos ETL en la base de datos?**

---

## RESUMEN EJECUTIVO

### Preguntas del Usuario

```
1. CallRecord NO es componente fundamental del framework
   → ¿Debería estar en apps/core/?

2. ETL query tabla en otra DB (IVR_LEGACY MariaDB)
   → ¿Debe guardarse como serializer para view?
   → ¿Es necesario asignarla a un modelo?
   → ¿Si se asigna a modelo, DEBE guardarse en DB?

RESPUESTAS CORTAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. NO, CallRecord NO debería estar en apps/core/
   → Debería estar en apps/analytics/ (nueva) o apps/pipeline/

2. NO es necesario usar modelo, PERO...
   → Sí es necesario guardar en DB (analytics, performance, histórico)

3. Modelo Django NO obliga a guardar en DB
   → Puede query externa sin guardar (via unmanaged models)
   → PERO en este caso, SÍ conviene guardar (razones abajo)
```

---

## TABLA DE CONTENIDOS

1. [CallRecord - Ubicación Correcta](#ubicacion)
2. [¿Modelo vs Serializer? Análisis](#modelo-vs-serializer)
3. [¿Es necesario guardar en DB?](#necesidad-db)
4. [Opciones de Arquitectura](#opciones)
5. [Recomendación Final](#recomendacion)

---

<a name="ubicacion"></a>
## 1. CallRecord - Ubicación Correcta

### 1.1 Estado Actual (Incorrecto)

```python
# apps/core/models.py (UBICACIÓN ACTUAL)

class CallRecord(models.Model):
    """
    Registro de llamada en analytics DB.
    
    PROBLEMA: Esto NO es "framework core"
    """
    fecha = models.DateField()
    telefono = models.CharField(max_length=20)
    servicio_800 = models.CharField(max_length=20)
    total_llamadas = models.IntegerField()
    # ...

ANÁLISIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CallRecord es:
❌ NO es Abstract Model (no se hereda)
❌ NO es Manager/QuerySet personalizado
❌ NO es Mixin para framework
❌ NO es componente fundamental de Django

CallRecord es:
✅ Modelo de NEGOCIO (dominio: llamadas)
✅ Modelo de ANALYTICS (datos procesados)
✅ Storage del ETL Pipeline
✅ Concrete model específico de la app

CONCLUSIÓN:
CallRecord NO debería estar en apps/core/ ❌
```

### 1.2 ¿Qué SÍ debería estar en core/?

```python
# apps/core/base_models.py (LO QUE SÍ VA EN CORE)

class SoftDeleteMixin(models.Model):
    """
    ESTO SÍ es framework core:
    - Abstract Model (se hereda)
    - Extiende comportamiento de Django
    - Componente fundamental reutilizable
    """
    is_deleted = models.BooleanField(default=False)
    
    def delete(self):
        # Override framework behavior
        self.is_deleted = True
        self.save()
    
    class Meta:
        abstract = True  # ← CLAVE: Abstract, no concrete


class SoftDeleteManager(models.Manager):
    """
    ESTO SÍ es framework core:
    - Manager personalizado
    - Extiende ORM de Django
    - Componente fundamental reutilizable
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

ESTOS SON FRAMEWORK CORE ✅
```

### 1.3 Comparación

```
┌────────────────────────────────────────────────────────────┐
│ apps/core/ (Framework components ONLY)                    │
│                                                            │
│ ✅ SoftDeleteMixin (Abstract Model)                        │
│ ✅ SoftDeleteManager (Manager personalizado)              │
│ ✅ ServiceFilterMixin (ViewSet mixin genérico)            │
│ ✅ HasServiceAccess (Permission genérica)                 │
│                                                            │
│ ❌ CallRecord (Concrete model de negocio)                 │
│ ❌ ServiceAccess (Concrete model de negocio)              │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ apps/analytics/ (Nueva app) o apps/pipeline/              │
│                                                            │
│ ✅ CallRecord (Analytics data)                             │
│ ✅ ETLExecution (Pipeline tracking)                        │
│ ✅ Otros modelos de analytics                             │
└────────────────────────────────────────────────────────────┘
```

---

<a name="modelo-vs-serializer"></a>
## 2. ¿Modelo vs Serializer? Análisis

### 2.1 Pregunta: ¿Es necesario asignar a modelo?

**Respuesta corta: NO, no es obligatorio.**

Django te da 3 opciones:

```
OPCIÓN 1: Modelo Managed (guarda en DB)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CallRecord(models.Model):
    fecha = models.DateField()
    # ...
    
    class Meta:
        managed = True  # ← Django crea tabla

Ventajas:
✅ Queries rápidos (indexes)
✅ Histórico persistente
✅ No depende de DB externa
✅ ORM completo

Desventajas:
⚠️ Duplica datos
⚠️ Requiere ETL para mantener sync


OPCIÓN 2: Modelo Unmanaged (query DB externa, NO guarda)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CallLog(models.Model):
    fecha = models.DateField()
    # ...
    
    class Meta:
        managed = False  # ← Django NO crea tabla
        db_table = 'call_logs'  # ← Tabla en DB externa

Ventajas:
✅ No duplica datos
✅ Siempre actualizado (real-time)
✅ ORM de Django funciona

Desventajas:
❌ Queries lentos (DB externa, sin indexes nuestros)
❌ Depende de disponibilidad de DB externa
❌ No podemos modificar schema


OPCIÓN 3: Solo Serializer (sin modelo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CallRecordSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    telefono = serializers.CharField()
    # ...

# Query manual
def get_calls():
    from apps.ivr_legacy.adapters import IVRAdapter
    adapter = IVRAdapter()
    raw_data = adapter.get_calls(...)
    serializer = CallRecordSerializer(data=raw_data, many=True)
    return serializer.data

Ventajas:
✅ No duplica datos
✅ Flexible (no atado a DB)
✅ Puede combinar múltiples sources

Desventajas:
❌ Sin ORM (queries manuales)
❌ Sin validación de DB
❌ Sin histórico persistente
❌ Más código manual
```

### 2.2 Comparación Práctica

```python
# ════════════════════════════════════════════════════════════
# ESCENARIO: REPORTS necesita query llamadas del mes pasado
# ════════════════════════════════════════════════════════════

# OPCIÓN 1: Modelo Managed (ACTUAL)
# ────────────────────────────────────────────────────────────
from apps.core.models import CallRecord

queryset = CallRecord.objects.filter(
    fecha__gte='2024-12-01',
    fecha__lte='2024-12-31'
).values('fecha', 'total_llamadas')

# ✅ Rápido (query local DB con indexes)
# ✅ Simple (ORM)
# ✅ No depende de IVR_LEGACY
# ⚠️ Requiere ETL previo


# OPCIÓN 2: Modelo Unmanaged
# ────────────────────────────────────────────────────────────
from apps.ivr_legacy.models import CallLog

queryset = CallLog.objects.using('ivr_legacy').filter(
    fecha__gte='2024-12-01',
    fecha__lte='2024-12-31'
).values('fecha', 'total_llamadas')

# ⚠️ Lento (query MariaDB externa, sin indexes nuestros)
# ⚠️ Depende de disponibilidad de IVR_LEGACY
# ⚠️ Viola CNST-003 si se hace frecuentemente
# ✅ Siempre actualizado


# OPCIÓN 3: Solo Serializer
# ────────────────────────────────────────────────────────────
from apps.ivr_legacy.adapters import IVRAdapter

adapter = IVRAdapter()
raw_data = adapter.get_calls(
    fecha_inicio='2024-12-01',
    fecha_fin='2024-12-31'
)

serializer = CallRecordSerializer(data=raw_data, many=True)
serializer.is_valid()
data = serializer.data

# ❌ Más código manual
# ❌ Sin ORM (filtros, paginación, etc manual)
# ❌ Sin histórico
# ⚠️ Lento (query MariaDB cada vez)
```

---

<a name="necesidad-db"></a>
## 3. ¿Es necesario guardar en DB?

### 3.1 Análisis de Necesidad

```
PREGUNTA: ¿Por qué CallRecord se guarda en analytics DB?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RAZÓN 1: Performance
────────────────────────────────────────────────────────────

Sin guardar (query IVR cada vez):
- Query a MariaDB externa (latencia red)
- Sin indexes optimizados para REPORTS
- Cada reporte query IVR_LEGACY
- 100 reportes/día = 100 queries a IVR

Con guardar (analytics DB):
- Query local (SQLite/Postgres)
- Indexes optimizados para analytics
- IVR_LEGACY solo 2 queries/día (ETL cada 12h)
- Performance 10-100x mejor

GANANCIA: 10-100x performance ✅


RAZÓN 2: Compliance CNST-003 (READ-ONLY)
────────────────────────────────────────────────────────────

CNST-003: "Mínimo acceso a IVR legacy (READ-ONLY)"

Sin guardar:
- Cada reporte query IVR_LEGACY
- 100 reportes/día = 100 queries
- Alta carga en MariaDB legacy

Con guardar:
- ETL query IVR 2 veces/día (cada 12h)
- 2 queries/día vs 100 queries/día
- Reduce carga 98% en legacy DB

GANANCIA: Cumple CNST-003 mejor ✅


RAZÓN 3: Histórico y Analytics
────────────────────────────────────────────────────────────

Sin guardar:
- IVR_LEGACY puede eliminar datos viejos
- Sin control sobre retención
- Depende de políticas de legacy DB

Con guardar:
- Control total sobre retención de datos
- Histórico garantizado
- Analytics de tendencias (meses/años)

GANANCIA: Control de histórico ✅


RAZÓN 4: Transformación de Datos
────────────────────────────────────────────────────────────

ETL hace Transform:
- Limpia datos inconsistentes
- Normaliza formatos
- Valida lógica de negocio
- Enriquece con metadata

Sin guardar:
- Repetir Transform en cada query
- Inconsistencias si logic cambia
- Más lento

Con guardar:
- Transform 1 vez (en ETL)
- Datos limpios siempre
- Consistente

GANANCIA: Datos limpios y validados ✅


RAZÓN 5: Independencia de IVR_LEGACY
────────────────────────────────────────────────────────────

Sin guardar:
- Si IVR_LEGACY cae → REPORTS no funciona
- Mantenimiento de MariaDB afecta REPORTS
- Acoplamiento fuerte

Con guardar:
- IVR_LEGACY puede estar down
- REPORTS sigue funcionando con datos hasta ETL previo
- Desacoplamiento

GANANCIA: Resiliencia ✅
```

### 3.2 Casos donde NO guardar tendría sentido

```
CASOS DONDE SERIALIZER SIN DB SERÍA VÁLIDO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Datos real-time (dashboard live)
   → Ejemplo: Llamadas activas ahora mismo
   → Query directo tiene sentido

2. Datos que cambian constantemente
   → Ejemplo: Precio de acciones
   → Guardar no tiene valor (obsoleto al instante)

3. Datos de consulta única
   → Ejemplo: Validar DNI en API externa
   → Solo se usa 1 vez, no vale guardar

4. Datos de terceros sin control
   → Ejemplo: Weather API
   → No podemos/queremos guardar

PERO CallRecord NO es ninguno de estos casos ❌
```

### 3.3 Decisión para CallRecord

```
CASO DE USO: CallRecord
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Características:
✅ Datos históricos (no real-time)
✅ Queries frecuentes (reportes diarios)
✅ Analytics complejos (tendencias, agregaciones)
✅ Performance crítica (CNST-007: 100K registros)
✅ IVR_LEGACY es legacy (reducir carga)

DECISIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SÍ, CallRecord DEBE guardarse en analytics DB ✅

Razones:
1. Performance 10-100x mejor
2. Compliance CNST-003 (reduce carga legacy)
3. Histórico controlado
4. Datos transformados y limpios
5. Resiliencia (independiente de IVR)

Por lo tanto:
- Usar Modelo Django (managed=True) ✅
- Guardar en analytics DB (SQLite/Postgres) ✅
- ETL cada 12 horas (CNST-004) ✅
```

---

<a name="opciones"></a>
## 4. Opciones de Arquitectura

### 4.1 Opción A: Crear apps/analytics/ (RECOMENDADA)

```
apps/analytics/ (NUEVA APP)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Analytics y data warehouse
Contiene: Modelos de analytics procesados por ETL

├── models.py
│   ├─ CallRecord (datos de llamadas procesados)
│   ├─ CallMetrics (métricas agregadas)
│   └─ ... otros analytics models
│
├── services.py
│   └─ AnalyticsService (queries complejos)
│
└── migrations/

VENTAJAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Separación clara de concerns
✅ apps/core limpio (solo framework)
✅ Escalable (más analytics models en futuro)
✅ Nombre semántico claro (analytics = datos procesados)

CAMBIOS NECESARIOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Crear apps/analytics/
2. Mover CallRecord de core/ a analytics/
3. Actualizar imports:
   - from apps.core.models import CallRecord
   + from apps.analytics.models import CallRecord

4. Actualizar INSTALLED_APPS:
   + 'apps.analytics',

TIEMPO: ~2 horas
```

### 4.2 Opción B: Mover a apps/pipeline/

```
apps/pipeline/ (YA EXISTE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: ETL processing
Contiene: Models de pipeline + resultados

├── models.py
│   ├─ ETLExecution (tracking de ETL)
│   └─ CallRecord (resultado del ETL) ← MOVER AQUÍ
│
└── ...

VENTAJAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CallRecord es producto del pipeline
✅ No crear nueva app
✅ Menos cambios

DESVENTAJAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Pipeline es sobre PROCESAMIENTO, no sobre STORAGE
⚠️ REPORTS depende de PIPELINE (acoplamiento)
⚠️ Menos escalable (¿otros analytics models dónde van?)

TIEMPO: ~1 hora
```

### 4.3 Opción C: Dejar en apps/core/ (ACTUAL - NO RECOMENDADA)

```
apps/core/ (ESTADO ACTUAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

├── base_models.py (framework - ✅ correcto)
├── models.py (CallRecord + ServiceAccess - ⚠️ mezcla)
└── ...

VENTAJAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ No requiere cambios
✅ Ya funciona

DESVENTAJAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Viola filosofía Django (core = framework, no negocio)
❌ apps/core se convierte en "cajón de sastre"
❌ Confusión semántica (¿qué es core?)
❌ No escalable (¿todos los analytics models en core?)

NO RECOMENDADA ❌
```

---

<a name="recomendacion"></a>
## 5. Recomendación Final

### 5.1 Arquitectura Propuesta

```
SEPARACIÓN CLARA DE RESPONSABILIDADES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/ (Framework components ONLY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Componentes fundamentales del framework
Contiene: Abstract models, Managers, Mixins genéricos

├── base_models.py ✅ NUEVO
│   ├─ SoftDeleteMixin
│   ├─ SoftDeleteManager
│   └─ SoftDeleteQuerySet
│
├── mixins.py ✅ MANTENER
│   └─ ServiceFilterMixin
│
├── permissions.py ✅ MANTENER
│   └─ HasServiceAccess
│
└── services.py ⚠️ REVISAR
    └─ ServiceAccessService (¿debería estar en access/?)


apps/analytics/ (Nueva app) ✅ CREAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Data warehouse y analytics
Contiene: Datos procesados por ETL

├── models.py
│   ├─ CallRecord (← MOVER desde core/)
│   └─ ... otros analytics models
│
├── services.py
│   └─ AnalyticsService (queries complejos)
│
└── serializers.py
    └─ CallRecordSerializer


apps/pipeline/ ✅ MANTENER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: ETL processing
Contiene: Scheduler, ETL logic, tracking

├── models.py
│   └─ ETLExecution (tracking)
│
├── scheduler.py
│   └─ ETLScheduler
│
└── ... (usa apps.analytics.models.CallRecord)


apps/reports/ ✅ MANTENER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Reportes y exportación
Contiene: Report models, export services

Uses: apps.analytics.models.CallRecord
```

### 5.2 Flujo de Datos Actualizado

```
┌──────────────┐
│  IVR_LEGACY  │  MariaDB READ-ONLY
│   call_logs  │
└──────┬───────┘
       │
       │ IVRAdapter.get_calls()
       │
       ▼
┌──────────────┐
│   PIPELINE   │  ETL cada 12h
│  ETLService  │
└──────┬───────┘
       │
       │ CallRecord.objects.update_or_create()
       │
       ▼
┌──────────────┐
│  ANALYTICS   │  Data Warehouse (NEW)
│  CallRecord  │  SQLite/Postgres
└──────┬───────┘
       │
       │ Query + Filter
       │
       ▼
┌──────────────┐
│   REPORTS    │  Generación de reportes
│ ExportService│  CSV/Excel export
└──────────────┘
       │
       │ RBAC permissions
       │
       ▼
┌──────────────┐
│    ACCESS    │  RBAC control
└──────────────┘
```

### 5.3 Respuestas a Preguntas Originales

```
PREGUNTA 1: CallRecord NO es componente fundamental
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CORRECTO. CallRecord es modelo de negocio/analytics
✅ NO debería estar en apps/core/
✅ Debería estar en apps/analytics/ (nueva app)


PREGUNTA 2: ETL query otra DB, ¿debe guardarse como serializer?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ NO necesariamente serializer
✅ SÍ necesita ser modelo para ORM
✅ Serializer es para API representation, no storage


PREGUNTA 3: ¿Es necesario asignar a modelo?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ NO es obligatorio (podría ser solo serializer)
✅ PERO es recomendado para analytics
✅ ORM simplifica queries complejos


PREGUNTA 4: Si se asigna a modelo, ¿DEBE guardarse en DB?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ NO obligatorio (managed=False permite query sin guardar)
✅ PERO para CallRecord SÍ conviene guardar:
   - Performance 10-100x mejor
   - Compliance CNST-003 (reduce carga legacy)
   - Histórico controlado
   - Datos transformados
   - Resiliencia
```

---

## RESUMEN Y PLAN DE ACCIÓN

```
HALLAZGOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ CallRecord NO es framework core (observación correcta)
2. ✅ SÍ necesita guardarse en DB (analytics, performance)
3. ✅ Modelo Django es apropiado (managed=True)
4. ❌ Ubicación actual incorrecta (apps/core/)

SOLUCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PASO 1: Crear apps/analytics/
PASO 2: Mover CallRecord de core/ a analytics/
PASO 3: Actualizar imports (PIPELINE, REPORTS)
PASO 4: Limpiar apps/core/ (solo framework components)

TIEMPO: ~2-3 horas
BENEFICIO: Arquitectura clara y escalable

ESTRUCTURA FINAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/         → Framework components (SoftDeleteMixin, etc)
apps/analytics/    → Data warehouse (CallRecord, metrics)
apps/pipeline/     → ETL processing (scheduler, tracking)
apps/reports/      → Reports generation (uses analytics data)
apps/ivr_legacy/   → Legacy DB adapter (READ-ONLY)

Cada app tiene responsabilidad clara ✅
```

---

**FIN DEL ANÁLISIS**

Documento creado: 2026-01-17  
Pregunta: ¿Modelo vs Serializer? ¿Necesidad de DB?  
Respuesta: Sí necesita modelo y DB (analytics, performance)  
Acción: Mover CallRecord de core/ a analytics/  
Tiempo: 2-3 horas
