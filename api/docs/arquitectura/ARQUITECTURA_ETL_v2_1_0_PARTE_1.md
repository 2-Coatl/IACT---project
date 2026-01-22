---
version: 2.1.0
date: 2026-01-19
project: IACT (Sistema Call Center)
type: Arquitectura Técnica
categoria: arquitectura/diseño
titulo: Arquitectura Real del Sistema ETL - Versión Definitiva
componente: ETL (Extract, Transform, Load)
tecnologias: MariaDB, Django, Stored Procedures, APScheduler
scope: Sistema completo (IVR Legacy → Django → API)
audiencia: Desarrolladores, Arquitectos Técnicos
estado: definitivo
base: Arquitectura Real Implementada + RESTRICCIONES v1.0.0
partes: 1/3
---

# ARQUITECTURA REAL DEL SISTEMA ETL - VERSIÓN DEFINITIVA

**PARTE 1/3: FUNDAMENTOS Y ARQUITECTURA DE DATOS**

---

## 📋 TABLA DE CONTENIDOS - DOCUMENTO COMPLETO

### PARTE 1/3: FUNDAMENTOS Y ARQUITECTURA DE DATOS (ESTA PARTE)
1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura de Datos (MariaDB)](#2-arquitectura-de-datos-mariadb)
3. [Proceso ETL](#3-proceso-etl)

### PARTE 2/3: ARQUITECTURA DJANGO Y APIS
4. Arquitectura Django
5. APIs y Endpoints
6. Flujo de Datos Completo

### PARTE 3/3: NOMENCLATURA, CONSTANTES Y REFERENCIAS
7. Nomenclatura y Convenciones
8. Constantes y Restricciones
9. Diagramas
10. Referencias

---

## CONTROL DE VERSIONES

| Versión | Fecha      | Cambios                                                     |
|---------|------------|-------------------------------------------------------------|
| 2.1.0   | 2026-01-19 | Eliminación Redis/Celery según RESTRICCIONES_IACT v1.0.0   |
| 2.0.0   | 2026-01-19 | Actualización con CLEAN_CODE v3.0.1 y arquitectura corregida |
| 1.0.0   | 2026-01-18 | Versión inicial definitiva consolidada                      |

---
---

## 🔄 CAMBIOS EN v2.1.0

**Actualización Crítica:** Este documento se ha actualizado de v2.0.0 → v2.1.0 para cumplir con **RESTRICCIONES_ARQUITECTONICAS_IACT v1.0.0**.

### ❌ Tecnologías Eliminadas

Según **RESTRICCIONES v1.0.0**, las siguientes tecnologías están **PROHIBIDAS** y han sido eliminadas de toda la arquitectura:

#### **1. Redis (CNST-010)**
```yaml
Prohibido:
  - Redis para cache
  - Redis para sessions
  - django_redis backend

Reemplazado por:
  - Cache: locmem (desarrollo), dummy (producción)
  - Sessions: database backend
```

#### **2. Celery (CNST-013)**
```yaml
Prohibido:
  - Celery workers
  - Celery beat
  - Async tasks con Celery
  - Brokers (RabbitMQ, Redis)

Reemplazado por:
  - APScheduler para jobs programados
  - Cron para ETL diario
  - BackgroundScheduler para procesamiento
```

#### **3. Docker en Producción (CNST-014)**
```yaml
Prohibido:
  - Docker containers en producción
  - Kubernetes/Swarm
  - docker-compose deployment

Permitido:
  - Docker solo para desarrollo local

Reemplazado por:
  - Nginx + Gunicorn tradicional
  - Systemd services
  - Deploy con scripts bash
```

#### **4. Servicios Cloud (CNST-011, CNST-012)**
```yaml
Prohibido:
  - AWS S3, Azure Blob, Google Cloud Storage
  - Sentry, New Relic, servicios externos
  - CDN externos

Reemplazado por:
  - Filesystem local (/opt/iact/)
  - Logging rotating local
  - Monitoring interno
```

### ✅ Cambios en este Documento (PARTE 1)

**PARTE 1** ya estaba **mayormente conforme** con RESTRICCIONES. Solo se actualizaron:

1. **Stack Tecnológico:**
   - ✅ Agregado: APScheduler
   - ✅ Removido: Referencias a tecnologías cloud

2. **Decisiones Arquitectónicas:**
   - ✅ Confirmado: ETL con Cron (NO Celery) - ya estaba correcto
   - ✅ Confirmado: Stored Procedures MariaDB

3. **Metadata:**
   - ✅ Versión 2.0.0 → 2.1.0
   - ✅ Tecnologías actualizadas

**Nota:** Los cambios mayores están en **PARTE 2 y PARTE 3** donde se eliminaron configuraciones de Redis/Celery/Docker.

### Migración

Para migrar de v2.0.0 → v2.1.0, consulta:
📄 **GUIA_MIGRACION_ETL_v2_0_0_a_v2_1_0.md** (por crear)

---

## 🔄 CAMBIOS EN v2.0.0

**Actualización:** Este documento se ha actualizado de v1.0.0 → v2.0.0 para alinearse con CLEAN_CODE NAMING PRINCIPLES v3.0.1.

### Cambios Principales

#### **1. Nomenclatura de Modelos (Español → Inglés)**

```
❌ v1.0.0:                      ✅ v2.0.0:
├─ HistoricoT1                  ├─ CallRecord
├─ HistoricoT2                  │  (configurable db_table)
├─ HistoricoT3                  │
├─ ReporteTrimestral            ├─ QuarterlyReport
├─ LlamadasAbandonadas          ├─ AbandonedCall
└─ ClientesUnicos               └─ UniqueClient
```

**Razón:** CLEAN_CODE v3.0.1 establece nomenclatura en inglés para código.

#### **2. Arquitectura apps/ Corregida**

```
❌ v1.0.0:                      ✅ v2.0.0:
apps/utils/models.py            apps/core/models.py
├─ SoftDeleteMixin              ├─ SoftDeleteMixin
└─ TimeStampedModel             ├─ TimeStampedModel
                                ├─ SoftDeleteManager
                                └─ SoftDeleteQuerySet

apps/utils/ (funciones)         apps/utils/ (funciones)
├─ pagination.py                ├─ pagination.py
├─ exceptions.py                ├─ exceptions.py
└─ request.py                   └─ request.py
```

**Razón:** apps/core/ para modelos abstractos, apps/utils/ solo funciones.

#### **3. Consolidación CallRecord**

En v2.0.0, **CallRecord** es un modelo único que mapea a diferentes tablas históricas mediante configuración de `db_table`:

```python
# Configuración dinámica por trimestre
class CallRecord(models.Model):
    class Meta:
        db_table = 'tbl_historico_t1_2025'  # O t2, t3 según trimestre
        managed = False
```

**IMPORTANTE:** Las tablas MariaDB NO cambian (`tbl_historico_t1/t2/t3_2025`). Solo cambia el nombre del modelo Django.

#### **4. Referencias Actualizadas**

- ✅ CLEAN_CODE v3.0.1 (antes v2.3.0)
- ✅ Importaciones desde apps/core/ (antes apps/utils/)
- ✅ Documentación actualizada

### Migración

Para migrar de v1.0.0 → v2.0.0, consulta:
📄 **RESUMEN_CAMBIOS_ETL_v1_0_0_a_v2_0_0.md**

---

<a name="1-resumen-ejecutivo"></a>
## 1. RESUMEN EJECUTIVO

### 1.1 Arquitectura en una Página

```
┌─────────────────────────────────────────────────────────────────┐
│ ARQUITECTURA REAL DEL SISTEMA ETL - IACT CALL CENTER           │
└─────────────────────────────────────────────────────────────────┘

ORIGEN DE DATOS:
┌──────────────────┐
│  IVR Legacy      │  → Sistema externo (fuera del control de Django)
│  (Sistema PBX)   │  → Genera CDRs (Call Detail Records)
└────────┬─────────┘  → Alimenta MariaDB en tiempo real
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ BASE DE DATOS: MariaDB (IVR_LEGACY)                             │
├─────────────────────────────────────────────────────────────────┤
│ TABLAS FUENTE:                                                  │
│ ├─ tbl_historico_t1_2025   (Trimestre 1: Ene-Mar)              │
│ ├─ tbl_historico_t2_2025   (Trimestre 2: Abr-Jun)              │
│ └─ tbl_historico_t3_2025   (Trimestre 3: Jul-Sep)              │
│                                                                 │
│ ETL (Stored Procedure):                                         │
│ ├─ Ejecutado por: Cron diario (2:00 AM)                        │
│ ├─ Lenguaje: SQL puro (MariaDB)                                │
│ └─ Función: Agrega datos → tbl_reporte_*                       │
│                                                                 │
│ TABLAS AGREGADAS (salida del ETL):                             │
│ ├─ tbl_reporte_trimestral                                      │
│ ├─ tbl_reporte_transferencias                                  │
│ ├─ tbl_reporte_menu_agregado                                   │
│ └─ ... (7 tablas de reportes)                                  │
│                                                                 │
│ TABLA DE CONTROL:                                              │
│ └─ job_execution_log (registra ejecuciones del ETL)            │
└─────────────────────────────────────────────────────────────────┘
         │
         ↓ Django lee (READONLY - managed=False)
┌─────────────────────────────────────────────────────────────────┐
│ DJANGO APPLICATION                                              │
├─────────────────────────────────────────────────────────────────┤
│ APPS:                                                           │
│ ├─ apps/ivr/         → Modelos readonly (managed=False)        │
│ ├─ apps/reports/     → Generación de reportes bajo demanda     │
│ ├─ apps/dashboard/   → Visualización widgets tiempo real       │
│ └─ apps/pipeline/    → Monitoreo estado ETL                    │
│                                                                 │
│ DATABASE ROUTER:                                                │
│ ├─ IVR_LEGACY (MariaDB) → apps/ivr/ (readonly)                 │
│ └─ DEFAULT (PostgreSQL) → Resto de apps (read/write)           │
└─────────────────────────────────────────────────────────────────┘
         │
         ↓ Django REST Framework
┌─────────────────────────────────────────────────────────────────┐
│ REST API                                                        │
├─────────────────────────────────────────────────────────────────┤
│ REPORTES (7 endpoints):                                         │
│ ├─ POST /api/v1/reports/llamadas-abandonadas/                  │
│ ├─ POST /api/v1/reports/clientes-unicos/                       │
│ ├─ POST /api/v1/reports/promedio-clientes/                     │
│ ├─ POST /api/v1/reports/clientes-menu/                         │
│ ├─ POST /api/v1/reports/llamadas-menu/                         │
│ ├─ POST /api/v1/reports/detalle-transferencias/                │
│ └─ POST /api/v1/reports/menu-errores/                          │
│                                                                 │
│ DASHBOARDS (3 endpoints):                                       │
│ ├─ GET  /api/v1/dashboard/metricas-trimestrales/               │
│ ├─ GET  /api/v1/dashboard/analisis-clientes/                   │
│ └─ GET  /api/v1/dashboard/performance-ivr/                     │
│                                                                 │
│ PIPELINE:                                                       │
│ └─ GET  /api/v1/pipeline/status/                               │
└─────────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (React/Vue)                                            │
│ ├─ Visualización de reportes                                   │
│ ├─ Dashboards interactivos                                     │
│ └─ Exportación (Excel, CSV)                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

### 1.2 Decisiones Arquitectónicas Clave

#### **DECISIÓN 1: MariaDB como Base de Datos del IVR**

```yaml
Decisión: Usar MariaDB para el sistema IVR Legacy
Razón: Sistema preexistente, fuera del control de Django
Alternativas consideradas: Migrar a PostgreSQL
Rechazada: IVR Legacy sigue alimentando MariaDB en tiempo real
Estado: Definitivo (no cambiará)
```

---

#### **DECISIÓN 2: Django managed=False (Readonly)**

```yaml
Decisión: Modelos Django con managed=False para tablas MariaDB
Razón: 
  - Django NO gestiona el schema de IVR_LEGACY
  - Django solo LEE datos (readonly)
  - El schema lo gestiona el ETL (Stored Procedure)
Alternativas consideradas: managed=True con migraciones
Rechazada: Django no debe tocar el schema de IVR Legacy
Código:
  class CallRecord(models.Model):
      class Meta:
          managed = False
          db_table = 'tbl_historico_t1_2025'
Estado: Definitivo
```

---

#### **DECISIÓN 3: ETL como Stored Procedure (no Python)**

```yaml
Decisión: ETL implementado como Stored Procedure en MariaDB
Razón:
  - ETL ya existe y funciona
  - Lenguaje: SQL puro (MariaDB)
  - Ejecutado por: Cron diario (2:00 AM)
  - NO usar Celery, Airflow, ni Python ETL
Alternativas consideradas: 
  - Celery + Python ETL
  - Django management commands
Rechazadas: ETL actual es robusto y estable
Estado: Definitivo
```

---

#### **DECISIÓN 4: Separación Reports vs Dashboard**

```yaml
Decisión: apps/reports/ y apps/dashboard/ como apps independientes
Razón:
  - Reports: Generación bajo demanda (POST), archivos descargables
  - Dashboard: Visualización tiempo real (GET), widgets en vivo
  - Responsabilidades diferentes
  - RBAC separado (reports.view vs dashboard.view)
Alternativas consideradas: Todo en reports/
Rechazada: Mezclaría responsabilidades
Estado: Definitivo
Ver: URLS_REPORTES_Y_DASHBOARDS.md
```

---

#### **DECISIÓN 5: Database Router**

```yaml
Decisión: Database Router para separar IVR_LEGACY (MariaDB) de DEFAULT (PostgreSQL)
Razón:
  - apps/ivr/ lee de MariaDB (IVR_LEGACY)
  - Resto de apps escriben a PostgreSQL (DEFAULT)
  - Separación clara de responsabilidades
Configuración:
  DATABASE_ROUTERS = ['config.routers.IVRRouter']
Estado: Definitivo
```

---

### 1.3 Stack Tecnológico

```
┌─────────────────────┬──────────────────────────────────────────┐
│ Componente          │ Tecnología                               │
├─────────────────────┼──────────────────────────────────────────┤
│ Base de Datos IVR   │ MariaDB 10.x                             │
│ Base de Datos App   │ PostgreSQL 14+                           │
│ Backend Framework   │ Django 4.2 LTS                           │
│ API Framework       │ Django REST Framework 3.14+              │
│ ETL                 │ Stored Procedure (SQL/MariaDB)           │
│ Trigger ETL         │ Cron (Linux) - Diario 2:00 AM            │
│ Jobs Programados    │ APScheduler (BackgroundScheduler)        │
│ ORM                 │ Django ORM (readonly para IVR)           │
│ Cache               │ locmem (dev), dummy (prod) - NO Redis    │
│ Sessions            │ Database backend - NO Redis              │
│ Auth/Permisos       │ RBAC Custom (apps/access/)               │
│ Storage             │ Filesystem local (/opt/iact/)            │
│ Logging             │ Filesystem rotating - NO Sentry          │
│ Export              │ openpyxl (Excel), csv (CSV)              │
│ Frontend            │ React/Vue (fuera de scope)               │
└─────────────────────┴──────────────────────────────────────────┘
```

**Nota Importante (RESTRICCIONES v1.0.0):**
- ❌ **NO** se usa Redis (cache, sessions)
- ❌ **NO** se usa Celery (async tasks)
- ❌ **NO** se usa Docker (producción)
- ❌ **NO** se usan servicios cloud (S3, Sentry, etc)
- ✅ Sistema **on-premise** con tecnologías tradicionales

---

### 1.4 Números Clave del Sistema

```
VOLUMETRÍA (Estimada):
├─ Llamadas/día:        ~5,000 - 10,000
├─ Llamadas/trimestre:  ~450,000 - 900,000
├─ Registros históricos: ~2.7M - 5.4M/año
└─ Crecimiento:         ~20% anual

PERFORMANCE ETL:
├─ Duración promedio:   10-15 minutos
├─ Horario ejecución:   2:00 AM (diario)
├─ Timeout máximo:      300 segundos (CNST-004)
└─ Reintentos:          3 (configurado en cron)

LÍMITES API:
├─ Rango fechas:        730 días máx (CNST-006)
├─ Registros export:    100,000 máx (CNST-007)
├─ Paginación default:  50 registros
└─ Rate limiting:       100 req/hora (configurado)

TABLAS:
├─ Tablas fuente:       3 (tbl_historico_t1/t2/t3)
├─ Tablas agregadas:    7 (tbl_reporte_*)
├─ Campos promedio:     15-20 por tabla
└─ Índices:             Por trimestre, DID, fecha
```

---

<a name="2-arquitectura-de-datos-mariadb"></a>
## 2. ARQUITECTURA DE DATOS (MariaDB)

### 2.1 Database IVR_LEGACY

#### **2.1.1 Configuración en Django**

```python
# config/settings/base.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'iact_db',
        'USER': 'iact_user',
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'ivr_legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ivr_database',
        'USER': 'ivr_readonly',  # Usuario con permisos de solo lectura
        'PASSWORD': env('IVR_DB_PASSWORD'),
        'HOST': 'mariadb-server.local',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# IMPORTANTE: Usuario ivr_readonly tiene SOLO SELECT
# NO tiene permisos de INSERT, UPDATE, DELETE
```

---

#### **2.1.2 Database Router**

```python
# config/routers.py

class IVRRouter:
    """
    Router para separar IVR_LEGACY (MariaDB) de DEFAULT (PostgreSQL).
    
    Reglas:
    - apps/ivr/ → 'ivr_legacy' database (MariaDB)
    - Resto de apps → 'default' database (PostgreSQL)
    - IVR es READONLY (no permite writes)
    """
    
    ivr_app_labels = {'ivr'}
    
    def db_for_read(self, model, **hints):
        """Lee de ivr_legacy si el modelo está en apps/ivr/."""
        if model._meta.app_label in self.ivr_app_labels:
            return 'ivr_legacy'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Escribe a default siempre.
        
        NOTA: apps/ivr/ tiene managed=False, así que Django
        nunca intentará escribir en ivr_legacy.
        """
        if model._meta.app_label in self.ivr_app_labels:
            # Esto no debería pasar (managed=False lo previene)
            # Pero si pasa, forzar a default para evitar errores
            return 'default'
        return 'default'
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        apps/ivr/ NO permite migraciones (managed=False).
        """
        if app_label in self.ivr_app_labels:
            return False  # ← CRÍTICO: No migrar IVR
        return db == 'default'
```

**Configuración:**
```python
# config/settings/base.py
DATABASE_ROUTERS = ['config.routers.IVRRouter']
```

---

### 2.2 Tablas Históricas (tbl_historico_t1/t2/t3)

#### **2.2.1 Propósito**

```
TABLAS FUENTE (Raw Data del IVR):

tbl_historico_t1_2025  → Trimestre 1 (Enero - Marzo)
tbl_historico_t2_2025  → Trimestre 2 (Abril - Junio)
tbl_historico_t3_2025  → Trimestre 3 (Julio - Septiembre)

CARACTERÍSTICAS:
- Alimentadas en tiempo real por el IVR Legacy
- 1 registro = 1 llamada (CDR - Call Detail Record)
- NO agregadas (datos crudos)
- Django las lee vía ORM (readonly)
- El ETL las procesa para generar tbl_reporte_*
```

---

#### **2.2.2 Estructura de Tabla (tbl_historico_t1_2025)**

```sql
-- NOTA: Schema REAL del IVR Legacy
-- Django NO gestiona este schema (managed=False)

CREATE TABLE tbl_historico_t1_2025 (
    -- Identificador único de la llamada
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Campos de fecha/hora (nomenclatura húngara del dominio)
    dFecha DATE NOT NULL,                    -- Fecha de la llamada
    dHora TIME NOT NULL,                     -- Hora de la llamada
    dFechaHora DATETIME NOT NULL,            -- Timestamp completo
    
    -- Campos de identificación (prefijo 'c' = código)
    cDID_800Transfer VARCHAR(20),            -- DID que recibió la llamada
    cTelefono_Origen VARCHAR(20),            -- Número del cliente
    cMenu VARCHAR(100),                      -- Menú IVR seleccionado
    cOpcion VARCHAR(50),                     -- Opción dentro del menú
    cSubOpcion VARCHAR(50),                  -- Sub-opción (si aplica)
    
    -- Campos de clasificación
    cTipoLlamada VARCHAR(50),                -- ENTRANTE, SALIENTE, INTERNA
    cEstado VARCHAR(50),                     -- COMPLETADA, ABANDONADA, TRANSFERIDA
    cResultado VARCHAR(100),                 -- Resultado final de la llamada
    
    -- Campos numéricos
    nDuracionSegundos INT,                   -- Duración total en segundos
    nTiempoEsperaSegundos INT,               -- Tiempo en cola
    nTiempoConversacionSegundos INT,         -- Tiempo hablando con agente
    
    -- Campos de agente (si fue transferida)
    cAgenteID VARCHAR(50),                   -- ID del agente
    cAgenteName VARCHAR(200),                -- Nombre del agente
    cCola VARCHAR(100),                      -- Cola de atención
    
    -- Campos de origen geográfico
    cCiudad VARCHAR(100),                    -- Ciudad del llamante
    cEstado VARCHAR(100),                    -- Estado/Provincia
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_fecha (dFecha),
    INDEX idx_did (cDID_800Transfer),
    INDEX idx_menu (cMenu),
    INDEX idx_telefono (cTelefono_Origen),
    INDEX idx_estado (cEstado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Nomenclatura Húngara del Dominio:**
- `d` = date (fecha/hora)
- `c` = código/char (texto)
- `n` = numérico

**IMPORTANTE:** Esta nomenclatura viene del IVR Legacy y se MANTIENE en Django (managed=False).

---

#### **2.2.3 Modelo Django (apps/ivr/models.py)**

```python
# apps/ivr/models.py

from django.db import models


class CallRecord(models.Model):
    """
    Histórico de llamadas Q1 (Enero-Marzo) 2025.
    
    Tabla fuente del IVR Legacy (MariaDB).
    Django solo LEE (managed=False).
    
    Nomenclatura:
    - dFecha, dHora: prefijo 'd' = date (del dominio IVR)
    - cMenu, cOpcion: prefijo 'c' = código (del dominio IVR)
    - nDuracion: prefijo 'n' = numérico (del dominio IVR)
    
    CRÍTICO:
    - managed=False → Django NO gestiona schema
    - db_table → Nombre EXACTO de la tabla en MariaDB
    - app_label → 'ivr' (para database router)
    """
    
    # Campo ID (auto_increment en MariaDB)
    id = models.BigAutoField(primary_key=True)
    
    # Campos de fecha/hora
    dFecha = models.DateField(
        verbose_name="Fecha",
        help_text="Fecha de la llamada"
    )
    dHora = models.TimeField(
        verbose_name="Hora",
        help_text="Hora de la llamada"
    )
    dFechaHora = models.DateTimeField(
        verbose_name="Fecha y Hora",
        help_text="Timestamp completo de la llamada"
    )
    
    # Campos de identificación
    cDID_800Transfer = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="DID",
        help_text="DID que recibió la llamada (ej: 19020084)"
    )
    cTelefono_Origen = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono Origen",
        help_text="Número del cliente"
    )
    cMenu = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Menú",
        help_text="Menú IVR seleccionado (ej: CREDITOS, SALDOS)"
    )
    cOpcion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Opción",
        help_text="Opción dentro del menú"
    )
    cSubOpcion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Sub-opción"
    )
    
    # Campos de clasificación
    cTipoLlamada = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Tipo de Llamada",
        help_text="ENTRANTE, SALIENTE, INTERNA"
    )
    cEstado = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Estado",
        help_text="COMPLETADA, ABANDONADA, TRANSFERIDA"
    )
    cResultado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Resultado"
    )
    
    # Campos numéricos
    nDuracionSegundos = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Duración (seg)",
        help_text="Duración total en segundos"
    )
    nTiempoEsperaSegundos = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Tiempo Espera (seg)"
    )
    nTiempoConversacionSegundos = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Tiempo Conversación (seg)"
    )
    
    # Campos de agente
    cAgenteID = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="ID Agente"
    )
    cAgenteName = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nombre Agente"
    )
    cCola = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cola"
    )
    
    # Campos geográficos
    cCiudad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ciudad"
    )
    cEstado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Estado"
    )
    
    # Metadatos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado en"
    )
    
    class Meta:
        app_label = 'ivr'
        managed = False  # ← CRÍTICO: Django NO gestiona schema
        db_table = 'tbl_historico_t1_2025'  # ← Nombre EXACTO en MariaDB
        verbose_name = 'Histórico T1 2025'
        verbose_name_plural = 'Históricos T1 2025'
        ordering = ['-dFechaHora']
    
    def __str__(self):
        """Representación string."""
        return f"{self.cTelefono_Origen} - {self.dFechaHora} - {self.cMenu}"


class CallRecord(models.Model):
    """
    Histórico de llamadas Q2 (Abril-Junio) 2025.
    
    MISMA ESTRUCTURA que CallRecord.
    Diferencia: Trimestre y nombre de tabla.
    """
    # ... MISMOS CAMPOS que CallRecord ...
    
    class Meta:
        app_label = 'ivr'
        managed = False
        db_table = 'tbl_historico_t2_2025'
        verbose_name = 'Histórico T2 2025'
        verbose_name_plural = 'Históricos T2 2025'
        ordering = ['-dFechaHora']


class CallRecord(models.Model):
    """
    Histórico de llamadas Q3 (Julio-Septiembre) 2025.
    
    MISMA ESTRUCTURA que CallRecord.
    Diferencia: Trimestre y nombre de tabla.
    """
    # ... MISMOS CAMPOS que CallRecord ...
    
    class Meta:
        app_label = 'ivr'
        managed = False
        db_table = 'tbl_historico_t3_2025'
        verbose_name = 'Histórico T3 2025'
        verbose_name_plural = 'Históricos T3 2025'
        ordering = ['-dFechaHora']
```

---

#### **2.2.4 Uso de Modelos Históricos**

```python
# apps/reports/services.py

from apps.ivr.models import CallRecord, CallRecord, CallRecord
from datetime import date


class ReportService:
    """Servicio de reportes."""
    
    @staticmethod
    def get_historico_model(fecha: date):
        """
        Determina qué tabla histórica usar según la fecha.
        
        Args:
            fecha: Fecha de la llamada
        
        Returns:
            Modelo correspondiente (CallRecord/T2/T3)
        """
        mes = fecha.month
        
        if 1 <= mes <= 3:  # Ene-Mar
            return CallRecord
        elif 4 <= mes <= 6:  # Abr-Jun
            return CallRecord
        elif 7 <= mes <= 9:  # Jul-Sep
            return CallRecord
        else:
            raise ValueError(f"Mes {mes} fuera de trimestres definidos")
    
    @staticmethod
    def get_call_records(start_date: date, end_date: date):
        """
        Obtiene registros de llamadas por rango de fechas.
        
        Puede consultar múltiples tablas si el rango cruza trimestres.
        """
        records = []
        
        # Determinar trimestres involucrados
        if start_date.month <= 3 and end_date.month <= 3:
            # Solo T1
            records = list(CallRecord.objects.filter(
                dFecha__gte=start_date,
                dFecha__lte=end_date
            ).values())
        
        elif start_date.month <= 3 and end_date.month > 3:
            # T1 + T2 o T1 + T2 + T3
            records_t1 = list(CallRecord.objects.filter(
                dFecha__gte=start_date,
                dFecha__lte=date(start_date.year, 3, 31)
            ).values())
            
            if end_date.month <= 6:
                records_t2 = list(CallRecord.objects.filter(
                    dFecha__gte=date(start_date.year, 4, 1),
                    dFecha__lte=end_date
                ).values())
                records = records_t1 + records_t2
            else:
                # Incluye T3
                records_t2 = list(CallRecord.objects.filter(
                    dFecha__gte=date(start_date.year, 4, 1),
                    dFecha__lte=date(start_date.year, 6, 30)
                ).values())
                records_t3 = list(CallRecord.objects.filter(
                    dFecha__gte=date(start_date.year, 7, 1),
                    dFecha__lte=end_date
                ).values())
                records = records_t1 + records_t2 + records_t3
        
        # ... más lógica para otros casos ...
        
        return records
```

---

### 2.3 Tablas Agregadas (tbl_reporte_*)

#### **2.3.1 Propósito**

```
TABLAS AGREGADAS (Salida del ETL):

GENERADAS POR: Stored Procedure ETL (diario, 2:00 AM)
FUENTE: tbl_historico_t1/t2/t3_2025
USO: Lectura por Django para reportes y dashboards

CARACTERÍSTICAS:
- Datos pre-calculados (agregaciones)
- Optimizadas para consultas rápidas
- Actualizadas diariamente
- Django las lee vía ORM (readonly)
```

---

#### **2.3.2 Lista de Tablas Agregadas**

```
┌────────────────────────────────────────┬──────────────────────────────────┐
│ Tabla                                  │ Propósito                        │
├────────────────────────────────────────┼──────────────────────────────────┤
│ tbl_reporte_trimestral                 │ Resumen trimestral general       │
│ tbl_reporte_transferencias             │ Detalle de transferencias        │
│ tbl_reporte_menu_agregado              │ Agregados por menú               │
│ tbl_reporte_llamadas_abandonadas       │ Llamadas abandonadas (RPT-TR-021)│
│ tbl_reporte_clientes_unicos            │ Clientes únicos (RPT-TR-011)     │
│ tbl_reporte_promedio_clientes          │ Promedio clientes (RPT-TR-031)   │
│ tbl_reporte_menu_errores               │ Errores de menú (RPT-ERR-001)    │
└────────────────────────────────────────┴──────────────────────────────────┘

TOTAL: 7 tablas agregadas
```

---

#### **2.3.3 Tabla: tbl_reporte_trimestral**

```sql
-- Tabla agregada: Reporte Trimestral
-- Generada por: Stored Procedure ETL
-- Frecuencia: Diaria (acumulativa)

CREATE TABLE tbl_reporte_trimestral (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Dimensiones
    trimestre VARCHAR(20) NOT NULL,          -- 'Q1', 'Q2', 'Q3'
    anio INT NOT NULL,                       -- 2025
    fecha DATE NOT NULL,                     -- Fecha del registro
    servicio_800 VARCHAR(50),                -- DID (ej: 'Puebla', 'Nacional A')
    
    -- Métricas agregadas
    total_llamadas INT DEFAULT 0,
    llamadas_completadas INT DEFAULT 0,
    llamadas_abandonadas INT DEFAULT 0,
    llamadas_transferidas INT DEFAULT 0,
    
    -- Clientes
    clientes_unicos INT DEFAULT 0,
    
    -- Tiempos (promedios en segundos)
    duracion_promedio_seg INT,
    tiempo_espera_promedio_seg INT,
    tiempo_conversacion_promedio_seg INT,
    
    -- Tasa de abandono (%)
    tasa_abandono DECIMAL(5,2),              -- Calculado: abandonadas/total*100
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    UNIQUE KEY idx_unico (trimestre, anio, fecha, servicio_800),
    INDEX idx_trimestre (trimestre),
    INDEX idx_fecha (fecha),
    INDEX idx_servicio (servicio_800)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Modelo Django:**

```python
# apps/ivr/models.py

class QuarterlyReport(models.Model):
    """
    Reporte trimestral agregado.
    
    Generado por: Stored Procedure ETL
    Django: Readonly (managed=False)
    """
    
    id = models.BigAutoField(primary_key=True)
    
    # Dimensiones
    trimestre = models.CharField(
        max_length=20,
        verbose_name="Trimestre",
        help_text="Q1, Q2, Q3"
    )
    anio = models.IntegerField(
        verbose_name="Año"
    )
    fecha = models.DateField(
        verbose_name="Fecha"
    )
    servicio_800 = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Servicio 800",
        help_text="DID: Puebla, Nacional A, etc."
    )
    
    # Métricas
    total_llamadas = models.IntegerField(
        default=0,
        verbose_name="Total Llamadas"
    )
    llamadas_completadas = models.IntegerField(
        default=0,
        verbose_name="Completadas"
    )
    llamadas_abandonadas = models.IntegerField(
        default=0,
        verbose_name="Abandonadas"
    )
    llamadas_transferidas = models.IntegerField(
        default=0,
        verbose_name="Transferidas"
    )
    clientes_unicos = models.IntegerField(
        default=0,
        verbose_name="Clientes Únicos"
    )
    
    # Tiempos
    duracion_promedio_seg = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Duración Prom. (seg)"
    )
    tiempo_espera_promedio_seg = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Espera Prom. (seg)"
    )
    tiempo_conversacion_promedio_seg = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Conversación Prom. (seg)"
    )
    
    # Tasa
    tasa_abandono = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Tasa Abandono (%)"
    )
    
    # Metadatos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizado"
    )
    
    class Meta:
        app_label = 'ivr'
        managed = False
        db_table = 'tbl_reporte_trimestral'
        verbose_name = 'Reporte Trimestral'
        verbose_name_plural = 'Reportes Trimestrales'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.trimestre} {self.anio} - {self.servicio_800}"
```

---

#### **2.3.4 Tabla: tbl_reporte_llamadas_abandonadas**

```sql
-- Tabla: Llamadas Abandonadas (RPT-TR-021)
-- Generada por: q_REPTRIM021_LLAMADAS_ABDANDONADAS.sql

CREATE TABLE tbl_reporte_llamadas_abandonadas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Dimensiones
    trimestre VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL,
    did VARCHAR(50),
    menu VARCHAR(100),
    
    -- Métricas
    total_abandonadas INT DEFAULT 0,
    tiempo_espera_promedio_seg INT,
    
    -- Clasificación
    abandonadas_antes_30seg INT DEFAULT 0,  -- < 30 segundos
    abandonadas_30_60seg INT DEFAULT 0,     -- 30-60 segundos
    abandonadas_mas_60seg INT DEFAULT 0,    -- > 60 segundos
    
    -- Tasa
    tasa_abandono DECIMAL(5,2),
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_trimestre (trimestre),
    INDEX idx_fecha (fecha),
    INDEX idx_did (did),
    INDEX idx_menu (menu)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Modelo Django:**

```python
# apps/ivr/models.py

class ReporteAbandonedCall(models.Model):
    """
    Reporte de llamadas abandonadas (RPT-TR-021).
    
    Generado por: q_REPTRIM021_LLAMADAS_ABDANDONADAS.sql
    Django: Readonly (managed=False)
    """
    
    id = models.BigAutoField(primary_key=True)
    
    # Dimensiones
    trimestre = models.CharField(max_length=20)
    fecha = models.DateField()
    did = models.CharField(max_length=50, blank=True, null=True)
    menu = models.CharField(max_length=100, blank=True, null=True)
    
    # Métricas
    total_abandonadas = models.IntegerField(default=0)
    tiempo_espera_promedio_seg = models.IntegerField(blank=True, null=True)
    
    # Clasificación por tiempo
    abandonadas_antes_30seg = models.IntegerField(default=0)
    abandonadas_30_60seg = models.IntegerField(default=0)
    abandonadas_mas_60seg = models.IntegerField(default=0)
    
    # Tasa
    tasa_abandono = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'ivr'
        managed = False
        db_table = 'tbl_reporte_llamadas_abandonadas'
        verbose_name = 'Reporte Llamadas Abandonadas'
        verbose_name_plural = 'Reportes Llamadas Abandonadas'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.trimestre} - {self.menu} - {self.total_abandonadas}"
```

---

### 2.4 Tabla de Control (job_execution_log)

#### **2.4.1 Propósito**

```
TABLA: job_execution_log

PROPÓSITO:
- Registrar cada ejecución del Stored Procedure ETL
- Monitorear estado del ETL (SUCCESS, FAILED, RUNNING)
- Auditoría de procesos
- Base para apps/pipeline/ (monitoreo)

ACTUALIZADA POR: Stored Procedure ETL
LEÍDA POR: apps/pipeline/services.py
```

---

#### **2.4.2 Estructura**

```sql
CREATE TABLE job_execution_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Identificación
    job_name VARCHAR(100) NOT NULL,          -- 'etl_daily'
    
    -- Timestamps
    start_time DATETIME NOT NULL,            -- Inicio ejecución
    end_time DATETIME,                       -- Fin ejecución (NULL si running)
    
    -- Estado
    status VARCHAR(20) NOT NULL,             -- 'PENDING', 'RUNNING', 'SUCCESS', 'FAILED'
    
    -- Métricas
    records_extracted INT DEFAULT 0,         -- Registros leídos de historico
    records_loaded INT DEFAULT 0,            -- Registros escritos en agregadas
    records_failed INT DEFAULT 0,            -- Registros con error
    
    -- Errores
    error_message TEXT,                      -- Mensaje de error (si FAILED)
    error_code VARCHAR(50),                  -- Código de error
    
    -- Metadatos
    executed_by VARCHAR(100),                -- 'cron', 'manual', etc.
    parameters JSON,                         -- Parámetros de ejecución
    
    -- Índices
    INDEX idx_status (status),
    INDEX idx_start_time (start_time),
    INDEX idx_job_name (job_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

#### **2.4.3 Modelo Django**

```python
# apps/ivr/models.py

class JobExecutionLog(models.Model):
    """
    Log de ejecuciones del ETL.
    
    Actualizado por: Stored Procedure ETL
    Django: Readonly (managed=False)
    Usado por: apps/pipeline/ para monitoreo
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('RUNNING', 'Ejecutando'),
        ('SUCCESS', 'Exitoso'),
        ('FAILED', 'Fallido'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    
    # Identificación
    job_name = models.CharField(
        max_length=100,
        verbose_name="Nombre del Job"
    )
    
    # Timestamps
    start_time = models.DateTimeField(
        verbose_name="Inicio"
    )
    end_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fin"
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="Estado"
    )
    
    # Métricas
    records_extracted = models.IntegerField(
        default=0,
        verbose_name="Registros Extraídos"
    )
    records_loaded = models.IntegerField(
        default=0,
        verbose_name="Registros Cargados"
    )
    records_failed = models.IntegerField(
        default=0,
        verbose_name="Registros Fallidos"
    )
    
    # Errores
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mensaje de Error"
    )
    error_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Código de Error"
    )
    
    # Metadatos
    executed_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ejecutado Por"
    )
    parameters = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Parámetros"
    )
    
    class Meta:
        app_label = 'ivr'
        managed = False
        db_table = 'job_execution_log'
        verbose_name = 'Log de Ejecución ETL'
        verbose_name_plural = 'Logs de Ejecución ETL'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.job_name} - {self.start_time} - {self.status}"
    
    @property
    def duration_seconds(self):
        """Duración de la ejecución en segundos."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds()
        return None
```

---

### 2.5 DIDs y Filtros

#### **2.5.1 DIDs Configurados**

```python
# apps/ivr/constants.py

# DIDs del sistema
DID_PUEBLA = '19020084'
DID_NACIONAL_A = '19028031'
DID_NACIONAL_B = '19020001'

ALLOWED_DIDS = [
    DID_PUEBLA,
    DID_NACIONAL_A,
    DID_NACIONAL_B,
]

# Mapeo DID → Nombre legible
DID_NAMES = {
    '19020084': 'Puebla',
    '19028031': 'Nacional A',
    '19020001': 'Nacional B',
}

# Función helper
def get_did_name(did: str) -> str:
    """Obtiene nombre legible del DID."""
    return DID_NAMES.get(did, f'DID {did}')
```

---

#### **2.5.2 Filtros Comunes en Consultas**

```python
# apps/reports/services.py

from apps.ivr.models import CallRecord, QuarterlyReport
from apps.ivr.constants import ALLOWED_DIDS


class ReportService:
    """Servicio de reportes."""
    
    @staticmethod
    def get_calls_by_did(did: str, start_date, end_date):
        """
        Obtiene llamadas filtradas por DID.
        
        Args:
            did: DID a filtrar (ej: '19020084')
            start_date: Fecha inicio
            end_date: Fecha fin
        
        Returns:
            QuerySet de llamadas
        """
        # Validar DID
        if did not in ALLOWED_DIDS:
            raise ValueError(f"DID {did} no permitido")
        
        # Obtener modelo según fecha
        Model = ReportService.get_historico_model(start_date)
        
        # Consulta con filtro DID
        return Model.objects.filter(
            cDID_800Transfer=did,
            dFecha__gte=start_date,
            dFecha__lte=end_date
        )
    
    @staticmethod
    def get_aggregated_by_did(trimestre: str, did: str = None):
        """
        Obtiene datos agregados por DID.
        
        Args:
            trimestre: 'Q1', 'Q2', 'Q3'
            did: Opcional, filtrar por DID específico
        
        Returns:
            QuerySet de reportes agregados
        """
        queryset = QuarterlyReport.objects.filter(
            trimestre=trimestre
        )
        
        if did:
            # Filtrar por servicio_800 (nombre del DID)
            did_name = get_did_name(did)
            queryset = queryset.filter(servicio_800=did_name)
        
        return queryset
```

---

### 2.6 Esquema Completo de MariaDB

```
┌─────────────────────────────────────────────────────────────────┐
│ DATABASE: ivr_database (MariaDB)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ TABLAS FUENTE (Raw Data):                                      │
│ ├─ tbl_historico_t1_2025    (Q1: Ene-Mar)                      │
│ ├─ tbl_historico_t2_2025    (Q2: Abr-Jun)                      │
│ └─ tbl_historico_t3_2025    (Q3: Jul-Sep)                      │
│                                                                 │
│ TABLAS AGREGADAS (ETL Output):                                 │
│ ├─ tbl_reporte_trimestral                                      │
│ ├─ tbl_reporte_transferencias                                  │
│ ├─ tbl_reporte_menu_agregado                                   │
│ ├─ tbl_reporte_llamadas_abandonadas                            │
│ ├─ tbl_reporte_clientes_unicos                                 │
│ ├─ tbl_reporte_promedio_clientes                               │
│ └─ tbl_reporte_menu_errores                                    │
│                                                                 │
│ TABLA DE CONTROL:                                              │
│ └─ job_execution_log                                           │
│                                                                 │
│ STORED PROCEDURES:                                             │
│ └─ sp_etl_daily()  (ejecutado por cron)                        │
│                                                                 │
│ USUARIOS:                                                       │
│ ├─ etl_user        (read/write para SP)                        │
│ └─ ivr_readonly    (read only para Django)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

<a name="3-proceso-etl"></a>
## 3. PROCESO ETL

### 3.1 Stored Procedure ETL (MariaDB)

#### **3.1.1 Descripción General**

```
NOMBRE: sp_etl_daily
LENGUAJE: SQL (MariaDB)
EJECUTADO POR: Cron (diario, 2:00 AM)
DURACIÓN: ~10-15 minutos
TIMEOUT: 300 segundos (CNST-004)

FLUJO:
1. Registrar inicio en job_execution_log
2. Leer de tbl_historico_t1/t2/t3 (según fecha)
3. Transformar y agregar datos
4. Escribir en tbl_reporte_*
5. Actualizar job_execution_log con resultado
```

---

#### **3.1.2 Pseudocódigo del SP**

```sql
DELIMITER $$

CREATE PROCEDURE sp_etl_daily()
BEGIN
    DECLARE v_job_id BIGINT;
    DECLARE v_start_time DATETIME;
    DECLARE v_extracted INT DEFAULT 0;
    DECLARE v_loaded INT DEFAULT 0;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- En caso de error, actualizar log con FAILED
        UPDATE job_execution_log
        SET status = 'FAILED',
            end_time = NOW(),
            error_message = 'Error en ejecución del ETL'
        WHERE id = v_job_id;
        
        ROLLBACK;
    END;
    
    -- PASO 1: Registrar inicio
    SET v_start_time = NOW();
    INSERT INTO job_execution_log (
        job_name,
        start_time,
        status,
        executed_by
    ) VALUES (
        'etl_daily',
        v_start_time,
        'RUNNING',
        'cron'
    );
    SET v_job_id = LAST_INSERT_ID();
    
    START TRANSACTION;
    
    -- PASO 2: Determinar trimestre actual
    SET @trimestre = CASE
        WHEN MONTH(CURDATE()) BETWEEN 1 AND 3 THEN 'Q1'
        WHEN MONTH(CURDATE()) BETWEEN 4 AND 6 THEN 'Q2'
        WHEN MONTH(CURDATE()) BETWEEN 7 AND 9 THEN 'Q3'
        ELSE 'Q4'
    END;
    
    -- PASO 3: Extraer y transformar (ejemplo para tbl_reporte_trimestral)
    INSERT INTO tbl_reporte_trimestral (
        trimestre,
        anio,
        fecha,
        servicio_800,
        total_llamadas,
        llamadas_completadas,
        llamadas_abandonadas,
        clientes_unicos,
        tasa_abandono
    )
    SELECT
        @trimestre AS trimestre,
        YEAR(CURDATE()) AS anio,
        CURDATE() AS fecha,
        CASE
            WHEN cDID_800Transfer = '19020084' THEN 'Puebla'
            WHEN cDID_800Transfer = '19028031' THEN 'Nacional A'
            ELSE 'Otros'
        END AS servicio_800,
        COUNT(*) AS total_llamadas,
        SUM(CASE WHEN cEstado = 'COMPLETADA' THEN 1 ELSE 0 END) AS llamadas_completadas,
        SUM(CASE WHEN cEstado = 'ABANDONADA' THEN 1 ELSE 0 END) AS llamadas_abandonadas,
        COUNT(DISTINCT cTelefono_Origen) AS clientes_unicos,
        ROUND(
            (SUM(CASE WHEN cEstado = 'ABANDONADA' THEN 1 ELSE 0 END) / COUNT(*)) * 100,
            2
        ) AS tasa_abandono
    FROM
        CASE @trimestre
            WHEN 'Q1' THEN tbl_historico_t1_2025
            WHEN 'Q2' THEN tbl_historico_t2_2025
            WHEN 'Q3' THEN tbl_historico_t3_2025
        END
    WHERE
        dFecha = CURDATE() - INTERVAL 1 DAY  -- Procesar día anterior
    GROUP BY
        servicio_800
    ON DUPLICATE KEY UPDATE
        total_llamadas = VALUES(total_llamadas),
        llamadas_completadas = VALUES(llamadas_completadas),
        llamadas_abandonadas = VALUES(llamadas_abandonadas),
        clientes_unicos = VALUES(clientes_unicos),
        tasa_abandono = VALUES(tasa_abandono),
        updated_at = NOW();
    
    SET v_loaded = ROW_COUNT();
    
    -- PASO 4: Repetir para otras tablas agregadas
    -- (tbl_reporte_transferencias, tbl_reporte_llamadas_abandonadas, etc.)
    
    -- PASO 5: Actualizar log con SUCCESS
    UPDATE job_execution_log
    SET status = 'SUCCESS',
        end_time = NOW(),
        records_extracted = v_extracted,
        records_loaded = v_loaded
    WHERE id = v_job_id;
    
    COMMIT;
END$$

DELIMITER ;
```

---

#### **3.1.3 Scripts SQL Reales (Referencia)**

Los siguientes scripts SQL fueron proporcionados y sirven de **base** para el Stored Procedure:

```
SCRIPTS SQL REALES:
├─ q_REPTRIM021_LLAMADAS_ABDANDONADAS.sql
│  → Genera tbl_reporte_llamadas_abandonadas
│
├─ q_REPTRIM011_CLIENTES_UNICOS.sql
│  → Genera tbl_reporte_clientes_unicos
│
├─ q_REPTRIM031_PROMEDIO_CLIENTES.sql
│  → Genera tbl_reporte_promedio_clientes
│
├─ q_REPTRIM041_CLIENTES_MENU.sql
│  → Genera tbl_reporte_clientes_menu
│
├─ q_REPTRIM121_LLAMADAS_MENU.sql
│  → Genera tbl_reporte_llamadas_menu
│
├─ q_REP_DETALLE_TRANSFERENCIA_MENU_OPCION-v.0.3.1.sql
│  → Genera tbl_reporte_transferencias
│
└─ q_cMENU_ERROR.sql
   → Genera tbl_reporte_menu_errores
```

**NOTA:** Estos scripts se ejecutan **dentro** del Stored Procedure `sp_etl_daily()` de forma secuencial.

---

### 3.2 Trigger Diario (Cron 2:00 AM)

#### **3.2.1 Configuración del Cron**

```bash
# /etc/cron.d/etl-daily
# Ejecuta el ETL todos los días a las 2:00 AM

# Minuto Hora Día Mes DiaSemana Usuario   Comando
0        2    *   *   *         etl_user  /usr/local/bin/run_etl.sh

# Log de ejecuciones
# Archivo: /var/log/etl/etl_daily.log
```

---

#### **3.2.2 Script de Ejecución**

```bash
#!/bin/bash
# /usr/local/bin/run_etl.sh
# Script que ejecuta el Stored Procedure ETL

set -e  # Exit on error

# Configuración
DB_HOST="mariadb-server.local"
DB_USER="etl_user"
DB_PASS="${ETL_DB_PASSWORD}"  # Variable de entorno
DB_NAME="ivr_database"
LOG_FILE="/var/log/etl/etl_daily_$(date +%Y%m%d).log"
MAX_RETRIES=3
TIMEOUT=300  # CNST-004: 300 segundos

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Iniciando ETL diario"
log "=========================================="

# Función de ejecución con reintentos
run_etl() {
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        log "Intento $attempt de $MAX_RETRIES"
        
        # Ejecutar Stored Procedure con timeout
        if timeout $TIMEOUT mysql \
            -h "$DB_HOST" \
            -u "$DB_USER" \
            -p"$DB_PASS" \
            "$DB_NAME" \
            -e "CALL sp_etl_daily();" >> "$LOG_FILE" 2>&1
        then
            log "✓ ETL ejecutado exitosamente"
            return 0
        else
            log "✗ ETL falló en intento $attempt"
            attempt=$((attempt + 1))
            
            if [ $attempt -le $MAX_RETRIES ]; then
                log "Reintentando en 30 segundos..."
                sleep 30
            fi
        fi
    done
    
    log "✗ ETL falló después de $MAX_RETRIES intentos"
    return 1
}

# Ejecutar ETL
if run_etl; then
    log "ETL completado con éxito"
    exit 0
else
    log "ETL falló - revisar logs"
    
    # Enviar notificación de error (opcional)
    # mail -s "ETL FAILED" admin@empresa.com < "$LOG_FILE"
    
    exit 1
fi
```

---

#### **3.2.3 Monitoreo del Cron**

```python
# apps/pipeline/services.py

from apps.ivr.models import JobExecutionLog
from datetime import datetime, timedelta


class ETLMonitoringService:
    """Servicio de monitoreo del ETL."""
    
    @staticmethod
    def check_etl_status() -> dict:
        """
        Verifica el estado del último ETL.
        
        Returns:
            {
                'status': 'SUCCESS' | 'FAILED' | 'RUNNING' | 'NEVER_RUN',
                'last_execution': datetime,
                'duration_seconds': int,
                'records_loaded': int,
                'error_message': str (si FAILED)
            }
        """
        last_execution = JobExecutionLog.objects.filter(
            job_name='etl_daily'
        ).order_by('-start_time').first()
        
        if not last_execution:
            return {
                'status': 'NEVER_RUN',
                'message': 'ETL nunca ha sido ejecutado'
            }
        
        return {
            'status': last_execution.status,
            'last_execution': last_execution.start_time,
            'duration_seconds': last_execution.duration_seconds,
            'records_loaded': last_execution.records_loaded,
            'error_message': last_execution.error_message
        }
    
    @staticmethod
    def check_etl_should_have_run() -> bool:
        """
        Verifica si el ETL debería haber corrido hoy.
        
        Returns:
            True si debería haber corrido y NO lo hizo
        """
        now = datetime.now()
        
        # ETL corre a las 2:00 AM
        # Si son más de las 3:00 AM, debería haber corrido
        if now.hour >= 3:
            today_start = now.replace(hour=0, minute=0, second=0)
            
            # Buscar ejecución de hoy
            today_execution = JobExecutionLog.objects.filter(
                job_name='etl_daily',
                start_time__gte=today_start
            ).first()
            
            return today_execution is None  # True si NO hay ejecución hoy
        
        return False  # Aún no es hora de verificar
```

---

### 3.3 Transformaciones (SQL Real de Scripts)

#### **3.3.1 Ejemplo: Llamadas Abandonadas (RPT-TR-021)**

```sql
-- Basado en: q_REPTRIM021_LLAMADAS_ABDANDONADAS.sql

INSERT INTO tbl_reporte_llamadas_abandonadas (
    trimestre,
    fecha,
    did,
    menu,
    total_abandonadas,
    tiempo_espera_promedio_seg,
    abandonadas_antes_30seg,
    abandonadas_30_60seg,
    abandonadas_mas_60seg,
    tasa_abandono
)
SELECT
    @trimestre AS trimestre,
    h.dFecha AS fecha,
    h.cDID_800Transfer AS did,
    h.cMenu AS menu,
    
    -- Total abandonadas
    COUNT(*) AS total_abandonadas,
    
    -- Tiempo promedio de espera
    AVG(h.nTiempoEsperaSegundos) AS tiempo_espera_promedio_seg,
    
    -- Clasificación por tiempo
    SUM(CASE WHEN h.nTiempoEsperaSegundos < 30 THEN 1 ELSE 0 END) AS abandonadas_antes_30seg,
    SUM(CASE WHEN h.nTiempoEsperaSegundos BETWEEN 30 AND 60 THEN 1 ELSE 0 END) AS abandonadas_30_60seg,
    SUM(CASE WHEN h.nTiempoEsperaSegundos > 60 THEN 1 ELSE 0 END) AS abandonadas_mas_60seg,
    
    -- Tasa de abandono
    ROUND(
        (COUNT(*) / (
            SELECT COUNT(*)
            FROM tbl_historico_t1_2025
            WHERE dFecha = h.dFecha
              AND cDID_800Transfer = h.cDID_800Transfer
              AND cMenu = h.cMenu
        )) * 100,
        2
    ) AS tasa_abandono

FROM
    tbl_historico_t1_2025 h
WHERE
    h.cEstado = 'ABANDONADA'
    AND h.dFecha = CURDATE() - INTERVAL 1 DAY
GROUP BY
    h.dFecha,
    h.cDID_800Transfer,
    h.cMenu
ON DUPLICATE KEY UPDATE
    total_abandonadas = VALUES(total_abandonadas),
    tiempo_espera_promedio_seg = VALUES(tiempo_espera_promedio_seg),
    abandonadas_antes_30seg = VALUES(abandonadas_antes_30seg),
    abandonadas_30_60seg = VALUES(abandonadas_30_60seg),
    abandonadas_mas_60seg = VALUES(abandonadas_mas_60seg),
    tasa_abandono = VALUES(tasa_abandono);
```

---

#### **3.3.2 Ejemplo: Clientes Únicos (RPT-TR-011)**

```sql
-- Basado en: q_REPTRIM011_CLIENTES_UNICOS.sql

INSERT INTO tbl_reporte_clientes_unicos (
    trimestre,
    fecha,
    did,
    total_clientes_unicos,
    total_llamadas,
    promedio_llamadas_por_cliente
)
SELECT
    @trimestre AS trimestre,
    h.dFecha AS fecha,
    h.cDID_800Transfer AS did,
    
    -- Clientes únicos
    COUNT(DISTINCT h.cTelefono_Origen) AS total_clientes_unicos,
    
    -- Total de llamadas
    COUNT(*) AS total_llamadas,
    
    -- Promedio de llamadas por cliente
    ROUND(
        COUNT(*) / COUNT(DISTINCT h.cTelefono_Origen),
        2
    ) AS promedio_llamadas_por_cliente

FROM
    tbl_historico_t1_2025 h
WHERE
    h.dFecha = CURDATE() - INTERVAL 1 DAY
    AND h.cTelefono_Origen IS NOT NULL
    AND h.cTelefono_Origen != ''
GROUP BY
    h.dFecha,
    h.cDID_800Transfer
ON DUPLICATE KEY UPDATE
    total_clientes_unicos = VALUES(total_clientes_unicos),
    total_llamadas = VALUES(total_llamadas),
    promedio_llamadas_por_cliente = VALUES(promedio_llamadas_por_cliente);
```

---

### 3.4 Gestión de Trimestres

#### **3.4.1 Lógica de Trimestres**

```python
# apps/ivr/utils.py

from datetime import date
from typing import Literal


TrimestreType = Literal['Q1', 'Q2', 'Q3']


def get_trimestre_from_date(fecha: date) -> TrimestreType:
    """
    Determina el trimestre según la fecha.
    
    Args:
        fecha: Fecha a evaluar
    
    Returns:
        'Q1', 'Q2', o 'Q3'
    
    Raises:
        ValueError: Si el mes está fuera de los trimestres definidos
    """
    mes = fecha.month
    
    if 1 <= mes <= 3:
        return 'Q1'
    elif 4 <= mes <= 6:
        return 'Q2'
    elif 7 <= mes <= 9:
        return 'Q3'
    else:
        raise ValueError(
            f"Mes {mes} fuera de trimestres definidos (Q1-Q3). "
            "Sistema solo maneja Ene-Sep."
        )


def get_table_suffix_from_trimestre(trimestre: TrimestreType) -> str:
    """
    Obtiene sufijo de tabla según trimestre.
    
    Args:
        trimestre: 'Q1', 'Q2', 'Q3'
    
    Returns:
        't1', 't2', 't3'
    """
    mapping = {
        'Q1': 't1',
        'Q2': 't2',
        'Q3': 't3',
    }
    return mapping[trimestre]


def get_date_range_for_trimestre(
    trimestre: TrimestreType,
    anio: int
) -> tuple[date, date]:
    """
    Obtiene rango de fechas para un trimestre.
    
    Args:
        trimestre: 'Q1', 'Q2', 'Q3'
        anio: Año
    
    Returns:
        (fecha_inicio, fecha_fin)
    """
    ranges = {
        'Q1': (date(anio, 1, 1), date(anio, 3, 31)),
        'Q2': (date(anio, 4, 1), date(anio, 6, 30)),
        'Q3': (date(anio, 7, 1), date(anio, 9, 30)),
    }
    return ranges[trimestre]
```

---

#### **3.4.2 Uso en Consultas**

```python
# apps/reports/services.py

from apps.ivr.utils import get_trimestre_from_date, get_date_range_for_trimestre
from apps.ivr.models import CallRecord, CallRecord, CallRecord


class ReportService:
    
    @staticmethod
    def get_historico_for_trimestre(trimestre: str):
        """
        Retorna el modelo Historico correspondiente al trimestre.
        
        Args:
            trimestre: 'Q1', 'Q2', 'Q3'
        
        Returns:
            Modelo Django (CallRecord/T2/T3)
        """
        mapping = {
            'Q1': CallRecord,
            'Q2': CallRecord,
            'Q3': CallRecord,
        }
        
        if trimestre not in mapping:
            raise ValueError(f"Trimestre inválido: {trimestre}")
        
        return mapping[trimestre]
    
    @staticmethod
    def get_data_by_trimestre(trimestre: str, anio: int):
        """
        Obtiene todos los datos de un trimestre.
        
        Args:
            trimestre: 'Q1', 'Q2', 'Q3'
            anio: Año
        
        Returns:
            QuerySet de registros
        """
        # Obtener modelo
        Model = ReportService.get_historico_for_trimestre(trimestre)
        
        # Obtener rango de fechas
        start_date, end_date = get_date_range_for_trimestre(trimestre, anio)
        
        # Consulta
        return Model.objects.filter(
            dFecha__gte=start_date,
            dFecha__lte=end_date
        )
```

---

### 3.5 Flujo ETL Completo

```
┌─────────────────────────────────────────────────────────────────┐
│ FLUJO ETL DIARIO - DETALLE COMPLETO                             │
└─────────────────────────────────────────────────────────────────┘

TIEMPO: 2:00 AM (diario)
DURACIÓN: ~10-15 minutos
TIMEOUT: 300 segundos (CNST-004)

PASO 1: INICIO
├─ Cron ejecuta /usr/local/bin/run_etl.sh
├─ Script llama a sp_etl_daily()
└─ SP inserta en job_execution_log (status='RUNNING')

PASO 2: EXTRACCIÓN
├─ Determinar trimestre actual (Q1/Q2/Q3)
├─ Seleccionar tabla fuente:
│  ├─ Q1 → tbl_historico_t1_2025
│  ├─ Q2 → tbl_historico_t2_2025
│  └─ Q3 → tbl_historico_t3_2025
├─ Leer registros del día anterior (dFecha = CURDATE() - 1)
└─ Registros extraídos: ~5,000 - 10,000

PASO 3: TRANSFORMACIÓN
├─ Ejecutar queries SQL de agregación:
│  ├─ q_REPTRIM021 (llamadas abandonadas)
│  ├─ q_REPTRIM011 (clientes únicos)
│  ├─ q_REPTRIM031 (promedio clientes)
│  ├─ q_REPTRIM041 (clientes por menú)
│  ├─ q_REPTRIM121 (llamadas por menú)
│  ├─ q_REP_DETALLE_TRANSFERENCIA (transferencias)
│  └─ q_cMENU_ERROR (errores de menú)
├─ Cálculos realizados:
│  ├─ COUNT(*) para totales
│  ├─ COUNT(DISTINCT) para únicos
│  ├─ AVG() para promedios
│  ├─ SUM(CASE WHEN...) para clasificaciones
│  └─ ROUND(...) para porcentajes
└─ Datos transformados: ~50-100 registros agregados

PASO 4: CARGA
├─ INSERT INTO tbl_reporte_* ... ON DUPLICATE KEY UPDATE
├─ Actualizar o insertar según uniqueness (trimestre+fecha+did+menu)
├─ 7 tablas agregadas actualizadas
└─ Registros cargados: ~50-100

PASO 5: FINALIZACIÓN
├─ UPDATE job_execution_log:
│  ├─ status = 'SUCCESS'
│  ├─ end_time = NOW()
│  ├─ records_extracted = 5000
│  └─ records_loaded = 75
├─ COMMIT transaction
└─ Script retorna exit 0

EN CASO DE ERROR:
├─ EXIT HANDLER captura SQLEXCEPTION
├─ UPDATE job_execution_log:
│  ├─ status = 'FAILED'
│  ├─ error_message = '...'
│  └─ error_code = '...'
├─ ROLLBACK transaction
└─ Script reintenta (hasta 3 veces)

MONITOREO:
├─ Logs en /var/log/etl/etl_daily_YYYYMMDD.log
├─ apps/pipeline/ consulta job_execution_log
└─ GET /api/v1/pipeline/status/ retorna estado
```

---

**FIN DE PARTE 1/3**

**Continúa en:** ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_2.md

---

**Resumen Parte 1:**
- ✅ Sección 1: Resumen Ejecutivo (arquitectura en una página)
- ✅ Sección 2: Arquitectura de Datos MariaDB (completa)
  - Tablas históricas (tbl_historico_t1/t2/t3)
  - Tablas agregadas (tbl_reporte_*)
  - Tabla de control (job_execution_log)
  - DIDs y filtros
  - Modelos Django (managed=False)
- ✅ Sección 3: Proceso ETL (completo)
  - Stored Procedure sp_etl_daily()
  - Cron diario (2:00 AM)
  - Scripts SQL reales
  - Gestión de trimestres
  - Flujo completo detallado

**Próxima parte:** Arquitectura Django, APIs, Endpoints, Flujos de Datos
