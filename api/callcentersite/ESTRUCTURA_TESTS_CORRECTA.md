# ESTRUCTURA CORRECTA DE TESTS - TDD

**Fecha:** 16 de enero de 2026  
**Proyecto:** IACT Call Center System  
**Ubicación:** /tmp/iact-project/callcentersite  

---

## ✅ ESTRUCTURA CORRECTA

Los tests **NO** deben estar dentro de las apps para evitar contaminar producción.

### Estructura implementada:

```
callcentersite/
├── apps/                       # Apps de producción (SIN tests)
│   ├── core/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── navigation/
│   │   │   ├── builders.py
│   │   │   └── views.py
│   │   └── ... (SIN carpeta tests/)
│   │
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── ... (SIN carpeta tests/)
│   │
│   └── ...
│
├── tests/                      # TODOS los tests aquí
│   ├── __init__.py
│   ├── conftest.py            # Fixtures compartidos
│   ├── pytest.ini             # Configuración
│   │
│   ├── unit/                   # Tests unitarios
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── test_navigation_builders.py    ✅
│   │   │   └── test_navigation_views.py       ✅
│   │   │
│   │   └── users/
│   │       ├── __init__.py
│   │       ├── test_user_model.py             ✅
│   │       ├── test_avatar_api.py             ✅
│   │       ├── test_profile_api.py            ✅
│   │       ├── test_serializers.py            (existente)
│   │       └── test_views.py                  (existente)
│   │
│   ├── integration/            # Tests de integración
│   │   └── ...
│   │
│   ├── api/                    # Tests de API
│   │   └── ...
│   │
│   ├── e2e/                    # Tests end-to-end
│   │   └── ...
│   │
│   └── fixtures/               # Fixtures reutilizables
│       ├── users.py
│       └── rbac.py
│
├── pytest.ini                  # Configuración pytest
├── run_tests.sh                # Script ejecutable
└── ...
```

---

## VENTAJAS DE ESTA ESTRUCTURA

### ✅ Separación de concerns
- Apps de producción limpias (sin código de tests)
- Tests centralizados y organizados
- Fácil exclusión de tests en deploy

### ✅ Mejor organización
- Tests agrupados por tipo (unit, integration, api, e2e)
- Fixtures compartidos en un solo lugar
- Configuración centralizada

### ✅ Deploy más limpio
- No se copian archivos de tests a producción
- Menor tamaño del paquete desplegado
- Mejor seguridad (no exponer datos de tests)

### ✅ CI/CD optimizado
```yaml
# .github/workflows/tests.yml
- name: Run tests
  run: pytest tests/unit/  # Solo el directorio tests/
```

---

## ARCHIVOS MOVIDOS

### De apps/ a tests/unit/

```
ANTES (❌ INCORRECTO):
apps/core/tests/
  ├── test_navigation_builders.py
  └── test_navigation_views.py

apps/users/tests/
  ├── test_user_model.py
  ├── test_avatar_api.py
  └── test_profile_api.py

DESPUÉS (✅ CORRECTO):
tests/unit/core/
  ├── test_navigation_builders.py
  └── test_navigation_views.py

tests/unit/users/
  ├── test_user_model.py
  ├── test_avatar_api.py
  └── test_profile_api.py
```

---

## CONFIGURACIÓN

### pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.testing

# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Test paths - Busca tests en tests/ (NO en apps/)
testpaths = tests

# Markers
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    e2e: End-to-end tests
```

### conftest.py

Fixtures compartidos disponibles para todos los tests:
- `api_client` - Cliente API de DRF
- `authenticated_client` - Cliente autenticado
- `admin_client` - Cliente admin
- `sample_user` - Usuario de prueba
- `sample_admin` - Admin de prueba

---

## COMO EJECUTAR TESTS

### Opción 1: Script interactivo
```bash
cd /tmp/iact-project/callcentersite
./run_tests.sh
```

### Opción 2: pytest directo

**Todos los tests:**
```bash
pytest tests/unit/
```

**Por directorio:**
```bash
pytest tests/unit/core/     # Solo tests de core
pytest tests/unit/users/    # Solo tests de users
```

**Por archivo:**
```bash
pytest tests/unit/core/test_navigation_builders.py -v
pytest tests/unit/users/test_avatar_api.py -v
```

**Con cobertura:**
```bash
pytest tests/unit/ \
  --cov=apps.core.navigation \
  --cov=apps.users \
  --cov-report=html
```

**Por marker:**
```bash
pytest -m unit        # Solo tests unitarios
pytest -m api         # Solo tests de API
pytest -m integration # Solo tests de integración
```

---

## IMPORTS EN LOS TESTS

Los tests importan directamente desde apps:

```python
# tests/unit/core/test_navigation_builders.py
from apps.core.navigation.builders import MenuBuilder, MenuValidator
from apps.users.models import CustomUser

# tests/unit/users/test_user_model.py
from django.contrib.auth import get_user_model

User = get_user_model()
```

**NO** necesitan imports relativos complicados porque tests/ está en la raíz del proyecto.

---

## FIXTURES COMPARTIDOS

### Desde conftest.py (automático):

```python
# Ya disponibles en todos los tests
def test_endpoint(api_client):
    """Usa fixture api_client automáticamente."""
    response = api_client.get('/api/v1/navigation/menu/')
    assert response.status_code == 401

def test_authenticated(authenticated_client):
    """Usa fixture authenticated_client."""
    response = authenticated_client.get('/api/v1/users/profile/')
    assert response.status_code == 200
```

### Fixtures específicos por app:

```python
# tests/unit/users/test_avatar_api.py
@pytest.fixture
def user_with_avatar(db):
    """Fixture específico para tests de avatar."""
    user = User.objects.create_user(...)
    user.avatar = ...
    return user
```

---

## ESTRUCTURA COMPLETA DE TESTS

```
tests/
├── __init__.py
├── conftest.py                 # Fixtures globales
├── README.md                   # Documentación
│
├── unit/                       # Tests unitarios (rápidos, aislados)
│   ├── __init__.py
│   ├── core/
│   │   ├── test_navigation_builders.py    (492 líneas, 40 tests)
│   │   ├── test_navigation_views.py       (256 líneas, 12 tests)
│   │   ├── test_core_models.py            (existente)
│   │   └── ...
│   │
│   ├── users/
│   │   ├── test_user_model.py             (380 líneas, 35 tests)
│   │   ├── test_avatar_api.py             (341 líneas, 21 tests)
│   │   ├── test_profile_api.py            (359 líneas, 22 tests)
│   │   ├── test_serializers.py            (existente)
│   │   └── test_views.py                  (existente)
│   │
│   ├── access/
│   ├── audit/
│   └── ...
│
├── integration/                # Tests de integración
│   └── ...
│
├── api/                        # Tests de endpoints completos
│   └── ...
│
├── e2e/                        # Tests end-to-end
│   └── ...
│
└── fixtures/                   # Fixtures reutilizables
    ├── users.py
    └── rbac.py
```

---

## VENTAJAS ESPECÍFICAS DEL PROYECTO

### Para Django:
```python
# settings/base.py NO necesita incluir tests en INSTALLED_APPS
INSTALLED_APPS = [
    'apps.core',
    'apps.users',
    # ... (SIN tests)
]
```

### Para Collectstatic:
```bash
# No copia archivos de tests a static/
python manage.py collectstatic
```

### Para Docker:
```dockerfile
# Dockerfile.prod
COPY apps/ /app/apps/
# NO copia tests/
```

---

## COMANDOS ÚTILES

### Ejecutar solo nuevos tests:
```bash
pytest tests/unit/core/test_navigation_builders.py tests/unit/users/test_user_model.py -v
```

### Ver estructura de tests:
```bash
pytest --collect-only tests/unit/
```

### Ejecutar tests rápidos:
```bash
pytest tests/unit/ -m "not slow"
```

### Coverage específico:
```bash
pytest tests/unit/core/ --cov=apps.core.navigation --cov-report=term-missing
```

---

## MÉTRICAS

```
Ubicación correcta:     tests/unit/
Archivos movidos:       5
Líneas de tests:        1,828
Tests unitarios:        130+
Estructura:             ✅ CORRECTA
Producción limpia:      ✅ SIN TESTS
```

---

## SIGUIENTE PASO

```bash
cd /tmp/iact-project/callcentersite

# Ejecutar todos los tests
pytest tests/unit/core/ tests/unit/users/ -v

# O usar el script
./run_tests.sh
```

---

**Estado:** ✅ ESTRUCTURA CORRECTA IMPLEMENTADA

**Ubicación:** tests/unit/ (fuera de apps/)

**Apps limpias:** ✅ Sin carpetas tests/

**Listo para producción:** ✅ SÍ
