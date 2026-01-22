---
version: 3.0.1
date: 2026-01-18
project: IACT (Sistema Call Center)
base: Clean Code (Robert Martin) + Clean Architecture
changelog: |
  v3.0.1 - PARTE 2/5 - Arquitectura corregida
  - CORRECCIÓN: SoftDeleteMixin y TimeStampedModel en apps/core/ (no utils/)
  - CORRECCIÓN: apps/core/ NO deprecado (solo abstractos)
  - Mantiene Principio de Equilibrio (válido)
  - Mantiene DRF ViewSets y Serializers (válido)
partes: 2/5
estado: completo
revision: v3.0.1 (arquitectura correcta)
replaces: CLEAN_CODE_NAMING_PRINCIPLES_v2_3_1_PARTE_2.md
---

# CLEAN CODE NAMING PRINCIPLES v3.0.1

**PARTE 2/5: PRINCIPIO DE EQUILIBRIO + DRF BÁSICO**

---

## 📋 CONTENIDO DE ESTA PARTE

15. [Principio de Equilibrio](#15-principio-de-equilibrio)
    - 15.1 Definición y Fundamento
    - 15.2 Evitar Verbosidad Excesiva
    - 15.3 Longitud Apropiada según Scope
    - 15.4 Nombres Pronunciables (No Trabalenguas)
    - 15.5 Balance Claridad vs Brevedad
    - 15.6 Regla de Oro por Tipo de Elemento
    - 15.7 Aplicación IACT (Arquitectura Real)
    - 15.8 Ejemplos Completos
    - 15.9 Anti-patterns de Equilibrio
    - 15.10 Checklist de Verificación
16. [Nomenclatura por Ubicación (IACT)](#16-nomenclatura-por-ubicacion)
17. [DRF: ViewSets y Views](#17-drf-viewsets-y-views)
18. [DRF: Serializers](#18-drf-serializers)

---

## ⚠️ CAMBIOS EN v3.0.1

```
ARQUITECTURA CORREGIDA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ v2.3.1 (INCORRECTO):
├─ apps/utils/models.py tiene SoftDeleteMixin (CLASE)
├─ apps/core/ marcado como "DEPRECADO"
└─ Confusión arquitectónica

✅ v3.0.1 (CORRECTO):
├─ apps/core/models.py tiene SoftDeleteMixin (SOLO abstractos)
├─ apps/core/ NO deprecado (fundamental del sistema)
└─ apps/utils/ SOLO funciones

MODELOS CORREGIDOS (desde v2.3.1):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CallRecord (antes HistoricoT1)
✅ QuarterlyReport (antes ReporteTrimestral)
✅ IVRMenu (antes Menu2)
✅ AbandonedCall (antes LlamadasAbandonadas)
```

---

<a name="15-principio-de-equilibrio"></a>
## 15. PRINCIPIO DE EQUILIBRIO

**Principio Fundamental**: Balancear claridad con brevedad según el scope del elemento.

Un nombre debe ser lo suficientemente descriptivo para ser claro, pero no tan largo que se convierta en una "disertación". El equilibrio perfecto depende del contexto (scope) donde se use.

---

### 15.1 Definición y Fundamento

```
REGLA DE ORO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"A mayor scope, mayor descriptividad permitida.
 A menor scope, mayor brevedad requerida."

Scope pequeño (loop):        i, user, record
Scope mediano (función):     start_date, user_id
Scope grande (clase):        ReportService, DashboardService
```

**Fundamento:**
- Variables de loop viven 3-5 líneas → nombre corto OK
- Parámetros de función viven toda la función → más descriptivos
- Clases existen en toda la aplicación → muy descriptivas

---

### 15.2 Evitar Verbosidad Excesiva

**Anti-pattern: "Nombres de Disertación"**

```python
# ❌ INCORRECTO - Nombres excesivamente verbosos ("disertaciones")

class QuarterlyReportDataAggregationAndExportService:
    """❌ Nombre excesivamente largo."""
    pass

def get_quarterly_report_data_with_filters_and_pagination_support(
    quarter,
    did,
    page_number,
    page_size
):
    """❌ Nombre de "disertación"."""
    pass

quarterly_report_generation_timestamp_in_utc = datetime.now()
# ❌ 6 palabras, ilegible


# ✅ CORRECTO - Balance adecuado

class ReportService:
    """✅ Claro y conciso."""
    pass

def get_quarterly_report(quarter: str, did: str, page: int = 1):
    """✅ Descriptivo pero legible."""
    pass

report_timestamp = datetime.now()  # ✅ 2 palabras, claro
```

**En IACT:**
```python
# ❌ INCORRECTO
class QuarterlyCallRecordDataRetrievalAndAggregationService:
    """❌ 7 palabras, excesivo."""
    pass

def get_quarterly_call_records_with_did_filtering_and_menu_grouping(
    quarter, did, menu
):
    """❌ Trabalenguas."""
    pass


# ✅ CORRECTO
class ReportService:
    """✅ Balance perfecto."""
    
    @staticmethod
    def get_quarterly_calls(quarter: str, did: str, menu: str = None):
        """
        Obtiene llamadas trimestrales.
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3, Q4)
            did: DID a consultar
            menu: Menú a filtrar (opcional)
        """  # ← Español
        
        from apps.ivr.models import CallRecord
        
        queryset = CallRecord.objects.filter(
            quarter=quarter,
            did=did
        )
        
        if menu:
            queryset = queryset.filter(menu=menu)
        
        return queryset
```

---

### 15.3 Longitud Apropiada según Scope

```
SCOPE                           LONGITUD        EJEMPLOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Loop variables                  1 palabra       i, user, record
Local variables (función)       1-2 palabras    count, total_calls
Parameters                      2-3 palabras    start_date, user_id
Instance variables              2-4 palabras    max_export_records
Functions/Methods               2-5 palabras    get_report_data
Classes                         1-4 palabras    ReportService
Modules/Packages                1-2 palabras    reports, dashboard
```

**Ejemplos por Scope:**

```python
# LOOP VARIABLES: 1 palabra
for i in range(10):  # ✅ OK en loops cortos
    print(i)

for user in users:  # ✅ Mejor aún
    print(user.name)

for call_record in call_records:  # ✅ 2 palabras OK si loop complejo
    process_call(call_record)


# LOCAL VARIABLES: 1-2 palabras
def calculate_metrics():
    count = 0  # ✅ 1 palabra
    total = 0  # ✅ 1 palabra
    average_duration = 0  # ✅ 2 palabras


# PARAMETERS: 2-3 palabras
def get_report(start_date, end_date, user_id):  # ✅ 2 palabras c/u
    pass


# INSTANCE VARIABLES: 2-4 palabras
class ReportConfig:
    max_records = 100000  # ✅ 2 palabras
    default_page_size = 25  # ✅ 3 palabras
    max_export_records = 100000  # ✅ 3 palabras


# FUNCTIONS: 2-5 palabras
def get_report():  # ✅ 2 palabras
    pass

def calculate_abandonment_rate():  # ✅ 3 palabras
    pass

def export_quarterly_report_to_excel():  # ✅ 5 palabras (límite)
    pass


# CLASSES: 1-4 palabras
class Report:  # ✅ 1 palabra
    pass

class ReportService:  # ✅ 2 palabras
    pass

class QuarterlyReport:  # ✅ 2 palabras
    pass

class DashboardService:  # ✅ 2 palabras
    pass
```

---

### 15.4 Nombres Pronunciables (No Trabalenguas)

**Principio**: Si cuesta trabajo pronunciarlo, cuesta trabajo usarlo.

```python
# ❌ INCORRECTO - Trabalenguas

def get_quarterly_aggregated_call_records_with_menu_filtering():
    """❌ Casi imposible de pronunciar naturalmente."""
    pass

class QuarterlyReportDataAggregationService:
    """❌ Trabalenguas."""
    pass


# ✅ CORRECTO - Fácil de pronunciar

def get_quarterly_calls(menu: str = None):
    """✅ "Get quarterly calls" - fluido."""
    pass

class ReportService:
    """✅ "Report Service" - natural."""
    pass
```

**Test de pronunciación:**
```
Imagina decir el nombre en una conversación:

❌ "Necesito el get-quarterly-aggregated-call-records-with-menu-filtering"
   → Trabalenguas, nadie dirá eso

✅ "Necesito get quarterly calls"
   → Natural, conversacional
```

---

### 15.5 Balance Claridad vs Brevedad

**Escala de Balance:**

```
DEMASIADO BREVE          BALANCE PERFECTO          DEMASIADO VERBOSO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ get_data()            ✅ get_report_data()      ❌ get_quarterly_report_data_with_all_filters()
❌ calc()                ✅ calculate_rate()       ❌ calculate_abandonment_rate_percentage()
❌ svc                   ✅ ReportService          ❌ QuarterlyReportGenerationService
```

**En IACT:**
```python
# ❌ DEMASIADO BREVE (pierde contexto)
def get():  # ❌ ¿Obtener qué?
    pass

def calc():  # ❌ ¿Calcular qué?
    pass

class Svc:  # ❌ ¿Service de qué?
    pass


# ✅ BALANCE PERFECTO (contexto + brevedad)
def get_quarterly_report():  # ✅ Claro qué obtiene
    pass

def calculate_abandonment_rate():  # ✅ Claro qué calcula
    pass

class ReportService:  # ✅ Claro qué servicio
    pass


# ❌ DEMASIADO VERBOSO (innecesario)
def get_quarterly_report_data_from_database_with_filters():
    """❌ "from_database" y "with_filters" obvios."""
    pass

def calculate_call_abandonment_rate_as_percentage():
    """❌ "as_percentage" obvio por contexto."""
    pass

class QuarterlyReportDataRetrievalService:
    """❌ "Data" y "Retrieval" redundantes."""
    pass
```

---

### 15.6 Regla de Oro por Tipo de Elemento

```python
# ══════════════════════════════════════════════════════════
# VARIABLES
# ══════════════════════════════════════════════════════════

# Loop: 1 palabra
for call in calls:  # ✅
    pass

# Local: 1-2 palabras
count = 0  # ✅
total_calls = 0  # ✅

# Parameter: 2-3 palabras
def get_report(start_date, end_date):  # ✅
    pass

# Instance: 2-4 palabras
class Config:
    max_export_records = 100000  # ✅ 3 palabras


# ══════════════════════════════════════════════════════════
# FUNCIONES
# ══════════════════════════════════════════════════════════

# Simple: 2 palabras
def get_report():  # ✅
    pass

# Estándar: 3 palabras
def calculate_abandonment_rate():  # ✅
    pass

# Compleja: 4-5 palabras (máximo)
def export_quarterly_report_to_excel():  # ✅ 5 palabras (límite)
    pass


# ══════════════════════════════════════════════════════════
# CLASES
# ══════════════════════════════════════════════════════════

# Modelo simple: 1-2 palabras
class Report(models.Model):  # ✅ 1 palabra
    pass

class CallRecord(models.Model):  # ✅ 2 palabras
    pass

# Modelo específico: 2-3 palabras
class QuarterlyReport(models.Model):  # ✅ 2 palabras
    pass

class AbandonedCall(models.Model):  # ✅ 2 palabras
    pass

# Service: 2 palabras (nombre + Service)
class ReportService:  # ✅
    pass

class DashboardService:  # ✅
    pass


# ══════════════════════════════════════════════════════════
# MÓDULOS/PAQUETES
# ══════════════════════════════════════════════════════════

# 1 palabra preferida
reports/     # ✅
dashboard/   # ✅
access/      # ✅
ivr/         # ✅

# 2 palabras OK si necesario
# (pero evitar)
```

---

### 15.7 Aplicación IACT (Arquitectura Real)

**Ejemplo Completo con Balance Perfecto:**

```python
# ══════════════════════════════════════════════════════════
# apps/ivr/models.py - MODELOS
# ══════════════════════════════════════════════════════════

from django.db import models


# ✅ CallRecord (2 palabras - balance perfecto)
class CallRecord(models.Model):
    """
    Registro de llamada del IVR.
    
    Mapea a: historico_t1 (tabla legacy)
    """  # ← Español
    
    # ✅ Campos: 1-2 palabras
    call_id = models.CharField(max_length=50, primary_key=True)
    did = models.CharField(max_length=20)
    menu = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    
    class Meta:
        db_table = 'historico_t1'
        managed = False


# ✅ QuarterlyReport (2 palabras - balance perfecto)
class QuarterlyReport(models.Model):
    """
    Reporte trimestral agregado.
    
    Mapea a: tbl_reporte_trimestral
    """  # ← Español
    
    # ✅ Campos: 2-3 palabras
    report_id = models.AutoField(primary_key=True)
    quarter = models.CharField(max_length=10)
    did = models.CharField(max_length=50)
    total_calls = models.IntegerField()
    abandoned_calls = models.IntegerField()
    
    class Meta:
        db_table = 'tbl_reporte_trimestral'
        managed = False


# ✅ IVRMenu (2 palabras - balance perfecto)
class IVRMenu(models.Model):
    """
    Menú del sistema IVR.
    
    Mapea a: menu2
    """  # ← Español
    
    menu_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    class Meta:
        db_table = 'menu2'
        managed = False


# ══════════════════════════════════════════════════════════
# apps/reports/services.py - SERVICE LAYER
# ══════════════════════════════════════════════════════════

from apps.ivr.models import CallRecord, QuarterlyReport


# ✅ ReportService (2 palabras - balance perfecto)
class ReportService:
    """
    Servicio de lógica de negocio para reportes.
    
    Responsabilidades:
    - Obtener datos de reportes
    - Calcular métricas
    - Validar parámetros
    """  # ← Español
    
    # ✅ Funciones: 3-4 palabras (balance perfecto)
    @staticmethod
    def get_quarterly_calls(quarter: str, did: str):
        """
        Obtiene llamadas trimestrales.
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3, Q4)
            did: DID a consultar
        """  # ← Español
        
        return CallRecord.objects.filter(
            quarter=quarter,
            did=did
        )
    
    @staticmethod
    def calculate_abandonment_rate(total: int, abandoned: int) -> float:
        """
        Calcula tasa de abandono.
        
        Args:
            total: Total de llamadas
            abandoned: Llamadas abandonadas
            
        Returns:
            Tasa como porcentaje (0-100)
        """  # ← Español
        
        if total == 0:
            return 0.0
        
        return (abandoned / total) * 100
    
    @staticmethod
    def get_quarterly_metrics(quarter: str, did: str):
        """
        Obtiene métricas trimestrales.
        
        Calcula:
        - Total de llamadas
        - Llamadas abandonadas
        - Tasa de abandono
        """  # ← Español
        
        # ✅ Variables locales: 1-2 palabras
        calls = ReportService.get_quarterly_calls(quarter, did)
        total = calls.count()
        abandoned = calls.filter(status='ABANDONED').count()
        rate = ReportService.calculate_abandonment_rate(total, abandoned)
        
        return {
            'total_calls': total,
            'abandoned_calls': abandoned,
            'abandonment_rate': rate
        }


# ══════════════════════════════════════════════════════════
# apps/dashboard/services.py - DASHBOARD SERVICE
# ══════════════════════════════════════════════════════════

# ✅ DashboardService (2 palabras)
class DashboardService:
    """
    Servicio de lógica de negocio para dashboards.
    
    Responsabilidades:
    - Agregar datos de múltiples fuentes
    - Calcular KPIs
    - Generar datos para widgets
    """  # ← Español
    
    @staticmethod
    def get_quarterly_dashboard(quarter: str):
        """
        Obtiene datos de dashboard trimestral.
        
        Incluye:
        - KPIs principales
        - Datos por DID
        - Top menús
        """  # ← Español
        
        # ✅ Variables: 2-3 palabras
        puebla_metrics = ReportService.get_quarterly_metrics(
            quarter=quarter,
            did='Puebla'
        )
        
        nacional_metrics = ReportService.get_quarterly_metrics(
            quarter=quarter,
            did='Nacional'
        )
        
        return {
            'quarter': quarter,
            'puebla': puebla_metrics,
            'nacional': nacional_metrics
        }
```

---

### 15.8 Ejemplos Completos

#### Ejemplo 1: ViewSet con Balance Perfecto

```python
# apps/reports/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.reports.services import ReportService


# ✅ ReportViewSet (2 palabras - perfecto)
class ReportViewSet(viewsets.ModelViewSet):
    """
    API de reportes.
    
    Endpoints:
    - GET /reports/ - Lista reportes
    - POST /reports/ - Crea reporte
    - GET /reports/{id}/ - Detalle
    - POST /reports/{id}/export/ - Exporta
    """  # ← Español
    
    queryset = Report.objects.filter(is_deleted=False)
    serializer_class = ReportSerializer
    
    # ✅ Funciones: 2-3 palabras
    @action(detail=False, methods=['get'])
    def quarterly_calls(self, request):
        """
        Obtiene llamadas trimestrales.
        
        GET /reports/quarterly-calls/?quarter=Q1&did=Puebla
        """  # ← Español
        
        # ✅ Variables locales: 2 palabras
        quarter = request.query_params.get('quarter')
        did = request.query_params.get('did')
        
        # ✅ Variable: 1 palabra (resultado)
        calls = ReportService.get_quarterly_calls(quarter, did)
        
        # ✅ Variable: 1 palabra (serializer)
        serializer = self.get_serializer(calls, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def export_excel(self, request):
        """
        Exporta reportes a Excel.
        
        POST /reports/export-excel/
        Body: { "quarter": "Q1", "did": "Puebla" }
        """  # ← Español
        
        quarter = request.data.get('quarter')
        did = request.data.get('did')
        
        # ✅ Variable: 2 palabras
        file_url = ReportService.export_to_excel(quarter, did)
        
        return Response({'file_url': file_url})
```

---

#### Ejemplo 2: Serializer con Balance

```python
# apps/reports/serializers.py

from rest_framework import serializers
from apps.ivr.models import CallRecord


# ✅ CallRecordSerializer (3 palabras - OK para serializer)
class CallRecordSerializer(serializers.ModelSerializer):
    """
    Serializer de registro de llamada.
    
    Incluye campos calculados:
    - duration_minutes: Duración en minutos
    - is_abandoned: Si fue abandonada
    """  # ← Español
    
    # ✅ Campos: 2-3 palabras
    duration_minutes = serializers.SerializerMethodField()
    is_abandoned = serializers.SerializerMethodField()
    
    class Meta:
        model = CallRecord
        fields = [
            'call_id',
            'did',
            'menu',
            'timestamp',
            'duration_minutes',
            'is_abandoned'
        ]
    
    # ✅ Métodos: 3 palabras
    def get_duration_minutes(self, obj):
        """Calcula duración en minutos."""  # ← Español
        return obj.duration / 60
    
    def get_is_abandoned(self, obj):
        """Verifica si llamada fue abandonada."""  # ← Español
        return obj.status == 'ABANDONED'
```

---

### 15.9 Anti-patterns de Equilibrio

```python
# ══════════════════════════════════════════════════════════
# ANTI-PATTERN 1: Nombres Demasiado Cortos
# ══════════════════════════════════════════════════════════

# ❌ INCORRECTO
def get():  # ❌ ¿Obtener qué?
    pass

def calc():  # ❌ ¿Calcular qué?
    pass

class Svc:  # ❌ ¿Service de qué?
    pass

# ✅ CORRECTO
def get_report():  # ✅
    pass

def calculate_rate():  # ✅
    pass

class ReportService:  # ✅
    pass


# ══════════════════════════════════════════════════════════
# ANTI-PATTERN 2: Nombres Demasiado Largos
# ══════════════════════════════════════════════════════════

# ❌ INCORRECTO
def get_quarterly_call_records_with_did_filtering_and_pagination():
    """❌ 8 palabras - excesivo."""
    pass

class QuarterlyReportDataAggregationAndExportService:
    """❌ 6 palabras - trabalenguas."""
    pass

# ✅ CORRECTO
def get_quarterly_calls(did: str, page: int = 1):
    """✅ 3 palabras - balance perfecto."""
    pass

class ReportService:
    """✅ 2 palabras - claro."""
    pass


# ══════════════════════════════════════════════════════════
# ANTI-PATTERN 3: Redundancia
# ══════════════════════════════════════════════════════════

# ❌ INCORRECTO
def get_report_data():  # ❌ "data" redundante
    """Todo lo que retorna get_report es data."""
    pass

class ReportDataService:  # ❌ "Data" redundante
    """Un service de reportes obviamente maneja data."""
    pass

# ✅ CORRECTO
def get_report():  # ✅
    """Implícito que retorna data."""
    pass

class ReportService:  # ✅
    """Obvio que maneja data."""
    pass


# ══════════════════════════════════════════════════════════
# ANTI-PATTERN 4: Información Obvia
# ══════════════════════════════════════════════════════════

# ❌ INCORRECTO
def calculate_rate_as_percentage():
    """❌ "as_percentage" obvio por contexto (rate = %)."""
    return (abandoned / total) * 100

def get_data_from_database():
    """❌ "from_database" obvio (¿de dónde más?)."""
    pass

# ✅ CORRECTO
def calculate_rate():
    """✅ Obvio que es porcentaje."""
    return (abandoned / total) * 100

def get_data():
    """✅ Obvio que viene de DB."""
    pass
```

---

### 15.10 Checklist de Verificación

```
ANTES DE NOMBRAR - VERIFICAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BREVEDAD:
□ ¿Puedo eliminar palabras sin perder claridad?
□ ¿Hay palabras redundantes? (data, info, object)
□ ¿Hay información obvia que puedo omitir?

CLARIDAD:
□ ¿El nombre revela qué hace sin comentarios?
□ ¿Es pronunciable y conversacional?
□ ¿Otro dev lo entenderá sin contexto?

BALANCE:
□ Loop variables: 1 palabra ✓
□ Local variables: 1-2 palabras ✓
□ Parameters: 2-3 palabras ✓
□ Functions: 2-5 palabras ✓
□ Classes: 1-4 palabras ✓

TEST DE PRONUNCIACIÓN:
□ ¿Puedo decirlo naturalmente en conversación?
□ ¿NO es un trabalenguas?
□ ¿NO suena a "disertación"?

SCOPE:
□ ¿El nombre es apropiado para su scope?
□ Variable local corta ✓
□ Clase global más descriptiva ✓
```

---

<a name="16-nomenclatura-por-ubicacion"></a>
## 16. NOMENCLATURA POR UBICACIÓN (IACT)

**Principio**: El nombre de un componente debe reflejar su ubicación en la arquitectura.

---

### 16.1 Regla por App

```
UBICACIÓN              PREFIJO         EJEMPLOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/access/           Access          AccessService
                                       AccessAuditMiddleware

apps/reports/          Report          ReportService
                                       ReportViewSet
                                       ReportExporter

apps/dashboard/        Dashboard       DashboardService
                                       DashboardViewSet
                                       WidgetService

apps/ivr/              (Sin prefijo)   CallRecord
                                       QuarterlyReport
                                       IVRMenu

apps/pipeline/         Pipeline        PipelineMonitoringService
                       ETL             ETLStatusChecker

apps/core/             (Sin prefijo)   TimeStampedModel
                                       SoftDeleteMixin
                                       
apps/utils/            (Sin prefijo)   get_client_ip()
                                       format_phone()
```

**CORRECCIÓN v3.0.1:**
```
apps/core/ (modelos abstractos):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ TimeStampedModel (abstract=True)
✅ SoftDeleteMixin (abstract=True)
✅ SoftDeleteManager
✅ SoftDeleteQuerySet

apps/utils/ (funciones helper):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ get_client_ip()
✅ format_phone()
✅ is_valid_nit()

❌ NO models.py (clases van en core/)
```

---

### 16.2 Ejemplos Correctos e Incorrectos

```python
# ══════════════════════════════════════════════════════════
# apps/access/services.py
# ══════════════════════════════════════════════════════════

# ✅ CORRECTO
class AccessService:
    """
    Servicio de gestión de accesos RBAC.
    
    Prefijo "Access" indica que está en apps/access/
    """  # ← Español
    pass

# ❌ INCORRECTO
class PermissionService:  # ❌ Sugiere apps/permissions/
    """Confuso - parece estar en otra app."""
    pass


# ══════════════════════════════════════════════════════════
# apps/reports/services.py
# ══════════════════════════════════════════════════════════

# ✅ CORRECTO
class ReportService:
    """
    Servicio de reportes.
    
    Prefijo "Report" indica apps/reports/
    """  # ← Español
    pass

class ExportService:
    """
    Servicio de exportación.
    
    Sin prefijo porque es específico de reports/
    (ExportService solo existe aquí)
    """  # ← Español
    pass

# ❌ INCORRECTO
class DataService:  # ❌ ¿Data de qué app?
    pass


# ══════════════════════════════════════════════════════════
# apps/dashboard/services.py
# ══════════════════════════════════════════════════════════

# ✅ CORRECTO
class DashboardService:
    """
    Servicio de dashboards.
    
    Prefijo "Dashboard" indica apps/dashboard/
    """  # ← Español
    pass

class WidgetService:
    """
    Servicio de widgets.
    
    Sin prefijo porque solo existe en dashboard/
    """  # ← Español
    pass


# ══════════════════════════════════════════════════════════
# apps/ivr/models.py
# ══════════════════════════════════════════════════════════

# ✅ CORRECTO
class CallRecord(models.Model):
    """
    Registro de llamada del IVR.
    
    NO lleva prefijo "IVR" porque:
    - Ya está en apps/ivr/
    - El contexto es obvio
    """  # ← Español
    pass

class QuarterlyReport(models.Model):
    """Reporte trimestral del IVR."""  # ← Español
    pass

class IVRMenu(models.Model):
    """
    Menú del sistema IVR.
    
    SÍ lleva "IVR" porque "Menu" es genérico.
    Evita confusión con otros tipos de menús.
    """  # ← Español
    pass
```

---

### 16.3 Regla de Oro

**Pregunta:** _"¿Si muevo este archivo a otra app, el nombre sigue teniendo sentido?"_

- **SI** → Nombre genérico (va en `utils/` o `core/`)
- **NO** → Nombre con prefijo de app

```python
# SoftDeleteMixin:
# - ¿Sirve para reports/? SÍ
# - ¿Sirve para dashboard/? SÍ
# - ¿Sirve para todas las apps? SÍ
# → Genérico ✅ (va en core/, sin prefijo)

# AccessService:
# - ¿Sirve para reports/? NO
# - ¿Es específico de access/? SÍ
# → Prefijo "Access" ✅


# CallRecord:
# - ¿Solo existe en ivr/? SÍ
# - ¿Contexto obvio por ubicación? SÍ
# → Sin prefijo ✅


# IVRMenu:
# - ¿"Menu" es demasiado genérico? SÍ
# - ¿Podría confundirse con otros menús? SÍ
# → Con prefijo "IVR" ✅
```

---

<a name="17-drf-viewsets-y-views"></a>
## 17. DRF: VIEWSETS Y VIEWS

### 17.1 ViewSets vs APIView

**Usar ViewSets cuando:**
- CRUD completo de un modelo
- Endpoints RESTful estándar
- Múltiples acciones sobre un recurso

**Usar APIView cuando:**
- Endpoint único sin modelo
- Lógica no-CRUD (login, logout)
- Personalización extrema

---

### 17.2 Nomenclatura de ViewSets con Soft Delete

```python
# apps/reports/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.reports.models import Report
from apps.reports.serializers import ReportSerializer


# ✅ CORRECTO - ViewSet completo con soft delete
class ReportViewSet(viewsets.ModelViewSet):
    """
    API CRUD de reportes con soft delete.
    
    Endpoints generados automáticamente:
    - GET    /reports/           - Lista reportes activos
    - POST   /reports/           - Crea reporte
    - GET    /reports/{id}/      - Obtiene reporte
    - PUT    /reports/{id}/      - Actualiza reporte
    - PATCH  /reports/{id}/      - Actualiza parcial
    - DELETE /reports/{id}/      - Soft delete (baja lógica)
    
    Endpoints custom:
    - POST /reports/{id}/restore/  - Restaura eliminado
    - GET  /reports/deleted/       - Lista eliminados
    
    CNST-005: DELETE es lógico, NO físico.
    """  # ← Español
    
    queryset = Report.objects.filter(is_deleted=False)
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Retorna solo reportes activos.
        
        Filtra is_deleted=False por defecto.
        """  # ← Español
        return Report.objects.filter(is_deleted=False)
    
    def destroy(self, request, pk=None):
        """
        Soft delete del reporte.
        
        DELETE /reports/{id}/
        
        NO elimina físicamente. Solo marca:
        - is_deleted = True
        - deleted_at = now()
        - deleted_by = request.user
        
        CNST-005: Prohibido DELETE físico.
        """  # ← Español
        
        report = self.get_object()
        report.soft_delete(deleted_by=request.user)
        
        return Response(
            {"message": "Reporte eliminado exitosamente"},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Restaura reporte eliminado.
        
        POST /reports/{id}/restore/
        
        Revierte soft delete:
        - is_deleted = False
        - deleted_at = None
        - deleted_by = None
        """  # ← Español
        
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response(
                {"error": "Reporte no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not report.is_deleted:
            return Response(
                {"error": "El reporte no está eliminado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report.restore()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """
        Lista reportes eliminados.
        
        GET /reports/deleted/
        
        Requiere permiso: reports.view_deleted
        """  # ← Español
        
        deleted_reports = Report.objects.filter(is_deleted=True)
        
        page = self.paginate_queryset(deleted_reports)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(deleted_reports, many=True)
        return Response(serializer.data)
```

---

### 17.3 Nomenclatura de APIView

```python
# apps/authentication/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# ✅ CORRECTO - APIView para login
class LoginView(APIView):
    """
    Vista para iniciar sesión.
    
    POST /auth/login/
    {
        "username": "juan",
        "password": "***"
    }
    
    Returns:
        200 OK con token JWT
        401 Unauthorized si credenciales inválidas
    """  # ← Español
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Procesa inicio de sesión."""  # ← Español
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {"error": "Usuario y contraseña requeridos"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id,
            "username": user.username
        })


# ✅ CORRECTO - APIView para logout
class LogoutView(APIView):
    """
    Vista para cerrar sesión.
    
    POST /auth/logout/
    
    Invalida token.
    """  # ← Español
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Cierra sesión del usuario."""  # ← Español
        
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response(
                {"message": "Sesión cerrada exitosamente"},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Error al cerrar sesión"},
                status=status.HTTP_400_BAD_REQUEST
            )
```

---

<a name="18-drf-serializers"></a>
## 18. DRF: SERIALIZERS

### 18.1 Nomenclatura

```python
# ✅ CORRECTO - Nombres descriptivos

# Serializer completo
class CallRecordSerializer(serializers.ModelSerializer):
    """
    Serializer completo de CallRecord.
    
    Incluye todos los campos del modelo.
    Uso: GET/POST/PUT/PATCH
    """  # ← Español
    
    class Meta:
        model = CallRecord
        fields = '__all__'


# Serializer de listado (reducido)
class CallRecordListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado.
    
    Solo campos esenciales para mejor performance.
    Uso: GET /call-records/ (lista)
    """  # ← Español
    
    class Meta:
        model = CallRecord
        fields = ['call_id', 'did', 'menu', 'timestamp']


# Serializer de detalle (expandido)
class CallRecordDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado con relaciones.
    
    Incluye campos calculados y relaciones expandidas.
    Uso: GET /call-records/{id}/ (detalle)
    """  # ← Español
    
    duration_minutes = serializers.SerializerMethodField()
    menu_name = serializers.CharField(source='menu.name', read_only=True)
    
    class Meta:
        model = CallRecord
        fields = '__all__'
    
    def get_duration_minutes(self, obj):
        """Calcula duración en minutos."""  # ← Español
        return obj.duration / 60


# ❌ INCORRECTO - Nombres confusos
class CallRecordSerializerFull(serializers.ModelSerializer):
    # ❌ Sufijo al final confuso
    pass

class CallRecords(serializers.ModelSerializer):
    # ❌ Plural + falta "Serializer"
    pass
```

---

### 18.2 SerializerMethodField Naming

```python
class QuarterlyReportSerializer(serializers.ModelSerializer):
    """Serializer de reporte trimestral."""  # ← Español
    
    # ✅ CORRECTO - Nombres descriptivos
    total_calls = serializers.SerializerMethodField()
    abandonment_rate = serializers.SerializerMethodField()
    average_duration = serializers.SerializerMethodField()
    
    def get_total_calls(self, obj):
        """Cuenta total de llamadas del trimestre."""  # ← Español
        return CallRecord.objects.filter(
            quarter=obj.quarter,
            did=obj.did
        ).count()
    
    def get_abandonment_rate(self, obj):
        """Calcula tasa de abandono."""  # ← Español
        total = obj.total_calls
        abandoned = obj.abandoned_calls
        
        if total == 0:
            return 0.0
        
        return (abandoned / total) * 100
    
    def get_average_duration(self, obj):
        """Calcula duración promedio."""  # ← Español
        from django.db.models import Avg
        
        result = CallRecord.objects.filter(
            quarter=obj.quarter,
            did=obj.did
        ).aggregate(Avg('duration'))
        
        return result['duration__avg'] or 0
```

---

**FIN DE PARTE 2/5**

**Continúa en:** CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_3.md

---

## ✅ RESUMEN PARTE 2

**Secciones completadas:**
- ✅ 15. Principio de Equilibrio (10 subsecciones)
  - Balance claridad vs brevedad
  - Longitud según scope
  - Anti-patterns de equilibrio
- ✅ 16. Nomenclatura por Ubicación (IACT)
  - Prefijos por app
  - apps/core/ con modelos abstractos (CORREGIDO)
  - apps/utils/ solo funciones (CORREGIDO)
- ✅ 17. DRF: ViewSets y Views
  - Soft delete integrado
  - destroy(), restore(), deleted()
- ✅ 18. DRF: Serializers
  - Naming conventions
  - SerializerMethodField

**Correcciones arquitectónicas v3.0.1:**
- ✅ SoftDeleteMixin en apps/core/ (antes en utils/)
- ✅ TimeStampedModel en apps/core/ (antes en utils/)
- ✅ apps/core/ NO deprecado (solo abstractos)
- ✅ apps/utils/ solo funciones helper

**Modelos corregidos aplicados:**
- ✅ CallRecord (antes HistoricoT1)
- ✅ QuarterlyReport (antes ReporteTrimestral)
- ✅ IVRMenu (antes Menu2)

**Próxima parte:** DRF Avanzado (Permissions, Decorators, Middleware, Mixins)
