---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Reports PARTE 1/5
categoria: arquitectura/apps
tema: apps/reports/ - Fundamentos, Models y Report Types
autor: Claude Technical Analysis
tags: [reports, export, excel, csv, pdf, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes) ⭐ APLICADO
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
estado: definitivo
parte: 1 de 5
relacionado:
  - ANALISIS_APP_IVR_v3_1_0_PARTE_1.md (consume modelos IVR)
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_2.md
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_3.md
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_4.md
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_5.md
replaces: []
---

# ANÁLISIS DE apps/reports/ v3.0.0 - PARTE 1/5
## FUNDAMENTOS, MODELS Y REPORT TYPES

**BASADO EN: CLEAN_CODE_NAMING_PRINCIPLES v3.0.1 (5 partes)**

---

## 1. RESUMEN EJECUTIVO

### 1.1 Información General

```yaml
App: apps/reports/
Tipo: COMPLEJA (5 partes)
Líneas estimadas: ~4,500 líneas código
Propósito: Generación de reportes tabulares desde datos ETL
Funciones RBAC: 4 (REPORTS_VIEW, REPORTS_CREATE, REPORTS_EXPORT, REPORTS_DELETE)
Dependencias:
  - apps/ivr/ (consume modelos readonly MariaDB)
  - openpyxl (export Excel)
  - reportlab (export PDF)
  - pandas (procesamiento datos)
  - apps/access/ (RBAC)
  - apps/audit/ (logs de generación)
Tests: 50 tests estimados
Coverage objetivo: >90%
Clean Code: v3.0.1 aplicado ✅
```

### 1.2 Responsabilidades Core

```yaml
Generación de Reportes:
  ✅ Reportes bajo demanda (POST)
  ✅ Consulta modelos IVR (readonly)
  ✅ Agregación y cálculos
  ✅ Filtros avanzados
  ✅ Paginación

Export Formats:
  ✅ Excel (.xlsx) - openpyxl
  ✅ CSV (.csv) - pandas
  ✅ PDF (.pdf) - reportlab
  ✅ JSON (API REST)

Report Types:
  ✅ Quarterly Summary (trimestral)
  ✅ Transfer Analysis (transferencias)
  ✅ Abandoned Calls (abandonadas)
  ✅ Client Activity (clientes)
  ✅ Custom Reports (personalizados)

Restricciones Aplicadas:
  - CNST-007: Export max 100K registros
  - CNST-031: Auditoría completa
  - CNST-002: Readonly IVR (consume apps/ivr/)
```

### 1.3 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│               apps/reports/                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Models (PostgreSQL DEFAULT):                      │
│  ├─ Report (metadata de reportes)                  │
│  ├─ ReportExecution (historial generaciones)       │
│  ├─ ReportTemplate (plantillas configurables)      │
│  └─ ReportSchedule (reportes programados)          │
│                                                     │
│  Services:                                          │
│  ├─ ReportGeneratorService (generación)            │
│  ├─ ExportService (Excel, CSV, PDF)                │
│  ├─ QueryBuilderService (filtros dinámicos)        │
│  └─ ReportCacheService (cache resultados)          │
│                                                     │
│  Report Types:                                      │
│  ├─ QuarterlySummaryReport                         │
│  ├─ TransferAnalysisReport                         │
│  ├─ AbandonedCallsReport                           │
│  ├─ ClientActivityReport                           │
│  └─ CustomReport (queries dinámicas)               │
│                                                     │
│  Integration:                                       │
│  ├─ apps/ivr/ (consume modelos ETL)                │
│  │   - QuarterlyReport                             │
│  │   - TransferReport                              │
│  │   - CallRecordQ1, Q2, Q3                        │
│  ├─ apps/audit/ (logs generación)                  │
│  └─ Storage (archivos generados)                   │
│                                                     │
└─────────────────────────────────────────────────────┘

FLUJO:
  User Request → POST /api/v1/reports/generate/
      ↓
  ReportGeneratorService → Consulta apps/ivr/
      ↓
  QueryBuilderService → Aplica filtros
      ↓
  Aggregate Data → Pandas DataFrame
      ↓
  ExportService → Genera Excel/CSV/PDF
      ↓
  Storage → Guarda archivo
      ↓
  Response → URL descarga
```

---

## 2. CLEAN CODE v3.0.1 APLICADO

### 2.1 Principio: Nombres que Revelan Intenciones

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 1, Sección 1
# ============================================================================

# ❌ INCORRECTO
class Report(models.Model):  # ¿Qué tipo de report?
    data = models.TextField()  # ¿Qué datos?

# ✅ CORRECTO (CLEAN_CODE v3.0.1)
class Report(models.Model):
    """
    Metadata de reporte generado.
    
    Almacena información del reporte:
    - Tipo (quarterly, transfers, etc)
    - Parámetros de generación
    - Formato (Excel, CSV, PDF)
    - URL del archivo generado
    
    Database: PostgreSQL (DEFAULT)
    """
    
    report_type = models.CharField(...)      # ✅ Auto-documentado
    generated_at = models.DateTimeField(...) # ✅ Claro
    file_format = models.CharField(...)      # ✅ Específico
    file_url = models.URLField(...)          # ✅ Específico
```

### 2.2 Principio: Una Palabra por Concepto

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 1, Sección 8
# ============================================================================

# ✅ CORRECTO - "Service" para todos los servicios
ReportGeneratorService    # ✅ Service
ExportService             # ✅ Service
QueryBuilderService       # ✅ Service
ReportCacheService        # ✅ Service (NO "ReportManager")

# ✅ CORRECTO - "Report" para tipos de reportes
QuarterlySummaryReport    # ✅ Report
TransferAnalysisReport    # ✅ Report
AbandonedCallsReport      # ✅ Report
ClientActivityReport      # ✅ Report
```

### 2.3 Principio: Service Layer Pattern

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 2, Sección 20
# ============================================================================

# ✅ CORRECTO - Lógica en Service, View delgado
class ReportGeneratorService:
    """
    Service para generación de reportes.
    
    Responsabilidades:
    - Consultar datos de apps/ivr/
    - Aplicar filtros y agregaciones
    - Formatear datos
    - Coordinar export
    """
    
    @staticmethod
    def generate_quarterly_report(quarter, year, filters):
        """
        Genera reporte trimestral.
        
        Args:
            quarter: Trimestre 1-4 (int)
            year: Año (int)
            filters: Filtros adicionales (dict)
        
        Returns:
            Report instance
        """
        # Lógica compleja aquí
        pass
```

---

## 3. RESTRICCIONES ARQUITECTÓNICAS

### 3.1 CNST-007: Export Limit 100K

```yaml
CNST-007: Export Limit 100K Registros (🟡 IMPORTANTE)

Descripción:
  Máximo 100,000 registros por export.
  Previene timeouts y archivos enormes.

Reglas:
  1. ✅ Validar count antes de export
  2. ✅ Lanzar exception si > 100K
  3. ✅ Mostrar mensaje al usuario
  4. ✅ Sugerir filtros adicionales
  5. ✅ Logs de rechazos

Implementación CLEAN_CODE v3.0.1:
  # services.py
  class ExportService:
      MAX_EXPORT_ROWS = 100_000  # CNST-007
      
      @staticmethod
      def validate_export_size(queryset):
          """
          Valida tamaño de export.
          
          Raises:
              ExportTooLargeError: Si > 100K registros
          """
          count = queryset.count()
          
          if count > ExportService.MAX_EXPORT_ROWS:
              raise ExportTooLargeError(
                  f"Export would contain {count:,} rows. "
                  f"Maximum is {ExportService.MAX_EXPORT_ROWS:,}. "
                  f"Please add more filters."
              )

Justificación:
  - Evitar timeouts en generación
  - Prevenir archivos Excel > 100MB
  - Performance de descarga

Referencias:
  - RESTRICCIONES v1.0.0 PARTE 2, Sección 2.3
```

### 3.2 CNST-002: Readonly IVR (Integration)

```yaml
CNST-002: Consume apps/ivr/ Readonly (🔴 CRÍTICO)

Descripción:
  apps/reports/ consume modelos de apps/ivr/.
  NO escribe a BD IVR.

Reglas:
  1. ✅ Importar modelos de apps.ivr.models
  2. ✅ SOLO queries SELECT
  3. ❌ NO crear/modificar/eliminar
  4. ✅ Usar Database Router de apps/ivr/

Implementación:
  # apps/reports/services.py
  from apps.ivr.models import QuarterlyReport, CallRecordQ1
  
  class ReportGeneratorService:
      @staticmethod
      def get_quarterly_data(quarter, year):
          """Consulta datos trimestrales (READONLY)."""
          
          # ✅ Solo SELECT
          return QuarterlyReport.objects.filter(
              quarter=quarter,
              year=year
          )
          
          # ❌ PROHIBIDO
          # QuarterlyReport.objects.create(...)
```

---

## 4. MODELOS DJANGO

### 4.1 Report

```python
"""
Modelos para apps/reports/.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
Database: PostgreSQL (DEFAULT).
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Report(models.Model):
    """
    Metadata de reporte generado.
    
    CNST-031: Auditoría de generaciones.
    CLEAN_CODE v3.0.1: Nombres que revelan intenciones.
    
    Almacena:
    - Tipo de reporte
    - Parámetros de generación
    - Usuario que generó
    - Formato de export
    - URL del archivo
    
    Database: PostgreSQL (DEFAULT)
    Tabla: reports_report
    """
    
    # Report types
    TYPE_QUARTERLY = 'quarterly'
    TYPE_TRANSFERS = 'transfers'
    TYPE_ABANDONED = 'abandoned'
    TYPE_CLIENTS = 'clients'
    TYPE_CUSTOM = 'custom'
    
    TYPE_CHOICES = [
        (TYPE_QUARTERLY, 'Reporte Trimestral'),
        (TYPE_TRANSFERS, 'Análisis de Transferencias'),
        (TYPE_ABANDONED, 'Llamadas Abandonadas'),
        (TYPE_CLIENTS, 'Actividad de Clientes'),
        (TYPE_CUSTOM, 'Reporte Personalizado'),
    ]
    
    # File formats
    FORMAT_EXCEL = 'xlsx'
    FORMAT_CSV = 'csv'
    FORMAT_PDF = 'pdf'
    FORMAT_JSON = 'json'
    
    FORMAT_CHOICES = [
        (FORMAT_EXCEL, 'Excel'),
        (FORMAT_CSV, 'CSV'),
        (FORMAT_PDF, 'PDF'),
        (FORMAT_JSON, 'JSON'),
    ]
    
    # Fields
    report_id = models.BigAutoField(
        primary_key=True,
        verbose_name='ID de reporte'
    )
    
    report_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        verbose_name='Tipo de reporte'
    )
    
    report_name = models.CharField(
        max_length=255,
        verbose_name='Nombre del reporte',
        help_text='Descriptivo para el usuario'
    )
    
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports',
        verbose_name='Generado por'
    )
    
    generated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Generado',
        help_text='Timestamp de generación'
    )
    
    file_format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default=FORMAT_EXCEL,
        verbose_name='Formato'
    )
    
    file_url = models.URLField(
        max_length=500,
        verbose_name='URL del archivo',
        help_text='URL para descarga'
    )
    
    file_size_bytes = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Tamaño (bytes)'
    )
    
    row_count = models.IntegerField(
        default=0,
        verbose_name='Cantidad de filas',
        help_text='Registros en el reporte'
    )
    
    parameters = models.JSONField(
        default=dict,
        verbose_name='Parámetros',
        help_text='Filtros y opciones usados (JSON)'
    )
    
    generation_time_seconds = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Tiempo generación (seg)'
    )
    
    is_cached = models.BooleanField(
        default=False,
        verbose_name='En cache',
        help_text='Si resultado fue cacheado'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expira',
        help_text='Fecha expiración del archivo'
    )
    
    class Meta:
        db_table = 'reports_report'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['generated_by', '-generated_at']),
            models.Index(fields=['report_type', '-generated_at']),
        ]
    
    def __str__(self):
        """String representation."""
        return f"{self.report_name} - {self.generated_at}"
    
    @property
    def file_size_mb(self):
        """Tamaño en MB."""
        if self.file_size_bytes:
            return round(self.file_size_bytes / (1024**2), 2)
        return None
    
    @property
    def is_expired(self):
        """Verifica si expiró."""
        from django.utils import timezone
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class ReportExecution(models.Model):
    """
    Historial de ejecuciones de reportes.
    
    CNST-031: Auditoría completa de generaciones.
    
    Similar a JobExecution de apps/pipeline/,
    pero específico para reportes.
    
    Database: PostgreSQL (DEFAULT)
    Tabla: reports_execution
    """
    
    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_RUNNING, 'Generando'),
        (STATUS_SUCCESS, 'Exitoso'),
        (STATUS_FAILED, 'Fallido'),
    ]
    
    execution_id = models.BigAutoField(
        primary_key=True,
        verbose_name='ID de ejecución'
    )
    
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name='Reporte'
    )
    
    execution_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Estado'
    )
    
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Inicio'
    )
    
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fin'
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de error'
    )
    
    class Meta:
        db_table = 'reports_execution'
        verbose_name = 'Ejecución de reporte'
        verbose_name_plural = 'Ejecuciones de reportes'
        ordering = ['-started_at']


class ReportTemplate(models.Model):
    """
    Plantilla de reporte configurable.
    
    Permite definir reportes reutilizables con
    parámetros predefinidos.
    
    Database: PostgreSQL (DEFAULT)
    Tabla: reports_template
    """
    
    template_id = models.AutoField(
        primary_key=True,
        verbose_name='ID de plantilla'
    )
    
    template_name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Nombre de plantilla'
    )
    
    report_type = models.CharField(
        max_length=50,
        choices=Report.TYPE_CHOICES,
        verbose_name='Tipo de reporte'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    default_parameters = models.JSONField(
        default=dict,
        verbose_name='Parámetros por defecto',
        help_text='Filtros y opciones predefinidas (JSON)'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates',
        verbose_name='Creado por'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creado'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Actualizado'
    )
    
    class Meta:
        db_table = 'reports_template'
        verbose_name = 'Plantilla de reporte'
        verbose_name_plural = 'Plantillas de reportes'
        ordering = ['template_name']
    
    def __str__(self):
        """String representation."""
        return self.template_name
```

---

## 5. CONSTANTS

```python
"""
Constants para apps/reports/.

CLEAN_CODE v3.0.1 PARTE 2, Sección 11: UPPER_SNAKE_CASE.
"""

# Report types
REPORT_TYPE_QUARTERLY = 'quarterly'
REPORT_TYPE_TRANSFERS = 'transfers'
REPORT_TYPE_ABANDONED = 'abandoned'
REPORT_TYPE_CLIENTS = 'clients'
REPORT_TYPE_CUSTOM = 'custom'

# File formats
FILE_FORMAT_EXCEL = 'xlsx'
FILE_FORMAT_CSV = 'csv'
FILE_FORMAT_PDF = 'pdf'
FILE_FORMAT_JSON = 'json'

# Export limits (CNST-007)
MAX_EXPORT_ROWS = 100_000       # 100K registros max
MAX_FILE_SIZE_MB = 100          # 100MB max

# Cache
CACHE_TTL_SECONDS = 3600        # 1 hora
CACHE_KEY_PREFIX = 'report_'

# File expiration
FILE_EXPIRATION_DAYS = 7        # 7 días

# Funciones RBAC
REPORTS_VIEW = 'REPORTS_VIEW'
REPORTS_CREATE = 'REPORTS_CREATE'
REPORTS_EXPORT = 'REPORTS_EXPORT'
REPORTS_DELETE = 'REPORTS_DELETE'
```

---

## 6. EXCEPTIONS

```python
"""
Custom exceptions para reports.

CLEAN_CODE v3.0.1: Nombres descriptivos.
"""


class ReportsBaseException(Exception):
    """Base exception para reports."""
    pass


class ExportTooLargeError(ReportsBaseException):
    """Export excede límite de registros."""
    
    def __init__(self, row_count):
        """
        Args:
            row_count: Cantidad de filas (int)
        """
        self.row_count = row_count
        super().__init__(
            f"Export would contain {row_count:,} rows. "
            f"Maximum is {MAX_EXPORT_ROWS:,}. "
            f"Please add more filters."
        )


class ReportGenerationError(ReportsBaseException):
    """Error durante generación de reporte."""
    pass


class InvalidReportParametersError(ReportsBaseException):
    """Parámetros de reporte inválidos."""
    pass
```

---

## 7. RESUMEN PARTE 1

```yaml
Modelos (3):
  ✅ Report (~180 líneas)
     - Metadata reportes generados
     - Tipos, formatos, parámetros
     - CNST-031: Auditoría
  
  ✅ ReportExecution (~80 líneas)
     - Historial de generaciones
     - Status tracking
  
  ✅ ReportTemplate (~100 líneas)
     - Plantillas configurables
     - Parámetros predefinidos

Clean Code Aplicado:
  ✅ v3.0.1 PARTE 1: Nombres auto-documentados
  ✅ v3.0.1 PARTE 1, Sección 8: Una palabra por concepto
  ✅ v3.0.1 PARTE 2, Sección 11: UPPER_SNAKE_CASE

Restricciones Aplicadas (3):
  ✅ CNST-007: Export max 100K rows
  ✅ CNST-002: Readonly IVR integration
  ✅ CNST-031: Auditoría completa

Constants:
  ✅ Report types (5)
  ✅ File formats (4)
  ✅ Export limits (CNST-007)
  ✅ RBAC functions (4)

Exceptions (3):
  ✅ ExportTooLargeError
  ✅ ReportGenerationError
  ✅ InvalidReportParametersError

Líneas código: ~600 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 2/5: Services y Report Generators**

Contenido:
- ✅ ReportGeneratorService
- ✅ QuarterlySummaryReport
- ✅ TransferAnalysisReport
- ✅ AbandonedCallsReport
- ✅ ClientActivityReport
- ✅ QueryBuilderService
- ✅ ReportCacheService

**Estimado:** ~1,400 líneas, 3 horas

---

**Fin de PARTE 1/5 - v3.0.0 con CLEAN_CODE v3.0.1 aplicado ✅**
