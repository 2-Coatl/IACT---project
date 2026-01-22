---
version: 3.0.0 - DEFINITIVO
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Flujo Real ETL y Reportes
categoria: arquitectura/etl-reportes-definitivo
tema: ETL como JOB en DB (día vencido), Django solo monitorea
autor: Claude Technical Analysis
tags: [etl, mysql-job, django-monitoring, reportes, default-db]
relacionado:
  - FLUJO_REAL_REPORTES_ETL_MYSQL_v2.0.0.md (parcialmente correcto)
  - ANALISIS_APP_PIPELINE_REFACTORING_v1.0.0.md (requiere actualización)
estado: completado-definitivo
---

# FLUJO REAL DEFINITIVO - ETL y Reportes

**Aclaración final: ETL es JOB en DB (noche), Django solo MONITOREA**

---

## RESUMEN EJECUTIVO

### Aclaraciones del Usuario

```
ACLARACIÓN 1:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"El ETL servicio no entra en esta fase"
→ ETL NO es responsabilidad de Django en esta fase

ETL real:
- JOB o cron en base de datos
- Se ejecuta por la noche (día vencido)
- Proceso aparte de Django


ACLARACIÓN 2:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"TODA la transformación se pasa a la base de datos 'default'"
→ Datos transformados van a MISMA DB de Django (SQLite/Postgres)
→ NO a una DB separada "analytics_db"


ACLARACIÓN 3:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Django solo consulta si el JOB se ejecutó correctamente"
→ apps/pipeline/ = MONITOREO del ETL
→ NO ejecuta ETL
→ Solo verifica ejecución


IMPLICACIONES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ETL = MySQL JOB/cron (fuera de Django)
✅ Datos transformados = DB default (misma de Django)
✅ apps/pipeline/ = Monitoring/Tracking
✅ apps/reports/ = Consume datos transformados
✅ Models pueden ser managed=True (en default DB)
```

---

## TABLA DE CONTENIDOS

1. [Flujo Completo del Sistema](#flujo-completo)
2. [Responsabilidades por Componente](#responsabilidades)
3. [Arquitectura Django Correcta](#arquitectura-django)
4. [ETL en Base de Datos](#etl-db)
5. [Apps Django: Pipeline vs Reports](#apps)
6. [Modelos y Database](#modelos)
7. [Ejemplo Completo](#ejemplo)

---

<a name="flujo-completo"></a>
## 1. FLUJO COMPLETO DEL SISTEMA

### 1.1 Diagrama de Arquitectura Real

```
┌─────────────────────────────────────────────────────────────┐
│ 1. IVR_LEGACY (MariaDB)                                    │
│    call_logs - Datos RAW de llamadas                       │
│    Actualización: Real-time (cada llamada)                 │
└────────────┬────────────────────────────────────────────────┘
             │
             │ Query (noche, día vencido)
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ETL JOB (MySQL/Postgres)                                │
│    - Cron job o DB scheduler                               │
│    - Ejecuta stored procedures                             │
│    - Horario: 2:00 AM (día vencido)                        │
│    - Proceso: Extract → Transform → Load                   │
└────────────┬────────────────────────────────────────────────┘
             │
             │ INSERT/UPDATE
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. DEFAULT DB (SQLite/Postgres)                            │
│    MISMA base de datos de Django                           │
│                                                             │
│    Tablas de Django (managed=True):                        │
│    ├─ auth_user                                            │
│    ├─ reports_etlexecution (tracking ETL)                  │
│    └─ ... otras tablas Django                              │
│                                                             │
│    Tablas del ETL (managed=True también):                  │
│    ├─ reporte_cmenu_agregado                               │
│    ├─ reporte_llamadas_diarias                             │
│    └─ ... otras tablas de reportes                         │
└────────────┬────────────────────────────────────────────────┘
             │
             │ Query + Monitoring
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. DJANGO APP                                              │
│                                                             │
│    apps/pipeline/ (MONITORING)                             │
│    ├─ Verifica si ETL corrió                              │
│    ├─ Registra ETLExecution                               │
│    ├─ Dashboard de estado                                 │
│    └─ Alertas si falla                                    │
│                                                             │
│    apps/reports/ (CONSUMPTION)                             │
│    ├─ Query tablas agregadas                              │
│    ├─ Genera Excel/CSV                                    │
│    ├─ API endpoints                                       │
│    └─ RBAC permissions                                    │
└────────────┬────────────────────────────────────────────────┘
             │
             │ API Response
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. USUARIO                                                 │
│    - Juan genera reporte cMenu                            │
│    - Descarga Excel                                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Timeline de Ejecución

```
DÍA 1 (17 de Agosto):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

00:00 - 23:59: Llamadas entran a IVR_LEGACY
              → MariaDB call_logs se va llenando

02:00 AM (DÍA 2 - 18 de Agosto):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ETL JOB ejecuta (día vencido):

02:00:00 - Cron/Scheduler dispara ETL JOB
02:00:01 - EXTRACT: Query IVR_LEGACY (llamadas del 17/08)
02:00:05 - TRANSFORM: Limpia y agrega datos
02:00:10 - LOAD: INSERT en default DB
           → reporte_cmenu_agregado
           → reporte_llamadas_diarias
02:00:15 - ETL completo ✓

02:05:00 - Django PIPELINE verifica
           → Query reporte_cmenu_agregado
           → Verifica última fecha procesada
           → Si fecha = 17/08 → ETL OK ✓
           → Registra ETLExecution (status='success')

08:00 AM:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usuario Juan llega a la oficina:

08:30 - Juan abre sistema
08:31 - Va a módulo Reportes
08:32 - Solicita reporte cMenu del 17/08
08:33 - Django query reporte_cmenu_agregado
        → Datos del 17/08 ya están ahí (ETL corrió a las 2 AM)
08:34 - Genera Excel
08:35 - Juan descarga Reporte_cMenu_170825.xlsx ✓
```

---

<a name="responsabilidades"></a>
## 2. RESPONSABILIDADES POR COMPONENTE

### 2.1 ETL JOB (Fuera de Django)

```sql
-- ════════════════════════════════════════════════════════════
-- STORED PROCEDURE: etl_cmenu_diario
-- Ejecuta: Cron job a las 2:00 AM
-- DB: MySQL o Postgres (donde corre el JOB)
-- ════════════════════════════════════════════════════════════

CREATE PROCEDURE etl_cmenu_diario()
BEGIN
    -- PASO 1: EXTRACT
    -- Query IVR_LEGACY (MariaDB externa)
    
    -- PASO 2: TRANSFORM
    -- Limpia y agrega datos
    
    -- PASO 3: LOAD
    -- INSERT en DEFAULT DB (misma de Django)
    INSERT INTO reporte_cmenu_agregado (
        fecha,
        sucursal,
        cmenu_opcion,
        total_llamadas,
        created_at
    )
    SELECT 
        DATE(c.call_timestamp) as fecha,
        c.sucursal,
        c.cmenu_option,
        COUNT(*) as total_llamadas,
        NOW() as created_at
    FROM ivr_legacy.call_logs c
    WHERE DATE(c.call_timestamp) = CURDATE() - INTERVAL 1 DAY
    GROUP BY 
        DATE(c.call_timestamp),
        c.sucursal,
        c.cmenu_option
    ON DUPLICATE KEY UPDATE
        total_llamadas = VALUES(total_llamadas),
        updated_at = NOW();
    
    -- Registrar ejecución
    INSERT INTO reports_etlexecution (
        etl_name,
        fecha_procesada,
        status,
        records_processed,
        started_at,
        completed_at
    )
    VALUES (
        'cmenu_diario',
        CURDATE() - INTERVAL 1 DAY,
        'success',
        ROW_COUNT(),
        @start_time,
        NOW()
    );
END;

-- Scheduler (cron)
CREATE EVENT etl_cmenu_diario_event
ON SCHEDULE EVERY 1 DAY STARTS '2025-01-01 02:00:00'
DO CALL etl_cmenu_diario();
```

**RESPONSABILIDADES DEL ETL JOB:**

```
✅ Extract de IVR_LEGACY
✅ Transform (limpiar, normalizar)
✅ Load en default DB
✅ Registro de ejecución
✅ Error handling
✅ Scheduling (2 AM diario)

HERRAMIENTAS:
- MySQL Events / Postgres pg_cron
- Stored Procedures
- Triggers
- Cron en servidor DB
```

### 2.2 apps/pipeline/ (Django - MONITORING)

```python
# ════════════════════════════════════════════════════════════
# apps/pipeline/models.py
# ════════════════════════════════════════════════════════════

class ETLExecution(models.Model):
    """
    Tracking de ejecuciones de ETL.
    
    Registrado POR el ETL JOB (no por Django).
    Django solo CONSULTA para monitorear.
    """
    
    etl_name = models.CharField(max_length=100)
    fecha_procesada = models.DateField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('running', 'Running')
        ]
    )
    records_processed = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True)
    
    class Meta:
        managed = True  # ← Django gestiona (en default DB)
        db_table = 'reports_etlexecution'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['etl_name', '-fecha_procesada']),
            models.Index(fields=['status', '-started_at']),
        ]


# ════════════════════════════════════════════════════════════
# apps/pipeline/services.py (MONITORING)
# ════════════════════════════════════════════════════════════

class ETLMonitoringService:
    """
    Servicio para monitorear estado del ETL.
    
    NO ejecuta ETL.
    Solo verifica si corrió correctamente.
    """
    
    @staticmethod
    def check_etl_status(etl_name: str, fecha: date) -> dict:
        """
        Verificar si ETL corrió para una fecha.
        
        Returns:
            {
                'executed': bool,
                'status': str,
                'records_processed': int,
                'last_run': datetime
            }
        """
        try:
            execution = ETLExecution.objects.filter(
                etl_name=etl_name,
                fecha_procesada=fecha
            ).latest('started_at')
            
            return {
                'executed': True,
                'status': execution.status,
                'records_processed': execution.records_processed,
                'last_run': execution.completed_at or execution.started_at
            }
        
        except ETLExecution.DoesNotExist:
            return {
                'executed': False,
                'status': 'not_run',
                'records_processed': 0,
                'last_run': None
            }
    
    @staticmethod
    def get_latest_processed_date(etl_name: str) -> date:
        """Obtener última fecha procesada exitosamente."""
        
        execution = ETLExecution.objects.filter(
            etl_name=etl_name,
            status='success'
        ).first()
        
        return execution.fecha_procesada if execution else None
    
    @staticmethod
    def get_etl_dashboard() -> dict:
        """Dashboard de estado de todos los ETLs."""
        
        etls = ['cmenu_diario', 'llamadas_diarias', 'metricas_semanales']
        
        dashboard = {}
        for etl_name in etls:
            latest = ETLExecution.objects.filter(
                etl_name=etl_name
            ).first()
            
            dashboard[etl_name] = {
                'last_run': latest.completed_at if latest else None,
                'status': latest.status if latest else 'never_run',
                'last_processed_date': latest.fecha_procesada if latest else None
            }
        
        return dashboard


# ════════════════════════════════════════════════════════════
# apps/pipeline/views.py (Dashboard de monitoreo)
# ════════════════════════════════════════════════════════════

class ETLMonitoringViewSet(viewsets.ViewSet):
    """ViewSet para monitorear ETLs."""
    
    permission_classes = [IsAuthenticated, IsSuperuser]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Dashboard de estado de ETLs.
        
        GET /api/v1/pipeline/dashboard/
        """
        dashboard = ETLMonitoringService.get_etl_dashboard()
        return Response(dashboard)
    
    @action(detail=False, methods=['get'])
    def check_status(self, request):
        """
        Verificar estado de un ETL específico.
        
        GET /api/v1/pipeline/check-status/?etl=cmenu_diario&fecha=2025-08-17
        """
        etl_name = request.query_params.get('etl')
        fecha_str = request.query_params.get('fecha')
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        status = ETLMonitoringService.check_etl_status(etl_name, fecha)
        return Response(status)
```

**RESPONSABILIDADES DE apps/pipeline/:**

```
✅ Monitorear estado de ETL
✅ Verificar última ejecución
✅ Dashboard de estado
✅ Alertas si ETL no corrió
✅ Registro de tracking (ETLExecution)

NO hace:
❌ Ejecutar ETL
❌ Extract/Transform/Load
❌ Scheduling
```

### 2.3 apps/reports/ (Django - CONSUMPTION)

```python
# ════════════════════════════════════════════════════════════
# apps/reports/models.py
# ════════════════════════════════════════════════════════════

class CMenuAgregado(models.Model):
    """
    Datos agregados de cMenu (creados por ETL JOB).
    
    Django puede usar managed=True porque:
    - Tabla está en DEFAULT DB (misma de Django)
    - Django crea la tabla con migrations
    - ETL JOB inserta datos (no Django)
    - Django solo lee (query)
    """
    
    fecha = models.DateField(db_index=True)
    sucursal = models.CharField(max_length=50, db_index=True)
    cmenu_opcion = models.CharField(max_length=100, null=True)
    total_llamadas = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True  # ← Django crea tabla (migrations)
        db_table = 'reporte_cmenu_agregado'
        unique_together = [
            ('fecha', 'sucursal', 'cmenu_opcion')
        ]
        ordering = ['-fecha', 'cmenu_opcion']
        indexes = [
            models.Index(fields=['fecha', 'sucursal']),
        ]
    
    def __str__(self):
        return f"{self.fecha} - {self.sucursal} - {self.cmenu_opcion}"


# ════════════════════════════════════════════════════════════
# apps/reports/services.py
# ════════════════════════════════════════════════════════════

class CMenuReportService:
    """Servicio para reportes cMenu."""
    
    @staticmethod
    def get_cmenu_data(fecha_inicio, fecha_fin, sucursal):
        """
        Query datos agregados.
        
        Datos ya están en DB (procesados por ETL).
        Django solo lee.
        """
        queryset = CMenuAgregado.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        )
        
        if sucursal != 'todas':
            queryset = queryset.filter(sucursal=sucursal)
        
        return list(queryset.values(
            'cmenu_opcion',
            'total_llamadas',
            'fecha',
            'sucursal'
        ))
    
    @staticmethod
    def verify_data_availability(fecha: date) -> bool:
        """
        Verificar si datos están disponibles para una fecha.
        
        Útil para validar antes de generar reporte.
        """
        # Verificar si ETL corrió
        from apps.pipeline.services import ETLMonitoringService
        
        etl_status = ETLMonitoringService.check_etl_status(
            'cmenu_diario',
            fecha
        )
        
        if not etl_status['executed'] or etl_status['status'] != 'success':
            return False
        
        # Verificar que datos existan
        exists = CMenuAgregado.objects.filter(fecha=fecha).exists()
        return exists
```

**RESPONSABILIDADES DE apps/reports/:**

```
✅ Query datos agregados
✅ Validar disponibilidad (verificar ETL corrió)
✅ Generar Excel/CSV
✅ API endpoints
✅ RBAC permissions

NO hace:
❌ ETL
❌ INSERT/UPDATE en tablas agregadas
❌ Procesamiento de datos RAW
```

---

<a name="arquitectura-django"></a>
## 3. ARQUITECTURA DJANGO CORRECTA

### 3.1 Estructura de Apps

```
apps/
│
├── core/
│   ├── base_models.py ✅ (SoftDeleteMixin, etc)
│   ├── mixins.py ✅ (ViewSet mixins)
│   └── permissions.py ✅ (DRF permissions)
│
├── pipeline/ (MONITORING del ETL)
│   ├── models.py
│   │   └── ETLExecution (tracking, managed=True)
│   ├── services.py
│   │   └── ETLMonitoringService (verificar estado)
│   ├── views.py
│   │   └── ETLMonitoringViewSet (dashboard API)
│   └── migrations/
│
├── reports/ (CONSUMPTION de datos)
│   ├── models.py
│   │   ├── CMenuAgregado (datos ETL, managed=True)
│   │   ├── LlamadasDiarias (datos ETL, managed=True)
│   │   └── Report, ExportJob (metadata, managed=True)
│   ├── services.py
│   │   ├── CMenuReportService (query + validation)
│   │   └── ExportService (Excel/CSV generation)
│   ├── exporters.py
│   │   └── ExcelExporter (generar archivos)
│   ├── views.py
│   │   └── CMenuReportViewSet (API endpoints)
│   └── migrations/
│
├── ivr_legacy/ (READ-ONLY al legacy)
│   ├── models.py (CallLog unmanaged, managed=False)
│   ├── adapters.py (IVRAdapter para queries)
│   └── routers.py (READ-ONLY enforcement)
│
└── access/ (RBAC)
    └── ... (permisos)
```

### 3.2 Database Configuration

```python
# ════════════════════════════════════════════════════════════
# settings.py
# ════════════════════════════════════════════════════════════

DATABASES = {
    'default': {
        # Base de datos principal de Django
        # AQUÍ van las tablas de:
        # - Django (auth, sessions)
        # - apps/pipeline/ETLExecution
        # - apps/reports/CMenuAgregado (datos del ETL)
        # - apps/reports/Report, ExportJob
        # - apps/users/User, Profile
        # - apps/access/Module, Function
        
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'callcenter_db',
        'USER': 'django_app',
        'PASSWORD': 'xxx',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'ivr_legacy': {
        # Base de datos legacy (READ-ONLY)
        # Solo para consultas puntuales si es necesario
        
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ivr_production',
        'USER': 'ivr_readonly',
        'PASSWORD': 'xxx',
        'HOST': 'mariadb-server',
        'PORT': '3306',
    }
}

# Router para IVR legacy (READ-ONLY)
DATABASE_ROUTERS = ['apps.ivr_legacy.routers.IVRRouter']
```

### 3.3 Migrations

```bash
# ════════════════════════════════════════════════════════════
# Crear migrations para tablas de reportes
# ════════════════════════════════════════════════════════════

# Django CREA las tablas (managed=True)
python manage.py makemigrations pipeline reports

# Genera:
# - pipeline/migrations/0001_initial.py
#   → CREATE TABLE reports_etlexecution
#
# - reports/migrations/0001_initial.py
#   → CREATE TABLE reporte_cmenu_agregado
#   → CREATE TABLE reporte_llamadas_diarias
#   → CREATE TABLE reports_report
#   → CREATE TABLE reports_exportjob

# Aplicar migrations
python manage.py migrate

# Resultado:
# - Tablas creadas en DEFAULT DB
# - ETL JOB puede hacer INSERT/UPDATE
# - Django puede hacer SELECT (query)
```

---

<a name="etl-db"></a>
## 4. ETL EN BASE DE DATOS

### 4.1 Implementación del ETL JOB

```sql
-- ════════════════════════════════════════════════════════════
-- ETL JOB completo para cMenu
-- Ejecuta: Diario a las 2:00 AM
-- ════════════════════════════════════════════════════════════

-- Stored Procedure principal
CREATE OR REPLACE PROCEDURE etl_cmenu_diario()
LANGUAGE plpgsql
AS $$
DECLARE
    v_fecha_proceso DATE;
    v_records_processed INT;
    v_execution_id BIGINT;
    v_start_time TIMESTAMP;
BEGIN
    -- Inicializar
    v_fecha_proceso := CURRENT_DATE - INTERVAL '1 day';
    v_start_time := NOW();
    
    -- Registrar inicio de ejecución
    INSERT INTO reports_etlexecution (
        etl_name,
        fecha_procesada,
        status,
        started_at,
        created_at,
        updated_at
    )
    VALUES (
        'cmenu_diario',
        v_fecha_proceso,
        'running',
        v_start_time,
        NOW(),
        NOW()
    )
    RETURNING id INTO v_execution_id;
    
    -- EXTRACT + TRANSFORM + LOAD
    -- (via dblink o similar para query externa)
    INSERT INTO reporte_cmenu_agregado (
        fecha,
        sucursal,
        cmenu_opcion,
        total_llamadas,
        created_at,
        updated_at
    )
    SELECT 
        DATE(c.call_timestamp) as fecha,
        c.sucursal,
        c.cmenu_option,
        COUNT(*) as total_llamadas,
        NOW(),
        NOW()
    FROM dblink(
        'ivr_legacy_connection',
        'SELECT call_timestamp, sucursal, cmenu_option 
         FROM call_logs 
         WHERE DATE(call_timestamp) = CURRENT_DATE - INTERVAL ''1 day'''
    ) AS c(
        call_timestamp TIMESTAMP,
        sucursal VARCHAR(50),
        cmenu_option VARCHAR(100)
    )
    GROUP BY 
        DATE(c.call_timestamp),
        c.sucursal,
        c.cmenu_option
    ON CONFLICT (fecha, sucursal, cmenu_opcion) 
    DO UPDATE SET
        total_llamadas = EXCLUDED.total_llamadas,
        updated_at = NOW();
    
    GET DIAGNOSTICS v_records_processed = ROW_COUNT;
    
    -- Registrar éxito
    UPDATE reports_etlexecution
    SET 
        status = 'success',
        records_processed = v_records_processed,
        completed_at = NOW(),
        updated_at = NOW()
    WHERE id = v_execution_id;
    
    RAISE NOTICE 'ETL cmenu_diario completed: % records', v_records_processed;

EXCEPTION
    WHEN OTHERS THEN
        -- Registrar error
        UPDATE reports_etlexecution
        SET 
            status = 'failed',
            error_message = SQLERRM,
            completed_at = NOW(),
            updated_at = NOW()
        WHERE id = v_execution_id;
        
        RAISE EXCEPTION 'ETL cmenu_diario failed: %', SQLERRM;
END;
$$;


-- ════════════════════════════════════════════════════════════
-- Scheduler (cron en Postgres)
-- ════════════════════════════════════════════════════════════

-- Usando pg_cron extension
SELECT cron.schedule(
    'etl-cmenu-diario',          -- job name
    '0 2 * * *',                  -- cron: 2:00 AM diario
    'CALL etl_cmenu_diario()'    -- command
);
```

### 4.2 Alternativa: Script Externo

```python
# ════════════════════════════════════════════════════════════
# scripts/etl_cmenu_diario.py
# Ejecutar vía cron externo (fuera de Django)
# ════════════════════════════════════════════════════════════

import psycopg2
from datetime import date, timedelta, datetime

def etl_cmenu_diario():
    """ETL cMenu ejecutado por cron externo."""
    
    fecha_proceso = date.today() - timedelta(days=1)
    
    # Conexiones
    conn_ivr = psycopg2.connect(
        host='mariadb-server',
        database='ivr_production',
        user='ivr_readonly',
        password='xxx'
    )
    
    conn_django = psycopg2.connect(
        host='localhost',
        database='callcenter_db',
        user='etl_user',
        password='xxx'
    )
    
    try:
        # Registrar inicio
        cur_django = conn_django.cursor()
        cur_django.execute("""
            INSERT INTO reports_etlexecution (
                etl_name, fecha_procesada, status, started_at
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, ('cmenu_diario', fecha_proceso, 'running', datetime.now()))
        
        execution_id = cur_django.fetchone()[0]
        conn_django.commit()
        
        # EXTRACT
        cur_ivr = conn_ivr.cursor()
        cur_ivr.execute("""
            SELECT 
                DATE(call_timestamp),
                sucursal,
                cmenu_option,
                COUNT(*)
            FROM call_logs
            WHERE DATE(call_timestamp) = %s
            GROUP BY 1, 2, 3
        """, (fecha_proceso,))
        
        data = cur_ivr.fetchall()
        
        # LOAD
        cur_django.executemany("""
            INSERT INTO reporte_cmenu_agregado (
                fecha, sucursal, cmenu_opcion, total_llamadas
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (fecha, sucursal, cmenu_opcion)
            DO UPDATE SET total_llamadas = EXCLUDED.total_llamadas
        """, data)
        
        records_processed = len(data)
        
        # Registrar éxito
        cur_django.execute("""
            UPDATE reports_etlexecution
            SET status = %s, 
                records_processed = %s,
                completed_at = %s
            WHERE id = %s
        """, ('success', records_processed, datetime.now(), execution_id))
        
        conn_django.commit()
        print(f"ETL completed: {records_processed} records")
    
    except Exception as e:
        # Registrar error
        cur_django.execute("""
            UPDATE reports_etlexecution
            SET status = %s, error_message = %s, completed_at = %s
            WHERE id = %s
        """, ('failed', str(e), datetime.now(), execution_id))
        
        conn_django.commit()
        print(f"ETL failed: {e}")
        raise
    
    finally:
        conn_ivr.close()
        conn_django.close()

if __name__ == '__main__':
    etl_cmenu_diario()


# ════════════════════════════════════════════════════════════
# Crontab (en servidor)
# ════════════════════════════════════════════════════════════

# /etc/crontab o crontab -e
0 2 * * * /usr/bin/python3 /opt/callcenter/scripts/etl_cmenu_diario.py
```

---

<a name="apps"></a>
## 5. APPS DJANGO: PIPELINE vs REPORTS

### 5.1 Separación de Responsabilidades

```
apps/pipeline/ (MONITORING)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Monitorear que ETL corra correctamente

Models:
✅ ETLExecution (tracking de ejecuciones)

Services:
✅ ETLMonitoringService (verificar estado)

Views:
✅ ETLMonitoringViewSet (dashboard, alertas)

NO tiene:
❌ ETLService (no ejecuta ETL)
❌ Scheduler (ETL corre fuera de Django)
❌ Extract/Transform/Load logic


apps/reports/ (CONSUMPTION)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Propósito: Generar reportes basados en datos del ETL

Models:
✅ CMenuAgregado (datos procesados por ETL)
✅ LlamadasDiarias (datos procesados por ETL)
✅ Report, ExportJob (metadata de reportes)

Services:
✅ CMenuReportService (query + validación)
✅ ExportService (generar Excel/CSV)

Views:
✅ CMenuReportViewSet (API endpoints)

Exporters:
✅ ExcelExporter (openpyxl)
✅ CSVExporter

NO tiene:
❌ ETL logic
❌ Procesamiento de datos RAW
❌ INSERT en tablas agregadas
```

---

<a name="modelos"></a>
## 6. MODELOS Y DATABASE

### 6.1 ¿managed=True o managed=False?

```python
# ════════════════════════════════════════════════════════════
# DECISIÓN: managed=True (Django gestiona tablas)
# ════════════════════════════════════════════════════════════

class CMenuAgregado(models.Model):
    """Datos agregados cMenu (creados por ETL JOB)."""
    
    # ... campos
    
    class Meta:
        managed = True  # ← Django crea tabla
        db_table = 'reporte_cmenu_agregado'

RAZÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Tabla está en DEFAULT DB (misma de Django)
✅ Django puede gestionar schema con migrations
✅ ETL JOB solo hace INSERT/UPDATE (no DROP/ALTER)
✅ Si ETL necesita cambios de schema → makemigrations

ALTERNATIVA (managed=False):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usar managed=False SI:
⚠️ Tabla es creada por DBA externo
⚠️ Schema cambia fuera de Django
⚠️ No quieres migrations de Django

Para este proyecto: managed=True es apropiado ✅
```

### 6.2 Permisos de Usuario ETL

```sql
-- ════════════════════════════════════════════════════════════
-- Usuario para ETL JOB
-- ════════════════════════════════════════════════════════════

-- Crear usuario ETL
CREATE USER etl_job_user WITH PASSWORD 'xxx';

-- Permisos necesarios
GRANT SELECT, INSERT, UPDATE ON TABLE reporte_cmenu_agregado TO etl_job_user;
GRANT SELECT, INSERT, UPDATE ON TABLE reporte_llamadas_diarias TO etl_job_user;
GRANT SELECT, INSERT, UPDATE ON TABLE reports_etlexecution TO etl_job_user;
GRANT USAGE, SELECT ON SEQUENCE reports_etlexecution_id_seq TO etl_job_user;

-- NO necesita DELETE ni DROP
-- NO necesita permisos en otras tablas de Django
```

---

<a name="ejemplo"></a>
## 7. EJEMPLO COMPLETO

### 7.1 Flujo de Usuario Juan

```python
# ════════════════════════════════════════════════════════════
# Usuario: Juan
# Acción: Generar reporte cMenu del 17/08/2025
# ════════════════════════════════════════════════════════════

# PASO 1: Request a Django API
# ────────────────────────────────────────────────────────────

POST /api/v1/reports/cmenu/generate/

Headers:
  Authorization: Bearer {token}

Body:
{
  "fecha_inicio": "2025-08-17",
  "fecha_fin": "2025-08-17",
  "sucursal": "puebla",
  "formato": "excel"
}


# PASO 2: Django valida y verifica ETL
# ────────────────────────────────────────────────────────────

# apps/reports/views.py

@action(detail=False, methods=['post'])
def generate(self, request):
    # Validar input
    serializer = CMenuReportRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    fecha = serializer.validated_data['fecha_inicio']
    
    # VERIFICAR QUE ETL CORRIÓ ✅
    from apps.pipeline.services import ETLMonitoringService
    
    etl_status = ETLMonitoringService.check_etl_status(
        'cmenu_diario',
        fecha
    )
    
    if not etl_status['executed']:
        return Response({
            "error": "ETL no ha corrido para esta fecha",
            "fecha": fecha,
            "suggestion": "El ETL corre diariamente a las 2 AM"
        }, status=400)
    
    if etl_status['status'] != 'success':
        return Response({
            "error": "ETL falló para esta fecha",
            "fecha": fecha,
            "etl_status": etl_status
        }, status=400)
    
    # ETL corrió OK → proceder ✅
    
    # Query datos
    data = CMenuReportService.get_cmenu_data(
        fecha_inicio=fecha,
        fecha_fin=fecha,
        sucursal=serializer.validated_data['sucursal']
    )
    
    # Generar Excel
    excel_file = ExcelExporter.generate_cmenu_excel(
        data=data,
        sucursal=serializer.validated_data['sucursal']
    )
    
    return Response({
        "status": "completed",
        "file_url": excel_file,
        "etl_info": etl_status
    })


# PASO 3: Query ejecutado
# ────────────────────────────────────────────────────────────

# SQL generado por Django ORM:
SELECT 
    cmenu_opcion,
    total_llamadas,
    fecha,
    sucursal
FROM reporte_cmenu_agregado
WHERE fecha = '2025-08-17'
AND sucursal = 'puebla'
ORDER BY cmenu_opcion;

# Resultado: 25 filas (datos ya agregados por ETL)


# PASO 4: Excel generado
# ────────────────────────────────────────────────────────────

Reporte_cMenu_170825.xlsx

| cMenu                   | Numero |
|-------------------------|--------|
| NULL                    | 11592  |
| Opción Invalida         | 185    |
| ANI                     | 2181   |
| ...                     | ...    |

Total: 132,473 llamadas
```

---

## RESUMEN Y CONCLUSIONES

```
FLUJO REAL DEFINITIVO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. IVR_LEGACY (MariaDB)
   └─ call_logs (datos RAW)

2. ETL JOB (MySQL/Postgres - fuera de Django)
   └─ Stored procedure o script externo
   └─ Corre 2 AM diario (cron/scheduler)
   └─ Extract → Transform → Load

3. DEFAULT DB (Postgres - misma de Django)
   └─ reporte_cmenu_agregado (managed=True)
   └─ reports_etlexecution (managed=True)

4. Django apps/pipeline/
   └─ MONITOREA que ETL corrió ✅
   └─ NO ejecuta ETL ❌

5. Django apps/reports/
   └─ CONSUME datos agregados ✅
   └─ Genera Excel/CSV ✅
   └─ API endpoints ✅

6. Usuario
   └─ Descarga reporte ✅


DECISIONES CLAVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ETL = JOB en DB (fuera de Django)
✅ Datos en default DB (misma de Django)
✅ Models managed=True (Django crea tablas)
✅ apps/pipeline = Monitoring (no ejecución)
✅ apps/reports = Consumption (query + Excel)

TODO CONECTA ✅
```

---

**FIN DEL ANÁLISIS DEFINITIVO**

Documento creado: 2026-01-17  
Versión: 3.0.0 - DEFINITIVO  
Flujo: ETL en DB (noche) → Django monitorea + consume  
Apps: pipeline=monitoring, reports=consumption  
Database: Default DB (managed=True)
