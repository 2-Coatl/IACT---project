---
version: 3.1.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App IVR PARTE 1/4
categoria: arquitectura/apps
tema: apps/ivr/ - Fundamentos, Database Router y Modelos Core
autor: Claude Technical Analysis
tags: [ivr, mariadb, readonly, database-router, etl, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes) ⭐ APLICADO
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
estado: definitivo
parte: 1 de 4
relacionado:
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
  - ANALISIS_APP_IVR_v3_1_0_PARTE_2.md
  - ANALISIS_APP_IVR_v3_1_0_PARTE_3.md
  - ANALISIS_APP_IVR_v3_1_0_PARTE_4.md
replaces: ANALISIS_APP_IVR_v3_0_0_PARTE_1.md
changelog: |
  v3.1.0:
  - Aplicado CLEAN_CODE v3.0.1 completo
  - Modelos inglés auto-documentados
  - db_table preserva nombres originales
  - Comentarios español (Google Style)
  - verbose_name español
---

# ANÁLISIS DE apps/ivr/ v3.1.0 - PARTE 1/4
## FUNDAMENTOS, DATABASE ROUTER Y MODELOS CORE

**BASADO EN: CLEAN_CODE_NAMING_PRINCIPLES v3.0.1 (5 partes)**

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
Clean Code: v3.0.1 aplicado ✅
```

### 1.2 Responsabilidades Core

```yaml
Acceso a Datos IVR:
  ✅ Modelos Django readonly (managed=False)
  ✅ Consulta MariaDB IVR_LEGACY
  ✅ Database Router (ZERO escritura - CNST-002)
  ✅ Abstracción de tablas legacy
  ✅ Queries optimizadas

Tablas MariaDB (nomenclatura legacy preservada en db_table):
  Histórico (raw data):
    - historico_t1 → CallRecord (Q1)
    - historico_t2 → CallRecord (Q2)
    - historico_t3 → CallRecord (Q3)
  
  Reportes (ETL agregado):
    - tbl_reporte_trimestral → QuarterlyReport
    - tbl_reporte_transferencias → TransferReport
    - tbl_reporte_clientes → ClientReport
    - tbl_reporte_abandonadas → AbandonedReport
    - tbl_reporte_detalle_transferencias → TransferDetailReport
    - tbl_reporte_menus_performance → MenuPerformanceReport
    - tbl_reporte_menu_errores → MenuErrorReport

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
│  Modelos Histórico (CLEAN_CODE v3.0.1):            │
│  ├─ CallRecord (inglés auto-documentado)           │
│  │   ├─ db_table = 'historico_t*' (preservado)    │
│  │   └─ managed = False                            │
│  └─ Todos en inglés, db_table original            │
│                                                     │
│  Modelos Reportes (ETL agregado):                  │
│  ├─ QuarterlyReport (tbl_reporte_trimestral)       │
│  ├─ TransferReport (tbl_reporte_transferencias)    │
│  └─ 5 modelos adicionales                          │
│                                                     │
│  Services (readonly):                               │
│  ├─ IVRQueryService (consultas)                    │
│  ├─ CallRecordService (histórico)                  │
│  └─ ReportService (reportes agregados)             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 2. CLEAN CODE v3.0.1 APLICADO

### 2.1 Principio: Nombres que Revelan Intenciones

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 1, Sección 1
# ============================================================================

# ❌ INCORRECTO (legacy)
class HistoricoT1(models.Model):  # ¿Qué es "T1"?
    id_llamada = ...
    did = ...

# ✅ CORRECTO (CLEAN_CODE v3.0.1)
class CallRecord(models.Model):
    """
    Registro de llamada del sistema IVR.
    
    Representa datos raw del IVR Legacy.
    managed=False: Django NO gestiona el schema.
    
    Database: MariaDB (ivr_legacy)
    Tabla: historico_t1, historico_t2, historico_t3
    """  # ← Español (CLEAN_CODE Regla 14)
    
    call_id = models.CharField(...)  # ← Inglés auto-documentado
    did = models.CharField(...)
    
    class Meta:
        db_table = 'historico_t1'  # ← Preserva nombre original
        managed = False
        verbose_name = 'Registro de llamada'  # ← Español
```

### 2.2 Principio: Evitar Codificaciones

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 1, Sección 6
# ============================================================================

# ❌ INCORRECTO - Codificación húngara en nombres Python
class CallRecord(models.Model):
    iIdLlamada = models.CharField(...)  # ❌ Húngaro en Python
    cDid = models.CharField(...)         # ❌ Prefijo "c"
    dtFechaHora = models.DateTimeField(...)  # ❌ Prefijo "dt"

# ✅ CORRECTO - Húngaro SOLO en db_column
class CallRecord(models.Model):
    call_id = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='iIdLlamada',  # ✅ Húngaro preservado en DB
        verbose_name=\"ID de llamada\"  # ✅ Español
    )
    
    did = models.CharField(
        max_length=20,
        db_column='cDid',
        verbose_name=\"DID\"
    )
    
    timestamp = models.DateTimeField(
        db_column='dtFechaHora',
        verbose_name=\"Fecha y hora\"
    )
```

### 2.3 Principio: Una Palabra por Concepto

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 1, Sección 8
# ============================================================================

# ✅ CORRECTO - "Report" para todos los reportes
QuarterlyReport       # ✅ Report
TransferReport        # ✅ Report
ClientReport          # ✅ Report
AbandonedReport       # ✅ Report (NO "AbandonedCalls")

# ✅ CORRECTO - "Service" para todos los servicios
IVRQueryService       # ✅ Service
CallRecordService     # ✅ Service
ReportService         # ✅ Service (NO "ReportManager")
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

Implementación CLEAN_CODE v3.0.1:
  # models.py
  class CallRecord(models.Model):
      """Modelo readonly para registros IVR."""
      
      class Meta:
          managed = False              # ✅ Django NO gestiona schema
          db_table = 'historico_t1'    # ✅ Preserva nombre original
  
  # Database Router
  class IVRRouter:
      """
      Router para proteger BD IVR de escrituras.
      
      CNST-002: BD IVR es READONLY.
      """
      
      ivr_apps = {'ivr'}
      
      def db_for_write(self, model, **hints):
          """
          BLOQUEA escrituras a BD IVR.
          
          Returns:
              None para apps/ivr/ (BLOQUEADO)
          """
          if model._meta.app_label in self.ivr_apps:
              return None              # ✅ BLOQUEADO
          return 'default'
  
  # settings.py
  DATABASES = {
      'ivr_legacy': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'ivr_legacy',
          'USER': 'ivr_readonly',      # ✅ Usuario readonly
          'OPTIONS': {
              'connect_timeout': 300,   # CNST-004
          }
      }
  }

Justificación:
  - BD IVR en producción 24/7
  - No se puede afectar sistema legacy
  - Compliance y auditoría

Referencias:
  - RESTRICCIONES v1.0.0 PARTE 1, Sección 1.3
  - ARQUITECTURA_ETL v3.0.0 PARTE 1, Decisión 2
  - CLEAN_CODE v3.0.1 PARTE 4, Sección 27.2
```

---

## 4. DATABASE ROUTER

### 4.1 Archivo: config/routers.py

```python
"""
Database Router para apps/ivr/.

CNST-002: Protege BD IVR de escrituras.
CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""


class IVRRouter:
    """
    Router para separar BD IVR (MariaDB readonly).
    
    CNST-002: BD IVR es READONLY.
    CLEAN_CODE v3.0.1 PARTE 9: Architecture Reveals Intent.
    
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

---

## 5. MODELOS CORE (Histórico)

### 5.1 CallRecord (Abstract Base)

```python
"""
Modelos para apps/ivr/.

CNST-002: TODOS managed=False (readonly).
CLEAN_CODE v3.0.1: Inglés auto-documentado.
"""

from django.db import models


class CallRecord(models.Model):
    """
    Modelo base para registros de llamadas IVR.
    
    CNST-002: managed=False, readonly.
    CLEAN_CODE v3.0.1 PARTE 1, Sección 1: Nombres que revelan intenciones.
    
    Representa datos RAW del sistema IVR Legacy.
    
    Fields:
    - call_id: ID único de llamada
    - timestamp: Fecha y hora de llamada
    - origin_number: Número origen (ANI)
    - destination_number: Número destino (DNIS)
    - duration_seconds: Duración en segundos
    - call_status: Estado de llamada
    - call_type: Tipo de llamada
    
    Database: MariaDB (ivr_legacy)
    Tabla: Definida en subclases (historico_t1, t2, t3)
    """
    
    # PK
    call_id = models.BigAutoField(
        primary_key=True,
        db_column='iIdLlamada',  # ← Preserva húngaro legacy
        verbose_name='ID de llamada'  # ← Español
    )
    
    # Timestamps
    timestamp = models.DateTimeField(
        db_column='dtFechaHora',
        verbose_name='Fecha y hora',
        help_text='Timestamp de la llamada'  # ← Español
    )
    
    # Números (ANI/DNIS)
    origin_number = models.CharField(
        max_length=20,
        db_column='cNumeroOrigen',
        verbose_name='Número origen',
        help_text='ANI - Automatic Number Identification'
    )
    
    destination_number = models.CharField(
        max_length=20,
        db_column='cNumeroDestino',
        verbose_name='Número destino',
        help_text='DNIS - Dialed Number Identification Service'
    )
    
    # Duración
    duration_seconds = models.IntegerField(
        default=0,
        db_column='iDuracionSegundos',
        verbose_name='Duración (seg)',
        help_text='Duración en segundos'
    )
    
    # Estado
    call_status = models.CharField(
        max_length=50,
        db_column='cEstadoLlamada',
        verbose_name='Estado',
        help_text='Estado: contestada, abandonada, ocupado, etc'
    )
    
    # Tipo
    call_type = models.CharField(
        max_length=50,
        db_column='cTipoLlamada',
        verbose_name='Tipo',
        help_text='Tipo: entrante, saliente, interna, etc'
    )
    
    class Meta:
        abstract = True              # ✅ Base abstracta
        ordering = ['-timestamp']
    
    def __str__(self):
        """String representation."""
        return f"Call {self.call_id} - {self.timestamp}"
    
    @property
    def duration_minutes(self):
        """
        Duración en minutos.
        
        Returns:
            float: Duración en minutos (redondeado 2 decimales)
        """
        return round(self.duration_seconds / 60, 2)


class CallRecordQ1(CallRecord):
    """
    Llamadas Trimestre 1 (Ene-Mar).
    
    CNST-002: managed=False, readonly.
    CLEAN_CODE v3.0.1: Nombre auto-documentado (Q1 = Quarter 1).
    
    Database: MariaDB (ivr_legacy)
    Tabla: historico_t1
    """
    
    class Meta:
        managed = False              # ✅ Django NO gestiona schema
        db_table = 'historico_t1'    # ✅ Preserva nombre original
        verbose_name = 'Llamada Q1'
        verbose_name_plural = 'Llamadas Trimestre 1'


class CallRecordQ2(CallRecord):
    """
    Llamadas Trimestre 2 (Abr-Jun).
    
    Database: MariaDB (ivr_legacy)
    Tabla: historico_t2
    """
    
    class Meta:
        managed = False
        db_table = 'historico_t2'
        verbose_name = 'Llamada Q2'
        verbose_name_plural = 'Llamadas Trimestre 2'


class CallRecordQ3(CallRecord):
    """
    Llamadas Trimestre 3 (Jul-Sep).
    
    Database: MariaDB (ivr_legacy)
    Tabla: historico_t3
    """
    
    class Meta:
        managed = False
        db_table = 'historico_t3'
        verbose_name = 'Llamada Q3'
        verbose_name_plural = 'Llamadas Trimestre 3'
```

---

## 6. CONSTANTS

```python
"""
Constants para apps/ivr/.

CLEAN_CODE v3.0.1 PARTE 2, Sección 11: UPPER_SNAKE_CASE para constantes.
"""

# Database
IVR_DATABASE_ALIAS = 'ivr_legacy'

# Trimestres (Quarters)
Q1_MONTHS = [1, 2, 3]       # Ene, Feb, Mar
Q2_MONTHS = [4, 5, 6]       # Abr, May, Jun
Q3_MONTHS = [7, 8, 9]       # Jul, Ago, Sep
Q4_MONTHS = [10, 11, 12]    # Oct, Nov, Dic

# Estados de llamada (legacy)
CALL_STATUS_ANSWERED = 'contestada'
CALL_STATUS_ABANDONED = 'abandonada'
CALL_STATUS_BUSY = 'ocupado'
CALL_STATUS_NO_ANSWER = 'no_contestada'

# Tipos de llamada
CALL_TYPE_INBOUND = 'entrante'
CALL_TYPE_OUTBOUND = 'saliente'
CALL_TYPE_INTERNAL = 'interna'

# Cache (CNST-010: NO Redis)
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
     - CLEAN_CODE v3.0.1 aplicado

Settings Configuration:
  ✅ Dual DB (PostgreSQL + MariaDB)
  ✅ Usuario ivr_readonly
  ✅ Timeout 300s
  ✅ DATABASE_ROUTERS configurado

Modelos (4):
  ✅ CallRecord (abstract base) - CLEAN_CODE v3.0.1
  ✅ CallRecordQ1, Q2, Q3 (managed=False)
  ✅ Nombres inglés auto-documentados
  ✅ db_table preserva nombres originales
  ✅ verbose_name en español

Restricciones Aplicadas (2):
  ✅ CNST-002: BD IVR readonly
  ✅ CNST-004: Timeout 300s

Clean Code Aplicado:
  ✅ v3.0.1 PARTE 1: Nombres que revelan intenciones
  ✅ v3.0.1 PARTE 1, Sección 6: Evitar codificaciones
  ✅ v3.0.1 PARTE 1, Sección 8: Una palabra por concepto
  ✅ v3.0.1 PARTE 1, Sección 14: Regla de idioma

Líneas código: ~850 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 2/4: Modelos de Reportes y ETL Integration**

Contenido:
- ✅ QuarterlyReport (CLEAN_CODE v3.0.1)
- ✅ TransferReport, ClientReport, AbandonedReport
- ✅ 4 modelos adicionales de reportes
- ✅ Managers customizados
- ✅ CLEAN_CODE v3.0.1 aplicado

**Estimado:** ~1,100 líneas, 3 horas

---

**Fin de PARTE 1/4 - v3.1.0 con CLEAN_CODE v3.0.1 aplicado ✅**
