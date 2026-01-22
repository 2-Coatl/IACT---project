# FASE A - RESUMEN DE PROGRESO

**Fecha:** 2026-01-21  
**DT-002:** Eliminación UserServiceAccess  
**Progreso:** 70% (4/6 pasos)  

---

## ✅ COMPLETADO

### A.1: Análisis de Impacto (30 min) ✅

```yaml
Resultado:
  - 9 archivos afectados identificados
  - 1 ViewSet principal (CallRecordViewSet)
  - 5 functions MOD_Calls necesarias
  - Data migración planificada

Documento:
  docs/ejecucion/FASE_A_ANALISIS_IMPACTO.md
```

### A.2: Crear Functions MOD_Calls (30 min) ✅

```yaml
Functions creadas:
  - CALL_VIEW: Ver llamadas
  - CALL_EDIT: Editar llamadas
  - CALL_DELETE: Eliminar llamadas
  - CALL_EXP_CSV: Exportar CSV
  - CALL_STATS: Estadísticas

Script:
  apps/access/management/commands/create_mod_calls_functions.py
  
Comando:
  python manage.py create_mod_calls_functions
```

### A.3: Actualizar ViewSets (1h) ✅

```yaml
CallRecordViewSet:
  ANTES:
    permission_classes = [
        IsAuthenticated,
        IsActiveUser,
        HasServiceAccess,  ❌
    ]
  
  DESPUÉS:
    permission_classes = [
        IsAuthenticated,
        IsActiveUser,
        RequiresFunctionPermission,  ✅
    ]
    
    function_map = {
        'list': 'CALL_VIEW',
        'retrieve': 'CALL_VIEW',
        'create': 'CALL_EDIT',
        'update': 'CALL_EDIT',
        'partial_update': 'CALL_EDIT',
        'destroy': 'CALL_DELETE',
        'bulk_create': 'CALL_EDIT',
        'stats': 'CALL_STATS',
        'daily_stats': 'CALL_STATS',
        'top_callers': 'CALL_STATS',
    }

Imports actualizados:
  ✅ RequiresFunctionPermission agregado
  ❌ HasServiceAccess removido
  ❌ UserServiceAccess removido
  ❌ UserServiceAccessSerializer removido
  ❌ UserServiceAccessFilter removido
```

### A.4: Eliminar Código (30 min) ✅

```yaml
Eliminado (~860 líneas):

1. apps/access/models.py:
   ❌ class UserServiceAccess (127 líneas)

2. apps/access/serializers.py:
   ❌ UserServiceAccessSerializer
   ❌ UserServiceAccessListSerializer
   ❌ GrantAccessSerializer
   ❌ BulkGrantAccessSerializer
   ❌ RevokeAccessSerializer
   (175 líneas)

3. apps/access/filters.py:
   ❌ UserServiceAccessFilter
   (87 líneas)

4. apps/core/permissions.py:
   ❌ class HasServiceAccess
   (110 líneas)

5. apps/pipeline/permissions.py:
   ❌ class HasServiceAccess
   ❌ class CanGrantAccess
   ❌ class CanRevokeAccess
   (70 líneas)

6. apps/core/mixins.py:
   ❌ class ServiceFilterMixin
   (72 líneas)

7. apps/core/services.py:
   ❌ class ServiceAccessService
   (218 líneas)

Total: 7 archivos, ~860 líneas eliminadas
```

---

## ⏳ PENDIENTE

### A.5: Migración DB (30 min) ⏳

```yaml
Tarea:
  - Crear migración para eliminar tabla
  - Tabla: core_user_service_access
  - Aplicar migración
  - Verificar tablas eliminadas

Comando:
  python manage.py makemigrations access -n "remove_user_service_access"
  python manage.py migrate access

Precaución:
  - Verificar si hay data en producción
  - Backup si necesario
  - Migrar usuarios a Groups si aplicable
```

### A.6: Testing y Verificación (1h) ⏳

```yaml
Tests a eliminar:
  - tests/unit/core/test_permissions.py:
      TestHasServiceAccess (5 tests)

Tests a ejecutar:
  - pytest tests/unit/access/ -v
  - pytest tests/unit/core/test_permissions.py -v
  - pytest tests/unit/pipeline/ -v

Verificación manual:
  1. Ejecutar script create_mod_calls_functions.py
  2. Asignar CALL_VIEW a usuario de prueba
  3. GET /api/call-records/ → 200 OK
  4. GET /api/call-records/1/ → 200 OK
  5. POST /api/call-records/ → 403 (sin CALL_EDIT)

Criterios:
  ✅ Migraciones aplicadas sin errores
  ✅ Tests unitarios pasando
  ✅ CallRecordViewSet funciona con RBAC
  ✅ No referencias a UserServiceAccess
  ✅ No imports rotos
```

---

## 📊 ESTADÍSTICAS ACTUALES

```yaml
Tiempo invertido: 2h 30min
  A.1: 30 min
  A.2: 30 min
  A.3: 1h
  A.4: 30 min

Tiempo estimado restante: 1h 30min
  A.5: 30 min
  A.6: 1h

Total estimado: 4h
Real: ~4h (en target)

Progreso: 70% (4/6)
```

---

## 🔗 ARCHIVOS MODIFICADOS

```yaml
Modificados:
  ✅ apps/access/models.py
  ✅ apps/access/serializers.py
  ✅ apps/access/filters.py
  ✅ apps/core/permissions.py
  ✅ apps/core/mixins.py
  ✅ apps/core/services.py
  ✅ apps/pipeline/permissions.py
  ✅ apps/pipeline/viewsets.py

Creados:
  ✅ apps/access/management/commands/create_mod_calls_functions.py
  ✅ docs/ejecucion/FASE_A_ANALISIS_IMPACTO.md

Pendiente modificar:
  ⏳ apps/access/migrations/000X_remove_user_service_access.py (crear)
  ⏳ tests/unit/core/test_permissions.py (eliminar tests)
```

---

## 📋 COMMITS REALIZADOS

```yaml
1. 98a0cb0: FASE A DT-002: A.1-A.3 Análisis + ViewSets actualizados
   - Análisis de impacto
   - Script functions MOD_Calls
   - ViewSets con RequiresFunctionPermission

2. 8f20b9b: FASE A DT-002: A.4 Código eliminado (80%)
   - Models, serializers, filters eliminados
   - Permissions eliminadas
   - Mixins eliminados

3. 15513bf: FASE A DT-002: A.4 Código eliminado (100%)
   - ServiceAccessService eliminado
   - ~860 líneas eliminadas total
```

---

## ✅ CRITERIOS DE COMPLETITUD FASE A

```yaml
A.1: ✅ Análisis de impacto completado
A.2: ✅ Functions MOD_Calls creadas
A.3: ✅ ViewSets actualizados a RBAC
A.4: ✅ Código UserServiceAccess eliminado
A.5: ⏳ Migración DB pendiente
A.6: ⏳ Testing pendiente

Cuando A.5 y A.6 completen:
  ✅ UserServiceAccess eliminado
  ✅ HasServiceAccess eliminado
  ✅ RBAC puro implementado
  ✅ SRP apps/access/ mejorado a 9/10
  ✅ Tests pasando
  ✅ No código roto
```

---

## 🚀 PRÓXIMOS PASOS

1. **A.5: Migración DB** (30 min)
   ```bash
   # Crear functions
   python manage.py create_mod_calls_functions
   
   # Migrar data si necesario
   # (verificar count UserServiceAccess primero)
   
   # Crear migración
   python manage.py makemigrations access -n "remove_user_service_access"
   
   # Aplicar
   python manage.py migrate access
   ```

2. **A.6: Testing** (1h)
   ```bash
   # Eliminar tests obsoletos
   # tests/unit/core/test_permissions.py (TestHasServiceAccess)
   
   # Ejecutar tests
   pytest tests/unit/access/ -v
   pytest tests/unit/core/ -v
   pytest tests/unit/pipeline/ -v
   
   # Verificación manual
   # (con usuario de prueba + CALL_VIEW)
   ```

3. **Finalización FASE A**
   - Commit final
   - Documentar en DEUDA_TECNICA.md
   - Marcar DT-002 como RESUELTO

---

**Estado:** En progreso  
**Bloqueado:** No  
**Siguiente:** A.5 Migración DB  
**Aprobación:** Pendiente  
**Última actualización:** 2026-01-21
