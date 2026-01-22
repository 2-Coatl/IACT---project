---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System  
type: Análisis Técnico Testing
categoria: arquitectura/testing
---

# ANÁLISIS OPCIONES TESTING - ENTORNO RESTRINGIDO

## RESTRICCIONES

```
❌ NO red externa
❌ NO git clone
❌ NO puertos
❌ NO PostgreSQL
❌ NO MariaDB

✅ Python + venv
✅ SQLite
✅ pytest
```

## ESTADO ACTUAL

```
37 PASSED   ✓
25 FAILED   (esperan DB real)
232 ERRORS  (imports faltantes)
```

## PROBLEMAS DETECTADOS

### 1. Imports Faltantes (3 archivos):

```
ERROR: apps.access.permissions.HasFunction
       → Archivo tiene HasModuleAccess, falta alias

ERROR: apps.core.services.ServiceAccessService
       → No existe, usar model.has_service_access()

ERROR: apps.utils.network
       → Módulo no existe, crear
```

### 2. Base de Datos:

```
testing.py usa: SQLite :memory: (DEFAULT)
Falta: ivr_legacy database (MariaDB)
```

## SOLUCIONES

### OPCIÓN 1: SQLite Dual (RECOMENDADA - 1h)

```python
# testing.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'ivr_legacy': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}
```

**Ventajas:**
- ✅ Sin servicios externos
- ✅ Rápido
- ✅ CI/CD ready

**Limitación:**
- ⚠️ SQLite != PostgreSQL/MariaDB (diferencias menores)

---

### OPCIÓN 2: Arreglar Imports (2h)

```python
# 1. apps/access/permissions/__init__.py
from .module_permissions import HasModuleAccess
HasFunction = HasModuleAccess  # Alias

# 2. apps/utils/network.py (CREAR)
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT', '')

# 3. apps/core/services/__init__.py
# Importar o crear ServiceAccessService
```

---

## ESTRATEGIA RECOMENDADA

### FASE 1: QUICK WINS (3h)

```
1. Arreglar imports (2h)
   232 errors → 0

2. SQLite dual (1h)
   Tests ejecutan completos

RESULTADO: 37 → 200 tests ✓
```

### FASE 2: OPTIMIZACIÓN (4h)

```
3. Fixtures (2h)
4. Mocks (2h)

RESULTADO: 200 → 250 tests ✓
```

### FASE 3: COMPLETAR (3h)

```
5. Tests DB (2h)
6. Coverage (1h)

RESULTADO: 250 → 270+ tests ✓
```

## IMPLEMENTACIÓN INMEDIATA

### Paso 1: Crear network.py

```bash
cd /tmp/iact-real/callcentersite
cat > apps/utils/network.py << 'PY'
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT', '')

def get_request_metadata(request):
    return {
        'ip': get_client_ip(request),
        'user_agent': get_user_agent(request),
        'method': request.method,
        'path': request.path,
    }
PY
```

### Paso 2: Actualizar permissions/__init__.py

```bash
cat > apps/access/permissions/__init__.py << 'PY'
from .module_permissions import (
    HasModuleAccess,
    HasAnyModuleAccess,
    HasAllModuleAccess,
)

# Alias para compatibilidad
HasFunction = HasModuleAccess
PY
```

### Paso 3: Actualizar testing.py

```python
# Agregar ivr_legacy database
DATABASES = {
    'default': {...},
    'ivr_legacy': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}
```

### Paso 4: Ejecutar

```bash
./venv/bin/pytest -v
```

## MÉTRICAS ESPERADAS

```
ANTES:     37 PASSED / 232 ERRORS
FASE 1:   200 PASSED / 44 ERRORS
FASE 2:   250 PASSED / 14 ERRORS  
FASE 3:   270+ PASSED / 9 ERRORS
```

## CONCLUSIÓN

**ACCIÓN INMEDIATA:** Implementar Fase 1 (3 horas)

**Resultado:** 13% → 68% cobertura tests

---

