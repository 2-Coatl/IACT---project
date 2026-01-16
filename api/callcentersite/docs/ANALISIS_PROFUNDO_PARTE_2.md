# ANÁLISIS PROFUNDO DEL PROYECTO - PARTE 2 DE 5
## ANÁLISIS DETALLADO POR APP

**Proyecto:** IACT Call Center System  
**Fecha Análisis:** 16 de enero de 2026  

---

## 2.1 APP: ACCESS (Sistema RBAC)

### Estado: ⚠️ PARCIALMENTE IMPLEMENTADO

### Modelos (4):
✅ `Function` - Funciones atómicas RBAC (422 líneas)
✅ `UserFunctionAssignment` - Asignación user-function
✅ `Module` - Módulos jerárquicos del sistema
✅ `UserModuleAccess` - Acceso user-module

### APIs:
⚠️ `ModuleViewSet` - CRUD módulos (parcial)
⚠️ `UserModuleAccessViewSet` - Gestión accesos (parcial)

### Migraciones:
❌ 0 migraciones - CRÍTICO

### Tests:
✅ 2 archivos en tests/unit/access/

### Faltante:
❌ API para asignar funciones a usuarios
❌ API para revocar funciones
❌ API para listar funciones disponibles
❌ Integración completa con MenuBuilder
❌ Command para poblar funciones iniciales

---

## 2.2 APP: AUDIT (Auditoría)

### Estado: ✅ IMPLEMENTADO

### Modelos (1):
✅ `AuditLog` - Registro de auditoría

### APIs:
✅ `AuditLogViewSet` - ReadOnly viewset
✅ Decorator `@audit_log` para auditar acciones

### Migraciones:
❌ 0 migraciones - CRÍTICO

### Tests:
✅ 2 archivos en tests/unit/audit/

### Faltante:
⚠️ Integración con todas las vistas críticas
⚠️ Dashboard de auditoría

---

## 2.3 APP: AUTHENTICATION

### Estado: ✅ IMPLEMENTADO

### Modelos (2):
✅ `SecurityQuestion` - Preguntas de seguridad
✅ `UserSecurityAnswer` - Respuestas de usuarios

### APIs:
✅ Login/Logout/Refresh JWT
✅ Gestión de sesiones

### Migraciones:
❌ 0 migraciones - CRÍTICO

### Tests:
✅ 3 archivos en tests/unit/authentication/

### Faltante:
❌ Reset de contraseña
❌ Cambio de contraseña
❌ 2FA (opcional)
❌ Recuperación por preguntas de seguridad

---

## 2.4 APP: CORE

### Estado: ⚠️ PARCIALMENTE IMPLEMENTADO

### Modelos (4):
✅ `CallRecord` - Registros de llamadas (316 líneas totales en models.py)
✅ `Center` - Centros de atención
✅ `Service` - Servicios 800
✅ `UserServiceAccess` - Acceso user-service

### APIs:
✅ `CallRecordViewSet` - ReadOnly
✅ `CenterViewSet` - ReadOnly
✅ `ServiceViewSet` - ReadOnly
✅ `user_menu_view` - Menú navegación RBAC ✅ NUEVO

### Navigation:
✅ `MenuBuilder` - Constructor de menús (17K, 450 líneas) ✅ NUEVO
✅ `MenuValidator` - Validación IDs numéricos ✅ NUEVO
✅ `MenuSerializer` - Serialización ✅ NUEVO

### Migraciones:
❌ 0 migraciones - CRÍTICO

### Tests:
✅ 2 archivos en tests/unit/core/ (navegación) ✅ NUEVO
⚠️ Faltan tests para CallRecord, Center, Service

### Faltante:
❌ CRUD completo para Centers
❌ CRUD completo para Services
❌ APIs de escritura para CallRecords
❌ Metadata navegación para core

---

## 2.5 APP: USERS

### Estado: ✅ IMPLEMENTADO (EXTENDIDO)

### Modelos (1):
✅ `CustomUser` - Usuario extendido con:
  - ✅ avatar (ImageField) ✅ NUEVO
  - ✅ phone (CharField) ✅ NUEVO
  - ✅ position (CharField) ✅ NUEVO
  - ✅ employee_id (CharField, unique) ✅ NUEVO
  - ✅ get_avatar_url() ✅ NUEVO
  - ✅ delete_avatar() ✅ NUEVO
  - ✅ get_functions() ✅ NUEVO
  - ✅ has_function() ✅ NUEVO
  - ✅ has_any_function() ✅ NUEVO
  - ✅ has_all_functions() ✅ NUEVO

### APIs:
✅ `UserViewSet` - CRUD básico
✅ `upload_avatar_view` - Upload avatar ✅ NUEVO
✅ `delete_avatar_view` - Delete avatar ✅ NUEVO
✅ `get_user_profile_view` - Get profile ✅ NUEVO
✅ `update_user_profile_view` - Update profile ✅ NUEVO

### Migraciones:
❌ 0 migraciones - CRÍTICO
❌ Campos nuevos (avatar, phone, etc.) NO están en BD

### Tests:
✅ 5 archivos en tests/unit/users/ (1,792 líneas, 113 tests) ✅ NUEVO

### Faltante:
❌ API para cambiar contraseña
❌ API para reset contraseña
❌ API para gestionar funciones del usuario
❌ Metadata navegación para users ✅ (EXISTE)

---

## 2.6 APP: REPORTS

### Estado: ❌ NO IMPLEMENTADO

### Modelos:
❌ 0 modelos - Necesita implementación completa

### APIs:
❌ 0 APIs funcionales

### Migraciones:
❌ 0 migraciones

### Tests:
❌ 0 tests

### Faltante TODO:
❌ Modelo Report
❌ Modelo ReportSchedule
❌ Modelo Dashboard
❌ APIs para generar reportes
❌ APIs para exportar (CSV, Excel, PDF)
❌ APIs para dashboards
❌ Metadata navegación ✅ (EXISTE)

---

## 2.7 APP: IVR_LEGACY

### Estado: ✅ LEGACY (READ-ONLY)

### Modelos (1):
✅ Modelo legacy para MariaDB

### APIs:
❌ 0 APIs (solo lectura en pipelines)

### Observaciones:
⚠️ Base de datos externa READ-ONLY
⚠️ No requiere migraciones
⚠️ Solo consultas, no escrituras

---

## 2.8 APP: PIPELINE

### Estado: ⚠️ PARCIALMENTE IMPLEMENTADO

### Modelos (1):
✅ Pipeline model

### APIs:
⚠️ 1 API básica

### Migraciones:
❌ 0 migraciones

### Tests:
✅ 3 archivos en tests/unit/pipeline/

### Faltante:
⚠️ Pipeline completo de ETL
⚠️ Scheduling de pipelines
⚠️ Logs de ejecución

---

## 2.9 APP: UTILS

### Estado: ✅ IMPLEMENTADO

### Modelos (3):
✅ `SoftDeleteMixin` - Mixin para soft delete
✅ `TimeStampedModel` - Mixin timestamps
✅ Otros mixins

### APIs:
✅ Utilidades compartidas

### Observaciones:
✅ Base compartida para otras apps
✅ No requiere migraciones propias

---

## RESUMEN PARTE 2

### MODELOS TOTALES: ~14 modelos implementados

| App | Modelos | Estado |
|-----|---------|--------|
| access | 4 | ⚠️ Sin migraciones |
| audit | 1 | ⚠️ Sin migraciones |
| authentication | 2 | ⚠️ Sin migraciones |
| core | 4 | ⚠️ Sin migraciones |
| users | 1 | ⚠️ Sin migraciones (extendido) |
| ivr_legacy | 1 | ✅ Legacy (no aplica) |
| pipeline | 1 | ⚠️ Sin migraciones |
| reports | 0 | ❌ No implementado |
| utils | 3 | ✅ Mixins |

### CRÍTICO:
❌ **0 MIGRACIONES EN TODAS LAS APPS**
❌ Los modelos existen pero NO están en la BD
❌ El sistema NO puede funcionar sin migraciones

### APIs IMPLEMENTADAS: ~18 endpoints

✅ Navigation: 1 endpoint (nuevo)
✅ Users: 5 endpoints (4 nuevos)
✅ Authentication: 3 endpoints
✅ Access: 2 endpoints (parciales)
✅ Core: 3 endpoints (ReadOnly)
✅ Audit: 1 endpoint
✅ Pipeline: 1 endpoint

### APIs FALTANTES: ~40+ endpoints

---

## PRÓXIMA PARTE

**PARTE 3:** Gap Analysis - Qué falta específicamente

**PARTE 4:** Dependencias y priorización

**PARTE 5:** Plan de acción dividido en sprints
