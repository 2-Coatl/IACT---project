# PLAN FASE 3 - apps/core & apps/utils

**Versión:** 1.1.0  
**Fecha:** 2026-01-21  
**Estado:** Planificación  
**Prioridad:** ALTA  
**Cambios v1.1.0:** Actualizado según análisis de dependencias v1.1.0  

---

## 📋 CAMBIOS EN v1.1.0

```yaml
v1.0.0 → v1.1.0:
  ✅ Actualizado: Referencias a ANALISIS_RELACIONES_Y_SRP_v1.1.0.md
  ✅ Mejorado: Contexto de dependencias apps/authentication → apps/access
  ✅ Agregado: Importancia de tests en RequiresFunctionPermission
  ✅ Mejorado: Explicación de por qué FASE 3 es crítica
```

---

## 📋 CONTEXTO

### Situación Actual

```yaml
FASE 1: ✅ Completada
  - Sistema básico funcional
  - 11 endpoints
  - Tests básicos

FASE 2: ✅ Completada
  - apps/users/ refactorizado
  - 94+ tests (~95% coverage)
  - Documentación completa
  - Producción ready

FASE 3: ⏳ Pendiente
  - apps/core/ necesita refactor + tests
  - apps/utils/ necesita tests + docs
  - Infraestructura sin coverage adecuado
```

### Problemas Identificados

Según [ANALISIS_RELACIONES_Y_SRP_v1.1.0.md](../architecture/ANALISIS_RELACIONES_Y_SRP_v1.1.0.md):

```yaml
🔴 CRÍTICO:
  1. apps/core/ tiene services de negocio
     - callrecord_service.py → Debería estar en apps/pipeline/
     - center_service.py → Debería estar en apps/pipeline/
     - etl_service.py → Debería estar en apps/pipeline/
     - service_service.py → Debería estar en apps/pipeline/
     Impacto: Viola SRP, confunde arquitectura
  
  2. apps/core/ y apps/utils/ sin tests
     - Coverage desconocido
     - Permissions sin tests (RequiresFunctionPermission es CRÍTICO)
     - Riesgo de regresiones
     Impacto: Base del sistema sin garantías de calidad
  
⚠️ ADVERTENCIA:
  3. Documentación insuficiente
     - No hay README.md en apps/core/
     - No hay README.md en apps/utils/
     - Flujo RBAC no documentado
     Impacto: Dificulta onboarding y mantenimiento
```

### Por Qué FASE 3 es Crítica

```yaml
apps/core/ es FUNDACIÓN:
  - Nivel 2 en mapa de dependencias
  - TODOS los otros apps dependen de core
  - RequiresFunctionPermission usado por 6+ apps
  - Abstract models usados por 10+ apps
  
Si apps/core/ falla:
  ❌ TODO el sistema falla
  ❌ RBAC permissions no funcionan
  ❌ SoftDelete no funciona
  ❌ Timestamps incorrectos
  
apps/utils/ es FUNDACIÓN PURA:
  - Nivel 1 en mapa de dependencias
  - NO depende de nadie
  - TODOS dependen de utils
  
Si apps/utils/ falla:
  ❌ Validators no funcionan
  ❌ Phone/email validation rota
  ❌ Formatters incorrectos
  ❌ 11 apps afectados
```

---

## 🎯 OBJETIVOS FASE 3

### Objetivo General

Refactorizar, testear y documentar la infraestructura base (apps/core y apps/utils) para garantizar estabilidad del sistema.

### Objetivos Específicos

```yaml
1. Refactorizar apps/core/:
   ✅ Mover services de negocio a apps/pipeline/
   ✅ Limpiar responsabilidades (SRP)
   ✅ Mejorar arquitectura
   ✅ Actualizar imports en todo el proyecto

2. Crear tests completos apps/core/:
   ✅ Unit tests para permissions (CRÍTICO - RequiresFunctionPermission)
   ✅ Unit tests para abstract models (TimeStampedModel, SoftDeleteMixin)
   ✅ Unit tests para middleware (healthcheck, logging, security)
   ✅ Unit tests para mixins (AuditMixin, etc)
   ✅ Coverage objetivo: 90%+

3. Crear tests completos apps/utils/:
   ✅ Unit tests para validators (validate_phone_number, etc)
   ✅ Unit tests para helpers (get_client_ip, etc)
   ✅ Unit tests para formatters
   ✅ Unit tests para date/string/number utils
   ✅ Coverage objetivo: 95%+

4. Documentar apps/core/:
   ✅ README.md completo
   ✅ INTEGRATION_GUIDE_CORE.md
   ✅ Flujo RBAC (authentication → access vía RequiresFunctionPermission)
   ✅ Ejemplos de uso

5. Documentar apps/utils/:
   ✅ README.md completo
   ✅ Guía de funciones
   ✅ Ejemplos de uso
```

---

## 📅 PLANIFICACIÓN

### PARTE 1: Refactor apps/core/ (3h)

**Objetivo:** Limpiar apps/core/ moviendo lógica de negocio a apps apropiadas.

#### Tareas

```yaml
1.1. Análisis de services en apps/core/:
   - Revisar callrecord_service.py
   - Revisar center_service.py
   - Revisar etl_service.py
   - Revisar service_service.py
   - Identificar dependencias
   Tiempo: 30 min

1.2. Crear apps/pipeline/services/ si no existe:
   - Crear directorio services/
   - Crear __init__.py
   - Preparar estructura
   Tiempo: 15 min

1.3. Mover services a apps/pipeline/services/:
   - Mover callrecord_service.py
   - Mover center_service.py
   - Mover etl_service.py
   - Mover service_service.py
   - Mantener base_service.py en apps/core/
   Tiempo: 30 min

1.4. Actualizar imports en todo el proyecto:
   - Buscar "from apps.core.services import"
   - Actualizar a "from apps.pipeline.services import"
   - Verificar apps/pipeline/viewsets.py
   - Verificar apps/reports/ (si usa estos services)
   Tiempo: 45 min

1.5. Limpiar apps/core/:
   - Eliminar archivos movidos
   - Actualizar __init__.py
   - Verificar estructura limpia
   - Solo debe quedar base_service.py
   Tiempo: 15 min

1.6. Testing de regresión:
   - Correr tests existentes
   - Verificar no hay imports rotos
   - Verificar funcionalidad
   Tiempo: 45 min

Total PARTE 1: 3h
```

#### Entregables

```yaml
✅ apps/core/services/:
   - Solo base_service.py
   - Limpio de lógica de negocio

✅ apps/pipeline/services/:
   - callrecord_service.py
   - center_service.py
   - etl_service.py
   - service_service.py

✅ Todo el proyecto:
   - Imports actualizados
   - Tests pasando
   - Sin regresiones
```

---

### PARTE 2: Tests apps/core/ (4h)

**Objetivo:** Crear suite completa de tests para apps/core/ con 90%+ coverage.

#### 2.1. Tests Permissions (1.5h)

```yaml
test_permissions.py:

TestRequiresFunctionPermission (8 tests) - CRÍTICO:
  ✅ Con permission → 200
  ✅ Sin permission → 403
  ✅ Sin autenticación → 401
  ✅ Superuser bypass
  ✅ Sin function_map → 403
  ✅ Action no en function_map → 403
  ✅ has_function() llamado correctamente
  ✅ Integration con ViewSet

  IMPORTANTE: Este permission es usado por:
    - apps/authentication (change_password, set_security_answers)
    - apps/users (CRUD operations)
    - apps/pipeline (si usa RBAC)
    - apps/reports (si usa RBAC)
  
  Si falla, TODO el RBAC falla

TestIsOwnerOrReadOnly (4 tests):
  ✅ Owner puede editar
  ✅ No owner solo lectura
  ✅ Sin created_by → 403
  ✅ SAFE_METHODS permitidos

TestIsSuperUserOrReadOnly (3 tests):
  ✅ Superuser puede editar
  ✅ Usuario normal solo lectura
  ✅ SAFE_METHODS permitidos

TestIsStaffOrReadOnly (3 tests):
  ✅ Staff puede editar
  ✅ Usuario normal solo lectura
  ✅ Superuser puede editar

TestHasServiceAccess (5 tests):
  ✅ Con acceso al servicio
  ✅ Sin acceso al servicio
  ✅ Superuser bypass
  ✅ _get_service_from_object()
  ✅ Service no existe → 403

TestAllowOptionsAuthentication (2 tests):
  ✅ OPTIONS permitido sin auth
  ✅ Otros métodos requieren auth

Total: 25 tests
Coverage objetivo: 95%+
```

#### 2.2. Tests Abstract Models (1h)

```yaml
test_models.py:

TestTimeStampedModel (5 tests):
  ✅ created_at auto-seteado
  ✅ updated_at auto-actualizado
  ✅ Timestamps son DateTimeField
  ✅ created_at inmutable
  ✅ updated_at mutable
  
  IMPORTANTE: Usado por 10+ models

TestSoftDeleteMixin (8 tests):
  ✅ delete() marca is_deleted=True
  ✅ delete() setea deleted_at
  ✅ hard_delete() elimina de DB
  ✅ restore() recupera eliminado
  ✅ is_deleted default=False
  ✅ deleted_at default=None
  ✅ SoftDeleteManager.all() solo activos
  ✅ SoftDeleteManager.deleted() solo eliminados
  
  IMPORTANTE: Usado por User, Function, etc

TestSoftDeleteQuerySet (5 tests):
  ✅ active() solo no eliminados
  ✅ deleted() solo eliminados
  ✅ with_deleted() todos
  ✅ Filtros combinables
  ✅ Performance optimizado

Total: 18 tests
Coverage objetivo: 95%+
```

#### 2.3. Tests Middleware (1h)

```yaml
test_middleware.py:

TestHealthCheckMiddleware (3 tests):
  ✅ GET /health/ → 200
  ✅ Response correcto
  ✅ No afecta otros endpoints

TestLoggingMiddleware (4 tests):
  ✅ Log request
  ✅ Log response
  ✅ Log tiempo de ejecución
  ✅ Log errores

TestSecurityMiddleware (4 tests):
  ✅ Headers de seguridad
  ✅ XSS protection
  ✅ CSRF protection
  ✅ Clickjacking protection

TestTimezoneMiddleware (3 tests):
  ✅ Timezone activado
  ✅ Timezone correcto (America/Mexico_City)
  ✅ No afecta otros

Total: 14 tests
Coverage objetivo: 90%+
```

#### 2.4. Tests Mixins (30 min)

```yaml
test_mixins.py:

TestAuditMixin (según funcionalidad):
  ✅ Audit trail creado
  ✅ User registrado
  ✅ Action registrada
  ✅ Timestamp correcto

TestOtrosMixins (según contenido):
  ✅ Tests apropiados

Total: ~10 tests
Coverage objetivo: 90%+
```

#### Entregables PARTE 2

```yaml
✅ tests/unit/core/:
   - test_permissions.py (25 tests) ← CRÍTICO
   - test_models.py (18 tests)
   - test_middleware.py (14 tests)
   - test_mixins.py (~10 tests)

Total: ~67 tests
Coverage: 90%+

NOTA: RequiresFunctionPermission es CRÍTICO
  - Prueba flujo: ViewSet → Permission → has_function → UserFunctionAssignment
  - Valida integración apps/authentication → apps/access
```

---

### PARTE 3: Tests apps/utils/ (3h)

**Objetivo:** Crear suite completa de tests para apps/utils/ con 95%+ coverage.

#### 3.1. Tests Validators (1h)

```yaml
test_validators.py:

TestPhoneValidator (8 tests):
  ✅ Formato válido México
  ✅ Formato inválido → ValidationError
  ✅ Con espacios válido
  ✅ Sin espacios válido
  ✅ Con guiones válido
  ✅ Muy corto → Error
  ✅ Muy largo → Error
  ✅ Caracteres inválidos → Error
  
  IMPORTANTE: Usado en User.phone (apps/users)

TestEmailValidator (6 tests):
  ✅ Email válido
  ✅ Email inválido → Error
  ✅ Multiple @ → Error
  ✅ Sin dominio → Error
  ✅ Caracteres especiales
  ✅ Case insensitive

TestOtrosValidators (según contenido):
  ✅ Tests apropiados
  ✅ Edge cases
  ✅ Error handling

Total: ~25 tests
```

#### 3.2. Tests Helpers (45 min)

```yaml
test_helpers.py:

TestGetClientIP (6 tests):
  ✅ IP desde HTTP_X_FORWARDED_FOR
  ✅ IP desde REMOTE_ADDR
  ✅ IP desde HTTP_X_REAL_IP
  ✅ Sin IP → None
  ✅ Multiple IPs → Primera
  ✅ IPv6 support
  
  IMPORTANTE: Usado en apps/users/signals.py

TestOtrosHelpers (según contenido):
  ✅ Tests apropiados
  ✅ Coverage completo

Total: ~20 tests
```

#### 3.3. Tests Formatters (45 min)

```yaml
test_formatters.py:

TestPhoneFormatter (5 tests):
  ✅ Format México
  ✅ Parse México
  ✅ Format internacional
  ✅ Invalid → None
  ✅ Empty → None

TestCurrencyFormatter (5 tests):
  ✅ Format MXN
  ✅ Format USD
  ✅ Decimales correctos
  ✅ Símbolos correctos
  ✅ Negative numbers

TestOtrosFormatters:
  ✅ Tests apropiados

Total: ~15 tests
```

#### 3.4. Tests Utils (30 min)

```yaml
test_date_utils.py:
  ✅ Parse dates
  ✅ Format dates
  ✅ Date ranges
  ✅ Timezone handling
  Total: ~8 tests

test_string_utils.py:
  ✅ Slugify
  ✅ Sanitize
  ✅ Truncate
  ✅ Clean
  Total: ~8 tests

test_number_utils.py:
  ✅ Parse numbers
  ✅ Format numbers
  ✅ Round
  ✅ Validate
  Total: ~6 tests
```

#### Entregables PARTE 3

```yaml
✅ tests/unit/utils/:
   - test_validators.py (25 tests)
   - test_helpers.py (20 tests)
   - test_formatters.py (15 tests)
   - test_date_utils.py (8 tests)
   - test_string_utils.py (8 tests)
   - test_number_utils.py (6 tests)

Total: ~82 tests
Coverage: 95%+
```

---

### PARTE 4: Documentación (2h)

**Objetivo:** Documentar apps/core/ y apps/utils/ completamente.

#### 4.1. README.md apps/core/ (45 min)

```yaml
Secciones:
  ✅ Descripción general
  ✅ Responsabilidades (SOLO infraestructura)
  ✅ Abstract Models
     - TimeStampedModel (usado por 10+ models)
     - SoftDeleteMixin (usado por User, Function)
  ✅ Permissions DRF (7 permissions)
     - RequiresFunctionPermission (CRÍTICO - flujo RBAC)
     - IsOwnerOrReadOnly
     - Etc.
  ✅ Middleware (4 middlewares)
  ✅ Mixins
  ✅ Ejemplos de uso
  ✅ Testing
  ✅ Troubleshooting
  ✅ Flujo RBAC (authentication → access)

Líneas: ~500
```

#### 4.2. README.md apps/utils/ (30 min)

```yaml
Secciones:
  ✅ Descripción general
  ✅ Principio: Funciones puras, sin DB
  ✅ Validators
     - validate_phone_number (usado en User)
     - validate_email
  ✅ Formatters
  ✅ Helpers
     - get_client_ip (usado en signals)
  ✅ Date/String/Number Utils
  ✅ Decorators
  ✅ Ejemplos de uso
  ✅ Testing
  ✅ API Reference

Líneas: ~350
```

#### 4.3. INTEGRATION_GUIDE_CORE.md (45 min)

```yaml
Secciones:
  ✅ Cómo usar abstract models
  ✅ Cómo usar permissions
     - RequiresFunctionPermission en ViewSets
     - function_map pattern
     - Flujo completo RBAC
  ✅ Cómo usar middleware
  ✅ Cómo usar mixins
  ✅ Integración con otras apps
     - apps/authentication usa RequiresFunctionPermission
     - apps/users usa SoftDeleteMixin
  ✅ Flujo detallado RBAC:
     ViewSet → Permission → User.has_function() → UserFunctionAssignment
  ✅ Ejemplos completos
  ✅ Best practices
  ✅ Diagrama de dependencias

Líneas: ~600
```

#### Entregables PARTE 4

```yaml
✅ callcentersite/apps/core/README.md (500 líneas)
✅ callcentersite/apps/utils/README.md (350 líneas)
✅ docs/INTEGRATION_GUIDE_CORE.md (600 líneas)

Total: 3 documentos (~1,450 líneas)
```

---

## 📊 RESUMEN FASE 3

### Tiempo Total Estimado

```yaml
PARTE 1: Refactor apps/core/ - 3h
PARTE 2: Tests apps/core/ - 4h
PARTE 3: Tests apps/utils/ - 3h
PARTE 4: Documentación - 2h

Total: 12h
```

### Entregables Totales

```yaml
Código:
  ✅ apps/core/ refactorizado (SRP mejorado)
  ✅ apps/pipeline/services/ con 4 services movidos
  ✅ Imports actualizados en proyecto

Tests:
  ✅ ~67 tests apps/core/ (90%+ coverage)
     - 25 tests permissions (CRÍTICO)
     - 18 tests abstract models
     - 14 tests middleware
     - 10 tests mixins
  ✅ ~82 tests apps/utils/ (95%+ coverage)
  ✅ Total: ~149 tests

Documentación:
  ✅ README.md apps/core/ (500 líneas)
  ✅ README.md apps/utils/ (350 líneas)
  ✅ INTEGRATION_GUIDE_CORE.md (600 líneas)
  ✅ Total: ~1,450 líneas
```

### Beneficios

```yaml
✅ Infraestructura estable:
   - Tests completos de fundación
   - Coverage 90-95%
   - Confianza en RBAC permissions
   - Confianza en abstract models

✅ SRP mejorado:
   - apps/core/ solo infraestructura
   - Lógica de negocio en apps apropiadas
   - Arquitectura limpia

✅ Mantenibilidad:
   - Documentación completa
   - Flujo RBAC documentado
   - Tests como documentación viva
   - Fácil onboarding

✅ Calidad:
   - Regresiones prevenidas
   - Bugs detectados temprano
   - Código confiable
   - RBAC garantizado
```

---

## 🎯 CRITERIOS DE ACEPTACIÓN

### PARTE 1: Refactor

```yaml
✅ apps/core/services/ solo tiene base_service.py
✅ apps/pipeline/services/ tiene 4 services movidos
✅ Todos los imports actualizados
✅ Tests existentes pasando
✅ Sin regresiones
✅ SRP cumplido
```

### PARTE 2: Tests apps/core/

```yaml
✅ Mínimo 67 tests creados
✅ Coverage ≥ 90%
✅ RequiresFunctionPermission 100% testeado (CRÍTICO)
✅ Abstract models 100% testeados
✅ Middleware 90%+ testeado
✅ Todos los tests pasan
✅ Tests bien documentados
```

### PARTE 3: Tests apps/utils/

```yaml
✅ Mínimo 82 tests creados
✅ Coverage ≥ 95%
✅ Todos los tests pasan
✅ validate_phone_number testeado (usado en User)
✅ get_client_ip testeado (usado en signals)
✅ Edge cases cubiertos
```

### PARTE 4: Documentación

```yaml
✅ README.md apps/core/ completo
✅ README.md apps/utils/ completo
✅ INTEGRATION_GUIDE_CORE.md completo
✅ Flujo RBAC documentado
✅ Ejemplos funcionales
✅ Sin TODOs pendientes
```

---

## 🚀 EJECUCIÓN

### Pre-requisitos

```yaml
✅ FASE 2 completada
✅ Entorno de desarrollo configurado
✅ Tests existentes pasando
✅ Branch limpio
✅ ANALISIS_RELACIONES_Y_SRP_v1.1.0.md leído
```

### Orden de Ejecución

```
1. Crear branch: feature/core-utils-refactor
2. PARTE 1: Refactor (3h)
   ├─ Mover services
   ├─ Actualizar imports
   └─ Commit: "Refactor: Mover services de core a pipeline"
3. PARTE 2: Tests core (4h)
   ├─ test_permissions.py (CRÍTICO)
   ├─ test_models.py
   ├─ test_middleware.py
   ├─ test_mixins.py
   └─ Commit: "Tests: apps/core/ con 90%+ coverage"
4. PARTE 3: Tests utils (3h)
   ├─ test_validators.py
   ├─ test_helpers.py
   ├─ Otros tests
   └─ Commit: "Tests: apps/utils/ con 95%+ coverage"
5. PARTE 4: Docs (2h)
   ├─ READMEs
   ├─ Integration guide
   └─ Commit: "Docs: apps/core/ y apps/utils/ completos"
6. Review final
7. Merge a develop
```

---

## 📈 MÉTRICAS DE ÉXITO

```yaml
Código:
  ✅ 0 services de negocio en apps/core/
  ✅ SRP score apps/core/: 9/10+
  ✅ 0 imports rotos
  ✅ Arquitectura limpia

Tests:
  ✅ 149+ tests creados
  ✅ Coverage apps/core/: ≥90%
  ✅ Coverage apps/utils/: ≥95%
  ✅ 0 tests fallando
  ✅ RequiresFunctionPermission 100% testeado

Documentación:
  ✅ 3 documentos creados
  ✅ ~1,450 líneas de docs
  ✅ Flujo RBAC documentado
  ✅ Ejemplos funcionales

Tiempo:
  ✅ Completado en ≤15h
  ✅ Sin blockers críticos
```

---

## 🔄 PRÓXIMOS PASOS POST-FASE 3

```yaml
FASE 4 (Opcional):
  - Refactor apps/access/
  - Evaluar separar UserServiceAccess
  - Tests apps/access/

FASE 5 (Opcional):
  - Refactor apps/pipeline/
  - Tests apps/pipeline/
  - Documentación completa

FASE 6 (Opcional):
  - Refactor apps/reports/
  - Tests apps/reports/
  - Documentación completa
```

---

## 📚 REFERENCIAS

- [ANALISIS_RELACIONES_Y_SRP_v1.1.0.md](../architecture/ANALISIS_RELACIONES_Y_SRP_v1.1.0.md)
- [PLAN_FASE_2_v2.2.0.md](PLAN_FASE_2_v2.2.0.md)
- [FASE_2_PARTE_7_COMPLETADA.md](../compliance/FASE_2_PARTE_7_COMPLETADA.md)

---

**Estado:** ✅ LISTO PARA EJECUCIÓN  
**Versión:** 1.1.0  
**Prioridad:** ALTA  
**Complejidad:** Media  
**ROI:** Alto  
**Riesgo:** Bajo (con buen testing)  

**Aprobado para:** Inicio inmediato  
**Asignado a:** IACT Development Team  
**Fecha inicio:** 2026-01-21
