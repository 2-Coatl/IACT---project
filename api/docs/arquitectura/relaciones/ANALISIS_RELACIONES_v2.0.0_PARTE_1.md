---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Relaciones entre Apps
categoria: arquitectura/relaciones
tema: Relaciones y flujos de datos - ETL en DB, N Reportes/Dashboards
autor: Claude Technical Analysis
tags: [arquitectura, relaciones, flujo-datos, etl-db, reportes, dashboards]
replaces: ANALISIS_RELACIONES_REPORTS_ACCESS_IVR_PIPELINE_v1.0.0.md
relacionado:
  - FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md (flujo correcto)
  - ANALISIS_APP_PIPELINE_REFACTORING_v2.0.0.md (corregido)
  - ANALISIS_APP_REPORTS_REFACTORING_v2.0.0.md (por crear)
estado: completo-definitivo
partes: 1/6
---

# ANÁLISIS DE RELACIONES v2.0.0 - PARTE 1/6

**Relaciones entre IVR_LEGACY, ETL JOB, PIPELINE, REPORTS, ACCESS**

**🔴 VERSIÓN COMPLETAMENTE NUEVA - Basada en flujo definitivo**

---

## ⚠️ AVISO IMPORTANTE

```
VERSIÓN ANTERIOR (v1.0.0): OBSOLETA - CONTENÍA FLUJO INCORRECTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Flujo: IVR → PIPELINE → CORE → REPORTS
❌ Pipeline ejecutaba ETL en Python
❌ CallRecord en apps/core/
❌ PIPELINE dependía de CORE

ESTA VERSIÓN (v2.0.0): FLUJO CORRECTO DEFINITIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Flujo: IVR → ETL JOB (DB) → default DB → REPORTS + PIPELINE
✅ ETL corre en DB (stored procedure/cron)
✅ Pipeline solo MONITOREA ETL
✅ Reports CONSUME datos + genera Excel/CSV
✅ Access proporciona RBAC
✅ Soporta N reportes/dashboards
```

---

## RESUMEN EJECUTIVO

### Cambios Fundamentales

```
NUEVO FLUJO DE ARQUITECTURA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                    ┌──────────────┐
                    │  IVR_LEGACY  │  MariaDB (origen de datos)
                    │   call_logs  │  Actualización: Real-time
                    └──────┬───────┘
                           │
                           │ ETL JOB (2 AM, día vencido)
                           │ Stored Procedure + Cron
                           │
                           ▼
                    ┌──────────────┐
                    │  DEFAULT DB  │  Postgres/SQLite (Django)
                    │              │
                    │  Tablas ETL: │
                    │  ├─ cmenu_agregado
                    │  ├─ llamadas_diarias
                    │  ├─ dashboard_metricas
                    │  └─ ... (N reportes)
                    │              │
                    │  Tracking:   │
                    │  └─ etlexecution
                    └──────┬───────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
         ┌──────────┐          ┌──────────┐
         │ PIPELINE │          │ REPORTS  │
         │ Monitor  │          │ Consume  │
         │          │          │ Generate │
         └──────────┘          └─────┬────┘
                                     │
                                     │ RBAC
                                     ▼
                              ┌──────────┐
                              │  ACCESS  │
                              │   RBAC   │
                              └──────────┘

COMPONENTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. IVR_LEGACY (MariaDB)
   - Origen de datos RAW
   - Modelo: CallLog (unmanaged, READ-ONLY)
   
2. ETL JOB (Fuera de Django)
   - Stored procedure en DB
   - Cron job 2 AM diario
   - Extract → Transform → Load
   - Escribe en default DB

3. DEFAULT DB (Postgres/SQLite)
   - Datos procesados (N tablas de reportes)
   - Tracking (ETLExecution)
   - Misma DB de Django

4. apps/pipeline/ (Django - MONITORING)
   - Verifica que ETL corrió
   - Dashboard de estado
   - NO ejecuta ETL

5. apps/reports/ (Django - CONSUMPTION)
   - Query datos procesados
   - Genera Excel/CSV/PDF
   - N reportes/dashboards
   - API endpoints

6. apps/access/ (Django - RBAC)
   - Control de permisos
   - user.has_function()
   - Permisos por reporte
```

### Escalabilidad: N Reportes/Dashboards

```
EL SISTEMA SOPORTA N REPORTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REPORTES ACTUALES (ejemplos):
1. Reporte cMenu (agregado por opción de menú)
2. Reporte Llamadas Diarias (métricas diarias)
3. Dashboard Métricas Semanales (tendencias)
4. Reporte por Sucursal (comparativas)
5. Dashboard Tiempo Real (KPIs)
... (se pueden agregar más)

PATRÓN GENERAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para cada reporte:

1. ETL JOB crea tabla agregada
   - Tabla: reporte_{nombre}_agregado
   - Example: reporte_cmenu_agregado
   
2. Django Model (managed=True)
   - apps/reports/models.py
   - class {Nombre}Agregado(models.Model)
   
3. Service para query
   - apps/reports/services.py
   - class {Nombre}ReportService
   
4. Exporter para generar archivo
   - apps/reports/exporters.py
   - Excel/CSV/PDF según necesidad
   
5. ViewSet para API
   - apps/reports/views.py
   - class {Nombre}ReportViewSet
   
6. Permisos RBAC
   - apps/access/ define functions
   - reports.view_{nombre}_report
   - reports.export_{nombre}_report

VENTAJAS:
✅ Patrón repetible
✅ Fácil agregar nuevos reportes
✅ Cada reporte independiente
✅ RBAC granular por reporte
```

---

## TABLA DE CONTENIDOS COMPLETA

```
PARTE 1 (ESTE DOCUMENTO):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Resumen Ejecutivo
2. Tabla de Contenidos
3. Diagrama de Arquitectura General
4. Flujo de Datos End-to-End

PARTE 2:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. Relación 1: IVR_LEGACY → ETL JOB
6. Relación 2: ETL JOB → DEFAULT DB

PARTE 3:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7. Relación 3: DEFAULT DB → PIPELINE (Monitoring)
8. Relación 4: DEFAULT DB → REPORTS (Consumption)

PARTE 4:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9. Relación 5: ACCESS → REPORTS (RBAC)
10. Compliance Standards (CNST)

PARTE 5:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

11. Ejemplos de N Reportes/Dashboards
12. Patrón de Implementación

PARTE 6:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

13. Matriz de Dependencias
14. Puntos de Integración
15. Resumen y Conclusiones
```

---

## 1. DIAGRAMA DE ARQUITECTURA GENERAL

### 1.1 Vista de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA COMPLETA                               │
│                IVR_LEGACY → ETL JOB → DB → PIPELINE + REPORTS               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   1. IVR_LEGACY      │  MariaDB Externo (Legacy System)
│      (MariaDB)       │  
│                      │  Database: ivr_production
│   call_logs table    │  User: ivr_readonly (SELECT only)
│                      │  
│   - call_timestamp   │  Actualizaciones:
│   - telefono         │  - Real-time (cada llamada)
│   - sucursal         │  - Miles de inserts/día
│   - cmenu_option     │  
│   - duration         │  Propósito:
│   - status           │  - Sistema de telefonía (producción)
│   - ...              │  - NO modificar
└──────────┬───────────┘  - Solo lectura
           │
           │ ┌──────────────────────────────────────────────────────┐
           │ │ CNST-003: Acceso READ-ONLY                          │
           │ │ - IVRRouter.db_for_write() → None                   │
           │ │ - Database user: ivr_readonly (GRANT SELECT ONLY)   │
           │ │ - CallLog.Meta.managed = False                      │
           │ └──────────────────────────────────────────────────────┘
           │
           │ Query por ETL JOB (2 AM, día vencido)
           │
           ▼
┌──────────────────────┐
│   2. ETL JOB         │  Proceso FUERA de Django
│   (DB Stored Proc)   │
│                      │  Implementación:
│   Opciones:          │  - Stored Procedure (MySQL/Postgres)
│   A) Stored Proc     │  - Cron job + script Python
│   B) Cron + Script   │  - MySQL Event / pg_cron
│                      │
│   Schedule:          │  Horario:
│   - 2:00 AM diario   │  - Día vencido (procesa datos de ayer)
│   - Automático       │  - Ejemplo: 18/ago 2 AM → procesa 17/ago
│                      │
│   Proceso:           │  Pasos:
│   1. EXTRACT         │  1. Query IVR_LEGACY (SELECT)
│   2. TRANSFORM       │  2. Limpiar, normalizar, agregar
│   3. LOAD            │  3. INSERT en default DB
│   4. REGISTRO        │  4. INSERT en ETLExecution (tracking)
└──────────┬───────────┘
           │
           │ INSERT/UPDATE en default DB
           │
           ▼
┌──────────────────────┐
│   3. DEFAULT DB      │  Postgres/SQLite (Django)
│   (Django managed)   │
│                      │  Database: callcenter_db (ejemplo)
│   Tablas ETL:        │  User: django_app (READ/WRITE)
│   ┌────────────────┐ │
│   │ cmenu_agregado │ │  Datos Procesados:
│   │ llamadas_dia   │ │  - N tablas de reportes
│   │ metricas_sem   │ │  - Datos agregados, limpios
│   │ dashboard_kpi  │ │  - Listos para consumir
│   │ ... (N más)    │ │
│   └────────────────┘ │  Tracking:
│                      │  - ETLExecution (pipeline)
│   Tracking ETL:      │
│   ┌────────────────┐ │  Django Tables:
│   │ etlexecution   │ │  - auth_user, sessions, etc
│   └────────────────┘ │
│                      │  Características:
│   Django Tables:     │  - managed=True (Django crea tablas)
│   - auth_user        │  - Migrations controladas
│   - sessions         │  - ETL solo INSERT/UPDATE datos
│   - ...              │
└──────────┬───────────┘
           │
           │ Django query (SELECT)
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────────┐  ┌────────────┐
│ 4. PIPELINE│  │ 5. REPORTS │  Django Apps
│  (Monitor) │  │  (Consume) │
│            │  │            │
│ Monitoring │  │ Generation │  Pipeline:
│ - Status   │  │ - Query    │  - Verifica ETL corrió
│ - Dashboard│  │ - Excel    │  - Dashboard de estado
│ - Alerts   │  │ - CSV/PDF  │  - Alertas si falla
│            │  │ - API      │
└────────────┘  └─────┬──────┘  Reports:
                      │         - Query datos procesados
                      │         - Genera archivos
                      │         - N reportes/dashboards
                      │         - API endpoints
                      │
                      │ RBAC check
                      │
                      ▼
                ┌────────────┐
                │ 6. ACCESS  │  Django App (RBAC)
                │   (RBAC)   │
                │            │  Control de Permisos:
                │ Permisos:  │  - user.has_function()
                │ - view     │  - Permisos por reporte
                │ - export   │  - Granular por acción
                │ - ...      │
                └────────────┘
```

### 1.2 Separación de Responsabilidades

```
FUERA DE DJANGO (ETL):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Extract de IVR_LEGACY
✅ Transform (limpiar, agregar)
✅ Load en default DB
✅ Scheduling (cron, DB event)

Herramientas:
- MySQL Stored Procedures
- Postgres Functions + pg_cron
- Script Python + cron
- dblink para queries externas


DENTRO DE DJANGO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/pipeline/ (MONITORING):
✅ Verificar que ETL corrió
✅ Dashboard de estado
✅ Tracking (ETLExecution model)
✅ Alertas si falla

apps/reports/ (CONSUMPTION):
✅ Query datos procesados
✅ Generar Excel/CSV/PDF
✅ API endpoints
✅ N reportes/dashboards
✅ Validar disponibilidad de datos

apps/access/ (RBAC):
✅ Control de permisos
✅ user.has_function()
✅ Permisos granulares
```

---

## 2. FLUJO DE DATOS END-TO-END

### 2.1 Timeline Completo

```
DÍA 1: 17 de Agosto 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

00:00 - 23:59  Llamadas entran al Call Center
               │
               ├─ Sistema IVR procesa llamadas
               ├─ Cada llamada → INSERT en IVR_LEGACY.call_logs
               ├─ Campos: timestamp, telefono, sucursal, cmenu, duración
               └─ Total día: ~50,000 llamadas

               IVR_LEGACY acumula datos en tiempo real ✓


DÍA 2: 18 de Agosto 2025 - MADRUGADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

02:00:00       ETL JOB inicia (día vencido - procesa 17/ago)
               │
               ├─ Cron/Scheduler dispara stored procedure
               │
02:00:01       EXTRACT: Query IVR_LEGACY
               │
               SELECT 
                   DATE(call_timestamp) as fecha,
                   sucursal,
                   cmenu_option,
                   COUNT(*) as total_llamadas,
                   ...
               FROM ivr_legacy.call_logs
               WHERE DATE(call_timestamp) = '2025-08-17'
               GROUP BY fecha, sucursal, cmenu_option
               │
               Resultado: ~500 filas agregadas
               │
02:00:05       TRANSFORM: Validar y limpiar
               │
               ├─ Validar campos requeridos
               ├─ Normalizar strings
               ├─ Validar lógica de negocio
               └─ Filter out invalids
               │
               Resultado: ~485 filas válidas
               │
02:00:10       LOAD: INSERT en default DB
               │
               INSERT INTO reporte_cmenu_agregado (
                   fecha, sucursal, cmenu_opcion, total_llamadas
               )
               VALUES (...), (...), ...
               ON CONFLICT (...) DO UPDATE SET ...
               │
02:00:12       REGISTRO: INSERT en ETLExecution
               │
               INSERT INTO pipeline_etlexecution (
                   etl_name='cmenu_diario',
                   fecha_procesada='2025-08-17',
                   status='success',
                   records_processed=485,
                   started_at='2025-08-18 02:00:00',
                   completed_at='2025-08-18 02:00:12'
               )
               │
02:00:15       ETL JOB completo ✓
               │
               Duración: 15 segundos
               Registros procesados: 485
               Status: SUCCESS


02:05:00       Django PIPELINE verifica (opcional)
               │
               ├─ Scheduled task Django (cada hora)
               ├─ ETLMonitoringService.check_etl_status()
               ├─ Query: pipeline_etlexecution
               │   WHERE etl_name='cmenu_diario'
               │   AND fecha_procesada='2025-08-17'
               │
               ├─ Resultado: status='success', 485 records
               │
               └─ Si failed → Enviar alerta a admins


DÍA 2: 18 de Agosto 2025 - MAÑANA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

08:30:00       Usuario Juan llega a la oficina
               │
08:31:00       Abre sistema web → https://callcenter.com
               │
               ├─ Login: juan@company.com
               ├─ Auth token recibido
               └─ Permisos RBAC cargados
               │
08:32:00       Navega a módulo "Reportes"
               │
               Frontend muestra opciones:
               ├─ Reporte cMenu
               ├─ Reporte Llamadas Diarias
               ├─ Dashboard Métricas
               └─ ... otros reportes
               │
08:33:00       Selecciona "Reporte cMenu"
               │
               Formulario:
               ├─ Fecha: [17/08/2025]
               ├─ Sucursal: [Puebla]
               └─ Formato: [Excel]
               │
               Click [Generar Reporte]
               │
08:33:01       POST /api/v1/reports/cmenu/generate/
               │
               Headers:
                 Authorization: Bearer {token}
               
               Body:
               {
                 "fecha_inicio": "2025-08-17",
                 "fecha_fin": "2025-08-17",
                 "sucursal": "puebla",
                 "formato": "excel"
               }
               │
08:33:02       Django CMenuReportViewSet.generate()
               │
               ├─ 1. Validar permisos (RBAC)
               │    user.has_function('reports.view_cmenu_report') ✓
               │
               ├─ 2. Verificar que ETL corrió
               │    ETLMonitoringService.check_etl_status(
               │        'cmenu_diario', '2025-08-17'
               │    )
               │    → status='success' ✓
               │
               ├─ 3. Query datos procesados
               │    queryset = CMenuAgregado.objects.filter(
               │        fecha='2025-08-17',
               │        sucursal='puebla'
               │    )
               │    → 25 filas
               │
               ├─ 4. Generar Excel
               │    ExcelExporter.generate_cmenu_excel(data)
               │    → Reporte_cMenu_170825.xlsx
               │
               └─ 5. Response con file URL
               │
08:33:05       Response HTTP 200 OK
               │
               {
                 "status": "completed",
                 "file_url": "/media/reports/cmenu_puebla_170825.xlsx",
                 "total_records": 25,
                 "total_llamadas": 132473,
                 "etl_info": {
                   "last_run": "2025-08-18T02:00:12Z",
                   "status": "success"
                 }
               }
               │
08:33:06       Frontend muestra link de descarga
               │
               ✅ Reporte generado exitosamente
               [Descargar Excel] ← Click
               │
08:33:10       Juan descarga archivo
               │
               Reporte_cMenu_170825.xlsx
               │
               ├─ Hoja "Puebla"
               ├─ 25 filas de datos
               ├─ Total: 132,473 llamadas
               └─ Formato igual que ejemplo


FLUJO COMPLETO ✓
Total time: 5 segundos (desde request hasta download)
Datos procesados: Noche anterior (ETL)
```

### 2.2 Tipos de Flujos

```
FLUJO TIPO 1: Generación de Reporte On-Demand
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usuario Request
  → REPORTS query datos (ya procesados)
  → Genera Excel/CSV
  → Response con archivo
  
Latencia: ~3-5 segundos
ETL required: Sí (debe haber corrido previamente)


FLUJO TIPO 2: Dashboard en Tiempo Real (KPIs)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usuario Request
  → REPORTS query agregados recientes
  → Calcula KPIs (promedio, total, etc)
  → Response JSON
  
Latencia: <1 segundo
ETL required: Sí (datos hasta última ejecución)
Actualización: Cada 24h (después de ETL 2 AM)


FLUJO TIPO 3: Monitoring de ETL (PIPELINE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Admin Request
  → PIPELINE query ETLExecution
  → Verifica status de últimas ejecuciones
  → Response dashboard
  
Latencia: <1 segundo
ETL required: No (solo lee tracking)
```

---

**FIN DE PARTE 1/6**

Continuará en PARTE 2: Relaciones IVR → ETL JOB → DB

---

**NAVEGACIÓN:**
- ✅ PARTE 1/6 (este documento)
- ⏭️ PARTE 2/6: Relación IVR_LEGACY → ETL JOB → DEFAULT DB
- ⏭️ PARTE 3/6: Relación PIPELINE y REPORTS con DB
- ⏭️ PARTE 4/6: Relación ACCESS (RBAC)
- ⏭️ PARTE 5/6: Ejemplos de N Reportes
- ⏭️ PARTE 6/6: Matriz de dependencias y conclusiones
