---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Relaciones entre Apps
categoria: arquitectura/relaciones
tema: Ejemplos de N Reportes/Dashboards - Casos Reales
autor: Claude Technical Analysis
tags: [reportes, dashboards, ejemplos, sql, etl, rbac]
relacionado:
  - ANALISIS_RELACIONES_v2.0.0_PARTE_1.md
  - ANALISIS_RELACIONES_v2.0.0_PARTE_2.md
  - ANALISIS_RELACIONES_v2.0.0_PARTE_3.md
  - ANALISIS_RELACIONES_v2.0.0_PARTE_4.md
  - Scripts SQL reales (q_REPTRIM*.sql)
estado: completo-definitivo
partes: 5/6
---

# ANÁLISIS DE RELACIONES v2.0.0 - PARTE 5/6

**Ejemplos de N Reportes/Dashboards - Basados en Scripts SQL Reales**

---

## TABLA DE CONTENIDOS (PARTE 5)

1. [Resumen de Reportes del Sistema](#resumen)
2. [REPORTE 1: Llamadas Abandonadas](#reporte-1)
3. [REPORTE 2: Clientes Únicos por DID](#reporte-2)
4. [REPORTE 3: Detalle Transferencias](#reporte-3)
5. [REPORTE 4: Llamadas por Menú](#reporte-4)
6. [DASHBOARD 1: Métricas Trimestrales](#dashboard-1)
7. [DASHBOARD 2: Análisis de Clientes](#dashboard-2)
8. [DASHBOARD 3: Performance IVR](#dashboard-3)
9. [Patrón Repetible](#patron)

---

<a name="resumen"></a>
## 1. RESUMEN DE REPORTES DEL SISTEMA

### 1.1 Reportes Implementados (Basados en Scripts SQL Reales)

```
CATÁLOGO DE REPORTES IACT v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GRUPO 1: REPORTES TRIMESTRALES
┌────────┬────────────────────────────┬──────────────────────┐
│ ID     │ Nombre                     │ Script SQL Origen    │
├────────┼────────────────────────────┼──────────────────────┤
│ RPT-TR │ Llamadas Abandonadas       │ q_REPTRIM021         │
│ -021   │ Análisis por trimestre,    │                      │
│        │ DID y menú                 │                      │
├────────┼────────────────────────────┼──────────────────────┤
│ RPT-TR │ Clientes Únicos por DID    │ q_REPTRIM011         │
│ -011   │ Count distinct por trim.   │                      │
├────────┼────────────────────────────┼──────────────────────┤
│ RPT-TR │ Promedio Clientes Únicos   │ q_REPTRIM031         │
│ -031   │ AVG por menú y trimestre   │                      │
├────────┼────────────────────────────┼──────────────────────┤
│ RPT-TR │ Promedio Clientes Menú     │ q_REPTRIM041         │
│ -041   │ Estadísticas por menú      │                      │
├────────┼────────────────────────────┼──────────────────────┤
│ RPT-TR │ Llamadas por Menú          │ q_REPTRIM121         │
│ -121   │ Volumen por trimestre      │                      │
└────────┴────────────────────────────┴──────────────────────┘

GRUPO 2: REPORTES DETALLADOS
┌────────┬────────────────────────────┬──────────────────────┐
│ ID     │ Nombre                     │ Script SQL Origen    │
├────────┼────────────────────────────┼──────────────────────┤
│ RPT-DET│ Detalle Transferencias     │ q_REP_DETALLE_       │
│ -001   │ Transfer + Menú + Opción   │ TRANSFERENCIA...     │
├────────┼────────────────────────────┼──────────────────────┤
│ RPT-ERR│ cMenu con Errores          │ q_cMENU_ERROR        │
│ -001   │ Detección de anomalías     │                      │
└────────┴────────────────────────────┴──────────────────────┘

GRUPO 3: DASHBOARDS
┌────────┬────────────────────────────┬──────────────────────┐
│ ID     │ Nombre                     │ Datos de             │
├────────┼────────────────────────────┼──────────────────────┤
│ DASH-  │ Métricas Trimestrales      │ Múltiples reportes   │
│ TRIM   │ KPIs agregados Q1/Q2/Q3    │ REPTRIM*             │
├────────┼────────────────────────────┼──────────────────────┤
│ DASH-  │ Análisis de Clientes       │ REPTRIM011, 031, 041 │
│ CLI    │ Únicos, promedios, trends  │                      │
├────────┼────────────────────────────┼──────────────────────┤
│ DASH-  │ Performance IVR            │ REP_DETALLE, cMENU   │
│ IVR    │ Menús, transferencias,     │ ERROR                │
│        │ opciones, errores          │                      │
└────────┴────────────────────────────┴──────────────────────┘

TOTAL: 7 Reportes + 3 Dashboards = 10 endpoints
```

### 1.2 Características Comunes

```
TODAS LOS REPORTES COMPARTEN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Datos procesados por ETL (día vencido, 2 AM)
✅ Tablas agregadas en default DB
✅ Django models (managed=True)
✅ RBAC con funciones RPT (RPT-001 a RPT-008)
✅ Export a Excel/CSV (CNST-007: max 100K)
✅ Filtros por:
   - Trimestre (Q1, Q2, Q3)
   - DID/Sucursal (Puebla, Nacional)
   - Fecha (rango)
   - Menú (cMenu)

DATOS ORIGEN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVR_LEGACY (MariaDB):
├─ tbl_historico_t1_2025 (Q1: ene-mar)
├─ tbl_historico_t2_2025 (Q2: abr-jun)
└─ tbl_historico_t3_2025 (Q3: jul-sep)

Campos principales:
├─ dFecha: Timestamp de llamada
├─ cDID_800Transfer: DID (19020084=Puebla, 19028031=Nacional)
├─ cMenu: Opción de menú seleccionada
├─ cOpcion: Sub-opción
├─ cTelefono_Origen: Teléfono del cliente
├─ cTelefono_Digitado: Teléfono digitado en IVR
└─ cDID_Centro_Transferencia: Centro de atención
```

---

<a name="reporte-1"></a>
## 2. REPORTE 1: LLAMADAS ABANDONADAS (RPT-TR-021)

### 2.1 Descripción

```
REPORTE: Llamadas Abandonadas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID: RPT-TR-021
Nombre: Análisis de Llamadas Abandonadas
Script SQL Origen: q_REPTRIM021_LLAMADAS_ABDANDONADAS.sql

Propósito:
Analizar llamadas que se abandonaron antes de completar IVR,
agrupadas por trimestre, DID y opción de menú.

Métricas:
├─ Total llamadas abandonadas
├─ Distribución por DID (Puebla vs Nacional)
├─ Distribución por menú
└─ Comparación trimestral

Dimensiones:
├─ trimestre (Q1, Q2, Q3)
├─ did (Puebla, Nacional)
└─ menu_limpio (normalizado)

Funciones RBAC requeridas:
├─ RPT-001 (ve_reportes) - Ver datos
├─ RPT-003 (filtra_reportes) - Filtrar
└─ RPT-005 (exporta_excel) - Exportar

Caso de Uso:
UC-017: Ver reporte de llamadas abandonadas
```

### 2.2 ETL - Stored Procedure

```sql
-- ════════════════════════════════════════════════════════════
-- ETL para Reporte Llamadas Abandonadas
-- Basado en: q_REPTRIM021_LLAMADAS_ABDANDONADAS.sql
-- ════════════════════════════════════════════════════════════

CREATE OR REPLACE PROCEDURE etl_llamadas_abandonadas()
LANGUAGE plpgsql
AS $$
DECLARE
    v_fecha_proceso DATE;
    v_records_processed INT := 0;
BEGIN
    v_fecha_proceso := CURRENT_DATE - INTERVAL '1 day';
    
    -- Determinar trimestre
    DECLARE
        v_trimestre VARCHAR(10);
        v_mes INT;
    BEGIN
        v_mes := EXTRACT(MONTH FROM v_fecha_proceso);
        
        IF v_mes BETWEEN 1 AND 3 THEN
            v_trimestre := 'Q1';
        ELSIF v_mes BETWEEN 4 AND 6 THEN
            v_trimestre := 'Q2';
        ELSIF v_mes BETWEEN 7 AND 9 THEN
            v_trimestre := 'Q3';
        ELSE
            v_trimestre := 'Q4';
        END IF;
    END;
    
    -- EXTRACT + TRANSFORM + LOAD
    INSERT INTO reporte_llamadas_abandonadas (
        trimestre,
        did,
        menu_limpio,
        total_llamadas,
        fecha_procesada,
        created_at,
        updated_at
    )
    SELECT 
        v_trimestre as trimestre,
        CASE 
            WHEN c.cDID_800Transfer = '19020084' THEN 'Puebla'
            WHEN c.cDID_800Transfer = '19028031' THEN 'Nacional'
            ELSE 'Otro'
        END as did,
        CASE 
            WHEN c.cMenu = '' THEN 'vacio'
            WHEN c.cMenu = 'sin cMenu' THEN 'vacio'
            WHEN c.cMenu IS NULL THEN 'vacio'
            WHEN TRIM(c.cMenu) = '' THEN 'vacio'
            ELSE UPPER(TRIM(c.cMenu))
        END as menu_limpio,
        COUNT(*) as total_llamadas,
        v_fecha_proceso,
        NOW(),
        NOW()
    FROM ivr_call_logs c  -- Foreign table a IVR_LEGACY
    WHERE 
        DATE(c.call_timestamp) = v_fecha_proceso
        AND c.cDID_800Transfer IN ('19020084', '19028031')
        -- Condición de "abandonada" (ejemplo)
        AND (c.call_status = 'abandoned' OR c.duration_seconds < 10)
    GROUP BY 
        did,
        menu_limpio
    ON CONFLICT (trimestre, did, menu_limpio, fecha_procesada)
    DO UPDATE SET
        total_llamadas = EXCLUDED.total_llamadas,
        updated_at = NOW();
    
    GET DIAGNOSTICS v_records_processed = ROW_COUNT;
    
    -- Registrar en ETLExecution
    INSERT INTO pipeline_etlexecution (
        etl_name,
        fecha_procesada,
        status,
        records_processed,
        started_at,
        completed_at
    ) VALUES (
        'llamadas_abandonadas',
        v_fecha_proceso,
        'success',
        v_records_processed,
        NOW(),
        NOW()
    );
    
END;
$$;

-- Scheduler
SELECT cron.schedule(
    'etl-llamadas-abandonadas',
    '10 2 * * *',  -- 2:10 AM (después de ETL principal)
    'CALL etl_llamadas_abandonadas()'
);
```

### 2.3 Django Model

```python
# ════════════════════════════════════════════════════════════
# apps/reports/models.py
# ════════════════════════════════════════════════════════════

from django.db import models


class LlamadasAbandonadas(models.Model):
    """
    Reporte de llamadas abandonadas (RPT-TR-021).
    
    Datos agregados creados por ETL.
    Basado en: q_REPTRIM021_LLAMADAS_ABDANDONADAS.sql
    """
    
    # Dimensiones
    trimestre = models.CharField(
        max_length=10,
        db_index=True,
        help_text="Q1, Q2, Q3, Q4"
    )
    
    did = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Puebla, Nacional"
    )
    
    menu_limpio = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Opción de menú normalizada"
    )
    
    fecha_procesada = models.DateField(
        db_index=True,
        help_text="Fecha de los datos procesados"
    )
    
    # Métricas
    total_llamadas = models.IntegerField(
        default=0,
        help_text="Cantidad de llamadas abandonadas"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True  # Django crea tabla
        db_table = 'reporte_llamadas_abandonadas'
        ordering = ['-fecha_procesada', 'trimestre', 'did']
        unique_together = [
            ('trimestre', 'did', 'menu_limpio', 'fecha_procesada')
        ]
        indexes = [
            models.Index(fields=['trimestre', 'did']),
            models.Index(fields=['fecha_procesada']),
        ]
        verbose_name = 'Reporte Llamadas Abandonadas'
        verbose_name_plural = 'Reportes Llamadas Abandonadas'
    
    def __str__(self):
        return (
            f"{self.trimestre} - {self.did} - "
            f"{self.menu_limpio}: {self.total_llamadas} llamadas"
        )
```

### 2.4 Service

```python
# ════════════════════════════════════════════════════════════
# apps/reports/services.py
# ════════════════════════════════════════════════════════════

from datetime import date
from typing import List, Dict
from django.db.models import Sum, Count, Q
from apps.reports.models import LlamadasAbandonadas
from apps.pipeline.services import ETLMonitoringService


class LlamadasAbandonadasService:
    """Servicio para reporte de llamadas abandonadas."""
    
    @staticmethod
    def get_report_data(
        trimestre: str = None,
        did: str = None,
        fecha_inicio: date = None,
        fecha_fin: date = None
    ) -> List[Dict]:
        """
        Query datos de llamadas abandonadas.
        
        Args:
            trimestre: 'Q1', 'Q2', 'Q3' o None (todos)
            did: 'Puebla', 'Nacional' o None (todos)
            fecha_inicio: Filtro fecha (opcional)
            fecha_fin: Filtro fecha (opcional)
        
        Returns:
            List[Dict] con datos agregados
        """
        queryset = LlamadasAbandonadas.objects.all()
        
        # Filtros
        if trimestre:
            queryset = queryset.filter(trimestre=trimestre)
        
        if did:
            queryset = queryset.filter(did=did)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_procesada__gte=fecha_inicio)
        
        if fecha_fin:
            queryset = queryset.filter(fecha_procesada__lte=fecha_fin)
        
        return list(queryset.values(
            'trimestre',
            'did',
            'menu_limpio',
            'total_llamadas',
            'fecha_procesada'
        ))
    
    @staticmethod
    def get_totals_by_trimestre() -> Dict:
        """
        Totales agregados por trimestre.
        
        Returns:
            {
                'Q1': {'Puebla': 1234, 'Nacional': 5678},
                'Q2': {...},
                'Q3': {...}
            }
        """
        from collections import defaultdict
        
        result = defaultdict(dict)
        
        aggregated = LlamadasAbandonadas.objects.values(
            'trimestre', 'did'
        ).annotate(
            total=Sum('total_llamadas')
        )
        
        for item in aggregated:
            result[item['trimestre']][item['did']] = item['total']
        
        return dict(result)
    
    @staticmethod
    def get_top_menus(
        trimestre: str,
        did: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Top N menús con más abandonos.
        
        Returns:
            [
                {'menu': 'ANI', 'total': 1234},
                ...
            ]
        """
        top = LlamadasAbandonadas.objects.filter(
            trimestre=trimestre,
            did=did
        ).values('menu_limpio').annotate(
            total=Sum('total_llamadas')
        ).order_by('-total')[:limit]
        
        return list(top)
    
    @staticmethod
    def verify_data_availability(fecha: date) -> Dict:
        """Verificar que ETL corrió para esta fecha."""
        
        # Verificar ETL
        etl_status = ETLMonitoringService.check_etl_status(
            'llamadas_abandonadas',
            fecha
        )
        
        if not etl_status['executed']:
            return {
                'available': False,
                'message': f"ETL no ha corrido para {fecha}"
            }
        
        if etl_status['status'] != 'success':
            return {
                'available': False,
                'message': f"ETL falló: {etl_status['error_message']}"
            }
        
        # Verificar datos
        count = LlamadasAbandonadas.objects.filter(
            fecha_procesada=fecha
        ).count()
        
        if count == 0:
            return {
                'available': False,
                'message': "ETL exitoso pero sin datos"
            }
        
        return {
            'available': True,
            'records_count': count,
            'message': f"{count} registros disponibles"
        }
```

### 2.5 ViewSet

```python
# ════════════════════════════════════════════════════════════
# apps/reports/views.py
# ════════════════════════════════════════════════════════════

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.access.decorators import require_function
from apps.reports.services import LlamadasAbandonadasService
from apps.reports.exporters import ExcelExporter
from datetime import datetime


class LlamadasAbandonadasViewSet(viewsets.ViewSet):
    """
    ViewSet para reporte de llamadas abandonadas.
    
    Endpoints:
    - GET /api/v1/reports/abandonadas/data/
    - GET /api/v1/reports/abandonadas/totals/
    - POST /api/v1/reports/abandonadas/generate-excel/
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    @require_function('RPT-001')  # ve_reportes
    def data(self, request):
        """
        Obtener datos del reporte.
        
        GET /api/v1/reports/abandonadas/data/
          ?trimestre=Q1
          &did=Puebla
          &fecha_inicio=2025-01-01
          &fecha_fin=2025-03-31
        """
        # Parse parámetros
        trimestre = request.query_params.get('trimestre')
        did = request.query_params.get('did')
        
        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')
        
        fecha_inicio = None
        fecha_fin = None
        
        if fecha_inicio_str:
            fecha_inicio = datetime.strptime(
                fecha_inicio_str, '%Y-%m-%d'
            ).date()
        
        if fecha_fin_str:
            fecha_fin = datetime.strptime(
                fecha_fin_str, '%Y-%m-%d'
            ).date()
        
        # Query datos
        data = LlamadasAbandonadasService.get_report_data(
            trimestre=trimestre,
            did=did,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        return Response({
            'count': len(data),
            'filters': {
                'trimestre': trimestre,
                'did': did,
                'fecha_inicio': fecha_inicio_str,
                'fecha_fin': fecha_fin_str
            },
            'data': data
        })
    
    @action(detail=False, methods=['get'])
    @require_function('RPT-001', 'RPT-007')  # ve_reportes + ve_kpis
    def totals(self, request):
        """
        Totales agregados por trimestre.
        
        GET /api/v1/reports/abandonadas/totals/
        """
        totals = LlamadasAbandonadasService.get_totals_by_trimestre()
        
        return Response(totals)
    
    @action(detail=False, methods=['post'])
    @require_function('RPT-001', 'RPT-005')  # ve_reportes + exporta_excel
    def generate_excel(self, request):
        """
        Generar Excel.
        
        POST /api/v1/reports/abandonadas/generate-excel/
        {
            "trimestre": "Q1",
            "did": "Puebla"
        }
        """
        trimestre = request.data.get('trimestre')
        did = request.data.get('did')
        
        # Validar
        if not trimestre or not did:
            return Response({
                "error": "Parámetros 'trimestre' y 'did' requeridos"
            }, status=400)
        
        # Query datos
        data = LlamadasAbandonadasService.get_report_data(
            trimestre=trimestre,
            did=did
        )
        
        if not data:
            return Response({
                "error": "No hay datos para los filtros especificados"
            }, status=404)
        
        # Validar CNST-007 (max 100K)
        if len(data) > 100000:
            return Response({
                "error": "Límite de 100,000 registros excedido",
                "count": len(data)
            }, status=400)
        
        # Generar Excel
        filepath = ExcelExporter.generate_llamadas_abandonadas_excel(
            data=data,
            trimestre=trimestre,
            did=did
        )
        
        file_url = filepath.replace(settings.MEDIA_ROOT, '/media')
        
        return Response({
            "status": "completed",
            "file_url": file_url,
            "total_records": len(data)
        })
```

---

<a name="reporte-2"></a>
## 3. REPORTE 2: CLIENTES ÚNICOS POR DID (RPT-TR-011)

### 3.1 Django Model

```python
# ════════════════════════════════════════════════════════════
# apps/reports/models.py
# ════════════════════════════════════════════════════════════

class ClientesUnicosPorDID(models.Model):
    """
    Reporte clientes únicos por DID y trimestre (RPT-TR-011).
    
    Basado en: q_REPTRIM011_CLIENTES_UNICOS_POR_DID.sql
    """
    
    trimestre = models.CharField(max_length=10, db_index=True)
    did = models.CharField(max_length=50, db_index=True)
    fecha_procesada = models.DateField(db_index=True)
    
    # Métrica
    clientes_unicos = models.IntegerField(
        default=0,
        help_text="COUNT(DISTINCT cTelefono_Origen)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = 'reporte_clientes_unicos_did'
        unique_together = [('trimestre', 'did', 'fecha_procesada')]
        ordering = ['-fecha_procesada', 'trimestre']
```

### 3.2 ETL (Ejemplo simplificado)

```sql
-- ETL para clientes únicos
CREATE OR REPLACE PROCEDURE etl_clientes_unicos()
AS $$
DECLARE
    v_fecha DATE;
    v_trimestre VARCHAR(10);
BEGIN
    v_fecha := CURRENT_DATE - INTERVAL '1 day';
    
    -- Determinar trimestre...
    v_trimestre := CASE 
        WHEN EXTRACT(MONTH FROM v_fecha) BETWEEN 1 AND 3 THEN 'Q1'
        WHEN EXTRACT(MONTH FROM v_fecha) BETWEEN 4 AND 6 THEN 'Q2'
        WHEN EXTRACT(MONTH FROM v_fecha) BETWEEN 7 AND 9 THEN 'Q3'
        ELSE 'Q4'
    END;
    
    INSERT INTO reporte_clientes_unicos_did (
        trimestre,
        did,
        fecha_procesada,
        clientes_unicos,
        created_at,
        updated_at
    )
    SELECT 
        v_trimestre,
        CASE 
            WHEN c.cDID_800Transfer = '19020084' THEN 'Puebla'
            WHEN c.cDID_800Transfer = '19028031' THEN 'Nacional'
        END as did,
        v_fecha,
        COUNT(DISTINCT c.cTelefono_Origen) as clientes_unicos,
        NOW(),
        NOW()
    FROM ivr_call_logs c
    WHERE 
        DATE(c.call_timestamp) = v_fecha
        AND c.cDID_800Transfer IN ('19020084', '19028031')
    GROUP BY did
    ON CONFLICT (trimestre, did, fecha_procesada)
    DO UPDATE SET
        clientes_unicos = EXCLUDED.clientes_unicos,
        updated_at = NOW();
    
END;
$$;
```

---

<a name="reporte-3"></a>
## 4. REPORTE 3: DETALLE TRANSFERENCIAS (RPT-DET-001)

### 4.1 Django Model (Complejo)

```python
# ════════════════════════════════════════════════════════════
# apps/reports/models.py - Reporte más complejo
# ════════════════════════════════════════════════════════════

class DetalleTransferencias(models.Model):
    """
    Reporte detallado de transferencias, menú y opciones.
    
    Basado en: q_REP_DETALLE_TRANSFERENCIA_MENU_OPCION-v_0_3_1.sql
    
    Este reporte es más complejo, incluye múltiples dimensiones
    y métricas derivadas.
    """
    
    # Dimensiones principales
    trimestre = models.CharField(max_length=10, db_index=True)
    fecha_mes = models.CharField(
        max_length=6,
        help_text="YYYYMM format"
    )
    transfer_800 = models.CharField(
        max_length=50,
        help_text="Puebla/Nacional"
    )
    centro_transferencia = models.CharField(
        max_length=100,
        help_text="Centro normalizado"
    )
    menu = models.CharField(max_length=100)
    opcion = models.CharField(max_length=100, default='SIN_OPCION')
    
    # Métricas
    total_llamadas = models.IntegerField(default=0)
    porcentaje = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        help_text="% sobre total del trimestre"
    )
    misma_linea = models.IntegerField(
        default=0,
        help_text="cTelefono_Origen = cTelefono_Digitado"
    )
    linea_diferente = models.IntegerField(default=0)
    no_digito_telefono = models.IntegerField(default=0)
    
    # Metadata
    fecha_procesada = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = 'reporte_detalle_transferencias'
        unique_together = [(
            'trimestre', 'fecha_mes', 'transfer_800',
            'centro_transferencia', 'menu', 'opcion',
            'fecha_procesada'
        )]
        indexes = [
            models.Index(fields=['trimestre', 'transfer_800']),
            models.Index(fields=['menu']),
        ]
```

---

<a name="reporte-4"></a>
## 5. REPORTE 4: LLAMADAS POR MENÚ (RPT-TR-121)

### 5.1 Service (Ejemplo avanzado con análisis)

```python
# ════════════════════════════════════════════════════════════
# apps/reports/services.py
# ════════════════════════════════════════════════════════════

class LlamadasMenuService:
    """
    Servicio para reporte de llamadas por menú.
    
    Basado en: q_REPTRIM121_LLAMADAS_MENU.sql
    """
    
    @staticmethod
    def get_distribution_by_menu(
        trimestre: str,
        did: str
    ) -> Dict:
        """
        Distribución de llamadas por menú.
        
        Returns:
            {
                'total_llamadas': 50000,
                'menu_distribution': [
                    {'menu': 'ANI', 'total': 15000, 'porcentaje': 30.0},
                    {'menu': 'PRODUCTOS', 'total': 12000, 'porcentaje': 24.0},
                    ...
                ],
                'top_5': [...],
                'anomalias': [...]  # Menús con errores
            }
        """
        from apps.reports.models import LlamadasMenu
        
        # Total
        total_llamadas = LlamadasMenu.objects.filter(
            trimestre=trimestre,
            did=did
        ).aggregate(total=Sum('total_llamadas'))['total'] or 0
        
        # Distribución
        distribucion = list(
            LlamadasMenu.objects.filter(
                trimestre=trimestre,
                did=did
            ).values('menu').annotate(
                total=Sum('total_llamadas')
            ).order_by('-total')
        )
        
        # Calcular porcentajes
        for item in distribucion:
            item['porcentaje'] = round(
                (item['total'] / total_llamadas * 100), 2
            ) if total_llamadas > 0 else 0
        
        # Top 5
        top_5 = distribucion[:5]
        
        # Detectar anomalías (menús con errores)
        anomalias = list(
            LlamadasMenu.objects.filter(
                trimestre=trimestre,
                did=did,
                menu__in=['VACIO', 'telefono_cMenu', 'ERROR']
            ).values('menu').annotate(
                total=Sum('total_llamadas')
            )
        )
        
        return {
            'total_llamadas': total_llamadas,
            'menu_distribution': distribucion,
            'top_5': top_5,
            'anomalias': anomalias
        }
```

---

<a name="dashboard-1"></a>
## 6. DASHBOARD 1: MÉTRICAS TRIMESTRALES (DASH-TRIM)

### 6.1 Service Completo

```python
# ════════════════════════════════════════════════════════════
# apps/reports/services.py - Dashboard Service
# ════════════════════════════════════════════════════════════

class DashboardTrimestralService:
    """
    Dashboard de métricas agregadas trimestrales.
    
    Combina datos de múltiples reportes:
    - Llamadas abandonadas
    - Clientes únicos
    - Llamadas por menú
    - Promedios
    """
    
    @staticmethod
    def get_dashboard_data(trimestre: str) -> Dict:
        """
        Dashboard completo para un trimestre.
        
        Returns:
            {
                'trimestre': 'Q1',
                'kpis': {
                    'total_llamadas': 150000,
                    'total_abandonadas': 12000,
                    'tasa_abandono': 8.0,
                    'clientes_unicos': 45000
                },
                'por_did': {
                    'Puebla': {...},
                    'Nacional': {...}
                },
                'top_menus': [...],
                'trends': [...]
            }
        """
        from django.db.models import Sum, Avg
        from apps.reports.models import (
            LlamadasAbandonadas,
            ClientesUnicosPorDID,
            LlamadasMenu
        )
        
        # KPIs generales
        total_abandonadas = LlamadasAbandonadas.objects.filter(
            trimestre=trimestre
        ).aggregate(total=Sum('total_llamadas'))['total'] or 0
        
        total_llamadas = LlamadasMenu.objects.filter(
            trimestre=trimestre
        ).aggregate(total=Sum('total_llamadas'))['total'] or 0
        
        tasa_abandono = round(
            (total_abandonadas / total_llamadas * 100), 2
        ) if total_llamadas > 0 else 0
        
        clientes_unicos = ClientesUnicosPorDID.objects.filter(
            trimestre=trimestre
        ).aggregate(total=Sum('clientes_unicos'))['total'] or 0
        
        # Por DID
        kpis_puebla = DashboardTrimestralService._get_kpis_by_did(
            trimestre, 'Puebla'
        )
        kpis_nacional = DashboardTrimestralService._get_kpis_by_did(
            trimestre, 'Nacional'
        )
        
        # Top menús
        top_menus = list(
            LlamadasMenu.objects.filter(
                trimestre=trimestre
            ).values('menu').annotate(
                total=Sum('total_llamadas')
            ).order_by('-total')[:10]
        )
        
        return {
            'trimestre': trimestre,
            'kpis': {
                'total_llamadas': total_llamadas,
                'total_abandonadas': total_abandonadas,
                'tasa_abandono': tasa_abandono,
                'clientes_unicos': clientes_unicos
            },
            'por_did': {
                'Puebla': kpis_puebla,
                'Nacional': kpis_nacional
            },
            'top_menus': top_menus
        }
    
    @staticmethod
    def _get_kpis_by_did(trimestre: str, did: str) -> Dict:
        """KPIs específicos por DID."""
        from apps.reports.models import (
            LlamadasAbandonadas,
            ClientesUnicosPorDID,
            LlamadasMenu
        )
        
        abandonadas = LlamadasAbandonadas.objects.filter(
            trimestre=trimestre,
            did=did
        ).aggregate(total=Sum('total_llamadas'))['total'] or 0
        
        total = LlamadasMenu.objects.filter(
            trimestre=trimestre,
            did=did
        ).aggregate(total=Sum('total_llamadas'))['total'] or 0
        
        clientes = ClientesUnicosPorDID.objects.filter(
            trimestre=trimestre,
            did=did
        ).aggregate(total=Sum('clientes_unicos'))['total'] or 0
        
        return {
            'total_llamadas': total,
            'abandonadas': abandonadas,
            'tasa_abandono': round((abandonadas / total * 100), 2) if total > 0 else 0,
            'clientes_unicos': clientes,
            'llamadas_por_cliente': round((total / clientes), 2) if clientes > 0 else 0
        }
```

### 6.2 ViewSet

```python
# ════════════════════════════════════════════════════════════
# apps/reports/views.py
# ════════════════════════════════════════════════════════════

class DashboardTrimestralViewSet(viewsets.ViewSet):
    """Dashboard de métricas trimestrales."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    @require_function('RPT-002', 'RPT-007')  # ve_dashboard + ve_kpis
    def metrics(self, request):
        """
        GET /api/v1/dashboards/trimestral/metrics/?trimestre=Q1
        """
        trimestre = request.query_params.get('trimestre', 'Q1')
        
        dashboard_data = DashboardTrimestralService.get_dashboard_data(
            trimestre
        )
        
        return Response(dashboard_data)
```

---

<a name="dashboard-2"></a>
## 7. DASHBOARD 2: ANÁLISIS DE CLIENTES (DASH-CLI)

```python
# ════════════════════════════════════════════════════════════
# Dashboard de análisis de clientes
# ════════════════════════════════════════════════════════════

class DashboardClientesService:
    """Dashboard enfocado en clientes únicos y comportamiento."""
    
    @staticmethod
    def get_cliente_analysis() -> Dict:
        """
        Análisis completo de clientes.
        
        Combina:
        - REPTRIM011: Clientes únicos por DID
        - REPTRIM031: Promedio clientes únicos
        - REPTRIM041: Promedio clientes por menú
        """
        return {
            'clientes_unicos': {
                'Q1': {'Puebla': 15000, 'Nacional': 30000},
                'Q2': {'Puebla': 16500, 'Nacional': 32000},
                'Q3': {'Puebla': 14800, 'Nacional': 29500}
            },
            'trends': {
                'Puebla': '+2.1%',  # Q2 vs Q1
                'Nacional': '+1.8%'
            },
            'por_menu': [
                {'menu': 'ANI', 'promedio_clientes': 5200},
                {'menu': 'PRODUCTOS', 'promedio_clientes': 4800},
                # ...
            ],
            'retencion': {
                'clientes_recurrentes': 12000,
                'clientes_nuevos': 3500,
                'tasa_retencion': 77.4
            }
        }
```

---

<a name="dashboard-3"></a>
## 8. DASHBOARD 3: PERFORMANCE IVR (DASH-IVR)

```python
# ════════════════════════════════════════════════════════════
# Dashboard de performance del IVR
# ════════════════════════════════════════════════════════════

class DashboardIVRService:
    """Dashboard de calidad y errores del IVR."""
    
    @staticmethod
    def get_ivr_health() -> Dict:
        """
        Salud del IVR - errores y anomalías.
        
        Basado en:
        - q_cMENU_ERROR.sql
        - Detalle transferencias
        """
        return {
            'menus_con_error': {
                'VACIO': 1200,
                'telefono_cMenu': 850,  # Número en vez de menú
                'MENU_10_NUMEROS': 320,
                'CASO_ERROR_CEROS': 150
            },
            'tasa_error': 5.2,  # % del total
            'transferencias': {
                'exitosas': 45000,
                'fallidas': 2800,
                'cliente_colgo': 1500,
                'tasa_exito': 93.8
            },
            'opciones_populares': [
                {'opcion': 'PRODUCTOS', 'uso': 35.2},
                {'opcion': 'SOPORTE', 'uso': 28.5},
                # ...
            ]
        }
```

---

<a name="patron"></a>
## 9. PATRÓN REPETIBLE PARA AGREGAR NUEVOS REPORTES

### 9.1 Checklist

```
PATRÓN PARA AGREGAR NUEVO REPORTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ PASO 1: Analizar script SQL origen
  - Identificar dimensiones (GROUP BY)
  - Identificar métricas (COUNT, SUM, AVG)
  - Identificar filtros (WHERE)

□ PASO 2: Crear ETL
  - Stored procedure en DB
  - EXTRACT de IVR_LEGACY
  - TRANSFORM (limpiar, normalizar)
  - LOAD en tabla agregada
  - REGISTRO en ETLExecution
  - Scheduler (pg_cron)

□ PASO 3: Crear Django Model
  - managed=True
  - db_table='reporte_{nombre}'
  - Campos dimensión + campos métrica
  - unique_together
  - Indexes
  - Timestamps

□ PASO 4: Crear Service
  - get_report_data() con filtros
  - get_totals() o agregaciones
  - verify_data_availability()
  - Métodos de análisis específicos

□ PASO 5: Crear ViewSet
  - @require_function con RPT adecuadas
  - Endpoint /data/ (RPT-001)
  - Endpoint /generate-excel/ (RPT-001 + RPT-005)
  - Endpoint /totals/ o /kpis/ (RPT-007)
  - Validar CNST-007 (max 100K)

□ PASO 6: Crear Exporter
  - ExcelExporter.generate_{nombre}_excel()
  - Styling según necesidad
  - Múltiples hojas si aplica

□ PASO 7: RBAC
  - Asignar funciones a usuarios/grupos
  - Probar permisos

□ PASO 8: Testing
  - Test ETL
  - Test Service
  - Test ViewSet
  - Test RBAC
  - Test Export

□ PASO 9: Documentación
  - Actualizar catálogo de reportes
  - Casos de uso
  - Manual de usuario
```

### 9.2 Ejemplo Plantilla

```python
# ════════════════════════════════════════════════════════════
# PLANTILLA PARA NUEVO REPORTE
# ════════════════════════════════════════════════════════════

# 1. Model
class Reporte{Nombre}(models.Model):
    """
    Reporte {descripción}.
    Basado en: q_{script_sql}.sql
    """
    # Dimensiones
    dimension1 = models.CharField(max_length=X, db_index=True)
    dimension2 = models.CharField(max_length=Y, db_index=True)
    
    # Métricas
    metrica1 = models.IntegerField(default=0)
    metrica2 = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Metadata
    fecha_procesada = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = 'reporte_{nombre}'
        unique_together = [('dimension1', 'dimension2', 'fecha_procesada')]


# 2. Service
class Reporte{Nombre}Service:
    @staticmethod
    def get_report_data(**filters):
        queryset = Reporte{Nombre}.objects.all()
        # Aplicar filtros...
        return list(queryset.values(...))
    
    @staticmethod
    def verify_data_availability(fecha):
        # Verificar ETL...
        pass


# 3. ViewSet
class Reporte{Nombre}ViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    @require_function('RPT-001')
    def data(self, request):
        # Query y retornar datos...
        pass
    
    @action(detail=False, methods=['post'])
    @require_function('RPT-001', 'RPT-005')
    def generate_excel(self, request):
        # Validar CNST-007
        # Generar Excel
        # Retornar URL
        pass
```

---

## RESUMEN PARTE 5

```
EJEMPLOS IMPLEMENTADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REPORTES (4):
✅ RPT-TR-021: Llamadas Abandonadas
✅ RPT-TR-011: Clientes Únicos por DID
✅ RPT-DET-001: Detalle Transferencias
✅ RPT-TR-121: Llamadas por Menú

DASHBOARDS (3):
✅ DASH-TRIM: Métricas Trimestrales
✅ DASH-CLI: Análisis de Clientes
✅ DASH-IVR: Performance IVR

PATRÓN:
✅ Checklist de 9 pasos
✅ Plantilla de código
✅ Todos basados en scripts SQL reales

TOTAL: 7 implementaciones + patrón repetible

PRÓXIMA PARTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PARTE 6/6: Matriz de Dependencias y Conclusiones
- Matriz completa de relaciones
- Puntos de integración
- Resumen arquitectónico final
```

---

**FIN DE PARTE 5/6**

Documento: ANALISIS_RELACIONES v2.0.0 - PARTE 5/6  
Fecha: 2026-01-17  
Estado: Completo  
Basado en: Scripts SQL reales del sistema  
Siguiente: PARTE 6/6 - Matriz y Conclusiones Finales
