---
version: 3.0.0
date: 2026-01-18
project: IACT (Sistema Call Center)
base: Clean Code (Robert Martin) + Clean Architecture
changelog: |
  v3.0.0 - PARTE 1/5 - Arquitectura corregida
  - CAMBIO MAYOR: Eliminadas referencias a apps/dashboard/ (no existe)
  - Arquitectura actualizada con apps reales del sistema
  - Mantiene principios 1-14 (válidos)
  - apps/core/ documentado correctamente (solo abstractos)
partes: 1/5
estado: completo
revision: v3.0.0 (arquitectura correcta)
replaces: CLEAN_CODE_NAMING_PRINCIPLES_v2_3_1_PARTE_1.md
---

# CLEAN CODE NAMING PRINCIPLES v3.0.0

**PARTE 1/5: PRINCIPIOS FUNDAMENTALES**

---

## 📋 CONTENIDO DE ESTA PARTE

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

---

## ⚠️ CAMBIOS EN v3.0.0

```
ARQUITECTURA CORREGIDA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ v2.3.1 (INCORRECTO):          ✅ v3.0.0 (CORRECTO):
├─ apps/dashboard/              ├─ (NO EXISTE - eliminado)
├─ apps/core/ (deprecado)       ├─ apps/core/ (SOLO abstractos)
└─ apps/utils/ (con clases)     └─ apps/utils/ (SOLO funciones)

APPS REALES IACT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ apps/access/        Control de acceso RBAC
✅ apps/audit/         Auditoría de acciones
✅ apps/authentication/ Autenticación usuarios
✅ apps/core/          Modelos abstractos base
✅ apps/ivr_legacy/    Adaptador datos IVR
✅ apps/pipeline/      Monitoreo ETL
✅ apps/reports/       Reportes tabulares
✅ apps/users/         Gestión usuarios
✅ apps/utils/         Funciones helper

MODELOS CORREGIDOS (desde v2.3.1):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CallRecord (antes HistoricoT1)
✅ QuarterlyReport (antes ReporteTrimestral)
✅ IVRMenu (antes Menu2)
✅ AbandonedCall (antes LlamadasAbandonadas)
✅ UniqueClient (antes ClientesUnicos)
✅ AverageClientPerMenu (antes PromedioClientesMenu)
```

---

<a name="1-usar-nombres-que-revelen-intenciones"></a>
## 1. USAR NOMBRES QUE REVELEN INTENCIONES

**Principio**: El nombre de una variable, función o clase debe responder a tres preguntas:
1. ¿Por qué existe?
2. ¿Qué hace?
3. ¿Cómo se usa?

Si un nombre requiere un comentario, entonces no revela su intención.

---

### 1.1 Variables

```python
# ❌ INCORRECTO - No revela intención
d = 10  # días transcurridos
t = datetime.now()
lst = []

# ✅ CORRECTO - Revela intención
elapsed_days = 10
current_timestamp = datetime.now()
active_users = []
```

**En IACT:**
```python
# ❌ INCORRECTO
from apps.ivr.models import HistoricoT1  # ❌ Nombre español + número

h = HistoricoT1.objects.filter(did='19020084')  # ❌ ¿Qué es 'h'?


# ✅ CORRECTO
from apps.ivr.models import CallRecord  # ✅ Inglés, auto-documentado

call_records = CallRecord.objects.filter(did='19020084')
# ✅ Claro: registros de llamadas del DID 19020084
```

---

### 1.2 Funciones

```python
# ❌ INCORRECTO - Nombre genérico
def get_data():
    """Obtiene datos."""  # ← Comentario necesario = mal nombre
    pass

# ✅ CORRECTO - Nombre específico
def get_quarterly_report_data(quarter: str, did: str):
    """
    Obtiene datos de reporte trimestral.
    
    Args:
        quarter: Trimestre (Q1, Q2, Q3, Q4)
        did: DID a consultar
    """  # ← Español
    pass
```

**En IACT:**
```python
# apps/reports/services.py

# ❌ INCORRECTO
def get_report(q, d):  # ❌ ¿Qué reporte? ¿Qué son q y d?
    pass

# ✅ CORRECTO
def get_abandoned_calls_report(quarter: str, did: str):
    """
    Obtiene reporte de llamadas abandonadas.
    
    Consulta tabla: tbl_reporte_llamadas_abandonadas
    
    Args:
        quarter: Trimestre (Q1, Q2, Q3, Q4)
        did: DID a consultar
        
    Returns:
        QuerySet de AbandonedCall
    """  # ← Español
    
    from apps.ivr.models import AbandonedCall
    
    return AbandonedCall.objects.filter(
        quarter=quarter,
        did=did
    )
```

---

### 1.3 Clases

```python
# ❌ INCORRECTO - Nombre genérico
class Manager:  # ❌ ¿Manager de qué?
    pass

class Data:  # ❌ ¿Qué datos?
    pass

# ✅ CORRECTO - Nombres específicos
class ReportService:  # ✅ Servicio de reportes
    """Gestión de lógica de negocio para reportes."""
    pass

class AccessService:  # ✅ Servicio de acceso RBAC
    """Gestión de funciones y permisos."""
    pass
```

**En IACT:**
```python
# apps/ivr/models.py

# ❌ INCORRECTO
class HistoricoT1(models.Model):  # ❌ Español + número "T1"
    """Tabla histórico T1."""  # ❌ ¿Qué es T1?
    pass

class Menu2(models.Model):  # ❌ ¿Por qué "2"?
    pass


# ✅ CORRECTO
class CallRecord(models.Model):
    """
    Registro histórico de llamadas del IVR.
    
    Mapea a tabla: historico_t1 (creada por ETL)
    
    Cada registro representa una llamada procesada
    por el sistema IVR con su metadata completa.
    """  # ← Español
    
    call_id = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='id_llamada',
        verbose_name="ID de llamada"
    )
    
    did = models.CharField(
        max_length=20,
        db_column='did',
        verbose_name="DID"
    )
    
    menu = models.CharField(
        max_length=100,
        db_column='menu',
        verbose_name="Menú navegado"
    )
    
    timestamp = models.DateTimeField(
        db_column='fecha_hora',
        verbose_name="Fecha y hora"
    )
    
    class Meta:
        db_table = 'historico_t1'  # ← Tabla real en MariaDB
        managed = False  # ← Django NO maneja (la crea ETL)
        verbose_name = 'Registro de llamada'
        verbose_name_plural = 'Registros de llamadas'
    
    def __str__(self):
        return f"Call {self.call_id}"


class IVRMenu(models.Model):
    """
    Menú del sistema IVR.
    
    Mapea a tabla: menu2 (creada por ETL)
    
    Contiene configuración de menús disponibles
    en el sistema IVR para navegación de usuarios.
    """  # ← Español
    
    menu_id = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='id_menu',
        verbose_name="ID de menú"
    )
    
    name = models.CharField(
        max_length=200,
        db_column='nombre',
        verbose_name="Nombre"
    )
    
    description = models.TextField(
        db_column='descripcion',
        verbose_name="Descripción"
    )
    
    class Meta:
        db_table = 'menu2'  # ← Tabla real en MariaDB
        managed = False
        verbose_name = 'Menú IVR'
        verbose_name_plural = 'Menús IVR'
    
    def __str__(self):
        return self.name
```

---

<a name="2-evitar-la-desinformacion"></a>
## 2. EVITAR LA DESINFORMACIÓN

**Principio**: No uses nombres que puedan confundir o dar información falsa sobre lo que representa.

---

### 2.1 No Usar Nombres Engañosos

```python
# ❌ INCORRECTO - Engañoso
user_list = {'id': 1, 'name': 'Juan'}  # ❌ Es un dict, no una lista

# ✅ CORRECTO
user_dict = {'id': 1, 'name': 'Juan'}
# O mejor aún:
user_data = {'id': 1, 'name': 'Juan'}
```

---

### 2.2 Evitar Variaciones Sutiles

```python
# ❌ INCORRECTO - Difícil de distinguir
report_controller = ReportController()
report_controler = ReportControler()  # ❌ Typo fácil de no detectar

# ✅ CORRECTO - Nombres distintivos
report_controller = ReportController()
report_service = ReportService()
```

**En IACT:**
```python
# ❌ INCORRECTO - Nombres similares confusos
from apps.ivr.models import ReporteTrimestral  # ❌ Español
from apps.reports.models import TrimesterReport  # ❌ Mezclado

# ✅ CORRECTO - Nombres consistentes
from apps.ivr.models import QuarterlyReport  # ✅ Inglés
from apps.reports.models import Report  # ✅ Consistente
```

---

### 2.3 No Usar Números Arbitrarios

```python
# ❌ INCORRECTO - Números sin significado
class Menu2(models.Model):  # ❌ ¿Por qué "2"?
    pass

class HistoricoT1(models.Model):  # ❌ ¿Qué significa "T1"?
    pass


# ✅ CORRECTO - Nombres descriptivos
class IVRMenu(models.Model):  # ✅ Claro: menú del IVR
    """Menú del sistema IVR."""
    pass

class CallRecord(models.Model):  # ✅ Claro: registro de llamada
    """Registro histórico de llamadas."""
    pass
```

---

<a name="3-realizar-distinciones-con-sentido"></a>
## 3. REALIZAR DISTINCIONES CON SENTIDO

**Principio**: Las distinciones en nombres deben ser significativas. No uses sufijos como "Info", "Data", "Object" sin razón.

---

### 3.1 Evitar Sufijos Sin Sentido

```python
# ❌ INCORRECTO - Sufijos redundantes
user_object = User()  # ❌ "object" es redundante
user_data = User()    # ❌ "data" no agrega información
user_info = User()    # ❌ "info" no agrega información

# ✅ CORRECTO
user = User()  # ✅ Simple y claro
```

---

### 3.2 Distinciones Significativas

```python
# ✅ CORRECTO - Cada nombre tiene propósito claro
user = User.objects.get(id=1)           # Instancia de User
user_dict = model_to_dict(user)         # Diccionario con datos
user_serializer = UserSerializer(user)  # Serializer de DRF
user_json = user_serializer.data        # JSON serializado
```

**En IACT:**
```python
# apps/reports/services.py

# ✅ CORRECTO - Distinciones claras
class ReportService:
    """
    Servicio de lógica de negocio para reportes.
    
    Responsabilidades:
    - Obtener datos de reportes
    - Validar parámetros
    - Aplicar reglas de negocio
    """  # ← Español
    
    @staticmethod
    def get_quarterly_report(quarter: str, did: str):
        """Obtiene reporte trimestral."""
        # Retorna QuerySet
        pass
    
    @staticmethod
    def export_quarterly_report_to_excel(quarter: str, did: str):
        """Exporta reporte trimestral a Excel."""
        # Retorna archivo Excel
        pass


class AccessService:
    """
    Servicio de lógica de negocio para RBAC.
    
    Responsabilidades:
    - Validar permisos
    - Asignar funciones
    - Verificar SOD
    """  # ← Español
    
    @staticmethod
    def get_user_functions(user_id: int):
        """Obtiene funciones del usuario."""
        # Retorna QuerySet de Function
        pass
```

---

<a name="4-usar-nombres-que-se-puedan-pronunciar"></a>
## 4. USAR NOMBRES QUE SE PUEDAN PRONUNCIAR

**Principio**: Si no puedes pronunciar un nombre, no puedes discutirlo sin sonar ridículo.

---

### 4.1 Nombres Pronunciables

```python
# ❌ INCORRECTO - Impronunciables
genymdhms = datetime.now()  # ❌ ¿Cómo se pronuncia?
modymdhms = datetime.now()  # ❌ Trabalenguas

# ✅ CORRECTO - Pronunciables
generation_timestamp = datetime.now()  # ✅ Fácil de decir
modification_timestamp = datetime.now()  # ✅ Claro
```

**En IACT:**
```python
# ❌ INCORRECTO - Difíciles de pronunciar
from apps.ivr.models import HistoricoT1  # ❌ "Histórico Te-uno"
from apps.ivr.models import ReporteTrimestral  # ❌ Mezclado

# Conversación:
# Dev 1: "Necesito el Histórico Te-uno"
# Dev 2: "¿Te-uno? ¿Qué es eso?"


# ✅ CORRECTO - Fáciles de pronunciar
from apps.ivr.models import CallRecord  # ✅ "Call Record"
from apps.ivr.models import QuarterlyReport  # ✅ "Quarterly Report"

# Conversación:
# Dev 1: "Necesito los Call Records del Q1"
# Dev 2: "Claro, los registros de llamadas del primer trimestre"
```

---

<a name="5-usar-nombres-que-se-puedan-buscar"></a>
## 5. USAR NOMBRES QUE SE PUEDAN BUSCAR

**Principio**: Nombres de una sola letra o números son difíciles de buscar. Usa constantes nombradas.

---

### 5.1 Constantes vs Números Mágicos

```python
# ❌ INCORRECTO - Números mágicos
if record_count > 100000:  # ❌ ¿Por qué 100,000?
    raise Exception("Demasiados registros")

# ✅ CORRECTO - Constantes nombradas
MAX_EXPORT_RECORDS = 100000  # CNST-007

if record_count > MAX_EXPORT_RECORDS:
    raise ExportLimitExceeded(record_count)
```

**En IACT:**
```python
# apps/reports/services.py

# ✅ CORRECTO - Constantes buscables
MAX_EXPORT_RECORDS = 100000  # CNST-007
MAX_DATE_RANGE_DAYS = 730    # CNST-006 (2 años)
DEFAULT_PAGE_SIZE = 25


class ReportService:
    """Servicio de reportes."""  # ← Español
    
    @staticmethod
    def validate_export_limit(record_count: int):
        """
        Valida límite de exportación.
        
        CNST-007: Máximo 100,000 registros por exportación.
        """  # ← Español
        
        if record_count > MAX_EXPORT_RECORDS:
            raise ExportLimitExceeded(
                f"Máximo {MAX_EXPORT_RECORDS:,} registros. "
                f"Intentaste exportar {record_count:,}"
            )
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        """
        Valida rango de fechas.
        
        CNST-006: Rango máximo de 2 años (730 días).
        """  # ← Español
        
        days_diff = (end_date - start_date).days
        
        if days_diff > MAX_DATE_RANGE_DAYS:
            raise ValidationError(
                f"Rango máximo {MAX_DATE_RANGE_DAYS} días (2 años). "
                f"Rango solicitado: {days_diff} días"
            )
```

---

<a name="6-evitar-codificaciones"></a>
## 6. EVITAR CODIFICACIONES

**Principio**: No uses prefijos que indiquen tipo o alcance. El código moderno no necesita notación húngara.

---

### 6.1 No Notación Húngara

```python
# ❌ INCORRECTO - Notación húngara
strName = "Juan"      # ❌ Prefijo de tipo
intCount = 10         # ❌ Prefijo de tipo
lstUsers = []         # ❌ Prefijo de tipo

# ✅ CORRECTO
name = "Juan"         # ✅ Tipo inferido
count = 10            # ✅ Tipo inferido
users = []            # ✅ Tipo inferido
```

---

### 6.2 No Prefijos de Alcance

```python
# ❌ INCORRECTO - Prefijos de alcance
class User:
    m_name = ""       # ❌ m_ para member
    m_email = ""      # ❌ Innecesario

# ✅ CORRECTO
class User:
    name = ""         # ✅ Sin prefijo
    email = ""        # ✅ Claro por contexto
```

---

### 6.3 No Sufijos Numéricos

```python
# ❌ INCORRECTO - Números arbitrarios
class HistoricoT1(models.Model):  # ❌ ¿Qué es "T1"?
    pass

class Menu2(models.Model):  # ❌ ¿Por qué "2"?
    pass


# ✅ CORRECTO - Nombres descriptivos
class CallRecord(models.Model):  # ✅ Auto-documentado
    """
    Registro de llamada del IVR.
    
    Mapea a: historico_t1
    """  # ← Español
    
    class Meta:
        db_table = 'historico_t1'
        managed = False


class IVRMenu(models.Model):  # ✅ Claro
    """
    Menú del sistema IVR.
    
    Mapea a: menu2
    """  # ← Español
    
    class Meta:
        db_table = 'menu2'
        managed = False
```

---

<a name="7-evitar-asignaciones-mentales"></a>
## 7. EVITAR ASIGNACIONES MENTALES

**Principio**: Los lectores no deberían traducir mentalmente tus nombres a otros que ya conocen.

---

### 7.1 No Variables de Una Letra (excepto loops)

```python
# ❌ INCORRECTO - Variables crípticas
r = requests.get(url)  # ❌ ¿Qué es 'r'?
d = {'name': 'Juan'}   # ❌ ¿Qué es 'd'?

# ✅ CORRECTO
response = requests.get(url)  # ✅ Claro
user_data = {'name': 'Juan'}  # ✅ Descriptivo

# ✅ EXCEPCIÓN: Loops simples
for i in range(10):  # ✅ OK en loops
    print(i)

for user in users:  # ✅ Mejor aún
    print(user.name)
```

**En IACT:**
```python
# apps/reports/services.py

# ❌ INCORRECTO
def get_report(q, d, m):  # ❌ ¿Qué son q, d, m?
    r = CallRecord.objects.filter(quarter=q, did=d, menu=m)
    return r


# ✅ CORRECTO
def get_quarterly_call_records(
    quarter: str,
    did: str,
    menu: str = None
):
    """
    Obtiene registros de llamadas trimestrales.
    
    Args:
        quarter: Trimestre (Q1, Q2, Q3, Q4)
        did: DID a consultar
        menu: Menú a filtrar (opcional)
        
    Returns:
        QuerySet de CallRecord
    """  # ← Español
    
    queryset = CallRecord.objects.filter(
        quarter=quarter,
        did=did
    )
    
    if menu:
        queryset = queryset.filter(menu=menu)
    
    return queryset
```

---

<a name="8-una-palabra-por-concepto"></a>
## 8. UNA PALABRA POR CONCEPTO

**Principio**: Usa una palabra consistente para cada concepto abstracto. No uses "get", "fetch", "retrieve" indistintamente.

---

### 8.1 Consistencia en Verbos

```python
# ❌ INCORRECTO - Verbos inconsistentes
def get_user(user_id):
    pass

def fetch_report(report_id):  # ❌ ¿Por qué "fetch" y no "get"?
    pass

def retrieve_function(function_id):  # ❌ ¿Por qué "retrieve"?
    pass


# ✅ CORRECTO - Verbo consistente
def get_user(user_id):
    """Obtiene usuario por ID."""
    pass

def get_report(report_id):
    """Obtiene reporte por ID."""
    pass

def get_function(function_id):
    """Obtiene función por ID."""
    pass
```

**En IACT:**
```python
# apps/reports/services.py

class ReportService:
    """Servicio de reportes."""  # ← Español
    
    # ✅ CORRECTO - "get" consistente
    @staticmethod
    def get_quarterly_report(quarter: str, did: str):
        """Obtiene reporte trimestral."""
        pass
    
    @staticmethod
    def get_abandoned_calls_report(quarter: str, did: str):
        """Obtiene reporte de llamadas abandonadas."""
        pass
    
    @staticmethod
    def get_unique_clients_report(quarter: str, did: str):
        """Obtiene reporte de clientes únicos."""
        pass


# apps/access/services.py

class AccessService:
    """Servicio de RBAC."""  # ← Español
    
    # ✅ CORRECTO - "get" consistente
    @staticmethod
    def get_user_functions(user_id: int):
        """Obtiene funciones del usuario."""
        pass
    
    @staticmethod
    def get_function_permissions(function_id: int):
        """Obtiene permisos de la función."""
        pass
```

---

<a name="9-architecture-reveals-intent"></a>
## 9. ARCHITECTURE REVEALS INTENT

**Principio**: La arquitectura debe hacer evidente la intención del sistema, no los frameworks usados.

---

### 9.1 Arquitectura por Intención de Negocio

```
❌ INCORRECTO - Arquitectura por framework:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

myproject/
├── models/          # ← Organizado por capa técnica
├── views/
├── serializers/
└── services/

No revela qué hace el sistema. ¿Es un e-commerce? ¿Un CRM?


✅ CORRECTO - Arquitectura por dominio (IACT REAL):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

callcentersite/apps/
├── access/          # Control de acceso RBAC
├── audit/           # Auditoría de acciones
├── authentication/  # Autenticación de usuarios
├── core/            # Modelos abstractos base
├── ivr_legacy/      # Adaptador a datos IVR
├── pipeline/        # Monitoreo de ETL
├── reports/         # Reportes tabulares
├── users/           # Gestión de usuarios
└── utils/           # Funciones helper

Revela inmediatamente: sistema de call center con RBAC,
reportes, auditoría y adaptador a IVR.
```

**En IACT:**
```python
# ✅ CORRECTO - Arquitectura revela intención

apps/
├── access/           # Sistema de control de acceso (RBAC)
│   ├── models.py     # Function, UserFunctionAssignment, etc.
│   ├── services.py   # AccessService
│   └── permissions.py
│
├── audit/            # Auditoría de acciones de usuarios
│   ├── models.py     # AuditLog
│   └── services.py   # AuditService
│
├── reports/          # Generación de reportes tabulares
│   ├── models.py     # Report, ReportConfig
│   ├── services.py   # ReportService, ExportService
│   └── views.py      # ReportViewSet
│
├── ivr_legacy/       # Adaptador a datos IVR (READ-ONLY)
│   ├── models.py     # CallRecord, QuarterlyReport, IVRMenu
│   └── services.py   # IVRDataService
│
├── pipeline/         # Monitoreo de ETL
│   ├── models.py     # JobExecutionLog
│   └── services.py   # ETLMonitoringService
│
├── core/             # Modelos abstractos base
│   └── models.py     # TimeStampedModel, SoftDeleteMixin
│
└── utils/            # Funciones helper
    ├── request.py    # get_client_ip()
    └── formatters.py # format_phone()

Solo con ver la estructura sabemos:
✅ Sistema de call center
✅ Genera reportes tabulares
✅ Control de acceso RBAC
✅ Adaptador a datos IVR
✅ Monitoreo de ETL
✅ Auditoría de acciones
```

---

<a name="10-frameworks-are-plugins"></a>
## 10. FRAMEWORKS ARE PLUGINS

**Principio**: Los frameworks deben ser detalles, no el núcleo. Tu lógica de negocio no debe depender de Django/DRF.

---

### 10.1 Lógica de Negocio Independiente

```python
# ❌ INCORRECTO - Lógica acoplada a framework
class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet con lógica de negocio."""  # ← Español
    
    def list(self, request):
        # ❌ Lógica de negocio EN ViewSet
        quarter = request.query_params.get('quarter')
        did = request.query_params.get('did')
        
        # ❌ Query compleja en View
        queryset = CallRecord.objects.filter(
            quarter=quarter,
            did=did
        ).annotate(
            # 20 líneas de lógica...
        )
        
        # ❌ Validaciones de negocio en View
        if queryset.count() > 100000:
            return Response({"error": "..."}, status=400)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ✅ CORRECTO - Lógica en Service (independiente de framework)
# apps/reports/services.py
class ReportService:
    """
    Servicio de lógica de negocio (sin dependencia de DRF).
    
    Este servicio puede usarse desde:
    - ViewSets de DRF
    - Comandos de Django
    - Tareas de Celery
    - Scripts standalone
    """  # ← Español
    
    @staticmethod
    def get_quarterly_call_records(quarter: str, did: str):
        """Obtiene registros trimestrales."""  # ← Español
        
        # Validar parámetros
        ReportService.validate_quarter(quarter)
        ReportService.validate_did(did)
        
        # Query
        queryset = CallRecord.objects.filter(
            quarter=quarter,
            did=did
        )
        
        # Validar límite
        if queryset.count() > 100000:
            raise ExportLimitExceeded(queryset.count())
        
        return queryset


# apps/reports/views.py (delgado, solo coordina)
class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet delgado que delega a Service."""  # ← Español
    
    @action(detail=False, methods=['get'])
    def quarterly_calls(self, request):
        """Endpoint para registros trimestrales."""  # ← Español
        
        # Extraer parámetros
        quarter = request.query_params.get('quarter')
        did = request.query_params.get('did')
        
        # Delegar a service
        try:
            queryset = ReportService.get_quarterly_call_records(
                quarter=quarter,
                did=did
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Serializar
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

---

<a name="11-dependencies-point-inward"></a>
## 11. DEPENDENCIES POINT INWARD

**Principio**: Las dependencias apuntan hacia adentro. El dominio no conoce la infraestructura.

---

### 11.1 Capas de Dependencia

```
CAPAS (de afuera hacia adentro):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────┐
│ INFRAESTRUCTURA (Django, DRF, DB)                       │
│ ↓ depende de                                            │
│ INTERFACES (ViewSets, Serializers)                      │
│ ↓ depende de                                            │
│ APPLICATION (Services)                                   │
│ ↓ depende de                                            │
│ DOMAIN (Models, Business Rules)                         │
└─────────────────────────────────────────────────────────┘

❌ Domain NO puede importar de Views
❌ Services NO pueden importar de ViewSets
✅ Views pueden importar de Services
✅ Services pueden importar de Models
```

**En IACT:**
```python
# ✅ CORRECTO - Flujo de dependencias

# DOMAIN (núcleo)
# apps/ivr/models.py
class CallRecord(models.Model):
    """Registro de llamada (DOMAIN)."""  # ← Español
    # ✅ No importa nada de views/ ni services/
    pass


# APPLICATION (lógica de negocio)
# apps/reports/services.py
from apps.ivr.models import CallRecord  # ✅ Importa de domain

class ReportService:
    """Servicio de reportes (APPLICATION)."""  # ← Español
    
    @staticmethod
    def get_quarterly_report(quarter: str):
        # ✅ Usa modelos del domain
        return CallRecord.objects.filter(quarter=quarter)


# INTERFACES (adaptadores)
# apps/reports/views.py
from apps.reports.services import ReportService  # ✅ Importa de application

class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet (INTERFACE)."""  # ← Español
    
    def list(self, request):
        # ✅ Delega a service
        data = ReportService.get_quarterly_report('Q1')
        # ...
```

---

<a name="12-use-cases-drive-architecture"></a>
## 12. USE CASES DRIVE ARCHITECTURE

**Principio**: Los casos de uso deben estar visibles en la arquitectura del sistema.

---

### 12.1 Casos de Uso Evidentes

**En IACT:**
```python
# ✅ CORRECTO - Casos de uso evidentes en la estructura

apps/reports/
├── services.py
│   ├── ReportService
│   │   ├── get_abandoned_calls_report()      # UC-001
│   │   ├── get_unique_clients_report()       # UC-002
│   │   └── get_quarterly_metrics()           # UC-003
│   │
│   └── ExportService
│       ├── export_to_excel()                 # UC-004
│       └── export_to_csv()                   # UC-005

apps/access/
├── services.py
│   ├── AccessService
│   │   ├── assign_function_to_user()         # UC-006
│   │   ├── check_user_permission()           # UC-007
│   │   └── validate_sod_violations()         # UC-008

Solo viendo los nombres sabemos QUÉ hace el sistema.
```

---

<a name="13-testability-without-framework"></a>
## 13. TESTABILITY WITHOUT FRAMEWORK

**Principio**: Debe poder testear lógica de negocio sin iniciar el framework completo.

---

### 13.1 Tests Sin Framework

```python
# ✅ CORRECTO - Service testeable sin Django

# apps/reports/services.py
class ReportService:
    """Servicio sin dependencia de DRF."""  # ← Español
    
    @staticmethod
    def calculate_abandonment_rate(
        total_calls: int,
        abandoned_calls: int
    ) -> float:
        """
        Calcula tasa de abandono.
        
        Args:
            total_calls: Total de llamadas
            abandoned_calls: Llamadas abandonadas
            
        Returns:
            Tasa de abandono (0-100)
        """  # ← Español
        
        if total_calls == 0:
            return 0.0
        
        return (abandoned_calls / total_calls) * 100


# tests/test_report_service.py (sin Django)
import pytest
from apps.reports.services import ReportService

def test_calculate_abandonment_rate():
    """Test simple sin framework."""  # ← Español
    
    # ✅ No requiere DB, no requiere Django
    rate = ReportService.calculate_abandonment_rate(
        total_calls=1000,
        abandoned_calls=80
    )
    
    assert rate == 8.0

def test_calculate_abandonment_rate_zero_calls():
    """Test con cero llamadas."""  # ← Español
    
    rate = ReportService.calculate_abandonment_rate(
        total_calls=0,
        abandoned_calls=0
    )
    
    assert rate == 0.0
```

---

<a name="14-regla-de-idioma-para-iact"></a>
## 14. REGLA DE IDIOMA PARA IACT

**Principio**: Código en inglés, comentarios en español, nombres de dominio según contexto.

---

### 14.1 Principio Central

```
REGLA DE ORO IACT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CÓDIGO: Siempre en INGLÉS
   - Variables, funciones, clases
   - Atributos, parámetros
   - Constantes
   - URLs, endpoints

✅ COMENTARIOS/DOCSTRINGS: Siempre en ESPAÑOL
   - Docstrings de funciones/clases
   - Comentarios inline
   - Help text, verbose_name
   - Mensajes de error

✅ NOMBRES DE DOMINIO: Depende del contexto
   - Function IDs RBAC: inglés (reports.view)
   - Display names: español (ve_reportes)
   - Choice keys: inglés (PENDING)
   - Choice labels: español ('Pendiente')
```

---

### 14.2 Justificación

**Por qué código en inglés:**
- ✅ Compatibilidad internacional
- ✅ Búsquedas en Google/Stack Overflow
- ✅ Colaboración con devs de otros países
- ✅ Frameworks y librerías en inglés
- ✅ Convención estándar de la industria

**Por qué comentarios en español:**
- ✅ Equipo es hispanohablante
- ✅ Dominio de negocio en español
- ✅ Documentación más clara para equipo local
- ✅ Facilita onboarding de nuevos devs

---

### 14.3 Reglas Específicas

```python
# ✅ CORRECTO

# Variables, funciones, clases: INGLÉS
user_count = 10
abandoned_call_rate = 8.5

def get_quarterly_report(quarter: str):
    """Obtiene reporte trimestral."""  # ← ESPAÑOL
    pass

class ReportService:
    """Servicio de generación de reportes."""  # ← ESPAÑOL
    pass


# Docstrings, comentarios: ESPAÑOL
def calculate_metrics(data):
    """
    Calcula métricas agregadas.
    
    Args:
        data: Datos a procesar
        
    Returns:
        Dict con métricas calculadas
    """  # ← ESPAÑOL
    
    # Validar CNST-007: máximo 100k registros  ← ESPAÑOL
    if len(data) > 100000:
        raise ExportLimitExceeded()
    
    return metrics
```

---

### 14.4 Tabla de Decisión Rápida

```
┌──────────────────────┬─────────┬──────────────────────────┐
│ Elemento             │ Idioma  │ Ejemplo                  │
├──────────────────────┼─────────┼──────────────────────────┤
│ Variables            │ Inglés  │ user_count               │
│ Funciones            │ Inglés  │ get_report()             │
│ Clases               │ Inglés  │ ReportService            │
│ Modelos              │ Inglés  │ CallRecord               │
│ db_table             │ Legacy  │ 'historico_t1'           │
│ db_column            │ Legacy  │ 'id_llamada'             │
├──────────────────────┼─────────┼──────────────────────────┤
│ Docstrings           │ Español │ """Calcula métricas."""  │
│ Comentarios          │ Español │ # Validar CNST-007       │
│ verbose_name         │ Español │ 'ID de llamada'          │
│ help_text            │ Español │ 'Timestamp de creación'  │
├──────────────────────┼─────────┼──────────────────────────┤
│ Function ID (RBAC)   │ Inglés  │ reports.view             │
│ Display name (UI)    │ Español │ ve_reportes              │
│ Choice keys          │ Inglés  │ PENDING, APPROVED        │
│ Choice labels        │ Español │ 'Pendiente', 'Aprobado'  │
│ Error messages       │ Español │ 'Error al procesar'      │
│ URLs                 │ Inglés  │ /api/v1/reports/         │
└──────────────────────┴─────────┴──────────────────────────┘
```

---

### 14.5 Ejemplos Completos IACT

#### Modelo Django Completo

```python
# apps/ivr/models.py

from django.db import models


class CallRecord(models.Model):  # ← Inglés
    """
    Registro histórico de llamadas del IVR.
    
    Mapea a tabla: historico_t1 (creada por ETL)
    
    Cada registro representa una llamada procesada
    por el sistema IVR con metadata completa.
    """  # ← Español
    
    # Campos en INGLÉS
    call_id = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='id_llamada',  # ← Columna legacy en DB
        verbose_name="ID de llamada",  # ← Español
        help_text="Identificador único de la llamada"  # ← Español
    )
    
    did = models.CharField(
        max_length=20,
        db_column='did',
        verbose_name="DID",  # ← Español
        help_text="DID de entrada de la llamada"  # ← Español
    )
    
    menu = models.CharField(
        max_length=100,
        db_column='menu',
        verbose_name="Menú",  # ← Español
        help_text="Menú navegado por el usuario"  # ← Español
    )
    
    timestamp = models.DateTimeField(
        db_column='fecha_hora',
        verbose_name="Fecha y hora",  # ← Español
        help_text="Timestamp de la llamada"  # ← Español
    )
    
    class Meta:
        db_table = 'historico_t1'  # ← Tabla legacy
        managed = False  # ← Django NO maneja tabla
        verbose_name = 'Registro de llamada'  # ← Español
        verbose_name_plural = 'Registros de llamadas'  # ← Español
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Call {self.call_id}"  # ← Inglés
```

---

#### Service Layer con Regla Aplicada

```python
# apps/reports/services.py

from apps.ivr.models import CallRecord, QuarterlyReport


class ReportService:  # ← Inglés
    """
    Servicio de lógica de negocio para reportes.
    
    Responsabilidades:
    - Obtener datos de reportes con validaciones
    - Calcular métricas agregadas
    - Aplicar reglas de negocio IACT
    """  # ← Español
    
    @staticmethod
    def get_quarterly_call_records(  # ← Inglés
        quarter: str,
        did: str
    ):
        """
        Obtiene registros de llamadas trimestrales.
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3, Q4)
            did: DID a consultar
            
        Returns:
            QuerySet de CallRecord
            
        Raises:
            ValidationError: Si parámetros inválidos
        """  # ← Español
        
        # Validar trimestre (comentario en español)
        valid_quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        if quarter not in valid_quarters:
            raise ValidationError(
                f"Trimestre debe ser uno de: {', '.join(valid_quarters)}"
            )
        
        # Consultar datos
        queryset = CallRecord.objects.filter(
            quarter=quarter,
            did=did
        )
        
        return queryset
    
    @staticmethod
    def calculate_abandonment_rate(  # ← Inglés
        total_calls: int,
        abandoned_calls: int
    ) -> float:
        """
        Calcula tasa de abandono.
        
        Formula: (abandonadas / total) * 100
        
        Args:
            total_calls: Total de llamadas
            abandoned_calls: Llamadas abandonadas
            
        Returns:
            Tasa de abandono (0-100)
        """  # ← Español
        
        if total_calls == 0:
            return 0.0
        
        # Calcular tasa (comentario en español)
        rate = (abandoned_calls / total_calls) * 100
        
        return round(rate, 2)
```

---

#### ViewSet DRF con Decorators

```python
# apps/reports/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.access.decorators import require_function


class ReportViewSet(viewsets.ModelViewSet):  # ← Inglés
    """
    API de reportes.
    
    Endpoints:
    - GET /reports/ - Lista reportes
    - POST /reports/ - Crea reporte
    - GET /reports/{id}/ - Detalle de reporte
    - POST /reports/{id}/export/ - Exporta a Excel/CSV
    """  # ← Español
    
    queryset = Report.objects.filter(is_deleted=False)
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])  # ← Inglés
    @require_function('reports.export.excel')  # ← Function ID en inglés
    def export_excel(self, request):  # ← Inglés
        """
        Exporta reportes a Excel.
        
        POST /reports/export-excel/
        
        Body:
            {
                "quarter": "Q1",
                "did": "Puebla"
            }
            
        Returns:
            { "file_url": "/media/exports/report.xlsx" }
        """  # ← Español
        
        # Extraer parámetros (comentario en español)
        quarter = request.data.get('quarter')
        did = request.data.get('did')
        
        # Validar y generar (comentario en español)
        try:
            file_url = ReportService.export_to_excel(quarter, did)
        except ValidationError as e:
            return Response(
                {"error": str(e)},  # ← Mensaje en español
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({"file_url": file_url})
```

---

### 14.6 Casos Especiales

#### URLs: Inglés (parte del código/API)
```python
# config/urls.py

urlpatterns = [
    # ✅ URLs en INGLÉS
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/access/', include('apps.access.urls')),
    
    # ❌ NO en español
    # path('api/v1/reportes/', ...)  # ❌ Incorrecto
]
```

#### Logs: Español (para equipo local)
```python
import logging

logger = logging.getLogger(__name__)

# ✅ Logs en ESPAÑOL
logger.info("Reporte generado exitosamente")  # ← Español
logger.error("Error al procesar archivo")     # ← Español
logger.warning("Límite de exportación excedido")  # ← Español
```

#### Choices: Keys inglés, labels español
```python
class Report(models.Model):
    """Modelo de reporte."""  # ← Español
    
    class Status(models.TextChoices):
        # Keys en INGLÉS, labels en ESPAÑOL
        DRAFT = 'draft', 'Borrador'  # ← Key: inglés, Label: español
        PENDING = 'pending', 'Pendiente'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado"  # ← Español
    )
```

---

### 14.7 Checklist de Verificación

```
ANTES DE COMMIT - VERIFICAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Nombres de variables: INGLÉS
□ Nombres de funciones: INGLÉS
□ Nombres de clases: INGLÉS
□ Nombres de modelos: INGLÉS
□ db_table: tabla legacy (sin cambiar)
□ db_column: columna legacy (sin cambiar)

□ Docstrings: ESPAÑOL
□ Comentarios: ESPAÑOL
□ verbose_name: ESPAÑOL
□ help_text: ESPAÑOL
□ Mensajes de error: ESPAÑOL

□ Function IDs RBAC: INGLÉS (reports.view)
□ Display names: ESPAÑOL (ve_reportes)
□ Choice keys: INGLÉS (PENDING)
□ Choice labels: ESPAÑOL ('Pendiente')
□ URLs: INGLÉS (/api/v1/reports/)
```

---

**FIN DE PARTE 1/5**

**Continúa en:** CLEAN_CODE_NAMING_PRINCIPLES_v3_0_0_PARTE_2.md

---

## ✅ RESUMEN PARTE 1

**Secciones completadas:**
- ✅ 1. Usar Nombres que Revelen Intenciones
- ✅ 2. Evitar la Desinformación
- ✅ 3. Realizar Distinciones con Sentido
- ✅ 4. Usar Nombres que se Puedan Pronunciar
- ✅ 5. Usar Nombres que se Puedan Buscar
- ✅ 6. Evitar Codificaciones
- ✅ 7. Evitar Asignaciones Mentales
- ✅ 8. Una Palabra por Concepto
- ✅ 9. Architecture Reveals Intent
- ✅ 10. Frameworks are Plugins
- ✅ 11. Dependencies Point Inward
- ✅ 12. Use Cases Drive Architecture
- ✅ 13. Testability Without Framework
- ✅ 14. Regla de Idioma para IACT

**Ejemplos con modelos corregidos:**
- ✅ CallRecord (antes HistoricoT1)
- ✅ QuarterlyReport (antes ReporteTrimestral)
- ✅ IVRMenu (antes Menu2)
- ✅ AbandonedCall (antes LlamadasAbandonadas)
- ✅ UniqueClient (antes ClientesUnicos)
- ✅ AverageClientPerMenu (antes PromedioClientesMenu)

**Arquitectura actualizada:**
- ✅ Apps reales documentadas (sin apps/dashboard/)
- ✅ apps/core/ solo modelos abstractos
- ✅ apps/utils/ solo funciones helper

**Próxima parte:** Principio de Equilibrio + DRF Básico
