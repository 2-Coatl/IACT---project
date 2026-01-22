---
version: 1.0.0
date: 2026-01-20
project: IACT Call Center System
type: Refactoring Progress
categoria: refactoring
tema: REFACTORING PARTE 1 - apps/centers/ Creada
autor: Claude Technical Analysis
tags: [refactoring, centers, models, migration]
estado: parte-1-completada
---

# REFACTORING PARTE 1: apps/centers/ CREADA ✅

---

## 📋 OBJETIVO PARTE 1

Crear **apps/centers/** y mover modelos **Center** y **Service** desde apps/core/.

---

## ✅ COMPLETADO

### 1. Estructura apps/centers/ Creada

```bash
apps/centers/
├── __init__.py           ✅ CREADO
├── apps.py               ✅ CREADO (CentersConfig)
├── models.py             ✅ CREADO (Center, Service)
├── admin.py              ✅ CREADO (CenterAdmin, ServiceAdmin)
├── tests.py              ✅ CREADO (CenterModelTest, ServiceModelTest)
├── views.py              ✅ CREADO (placeholder)
└── migrations/
    └── __init__.py       ✅ CREADO
```

### 2. Models Movidos

```python
# apps/centers/models.py

✅ Center Model:
- Campos: nombre, codigo, descripcion, direccion, activo
- Meta: db_table='core_centers' (PRESERVED ✅)
- Methods: get_active_services_count(), deactivate()
- SoftDeleteMixin integrado

✅ Service Model:
- Campos: numero_800, nombre, descripcion, center (FK), activo
- Meta: db_table='core_services' (PRESERVED ✅)
- Methods: get_users_with_access_count(), grant_access_to_user()
- SoftDeleteMixin integrado
```

### 3. Imports Actualizados

```python
# apps/centers/models.py
from apps.utils import SoftDeleteMixin
from apps.utils.validators import validate_service_800, validate_codigo_center

# Circular dependency evitada
from apps.access.models import UserServiceAccess  # Solo en método
```

### 4. Admin Configurado

```python
✅ CenterAdmin:
- list_display: codigo, nombre, activo, created_at
- search_fields: codigo, nombre, descripcion
- Fieldsets organizados

✅ ServiceAdmin:
- list_display: numero_800, nombre, center, activo
- search_fields: numero_800, nombre, descripcion, center__nombre
- Fieldsets organizados
```

### 5. Tests Básicos Creados

```python
✅ CenterModelTest (3 tests):
- test_center_creation()
- test_center_str()
- (tests de métodos de negocio pendientes)

✅ ServiceModelTest (3 tests):
- test_service_creation()
- test_service_str()
- test_service_center_relationship()
```

---

## 🔴 CRÍTICO: db_table PRESERVADO

```python
# IMPORTANTE: Las tablas de BD NO cambian

class Center(SoftDeleteMixin, models.Model):
    class Meta:
        db_table = 'core_centers'  # ✅ MANTIENE tabla existente

class Service(SoftDeleteMixin, models.Model):
    class Meta:
        db_table = 'core_services'  # ✅ MANTIENE tabla existente
```

**Beneficios:**
- ✅ NO requiere migración de datos
- ✅ BD existente sigue funcionando
- ✅ Solo cambian los imports en código Python

---

## ⏳ PENDIENTE PARTE 2

```yaml
1. Actualizar Imports en apps existentes:
   [ ] apps/core/serializers.py
   [ ] apps/core/filters.py
   [ ] apps/core/permissions.py
   [ ] apps/core/viewsets.py (si existe)
   [ ] apps/core/services/center_service.py
   [ ] apps/core/services/service_service.py
   [ ] tests/factories/ (si existen factories)
   [ ] Cualquier otro archivo que importe Center/Service

2. Eliminar de apps/core/models.py:
   [ ] class Center (mover a deprecation warning)
   [ ] class Service (mover a deprecation warning)

3. Registrar app en settings:
   [ ] Agregar 'apps.centers' a INSTALLED_APPS

4. Crear migration SeparateDatabaseAndState:
   [ ] Migration que declare modelos sin alterar BD
```

---

## 📊 PRÓXIMOS PASOS

```yaml
PARTE 2: Actualizar Imports (próximo)
  [ ] Actualizar imports en ~10-15 archivos
  [ ] Eliminar Center/Service de apps/core/models.py
  [ ] Agregar apps.centers a INSTALLED_APPS
  [ ] Crear migration sin alterar BD
  
PARTE 3: apps/calls/ + CallRecord
  [ ] Crear apps/calls/
  [ ] Mover CallRecord desde apps/core/
  [ ] Actualizar imports
  
PARTE 4: apps/access/ + UserServiceAccess
  [ ] Mover UserServiceAccess a apps/access/
  [ ] Actualizar imports
  
PARTE 5: apps/core/ Solo Abstract Models
  [ ] Limpiar apps/core/models.py
  [ ] Dejar SOLO TimeStampedModel, SoftDeleteMixin
  [ ] Verificar arquitectura final
```

---

## ✅ VERIFICACIÓN

```bash
# Estructura apps/centers/ creada
✅ 7 archivos creados
✅ Models con db_table preserved
✅ Admin configurado
✅ Tests básicos
✅ No cambios en BD

# Pendiente
⏳ Actualizar imports (PARTE 2)
⏳ Registrar en INSTALLED_APPS
⏳ Migration SeparateDatabaseAndState
```

---

**FIN PARTE 1**

**Estado:** ✅ COMPLETADA  
**Archivos Creados:** 7  
**Próximo:** PARTE 2 - Actualizar Imports
