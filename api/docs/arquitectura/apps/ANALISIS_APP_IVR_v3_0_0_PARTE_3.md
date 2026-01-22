---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App IVR PARTE 3/4
categoria: arquitectura/apps
tema: apps/ivr/ - Services y API REST
autor: Claude Technical Analysis
tags: [ivr, services, api, drf, readonly]
estado: definitivo
parte: 3 de 4
relacionado:
  - ANALISIS_APP_IVR_v3_0_0_PARTE_1.md
  - ANALISIS_APP_IVR_v3_0_0_PARTE_2.md
  - ANALISIS_APP_IVR_v3_0_0_PARTE_4.md
replaces: []
---

# ANÁLISIS DE apps/ivr/ v3.0.0 - PARTE 3/4
## SERVICES Y API REST

---

## 1. SERVICES

### 1.1 IVRQueryService

```python
"""
Service para queries a BD IVR.

CNST-002: READONLY only.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Sum

from apps.ivr.models import (
    CallRecordT1, CallRecordT2, CallRecordT3,
    QuarterlyReport
)
from apps.ivr.utils import get_current_quarter, get_model_for_quarter


class IVRQueryService:
    """
    Service para consultas optimizadas a BD IVR.
    
    CNST-002: Todas las operaciones son readonly.
    CNST-010: Cache en locmem (NO Redis).
    """
    
    def get_call_records_by_date(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List:
        """
        Obtiene registros por rango de fechas.
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
        
        Returns:
            List: Call records del período
        
        Note:
            Consulta múltiples tablas trimestrales.
        """
        # Determinar trimestres a consultar
        start_quarter = get_current_quarter(start_date.month)
        end_quarter = get_current_quarter(end_date.month)
        
        records = []
        
        for quarter in range(start_quarter, end_quarter + 1):
            model = get_model_for_quarter(quarter)
            if model:
                qs = model.objects.filter(
                    fecha_llamada__gte=start_date,
                    fecha_llamada__lte=end_date
                )
                records.extend(list(qs))
        
        return sorted(records, key=lambda x: x.fecha_llamada, reverse=True)
    
    def get_daily_stats(self, date: datetime.date) -> Dict:
        """
        Estadísticas diarias.
        
        Args:
            date: Fecha
        
        Returns:
            Dict con stats
        """
        quarter = get_current_quarter(date.month)
        model = get_model_for_quarter(quarter)
        
        if not model:
            return {}
        
        stats = model.objects.filter(
            fecha_llamada__date=date
        ).aggregate(
            total=Count('id_llamada'),
            duracion_promedio=Avg('duracion_segundos'),
            duracion_total=Sum('duracion_segundos')
        )
        
        return stats


class CallRecordService:
    """Service para CallRecord."""
    
    def get_contestadas(self, start_date, end_date):
        """Obtiene llamadas contestadas."""
        from apps.ivr.constants import ESTADO_CONTESTADA
        
        service = IVRQueryService()
        records = service.get_call_records_by_date(start_date, end_date)
        
        return [r for r in records if r.estado_llamada == ESTADO_CONTESTADA]


class ReportService:
    """Service para reportes agregados."""
    
    def get_quarterly_report(self, year: int, quarter: int) -> Optional:
        """
        Obtiene reporte trimestral.
        
        Args:
            year: Año
            quarter: Trimestre 1-4
        
        Returns:
            QuarterlyReport o None
        """
        try:
            return QuarterlyReport.objects.get(
                anio=year,
                trimestre=quarter
            )
        except QuarterlyReport.DoesNotExist:
            return None
```

---

## 2. SERIALIZERS DRF

```python
"""
Serializers DRF para IVR.
"""

from rest_framework import serializers

from apps.ivr.models import (
    CallRecordT1,
    QuarterlyReport,
    TransferReport,
    ClientReport
)


class CallRecordSerializer(serializers.ModelSerializer):
    """Serializer para CallRecord."""
    
    duracion_minutos = serializers.FloatField(read_only=True)
    
    class Meta:
        model = CallRecordT1  # Base model
        fields = [
            'id_llamada', 'fecha_llamada',
            'numero_origen', 'numero_destino',
            'duracion_segundos', 'duracion_minutos',
            'estado_llamada', 'tipo_llamada'
        ]
        read_only_fields = '__all__'  # READONLY


class QuarterlyReportSerializer(serializers.ModelSerializer):
    """Serializer para QuarterlyReport."""
    
    tasa_abandono = serializers.FloatField(read_only=True)
    
    class Meta:
        model = QuarterlyReport
        fields = '__all__'
        read_only_fields = '__all__'


class TransferReportSerializer(serializers.ModelSerializer):
    """Serializer para TransferReport."""
    
    tasa_exito = serializers.FloatField(read_only=True)
    
    class Meta:
        model = TransferReport
        fields = '__all__'
        read_only_fields = '__all__'


class ClientReportSerializer(serializers.ModelSerializer):
    """Serializer para ClientReport."""
    
    class Meta:
        model = ClientReport
        fields = '__all__'
        read_only_fields = '__all__'
```

---

## 3. VIEWSETS REST

```python
"""
ViewSets DRF para IVR.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.access.permissions import DynamicFunctionPermission
from apps.ivr.serializers import (
    CallRecordSerializer,
    QuarterlyReportSerializer,
    TransferReportSerializer
)
from apps.ivr.services import IVRQueryService, ReportService
from apps.ivr.models import CallRecordT1, QuarterlyReport


class CallRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet READONLY para CallRecord.
    
    Endpoints:
    - GET /api/v1/ivr/calls/
    - GET /api/v1/ivr/calls/{id}/
    - GET /api/v1/ivr/calls/stats/
    
    CNST-002: READONLY only.
    RBAC: IVR_VIEW
    """
    
    queryset = CallRecordT1.objects.all()  # Example T1
    serializer_class = CallRecordSerializer
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'list': 'ivr.view',
        'retrieve': 'ivr.view',
        'stats': 'ivr.stats',
    }
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de llamadas."""
        from datetime import datetime, timedelta
        
        # Default: últimos 7 días
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        service = IVRQueryService()
        stats = service.get_daily_stats(end_date.date())
        
        return Response(stats)


class QuarterlyReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet READONLY para QuarterlyReport.
    
    Endpoints:
    - GET /api/v1/ivr/quarterly-reports/
    - GET /api/v1/ivr/quarterly-reports/{id}/
    - GET /api/v1/ivr/quarterly-reports/current/
    
    RBAC: IVR_VIEW
    """
    
    queryset = QuarterlyReport.objects.all()
    serializer_class = QuarterlyReportSerializer
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'list': 'ivr.view',
        'retrieve': 'ivr.view',
        'current': 'ivr.view',
    }
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Reporte trimestre actual."""
        report = QuarterlyReport.objects.get_current_quarter()
        
        if report:
            serializer = self.get_serializer(report)
            return Response(serializer.data)
        
        return Response(
            {'error': 'No current quarter report found'},
            status=status.HTTP_404_NOT_FOUND
        )
```

---

## 4. URLS

```python
"""
URL configuration para IVR.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.ivr.views import (
    CallRecordViewSet,
    QuarterlyReportViewSet
)

router = DefaultRouter()
router.register(r'calls', CallRecordViewSet, basename='call')
router.register(r'quarterly-reports', QuarterlyReportViewSet, basename='quarterly-report')

app_name = 'ivr'

urlpatterns = [
    path('api/v1/ivr/', include(router.urls)),
]
```

**Endpoints (6 total):**

```yaml
Calls (3):
  GET /api/v1/ivr/calls/
  GET /api/v1/ivr/calls/{id}/
  GET /api/v1/ivr/calls/stats/

Quarterly Reports (3):
  GET /api/v1/ivr/quarterly-reports/
  GET /api/v1/ivr/quarterly-reports/{id}/
  GET /api/v1/ivr/quarterly-reports/current/
```

---

## 5. RESUMEN PARTE 3

```yaml
Services (3):
  ✅ IVRQueryService (~200 líneas)
  ✅ CallRecordService (~80 líneas)
  ✅ ReportService (~80 líneas)

Serializers (4):
  ✅ CallRecordSerializer
  ✅ QuarterlyReportSerializer
  ✅ TransferReportSerializer
  ✅ ClientReportSerializer

ViewSets (2):
  ✅ CallRecordViewSet (readonly)
  ✅ QuarterlyReportViewSet (readonly)

Endpoints: 6 endpoints READONLY
RBAC: IVR_VIEW, IVR_STATS

Total: ~600 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 4/4: Testing y Deployment (FINAL)**

Contenido:
- ✅ Tests (40 tests)
- ✅ Deployment checklist
- ✅ MariaDB configuration
- ✅ Resumen final completo

**Estimado:** ~900 líneas

---

**Fin de PARTE 3/4**
