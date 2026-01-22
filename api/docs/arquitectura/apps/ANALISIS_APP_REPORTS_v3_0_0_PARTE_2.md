---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Reports PARTE 2/5
categoria: arquitectura/apps
tema: apps/reports/ - Services y Report Generators
autor: Claude Technical Analysis
tags: [reports, services, generators, pandas, clean-code]
estado: definitivo
parte: 2 de 5
relacionado:
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_1.md
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_3.md
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_4.md
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_5.md
replaces: []
---

# ANÁLISIS DE apps/reports/ v3.0.0 - PARTE 2/5
## SERVICES Y REPORT GENERATORS

---

## 1. REPORT GENERATOR SERVICE

```python
"""
Services para apps/reports/.

CLEAN_CODE v3.0.1 PARTE 2, Sección 20: Service Layer Pattern.
"""

from typing import Dict, List
import pandas as pd
from datetime import datetime

from apps.reports.models import Report, ReportExecution
from apps.reports.exceptions import ExportTooLargeError, ReportGenerationError
from apps.reports.constants import MAX_EXPORT_ROWS


class ReportGeneratorService:
    """
    Service para generación de reportes.
    
    Responsabilidades:
    - Coordinar generación de reportes
    - Validar parámetros
    - Consultar datos de apps/ivr/
    - Crear metadata (Report instance)
    - Coordinar export
    """
    
    @staticmethod
    def generate_report(
        report_type: str,
        parameters: dict,
        file_format: str,
        generated_by
    ) -> Report:
        """
        Genera reporte.
        
        Args:
            report_type: Tipo (quarterly, transfers, etc)
            parameters: Parámetros y filtros (dict)
            file_format: Formato (xlsx, csv, pdf)
            generated_by: User instance
        
        Returns:
            Report instance
        
        Raises:
            ReportGenerationError: Si falla generación
        """
        from apps.reports.generators import REPORT_GENERATORS
        
        # Obtener generator class
        generator_class = REPORT_GENERATORS.get(report_type)
        if not generator_class:
            raise ReportGenerationError(
                f"Unknown report type: {report_type}"
            )
        
        # Crear Report instance (metadata)
        report = Report.objects.create(
            report_type=report_type,
            report_name=generator_class.get_report_name(parameters),
            generated_by=generated_by,
            file_format=file_format,
            parameters=parameters
        )
        
        # Crear ReportExecution
        execution = ReportExecution.objects.create(
            report=report,
            execution_status=ReportExecution.STATUS_RUNNING
        )
        
        try:
            # Medir tiempo
            start_time = datetime.now()
            
            # Generar datos
            generator = generator_class(parameters)
            data = generator.generate_data()
            
            # Validar tamaño (CNST-007)
            row_count = len(data)
            if row_count > MAX_EXPORT_ROWS:
                raise ExportTooLargeError(row_count)
            
            # Export a archivo
            from apps.reports.services import ExportService
            file_url, file_size = ExportService.export_data(
                data,
                file_format,
                report.report_id
            )
            
            # Actualizar Report
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            report.file_url = file_url
            report.file_size_bytes = file_size
            report.row_count = row_count
            report.generation_time_seconds = generation_time
            report.save(update_fields=[
                'file_url',
                'file_size_bytes',
                'row_count',
                'generation_time_seconds'
            ])
            
            # Marcar execution como success
            execution.execution_status = ReportExecution.STATUS_SUCCESS
            execution.finished_at = end_time
            execution.save(update_fields=['execution_status', 'finished_at'])
            
            return report
        
        except Exception as e:
            # Marcar execution como failed
            execution.execution_status = ReportExecution.STATUS_FAILED
            execution.finished_at = datetime.now()
            execution.error_message = str(e)
            execution.save(update_fields=[
                'execution_status',
                'finished_at',
                'error_message'
            ])
            
            raise ReportGenerationError(f"Report generation failed: {e}")
```

---

## 2. REPORT GENERATORS

### 2.1 Base Generator

```python
"""
Report generators (report types).

CLEAN_CODE v3.0.1: Clases auto-documentadas.
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseReportGenerator(ABC):
    """
    Base class para report generators.
    
    CLEAN_CODE v3.0.1: Template Method Pattern.
    
    Subclases deben implementar:
    - generate_data()
    - get_report_name()
    """
    
    def __init__(self, parameters: dict):
        """
        Args:
            parameters: Filtros y opciones (dict)
        """
        self.parameters = parameters
        self.validate_parameters()
    
    @abstractmethod
    def validate_parameters(self):
        """Valida parámetros requeridos."""
        pass
    
    @abstractmethod
    def generate_data(self) -> pd.DataFrame:
        """
        Genera datos del reporte.
        
        Returns:
            pd.DataFrame con datos
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_report_name(cls, parameters: dict) -> str:
        """
        Obtiene nombre del reporte.
        
        Args:
            parameters: Parámetros (dict)
        
        Returns:
            str: Nombre descriptivo
        """
        pass


### 2.2 Quarterly Summary Report

```python
class QuarterlySummaryReport(BaseReportGenerator):
    """
    Reporte de resumen trimestral.
    
    Consume: apps/ivr/QuarterlyReport
    
    Columnas:
    - Trimestre
    - Año
    - Total llamadas
    - Llamadas contestadas
    - Llamadas abandonadas
    - Duración promedio
    - Tasa abandono
    """
    
    def validate_parameters(self):
        """Valida parámetros."""
        required = ['year', 'quarter']
        for param in required:
            if param not in self.parameters:
                raise InvalidReportParametersError(
                    f"Missing required parameter: {param}"
                )
    
    def generate_data(self) -> pd.DataFrame:
        """
        Genera datos trimestrales.
        
        Returns:
            pd.DataFrame con resumen trimestral
        """
        from apps.ivr.models import QuarterlyReport
        
        # Consultar datos (CNST-002: READONLY)
        quarterly_data = QuarterlyReport.objects.filter(
            year=self.parameters['year'],
            quarter=self.parameters['quarter']
        )
        
        # Convertir a DataFrame
        data = []
        for record in quarterly_data:
            data.append({
                'Trimestre': f"Q{record.quarter}",
                'Año': record.year,
                'Total Llamadas': record.total_calls,
                'Contestadas': record.answered_calls,
                'Abandonadas': record.abandoned_calls,
                'Duración Promedio (seg)': record.average_duration,
                'Tiempo Espera Promedio (seg)': record.average_wait_time,
                'Tasa de Abandono (%)': record.abandonment_rate,
                'Generado': record.generated_at
            })
        
        df = pd.DataFrame(data)
        return df
    
    @classmethod
    def get_report_name(cls, parameters: dict) -> str:
        """Nombre del reporte."""
        return f"Resumen Trimestral Q{parameters['quarter']} {parameters['year']}"


### 2.3 Transfer Analysis Report

```python
class TransferAnalysisReport(BaseReportGenerator):
    """
    Reporte de análisis de transferencias.
    
    Consume: apps/ivr/TransferReport
    
    Columnas:
    - Fecha
    - Total transferencias
    - Exitosas
    - Fallidas
    - Tasa éxito
    - Duración promedio
    """
    
    def validate_parameters(self):
        """Valida parámetros."""
        required = ['start_date', 'end_date']
        for param in required:
            if param not in self.parameters:
                raise InvalidReportParametersError(
                    f"Missing required parameter: {param}"
                )
    
    def generate_data(self) -> pd.DataFrame:
        """Genera datos de transferencias."""
        from apps.ivr.models import TransferReport
        
        # Consultar datos
        transfer_data = TransferReport.objects.filter(
            date__gte=self.parameters['start_date'],
            date__lte=self.parameters['end_date']
        ).order_by('date')
        
        # Convertir a DataFrame
        data = []
        for record in transfer_data:
            data.append({
                'Fecha': record.date,
                'Total Transferencias': record.total_transfers,
                'Exitosas': record.successful_transfers,
                'Fallidas': record.failed_transfers,
                'Tasa de Éxito (%)': record.success_rate,
                'Duración Promedio (seg)': record.average_transfer_duration
            })
        
        df = pd.DataFrame(data)
        
        # Agregar totales
        if not df.empty:
            totals = {
                'Fecha': 'TOTAL',
                'Total Transferencias': df['Total Transferencias'].sum(),
                'Exitosas': df['Exitosas'].sum(),
                'Fallidas': df['Fallidas'].sum(),
                'Tasa de Éxito (%)': (
                    df['Exitosas'].sum() / df['Total Transferencias'].sum() * 100
                ) if df['Total Transferencias'].sum() > 0 else 0,
                'Duración Promedio (seg)': df['Duración Promedio (seg)'].mean()
            }
            df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)
        
        return df
    
    @classmethod
    def get_report_name(cls, parameters: dict) -> str:
        """Nombre del reporte."""
        return (
            f"Análisis de Transferencias "
            f"{parameters['start_date']} - {parameters['end_date']}"
        )


### 2.4 Abandoned Calls Report

```python
class AbandonedCallsReport(BaseReportGenerator):
    """
    Reporte de llamadas abandonadas.
    
    Consume: apps/ivr/AbandonedReport
    
    Columnas:
    - Fecha
    - Hora
    - Total abandonadas
    - Tiempo espera promedio
    - Abandonadas < 30s
    """
    
    def validate_parameters(self):
        """Valida parámetros."""
        required = ['start_date', 'end_date']
        for param in required:
            if param not in self.parameters:
                raise InvalidReportParametersError(
                    f"Missing required parameter: {param}"
                )
    
    def generate_data(self) -> pd.DataFrame:
        """Genera datos de abandonadas."""
        from apps.ivr.models import AbandonedReport
        
        # Consultar datos
        abandoned_data = AbandonedReport.objects.filter(
            date__gte=self.parameters['start_date'],
            date__lte=self.parameters['end_date']
        ).order_by('date', 'hour')
        
        # Convertir a DataFrame
        data = []
        for record in abandoned_data:
            data.append({
                'Fecha': record.date,
                'Hora': f"{record.hour:02d}:00",
                'Total Abandonadas': record.total_abandoned,
                'Tiempo Espera Promedio (seg)': record.average_wait_time,
                'Abandonadas < 30s': record.abandoned_before_30s,
                '% < 30s': (
                    record.abandoned_before_30s / record.total_abandoned * 100
                ) if record.total_abandoned > 0 else 0
            })
        
        df = pd.DataFrame(data)
        return df
    
    @classmethod
    def get_report_name(cls, parameters: dict) -> str:
        """Nombre del reporte."""
        return (
            f"Llamadas Abandonadas "
            f"{parameters['start_date']} - {parameters['end_date']}"
        )


### 2.5 Client Activity Report

```python
class ClientActivityReport(BaseReportGenerator):
    """
    Reporte de actividad de clientes.
    
    Consume: apps/ivr/ClientReport
    
    Columnas:
    - ID Cliente
    - Nombre
    - Total llamadas
    - Llamadas último mes
    - Duración total
    - Última llamada
    """
    
    def validate_parameters(self):
        """Valida parámetros."""
        # Opcional: puede filtrar por cliente específico
        pass
    
    def generate_data(self) -> pd.DataFrame:
        """Genera datos de clientes."""
        from apps.ivr.models import ClientReport
        
        # Consultar datos
        qs = ClientReport.objects.all()
        
        # Filtro opcional por cliente
        if 'client_id' in self.parameters:
            qs = qs.filter(client_id=self.parameters['client_id'])
        
        # Top N clientes
        limit = self.parameters.get('limit', 100)
        client_data = qs.order_by('-total_calls')[:limit]
        
        # Convertir a DataFrame
        data = []
        for record in client_data:
            data.append({
                'ID Cliente': record.client_id,
                'Nombre': record.client_name,
                'Total Llamadas': record.total_calls,
                'Llamadas Último Mes': record.calls_last_month,
                'Duración Total (min)': record.total_duration_minutes,
                'Última Llamada': record.last_call
            })
        
        df = pd.DataFrame(data)
        return df
    
    @classmethod
    def get_report_name(cls, parameters: dict) -> str:
        """Nombre del reporte."""
        if 'client_id' in parameters:
            return f"Actividad Cliente {parameters['client_id']}"
        return f"Actividad de Clientes (Top {parameters.get('limit', 100)})"
```

---

## 3. QUERY BUILDER SERVICE

```python
"""
Query Builder Service.

CLEAN_CODE v3.0.1: Construcción dinámica de queries.
"""


class QueryBuilderService:
    """
    Service para construcción de queries dinámicas.
    
    Permite aplicar filtros avanzados sin hardcodear
    en cada generator.
    """
    
    @staticmethod
    def apply_filters(queryset, filters: dict):
        """
        Aplica filtros a queryset.
        
        Args:
            queryset: Django QuerySet
            filters: Filtros a aplicar (dict)
                {
                    'date__gte': '2025-01-01',
                    'status': 'active',
                    'total_calls__gte': 100
                }
        
        Returns:
            QuerySet filtrado
        """
        for field, value in filters.items():
            queryset = queryset.filter(**{field: value})
        
        return queryset
    
    @staticmethod
    def apply_sorting(queryset, sort_by: str, order: str = 'asc'):
        """
        Aplica sorting a queryset.
        
        Args:
            queryset: Django QuerySet
            sort_by: Campo a ordenar (str)
            order: 'asc' o 'desc' (str)
        
        Returns:
            QuerySet ordenado
        """
        order_field = sort_by if order == 'asc' else f'-{sort_by}'
        return queryset.order_by(order_field)


# Generator registry
REPORT_GENERATORS = {
    'quarterly': QuarterlySummaryReport,
    'transfers': TransferAnalysisReport,
    'abandoned': AbandonedCallsReport,
    'clients': ClientActivityReport,
}
```

---

## 4. REPORT CACHE SERVICE

```python
"""
Report Cache Service.

CLEAN_CODE v3.0.1 CNST-010: Cache locmem (NO Redis).
"""

from django.core.cache import cache
from apps.reports.constants import CACHE_TTL_SECONDS, CACHE_KEY_PREFIX


class ReportCacheService:
    """
    Service para cache de reportes.
    
    CNST-010: Cache en locmem (NO Redis).
    
    Cachea resultados de reportes para evitar
    regeneraciones innecesarias.
    """
    
    @staticmethod
    def get_cache_key(report_type: str, parameters: dict) -> str:
        """
        Genera cache key.
        
        Args:
            report_type: Tipo de reporte (str)
            parameters: Parámetros (dict)
        
        Returns:
            str: Cache key
        """
        import hashlib
        import json
        
        # Serializar parámetros
        params_str = json.dumps(parameters, sort_keys=True)
        
        # Hash
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        return f"{CACHE_KEY_PREFIX}{report_type}_{params_hash}"
    
    @staticmethod
    def get_cached_report(report_type: str, parameters: dict):
        """
        Obtiene reporte cacheado.
        
        Args:
            report_type: Tipo (str)
            parameters: Parámetros (dict)
        
        Returns:
            Report instance o None
        """
        cache_key = ReportCacheService.get_cache_key(
            report_type,
            parameters
        )
        
        return cache.get(cache_key)
    
    @staticmethod
    def cache_report(report):
        """
        Cachea reporte.
        
        Args:
            report: Report instance
        """
        cache_key = ReportCacheService.get_cache_key(
            report.report_type,
            report.parameters
        )
        
        cache.set(
            cache_key,
            report,
            timeout=CACHE_TTL_SECONDS
        )
        
        # Marcar como cacheado
        report.is_cached = True
        report.save(update_fields=['is_cached'])
```

---

## 5. RESUMEN PARTE 2

```yaml
Services (4):
  ✅ ReportGeneratorService (~250 líneas)
     - Coordina generación
     - Valida tamaño (CNST-007)
     - Crea metadata

  ✅ QueryBuilderService (~80 líneas)
     - Filtros dinámicos
     - Sorting

  ✅ ReportCacheService (~100 líneas)
     - Cache locmem (CNST-010)
     - Evita regeneraciones

Report Generators (5):
  ✅ BaseReportGenerator (~50 líneas)
     - Template Method Pattern
  
  ✅ QuarterlySummaryReport (~120 líneas)
     - Consume QuarterlyReport
  
  ✅ TransferAnalysisReport (~140 líneas)
     - Consume TransferReport
     - Incluye totales
  
  ✅ AbandonedCallsReport (~120 líneas)
     - Consume AbandonedReport
  
  ✅ ClientActivityReport (~100 líneas)
     - Consume ClientReport
     - Top N clientes

Integration:
  ✅ Consume apps/ivr/ modelos (CNST-002)
  ✅ pandas DataFrame para procesamiento
  ✅ Validación export size (CNST-007)

Total: ~1,060 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 3/5: Export Service (Excel, CSV, PDF)**

Contenido:
- ✅ ExportService
- ✅ ExcelExporter (openpyxl)
- ✅ CSVExporter (pandas)
- ✅ PDFExporter (reportlab)
- ✅ File storage management
- ✅ URL generation

**Estimado:** ~1,200 líneas, 3 horas

---

**Fin de PARTE 2/5**
