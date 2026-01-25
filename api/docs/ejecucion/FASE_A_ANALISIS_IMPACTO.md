# ANÁLISIS DE IMPACTO - Eliminación UserServiceAccess

**Fecha:** 2026-01-21  
**FASE A - DT-002**  
**Duración análisis:** 30 min  

---

## 📊 ARCHIVOS AFECTADOS

### 1. Models

```yaml
apps/access/models.py:
  ✅ class UserServiceAccess (líneas ~427-553)
  ✅ Métodos:
     - has_service_access(user, service)
     - get_user_services(user)
     - grant_access(...)
     - revoke_access(...)
```

### 2. Serializers

```yaml
apps/access/serializers.py:
  ✅ UserServiceAccessSerializer
  ✅ UserServiceAccessListSerializer
  ✅ Validaciones custom
```

### 3. Filters

```yaml
apps/access/filters.py:
  ✅ UserServiceAccessFilter
  ✅ 10 filtros aprox
```

### 4. Permissions

```yaml
apps/core/permissions.py:
  ✅ class HasServiceAccess
  ✅ has_permission() method
  ✅ Usa UserServiceAccess.has_service_access()

apps/pipeline/permissions.py:
  ✅ class HasServiceAccess (DUPLICADO!)
  ✅ Implementación similar
```

### 5. Mixins

```yaml
apps/core/mixins.py:
  ✅ ServiceFilterMixin
  ✅ get_queryset() filtra por UserServiceAccess
```

### 6. Services

```yaml
apps/core/services.py:
  ✅ Métodos que usan UserServiceAccess
  ✅ get_user_services(user)
```

### 7. ViewSets (USO REAL)

```yaml
apps/pipeline/viewsets.py:
  ✅ CallRecordViewSet
     permission_classes = [
         IsAuthenticated,
         IsActiveUser,
         HasServiceAccess,  ← AQUÍ
     ]
```

### 8. Migrations

```yaml
apps/access/migrations/0001_initial.py:
  ✅ CreateModel UserServiceAccess
  ✅ Fields, indexes, constraints
```

### 9. Tests

```yaml
tests/unit/core/test_permissions.py:
  ✅ TestHasServiceAccess (5 tests creados en FASE 3)
```

---

## 🔍 ANÁLISIS DETALLADO

### ViewSets Afectados

```python
# apps/pipeline/views.py

class CallRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CallRecord.
    
    ACTUALMENTE usa HasServiceAccess.
    """
    permission_classes = [
        drf_permissions.IsAuthenticated,
        IsActiveUser,
        HasServiceAccess,  # ← ELIMINAR
    ]
```

**Reemplazo con RBAC:**

```python
from apps.core.permissions import RequiresFunctionPermission

class CallRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [
        drf_permissions.IsAuthenticated,
        RequiresFunctionPermission,  # ← NUEVO
    ]
    
    function_map = {
        'list': 'CALL_VIEW',
        'retrieve': 'CALL_VIEW',
        'create': 'CALL_EDIT',
        'update': 'CALL_EDIT',
        'partial_update': 'CALL_EDIT',
        'destroy': 'CALL_DELETE',
        'export_csv': 'CALL_EXP_CSV',
        'stats': 'CALL_STATS',
    }
```

---

## 📋 FUNCIONES A USAR (MOD_Calls)

```yaml
Funciones existentes en MOD_Calls:
  ✅ CALL_VIEW: Ver llamadas
  ✅ CALL_EDIT: Editar llamadas
  ✅ CALL_DELETE: Eliminar llamadas
  ✅ CALL_EXP_CSV: Exportar llamadas
  ✅ CALL_STATS: Estadísticas llamadas

NO necesitamos crear nuevas functions.
Solo usar las existentes.
```

---

## 🗄️ DATA EN DB

```bash
# Verificar si hay data
python manage.py shell
>>> from apps.access.models import UserServiceAccess
>>> count = UserServiceAccess.objects.count()
>>> active = UserServiceAccess.objects.filter(is_active=True).count()
>>> print(f"Total: {count}, Activos: {active}")
```

**Estrategia según data:**

```yaml
Si count < 50:
  → Reasignar manualmente a Groups con CALL_VIEW
  → No migración automática

Si count >= 50:
  → Script de migración
  → Crear Group "GRP_CallRecords"
  → Asignar usuarios automáticamente
```

---

## 🚨 IMPACTO EN PRODUCCIÓN

### Alto Impacto

```yaml
CallRecordViewSet:
  ✅ Endpoint crítico
  ✅ Usado diariamente
  ✅ Debe funcionar post-migración
  
  Mitigación:
    - Asignar CALL_VIEW a usuarios actuales
    - Testing exhaustivo
    - Deploy en horario bajo
```

### Bajo Impacto

```yaml
Serializers/Filters:
  ✅ Solo eliminación
  ✅ No usados en producción directamente
```

---

## ✅ PLAN DE MIGRACIÓN

### Opción A: Manual (< 50 usuarios)

```python
# Script: migrate_service_access_manual.py

from apps.access.models import UserServiceAccess, Function, Group, UserGroup, GroupFunction

# 1. Crear Group para CallRecords
call_group, _ = Group.objects.get_or_create(
    code='GRP_CallRecords',
    defaults={
        'name': 'Acceso a Registros de Llamadas',
        'description': 'Usuarios con acceso a call records (migrado de UserServiceAccess)',
    }
)

# 2. Asignar CALL_VIEW al grupo
call_view = Function.objects.get(code='CALL_VIEW')
GroupFunction.objects.get_or_create(
    group=call_group,
    function=call_view,
)

# 3. Migrar usuarios
service_accesses = UserServiceAccess.objects.filter(is_active=True)
for access in service_accesses:
    UserGroup.objects.get_or_create(
        user=access.user,
        group=call_group,
        defaults={
            'assigned_by': access.granted_by,
            'reason': f'Migrado de UserServiceAccess (servicio: {access.servicio_800})',
        }
    )

print(f'Migrados {service_accesses.count()} usuarios a {call_group.code}')
```

### Opción B: Automática (>= 50 usuarios)

Similar a Opción A pero con verificaciones adicionales.

---

## 🔍 VERIFICACIÓN PRE-ELIMINACIÓN

```bash
# 1. Verificar imports
grep -r "UserServiceAccess" apps/ --include="*.py" | wc -l
# Resultado esperado: ~30 líneas

# 2. Verificar permission classes
grep -r "HasServiceAccess" apps/ --include="*.py" | wc -l
# Resultado esperado: ~7 líneas

# 3. Verificar tests
grep -r "UserServiceAccess\|HasServiceAccess" tests/ --include="*.py" | wc -l
# Resultado esperado: ~5-10 líneas
```

---

## 📊 RESUMEN

```yaml
Archivos a modificar: 9
  - apps/access/models.py (eliminar)
  - apps/access/serializers.py (eliminar)
  - apps/access/filters.py (eliminar)
  - apps/core/permissions.py (eliminar)
  - apps/core/mixins.py (eliminar)
  - apps/core/services.py (modificar)
  - apps/pipeline/permissions.py (eliminar)
  - apps/pipeline/views.py (modificar)
  - tests/unit/core/test_permissions.py (eliminar)

ViewSets afectados: 1
  - CallRecordViewSet (usar RequiresFunctionPermission)

Functions a usar: 5 (ya existen)
  - CALL_VIEW, CALL_EDIT, CALL_DELETE, CALL_EXP_CSV, CALL_STATS

Migración data:
  - Depende de count en DB
  - Script de migración si necesario

Riesgo: MEDIO
  - Endpoint usado en producción
  - Requiere testing exhaustivo
  - Deploy controlado
```

---

## ✅ SIGUIENTE PASO

```yaml
A.2: Verificar Functions MOD_Calls
  - Confirmar CALL_VIEW, CALL_EDIT, etc. existen
  - Si no, crearlas
  - Continuar con A.3
```

---

**Análisis completado:** ✅  
**Duración:** 30 min  
**Estado:** Listo para A.2
