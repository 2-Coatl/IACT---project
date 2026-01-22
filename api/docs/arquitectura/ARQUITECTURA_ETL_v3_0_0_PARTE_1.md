---
version: 3.0.0
date: 2026-01-19
project: IACT (Sistema Call Center)
type: Arquitectura Técnica
categoria: arquitectura/diseño
titulo: Arquitectura Real del Sistema ETL - Versión Definitiva
componente: ETL (Extract, Transform, Load)
tecnologias: MariaDB, Django, APScheduler, PostgreSQL
scope: Sistema completo (IVR Legacy → Django → API)
audiencia: Desarrolladores, Arquitectos Técnicos
estado: definitivo
base: CLEAN_CODE v3.0.1 + RESTRICCIONES v1.0.0 + RBAC v6.0.0
partes: 1/3
---

# ARQUITECTURA REAL DEL SISTEMA ETL - v3.0.0

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

### PARTE 3/3: INFRAESTRUCTURA Y DEPLOYMENT
7. Jobs Programados (APScheduler)
8. Deployment y Configuración
9. Seguridad
10. Testing y QA

---

## 📚 CONTROL DE VERSIONES

| Versión | Fecha | Cambios | Documentos Base |
|---------|-------|---------|-----------------|
| **3.0.0** | **2026-01-19** | **VERSIÓN DEFINITIVA desde cero** | **CLEAN_CODE v3.0.1 + RESTRICCIONES v1.0.0 + RBAC v6.0.0** |
| 2.0.0 | 2026-01-19 | CLEAN_CODE v3.0.1 aplicado | CLEAN_CODE v3.0.1 |
| 1.0.0 | 2026-01-18 | Versión inicial consolidada | N/A |

---

## 🎯 CAMBIOS EN v3.0.0

**Actualización Mayor:** Este documento ha sido **reescrito completamente desde cero** para cumplir con los 3 documentos maestros definitivos del proyecto IACT.

### Documentos Maestros Aplicados

#### 1. CLEAN_CODE_NAMING_PRINCIPLES v3.0.1 (5 partes, 206KB)
```yaml
Aplicado:
  - Nomenclatura código: inglés, PascalCase/snake_case
  - Comentarios y docstrings: español, formato Google
  - db_table: preserva nomenclatura húngara original
  - Ejemplos: CallRecord, get_dashboard_widgets()
```

#### 2. RESTRICCIONES_ARQUITECTONICAS_IACT v1.0.0 (3 partes, 144KB)
```yaml
Aplicado (14 restricciones críticas):
  - CNST-001: NO email (solo buzón interno)
  - CNST-002: BD IVR readonly (ZERO escritura)
  - CNST-003: NO real-time (updates cada 6-12h)
  - CNST-004: Timeout DB 300s
  - CNST-010: NO Redis (cache locmem/dummy, sessions DB) ⭐
  - CNST-011: NO Cloud (AWS/GCP/Azure) ⭐
  - CNST-012: NO Servicios Externos (Sentry/Twilio) ⭐
  - CNST-013: NO Message Brokers (Celery/RabbitMQ) ⭐
  - CNST-014: NO Containerización (Docker producción) ⭐
  - CNST-007: Límites export (100K CSV, 50K Excel, 10K PDF)
  - CNST-021: Permisos temporales (6 meses máx)
  - CNST-025: Timeout request 90s
  - CNST-030: Logs locales rotating
  - CNST-031: Auditoría completa
```

#### 3. MODELO_RBAC_IACT v6.0.0 (2 partes, 122KB)
```yaml
Aplicado:
  - 46 funciones (42 activas + 4 planificadas)
  - 9 módulos (MOD_Dashboard separado)
  - Nomenclatura v6.0.0:
    - code: RPT_VIEW, DSH_EXP_CSV
    - permission_django: reports.view, dashboard.export.csv
    - status: activo/planificado/deprecado
  - Separación Reports vs Dashboard documentada
```

### Cambios Fundamentales v2.0.0 → v3.0.0

```diff
STACK TECNOLÓGICO:
- Redis (cache, sessions)               + LocMem Cache (dev) / Dummy Cache (prod)
- Celery (async tasks)                  + APScheduler (BackgroundScheduler)
- Docker (producción)                   + Nginx + Gunicorn + Systemd
- AWS S3 (storage)                      + Filesystem local (/opt/iact/)
- Sentry (logging externo)              + Filesystem rotating (/var/log/iact/)

CONFIGURACIÓN DJANGO:
- CACHES: django_redis                  + locmem.LocMemCache
- SESSION_ENGINE: cache                 + backends.db (database)
- DEFAULT_FILE_STORAGE: S3              + FileSystemStorage
- LOGGING: Sentry                       + RotatingFileHandler

RBAC:
- reports.view_report                   + reports.view
- dashboard.view_dashboard              + dashboard.view
- 42 funciones                          + 46 funciones (4 planificadas)
- 8 módulos                             + 9 módulos (MOD_Dashboard)

DEPLOYMENT:
- docker-compose.yml                    + nginx.conf + gunicorn.conf
- Containers                            + Systemd unit files
```

---

<a name="1-resumen-ejecutivo"></a>

## 1. RESUMEN EJECUTIVO

### 1.1 Arquitectura en una Página

```
┌─────────────────────────────────────────────────────────────────┐
│ ARQUITECTURA REAL DEL SISTEMA ETL - IACT CALL CENTER v3.0.0    │
└─────────────────────────────────────────────────────────────────┘

DOCUMENTOS MAESTROS:
  ✅ CLEAN_CODE v3.0.1     → Nomenclatura + Estándares Código
  ✅ RESTRICCIONES v1.0.0  → 14 Restricciones Críticas
  ✅ RBAC v6.0.0           → 46 Funciones + 9 Módulos

ORIGEN DE DATOS:
┌──────────────────┐
│  IVR Legacy      │  → Sistema externo (fuera del control de Django)
│  (Sistema PBX)   │  → Genera CDRs (Call Detail Records)
└────────┬─────────┘  → Alimenta MariaDB en tiempo real
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ BASE DE DATOS: MariaDB (IVR_LEGACY) - READONLY (CNST-002)      │
├─────────────────────────────────────────────────────────────────┤
│ TABLAS FUENTE:                                                  │
│ ├─ tbl_historico_t1_2025   (Trimestre 1: Ene-Mar)              │
│ ├─ tbl_historico_t2_2025   (Trimestre 2: Abr-Jun)              │
│ └─ tbl_historico_t3_2025   (Trimestre 3: Jul-Sep)              │
│                                                                 │
│ ETL (Stored Procedure):                                         │
│ ├─ Ejecutado por: APScheduler (6-12h) + Cron backup            │
│ ├─ Lenguaje: SQL puro (MariaDB)                                │
│ ├─ Función: sp_etl_daily() agrega datos → tbl_reporte_*        │
│ └─ RESTRICCIÓN: CNST-013 (NO Celery, SÍ APScheduler)           │
│                                                                 │
│ TABLAS AGREGADAS (salida del ETL):                             │
│ ├─ tbl_reporte_trimestral                                      │
│ ├─ tbl_reporte_transferencias                                  │
│ ├─ tbl_reporte_clientes                                        │
│ ├─ tbl_reporte_abandonadas                                     │
│ ├─ tbl_reporte_detalle_transferencias                          │
│ ├─ tbl_reporte_menus_performance                               │
│ └─ tbl_reporte_menu_errores                                    │
│                                                                 │
│ CONTROL ETL:                                                    │
│ └─ job_execution_log (estado, timestamps, errores)             │
└─────────────────────────────────────────────────────────────────┘
         │
         │ Django Database Router (IVRRouter)
         │ ├─ db_for_read()  → 'ivr_legacy' ✅
         │ ├─ db_for_write() → None (BLOQUEADO) ✅
         │ └─ allow_migrate() → False (SIN migraciones) ✅
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ APLICACIÓN DJANGO (Backend)                                     │
├─────────────────────────────────────────────────────────────────┤
│ Framework: Django 4.2 LTS + DRF 3.14+                           │
│ BD Analytics: PostgreSQL 14+ (DEFAULT)                          │
│ Cache: LocMem (dev) / Dummy (prod) - CNST-010 ❌ NO Redis      │
│ Sessions: Database Backend - CNST-010 ❌ NO Redis              │
│ Jobs: APScheduler - CNST-013 ❌ NO Celery                      │
│ Storage: Filesystem (/opt/iact/) - CNST-011 ❌ NO S3           │
│ Logging: Rotating local - CNST-012 ❌ NO Sentry                │
│                                                                 │
│ APPS PRINCIPALES (CLEAN_CODE v3.0.1):                           │
│ ├─ apps/ivr/           → Modelos IVR (managed=False, readonly) │
│ ├─ apps/reports/       → Generación reportes (POST endpoints)  │
│ ├─ apps/dashboard/     → Visualización (GET endpoints)         │
│ ├─ apps/pipeline/      → Monitoreo ETL + APScheduler           │
│ ├─ apps/access/        → RBAC v6.0.0 (46 funciones)            │
│ ├─ apps/authentication/→ Login/Logout (Django auth)            │
│ ├─ apps/users/         → CRUD usuarios                         │
│ ├─ apps/alerts/        → Buzón interno (CNST-001)              │
│ └─ apps/audit/         → Auditoría completa (CNST-031)         │
│                                                                 │
│ APPS SOPORTE:                                                   │
│ ├─ apps/core/          → Modelos abstractos (TimeStampedModel) │
│ └─ apps/utils/         → Funciones utilitarias                 │
└─────────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ API REST (DRF)                                                  │
├─────────────────────────────────────────────────────────────────┤
│ RBAC v6.0.0:                                                    │
│ ├─ 46 funciones (42 activas + 4 planificadas)                  │
│ ├─ Decorador: @require_function('reports.view')                │
│ └─ Permission classes: HasFunction, DynamicFunctionPermission  │
│                                                                 │
│ ENDPOINTS REPORTES (POST):                                      │
│ ├─ /api/v1/reports/abandonadas/                                │
│ ├─ /api/v1/reports/clientes/                                   │
│ ├─ /api/v1/reports/transferencias/                             │
│ ├─ /api/v1/reports/detalle-transferencias/                     │
│ └─ /api/v1/reports/menu-errores/                               │
│                                                                 │
│ ENDPOINTS DASHBOARDS (GET):                                     │
│ ├─ /api/v1/dashboard/metricas-trimestrales/                    │
│ ├─ /api/v1/dashboard/analisis-clientes/                        │
│ └─ /api/v1/dashboard/performance-ivr/                          │
│                                                                 │
│ LÍMITES (CNST-007):                                             │
│ ├─ CSV export: 100,000 registros máx                           │
│ ├─ Excel export: 50,000 registros máx                          │
│ └─ PDF export: 10,000 registros máx (planificado)              │
│                                                                 │
│ TIMEOUTS:                                                       │
│ ├─ Request: 90s (CNST-025)                                     │
│ └─ DB Query: 300s (CNST-004)                                   │
└─────────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (React/Vue)                                            │
│ ├─ Dashboard con widgets (KPI, Charts, Tables)                 │
│ ├─ Generación de reportes                                      │
│ ├─ Exportación (Excel, CSV)                                    │
│ └─ NOTA: Datos estáticos (6-12h desfase) - CNST-003            │
└─────────────────────────────────────────────────────────────────┘

DEPLOYMENT (CNST-014):
┌─────────────────────────────────────────────────────────────────┐
│ ❌ NO Docker/Kubernetes (producción)                           │
│ ✅ Nginx + Gunicorn + Systemd (tradicional)                    │
│ ✅ Estructura: /opt/iact/{app,media,logs,secrets}/             │
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
Documentos: N/A (decisión histórica)
```

---

#### **DECISIÓN 2: Django managed=False (Readonly) - CNST-002**

```yaml
Decisión: Modelos Django con managed=False para tablas MariaDB
Razón: 
  - Django NO gestiona el schema de IVR_LEGACY
  - Django solo LEE datos (readonly) ← CNST-002
  - El schema lo gestiona el ETL (Stored Procedure)
  - Database Router bloquea escrituras (db_for_write() → None)
  
Código (CLEAN_CODE v3.0.1):
  class CallRecord(models.Model):
      """
      Registro de llamada del sistema IVR Legacy.
      
      IMPORTANTE: Modelo readonly, managed=False.
      BD: MariaDB (ivr_legacy)
      Tabla: tbl_historico_t{1,2,3}_2025
      """
      class Meta:
          managed = False  # ✅ Django NO gestiona schema
          db_table = 'tbl_historico_t1_2025'  # ✅ Preserva nombre húngaro

Estado: Definitivo
Referencias: CNST-002, CLEAN_CODE v3.0.1 (Parte 4, Sección 4.2)
```

---

#### **DECISIÓN 3: ETL como Stored Procedure (no Python) - CNST-013**

```yaml
Decisión: ETL implementado como Stored Procedure en MariaDB
Razón:
  - ETL ya existe y funciona
  - Lenguaje: SQL puro (MariaDB)
  - Ejecutado por: APScheduler (6-12h) + Cron backup
  - ❌ NO usar Celery (CNST-013)
  - ❌ NO usar Airflow
  - ❌ NO usar Python ETL custom
  
Alternativas consideradas y rechazadas:
  - Celery + Python ETL → ❌ CNST-013 (NO Celery)
  - Django management commands → Menos eficiente que SQL
  - Airflow → Over-engineering para el scope
  
Ejecutor Permitido:
  - APScheduler (BackgroundScheduler) ← CNST-013 ✅
  - Cron (backup) ✅
  
Estado: Definitivo
Referencias: CNST-013, RESTRICCIONES v1.0.0 (Parte 1, Sección 1.7)
```

---

#### **DECISIÓN 4: Separación Reports vs Dashboard - RBAC v6.0.0**

```yaml
Decisión: apps/reports/ y apps/dashboard/ como apps independientes
Razón:
  - Reports: Generación bajo demanda (POST), archivos descargables
  - Dashboard: Visualización tiempo real (GET), widgets en vivo
  - Responsabilidades diferentes (Single Responsibility Principle)
  - RBAC separado:
    - reports.view, reports.create, reports.export.csv
    - dashboard.view, dashboard.export.csv, dashboard.export.excel
  - MOD_Reports: 6 funciones
  - MOD_Dashboard: 6 funciones (nuevo módulo v6.0.0)
  
Alternativas consideradas: Todo en reports/
Rechazada: Mezclaría responsabilidades, violación SRP
Estado: Definitivo
Referencias: 
  - RBAC v6.0.0 (Parte 1, Sección 3.5 y 3.6)
  - URLS_REPORTES_Y_DASHBOARDS.md
```

---

#### **DECISIÓN 5: Database Router - CNST-002**

```yaml
Decisión: Database Router para separar IVR_LEGACY (MariaDB) de DEFAULT (PostgreSQL)
Razón:
  - apps/ivr/ lee de MariaDB (IVR_LEGACY)
  - Resto de apps escriben a PostgreSQL (DEFAULT)
  - Separación clara de responsabilidades
  - PROTECCIÓN: db_for_write() retorna None para IVR → BLOQUEA escrituras
  
Configuración:
  DATABASE_ROUTERS = ['config.routers.IVRRouter']
  
Código (CLEAN_CODE v3.0.1):
  class IVRRouter:
      """Router para proteger BD IVR de escrituras."""
      ivr_apps = {'ivr'}
      
      def db_for_write(self, model, **hints):
          """Escritura: IVR SIEMPRE None (bloqueado)."""
          if model._meta.app_label in self.ivr_apps:
              return None  # ✅ CNST-002: ZERO escritura a BD IVR
          return 'default'

Estado: Definitivo
Referencias: CNST-002, RESTRICCIONES v1.0.0 (Parte 1, Sección 1.3)
```

---

#### **DECISIÓN 6: NO Redis - CNST-010**

```yaml
Decisión: NO usar Redis para cache ni sessions
Razón:
  - CNST-010: Redis PROHIBIDO
  - Dependencia externa innecesaria
  - Sistema on-premise sin cloud
  - Complejidad adicional no justificada
  
Alternativas Obligatorias:
  - Cache: LocMem (dev), Dummy (prod)
  - Sessions: Database Backend (django_session table)
  
Configuración:
  CACHES = {
      'default': {
          'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
          'LOCATION': 'iact-cache',
      }
  }
  
  SESSION_ENGINE = 'django.contrib.sessions.backends.db'

Estado: Definitivo e Inmutable
Referencias: CNST-010, RESTRICCIONES v1.0.0 (Parte 1, Sección 1.2)
```

---

#### **DECISIÓN 7: APScheduler (NO Celery) - CNST-013**

```yaml
Decisión: APScheduler para jobs programados (NO Celery)
Razón:
  - CNST-013: Celery PROHIBIDO
  - No hay Redis (CNST-010) → No hay broker
  - ETL cada 6-12h (no requiere procesamiento real-time)
  - Arquitectura simplificada
  
Configuración:
  from apscheduler.schedulers.background import BackgroundScheduler
  
  scheduler = BackgroundScheduler()
  scheduler.add_job(
      run_etl,
      trigger='interval',
      hours=6,
      id='etl_job'
  )
  scheduler.start()

Estado: Definitivo e Inmutable
Referencias: CNST-013, RESTRICCIONES v1.0.0 (Parte 1, Sección 1.7)
```

---

#### **DECISIÓN 8: NO Docker Producción - CNST-014**

```yaml
Decisión: Deployment tradicional Nginx + Gunicorn (NO Docker en producción)
Razón:
  - CNST-014: Docker PROHIBIDO en producción
  - Deployment tradicional más simple
  - Systemd para gestión de servicios
  - Sin overhead de containerización
  
Permitido:
  - Docker: Solo desarrollo local ✅
  
Obligatorio Producción:
  - Nginx como reverse proxy
  - Gunicorn como WSGI server
  - Systemd unit files
  - Scripts bash deployment
  
Estado: Definitivo e Inmutable
Referencias: CNST-014, RESTRICCIONES v1.0.0 (Parte 1, Sección 1.8)
```

---

### 1.3 Stack Tecnológico v3.0.0

```
┌──────────────────────┬─────────────────────────────────────────────────┐
│ Componente           │ Tecnología                                      │
├──────────────────────┼─────────────────────────────────────────────────┤
│ Base de Datos IVR    │ MariaDB 10.x (readonly - CNST-002)              │
│ Base de Datos App    │ PostgreSQL 14+                                  │
│ Backend Framework    │ Django 4.2 LTS                                  │
│ API Framework        │ Django REST Framework 3.14+                     │
│ ETL                  │ Stored Procedure (SQL/MariaDB)                  │
│ Trigger ETL          │ APScheduler (6-12h) + Cron backup               │
│ Jobs Programados     │ APScheduler BackgroundScheduler (CNST-013)      │
│ ORM                  │ Django ORM (readonly para IVR)                  │
│ Cache                │ LocMem (dev), Dummy (prod) - NO Redis ❌        │
│ Sessions             │ Database backend (django_session) - NO Redis ❌ │
│ Auth/Permisos        │ RBAC v6.0.0 (apps/access/) - 46 funciones       │
│ Storage              │ FileSystemStorage (/opt/iact/) - NO S3 ❌       │
│ Logging              │ RotatingFileHandler - NO Sentry ❌              │
│ Email                │ NINGUNO - Buzón interno (CNST-001) ❌           │
│ Export               │ openpyxl (Excel), csv (CSV)                     │
│ Web Server           │ Nginx (reverse proxy)                           │
│ WSGI Server          │ Gunicorn                                        │
│ Service Manager      │ Systemd                                         │
│ Frontend             │ React/Vue (fuera de scope)                      │
└──────────────────────┴─────────────────────────────────────────────────┘
```

**Restricciones Aplicadas (RESTRICCIONES v1.0.0):**

| Tecnología PROHIBIDA | CNST | Reemplazo OBLIGATORIO |
|---------------------|------|----------------------|
| Redis | CNST-010 | LocMem/Dummy cache, DB sessions |
| Celery/RabbitMQ | CNST-013 | APScheduler + Cron |
| Docker (prod) | CNST-014 | Nginx + Gunicorn + Systemd |
| AWS S3/GCP/Azure | CNST-011 | FileSystemStorage (/opt/iact/) |
| Sentry/New Relic | CNST-012 | RotatingFileHandler local |
| SendGrid/Twilio | CNST-012 | Buzón interno (apps/alerts/) |
| Email/SMTP | CNST-001 | Buzón interno |

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
├─ Frecuencia:          6-12 horas (configurable)
├─ Ejecutor:            APScheduler (CNST-013) ✅
├─ Backup:              Cron diario 2:00 AM
├─ Timeout máximo:      300 segundos (CNST-004)
└─ Reintentos:          3 (configurado en APScheduler)

LÍMITES API (CNST-007):
├─ Rango fechas:        730 días máx (CNST-006)
├─ CSV export:          100,000 registros máx
├─ Excel export:        50,000 registros máx
├─ PDF export:          10,000 registros máx (planificado - RBAC v6.0.0)
├─ Paginación default:  50 registros
└─ Rate limiting:       100 req/hora (DRF throttling)

TIMEOUTS (RESTRICCIONES v1.0.0):
├─ DB Query:            300s (CNST-004)
├─ Request:             90s (CNST-025)
└─ File Upload:         60s

TABLAS:
├─ Tablas fuente:       3 (tbl_historico_t1/t2/t3)
├─ Tablas agregadas:    7 (tbl_reporte_*)
├─ Tabla control:       1 (job_execution_log)
├─ Campos promedio:     15-20 por tabla
└─ Índices:             Por trimestre, DID, fecha

RBAC v6.0.0:
├─ Módulos:             9 (MOD_Dashboard separado)
├─ Funciones totales:   46
├─ Funciones activas:   42
├─ Funciones planificadas: 4
└─ Grupos:              10 (AGR-001 a AGR-010)
```

---

<a name="2-arquitectura-de-datos-mariadb"></a>

## 2. ARQUITECTURA DE DATOS (MariaDB)

### 2.1 Database IVR_LEGACY

#### **2.1.1 Configuración en Django (CLEAN_CODE v3.0.1)**

```python
# config/settings/base.py

DATABASES = {
    # BD Principal (PostgreSQL) - Escritura de apps Django
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'iact_analytics',
        'USER': 'iact_app',
        'PASSWORD': env('DB_PASSWORD'),  # ✅ CNST-014: Secrets en /opt/iact/secrets/
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 300,  # ✅ CNST-004: Timeout 300s
        },
        'CONN_MAX_AGE': 600,
    },
    
    # BD IVR Legacy (MariaDB) - Solo lectura ← CNST-002
    'ivr_legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ivr_call_center',
        'USER': 'ivr_readonly',  # ✅ Usuario con permisos SELECT ONLY
        'PASSWORD': env('IVR_DB_PASSWORD'),
        'HOST': 'ivr-server.local',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'connect_timeout': 300,  # ✅ CNST-004
        },
        'CONN_MAX_AGE': 600,
    },
}

# Router para proteger BD IVR ← CNST-002
DATABASE_ROUTERS = ['config.routers.IVRRouter']
```

**Notas Importantes:**

1. **Usuario readonly (CNST-002):**
```sql
-- Crear usuario con permisos SOLO de lectura
CREATE USER 'ivr_readonly'@'%' IDENTIFIED BY 'password';
GRANT SELECT ON ivr_call_center.* TO 'ivr_readonly'@'%';
FLUSH PRIVILEGES;

-- ✅ Verificar permisos (debe mostrar SOLO SELECT)
SHOW GRANTS FOR 'ivr_readonly'@'%';
-- GRANT SELECT ON ivr_call_center.* TO 'ivr_readonly'@'%'
```

2. **Secrets (CNST-014):**
```bash
# Passwords en filesystem local (NO en cloud)
/opt/iact/secrets/.env.production
  DB_PASSWORD=xxx
  IVR_DB_PASSWORD=yyy
```

---

#### **2.1.2 Database Router (CLEAN_CODE v3.0.1 + CNST-002)**

```python
# config/routers.py

class IVRRouter:
    """
    Router para proteger BD IVR de escrituras accidentales.
    
    CRÍTICO: Implementa CNST-002 (BD IVR readonly).
    
    Responsabilidades:
    - Rutea lecturas de apps/ivr/ → 'ivr_legacy'
    - Rutea escrituras de apps/ivr/ → None (BLOQUEADO)
    - Bloquea migraciones en BD IVR
    - Permite migraciones solo en 'default'
    
    Referencias:
    - CNST-002: Base de Datos Dual (readonly IVR)
    - CLEAN_CODE v3.0.1: Nomenclatura + Docstrings español
    """
    
    # Apps que usan BD IVR
    ivr_apps = {'ivr'}
    
    def db_for_read(self, model, **hints):
        """
        Rutea lecturas según app.
        
        Args:
            model: Modelo Django
            **hints: Hints adicionales
        
        Returns:
            str: 'ivr_legacy' si es app ivr, 'default' en otro caso
        """
        if model._meta.app_label in self.ivr_apps:
            return 'ivr_legacy'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Rutea escrituras según app.
        
        CRÍTICO: Retorna None para apps/ivr/ → BLOQUEA escrituras.
        Implementa CNST-002: ZERO escritura a BD IVR.
        
        Args:
            model: Modelo Django
            **hints: Hints adicionales
        
        Returns:
            str|None: None si es app ivr (BLOQUEADO), 'default' en otro caso
        """
        if model._meta.app_label in self.ivr_apps:
            # ✅ CNST-002: BLOQUEAR escrituras a BD IVR
            return None
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Permite relaciones solo dentro de la misma BD.
        
        Args:
            obj1: Primer objeto
            obj2: Segundo objeto
            **hints: Hints adicionales
        
        Returns:
            bool|None: True si misma BD, False si diferente, None si no aplica
        """
        db_set = {'default', 'ivr_legacy'}
        
        # Ambos en ivr → permitir
        if (obj1._meta.app_label in self.ivr_apps and 
            obj2._meta.app_label in self.ivr_apps):
            return True
        
        # Uno en ivr, otro no → bloquear
        if (obj1._meta.app_label in self.ivr_apps or 
            obj2._meta.app_label in self.ivr_apps):
            return False
        
        # Ninguno en ivr → permitir
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Bloquea migraciones en BD IVR.
        
        CRÍTICO: Nunca ejecutar migraciones en 'ivr_legacy'.
        El schema de BD IVR es gestionado por el sistema IVR externo.
        
        Args:
            db: Nombre de la BD
            app_label: Label de la app
            model_name: Nombre del modelo (opcional)
            **hints: Hints adicionales
        
        Returns:
            bool: False si es app ivr, True si db=='default' y no es ivr
        """
        if app_label in self.ivr_apps:
            # ✅ NUNCA migrar app ivr
            return False
        
        # ✅ Solo migrar en 'default'
        return db == 'default'
```

**Validación del Router:**

```python
# tests/test_router.py

from django.test import TestCase
from apps.ivr.models import CallRecord
from django.db import router

class IVRRouterTestCase(TestCase):
    """Tests para IVRRouter."""
    
    def test_db_for_read_ivr(self):
        """Verifica que apps/ivr/ lee de ivr_legacy."""
        db = router.db_for_read(CallRecord)
        self.assertEqual(db, 'ivr_legacy')
    
    def test_db_for_write_ivr_blocked(self):
        """Verifica que escrituras a apps/ivr/ están BLOQUEADAS."""
        db = router.db_for_write(CallRecord)
        self.assertIsNone(db, "CNST-002 VIOLADO: Escritura a BD IVR permitida")
    
    def test_allow_migrate_ivr_blocked(self):
        """Verifica que migraciones en ivr_legacy están BLOQUEADAS."""
        allowed = router.allow_migrate('ivr_legacy', 'ivr')
        self.assertFalse(allowed, "Migraciones en BD IVR permitidas")
```

---

### 2.2 Tablas Históricas (IVR Legacy)

#### **2.2.1 Nomenclatura Húngara Original (CLEAN_CODE v3.0.1)**

Las tablas IVR usan nomenclatura húngara del dominio:

```
Prefijos de Campos:
├─ d → Fecha/Datetime (dFecha, dFechaIngreso)
├─ c → Character/String (cMenu, cDID, cTelefono)
├─ n → Numeric/Integer (nDuracion, nTiempoEspera)
├─ b → Boolean (bTransferida, bAbandonada)
└─ t → Time (tHoraLlamada)

Nomenclatura:
- db_table: 'tbl_historico_t1_2025'  ✅ Preservado (CLEAN_CODE v3.0.1)
- Modelo Django: CallRecord          ✅ Inglés, PascalCase
- Campos BD: cMenu, dFecha, nDuracion ✅ Original húngaro
- Atributos modelo: menu, date, duration ✅ Inglés, snake_case
```

**Referencia:** CLEAN_CODE v3.0.1, Parte 4, Sección 4.2 (db_table)

---

#### **2.2.2 Schema SQL Completo**

```sql
-- Tabla: tbl_historico_t1_2025 (Trimestre 1: Enero-Marzo)
-- IMPORTANTE: Schema gestionado por sistema IVR externo (NO Django)
-- Django acceso: READONLY (SELECT only)

CREATE TABLE IF NOT EXISTS `tbl_historico_t1_2025` (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  
  -- Identificación de llamada
  `cDID` VARCHAR(20) NOT NULL COMMENT 'Número marcado (DID)',
  `cTelefono` VARCHAR(20) NOT NULL COMMENT 'Número origen',
  `cCallID` VARCHAR(50) UNIQUE COMMENT 'ID único de llamada',
  
  -- Fecha y hora
  `dFechaIngreso` DATETIME NOT NULL COMMENT 'Timestamp ingreso al IVR',
  `dFechaFin` DATETIME COMMENT 'Timestamp fin de llamada',
  `tHoraLlamada` TIME COMMENT 'Hora del día (para análisis)',
  
  -- Navegación en menús
  `cMenuInicial` VARCHAR(50) COMMENT 'Primer menú visitado',
  `cMenuFinal` VARCHAR(50) COMMENT 'Último menú antes de salir',
  `cRutaMenus` TEXT COMMENT 'Ruta completa: MENU1>MENU2>MENU3',
  `nCantidadMenus` INT(3) DEFAULT 0 COMMENT 'Número de menús visitados',
  
  -- Duración y tiempos
  `nDuracionTotal` INT(6) DEFAULT 0 COMMENT 'Duración total llamada (segundos)',
  `nTiempoEspera` INT(6) DEFAULT 0 COMMENT 'Tiempo en cola (segundos)',
  `nTiempoIVR` INT(6) DEFAULT 0 COMMENT 'Tiempo navegando IVR (segundos)',
  
  -- Estado de llamada
  `bTransferida` BOOLEAN DEFAULT FALSE COMMENT 'Si llamada fue transferida',
  `cDestinoTransferencia` VARCHAR(50) COMMENT 'Extension/cola destino',
  `bAbandonada` BOOLEAN DEFAULT FALSE COMMENT 'Si llamada fue abandonada',
  `cMotivoSalida` VARCHAR(100) COMMENT 'Razón de salida del IVR',
  
  -- Clasificación
  `cTipoLlamada` VARCHAR(30) COMMENT 'Entrante/Saliente',
  `cCategoriaCliente` VARCHAR(50) COMMENT 'Nuevo/Recurrente/VIP',
  
  -- Índices para optimización
  INDEX idx_fecha (`dFechaIngreso`),
  INDEX idx_did (`cDID`),
  INDEX idx_trimestre (`dFechaIngreso`, `cDID`),
  INDEX idx_menu_final (`cMenuFinal`),
  INDEX idx_transferidas (`bTransferida`, `dFechaIngreso`),
  INDEX idx_abandonadas (`bAbandonada`, `dFechaIngreso`)
  
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Histórico llamadas Trimestre 1 (Ene-Mar 2025)';

-- Tablas t2 y t3 tienen estructura idéntica
-- CREATE TABLE `tbl_historico_t2_2025` LIKE `tbl_historico_t1_2025`;
-- CREATE TABLE `tbl_historico_t3_2025` LIKE `tbl_historico_t1_2025`;
```

---

#### **2.2.3 Modelo Django (CLEAN_CODE v3.0.1)**

```python
# apps/ivr/models.py

from django.db import models
from apps.core.models import TimeStampedModel

class CallRecord(models.Model):
    """
    Registro de llamada del sistema IVR Legacy.
    
    IMPORTANTE:
    - Modelo readonly (managed=False)
    - BD: MariaDB (ivr_legacy)
    - Tabla: tbl_historico_t{1,2,3}_2025 (según trimestre)
    - Nomenclatura campos: Húngara original (cDID, dFecha, nDuracion)
    - Atributos modelo: Inglés snake_case (did, date, duration)
    
    Restricciones:
    - CNST-002: Solo lectura (ZERO escritura)
    - Router: db_for_write() → None (BLOQUEADO)
    
    Referencias:
    - CLEAN_CODE v3.0.1: Parte 2 (Nomenclatura) + Parte 4 (db_table)
    - RESTRICCIONES v1.0.0: CNST-002 (BD Dual readonly)
    """
    
    # Identificación
    did = models.CharField(
        max_length=20,
        db_column='cDID',
        help_text="Número marcado (DID)"
    )
    phone_number = models.CharField(
        max_length=20,
        db_column='cTelefono',
        help_text="Número origen llamada"
    )
    call_id = models.CharField(
        max_length=50,
        db_column='cCallID',
        unique=True,
        null=True,
        blank=True,
        help_text="ID único de llamada"
    )
    
    # Fecha y hora
    entry_datetime = models.DateTimeField(
        db_column='dFechaIngreso',
        help_text="Timestamp ingreso al IVR"
    )
    end_datetime = models.DateTimeField(
        db_column='dFechaFin',
        null=True,
        blank=True,
        help_text="Timestamp fin de llamada"
    )
    call_time = models.TimeField(
        db_column='tHoraLlamada',
        null=True,
        blank=True,
        help_text="Hora del día (análisis)"
    )
    
    # Navegación menús
    initial_menu = models.CharField(
        max_length=50,
        db_column='cMenuInicial',
        null=True,
        blank=True,
        help_text="Primer menú visitado"
    )
    final_menu = models.CharField(
        max_length=50,
        db_column='cMenuFinal',
        null=True,
        blank=True,
        help_text="Último menú visitado"
    )
    menu_path = models.TextField(
        db_column='cRutaMenus',
        null=True,
        blank=True,
        help_text="Ruta completa: MENU1>MENU2>MENU3"
    )
    menu_count = models.IntegerField(
        db_column='nCantidadMenus',
        default=0,
        help_text="Cantidad de menús visitados"
    )
    
    # Duración
    total_duration = models.IntegerField(
        db_column='nDuracionTotal',
        default=0,
        help_text="Duración total (segundos)"
    )
    wait_time = models.IntegerField(
        db_column='nTiempoEspera',
        default=0,
        help_text="Tiempo en cola (segundos)"
    )
    ivr_time = models.IntegerField(
        db_column='nTiempoIVR',
        default=0,
        help_text="Tiempo navegando IVR (segundos)"
    )
    
    # Estado
    is_transferred = models.BooleanField(
        db_column='bTransferida',
        default=False,
        help_text="Si fue transferida"
    )
    transfer_destination = models.CharField(
        max_length=50,
        db_column='cDestinoTransferencia',
        null=True,
        blank=True,
        help_text="Destino transferencia"
    )
    is_abandoned = models.BooleanField(
        db_column='bAbandonada',
        default=False,
        help_text="Si fue abandonada"
    )
    exit_reason = models.CharField(
        max_length=100,
        db_column='cMotivoSalida',
        null=True,
        blank=True,
        help_text="Motivo de salida del IVR"
    )
    
    # Clasificación
    call_type = models.CharField(
        max_length=30,
        db_column='cTipoLlamada',
        null=True,
        blank=True,
        help_text="Entrante/Saliente"
    )
    customer_category = models.CharField(
        max_length=50,
        db_column='cCategoriaCliente',
        null=True,
        blank=True,
        help_text="Nuevo/Recurrente/VIP"
    )
    
    class Meta:
        managed = False  # ✅ Django NO gestiona schema
        db_table = 'tbl_historico_t1_2025'  # ✅ Preserva nombre húngaro
        ordering = ['-entry_datetime']
        verbose_name = 'Registro de Llamada'
        verbose_name_plural = 'Registros de Llamadas'
        
        indexes = [
            models.Index(fields=['entry_datetime']),
            models.Index(fields=['did']),
            models.Index(fields=['is_transferred', 'entry_datetime']),
            models.Index(fields=['is_abandoned', 'entry_datetime']),
        ]
    
    def __str__(self):
        """Representación string del modelo."""
        return f"CallRecord {self.call_id} - {self.did} - {self.entry_datetime}"
    
    def get_quarter(self):
        """
        Obtiene el trimestre de la llamada.
        
        Returns:
            str: 'Q1', 'Q2', 'Q3', o 'Q4'
        """
        month = self.entry_datetime.month
        if month <= 3:
            return 'Q1'
        elif month <= 6:
            return 'Q2'
        elif month <= 9:
            return 'Q3'
        else:
            return 'Q4'
    
    @classmethod
    def get_table_for_quarter(cls, quarter):
        """
        Retorna el nombre de tabla según trimestre.
        
        Args:
            quarter (str): 'Q1', 'Q2', 'Q3'
        
        Returns:
            str: Nombre de tabla (ej: 'tbl_historico_t1_2025')
        """
        mapping = {
            'Q1': 'tbl_historico_t1_2025',
            'Q2': 'tbl_historico_t2_2025',
            'Q3': 'tbl_historico_t3_2025',
        }
        return mapping.get(quarter, 'tbl_historico_t1_2025')
```

**Notas CLEAN_CODE v3.0.1:**

1. **Clase:** PascalCase en inglés (`CallRecord`) ✅
2. **Atributos:** snake_case en inglés (`entry_datetime`, `is_transferred`) ✅
3. **Métodos:** snake_case en inglés (`get_quarter()`) ✅
4. **Docstrings:** Español, formato Google ✅
5. **db_column:** Preserva nombre húngaro original (`cDID`, `dFechaIngreso`) ✅
6. **db_table:** Preserva nombre tabla original (`tbl_historico_t1_2025`) ✅

---

### 2.3 Tablas Agregadas (Salida del ETL)

Las tablas agregadas son generadas por el Stored Procedure `sp_etl_daily()`.

#### **2.3.1 Lista de Tablas Agregadas**

```
1. tbl_reporte_trimestral
   └─ Métricas consolidadas por trimestre/DID

2. tbl_reporte_transferencias
   └─ Análisis de llamadas transferidas

3. tbl_reporte_clientes
   └─ Análisis de clientes únicos

4. tbl_reporte_abandonadas
   └─ Llamadas abandonadas con detalle

5. tbl_reporte_detalle_transferencias
   └─ Detalle granular de transferencias

6. tbl_reporte_menus_performance
   └─ Performance por menú IVR

7. tbl_reporte_menu_errores
   └─ Errores/timeouts en menús
```

---

#### **2.3.2 Tabla: tbl_reporte_trimestral**

```sql
CREATE TABLE IF NOT EXISTS `tbl_reporte_trimestral` (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `cDID` VARCHAR(20) NOT NULL,
  `cTrimestre` CHAR(2) NOT NULL COMMENT 'Q1, Q2, Q3',
  `dFechaInicio` DATE NOT NULL,
  `dFechaFin` DATE NOT NULL,
  
  -- Métricas generales
  `nTotalLlamadas` INT(10) DEFAULT 0,
  `nLlamadasTransferidas` INT(10) DEFAULT 0,
  `nLlamadasAbandonadas` INT(10) DEFAULT 0,
  `nLlamadasCompletadas` INT(10) DEFAULT 0,
  
  -- Porcentajes
  `fPorcentajeTransferidas` DECIMAL(5,2) DEFAULT 0.00,
  `fPorcentajeAbandonadas` DECIMAL(5,2) DEFAULT 0.00,
  
  -- Tiempos promedio
  `nDuracionPromedio` INT(6) DEFAULT 0,
  `nTiempoEsperaPromedio` INT(6) DEFAULT 0,
  
  -- Fechas de proceso
  `dFechaProceso` DATETIME NOT NULL,
  
  UNIQUE KEY unique_did_trimestre (`cDID`, `cTrimestre`),
  INDEX idx_trimestre (`cTrimestre`),
  INDEX idx_did (`cDID`)
  
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
COMMENT='Reporte consolidado trimestral por DID';
```

**Modelo Django:**

```python
# apps/ivr/models.py

class QuarterlyReport(models.Model):
    """
    Reporte consolidado trimestral.
    
    Generado por: sp_etl_daily() cada 6-12h
    BD: MariaDB (ivr_legacy)
    Acceso: Readonly (CNST-002)
    """
    
    did = models.CharField(max_length=20, db_column='cDID')
    quarter = models.CharField(max_length=2, db_column='cTrimestre')
    start_date = models.DateField(db_column='dFechaInicio')
    end_date = models.DateField(db_column='dFechaFin')
    
    # Métricas
    total_calls = models.IntegerField(db_column='nTotalLlamadas', default=0)
    transferred_calls = models.IntegerField(db_column='nLlamadasTransferidas', default=0)
    abandoned_calls = models.IntegerField(db_column='nLlamadasAbandonadas', default=0)
    completed_calls = models.IntegerField(db_column='nLlamadasCompletadas', default=0)
    
    # Porcentajes
    transferred_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        db_column='fPorcentajeTransferidas',
        default=0.00
    )
    abandoned_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        db_column='fPorcentajeAbandonadas',
        default=0.00
    )
    
    # Tiempos
    average_duration = models.IntegerField(db_column='nDuracionPromedio', default=0)
    average_wait_time = models.IntegerField(db_column='nTiempoEsperaPromedio', default=0)
    
    # Control
    processed_at = models.DateTimeField(db_column='dFechaProceso')
    
    class Meta:
        managed = False
        db_table = 'tbl_reporte_trimestral'
        unique_together = [['did', 'quarter']]
        ordering = ['-quarter', 'did']
        verbose_name = 'Reporte Trimestral'
        verbose_name_plural = 'Reportes Trimestrales'
```

---

### 2.4 Tabla de Control ETL

```sql
CREATE TABLE IF NOT EXISTS `job_execution_log` (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `cJobName` VARCHAR(100) NOT NULL COMMENT 'Nombre del job',
  `dStartTime` DATETIME NOT NULL,
  `dEndTime` DATETIME,
  `cStatus` VARCHAR(20) NOT NULL COMMENT 'running, completed, failed',
  `nRecordsProcessed` INT(10) DEFAULT 0,
  `nRecordsFailed` INT(10) DEFAULT 0,
  `tErrorMessage` TEXT,
  `fDurationSeconds` DECIMAL(10,2),
  
  INDEX idx_job_name (`cJobName`),
  INDEX idx_status (`cStatus`),
  INDEX idx_start_time (`dStartTime`)
  
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
COMMENT='Log de ejecución de jobs ETL';
```

**Modelo Django:**

```python
# apps/pipeline/models.py

class JobExecutionLog(models.Model):
    """
    Log de ejecución de jobs ETL.
    
    Registra cada ejecución del ETL para monitoreo.
    BD: MariaDB (ivr_legacy)
    """
    
    class JobStatus(models.TextChoices):
        """Estados posibles del job."""
        RUNNING = 'running', 'En Ejecución'
        COMPLETED = 'completed', 'Completado'
        FAILED = 'failed', 'Fallido'
    
    job_name = models.CharField(max_length=100, db_column='cJobName')
    start_time = models.DateTimeField(db_column='dStartTime')
    end_time = models.DateTimeField(db_column='dEndTime', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        db_column='cStatus'
    )
    records_processed = models.IntegerField(
        db_column='nRecordsProcessed',
        default=0
    )
    records_failed = models.IntegerField(
        db_column='nRecordsFailed',
        default=0
    )
    error_message = models.TextField(
        db_column='tErrorMessage',
        null=True,
        blank=True
    )
    duration_seconds = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='fDurationSeconds',
        null=True,
        blank=True
    )
    
    class Meta:
        managed = False
        db_table = 'job_execution_log'
        ordering = ['-start_time']
        verbose_name = 'Log de Ejecución ETL'
        verbose_name_plural = 'Logs de Ejecución ETL'
    
    def __str__(self):
        """Representación string."""
        return f"{self.job_name} - {self.status} - {self.start_time}"
```

---

### 2.5 DIDs y Filtros

```python
# apps/ivr/constants.py

"""
Constantes para el sistema IVR.

CLEAN_CODE v3.0.1: Constantes en UPPER_SNAKE_CASE, inglés.
"""

# DIDs configurados en el sistema
VALID_DIDS = [
    '555-1234',
    '555-5678',
    '555-9012',
]

# Trimestres disponibles
AVAILABLE_QUARTERS = ['Q1', 'Q2', 'Q3']

# Tipos de llamada
CALL_TYPES = [
    ('inbound', 'Entrante'),
    ('outbound', 'Saliente'),
]

# Categorías de cliente
CUSTOMER_CATEGORIES = [
    ('new', 'Nuevo'),
    ('recurring', 'Recurrente'),
    ('vip', 'VIP'),
]

# Límites de export (CNST-007)
MAX_EXPORT_ROWS_CSV = 100000    # 100K registros
MAX_EXPORT_ROWS_EXCEL = 50000   # 50K registros
MAX_EXPORT_ROWS_PDF = 10000     # 10K registros (planificado)

# Timeout DB (CNST-004)
DB_QUERY_TIMEOUT = 300  # 300 segundos

# Timeout request (CNST-025)
REQUEST_TIMEOUT = 90  # 90 segundos
```

---

<a name="3-proceso-etl"></a>

## 3. PROCESO ETL

### 3.1 Stored Procedure: sp_etl_daily()

El ETL está implementado como Stored Procedure en MariaDB.

**Características:**
- Lenguaje: SQL puro (MariaDB)
- Ejecutor: APScheduler (CNST-013) + Cron backup
- Frecuencia: 6-12 horas (configurable)
- Timeout: 300s (CNST-004)
- Logging: job_execution_log

```sql
-- ══════════════════════════════════════════════════════════
-- STORED PROCEDURE: sp_etl_daily()
-- Descripción: Procesa datos históricos y genera reportes
-- Ejecutor: APScheduler (cada 6-12h) + Cron backup (2:00 AM)
-- CNST-013: NO Celery, SÍ APScheduler
-- ══════════════════════════════════════════════════════════

DELIMITER $$

CREATE PROCEDURE sp_etl_daily()
BEGIN
    DECLARE v_job_id INT;
    DECLARE v_start_time DATETIME;
    DECLARE v_records_processed INT DEFAULT 0;
    DECLARE v_records_failed INT DEFAULT 0;
    DECLARE v_error_msg TEXT DEFAULT NULL;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_error_msg = MESSAGE_TEXT;
        
        UPDATE job_execution_log
        SET 
            dEndTime = NOW(),
            cStatus = 'failed',
            nRecordsFailed = v_records_failed,
            tErrorMessage = v_error_msg,
            fDurationSeconds = TIMESTAMPDIFF(SECOND, v_start_time, NOW())
        WHERE id = v_job_id;
        
        ROLLBACK;
    END;
    
    -- ════════════════════════════════════════════════════════
    -- 1. INICIAR LOG
    -- ════════════════════════════════════════════════════════
    
    SET v_start_time = NOW();
    
    INSERT INTO job_execution_log (
        cJobName,
        dStartTime,
        cStatus
    ) VALUES (
        'sp_etl_daily',
        v_start_time,
        'running'
    );
    
    SET v_job_id = LAST_INSERT_ID();
    
    -- ════════════════════════════════════════════════════════
    -- 2. GENERAR tbl_reporte_trimestral
    -- ════════════════════════════════════════════════════════
    
    -- Limpiar datos del trimestre actual
    DELETE FROM tbl_reporte_trimestral
    WHERE cTrimestre = (
        SELECT 
            CASE 
                WHEN MONTH(CURDATE()) <= 3 THEN 'Q1'
                WHEN MONTH(CURDATE()) <= 6 THEN 'Q2'
                WHEN MONTH(CURDATE()) <= 9 THEN 'Q3'
                ELSE 'Q4'
            END
    );
    
    -- Insertar métricas agregadas
    INSERT INTO tbl_reporte_trimestral (
        cDID,
        cTrimestre,
        dFechaInicio,
        dFechaFin,
        nTotalLlamadas,
        nLlamadasTransferidas,
        nLlamadasAbandonadas,
        nLlamadasCompletadas,
        fPorcentajeTransferidas,
        fPorcentajeAbandonadas,
        nDuracionPromedio,
        nTiempoEsperaPromedio,
        dFechaProceso
    )
    SELECT 
        h.cDID,
        CASE 
            WHEN MONTH(h.dFechaIngreso) <= 3 THEN 'Q1'
            WHEN MONTH(h.dFechaIngreso) <= 6 THEN 'Q2'
            WHEN MONTH(h.dFechaIngreso) <= 9 THEN 'Q3'
            ELSE 'Q4'
        END AS trimestre,
        MIN(DATE(h.dFechaIngreso)) AS fecha_inicio,
        MAX(DATE(h.dFechaIngreso)) AS fecha_fin,
        COUNT(*) AS total_llamadas,
        SUM(CASE WHEN h.bTransferida = 1 THEN 1 ELSE 0 END) AS llamadas_transferidas,
        SUM(CASE WHEN h.bAbandonada = 1 THEN 1 ELSE 0 END) AS llamadas_abandonadas,
        SUM(CASE WHEN h.bTransferida = 0 AND h.bAbandonada = 0 THEN 1 ELSE 0 END) AS llamadas_completadas,
        ROUND((SUM(CASE WHEN h.bTransferida = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS pct_transferidas,
        ROUND((SUM(CASE WHEN h.bAbandonada = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS pct_abandonadas,
        AVG(h.nDuracionTotal) AS duracion_promedio,
        AVG(h.nTiempoEspera) AS espera_promedio,
        NOW() AS fecha_proceso
    FROM (
        SELECT * FROM tbl_historico_t1_2025
        UNION ALL
        SELECT * FROM tbl_historico_t2_2025
        UNION ALL
        SELECT * FROM tbl_historico_t3_2025
    ) h
    WHERE h.dFechaIngreso >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
    GROUP BY h.cDID, trimestre;
    
    SET v_records_processed = v_records_processed + ROW_COUNT();
    
    -- ════════════════════════════════════════════════════════
    -- 3. GENERAR tbl_reporte_abandonadas
    -- ════════════════════════════════════════════════════════
    
    TRUNCATE TABLE tbl_reporte_abandonadas;
    
    INSERT INTO tbl_reporte_abandonadas (
        cDID,
        dFecha,
        nTotalAbandonadas,
        nAbandonadasMenos30s,
        nAbandonadas30a60s,
        nAbandonadasMas60s,
        nTiempoEsperaPromedio,
        dFechaProceso
    )
    SELECT 
        h.cDID,
        DATE(h.dFechaIngreso) AS fecha,
        COUNT(*) AS total_abandonadas,
        SUM(CASE WHEN h.nTiempoEspera < 30 THEN 1 ELSE 0 END) AS menos_30s,
        SUM(CASE WHEN h.nTiempoEspera >= 30 AND h.nTiempoEspera < 60 THEN 1 ELSE 0 END) AS entre_30_60s,
        SUM(CASE WHEN h.nTiempoEspera >= 60 THEN 1 ELSE 0 END) AS mas_60s,
        AVG(h.nTiempoEspera) AS espera_promedio,
        NOW() AS fecha_proceso
    FROM (
        SELECT * FROM tbl_historico_t1_2025 WHERE bAbandonada = 1
        UNION ALL
        SELECT * FROM tbl_historico_t2_2025 WHERE bAbandonada = 1
        UNION ALL
        SELECT * FROM tbl_historico_t3_2025 WHERE bAbandonada = 1
    ) h
    WHERE h.dFechaIngreso >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
    GROUP BY h.cDID, DATE(h.dFechaIngreso);
    
    SET v_records_processed = v_records_processed + ROW_COUNT();
    
    -- ════════════════════════════════════════════════════════
    -- 4. GENERAR tbl_reporte_clientes
    -- ════════════════════════════════════════════════════════
    
    TRUNCATE TABLE tbl_reporte_clientes;
    
    INSERT INTO tbl_reporte_clientes (
        cDID,
        dMes,
        nClientesUnicos,
        nClientesNuevos,
        nClientesRecurrentes,
        nPromedioLlamadasPorCliente,
        dFechaProceso
    )
    SELECT 
        h.cDID,
        DATE_FORMAT(h.dFechaIngreso, '%Y-%m-01') AS mes,
        COUNT(DISTINCT h.cTelefono) AS clientes_unicos,
        COUNT(DISTINCT CASE WHEN h.cCategoriaCliente = 'Nuevo' THEN h.cTelefono END) AS clientes_nuevos,
        COUNT(DISTINCT CASE WHEN h.cCategoriaCliente = 'Recurrente' THEN h.cTelefono END) AS clientes_recurrentes,
        COUNT(*) / COUNT(DISTINCT h.cTelefono) AS promedio_llamadas_por_cliente,
        NOW() AS fecha_proceso
    FROM (
        SELECT * FROM tbl_historico_t1_2025
        UNION ALL
        SELECT * FROM tbl_historico_t2_2025
        UNION ALL
        SELECT * FROM tbl_historico_t3_2025
    ) h
    WHERE h.dFechaIngreso >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
    GROUP BY h.cDID, mes;
    
    SET v_records_processed = v_records_processed + ROW_COUNT();
    
    -- ════════════════════════════════════════════════════════
    -- 5. GENERAR tbl_reporte_transferencias
    -- ════════════════════════════════════════════════════════
    
    TRUNCATE TABLE tbl_reporte_transferencias;
    
    INSERT INTO tbl_reporte_transferencias (
        cDID,
        cDestinoTransferencia,
        dFecha,
        nTotalTransferencias,
        nTiempoPreTransferencia,
        nTasaExito,
        dFechaProceso
    )
    SELECT 
        h.cDID,
        h.cDestinoTransferencia,
        DATE(h.dFechaIngreso) AS fecha,
        COUNT(*) AS total_transferencias,
        AVG(h.nTiempoIVR) AS tiempo_pre_transferencia,
        ROUND((SUM(CASE WHEN h.bAbandonada = 0 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS tasa_exito,
        NOW() AS fecha_proceso
    FROM (
        SELECT * FROM tbl_historico_t1_2025 WHERE bTransferida = 1
        UNION ALL
        SELECT * FROM tbl_historico_t2_2025 WHERE bTransferida = 1
        UNION ALL
        SELECT * FROM tbl_historico_t3_2025 WHERE bTransferida = 1
    ) h
    WHERE h.dFechaIngreso >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
    GROUP BY h.cDID, h.cDestinoTransferencia, DATE(h.dFechaIngreso);
    
    SET v_records_processed = v_records_processed + ROW_COUNT();
    
    -- ════════════════════════════════════════════════════════
    -- 6. GENERAR tbl_reporte_menus_performance
    -- ════════════════════════════════════════════════════════
    
    TRUNCATE TABLE tbl_reporte_menus_performance;
    
    INSERT INTO tbl_reporte_menus_performance (
        cMenuID,
        dFecha,
        nVisitas,
        nTiempoPromedioMenu,
        nSalidasExitosas,
        nAbandonos,
        nTransferencias,
        fTasaExito,
        dFechaProceso
    )
    SELECT 
        h.cMenuFinal AS menu_id,
        DATE(h.dFechaIngreso) AS fecha,
        COUNT(*) AS visitas,
        AVG(h.nTiempoIVR) AS tiempo_promedio,
        SUM(CASE WHEN h.bAbandonada = 0 AND h.bTransferida = 0 THEN 1 ELSE 0 END) AS salidas_exitosas,
        SUM(CASE WHEN h.bAbandonada = 1 THEN 1 ELSE 0 END) AS abandonos,
        SUM(CASE WHEN h.bTransferida = 1 THEN 1 ELSE 0 END) AS transferencias,
        ROUND((SUM(CASE WHEN h.bAbandonada = 0 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS tasa_exito,
        NOW() AS fecha_proceso
    FROM (
        SELECT * FROM tbl_historico_t1_2025
        UNION ALL
        SELECT * FROM tbl_historico_t2_2025
        UNION ALL
        SELECT * FROM tbl_historico_t3_2025
    ) h
    WHERE h.dFechaIngreso >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
      AND h.cMenuFinal IS NOT NULL
    GROUP BY h.cMenuFinal, DATE(h.dFechaIngreso);
    
    SET v_records_processed = v_records_processed + ROW_COUNT();
    
    -- ════════════════════════════════════════════════════════
    -- 7. FINALIZAR LOG
    -- ════════════════════════════════════════════════════════
    
    UPDATE job_execution_log
    SET 
        dEndTime = NOW(),
        cStatus = 'completed',
        nRecordsProcessed = v_records_processed,
        fDurationSeconds = TIMESTAMPDIFF(SECOND, v_start_time, NOW())
    WHERE id = v_job_id;
    
    COMMIT;
    
END$$

DELIMITER ;
```

---

### 3.2 Ejecutor APScheduler (CNST-013)

**Configuración APScheduler (NO Celery):**

```python
# apps/pipeline/scheduler.py

"""
Scheduler para jobs programados del sistema.

RESTRICCIÓN: CNST-013 (NO Celery, SÍ APScheduler)

Este módulo configura APScheduler para ejecutar el ETL cada 6-12 horas.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

# Scheduler global
scheduler = BackgroundScheduler({
    'apscheduler.jobstores.default': {
        'type': 'memory'
    },
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '3'
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '1',
    'apscheduler.timezone': 'America/Santiago',
})

def run_etl():
    """
    Ejecuta ETL desde stored procedure.
    
    Llama al management command que ejecuta sp_etl_daily().
    """
    try:
        logger.info("═══ Iniciando ETL programado ═══")
        call_command('run_etl')
        logger.info("═══ ETL completado exitosamente ═══")
    except Exception as e:
        logger.error(f"❌ Error en ETL: {str(e)}", exc_info=True)


def cleanup_old_sessions():
    """
    Limpia sesiones expiradas de la BD.
    
    Ejecuta clearsessions de Django.
    """
    try:
        logger.info("Limpiando sesiones expiradas...")
        call_command('clearsessions')
        logger.info("✅ Sesiones limpiadas")
    except Exception as e:
        logger.error(f"❌ Error limpiando sesiones: {str(e)}")


def configure_jobs():
    """
    Configura los jobs en el scheduler.
    
    Jobs configurados:
    - ETL: Cada 6 horas (configurable)
    - Cleanup sessions: Diario a las 3:00 AM
    """
    # Job 1: ETL cada 6 horas
    scheduler.add_job(
        run_etl,
        trigger=IntervalTrigger(hours=6),
        id='etl_job',
        name='ETL IVR → Analytics',
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )
    logger.info("✅ Job ETL configurado: cada 6 horas")
    
    # Job 2: Cleanup sesiones diario
    scheduler.add_job(
        cleanup_old_sessions,
        trigger=CronTrigger(hour=3, minute=0),
        id='cleanup_sessions',
        name='Cleanup Sesiones Expiradas',
        replace_existing=True,
        max_instances=1
    )
    logger.info("✅ Job Cleanup configurado: diario 3:00 AM")


def start_scheduler():
    """Inicia el scheduler."""
    if not scheduler.running:
        configure_jobs()
        scheduler.start()
        logger.info("🚀 APScheduler iniciado")
    else:
        logger.warning("⚠️ APScheduler ya está corriendo")


def shutdown_scheduler():
    """Detiene el scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("🛑 APScheduler detenido")
```

**Inicialización en Django:**

```python
# config/apps.py

from django.apps import AppConfig

class CoreAppConfig(AppConfig):
    """Configuración de la app core."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    
    def ready(self):
        """Inicializa scheduler cuando Django está listo."""
        import os
        
        # Solo iniciar scheduler en proceso principal
        # (no en runserver reloader)
        if os.environ.get('RUN_MAIN') == 'true':
            from apps.pipeline.scheduler import start_scheduler
            start_scheduler()
```

---

### 3.3 Cron Backup (Redundancia)

Además de APScheduler, se configura un Cron como backup:

```bash
# /etc/cron.d/iact-etl

# ETL diario a las 2:00 AM (backup)
0 2 * * * iact /usr/local/bin/run_etl.sh >> /var/log/iact/etl_cron.log 2>&1
```

**Script Bash:**

```bash
#!/bin/bash
# /usr/local/bin/run_etl.sh
# Script para ejecutar ETL desde cron

set -e

# Activar virtualenv
source /opt/iact/venv/bin/activate

# Navegar a proyecto
cd /opt/iact/app

# Ejecutar management command
python manage.py run_etl --settings=config.settings.production

exit 0
```

---

### 3.4 Management Command

```python
# apps/pipeline/management/commands/run_etl.py

"""
Management command para ejecutar el ETL.

Llama al stored procedure sp_etl_daily() en MariaDB.
"""

from django.core.management.base import BaseCommand
from django.db import connections
from apps.pipeline.models import JobExecutionLog
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Ejecuta el stored procedure ETL."""
    
    help = 'Ejecuta sp_etl_daily() para procesar datos IVR'
    
    def add_arguments(self, parser):
        """Agrega argumentos opcionales."""
        parser.add_argument(
            '--timeout',
            type=int,
            default=300,
            help='Timeout en segundos (default: 300 - CNST-004)'
        )
    
    def handle(self, *args, **options):
        """Ejecuta el comando."""
        timeout = options['timeout']
        
        self.stdout.write(self.style.SUCCESS('═══ Iniciando ETL ═══'))
        
        try:
            with connections['ivr_legacy'].cursor() as cursor:
                # Configurar timeout
                cursor.execute(f"SET SESSION max_execution_time = {timeout * 1000}")
                
                # Ejecutar stored procedure
                self.stdout.write('Ejecutando sp_etl_daily()...')
                cursor.execute("CALL sp_etl_daily()")
                
                # Confirmar
                self.stdout.write(self.style.SUCCESS('✅ ETL completado'))
                
                # Mostrar último log
                last_log = JobExecutionLog.objects.filter(
                    status='completed'
                ).order_by('-end_time').first()
                
                if last_log:
                    self.stdout.write(f"  Registros procesados: {last_log.records_processed}")
                    self.stdout.write(f"  Duración: {last_log.duration_seconds}s")
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error en ETL: {str(e)}'))
            logger.error(f"Error ejecutando ETL: {str(e)}", exc_info=True)
            raise
```

---

### 3.5 Flujo ETL Completo

```
┌────────────────────────────────────────────────────────────────┐
│ FLUJO ETL COMPLETO                                             │
└────────────────────────────────────────────────────────────────┘

TRIGGER 1: APScheduler (cada 6 horas)
  │
  ├─> apps/pipeline/scheduler.py::run_etl()
  │   └─> call_command('run_etl')
  │
  ↓

TRIGGER 2: Cron (backup, 2:00 AM)
  │
  ├─> /usr/local/bin/run_etl.sh
  │   └─> python manage.py run_etl
  │
  ↓

MANAGEMENT COMMAND:
  │
  ├─> apps/pipeline/management/commands/run_etl.py
  │   │
  │   ├─> SET SESSION max_execution_time = 300000 (CNST-004)
  │   │
  │   └─> CALL sp_etl_daily()
  │
  ↓

STORED PROCEDURE (MariaDB):
  │
  ├─> 1. Insertar log inicial (job_execution_log)
  │   └─> status = 'running'
  │
  ├─> 2. Procesar tbl_reporte_trimestral
  │   ├─> DELETE trimestre actual
  │   ├─> UNION ALL (t1 + t2 + t3)
  │   └─> GROUP BY (cDID, trimestre)
  │
  ├─> 3. Procesar tbl_reporte_abandonadas
  │   ├─> TRUNCATE
  │   ├─> WHERE bAbandonada = 1
  │   └─> GROUP BY (cDID, fecha)
  │
  ├─> 4. Procesar tbl_reporte_clientes
  │   ├─> TRUNCATE
  │   ├─> COUNT(DISTINCT cTelefono)
  │   └─> GROUP BY (cDID, mes)
  │
  ├─> 5. Procesar tbl_reporte_transferencias
  │   ├─> TRUNCATE
  │   ├─> WHERE bTransferida = 1
  │   └─> GROUP BY (cDID, destino, fecha)
  │
  ├─> 6. Procesar tbl_reporte_menus_performance
  │   ├─> TRUNCATE
  │   ├─> Calcular métricas por menú
  │   └─> GROUP BY (cMenuFinal, fecha)
  │
  └─> 7. Actualizar log final
      ├─> status = 'completed'
      ├─> nRecordsProcessed
      └─> fDurationSeconds

RESULTADO:
  ├─> 7 tablas agregadas actualizadas
  ├─> 1 registro en job_execution_log
  └─> Dashboard actualizado (datos 6-12h desfase - CNST-003)

RESTRICCIONES APLICADAS:
  ✅ CNST-003: NO real-time (desfase 6-12h aceptable)
  ✅ CNST-004: Timeout 300s configurado
  ✅ CNST-013: APScheduler (NO Celery)
```

---

**FIN DE PARTE 1/3**

**Continúa en:** ARQUITECTURA_ETL_v3_0_0_PARTE_2.md

---

## RESUMEN PARTE 1

**✅ Completado:**
- Sección 1: Resumen Ejecutivo
  - Arquitectura en una página (ASCII completo)
  - 8 decisiones arquitectónicas clave documentadas
  - Stack tecnológico v3.0.0 (con restricciones aplicadas)
  - Números clave del sistema

- Sección 2: Arquitectura de Datos (MariaDB)
  - Configuración Django DATABASES (ivr_legacy + default)
  - Database Router completo (CNST-002)
  - Tablas históricas (schema SQL + modelos Django)
  - Tablas agregadas (7 tablas documentadas)
  - Tabla control ETL (job_execution_log)
  - DIDs y constantes

- Sección 3: Proceso ETL
  - Stored Procedure sp_etl_daily() (completo)
  - APScheduler configuration (CNST-013)
  - Cron backup
  - Management command
  - Flujo ETL completo con diagrama

**📊 Estadísticas:**
- Líneas: ~2,600
- Tamaño: ~95KB
- Documentos aplicados: 3 (CLEAN_CODE v3.0.1, RESTRICCIONES v1.0.0, RBAC v6.0.0)
- Restricciones aplicadas: 14 (CNST-001 a CNST-031)

**📚 Referencias:**
- CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
- RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
- MODELO_RBAC_IACT_v6_0_0.md (2 partes)

**🔜 Próxima parte:**
- Sección 4: Arquitectura Django
- Sección 5: APIs y Endpoints
- Sección 6: Flujo de Datos Completo
