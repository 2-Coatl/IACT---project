---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App IVR PARTE 1/4
categoria: arquitectura/apps
tema: apps/ivr/ - Fundamentos, Database Router y Modelos Core
autor: Claude Technical Analysis
tags: [ivr, mariadb, readonly, database-router, etl, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
estado: definitivo
parte: 1 de 4
relacionado:
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
  - ANALISIS_APP_IVR_v3_0_0_PARTE_2.md
  - ANALISIS_APP_IVR_v3_0_0_PARTE_3.md
  - ANALISIS_APP_IVR_v3_0_0_PARTE_4.md
replaces: []
---

# ANÁLISIS DE apps/ivr/ v3.0.0 - PARTE 1/4
## FUNDAMENTOS, DATABASE ROUTER Y MODELOS CORE

---

## 1. RESUMEN EJECUTIVO

### 1.1 Información General

```yaml
App: apps/ivr/
Tipo: COMPLEJA (4 partes)
Líneas estimadas: ~4,200 líneas código
Propósito: Modelos readonly para consultar datos IVR Legacy (MariaDB)
Funciones RBAC: 3 (IVR_VIEW, IVR_EDIT, IVR_STATS)
Dependencias:
  - MariaDB (IVR_LEGACY database)
  - ETL (Stored Procedures)
  - apps/access/ (RBAC)
Tests: 40 tests estimados
Coverage objetivo: >85%
```

### 1.2 Responsabilidades Core

```yaml
Acceso a Datos IVR:
  ✅ Modelos Django readonly (managed=False)
  ✅ Consulta MariaDB IVR_LEGACY
  ✅ Database Router (ZERO escritura - CNST-002)
  ✅ Abstracción de tablas legacy
  ✅ Queries optimizadas

Tablas MariaDB:
  Histórico (raw data):
    - tbl_historico_t1_2025 (Trimestre 1)
    - tbl_historico_t2_2025 (Trimestre 2)
    - tbl_historico_t3_2025 (Trimestre 3)
  
  Reportes (ETL agregado):
    - tbl_reporte_trimestral
    - tbl_reporte_transferencias
    - tbl_reporte_clientes
    - tbl_reporte_abandonadas
    - tbl_reporte_detalle_transferencias
    - tbl_reporte_menus_performance
    - tbl_reporte_menu_errores

Restricciones Aplicadas:
  - CNST-002: BD IVR readonly (ZERO escritura)
  - CNST-004: Timeout DB 300s
  - CNST-010: NO Redis (cache locmem)
```

### 1.3 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                  apps/ivr/                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Database Router:                                   │
│  └─ IVRRouter                                       │
│     ├─ db_for_read()  → 'ivr_legacy' ✅            │
│     ├─ db_for_write() → None (BLOQUEADO) ✅        │
│     └─ allow_migrate() → False ✅                   │
│                                                     │
│  Modelos Histórico (raw data):                     │
│  ├─ CallRecord (tbl_historico_t*_2025)             │
│  └─ Todos managed=False                            │
│                                                     │
│  Modelos Reportes (ETL agregado):                  │
│  ├─ QuarterlyReport (tbl_reporte_trimestral)       │
│  ├─ TransferReport (tbl_reporte_transferencias)    │
│  ├─ ClientReport (tbl_reporte_clientes)            │
│  ├─ AbandonedReport (tbl_reporte_abandonadas)      │
│  ├─ TransferDetailReport                           │
│  ├─ MenuPerformanceReport                          │
│  └─ MenuErrorReport                                │
│                                                     │
│  Services (readonly):                               │
│  ├─ IVRQueryService (consultas)                    │
│  ├─ CallRecordService (histórico)                  │
│  └─ ReportService (reportes agregados)             │
│                                                     │
│  Integration:                                       │
│  ├─ MariaDB (IVR_LEGACY)                           │
│  ├─ ETL (Stored Procedures)                        │
│  ├─ apps/reports/ (consume estos modelos)          │
│  └─ apps/dashboard/ (consume estos modelos)        │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         FLUJO DE DATOS (ARQUITECTURA ETL)           │
└─────────────────────────────────────────────────────┘

IVR Legacy System (PBX)
    ↓ (tiempo real)
MariaDB: tbl_historico_t*_2025
    ↓ (ETL cada 6-12h)
MariaDB: tbl_reporte_*
    ↓ (Database Router - readonly)
Django apps/ivr/ models (managed=False)
    ↓ (consultas)
apps/reports/, apps/dashboard/
    ↓ (API REST)
Frontend (React/Vue)
```

---

## 2. CLEAN CODE v3.0.1

```python
# ============================================================================
# CLASES - PascalCase
# ============================================================================

# Database Router
class IVRRouter:                        # ✅ Router para BD IVR

# Modelos Histórico
class CallRecord(models.Model):         # ✅ Registro de llamada
class CallRecordT1(CallRecord):         # ✅ Trimestre 1
class CallRecordT2(CallRecord):         # ✅ Trimestre 2
class CallRecordT3(CallRecord):         # ✅ Trimestre 3

# Modelos Reportes
class QuarterlyReport(models.Model):    # ✅ Reporte trimestral
class TransferReport(models.Model):     # ✅ Reporte transferencias
class ClientReport(models.Model):       # ✅ Reporte clientes
class AbandonedReport(models.Model):    # ✅ Reporte abandonadas

# Managers
class CallRecordManager(models.Manager): # ✅ Manager para CallRecord
class ReportManager(models.Manager):     # ✅ Manager para reportes

# Services
class IVRQueryService:                   # ✅ Consultas IVR
class CallRecordService:                 # ✅ Histórico llamadas
class ReportService:                     # ✅ Reportes agregados

# ============================================================================
# MÉTODOS - snake_case (inglés técnico)
# ============================================================================

# Queries
def get_call_records(filters):              # ✅ Obtener registros
def filter_by_date_range(start, end):       # ✅ Filtrar por fechas
def get_quarterly_data(year, quarter):      # ✅ Datos trimestrales
def get_transfer_stats(period):             # ✅ Stats transferencias

# Utils
def get_current_quarter():                   # ✅ Trimestre actual
def get_table_name_for_quarter(year, q):   # ✅ Nombre tabla
def validate_readonly_operation():          # ✅ Validar readonly

# ============================================================================
# DATABASE - Húngaro (legacy MariaDB)
# ============================================================================

# Tabla: tbl_historico_t1_2025 (Trimestre 1)
iIdLlamada                  # PK (bigint)       # ✅ ID llamada
dtFechaLlamada              # datetime          # ✅ Fecha llamada
cNumeroOrigen               # varchar(20)       # ✅ Número origen
cNumeroDestino              # varchar(20)       # ✅ Número destino
iDuracionSegundos           # int               # ✅ Duración
cEstadoLlamada              # varchar(50)       # ✅ Estado
cTipoLlamada                # varchar(50)       # ✅ Tipo

# Tabla: tbl_reporte_trimestral
iIdReporte                  # PK (int)          # ✅ ID reporte
iTrimestre                  # int               # ✅ Trimestre (1-4)
iAnio                       # int               # ✅ Año
iTotalLlamadas              # int               # ✅ Total llamadas
iLlamadasContestadas        # int               # ✅ Contestadas
fDuracionPromedio           # float             # ✅ Duración promedio
dtGeneradoEn                # datetime          # ✅ Generado

# ============================================================================
# PERMISSIONS - apps/access/
# ============================================================================

IVR_VIEW = 'IVR_VIEW'           # Ver datos IVR
IVR_EDIT = 'IVR_EDIT'           # Editar configuración IVR
IVR_STATS = 'IVR_STATS'         # Ver estadísticas IVR
```

---

## 3. RESTRICCIONES ARQUITECTÓNICAS

### 3.1 CNST-002: BD IVR Readonly (CRÍTICO)

```yaml
CNST-002: BD IVR Readonly (🔴 CRÍTICO)

Descripción:
  Base de datos IVR es READONLY para Django.
  ZERO escritura permitida.

Reglas:
  1. ❌ NO escribir a tablas IVR (INSERT, UPDATE, DELETE)
  2. ❌ NO ejecutar migrations en BD IVR
  3. ✅ SÍ managed=False en TODOS los modelos
  4. ✅ SÍ Database Router bloqueando escrituras
  5. ✅ SÍ usuario DB readonly (ivr_readonly)

Implementación:
  # models.py
  class CallRecord(models.Model):
      """Modelo readonly."""
      
      class Meta:
          managed = False              # ✅ Django NO gestiona schema
          db_table = 'tbl_historico_t1_2025'
  
  # Database Router
  class IVRRouter:
      ivr_apps = {'ivr'}
      
      def db_for_write(self, model, **hints):
          """BLOQUEA escrituras a BD IVR."""
          if model._meta.app_label in self.ivr_apps:
              return None              # ✅ BLOQUEADO
          return 'default'
      
      def allow_migrate(self, db, app_label, model_name=None, **hints):
          """NO migraciones en BD IVR."""
          if app_label in self.ivr_apps:
              return False             # ✅ BLOQUEADO
          return db == 'default'
  
  # settings.py
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          # ... PostgreSQL config
      },
      'ivr_legacy': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'ivr_legacy',
          'USER': 'ivr_readonly',      # ✅ Usuario readonly
          'PASSWORD': '***',
          'HOST': '10.0.1.50',
          'PORT': '3306',
          'OPTIONS': {
              'connect_timeout': 300,   # CNST-004: 300s timeout
          }
      }
  }
  
  DATABASE_ROUTERS = ['config.routers.IVRRouter']

Justificación:
  - BD IVR en producción 24/7
  - No se puede afectar sistema legacy
  - Compliance y auditoría

Referencias:
  - RESTRICCIONES v1.0.0 PARTE 1, Sección 1.3
  - ARQUITECTURA_ETL v3.0.0 PARTE 1, Decisión 2
```

### 3.2 CNST-004: Timeout DB

```yaml
CNST-004: Timeout DB 300s (🟡 IMPORTANTE)

Descripción:
  Timeout de conexión DB 300 segundos.

Implementación:
  DATABASES = {
      'ivr_legacy': {
          'OPTIONS': {
              'connect_timeout': 300,
              'read_timeout': 300,
              'write_timeout': 300,
          }
      }
  }

Referencias:
  - RESTRICCIONES v1.0.0 PARTE 2, Sección 4.2
```

---

## 4. DATABASE ROUTER

### 4.1 Archivo: config/routers.py

```python
"""
Database Router para apps/ivr/.

CNST-002: Protege BD IVR de escrituras.
"""


class IVRRouter:
    """
    Router para separar BD IVR (MariaDB readonly).
    
    CNST-002: BD IVR es READONLY.
    
    Responsabilidades:
    - Rutear lecturas a 'ivr_legacy'
    - BLOQUEAR escrituras (return None)
    - BLOQUEAR migraciones (return False)
    
    Apps afectadas:
    - apps/ivr/
    """
    
    ivr_apps = {'ivr'}
    
    def db_for_read(self, model, **hints):
        """
        Rutea lecturas de IVR a MariaDB.
        
        Args:
            model: Django model
            **hints: Query hints
        
        Returns:
            str: 'ivr_legacy' para apps/ivr/, else None
        """
        if model._meta.app_label in self.ivr_apps:
            return 'ivr_legacy'
        return None
    
    def db_for_write(self, model, **hints):
        """
        BLOQUEA escrituras a BD IVR.
        
        CNST-002: ZERO escritura permitida.
        
        Args:
            model: Django model
            **hints: Query hints
        
        Returns:
            None: Para apps/ivr/ (BLOQUEADO)
            'default': Para otras apps
        """
        if model._meta.app_label in self.ivr_apps:
            # CRÍTICO: Retorna None = BLOQUEA escritura
            return None
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Permite relaciones entre modelos.
        
        Args:
            obj1, obj2: Django models
            **hints: Query hints
        
        Returns:
            bool: True si permitido
        """
        # Permitir relaciones entre IVR models
        if (obj1._meta.app_label in self.ivr_apps or
            obj2._meta.app_label in self.ivr_apps):
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        BLOQUEA migraciones en BD IVR.
        
        CNST-002: NO migraciones en BD IVR.
        
        Args:
            db: Database alias
            app_label: App label
            model_name: Model name
            **hints: Migration hints
        
        Returns:
            False: Para apps/ivr/ (BLOQUEADO)
            True/None: Para otras apps
        """
        if app_label in self.ivr_apps:
            # CRÍTICO: NO migraciones en BD IVR
            return False
        
        # Otras apps solo migran en 'default'
        return db == 'default'
```

### 4.2 Configuration: settings.py

```python
# config/settings/base.py

# ============================================================================
# DATABASES - Dual DB (CNST-002)
# ============================================================================

DATABASES = {
    # PostgreSQL - DEFAULT (write)
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'iact_analytics',
        'USER': 'iact_app',
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    },
    
    # MariaDB - IVR LEGACY (readonly) - CNST-002
    'ivr_legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ivr_legacy',
        'USER': 'ivr_readonly',              # ✅ Usuario readonly
        'PASSWORD': env('IVR_DB_PASSWORD'),
        'HOST': env('IVR_DB_HOST'),          # ej: '10.0.1.50'
        'PORT': env('IVR_DB_PORT', default='3306'),
        'OPTIONS': {
            'connect_timeout': 300,          # CNST-004: 300s
            'read_timeout': 300,
            'write_timeout': 300,
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Database Router (CNST-002)
DATABASE_ROUTERS = ['config.routers.IVRRouter']

# ============================================================================
# CACHE - LocMem (CNST-010: NO Redis)
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'iact-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 5000,
        }
    }
}
```

---

## 5. MODELOS CORE (Histórico)

### 5.1 CallRecord (Abstract Base)

```python
"""
Modelos para apps/ivr/.

CNST-002: TODOS managed=False (readonly).
"""

from django.db import models


class CallRecord(models.Model):
    """
    Modelo base para registros de llamadas IVR.
    
    CNST-002: managed=False, readonly.
    
    Representa datos RAW del sistema IVR Legacy.
    
    Fields (nomenclatura húngara legacy):
    - iIdLlamada: PK
    - dtFechaLlamada: Timestamp
    - cNumeroOrigen: ANI
    - cNumeroDestino: DNIS
    - iDuracionSegundos: Duración
    - cEstadoLlamada: Estado
    - cTipoLlamada: Tipo
    
    Database: MariaDB (ivr_legacy)
    Tabla: Definida en subclases
    """
    
    # PK
    id_llamada = models.BigAutoField(
        primary_key=True,
        db_column='iIdLlamada'
    )
    
    # Timestamps
    fecha_llamada = models.DateTimeField(
        'Fecha Llamada',
        db_column='dtFechaLlamada',
        help_text='Timestamp de la llamada'
    )
    
    # Números
    numero_origen = models.CharField(
        'Número Origen',
        max_length=20,
        db_column='cNumeroOrigen',
        help_text='ANI - Automatic Number Identification'
    )
    
    numero_destino = models.CharField(
        'Número Destino',
        max_length=20,
        db_column='cNumeroDestino',
        help_text='DNIS - Dialed Number Identification Service'
    )
    
    # Duración
    duracion_segundos = models.IntegerField(
        'Duración (seg)',
        default=0,
        db_column='iDuracionSegundos',
        help_text='Duración en segundos'
    )
    
    # Estado
    estado_llamada = models.CharField(
        'Estado',
        max_length=50,
        db_column='cEstadoLlamada',
        help_text='Estado: contestada, abandonada, ocupado, etc'
    )
    
    # Tipo
    tipo_llamada = models.CharField(
        'Tipo',
        max_length=50,
        db_column='cTipoLlamada',
        help_text='Tipo: entrante, saliente, interna, etc'
    )
    
    class Meta:
        abstract = True              # ✅ Base abstracta
        ordering = ['-fecha_llamada']
    
    def __str__(self):
        """String representation."""
        return f"Call {self.id_llamada} - {self.fecha_llamada}"
    
    @property
    def duracion_minutos(self):
        """Duración en minutos."""
        return round(self.duracion_segundos / 60, 2)


class CallRecordT1(CallRecord):
    """
    Llamadas Trimestre 1 (Ene-Mar).
    
    CNST-002: managed=False, readonly.
    Database: MariaDB (ivr_legacy)
    Tabla: tbl_historico_t1_2025
    """
    
    class Meta:
        managed = False              # ✅ Django NO gestiona schema
        db_table = 'tbl_historico_t1_2025'
        verbose_name = 'Llamada T1'
        verbose_name_plural = 'Llamadas Trimestre 1'


class CallRecordT2(CallRecord):
    """
    Llamadas Trimestre 2 (Abr-Jun).
    
    CNST-002: managed=False, readonly.
    Database: MariaDB (ivr_legacy)
    Tabla: tbl_historico_t2_2025
    """
    
    class Meta:
        managed = False
        db_table = 'tbl_historico_t2_2025'
        verbose_name = 'Llamada T2'
        verbose_name_plural = 'Llamadas Trimestre 2'


class CallRecordT3(CallRecord):
    """
    Llamadas Trimestre 3 (Jul-Sep).
    
    CNST-002: managed=False, readonly.
    Database: MariaDB (ivr_legacy)
    Tabla: tbl_historico_t3_2025
    """
    
    class Meta:
        managed = False
        db_table = 'tbl_historico_t3_2025'
        verbose_name = 'Llamada T3'
        verbose_name_plural = 'Llamadas Trimestre 3'
```

---

## 6. CONSTANTS

```python
"""
Constants para apps/ivr/.
"""

# Database
IVR_DATABASE_ALIAS = 'ivr_legacy'

# Trimestres
Q1_MONTHS = [1, 2, 3]       # Ene, Feb, Mar
Q2_MONTHS = [4, 5, 6]       # Abr, May, Jun
Q3_MONTHS = [7, 8, 9]       # Jul, Ago, Sep
Q4_MONTHS = [10, 11, 12]    # Oct, Nov, Dic

# Estados de llamada (legacy)
ESTADO_CONTESTADA = 'contestada'
ESTADO_ABANDONADA = 'abandonada'
ESTADO_OCUPADO = 'ocupado'
ESTADO_NO_CONTESTADA = 'no_contestada'

# Tipos de llamada
TIPO_ENTRANTE = 'entrante'
TIPO_SALIENTE = 'saliente'
TIPO_INTERNA = 'interna'

# Cache
CACHE_TTL_SECONDS = 300     # 5 minutos

# Funciones RBAC
IVR_VIEW = 'IVR_VIEW'
IVR_EDIT = 'IVR_EDIT'
IVR_STATS = 'IVR_STATS'
```

---

## 7. RESUMEN PARTE 1

```yaml
Database Router:
  ✅ IVRRouter (~100 líneas)
     - db_for_read() → 'ivr_legacy'
     - db_for_write() → None (BLOQUEADO)
     - allow_migrate() → False

Settings Configuration:
  ✅ Dual DB (PostgreSQL + MariaDB)
  ✅ Usuario ivr_readonly
  ✅ Timeout 300s
  ✅ DATABASE_ROUTERS configurado

Modelos (4):
  ✅ CallRecord (abstract base)
  ✅ CallRecordT1 (managed=False)
  ✅ CallRecordT2 (managed=False)
  ✅ CallRecordT3 (managed=False)

Restricciones Aplicadas (2):
  ✅ CNST-002: BD IVR readonly
  ✅ CNST-004: Timeout 300s

Constants:
  ✅ Estados, tipos, trimestres
  ✅ RBAC functions (3)

Líneas código: ~800 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 2/4: Modelos de Reportes y ETL Integration**

Contenido:
- ✅ QuarterlyReport (tbl_reporte_trimestral)
- ✅ TransferReport (tbl_reporte_transferencias)
- ✅ ClientReport (tbl_reporte_clientes)
- ✅ AbandonedReport (tbl_reporte_abandonadas)
- ✅ 4 modelos adicionales de reportes
- ✅ Managers customizados

**Estimado:** ~1,100 líneas, 3 horas

---

**Fin de PARTE 1/4**
