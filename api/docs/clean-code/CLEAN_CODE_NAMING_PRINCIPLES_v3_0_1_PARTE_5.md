---
version: 3.0.1
date: 2026-01-18
project: IACT (Sistema Call Center)
base: Clean Code (Robert Martin) + Clean Architecture
changelog: |
  v3.0.1 - PARTE 5/5 - Cierre con arquitectura corregida
  - CORRECCIÓN: apps/core/ NO deprecado (fundamental)
  - Tabla resumen actualizada con arquitectura correcta
  - Changelog v3.0.1 completo
  - Anti-patterns válidos mantenidos
partes: 5/5
estado: completo
revision: v3.0.1 (arquitectura correcta)
replaces: CLEAN_CODE_NAMING_PRINCIPLES_v2_3_0_PARTE_5.md
---

# CLEAN CODE NAMING PRINCIPLES v3.0.1

**PARTE 5/5: ANTI-PATTERNS, RESUMEN Y REFERENCIAS**

---

## 📋 CONTENIDO DE ESTA PARTE (FINAL)

28. [Anti-patterns Comunes](#28-anti-patterns-comunes)
    - 28.1 Anti-pattern: Nombres Genéricos
    - 28.2 Anti-pattern: Notación Húngara
    - 28.3 Anti-pattern: Abreviaciones Ambiguas
    - 28.4 Anti-pattern: Números en Nombres
    - 28.5 Anti-pattern: Nombres Negativos
    - 28.6 Anti-pattern: Nombres con "Manager"
    - 28.7 Anti-pattern: Verbosidad Excesiva
    - 28.8 Anti-pattern: Mezcla de Idiomas

29. [Tabla de Resumen](#29-tabla-de-resumen)
    - 29.1 Resumen por Sección
    - 29.2 Tabla de Decisión Rápida
    - 29.3 Checklist Master

30. [Referencias](#30-referencias)
    - 30.1 Libros
    - 30.2 Documentación
    - 30.3 Documentos IACT Relacionados

31. [Changelog v3.0.1](#31-changelog-v3-0-1)
    - 31.1 Cambios Principales v3.0.1
    - 31.2 Comparación Versiones
    - 31.3 Migración desde v2.3.1

---

## ⚠️ CAMBIOS EN v3.0.1

```
ARQUITECTURA CORREGIDA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ v2.3.1: apps/core/ marcado "DEPRECADO" → ERROR
✅ v3.0.1: apps/core/ FUNDAMENTAL (modelos abstractos)

apps/core/models.py
├── TimeStampedModel (abstract=True)      ✅ CORRECTO
├── SoftDeleteMixin (abstract=True)       ✅ CORRECTO
├── SoftDeleteManager                     ✅ CORRECTO
└── SoftDeleteQuerySet                    ✅ CORRECTO

apps/core/mixins.py
└── SoftDeleteViewSetMixin                ✅ CORRECTO

apps/utils/
├── pagination.py (funciones + helpers)   ✅ CORRECTO
├── exceptions.py (funciones + exceptions)✅ CORRECTO
└── request.py (funciones)                ✅ CORRECTO
```

---

## RECORDATORIO: REGLA DE IDIOMA

```
✅ CÓDIGO: Siempre en INGLÉS
✅ COMENTARIOS/DOCSTRINGS: Siempre en ESPAÑOL
✅ NOMBRES DE DOMINIO: Depende del contexto

Function ID RBAC: reports.view (inglés)
Display name: ve_reportes (español)
Error messages: español
```

---

<a name="28-anti-patterns-comunes"></a>
## 28. ANTI-PATTERNS COMUNES

### **28.1 Anti-pattern: Nombres Genéricos**

**Problema**: Usar nombres que no aportan información.

```python
# ❌ ANTI-PATTERN
data = get_data()
info = get_info()
stuff = get_stuff()
thing = process_thing()
obj = create_obj()
temp = calculate_temp()
result = do_something()

# ✅ CORRECTO
report_metrics = get_report_metrics()
user_permissions = get_user_permissions()
dashboard_widgets = get_dashboard_widgets()
call_record = process_call_record()
export_file = create_export_file()
abandonment_rate = calculate_abandonment_rate()
validation_result = validate_date_range()
```

**Aplicación IACT:**

```python
# apps/reports/services.py

# ❌ ANTI-PATTERN - Nombres genéricos
class ReportService:
    @staticmethod
    def process(data):  # ❌ ¿Procesar qué? ¿Cómo?
        result = do_stuff(data)  # ❌ ¿Qué stuff?
        info = get_info(result)  # ❌ ¿Qué info?
        return info

# ✅ CORRECTO - Nombres específicos
class ReportService:
    @staticmethod
    def generate_quarterly_report(call_records: List[Dict]) -> Dict:
        """Genera reporte trimestral."""
        aggregated_metrics = aggregate_by_quarter(call_records)
        formatted_data = format_for_export(aggregated_metrics)
        return formatted_data
```

---

### **28.2 Anti-pattern: Notación Húngara**

**Problema**: Prefijos que indican tipo (innecesarios con type hints).

```python
# ❌ ANTI-PATTERN - Notación húngara
strName = "Report"
intCount = 100
lstRecords = []
dictFilters = {}
boolIsActive = True
dtStartDate = date.today()

# ✅ CORRECTO - Type hints en lugar de prefijos
name: str = "Report"
count: int = 100
records: List[Dict] = []
filters: Dict[str, Any] = {}
is_active: bool = True
start_date: date = date.today()
```

**EXCEPCIÓN en IACT**: Prefijos de dominio (nomenclatura IVR legacy)

```python
# ✅ CORRECTO - Prefijos de DOMINIO (no de tipo)
# apps/ivr/models.py

class CallRecord(models.Model):
    """Registro de llamada del IVR."""
    
    # Estos prefijos son del DOMINIO IVR, no notación húngara:
    dFecha = models.DateField()  # 'd' = date (del dominio legacy)
    cMenu = models.CharField()  # 'c' = código (del dominio legacy)
    cDID_800Transfer = models.CharField()  # Del dominio IVR
    cTelefono_Origen = models.CharField()
    
    class Meta:
        db_table = 'historico_t1'
        managed = False
    
    # RAZÓN: Mantienen nomenclatura original del sistema IVR legacy
    # NO son notación húngara moderna, son convención del dominio
```

---

### **28.3 Anti-pattern: Abreviaciones Ambiguas**

**Problema**: Abreviaciones que requieren traducción mental.

```python
# ❌ ANTI-PATTERN - Abreviaciones ambiguas
usr = get_user()
rpt = generate_report()
fn = get_function()
cfg = load_config()
ctx = get_context()
req = validate_request()
resp = create_response()

# ✅ CORRECTO - Nombres completos
user = get_user()
report = generate_report()
function = get_function()
config = load_config()
context = get_context()
request = validate_request()
response = create_response()
```

**Excepción**: Abreviaciones estándar de la industria

```python
# ✅ ACEPTABLE - Abreviaciones universales
id = user.id  # ✅ "ID" es universal
url = get_url()  # ✅ "URL" es estándar
api = create_api()  # ✅ "API" es estándar
etl = run_etl()  # ✅ "ETL" es término de la industria
pdf = generate_pdf()  # ✅ "PDF" es universal
csv = export_csv()  # ✅ "CSV" es estándar
```

**Aplicación IACT:**

```python
# apps/access/services.py

# ❌ ANTI-PATTERN
class AccessService:
    @staticmethod
    def chk_usr_fn(u, f):  # ❌ Imposible leer
        agr = get_agr(u)
        for a in agr:
            if f in a.fns:
                return True
        return False

# ✅ CORRECTO
class AccessService:
    @staticmethod
    def check_user_has_function(user: User, function_id: str) -> bool:
        """Verifica si usuario tiene función."""
        agrupadores = get_user_agrupadores(user)
        
        for agrupador in agrupadores:
            if function_id in agrupador.function_ids:
                return True
        
        return False
```

---

### **28.4 Anti-pattern: Números en Nombres**

**Problema**: Usar números para versiones de variables.

```python
# ❌ ANTI-PATTERN - Números en nombres
data1 = get_data()
data2 = transform_data(data1)
data3 = validate_data(data2)
result1 = calculate(data3)
result2 = format(result1)

# ✅ CORRECTO - Nombres descriptivos
raw_data = get_data()
transformed_data = transform_data(raw_data)
validated_data = validate_data(transformed_data)
calculated_metrics = calculate(validated_data)
formatted_result = format(calculated_metrics)
```

**Excepción**: Números que son parte del dominio

```python
# ✅ ACEPTABLE - Números del dominio
class CallRecord(models.Model):  # ✅ Mapea a historico_t1
    """Histórico de llamadas."""
    
    class Meta:
        db_table = 'historico_t1'  # ✅ Tabla real del dominio
        managed = False

tbl_historico_t1_2025 = ...  # ✅ Tabla real del dominio
tbl_historico_t2_2025 = ...
```

---

### **28.5 Anti-pattern: Nombres Negativos**

**Problema**: Usar nombres con negación (confusos en lógica booleana).

```python
# ❌ ANTI-PATTERN - Nombres negativos
if not is_not_valid:  # ❌ Doble negación, confuso
    process()

if not is_disabled:  # ❌ Difícil de leer
    enable()

if not is_not_deleted:  # ❌ Triple negación!
    restore()

# ✅ CORRECTO - Nombres positivos
if is_valid:  # ✅ Claro
    process()

if is_enabled:  # ✅ Directo
    activate()

if is_deleted:  # ✅ Simple
    # Ya está eliminado, no hacer nada
    pass
else:
    # No está eliminado, procesar
    process()
```

**Aplicación IACT:**

```python
# apps/core/models.py

# ❌ ANTI-PATTERN
class SoftDeleteMixin(models.Model):
    is_not_deleted = models.BooleanField(default=True)  # ❌ Negativo
    
    def is_not_active(self):  # ❌ Negativo
        return self.is_not_deleted == False
    
    class Meta:
        abstract = True

# ✅ CORRECTO
class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)  # ✅ Positivo
    
    def is_active(self):  # ✅ Positivo
        return not self.is_deleted
    
    class Meta:
        abstract = True
```

---

### **28.6 Anti-pattern: Nombres con "Manager"**

**Problema**: Sobre-uso de "Manager" sin agregar valor.

```python
# ❌ ANTI-PATTERN - "Manager" excesivo
class ReportManager:  # ❌ ¿Qué gestiona exactamente?
    def manage_reports(self):  # ❌ Redundante
        pass

class DataManager:  # ❌ Demasiado genérico
    def manage_data(self):
        pass

class FileManager:  # ❌ Vago
    def manage_files(self):
        pass

# ✅ CORRECTO - Nombres específicos
class ReportService:  # ✅ Claro: lógica de negocio
    def generate_report(self):
        pass

class ReportRepository:  # ✅ Claro: acceso a datos
    def save_report(self):
        pass

class ReportExporter:  # ✅ Claro: responsabilidad específica
    def export_to_excel(self):
        pass
```

**Excepción**: Django Managers (patrón del framework)

```python
# ✅ ACEPTABLE - Django Manager (patrón oficial)
# apps/core/models.py

class SoftDeleteManager(models.Manager):  # ✅ Patrón Django
    """Manager para soft delete."""
    
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

class Report(models.Model):
    objects = models.Manager()  # ✅ Manager por defecto
    active = SoftDeleteManager()  # ✅ Manager custom
```

---

### **28.7 Anti-pattern: Verbosidad Excesiva**

**Problema**: Nombres demasiado largos ("dissertaciones").

```python
# ❌ ANTI-PATTERN - Verbosidad excesiva
execution_date_and_time_of_etl_processing = datetime.now()
total_number_of_records_processed_successfully = 100
average_number_of_calls_per_unique_client = 2.5
get_all_reports_filtered_by_date_range_and_quarter = lambda: None

# ✅ CORRECTO - Equilibrado (ver Sección 15)
start_time = datetime.now()
processed_count = 100
avg_calls_per_client = 2.5
get_report_data = lambda: None
```

**Ver Sección 15**: Principio de Equilibrio para guía completa.

---

### **28.8 Anti-pattern: Mezcla de Idiomas**

**Problema**: Mezclar inglés y español sin consistencia.

```python
# ❌ ANTI-PATTERN - Mezcla de idiomas
class ReporteService:  # ❌ "Reporte" español, "Service" inglés
    def get_datos(self):  # ❌ "get" inglés, "datos" español
        usuario_id = self.obtener_user()  # ❌ Mezclado
        return self.generate_reporte(usuario_id)

# ✅ CORRECTO - Todo código en inglés
class ReportService:
    def get_data(self):
        """Obtiene datos del reporte."""  # ← Docstring español
        user_id = self.get_user()
        return self.generate_report(user_id)
```

**Ver Sección 14**: Regla de Idioma para IACT.

---

### **28.9 Resumen de Anti-patterns**

```
ANTI-PATTERNS A EVITAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ❌ Nombres genéricos (data, info, stuff, thing)
2. ❌ Notación húngara (strName, intCount, lstRecords)
3. ❌ Abreviaciones ambiguas (usr, rpt, fn, cfg)
4. ❌ Números en nombres (data1, data2, result1)
5. ❌ Nombres negativos (is_not_valid, is_disabled)
6. ❌ "Manager" excesivo (DataManager, FileManager)
7. ❌ Verbosidad excesiva (nombres de "dissertación")
8. ❌ Mezcla de idiomas (ReporteService, get_datos)

USAR EN SU LUGAR:
✅ Nombres específicos y descriptivos
✅ Type hints en lugar de prefijos
✅ Nombres completos o abreviaciones estándar
✅ Nombres descriptivos en pipeline
✅ Nombres positivos (is_valid, is_enabled)
✅ Nombres específicos (Service, Repository, Exporter)
✅ Equilibrio claridad-brevedad (Sección 15)
✅ Código inglés, comentarios español (Sección 14)
```

---

<a name="29-tabla-de-resumen"></a>
## 29. TABLA DE RESUMEN

### **29.1 Resumen por Sección**

```
CLEAN CODE NAMING PRINCIPLES v3.0.1 - RESUMEN
════════════════════════════════════════════════════════════════════

PARTE 1: PRINCIPIOS FUNDAMENTALES (Secciones 1-14)
├─ 1.  Nombres que Revelen Intenciones
├─ 2.  Evitar la Desinformación
├─ 3.  Realizar Distinciones con Sentido
├─ 4.  Usar Nombres Pronunciables
├─ 5.  Usar Nombres Buscables
├─ 6.  Evitar Codificaciones
├─ 7.  Evitar Asignaciones Mentales
├─ 8.  Una Palabra por Concepto
├─ 9.  Architecture Reveals Intent
├─ 10. Frameworks are Plugins
├─ 11. Dependencies Point Inward
├─ 12. Use Cases Drive Architecture
├─ 13. Testability Without Framework
└─ 14. Regla de Idioma para IACT

PARTE 2: EQUILIBRIO Y DRF BÁSICO (Secciones 15-18)
├─ 15. ⭐ PRINCIPIO DE EQUILIBRIO ⭐
├─ 16. Nomenclatura por Ubicación (IACT)
├─ 17. DRF: ViewSets y Views
└─ 18. DRF: Serializers

PARTE 3: DRF AVANZADO (Secciones 19-23)
├─ 19. DRF: Permissions y Authentication
├─ 20. DRF: Decorators
├─ 21. Django: Middleware
├─ 22. DRF: Mixins
└─ 23. DRF: Response y Exception Handling

PARTE 4: IACT ESPECÍFICO (Secciones 24-27)
├─ 24. DRF: Renderers, Parsers, Pagination
├─ 25. ⭐ IACT: Arquitectura apps/core/ vs apps/utils/ ⭐ (v3.0.1)
├─ 26. IACT: Service Layer Pattern
└─ 27. IACT: Modelos y Herencia

PARTE 5: CIERRE (Secciones 28-31)
├─ 28. Anti-patterns Comunes
├─ 29. Tabla de Resumen
├─ 30. Referencias
└─ 31. ⭐ Changelog v3.0.1 ⭐

TOTAL: 31 Secciones | 5 Partes | ARQUITECTURA CORREGIDA v3.0.1
```

---

### **29.2 Tabla de Decisión Rápida**

#### **29.2.1 ¿Dónde va mi código?**

```
┌──────────────────────────┬─────────────────────────────────┐
│ Tipo de Código           │ Ubicación                       │
├──────────────────────────┼─────────────────────────────────┤
│ Modelo abstracto         │ apps/core/models.py             │
│ Mixin ViewSet            │ apps/core/mixins.py             │
│ Manager/QuerySet         │ apps/core/models.py             │
├──────────────────────────┼─────────────────────────────────┤
│ Función helper           │ apps/utils/*.py                 │
│ Pagination helper        │ apps/utils/pagination.py        │
│ Exception personalizada  │ apps/utils/exceptions.py        │
├──────────────────────────┼─────────────────────────────────┤
│ Modelo concreto          │ apps/{app}/models.py            │
│ Service lógica negocio   │ apps/{app}/services.py          │
│ ViewSet API              │ apps/{app}/views.py             │
│ Serializer               │ apps/{app}/serializers.py       │
└──────────────────────────┴─────────────────────────────────┘

REGLA CLAVE:
"¿Otros modelos HEREDAN de esto?"
  SÍ  → apps/core/
  NO  → apps/utils/ (si es función/helper)
        apps/{app}/ (si es modelo concreto)
```

---

#### **29.2.2 ¿Qué idioma usar?**

```
┌───────────────────────┬─────────┬──────────────────────────┐
│ Elemento              │ Idioma  │ Ejemplo                  │
├───────────────────────┼─────────┼──────────────────────────┤
│ Variables             │ Inglés  │ user_id, report_data     │
│ Funciones             │ Inglés  │ get_data, generate_excel │
│ Clases                │ Inglés  │ ReportService, User      │
│ Atributos modelo      │ Inglés  │ function_id, is_active   │
│ URLs                  │ Inglés  │ /reports/, /dashboard/   │
│ Constantes            │ Inglés  │ MAX_RECORDS              │
├───────────────────────┼─────────┼──────────────────────────┤
│ Docstrings            │ Español │ """Calcula métricas."""  │
│ Comentarios           │ Español │ # Validar CNST-007       │
│ help_text             │ Español │ help_text="ID único"     │
│ verbose_name          │ Español │ verbose_name="Usuario"   │
│ Error messages        │ Español │ "Límite excedido"        │
│ Logs                  │ Español │ logger.info("Inicio")    │
├───────────────────────┼─────────┼──────────────────────────┤
│ Function ID (RBAC)    │ Inglés  │ reports.view             │
│ Display name (UI)     │ Español │ ve_reportes              │
│ Choice keys           │ Inglés  │ PENDING                  │
│ Choice labels         │ Español │ 'Pendiente'              │
└───────────────────────┴─────────┴──────────────────────────┘
```

---

#### **29.2.3 ¿Qué longitud usar?**

```
┌─────────────────────────┬──────────┬──────────────────────┐
│ Tipo                    │ Palabras │ Ejemplo              │
├─────────────────────────┼──────────┼──────────────────────┤
│ Loop variables          │ 1        │ i, user, record      │
│ Local variables         │ 1-2      │ count, total         │
│ Function parameters     │ 2-3      │ start_date, user_id  │
│ Instance variables      │ 2-4      │ max_records          │
│ Function names          │ 2-5      │ get_report_data      │
│ Class names             │ 2-4      │ ReportService        │
│ Module constants        │ 2-5      │ MAX_EXPORT_RECORDS   │
└─────────────────────────┴──────────┴──────────────────────┘

REGLA: Longitud proporcional al scope
```

---

#### **29.2.4 ¿Qué patrón usar?**

```
┌─────────────────┬───────────────────────────────────────┐
│ Componente      │ Patrón                                │
├─────────────────┼───────────────────────────────────────┤
│ ViewSet         │ {Modelo}ViewSet                       │
│                 │ Ejemplo: ReportViewSet                │
├─────────────────┼───────────────────────────────────────┤
│ Serializer      │ {Modelo}Serializer                    │
│                 │ Ejemplo: ReportSerializer             │
├─────────────────┼───────────────────────────────────────┤
│ Service         │ {App}Service                          │
│                 │ Ejemplo: ReportService                │
├─────────────────┼───────────────────────────────────────┤
│ Permission      │ {Action}{Resource}Permission          │
│                 │ Ejemplo: CanViewReportPermission      │
├─────────────────┼───────────────────────────────────────┤
│ Middleware      │ {Propósito}Middleware                 │
│                 │ Ejemplo: AccessAuditMiddleware        │
├─────────────────┼───────────────────────────────────────┤
│ Decorator       │ {verbo}_{concepto}                    │
│                 │ Ejemplo: require_function             │
├─────────────────┼───────────────────────────────────────┤
│ Manager         │ {Filtro}Manager                       │
│                 │ Ejemplo: SoftDeleteManager            │
├─────────────────┼───────────────────────────────────────┤
│ Mixin           │ {Funcionalidad}Mixin                  │
│                 │ Ejemplo: SoftDeleteMixin              │
└─────────────────┴───────────────────────────────────────┘
```

---

### **29.3 Checklist Master**

```
CHECKLIST COMPLETO - CLEAN CODE v3.0.1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANTES DE COMMIT:

1. UBICACIÓN CORRECTA (Sección 25) ⭐ v3.0.1
   ☐ Modelo abstracto → apps/core/models.py
   ☐ Mixin ViewSet → apps/core/mixins.py
   ☐ Función helper → apps/utils/
   ☐ Modelo concreto → apps/{app}/models.py
   ☐ Service → apps/{app}/services.py

2. REGLA DE IDIOMA (Sección 14)
   ☐ Código en INGLÉS
   ☐ Comentarios/docstrings en ESPAÑOL
   ☐ Function IDs en inglés
   ☐ Display names en español

3. PRINCIPIO DE EQUILIBRIO (Sección 15) ⭐
   ☐ Nombre pronunciable 3 veces seguidas
   ☐ Menos de 5 palabras
   ☐ Menos de 50 caracteres
   ☐ Longitud apropiada al scope
   ☐ Sin verbosidad excesiva

4. NOMBRES DESCRIPTIVOS (Secciones 1-8)
   ☐ Revela intención
   ☐ Sin desinformación
   ☐ Distinción clara
   ☐ Pronunciable
   ☐ Buscable
   ☐ Sin codificaciones (type hints en su lugar)
   ☐ Sin asignaciones mentales
   ☐ Una palabra por concepto

5. ARQUITECTURA CLEAN (Secciones 9-13)
   ☐ Arquitectura revela intención
   ☐ Framework como plugin
   ☐ Dependencias apuntan hacia adentro
   ☐ Casos de uso conducen arquitectura
   ☐ Testeable sin framework

6. PATRONES DRF (Secciones 16-24)
   ☐ ViewSet: {Modelo}ViewSet
   ☐ Serializer: {Modelo}Serializer
   ☐ Permission: Can{Action}{Resource}Permission
   ☐ Middleware: {Propósito}Middleware

7. IACT ESPECÍFICO (Secciones 25-27)
   ☐ Service en apps/{app}/services.py
   ☐ Herencia desde apps/core/models.py ⭐
   ☐ SoftDeleteMixin desde core/ ⭐
   ☐ TimeStampedModel desde core/ ⭐
   ☐ Manager personalizado si soft delete
   ☐ Validaciones en clean()

8. ANTI-PATTERNS (Sección 28)
   ☐ Sin nombres genéricos (data, info, stuff)
   ☐ Sin notación húngara (strName, intCount)
   ☐ Sin abreviaciones ambiguas (usr, rpt)
   ☐ Sin nombres negativos (is_not_valid)
   ☐ Sin "Manager" excesivo
   ☐ Sin verbosidad excesiva
   ☐ Sin mezcla de idiomas

9. VALIDACIÓN FINAL
   ☐ Tests pasan
   ☐ Linter pasa (flake8, pylint)
   ☐ Type checker pasa (mypy)
   ☐ Documentación actualizada
```

---

<a name="30-referencias"></a>
## 30. REFERENCIAS

### **30.1 Libros**

#### **Clean Code: A Handbook of Agile Software Craftsmanship**
- **Autor**: Robert C. Martin ("Uncle Bob")
- **Año**: 2008
- **Editorial**: Prentice Hall
- **ISBN**: 978-0132350884

**Capítulos relevantes:**
- Chapter 2: Meaningful Names (base de este documento)
- Chapter 3: Functions
- Chapter 10: Classes

**Citas usadas en este documento:**
- Sección 1: "El nombre debe indicar por qué existe..."
- Sección 2: "No haga referencia a un grupo de cuentas..."
- Sección 4: "Si no lo puede pronunciar..."
- Sección 5: "La longitud de un nombre debe corresponderse..."
- Sección 8: "Escoja una palabra por cada concepto..."

---

#### **Clean Architecture: A Craftsman's Guide to Software Structure and Design**
- **Autor**: Robert C. Martin
- **Año**: 2017
- **Editorial**: Prentice Hall
- **ISBN**: 978-0134494166

**Capítulos relevantes:**
- Part IV: Component Principles
- Part V: Architecture (base secciones 9-13)

**Principios aplicados:**
- Sección 9: Architecture Reveals Intent
- Sección 10: Frameworks are Plugins
- Sección 11: Dependencies Point Inward
- Sección 12: Use Cases Drive Architecture
- Sección 13: Testability Without Framework

---

#### **The Pragmatic Programmer**
- **Autores**: Andrew Hunt, David Thomas
- **Año**: 2019 (20th Anniversary Edition)
- **Editorial**: Addison-Wesley
- **ISBN**: 978-0135957059

**Conceptos aplicados:**
- DRY (Don't Repeat Yourself)
- Orthogonality
- Tracer Bullets (usado en Service Layer)

---

### **30.2 Documentación**

#### **Django Documentation**
- **URL**: https://docs.djangoproject.com/
- **Versión**: 4.2 LTS
- **Secciones relevantes**:
  - Model Layer
  - View Layer
  - Django REST Framework

#### **Django REST Framework**
- **URL**: https://www.django-rest-framework.org/
- **Versión**: 3.14+
- **Secciones usadas**:
  - ViewSets (Sección 17)
  - Serializers (Sección 18)
  - Permissions (Sección 19)
  - Generic Views

#### **Python Style Guide (PEP 8)**
- **URL**: https://peps.python.org/pep-0008/
- **Aplicación**: Convenciones base de nomenclatura Python

#### **Python Type Hints (PEP 484)**
- **URL**: https://peps.python.org/pep-0484/
- **Aplicación**: Type hints en lugar de notación húngara (Sección 6)

---

### **30.3 Documentos IACT Relacionados**

#### **Análisis Arquitectónico**

```
docs/clean-code/
├─ ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v3.0.0.md
│  → ⭐ Base para correcciones v3.0.1
│  → Define apps/core/ vs apps/utils/
│  → Arquitectura real del proyecto
│
└─ GUIA_CORE_VS_UTILS_v2.0.0.md
   → Reglas de apps/core/ (abstractos)
   → Reglas de apps/utils/ (funciones)
```

#### **Arquitectura**

```
docs/arquitectura/diseño/
├─ ARQUITECTURA_REAL_ETL_DEFINITIVA.md
│  → Define arquitectura IVR_LEGACY (MariaDB)
│  → Tablas: historico_t1, tbl_reporte_*
│  → Stored Procedure ETL
│
└─ URLS_REPORTES_Y_DASHBOARDS.md
   → ⭐ Define apps/dashboard/ (widgets)
   → Define apps/reports/ (tabulares)
   → Arquitectura completa
```

#### **Análisis**

```
docs/analisis/requisitos/
├─ CASOS_DE_USO_IACT_v5_0_0.md
│  → UC-001 a UC-030
│  → Base para Sección 12 (Use Cases Drive Architecture)
│
└─ LEVANTAMIENTO_APPS_IACT.md
   → Estructura de apps/
   → Justificación de separación
```

---

#### **Scripts SQL Reales**

```
Ubicación: /mnt/user-data/uploads/

Scripts ETL (base para nomenclatura):
├─ q_REPTRIM021_LLAMADAS_ABDANDONADAS.sql
├─ q_REPTRIM011_CLIENTES_UNICOS.sql
├─ q_REP_DETALLE_TRANSFERENCIA_MENU_OPCION-v.0.3.1.sql
└─ q_cMENU_ERROR.sql

Nomenclatura real:
- tbl_reporte_trimestral
- tbl_reporte_transferencias
- tbl_historico_t1_2025
- job_execution_log
```

---

#### **Constantes del Proyecto**

```
Constantes referenciadas en este documento:

CNST-004: ETL_TIMEOUT_SECONDS = 300
CNST-005: OBLIGATORIO soft delete (SoftDeleteMixin)
CNST-006: REPORT_MAX_DATE_RANGE_DAYS = 730
CNST-007: MAX_EXPORT_RECORDS = 100000

Ver: docs/arquitectura/CONSTANTES_PROYECTO.md
```

---

<a name="31-changelog-v3-0-1"></a>
## 31. CHANGELOG v3.0.1

### **31.1 Cambios Principales v3.0.1**

#### **⭐ CORRECCIÓN CRÍTICA: apps/core/ NO deprecado**

```
PROBLEMA IDENTIFICADO EN v2.3.1:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PARTE 4, Sección 25.1:
"apps/core/ → ❌ DEPRECADO"
"Nueva arquitectura: ... └── core/ ❌ ELIMINAR COMPLETAMENTE"

ERROR CONCEPTUAL GRAVE:
- apps/core/ contiene modelos abstractos (TimeStampedModel)
- apps/core/ contiene SoftDeleteMixin
- apps/core/ contiene SoftDeleteViewSetMixin
- apps/core/ es FUNDAMENTAL, no deprecado

CORRECCIÓN EN v3.0.1:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/core/          ✅ FUNDAMENTAL (modelos abstractos + mixins)
  ├── models.py
  │   ├── TimeStampedModel (abstract=True)
  │   ├── SoftDeleteMixin (abstract=True)
  │   ├── SoftDeleteManager
  │   └── SoftDeleteQuerySet
  └── mixins.py
      └── SoftDeleteViewSetMixin

apps/utils/         ✅ FUNCIONES + CLASES HELPER
  ├── pagination.py (helpers OK)
  ├── exceptions.py (funciones + exceptions)
  └── request.py (funciones)
```

---

#### **Sección 25 Reescrita Completamente**

```
v2.3.1: "IACT: Separación access/ vs core/"
v3.0.1: "IACT: Arquitectura apps/core/ vs apps/utils/"

CAMBIOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

25.1 Estado Actual → 25.1 Arquitectura Correcta
   ❌ v2.3.1: "apps/core/ → DEPRECADO"
   ✅ v3.0.1: "apps/core/ → FUNDAMENTAL"

25.2 Responsabilidades por App
   ✅ apps/core/ documentado correctamente
   ✅ apps/utils/ clarificado (solo funciones)

25.3 Reglas de Arquitectura (NUEVA)
   ✅ Pregunta clave: "¿Otros modelos HEREDAN?"
   ✅ SÍ → apps/core/
   ✅ NO → apps/utils/ o apps/{app}/

25.4 Flujo de Datos IACT
   ✅ Mantiene flujo ETL → Django
   ✅ apps/dashboard/ incluido
```

---

#### **Todas las Importaciones Corregidas**

```
CAMBIOS EN TODAS LAS PARTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ v2.3.1:
from apps.utils.models import SoftDeleteMixin, TimeStampedModel
from apps.utils.mixins import SoftDeleteViewSetMixin

✅ v3.0.1:
from apps.core.models import SoftDeleteMixin, TimeStampedModel
from apps.core.mixins import SoftDeleteViewSetMixin

ARCHIVOS ACTUALIZADOS:
- PARTE 1: Sección 3, 9, 13
- PARTE 2: Sección 16
- PARTE 3: Sección 22
- PARTE 4: Sección 25, 27
- PARTE 5: Sección 28, 29, 31
```

---

### **31.2 Comparación Versiones**

```
┌─────────────────────┬──────────┬──────────┬────────────┬────────────┐
│ Aspecto             │ v2.1.0   │ v2.2.0   │ v2.3.1     │ v3.0.1     │
├─────────────────────┼──────────┼──────────┼────────────┼────────────┤
│ Total secciones     │ 29       │ 30       │ 31         │ 31         │
│ Partes              │ 1        │ 4        │ 5          │ 5          │
│ Regla de idioma     │ Implícita│ Explícita│ Explícita  │ Explícita  │
│ Principio equilibrio│ ❌       │ ❌       │ ✅         │ ✅         │
│ apps/core/          │ Confuso  │ Confuso  │ ❌ Deprec. │ ✅ Correct │
│ apps/utils/         │ Confuso  │ Confuso  │ ❌ Clases  │ ✅ Funcs   │
│ apps/dashboard/     │ ❌       │ ❌       │ ✅         │ ✅         │
│ Ejemplos IACT       │ Básicos  │ Buenos   │ Real arch. │ Real arch. │
│ Anti-patterns       │ ❌       │ Básicos  │ Completos  │ Completos  │
│ Tabla resumen       │ ❌       │ Básica   │ Completa   │ ✅ Correct │
│ Referencias         │ ❌       │ Básicas  │ Completas  │ ✅ +v3.0.1 │
├─────────────────────┼──────────┼──────────┼────────────┼────────────┤
│ ESTADO              │ Obsoleto │ Obsoleto │ ❌ ERROR   │ **ACTUAL** │
└─────────────────────┴──────────┴──────────┴────────────┴────────────┘
```

---

### **31.3 Migración desde v2.3.1**

#### **Paso 1: Corregir Importaciones**

```python
# BUSCAR Y REEMPLAZAR en todo el proyecto:

# Buscar:
from apps.utils.models import SoftDeleteMixin
from apps.utils.models import TimeStampedModel
from apps.utils.mixins import SoftDeleteViewSetMixin

# Reemplazar por:
from apps.core.models import SoftDeleteMixin
from apps.core.models import TimeStampedModel
from apps.core.mixins import SoftDeleteViewSetMixin
```

---

#### **Paso 2: Verificar Arquitectura**

```bash
# Verificar que apps/core/ existe y tiene contenido correcto:
ls apps/core/models.py  # Debe existir
ls apps/core/mixins.py  # Debe existir

# Verificar que apps/utils/ NO tiene modelos abstractos:
grep -r "class.*Mixin.*models.Model" apps/utils/  # No debe encontrar
grep -r "abstract = True" apps/utils/  # No debe encontrar

# Verificar que apps/utils/ SOLO tiene funciones/helpers:
find apps/utils/ -name "*.py" -exec grep -l "^def " {} \;  # OK
find apps/utils/ -name "*.py" -exec grep -l "^class.*Pagination" {} \;  # OK
```

---

#### **Paso 3: Actualizar Modelos**

```python
# ANTES (v2.3.1 - importación incorrecta)
from apps.utils.models import SoftDeleteMixin, TimeStampedModel

class Report(SoftDeleteMixin, TimeStampedModel, models.Model):
    """Modelo de reporte."""
    name = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'reports'


# DESPUÉS (v3.0.1 - importación correcta)
from apps.core.models import SoftDeleteMixin, TimeStampedModel

class Report(SoftDeleteMixin, TimeStampedModel, models.Model):
    """Modelo de reporte."""
    name = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'reports'
```

---

#### **Paso 4: Actualizar ViewSets**

```python
# ANTES (v2.3.1 - importación incorrecta)
from apps.utils.mixins import SoftDeleteViewSetMixin

class ReportViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet con soft delete."""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


# DESPUÉS (v3.0.1 - importación correcta)
from apps.core.mixins import SoftDeleteViewSetMixin

class ReportViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet con soft delete."""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
```

---

#### **Paso 5: Verificar con Tests**

```bash
# Ejecutar tests para verificar que todo funciona:
python manage.py test

# Verificar imports con linter:
pylint apps/

# Verificar types:
mypy apps/
```

---

### **31.4 Documentos Obsoletos**

```
DEPRECADOS (NO USAR):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ CLEAN_CODE_NAMING_PRINCIPLES_v2_1_0.md
❌ CLEAN_CODE_NAMING_PRINCIPLES_v2_2_0_PARTE_*.md
❌ CLEAN_CODE_NAMING_PRINCIPLES_v2_3_0_PARTE_*.md
❌ CLEAN_CODE_NAMING_PRINCIPLES_v2_3_1_PARTE_*.md (ERROR apps/core/)

USAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_1.md (Secciones 1-14)
✅ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_2.md (Secciones 15-18)
✅ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_3.md (Secciones 19-23)
✅ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_4.md (Secciones 24-27) ⭐
✅ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_5.md (Secciones 28-31) ⭐

DOCUMENTOS DE SOPORTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v3.0.0.md (base corrección)
✅ GUIA_CORE_VS_UTILS_v2.0.0.md (reglas apps/core/ vs apps/utils/)
✅ URLS_REPORTES_Y_DASHBOARDS.md (apps/dashboard/ documentado)
```

---

### **31.5 Resumen de Cambios por Parte**

```
PARTE 1/5: Principios Fundamentales
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Mantiene contenido válido de v2.3.1
✅ apps/dashboard/ incluido en Sección 9
✅ Importaciones corregidas en ejemplos

PARTE 2/5: Equilibrio + DRF Básico
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Sección 15 (Principio de Equilibrio) válida
✅ Sección 16 actualizada con apps/core/ correcto
✅ DRF ViewSets y Serializers válidos

PARTE 3/5: DRF Avanzado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Sección 22 actualizada (SoftDeleteViewSetMixin en core/)
✅ Permissions, Decorators, Middleware válidos
✅ Response y Exception Handling válidos

PARTE 4/5: IACT Específico ⭐ REESCRITA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Sección 24 (Pagination) válida
⭐ Sección 25 REESCRITA completamente
   - apps/core/ NO deprecado
   - apps/utils/ solo funciones
   - Arquitectura correcta documentada
✅ Sección 26 (Service Layer) válida
✅ Sección 27 actualizada (importaciones desde core/)

PARTE 5/5: Cierre ⭐ ACTUALIZADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Sección 28 (Anti-patterns) válida
⭐ Sección 29 actualizada (arquitectura correcta)
⭐ Sección 30 actualizada (referencias v3.0.1)
⭐ Sección 31 NUEVA (Changelog v3.0.1)
```

---

## 📊 RESUMEN FINAL v3.0.1

```
═══════════════════════════════════════════════════════════════════
CLEAN CODE NAMING PRINCIPLES v3.0.1 - DOCUMENTO COMPLETO
═══════════════════════════════════════════════════════════════════

ESTRUCTURA:
├─ 5 Partes
├─ 31 Secciones
└─ ARQUITECTURA CORREGIDA (apps/core/ vs apps/utils/)

CONTENIDO:
├─ 13 Principios Clean Code (Robert Martin)
├─ 5 Principios Clean Architecture (Robert Martin)
├─ 1 ⭐ Principio de Equilibrio
├─ 12 Patrones DRF
├─ 4 Patrones IACT Específicos (CORREGIDOS v3.0.1)
├─ 8 Anti-patterns
├─ 3 Tablas de Resumen (ACTUALIZADAS v3.0.1)
└─ Referencias Completas

APLICACIÓN:
✅ Proyecto: IACT Call Center System
✅ Framework: Django 4.2 + DRF 3.14
✅ Arquitectura: Clean Architecture + Service Layer
✅ Apps: core, utils, ivr, reports, dashboard, access, pipeline
✅ Base de Datos: MariaDB (IVR_LEGACY) + PostgreSQL (DEFAULT)

CORRECCIONES v3.0.1:
⭐ apps/core/ NO deprecado (fundamental)
⭐ apps/utils/ solo funciones helper
⭐ Arquitectura correcta documentada
⭐ Todas las importaciones corregidas

ESTADO:
✅ Completo
✅ Arquitectura correcta validada
✅ Listo para uso en desarrollo

VERSIÓN:
3.0.1 (18 enero 2026)
═══════════════════════════════════════════════════════════════════
```

---

**FIN DE PARTE 5/5**

**FIN DE DOCUMENTO COMPLETO v3.0.1**

---

## 🎯 SIGUIENTE PASO

Aplicar estos principios en todo el código IACT:

1. ✅ Corregir importaciones (apps/core/ en lugar de apps/utils/)
2. ✅ Verificar arquitectura con Checklist (Sección 29.3)
3. ✅ Revisar código existente
4. ✅ Refactorizar nombres verbosos usando Sección 15
5. ✅ Validar con linters (flake8, pylint, mypy)
6. ✅ Documentar decisiones de nomenclatura en PRs

---

**Documento generado:** 18 enero 2026  
**Versión:** 3.0.1  
**Estado:** COMPLETO (5/5 partes) - ARQUITECTURA CORREGIDA  
**Ubicación:** `/tmp/iact-real/docs/clean-code/`  

**Autores:**  
- Robert C. Martin (fundamentos Clean Code/Architecture)
- Equipo IACT (aplicación específica + correcciones arquitectónicas)

**Cambios v3.0.1:**
- ⭐ apps/core/ NO deprecado (modelos abstractos fundamentales)
- ⭐ apps/utils/ solo funciones helper (correcto)
- ⭐ Arquitectura apps/core/ vs apps/utils/ documentada
- ⭐ Todas las importaciones corregidas en 5 partes

---

**¡Código limpio con arquitectura correcta!** ✨
