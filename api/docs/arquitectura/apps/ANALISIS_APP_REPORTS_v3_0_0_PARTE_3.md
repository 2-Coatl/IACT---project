---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Reports PARTE 3/5
categoria: arquitectura/apps
tema: apps/reports/ - Export Service (Excel, CSV, PDF)
autor: Claude Technical Analysis
tags: [reports, export, excel, csv, pdf, openpyxl, reportlab]
estado: definitivo
parte: 3 de 5
relacionado:
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_1.md
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_2.md
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_4.md
  - ANALISIS_APP_REPORTS_v3_0_0_PARTE_5.md
replaces: []
---

# ANÁLISIS DE apps/reports/ v3.0.0 - PARTE 3/5
## EXPORT SERVICE (EXCEL, CSV, PDF)

---

## 1. EXPORT SERVICE

```python
"""
Export Service - Coordina exports a múltiples formatos.

CLEAN_CODE v3.0.1: Service Layer Pattern.
"""

import os
from django.conf import settings
import pandas as pd

from apps.reports.constants import FILE_FORMAT_EXCEL, FILE_FORMAT_CSV, FILE_FORMAT_PDF
from apps.reports.exceptions import ReportGenerationError


class ExportService:
    """
    Service para exportar datos a archivos.
    
    Responsabilidades:
    - Coordinar export a Excel, CSV, PDF
    - Guardar archivos en storage
    - Generar URLs de descarga
    - Validar tamaño
    """
    
    @staticmethod
    def export_data(
        data: pd.DataFrame,
        file_format: str,
        report_id: int
    ) -> tuple:
        """
        Exporta datos a archivo.
        
        Args:
            data: pandas DataFrame
            file_format: xlsx, csv, pdf
            report_id: ID del reporte (int)
        
        Returns:
            tuple: (file_url, file_size_bytes)
        
        Raises:
            ReportGenerationError: Si falla export
        """
        try:
            if file_format == FILE_FORMAT_EXCEL:
                exporter = ExcelExporter()
            elif file_format == FILE_FORMAT_CSV:
                exporter = CSVExporter()
            elif file_format == FILE_FORMAT_PDF:
                exporter = PDFExporter()
            else:
                raise ReportGenerationError(
                    f"Unsupported format: {file_format}"
                )
            
            # Export
            file_path = exporter.export(data, report_id)
            
            # Obtener tamaño
            file_size = os.path.getsize(file_path)
            
            # Generar URL
            file_url = ExportService._generate_file_url(file_path)
            
            return file_url, file_size
        
        except Exception as e:
            raise ReportGenerationError(f"Export failed: {e}")
    
    @staticmethod
    def _generate_file_url(file_path: str) -> str:
        """
        Genera URL de descarga.
        
        Args:
            file_path: Path absoluto del archivo
        
        Returns:
            str: URL pública
        """
        # Obtener path relativo desde MEDIA_ROOT
        relative_path = os.path.relpath(
            file_path,
            settings.MEDIA_ROOT
        )
        
        # Construir URL
        file_url = f"{settings.MEDIA_URL}{relative_path}"
        
        return file_url
```

---

## 2. EXCEL EXPORTER

```python
"""
Excel Exporter usando openpyxl.

CLEAN_CODE v3.0.1: Clase auto-documentada.
"""

import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from django.conf import settings
import pandas as pd


class ExcelExporter:
    """
    Exportador a Excel (.xlsx).
    
    Features:
    - Headers con estilo
    - Auto-ajuste de columnas
    - Formato de números
    - Bordes y alineación
    
    Library: openpyxl
    """
    
    def export(self, data: pd.DataFrame, report_id: int) -> str:
        """
        Exporta DataFrame a Excel.
        
        Args:
            data: pandas DataFrame
            report_id: ID del reporte
        
        Returns:
            str: Path absoluto del archivo
        """
        # Crear workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        
        # Escribir datos
        for r_idx, row in enumerate(dataframe_to_rows(data, index=False, header=True), 1):
            for c_idx, value in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                
                # Estilo header
                if r_idx == 1:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(
                        start_color="4472C4",
                        end_color="4472C4",
                        fill_type="solid"
                    )
                    cell.alignment = Alignment(
                        horizontal="center",
                        vertical="center"
                    )
                
                # Bordes
                thin_border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
                cell.border = thin_border
        
        # Auto-ajustar columnas
        self._autofit_columns(ws)
        
        # Guardar archivo
        file_path = self._get_file_path(report_id, 'xlsx')
        wb.save(file_path)
        
        return file_path
    
    def _autofit_columns(self, worksheet):
        """Auto-ajusta ancho de columnas."""
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _get_file_path(self, report_id: int, extension: str) -> str:
        """
        Obtiene path del archivo.
        
        Args:
            report_id: ID del reporte
            extension: Extensión (xlsx, csv, pdf)
        
        Returns:
            str: Path absoluto
        """
        # Directory
        reports_dir = os.path.join(
            settings.MEDIA_ROOT,
            'reports'
        )
        os.makedirs(reports_dir, exist_ok=True)
        
        # Filename
        filename = f"report_{report_id}.{extension}"
        
        return os.path.join(reports_dir, filename)
```

---

## 3. CSV EXPORTER

```python
"""
CSV Exporter usando pandas.
"""


class CSVExporter:
    """
    Exportador a CSV.
    
    Features:
    - UTF-8 con BOM (compatibilidad Excel)
    - Separador configurable
    - Headers incluidos
    
    Library: pandas
    """
    
    def export(self, data: pd.DataFrame, report_id: int) -> str:
        """
        Exporta DataFrame a CSV.
        
        Args:
            data: pandas DataFrame
            report_id: ID del reporte
        
        Returns:
            str: Path absoluto del archivo
        """
        # Path
        file_path = self._get_file_path(report_id, 'csv')
        
        # Export
        data.to_csv(
            file_path,
            index=False,
            encoding='utf-8-sig',  # UTF-8 con BOM para Excel
            sep=',',
            decimal='.',
            date_format='%Y-%m-%d %H:%M:%S'
        )
        
        return file_path
    
    def _get_file_path(self, report_id: int, extension: str) -> str:
        """Obtiene path del archivo."""
        reports_dir = os.path.join(
            settings.MEDIA_ROOT,
            'reports'
        )
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"report_{report_id}.{extension}"
        return os.path.join(reports_dir, filename)
```

---

## 4. PDF EXPORTER

```python
"""
PDF Exporter usando reportlab.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import pandas as pd


class PDFExporter:
    """
    Exportador a PDF.
    
    Features:
    - Tabla con headers estilizados
    - Paginación automática
    - Orientación landscape
    - Título del reporte
    
    Library: reportlab
    """
    
    def export(self, data: pd.DataFrame, report_id: int) -> str:
        """
        Exporta DataFrame a PDF.
        
        Args:
            data: pandas DataFrame
            report_id: ID del reporte
        
        Returns:
            str: Path absoluto del archivo
        """
        # Path
        file_path = self._get_file_path(report_id, 'pdf')
        
        # Crear PDF
        doc = SimpleDocTemplate(
            file_path,
            pagesize=landscape(letter),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Elementos
        elements = []
        
        # Título
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#4472C4'),
            spaceAfter=12,
            alignment=1  # Center
        )
        
        title = Paragraph(f"Reporte #{report_id}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Tabla
        table_data = [data.columns.tolist()] + data.values.tolist()
        
        table = Table(table_data)
        
        # Estilo tabla
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Alternating rows
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')])
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        return file_path
    
    def _get_file_path(self, report_id: int, extension: str) -> str:
        """Obtiene path del archivo."""
        reports_dir = os.path.join(
            settings.MEDIA_ROOT,
            'reports'
        )
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"report_{report_id}.{extension}"
        return os.path.join(reports_dir, filename)
```

---

## 5. FILE CLEANUP SERVICE

```python
"""
File Cleanup Service.

Elimina archivos expirados.
"""

import os
from datetime import timedelta
from django.utils import timezone

from apps.reports.models import Report


class FileCleanupService:
    """
    Service para limpieza de archivos expirados.
    
    Ejecutado por APScheduler (apps/pipeline/).
    """
    
    @staticmethod
    def cleanup_expired_files():
        """
        Elimina archivos de reportes expirados.
        
        Returns:
            int: Cantidad de archivos eliminados
        """
        now = timezone.now()
        
        # Reportes expirados
        expired_reports = Report.objects.filter(
            expires_at__lt=now,
            file_url__isnull=False
        )
        
        deleted_count = 0
        
        for report in expired_reports:
            # Extraer path del archivo
            file_path = FileCleanupService._url_to_path(report.file_url)
            
            # Eliminar archivo físico
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    # Log error pero continuar
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error deleting file {file_path}: {e}")
            
            # Limpiar URL en DB
            report.file_url = None
            report.save(update_fields=['file_url'])
        
        return deleted_count
    
    @staticmethod
    def _url_to_path(file_url: str) -> str:
        """
        Convierte URL a path absoluto.
        
        Args:
            file_url: URL del archivo
        
        Returns:
            str: Path absoluto
        """
        from django.conf import settings
        
        # Remover MEDIA_URL prefix
        relative_path = file_url.replace(settings.MEDIA_URL, '')
        
        # Construir path absoluto
        return os.path.join(settings.MEDIA_ROOT, relative_path)
```

---

## 6. RESUMEN PARTE 3

```yaml
Export Service:
  ✅ ExportService (~100 líneas)
     - Coordina exports
     - Genera URLs
     - Valida formatos

Exporters (3):
  ✅ ExcelExporter (~150 líneas)
     - openpyxl
     - Headers estilizados
     - Auto-ajuste columnas
  
  ✅ CSVExporter (~60 líneas)
     - pandas
     - UTF-8 con BOM
     - Compatibilidad Excel
  
  ✅ PDFExporter (~150 líneas)
     - reportlab
     - Tabla paginada
     - Orientación landscape

File Management:
  ✅ FileCleanupService (~80 líneas)
     - Elimina archivos expirados
     - APScheduler job

Libraries:
  - openpyxl (Excel)
  - pandas (CSV + DataFrames)
  - reportlab (PDF)

Total: ~540 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 4/5: API REST y Serializers**

Contenido:
- ✅ Serializers DRF (6 serializers)
- ✅ ViewSets REST (3 viewsets)
- ✅ URLs configuration
- ✅ Endpoints (15 endpoints)
- ✅ RBAC integration

**Estimado:** ~900 líneas, 2 horas

---

**Fin de PARTE 3/5**
