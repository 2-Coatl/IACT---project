---
version: 2.3.0
date: 2026-01-18
project: IACT (Sistema Call Center)
base: Clean Code (Robert Martin) + Clean Architecture
changelog: PARTE 2/5 - ⭐ NUEVA Sección 15 (Principio de Equilibrio) + DRF básico
partes: 2/5
estado: completo
---

# CLEAN CODE NAMING PRINCIPLES v2.3.0

**PARTE 2/5: ⭐ PRINCIPIO DE EQUILIBRIO + DRF BÁSICO**

---

## 📋 CONTENIDO DE ESTA PARTE

15. ⭐ **[NUEVO] PRINCIPIO DE EQUILIBRIO** ⭐
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

## ⭐ NOVEDAD v2.3.0

```
CAMBIO PRINCIPAL DE ESTA VERSIÓN:

Sección 15: PRINCIPIO DE EQUILIBRIO

Resuelve el problema de:
❌ Nombres demasiado largos ("trabalenguas", "dissertaciones")
❌ Verbosidad excesiva que dificulta lectura
❌ Falta de guía sobre "cuánto es demasiado"

Proporciona:
✅ Reglas explícitas de longitud según scope
✅ Ejemplos de nombres equilibrados
✅ Guía para evitar verbosidad
✅ Balance entre claridad y brevedad
```

---

## RECORDATORIO: REGLA DE IDIOMA (de PARTE 1)

```
✅ CÓDIGO: Siempre en INGLÉS
✅ COMENTARIOS/DOCSTRINGS: Siempre en ESPAÑOL
✅ NOMBRES DE DOMINIO: Depende del contexto

Function ID RBAC: reports.view (inglés)
Display name: ve_reportes (español)
Error messages: español
```

---

<a name="15-principio-de-equilibrio"></a>
## 15. ⭐ PRINCIPIO DE EQUILIBRIO ⭐

### **15.1 Definición y Fundamento**

**Principio**: _"Los nombres deben balancear claridad con brevedad. Un nombre muy corto es críptico; un nombre muy largo es un trabalenguas. La longitud debe ser apropiada al scope."_

**Origen del problema en IACT:**

Durante el desarrollo de IACT v3.0.0, se identificó que algunos nombres eran excesivamente verbosos:

```python
# ❌ PROBLEMA REAL ENCONTRADO
execution_date_for_etl_processing = models.DateField(
    verbose_name="Fecha de ejecución del proceso ETL",
    help_text="Día para el cual se ejecutó el proceso de ETL (día vencido)"
)

total_number_of_records_processed_successfully = models.IntegerField(
    verbose_name="Total de registros procesados exitosamente",
    help_text="Cantidad total de registros que fueron procesados sin errores"
)
```

**Comentario del equipo:**
> "Estos son nombres de dissertación, trabalenguas que nadie puede pronunciar en una reunión."

**Fundamento Clean Code:**

Robert Martin sobre longitud de nombres:
> "La longitud de un nombre debe corresponderse al tamaño de su ámbito (scope). Las variables en ámbitos pequeños pueden tener nombres muy cortos, pero las variables en ámbitos grandes deben tener nombres más largos."

**PERO** (el equilibrio):
> "Un nombre largo no siempre es mejor. La verbosidad excesiva dificulta la lectura tanto como la brevedad extrema."

---

### **15.2 Evitar Verbosidad Excesiva**

**Problema**: Nombres que intentan describir TODO en el nombre mismo.

**Regla**: El nombre debe identificar el concepto. Los detalles van en:
- Docstring (función/clase)
- `help_text` (campo de modelo)
- Comentario (si es necesario)

#### **Ejemplo 1: Campos de Modelo**

```python
# ❌ INCORRECTO - Verbosidad excesiva
class JobExecutionLog(models.Model):
    execution_date_and_time_of_etl_process = models.DateTimeField(
        verbose_name="Fecha y hora de ejecución del proceso ETL",
        help_text="Timestamp que indica el momento exacto en que se ejecutó el proceso de extracción, transformación y carga de datos"
    )
    
    total_number_of_records_processed_successfully = models.IntegerField(
        verbose_name="Número total de registros procesados con éxito",
        help_text="Cantidad total de registros que fueron procesados correctamente sin ningún error durante la ejecución"
    )
    
    total_number_of_records_that_failed_processing = models.IntegerField(
        verbose_name="Número total de registros que fallaron en el procesamiento",
        help_text="Cantidad de registros que no pudieron ser procesados debido a errores"
    )

# ✅ CORRECTO - Equilibrado
class JobExecutionLog(models.Model):
    """Log de ejecuciones del ETL."""  # ← Contexto en docstring
    
    start_time = models.DateTimeField(
        verbose_name="Inicio",
        help_text="Timestamp de inicio del ETL"
    )
    
    processed = models.IntegerField(
        default=0,
        verbose_name="Procesados",
        help_text="Registros procesados exitosamente"
    )
    
    failed = models.IntegerField(
        default=0,
        verbose_name="Fallidos",
        help_text="Registros que fallaron"
    )

# COMPARACIÓN:
# Verboso: execution_date_and_time_of_etl_process (48 caracteres)
# Equilibrado: start_time (10 caracteres)
# Ahorro: 38 caracteres, MUCHO más legible
```

#### **Ejemplo 2: Funciones/Métodos**

```python
# ❌ INCORRECTO - Nombre de dissertación
def get_all_reports_filtered_by_date_range_and_trimester_with_aggregation_of_metrics(
    start_date,
    end_date,
    trimestre
):
    """Obtiene reportes."""
    pass

# ✅ CORRECTO - Equilibrado
def get_report_data(start_date: date, end_date: date, trimestre: str) -> List[Dict]:
    """
    Obtiene datos de reportes con filtros aplicados.
    
    Filtra por rango de fechas y trimestre, y agrega métricas.
    
    Args:
        start_date: Fecha inicio
        end_date: Fecha fin
        trimestre: Trimestre (Q1, Q2, Q3)
    
    Returns:
        Lista de diccionarios con datos agregados
    """
    # Detalles en docstring, no en nombre
    pass

# COMPARACIÓN:
# Verboso: get_all_reports_filtered_by_date_range_and_trimester_with_aggregation_of_metrics
#          (90 caracteres, 14 palabras)
# Equilibrado: get_report_data (15 caracteres, 3 palabras)
```

#### **Ejemplo 3: Variables**

```python
# ❌ INCORRECTO - Verbosidad innecesaria
total_number_of_unique_clients_that_called_during_trimester = 450
average_number_of_calls_per_unique_client_per_day = 2.5
percentage_of_calls_that_were_abandoned_by_client = 8.2

# ✅ CORRECTO - Equilibrado (contexto claro en scope)
unique_clients = 450  # En scope de reporte trimestral
avg_calls_per_day = 2.5  # Contexto: por cliente
abandonment_rate = 8.2  # Porcentaje claro del contexto
```

**Regla**: Si necesitas 10+ palabras para explicar algo, el problema no es el nombre, es que necesitas documentación.

---

### **15.3 Longitud Apropiada según Scope**

**Regla de Martin**: "La longitud de un nombre debe corresponderse al tamaño de su ámbito."

#### **15.3.1 Regla de Oro IACT**

```python
┌─────────────────────────┬──────────────┬─────────────────────────┐
│ Tipo de Elemento        │ Palabras     │ Caracteres Aprox        │
├─────────────────────────┼──────────────┼─────────────────────────┤
│ Loop variables          │ 1            │ 1-5 (i, j, user)        │
│ Local variables         │ 1-2          │ 5-20                    │
│ Function parameters     │ 2-3          │ 10-30                   │
│ Instance variables      │ 2-4          │ 15-40                   │
│ Function names          │ 2-5          │ 15-50                   │
│ Class names             │ 2-4          │ 15-40                   │
│ Module-level constants  │ 2-5          │ 15-50                   │
│ Global/App names        │ 1-2          │ 5-20                    │
└─────────────────────────┴──────────────┴─────────────────────────┘

IMPORTANTE: Estos son MÁXIMOS recomendados, no mínimos.
```

#### **15.3.2 Ejemplos por Scope**

**Scope 1: Variables de Loop (muy pequeño)**

```python
# ✅ CORRECTO - Scope pequeño, nombre corto
for i in range(10):
    total += i

for user in users:
    print(user.name)

for record in records:
    process(record)

# ❌ INCORRECTO - Scope pequeño, nombre innecesariamente largo
for individual_user_object_from_database in users:  # ❌ 42 caracteres
    print(individual_user_object_from_database.name)
```

**Scope 2: Variables Locales (pequeño - 5-10 líneas)**

```python
# ✅ CORRECTO - Scope local, nombres concisos
def calculate_metrics(records):
    total = 0
    count = len(records)
    avg = total / count if count > 0 else 0
    return {'total': total, 'average': avg}

# ❌ INCORRECTO - Verbosidad innecesaria en scope pequeño
def calculate_metrics(records):
    total_number_of_calls = 0  # ❌ 5 líneas abajo, obvio que es "total"
    total_count_of_records = len(records)  # ❌ "count" es suficiente
    calculated_average_value = total_number_of_calls / total_count_of_records
    return {'total': total_number_of_calls, 'average': calculated_average_value}
```

**Scope 3: Variables de Instancia (mediano - toda la clase)**

```python
# ✅ CORRECTO - Scope de clase, nombres descriptivos pero no excesivos
class ReportService:
    def __init__(self):
        self.max_records = 100000  # CNST-007
        self.timeout_seconds = 300
        self.retry_attempts = 3
        self.cache_ttl = 3600

# ❌ INCORRECTO - Verbosidad excesiva
class ReportService:
    def __init__(self):
        self.maximum_number_of_records_allowed_for_export = 100000
        self.timeout_in_seconds_for_database_queries = 300
        self.maximum_number_of_retry_attempts_on_failure = 3
        self.cache_time_to_live_in_seconds_before_expiration = 3600
```

**Scope 4: Constantes Module-Level (grande - todo el módulo)**

```python
# ✅ CORRECTO - Scope grande, nombres descriptivos
# apps/reports/constants.py

MAX_EXPORT_RECORDS = 100000  # CNST-007
MAX_DATE_RANGE_DAYS = 730  # CNST-006
ETL_TIMEOUT_SECONDS = 300  # CNST-004
DEFAULT_PAGINATION_SIZE = 50

# ❌ INCORRECTO - Demasiado verboso
MAXIMUM_NUMBER_OF_RECORDS_ALLOWED_FOR_SINGLE_EXPORT_OPERATION = 100000
MAXIMUM_NUMBER_OF_DAYS_PERMITTED_IN_DATE_RANGE_FOR_REPORTS = 730
```

**Scope 5: Nombres de Clase (grande - toda la app)**

```python
# ✅ CORRECTO
class ReportService
class DashboardService
class AccessService
class ETLMonitoringService

# ❌ INCORRECTO - Excesivamente descriptivo
class ServiceForGeneratingAndExportingReports
class ServiceForMonitoringETLExecutionStatus
class ServiceForManagingUserAccessAndPermissions
```

---

### **15.4 Nombres Pronunciables (No Trabalenguas)**

**Regla**: Si no puedes pronunciar el nombre cómodamente en una reunión, es demasiado largo o complejo.

#### **Test del Trabalenguas**

Intenta decir estos nombres en voz alta 3 veces seguidas:

```python
# ❌ TRABALENGUAS - Imposible pronunciar cómodamente
execution_date_for_etl_processing_pipeline
total_number_of_records_processed_successfully
get_all_aggregated_metrics_for_dashboard_widgets

# ✅ PRONUNCIABLE - Fluido y natural
start_time
processed_count
get_dashboard_metrics
```

#### **Ejemplo Real IACT**

```python
# apps/ivr/models.py

# ❌ INCORRECTO - Trabalenguas (intenta decirlo 3 veces)
class HistoricalCallDetailRecordFromIVRLegacySystemQuarterOne(models.Model):
    date_and_time_of_call_initiation = models.DateTimeField()
    telephone_number_of_calling_party = models.CharField()
    interactive_voice_response_menu_selected = models.CharField()

# ✅ CORRECTO - Pronunciable (fácil de decir)
class HistoricoT1(models.Model):
    """Histórico Q1 del IVR."""
    dFecha = models.DateTimeField()  # Del dominio IVR
    cTelefono_Origen = models.CharField()
    cMenu = models.CharField()

# En reunión:
# ❌ "El date_and_time_of_call_initiation del 
#     historical_call_detail_record_from_IVR_legacy..."
# ✅ "El dFecha del Histórico T1..."
```

#### **Test en Reuniones**

Prueba estos diálogos en voz alta:

```python
# ❌ INCÓMODO
Dev 1: "El total_number_of_records_processed_successfully está en 
        execution_date_for_etl_processing"
Dev 2: "¿El qué está dónde? Repite más despacio..."

# ✅ NATURAL
Dev 1: "El processed count está en start time"
Dev 2: "Perfecto, entendido"
```

---

### **15.5 Balance Claridad vs Brevedad**

**Dilema**: Nombre muy corto → críptico. Nombre muy largo → trabalenguas.

**Solución**: Encuentra el punto medio usando contexto.

#### **15.5.1 Espectro de Claridad**

```
CRÍPTICO ←──────── EQUILIBRADO ────────→ VERBOSO
   ❌                   ✅                   ❌

r          →  processed_count  →  total_number_of_records_processed
p          →  phone_number     →  telephone_number_of_calling_party
d          →  start_date       →  date_when_process_started
fn         →  function_id      →  unique_identifier_of_function
```

#### **15.5.2 Criterios de Balance**

**Pregunta 1:** ¿El contexto ya proporciona claridad?

```python
# Contexto: Clase ReportService, método get_data()
class ReportService:
    @staticmethod
    def get_data(start: date, end: date) -> List[Dict]:
        # ✅ CORRECTO - Contexto claro (clase + método)
        records = fetch_from_database(start, end)
        count = len(records)
        
        # ❌ INCORRECTO - Contexto se repite en nombre
        report_records_from_report_service = fetch_from_database(start, end)
        total_count_of_report_records = len(report_records_from_report_service)
```

**Pregunta 2:** ¿El tipo ya está en el type hint?

```python
# ✅ CORRECTO - Type hint provee contexto
def process_reports(report_list: List[Report]) -> Dict[str, int]:
    count = len(report_list)  # Obvio que es "count de reports"
    return {'total': count}

# ❌ INCORRECTO - Tipo se repite en nombre
def process_reports(report_list: List[Report]) -> Dict[str, int]:
    total_count_of_reports_in_list = len(report_list)
    return {'total': total_count_of_reports_in_list}
```

**Pregunta 3:** ¿El ámbito es pequeño?

```python
# ✅ CORRECTO - Scope pequeño (5 líneas)
for i, record in enumerate(records):
    if i > 100:
        break

# ❌ INCORRECTO - Scope pequeño con nombres largos
for current_iteration_index, individual_record_object in enumerate(records):
    if current_iteration_index > maximum_iteration_count:
        break
```

---

### **15.6 Regla de Oro por Tipo de Elemento**

#### **15.6.1 Variables**

```python
# SCOPE PEQUEÑO (1-5 líneas): 1-2 palabras
for i in range(10):  # ✅ 1 palabra
    total += i

# SCOPE MEDIANO (función): 2-3 palabras
def calculate_metrics(records):
    unique_clients = set(...)  # ✅ 2 palabras
    total_calls = sum(...)  # ✅ 2 palabras

# SCOPE GRANDE (clase): 2-4 palabras
class Report:
    self.generated_at = ...  # ✅ 2 palabras
    self.export_format = ...  # ✅ 2 palabras
```

#### **15.6.2 Funciones**

```python
# UTILITIES (scope general): 2-3 palabras
def parse_date(...)  # ✅ 2 palabras
def format_phone(...)  # ✅ 2 palabras

# SERVICES (scope específico): 3-4 palabras
def get_report_data(...)  # ✅ 3 palabras
def generate_excel_file(...)  # ✅ 3 palabras

# CASES DE USO (scope muy específico): 4-5 palabras
def validate_user_has_permission(...)  # ✅ 4 palabras
def calculate_abandonment_rate_by_menu(...)  # ✅ 5 palabras

# ❌ MUY LARGO (6+ palabras)
def get_all_reports_filtered_by_date_with_metrics(...)  # ❌ 7 palabras
```

#### **15.6.3 Clases**

```python
# MODELOS: 1-3 palabras
class Report  # ✅ 1 palabra
class Dashboard  # ✅ 1 palabra
class JobExecutionLog  # ✅ 3 palabras

# SERVICES: 2-3 palabras
class ReportService  # ✅ 2 palabras
class DashboardService  # ✅ 2 palabras
class ETLMonitoringService  # ✅ 3 palabras

# ❌ MUY LARGO
class ServiceForGeneratingReportsAndDashboards  # ❌ 5 palabras
```

---

### **15.7 Aplicación IACT (Arquitectura Real)**

#### **15.7.1 Modelos Django**

```python
# apps/ivr/models.py

# ❌ INCORRECTO - Verbosidad excesiva
class ETLJobExecutionHistoryLog(models.Model):
    """Log de ejecución."""
    execution_start_date_and_time = models.DateTimeField(
        verbose_name="Fecha y hora de inicio de ejecución",
        help_text="Timestamp que indica cuándo comenzó la ejecución del job ETL"
    )
    total_number_of_records_successfully_extracted = models.IntegerField(
        verbose_name="Total de registros extraídos exitosamente",
        help_text="Cantidad de registros que fueron extraídos sin errores"
    )
    total_number_of_records_successfully_loaded = models.IntegerField(
        verbose_name="Total de registros cargados exitosamente",
        help_text="Cantidad de registros que fueron cargados en destino sin errores"
    )

# ✅ CORRECTO - Equilibrado
class JobExecutionLog(models.Model):
    """
    Log de ejecuciones del ETL.
    
    Registra cada ejecución del Stored Procedure que corre
    diariamente a las 2:00 AM para procesar datos del IVR legacy.
    """
    start_time = models.DateTimeField(
        verbose_name="Inicio",
        help_text="Timestamp de inicio"
    )
    extracted = models.IntegerField(
        default=0,
        verbose_name="Extraídos",
        help_text="Registros extraídos"
    )
    loaded = models.IntegerField(
        default=0,
        verbose_name="Cargados",
        help_text="Registros cargados"
    )
    
    class Meta:
        app_label = 'ivr'
        managed = False
        db_table = 'job_execution_log'
```

#### **15.7.2 Services**

```python
# apps/reports/services.py

# ❌ INCORRECTO - Nombres excesivos
class ReportGenerationService:
    @staticmethod
    def get_all_aggregated_data_for_trimestral_reports(
        starting_date_of_period,
        ending_date_of_period,
        specific_trimester_identifier,
        optional_did_filter_value=None
    ):
        total_number_of_records_in_result_set = 0
        # ...

# ✅ CORRECTO - Equilibrado
class ReportService:
    @staticmethod
    def get_trimestral_data(
        start_date: date,
        end_date: date,
        trimestre: str,
        did: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtiene datos de reportes trimestrales.
        
        Args:
            start_date: Fecha inicio del rango
            end_date: Fecha fin del rango
            trimestre: Trimestre (Q1, Q2, Q3)
            did: Filtro opcional de DID (Puebla/Nacional)
        
        Returns:
            Lista de registros del reporte
        """
        record_count = 0  # Scope pequeño, nombre corto
        # ...
```

#### **15.7.3 ViewSets**

```python
# apps/dashboard/views.py

# ❌ INCORRECTO - Método con nombre excesivo
class DashboardViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def get_all_aggregated_metrics_for_dashboard_display(self, request):
        """Obtiene métricas."""
        starting_date_from_request_parameters = request.query_params.get('start')
        # ...

# ✅ CORRECTO - Equilibrado
class DashboardViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """
        Obtiene métricas del dashboard.
        
        GET /api/v1/dashboard/metrics/
        Query params: start, end, trimestre
        """
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        trimestre = request.query_params.get('trimestre')
        
        data = DashboardService.get_metrics(start, end, trimestre)
        return Response(data)
```

---

### **15.8 Ejemplos Completos**

#### **15.8.1 Archivo Completo: apps/pipeline/services.py**

```python
# apps/pipeline/services.py

from datetime import date, timedelta
from typing import Dict, List, Optional
from apps.ivr.models import JobExecutionLog


class ETLMonitoringService:
    """
    Servicio de monitoreo del ETL.
    
    Proporciona métodos para verificar estado y obtener
    historial de ejecuciones del proceso ETL.
    """
    
    @staticmethod
    def get_status() -> str:
        """
        Obtiene estado actual del ETL.
        
        Returns:
            Estado: 'SUCCESS', 'FAILED', 'RUNNING'
        """
        # ✅ Variables locales: nombres cortos (scope pequeño)
        last = JobExecutionLog.objects.last()
        
        if not last:
            return 'NEVER_RUN'
        
        return last.status
    
    @staticmethod
    def get_last_execution() -> Optional[Dict]:
        """
        Obtiene detalles de última ejecución.
        
        Returns:
            Dict con datos de ejecución o None
        """
        last = JobExecutionLog.objects.order_by('-start_time').first()
        
        if not last:
            return None
        
        # ✅ Variables con 2-3 palabras (contexto claro)
        duration_seconds = (
            (last.end_time - last.start_time).total_seconds()
            if last.end_time
            else 0
        )
        
        return {
            'status': last.status,
            'start': last.start_time,
            'end': last.end_time,
            'duration': duration_seconds,
            'extracted': last.extracted,
            'loaded': last.loaded
        }
    
    @staticmethod
    def get_history(days: int = 7) -> List[Dict]:
        """
        Obtiene historial de ejecuciones.
        
        Args:
            days: Días hacia atrás (default: 7)
        
        Returns:
            Lista de ejecuciones
        """
        # ✅ Nombre equilibrado (2 palabras)
        cutoff_date = date.today() - timedelta(days=days)
        
        # ✅ Nombre claro en contexto
        executions = JobExecutionLog.objects.filter(
            start_time__gte=cutoff_date
        ).order_by('-start_time')
        
        return [
            {
                'date': e.start_time.date(),
                'status': e.status,
                'records': e.extracted
            }
            for e in executions
        ]
```

**Análisis de equilibrio:**
- `get_status()` - ✅ 2 palabras (claro y conciso)
- `last` - ✅ 1 palabra (scope pequeño, contexto obvio)
- `duration_seconds` - ✅ 2 palabras (valor numérico, unidad clara)
- `cutoff_date` - ✅ 2 palabras (punto de corte, concepto estándar)

---

#### **15.8.2 Comparación Lado a Lado**

```python
# ════════════════════════════════════════════════════════
# COMPARACIÓN: VERBOSO vs EQUILIBRADO
# ════════════════════════════════════════════════════════

# ❌ VERSIÓN VERBOSA (difícil de leer)
class ServiceForMonitoringExecutionOfETLProcesses:
    @staticmethod
    def get_current_execution_status_of_etl_process() -> str:
        last_execution_record_from_database = (
            ExecutionLogTable.objects.order_by(
                'timestamp_of_execution_start'
            ).last()
        )
        
        if last_execution_record_from_database is None:
            return 'PROCESS_HAS_NEVER_BEEN_EXECUTED'
        
        return last_execution_record_from_database.current_status_value

# ✅ VERSIÓN EQUILIBRADA (fácil de leer)
class ETLMonitoringService:
    @staticmethod
    def get_status() -> str:
        last_execution = JobExecutionLog.objects.last()
        
        if not last_execution:
            return 'NEVER_RUN'
        
        return last_execution.status

# MÉTRICAS:
# Verboso:
# - Nombre clase: 43 caracteres, 6 palabras
# - Nombre método: 46 caracteres, 7 palabras
# - Variable: 37 caracteres, 5 palabras
# - Total líneas: 13
#
# Equilibrado:
# - Nombre clase: 22 caracteres, 3 palabras
# - Nombre método: 10 caracteres, 2 palabras
# - Variable: 14 caracteres, 2 palabras
# - Total líneas: 8
#
# REDUCCIÓN: 38% menos líneas, MUCHO más legible
```

---

### **15.9 Anti-patterns de Equilibrio**

#### **Anti-pattern 1: Repetir el Tipo en el Nombre**

```python
# ❌ ANTI-PATTERN
report_dict: Dict = get_data()
user_list: List[User] = User.objects.all()
count_int: int = len(records)

# ✅ CORRECTO - Type hint ya provee info
report_data: Dict = get_data()
users: List[User] = User.objects.all()
count: int = len(records)
```

#### **Anti-pattern 2: Repetir el Contexto**

```python
# ❌ ANTI-PATTERN
class ReportService:
    def get_report_data_for_report(self):  # "report" 3 veces
        report_records_list = []
        return report_records_list

# ✅ CORRECTO
class ReportService:
    def get_data(self):  # Contexto: "Report" ya está en clase
        records = []
        return records
```

#### **Anti-pattern 3: Describir la Implementación**

```python
# ❌ ANTI-PATTERN - Describe CÓMO, no QUÉ
def get_data_from_database_using_orm_query():
    pass

def calculate_using_sum_of_all_elements_divided_by_count():
    pass

# ✅ CORRECTO - Describe QUÉ hace
def get_data():
    pass

def calculate_average():
    pass
```

#### **Anti-pattern 4: "And" en Nombres**

```python
# ❌ ANTI-PATTERN - "and" indica que hace demasiado
def get_and_process_and_save_data():
    pass

def validate_and_transform_and_load():
    pass

# ✅ CORRECTO - Separar responsabilidades
def get_data():
    pass

def process_data():
    pass

def save_data():
    pass
```

---

### **15.10 Checklist de Verificación**

```
ANTES DE COMMIT - VERIFICAR EQUILIBRIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NOMBRES GENERALES:
☐ ¿Puedo pronunciar el nombre 3 veces seguidas fácilmente?
☐ ¿El nombre tiene menos de 5 palabras?
☐ ¿El nombre tiene menos de 50 caracteres?
☐ ¿El nombre evita palabras como "data", "info", "stuff"?
☐ ¿El nombre NO repite el tipo (si hay type hint)?
☐ ¿El nombre NO repite el contexto (clase/módulo)?

POR SCOPE:
☐ Variables de loop: ¿1 palabra? (i, user, record)
☐ Variables locales: ¿1-2 palabras? (count, total)
☐ Parámetros: ¿2-3 palabras? (start_date, user_id)
☐ Variables de instancia: ¿2-4 palabras? (max_records)
☐ Funciones: ¿2-5 palabras? (get_data, calculate_metrics)
☐ Clases: ¿1-4 palabras? (Report, ReportService)

ANTI-PATTERNS:
☐ ¿Sin "and" en nombres de función?
☐ ¿Sin describir implementación?
☐ ¿Sin "dissertations" o "trabalenguas"?

DOCUMENTACIÓN:
☐ Detalles en docstring, NO en nombre
☐ help_text complementa, NO repite nombre
☐ Comentarios solo si necesarios
```

---

## 📊 RESUMEN SECCIÓN 15

```
PRINCIPIO DE EQUILIBRIO:

CONCEPTO CLAVE:
"Balancear claridad con brevedad según el scope"

REGLAS:
1. Evitar verbosidad excesiva
2. Longitud apropiada según scope
3. Nombres pronunciables (no trabalenguas)
4. Balance claridad vs brevedad
5. Usar contexto para acortar nombres

REGLA DE ORO:
- Loop vars: 1 palabra
- Local vars: 1-2 palabras
- Parameters: 2-3 palabras
- Instance vars: 2-4 palabras
- Functions: 2-5 palabras
- Classes: 1-4 palabras

ANTI-PATTERNS:
❌ Repetir tipo en nombre
❌ Repetir contexto
❌ Describir implementación
❌ Usar "and" en nombres
❌ Nombres de "dissertación"
```

---

<a name="16-nomenclatura-por-ubicacion"></a>
## 16. NOMENCLATURA POR UBICACIÓN (IACT)

**Principio**: El nombre de un componente debe reflejar su ubicación en la arquitectura.

### 16.1 Regla por App

| Ubicación | Prefijo | Ejemplos |
|-----------|---------|----------|
| `apps/access/` | **Access** | AccessService, AccessAuditMiddleware |
| `apps/reports/` | **Report** | ReportService, ReportViewSet |
| `apps/dashboard/` | **Dashboard** | DashboardService, DashboardViewSet |
| `apps/authentication/` | **Auth/Session** | AuthService, SessionMiddleware |
| `apps/users/` | **User** | UserService, UserViewSet |
| `apps/pipeline/` | **Pipeline/ETL** | ETLMonitoringService, PipelineService |
| `apps/ivr/` | **Sin prefijo** | HistoricoT1, ReporteTrimestral (nombres reales) |
| `apps/utils/` | **Sin prefijo** | SoftDeleteMixin, TimeStampedModel |

### 16.2 Ejemplos por App

```python
# apps/access/services.py
class AccessService:  # ✅ Prefijo "Access"
    """Gestión de funciones RBAC."""
    pass

# apps/reports/services.py
class ReportService:  # ✅ Prefijo "Report"
    """Generación de reportes."""
    pass

# apps/dashboard/services.py
class DashboardService:  # ✅ Prefijo "Dashboard"
    """Gestión de dashboards."""
    pass

# apps/pipeline/services.py
class ETLMonitoringService:  # ✅ Prefijo "ETL" o "Pipeline"
    """Monitoreo del ETL."""
    pass

# apps/utils/models.py
class SoftDeleteMixin:  # ✅ Sin prefijo (compartido)
    """Mixin compartido por todas las apps."""
    pass
```

### 16.3 Regla de Oro

**Pregunta:** _"¿Si muevo este archivo a otra app, el nombre sigue teniendo sentido?"_

- **SI** → Nombre genérico (va en `utils/`)
- **NO** → Nombre con prefijo de app

**Ejemplos:**

```python
# SoftDeleteMixin:
# - ¿Sirve para reports/? SÍ
# - ¿Sirve para users/? SÍ
# - ¿Sirve para todas las apps? SÍ
# → Genérico ✅ (va en utils/)

# AccessService:
# - ¿Sirve para reports/? NO
# - ¿Es específico de access/? SÍ
# → Prefijo Access ✅ (está en access/)

# ReportService:
# - ¿Sirve para access/? NO
# - ¿Es específico de reports/? SÍ
# → Prefijo Report ✅ (está en reports/)
```

---

<a name="17-drf-viewsets-y-views"></a>
## 17. DRF: VIEWSETS Y VIEWS

### 17.1 Cuándo usar ViewSets vs APIView

**Usar ViewSets cuando:**
- CRUD completo de un modelo
- Endpoints RESTful estándar
- Muchas acciones sobre un recurso

**Usar APIView cuando:**
- Endpoint único sin modelo
- Lógica no-CRUD (login, logout)
- Personalización extrema

### 17.2 Nomenclatura de ViewSets

```python
# ✅ CORRECTO - Patrón: {Modelo}ViewSet
class ReportViewSet(viewsets.ModelViewSet):
    """API CRUD de reportes."""
    pass

class DashboardViewSet(viewsets.ModelViewSet):
    """API CRUD de dashboards."""
    pass

class UserViewSet(viewsets.ModelViewSet):
    """API CRUD de usuarios."""
    pass

# ❌ INCORRECTO
class ReportAPI(viewsets.ModelViewSet):  # ❌ No usa sufijo ViewSet
    pass

class ReportsViewSet(viewsets.ModelViewSet):  # ❌ Plural (usar singular)
    pass
```

### 17.3 Custom Actions

```python
# apps/reports/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class ReportViewSet(viewsets.ModelViewSet):
    """API de reportes."""
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):  # ✅ Verbo simple
        """
        Exporta reporte a Excel.
        
        POST /api/v1/reports/{id}/export/
        """
        report = self.get_object()
        file_path = ReportService.generate_excel(report)
        return Response({'file_url': file_path})
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):  # ✅ Nombre sustantivo
        """
        Obtiene métricas de reportes.
        
        GET /api/v1/reports/metrics/
        """
        data = ReportService.get_metrics()
        return Response(data)
```

---

<a name="18-drf-serializers"></a>
## 18. DRF: SERIALIZERS

### 18.1 Nomenclatura Básica

```python
# ✅ CORRECTO - Patrón: {Modelo}Serializer
class ReportSerializer(serializers.ModelSerializer):
    """Serializer de Report."""
    
    class Meta:
        model = Report
        fields = ['id', 'name', 'description', 'created_at']

class DashboardSerializer(serializers.ModelSerializer):
    """Serializer de Dashboard."""
    
    class Meta:
        model = Dashboard
        fields = '__all__'

# ❌ INCORRECTO
class ReportSerializerClass(serializers.ModelSerializer):  # ❌ Redundante
    pass

class ReportSer(serializers.ModelSerializer):  # ❌ Abreviado
    pass
```

### 18.2 Serializers Especializados

```python
# apps/reports/serializers.py

# ✅ CORRECTO - Sufijo indica propósito
class ReportListSerializer(serializers.ModelSerializer):
    """Serializer para listar reportes (campos mínimos)."""
    
    class Meta:
        model = Report
        fields = ['id', 'name', 'created_at']

class ReportDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de reporte (todos los campos)."""
    
    class Meta:
        model = Report
        fields = '__all__'

class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reporte (sin campos auto)."""
    
    class Meta:
        model = Report
        fields = ['name', 'description']
```

---

**FIN DE PARTE 2/5**

**Continúa en:** CLEAN_CODE_NAMING_PRINCIPLES_v2_3_0_PARTE_3.md

---

**Resumen Parte 2:**
- ✅ ⭐ **NUEVA Sección 15: Principio de Equilibrio** ⭐ (exhaustiva, 10 subsecciones)
- ✅ Reglas explícitas de longitud según scope
- ✅ Ejemplos IACT con arquitectura real
- ✅ Anti-patterns de equilibrio
- ✅ Checklist de verificación
- ✅ Sección 16: Nomenclatura por ubicación
- ✅ Sección 17: DRF ViewSets
- ✅ Sección 18: DRF Serializers

**Próxima parte:** DRF avanzado (secciones 19-23)
