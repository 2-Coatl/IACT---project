# TESTS GENERADOS - SISTEMA DE NAVEGACION v3.0.0

**Fecha:** 16 de enero de 2026  
**Enfoque:** TDD (Test-Driven Development)  
**Framework:** pytest + pytest-django  
**Cobertura:** Sistema completo de navegación, User model, APIs

---

## RESUMEN DE TESTS

### Total de archivos de tests: 5

```
apps/core/tests/
  ├── test_navigation_builders.py    (~700 líneas, 40+ tests)
  └── test_navigation_views.py       (~250 líneas, 12+ tests)

apps/users/tests/
  ├── test_user_model.py              (~500 líneas, 35+ tests)
  ├── test_avatar_api.py              (~450 líneas, 25+ tests)
  └── test_profile_api.py             (~450 líneas, 30+ tests)

Total: ~2,350 líneas de tests
Total: ~142 tests unitarios
```

---

## COBERTURA DETALLADA

### 1. MenuBuilder y MenuValidator (40+ tests)

**Archivo:** `apps/core/tests/test_navigation_builders.py`

**Tests MenuValidator:**
- ✅ Validación de IDs numéricos válidos/inválidos
- ✅ Validación de IDs nivel 1 (1-99)
- ✅ Validación de IDs nivel 2 (100-899)
- ✅ Validación de estructura de menú
- ✅ Validación de campos requeridos
- ✅ Validación de iconos físicos
- ✅ Detección de IDs fuera de rango

**Tests MenuBuilder:**
- ✅ Construcción de menú filtrado por permisos RBAC
- ✅ Menú sin permisos (vacío)
- ✅ Menú con todos los permisos
- ✅ Filtrado por required_functions
- ✅ Personalización de {{user.avatar_url}}
- ✅ Personalización de {{user.username}}
- ✅ Carga de múltiples metadata
- ✅ Ordenamiento de menús

**Tests MenuSerializer:**
- ✅ Serialización nivel 1
- ✅ Serialización con endpoint
- ✅ Serialización con submenús
- ✅ Eliminación de campos internos

**Tests de Integración:**
- ✅ Construcción con múltiples apps
- ✅ Ordenamiento correcto

---

### 2. API Navigation (12+ tests)

**Archivo:** `apps/core/tests/test_navigation_views.py`

**Tests user_menu_view:**
- ✅ Requiere autenticación
- ✅ Retorna menú del usuario
- ✅ Retorna menú vacío (sin permisos)
- ✅ Manejo de errores en MenuBuilder
- ✅ Serialización correcta
- ✅ URL pattern correcto
- ✅ Respuesta JSON
- ✅ Usuario sin nombre completo
- ✅ Estructura de respuesta (menu + user)

**Tests URLs:**
- ✅ app_name correcto
- ✅ URLs resuelven correctamente

---

### 3. User Model Extendido (35+ tests)

**Archivo:** `apps/users/tests/test_user_model.py`

**Tests Campos:**
- ✅ Crear usuario con avatar
- ✅ Crear usuario con phone
- ✅ Crear usuario con position
- ✅ Crear usuario con employee_id
- ✅ employee_id único
- ✅ __str__ con/sin nombre completo

**Tests Avatar:**
- ✅ get_avatar_url() con avatar
- ✅ get_avatar_url() sin avatar (default)
- ✅ delete_avatar() exitoso
- ✅ delete_avatar() sin avatar
- ✅ user_avatar_path() correcto
- ✅ Preservación de extensión

**Tests RBAC:**
- ✅ get_functions() retorna lista
- ✅ get_functions() vacío para usuario nuevo
- ✅ has_function() True/False
- ✅ has_any_function() True/False
- ✅ has_all_functions() True/False
- ✅ has_all_functions() con lista vacía

**Tests Meta:**
- ✅ db_table correcto
- ✅ verbose_name correcto
- ✅ Ordenamiento por username
- ✅ Índices en username, email, employee_id

**Tests get_full_name:**
- ✅ Con first_name y last_name
- ✅ Solo first_name
- ✅ Vacío retorna username
- ✅ Espacios retorna username

---

### 4. API Avatar (25+ tests)

**Archivo:** `apps/users/tests/test_avatar_api.py`

**Tests Upload Avatar:**
- ✅ Requiere autenticación
- ✅ Upload exitoso
- ✅ Sin archivo enviado (error)
- ✅ Extensión inválida (error)
- ✅ Archivo muy grande (error)
- ✅ Reemplaza avatar anterior
- ✅ Upload JPG
- ✅ Upload PNG
- ✅ Upload GIF

**Tests Delete Avatar:**
- ✅ Requiere autenticación
- ✅ Delete exitoso
- ✅ Sin avatar para eliminar
- ✅ Manejo de errores
- ✅ Retorna URL default

**Tests URLs:**
- ✅ URLs resuelven correctamente
- ✅ URLs diferentes

---

### 5. API Profile (30+ tests)

**Archivo:** `apps/users/tests/test_profile_api.py`

**Tests Get Profile:**
- ✅ Requiere autenticación
- ✅ Retorna perfil completo
- ✅ Incluye avatar_url
- ✅ Incluye funciones RBAC
- ✅ Usuario mínimo (solo username)
- ✅ Incluye created_at
- ✅ Manejo de errores

**Tests Update Profile:**
- ✅ Requiere autenticación
- ✅ Actualizar first_name
- ✅ Actualizar last_name
- ✅ Actualizar phone
- ✅ Actualizar position
- ✅ Actualizar múltiples campos
- ✅ Sin campos enviados
- ✅ Ignora campos no permitidos
- ✅ Retorna perfil actualizado
- ✅ Manejo de errores

**Tests URLs:**
- ✅ URLs resuelven correctamente
- ✅ URLs diferentes

---

## COMO EJECUTAR LOS TESTS

### Todos los tests:

```bash
cd /tmp/iact-project/callcentersite
pytest
```

### Por módulo:

```bash
# Tests de navegación
pytest apps/core/tests/test_navigation_builders.py -v
pytest apps/core/tests/test_navigation_views.py -v

# Tests de usuario
pytest apps/users/tests/test_user_model.py -v
pytest apps/users/tests/test_avatar_api.py -v
pytest apps/users/tests/test_profile_api.py -v
```

### Con cobertura:

```bash
pytest --cov=apps.core.navigation --cov=apps.users -v
```

### Tests específicos:

```bash
# Solo tests de MenuBuilder
pytest apps/core/tests/test_navigation_builders.py::TestMenuBuilder -v

# Solo tests de avatar
pytest apps/users/tests/test_avatar_api.py::TestUploadAvatarAPI -v

# Solo tests de RBAC
pytest apps/users/tests/test_user_model.py::TestUserRBACMethods -v
```

---

## FIXTURES Y MOCKS

### Fixtures comunes:

```python
@pytest.fixture
def api_client():
    """Cliente API de DRF."""
    return APIClient()

@pytest.fixture
def authenticated_user(django_user_model):
    """Usuario autenticado."""
    return django_user_model.objects.create_user(...)

@pytest.fixture
def sample_metadata():
    """Metadata de menú de ejemplo."""
    return {...}
```

### Mocks utilizados:

```python
# MenuBuilder
@patch('apps.core.navigation.builders.MenuBuilder._load_all_menu_metadata')

# User methods
@patch.object(User, 'get_functions')
@patch.object(User, 'delete_avatar')

# File system
@patch('os.path.exists')
@patch('os.remove')

# Settings
@patch('apps.users.views.settings')
```

---

## ASSERTIONS COMUNES

```python
# Status codes
assert response.status_code == status.HTTP_200_OK
assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Data structure
assert 'menu' in response.data
assert len(menu_data) == 1

# Field values
assert user.avatar is not None
assert user.phone == '+56912345678'

# Validation
assert MenuValidator.validate_numeric_id(5) is True
assert builder._has_permission(user, item) is True

# DB changes
user.refresh_from_db()
assert user.first_name == 'Updated'
```

---

## COBERTURA ESPERADA

Estimación de cobertura:

```
apps/core/navigation/builders.py    95%+
apps/core/navigation/views.py       90%+
apps/users/models.py (extended)     85%+
apps/users/views.py (avatar+profile)90%+
```

---

## DEPENDENCIAS

```bash
# Requirements para tests
pytest>=7.0.0
pytest-django>=4.5.0
pytest-cov>=4.0.0
factory-boy>=3.2.0  # Opcional, para fixtures complejas
freezegun>=1.2.0    # Opcional, para tests de tiempo
```

---

## SIGUIENTE PASO

```bash
# Ejecutar tests
cd /tmp/iact-project/callcentersite
pytest -v --tb=short

# Ver cobertura
pytest --cov=apps --cov-report=html
open htmlcov/index.html
```

---

## METRICAS

| Métrica | Valor |
|---------|-------|
| Archivos de tests | 5 |
| Líneas de tests | ~2,350 |
| Tests unitarios | ~142 |
| Fixtures | ~15 |
| Mocks/Patches | ~20 |
| Cobertura estimada | 90%+ |

---

**Estado:** ✅ TESTS COMPLETOS Y LISTOS PARA EJECUTAR

**Ubicación:** /tmp/iact-project/callcentersite/apps/*/tests/

**Enfoque:** TDD - Los tests cubren toda la funcionalidad implementada
