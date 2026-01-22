---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Relaciones entre Apps
categoria: arquitectura/relaciones
tema: Relaciones REPORTS ↔ ACCESS ↔ IVR_LEGACY ↔ PIPELINE (v2.0.0)
autor: Claude Technical Analysis
parte: 1/7 - Introducción y Arquitectura General
tags: [relaciones, flujo-datos, etl, reportes, rbac, arquitectura-completa]
replaces: ANALISIS_RELACIONES_REPORTS_ACCESS_IVR_PIPELINE_v1.0.0.md
relacionado:
  - FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md (flujo correcto)
  - ANALISIS_APP_PIPELINE_REFACTORING_v2.0.0.md
  - ANALISIS_APP_REPORTS_REFACTORING_v2.0.0.md
estado: parte-1-de-7
---

# ANÁLISIS DE RELACIONES v2.0.0 - PARTE 1/7

**Introducción y Arquitectura General**

---

## ⚠️ AVISO DE ACTUALIZACIÓN

```
VERSIÓN ANTERIOR (v1.0.0): CONTENÍA FLUJO INCORRECTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Flujo: IVR → PIPELINE → CORE → REPORTS
❌ PIPELINE ejecuta ETL en Python
❌ CallRecord en apps/core/
❌ PIPELINE depende de CORE
❌ Database separada "analytics_db"

ESTA VERSIÓN (v2.0.0): FLUJO CORRECTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Flujo: IVR → ETL JOB → default DB → REPORTS
✅ ETL es JOB en DB (stored procedure/cron)
✅ PIPELINE solo MONITOREA ETL
✅ CMenuAgregado y múltiples reportes en apps/reports/
✅ Misma DB (default) para todo
✅ ACCESS controla permisos RBAC
```

---

## ESTRUCTURA DEL DOCUMENTO (7 PARTES)

```
PARTE 1/7 (ESTE DOCUMENTO):
- Resumen Ejecutivo
- Arquitectura General del Sistema
- Mapa de Relaciones
- Glosario de Términos

PARTE 2/7:
- Relación: IVR_LEGACY → ETL JOB
- Adapter Pattern
- READ-ONLY Enforcement

PARTE 3/7:
- Relación: ETL JOB → DEFAULT DB
- Stored Procedures
- Tablas de Reportes

PARTE 4/7:
- Relación: PIPELINE (Monitoring)
- ETLExecution tracking
- Dashboard de estado

PARTE 5/7:
- Relación: REPORTS (Consumption)
- Múltiples reportes
- Dashboards
- Excel/CSV generation

PARTE 6/7:
- Relación: ACCESS (RBAC)
- Permisos granulares
- User → Function mapping

PARTE 7/7:
- Flujo Completo End-to-End
- Casos de Uso
- Diagramas de Secuencia
- Resumen Final
```

---

## TABLA DE CONTENIDOS (PARTE 1)

1. [Resumen Ejecutivo](#resumen)
2. [Arquitectura General](#arquitectura)
3. [Mapa de Relaciones](#mapa)
4. [Componentes del Sistema](#componentes)
5. [Glosario de Términos](#glosario)

---

<a name="resumen"></a>
## 1. RESUMEN EJECUTIVO

### 1.1 Flujo Real del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│ FLUJO DE DATOS COMPLETO                                     │
└─────────────────────────────────────────────────────────────┘

1. IVR_LEGACY (MariaDB)
   └─ call_logs table (datos RAW de llamadas)
   └─ Actualización: Real-time

         │
         │ ETL JOB (2:00 AM diario, día vencido)
         │ - Stored Procedure en MySQL/Postgres
         │ - O cron job ejecutando script
         │ - Extract → Transform → Load
         ▼

2. DEFAULT DB (Postgres/SQLite)
   └─ MISMA base de datos de Django
   └─ Tablas de reportes agregados:
      ├─ reporte_cmenu_agregado
      ├─ reporte_llamadas_diarias
      ├─ reporte_metricas_semanales
      ├─ dashboard_agentes
      └─ ... (N reportes posibles)
   └─ Tablas de Django:
      ├─ auth_user, sessions, etc
      ├─ pipeline_etlexecution (tracking ETL)
      ├─ reports_report (metadata reportes)
      └─ access_* (RBAC tables)

         │
         ├──────────┬──────────┐
         │          │          │
         ▼          ▼          ▼

3a. PIPELINE      3b. REPORTS    3c. ACCESS
    (Monitoring)      (Consumption)   (RBAC)
    
    - Verifica ETL  - Query datos   - Permisos
    - Dashboard     - Genera Excel  - user.has_function()
    - Alertas       - API endpoints - Profile → Function
```

### 1.2 Apps Involucradas

```
┌────────────────────┬─────────────────────────────────────────┐
│ App                │ Responsabilidad                         │
├────────────────────┼─────────────────────────────────────────┤
│ ivr_legacy/        │ Acceso READ-ONLY a MariaDB legacy       │
│                    │ - CallLog model (unmanaged)             │
│                    │ - IVRAdapter (queries)                  │
│                    │ - IVRRouter (enforcement READ-ONLY)     │
├────────────────────┼─────────────────────────────────────────┤
│ pipeline/          │ MONITOREO de ETL                        │
│                    │ - ETLExecution (tracking)               │
│                    │ - ETLMonitoringService (verificar)      │
│                    │ - Dashboard de estado                   │
├────────────────────┼─────────────────────────────────────────┤
│ reports/           │ CONSUMO de datos + Generación           │
│                    │ - CMenuAgregado, LlamadasDiarias, etc   │
│                    │ - ReportService (query + validation)    │
│                    │ - ExportService (Excel/CSV)             │
│                    │ - DashboardService (métricas)           │
├────────────────────┼─────────────────────────────────────────┤
│ access/            │ RBAC - Control de permisos              │
│                    │ - Profile, Function, ProfileFunction    │
│                    │ - ModuleAccessService                   │
│                    │ - user.has_function()                   │
└────────────────────┴─────────────────────────────────────────┘
```

### 1.3 Características Clave

```
CARACTERÍSTICAS DEL SISTEMA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ETL fuera de Django (JOB en DB)
✅ Django solo consume y monitorea
✅ Múltiples reportes posibles (N reportes)
✅ Dashboards en tiempo real
✅ RBAC granular (por función)
✅ Data isolation por usuario
✅ Export formats: Excel, CSV, PDF
✅ Día vencido (datos del día anterior)
✅ Monitoreo automático de ETL
✅ Alertas si ETL falla

COMPLIANCE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CNST-003: IVR_LEGACY READ-ONLY
✅ CNST-004: ETL programado (NO real-time)
✅ CNST-007: Export límite 100K registros
```

---

<a name="arquitectura"></a>
## 2. ARQUITECTURA GENERAL

### 2.1 Diagrama de Alto Nivel

```
╔══════════════════════════════════════════════════════════════╗
║                    ARQUITECTURA GENERAL                       ║
╚══════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────┐
│ CAPA 1: ORIGEN DE DATOS (Legacy System)                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ IVR_LEGACY (MariaDB)                               │     │
│  │                                                     │     │
│  │ Database: ivr_production                          │     │
│  │ Table: call_logs                                   │     │
│  │ Access: READ-ONLY (CNST-003)                      │     │
│  │                                                     │     │
│  │ Datos:                                             │     │
│  │ - Llamadas en tiempo real                         │     │
│  │ - Sin transformación                               │     │
│  │ - Sin agregación                                   │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Query nocturno (2 AM)
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ CAPA 2: PROCESAMIENTO (ETL - Fuera de Django)               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ ETL JOB (Stored Procedure / Cron)                 │     │
│  │                                                     │     │
│  │ Ejecuta: 2:00 AM (día vencido)                    │     │
│  │ Frecuencia: Diario                                 │     │
│  │                                                     │     │
│  │ Proceso:                                           │     │
│  │ 1. EXTRACT   - Query IVR_LEGACY (ayer)           │     │
│  │ 2. TRANSFORM - Limpiar, normalizar, agregar      │     │
│  │ 3. LOAD      - INSERT en default DB               │     │
│  │ 4. REGISTRO  - ETLExecution (tracking)            │     │
│  │                                                     │     │
│  │ Tecnologías:                                       │     │
│  │ - MySQL Stored Procedures                         │     │
│  │ - Postgres pg_cron                                │     │
│  │ - Python script (externo a Django)                │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ INSERT/UPDATE
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ CAPA 3: ALMACENAMIENTO (Default DB)                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ DEFAULT DB (Postgres / SQLite)                     │     │
│  │                                                     │     │
│  │ TABLAS DE REPORTES (Creadas por Django):          │     │
│  │ ├─ reporte_cmenu_agregado                         │     │
│  │ ├─ reporte_llamadas_diarias                       │     │
│  │ ├─ reporte_metricas_semanales                     │     │
│  │ ├─ reporte_agentes_performance                    │     │
│  │ ├─ dashboard_tiempo_real                          │     │
│  │ └─ ... (N reportes)                               │     │
│  │                                                     │     │
│  │ TABLAS DE DJANGO:                                  │     │
│  │ ├─ auth_user, auth_group, sessions                │     │
│  │ ├─ pipeline_etlexecution (tracking)               │     │
│  │ ├─ reports_report (metadata)                      │     │
│  │ ├─ reports_exportjob (jobs)                       │     │
│  │ └─ access_* (RBAC)                                │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Query + Monitor
                         │
                ┌────────┴────────┬───────────────┐
                │                 │               │
                ▼                 ▼               ▼
┌──────────────────────────────────────────────────────────────┐
│ CAPA 4: APLICACIÓN DJANGO (Consumo y Monitoreo)             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  PIPELINE   │  │   REPORTS   │  │   ACCESS    │         │
│  │  (Monitor)  │  │ (Consumption)│  │   (RBAC)    │         │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤         │
│  │             │  │             │  │             │         │
│  │ • Verifica  │  │ • Query     │  │ • Permisos  │         │
│  │   ETL       │  │   datos     │  │   granular  │         │
│  │ • Dashboard │  │ • Genera    │  │ • Profile → │         │
│  │   estado    │  │   Excel     │  │   Function  │         │
│  │ • Alertas   │  │ • API       │  │ • RBAC      │         │
│  │             │  │ • Dashboard │  │   checks    │         │
│  │             │  │ • Métricas  │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ API Response
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ CAPA 5: PRESENTACIÓN (Frontend / Usuario)                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ USUARIO FINAL                                      │     │
│  │                                                     │     │
│  │ Acciones:                                          │     │
│  │ • Ver dashboard de ETL (PIPELINE)                 │     │
│  │ • Generar reportes (REPORTS)                      │     │
│  │ • Descargar Excel/CSV                             │     │
│  │ • Ver métricas en tiempo real                     │     │
│  │                                                     │     │
│  │ Permisos controlados por ACCESS (RBAC)            │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Separación de Responsabilidades

```
PRINCIPIO: SEPARATION OF CONCERNS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ETL JOB (Fuera de Django):
├─ Extract de IVR_LEGACY
├─ Transform (limpiar, agregar)
├─ Load en default DB
├─ Scheduling (2 AM diario)
└─ Error handling

apps/pipeline/ (Django):
├─ MONITOREAR que ETL corrió
├─ Verificar última ejecución
├─ Dashboard de estado
└─ Alertas si falla

apps/reports/ (Django):
├─ CONSUMIR datos procesados
├─ Query tablas agregadas
├─ Generar Excel/CSV/PDF
├─ API endpoints
├─ Dashboards de métricas
└─ Validar disponibilidad de datos

apps/access/ (Django):
├─ CONTROLAR permisos
├─ RBAC granular
├─ Profile → Function mapping
└─ user.has_function()

apps/ivr_legacy/ (Django):
├─ ACCESO READ-ONLY a legacy
├─ Adapter pattern
└─ Solo queries puntuales (si es necesario)
```

---

<a name="mapa"></a>
## 3. MAPA DE RELACIONES

### 3.1 Matriz de Dependencias

```
MATRIZ DE DEPENDENCIAS ENTRE APPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

              │ IVR_LEGACY │ PIPELINE │ REPORTS │ ACCESS │
──────────────┼────────────┼──────────┼─────────┼────────┤
IVR_LEGACY    │     -      │    X     │    X    │   X    │
PIPELINE      │     X      │    -     │    X    │   ✓    │
REPORTS       │     X      │    ✓     │    -    │   ✓    │
ACCESS        │     X      │    X     │    X    │   -    │

✓ = Depende directamente
X = No depende

INTERPRETACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVR_LEGACY:
  └─ Independiente (no depende de ninguna app)
     Usado por: ETL JOB (fuera de Django)

PIPELINE:
  └─ Depende de: ACCESS (para permisos del dashboard)
     Usado por: REPORTS (para verificar ETL antes de reportes)

REPORTS:
  ├─ Depende de: PIPELINE (verificar ETL), ACCESS (RBAC)
  └─ Usado por: Usuario final

ACCESS:
  └─ Independiente (transversal)
     Usado por: PIPELINE, REPORTS, todas las apps
```

### 3.2 Flujo de Datos

```
FLUJO DE DATOS SIMPLIFICADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVR_LEGACY
    │
    │ (1) ETL JOB query
    │     2:00 AM diario
    │
    ▼
ETL JOB ──────────────────────┐
    │                         │
    │ (2) Extract             │ (4) Registra
    │     Transform           │     ETLExecution
    │     Load                │
    ▼                         ▼
DEFAULT DB ◄──────────────────┘
    │
    ├───────────┬──────────────┐
    │           │              │
    ▼           ▼              ▼
PIPELINE    REPORTS        ACCESS
(Monitor)   (Consume)      (RBAC)
    │           │              │
    │           └──────┬───────┘
    │                  │
    │              (5) Permissions
    │                  │
    └──────────────────┴───────────→ USUARIO
                                     (Dashboard/Excel)
```

### 3.3 Relaciones Detalladas

```
RELACIÓN 1: IVR_LEGACY → ETL JOB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tipo: Data Source
Dirección: Unidireccional (solo lectura)
Acoplamiento: Bajo (vía SQL query)
Compliance: CNST-003 (READ-ONLY)

RELACIÓN 2: ETL JOB → DEFAULT DB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tipo: Data Processing & Storage
Dirección: Unidireccional (solo escritura en tablas reportes)
Acoplamiento: Medio (schema de tablas)
Compliance: CNST-004 (día vencido)

RELACIÓN 3: PIPELINE → DEFAULT DB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tipo: Monitoring (READ-ONLY)
Dirección: Unidireccional (solo lectura ETLExecution)
Acoplamiento: Bajo (solo query tracking)
Propósito: Verificar estado de ETL

RELACIÓN 4: REPORTS → DEFAULT DB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tipo: Data Consumption (READ-ONLY)
Dirección: Unidireccional (solo lectura reportes)
Acoplamiento: Medio (ORM queries)
Compliance: CNST-007 (límite 100K)

RELACIÓN 5: REPORTS → PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tipo: Dependency (verificación)
Dirección: Unidireccional (REPORTS usa PIPELINE)
Acoplamiento: Bajo (interface method)
Propósito: Verificar que ETL corrió antes de generar reporte

RELACIÓN 6: ACCESS → REPORTS/PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tipo: RBAC (Permissions)
Dirección: Transversal (usado por todas las apps)
Acoplamiento: Bajo (user.has_function())
Propósito: Control de acceso granular
```

---

<a name="componentes"></a>
## 4. COMPONENTES DEL SISTEMA

### 4.1 IVR_LEGACY

```python
apps/ivr_legacy/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito:
- Acceso READ-ONLY a base de datos legacy
- Solo queries puntuales si es necesario
- ETL JOB accede directamente (fuera de Django)

Componentes:
├─ models.py
│  └─ CallLog (managed=False, db_table='call_logs')
├─ adapters.py
│  └─ IVRAdapter (queries READ-ONLY)
└─ routers.py
   └─ IVRRouter (enforcement READ-ONLY)

CNST-003 Enforcement:
✅ CallLog.Meta.managed = False
✅ IVRRouter.db_for_write() → None
✅ Database user: ivr_readonly (GRANT SELECT)
```

### 4.2 PIPELINE

```python
apps/pipeline/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito:
- MONITOREAR ejecución de ETL
- Dashboard de estado
- Alertas si falla

Componentes:
├─ models.py
│  └─ ETLExecution (tracking de ejecuciones)
├─ services.py
│  └─ ETLMonitoringService (verificar estado)
├─ views.py
│  └─ ETLMonitoringViewSet (dashboard API)
└─ serializers.py
   └─ ETLExecutionSerializer

NO tiene:
❌ ETLService (ejecución)
❌ Scheduler
❌ Extract/Transform/Load logic
```

### 4.3 REPORTS

```python
apps/reports/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito:
- CONSUMIR datos procesados por ETL
- Generar reportes (Excel, CSV, PDF)
- Dashboards de métricas
- API endpoints

Componentes:
├─ models.py
│  ├─ CMenuAgregado (datos ETL)
│  ├─ LlamadasDiarias (datos ETL)
│  ├─ MetricasSemanales (datos ETL)
│  ├─ AgentesPerformance (datos ETL)
│  ├─ Report (metadata de reportes)
│  └─ ExportJob (jobs de exportación)
│
├─ services.py
│  ├─ CMenuReportService
│  ├─ LlamadasReportService
│  ├─ DashboardService
│  └─ ExportService
│
├─ exporters.py
│  ├─ ExcelExporter
│  ├─ CSVExporter
│  └─ PDFExporter
│
├─ views.py
│  ├─ CMenuReportViewSet
│  ├─ LlamadasReportViewSet
│  └─ DashboardViewSet
│
└─ permissions.py
   ├─ CanViewReports
   ├─ CanCreateReports
   └─ CanExportReports

CNST-007 Enforcement:
✅ ExportService.MAX_EXPORT_SIZE = 100000
✅ Validación en 3 capas
✅ Hard limit en queries
```

### 4.4 ACCESS

```python
apps/access/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito:
- RBAC (Role-Based Access Control)
- Permisos granulares por función
- Profile → Function mapping

Componentes:
├─ models.py
│  ├─ Profile (perfiles de usuario)
│  ├─ Module (módulos del sistema)
│  ├─ Function (funciones disponibles)
│  └─ ProfileFunction (asignación)
│
├─ services.py
│  └─ ModuleAccessService
│
└─ middleware.py
   └─ RBACMiddleware (opcional)

Integración:
✅ user.has_function(function_code)
✅ Usado por todas las apps
✅ Permisos granulares
```

---

<a name="glosario"></a>
## 5. GLOSARIO DE TÉRMINOS

```
TÉRMINOS CLAVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ETL JOB:
  Proceso de Extract-Transform-Load que corre FUERA de Django
  como stored procedure o cron job. Ejecuta a las 2 AM diario.

Day-Behind (Día Vencido):
  Datos procesados corresponden al día anterior. ETL del 18/08
  procesa llamadas del 17/08.

managed=True/False:
  - True: Django gestiona tabla (migrations)
  - False: Tabla existe externamente, Django solo query

READ-ONLY:
  Restricción que impide INSERT/UPDATE/DELETE. Solo SELECT.

RBAC:
  Role-Based Access Control. Sistema de permisos basado en
  funciones asignadas a perfiles de usuario.

Monitoring:
  Verificación de que un proceso (ETL) corrió correctamente.
  NO ejecución del proceso.

Consumption:
  Uso de datos ya procesados para generar reportes, dashboards,
  etc. NO procesamiento de datos RAW.

Aggregate Table:
  Tabla con datos ya agregados (SUM, COUNT, GROUP BY). Ejemplo:
  total_llamadas por día, sucursal, opción de menú.

Dashboard:
  Interfaz que muestra métricas en tiempo real o cercano a
  tiempo real.

CNST-003:
  Constraint de sistema: IVR_LEGACY READ-ONLY. No se permite
  escribir en base de datos legacy.

CNST-004:
  Constraint de sistema: ETL programado (día vencido), NO
  real-time.

CNST-007:
  Constraint de sistema: Máximo 100,000 registros por
  exportación.
```

---

## PRÓXIMA PARTE

```
PARTE 2/7: Relación IVR_LEGACY → ETL JOB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Contenido:
- Arquitectura de IVR_LEGACY
- CallLog model (unmanaged)
- IVRAdapter pattern
- READ-ONLY enforcement (3 capas)
- ETL JOB acceso directo
- Queries de ejemplo
- Compliance CNST-003
```

---

**FIN DE PARTE 1/7**

Documento: ANALISIS_RELACIONES v2.0.0 - PARTE 1/7  
Fecha: 2026-01-17  
Estado: Completo  
Siguiente: PARTE 2/7 - Relación IVR_LEGACY → ETL JOB
