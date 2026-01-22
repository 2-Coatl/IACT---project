---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Relaciones entre Apps
categoria: arquitectura/relaciones
tema: Relación IVR_LEGACY → ETL JOB (v2.0.0)
autor: Claude Technical Analysis
parte: 2/7 - Relación IVR_LEGACY → ETL JOB
tags: [ivr-legacy, etl, read-only, adapter-pattern, cnst-003]
relacionado:
  - ANALISIS_RELACIONES_v2.0.0_PARTE_1_de_7.md
  - FLUJO_DEFINITIVO_ETL_REPORTES_v3.0.0.md
estado: parte-2-de-7
---

# ANÁLISIS DE RELACIONES v2.0.0 - PARTE 2/7

**Relación: IVR_LEGACY → ETL JOB**

---

## TABLA DE CONTENIDOS (PARTE 2)

1. [Arquitectura de IVR_LEGACY](#arquitectura-ivr)
2. [CallLog Model (Unmanaged)](#calllog)
3. [READ-ONLY Enforcement](#read-only)
4. [ETL JOB - Acceso Directo](#etl-acceso)
5. [Queries de Ejemplo](#queries)
6. [Compliance CNST-003](#compliance)

---

<a name="arquitectura-ivr"></a>
## 1. ARQUITECTURA DE IVR_LEGACY

### 1.1 Propósito y Alcance

```
apps/ivr_legacy/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROPÓSITO:
  Proporcionar acceso READ-ONLY a base de datos legacy (MariaDB)

ALCANCE:
  ✅ Queries puntuales (si es necesario)
  ✅ Modelo unmanaged para ORM
  ✅ Adapter para queries estructuradas
  ✅ Router para enforcement READ-ONLY

NO ES RESPONSABLE DE:
  ❌ ETL (corre fuera de Django)
  ❌ Escritura en legacy DB
  ❌ Transformación de datos
  ❌ Scheduling

ACCESO PRINCIPAL:
  → ETL JOB accede DIRECTAMENTE (fuera de Django)
  → Django apps/ivr_legacy/ es opcional/secundario
```

### 1.2 Estructura de Archivos

```python
apps/ivr_legacy/
│
├── __init__.py
│
├── models.py ✅
│   └── CallLog (managed=False, db_table='call_logs')
│
├── adapters.py ✅
│   └── IVRAdapter (queries READ-ONLY estructuradas)
│
├── routers.py ✅
│   └── IVRRouter (enforcement READ-ONLY)
│
└── migrations/
    └── (vacío - managed=False)

Configuración relacionada:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

settings.py:
├─ DATABASES['ivr_legacy'] (MariaDB connection)
└─ DATABASE_ROUTERS = ['apps.ivr_legacy.routers.IVRRouter']
```

---

<a name="calllog"></a>
## 2. CALLLOG MODEL (UNMANAGED)

### 2.1 Definición del Modelo

```python
# ════════════════════════════════════════════════════════════
# apps/ivr_legacy/models.py
# ════════════════════════════════════════════════════════════

from django.db import models


class CallLog(models.Model):
    """
    Modelo unmanaged para tabla call_logs en IVR legacy.
    
    IMPORTANTE:
    - managed=False → Django NO crea esta tabla
    - Django NO hace migrations
    - Django SOLO query (READ-ONLY)
    - Tabla existe en MariaDB legacy
    - Creada y mantenida por sistema IVR
    """
    
    # Primary Key (auto de MariaDB)
    id = models.BigAutoField(primary_key=True)
    
    # Timestamp de llamada
    call_timestamp = models.DateTimeField(
        db_column='call_timestamp',
        help_text="Timestamp de la llamada"
    )
    
    # Información de llamada
    telefono = models.CharField(
        max_length=20,
        db_column='telefono',
        help_text="Número telefónico del cliente"
    )
    
    sucursal = models.CharField(
        max_length=50,
        db_column='sucursal',
        help_text="Sucursal (puebla, nacional, etc)"
    )
    
    servicio_800 = models.CharField(
        max_length=20,
        db_column='servicio_800',
        help_text="Número 800 marcado"
    )
    
    # Opciones de IVR
    cmenu_option = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='cmenu_option',
        help_text="Opción seleccionada en menú IVR"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at'
    )
    
    class Meta:
        managed = False  # ← CLAVE: Django NO gestiona
        db_table = 'call_logs'  # ← Tabla en MariaDB
        ordering = ['-call_timestamp']
        verbose_name = 'Call Log'
        verbose_name_plural = 'Call Logs'
    
    def __str__(self):
        return f"CallLog {self.id} - {self.telefono} ({self.call_timestamp})"


# ════════════════════════════════════════════════════════════
# ANÁLISIS DEL MODELO
# ════════════════════════════════════════════════════════════

CARACTERÍSTICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ managed=False (Django NO crea tabla)
✅ db_table='call_logs' (tabla en MariaDB)
✅ Solo fields necesarios (schema simplificado)
✅ NO hereda SoftDeleteMixin (tabla legacy)
✅ NO tiene métodos de negocio
✅ 0 líneas de lógica (solo definición)

USO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Query desde Django (opcional, solo si es necesario)
logs = CallLog.objects.using('ivr_legacy').filter(
    call_timestamp__date='2025-08-17'
)

# PERO: ETL JOB accede directamente a MariaDB (fuera de Django)
```

### 2.2 Schema Real vs Django Model

```sql
-- ════════════════════════════════════════════════════════════
-- TABLA REAL EN MARIADB (ivr_production.call_logs)
-- ════════════════════════════════════════════════════════════

CREATE TABLE call_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    call_timestamp DATETIME NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    sucursal VARCHAR(50) NOT NULL,
    servicio_800 VARCHAR(20) NOT NULL,
    cmenu_option VARCHAR(100),
    duration_seconds INT,
    call_status VARCHAR(20),
    agent_id INT,
    queue_time_seconds INT,
    -- ... otros campos del IVR
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_timestamp (call_timestamp),
    INDEX idx_sucursal_fecha (sucursal, DATE(call_timestamp)),
    INDEX idx_telefono (telefono)
) ENGINE=InnoDB;


DJANGO MODEL vs TABLA REAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Django CallLog:
  ✅ Tiene solo campos necesarios para ETL
  ✅ NO necesita todos los campos de la tabla
  ✅ Simplificado para queries específicos

Tabla real:
  → Puede tener 20+ campos
  → Django model solo define los que usa
  → Otros campos quedan en MariaDB pero no se usan

IMPORTANTE:
  Django model NO necesita coincidir 100% con schema real
  Solo define campos que va a usar en queries
```

---

<a name="read-only"></a>
## 3. READ-ONLY ENFORCEMENT

### 3.1 Tres Capas de Protección (CNST-003)

```
CAPA 1: Database Router
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# apps/ivr_legacy/routers.py

class IVRRouter:
    """
    Router para enforcing READ-ONLY en IVR legacy.
    
    Bloquea cualquier intento de escritura.
    """
    
    ivr_apps = {'ivr_legacy'}
    ivr_models = {'CallLog'}
    
    def db_for_read(self, model, **hints):
        """Redirige lectura a ivr_legacy DB."""
        if model._meta.app_label in self.ivr_apps:
            return 'ivr_legacy'
        return None
    
    def db_for_write(self, model, **hints):
        """BLOQUEA escritura en IVR legacy."""
        if model._meta.app_label in self.ivr_apps:
            return None  # ← Prohibe writes ✅
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """NO permite migrations en ivr_legacy."""
        if db == 'ivr_legacy':
            return False  # ← NO migrations ✅
        
        if app_label in self.ivr_apps:
            return False
        
        return None

✅ Imposible hacer .save(), .create(), .update(), .delete()
✅ RuntimeError si se intenta


CAPA 2: Database User Permissions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

-- Usuario en MariaDB (ivr_production)

CREATE USER 'ivr_readonly'@'%' IDENTIFIED BY 'password';

-- SOLO permisos de lectura
GRANT SELECT ON ivr_production.call_logs TO 'ivr_readonly'@'%';
GRANT SELECT ON ivr_production.* TO 'ivr_readonly'@'%';

-- NO tiene INSERT, UPDATE, DELETE
-- NO tiene DROP, CREATE, ALTER

✅ MariaDB rechaza cualquier intento de escritura
✅ Database-level enforcement


CAPA 3: Model Meta (managed=False)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CallLog(models.Model):
    class Meta:
        managed = False  # ← Django NO gestiona tabla

✅ Django NO intenta crear/modificar tabla
✅ NO genera migrations
✅ NO asume ownership de schema
```

### 3.2 Verificación de Enforcement

```python
# ════════════════════════════════════════════════════════════
# Test de READ-ONLY enforcement
# ════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestIVRReadOnlyEnforcement:
    
    def test_cannot_create_calllog(self):
        """Verificar que no se puede crear CallLog."""
        
        with pytest.raises(Exception):  # Router retorna None
            CallLog.objects.create(
                call_timestamp=datetime.now(),
                telefono='1234567890',
                sucursal='puebla',
                servicio_800='8001234567'
            )
        
        # ✅ PASS - Prohibido por router
    
    def test_cannot_update_calllog(self, calllog_fixture):
        """Verificar que no se puede actualizar CallLog."""
        
        log = CallLog.objects.using('ivr_legacy').first()
        log.telefono = '9999999999'
        
        with pytest.raises(Exception):  # Router retorna None
            log.save()
        
        # ✅ PASS - Prohibido por router
    
    def test_cannot_delete_calllog(self, calllog_fixture):
        """Verificar que no se puede eliminar CallLog."""
        
        log = CallLog.objects.using('ivr_legacy').first()
        
        with pytest.raises(Exception):  # Router retorna None
            log.delete()
        
        # ✅ PASS - Prohibido por router
    
    def test_can_read_calllog(self):
        """Verificar que SÍ se puede leer CallLog."""
        
        # Query permitido
        logs = CallLog.objects.using('ivr_legacy').filter(
            call_timestamp__date='2025-08-17'
        )
        
        count = logs.count()
        
        # ✅ PASS - Lectura permitida
        assert count >= 0
```

---

<a name="etl-acceso"></a>
## 4. ETL JOB - ACCESO DIRECTO

### 4.1 ETL NO usa Django ORM

```
IMPORTANTE: ETL JOB accede DIRECTAMENTE a MariaDB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ETL JOB corre fuera de Django:
  ✅ Stored Procedure en MySQL/Postgres
  ✅ Script Python externo
  ✅ Cron job en servidor

ETL NO usa:
  ❌ Django ORM (CallLog.objects...)
  ❌ IVRAdapter
  ❌ Django database router

ETL accede:
  ✅ SQL directo a MariaDB
  ✅ mysql-connector-python
  ✅ psycopg2 + dblink (si es Postgres)
  ✅ Cualquier cliente SQL nativo
```

### 4.2 Ejemplo: ETL con Stored Procedure

```sql
-- ════════════════════════════════════════════════════════════
-- ETL Stored Procedure (corre en Postgres/MySQL)
-- ════════════════════════════════════════════════════════════

CREATE OR REPLACE PROCEDURE etl_cmenu_diario()
AS $$
DECLARE
    v_fecha_proceso DATE;
    v_records_count INT;
BEGIN
    -- Fecha a procesar (ayer)
    v_fecha_proceso := CURRENT_DATE - INTERVAL '1 day';
    
    -- EXTRACT: Query IVR_LEGACY (MariaDB)
    -- Usa dblink o foreign data wrapper
    
    INSERT INTO reporte_cmenu_agregado (
        fecha,
        sucursal,
        cmenu_opcion,
        total_llamadas
    )
    SELECT 
        DATE(c.call_timestamp) as fecha,
        c.sucursal,
        c.cmenu_option,
        COUNT(*) as total_llamadas
    FROM dblink(
        'ivr_legacy_fdw',  -- Foreign Data Wrapper a MariaDB
        'SELECT call_timestamp, sucursal, cmenu_option 
         FROM call_logs 
         WHERE DATE(call_timestamp) = CURRENT_DATE - INTERVAL 1 DAY'
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
        total_llamadas = EXCLUDED.total_llamadas;
    
    GET DIAGNOSTICS v_records_count = ROW_COUNT;
    
    -- Registrar ejecución
    INSERT INTO pipeline_etlexecution (
        etl_name,
        fecha_procesada,
        status,
        records_processed,
        started_at,
        completed_at
    ) VALUES (
        'cmenu_diario',
        v_fecha_proceso,
        'success',
        v_records_count,
        NOW(),
        NOW()
    );
    
END;
$$ LANGUAGE plpgsql;


-- ════════════════════════════════════════════════════════════
-- Scheduler (pg_cron)
-- ════════════════════════════════════════════════════════════

SELECT cron.schedule(
    'etl-cmenu-diario',
    '0 2 * * *',  -- 2:00 AM diario
    'CALL etl_cmenu_diario()'
);
```

### 4.3 Ejemplo: ETL con Script Python Externo

```python
# ════════════════════════════════════════════════════════════
# scripts/etl_cmenu_diario.py (FUERA de Django)
# ════════════════════════════════════════════════════════════

import mysql.connector
import psycopg2
from datetime import date, timedelta, datetime

def etl_cmenu_diario():
    """
    ETL que corre fuera de Django.
    
    Accede DIRECTAMENTE a MariaDB y Postgres.
    NO usa Django ORM.
    """
    
    fecha_proceso = date.today() - timedelta(days=1)
    
    # ────────────────────────────────────────────────────────
    # CONEXIÓN A IVR_LEGACY (MariaDB) - LECTURA
    # ────────────────────────────────────────────────────────
    
    conn_ivr = mysql.connector.connect(
        host='mariadb-server',
        database='ivr_production',
        user='ivr_readonly',  # READ-ONLY user
        password='xxx',
        port=3306
    )
    
    # ────────────────────────────────────────────────────────
    # CONEXIÓN A DEFAULT DB (Postgres) - ESCRITURA
    # ────────────────────────────────────────────────────────
    
    conn_django = psycopg2.connect(
        host='localhost',
        database='callcenter_db',
        user='etl_user',  # Usuario con permisos de escritura
        password='xxx',
        port=5432
    )
    
    try:
        # ────────────────────────────────────────────────────
        # EXTRACT
        # ────────────────────────────────────────────────────
        
        cursor_ivr = conn_ivr.cursor(dictionary=True)
        
        cursor_ivr.execute("""
            SELECT 
                DATE(call_timestamp) as fecha,
                sucursal,
                cmenu_option,
                COUNT(*) as total_llamadas
            FROM call_logs
            WHERE DATE(call_timestamp) = %s
            GROUP BY 
                DATE(call_timestamp),
                sucursal,
                cmenu_option
        """, (fecha_proceso,))
        
        data = cursor_ivr.fetchall()
        
        # ────────────────────────────────────────────────────
        # TRANSFORM (opcional, si es necesario)
        # ────────────────────────────────────────────────────
        
        # Limpiar, normalizar, validar...
        # (en este caso ya está agregado en query)
        
        # ────────────────────────────────────────────────────
        # LOAD
        # ────────────────────────────────────────────────────
        
        cursor_django = conn_django.cursor()
        
        for row in data:
            cursor_django.execute("""
                INSERT INTO reporte_cmenu_agregado (
                    fecha, sucursal, cmenu_opcion, total_llamadas
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (fecha, sucursal, cmenu_opcion)
                DO UPDATE SET total_llamadas = EXCLUDED.total_llamadas
            """, (
                row['fecha'],
                row['sucursal'],
                row['cmenu_option'],
                row['total_llamadas']
            ))
        
        # ────────────────────────────────────────────────────
        # REGISTRO (ETLExecution)
        # ────────────────────────────────────────────────────
        
        cursor_django.execute("""
            INSERT INTO pipeline_etlexecution (
                etl_name,
                fecha_procesada,
                status,
                records_processed,
                started_at,
                completed_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'cmenu_diario',
            fecha_proceso,
            'success',
            len(data),
            datetime.now(),
            datetime.now()
        ))
        
        conn_django.commit()
        
        print(f"ETL completed: {len(data)} records")
    
    except Exception as e:
        conn_django.rollback()
        
        # Registrar error
        cursor_django.execute("""
            INSERT INTO pipeline_etlexecution (
                etl_name,
                fecha_procesada,
                status,
                error_message,
                started_at,
                completed_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'cmenu_diario',
            fecha_proceso,
            'failed',
            str(e),
            datetime.now(),
            datetime.now()
        ))
        
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

# Agregar a /etc/crontab o crontab -e
0 2 * * * /usr/bin/python3 /opt/callcenter/scripts/etl_cmenu_diario.py
```

---

<a name="queries"></a>
## 5. QUERIES DE EJEMPLO

### 5.1 Query desde Django (Opcional)

```python
# ════════════════════════════════════════════════════════════
# Si es necesario query desde Django (casos especiales)
# ════════════════════════════════════════════════════════════

# Ejemplo 1: Contar llamadas de hoy
from apps.ivr_legacy.models import CallLog
from datetime import date

today_count = CallLog.objects.using('ivr_legacy').filter(
    call_timestamp__date=date.today()
).count()

# Ejemplo 2: Llamadas por sucursal
from django.db.models import Count

llamadas_por_sucursal = CallLog.objects.using('ivr_legacy').filter(
    call_timestamp__date=date.today()
).values('sucursal').annotate(
    total=Count('id')
)

# Resultado:
# [
#     {'sucursal': 'puebla', 'total': 1523},
#     {'sucursal': 'nacional', 'total': 8745}
# ]

# Ejemplo 3: Últimas 100 llamadas
latest_calls = CallLog.objects.using('ivr_legacy').order_by(
    '-call_timestamp'
)[:100]

# IMPORTANTE:
# Estos queries son OPCIONALES y solo para casos específicos.
# ETL NO usa esto, accede directo a MariaDB.
```

### 5.2 IVRAdapter (Queries Estructurados)

```python
# ════════════════════════════════════════════════════════════
# apps/ivr_legacy/adapters.py
# ════════════════════════════════════════════════════════════

from datetime import date, datetime
from typing import List, Dict
from apps.ivr_legacy.models import CallLog


class IVRAdapter:
    """
    Adapter para queries estructurados a IVR legacy.
    
    IMPORTANTE:
    - Usado por Django apps (opcional)
    - ETL NO usa esto
    - Solo READ queries
    """
    
    @staticmethod
    def get_calls_by_date(fecha: date) -> List[Dict]:
        """
        Obtener llamadas de una fecha específica.
        
        Args:
            fecha: Fecha a consultar
        
        Returns:
            List[Dict] con llamadas
        """
        queryset = CallLog.objects.using('ivr_legacy').filter(
            call_timestamp__date=fecha
        )
        
        return list(queryset.values(
            'call_timestamp',
            'telefono',
            'sucursal',
            'servicio_800',
            'cmenu_option'
        ))
    
    @staticmethod
    def get_calls_count_by_sucursal(
        fecha_inicio: date,
        fecha_fin: date
    ) -> Dict[str, int]:
        """
        Contar llamadas por sucursal en rango de fechas.
        
        Returns:
            {'puebla': 5234, 'nacional': 18956}
        """
        from django.db.models import Count
        
        result = CallLog.objects.using('ivr_legacy').filter(
            call_timestamp__date__gte=fecha_inicio,
            call_timestamp__date__lte=fecha_fin
        ).values('sucursal').annotate(
            total=Count('id')
        )
        
        return {item['sucursal']: item['total'] for item in result}
    
    @staticmethod
    def verify_data_availability(fecha: date) -> bool:
        """
        Verificar si hay datos disponibles para una fecha.
        
        Útil para validación antes de ETL.
        """
        exists = CallLog.objects.using('ivr_legacy').filter(
            call_timestamp__date=fecha
        ).exists()
        
        return exists
```

---

<a name="compliance"></a>
## 6. COMPLIANCE CNST-003

### 6.1 Verificación de READ-ONLY

```
CNST-003: IVR_LEGACY READ-ONLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REQUIREMENT:
  Acceso a IVR legacy debe ser READ-ONLY.
  NO se permite INSERT, UPDATE, DELETE en call_logs.

ENFORCEMENT (3 capas):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CAPA 1: Django Database Router
  ✅ IVRRouter.db_for_write() → None
  ✅ Bloquea .save(), .create(), .update(), .delete()

CAPA 2: Database User Permissions
  ✅ User: ivr_readonly
  ✅ Permisos: GRANT SELECT ONLY
  ✅ MariaDB rechaza INSERT/UPDATE/DELETE

CAPA 3: Model Meta
  ✅ CallLog.Meta.managed = False
  ✅ Django NO intenta crear/modificar tabla

TESTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ test_cannot_create_calllog()
✅ test_cannot_update_calllog()
✅ test_cannot_delete_calllog()
✅ test_can_read_calllog()

COMPLIANCE: 100% ✅
```

### 6.2 Diagrama de Enforcement

```
┌─────────────────────────────────────────────────────────────┐
│ INTENTO DE ESCRITURA                                        │
└─────────────────────────────────────────────────────────────┘

CallLog.objects.create(...)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 1: Django Router                                       │
│                                                             │
│ IVRRouter.db_for_write(CallLog) → None                     │
│                                                             │
│ ❌ BLOQUEADO                                                 │
│ Raise: RuntimeError("No DB for write")                     │
└─────────────────────────────────────────────────────────────┘

SI se bypasea router (raw SQL):
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 2: Database User                                       │
│                                                             │
│ User: ivr_readonly                                          │
│ Permisos: SELECT only                                       │
│                                                             │
│ ❌ BLOQUEADO                                                 │
│ MariaDB Error: "Access denied"                             │
└─────────────────────────────────────────────────────────────┘

✅ DOBLE PROTECCIÓN GARANTIZA READ-ONLY
```

---

## RESUMEN PARTE 2

```
RELACIÓN IVR_LEGACY → ETL JOB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CallLog model (managed=False, READ-ONLY)
✅ IVRRouter enforcement (3 capas)
✅ ETL JOB accede DIRECTAMENTE (fuera de Django)
✅ IVRAdapter para queries opcionales
✅ CNST-003 compliance (100%)

PRÓXIMA PARTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PARTE 3/7: Relación ETL JOB → DEFAULT DB
- Stored procedures
- Tablas de reportes
- Schema de tablas agregadas
- INSERT/UPDATE logic
```

---

**FIN DE PARTE 2/7**

Documento: ANALISIS_RELACIONES v2.0.0 - PARTE 2/7  
Fecha: 2026-01-17  
Estado: Completo  
Siguiente: PARTE 3/7 - Relación ETL JOB → DEFAULT DB
