---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Plan de Acción
categoria: arquitectura/testing
---

# PLAN ACCIÓN INMEDIATA - TESTING FUNCIONAL

## OBJETIVO

Pasar de **37 tests** a **200+ tests** en 3 horas.

---

## ACCIONES

### ACCIÓN 1: Crear network.py (15 min)

```bash
cd /tmp/iact-real/callcentersite

cat > apps/utils/network.py << 'PYEOF'
"""
Utilidades de red.

Funciones para obtener información del request HTTP.
"""

def get_client_ip(request):
    """
    Obtener IP del cliente.
    
    Maneja proxies (X-Forwarded-For).
    
    Args:
        request: HttpRequest
        
    Returns:
        str: IP del cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def get_user_agent(request):
    """
    Obtener User-Agent del request.
    
    Args:
        request: HttpRequest
        
    Returns:
        str: User-Agent string
    """
    return request.META.get('HTTP_USER_AGENT', '')


def get_request_metadata(request):
    """
    Obtener metadata completo del request.
    
    Args:
        request: HttpRequest
        
    Returns:
        dict: Metadata con ip, user_agent, method, path
    """
    return {
        'ip': get_client_ip(request),
        'user_agent': get_user_agent(request),
        'method': request.method,
        'path': request.path,
    }
PYEOF

echo "✓ network.py creado"
```

---

### ACCIÓN 2: Actualizar permissions/__init__.py (10 min)

```bash
cd /tmp/iact-real/callcentersite

cat > apps/access/permissions/__init__.py << 'PYEOF'
"""
Custom permissions para sistema de acceso.

Exporta:
- HasModuleAccess: Permiso basado en módulo único
- HasAnyModuleAccess: Permiso basado en cualquier módulo de lista
- HasAllModuleAccess: Permiso basado en todos los módulos de lista
- HasFunction: Alias de HasModuleAccess (compatibilidad)
"""

from .module_permissions import (
    HasModuleAccess,
    HasAnyModuleAccess,
    HasAllModuleAccess,
)

# Alias para compatibilidad con tests antiguos
HasFunction = HasModuleAccess

__all__ = [
    'HasModuleAccess',
    'HasAnyModuleAccess',
    'HasAllModuleAccess',
    'HasFunction',
]
PYEOF

echo "✓ permissions/__init__.py actualizado"
```

---

### ACCIÓN 3: Actualizar core/services/__init__.py (15 min)

```bash
cd /tmp/iact-real/callcentersite

# Primero ver qué hay
ls -la apps/core/services/

# Crear ServiceAccessService si no existe
cat >> apps/core/services/__init__.py << 'PYEOF'

class ServiceAccessService:
    """
    Service para gestión de acceso a servicios.
    
    Wrapper sobre UserServiceAccess model.
    """
    
    @staticmethod
    def has_service_access(user, service):
        """
        Verificar si usuario tiene acceso a servicio.
        
        Args:
            user: Usuario
            service: Instancia Service o ID
            
        Returns:
            bool: True si tiene acceso
        """
        from apps.core.models import UserServiceAccess
        return UserServiceAccess.has_service_access(user, service)
    
    @staticmethod
    def get_user_services(user):
        """
        Obtener servicios del usuario.
        
        Args:
            user: Usuario
            
        Returns:
            QuerySet: Servicios accesibles
        """
        from apps.core.models import UserServiceAccess
        return UserServiceAccess.get_user_services(user)
PYEOF

echo "✓ ServiceAccessService agregado"
```

---

### ACCIÓN 4: Actualizar testing.py (20 min)

```bash
cd /tmp/iact-real/callcentersite

# Backup
cp config/settings/testing.py config/settings/testing.py.bak

# Agregar ivr_legacy database
cat > /tmp/update_testing.py << 'PYEOF'
import sys

# Leer archivo
with open('config/settings/testing.py', 'r') as f:
    content = f.read()

# Reemplazar DATABASES
old_db = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    # IVR legacy se mantiene si tests lo requieren
    # O se puede mock
}"""

new_db = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {'NAME': ':memory:'},
    },
    'ivr_legacy': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {'NAME': ':memory:'},
    },
}"""

content = content.replace(old_db, new_db)

# Guardar
with open('config/settings/testing.py', 'w') as f:
    f.write(content)

print("✓ testing.py actualizado")
PYEOF

./venv/bin/python /tmp/update_testing.py
```

---

### ACCIÓN 5: Verificar INSTALLED_APPS (10 min)

```bash
cd /tmp/iact-real/callcentersite

# Ver qué hay en base.py
grep -A 30 "INSTALLED_APPS" config/settings/base.py | head -40
```

Si no existe, agregar a testing.py:

```python
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_spectacular',
    
    # IACT apps
    'apps.access',
    'apps.audit',
    'apps.authentication',
    'apps.core',
    'apps.ivr_legacy',
    'apps.pipeline',
    'apps.reports',
    'apps.users',
    'apps.utils',
]
```

---

### ACCIÓN 6: Ejecutar Tests (5 min)

```bash
cd /tmp/iact-real/callcentersite

# Limpiar cache
rm -rf .pytest_cache
rm -rf __pycache__
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Ejecutar
./venv/bin/pytest -v --tb=short 2>&1 | tee test_results.txt

# Ver resumen
tail -20 test_results.txt
```

---

## VERIFICACIÓN

### Comando Rápido:

```bash
cd /tmp/iact-real/callcentersite
./venv/bin/pytest --tb=no -q
```

### Resultado Esperado:

```
ANTES:  37 passed, 25 failed, 232 errors
DESPUÉS: 200+ passed, 50 failed, 44 errors
```

---

## TROUBLESHOOTING

### Si aún hay errores de imports:

```bash
# Ver errores
./venv/bin/pytest --tb=line 2>&1 | grep "ImportError\|ModuleNotFoundError"

# Verificar archivos creados
ls -la apps/utils/network.py
cat apps/access/permissions/__init__.py | grep HasFunction
```

### Si tests fallan por DB:

```bash
# Verificar testing.py
cat config/settings/testing.py | grep -A 10 "DATABASES"
```

---

## TIEMPO TOTAL

```
Acción 1: 15 min
Acción 2: 10 min
Acción 3: 15 min
Acción 4: 20 min
Acción 5: 10 min
Acción 6:  5 min
-----------------
TOTAL:   75 min (1.25 horas)
```

---

## SIGUIENTE PASO

Una vez que los tests pasen:

```bash
# Generar reporte de cobertura
./venv/bin/pytest --cov=apps --cov-report=html

# Ver reporte
# htmlcov/index.html
```

---

**FIN DEL PLAN**

Version: 1.0.0
Fecha: 2026-01-17
Tiempo: 75 minutos
Objetivo: 37 → 200+ tests

