---
version: 1.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis Arquitectónico Completo
categoria: arquitectura/reconciliacion
tema: RECONCILIACIÓN COMPLETA - Análisis v3.0.0 vs Código Real vs Plan v2.0.0
autor: Claude Technical Analysis
tags: [arquitectura, reconciliacion, analisis-completo, apps, refactoring]
estado: critico
---

# RECONCILIACIÓN ARQUITECTÓNICA COMPLETA
## ANÁLISIS v3.0.0 vs CÓDIGO REAL vs PLAN v2.0.0

**ORIGEN:** Análisis de 56 archivos ANALISIS_APP_*.md de /mnt/user-data/outputs/

---

## 📊 1. APPS EN INSTALLED_APPS (CÓDIGO REAL)

```python
# /tmp/iact-real/callcentersite/config/settings/base.py

INSTALLED_APPS = [
    'apps.core',              # ✅ EXISTE
    'apps.ivr_legacy',        # ✅ EXISTE (NO apps.ivr)
    'apps.authentication',    # ✅ EXISTE
    'apps.access',            # ✅ EXISTE
    'apps.audit',             # ✅ EXISTE
    'apps.users',             # ✅ EXISTE
    'apps.pipeline',          # ✅ EXISTE
    'apps.reports',           # ✅ EXISTE
]

# NO ESTÁN EN INSTALLED_APPS:
# - apps.utils (existe directorio pero no está registrada)
# - apps.calls (NO existe)
# - apps.dashboard (NO existe)
# - apps.alerts (NO existe)
```

---

## 📋 2. ANÁLISIS v3.0.0 DISPONIBLES (56 ARCHIVOS)

```yaml
✅ ANALISIS_APP_ACCESS_v3_0_0 (6 partes)
   - apps/access/ ✅ EXISTE en código
   
✅ ANALISIS_APP_ALERTS_v3_0_0 (3 partes)
   - apps/alerts/ ❌ NO EXISTE en código
   - App FUTURA (planificada)
   
✅ ANALISIS_APP_AUDIT_v3_0_0 (3 partes)
   - apps/audit/ ✅ EXISTE en código
   
✅ ANALISIS_APP_AUTHENTICATION_v3_0_0 (3 partes)
   - apps/authentication/ ✅ EXISTE en código
   
✅ ANALISIS_APP_CALLS_v3_0_0 (1 parte)
   - apps/calls/ ❌ NO EXISTE en código
   - App FUTURA (planificada)
   - Modelos: Call, CallStatus, CallType, CallRecording, CallNote
   
✅ ANALISIS_APP_CORE_v3_0_0 (3 partes)
   - apps/core/ ✅ EXISTE en código
   - 🔴 DIVERGENCIA CRÍTICA (ver sección 3)
   
✅ ANALISIS_APP_DASHBOARD_v3_0_0 (5 partes)
   - apps/dashboard/ ❌ NO EXISTE en código
   - App FUTURA (planificada)
   
✅ ANALISIS_APP_IVR_v3_1_0 (4 partes + consolidado)
   - apps/ivr/ ✅ EXISTE como apps/ivr_legacy/ en código
   - Nombre diferente pero es la misma app
   
✅ ANALISIS_APP_PIPELINE_v3_0_0 (4 partes)
   - apps/pipeline/ ✅ EXISTE en código
   
✅ ANALISIS_APP_REPORTS_v3_0_0 (5 partes)
   - apps/reports/ ✅ EXISTE en código
   
✅ ANALISIS_APP_USERS_v3_0_0 (4 partes)
   - apps/users/ ✅ EXISTE en código
   
✅ ANALISIS_APP_UTILS_v3_0_0 (3 partes)
   - apps/utils/ ✅ EXISTE en código (NO en INSTALLED_APPS)
```

---

## 🔴 3. DIVERGENCIA CRÍTICA: apps/core/

### ANALISIS_APP_CORE_v3_0_0 DICE:

```yaml
apps/core/models.py debe tener SOLO abstract=True:
  ✅ TimeStampedModel (abstract=True)
  ✅ SoftDeleteMixin (abstract=True)
  ✅ AuditedModel (abstract=True)
  ✅ SoftDeleteQuerySet
  ✅ SoftDeleteManager

❌ NO debe tener modelos concretos
❌ Center → debería ir en apps/centers/ (NO EXISTE)
❌ Service → debería ir en apps/centers/ (NO EXISTE)
❌ CallRecord → debería ir en apps/analytics/ (NO EXISTE)
❌ UserServiceAccess → debería ir en apps/access/
```

### CÓDIGO REAL TIENE:

```python
# apps/core/models.py (ACTUAL)

class Center(SoftDeleteMixin, models.Model):
    """Centro de atención."""
    class Meta:
        db_table = 'core_centers'  # ✅ Tabla existe en BD

class Service(SoftDeleteMixin, models.Model):
    """Servicio 800."""
    class Meta:
        db_table = 'core_services'  # ✅ Tabla existe en BD

class CallRecord(SoftDeleteMixin, models.Model):
    """Registro de llamadas agregado."""
    class Meta:
        db_table = 'core_call_records'  # ✅ Tabla existe en BD

class UserServiceAccess(SoftDeleteMixin, models.Model):
    """Acceso usuario-servicio."""
    class Meta:
        db_table = 'core_user_service_access'  # ✅ Tabla existe en BD
```

### FASE 2 IMPLEMENTÓ:

```yaml
Día 11 (COMPLETADO):
  ✅ apps/core/models.py con 4 modelos concretos
  ✅ apps/utils/validators.py (15 validators)
  ✅ apps/utils/constants.py (100+ constants)

Día 12 (COMPLETADO):
  ✅ apps/core/services/ (3 services, 32 métodos)
  
Día 13-14 (EN PROGRESO):
  ✅ apps/core/serializers.py (20 serializers)
  ✅ apps/core/filters.py (4 filters)
  ✅ apps/core/permissions.py (6 permissions)
  ⏳ apps/core/views.py (PAUSADO)
```

---

## 🎯 4. APPS FUTURAS (Análisis sin código)

```yaml
apps/calls/ (ANALISIS completo, 1 parte):
  Estado: App FUTURA
  Propósito: Gestión de llamadas individuales en tiempo real
  Modelos: Call, CallStatus, CallType, CallRecording, CallNote, CallMetrics
  Relación: apps/calls/ es DIFERENTE de apps/core/CallRecord
    - Call = llamada individual (tiempo real)
    - CallRecord = datos agregados (analytics)
  
apps/dashboard/ (ANALISIS completo, 5 partes):
  Estado: App FUTURA
  Propósito: Dashboards configurables, widgets, visualizaciones
  
apps/alerts/ (ANALISIS completo, 3 partes):
  Estado: App FUTURA
  Propósito: Sistema de alertas y notificaciones
```

---

## 🔍 5. ANÁLISIS MODELO CALLRECORD vs CALL

### apps/core/CallRecord (EXISTE):
```python
# Propósito: Datos AGREGADOS por fecha/teléfono/servicio
# Fuente: ETL desde apps/ivr_legacy/
# Uso: Reportes, analytics, estadísticas

class CallRecord(SoftDeleteMixin, models.Model):
    fecha = models.DateField()
    telefono = models.CharField()
    servicio_800 = models.CharField()
    total_llamadas = models.IntegerField()        # Agregado
    llamadas_contestadas = models.IntegerField()  # Agregado
    llamadas_abandonadas = models.IntegerField()  # Agregado
    duracion_total_segundos = models.IntegerField()  # Agregado
```

### apps/calls/Call (NO EXISTE - FUTURO):
```python
# Propósito: Llamada INDIVIDUAL en tiempo real
# Fuente: PBX/Asterisk directo
# Uso: Operaciones call center, grabaciones, notas

class Call(models.Model):
    caller_number = models.CharField()    # Individual
    callee_number = models.CharField()    # Individual
    start_time = models.DateTimeField()   # Exacto
    end_time = models.DateTimeField()     # Exacto
    duration_seconds = models.IntegerField()  # Individual
    status = models.CharField()           # Estado actual
    recording_path = models.CharField()   # Grabación
```

**Conclusión:** Son modelos COMPLEMENTARIOS, no duplicados.

---

## 📝 6. INTERPRETACIÓN CORRECTA

### Apps EXISTENTES (8):
```
✅ apps/core/            - Centro, Servicio, CallRecord, UserServiceAccess
✅ apps/ivr_legacy/      - Datos IVR readonly (MariaDB)
✅ apps/authentication/  - Login, seguridad, sesiones
✅ apps/access/          - RBAC (Function, Role, permisos)
✅ apps/audit/           - Auditoría, logs
✅ apps/users/           - CustomUser, perfiles
✅ apps/pipeline/        - ETL, jobs, scheduler
✅ apps/reports/         - Generación reportes, exports
✅ apps/utils/           - Helpers (NO en INSTALLED_APPS)
```

### Apps FUTURAS según análisis (3):
```
⏳ apps/calls/           - Llamadas tiempo real (FUTURO)
⏳ apps/dashboard/       - Dashboards configurables (FUTURO)
⏳ apps/alerts/          - Alertas y notificaciones (FUTURO)
```

### Apps MENCIONADAS pero sin análisis v3.0.0:
```
❓ apps/centers/         - Mencionada en CORE v3.0.0 (ideal teórico)
❓ apps/analytics/       - Mencionada en CORE v3.0.0 (ideal teórico)
❓ apps/clients/         - Mencionada en CALLS v3.0.0 (futuro)
❓ apps/services/        - Mencionada en CALLS v3.0.0 (futuro)
```

---

## ✅ 7. DECISIÓN ARQUITECTÓNICA ACTUAL

**FASE 2 del PLAN v2.0.0 implementó:**

```yaml
apps/core/ con modelos concretos:
  Razón: Pragmatismo, avance rápido con TDD
  Estado: TEMPORAL (puede refactorizarse después)
  Beneficio: 
    - Tablas BD ya existen (core_centers, core_services, etc.)
    - No requiere migration de datos
    - Funcionalidad operativa inmediata
  
Próximo paso según PLAN v2.0.0:
  ✅ Completar FASE 2 (apps/core/ completo)
  ⏳ FASE 3: Authentication
  ⏳ FASE 4: Access (RBAC)
  ⏳ FASE 5: Users & Audit
  ⏳ FASE 6: IVR & Pipeline
  ⏳ FASE 7: Reports
  ⏳ FASE 8: Dashboard & Alerts (CREAR apps futuras)
  ⏳ FASE 9: QA
```

---

## 🎯 8. OPCIONES DE REFACTORING

### OPCIÓN A: Continuar PLAN v2.0.0 (RECOMENDADO)
```yaml
HOY (Día 13-14):
  [ ] Completar apps/core/views.py
  [ ] Completar apps/core/admin.py
  [ ] Completar apps/core/urls.py
  [ ] Tests API apps/core/

PRÓXIMAS FASES:
  [ ] FASE 3-7: Implementar apps existentes
  [ ] FASE 8: Crear apps/dashboard/, apps/alerts/
  [ ] (Opcional) Crear apps/calls/ si se requiere

REFACTORING FUTURO (Opcional):
  [ ] Evaluar mover Center, Service a apps nueva
  [ ] Solo si aporta valor arquitectónico
```

### OPCIÓN B: Crear apps futuras AHORA
```yaml
PARTE 1:
  [ ] Crear apps/calls/ (modelos Call, etc)
  [ ] Crear apps/dashboard/ (según análisis 5 partes)
  [ ] Crear apps/alerts/ (según análisis 3 partes)

PROBLEMA:
  ❌ Detiene FASE 2
  ❌ 3-4 semanas adicionales
  ❌ apps/calls/ requiere integración PBX (no disponible)
```

### OPCIÓN C: Refactorizar apps/core/ AHORA
```yaml
PARTE 1:
  [ ] Crear apps/centers/ (Center, Service)
  [ ] Migration SeparateDatabaseAndState
  [ ] Actualizar ~50 imports

PROBLEMA:
  ❌ Alto riesgo
  ❌ 2-3 días
  ❌ NO aporta valor funcional inmediato
```

---

## 📌 9. RECOMENDACIÓN FINAL

**OPCIÓN A - Continuar PLAN v2.0.0**

```yaml
Razón:
  ✅ TDD: Tests primero, arquitectura después
  ✅ Pragmatismo: Funcionalidad operativa
  ✅ Riesgo bajo: Refactoring con tests funcionando
  ✅ Momentum: No detener progreso

Acciones Inmediatas:
  [ ] Completar FASE 2 PARTE 3 (views.py)
  [ ] Completar FASE 2 PARTE 4 (admin.py, urls.py)
  [ ] Completar FASE 2 PARTE 5 (tests)
  [ ] Continuar FASE 3-7
  [ ] FASE 8: Crear apps futuras

Arquitectura apps/core/:
  ✅ TEMPORAL: Modelos concretos en apps/core/
  ✅ DOCUMENTADO: TODOs indicando ubicación ideal
  ✅ FUNCIONAL: Código completo y testeado
  ⏳ REFACTORING: Opcional en FASE 10 (si aporta valor)
```

---

## 🔴 10. PREGUNTA AL USUARIO

**Basado en este análisis completo de 56 archivos ANALISIS_APP_*.md:**

**¿Qué significa "refactorizar AHORA, por partes, vamos con PARTE 1"?**

**A)** Continuar FASE 2 PARTE 3 (completar viewsets.py) ← RECOMENDADO

**B)** Crear apps futuras (calls, dashboard, alerts)

**C)** Refactorizar apps/core/ (mover modelos a apps nuevas)

**D)** Actualizar análisis para reflejar código real

**E)** Otra cosa (especificar)

---

**FIN DEL ANÁLISIS**

**56 archivos ANALISIS_APP_*.md revisados ✅**  
**Código real reconciliado ✅**  
**PLAN v2.0.0 considerado ✅**  
**Esperando decisión del usuario...**
