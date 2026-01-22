---
version: 1.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis Crítico + Plan Actualizado
categoria: arquitectura/analisis
tema: Divergencia Código Real vs Análisis + Propuesta Plan Actualizado
autor: Claude Technical Analysis
tags: [analisis, divergencia, plan, refactoring, tdd]
documentos_base:
  - PLAN_IMPLEMENTACION_v2_0_0.md
  - ANALISIS_APP_CORE_v3_0_0.md (3 partes)
  - ANALISIS_APP_CALLS_v3_0_0.md
  - ANALISIS_APP_ACCESS_v3_0_0.md (6 partes)
  - TODOS los ANALISIS_APP_* (12 apps)
estado: critico
---

# ANÁLISIS DE DIVERGENCIA + PLAN ACTUALIZADO v1.0.0
## CÓDIGO REAL VS ANÁLISIS: RECONCILIACIÓN Y PROPUESTA

---

## 🔴 PROBLEMA DETECTADO

### Divergencia Crítica

```yaml
PLAN v2.0.0 FASE 2 dice:
  ✅ apps/core/models.py SOLO abstract=True
  ❌ NINGÚN modelo concreto

CÓDIGO REAL tiene:
  ❌ apps/core/models.py CON modelos concretos:
      - Center (db_table='core_centers')
      - Service (db_table='core_services')
      - CallRecord (db_table='core_call_records')
      - UserServiceAccess (db_table='core_user_service_access')

ANÁLISIS_APP_CORE v3.0.0 dice:
  ✅ Solo abstract models
  ❌ Modelos concretos deben ir en apps de negocio:
      - Center, Service → apps/centers/ o apps/services/
      - CallRecord → apps/analytics/ o apps/calls/
      - UserServiceAccess → apps/access/
```

**Conclusión:** El proyecto está en **refactorización** con modelos en ubicaciones temporales.

---

## 📊 ESTADO ACTUAL DEL PROYECTO

### Apps que EXISTEN Realmente

```bash
callcentersite/apps/
├── access/          ✅ EXISTE (Function model)
├── audit/           ✅ EXISTE (AuditLog model)
├── authentication/  ✅ EXISTE (SecurityQuestion, UserSecurityAnswer)
├── core/            ✅ EXISTE (Center, Service, CallRecord, UserServiceAccess) 🔴
├── ivr_legacy/      ✅ EXISTE (CallLog, etc - readonly)
├── pipeline/        ✅ EXISTE (ETLExecution, etc)
├── reports/         ✅ EXISTE (Report model)
├── users/           ✅ EXISTE (CustomUser model)
└── utils/           ✅ EXISTE (SoftDeleteMixin, validators, helpers)
```

### Apps con ANALISIS pero NO EXISTEN

```bash
❌ apps/centers/     - No existe (mencionada en análisis)
❌ apps/services/    - No existe (mencionada en análisis)
❌ apps/analytics/   - No existe (mencionada en análisis)
❌ apps/calls/       - No existe (pero hay ANALISIS_APP_CALLS_v3_0_0.md)
❌ apps/dashboard/   - No existe (pero hay ANALISIS_APP_DASHBOARD_v3_0_0.md)
❌ apps/alerts/      - No existe (pero hay ANALISIS_APP_ALERTS_v3_0_0.md)
```

---

## 🎯 ANÁLISIS DE OPCIONES

### Opción A: Refactorizar Ahora (Análisis Estricto)

**Mover modelos a apps correctas AHORA:**

```yaml
Crear nuevas apps:
  [ ] apps/centers/ (Center, Service models)
  [ ] apps/calls/ (CallRecord model)
  
Mover modelos:
  [ ] Center: core/ → centers/
  [ ] Service: core/ → centers/
  [ ] CallRecord: core/ → calls/
  [ ] UserServiceAccess: core/ → access/
  
Dejar en core/:
  [ ] SOLO TimeStampedModel (abstract=True)
  [ ] SOLO SoftDeleteMixin (abstract=True)
  [ ] SOLO AuditedModel (abstract=True)

Impacto:
  ✅ Arquitectura limpia desde el inicio
  ❌ Mucho refactoring inmediato
  ❌ Cambios masivos en imports
  ❌ Tests a actualizar
  ❌ 2-3 días adicionales
```

**PROS:**
- Arquitectura correcta desde el inicio
- Sigue ANALISIS_APP estrictamente
- apps/core/ queda limpio (solo abstract)
- Separación clara de responsabilidades

**CONTRAS:**
- 2-3 días de refactoring masivo
- Alto riesgo de romper código existente
- Cambios en muchos archivos simultáneamente
- Detiene progreso FASE 2

---

### Opción B: Refactorizar Después (Pragmático)

**MANTENER estructura actual, refactorizar en FASE dedicada:**

```yaml
AHORA (FASE 2):
  ✅ Mantener modelos en apps/core/
  ✅ Completar serializers, viewsets, services
  ✅ Completar tests
  ✅ Avanzar con FASE 2-3-4

DESPUÉS (FASE 10 - Refactoring):
  [ ] Crear apps/centers/, apps/calls/
  [ ] Mover modelos con migrations
  [ ] Actualizar imports
  [ ] Refactorizar tests
  [ ] apps/core/ → solo abstract models

Impacto:
  ✅ Continuar progreso sin detención
  ✅ Refactoring planificado y controlado
  ✅ Tests ya funcionando
  ❌ Arquitectura temporalmente imperfecta
  ❌ Deuda técnica temporal
```

**PROS:**
- Mantiene momentum del proyecto
- Refactoring planificado y controlado
- Tests y funcionalidad primero
- Menor riesgo inmediato

**CONTRAS:**
- Arquitectura temporalmente incorrecta
- Deuda técnica que hay que pagar después
- Posible duplicación de esfuerzo

---

### Opción C: Híbrido (Recomendado) ⭐

**MANTENER core/ temporalmente, pero documentar destino final:**

```yaml
AHORA (FASE 2-5):
  ✅ Mantener modelos en apps/core/ (temporal)
  ✅ Completar funcionalidad completa (API, tests)
  ✅ Documentar en cada modelo: # TODO: Mover a apps/X/
  ✅ Crear PLAN_REFACTORING_ARQUITECTURA.md
  
  # apps/core/models.py
  class Center(SoftDeleteMixin, models.Model):
      # TODO REFACTORING: Mover a apps/centers/models.py (FASE 10)
      """Centro de atención."""
      ...

DESPUÉS (FASE 10):
  [ ] Ejecutar refactoring planificado
  [ ] apps/centers/ (Center, Service)
  [ ] apps/calls/ (CallRecord)
  [ ] apps/access/ (UserServiceAccess - mover)
  [ ] apps/core/ (SOLO abstract)

Beneficios:
  ✅ Progreso inmediato
  ✅ Refactoring planificado
  ✅ Deuda técnica documentada
  ✅ Menos riesgo
  ✅ Testing completo antes de refactoring
```

**PROS:**
- Balance perfecto: progreso + planificación
- Refactoring con tests ya funcionando
- Deuda técnica visible y cuantificada
- Riesgo controlado

**CONTRAS:**
- Requiere disciplina (no olvidar refactoring)
- Código temporal debe estar bien documentado

---

## 📋 PLAN ACTUALIZADO - OPCIÓN C (RECOMENDADA)

### FASE 2 ACTUALIZADA: Core & Utils (Semana 3 - 7 días)

**Objetivo:** Completar apps/core/ con modelos actuales (temporales)

#### Día 11: ✅ COMPLETADO
```yaml
✅ Core Models mejorados:
    - Center, Service, CallRecord, UserServiceAccess
✅ Validators reutilizables (15)
✅ Constants centralizadas (100+)
✅ SoftDelete, indexes optimizados
✅ CLEAN_CODE v3.0.1 aplicado
```

#### Día 12: ✅ COMPLETADO
```yaml
✅ Services Layer (3 services):
    - CenterService (9 methods)
    - ServiceService (12 methods)
    - CallRecordService (11 methods)
✅ Service Layer Pattern
✅ Transacciones, cache, validaciones
```

#### Día 13-14: ⏳ EN PROGRESO
```yaml
⏳ Serializers + Filters + Permissions:
    - 20 serializers DRF
    - 4 filter classes
    - 6 custom permissions
    - ❌ ViewSets (pausado por análisis)

SIGUIENTE PASO:
  [ ] Completar viewsets.py (4 viewsets)
  [ ] URLs + routing
  [ ] Tests de API (40+ tests)
```

#### Día 15-17: PENDIENTE
```yaml
Pendiente:
  [ ] Django Admin (4 admins personalizados)
  [ ] URLs configuration
  [ ] API documentation (DRF browsable)
  [ ] Tests completos (60+ tests)
  [ ] Coverage >90%
```

---

### NUEVA FASE 10: REFACTORING ARQUITECTÓNICO (Semana 14)

**Objetivo:** Mover modelos a apps correctas

```yaml
Día 1-2: Crear apps + Migrations
  [ ] Crear apps/centers/ (Center, Service)
  [ ] Crear apps/calls/ (CallRecord)
  [ ] Generar migrations (SeparateDatabaseAndState)
  
Día 3-4: Mover código
  [ ] Mover modelos con db_table preservation
  [ ] Actualizar imports (100+ archivos)
  [ ] Actualizar tests
  
Día 5: Testing completo
  [ ] Ejecutar test suite completa
  [ ] Verificar migrations
  [ ] Verificar data integrity
  
Día 6-7: apps/core/ limpieza final
  [ ] Dejar SOLO abstract models
  [ ] Verificar arquitectura final
  [ ] Actualizar documentación
```

---

## 🎯 DECISIÓN RECOMENDADA

### ✅ IMPLEMENTAR OPCIÓN C (HÍBRIDO)

**Razones:**

1. **Pragmatismo:** Mantener momentum del proyecto
2. **Riesgo:** Refactoring con tests ya funcionando es más seguro
3. **TDD:** Primero funcionalidad, luego arquitectura
4. **Planificación:** Refactoring documentado y planificado
5. **Real-world:** Así funcionan proyectos reales (iterativo)

**Acciones Inmediatas:**

```yaml
HOY (Día 13-14):
  [ ] Aceptar estructura actual apps/core/
  [ ] Completar viewsets.py (4 viewsets)
  [ ] Completar filters, permissions, serializers
  [ ] Documentar TODO en cada modelo

MAÑANA (Día 15):
  [ ] Django Admin
  [ ] URLs
  [ ] Tests API

PRÓXIMA SEMANA:
  [ ] FASE 3-4-5 (Authentication, Access, Users)
  
SEMANA 14:
  [ ] FASE 10: Refactoring arquitectónico
```

---

## 📝 DOCUMENTACIÓN REQUERIDA

### 1. Actualizar en apps/core/models.py

```python
"""
Modelos core - IACT Call Center System.

🔴 TEMPORAL: Estos modelos están aquí temporalmente.

REFACTORING PLANIFICADO (FASE 10):
- Center, Service → apps/centers/models.py
- CallRecord → apps/calls/models.py  
- UserServiceAccess → apps/access/models.py

Luego apps/core/models.py tendrá SOLO:
- TimeStampedModel (abstract=True)
- SoftDeleteMixin (abstract=True)
- AuditedModel (abstract=True)
"""
```

### 2. Crear PLAN_REFACTORING_ARQUITECTURA.md

```markdown
# PLAN DE REFACTORING ARQUITECTÓNICO

## Modelos a Mover

### apps/core/ → apps/centers/
- Center
- Service

### apps/core/ → apps/calls/
- CallRecord

### apps/core/ → apps/access/
- UserServiceAccess (ya existe apps/access/)

## Estrategia
1. Crear apps con models
2. Migrations con db_table preservation
3. Actualizar imports
4. Tests regression
```

### 3. Agregar TODO en cada modelo

```python
class Center(SoftDeleteMixin, models.Model):
    # TODO REFACTORING FASE 10: Mover a apps/centers/models.py
    # Preservar db_table='core_centers'
    # Actualizar imports en ~15 archivos
    """Centro de atención."""
    ...
```

---

## ✅ ACCIÓN INMEDIATA

**¿Qué hacer AHORA?**

```yaml
OPCIÓN C - HÍBRIDO:
  1. Aceptar estructura actual
  2. Documentar TODOs en código
  3. Completar FASE 2 PARTE 3 (viewsets)
  4. Continuar con testing y funcionalidad
  5. Plan refactoring para FASE 10

VENTAJAS:
  ✅ Progreso inmediato
  ✅ Menor riesgo
  ✅ Testing primero
  ✅ Refactoring planificado

PRÓXIMOS PASOS:
  [ ] Completar viewsets.py
  [ ] Completar tests API
  [ ] FASE 3: Authentication
  [ ] FASE 4: Access (RBAC)
  ...
  [ ] FASE 10: Refactoring arquitectónico
```

---

## 📊 RESUMEN EJECUTIVO

```yaml
Problema:
  ✅ DETECTADO: Divergencia código real vs análisis

Análisis:
  ✅ 3 opciones evaluadas
  ✅ Opción C (Híbrido) recomendada

Decisión:
  ⏳ PENDIENTE: Usuario debe aprobar

Plan si Opción C:
  ✅ Continuar FASE 2 (viewsets)
  ✅ Documentar deuda técnica
  ✅ FASE 10: Refactoring arquitectónico
  ✅ TDD approach mantenido
  ✅ 14 semanas total (sin cambios)
```

---

**FIN DEL ANÁLISIS**

**Estado:** Esperando decisión del usuario  
**Opciones:** A (Refactorizar ahora) | B (Refactorizar después) | C (Híbrido) ⭐  
**Recomendación:** OPCIÓN C (mantener momentum, refactorizar en FASE 10)
