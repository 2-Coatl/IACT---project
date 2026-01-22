---
version: 1.0.0
date: 2026-01-20
project: IACT Call Center System
type: Decisión Arquitectónica
categoria: arquitectura/decisiones
tema: Ubicación de Center, Service, CallRecord en apps/pipeline/
autor: Claude Technical Analysis
tags: [arquitectura, decision, pipeline, etl, flujo-datos]
---

# DECISIÓN ARQUITECTÓNICA: Center, Service, CallRecord → apps/pipeline/

## 1. CONTEXTO

**Pregunta Original:**
> "Center, Service, CallRecord, ¿PORQUE NO EN apps/pipeline/ o apps/ivr_legacy/?"

**Decisión Tomada:**
```yaml
✅ Center, Service, CallRecord → apps/pipeline/
✅ apps/ivr_legacy/ → apps/ivr/ (renombre)
❌ NO en apps/dashboard/
❌ NO en apps/reports/
❌ NO en apps/ivr/
```

---

## 2. FLUJO ETL DEL SISTEMA

```
┌──────────────────────────────────────┐
│ apps/ivr/                            │
│ MariaDB READONLY (CNST-002)          │
│                                      │
│ Modelos:                             │
│ - QuarterlyReport (readonly)         │
│ - TransferReport (readonly)          │
│ - CallRecordQ1/Q2/Q3/Q4 (readonly)  │
│ - AbandonedReport (readonly)         │
│                                      │
│ Propósito: Datos crudos del PBX      │
└──────────────┬───────────────────────┘
               │
               │ ① ETL lee datos crudos
               ↓
┌──────────────────────────────────────┐
│ apps/pipeline/                       │
│ PostgreSQL WRITABLE                  │
│                                      │
│ Jobs ETL:                            │
│ - JobExecution                       │
│ - JobLog                             │
│ - ScheduledJob                       │
│                                      │
│ ② ETL procesa y transforma           │
│                                      │
│ Configuración ETL:                   │
│ - Center (qué centros procesar)      │
│ - Service (qué servicios procesar)   │
│                                      │
│ ③ ETL escribe output                 │
│                                      │
│ Output ETL:                          │
│ - CallRecord (datos agregados)       │
│                                      │
│ Propósito: Dueño del ciclo ETL       │
└──────────────┬───────────────────────┘
               │
               │ ④ Consume datos procesados
               ↓
┌──────────────────────────────────────┐
│ apps/reports/ + apps/dashboard/      │
│                                      │
│ Solo CONSUMEN (readonly):            │
│ - Leen CallRecord                    │
│ - Usan Center, Service para filtros │
│ - Generan visualizaciones            │
│                                      │
│ Propósito: Presentación de datos     │
└──────────────────────────────────────┘
```

---

## 3. ANÁLISIS DE OPCIONES

### Opción 1: apps/pipeline/ ⭐ ELEGIDA

```yaml
Razones a favor:
  ✅ Pipeline es el DUEÑO de CallRecord
     - Pipeline LEE de IVR
     - Pipeline PROCESA
     - Pipeline CREA CallRecord
     - reports/dashboard solo CONSUMEN
  
  ✅ Center, Service son configuración ETL
     - Configuran QUÉ procesar
     - QUÉ centros incluir
     - QUÉ servicios agregar
  
  ✅ Cohesión arquitectónica
     - Todo el flujo ETL en un lugar
     - Jobs + Config + Output juntos
     - Single Responsibility (ETL)
  
  ✅ Claridad de responsabilidades
     - pipeline/ = OWNER (crea datos)
     - reports/ = CONSUMER (lee datos)
     - dashboard/ = CONSUMER (visualiza datos)

Responsabilidades apps/pipeline/:
  1. Configuración ETL (Center, Service)
  2. Ejecución ETL (Jobs, Scheduler)
  3. Output ETL (CallRecord)
  4. Monitoreo ETL (Logs)
```

---

### Opción 2: apps/ivr/ ❌ DESCARTADA

```yaml
Razones en contra:
  ❌ IVR es MariaDB READONLY (CNST-002)
     - No se puede escribir en IVR
     - CallRecord es PostgreSQL WRITABLE
     - Diferentes bases de datos
  
  ❌ IVR son datos CRUDOS
     - CallRecord son datos PROCESADOS
     - Diferente propósito
     - Diferente naturaleza
  
  ❌ IVR es legacy readonly
     - No debe mezclarse con datos nuevos
     - Solo lectura (Router bloquea writes)

Conclusión:
  IVR y Pipeline son separados por diseño
```

---

### Opción 3: apps/dashboard/ ❌ DESCARTADA

```yaml
Razones en contra:
  ❌ Dashboard solo VISUALIZA
     - No crea datos
     - Solo consume y presenta
     - Responsabilidad: UI/UX
  
  ❌ Viola Single Responsibility
     - Dashboard mezclaría lógica ETL con UI
     - No cohesivo
  
  ❌ Dependencia inversa
     - Pipeline crearía datos en dashboard
     - dashboard debería depender de pipeline
     - No al revés

Conclusión:
  dashboard/ consume datos, no los crea
```

---

### Opción 4: apps/reports/ ❌ DESCARTADA

```yaml
Razones en contra:
  ❌ Reports solo CONSUME datos
     - Genera reportes Excel/PDF/CSV
     - Lee CallRecord, no lo crea
     - Responsabilidad: Generación outputs
  
  ❌ No tiene lógica ETL
     - No procesa datos raw
     - Solo formatea para presentación

Conclusión:
  reports/ consume datos, no los crea
```

---

## 4. PRINCIPIOS ARQUITECTÓNICOS APLICADOS

### Single Responsibility Principle

```yaml
apps/pipeline/:
  Responsabilidad ÚNICA: ETL
  - Configurar (Center, Service)
  - Procesar (Jobs)
  - Almacenar output (CallRecord)

apps/dashboard/:
  Responsabilidad ÚNICA: Visualización
  - Widgets
  - Layouts
  - User preferences

apps/reports/:
  Responsabilidad ÚNICA: Generación reportes
  - Templates
  - Exports (Excel, PDF, CSV)
  - Scheduled reports
```

---

### Ownership Principle

```yaml
OWNER (pipeline) crea y gestiona:
  ✅ CallRecord (pipeline lo escribe)
  ✅ Center (pipeline lo usa para configurar)
  ✅ Service (pipeline lo usa para filtrar)

CONSUMERS (dashboard, reports) solo leen:
  ✅ Consultan CallRecord
  ✅ Usan Center/Service para filtros
  ❌ NO modifican
  ❌ NO crean
```

---

### Data Flow Principle

```yaml
Flujo unidireccional:
  IVR → pipeline → reports/dashboard

NUNCA:
  dashboard → pipeline (no debe crear datos ETL)
  reports → pipeline (no debe crear datos ETL)
```

---

## 5. VENTAJAS DE LA DECISIÓN

```yaml
Arquitectura:
  ✅ Claridad: pipeline OWNER de datos ETL
  ✅ Cohesión: Todo ETL en un lugar
  ✅ Separación: dashboard/reports solo consumen

Mantenimiento:
  ✅ Bugs ETL → mirar solo apps/pipeline/
  ✅ Cambios ETL → tocar solo apps/pipeline/
  ✅ Testing ETL → tests/unit/pipeline/

Escalabilidad:
  ✅ Agregar nuevos jobs → apps/pipeline/
  ✅ Agregar nuevas fuentes → apps/pipeline/
  ✅ Dashboard crece independiente

Performance:
  ✅ Cache en pipeline (owner de datos)
  ✅ Optimizaciones ETL centralizadas
  ✅ Queries desde dashboard optimizadas
```

---

## 6. CAMBIOS REQUERIDOS

### apps/ivr_legacy/ → apps/ivr/

```yaml
Razón: Nombre más limpio
Acción:
  - Renombrar directorio
  - Actualizar INSTALLED_APPS
  - Actualizar imports (~20 archivos)
  - Sin cambios en BD (solo código)
```

---

### apps/core/ → apps/pipeline/

```yaml
Mover modelos:
  - Center → apps/pipeline/models.py
  - Service → apps/pipeline/models.py
  - CallRecord → apps/pipeline/models.py

Mover services:
  - CenterService → apps/pipeline/services/
  - ServiceService → apps/pipeline/services/
  - CallRecordService → apps/pipeline/services/

Mover API:
  - Serializers → apps/pipeline/serializers.py
  - Filters → apps/pipeline/filters.py
  - ViewSets → apps/pipeline/viewsets.py

Migrations:
  - SeparateDatabaseAndState
  - Preservar db_table (sin cambios BD)
```

---

### apps/core/ limpieza

```yaml
Dejar SOLO:
  ✅ Abstract models (TimeStampedModel, etc)
  ✅ Exceptions base
  ✅ Middleware
  ✅ Permissions DRF base

Eliminar:
  ❌ Modelos concretos
  ❌ Services específicos
  ❌ Serializers específicos
  ❌ ViewSets específicos
```

---

## 7. IMPACTO EN OTRAS APPS

### apps/dashboard/ (futura)

```yaml
Relación con pipeline:
  - Importa Center, Service, CallRecord
  - FK opcionales a Center (para filtros)
  - Consultas a CallRecord (para widgets)
  - NO crea CallRecord (solo lee)

Ejemplo:
  from apps.pipeline.models import Center, Service, CallRecord
  
  class Widget(models.Model):
      center = models.ForeignKey(Center, null=True)  # Filtro
      
      def get_data(self):
          return CallRecord.objects.filter(...)  # Consulta
```

---

### apps/reports/ (existente)

```yaml
Relación con pipeline:
  - Importa Center, Service, CallRecord
  - Usa para generar reportes
  - NO modifica

Ejemplo:
  from apps.pipeline.models import CallRecord
  
  class ReportGenerator:
      def generate_monthly_report(self, month):
          data = CallRecord.objects.filter(fecha__month=month)
          return self.render_excel(data)
```

---

## 8. VALIDACIÓN DE LA DECISIÓN

### Checklist de Validación

```yaml
✅ Pipeline es OWNER de CallRecord
✅ Pipeline CREA CallRecord
✅ dashboard/reports solo CONSUMEN
✅ Center, Service configuran ETL
✅ Cohesión: Todo ETL en pipeline
✅ Single Responsibility respetado
✅ Data Flow unidireccional
✅ No circular dependencies
✅ Testeable independiente
✅ Mantenible a largo plazo
```

---

## 9. CONCLUSIÓN

**La decisión de ubicar Center, Service, CallRecord en apps/pipeline/ es CORRECTA porque:**

1. **Pipeline es el OWNER** - Crea y gestiona estos datos
2. **Cohesión arquitectónica** - Todo el ETL en un lugar
3. **Single Responsibility** - Cada app una responsabilidad
4. **Data Flow claro** - IVR → pipeline → reports/dashboard
5. **Mantenibilidad** - Cambios ETL aislados en pipeline

**apps/ivr/ NO es opción porque:**
- Es readonly (MariaDB)
- Son datos crudos, no procesados
- Diferentes bases de datos

**apps/dashboard/ NO es opción porque:**
- Solo visualiza, no crea datos
- Viola Single Responsibility
- Dependencia inversa incorrecta

**apps/reports/ NO es opción porque:**
- Solo genera outputs, no crea datos
- No tiene lógica ETL

---

**DECISIÓN FINAL:**
```yaml
✅ Center → apps/pipeline/models.py
✅ Service → apps/pipeline/models.py
✅ CallRecord → apps/pipeline/models.py
✅ apps/ivr_legacy/ → apps/ivr/
```

---

**FIN DEL DOCUMENTO**

**Decisión validada ✅**  
**Flujo ETL preservado ✅**  
**Arquitectura correcta ✅**
