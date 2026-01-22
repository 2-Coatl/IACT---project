---
version: 2.3.0
date: 2026-01-18
project: IACT (Sistema Call Center)
base: Clean Code (Robert Martin) + Clean Architecture
changelog: PARTE 1/5 - Preparación para nueva Sección 15 (Principio de Equilibrio)
partes: 1/5
estado: completo
---

# CLEAN CODE NAMING PRINCIPLES v2.3.0

**PARTE 1/5: PRINCIPIOS FUNDAMENTALES**

---

## 📋 TABLA DE CONTENIDOS - DOCUMENTO COMPLETO

### PARTE 1/5: PRINCIPIOS FUNDAMENTALES (ESTA PARTE)
1. [Usar Nombres que Revelen Intenciones](#1-usar-nombres-que-revelen-intenciones)
2. [Evitar la Desinformación](#2-evitar-la-desinformacion)
3. [Realizar Distinciones con Sentido](#3-realizar-distinciones-con-sentido)
4. [Usar Nombres que se Puedan Pronunciar](#4-usar-nombres-que-se-puedan-pronunciar)
5. [Usar Nombres que se Puedan Buscar](#5-usar-nombres-que-se-puedan-buscar)
6. [Evitar Codificaciones](#6-evitar-codificaciones)
7. [Evitar Asignaciones Mentales](#7-evitar-asignaciones-mentales)
8. [Una Palabra por Concepto](#8-una-palabra-por-concepto)
9. [Architecture Reveals Intent](#9-architecture-reveals-intent)
10. [Frameworks are Plugins](#10-frameworks-are-plugins)
11. [Dependencies Point Inward](#11-dependencies-point-inward)
12. [Use Cases Drive Architecture](#12-use-cases-drive-architecture)
13. [Testability Without Framework](#13-testability-without-framework)
14. [Regla de Idioma para IACT](#14-regla-de-idioma-para-iact)

### PARTE 2/5: EQUILIBRIO Y DRF BÁSICO (Ver PARTE 2/5)
15. ⭐ **PRINCIPIO DE EQUILIBRIO** ⭐ (NUEVA SECCIÓN)
16. Nomenclatura por Ubicación (IACT)
17. DRF: ViewSets y Views
18. DRF: Serializers

### PARTE 3/5: DRF AVANZADO (Ver PARTE 3/5)
19. DRF: Permissions y Authentication
20. DRF: Decorators
21. Django: Middleware
22. DRF: Mixins
23. DRF: Response y Exception Handling

### PARTE 4/5: IACT ESPECÍFICO (Ver PARTE 4/5)
24. DRF: Renderers, Parsers, Pagination
25. IACT: Separación access/ vs core/
26. IACT: Service Layer Pattern
27. IACT: Modelos y Herencia

### PARTE 5/5: ANTI-PATTERNS Y CIERRE (Ver PARTE 5/5)
28. Anti-patterns Comunes
29. Tabla de Resumen
30. Referencias
31. Changelog v2.3.0

---

## CONTROL DE CAMBIOS v2.2.0 → v2.3.0

| Aspecto | v2.2.0 | v2.3.0 |
|---------|--------|--------|
| Total secciones | 30 | 31 |
| Partes | 4 | 5 |
| **Principio Equilibrio** | ❌ No existe | ✅ **Sección 15 (nueva)** |
| Nombres trabalenguas | No abordado | ✅ **Guía explícita** |
| Longitud según scope | Implícito | ✅ **Reglas específicas** |
| Ejemplos IACT | v2.2.0 | ✅ **Arquitectura real** |
| Estructura | 4 partes | ✅ **5 partes** |

---

## PARTE I: PRINCIPIOS FUNDAMENTALES

### **FUNDAMENTO CIENTÍFICO:**

**Robert Martin**: _"En el software, los nombres son omnipresentes. Aparecen en variables, funciones, argumentos, clases y paquetes. Usamos nombres constantemente. Por ello, debemos hacerlo bien."_

---

<a name="1-usar-nombres-que-revelen-intenciones"></a>
### **1. USAR NOMBRES QUE REVELEN INTENCIONES**

**Martin's Definition**: _"El nombre debe indicar por qué existe, qué hace y cómo se usa. Si un nombre requiere un comentario, significa que no revela su cometido."_

**Aplicación**: Los nombres deben ser tan descriptivos que eliminen la necesidad de comentarios explicativos. El nombre debe comunicar inmediatamente el propósito.

**Ejemplos Generales:**

```python
# ❌ INCORRECTO
def get_data(u):
    # Obtiene datos del usuario
    return db.query(u)

# ✅ CORRECTO
def get_user_profile_data(user_id: int):
    """Obtiene datos del perfil del usuario."""
    return database.query_user_profile(user_id)
```

**Aplicación IACT (Arquitectura Real):**

```python
# apps/ivr/models.py

# ❌ INCORRECTO - Nombre genérico
def process(data):
    # Procesa datos
    return etl.run(data)

# ✅ CORRECTO - Revela intención específica
def extract_call_records_from_ivr_legacy(
    start_date: date,
    end_date: date
) -> List[Dict]:
    """
    Extrae registros de llamadas del IVR legacy (MariaDB).
    
    Lee de tbl_historico_t1/t2/t3_2025 filtrando por:
    - Rango de fechas
    - DIDs específicos (19020084, 19028031)
    
    Returns:
        Lista de diccionarios con campos:
        - dFecha, cMenu, cOpcion, cTelefono_Origen
    """
    from apps.ivr.models import HistoricoT1, HistoricoT2, HistoricoT3
    
    # Determinar tabla según trimestre
    trimester = determine_trimester(start_date)
    
    if trimester == 1:
        queryset = HistoricoT1.objects.all()
    elif trimester == 2:
        queryset = HistoricoT2.objects.all()
    else:
        queryset = HistoricoT3.objects.all()
    
    return list(queryset.filter(
        dFecha__gte=start_date,
        dFecha__lte=end_date,
        cDID_800Transfer__in=['19020084', '19028031']
    ).values())
```

**Comparación:**
- ❌ `process(data)` → ¿Qué procesa? ¿Cómo? ¿Dónde?
- ✅ `extract_call_records_from_ivr_legacy()` → Queda claro: EXTRAE registros de LLAMADAS del IVR LEGACY

---

<a name="2-evitar-la-desinformacion"></a>
### **2. EVITAR LA DESINFORMACIÓN**

**Martin's Principle**: _"No haga referencia a un grupo de cuentas como accountList a menos que realmente sea una lista. Evite usar nombres con variaciones mínimas."_

**Aplicación**: Los nombres deben ser precisos y no sugerir características que el objeto no posee. Las abreviaciones ambiguas generan confusión.

**Ejemplos Generales:**

```python
# ❌ INCORRECTO
accountList = User.objects.all()  # No es una lista, es QuerySet

# ✅ CORRECTO
user_queryset = User.objects.all()
# o mejor aún
active_users = User.objects.filter(is_active=True)
```

**Aplicación IACT (Arquitectura Real):**

```python
# apps/reports/services.py

# ❌ INCORRECTO - Sugiere tipo incorrecto
report_list = ReporteTrimestral.objects.all()  # QuerySet, NO lista
call_array = get_call_data()  # Retorna dict, NO array
menu_string = get_menu_options()  # Retorna List[str], NO string

# ✅ CORRECTO - Tipo claro y preciso
report_queryset = ReporteTrimestral.objects.all()
call_records_dict = get_call_data()  # Dict con estructura conocida
menu_options = get_menu_options()  # List[str] claro

# ✅ MÁS ESPECÍFICO AÚN - Arquitectura real
trimestral_reports = ReporteTrimestral.objects.filter(
    trimestre='Q1'
)  # Nombre describe QUÉ contiene, no solo tipo

# apps/ivr/models.py - Modelo real
class ReporteTrimestral(models.Model):
    """
    Tabla agregada generada por ETL.
    Django solo lee (managed=False).
    """
    trimestre = models.CharField(max_length=20)
    fecha = models.DateField()
    servicio_800 = models.CharField(max_length=50)
    total_llamadas = models.IntegerField()
    
    class Meta:
        app_label = 'ivr'
        managed = False  # Django NO gestiona schema
        db_table = 'tbl_reporte_trimestral'  # Tabla real en MariaDB
```

**Por qué es importante en IACT:**
- `ReporteTrimestral.objects.all()` es un QuerySet que NO carga datos hasta evaluarse
- Llamarlo `report_list` sugiere que ya tiene datos en memoria → ❌ DESINFORMACIÓN
- Usar `trimestral_reports` describe CONTENIDO, no tipo → ✅ CORRECTO

---

<a name="3-realizar-distinciones-con-sentido"></a>
### **3. REALIZAR DISTINCIONES CON SENTIDO**

**Martin's Warning**: _"No basta con añadir series de números o palabras adicionales. Info y Data son palabras adicionales, como a, an y the."_

**Aplicación**: Cada palabra en el nombre debe añadir valor semántico real. Las palabras como "info", "data", "stuff" son ruido.

**Ejemplos Generales:**

```python
# ❌ INCORRECTO
user_data = get_user_data()
user_info = get_user_info()
# ¿Cuál es la diferencia?

# ✅ CORRECTO
user_profile = get_user_profile()
user_permissions = get_user_permissions()
# Distinción clara
```

**Aplicación IACT (Arquitectura Real):**

```python
# apps/reports/services.py

# ❌ INCORRECTO - Sin distinción semántica
report_data = get_report_data()
report_info = get_report_info()
report_stuff = get_report_stuff()
report_things = get_report_things()

# ✅ CORRECTO - Distinción clara con arquitectura real
report_metrics = get_report_metrics()  
# Retorna: {'total_llamadas': 1500, 'tasa_abandono': 8.5}

report_metadata = get_report_metadata()  
# Retorna: {'generated_at': datetime, 'author': 'user_id', 'version': '1.0'}

report_filters = get_report_filters()  
# Retorna: {'trimestre': 'Q1', 'did': 'Puebla', 'start_date': date}

dashboard_widgets = get_dashboard_widgets()
# Retorna: List de objetos Widget configurados

# apps/dashboard/services.py - Arquitectura real

class DashboardService:
    """
    Servicio para obtener datos de dashboards.
    
    Dashboard ≠ Report:
    - Dashboard: Visualización en vivo con widgets
    - Report: Generación bajo demanda, exportable
    """
    
    @staticmethod
    def get_dashboard_metrics(trimestre: str) -> Dict:
        """
        Obtiene métricas (KPIs) del dashboard.
        
        Returns:
            {
                'total_llamadas': int,
                'tasa_abandono': float,
                'clientes_unicos': int
            }
        """
        from apps.ivr.models import ReporteTrimestral
        
        metrics = ReporteTrimestral.objects.filter(
            trimestre=trimestre
        ).aggregate(
            total_llamadas=Sum('total_llamadas'),
            # ... más agregaciones
        )
        
        return metrics
    
    @staticmethod
    def get_dashboard_configuration(dashboard_id: str) -> Dict:
        """
        Obtiene configuración del dashboard.
        
        Returns:
            {
                'layout': {...},
                'widgets': [...],
                'filters': {...}
            }
        """
        from apps.dashboard.models import Dashboard
        
        dashboard = Dashboard.objects.get(uuid=dashboard_id)
        return {
            'layout': dashboard.layout_config,
            'widgets': list(dashboard.widgets.all()),
            'filters': dashboard.default_filters
        }
```

**Distinción clara en IACT:**
- `report_metrics` → Números/KPIs
- `report_metadata` → Info del reporte mismo
- `report_filters` → Criterios aplicados
- `dashboard_widgets` → Componentes visuales
- `dashboard_configuration` → Setup del dashboard

---

<a name="4-usar-nombres-que-se-puedan-pronunciar"></a>
### **4. USAR NOMBRES QUE SE PUEDAN PRONUNCIAR**

**Martin's Insight**: _"Si no lo puede pronunciar, no podrá explicarlo sin parecer tonto. La programación es una actividad social."_

**Aplicación**: La capacidad de pronunciar nombres facilita la comunicación en equipos.

**Ejemplos Generales:**

```python
# ❌ INCORRECTO
genymdhms = datetime.now()  # "gen-y-m-d-h-m-s"?
modymdhms = user.modified_at

# ✅ CORRECTO
generation_timestamp = datetime.now()
modification_timestamp = user.modified_at
```

**Aplicación IACT (Arquitectura Real):**

```python
# apps/ivr/models.py

# ❌ INCORRECTO - Impronunciable
rptctxt = get_context()  # "rpt-c-t-x-t"?
usrfnc = get_functions()  # "u-s-r-f-n-c"?
etlsts = check_status()  # "e-t-l-s-t-s"?
cmenuagr = CMenuAgregado.objects.all()  # "c-menu-a-g-r"?

# ✅ CORRECTO - Pronunciable y claro
report_context = get_context()
user_functions = get_functions()
etl_status = check_status()
menu_agregado = CMenuAgregado.objects.all()

# apps/pipeline/services.py - Arquitectura real

class ETLMonitoringService:
    """Servicio para monitorear ejecuciones del ETL."""
    
    @staticmethod
    def get_last_execution_status() -> Dict:
        """
        Obtiene estado de la última ejecución del ETL.
        
        Lee de job_execution_log (tabla de control en MariaDB).
        """
        from apps.ivr.models import JobExecutionLog
        
        # ❌ INCORRECTO - Variables impronunciables
        lstexec = JobExecutionLog.objects.last()
        sts = lstexec.status
        recs = lstexec.records_extracted
        
        # ✅ CORRECTO - Variables pronunciables
        last_execution = JobExecutionLog.objects.order_by('-start_time').first()
        execution_status = last_execution.status
        extracted_records = last_execution.records_extracted
        loaded_records = last_execution.records_loaded
        
        return {
            'status': execution_status,  # 'SUCCESS', 'FAILED', 'RUNNING'
            'extracted': extracted_records,
            'loaded': loaded_records,
            'last_run': last_execution.start_time
        }
```

**En reuniones de equipo:**
- ❌ "El rpt-ctx necesita el e-t-l-s-t-s" → Imposible de seguir
- ✅ "El report context necesita el etl status" → Se entiende perfectamente

---

<a name="5-usar-nombres-que-se-puedan-buscar"></a>
### **5. USAR NOMBRES QUE SE PUEDAN BUSCAR**

**Martin's Rule**: _"Los nombres extensos superan a los breves y cualquier nombre que se pueda buscar supera a una constante. La longitud de un nombre debe corresponderse al tamaño de su ámbito."_

**Aplicación**: Los nombres deben ser únicos y específicos para facilitar búsquedas en el codebase.

**Ejemplos Generales:**

```python
# ❌ INCORRECTO
WORK_DAYS_PER_WEEK = 5
s = WORK_DAYS_PER_WEEK * 4  # ¿Qué es 's'? Imposible buscar

# ✅ CORRECTO
WORK_DAYS_PER_WEEK = 5
total_work_days_in_month = WORK_DAYS_PER_WEEK * 4  # Fácil buscar
```

**Aplicación IACT (Arquitectura Real):**

```python
# apps/reports/constants.py

# ❌ INCORRECTO - Difícil de buscar
MAX_RECORDS = 100000  # ¿Para qué? Hay muchos "MAX_RECORDS"
r = query.count()  # Imposible buscar todas las "r"
if r > MAX_RECORDS:
    raise Error()  # ¿Qué error?

# ✅ CORRECTO - Fácil de buscar (CNST-007)
MAX_EXPORT_RECORDS = 100000  # Específico para exports
CNST_007_MAX_EXPORT_RECORDS = 100000  # Aún más específico

total_records_count = query.count()
if total_records_count > MAX_EXPORT_RECORDS:
    raise ExportLimitExceeded(
        f"Límite de {MAX_EXPORT_RECORDS} registros excedido"
    )

# apps/ivr/constants.py - Arquitectura real

# Constantes de configuración ETL
ETL_TIMEOUT_SECONDS = 300  # CNST-004
ETL_MAX_RETRIES = 3
ETL_RETRY_DELAY_SECONDS = 30

# Constantes de validación reportes
REPORT_MAX_DATE_RANGE_DAYS = 730  # CNST-006 (2 años)
REPORT_MAX_EXPORT_RECORDS = 100000  # CNST-007

# Constantes de DIDs
DID_PUEBLA = '19020084'
DID_NACIONAL_A = '19028031'
DID_NACIONAL_B = '19020001'
ALLOWED_DIDS = [DID_PUEBLA, DID_NACIONAL_A, DID_NACIONAL_B]

# apps/reports/services.py

class ReportService:
    """Servicio para generación de reportes."""
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> None:
        """
        Valida que el rango de fechas no exceda CNST-006.
        
        Raises:
            ValidationError: Si rango > 730 días
        """
        # ❌ INCORRECTO - Número mágico, variable críptica
        d = (end_date - start_date).days
        if d > 730:
            raise ValidationError("Rango excedido")
        
        # ✅ CORRECTO - Constante nombrada, variable buscable
        date_range_days = (end_date - start_date).days
        
        if date_range_days > REPORT_MAX_DATE_RANGE_DAYS:
            raise ValidationError(
                f"Rango máximo permitido: {REPORT_MAX_DATE_RANGE_DAYS} días "
                f"(CNST-006). Rango solicitado: {date_range_days} días"
            )
```

**Beneficios en búsqueda:**
- Buscar `MAX_EXPORT_RECORDS` → Encuentra TODOS los lugares donde se usa el límite
- Buscar `CNST_007` → Encuentra la restricción específica
- Buscar `total_records_count` → Encuentra cálculos relacionados
- Buscar `r` → Encuentra millones de variables sin relación

---

<a name="6-evitar-codificaciones"></a>
### **6. EVITAR CODIFICACIONES**

**Martin's Principle**: _"No añada prefijos ni sufijos que indiquen el tipo. El código moderno no necesita notación húngara."_

**Aplicación**: Evitar prefijos como `str`, `int`, `obj` que indican tipo. Python tiene type hints.

**Ejemplos Generales:**

```python
# ❌ INCORRECTO - Notación húngara
strName = "John"
intAge = 25
lstUsers = [user1, user2]

# ✅ CORRECTO - Sin prefijos, usa type hints
name: str = "John"
age: int = 25
users: List[User] = [user1, user2]
```

**Aplicación IACT (Arquitectura Real):**

```python
# apps/reports/services.py

# ❌ INCORRECTO - Codificaciones innecesarias
strReportName = "Monthly Report"
intRecordCount = 1000
dictFilters = {'trimestre': 'Q1'}
lstResults = query.all()

# ✅ CORRECTO - Type hints en lugar de prefijos
report_name: str = "Monthly Report"
record_count: int = 1000
filters: Dict[str, Any] = {'trimestre': 'Q1'}
results: List[Dict] = list(query.values())

# apps/ivr/models.py - Modelo real (managed=False)

class HistoricoT1(models.Model):
    """
    Tabla histórica Q1 del IVR.
    Django solo lee (readonly, managed=False).
    """
    # ❌ INCORRECTO - Notación húngara en campos
    strMenu = models.CharField(max_length=100)
    intCantidadLlamadas = models.IntegerField()
    dtFecha = models.DateField()
    
    # ✅ CORRECTO - Django ya provee tipos en el modelo
    cMenu = models.CharField(max_length=100)  # 'c' es del dominio, no tipo
    total_llamadas = models.IntegerField()
    dFecha = models.DateField()  # 'd' es del dominio (date)
    
    class Meta:
        app_label = 'ivr'
        managed = False
        db_table = 'tbl_historico_t1_2025'

# apps/dashboard/services.py - Type hints modernos

from typing import Dict, List, Optional
from datetime import date

class DashboardService:
    """Servicio de dashboards con type hints."""
    
    @staticmethod
    def get_dashboard_data(
        dashboard_id: str,
        start_date: date,
        end_date: date,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene datos del dashboard con filtros aplicados.
        
        Type hints eliminan necesidad de notación húngara:
        - dashboard_id: str → No necesita 'strDashboardId'
        - filters: Optional[Dict] → No necesita 'dictFilters'
        """
        # ❌ INCORRECTO
        dictMetrics = {}
        lstWidgets = []
        intTotalLlamadas = 0
        
        # ✅ CORRECTO
        metrics: Dict[str, Any] = {}
        widgets: List[Widget] = []
        total_llamadas: int = 0
        
        return {
            'metrics': metrics,
            'widgets': [w.to_dict() for w in widgets],
            'total_llamadas': total_llamadas
        }
```

**EXCEPCIÓN: Prefijos de dominio en IACT**

Algunos prefijos NO son codificaciones, son PARTE DEL DOMINIO (nomenclatura del IVR legacy):

```python
# ✅ CORRECTO - Prefijos de dominio (no de tipo)
cMenu = models.CharField()  # 'c' = código (del dominio IVR)
dFecha = models.DateField()  # 'd' = date (del dominio IVR)
cDID_800Transfer = models.CharField()  # Del dominio IVR

# Estos prefijos vienen de las tablas legacy y se mantienen
# porque reflejan la nomenclatura real del sistema IVR
```

---

<a name="7-evitar-asignaciones-mentales"></a>
### **7. EVITAR ASIGNACIONES MENTALES**

**Martin's Warning**: _"Los lectores no deberían tener que traducir mentalmente sus nombres a otros que ya conocen."_

**Aplicación**: No usar abreviaciones que requieran traducción mental. El código se lee más veces de las que se escribe.

**Ejemplos Generales:**

```python
# ❌ INCORRECTO - Requiere traducción mental
for i in users:
    for j in permissions:
        if i.has_permission(j):
            r.append((i, j))

# ✅ CORRECTO - Auto-explicativo
for user in users:
    for permission in permissions:
        if user.has_permission(permission):
            results.append((user, permission))
```

**Aplicación IACT (Arquitectura Real):**

```python
# apps/access/services.py

# ❌ INCORRECTO - Traducción mental necesaria
def check_fn(u, f):
    """¿Qué es u? ¿Qué es f?"""
    a = get_agr(u)
    for ag in a:
        for func in ag.fns:
            if func.fid == f:
                return True
    return False

# ✅ CORRECTO - Sin traducción mental
def user_has_function(user: User, function_id: str) -> bool:
    """
    Verifica si usuario tiene función asignada.
    
    Args:
        user: Usuario a verificar
        function_id: ID de función (ej: 'reports.view')
    
    Returns:
        True si el usuario tiene la función
    """
    agrupadores = get_user_agrupadores(user)
    
    for agrupador in agrupadores:
        for function in agrupador.functions.all():
            if function.function_id == function_id:
                return True
    
    return False

# apps/reports/services.py - Arquitectura real

class ReportService:
    """Servicio de reportes."""
    
    @staticmethod
    def generate_trimestral_report(
        trimestre: str,
        did: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera reporte trimestral.
        
        NO usar:
        - t para trimestre
        - d para DID
        - r para resultado
        """
        # ❌ INCORRECTO - Traducción mental
        q = ReporteTrimestral.objects.filter(trimestre=trimestre)
        if did:
            q = q.filter(servicio_800=did)
        r = list(q.values())
        c = len(r)
        
        # ✅ CORRECTO - Auto-explicativo
        queryset = ReporteTrimestral.objects.filter(trimestre=trimestre)
        
        if did:
            queryset = queryset.filter(servicio_800=did)
        
        report_data = list(queryset.values(
            'fecha',
            'servicio_800',
            'total_llamadas',
            'clientes_unicos'
        ))
        
        total_records = len(report_data)
        
        return {
            'trimestre': trimestre,
            'did': did or 'TODOS',
            'data': report_data,
            'count': total_records
        }
```

**Por qué es crítico en IACT:**
- Sistema complejo con múltiples apps (ivr, reports, dashboard, access, pipeline)
- Código lo leen: desarrolladores nuevos, revisores, equipos de QA
- Nombres auto-explicativos eliminan necesidad de contexto mental

---

<a name="8-una-palabra-por-concepto"></a>
### **8. UNA PALABRA POR CONCEPTO**

**Martin's Rule**: _"Escoja una palabra por cada concepto abstracto y manténgala. Por ejemplo, use 'fetch', 'retrieve' o 'get', pero no las tres para el mismo concepto."_

**Aplicación**: Consistencia en el vocabulario del proyecto.

**Ejemplos Generales:**

```python
# ❌ INCORRECTO - Palabras diferentes para mismo concepto
user = get_user(id)
profile = fetch_profile(id)
account = retrieve_account(id)
# ¿Cuál es la diferencia?

# ✅ CORRECTO - Una palabra consistente
user = get_user(id)
profile = get_profile(id)
account = get_account(id)
```

**Aplicación IACT (Arquitectura Real):**

```python
# VOCABULARIO IACT ESTANDARIZADO

# ✅ CORRECTO - Palabra única por concepto

# CONCEPTO: Obtener datos → Palabra: "get"
def get_report_data(...)
def get_dashboard_metrics(...)
def get_user_functions(...)

# CONCEPTO: Generar archivos → Palabra: "generate"
def generate_excel_report(...)
def generate_csv_export(...)
def generate_pdf_document(...)

# CONCEPTO: Validar → Palabra: "validate"
def validate_date_range(...)
def validate_permissions(...)
def validate_export_limit(...)

# CONCEPTO: Verificar existencia → Palabra: "check"
def check_etl_status(...)
def check_user_access(...)
def check_data_availability(...)

# apps/reports/services.py - Ejemplo real

class ReportService:
    """
    Servicio de reportes con vocabulario consistente.
    
    Usa:
    - get_* para OBTENER datos
    - generate_* para CREAR archivos
    - validate_* para VERIFICAR reglas
    """
    
    # ❌ INCORRECTO - Palabras mezcladas
    @staticmethod
    def fetch_report_data(...):  # ❌ fetch
        pass
    
    @staticmethod
    def retrieve_dashboard_info(...):  # ❌ retrieve
        pass
    
    @staticmethod
    def obtain_user_permissions(...):  # ❌ obtain
        pass
    
    # ✅ CORRECTO - Palabra consistente: "get"
    @staticmethod
    def get_report_data(
        trimestre: str,
        did: Optional[str] = None
    ) -> List[Dict]:
        """Obtiene datos del reporte."""
        return list(ReporteTrimestral.objects.filter(
            trimestre=trimestre
        ).values())
    
    @staticmethod
    def get_dashboard_metrics(dashboard_id: str) -> Dict:
        """Obtiene métricas del dashboard."""
        return DashboardService.get_metrics(dashboard_id)
    
    @staticmethod
    def get_user_permissions(user: User) -> List[str]:
        """Obtiene permisos del usuario."""
        return AccessService.get_user_function_ids(user)

# apps/pipeline/services.py - Vocabulario ETL

class ETLMonitoringService:
    """
    Servicio de monitoreo ETL con vocabulario consistente.
    
    Usa:
    - check_* para VERIFICAR estado
    - get_* para OBTENER información
    """
    
    # ✅ Consistente
    @staticmethod
    def check_etl_status() -> str:
        """Verifica estado del ETL."""
        last_execution = JobExecutionLog.objects.last()
        return last_execution.status
    
    @staticmethod
    def get_last_execution() -> JobExecutionLog:
        """Obtiene última ejecución."""
        return JobExecutionLog.objects.order_by('-start_time').first()
    
    @staticmethod
    def get_execution_history(days: int = 7) -> List[JobExecutionLog]:
        """Obtiene historial de ejecuciones."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return list(JobExecutionLog.objects.filter(
            start_time__gte=cutoff_date
        ))
```

**VOCABULARIO OFICIAL IACT:**

| Concepto | Palabra | Ejemplo |
|----------|---------|---------|
| Obtener datos | `get_*` | `get_report_data()` |
| Crear/Generar | `generate_*` | `generate_excel()` |
| Verificar reglas | `validate_*` | `validate_date_range()` |
| Comprobar estado | `check_*` | `check_etl_status()` |
| Procesar/Transformar | `process_*` | `process_call_records()` |
| Calcular | `calculate_*` | `calculate_metrics()` |
| Crear registro | `create_*` | `create_report()` |
| Actualizar | `update_*` | `update_status()` |
| Eliminar | `delete_*` | `delete_report()` |

---

<a name="9-architecture-reveals-intent"></a>
### **9. ARCHITECTURE REVEALS INTENT**

**Clean Architecture Principle**: _"La arquitectura debe gritar el propósito del sistema, no el framework usado."_

**Aplicación**: La estructura del proyecto debe comunicar QUÉ hace el sistema, no CON QUÉ está hecho.

**Ejemplos Generales:**

```
# ❌ INCORRECTO - Estructura framework-céntrica
project/
├── models/
├── views/
├── controllers/
└── templates/
# No se ve QUÉ hace el sistema

# ✅ CORRECTO - Estructura que revela propósito
project/
├── reports/      → Sistema de REPORTES
├── dashboard/    → Sistema de DASHBOARDS
├── access/       → Control de ACCESO
└── pipeline/     → Pipeline ETL
# Queda claro QUÉ hace
```

**Aplicación IACT (Arquitectura Real):**

```
iact-call-center/
├── apps/
│   ├── access/          → ✅ Control de acceso RBAC
│   ├── authentication/  → ✅ Autenticación usuarios
│   ├── audit/           → ✅ Auditoría de acciones
│   ├── dashboard/       → ✅ Dashboards visualización
│   ├── ivr/             → ✅ Modelos IVR legacy (readonly)
│   ├── pipeline/        → ✅ Monitoreo ETL
│   ├── reports/         → ✅ Generación reportes
│   └── users/           → ✅ Gestión usuarios
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── routers.py       → ✅ Database routing
│
└── docs/
    ├── arquitectura/    → ✅ Diseño del sistema
    ├── analisis/        → ✅ Requisitos
    └── soporte/         → ✅ Referencias (este documento)

# Al ver esta estructura, INMEDIATAMENTE se entiende:
# - Es un sistema de Call Center
# - Tiene reportes y dashboards
# - Tiene pipeline ETL
# - Tiene control de acceso robusto
# - Lee de IVR legacy

# NO se ve "Django" hasta entrar en los archivos
# La arquitectura "grita" el DOMINIO, no el framework
```

**Estructura de apps/ detallada:**

```python
# apps/reports/  (ejemplo)
reports/
├── __init__.py
├── models.py           → Report, ReportConfiguration
├── services.py         → ReportService (lógica negocio)
├── views.py            → ReportViewSet (API)
├── serializers.py      → ReportSerializer
├── urls.py             → /api/v1/reports/
├── permissions.py      → reports.view, reports.export
└── tests/
    ├── test_services.py
    └── test_views.py

# Al ver "services.py", queda claro que hay SEPARACIÓN de capas
# Al ver "permissions.py", queda claro que hay RBAC
# La estructura REVELA la arquitectura Clean
```

---

<a name="10-frameworks-are-plugins"></a>
### **10. FRAMEWORKS ARE PLUGINS**

**Clean Architecture Principle**: _"Los frameworks son detalles. El negocio no debe depender del framework; el framework debe enchufarse al negocio."_

**Aplicación**: La lógica de negocio debe ser independiente del framework (Django).

**Aplicación IACT (Arquitectura Real):**

```python
# apps/reports/services.py

# ✅ CORRECTO - Lógica de negocio SIN dependencia de Django

from datetime import date
from typing import Dict, List, Optional

class ReportService:
    """
    Servicio de reportes.
    
    NOTA: Esta clase NO importa nada de Django.
    Puede testearse sin Django, sin DB, sin web.
    """
    
    @staticmethod
    def calculate_abandonment_rate(
        total_calls: int,
        abandoned_calls: int
    ) -> float:
        """
        Calcula tasa de abandono.
        
        Lógica pura de negocio:
        - NO usa Django
        - NO usa DB directamente
        - Testeable con pytest simple
        """
        if total_calls == 0:
            return 0.0
        
        return round((abandoned_calls / total_calls) * 100, 2)
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> None:
        """
        Valida rango de fechas (CNST-006).
        
        Lógica pura:
        - Sin Django
        - Sin ORM
        - Solo Python estándar
        """
        if end_date < start_date:
            raise ValueError("Fecha fin debe ser >= fecha inicio")
        
        max_days = 730  # CNST-006
        date_range = (end_date - start_date).days
        
        if date_range > max_days:
            raise ValueError(
                f"Rango máximo: {max_days} días. "
                f"Solicitado: {date_range} días"
            )
    
    @staticmethod
    def aggregate_metrics(records: List[Dict]) -> Dict[str, int]:
        """
        Agrega métricas de lista de records.
        
        Input: Lista de dicts (puede venir de Django, API, archivo)
        Output: Dict con métricas
        
        NO depende de Django ORM
        """
        total_calls = sum(r.get('total_llamadas', 0) for r in records)
        unique_clients = len(set(r.get('telefono_origen') for r in records))
        
        return {
            'total_calls': total_calls,
            'unique_clients': unique_clients
        }

# apps/reports/views.py

# ✅ CORRECTO - Django como PLUGIN

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.reports.services import ReportService  # ← Importa servicio

class ReportViewSet(viewsets.ViewSet):
    """
    API ViewSet.
    
    Esta capa SÍ depende de Django (DRF).
    Pero DELEGA lógica a ReportService (independiente).
    
    Django es un PLUGIN que se conecta al negocio.
    """
    
    @action(detail=False, methods=['post'])
    def calculate_metrics(self, request):
        """Endpoint que USA el servicio."""
        
        # 1. Extract datos del request (Django)
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        # 2. Validar con servicio (NO Django)
        try:
            ReportService.validate_date_range(start_date, end_date)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Obtener datos (Django ORM)
        from apps.ivr.models import ReporteTrimestral
        records = list(ReporteTrimestral.objects.filter(
            fecha__gte=start_date,
            fecha__lte=end_date
        ).values())
        
        # 4. Procesar con servicio (NO Django)
        metrics = ReportService.aggregate_metrics(records)
        
        # 5. Retornar (Django)
        return Response(metrics)
```

**Beneficios en IACT:**

```python
# Test de lógica SIN Django
def test_calculate_abandonment_rate():
    """Test unitario puro - Sin Django, sin DB."""
    rate = ReportService.calculate_abandonment_rate(
        total_calls=100,
        abandoned_calls=15
    )
    assert rate == 15.0  # ✅ Pasa

# Test de lógica SIN Django
def test_validate_date_range_exceeds_limit():
    """Test unitario puro - Sin Django."""
    start = date(2025, 1, 1)
    end = date(2027, 1, 1)  # > 730 días
    
    with pytest.raises(ValueError):
        ReportService.validate_date_range(start, end)  # ✅ Pasa
```

**Si algún día cambiamos Django → FastAPI:**
- `ReportService` NO cambia (lógica de negocio)
- Solo cambia `ReportViewSet` (capa de framework)

---

<a name="11-dependencies-point-inward"></a>
### **11. DEPENDENCIES POINT INWARD**

**Clean Architecture Principle**: _"Las dependencias apuntan hacia adentro. El código de negocio NO conoce el framework."_

**Aplicación IACT (Arquitectura Real):**

```
CAPAS DE LA ARQUITECTURA IACT:

┌─────────────────────────────────────────────────┐
│ CAPA 4: FRAMEWORK (Django/DRF)                  │ ← Más externa
│ - ViewSets, Serializers, Permissions            │
│ - Depende de: CAPA 3                            │
├─────────────────────────────────────────────────┤
│ CAPA 3: APPLICATION SERVICES                    │
│ - ReportService, DashboardService, AccessService│
│ - Depende de: CAPA 2                            │
│ - NO depende de: Django                         │
├─────────────────────────────────────────────────┤
│ CAPA 2: DOMAIN MODELS                           │
│ - Report, Dashboard, Function, Agrupador        │
│ - Depende de: CAPA 1                            │
│ - NO depende de: Django                         │
├─────────────────────────────────────────────────┤
│ CAPA 1: ENTITIES (Lógica pura)                  │ ← Más interna
│ - calculate_metrics(), validate_date_range()    │
│ - NO depende de NADA                            │
└─────────────────────────────────────────────────┘

REGLA: Las flechas van HACIA ADENTRO
❌ CAPA 1 NO puede importar de CAPA 2, 3, 4
❌ CAPA 2 NO puede importar de CAPA 3, 4
✅ CAPA 4 SÍ puede importar de CAPA 3, 2, 1
```

**Ejemplo IACT:**

```python
# ❌ INCORRECTO - Dependencia invertida

# apps/reports/services.py (CAPA 3)
from rest_framework.response import Response  # ❌ Django en servicio!

class ReportService:
    @staticmethod
    def get_data(...):
        # ❌ Servicio NO debe conocer Django Response
        return Response({'data': []})

# ✅ CORRECTO - Dependencias apuntan hacia adentro

# apps/reports/services.py (CAPA 3)
# NO importa nada de Django

class ReportService:
    @staticmethod
    def get_report_data(...) -> Dict:
        """Retorna Dict puro (NO Response de Django)."""
        return {'data': [], 'count': 0}

# apps/reports/views.py (CAPA 4)
from rest_framework.response import Response
from apps.reports.services import ReportService  # ← Apunta hacia adentro

class ReportViewSet:
    def get_data(self, request):
        # Servicio retorna Dict
        data = ReportService.get_report_data(...)
        
        # ViewSet convierte a Response (Django)
        return Response(data)
```

**Arquitectura real en IACT:**

```python
# apps/access/services.py (CAPA 3)

class AccessService:
    """
    Servicio de acceso.
    
    NO importa:
    - rest_framework
    - django.http
    - Nada de la web layer
    
    SÍ importa:
    - apps.access.models (CAPA 2)
    - typing, datetime (stdlib)
    """
    
    @staticmethod
    def user_has_function(user_id: int, function_id: str) -> bool:
        """
        Verifica si usuario tiene función.
        
        Input: int, str (tipos primitivos)
        Output: bool (tipo primitivo)
        
        NO retorna QuerySet, Response, etc.
        """
        from apps.access.models import Agrupador, Function
        
        # Lógica pura usando models (CAPA 2)
        agrupadores = Agrupador.objects.filter(
            users__id=user_id
        )
        
        for agrupador in agrupadores:
            if agrupador.functions.filter(
                function_id=function_id
            ).exists():
                return True
        
        return False

# apps/access/views.py (CAPA 4)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.access.services import AccessService  # ← Hacia adentro

@api_view(['POST'])
def check_permission(request):
    """Endpoint que USA el servicio."""
    
    # Extract (Django)
    user_id = request.user.id
    function_id = request.data.get('function_id')
    
    # Business logic (Servicio - NO Django)
    has_permission = AccessService.user_has_function(
        user_id=user_id,
        function_id=function_id
    )
    
    # Response (Django)
    return Response({'has_permission': has_permission})
```

---

<a name="12-use-cases-drive-architecture"></a>
### **12. USE CASES DRIVE ARCHITECTURE**

**Clean Architecture Principle**: _"Los casos de uso son el corazón. La arquitectura debe estar organizada por casos de uso, no por frameworks."_

**Aplicación IACT (Arquitectura Real):**

```python
# apps/reports/ organizado por CASOS DE USO

reports/
├── use_cases/                    # ← Casos de uso explícitos
│   ├── __init__.py
│   ├── generate_report.py        # UC-001: Generar reporte
│   ├── export_to_excel.py        # UC-002: Exportar a Excel
│   ├── validate_filters.py       # UC-003: Validar filtros
│   └── get_report_data.py        # UC-004: Obtener datos
│
├── services.py                   # ← Orquesta use cases
├── models.py
├── views.py
└── serializers.py

# apps/reports/use_cases/generate_report.py

from dataclasses import dataclass
from datetime import date
from typing import Dict, Optional

@dataclass
class GenerateReportRequest:
    """Input del caso de uso."""
    start_date: date
    end_date: date
    trimestre: str
    did: Optional[str] = None

@dataclass
class GenerateReportResponse:
    """Output del caso de uso."""
    report_id: str
    status: str
    record_count: int
    data: Dict

class GenerateReportUseCase:
    """
    UC-001: Generar Reporte.
    
    Este caso de uso:
    1. Valida fechas (CNST-006)
    2. Verifica datos ETL disponibles
    3. Obtiene datos de MariaDB
    4. Retorna reporte generado
    
    NO depende de Django.
    """
    
    def execute(self, request: GenerateReportRequest) -> GenerateReportResponse:
        """Ejecuta el caso de uso."""
        
        # 1. Validar fechas
        self._validate_date_range(request.start_date, request.end_date)
        
        # 2. Verificar disponibilidad datos ETL
        self._check_etl_data_available(request.start_date)
        
        # 3. Obtener datos
        data = self._get_report_data(request)
        
        # 4. Retornar response
        return GenerateReportResponse(
            report_id=self._generate_id(),
            status='SUCCESS',
            record_count=len(data),
            data=data
        )
    
    def _validate_date_range(self, start: date, end: date) -> None:
        """Valida CNST-006."""
        if (end - start).days > 730:
            raise ValueError("Rango máximo: 730 días")
    
    def _check_etl_data_available(self, date: date) -> None:
        """Verifica que ETL haya corrido."""
        from apps.pipeline.services import ETLMonitoringService
        
        if not ETLMonitoringService.has_data_for_date(date):
            raise ValueError(f"Sin datos ETL para {date}")
    
    def _get_report_data(self, request: GenerateReportRequest) -> Dict:
        """Obtiene datos del reporte."""
        from apps.ivr.models import ReporteTrimestral
        
        queryset = ReporteTrimestral.objects.filter(
            fecha__gte=request.start_date,
            fecha__lte=request.end_date,
            trimestre=request.trimestre
        )
        
        if request.did:
            queryset = queryset.filter(servicio_800=request.did)
        
        return list(queryset.values())
    
    def _generate_id(self) -> str:
        """Genera ID único."""
        import uuid
        return str(uuid.uuid4())

# apps/reports/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.reports.use_cases.generate_report import (
    GenerateReportUseCase,
    GenerateReportRequest
)

class ReportViewSet(viewsets.ViewSet):
    """API que INVOCA casos de uso."""
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        POST /api/v1/reports/generate/
        
        Este endpoint es un THIN WRAPPER sobre el caso de uso.
        Solo hace:
        1. Parse request (Django)
        2. Invoke use case (Negocio)
        3. Format response (Django)
        """
        
        # 1. Parse (Django)
        use_case_request = GenerateReportRequest(
            start_date=parse_date(request.data['start_date']),
            end_date=parse_date(request.data['end_date']),
            trimestre=request.data['trimestre'],
            did=request.data.get('did')
        )
        
        # 2. Execute (Negocio - NO Django)
        try:
            use_case = GenerateReportUseCase()
            result = use_case.execute(use_case_request)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Format (Django)
        return Response({
            'report_id': result.report_id,
            'status': result.status,
            'count': result.record_count
        }, status=status.HTTP_201_CREATED)
```

**Beneficios:**
- Caso de uso es TESTEABLE sin Django
- Caso de uso es REUTILIZABLE (puede llamarse desde CLI, Celery, etc.)
- La arquitectura GRITA "generar reporte", no "Django view"

---

<a name="13-testability-without-framework"></a>
### **13. TESTABILITY WITHOUT FRAMEWORK**

**Clean Architecture Principle**: _"La lógica de negocio debe ser testeable sin el framework, sin la DB, sin la web."_

**Aplicación IACT (Arquitectura Real):**

```python
# apps/reports/services.py

class ReportService:
    """Servicio testeable SIN Django."""
    
    @staticmethod
    def calculate_metrics(records: List[Dict]) -> Dict:
        """
        Calcula métricas de lista de records.
        
        Testeable con:
        - pytest simple
        - Sin Django
        - Sin DB
        - Sin configuración
        """
        total_calls = sum(r.get('total_llamadas', 0) for r in records)
        unique_menus = len(set(r.get('menu') for r in records if r.get('menu')))
        
        avg_calls_per_menu = (
            total_calls / unique_menus if unique_menus > 0 else 0
        )
        
        return {
            'total_calls': total_calls,
            'unique_menus': unique_menus,
            'avg_per_menu': round(avg_calls_per_menu, 2)
        }

# tests/unit/test_report_service.py

def test_calculate_metrics_with_valid_data():
    """Test PURO - Sin Django, sin DB, sin nada."""
    
    # Arrange
    records = [
        {'total_llamadas': 100, 'menu': 'CREDITOS'},
        {'total_llamadas': 50, 'menu': 'SALDOS'},
        {'total_llamadas': 75, 'menu': 'CREDITOS'},
    ]
    
    # Act
    result = ReportService.calculate_metrics(records)
    
    # Assert
    assert result['total_calls'] == 225
    assert result['unique_menus'] == 2  # CREDITOS, SALDOS
    assert result['avg_per_menu'] == 112.5  # 225 / 2
    
    # ✅ Test corre en MILISEGUNDOS
    # ✅ No necesita DB
    # ✅ No necesita Django
    # ✅ No necesita setup complejo

def test_calculate_metrics_with_empty_records():
    """Test PURO - Caso borde."""
    
    result = ReportService.calculate_metrics([])
    
    assert result['total_calls'] == 0
    assert result['unique_menus'] == 0
    assert result['avg_per_menu'] == 0

def test_calculate_metrics_with_missing_fields():
    """Test PURO - Datos incompletos."""
    
    records = [
        {'total_llamadas': 100},  # Sin 'menu'
        {'menu': 'CREDITOS'},     # Sin 'total_llamadas'
    ]
    
    result = ReportService.calculate_metrics(records)
    
    assert result['total_calls'] == 100
    assert result['unique_menus'] == 1  # Solo cuenta donde hay menu
```

**Contraste con test que REQUIERE Django:**

```python
# tests/integration/test_report_viewset.py

from django.test import TestCase
from rest_framework.test import APIClient
from apps.users.models import User

class ReportViewSetTest(TestCase):
    """
    Test de INTEGRACIÓN - Requiere Django.
    
    Necesita:
    - Django test framework
    - Base de datos de test
    - Fixtures
    - Setup/teardown
    
    Tarda SEGUNDOS en correr.
    """
    
    def setUp(self):
        """Setup complejo."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test',
            password='pass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_generate_report_endpoint(self):
        """Test de endpoint completo."""
        
        response = self.client.post('/api/v1/reports/generate/', {
            'start_date': '2025-01-01',
            'end_date': '2025-01-31',
            'trimestre': 'Q1'
        })
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('report_id', response.data)
```

**Pirámide de tests en IACT:**

```
        ┌─────────────────┐
        │   E2E Tests     │ ← Pocos (lentos, frágiles)
        │   (5%)          │
        ├─────────────────┤
        │ Integration     │ ← Algunos (requieren Django)
        │ Tests (15%)     │
        ├─────────────────┤
        │  Unit Tests     │ ← MUCHOS (rápidos, robustos)
        │   (80%)         │ ← SIN Django, SIN DB
        └─────────────────┘

80% de tests NO necesitan Django porque:
✅ Lógica de negocio está en servicios independientes
✅ Casos de uso son testeables aisladamente
✅ Funciones puras no tienen efectos secundarios
```

---

<a name="14-regla-de-idioma-para-iact"></a>
### **14. REGLA DE IDIOMA PARA IACT**

**Principio Fundamental**: En IACT, código en INGLÉS, comentarios/docs en ESPAÑOL.

**Justificación**:
- Equipo habla español nativamente
- Mejores prácticas de código requieren inglés
- Mantiene consistencia con ecosistema Python/Django

### **14.1 Regla General**

```
┌─────────────────────────────────────────────────────┐
│ CÓDIGO (programación):          Siempre INGLÉS      │
│ COMENTARIOS/DOCUMENTACIÓN:      Siempre ESPAÑOL     │
│ NOMBRES DE DOMINIO:             Depende del contexto│
└─────────────────────────────────────────────────────┘
```

### **14.2 Qué va en INGLÉS**

```python
# ✅ TODO esto en INGLÉS:

# Variables
user_id = 123
report_data = []
total_llamadas = 150

# Funciones
def get_report_data():
    pass

def generate_excel():
    pass

# Clases
class ReportService:
    pass

class DashboardViewSet:
    pass

# Atributos de modelo
class Function(models.Model):
    function_id = models.CharField()
    display_name = models.CharField()
    is_active = models.BooleanField()

# Constantes
MAX_EXPORT_RECORDS = 100000
DEFAULT_TIMEOUT = 30

# URLs
path('reports/', ...)
path('dashboard/metrics/', ...)

# Function IDs (RBAC)
function_id = 'reports.view'
function_id = 'dashboard.export.excel'
```

### **14.3 Qué va en ESPAÑOL**

```python
# ✅ TODO esto en ESPAÑOL:

# Docstrings
def get_report_data():
    """
    Obtiene datos del reporte aplicando filtros.
    
    Args:
        start_date: Fecha de inicio del rango
        end_date: Fecha de fin del rango
    
    Returns:
        Lista de diccionarios con los datos
    
    Raises:
        ValidationError: Si el rango excede 730 días
    """
    pass

# Comentarios inline
# Validar que el rango no exceda CNST-006
if date_range > 730:
    raise ValidationError("Rango excedido")

# Help text (modelos)
function_id = models.CharField(
    help_text="ID único de la función en formato namespace.action"
)

# Verbose name (modelos)
is_active = models.BooleanField(
    verbose_name="Activa",
    help_text="Indica si la función está activa"
)

# Error messages
raise ValidationError("El rango de fechas excede el máximo permitido")

# Logs
logger.info("Iniciando generación de reporte")
logger.error(f"Error al procesar: {error}")

# Meta de modelos
class Meta:
    verbose_name = "Función"
    verbose_name_plural = "Funciones"
```

### **14.4 Casos Especiales**

#### **Choice Fields**

```python
# ✅ CORRECTO - Keys inglés, Labels español

class Report(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),       # Key: inglés, Label: español
        ('PROCESSING', 'Procesando'),
        ('COMPLETED', 'Completado'),
        ('FAILED', 'Fallido')
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Estado",  # ← Español
        help_text="Estado actual del reporte"  # ← Español
    )
```

#### **Function IDs (RBAC) vs Display Names**

```python
# ✅ CORRECTO

# Function ID: INGLÉS (código)
function_id = 'reports.view'
function_id = 'reports.export.excel'
function_id = 'dashboard.view'

# Display Name: ESPAÑOL (UI)
display_name = 've_reportes'
display_name = 'exporta_excel'
display_name = 've_dashboard'
```

### **14.5 Tabla de Decisión Rápida**

```
┌──────────────────────┬─────────┬──────────────────────────┐
│ Elemento             │ Idioma  │ Ejemplo                  │
├──────────────────────┼─────────┼──────────────────────────┤
│ Variables            │ Inglés  │ user_id, report_data     │
│ Funciones            │ Inglés  │ get_data, generate_excel │
│ Clases               │ Inglés  │ ReportService, User      │
│ Atributos modelo     │ Inglés  │ function_id, is_active   │
│ URLs                 │ Inglés  │ /reports/, /dashboard/   │
│ Constantes           │ Inglés  │ MAX_RECORDS              │
├──────────────────────┼─────────┼──────────────────────────┤
│ Docstrings           │ Español │ """Calcula métricas."""  │
│ Comentarios inline   │ Español │ # Validar CNST-007       │
│ Help text            │ Español │ help_text="ID único"     │
│ Verbose name         │ Español │ verbose_name="Usuario"   │
│ Error messages       │ Español │ "Límite excedido"        │
├──────────────────────┼─────────┼──────────────────────────┤
│ Function ID (RBAC)   │ Inglés  │ reports.view             │
│ Display name (UI)    │ Español │ ve_reportes              │
│ Choice keys          │ Inglés  │ PENDING                  │
│ Choice labels        │ Español │ 'Pendiente'              │
└──────────────────────┴─────────┴──────────────────────────┘
```

### **14.6 Ejemplo Completo**

```python
# apps/access/models.py

from django.db import models

class Function(models.Model):
    """
    Función atómica del sistema RBAC.
    
    Representa una capacidad específica que puede ser asignada
    a usuarios a través de agrupadores.
    """  # ← Docstring: ESPAÑOL
    
    # Campos: INGLÉS
    function_id = models.CharField(
        max_length=100,
        primary_key=True,
        help_text="ID único en formato namespace.action"  # ← ESPAÑOL
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Nombre interno de la función"  # ← ESPAÑOL
    )
    
    display_name = models.CharField(
        max_length=200,
        verbose_name="Nombre a mostrar",  # ← ESPAÑOL
        help_text="Nombre legible para la interfaz"  # ← ESPAÑOL
    )
    
    module = models.CharField(
        max_length=50,
        choices=[  # Keys: INGLÉS, Labels: ESPAÑOL
            ('reports', 'Reportes'),
            ('dashboard', 'Dashboards'),
            ('access', 'Control de Acceso'),
            ('users', 'Usuarios'),
        ],
        help_text="Módulo al que pertenece"  # ← ESPAÑOL
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa",  # ← ESPAÑOL
        help_text="Si la función está activa"  # ← ESPAÑOL
    )
    
    class Meta:
        db_table = 'access_functions'  # ← INGLÉS
        verbose_name = 'Función'  # ← ESPAÑOL
        verbose_name_plural = 'Funciones'  # ← ESPAÑOL
        ordering = ['module', 'function_id']
    
    def __str__(self):
        """Representación string de la función."""  # ← ESPAÑOL
        return f"{self.function_id} - {self.display_name}"
    
    def is_in_module(self, module_name: str) -> bool:
        """
        Verifica si la función pertenece a un módulo.
        
        Args:
            module_name: Nombre del módulo a verificar
        
        Returns:
            True si pertenece al módulo
        """  # ← ESPAÑOL
        return self.module == module_name
```

### **14.7 Checklist de Verificación**

```
ANTES DE COMMIT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☐ Nombres de variables: INGLÉS
☐ Nombres de funciones: INGLÉS
☐ Nombres de clases: INGLÉS
☐ Atributos de modelos: INGLÉS
☐ Constantes: INGLÉS
☐ URLs/rutas: INGLÉS

☐ Docstrings: ESPAÑOL
☐ Comentarios inline: ESPAÑOL
☐ Help text: ESPAÑOL
☐ Verbose name: ESPAÑOL
☐ Error messages: ESPAÑOL
☐ Logs: ESPAÑOL

☐ Function IDs (RBAC): INGLÉS (namespace.action)
☐ Display names: ESPAÑOL
☐ Choice keys: INGLÉS
☐ Choice labels: ESPAÑOL
```

---

**FIN DE PARTE 1/5**

**Continúa en:** CLEAN_CODE_NAMING_PRINCIPLES_v2_3_0_PARTE_2.md

---

**Resumen Parte 1:**
- ✅ 13 principios fundamentales de Clean Code
- ✅ Regla de idioma completa (Sección 14)
- ✅ Ejemplos actualizados con arquitectura real IACT
- ✅ Modelos: HistoricoT1, ReporteTrimestral, JobExecutionLog
- ✅ Apps: ivr, reports, dashboard, pipeline, access
- ✅ Tabla de decisión rápida
- ✅ Checklist de verificación

**Próxima parte:** ⭐ **NUEVA Sección 15: Principio de Equilibrio** ⭐ + DRF básico (secciones 16-18)
