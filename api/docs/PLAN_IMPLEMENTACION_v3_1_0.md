---
version: 3.1.0
date: 2026-01-20
project: IACT Call Center System
type: Plan de Implementación Completo
categoria: implementacion
tema: PLAN v3.1.0 - Arquitectura Correcta + Apps Futuras
autor: Claude Technical Analysis
tags: [plan, implementacion, refactoring, dashboard, alerts, core, pipeline]
documentos_base:
  - RELACIONES_v3_0_0.md
  - 56 archivos ANALISIS_APP_*.md v3.0.0
  - PLAN_IMPLEMENTACION_v2_0_0.md
  - RECONCILIACION_COMPLETA_ANALISIS_v1_0_0.md
estado: plan-completo
replaces: 
  - PLAN_IMPLEMENTACION_v2_0_0.md
  - PLAN_IMPLEMENTACION_v3_0_0.md
---

# PLAN DE IMPLEMENTACIÓN v3.1.0 - IACT
## ARQUITECTURA CORRECTA + APPS DASHBOARD Y ALERTS

**CAMBIOS CRÍTICOS desde v3.0.0:**
```yaml
❌ NO crear: apps/centers/, apps/analytics/, apps/calls/
✅ SÍ crear: apps/dashboard/, apps/alerts/
✅ Refactorizar apps/core/ (SOLO abstract models)
✅ Center, Service, CallRecord → apps/pipeline/ ⭐ (dueño de datos ETL)
✅ apps/ivr_legacy/ → apps/ivr/ (renombrar)
✅ Tests centralizados en /tmp/.../callcentersite/tests/
✅ Factories (137) + Mocks (81) + conftest (246 fixtures) ✅ LISTOS

RAZÓN apps/pipeline/:
  Pipeline es el DUEÑO de estos datos:
  - Lee IVR crudo (apps/ivr/)
  - CREA CallRecord procesado (output ETL)
  - USA Center/Service para configurar qué procesar
  - reports/dashboard solo CONSUMEN los datos
```

---

## 📊 CONTEXTO Y ESTADO ACTUAL

### Estado de Implementación

```yaml
✅ COMPLETADO (Días 1-12):
  FASE 1 - Testing Infrastructure (Días 1-5):
    ✅ tests/factories/ (137 factories)
    ✅ tests/mocks/ (81 mocks)
    ✅ tests/conftest.py (246+ fixtures)
  
  FASE 2 PARTE 1 (Día 11):
    ✅ apps/core/models.py (4 modelos - TEMPORAL)
    ✅ apps/utils/validators.py (15 validators)
    ✅ apps/utils/constants.py (100+ constants)
  
  FASE 2 PARTE 2 (Día 12):
    ✅ apps/core/services/ (3 services - TEMPORAL)
      - CenterService (9 métodos)
      - ServiceService (12 métodos)
      - CallRecordService (11 métodos)

⏳ EN PROGRESO (Día 13-14):
  FASE 2 PARTE 3:
    ✅ apps/core/serializers.py (20 serializers - TEMPORAL)
    ✅ apps/core/filters.py (4 filters - TEMPORAL)
    ✅ apps/core/permissions.py (6 permissions - TEMPORAL)
    ❌ apps/core/views.py (PAUSADO)

Apps Existentes en Código: 9
  ✅ apps/access/
  ✅ apps/audit/
  ✅ apps/authentication/
  ✅ apps/core/ (CON PROBLEMAS)
  ✅ apps/ivr_legacy/
  ✅ apps/pipeline/
  ✅ apps/reports/
  ✅ apps/users/
  ✅ apps/utils/

Apps FUTURAS a Crear: 2
  ⏳ apps/dashboard/
  ⏳ apps/alerts/

Apps que NO se van a crear:
  ❌ apps/centers/
  ❌ apps/analytics/
  ❌ apps/calls/
```

---

## 🎯 OBJETIVOS DEL PLAN v3.0.0

### Objetivo Principal
Implementar arquitectura CORRECTA basada en ANALISIS_APP_v3_0_0, crear apps/dashboard/ y apps/alerts/, refactorizar apps/core/, y completar testing completo del sistema.

### Objetivos Específicos

```yaml
1. Refactorizar apps/core/:
   - Eliminar modelos concretos (Center, Service, CallRecord, UserServiceAccess)
   - Dejar SOLO abstract models (TimeStampedModel, SoftDeleteMixin, AuditedModel)
   - Mover validators a apps/utils/
   - Mover services/serializers/filters a apps correctas

2. Decidir ubicación de modelos:
   - Center, Service → apps/dashboard/ o apps/reports/
   - CallRecord → apps/dashboard/ (datos agregados para widgets)
   - UserServiceAccess → apps/access/ (control de permisos)

3. Crear apps/dashboard/:
   - Implementar según ANALISIS_APP_DASHBOARD_v3_0_0 (5 partes)
   - Dashboards configurables
   - Widgets dinámicos
   - Integración con IVR/Reports

4. Crear apps/alerts/:
   - Implementar según ANALISIS_APP_ALERTS_v3_0_0 (3 partes)
   - Sistema de alertas
   - Notificaciones internas
   - Suscripciones

5. Testing completo:
   - Unit tests para todas las apps
   - Integration tests
   - API tests
   - >85% coverage
```

---

## 📋 CRONOGRAMA GENERAL (16 SEMANAS)

```
Semanas 1-2:   FASE 1 - Testing Infrastructure ✅ COMPLETADO
Semana 3:      FASE 2 - Refactoring apps/core/ 🔴 EN PROGRESO
Semanas 4-5:   FASE 3 - apps/dashboard/ (5 partes)
Semana 6:      FASE 4 - apps/alerts/ (3 partes)
Semanas 7-8:   FASE 5 - Migrar modelos de apps/core/
Semanas 9-10:  FASE 6 - Completar apps existentes
Semanas 11-12: FASE 7 - Integration Testing
Semanas 13-14: FASE 8 - API Testing
Semanas 15-16: FASE 9 - QA & Deployment

TOTAL: 16 semanas (~4 meses)
```

---

## 🔴 FASE 2: REFACTORING apps/core/ (Semana 3 - 7 días)

### Objetivo
Limpiar apps/core/ dejando SOLO componentes abstractos según ANALISIS_APP_CORE_v3_0_0.

### Decisión Arquitectónica: Ubicación de Modelos

**DECISIÓN FINAL:**
```yaml
Center, Service, CallRecord:
  Ubicación: apps/pipeline/ ⭐ CORRECTO
  Razón: 
    - Pipeline es el DUEÑO de estos datos (los crea)
    - CallRecord es OUTPUT del ETL (pipeline lo escribe)
    - Center, Service son configuración ETL (qué procesar)
    - Cohesión: Todo el ciclo ETL en un lugar
  
  Flujo:
    apps/ivr/ (readonly MariaDB) 
      → apps/pipeline/ (ETL procesa) 
      → CallRecord (PostgreSQL writable)
      → apps/reports/ + apps/dashboard/ (consumen)

UserServiceAccess:
  Ubicación: apps/access/
  Razón: Control de permisos y accesos (naturaleza RBAC)
  Relación: Similar a UserGroup, GroupFunction

apps/ivr_legacy/:
  Renombrar a: apps/ivr/
  Razón: Nombre más limpio, menos confuso
  Contenido: Modelos readonly MariaDB (sin cambios)
```

---

### PARTE 1: Preparación y Decisiones (Día 15)

**Objetivo:** Documentar y planificar refactoring.

**Tareas:**
```yaml
1. Documentar estado actual:
   [ ] Listar TODOS los imports de Center, Service, CallRecord
   [ ] grep -r "from apps.core.models import" callcentersite/
   [ ] Crear MIGRATION_PLAN_CORE.md

2. Decidir ubicación final (CONFIRMADO):
   [✅] Center, Service, CallRecord → apps/pipeline/
   [✅] UserServiceAccess → apps/access/
   [✅] apps/ivr_legacy/ → apps/ivr/

3. Renombrar apps/ivr_legacy/ → apps/ivr/:
   [ ] mv callcentersite/apps/ivr_legacy/ callcentersite/apps/ivr/
   [ ] Actualizar INSTALLED_APPS:
       'apps.ivr_legacy' → 'apps.ivr'
   [ ] Actualizar imports:
       from apps.ivr_legacy → from apps.ivr
   [ ] Actualizar database router (IVRRouter)
   [ ] Tests de regresión

4. Verificar apps/pipeline/ existe:
   [ ] Revisar estructura actual
   [ ] Planificar integración de modelos

5. Plan de migrations:
   [ ] Migrations SeparateDatabaseAndState
   [ ] Preservar db_table (sin cambios en BD)
```

**Script para renombrar ivr_legacy:**
```bash
#!/bin/bash
# rename_ivr_legacy.sh

# 1. Renombrar directorio
mv callcentersite/apps/ivr_legacy callcentersite/apps/ivr

# 2. Actualizar imports en todo el código
find callcentersite -name "*.py" -exec sed -i \
  's/from apps\.ivr_legacy/from apps.ivr/g' {} \;
  
find callcentersite -name "*.py" -exec sed -i \
  's/import apps\.ivr_legacy/import apps.ivr/g' {} \;

# 3. Actualizar tests
find tests -name "*.py" -exec sed -i \
  's/from apps\.ivr_legacy/from apps.ivr/g' {} \;

# 4. Actualizar settings
sed -i "s/'apps\.ivr_legacy'/'apps.ivr'/g" callcentersite/config/settings/base.py

echo "✅ Renombre completado. Ejecutar tests para validar."
```

**Deliverable:** MIGRATION_PLAN_CORE.md

**Tiempo:** 1 día

---

### PARTE 2: Ampliar apps/pipeline/ (Día 16)

**Objetivo:** Preparar apps/pipeline/ para recibir Center, Service, CallRecord.

**apps/pipeline/ ya existe con:**
```bash
apps/pipeline/
├── models.py         # JobExecution, JobLog, ScheduledJob ✅
├── services/         # ETLService, SchedulerService ✅
└── ...
```

**Ampliar para recibir modelos de apps/core/:**
```bash
apps/pipeline/
├── models.py                 # Agregar: Center, Service, CallRecord
├── admin.py                  # Admin para todos los modelos
├── services/
│   ├── etl_service.py        # ✅ Ya existe
│   ├── center_service.py     # Mover desde apps/core/
│   ├── service_service.py    # Mover desde apps/core/
│   └── call_record_service.py # Mover desde apps/core/
├── serializers.py            # Mover desde apps/core/
├── filters.py                # Mover desde apps/core/
├── permissions.py            # Mover desde apps/core/
└── views.py               # Mover desde apps/core/
```

**Tareas:**
```yaml
1. Verificar apps/pipeline/ existe:
   [ ] Revisar estructura actual
   [ ] Identificar modelos existentes

2. Preparar models.py:
   [ ] Abrir apps/pipeline/models.py
   [ ] Planificar dónde agregar Center, Service, CallRecord
   [ ] (No tocar aún, solo planificar)

3. Verificar en INSTALLED_APPS:
   [ ] config/settings/base.py
   [ ] 'apps.pipeline' debe estar registrado
```

**Tiempo:** 2 horas

---

### PARTE 3: Mover Modelos a apps/pipeline/ (Día 17)

**Objetivo:** Mover Center, Service, CallRecord de apps/core/ a apps/pipeline/.

**Tareas:**
```yaml
1. Copiar modelos a apps/pipeline/models.py:
   [ ] Center → apps/pipeline/models.py
   [ ] Service → apps/pipeline/models.py
   [ ] CallRecord → apps/pipeline/models.py
   [ ] Preservar db_table (sin cambios en BD)

2. Crear migration SeparateDatabaseAndState:
   # apps/pipeline/migrations/000X_move_from_core.py
   
   operations = [
       migrations.SeparateDatabaseAndState(
           database_operations=[
               # NADA - tablas ya existen
           ],
           state_operations=[
               migrations.CreateModel(
                   name='Center',
                   fields=[...],
                   options={'db_table': 'core_centers'},
               ),
               migrations.CreateModel(
                   name='Service',
                   fields=[...],
                   options={'db_table': 'core_services'},
               ),
               migrations.CreateModel(
                   name='CallRecord',
                   fields=[...],
                   options={'db_table': 'core_call_records'},
               ),
           ],
       ),
   ]

3. Migration en apps/core/:
   # apps/core/migrations/000X_remove_concrete_models.py
   
   operations = [
       migrations.SeparateDatabaseAndState(
           database_operations=[
               # NADA - no tocar BD
           ],
           state_operations=[
               migrations.DeleteModel(name='Center'),
               migrations.DeleteModel(name='Service'),
               migrations.DeleteModel(name='CallRecord'),
           ],
       ),
   ]
```

**Tiempo:** 1 día

---

### PARTE 4: Actualizar Imports (Día 18)

**Objetivo:** Actualizar TODOS los imports en el código.

**Archivos a actualizar (~50 archivos):**
```python
# ANTES
from apps.core.models import Center, Service, CallRecord

# DESPUÉS
from apps.pipeline.models import Center, Service, CallRecord
```

**Tareas:**
```yaml
1. Actualizar imports en apps:
   [ ] apps/core/services/ (antes de mover)
   [ ] apps/core/serializers.py
   [ ] apps/core/filters.py
   [ ] apps/core/permissions.py
   [ ] apps/reports/ (si usa Center/Service)
   [ ] apps/dashboard/ (cuando se cree)

2. Actualizar tests:
   [ ] tests/factories/core.py
   [ ] tests/unit/core/
   [ ] tests/unit/pipeline/
   [ ] tests/integration/
   [ ] tests/api/

3. Ejecutar tests:
   [ ] pytest tests/ -v
   [ ] Verificar que todo pasa
```

**Script helper:**
```bash
#!/bin/bash
# update_imports.sh

find callcentersite/apps -name "*.py" -exec sed -i \
  's/from apps\.core\.models import Center/from apps.pipeline.models import Center/g' {} \;

find callcentersite/apps -name "*.py" -exec sed -i \
  's/from apps\.core\.models import Service/from apps.pipeline.models import Service/g' {} \;

find callcentersite/apps -name "*.py" -exec sed -i \
  's/from apps\.core\.models import CallRecord/from apps.pipeline.models import CallRecord/g' {} \;
  
# También actualizar tests
find callcentersite/tests -name "*.py" -exec sed -i \
  's/from apps\.core\.models import Center/from apps.pipeline.models import Center/g' {} \;
  
find callcentersite/tests -name "*.py" -exec sed -i \
  's/from apps\.core\.models import Service/from apps.pipeline.models import Service/g' {} \;
  
find callcentersite/tests -name "*.py" -exec sed -i \
  's/from apps\.core\.models import CallRecord/from apps.pipeline.models import CallRecord/g' {} \;
```

**Tiempo:** 1 día

---

### PARTE 5: Mover Services/Serializers (Día 19)

**Objetivo:** Mover services, serializers, filters, permissions a apps/pipeline/.

**Tareas:**
```yaml
1. Mover services:
   [ ] apps/core/services/center_service.py → apps/pipeline/services/
   [ ] apps/core/services/service_service.py → apps/pipeline/services/
   [ ] apps/core/services/call_record_service.py → apps/pipeline/services/
   [ ] Actualizar imports internos

2. Mover serializers:
   [ ] apps/core/serializers.py → apps/pipeline/serializers.py
   [ ] Filtrar solo serializers de Center/Service/CallRecord
   [ ] Actualizar imports

3. Mover filters:
   [ ] apps/core/filters.py → apps/pipeline/filters.py
   [ ] Filtrar solo filters de Center/Service/CallRecord

4. Mover permissions:
   [ ] apps/core/permissions.py → apps/pipeline/permissions.py
   [ ] Filtrar solo permissions específicas

5. Crear/actualizar viewsets.py:
   [ ] apps/pipeline/views.py
   [ ] CenterViewSet, ServiceViewSet, CallRecordViewSet
   [ ] Integrar con ETL (custom actions)
```

**Tiempo:** 1 día

---

### PARTE 6: Limpiar apps/core/ (Día 20)

**Objetivo:** Dejar apps/core/ con SOLO componentes abstractos.

**apps/core/ FINAL:**
```python
# apps/core/models.py (CORRECTO)

class TimeStampedModel(models.Model):
    """Modelo base con timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # ✅

class SoftDeleteMixin(models.Model):
    """Mixin para soft delete."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True  # ✅
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

class AuditedModel(models.Model):
    """Modelo con auditoría."""
    created_by = models.ForeignKey(User, ...)
    updated_by = models.ForeignKey(User, ...)
    
    class Meta:
        abstract = True  # ✅
```

**Tareas:**
```yaml
1. Eliminar de apps/core/:
   [ ] Eliminar Center, Service, CallRecord, UserServiceAccess
   [ ] Eliminar apps/core/services/ (directorio completo)
   [ ] Eliminar apps/core/serializers.py
   [ ] Eliminar apps/core/filters.py
   [ ] Eliminar apps/core/permissions.py (custom)
   [ ] Eliminar apps/core/views.py

2. Mantener en apps/core/:
   [ ] models.py (SOLO abstract)
   [ ] exceptions.py (7 excepciones)
   [ ] validators.py (clases validadoras) - MOVER a apps/utils/
   [ ] middleware.py (4 middlewares)
   [ ] permissions.py (DRF base: RequiresFunctionPermission, etc)
   [ ] mixins.py (5 mixins)
   [ ] services.py (BaseService)

3. Mover validators a apps/utils/:
   [ ] apps/core/validators.py → apps/utils/validators.py
   [ ] Consolidar con validators existentes
   [ ] Actualizar imports
```

**Tiempo:** 4 horas

---

### PARTE 7: Mover UserServiceAccess a apps/access/ (Día 21)

**Objetivo:** Mover UserServiceAccess a apps/access/.

**Razón:** Es un modelo de control de acceso (RBAC), similar a UserGroup.

**Tareas:**
```yaml
1. Copiar modelo:
   [ ] UserServiceAccess → apps/access/models.py
   [ ] Preservar db_table='core_user_service_access'

2. Migration en apps/access/:
   # apps/access/migrations/000X_add_user_service_access.py
   
   operations = [
       migrations.SeparateDatabaseAndState(
           database_operations=[],
           state_operations=[
               migrations.CreateModel(
                   name='UserServiceAccess',
                   fields=[...],
                   options={'db_table': 'core_user_service_access'},
               ),
           ],
       ),
   ]

3. Migration en apps/core/:
   # Ya eliminado en PARTE 3

4. Actualizar imports:
   [ ] from apps.dashboard.models import UserServiceAccess
   [ ] → from apps.access.models import UserServiceAccess
   [ ] Script sed para actualizar

5. Actualizar Service.grant_access_to_user():
   [ ] apps/dashboard/models.py
   [ ] from apps.access.models import UserServiceAccess
```

**Tiempo:** 4 horas

---

### PARTE 8: Testing y Validación (Día 21)

**Objetivo:** Validar que todo funciona correctamente.

**Tareas:**
```yaml
1. Ejecutar migrations:
   [ ] python manage.py migrate pipeline
   [ ] python manage.py migrate access
   [ ] python manage.py migrate core
   [ ] Verificar que NO se alteran tablas

2. Ejecutar tests:
   [ ] pytest tests/unit/core/ -v
   [ ] pytest tests/unit/pipeline/ -v
   [ ] pytest tests/unit/access/ -v
   [ ] pytest tests/integration/ -v
   [ ] pytest tests/ -v (todos)

3. Verificar cobertura:
   [ ] coverage run -m pytest tests/
   [ ] coverage report
   [ ] Target: >85%

4. Smoke tests:
   [ ] python manage.py runserver
   [ ] Login funciona
   [ ] ETL funciona
   [ ] API funciona
   
5. Validar flujo ETL:
   [ ] apps/ivr/ (readonly) → lee datos
   [ ] apps/pipeline/ (ETL) → procesa
   [ ] CallRecord creado → verifica
   [ ] reports/dashboard → consumen OK
```

**Tiempo:** 4 horas

---

## ✅ RESUMEN FASE 2 (7 días)

```yaml
PARTE 1: Preparación (Día 15)
  ✅ Documentar estado actual
  ✅ Decidir ubicaciones:
      - Center, Service, CallRecord → apps/pipeline/
      - UserServiceAccess → apps/access/
      - apps/ivr_legacy/ → apps/ivr/
  ✅ Plan de migrations

PARTE 2: apps/pipeline/ preparación (Día 16)
  ✅ Verificar estructura existente
  ✅ Planificar adición de modelos

PARTE 3: Mover modelos (Día 17)
  ✅ Center, Service, CallRecord → apps/pipeline/
  ✅ Migrations SeparateDatabaseAndState

PARTE 4: Actualizar imports (Día 18)
  ✅ ~50 archivos actualizados
  ✅ Tests actualizados
  ✅ Script automatizado

PARTE 5: Mover services/serializers (Día 19)
  ✅ Services → apps/pipeline/services/
  ✅ Serializers, filters, permissions

PARTE 6: Limpiar apps/core/ (Día 20)
  ✅ SOLO abstract models
  ✅ Mover validators a apps/utils/

PARTE 7: UserServiceAccess (Día 21)
  ✅ Mover a apps/access/

PARTE 8: Testing (Día 21)
  ✅ Migrations
  ✅ Tests >85%
  ✅ Smoke tests
  ✅ Validar flujo ETL completo

Resultado:
  ✅ apps/core/ limpio (solo abstract)
  ✅ apps/pipeline/ con Center, Service, CallRecord
  ✅ apps/access/ con UserServiceAccess
  ✅ apps/ivr_legacy/ → apps/ivr/ (renombrado)
  ✅ NO cambios en BD (tablas preservadas)
  ✅ Tests pasando
  ✅ Flujo ETL validado: ivr → pipeline → reports/dashboard
```

---

## 🎨 FASE 3: apps/dashboard/ Completa (Semanas 4-5 - 10 días)

### Objetivo
Implementar apps/dashboard/ según ANALISIS_APP_DASHBOARD_v3_0_0 (5 partes).

**NOTA:** Center, Service, CallRecord ya están en apps/pipeline/. apps/dashboard/ solo consume estos datos.

### PARTE 1: Crear apps/dashboard/ y Modelos Base (Día 22-23)

**Crear app desde cero:**
```bash
apps/dashboard/
├── __init__.py
├── apps.py                   # DashboardConfig
├── models.py                 # NUEVOS modelos (no mover desde core)
├── admin.py
├── urls.py
├── services/
│   ├── __init__.py
│   ├── dashboard_service.py
│   ├── widget_service.py
│   └── data_service.py
├── serializers.py
├── filters.py
├── permissions.py
├── views.py
└── migrations/
    └── __init__.py
```

**Modelos NUEVOS según análisis:**
```python
# apps/dashboard/models.py

⏳ DashboardConfig       - Configuración de dashboards
⏳ Widget                - Widgets individuales
⏳ WidgetConfig          - Configuración de widgets
⏳ UserDashboard         - Dashboards personalizados
⏳ DashboardLayout       - Layout de widgets

# Relaciones con apps/pipeline/:
from apps.pipeline.models import Center, Service, CallRecord

# Los widgets CONSUMEN datos de pipeline (FK o queries)
```

**Tareas:**
```yaml
Día 22:
  [ ] Crear apps/dashboard/ (estructura completa)
  [ ] Registrar en INSTALLED_APPS
  [ ] Revisar ANALISIS_APP_DASHBOARD_v3_0_0 (5 partes)
  [ ] Diseñar modelos DashboardConfig, Widget
  [ ] Implementar modelos base
  [ ] Tests unitarios

Día 23:
  [ ] Implementar WidgetConfig, UserDashboard
  [ ] Implementar DashboardLayout
  [ ] Relaciones con apps/pipeline.models
  [ ] FK a Center, Service (opcional)
  [ ] Tests unitarios
  [ ] Coverage >85%
```

**Tiempo:** 2 días

---

### PARTE 2: Services Dashboard (Día 24-25)

**Services NUEVOS:**
```yaml
Services para gestionar dashboards:
  ⏳ DashboardService (CRUD dashboards)
  ⏳ WidgetService (CRUD widgets)
  ⏳ LayoutService (layouts)
  ⏳ DataService (agregación datos desde pipeline)
```

**Tareas:**
```yaml
Día 24:
  [ ] DashboardService (CRUD dashboards)
  [ ] WidgetService (CRUD widgets)
  [ ] Integración con apps/pipeline.models
  [ ] Tests unitarios

Día 25:
  [ ] LayoutService (gestión layouts)
  [ ] DataService (consultas a CallRecord, Center, Service)
  [ ] Cache de widgets
  [ ] Tests unitarios
```

**Tiempo:** 2 días

---

### PARTE 3: API REST Dashboard (Día 26-27)

**ViewSets NUEVOS:**
```yaml
ViewSets para dashboard (no incluye Center/Service/CallRecord):
  ⏳ DashboardViewSet (CRUD dashboards)
  ⏳ WidgetViewSet (CRUD widgets + preview)
  ⏳ LayoutViewSet (gestión layouts)
  ⏳ UserDashboardViewSet (dashboards personalizados)
```

**NOTA:** CenterViewSet, ServiceViewSet, CallRecordViewSet están en apps/pipeline/

**Tareas:**
```yaml
Día 26:
  [ ] DashboardViewSet (CRUD + custom actions)
  [ ] WidgetViewSet (CRUD + preview + data)
  [ ] Serializers correspondientes
  [ ] Filters

Día 27:
  [ ] LayoutViewSet
  [ ] UserDashboardViewSet
  [ ] Permissions (DSH_VIEW, DSH_EDIT, etc)
  [ ] URLs y routing
  [ ] Tests API
  [ ] Integración con apps/pipeline.models (consume datos)
```

**Tiempo:** 2 días

---

### PARTE 4: Widgets y Visualización (Día 28-29)

**Tipos de Widgets:**
```yaml
Widgets básicos:
  ⏳ ChartWidget (gráficos)
  ⏳ TableWidget (tablas)
  ⏳ KPIWidget (indicadores)
  ⏳ MapWidget (mapas)

Widgets específicos:
  ⏳ CallVolumeWidget
  ⏳ AbandonRateWidget
  ⏳ ServicePerformanceWidget
```

**Tareas:**
```yaml
Día 28:
  [ ] Widget base classes
  [ ] ChartWidget, TableWidget
  [ ] KPIWidget
  [ ] Data aggregation

Día 29:
  [ ] CallVolumeWidget
  [ ] AbandonRateWidget
  [ ] ServicePerformanceWidget
  [ ] Tests widgets
```

**Tiempo:** 2 días

---

### PARTE 5: Admin y Testing (Día 30-31)

**Admin:**
```yaml
Admin interfaces NUEVOS:
  ⏳ DashboardAdmin
  ⏳ WidgetAdmin
  ⏳ LayoutAdmin
  ⏳ UserDashboardAdmin
```

**NOTA:** CenterAdmin, ServiceAdmin, CallRecordAdmin están en apps/pipeline/

**Tareas:**
```yaml
Día 30:
  [ ] Django Admin completo para modelos dashboard
  [ ] Inlines para widgets en dashboards
  [ ] Custom actions (clone dashboard, export config)
  [ ] List filters

Día 31:
  [ ] Tests completos (unit + integration + API)
  [ ] Coverage >85%
  [ ] Documentation
  [ ] README apps/dashboard/
  [ ] Validar integración con apps/pipeline/
```

**Tiempo:** 2 días

---

## 📢 FASE 4: apps/alerts/ (Semana 6 - 7 días)

### Objetivo
Implementar apps/alerts/ según ANALISIS_APP_ALERTS_v3_0_0 (3 partes).

### PARTE 1: Modelos Alerts (Día 32-33)

**Modelos:**
```python
# apps/alerts/models.py

⏳ AlertConfiguration    - Configuración de alertas
⏳ AlertSubscription     - Suscripciones
⏳ InternalMessage       - Mensajes internos
⏳ MessageRecipient      - Destinatarios
```

**Tareas:**
```yaml
Día 32:
  [ ] Revisar ANALISIS_APP_ALERTS_v3_0_0 (3 partes)
  [ ] AlertConfiguration model
  [ ] AlertSubscription model
  [ ] Tests unitarios

Día 33:
  [ ] InternalMessage model
  [ ] MessageRecipient model
  [ ] Relaciones entre modelos
  [ ] Tests >85%
```

**Tiempo:** 2 días

---

### PARTE 2: Services y Notificaciones (Día 34-35)

**Services:**
```yaml
Services:
  ⏳ AlertService (gestión alertas)
  ⏳ NotificationService (envío notificaciones)
  ⏳ SubscriptionService (suscripciones)
```

**Tareas:**
```yaml
Día 34:
  [ ] AlertService (CRUD, trigger alerts)
  [ ] NotificationService (envío interno)
  [ ] Tests

Día 35:
  [ ] SubscriptionService
  [ ] Alert rules evaluation
  [ ] Background tasks (APScheduler)
  [ ] Tests
```

**Tiempo:** 2 días

---

### PARTE 3: API y Admin (Día 36-38)

**API:**
```yaml
ViewSets:
  ⏳ AlertConfigurationViewSet
  ⏳ AlertSubscriptionViewSet
  ⏳ InternalMessageViewSet
```

**Tareas:**
```yaml
Día 36:
  [ ] ViewSets completos
  [ ] Serializers
  [ ] Permissions (ALR_*)

Día 37:
  [ ] Django Admin
  [ ] Custom actions
  [ ] Tests API

Día 38:
  [ ] Integration tests
  [ ] Coverage >85%
  [ ] Documentation
```

**Tiempo:** 3 días

---

## 🔄 FASE 5-9: Completar Sistema (Semanas 7-16)

### FASE 5: Apps Existentes (Semanas 7-8)

```yaml
Completar apps existentes según análisis:
  [ ] apps/access/ (6 partes análisis)
  [ ] apps/authentication/ (3 partes análisis)
  [ ] apps/audit/ (3 partes análisis)
  [ ] apps/users/ (4 partes análisis)
  [ ] apps/reports/ (5 partes análisis)
  [ ] apps/pipeline/ (4 partes análisis)
  [ ] apps/ivr_legacy/ (4 partes análisis)
```

---

### FASE 6-7: Testing (Semanas 9-14)

```yaml
Semana 9-10: Integration Testing
  [ ] Tests de integración entre apps
  [ ] Flujos completos (login → dashboard → reportes)
  [ ] ETL end-to-end

Semana 11-12: API Testing
  [ ] Tests de todos los endpoints
  [ ] Postman collections
  [ ] Load testing básico

Semana 13-14: Performance & Security
  [ ] Query optimization
  [ ] Security audit
  [ ] Penetration testing básico
```

---

### FASE 8-9: QA & Deployment (Semanas 15-16)

```yaml
Semana 15: QA
  [ ] Regression testing
  [ ] User acceptance testing
  [ ] Bug fixing

Semana 16: Deployment
  [ ] Production migrations
  [ ] Deployment scripts
  [ ] Monitoring setup
  [ ] Documentation final
```

---

## 📊 MÉTRICAS Y KPIs

```yaml
Cobertura de Tests:
  Target: >85% global
  Critical paths: >95%

Performance:
  API response: <200ms (p95)
  Dashboard load: <2s
  Report generation: <30s

Code Quality:
  Pylint score: >8.5
  Complejidad ciclomática: <10
  Duplicación: <3%

Seguridad:
  Todas las restricciones CNST cumplidas
  RBAC en todos los endpoints
  Auditoría completa
```

---

## 🎯 ENTREGABLES POR FASE

```yaml
FASE 2 (Refactoring apps/core/):
  ✅ apps/core/ limpio (solo abstract)
  ✅ apps/pipeline/ con Center, Service, CallRecord
  ✅ apps/access/ con UserServiceAccess
  ✅ apps/ivr_legacy/ → apps/ivr/ (renombrado)
  ✅ MIGRATION_PLAN_CORE.md
  ✅ Tests >85%
  ✅ Flujo ETL validado

FASE 3 (apps/dashboard/):
  ✅ 5+ modelos Django (DashboardConfig, Widget, etc)
  ✅ 4+ services (DashboardService, WidgetService, etc)
  ✅ 4+ ViewSets (sin duplicar pipeline)
  ✅ Django Admin completo
  ✅ Tests >85%
  ✅ README.md
  ✅ Integración con apps/pipeline/

FASE 4 (apps/alerts/):
  ✅ 4 modelos Django
  ✅ 3 services
  ✅ 3 ViewSets
  ✅ Django Admin
  ✅ Tests >85%
  ✅ README.md

FASE 5-9:
  ✅ Sistema completo funcionando
  ✅ Tests >85% global
  ✅ Documentation completa
  ✅ Deployment ready
```

---

## ⚠️ RIESGOS Y MITIGACIÓN

```yaml
Riesgo: Imports rotos durante refactoring
  Mitigación:
    - Script automatizado update_imports.sh
    - Tests exhaustivos después de cada cambio
    - Git commits incrementales

Riesgo: Migrations fallan
  Mitigación:
    - Usar SeparateDatabaseAndState
    - NO alterar tablas existentes
    - Backup de BD antes de migrations

Riesgo: Circular dependencies
  Mitigación:
    - Diseño cuidadoso de imports
    - apps/core/ solo abstract (sin FK)
    - Lazy imports donde sea necesario

Riesgo: Performance degradation
  Mitigación:
    - Profiling antes/después
    - Indexes optimizados
    - Cache en servicios críticos
```

---

## ✅ CRITERIOS DE ÉXITO

```yaml
Arquitectura:
  ✅ apps/core/ SOLO abstract models
  ✅ apps/pipeline/ con Center, Service, CallRecord
  ✅ apps/dashboard/ funcionando completo (consume pipeline)
  ✅ apps/alerts/ funcionando completo
  ✅ apps/ivr_legacy/ → apps/ivr/ renombrado
  ✅ Ninguna app fantasma (centers, analytics, calls)
  ✅ Flujo ETL validado: ivr → pipeline → reports/dashboard

Funcionalidad:
  ✅ TODAS las features funcionando
  ✅ Migrations sin errores
  ✅ API completa y documentada
  ✅ ETL jobs corriendo correctamente

Testing:
  ✅ >85% coverage global
  ✅ >95% critical paths
  ✅ 0 errores en pytest

Performance:
  ✅ API <200ms p95
  ✅ Dashboards <2s load
  ✅ ETL jobs <30min
  ✅ Sin queries N+1

Seguridad:
  ✅ RBAC en todos los endpoints
  ✅ Auditoría completa
  ✅ Todas las CNST cumplidas
  ✅ IVR readonly (CNST-002)
```

---

## 📋 PRÓXIMOS PASOS INMEDIATOS

```yaml
AHORA (próximas horas):
  [✅] Revisar este plan con usuario
  [✅] Confirmar decisiones arquitectónicas:
      - Center, Service, CallRecord → apps/pipeline/ ✅
      - UserServiceAccess → apps/access/ ✅
      - apps/ivr_legacy/ → apps/ivr/ ✅

MAÑANA (Día 15):
  [ ] Iniciar FASE 2 PARTE 1
  [ ] Renombrar apps/ivr_legacy/ → apps/ivr/
  [ ] Documentar estado actual
  [ ] Crear MIGRATION_PLAN_CORE.md
  [ ] Verificar apps/pipeline/ estructura

PRÓXIMA SEMANA (Días 16-21):
  [ ] Completar FASE 2 (Refactoring apps/core/)
  [ ] Mover Center, Service, CallRecord → apps/pipeline/
  [ ] Mover UserServiceAccess → apps/access/
  [ ] Migrations exitosas (SeparateDatabaseAndState)
  [ ] Tests >85%
  [ ] apps/core/ limpio (solo abstract)
  [ ] Validar flujo ETL completo
```

---

**FIN DEL PLAN v3.0.0**

**16 semanas estimadas**  
**Arquitectura correcta según análisis ✅**  
**Tests centralizados ✅**  
**Factories/Mocks listos ✅**  
**apps/dashboard/ y apps/alerts/ a crear ✅**
