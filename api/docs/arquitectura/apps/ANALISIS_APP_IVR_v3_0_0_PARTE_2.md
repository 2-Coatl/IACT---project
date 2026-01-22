---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App IVR PARTE 2/4
categoria: arquitectura/apps
tema: apps/ivr/ - Modelos de Reportes y ETL Integration
autor: Claude Technical Analysis
tags: [ivr, etl, reports, mariadb, readonly]
estado: definitivo
parte: 2 de 4
relacionado:
  - ANALISIS_APP_IVR_v3_0_0_PARTE_1.md
  - ANALISIS_APP_IVR_v3_0_0_PARTE_3.md
  - ANALISIS_APP_IVR_v3_0_0_PARTE_4.md
replaces: []
---

# ANÁLISIS DE apps/ivr/ v3.0.0 - PARTE 2/4
## MODELOS DE REPORTES Y ETL INTEGRATION

---

## 1. MODELOS DE REPORTES ETL

### 1.1 QuarterlyReport

```python
"""
Modelos de reportes generados por ETL.

CNST-002: TODOS managed=False (readonly).
"""

from django.db import models


class QuarterlyReport(models.Model):
    """
    Reporte trimestral agregado.
    
    CNST-002: managed=False, readonly.
    Generado por: ETL (sp_etl_daily)
    Frecuencia: Diaria (acumulativo)
    Database: MariaDB (ivr_legacy)
    Tabla: tbl_reporte_trimestral
    """
    
    id_reporte = models.AutoField(
        primary_key=True,
        db_column='iIdReporte'
    )
    
    trimestre = models.IntegerField(
        'Trimestre',
        db_column='iTrimestre',
        help_text='1-4 (Q1-Q4)'
    )
    
    anio = models.IntegerField(
        'Año',
        db_column='iAnio'
    )
    
    total_llamadas = models.IntegerField(
        'Total Llamadas',
        default=0,
        db_column='iTotalLlamadas'
    )
    
    llamadas_contestadas = models.IntegerField(
        'Contestadas',
        default=0,
        db_column='iLlamadasContestadas'
    )
    
    llamadas_abandonadas = models.IntegerField(
        'Abandonadas',
        default=0,
        db_column='iLlamadasAbandonadas'
    )
    
    duracion_promedio = models.FloatField(
        'Duración Promedio (seg)',
        default=0.0,
        db_column='fDuracionPromedio'
    )
    
    tiempo_espera_promedio = models.FloatField(
        'Tiempo Espera Promedio (seg)',
        default=0.0,
        db_column='fTiempoEsperaPromedio'
    )
    
    generado_en = models.DateTimeField(
        'Generado',
        db_column='dtGeneradoEn',
        help_text='Timestamp última ejecución ETL'
    )
    
    class Meta:
        managed = False
        db_table = 'tbl_reporte_trimestral'
        verbose_name = 'Reporte Trimestral'
        verbose_name_plural = 'Reportes Trimestrales'
        ordering = ['-anio', '-trimestre']
    
    def __str__(self):
        return f"Q{self.trimestre} {self.anio}"
    
    @property
    def tasa_abandono(self):
        """Tasa de abandono (%)."""
        if self.total_llamadas > 0:
            return round(
                (self.llamadas_abandonadas / self.total_llamadas) * 100,
                2
            )
        return 0.0


class TransferReport(models.Model):
    """
    Reporte de transferencias.
    
    Database: MariaDB (ivr_legacy)
    Tabla: tbl_reporte_transferencias
    """
    
    id_reporte = models.AutoField(
        primary_key=True,
        db_column='iIdReporte'
    )
    
    fecha = models.DateField(
        'Fecha',
        db_column='dtFecha'
    )
    
    total_transferencias = models.IntegerField(
        'Total Transferencias',
        default=0,
        db_column='iTotalTransferencias'
    )
    
    transferencias_exitosas = models.IntegerField(
        'Exitosas',
        default=0,
        db_column='iTransferenciasExitosas'
    )
    
    transferencias_fallidas = models.IntegerField(
        'Fallidas',
        default=0,
        db_column='iTransferenciasFallidas'
    )
    
    duracion_promedio_transferencia = models.FloatField(
        'Duración Promedio Transfer (seg)',
        default=0.0,
        db_column='fDuracionPromedioTransferencia'
    )
    
    class Meta:
        managed = False
        db_table = 'tbl_reporte_transferencias'
        verbose_name = 'Reporte de Transferencias'
        ordering = ['-fecha']
    
    @property
    def tasa_exito(self):
        """Tasa de éxito (%)."""
        if self.total_transferencias > 0:
            return round(
                (self.transferencias_exitosas / self.total_transferencias) * 100,
                2
            )
        return 0.0


class ClientReport(models.Model):
    """
    Reporte de clientes.
    
    Database: MariaDB (ivr_legacy)
    Tabla: tbl_reporte_clientes
    """
    
    id_reporte = models.AutoField(
        primary_key=True,
        db_column='iIdReporte'
    )
    
    id_cliente = models.IntegerField(
        'ID Cliente',
        db_column='iIdCliente'
    )
    
    nombre_cliente = models.CharField(
        'Nombre',
        max_length=255,
        db_column='cNombreCliente'
    )
    
    total_llamadas = models.IntegerField(
        'Total Llamadas',
        default=0,
        db_column='iTotalLlamadas'
    )
    
    llamadas_ultimo_mes = models.IntegerField(
        'Llamadas Último Mes',
        default=0,
        db_column='iLlamadasUltimoMes'
    )
    
    duracion_total_minutos = models.FloatField(
        'Duración Total (min)',
        default=0.0,
        db_column='fDuracionTotalMinutos'
    )
    
    ultima_llamada = models.DateTimeField(
        'Última Llamada',
        null=True,
        db_column='dtUltimaLlamada'
    )
    
    class Meta:
        managed = False
        db_table = 'tbl_reporte_clientes'
        verbose_name = 'Reporte de Clientes'
        ordering = ['-total_llamadas']


class AbandonedReport(models.Model):
    """
    Reporte de llamadas abandonadas.
    
    Database: MariaDB (ivr_legacy)
    Tabla: tbl_reporte_abandonadas
    """
    
    id_reporte = models.AutoField(
        primary_key=True,
        db_column='iIdReporte'
    )
    
    fecha = models.DateField(
        'Fecha',
        db_column='dtFecha'
    )
    
    hora = models.IntegerField(
        'Hora',
        db_column='iHora',
        help_text='0-23 (24h format)'
    )
    
    total_abandonadas = models.IntegerField(
        'Total Abandonadas',
        default=0,
        db_column='iTotalAbandonadas'
    )
    
    tiempo_espera_promedio = models.FloatField(
        'Tiempo Espera Promedio (seg)',
        default=0.0,
        db_column='fTiempoEsperaPromedio'
    )
    
    abandonadas_antes_30s = models.IntegerField(
        'Abandonadas < 30s',
        default=0,
        db_column='iAbandonadasAntes30s'
    )
    
    class Meta:
        managed = False
        db_table = 'tbl_reporte_abandonadas'
        verbose_name = 'Reporte de Abandonadas'
        ordering = ['-fecha', '-hora']


class TransferDetailReport(models.Model):
    """
    Reporte detalle de transferencias.
    
    Database: MariaDB (ivr_legacy)
    Tabla: tbl_reporte_detalle_transferencias
    """
    
    id_reporte = models.AutoField(
        primary_key=True,
        db_column='iIdReporte'
    )
    
    fecha = models.DateField(
        'Fecha',
        db_column='dtFecha'
    )
    
    extension_origen = models.CharField(
        'Extensión Origen',
        max_length=20,
        db_column='cExtensionOrigen'
    )
    
    extension_destino = models.CharField(
        'Extensión Destino',
        max_length=20,
        db_column='cExtensionDestino'
    )
    
    total_transferencias = models.IntegerField(
        'Total',
        default=0,
        db_column='iTotalTransferencias'
    )
    
    duracion_promedio = models.FloatField(
        'Duración Promedio (seg)',
        default=0.0,
        db_column='fDuracionPromedio'
    )
    
    class Meta:
        managed = False
        db_table = 'tbl_reporte_detalle_transferencias'
        verbose_name = 'Detalle de Transferencias'
        ordering = ['-fecha', '-total_transferencias']


class MenuPerformanceReport(models.Model):
    """
    Reporte de performance de menús IVR.
    
    Database: MariaDB (ivr_legacy)
    Tabla: tbl_reporte_menus_performance
    """
    
    id_reporte = models.AutoField(
        primary_key=True,
        db_column='iIdReporte'
    )
    
    id_menu = models.IntegerField(
        'ID Menú',
        db_column='iIdMenu'
    )
    
    nombre_menu = models.CharField(
        'Nombre Menú',
        max_length=255,
        db_column='cNombreMenu'
    )
    
    total_accesos = models.IntegerField(
        'Total Accesos',
        default=0,
        db_column='iTotalAccesos'
    )
    
    tiempo_promedio_navegacion = models.FloatField(
        'Tiempo Promedio Nav (seg)',
        default=0.0,
        db_column='fTiempoPromedioNavegacion'
    )
    
    salidas_menu = models.IntegerField(
        'Salidas',
        default=0,
        db_column='iSalidasMenu'
    )
    
    class Meta:
        managed = False
        db_table = 'tbl_reporte_menus_performance'
        verbose_name = 'Performance de Menús'
        ordering = ['-total_accesos']


class MenuErrorReport(models.Model):
    """
    Reporte de errores de menús IVR.
    
    Database: MariaDB (ivr_legacy)
    Tabla: tbl_reporte_menu_errores
    """
    
    id_reporte = models.AutoField(
        primary_key=True,
        db_column='iIdReporte'
    )
    
    fecha = models.DateField(
        'Fecha',
        db_column='dtFecha'
    )
    
    id_menu = models.IntegerField(
        'ID Menú',
        db_column='iIdMenu'
    )
    
    nombre_menu = models.CharField(
        'Nombre Menú',
        max_length=255,
        db_column='cNombreMenu'
    )
    
    total_errores = models.IntegerField(
        'Total Errores',
        default=0,
        db_column='iTotalErrores'
    )
    
    tipo_error = models.CharField(
        'Tipo Error',
        max_length=100,
        db_column='cTipoError'
    )
    
    class Meta:
        managed = False
        db_table = 'tbl_reporte_menu_errores'
        verbose_name = 'Errores de Menús'
        ordering = ['-fecha', '-total_errores']
```

---

## 2. MANAGERS CUSTOMIZADOS

```python
"""
Managers para modelos IVR.
"""

from django.db import models
from datetime import datetime


class QuarterlyReportManager(models.Manager):
    """Manager para QuarterlyReport."""
    
    def get_current_quarter(self):
        """
        Obtiene reporte del trimestre actual.
        
        Returns:
            QuarterlyReport o None
        """
        now = datetime.now()
        quarter = (now.month - 1) // 3 + 1
        year = now.year
        
        try:
            return self.get(trimestre=quarter, anio=year)
        except self.model.DoesNotExist:
            return None
    
    def get_quarter(self, year, quarter):
        """
        Obtiene reporte de trimestre específico.
        
        Args:
            year: Año (int)
            quarter: Trimestre 1-4 (int)
        
        Returns:
            QuarterlyReport o None
        """
        try:
            return self.get(trimestre=quarter, anio=year)
        except self.model.DoesNotExist:
            return None


class CallRecordManager(models.Manager):
    """Manager para CallRecord."""
    
    def filter_by_date_range(self, start_date, end_date):
        """
        Filtra por rango de fechas.
        
        Args:
            start_date: Fecha inicio (datetime)
            end_date: Fecha fin (datetime)
        
        Returns:
            QuerySet
        """
        return self.filter(
            fecha_llamada__gte=start_date,
            fecha_llamada__lte=end_date
        )
    
    def contestadas(self):
        """Filtra llamadas contestadas."""
        from apps.ivr.constants import ESTADO_CONTESTADA
        return self.filter(estado_llamada=ESTADO_CONTESTADA)
    
    def abandonadas(self):
        """Filtra llamadas abandonadas."""
        from apps.ivr.constants import ESTADO_ABANDONADA
        return self.filter(estado_llamada=ESTADO_ABANDONADA)
```

---

## 3. UTILS

```python
"""
Utility functions para IVR.
"""

from datetime import datetime


def get_current_quarter():
    """
    Obtiene trimestre actual.
    
    Returns:
        int: 1-4 (Q1-Q4)
    """
    month = datetime.now().month
    return (month - 1) // 3 + 1


def get_quarter_from_month(month):
    """
    Obtiene trimestre desde mes.
    
    Args:
        month: Mes 1-12
    
    Returns:
        int: 1-4
    """
    return (month - 1) // 3 + 1


def get_table_name_for_quarter(year, quarter):
    """
    Obtiene nombre de tabla para trimestre.
    
    Args:
        year: Año (int)
        quarter: Trimestre 1-4 (int)
    
    Returns:
        str: Nombre de tabla
    
    Example:
        >>> get_table_name_for_quarter(2025, 1)
        'tbl_historico_t1_2025'
    """
    return f'tbl_historico_t{quarter}_{year}'


def get_model_for_quarter(quarter):
    """
    Obtiene modelo Django para trimestre.
    
    Args:
        quarter: Trimestre 1-4 (int)
    
    Returns:
        Model class: CallRecordT1, T2, o T3
    """
    from apps.ivr.models import CallRecordT1, CallRecordT2, CallRecordT3
    
    models_map = {
        1: CallRecordT1,
        2: CallRecordT2,
        3: CallRecordT3,
    }
    
    return models_map.get(quarter)


def validate_readonly_operation():
    """
    Valida que operación sea readonly.
    
    Raises:
        RuntimeError: Si se intenta escribir
    
    CNST-002: BD IVR es readonly.
    """
    raise RuntimeError(
        "CNST-002 VIOLATION: Cannot write to IVR database. "
        "IVR database is READONLY."
    )
```

---

## 4. RESUMEN PARTE 2

```yaml
Modelos de Reportes (7):
  ✅ QuarterlyReport (trimestral agregado)
  ✅ TransferReport (transferencias diarias)
  ✅ ClientReport (resumen clientes)
  ✅ AbandonedReport (abandonadas por hora)
  ✅ TransferDetailReport (detalle transfers)
  ✅ MenuPerformanceReport (performance menús)
  ✅ MenuErrorReport (errores menús)

Todos:
  - managed=False ✅
  - readonly ✅
  - Database: ivr_legacy (MariaDB) ✅

Managers (2):
  ✅ QuarterlyReportManager
  ✅ CallRecordManager

Utils (5 funciones):
  ✅ get_current_quarter()
  ✅ get_quarter_from_month()
  ✅ get_table_name_for_quarter()
  ✅ get_model_for_quarter()
  ✅ validate_readonly_operation()

Total: ~650 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 3/4: Services y API REST**

Contenido:
- ✅ IVRQueryService (queries optimizadas)
- ✅ CallRecordService (histórico)
- ✅ ReportService (reportes agregados)
- ✅ Serializers DRF (8 serializers)
- ✅ ViewSets REST (4 viewsets)
- ✅ URLs configuration

**Estimado:** ~1,400 líneas, 3 horas

---

**Fin de PARTE 2/4**
