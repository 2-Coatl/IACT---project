---
version: 2.0.0
date: 2026-01-19
project: IACT (Sistema Call Center)
type: Arquitectura Técnica
categoria: arquitectura/diseño
titulo: Arquitectura Real del Sistema ETL - Versión Definitiva
componente: ETL (Extract, Transform, Load)
tecnologias: MariaDB, Django, Stored Procedures
scope: Sistema completo (IVR Legacy → Django → API)
audiencia: Desarrolladores, Arquitectos Técnicos
estado: definitivo
base: Arquitectura Real Implementada
partes: 3/3
---

# ARQUITECTURA REAL DEL SISTEMA ETL - VERSIÓN DEFINITIVA

**PARTE 3/3: NOMENCLATURA, CONSTANTES Y REFERENCIAS**

---

## 📋 CONTENIDO DE ESTA PARTE

7. [Nomenclatura y Convenciones](#7-nomenclatura-y-convenciones)
8. [Constantes y Restricciones](#8-constantes-y-restricciones)
9. [Diagramas](#9-diagramas)
10. [Referencias](#10-referencias)

---

<a name="7-nomenclatura-y-convenciones"></a>
## 7. NOMENCLATURA Y CONVENCIONES

### 7.1 Nomenclatura de Tablas MariaDB

#### **7.1.1 Convención tbl_***

```yaml
Patrón: tbl_{tipo}_{detalle}_{año}
Prefijo: tbl_ (obligatorio para todas las tablas)

Razón:
  - Herencia del IVR Legacy
  - Distingue tablas IVR de otras en el mismo MariaDB
  - Se MANTIENE por compatibilidad (managed=False)

Ejemplos:
  - tbl_historico_t1_2025
  - tbl_historico_t2_2025
  - tbl_historico_t3_2025
  - tbl_reporte_trimestral
  - tbl_reporte_llamadas_abandonadas
  - tbl_reporte_clientes_unicos
  - tbl_reporte_transferencias
  - tbl_reporte_menu_errores
  - job_execution_log  (excepción: tabla de control, no usa tbl_)
```

---

#### **7.1.2 Nomenclatura de Campos**

```yaml
Nomenclatura Húngara del Dominio IVR:
  
  IMPORTANTE:
  Esta NO es notación húngara moderna (anti-pattern).
  Es la nomenclatura ORIGINAL del IVR Legacy que se MANTIENE
  porque Django usa managed=False (no gestiona el schema).

Prefijos:
  d*  = date/datetime (fecha/hora)
      Ejemplos: dFecha, dHora, dFechaHora
  
  c*  = código/char (texto/cadena)
      Ejemplos: cMenu, cOpcion, cDID_800Transfer, cTelefono_Origen
  
  n*  = numérico (entero/decimal)
      Ejemplos: nDuracionSegundos, nTiempoEsperaSegundos
  
  (sin prefijo) = campos estándar de Django
      Ejemplos: id, created_at, updated_at

Razón de mantener esta nomenclatura:
  ✅ Schema lo gestiona el IVR/ETL (no Django)
  ✅ Django solo LEE (managed=False)
  ✅ Cambiar nombres rompería compatibilidad
  ✅ Query SQL del ETL usa estos nombres
```

---

#### **7.1.3 Tabla de Campos Comunes**

```
┌────────────────────────────┬──────────┬──────────────────────┐
│ Campo MariaDB              │ Tipo     │ Significado          │
├────────────────────────────┼──────────┼──────────────────────┤
│ dFecha                     │ DATE     │ Fecha de llamada     │
│ dHora                      │ TIME     │ Hora de llamada      │
│ dFechaHora                 │ DATETIME │ Timestamp completo   │
│ cDID_800Transfer           │ VARCHAR  │ DID receptor         │
│ cTelefono_Origen           │ VARCHAR  │ Número cliente       │
│ cMenu                      │ VARCHAR  │ Menú IVR             │
│ cOpcion                    │ VARCHAR  │ Opción menú          │
│ cSubOpcion                 │ VARCHAR  │ Sub-opción           │
│ cTipoLlamada               │ VARCHAR  │ ENTRANTE/SALIENTE    │
│ cEstado                    │ VARCHAR  │ COMPLETADA/ABANDONADA│
│ cResultado                 │ VARCHAR  │ Resultado final      │
│ nDuracionSegundos          │ INT      │ Duración total       │
│ nTiempoEsperaSegundos      │ INT      │ Tiempo en cola       │
│ nTiempoConversacionSegundos│ INT      │ Tiempo con agente    │
│ cAgenteID                  │ VARCHAR  │ ID del agente        │
│ cAgenteName                │ VARCHAR  │ Nombre agente        │
│ cCola                      │ VARCHAR  │ Cola de atención     │
│ cCiudad                    │ VARCHAR  │ Ciudad llamante      │
│ cEstado                    │ VARCHAR  │ Estado/Provincia     │
│ created_at                 │ TIMESTAMP│ Creación registro    │
│ updated_at                 │ TIMESTAMP│ Última actualización │
└────────────────────────────┴──────────┴──────────────────────┘
```

---

### 7.2 Nomenclatura Django

#### **7.2.1 Modelos Django**

```yaml
Convención: PascalCase (sin prefijos)

Reglas:
  - Nombres descriptivos en inglés
  - Singular (no plural)
  - Sin prefijos tbl_ (Django lo añade si es necesario)
  - Sigue CLEAN_CODE v3.0.1 Principio de Equilibrio (1-4 palabras)

Ejemplos CORRECTOS:
  ✅ CallRecord           (2 palabras)
  ✅ CallRecord
  ✅ CallRecord
  ✅ QuarterlyReport     (2 palabras)
  ✅ ReporteAbandonedCall  (3 palabras)
  ✅ ReporteUniqueClient      (3 palabras)
  ✅ TransferDetail      (2 palabras)
  ✅ MenuError         (3 palabras)
  ✅ JobExecutionLog            (3 palabras)

Ejemplos INCORRECTOS:
  ❌ TblHistoricoT1       (incluye prefijo tbl_, usa español)
  ❌ HistoricoTrimestre1   (verboso)
  ❌ H1                    (demasiado corto)
  ❌ HistoricoDeTodasLasLlamadasDelPrimerTrimestreDelAnio2025  (verboso excesivo)
```

---

#### **7.2.2 Nombres de Campos en Modelos**

```yaml
Regla General:
  - Campos en inglés (variables de código)
  - verbose_name en español (UI/Admin)
  - Mantener nombres originales si managed=False

Ejemplo:
  class CallRecord(models.Model):
      # Campo original del IVR (se mantiene)
      dFecha = models.DateField(
          verbose_name="Fecha",  # ← Español para UI
          help_text="Fecha de la llamada"
      )
      
      # Campo de Django (inglés)
      created_at = models.DateTimeField(
          auto_now_add=True,
          verbose_name="Creado en"  # ← Español para UI
      )

EXCEPCIÓN para apps/ivr/:
  - Mantener nomenclatura húngara del IVR
  - Razón: managed=False, schema es del IVR
  - NO renombrar: dFecha, cMenu, nDuracionSegundos

Para otras apps (reports/, dashboard/):
  - Usar inglés estándar
  - Ejemplo: created_at, updated_at, is_active
```

---

#### **7.2.3 Vistas (ViewSets)**

```yaml
Convención: {Modelo}ViewSet

Ejemplos:
  ✅ AbandonedCallViewSet
  ✅ UniqueClientViewSet
  ✅ DetalleTransferenciasViewSet
  ✅ MenuErroresViewSet
  ✅ MetricasTrimestralesViewSet
  ✅ AnalisisClientesViewSet
  ✅ PerformanceIVRViewSet
  ✅ PipelineViewSet

Regla:
  - PascalCase
  - Nombre descriptivo del recurso + ViewSet
  - 2-5 palabras (CLEAN_CODE v3.0.1)
```

---

#### **7.2.4 Servicios**

```yaml
Convención: {Dominio}Service

Ejemplos:
  ✅ ReportService
  ✅ DashboardService
  ✅ ETLMonitoringService
  ✅ AccessService
  ✅ UserService

Regla:
  - PascalCase
  - Nombre del dominio + Service
  - 1-3 palabras
  - Clase única por archivo services.py
```

---

#### **7.2.5 Serializers**

```yaml
Convención: {Modelo}Serializer o {Propósito}Serializer

Ejemplos:
  ✅ ReportMetricsSerializer
  ✅ AbandonedCallRequestSerializer
  ✅ DashboardWidgetSerializer
  ✅ JobExecutionLogSerializer

Regla:
  - PascalCase
  - Descriptivo del propósito + Serializer
  - 2-4 palabras
```

---

### 7.3 URLs y Endpoints

#### **7.3.1 Convención de URLs**

```yaml
Patrón: /api/v1/{app}/{recurso}/

Reglas:
  - Lowercase con guiones (kebab-case)
  - Versión explícita (v1)
  - Plural para colecciones
  - Verbos HTTP (no en URL)

Ejemplos CORRECTOS:
  ✅ /api/v1/reports/llamadas-abandonadas/
  ✅ /api/v1/reports/clientes-unicos/
  ✅ /api/v1/dashboard/metricas-trimestrales/
  ✅ /api/v1/pipeline/status/

Ejemplos INCORRECTOS:
  ❌ /api/reports/getAbandonedCall/    (verbo en URL)
  ❌ /api/v1/Reports/AbandonedCall/    (PascalCase)
  ❌ /api/v1/reports/llamadas_abandonadas/   (snake_case)
  ❌ /llamadas-abandonadas/                  (sin versión)
```

---

#### **7.3.2 Tabla de URLs Completa**

```
┌─────────────────────────────────────────────┬────────┬──────────┐
│ URL                                         │ Method │ RBAC     │
├─────────────────────────────────────────────┼────────┼──────────┤
│ REPORTES                                    │        │          │
├─────────────────────────────────────────────┼────────┼──────────┤
│ /api/v1/reports/llamadas-abandonadas/      │ POST   │ reports.view │
│ /api/v1/reports/clientes-unicos/           │ POST   │ reports.view │
│ /api/v1/reports/promedio-clientes/         │ POST   │ reports.view │
│ /api/v1/reports/clientes-menu/             │ POST   │ reports.view │
│ /api/v1/reports/llamadas-menu/             │ POST   │ reports.view │
│ /api/v1/reports/detalle-transferencias/    │ POST   │ reports.view │
│ /api/v1/reports/menu-errores/              │ POST   │ reports.view │
├─────────────────────────────────────────────┼────────┼──────────┤
│ DASHBOARDS                                  │        │          │
├─────────────────────────────────────────────┼────────┼──────────┤
│ /api/v1/dashboard/metricas-trimestrales/   │ GET    │ dashboard.view │
│ /api/v1/dashboard/analisis-clientes/       │ GET    │ dashboard.view │
│ /api/v1/dashboard/performance-ivr/         │ GET    │ dashboard.view │
├─────────────────────────────────────────────┼────────┼──────────┤
│ PIPELINE                                    │        │          │
├─────────────────────────────────────────────┼────────┼──────────┤
│ /api/v1/pipeline/status/                   │ GET    │ pipeline.monitor │
├─────────────────────────────────────────────┼────────┼──────────┤
│ ACCESO                                      │        │          │
├─────────────────────────────────────────────┼────────┼──────────┤
│ /api/v1/access/functions/                  │ GET    │ access.view │
│ /api/v1/access/agrupadores/                │ GET    │ access.view │
└─────────────────────────────────────────────┴────────┴──────────┘

Total: 14 endpoints principales
```

---

### 7.4 Aplicación de CLEAN_CODE v3.0.1

#### **7.4.1 Principio de Equilibrio**

```yaml
Referencia: CLEAN_CODE_NAMING_PRINCIPLES v3.0.1 Sección 15

Reglas de Longitud por Scope:

Loop Variables (1 palabra):
  for i in range(10):          ✅
  for record in records:       ✅
  for trimestre in ['Q1', 'Q2', 'Q3']:  ✅

Local Variables (1-2 palabras):
  start_date = ...             ✅
  did_name = ...               ✅
  total_records = ...          ✅

Function Parameters (2-3 palabras):
  def validate_date_range(start_date, end_date):  ✅
  def get_report_data(trimestre, did):            ✅

Function Names (2-5 palabras):
  get_trimestre_from_date()    ✅ (4 palabras)
  validate_date_range()        ✅ (3 palabras)
  calculate_metrics()          ✅ (2 palabras)

Class Names (1-4 palabras):
  ReportService                ✅ (2 palabras)
  CallRecord                  ✅ (2 palabras)
  JobExecutionLog              ✅ (3 palabras)

EVITAR:
  execution_date_and_time_for_etl_processing  ❌ (verboso excesivo)
  total_number_of_records_processed           ❌ (verboso excesivo)
  
  Mejor:
  start_time                   ✅
  processed_count              ✅
```

---

#### **7.4.2 Anti-patterns Evitados**

```yaml
ANTI-PATTERN 1: Nombres Genéricos
  ❌ data, info, obj, temp, result
  ✅ report_data, user_info, call_record, cache_key, metrics

ANTI-PATTERN 2: Notación Húngara Moderna (NO confundir con IVR)
  ❌ strName, intCount, lstRecords, dictFilters
  ✅ name, count, records, filters
  
  EXCEPCIÓN: IVR Legacy (dFecha, cMenu, nDuracion)
  Razón: Schema original del IVR, managed=False

ANTI-PATTERN 3: Abreviaciones Ambiguas
  ❌ usr, rpt, fn, cfg, ctx
  ✅ user, report, function, config, context
  
  EXCEPCIÓN: Abreviaciones universales
  ✅ id, url, api, etl, pdf, csv, did

ANTI-PATTERN 4: Números en Nombres
  ❌ data1, data2, result1, result2
  ✅ raw_data, transformed_data, initial_result, final_result
  
  EXCEPCIÓN: Nombres del dominio
  ✅ CallRecord, CallRecord, CallRecord (T1 = Trimestre 1)

ANTI-PATTERN 5: Verbosidad Excesiva
  ❌ execution_date_and_time_of_etl_processing
  ✅ start_time
  
  ❌ total_number_of_records_processed_successfully
  ✅ processed_count

ANTI-PATTERN 6: Mezcla de Idiomas
  ❌ ReporteService (mezcla español/inglés)
  ❌ get_datos()
  ❌ obtener_user()
  
  ✅ ReportService (todo inglés)
  ✅ get_data()
  ✅ get_user()
```

---

### 7.5 Regla de Idioma

```yaml
Referencia: CLEAN_CODE v3.0.1 Sección 14

CÓDIGO: Inglés
  - Nombres de variables
  - Nombres de funciones
  - Nombres de clases
  - URLs
  - Nombres de archivos

DOCUMENTACIÓN: Español
  - Docstrings
  - Comentarios
  - verbose_name
  - help_text
  - README.md (del proyecto IACT)

IDENTIFICADORES DE FUNCIÓN: Inglés
  - function.code: 'reports.view' (inglés)
  - function.name: 'Ver Reportes' (español)

NOMBRES DE DISPLAY: Español
  - Interfaces de usuario
  - Mensajes de error mostrados al usuario
  - Nombres de menús en frontend

Ejemplo:
  class ReportService:  # ← Inglés (código)
      """
      Servicio de reportes.  # ← Español (docstring)
      
      Responsabilidades:
      - Validación de reglas de negocio
      - Consultas a MariaDB
      """
      
      @staticmethod
      def validate_date_range(  # ← Inglés (código)
          start_date: date,     # ← Inglés (código)
          end_date: date
      ) -> None:
          """
          Valida rango de fechas.  # ← Español (docstring)
          
          Args:
              start_date: Fecha inicio
              end_date: Fecha fin
          """
          if end_date < start_date:
              raise ValidationError(
                  "Fecha fin debe ser mayor o igual a fecha inicio"  # ← Español (mensaje usuario)
              )
```

---

<a name="8-constantes-y-restricciones"></a>
## 8. CONSTANTES Y RESTRICCIONES

### 8.1 Constantes del Sistema

#### **8.1.1 CNST-004: ETL_TIMEOUT_SECONDS**

```python
# apps/ivr/constants.py

ETL_TIMEOUT_SECONDS = 300  # 5 minutos

"""
CNST-004: Timeout máximo para ejecución del ETL.

Valor: 300 segundos (5 minutos)

Razón:
  - ETL diario toma ~10-15 minutos en promedio
  - Timeout de 5 min es para CADA INTENTO
  - Script bash hace 3 reintentos (total: 15 min)

Uso:
  - Script bash: timeout $TIMEOUT mysql ...
  - Cron log: /var/log/etl/etl_daily_YYYYMMDD.log

Validación:
  - Si ETL excede 5 min en un intento → TIMEOUT
  - Script reintenta automáticamente
  - Si 3 intentos fallan → Alerta manual

Referencias:
  - /usr/local/bin/run_etl.sh (línea 15)
  - Cron: /etc/cron.d/etl-daily
"""
```

---

#### **8.1.2 CNST-005: SOFT_DELETE_REQUIRED**

```python
# apps/utils/constants.py

SOFT_DELETE_REQUIRED = True

"""
CNST-005: Soft delete obligatorio en tablas DEFAULT (PostgreSQL).

Valor: True (obligatorio)

Razón:
  - Auditoría de datos
  - Recuperación de información
  - Cumplimiento normativo

Implementación:
  - SoftDeleteMixin en apps/core/models.py
  - Campo: is_deleted (BooleanField)
  - Campo: deleted_at (DateTimeField)

Uso:
  class Report(SoftDeleteMixin, models.Model):
      # ... campos ...
      pass

Métodos:
  - report.soft_delete()  # Marca como eliminado
  - Report.objects.alive()  # Solo no eliminados
  - Report.objects.deleted()  # Solo eliminados
  - Report.objects.all_with_deleted()  # Todos

EXCEPCIÓN:
  - apps/ivr/ NO usa soft delete (managed=False)
  - MariaDB lo gestiona el ETL

Referencias:
  - apps/core/models.py (SoftDeleteMixin)
  - CLEAN_CODE v3.0.1 Sección 5.3
"""
```

---

#### **8.1.3 CNST-006: REPORT_MAX_DATE_RANGE_DAYS**

```python
# apps/reports/constants.py

REPORT_MAX_DATE_RANGE_DAYS = 730  # 2 años

"""
CNST-006: Rango máximo de fechas permitido en reportes.

Valor: 730 días (2 años / 24 meses)

Razón:
  - Performance: Consultas >2 años tardan mucho
  - Memoria: Riesgo de OOM con datasets grandes
  - Uso típico: Usuarios consultan 3-6 meses

Validación:
  - ReportService.validate_date_range()
  - Lanza ValidationError si rango > 730 días

Ejemplo:
  start_date = date(2023, 1, 1)
  end_date = date(2025, 1, 1)
  date_range = (end_date - start_date).days  # 730 días
  
  if date_range > REPORT_MAX_DATE_RANGE_DAYS:
      raise ValidationError("Rango máximo: 730 días")

Workaround:
  - Usuario puede hacer múltiples requests
  - Request 1: 2023-01-01 a 2024-01-01
  - Request 2: 2024-01-01 a 2025-01-01

Referencias:
  - apps/reports/services.py (ReportService)
  - apps/reports/serializers.py (validación)
"""
```

---

#### **8.1.4 CNST-007: MAX_EXPORT_RECORDS**

```python
# apps/reports/constants.py

MAX_EXPORT_RECORDS = 100000  # 100k registros

"""
CNST-007: Límite máximo de registros para exportación.

Valor: 100,000 registros

Razón:
  - Excel: Límite práctico ~65k (XLS) o 1M (XLSX)
  - Memoria: Evitar OOM al generar archivos grandes
  - Performance: Archivos >100k son lentos de generar
  - UX: Archivos muy grandes son difíciles de abrir

Validación:
  - ReportService.get_report_data()
  - Lanza ValidationError si len(records) > 100k

Comportamiento:
  - Si query retorna >100k → Error claro
  - Usuario debe refinar filtros (fecha, DID, menú)

Ejemplo:
  records = get_call_records(...)
  
  if len(records) > MAX_EXPORT_RECORDS:
      raise ValidationError(
          f"Límite de {MAX_EXPORT_RECORDS} registros excedido. "
          f"Total: {len(records)}. Refine los filtros."
      )

Alternativa (futuro):
  - Job asíncrono con Celery para >100k
  - Exportación por lotes (batch export)
  - Streaming de datos grandes

Referencias:
  - apps/reports/services.py
  - apps/reports/views.py (mensaje de error)
"""
```

---

### 8.2 Tabla de Constantes Completa

```
┌────────┬─────────────────────────────┬──────────┬───────────────────┐
│ Código │ Nombre                      │ Valor    │ Scope             │
├────────┼─────────────────────────────┼──────────┼───────────────────┤
│ CNST-004│ ETL_TIMEOUT_SECONDS        │ 300      │ ETL / Pipeline    │
│ CNST-005│ SOFT_DELETE_REQUIRED       │ True     │ Global (DEFAULT)  │
│ CNST-006│ REPORT_MAX_DATE_RANGE_DAYS │ 730      │ Reports           │
│ CNST-007│ MAX_EXPORT_RECORDS         │ 100,000  │ Reports           │
└────────┴─────────────────────────────┴──────────┴───────────────────┘
```

---

### 8.3 DIDs Permitidos

```python
# apps/ivr/constants.py

# DIDs del sistema
DID_PUEBLA = '19020084'
DID_NACIONAL_A = '19028031'
DID_NACIONAL_B = '19020001'

ALLOWED_DIDS = [
    DID_PUEBLA,
    DID_NACIONAL_A,
    DID_NACIONAL_B,
]

# Mapeo DID → Nombre legible
DID_NAMES = {
    '19020084': 'Puebla',
    '19028031': 'Nacional A',
    '19020001': 'Nacional B',
}

def get_did_name(did: str) -> str:
    """
    Obtiene nombre legible del DID.
    
    Args:
        did: DID numérico (ej: '19020084')
    
    Returns:
        Nombre legible (ej: 'Puebla')
    
    Raises:
        ValueError: Si DID no está en DID_NAMES
    """
    if did not in DID_NAMES:
        raise ValueError(f"DID {did} no reconocido")
    return DID_NAMES[did]

def validate_did(did: str) -> None:
    """
    Valida que el DID sea permitido.
    
    Args:
        did: DID a validar
    
    Raises:
        ValueError: Si DID no está en ALLOWED_DIDS
    """
    if did not in ALLOWED_DIDS:
        raise ValueError(
            f"DID '{did}' no permitido. "
            f"DIDs válidos: {', '.join(ALLOWED_DIDS)}"
        )
```

---

### 8.4 Trimestres

```python
# apps/ivr/constants.py

# Trimestres soportados
TRIMESTRES = ['Q1', 'Q2', 'Q3']

# Mapeo trimestre → meses
TRIMESTRE_MESES = {
    'Q1': (1, 2, 3),      # Enero-Marzo
    'Q2': (4, 5, 6),      # Abril-Junio
    'Q3': (7, 8, 9),      # Julio-Septiembre
}

# Mapeo trimestre → nombre tabla
TRIMESTRE_TABLA = {
    'Q1': 'tbl_historico_t1_2025',
    'Q2': 'tbl_historico_t2_2025',
    'Q3': 'tbl_historico_t3_2025',
}

def validate_trimestre(trimestre: str) -> None:
    """Valida que el trimestre sea válido."""
    if trimestre not in TRIMESTRES:
        raise ValueError(
            f"Trimestre '{trimestre}' no válido. "
            f"Trimestres válidos: {', '.join(TRIMESTRES)}"
        )
```

---

### 8.5 Estados de Llamada

```python
# apps/ivr/constants.py

# Estados de llamada (cEstado)
ESTADO_COMPLETADA = 'COMPLETADA'
ESTADO_ABANDONADA = 'ABANDONADA'
ESTADO_TRANSFERIDA = 'TRANSFERIDA'

ESTADOS_VALIDOS = [
    ESTADO_COMPLETADA,
    ESTADO_ABANDONADA,
    ESTADO_TRANSFERIDA,
]

# Tipos de llamada (cTipoLlamada)
TIPO_ENTRANTE = 'ENTRANTE'
TIPO_SALIENTE = 'SALIENTE'
TIPO_INTERNA = 'INTERNA'

TIPOS_VALIDOS = [
    TIPO_ENTRANTE,
    TIPO_SALIENTE,
    TIPO_INTERNA,
]
```

---

### 8.6 Configuración de Cache

```python
# config/settings/base.py

# Cache (Redis)
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos

# Cache específico para dashboards
DASHBOARD_CACHE_TIMEOUT = 300  # 5 minutos
DASHBOARD_CACHE_KEY_PREFIX = 'dashboard'

# Cache específico para reportes (más largo)
REPORT_METADATA_CACHE_TIMEOUT = 3600  # 1 hora
```

---

### 8.7 Límites de Paginación

```python
# config/settings/base.py

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,  # Default
}

# Paginación específica por app
REPORTS_PAGE_SIZE = 50
DASHBOARD_PAGE_SIZE = 100  # Dashboards pueden tener más datos
PIPELINE_PAGE_SIZE = 20
```

---

<a name="9-diagramas"></a>
## 9. DIAGRAMAS

### 9.1 Diagrama de Arquitectura General

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA GENERAL DEL SISTEMA                      │
│                         IACT Call Center ETL                             │
└──────────────────────────────────────────────────────────────────────────┘

┌───────────────────┐
│   IVR Legacy      │  Sistema PBX (fuera de Django)
│   (Sistema PBX)   │  Genera CDRs en tiempo real
└─────────┬─────────┘
          │
          │ Inserta CDRs
          ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATABASE: MariaDB                                │
│                         (IVR_LEGACY)                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ TABLAS FUENTE (Raw Data)                                         │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ • tbl_historico_t1_2025  (Q1: Ene-Mar)                          │  │
│  │ • tbl_historico_t2_2025  (Q2: Abr-Jun)                          │  │
│  │ • tbl_historico_t3_2025  (Q3: Jul-Sep)                          │  │
│  │                                                                  │  │
│  │ Campos: dFecha, cMenu, cDID, nDuracion, etc.                    │  │
│  │ Registros: ~8,920 nuevos/día                                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ PROCESO ETL (Stored Procedure)                                   │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Nombre: sp_etl_daily()                                           │  │
│  │ Trigger: Cron diario 2:00 AM                                     │  │
│  │ Duración: ~10-15 minutos                                         │  │
│  │                                                                  │  │
│  │ Transformaciones:                                                │  │
│  │ ├─ q_REPTRIM021 → Llamadas Abandonadas                          │  │
│  │ ├─ q_REPTRIM011 → Clientes Únicos                               │  │
│  │ ├─ q_REPTRIM031 → Promedio Clientes                             │  │
│  │ ├─ q_REP_DETALLE → Transferencias                               │  │
│  │ └─ q_cMENU_ERROR → Errores de Menú                              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ TABLAS AGREGADAS (ETL Output)                                    │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ • tbl_reporte_trimestral                                         │  │
│  │ • tbl_reporte_llamadas_abandonadas                               │  │
│  │ • tbl_reporte_clientes_unicos                                    │  │
│  │ • tbl_reporte_transferencias                                     │  │
│  │ • tbl_reporte_menu_errores                                       │  │
│  │                                                                  │  │
│  │ Actualización: Diaria (acumulativa)                              │  │
│  │ Registros: ~85 nuevos/día                                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ TABLA DE CONTROL                                                 │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ • job_execution_log                                              │  │
│  │   - Registra cada ejecución del ETL                              │  │
│  │   - Estados: RUNNING, SUCCESS, FAILED                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
          │
          │ Django lee (READONLY)
          │ Database Router: 'ivr_legacy'
          │ Usuario: ivr_readonly (SELECT only)
          ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         DJANGO APPLICATION                              │
│                          (Python 3.11+)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ APPS (Arquitectura de Capas)                                     │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │ apps/ivr/                                                        │  │
│  │ ├─ models.py      → Modelos (managed=False)                     │  │
│  │ ├─ constants.py   → DIDs, Trimestres                            │  │
│  │ └─ utils.py       → Helpers                                      │  │
│  │                                                                  │  │
│  │ apps/reports/                                                    │  │
│  │ ├─ views.py       → ViewSets (API)                              │  │
│  │ ├─ services.py    → ReportService (lógica)                      │  │
│  │ ├─ serializers.py → Serialización                               │  │
│  │ └─ permissions.py → RBAC                                         │  │
│  │                                                                  │  │
│  │ apps/dashboard/                                                  │  │
│  │ ├─ views.py       → DashboardViewSet                            │  │
│  │ ├─ services.py    → DashboardService                            │  │
│  │ └─ widgets.py     → Widget System                               │  │
│  │                                                                  │  │
│  │ apps/pipeline/                                                   │  │
│  │ ├─ views.py       → PipelineViewSet                             │  │
│  │ └─ services.py    → ETLMonitoringService                        │  │
│  │                                                                  │  │
│  │ apps/access/                                                     │  │
│  │ ├─ models.py      → Function, Agrupador                         │  │
│  │ ├─ decorators.py  → @require_function                           │  │
│  │ └─ middleware.py  → AccessAuditMiddleware                       │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ DATABASE ROUTER                                                   │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ config/routers.py → IVRRouter                                    │  │
│  │                                                                  │  │
│  │ apps/ivr/        → 'ivr_legacy' (MariaDB)                       │  │
│  │ apps/reports/    → 'default' (PostgreSQL)                       │  │
│  │ apps/dashboard/  → 'default' + 'ivr_legacy'                     │  │
│  │ apps/pipeline/   → 'ivr_legacy' (readonly)                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
          │
          │ Django REST Framework
          │
          ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         REST API (DRF 3.14+)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  REPORTES (POST - Generación bajo demanda)                             │
│  ├─ POST /api/v1/reports/llamadas-abandonadas/                         │
│  ├─ POST /api/v1/reports/clientes-unicos/                              │
│  ├─ POST /api/v1/reports/promedio-clientes/                            │
│  ├─ POST /api/v1/reports/clientes-menu/                                │
│  ├─ POST /api/v1/reports/llamadas-menu/                                │
│  ├─ POST /api/v1/reports/detalle-transferencias/                       │
│  └─ POST /api/v1/reports/menu-errores/                                 │
│                                                                         │
│  DASHBOARDS (GET - Visualización en vivo)                              │
│  ├─ GET /api/v1/dashboard/metricas-trimestrales/                       │
│  ├─ GET /api/v1/dashboard/analisis-clientes/                           │
│  └─ GET /api/v1/dashboard/performance-ivr/                             │
│                                                                         │
│  PIPELINE (GET - Monitoreo)                                            │
│  └─ GET /api/v1/pipeline/status/                                       │
│                                                                         │
│  AUTENTICACIÓN: Token (Bearer)                                         │
│  RBAC: @require_function decorator                                     │
│  RATE LIMITING: 100 req/hora                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
          │
          │ HTTP/JSON
          │
          ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React/Vue)                               │
│                        (Fuera de scope)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  • Visualización de reportes                                           │
│  • Dashboards interactivos (Charts, KPIs, Tables)                      │
│  • Descarga de archivos (Excel, CSV)                                   │
│  • Gestión de usuarios y permisos                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     DATABASE: PostgreSQL                                │
│                          (DEFAULT)                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  • Usuarios (User, Profile)                                            │
│  • Acceso (Function, Agrupador, UserFunction)                          │
│  • Metadata de reportes (Report, ReportJob)                            │
│  • Auditoría (AccessLog, ActionLog)                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         CACHE: Redis                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  • Cache de dashboards (5 min TTL)                                     │
│  • Session storage                                                      │
│  • Rate limiting counters                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 9.2 Diagrama de Flujo ETL

```
┌──────────────────────────────────────────────────────────────────┐
│              FLUJO ETL DIARIO - sp_etl_daily()                   │
└──────────────────────────────────────────────────────────────────┘

                    [02:00 AM - Cron Trigger]
                              │
                              ↓
                    ┌─────────────────────┐
                    │ run_etl.sh ejecuta  │
                    └─────────┬───────────┘
                              │
                              ↓
                    ┌─────────────────────┐
                    │ Conecta a MariaDB   │
                    └─────────┬───────────┘
                              │
                              ↓
                    ┌─────────────────────────────────┐
                    │ CALL sp_etl_daily();            │
                    └─────────┬───────────────────────┘
                              │
                              ↓
          ┌───────────────────────────────────────────────┐
          │ INSERT job_execution_log                      │
          │ SET status='RUNNING', start_time=NOW()        │
          └───────────────────┬───────────────────────────┘
                              │
                              ↓
          ┌───────────────────────────────────────────────┐
          │ Determinar trimestre actual                   │
          │ @trimestre = 'Q1' | 'Q2' | 'Q3'              │
          └───────────────────┬───────────────────────────┘
                              │
                              ↓
          ┌───────────────────────────────────────────────┐
          │ Seleccionar tabla fuente                      │
          │ IF @trimestre='Q1' → tbl_historico_t1_2025   │
          │ IF @trimestre='Q2' → tbl_historico_t2_2025   │
          │ IF @trimestre='Q3' → tbl_historico_t3_2025   │
          └───────────────────┬───────────────────────────┘
                              │
                              ↓
          ┌───────────────────────────────────────────────┐
          │ LEER datos del día anterior                   │
          │ SELECT * FROM tbl_historico_t*                │
          │ WHERE dFecha = CURDATE() - INTERVAL 1 DAY     │
          │                                               │
          │ Registros extraídos: ~8,920                   │
          └───────────────────┬───────────────────────────┘
                              │
                              ↓
          ┌───────────────────────────────────────────────┐
          │ TRANSFORMAR datos (7 queries SQL)             │
          └───────────────────┬───────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ↓               ↓               ↓
    ┌─────────────────┐ ┌──────────────┐ ┌────────────────┐
    │ q_REPTRIM021    │ │ q_REPTRIM011 │ │ q_REPTRIM031   │
    │ Abandonadas     │ │ Clientes U.  │ │ Prom. Clientes │
    └────────┬────────┘ └──────┬───────┘ └───────┬────────┘
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ↓                ↓                ↓
    ┌─────────────────┐ ┌──────────────┐ ┌────────────────┐
    │ q_REPTRIM041    │ │ q_REPTRIM121 │ │ q_REP_DETALLE  │
    │ Clientes Menú   │ │ Llamadas Menú│ │ Transferencias │
    └────────┬────────┘ └──────┬───────┘ └───────┬────────┘
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
                               ↓
                    ┌──────────────────────┐
                    │ q_cMENU_ERROR        │
                    │ Errores de Menú      │
                    └──────────┬───────────┘
                               │
                               ↓
          ┌───────────────────────────────────────────────┐
          │ CARGAR datos agregados                        │
          │ INSERT INTO tbl_reporte_*                     │
          │ ... ON DUPLICATE KEY UPDATE ...               │
          │                                               │
          │ Registros cargados: ~85                       │
          └───────────────────┬───────────────────────────┘
                              │
                              ↓
                  ┌───────────────────────┐
                  │ ¿Hubo errores?        │
                  └───────┬───────────────┘
                          │
                 ┌────────┴────────┐
                 │                 │
                NO                SI
                 │                 │
                 ↓                 ↓
      ┌──────────────────┐  ┌─────────────────────┐
      │ UPDATE           │  │ UPDATE              │
      │ job_execution_log│  │ job_execution_log   │
      │ SET              │  │ SET                 │
      │ status='SUCCESS' │  │ status='FAILED'     │
      │ end_time=NOW()   │  │ error_message='...' │
      │ records_loaded=85│  │ end_time=NOW()      │
      └──────┬───────────┘  └─────────┬───────────┘
             │                        │
             └────────┬───────────────┘
                      │
                      ↓
              ┌───────────────┐
              │ COMMIT        │
              └───────┬───────┘
                      │
                      ↓
              ┌───────────────┐
              │ Retornar EXIT │
              │ CODE: 0|1     │
              └───────┬───────┘
                      │
                      ↓
              ┌───────────────────────┐
              │ run_etl.sh verifica   │
              │ exit code             │
              └───────┬───────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
    EXIT 0                    EXIT 1
         │                         │
         ↓                         ↓
┌────────────────┐      ┌──────────────────┐
│ Log: SUCCESS   │      │ Log: FAILED      │
│ Finalizar      │      │ Reintentar (3x)  │
└────────────────┘      └──────────────────┘
```

---

### 9.3 Diagrama ER (Tablas MariaDB)

```
┌──────────────────────────────────────────────────────────────────┐
│        DIAGRAMA ENTIDAD-RELACIÓN - DATABASE: ivr_database        │
│                         (MariaDB)                                │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ tbl_historico_t1_2025                                           │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id (BIGINT AUTO_INCREMENT)                                 │
│    │ dFecha (DATE)                                              │
│    │ dHora (TIME)                                               │
│    │ dFechaHora (DATETIME)                                      │
│ FK?│ cDID_800Transfer (VARCHAR) ──┐                             │
│    │ cTelefono_Origen (VARCHAR)   │                             │
│    │ cMenu (VARCHAR)               │                             │
│    │ cOpcion (VARCHAR)             │                             │
│    │ cSubOpcion (VARCHAR)          │                             │
│    │ cTipoLlamada (VARCHAR)        │                             │
│    │ cEstado (VARCHAR)             │                             │
│    │ cResultado (VARCHAR)          │                             │
│    │ nDuracionSegundos (INT)       │                             │
│    │ nTiempoEsperaSegundos (INT)   │                             │
│    │ nTiempoConversacionSegundos   │                             │
│    │ cAgenteID (VARCHAR)           │                             │
│    │ cAgenteName (VARCHAR)         │                             │
│    │ cCola (VARCHAR)               │                             │
│    │ cCiudad (VARCHAR)             │                             │
│    │ cEstado (VARCHAR)             │                             │
│    │ created_at (TIMESTAMP)        │                             │
└─────────────────────────────────────┘                             │
                                      │                             │
┌─────────────────────────────────────┼─────────────────────────────┼
│ tbl_historico_t2_2025               │                             │
├─────────────────────────────────────┘ (MISMA ESTRUCTURA)          │
│ ... (mismos campos que t1)                                        │
└───────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼─────────────────────────────┐
│ tbl_historico_t3_2025               │                             │
├─────────────────────────────────────┘                             │
│ ... (mismos campos que t1)                                        │
└───────────────────────────────────────────────────────────────────┘
                                      │
                                      │ ETL (sp_etl_daily)
                                      │ Agrega datos
                                      ↓
┌─────────────────────────────────────────────────────────────────┐
│ tbl_reporte_trimestral                                          │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id (BIGINT)                                                │
│    │ trimestre (VARCHAR)  'Q1'|'Q2'|'Q3'                        │
│    │ anio (INT)                                                 │
│    │ fecha (DATE)                                               │
│    │ servicio_800 (VARCHAR)  'Puebla'|'Nacional A'|...          │
│    │ total_llamadas (INT)                                       │
│    │ llamadas_completadas (INT)                                 │
│    │ llamadas_abandonadas (INT)                                 │
│    │ llamadas_transferidas (INT)                                │
│    │ clientes_unicos (INT)                                      │
│    │ duracion_promedio_seg (INT)                                │
│    │ tiempo_espera_promedio_seg (INT)                           │
│    │ tiempo_conversacion_promedio_seg (INT)                     │
│    │ tasa_abandono (DECIMAL)                                    │
│    │ created_at (TIMESTAMP)                                     │
│    │ updated_at (TIMESTAMP)                                     │
│ UK │ UNIQUE(trimestre, anio, fecha, servicio_800)               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ tbl_reporte_llamadas_abandonadas                                │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id (BIGINT)                                                │
│    │ trimestre (VARCHAR)                                        │
│    │ fecha (DATE)                                               │
│    │ did (VARCHAR)                                              │
│    │ menu (VARCHAR)                                             │
│    │ total_abandonadas (INT)                                    │
│    │ tiempo_espera_promedio_seg (INT)                           │
│    │ abandonadas_antes_30seg (INT)                              │
│    │ abandonadas_30_60seg (INT)                                 │
│    │ abandonadas_mas_60seg (INT)                                │
│    │ tasa_abandono (DECIMAL)                                    │
│    │ created_at (TIMESTAMP)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ tbl_reporte_clientes_unicos                                     │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id (BIGINT)                                                │
│    │ trimestre (VARCHAR)                                        │
│    │ fecha (DATE)                                               │
│    │ did (VARCHAR)                                              │
│    │ total_clientes_unicos (INT)                                │
│    │ total_llamadas (INT)                                       │
│    │ promedio_llamadas_por_cliente (DECIMAL)                    │
│    │ created_at (TIMESTAMP)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ tbl_reporte_transferencias                                      │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id (BIGINT)                                                │
│    │ trimestre (VARCHAR)                                        │
│    │ fecha (DATE)                                               │
│    │ menu (VARCHAR)                                             │
│    │ opcion (VARCHAR)                                           │
│    │ total_transferencias (INT)                                 │
│    │ transferencias_exitosas (INT)                              │
│    │ transferencias_fallidas (INT)                              │
│    │ tiempo_promedio_transferencia_seg (INT)                    │
│    │ created_at (TIMESTAMP)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ tbl_reporte_menu_errores                                        │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id (BIGINT)                                                │
│    │ trimestre (VARCHAR)                                        │
│    │ fecha (DATE)                                               │
│    │ menu (VARCHAR)                                             │
│    │ tipo_error (VARCHAR)                                       │
│    │ total_errores (INT)                                        │
│    │ descripcion_error (TEXT)                                   │
│    │ created_at (TIMESTAMP)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ job_execution_log  (TABLA DE CONTROL)                          │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id (BIGINT)                                                │
│    │ job_name (VARCHAR)  'etl_daily'                            │
│    │ start_time (DATETIME)                                      │
│    │ end_time (DATETIME)                                        │
│    │ status (VARCHAR)  'PENDING'|'RUNNING'|'SUCCESS'|'FAILED'   │
│    │ records_extracted (INT)                                    │
│    │ records_loaded (INT)                                       │
│    │ records_failed (INT)                                       │
│    │ error_message (TEXT)                                       │
│    │ error_code (VARCHAR)                                       │
│    │ executed_by (VARCHAR)  'cron'|'manual'                     │
│    │ parameters (JSON)                                          │
└─────────────────────────────────────────────────────────────────┘

NOTAS:
  • NO hay ForeignKeys explícitos (Django managed=False)
  • Relaciones son lógicas, no en DB
  • ETL maneja integridad referencial
  • Django solo LEE estas tablas
```

---

### 9.4 Diagrama de Apps Django

```
┌──────────────────────────────────────────────────────────────────┐
│              DIAGRAMA DE APPS DJANGO - IACT                      │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ apps/ivr/                                                       │
├─────────────────────────────────────────────────────────────────┤
│ Database: ivr_legacy (MariaDB)                                  │
│ Managed: False (readonly)                                       │
│                                                                 │
│ Modelos:                                                        │
│ ├─ CallRecord                                                  │
│ ├─ CallRecord                                                  │
│ ├─ CallRecord                                                  │
│ ├─ QuarterlyReport                                            │
│ ├─ ReporteAbandonedCall                                   │
│ ├─ ReporteUniqueClient                                        │
│ ├─ TransferDetail                                        │
│ ├─ MenuError                                           │
│ └─ JobExecutionLog                                              │
│                                                                 │
│ Constants:                                                      │
│ ├─ ALLOWED_DIDS                                                 │
│ ├─ DID_NAMES                                                    │
│ └─ TRIMESTRES                                                   │
│                                                                 │
│ Utils:                                                          │
│ ├─ get_trimestre_from_date()                                    │
│ ├─ get_historico_model()                                        │
│ └─ validate_did()                                               │
│                                                                 │
│ NO tiene:                                                       │
│ ❌ Views                                                         │
│ ❌ Serializers                                                   │
│ ❌ URLs                                                          │
└─────────────────────────────────────────────────────────────────┘
                      │
                      │ Usa modelos (readonly)
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│ apps/reports/                                                   │
├─────────────────────────────────────────────────────────────────┤
│ Database: default (PostgreSQL) + ivr_legacy (readonly)          │
│                                                                 │
│ Views (ViewSets):                                               │
│ ├─ AbandonedCallViewSet      POST /llamadas-abandonadas/ │
│ ├─ UniqueClientViewSet            POST /clientes-unicos/     │
│ ├─ DetalleTransferenciasViewSet     POST /detalle-transferencias/ │
│ └─ MenuErroresViewSet               POST /menu-errores/        │
│                                                                 │
│ Services:                                                       │
│ └─ ReportService                                                │
│    ├─ validate_date_range()          (CNST-006)                │
│    ├─ get_report_data()              (query MariaDB)           │
│    ├─ calculate_metrics()            (lógica pura)             │
│    ├─ generate_excel()               (export)                  │
│    └─ generate_csv()                 (export)                  │
│                                                                 │
│ Serializers:                                                    │
│ ├─ ReportMetricsSerializer                                      │
│ ├─ AbandonedCallRequestSerializer                         │
│ └─ ReportResponseSerializer                                     │
│                                                                 │
│ Permissions:                                                    │
│ └─ @require_function('reports.view')                            │
│                                                                 │
│ Constants:                                                      │
│ ├─ REPORT_MAX_DATE_RANGE_DAYS = 730  (CNST-006)                │
│ └─ MAX_EXPORT_RECORDS = 100000       (CNST-007)                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ apps/dashboard/                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Database: default + ivr_legacy (readonly)                       │
│                                                                 │
│ Views:                                                          │
│ ├─ MetricasTrimestralesViewSet      GET /metricas-trimestrales/ │
│ ├─ AnalisisClientesViewSet          GET /analisis-clientes/    │
│ └─ PerformanceIVRViewSet             GET /performance-ivr/     │
│                                                                 │
│ Services:                                                       │
│ └─ DashboardService                                             │
│    ├─ get_dashboard_metrics()        (con cache)               │
│    ├─ get_dashboard_widgets()        (KPI, Charts, Tables)     │
│    └─ _get_evolution_data()          (helper)                  │
│                                                                 │
│ Widgets:                                                        │
│ ├─ KPIWidget                                                    │
│ ├─ ChartWidget                                                  │
│ └─ TableWidget                                                  │
│                                                                 │
│ Cache:                                                          │
│ └─ Redis (TTL: 5 minutos)                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ apps/pipeline/                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Database: ivr_legacy (readonly)                                 │
│                                                                 │
│ Views:                                                          │
│ └─ PipelineViewSet                   GET /pipeline/status/     │
│                                                                 │
│ Services:                                                       │
│ └─ ETLMonitoringService                                         │
│    ├─ check_etl_status()             (query job_execution_log) │
│    └─ check_etl_should_have_run()    (validación horaria)      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ apps/access/                                                    │
├─────────────────────────────────────────────────────────────────┤
│ Database: default (PostgreSQL)                                  │
│                                                                 │
│ Models:                                                         │
│ ├─ Function                          (permisos)                │
│ ├─ Agrupador                         (roles)                   │
│ └─ UserFunction                      (M2M User-Function)       │
│                                                                 │
│ Decorators:                                                     │
│ └─ @require_function('codigo')       (RBAC)                    │
│                                                                 │
│ Middleware:                                                     │
│ └─ AccessAuditMiddleware             (auditoría)               │
│                                                                 │
│ Services:                                                       │
│ └─ AccessService                                                │
│    ├─ user_has_function()                                       │
│    └─ audit_access()                                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ apps/users/                                                     │
├─────────────────────────────────────────────────────────────────┤
│ Database: default (PostgreSQL)                                  │
│                                                                 │
│ Models:                                                         │
│ ├─ User (AbstractUser)                                          │
│ └─ UserProfile                                                  │
│                                                                 │
│ Views:                                                          │
│ └─ UserViewSet                       CRUD /api/v1/users/       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ apps/utils/                                                     │
├─────────────────────────────────────────────────────────────────┤
│ Database: N/A (utilidades compartidas)                          │
│                                                                 │
│ Models (Mixins):                                                │
│ ├─ SoftDeleteMixin                   (CNST-005)                │
│ └─ TimeStampedModel                  (created_at, updated_at)  │
│                                                                 │
│ Helpers:                                                        │
│ ├─ format_did()                                                 │
│ ├─ format_phone()                                               │
│ └─ calculate_percentage()                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ config/                                                         │
├─────────────────────────────────────────────────────────────────┤
│ routers.py:                                                     │
│ └─ IVRRouter                         (Database routing)        │
│    ├─ db_for_read()                  (ivr → ivr_legacy)        │
│    ├─ db_for_write()                 (todos → default)         │
│    └─ allow_migrate()                (ivr → False)             │
│                                                                 │
│ urls.py:                                                        │
│ ├─ /api/v1/reports/                  → apps.reports.urls       │
│ ├─ /api/v1/dashboard/                → apps.dashboard.urls     │
│ ├─ /api/v1/pipeline/                 → apps.pipeline.urls      │
│ ├─ /api/v1/access/                   → apps.access.urls        │
│ └─ /api/v1/users/                    → apps.users.urls         │
└─────────────────────────────────────────────────────────────────┘
```

---

### 9.5 Diagrama de Secuencia Completo

```
┌──────────────────────────────────────────────────────────────────┐
│   SECUENCIA COMPLETA: Usuario → Reporte → Descarga              │
└──────────────────────────────────────────────────────────────────┘

User        Frontend      Django      ReportService   MariaDB     PostgreSQL
 │              │            │              │            │            │
 │ 1. Login     │            │              │            │            │
 ├─────────────>│            │              │            │            │
 │              │            │              │            │            │
 │              │ 2. POST /auth/login/      │            │            │
 │              ├───────────>│              │            │            │
 │              │            │              │            │            │
 │              │            │ 3. Validate credentials   │ 4. SELECT  │
 │              │            ├──────────────────────────────────────>│
 │              │            │              │            │            │
 │              │            │<───────────────────────────────────────┤
 │              │            │ 5. User data │            │            │
 │              │            │              │            │            │
 │              │<───────────┤              │            │            │
 │<─────────────┤ 6. Token   │              │            │            │
 │              │            │              │            │            │
 │ 7. Solicitar reporte       │              │            │            │
 │ POST /reports/llamadas-abandonadas/       │            │            │
 │ Body: {trimestre: Q1}     │              │            │            │
 ├─────────────>│            │              │            │            │
 │              │            │              │            │            │
 │              │ 8. POST (+ Token)          │            │            │
 │              ├───────────>│              │            │            │
 │              │            │              │            │            │
 │              │            │ 9. Check RBAC (reports.view)           │
 │              │            ├──────────────────────────────────────>│
 │              │            │              │            │            │
 │              │            │<───────────────────────────────────────┤
 │              │            │ 10. OK       │            │            │
 │              │            │              │            │            │
 │              │            │ 11. Delegar a Service     │            │
 │              │            ├─────────────>│            │            │
 │              │            │              │            │            │
 │              │            │              │ 12. SELECT │            │
 │              │            │              ├───────────>│            │
 │              │            │              │            │            │
 │              │            │              │<───────────┤            │
 │              │            │              │ 13. Datos  │            │
 │              │            │              │            │            │
 │              │            │              │ 14. Procesar            │
 │              │            │              ├─────────   │            │
 │              │            │              │      │     │            │
 │              │            │              │<─────┘     │            │
 │              │            │              │            │            │
 │              │            │              │ 15. Generar Excel       │
 │              │            │              ├─────────   │            │
 │              │            │              │      │     │            │
 │              │            │              │<─────┘     │            │
 │              │            │              │            │            │
 │              │            │              │ 16. Guardar metadata    │
 │              │            │              ├────────────────────────>│
 │              │            │              │            │            │
 │              │            │<─────────────┤            │            │
 │              │            │ 17. Response │            │            │
 │              │            │              │            │            │
 │              │<───────────┤              │            │            │
 │<─────────────┤ 18. JSON + download_url   │            │            │
 │              │              │            │            │            │
 │              │              │            │            │            │
 │ 19. GET /media/reports/file.xlsx         │            │            │
 ├─────────────>│              │            │            │            │
 │              │              │            │            │            │
 │              ├─────────────>│            │            │            │
 │              │              │            │            │            │
 │              │<─────────────┤            │            │            │
 │<─────────────┤ 20. Archivo Excel          │            │            │
 │              │              │            │            │            │
 │ 21. Descarga completa        │            │            │            │
 │              │              │            │            │            │
```

---

<a name="10-referencias"></a>
## 10. REFERENCIAS

### 10.1 Scripts SQL Reales

```
UBICACIÓN: /mnt/user-data/uploads/

Scripts ETL (Base para Stored Procedure):
├─ q_REPTRIM021_LLAMADAS_ABDANDONADAS.sql
│  → Genera: tbl_reporte_llamadas_abandonadas
│  → Cálculo: Total abandonadas, tiempos, clasificación por segundos
│
├─ q_REPTRIM011_CLIENTES_UNICOS.sql
│  → Genera: tbl_reporte_clientes_unicos
│  → Cálculo: COUNT(DISTINCT cTelefono_Origen)
│
├─ q_REPTRIM031_PROMEDIO_CLIENTES.sql
│  → Genera: tbl_reporte_promedio_clientes
│  → Cálculo: Promedio llamadas por cliente único
│
├─ q_REPTRIM041_CLIENTES_MENU.sql
│  → Genera: tbl_reporte_clientes_menu
│  → Cálculo: Clientes únicos por menú IVR
│
├─ q_REPTRIM121_LLAMADAS_MENU.sql
│  → Genera: tbl_reporte_llamadas_menu
│  → Cálculo: Total llamadas por menú IVR
│
├─ q_REP_DETALLE_TRANSFERENCIA_MENU_OPCION-v.0.3.1.sql
│  → Genera: tbl_reporte_transferencias
│  → Cálculo: Detalle de transferencias por menú y opción
│  → Versión: 0.3.1
│
└─ q_cMENU_ERROR.sql
   → Genera: tbl_reporte_menu_errores
   → Cálculo: Errores de menú IVR por tipo

NOTA:
  - Estos scripts SQL se ejecutan DENTRO de sp_etl_daily()
  - NO son archivos separados en producción
  - Son la BASE para el desarrollo del SP
  - Versión actual del SP puede tener optimizaciones
```

---

### 10.2 Documentos Relacionados

#### **10.2.1 Documentos de Arquitectura**

```
/tmp/iact-real/docs/arquitectura/diseño/
├─ ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_1.md
│  → Secciones 1-3: Resumen, Arquitectura Datos, Proceso ETL
│
├─ ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_2.md
│  → Secciones 4-6: Arquitectura Django, APIs, Flujo de Datos
│
└─ ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_3.md  (ESTE)
   → Secciones 7-10: Nomenclatura, Constantes, Diagramas, Referencias
```

---

#### **10.2.2 Documentos de Nomenclatura**

```
/tmp/iact-real/docs/soporte/
├─ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_1.md
│  → Secciones 1-14: Principios fundamentales
│
├─ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_2.md
│  → Secciones 15-18: ⭐ Principio de Equilibrio + DRF básico
│
├─ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_3.md
│  → Secciones 19-23: DRF avanzado
│
├─ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_4.md
│  → Secciones 24-27: IACT específico
│
└─ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_5.md
   → Secciones 28-31: Anti-patterns, Resumen, Referencias

APLICACIÓN EN ESTE DOCUMENTO:
  - Sección 14: Regla de Idioma (código inglés, docs español)
  - Sección 15: Principio de Equilibrio (1-4 palabras por scope)
  - Sección 28: Anti-patterns evitados
```

---

#### **10.2.3 Documentos de Análisis**

```
/mnt/user-data/uploads/
├─ URLS_REPORTES_Y_DASHBOARDS.md
│  → Lista completa de endpoints (7 reportes + 3 dashboards)
│  → Request/Response ejemplos
│  → Usado en: Sección 5 de PARTE 2
│
├─ CASOS_DE_USO_IACT_v5_0_0.md
│  → Casos de uso del sistema
│  → Escenarios de usuario
│
└─ LEVANTAMIENTO_APPS_IACT.md
   → Estado actual de las apps
   → Estructura de código existente
```

---

#### **10.2.4 Documentos de Metodología**

```
/mnt/user-data/uploads/
└─ METODOLOGIA_CREACION_DOCUMENTOS_v1_0_0.md
   → Metodología usada para crear ESTE documento
   → Proceso de 6 pasos seguido
   → Estructura semántica de /docs/
```

---

### 10.3 Convenciones Aplicadas

```yaml
Nomenclatura:
  - CLEAN_CODE v3.0.1 (completo)
  - Principio de Equilibrio (Sección 15)
  - Regla de Idioma (Sección 14)

Constantes:
  - CNST-004: ETL_TIMEOUT_SECONDS = 300
  - CNST-005: SOFT_DELETE_REQUIRED = True
  - CNST-006: REPORT_MAX_DATE_RANGE_DAYS = 730
  - CNST-007: MAX_EXPORT_RECORDS = 100000

Arquitectura:
  - Service Layer Pattern (separación de lógica)
  - Database Router (IVR_LEGACY vs DEFAULT)
  - managed=False para modelos IVR
  - RBAC con @require_function

URLs:
  - Versión: /api/v1/
  - Kebab-case: /llamadas-abandonadas/
  - Verbos HTTP (no en URL)
```

---

### 10.4 Tecnologías y Versiones

```
┌────────────────────┬─────────────┬──────────────────────┐
│ Tecnología         │ Versión     │ Notas                │
├────────────────────┼─────────────┼──────────────────────┤
│ Python             │ 3.11+       │ Requerido            │
│ Django             │ 4.2 LTS     │ Framework base       │
│ Django REST Frmwrk │ 3.14+       │ API                  │
│ MariaDB            │ 10.x        │ IVR_LEGACY (readonly)│
│ PostgreSQL         │ 14+         │ DEFAULT (read/write) │
│ Redis              │ 7.x         │ Cache, sessions      │
│ openpyxl           │ 3.x         │ Export Excel         │
│ python-dotenv      │ 1.x         │ Variables de entorno │
│ mysqlclient        │ 2.x         │ Conector MariaDB     │
│ psycopg2-binary    │ 2.9+        │ Conector PostgreSQL  │
│ django-redis       │ 5.x         │ Cache backend        │
└────────────────────┴─────────────┴──────────────────────┘
```

---

### 10.5 Contactos y Soporte


```yaml
Documentación del Proyecto:
  Ubicación: /tmp/iact-real/docs/
  Estructura: arquitectura/, analisis/, gestion/, soporte/

Scripts ETL:
  Ubicación: /mnt/user-data/uploads/
  Archivos: q_*.sql

Logs del Sistema:
  ETL: /var/log/etl/etl_daily_YYYYMMDD.log
  Django: /var/log/django/
  Cron: /var/log/cron

Configuración:
  Django: config/settings/
  Cron: /etc/cron.d/etl-daily
  Script ETL: /usr/local/bin/run_etl.sh
```

---

### 10.6 Changelog

#### **Version 1.0.0 (2026-01-18)**

```yaml
Cambios:
  - Versión inicial definitiva consolidada
  - Arquitectura REAL documentada (no proyectada)
  - 3 partes completas (~7,000 líneas totales)
  - Basada en arquitectura confirmada:
    * MariaDB (IVR_LEGACY) managed=False
    * Stored Procedure ETL (no Python)
    * Apps separadas (reports/, dashboard/)
    * Database Router (IVR_LEGACY vs DEFAULT)

Secciones:
  PARTE 1/3:
    1. Resumen Ejecutivo
    2. Arquitectura de Datos (MariaDB)
    3. Proceso ETL
  
  PARTE 2/3:
    4. Arquitectura Django
    5. APIs y Endpoints
    6. Flujo de Datos Completo
  
  PARTE 3/3:
    7. Nomenclatura y Convenciones
    8. Constantes y Restricciones
    9. Diagramas
    10. Referencias (ESTA SECCIÓN)

Novedades:
  - ⭐ Principio de Equilibrio aplicado (CLEAN_CODE v3.0.1 Sec. 15)
  - Nomenclatura húngara del IVR documentada (dFecha, cMenu, nDuracion)
  - 7 endpoints de reportes POST
  - 3 endpoints de dashboards GET
  - RBAC completo con @require_function
  - Database Router exhaustivo
  - Service Layer Pattern aplicado
  - 4 constantes del sistema (CNST-004 a CNST-007)
  - 5 diagramas completos (Arquitectura, Flujo ETL, ER, Apps, Secuencia)

Documentos Base:
  - URLS_REPORTES_Y_DASHBOARDS.md
  - CLEAN_CODE v3.0.1 (5 partes)
  - Scripts SQL reales (q_*.sql)
  - METODOLOGIA_CREACION_DOCUMENTOS v1.0.0

Estado: COMPLETO Y DEFINITIVO
Próxima versión: 2.0.0 (solo si hay cambios arquitectónicos mayores)
```

---


### 10.7 Glosario de Términos

---

### 10.6 Changelog v2.0.0 - Consolidado

#### **Resumen Ejecutivo**

**Fecha:** 2026-01-19  
**Versión:** 2.0.0  
**Tipo:** Actualización arquitectónica mayor  
**Razón:** Alineación con CLEAN_CODE NAMING PRINCIPLES v3.0.1

---

#### **Cambios Globales (Todas las Partes)**

**1. Nomenclatura de Modelos (Español → Inglés)**

```
┌───────────────────────┬─────────────────────┬──────────────────────┐
│ v1.0.0 (Español)      │ v2.0.0 (Inglés)     │ Tabla MariaDB        │
├───────────────────────┼─────────────────────┼──────────────────────┤
│ CallRecord            │ CallRecord          │ tbl_historico_t1_*   │
│ CallRecord            │ CallRecord          │ tbl_historico_t2_*   │
│ CallRecord            │ CallRecord          │ tbl_historico_t3_*   │
│ QuarterlyReport       │ QuarterlyReport     │ tbl_reporte_trim...  │
│ AbandonedCall         │ AbandonedCall       │ tbl_reporte_llam...  │
│ UniqueClient          │ UniqueClient        │ tbl_reporte_clie...  │
│ IVRMenu               │ IVRMenu             │ menu2                │
│ ReporteTransferencias │ TransferDetail      │ tbl_reporte_tran...  │
│ ReporteMenuErrores    │ MenuError           │ tbl_reporte_menu...  │
└───────────────────────┴─────────────────────┴──────────────────────┘

NOTA: Tablas MariaDB NO cambian (nomenclatura legacy)
```

**2. Arquitectura apps/ Corregida**

```diff
❌ v1.0.0 (INCORRECTO):
apps/utils/
├─ models.py
│   ├─ SoftDeleteMixin          ❌ Clases en utils/
│   └─ TimeStampedModel          ❌ Clases en utils/
└─ mixins.py
    └─ SoftDeleteViewSetMixin    ❌ Mixin ViewSet en utils/

✅ v2.0.0 (CORRECTO):
apps/core/
├─ models.py
│   ├─ TimeStampedModel          ✅ Modelo abstracto en core/
│   ├─ SoftDeleteMixin           ✅ Modelo abstracto en core/
│   ├─ SoftDeleteManager         ✅ Manager en core/
│   └─ SoftDeleteQuerySet        ✅ QuerySet en core/
└─ mixins.py
    └─ SoftDeleteViewSetMixin    ✅ Mixin ViewSet en core/

apps/utils/
├─ pagination.py                 ✅ Funciones helper
├─ exceptions.py                 ✅ Funciones helper
└─ request.py                    ✅ Funciones helper
```

**3. Referencias Actualizadas**

```diff
- CLEAN_CODE_NAMING_PRINCIPLES v2.3.0 (obsoleto)
+ CLEAN_CODE_NAMING_PRINCIPLES v3.0.1 (actual)

- ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v2.0.0.md
+ ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v3.0.0.md

Nuevos documentos:
+ GUIA_CORE_VS_UTILS_v2.0.0.md
+ RESUMEN_CAMBIOS_ETL_v1_0_0_a_v2_0_0.md
```

---

#### **Cambios por Parte**

**PARTE 1/3: Fundamentos y Arquitectura de Datos**

```
Sección 1: Resumen Ejecutivo
├─ ✅ Diagrama arquitectura actualizado
├─ ✅ DECISIÓN 2: Ejemplo con CallRecord (antes CallRecord)
├─ ✅ Stack tecnológico actualizado
└─ ✅ Números clave sin cambios

Sección 2: Arquitectura de Datos (MariaDB)
├─ ✅ Database Router sin cambios (correcto)
├─ ✅ 2.2.2: Estructura SQL sin cambios (legacy)
├─ ✅ 2.2.3: Modelo Django CallRecord (antes CallRecord)
├─ ✅ 2.2.4: Configuración por trimestre actualizada
├─ ✅ 2.3: Tablas agregadas con nomenclatura inglesa
└─ ✅ 2.4: job_execution_log sin cambios

Sección 3: Proceso ETL
├─ ✅ Stored Procedure sin cambios (legacy)
├─ ✅ Cron sin cambios
├─ ✅ Transformaciones SQL sin cambios
└─ ✅ Referencias a modelos actualizadas
```

**PARTE 2/3: Arquitectura Django y APIs**

```
Sección 4: Arquitectura Django ⭐ CRÍTICA
├─ ✅ 4.1: Apps y Responsabilidades (apps/core/ agregada)
├─ ✅ 4.2: Modelos con nomenclatura inglesa
├─ ✅ 4.3: Database Router sin cambios
├─ ✅ 4.4: Service Layer con importaciones desde apps/core/
└─ ✅ 4.5: Estructura de archivos actualizada

Sección 5: APIs y Endpoints
├─ ✅ 5.1: Endpoints con modelos actualizados
├─ ✅ 5.2: Dashboards con ejemplos actualizados
├─ ✅ 5.3: Pipeline sin cambios estructurales
└─ ✅ 5.4: RBAC sin cambios

Sección 6: Flujo de Datos Completo
├─ ✅ Diagramas de secuencia actualizados
├─ ✅ Referencias a modelos corregidas
└─ ✅ Flujos sin cambios estructurales
```

**PARTE 3/3: Nomenclatura, Constantes y Referencias**

```
Sección 7: Nomenclatura y Convenciones ⭐ CRÍTICA
├─ ✅ 7.1: Nomenclatura MariaDB sin cambios (legacy)
├─ ✅ 7.2: Nomenclatura Django actualizada completa
│   ├─ 7.2.1: Modelos con nombres en inglés
│   ├─ 7.2.2: Campos sin cambios
│   ├─ 7.2.3: ViewSets actualizados
│   ├─ 7.2.4: Services actualizados
│   └─ 7.2.5: Serializers actualizados
├─ ✅ 7.3: URLs sin cambios
├─ ✅ 7.4: CLEAN_CODE v3.0.1 (antes v2.3.0)
└─ ✅ 7.5: Regla de Idioma sin cambios

Sección 8: Constantes y Restricciones
├─ ✅ CNST-004 a CNST-007 sin cambios
├─ ✅ DIDs sin cambios
├─ ✅ Trimestres sin cambios
└─ ✅ Ejemplos de código con modelos actualizados

Sección 9: Diagramas
├─ ✅ 9.1: Arquitectura General actualizado
├─ ✅ 9.2: Flujo ETL actualizado
├─ ✅ 9.3: Diagrama ER actualizado
├─ ✅ 9.4: Apps Django actualizado (apps/core/)
└─ ✅ 9.5: Secuencia completa actualizada

Sección 10: Referencias ⭐ ACTUALIZADA
├─ ✅ 10.1: Scripts SQL sin cambios
├─ ✅ 10.2: Documentos relacionados actualizados
│   ├─ CLEAN_CODE v3.0.1 (5 partes)
│   ├─ ANALISIS_CORE_VS_UTILS v3.0.0
│   └─ Documentos ETL v2.0.0
├─ ✅ 10.3: Convenciones actualizadas
├─ ✅ 10.4: Tecnologías sin cambios
├─ ✅ 10.5: Contactos sin cambios
├─ ✅ 10.6: Changelog v2.0.0 (esta sección)
├─ ✅ 10.7: Glosario actualizado
└─ ✅ 10.8: Recursos externos actualizados
```

---

#### **Estadísticas de Cambios**

```
TRANSFORMACIONES APLICADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nombres de modelos:
├─ CallRecord: 27 reemplazos (PARTE 1)
├─ CallRecord: 9 reemplazos (PARTE 2)
├─ CallRecord: 15 reemplazos (PARTE 3)
├─ QuarterlyReport: 5 reemplazos
├─ AbandonedCall: 8 reemplazos
├─ UniqueClient: 4 reemplazos
├─ IVRMenu: 3 reemplazos
└─ TransferDetail, MenuError: 6 reemplazos

Referencias CLEAN_CODE:
├─ v2.3.0 → v3.0.1: 16 reemplazos (PARTE 3)
├─ v2.3.0 → v3.0.1: 3 reemplazos (PARTE 2)
└─ v2.3.0 → v3.0.1: 0 reemplazos (PARTE 1)

Importaciones:
├─ apps.utils.models → apps.core.models: 0 (no había directas)
└─ Referencias actualizadas en documentación: 5+

Arquitectura apps/:
├─ apps/core/ agregada: 3 secciones
├─ apps/utils/ redefinida: 2 secciones
└─ Tabla responsabilidades: 1 actualización mayor
```

---

#### **Documentos Afectados**

**Obsoletos (NO USAR):**
```
❌ ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_1.md
❌ ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_2.md
❌ ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_3.md
❌ CLEAN_CODE_NAMING_PRINCIPLES_v2_3_0_PARTE_*.md (5 partes)
❌ ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v2.0.0.md
```

**Actuales (USAR):**
```
✅ ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0_PARTE_1.md
✅ ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0_PARTE_2.md
✅ ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0_PARTE_3.md
✅ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_*.md (5 partes)
✅ ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v3.0.0.md
✅ GUIA_CORE_VS_UTILS_v2.0.0.md
✅ RESUMEN_CAMBIOS_ETL_v1_0_0_a_v2_0_0.md
```

---

#### **Migración Recomendada**

**Orden de Aplicación:**

```
1. PREPARACIÓN
   ☐ Backup de código (branch migration-etl-v2.0.0)
   ☐ Backup de base de datos
   ☐ Tests pasando antes de cambios
   ☐ Leer RESUMEN_CAMBIOS_ETL_v1_0_0_a_v2_0_0.md

2. FASE 1: Estructura
   ☐ Crear apps/core/ con modelos abstractos
   ☐ Mover SoftDeleteMixin desde apps/utils/ → apps/core/
   ☐ Mover TimeStampedModel desde apps/utils/ → apps/core/
   ☐ Crear apps/core/mixins.py con SoftDeleteViewSetMixin

3. FASE 2: Modelos
   ☐ Renombrar CallRecord → CallRecord en apps/ivr/models.py
   ☐ Renombrar QuarterlyReport → QuarterlyReport
   ☐ Renombrar resto de modelos
   ☐ Actualizar importaciones en modelos

4. FASE 3: Services
   ☐ Actualizar imports en apps/reports/services.py
   ☐ Actualizar imports en apps/dashboard/services.py
   ☐ Actualizar imports en apps/pipeline/services.py
   ☐ Actualizar referencias a modelos

5. FASE 4: Views y Serializers
   ☐ Actualizar imports en views
   ☐ Actualizar Meta.model en serializers
   ☐ Ejecutar tests de integración

6. VALIDACIÓN
   ☐ Tests unitarios pasan
   ☐ Tests de integración pasan
   ☐ API funciona correctamente
   ☐ Dashboard carga sin errores
   ☐ Reportes se generan correctamente
```

---

#### **Contacto y Soporte**

**Preguntas sobre la migración:**
- Consultar: RESUMEN_CAMBIOS_ETL_v1_0_0_a_v2_0_0.md
- Revisar: CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_*.md

**Dudas arquitectónicas:**
- apps/core/ vs apps/utils/: GUIA_CORE_VS_UTILS_v2.0.0.md
- Arquitectura general: ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v3.0.0.md

---

**Documento generado:** 2026-01-19  
**Versión:** 2.0.0  
**Estado:** ✅ DEFINITIVO

```
AGR: Agrupador (rol RBAC)
  Ejemplo: AGR_008 = Reportes, AGR_009 = Dashboards

API: Application Programming Interface
  REST API basada en Django REST Framework

CDR: Call Detail Record
  Registro individual de una llamada en el IVR

CNST: Constante del sistema
  Ejemplo: CNST-006 = REPORT_MAX_DATE_RANGE_DAYS

DID: Direct Inward Dialing
  Número de teléfono que recibe llamadas
  Ejemplo: 19020084 = Puebla

DRF: Django REST Framework
  Framework para construir APIs REST en Django

ETL: Extract, Transform, Load
  Proceso de extracción, transformación y carga de datos

IVR: Interactive Voice Response
  Sistema de respuesta de voz interactiva (PBX)

KPI: Key Performance Indicator
  Indicador clave de rendimiento (widget en dashboard)

ORM: Object-Relational Mapping
  Django ORM para interactuar con bases de datos

PBX: Private Branch Exchange
  Sistema telefónico del call center

RBAC: Role-Based Access Control
  Control de acceso basado en roles/funciones

SP: Stored Procedure
  Procedimiento almacenado en MariaDB (sp_etl_daily)

TTL: Time To Live
  Tiempo de vida del cache (5 minutos para dashboards)

ViewSet: Django REST Framework ViewSet
  Clase que agrupa views CRUD de un recurso
```

---

### 10.8 Recursos Externos

```yaml
Django Documentation:
  - https://docs.djangoproject.com/en/4.2/
  - Topics: Models, Database Routers, Migrations

Django REST Framework:
  - https://www.django-rest-framework.org/
  - Topics: ViewSets, Serializers, Permissions

MariaDB Documentation:
  - https://mariadb.com/kb/en/
  - Topics: Stored Procedures, Triggers, Users

PostgreSQL Documentation:
  - https://www.postgresql.org/docs/14/
  - Topics: JSON Fields, Full Text Search

Redis Documentation:
  - https://redis.io/docs/
  - Topics: Caching, TTL, Data Types

Clean Code (Robert C. Martin):
  - Libro: "Clean Code: A Handbook of Agile Software Craftsmanship"
  - Capítulo 2: Meaningful Names
  - Aplicado en: CLEAN_CODE v3.0.1

Clean Architecture (Robert C. Martin):
  - Libro: "Clean Architecture"
  - Part V: Architecture
  - Aplicado en: Service Layer Pattern
```

---

## 📝 NOTAS FINALES

### Uso de Este Documento

```
PARA DESARROLLADORES:
  - Consultar Sección 4: Arquitectura Django
  - Consultar Sección 5: APIs y Endpoints
  - Consultar Sección 7: Nomenclatura
  - Consultar Sección 9.4: Diagrama de Apps

PARA ARQUITECTOS:
  - Consultar Sección 1: Resumen Ejecutivo
  - Consultar Sección 2: Arquitectura de Datos
  - Consultar Sección 6: Flujo de Datos
  - Consultar Sección 9.1: Diagrama General

PARA OPS/DEVOPS:
  - Consultar Sección 3: Proceso ETL
  - Consultar Sección 8: Constantes
  - Consultar Sección 9.2: Diagrama Flujo ETL
  - Logs: /var/log/etl/

PARA QA:
  - Consultar Sección 5: APIs (Request/Response)
  - Consultar Sección 8.7: Límites
  - Consultar CNST-006, CNST-007
```

---

### Mantenimiento del Documento

```yaml
Actualizar cuando:
  - Se agreguen nuevos endpoints
  - Se modifique el proceso ETL
  - Se agreguen nuevas tablas en MariaDB
  - Se cambien constantes del sistema (CNST-*)
  - Se agreguen nuevas apps Django

Proceso de actualización:
  1. Incrementar versión (v1.1.0, v2.0.0, etc.)
  2. Actualizar Sección 10.6: Changelog
  3. Revisar todas las partes (1/3, 2/3, 3/3)
  4. Validar diagramas (Sección 9)
  5. Actualizar fecha en header

Responsable:
  - Arquitecto del Proyecto
  - Revisor: Desarrollador Senior
```

---

**FIN DE PARTE 3/3**

**FIN DEL DOCUMENTO ARQUITECTURA_REAL_ETL_DEFINITIVA v1.0.0**

---

## 📊 RESUMEN COMPLETO DEL DOCUMENTO

```
ARQUITECTURA_REAL_ETL_DEFINITIVA v1.0.0

PARTE 1/3: FUNDAMENTOS Y ARQUITECTURA DE DATOS
  - Secciones: 1-3
  - Líneas: ~2,016
  - Tamaño: ~62K
  - Contenido: Resumen Ejecutivo, Arquitectura MariaDB, Proceso ETL

PARTE 2/3: ARQUITECTURA DJANGO Y APIS
  - Secciones: 4-6
  - Líneas: ~2,514
  - Tamaño: ~79K
  - Contenido: Apps Django, Service Layer, APIs, Flujos

PARTE 3/3: NOMENCLATURA, CONSTANTES Y REFERENCIAS
  - Secciones: 7-10
  - Líneas: ~2,483
  - Tamaño: ~78K
  - Contenido: Nomenclatura, Constantes, Diagramas, Referencias

═══════════════════════════════════════════════════════════════════
TOTAL: 10 secciones, 3 partes, ~7,013 líneas, ~219K
═══════════════════════════════════════════════════════════════════

Estado: COMPLETO Y DEFINITIVO
Fecha: 2026-01-18
Versión: 1.0.0
```

---

**Próximos pasos sugeridos:**
1. Revisar código existente contra esta arquitectura
2. Implementar Service Layer donde falte
3. Validar constantes (CNST-004 a CNST-007)
4. Actualizar ANALISIS_RELACIONES_APPS con arquitectura real
5. Crear tests basados en esta arquitectura
