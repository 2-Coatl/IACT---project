---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Índice de Actualizaciones - Corrección de Documentos
categoria: arquitectura/actualizaciones
tema: Documentos a actualizar basados en flujo real definitivo
autor: Claude Technical Analysis
tags: [actualizaciones, correcciones, flujo-definitivo, deprecaciones]
relacionado:
  - FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md (flujo correcto)
estado: indice-maestro
---

# ÍNDICE DE ACTUALIZACIONES - Corrección de Análisis Previos

**Basado en flujo definitivo: ETL en DB, Django solo monitorea**

---

## RESUMEN EJECUTIVO

### Cambios Fundamentales

```
ANTES (INCORRECTO):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CallRecord en apps/core/ (managed=True)
2. ETLService en Python ejecuta ETL
3. Pipeline ejecuta ETL cada 12h
4. Datos en DB separada "analytics_db"
5. Flujo: IVR → PIPELINE → CORE → REPORTS

AHORA (CORRECTO):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CallRecord NO existe, datos en CMenuAgregado
2. ETL = JOB en DB (stored procedure/cron)
3. Pipeline solo MONITOREA ETL
4. Datos en default DB (misma de Django)
5. Flujo: IVR → ETL JOB → default DB → REPORTS
```

---

## TABLA DE CONTENIDOS

1. [Documentos a Actualizar](#documentos)
2. [Documentos a Deprecar](#deprecar)
3. [Cambios por Documento](#cambios)
4. [Nuevos Documentos Creados](#nuevos)

---

<a name="documentos"></a>
## 1. DOCUMENTOS A ACTUALIZAR

### 1.1 Prioridad ALTA (Corrección Inmediata)

```
DOCUMENTO 1: ANALISIS_APP_PIPELINE_REFACTORING_v1.0.0.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Estado: ❌ CRÍTICO - Conceptos fundamentales incorrectos
Versión: v1.0.0 → v2.0.0

Errores principales:
1. Dice que ETLService ejecuta ETL en Python
2. Describe ETLService.extract(), transform(), load()
3. APScheduler ejecutando ETL cada 12h
4. Pipeline guarda en CallRecord

Correcciones necesarias:
✅ Pipeline solo MONITOREA ETL
✅ ETL es JOB en DB (fuera de Django)
✅ ETLExecution solo tracking
✅ NO hay ETLService que ejecute

Impacto: ALTO
Usuarios afectados: Desarrolladores de Pipeline/ETL
Prioridad: 🔴 INMEDIATA


DOCUMENTO 2: ANALISIS_RELACIONES_REPORTS_ACCESS_IVR_PIPELINE_v1.0.0.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Estado: ❌ CRÍTICO - Flujo incorrecto
Versión: v1.0.0 → v2.0.0

Errores principales:
1. Flujo: IVR → PIPELINE → CORE → REPORTS
2. Describe PIPELINE procesando datos
3. CallRecord en CORE
4. PIPELINE depende de CORE.CallRecord

Correcciones necesarias:
✅ Flujo: IVR → ETL JOB → default DB → REPORTS
✅ PIPELINE solo monitorea
✅ Sin CallRecord
✅ CMenuAgregado en REPORTS

Impacto: ALTO
Usuarios afectados: Arquitectos del sistema
Prioridad: 🔴 INMEDIATA


DOCUMENTO 3: ANALISIS_APP_CORE_REFACTORING_v1.0.0.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Estado: ⚠️ IMPORTANTE - Models incorrectos
Versión: v1.0.0 → v2.0.0

Errores principales:
1. CallRecord listado en models.py
2. Describe CallRecord como modelo de core
3. Análisis de código incluye CallRecord

Correcciones necesarias:
✅ Remover CallRecord de core
✅ core/ solo framework components
✅ SoftDeleteMixin, Managers, Mixins
✅ NO concrete business models

Impacto: MEDIO
Usuarios afectados: Desarrolladores de core
Prioridad: 🟡 ALTA
```

### 1.2 Prioridad MEDIA (Actualización Recomendada)

```
DOCUMENTO 4: ANALISIS_APP_REPORTS_REFACTORING_v1.0.0.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Estado: ⚠️ Revisar - Puede tener conceptos incorrectos
Versión: v1.0.0 → v2.0.0 (si es necesario)

Posibles errores:
1. Puede mencionar managed=False
2. Puede mencionar analytics_db separada
3. Puede describir query a DB externa

Correcciones si es necesario:
✅ managed=True (Django crea tablas)
✅ default DB (misma de Django)
✅ CMenuAgregado como modelo principal
✅ Verificación de ETL antes de reportes

Impacto: MEDIO
Usuarios afectados: Desarrolladores de reportes
Prioridad: 🟡 MEDIA
```

### 1.3 Prioridad BAJA (Actualización Opcional)

```
DOCUMENTO 5: ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v1.0.0.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Estado: ✅ Probablemente OK
Versión: v1.0.0 (mantener)

Posibles menciones:
⚠️ Puede mencionar CallRecord como ejemplo en core

Correcciones menores si es necesario:
- Remover menciones a CallRecord
- Usar CMenuAgregado como ejemplo si se necesita

Impacto: BAJO
Usuarios afectados: Ninguno crítico
Prioridad: 🟢 BAJA
```

---

<a name="deprecar"></a>
## 2. DOCUMENTOS A DEPRECAR

### 2.1 Obsoleto Completo

```
DOCUMENTO 6: ANALISIS_CALLRECORD_MODELO_VS_SERIALIZER_v1.0.0.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Estado: ❌ OBSOLETO COMPLETO
Acción: DEPRECAR

Razón:
- Todo el documento basado en CallRecord
- CallRecord NO existe en el sistema real
- Supuestos fundamentales incorrectos

Reemplazo:
✅ FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md (ya creado)

Marcar como:
[DEPRECATED] Este documento contiene supuestos incorrectos.
Ver FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md para flujo correcto.
```

---

<a name="cambios"></a>
## 3. CAMBIOS POR DOCUMENTO

### 3.1 ANALISIS_APP_PIPELINE v2.0.0

```
SECCIÓN: Propósito de la App
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANTES:
"Pipeline ejecuta ETL para procesar datos de IVR_LEGACY"

DESPUÉS:
"Pipeline MONITOREA ejecución de ETL (que corre como JOB en DB)"


SECCIÓN: Componentes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REMOVER:
❌ ETLService.extract()
❌ ETLService.transform()
❌ ETLService.load()
❌ ETLScheduler (APScheduler)
❌ IVRAdapter integration

AGREGAR:
✅ ETLMonitoringService.check_etl_status()
✅ ETLMonitoringService.get_latest_processed_date()
✅ ETLMonitoringService.get_etl_dashboard()
✅ ETLExecution model (tracking only)


SECCIÓN: Flujo de Datos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANTES:
IVR → ETLService → CallRecord

DESPUÉS:
ETL JOB (DB) → ETLExecution → Dashboard monitoring


SECCIÓN: Tests
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REMOVER:
❌ Tests de ETLService.extract()
❌ Tests de scheduling

MANTENER/AGREGAR:
✅ Tests de ETLMonitoringService
✅ Tests de verificación de status
✅ Tests de dashboard
```

### 3.2 ANALISIS_RELACIONES v2.0.0

```
SECCIÓN: Flujo de Datos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANTES:
┌──────────┐    ETL     ┌──────────┐   Save    ┌──────────┐
│IVR_LEGACY│ ─────────→ │ PIPELINE │ ────────→ │   CORE   │
│          │            │          │           │CallRecord│
└──────────┘            └──────────┘           └─────┬────┘
                                                     │
                                                     ▼
                                               ┌──────────┐
                                               │ REPORTS  │
                                               └──────────┘

DESPUÉS:
┌──────────┐           ┌──────────┐
│IVR_LEGACY│  ETL JOB  │ DEFAULT  │
│          │ ────────→ │    DB    │
│ MariaDB  │  (2 AM)   │CMenuAgre │
└──────────┘           └─────┬────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
            ┌──────────┐          ┌──────────┐
            │ PIPELINE │          │ REPORTS  │
            │ Monitor  │          │ Consume  │
            └──────────┘          └──────────┘


SECCIÓN: Relación PIPELINE → CORE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REMOVER COMPLETO:
❌ Esta relación no existe
❌ PIPELINE no depende de CORE
❌ CallRecord no existe

NUEVA RELACIÓN:
✅ PIPELINE → default DB (query ETLExecution)
✅ REPORTS → default DB (query CMenuAgregado)
```

### 3.3 ANALISIS_APP_CORE v2.0.0

```
SECCIÓN: Models
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REMOVER:
❌ CallRecord (8,151 bytes) - NO existe
❌ Análisis de CallRecord.Meta
❌ CallRecord fields

CLARIFICAR:
✅ core/ NO tiene concrete business models
✅ core/ solo framework components
✅ ServiceAccess puede estar aquí (es RBAC, no negocio)


SECCIÓN: Propósito
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AGREGAR:
"core/ contiene SOLO componentes de framework:
- Abstract Models (SoftDeleteMixin)
- Custom Managers/QuerySets
- ViewSet/Serializer mixins genéricos
- DRF permissions genéricas

NO contiene:
- Concrete business models
- Domain logic
- App-specific models"
```

---

<a name="nuevos"></a>
## 4. NUEVOS DOCUMENTOS CREADOS

### 4.1 Documentos Correctos (Reemplazan anteriores)

```
1. FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md ✅
   - Flujo completo correcto
   - ETL en DB, Django monitorea
   - Pipeline = monitoring
   - Reports = consumption

2. ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v1.0.0.md ✅
   - SoftDeleteMixin de utils a core
   - Filosofía Django core vs utils
   - Correcto según flujo definitivo

3. FLUJO_REAL_REPORTES_ETL_MYSQL_v2.0.0.md ✅
   - Parcialmente correcto
   - Base para v3.0.0 definitivo
```

---

## 5. PLAN DE ACTUALIZACIÓN

### 5.1 Fase 1: Actualizaciones Críticas (Hoy)

```
1. Crear ANALISIS_APP_PIPELINE_REFACTORING_v2.0.0.md
   - Tiempo: 30 min
   - Prioridad: 🔴 CRÍTICA

2. Crear ANALISIS_RELACIONES_v2.0.0.md
   - Tiempo: 30 min
   - Prioridad: 🔴 CRÍTICA

3. Crear ANALISIS_APP_CORE_REFACTORING_v2.0.0.md
   - Tiempo: 20 min
   - Prioridad: 🟡 ALTA

TOTAL: ~80 minutos
```

### 5.2 Fase 2: Deprecaciones (Hoy)

```
1. Marcar ANALISIS_CALLRECORD_MODELO_VS_SERIALIZER como DEPRECATED
   - Tiempo: 5 min
   - Agregar header [DEPRECATED]

TOTAL: 5 minutos
```

### 5.3 Fase 3: Actualizaciones Menores (Opcional)

```
1. Revisar ANALISIS_APP_REPORTS_REFACTORING_v1.0.0.md
   - Si tiene errores → crear v2.0.0
   - Tiempo: 15-30 min

2. Revisar ANALISIS_CORE_VS_UTILS
   - Remover menciones a CallRecord
   - Tiempo: 10 min

TOTAL: 25-40 minutos
```

---

## 6. CONTROL DE VERSIONES

### 6.1 Convención de Versionado

```
v1.0.0 → Análisis inicial (puede tener errores)
v2.0.0 → Análisis corregido basado en flujo definitivo
v3.0.0 → Análisis definitivo (flujo confirmado)

DEPRECATED → Documento obsoleto, no usar
```

### 6.2 Headers de Documentos

```markdown
---
version: 2.0.0
date: 2026-01-17
status: corregido-flujo-definitivo
replaces: ANALISIS_APP_PIPELINE_REFACTORING_v1.0.0.md
relacionado:
  - FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md (flujo correcto)
---

# ANÁLISIS APP PIPELINE v2.0.0

**ACTUALIZADO: Basado en flujo definitivo (ETL en DB, Django monitorea)**

[v1.0.0 contenía supuestos incorrectos - ver changelog]
```

---

## 7. CHANGELOG

### 7.1 Cambios Fundamentales

```
CAMBIO 1: ETL NO es Python
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

v1.0.0: ETLService ejecuta ETL en Python
v2.0.0: ETL es JOB en DB (stored procedure/cron)

Impacto:
- apps/pipeline/ es MONITORING, no ejecución
- No hay ETLScheduler (APScheduler)
- No hay extract(), transform(), load() en Python


CAMBIO 2: CallRecord NO existe
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

v1.0.0: CallRecord en apps/core/models.py
v2.0.0: CMenuAgregado en apps/reports/models.py

Impacto:
- core/ NO tiene concrete business models
- Datos van directo a tablas de reportes agregados
- No hay paso intermedio de "analytics storage"


CAMBIO 3: Datos en default DB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

v1.0.0: Datos en analytics_db separada
v2.0.0: Datos en default DB (misma de Django)

Impacto:
- managed=True (Django crea tablas)
- No necesita database router para analytics
- ETL JOB escribe en misma DB que Django


CAMBIO 4: Pipeline solo MONITOREA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

v1.0.0: Pipeline EJECUTA ETL
v2.0.0: Pipeline solo VERIFICA que ETL corrió

Impacto:
- ETLExecution solo tracking
- ETLMonitoringService en vez de ETLService
- Dashboard de estado, no ejecución
```

---

## RESUMEN Y PRÓXIMOS PASOS

```
DOCUMENTOS A ACTUALIZAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 CRÍTICO (3 docs):
1. ANALISIS_APP_PIPELINE v1.0.0 → v2.0.0
2. ANALISIS_RELACIONES v1.0.0 → v2.0.0
3. ANALISIS_APP_CORE v1.0.0 → v2.0.0

🟡 IMPORTANTE (1 doc):
4. ANALISIS_CALLRECORD → DEPRECATED

🟢 OPCIONAL (2 docs):
5. ANALISIS_APP_REPORTS (revisar)
6. ANALISIS_CORE_VS_UTILS (revisar)


TIEMPO TOTAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fase 1 (Crítico): ~80 minutos
Fase 2 (Deprecar): ~5 minutos
Fase 3 (Opcional): ~40 minutos

TOTAL: ~2 horas


PRÓXIMO PASO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¿Proceder con actualizaciones?

[ ] Crear los 3 documentos v2.0.0 críticos
[ ] Marcar CALLRECORD como deprecated
[ ] Revisar y actualizar opcionales
```

---

**FIN DEL ÍNDICE DE ACTUALIZACIONES**

Documento creado: 2026-01-17  
Total documentos a actualizar: 6  
Prioridad alta: 3 documentos  
Tiempo estimado: ~2 horas  
Estado: Listo para ejecutar
