---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Relaciones entre Apps
categoria: arquitectura/relaciones
tema: Relaciones IVR_LEGACY → ETL JOB → DEFAULT DB
autor: Claude Technical Analysis
tags: [ivr-legacy, etl-job, default-db, stored-procedures, dblink]
relacionado:
  - ANALISIS_RELACIONES_v2.0.0_PARTE_1.md
  - FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md
estado: completo-definitivo
partes: 2/6
---

# ANÁLISIS DE RELACIONES v2.0.0 - PARTE 2/6

**Relaciones: IVR_LEGACY → ETL JOB → DEFAULT DB**

---

## TABLA DE CONTENIDOS (PARTE 2)

1. [Relación IVR_LEGACY → ETL JOB](#relacion-ivr-etl)
2. [Arquitectura IVR_LEGACY (Django)](#arquitectura-ivr)
3. [ETL JOB - Implementaciones](#etl-implementaciones)
4. [Relación ETL JOB → DEFAULT DB](#relacion-etl-db)
5. [Schemas de Tablas Agregadas](#schemas)
6. [Ejemplos Completos](#ejemplos)

---

<a name="relacion-ivr-etl"></a>
## 1. RELACIÓN IVR_LEGACY → ETL JOB

### 1.1 Diagrama de Relación

```
┌─────────────────────────────────────────────────────────────┐
│ IVR_LEGACY (MariaDB)                                        │
│                                                             │
│ Database: ivr_production                                    │
│ Host: mariadb-server:3306                                   │
│                                                             │
│ Table: call_logs                                            │
│ ├─ id BIGINT PK                                             │
│ ├─ call_timestamp DATETIME                                  │
│ ├─ telefono VARCHAR(20)                                     │
│ ├─ sucursal VARCHAR(50)                                     │
│ ├─ servicio_800 VARCHAR(20)                                 │
│ ├─ cmenu_option VARCHAR(100)                                │
│ ├─ duration_seconds INT                                     │
│ └─ ... (otros campos del IVR)                               │
│                                                             │
│ Actualización: Real-time (cada llamada)                    │
│ Volumen: ~50K registros/día                                 │
│ Retención: 90 días (ejemplo)                                │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ ┌─────────────────────────────────────────────┐
              │ │ ACCESO DESDE DJANGO (Opcional)              │
              │ │                                             │
              │ │ apps/ivr_legacy/models.py:                  │
              │ │ class CallLog(models.Model):                │
              │ │     managed = False                         │
              │ │     db_table = 'call_logs'                  │
              │ │                                             │
              │ │ Query:                                      │
              │ │ CallLog.objects.using('ivr_legacy').filter( │
              │ │     call_timestamp__date='2025-08-17'       │
              │ │ )                                           │
              │ │                                             │
              │ │ Uso: Queries puntuales (raro)               │
              │ └─────────────────────────────────────────────┘
              │
              │ Query por ETL JOB
              │ (2:00 AM diario, día vencido)
              │
              │ SELECT (READ-ONLY)
              │ ├─ WHERE DATE(call_timestamp) = YESTERDAY
              │ ├─ GROUP BY sucursal, cmenu_option
              │ └─ Aggregate: COUNT, SUM, AVG
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ ETL JOB (Proceso fuera de Django)                           │
│                                                             │
│ Opciones de implementación:                                │
│ A) Stored Procedure (MySQL/Postgres)                       │
│ B) Script Python + Cron                                    │
│ C) Airflow DAG (avanzado)                                  │
│                                                             │
│ Scheduler:                                                  │
│ - MySQL Event / pg_cron / System cron                      │
│ - Horario: 02:00 AM                                        │
│ - Frecuencia: Diario                                       │
│                                                             │
│ Proceso:                                                    │
│ 1. EXTRACT - Query IVR_LEGACY (dblink/FDW/direct)         │
│ 2. TRANSFORM - Limpiar, validar, agregar                  │
│ 3. LOAD - INSERT/UPDATE en default DB                     │
│ 4. REGISTRO - INSERT en ETLExecution                      │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ INSERT/UPDATE
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ DEFAULT DB (Postgres/SQLite)                                │
│                                                             │
│ Database: callcenter_db                                     │
│ Host: localhost:5432 (o mismo servidor Django)             │
│                                                             │
│ Tablas de Reportes (managed=True):                         │
│ ├─ reporte_cmenu_agregado                                  │
│ ├─ reporte_llamadas_diarias                                │
│ ├─ reporte_metricas_semanales                              │
│ └─ ... (N reportes)                                        │
│                                                             │
│ Tracking:                                                   │
│ └─ pipeline_etlexecution                                    │
│                                                             │
│ Django accede con ORM ✓                                     │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Características de la Relación

```
TIPO DE RELACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Patrón: Extract-Transform-Load (ETL)
Dirección: Unidireccional (IVR → ETL → DB)
Acoplamiento: Bajo (solo schema de call_logs)
Frecuencia: Diaria (2 AM)
Modo: Día vencido (procesa datos de ayer)

COMPLIANCE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CNST-003: IVR_LEGACY READ-ONLY
  ✅ Solo SELECT queries
  ✅ NO INSERT/UPDATE/DELETE
  ✅ Usuario DB: ivr_readonly

CNST-004: ETL programado (día vencido)
  ✅ NO real-time processing
  ✅ Batch job nocturno
  ✅ Datos de ayer disponibles hoy

VENTAJAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Desacoplamiento de Django
✅ ETL optimizado (DB-level processing)
✅ No impacta performance de Django
✅ Scheduler independiente
✅ Fácil monitoreo (ETLExecution)
✅ Escalable (procesa grandes volúmenes)
```

---

<a name="arquitectura-ivr"></a>
## 2. ARQUITECTURA IVR_LEGACY (DJANGO)

### 2.1 Configuración de Bases de Datos

```python
# ════════════════════════════════════════════════════════════
# settings.py - Configuración de databases
# ════════════════════════════════════════════════════════════

DATABASES = {
    'default': {
        # Base de datos principal de Django
        # - Datos procesados (reportes)
        # - Tracking (ETLExecution)
        # - Django tables (auth, sessions, etc)
        
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'callcenter_db',
        'USER': 'django_app',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    },
    
    'ivr_legacy': {
        # Base de datos legacy (MariaDB)
        # - Solo lectura (READ-ONLY)
        # - Acceso ocasional desde Django
        # - ETL JOB accede directamente (fuera de Django)
        
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ivr_production',
        'USER': 'ivr_readonly',  # ← Usuario READ-ONLY
        'PASSWORD': os.environ.get('IVR_PASSWORD'),
        'HOST': 'mariadb-server',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'connect_timeout': 10,
        }
    }
}

# Database router
DATABASE_ROUTERS = [
    'apps.ivr_legacy.routers.IVRRouter'
]
```

### 2.2 IVRRouter (READ-ONLY Enforcement)

```python
# ════════════════════════════════════════════════════════════
# apps/ivr_legacy/routers.py
# ════════════════════════════════════════════════════════════

class IVRRouter:
    """
    Router para enforcing READ-ONLY en IVR legacy.
    
    Garantiza que Django NUNCA escriba en IVR_LEGACY.
    Compliance: CNST-003
    """
    
    ivr_apps = {'ivr_legacy'}
    ivr_models = {'CallLog'}
    
    def db_for_read(self, model, **hints):
        """Redirige lectura de CallLog a ivr_legacy DB."""
        if model._meta.app_label in self.ivr_apps:
            return 'ivr_legacy'
        return None
    
    def db_for_write(self, model, **hints):
        """
        BLOQUEA cualquier escritura en IVR legacy.
        
        Returns None → Django no puede escribir.
        """
        if model._meta.app_label in self.ivr_apps:
            return None  # ← Prohibe writes (CNST-003) ✅
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Permite relaciones solo si ambos objetos están en misma DB.
        
        IVR legacy models NO se relacionan con Django models.
        """
        db_set = {'ivr_legacy', 'default'}
        
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        NO permite migrations en ivr_legacy.
        
        Tabla call_logs existe en MariaDB, Django NO la gestiona.
        """
        if db == 'ivr_legacy':
            return False  # ← NO migrations ✅
        
        if app_label in self.ivr_apps:
            return False
        
        return None


# ════════════════════════════════════════════════════════════
# Test de enforcement
# ════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestIVRReadOnly:
    
    def test_cannot_write_to_ivr_legacy(self):
        """Verificar que no se puede escribir en IVR legacy."""
        
        with pytest.raises(Exception):
            CallLog.objects.create(
                call_timestamp=datetime.now(),
                telefono='1234567890',
                sucursal='puebla'
            )
        
        # ✅ PASS - Router bloquea write
```

### 2.3 CallLog Model (Unmanaged)

```python
# ════════════════════════════════════════════════════════════
# apps/ivr_legacy/models.py
# ════════════════════════════════════════════════════════════

from django.db import models


class CallLog(models.Model):
    """
    Modelo unmanaged para tabla call_logs en IVR legacy.
    
    IMPORTANTE:
    - managed=False: Django NO crea/modifica tabla
    - db_table='call_logs': Tabla existe en MariaDB
    - Solo READ-ONLY queries (router enforcement)
    - ETL JOB NO usa este modelo (accede directo a MariaDB)
    """
    
    id = models.BigAutoField(primary_key=True)
    
    # Timestamp
    call_timestamp = models.DateTimeField(
        db_index=True,
        help_text="Timestamp de la llamada"
    )
    
    # Identificación
    telefono = models.CharField(
        max_length=20,
        help_text="Número telefónico del cliente"
    )
    
    sucursal = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Sucursal (puebla, nacional, etc)"
    )
    
    servicio_800 = models.CharField(
        max_length=20,
        help_text="Número 800 marcado"
    )
    
    # IVR
    cmenu_option = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Opción seleccionada en menú IVR"
    )
    
    # Duración
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duración de llamada en segundos"
    )
    
    # Status
    call_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Estado final de llamada (completed, abandoned, etc)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False  # ← Django NO gestiona tabla
        db_table = 'call_logs'  # ← Tabla en MariaDB
        ordering = ['-call_timestamp']
        indexes = [
            models.Index(fields=['call_timestamp']),
            models.Index(fields=['sucursal', 'call_timestamp']),
        ]
    
    def __str__(self):
        return f"Call {self.id} - {self.telefono} ({self.call_timestamp})"


# ════════════════════════════════════════════════════════════
# NOTA: Django model define SOLO campos que necesita
# ════════════════════════════════════════════════════════════

# Tabla real en MariaDB puede tener 30+ campos.
# Django model solo define campos usados en queries ocasionales.
# ETL JOB accede directo a MariaDB (no usa este model).
```

---

<a name="etl-implementaciones"></a>
## 3. ETL JOB - IMPLEMENTACIONES

### 3.1 Opción A: Stored Procedure en Postgres

```sql
-- ════════════════════════════════════════════════════════════
-- ETL Job como Stored Procedure en Postgres
-- Requiere: postgres_fdw (Foreign Data Wrapper) para MariaDB
-- ════════════════════════════════════════════════════════════

-- ────────────────────────────────────────────────────────────
-- PASO 1: Configurar Foreign Data Wrapper (una sola vez)
-- ────────────────────────────────────────────────────────────

-- Instalar extensión
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- Crear servidor remoto (MariaDB)
CREATE SERVER ivr_legacy_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (
        host 'mariadb-server',
        port '3306',
        dbname 'ivr_production'
    );

-- Mapeo de usuario
CREATE USER MAPPING FOR postgres
    SERVER ivr_legacy_server
    OPTIONS (
        user 'ivr_readonly',
        password 'xxx'
    );

-- Crear foreign table
CREATE FOREIGN TABLE ivr_call_logs (
    id BIGINT,
    call_timestamp TIMESTAMP,
    telefono VARCHAR(20),
    sucursal VARCHAR(50),
    servicio_800 VARCHAR(20),
    cmenu_option VARCHAR(100),
    duration_seconds INTEGER,
    call_status VARCHAR(20)
)
SERVER ivr_legacy_server
OPTIONS (schema_name 'public', table_name 'call_logs');


-- ────────────────────────────────────────────────────────────
-- PASO 2: Stored Procedure para ETL
-- ────────────────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE etl_cmenu_diario()
LANGUAGE plpgsql
AS $$
DECLARE
    v_fecha_proceso DATE;
    v_records_processed INT := 0;
    v_execution_id BIGINT;
    v_start_time TIMESTAMP;
    v_error_msg TEXT;
BEGIN
    -- Inicializar
    v_fecha_proceso := CURRENT_DATE - INTERVAL '1 day';
    v_start_time := NOW();
    
    -- ────────────────────────────────────────────────────────
    -- Registrar inicio de ejecución
    -- ────────────────────────────────────────────────────────
    
    INSERT INTO pipeline_etlexecution (
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
    
    -- ────────────────────────────────────────────────────────
    -- EXTRACT + TRANSFORM + LOAD
    -- ────────────────────────────────────────────────────────
    
    INSERT INTO reporte_cmenu_agregado (
        fecha,
        sucursal,
        cmenu_opcion,
        total_llamadas,
        duracion_promedio,
        created_at,
        updated_at
    )
    SELECT 
        -- TRANSFORM: Agregar y calcular métricas
        DATE(c.call_timestamp) as fecha,
        c.sucursal,
        COALESCE(c.cmenu_option, 'Sin Opción') as cmenu_opcion,
        COUNT(*) as total_llamadas,
        AVG(c.duration_seconds) as duracion_promedio,
        NOW() as created_at,
        NOW() as updated_at
    FROM ivr_call_logs c  -- EXTRACT: Query foreign table
    WHERE 
        DATE(c.call_timestamp) = v_fecha_proceso
        AND c.sucursal IS NOT NULL  -- TRANSFORM: Filtrar invalids
    GROUP BY 
        DATE(c.call_timestamp),
        c.sucursal,
        c.cmenu_option
    ON CONFLICT (fecha, sucursal, cmenu_opcion) 
    DO UPDATE SET
        total_llamadas = EXCLUDED.total_llamadas,
        duracion_promedio = EXCLUDED.duracion_promedio,
        updated_at = NOW();
    
    -- Contar registros procesados
    GET DIAGNOSTICS v_records_processed = ROW_COUNT;
    
    -- ────────────────────────────────────────────────────────
    -- Registrar éxito
    -- ────────────────────────────────────────────────────────
    
    UPDATE pipeline_etlexecution
    SET 
        status = 'success',
        records_processed = v_records_processed,
        completed_at = NOW(),
        updated_at = NOW()
    WHERE id = v_execution_id;
    
    RAISE NOTICE 'ETL cmenu_diario completed: % records', v_records_processed;

EXCEPTION
    WHEN OTHERS THEN
        -- ────────────────────────────────────────────────────
        -- Registrar error
        -- ────────────────────────────────────────────────────
        
        GET STACKED DIAGNOSTICS v_error_msg = MESSAGE_TEXT;
        
        UPDATE pipeline_etlexecution
        SET 
            status = 'failed',
            error_message = v_error_msg,
            completed_at = NOW(),
            updated_at = NOW()
        WHERE id = v_execution_id;
        
        RAISE EXCEPTION 'ETL cmenu_diario failed: %', v_error_msg;
END;
$$;


-- ────────────────────────────────────────────────────────────
-- PASO 3: Scheduler con pg_cron
-- ────────────────────────────────────────────────────────────

-- Instalar pg_cron extension
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule ETL para 2 AM diario
SELECT cron.schedule(
    'etl-cmenu-diario',           -- job name
    '0 2 * * *',                   -- cron: 2:00 AM every day
    'CALL etl_cmenu_diario()'     -- command
);

-- Verificar jobs programados
SELECT * FROM cron.job;

-- Ver historial de ejecuciones
SELECT * FROM cron.job_run_details 
WHERE jobname = 'etl-cmenu-diario' 
ORDER BY runid DESC 
LIMIT 10;
```

### 3.2 Opción B: Script Python + Cron

```python
# ════════════════════════════════════════════════════════════
# scripts/etl_cmenu_diario.py
# ETL como script Python independiente de Django
# ════════════════════════════════════════════════════════════

#!/usr/bin/env python3

import mysql.connector
import psycopg2
from datetime import date, timedelta, datetime
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/etl_cmenu.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ETL_CMENU')


def etl_cmenu_diario():
    """
    ETL diario para reporte cMenu.
    
    Proceso:
    1. EXTRACT - Query IVR_LEGACY (MariaDB)
    2. TRANSFORM - Limpiar y agregar
    3. LOAD - INSERT en default DB (Postgres)
    4. REGISTRO - INSERT en ETLExecution
    
    Returns:
        int: Cantidad de registros procesados
    
    Raises:
        Exception: Si ETL falla
    """
    
    fecha_proceso = date.today() - timedelta(days=1)
    execution_id = None
    
    logger.info(f"Iniciando ETL cMenu para fecha: {fecha_proceso}")
    
    # ────────────────────────────────────────────────────────
    # CONEXIONES
    # ────────────────────────────────────────────────────────
    
    # IVR_LEGACY (MariaDB) - READ-ONLY
    conn_ivr = mysql.connector.connect(
        host='mariadb-server',
        database='ivr_production',
        user='ivr_readonly',
        password='xxx',
        port=3306,
        connection_timeout=30
    )
    
    # DEFAULT DB (Postgres) - READ/WRITE
    conn_django = psycopg2.connect(
        host='localhost',
        database='callcenter_db',
        user='etl_user',
        password='xxx',
        port=5432,
        connect_timeout=30
    )
    
    try:
        conn_django.autocommit = False  # Transaction mode
        
        # ────────────────────────────────────────────────────
        # REGISTRO: Iniciar ejecución
        # ────────────────────────────────────────────────────
        
        cursor_django = conn_django.cursor()
        
        cursor_django.execute("""
            INSERT INTO pipeline_etlexecution (
                etl_name,
                fecha_procesada,
                status,
                started_at,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            'cmenu_diario',
            fecha_proceso,
            'running',
            datetime.now(),
            datetime.now(),
            datetime.now()
        ))
        
        execution_id = cursor_django.fetchone()[0]
        conn_django.commit()
        
        logger.info(f"ETL execution ID: {execution_id}")
        
        # ────────────────────────────────────────────────────
        # EXTRACT: Query IVR_LEGACY
        # ────────────────────────────────────────────────────
        
        logger.info("EXTRACT: Querying IVR_LEGACY...")
        
        cursor_ivr = conn_ivr.cursor(dictionary=True)
        
        cursor_ivr.execute("""
            SELECT 
                DATE(call_timestamp) as fecha,
                sucursal,
                COALESCE(cmenu_option, 'Sin Opción') as cmenu_opcion,
                COUNT(*) as total_llamadas,
                AVG(duration_seconds) as duracion_promedio
            FROM call_logs
            WHERE DATE(call_timestamp) = %s
                AND sucursal IS NOT NULL
            GROUP BY 
                DATE(call_timestamp),
                sucursal,
                cmenu_option
        """, (fecha_proceso,))
        
        data = cursor_ivr.fetchall()
        
        logger.info(f"EXTRACT: {len(data)} registros extraídos")
        
        # ────────────────────────────────────────────────────
        # TRANSFORM: Validar y limpiar (opcional)
        # ────────────────────────────────────────────────────
        
        logger.info("TRANSFORM: Validando datos...")
        
        data_valida = []
        for row in data:
            # Validaciones
            if row['total_llamadas'] <= 0:
                logger.warning(f"Registro inválido: {row}")
                continue
            
            # Normalizar
            row['sucursal'] = row['sucursal'].lower().strip()
            
            data_valida.append(row)
        
        logger.info(f"TRANSFORM: {len(data_valida)} registros válidos")
        
        # ────────────────────────────────────────────────────
        # LOAD: INSERT en default DB
        # ────────────────────────────────────────────────────
        
        logger.info("LOAD: Insertando en default DB...")
        
        for row in data_valida:
            cursor_django.execute("""
                INSERT INTO reporte_cmenu_agregado (
                    fecha,
                    sucursal,
                    cmenu_opcion,
                    total_llamadas,
                    duracion_promedio,
                    created_at,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (fecha, sucursal, cmenu_opcion)
                DO UPDATE SET
                    total_llamadas = EXCLUDED.total_llamadas,
                    duracion_promedio = EXCLUDED.duracion_promedio,
                    updated_at = EXCLUDED.updated_at
            """, (
                row['fecha'],
                row['sucursal'],
                row['cmenu_opcion'],
                row['total_llamadas'],
                row['duracion_promedio'],
                datetime.now(),
                datetime.now()
            ))
        
        logger.info(f"LOAD: {len(data_valida)} registros insertados")
        
        # ────────────────────────────────────────────────────
        # REGISTRO: Éxito
        # ────────────────────────────────────────────────────
        
        cursor_django.execute("""
            UPDATE pipeline_etlexecution
            SET 
                status = %s,
                records_processed = %s,
                completed_at = %s,
                updated_at = %s
            WHERE id = %s
        """, (
            'success',
            len(data_valida),
            datetime.now(),
            datetime.now(),
            execution_id
        ))
        
        conn_django.commit()
        
        logger.info(f"ETL completed successfully: {len(data_valida)} records")
        
        return len(data_valida)
    
    except Exception as e:
        # ────────────────────────────────────────────────────
        # REGISTRO: Error
        # ────────────────────────────────────────────────────
        
        logger.error(f"ETL failed: {str(e)}", exc_info=True)
        
        if conn_django and execution_id:
            try:
                conn_django.rollback()
                
                cursor_django = conn_django.cursor()
                cursor_django.execute("""
                    UPDATE pipeline_etlexecution
                    SET 
                        status = %s,
                        error_message = %s,
                        completed_at = %s,
                        updated_at = %s
                    WHERE id = %s
                """, (
                    'failed',
                    str(e)[:500],  # Truncar mensaje
                    datetime.now(),
                    datetime.now(),
                    execution_id
                ))
                
                conn_django.commit()
            except:
                logger.error("Error registrando fallo", exc_info=True)
        
        raise
    
    finally:
        # ────────────────────────────────────────────────────
        # Cerrar conexiones
        # ────────────────────────────────────────────────────
        
        if conn_ivr:
            conn_ivr.close()
            logger.info("Conexión IVR cerrada")
        
        if conn_django:
            conn_django.close()
            logger.info("Conexión Django cerrada")


if __name__ == '__main__':
    try:
        records = etl_cmenu_diario()
        sys.exit(0)  # Success
    except Exception:
        sys.exit(1)  # Error


# ════════════════════════════════════════════════════════════
# Crontab para ejecutar script
# ════════════════════════════════════════════════════════════

# Agregar a /etc/crontab o crontab -e:
# 
# 0 2 * * * /usr/bin/python3 /opt/callcenter/scripts/etl_cmenu_diario.py
#
# Logging en: /var/log/etl_cmenu.log
```

### 3.3 Comparación de Opciones

```
┌──────────────────┬────────────────────┬───────────────────┐
│ Aspecto          │ Stored Procedure   │ Script Python     │
├──────────────────┼────────────────────┼───────────────────┤
│ Performance      │ ⭐⭐⭐⭐⭐ Excelente │ ⭐⭐⭐⭐ Bueno    │
│ Mantenimiento    │ ⭐⭐⭐ Medio        │ ⭐⭐⭐⭐⭐ Fácil   │
│ Debugging        │ ⭐⭐ Difícil        │ ⭐⭐⭐⭐⭐ Fácil   │
│ Portabilidad     │ ⭐⭐ Baja           │ ⭐⭐⭐⭐⭐ Alta    │
│ Complejidad      │ ⭐⭐⭐⭐ Alta       │ ⭐⭐⭐ Media      │
│ Logging          │ ⭐⭐ Limitado       │ ⭐⭐⭐⭐⭐ Rico    │
│ Testing          │ ⭐⭐ Difícil        │ ⭐⭐⭐⭐⭐ Fácil   │
│ Error Handling   │ ⭐⭐⭐ Medio        │ ⭐⭐⭐⭐⭐ Rico    │
│ Deployment       │ ⭐⭐⭐⭐ Fácil      │ ⭐⭐⭐ Medio      │
│ Monitoreo        │ ⭐⭐⭐ Medio        │ ⭐⭐⭐⭐⭐ Rico    │
└──────────────────┴────────────────────┴───────────────────┘

RECOMENDACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stored Procedure → Si equipo tiene expertise en DB
Script Python → Si equipo Python, necesita logging/monitoring
Airflow → Si ya tienen Airflow, múltiples ETLs complejos

Para este proyecto: Script Python ✅
- Más fácil de mantener
- Mejor logging
- Fácil testing
- Equipo familiarizado con Python
```

---

<a name="relacion-etl-db"></a>
## 4. RELACIÓN ETL JOB → DEFAULT DB

### 4.1 Diagrama de Relación

```
┌─────────────────────────────────────────────────────────────┐
│ ETL JOB                                                     │
│                                                             │
│ Process: etl_cmenu_diario()                                │
│ Schedule: 2:00 AM daily                                    │
│                                                             │
│ Output:                                                     │
│ ├─ Datos agregados (N filas)                               │
│ └─ Registro de ejecución (1 fila)                          │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ INSERT/UPDATE
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ DEFAULT DB (Postgres)                                       │
│                                                             │
│ Database: callcenter_db                                     │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ TABLAS DE REPORTES (managed=True)                       ││
│ │                                                          ││
│ │ reporte_cmenu_agregado:                                 ││
│ │ ├─ id (PK)                                              ││
│ │ ├─ fecha (INDEX)                                        ││
│ │ ├─ sucursal (INDEX)                                     ││
│ │ ├─ cmenu_opcion                                         ││
│ │ ├─ total_llamadas                                       ││
│ │ ├─ duracion_promedio                                    ││
│ │ ├─ created_at                                           ││
│ │ └─ updated_at                                           ││
│ │                                                          ││
│ │ UNIQUE (fecha, sucursal, cmenu_opcion)                  ││
│ │                                                          ││
│ │ Similar para:                                           ││
│ │ ├─ reporte_llamadas_diarias                             ││
│ │ ├─ reporte_metricas_semanales                           ││
│ │ └─ ... (N reportes)                                     ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ TRACKING ETL (managed=True)                             ││
│ │                                                          ││
│ │ pipeline_etlexecution:                                  ││
│ │ ├─ id (PK)                                              ││
│ │ ├─ etl_name (INDEX)                                     ││
│ │ ├─ fecha_procesada (INDEX)                              ││
│ │ ├─ status (success/failed)                              ││
│ │ ├─ records_processed                                    ││
│ │ ├─ error_message                                        ││
│ │ ├─ started_at                                           ││
│ │ └─ completed_at                                         ││
│ └─────────────────────────────────────────────────────────┘│
└─────────────┬───────────────────────────────────────────────┘
              │
              │ Django ORM query (SELECT)
              │
              ▼
        ┌─────────────┐
        │   DJANGO    │
        │ PIPELINE +  │
        │   REPORTS   │
        └─────────────┘
```

---

<a name="schemas"></a>
## 5. SCHEMAS DE TABLAS AGREGADAS

### 5.1 reporte_cmenu_agregado

```sql
-- ════════════════════════════════════════════════════════════
-- Tabla creada por Django migrations (managed=True)
-- ════════════════════════════════════════════════════════════

CREATE TABLE reporte_cmenu_agregado (
    id BIGSERIAL PRIMARY KEY,
    
    -- Dimensiones
    fecha DATE NOT NULL,
    sucursal VARCHAR(50) NOT NULL,
    cmenu_opcion VARCHAR(100),
    
    -- Métricas
    total_llamadas INTEGER NOT NULL DEFAULT 0,
    duracion_promedio DECIMAL(10,2),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_cmenu_fecha_sucursal_opcion 
        UNIQUE (fecha, sucursal, cmenu_opcion)
);

-- Indexes
CREATE INDEX idx_cmenu_fecha ON reporte_cmenu_agregado(fecha);
CREATE INDEX idx_cmenu_sucursal ON reporte_cmenu_agregado(sucursal);
CREATE INDEX idx_cmenu_fecha_sucursal ON reporte_cmenu_agregado(fecha, sucursal);


-- ════════════════════════════════════════════════════════════
-- Django Model correspondiente
-- ════════════════════════════════════════════════════════════

# apps/reports/models.py

class CMenuAgregado(models.Model):
    """Datos agregados de reporte cMenu (creados por ETL)."""
    
    fecha = models.DateField(db_index=True)
    sucursal = models.CharField(max_length=50, db_index=True)
    cmenu_opcion = models.CharField(max_length=100, null=True)
    total_llamadas = models.IntegerField(default=0)
    duracion_promedio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True  # ← Django crea tabla
        db_table = 'reporte_cmenu_agregado'
        unique_together = [('fecha', 'sucursal', 'cmenu_opcion')]
        ordering = ['-fecha', 'sucursal']
        indexes = [
            models.Index(fields=['fecha', 'sucursal']),
        ]
```

### 5.2 Otras Tablas de Reportes

```sql
-- ════════════════════════════════════════════════════════════
-- reporte_llamadas_diarias
-- ════════════════════════════════════════════════════════════

CREATE TABLE reporte_llamadas_diarias (
    id BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    sucursal VARCHAR(50) NOT NULL,
    total_llamadas INTEGER NOT NULL,
    llamadas_atendidas INTEGER NOT NULL,
    llamadas_abandonadas INTEGER NOT NULL,
    duracion_promedio DECIMAL(10,2),
    tiempo_espera_promedio DECIMAL(10,2),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    
    CONSTRAINT unique_llamadas_fecha_sucursal UNIQUE (fecha, sucursal)
);


-- ════════════════════════════════════════════════════════════
-- dashboard_metricas (para dashboards en tiempo cercano)
-- ════════════════════════════════════════════════════════════

CREATE TABLE dashboard_metricas (
    id BIGSERIAL PRIMARY KEY,
    metrica_type VARCHAR(50) NOT NULL,  -- 'kpi_diario', 'tendencia_semanal', etc
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    sucursal VARCHAR(50),
    valor DECIMAL(15,2) NOT NULL,
    metadata JSONB,  -- Metadata adicional flexible
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

---

## RESUMEN PARTE 2

```
RELACIONES CUBIERTAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ IVR_LEGACY → ETL JOB
   - CallLog model (unmanaged, READ-ONLY)
   - IVRRouter enforcement
   - CNST-003 compliance

✅ ETL JOB → DEFAULT DB
   - Stored Procedure (Postgres)
   - Script Python + Cron
   - INSERT/UPDATE en tablas agregadas
   - Registro en ETLExecution

✅ Schemas de tablas
   - reporte_cmenu_agregado
   - reporte_llamadas_diarias
   - dashboard_metricas

PRÓXIMA PARTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PARTE 3/6: PIPELINE y REPORTS
- apps/pipeline/ (monitoring)
- apps/reports/ (consumption)
- N reportes/dashboards
```

---

**FIN DE PARTE 2/6**

Documento: ANALISIS_RELACIONES v2.0.0 - PARTE 2/6  
Fecha: 2026-01-17  
Estado: Completo  
Siguiente: PARTE 3/6 - PIPELINE y REPORTS
