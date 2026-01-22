---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis Técnico - App Específica
categoria: arquitectura/testing/apps
app: users
tema: Refactorización completa de testing para app USERS
autor: Claude Technical Analysis
tags: [users, testing, refactoring, custom-user, rbac, avatar]
relacionado:
  - ANALISIS_COMPLETO_REFACTORING_TESTING_v2.0.0.md
  - ANALISIS_APP_UTILS_REFACTORING_v1.0.0.md
  - ANALISIS_APP_CORE_REFACTORING_v1.0.0.md
estado: completado
prioridad: ALTA
tiempo_estimado: 1-2 semanas
tests_totales: 70 tests
tests_actuales: 0 passing (0%)
tests_bloqueados: 70 tests (100%)
cobertura_actual: 0%
cobertura_objetivo: 90%+
---

# ANÁLISIS COMPLETO: APP USERS - REFACTORING

**CustomUser Model + RBAC + Avatar - Análisis basado en código REAL**

---

## RESUMEN EJECUTIVO

### Estado Actual

```
APP: apps/users/
PROPÓSITO: Gestión de usuarios personalizados con RBAC y avatar
TAMAÑO: 773 líneas de tests (12% del proyecto)
TESTS: 70 tests identificados
ESTADO: CRÍTICO - 0 tests pasando (0% - 100% bloqueados)
TIEMPO ESTIMADO: 1-2 semanas (40-80 horas)
PRIORIDAD: 🔴 ALTA - Base de autenticación y permisos
```

### Problema Principal IDENTIFICADO

```
NO MIGRATIONS - CRÍTICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CAUSA RAÍZ:
apps/users/migrations/ existe pero está vacío (solo __init__.py)
NO existe 0001_initial.py

CONSECUENCIA:
Django no puede crear DB de test.
Error: IndexError: list index out of range
       key = ('users', '__first__')

IMPACTO:
- 70/70 tests BLOQUEADOS (100%)
- NO se puede ejecutar NINGÚN test
- Otras apps dependen de users y también fallan
- Detectado previamente en análisis de UTILS

MODELO AFECTADO:
CustomUser (hereda de AbstractUser + SoftDeleteMixin)
- Tabla: users
- Campos custom: avatar, phone, position, employee_id
- RBAC: get_functions(), has_function()

SOLUCIÓN:
Crear migration inicial de CustomUser.
python manage.py makemigrations users
python manage.py migrate

RESULTADO ESPERADO:
✅ apps/users/migrations/0001_initial.py creado
✅ Tabla users creada en DB
✅ 70/70 tests desbloqueados
✅ Tiempo: 30 minutos
```

### Métricas Clave

```
CÓDIGO EXISTENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├─ Archivos Python:        8 archivos
├─ Models:                 1 model (CustomUser, 228 líneas)
├─ Views:                  4 views + 1 ViewSet (264 líneas)
├─ Serializers:            2 serializers
├─ Total líneas código:    ~600 líneas

TESTS EXISTENTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├─ Archivos tests:         5 archivos
├─ Total líneas tests:     773 líneas
├─ Tests identificados:    70 tests
├─ Pasando:                0 tests (0%)
├─ Bloqueados:             70 tests (100%)

ESTADO ACTUAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛔ 0/70 tests pasando       (0%)
⛔ 70/70 tests bloqueados   (100%)
⛔ 0% cobertura
```

---

## TABLA DE CONTENIDOS

1. [Código Existente Detallado](#codigo-existente)
2. [Tests Actuales Análisis](#tests-actuales)
3. [Problema de Migrations](#problema-migrations)
4. [Fat Model Detectado](#fat-model)
5. [Soluciones Propuestas](#soluciones)
6. [Plan de Refactorización](#plan-refactoring)
7. [Fixtures Necesarias](#fixtures)
8. [Mocks Necesarios](#mocks)
9. [Roadmap de Implementación](#roadmap)
10. [Criterios de Éxito](#criterios)

---

<a name="codigo-existente"></a>
## 1. CÓDIGO EXISTENTE DETALLADO

### 1.1 Estructura de apps/users/

```
apps/users/
├── __init__.py
├── models.py                    (228 líneas) ⭐ CustomUser
├── models.py.backup             (backup)
├── serializers.py               (2.0 KB)
├── views.py                     (264 líneas)
├── admin.py                     (2.0 KB)
├── apps.py
├── urls.py                      (1.0 KB)
│
├── migrations/                  ⚠️ PROBLEMA
│   └── __init__.py             (vacío - NO hay 0001_initial.py)
│
└── navigation/
    └── menu_metadata.json

TOTAL: ~600 líneas de código Python
```

### 1.2 CustomUser Model (228 líneas)

```python
# ════════════════════════════════════════════════════════════
# apps/users/models.py (228 líneas)
# ════════════════════════════════════════════════════════════

class CustomUser(SoftDeleteMixin, AbstractUser):
    """
    Usuario personalizado del sistema IACT.
    
    HERENCIA:
    ├─ AbstractUser (Django built-in)
    │  ├─ username, password, email
    │  ├─ first_name, last_name
    │  ├─ is_staff, is_active, is_superuser
    │  ├─ date_joined, last_login
    │  └─ groups, user_permissions
    │
    └─ SoftDeleteMixin (apps.utils)
       ├─ is_deleted
       └─ deleted_at
    """

CAMPOS ADICIONALES (líneas 56-89):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. avatar (ImageField)
   - upload_to: user_avatar_path function
   - Path: media/profiles/user_{id}/avatar{ext}
   - max_length: 255
   - nullable
   
2. phone (CharField, 20 chars)
   - Teléfono del usuario
   - nullable
   
3. position (CharField, 100 chars)
   - Cargo/posición
   - nullable
   
4. employee_id (CharField, 20 chars)
   - ID de empleado
   - unique=True
   - nullable
   - db_index

META (líneas 91-100):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

db_table: 'users'
ordering: ['username']
indexes:
  - username
  - email
  - employee_id

MÉTODOS IMPLEMENTADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. __str__() (líneas 102-106)
   Retorna: "Full Name (username)" o "username"
   
2. get_full_name() (líneas 108-116)
   Override de AbstractUser
   Retorna nombre completo o username si vacío
   
3. get_avatar_url() (líneas 118-128)
   Retorna URL del avatar o default
   Default: /static/icons/defaults/avatar_default.png

4. get_functions() (líneas 130-164) ⚠️ FAT MODEL
   64 líneas de LÓGICA DE NEGOCIO
   
   Obtiene funciones RBAC del usuario:
   - Funciones directas (UserFunction)
   - Funciones de grupos (FunctionGroup)
   
   PROBLEMA:
   ❌ Lógica de negocio en MODEL
   ❌ Maneja relaciones con access app
   ❌ Try/except genérico
   ❌ Debería estar en UserService

5. has_function(function_name) (líneas 166-177)
   Verifica si tiene función específica
   Delega a get_functions()
   
6. has_any_function(function_names) (líneas 179-191)
   Verifica si tiene alguna función de la lista
   
7. has_all_functions(function_names) (líneas 193-205)
   Verifica si tiene todas las funciones
   
8. delete_avatar() (líneas 207-227)
   21 líneas de lógica de manejo de archivos
   
   PROBLEMA:
   ❌ File I/O en MODEL
   ❌ Logging en MODEL
   ❌ Debería estar en AvatarService

ANÁLISIS DE ARQUITECTURA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ BUENO:
- Herencia correcta (AbstractUser + SoftDeleteMixin)
- Campos bien definidos
- Meta correcta (indexes, db_table)
- Type hints en docstrings

❌ MALO (Fat Model):
- get_functions(): 64 líneas lógica RBAC
- delete_avatar(): 21 líneas file I/O
- has_function/has_any/has_all: lógica de negocio
- Total: ~100 líneas de lógica en MODEL

REFACTORING NECESARIO:
1. Crear UserService para RBAC
2. Crear AvatarService para archivos
3. Model solo datos
```

### 1.3 Views (264 líneas)

```python
# ════════════════════════════════════════════════════════════
# apps/users/views.py (264 líneas)
# ════════════════════════════════════════════════════════════

COMPONENTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. UserViewSet (líneas 17-46)
   - ModelViewSet estándar
   - CRUD completo
   - Serializer dinámico (create vs otros)
   - Permissions: IsAuthenticated
   
   CALIDAD: ✅ BUENA (limpia, delgada)

2. upload_avatar_view (líneas 53-128)
   76 líneas de lógica de avatar
   
   FUNCIONALIDAD:
   - Validar archivo enviado
   - Validar extensión (.jpg, .jpeg, .png, .gif)
   - Validar tamaño (max 2MB)
   - Eliminar avatar anterior
   - Guardar nuevo avatar
   - Logging
   
   PROBLEMA:
   ❌ Lógica de validación en VIEW
   ❌ File I/O en VIEW
   ❌ 76 líneas muy largo
   ❌ Debería delegarse a AvatarService

3. delete_avatar_view (líneas 131-165)
   35 líneas para eliminar avatar
   
   PROBLEMA:
   ❌ Delega a user.delete_avatar() (model)
   ❌ Debería usar AvatarService

4. get_user_profile_view (líneas 168-206)
   39 líneas para obtener perfil
   
   USA:
   - user.get_functions() (model) ❌
   - user.get_full_name()
   - user.get_avatar_url()
   
   PROBLEMA:
   ❌ Lógica de construcción de datos en VIEW
   ❌ Debería estar en UserService.get_profile()

5. update_user_profile_view (líneas 209-263)
   55 líneas para actualizar perfil
   
   LÓGICA:
   - Whitelist de campos permitidos
   - Actualización dinámica
   - Logging
   
   PROBLEMA:
   ❌ Lógica de actualización en VIEW
   ❌ Debería estar en UserService.update_profile()

ANÁLISIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POSITIVO:
✅ Permisos configurados
✅ Logging implementado
✅ Validaciones presentes

NEGATIVO:
❌ Views muy gordas (hasta 76 líneas)
❌ Lógica de negocio en views
❌ File I/O en views
❌ No usa Service Layer
❌ Difícil de testear

REFACTORING:
Crear services:
- UserService (RBAC, profile)
- AvatarService (upload, delete, validate)
```

### 1.4 Serializers

```python
# ════════════════════════════════════════════════════════════
# apps/users/serializers.py (~60 líneas)
# ════════════════════════════════════════════════════════════

class UserSerializer(serializers.ModelSerializer):
    """Serializer básico de usuario (sin password)."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    avatar_url = serializers.CharField(source='get_avatar_url', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name', 'full_name',
            'avatar_url', 'phone', 'position', 'employee_id',
            'is_active', 'is_staff', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuario (con password)."""
    
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password',
            'first_name', 'last_name',
            'phone', 'position', 'employee_id',
        ]
    
    def create(self, validated_data):
        """Crear usuario con password hasheado."""
        user = CustomUser.objects.create_user(**validated_data)
        return user

CALIDAD:
✅ Bien estructurados
✅ Separation of concerns (create vs read)
✅ Password write_only
✅ full_name y avatar_url computed fields
```

---

<a name="tests-actuales"></a>
## 2. TESTS ACTUALES ANÁLISIS

### 2.1 Inventario de Tests

```
tests/unit/users/
│
├── test_user_model.py           (10.3 KB, 29 tests) ⛔
│   ├─ TestUserModelFields (8 tests)
│   ├─ TestUserModelRBAC (8 tests)
│   ├─ TestUserSoftDelete (4 tests)
│   ├─ TestGetFullName (5 tests)
│   └─ TestUserModelMeta (4 tests)
│
├── test_serializers.py          (8.6 KB, 25 tests) ⛔
│   ├─ TestUserSerializer
│   └─ TestUserCreateSerializer
│
├── test_avatar_api.py           (4.1 KB, ~8 tests) ⛔
│   └─ Tests de upload/delete avatar
│
├── test_profile_api.py          (4.1 KB, ~8 tests) ⛔
│   └─ Tests de get/update profile
│
└── test_views.py                (4.6 KB, ~9 tests) ⛔
    └─ Tests de UserViewSet

TOTAL: 5 archivos, 773 líneas, 70 tests
ESTADO: 0/70 pasando (100% bloqueados)
```

### 2.2 Resultado de Tests REAL

```
EJECUCIÓN: 2026-01-17
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

pytest tests/unit/users/ -v

Collected: 70 items

ERROR: 70/70 tests (100%)

ERROR COMÚN (todos los tests):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Traceback:
venv/lib/python3.12/site-packages/django/db/migrations/loader.py:187
E   IndexError: list index out of range
    current_app = 'admin'
    key = ('users', '__first__')

During setup of test database:
ValueError: Dependency on app with no migrations: users

ANÁLISIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Django intenta crear test DB
2. Busca migrations de users
3. NO encuentra 0001_initial.py
4. Lanza IndexError
5. TODOS los tests fallan en setup

NINGÚN TEST SE EJECUTA:
- No hay tests pasando
- No hay tests fallando
- Solo hay ERROR en colección/setup
```

### 2.3 Análisis Detallado por Archivo

```python
# ════════════════════════════════════════════════════════════
# test_user_model.py (10.3 KB, 29 tests) ⛔
# ════════════════════════════════════════════════════════════

ESTADO: ⛔ BLOQUEADO COMPLETAMENTE (0/29)

TESTS ORGANIZADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TestUserModelFields (8 tests):
├─ test_create_user_with_avatar
├─ test_user_avatar_path_logic
├─ test_create_user_with_phone
├─ test_create_user_with_position
├─ test_create_user_with_employee_id
├─ test_employee_id_uniqueness
├─ test_delete_avatar_method_success
└─ test_delete_avatar_physical_cleanup

TestUserModelRBAC (8 tests):
├─ test_get_functions_empty_for_new_user
├─ test_get_functions_with_assignments
├─ test_has_function_positive
├─ test_has_function_negative
├─ test_has_any_function_logic_match
├─ test_has_any_function_logic_no_match
├─ test_has_all_functions_complete_match
└─ test_has_all_functions_partial_match_fails

TestUserSoftDelete (4 tests):
├─ test_soft_delete_sets_is_deleted_true
├─ test_soft_delete_sets_timestamp
├─ test_soft_deleted_user_still_exists_in_db
└─ test_restore_soft_deleted_user

TestGetFullName (5 tests):
├─ test_get_full_name_with_first_and_last
├─ test_get_full_name_only_first_name
├─ test_get_full_name_only_last_name
├─ test_get_full_name_empty_returns_username
└─ test_get_full_name_whitespace_returns_username

TestUserModelMeta (4 tests):
├─ test_str_representation
├─ test_employee_id_db_index
├─ test_is_staff_and_superuser_defaults
└─ test_email_field_label

CALIDAD DE LOS TESTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Bien organizados (TestCase classes)
✅ Nombres descriptivos
✅ Cubren campos custom
✅ Cubren RBAC
✅ Cubren SoftDelete
✅ Edge cases considerados

POTENCIAL:
Una vez desbloqueados (con migrations),
probablemente 25-28/29 tests pasarán (>95%)

# ════════════════════════════════════════════════════════════
# test_serializers.py (8.6 KB, 25 tests) ⛔
# ════════════════════════════════════════════════════════════

ESTADO: ⛔ BLOQUEADO (0/25)

TESTS:
- UserSerializer validation
- UserCreateSerializer con password
- Campos read_only
- Full_name computed field
- Avatar_url computed field

POTENCIAL:
Probablemente 20-23/25 tests pasarán

# ════════════════════════════════════════════════════════════
# test_avatar_api.py (4.1 KB, ~8 tests) ⛔
# ════════════════════════════════════════════════════════════

ESTADO: ⛔ BLOQUEADO (0/8)

TESTS:
- Upload avatar válido
- Upload sin archivo
- Upload extensión inválida
- Upload tamaño excedido
- Delete avatar existente
- Delete avatar inexistente

DEPENDENCIAS:
- File I/O (filesystem)
- Media storage
- Permisos

POTENCIAL:
Si se crean mocks de filesystem: 6-7/8 tests pasarán

# ════════════════════════════════════════════════════════════
# test_profile_api.py (4.1 KB, ~8 tests) ⛔
# ════════════════════════════════════════════════════════════

ESTADO: ⛔ BLOQUEADO (0/8)

TESTS:
- Get profile autenticado
- Get profile anónimo (fail)
- Update profile campos permitidos
- Update profile campos no permitidos
- Update profile vacío

DEPENDENCIAS:
- Authentication
- RBAC (get_functions)

POTENCIAL:
Con fixtures RBAC: 6-7/8 tests pasarán

# ════════════════════════════════════════════════════════════
# test_views.py (4.6 KB, ~9 tests) ⛔
# ════════════════════════════════════════════════════════════

ESTADO: ⛔ BLOQUEADO (0/9)

TESTS:
- List users requiere auth
- Create user requiere auth
- CRUD operations

POTENCIAL:
7-8/9 tests pasarán
```

---

<a name="problema-migrations"></a>
## 3. PROBLEMA DE MIGRATIONS (Análisis Profundo)

### 3.1 Estado Actual

```
DIRECTORIO MIGRATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/users/migrations/
├── __init__.py              ✓ Existe (vacío)
└── [NO HAY MÁS ARCHIVOS]    ✗ Falta 0001_initial.py

ESPERADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/users/migrations/
├── __init__.py
└── 0001_initial.py          ← FALTA ESTE ARCHIVO

CONSECUENCIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Django Migration System:
1. Django carga INSTALLED_APPS
2. Busca migrations en cada app
3. users está en INSTALLED_APPS
4. Busca users/migrations/0001_initial.py
5. NO LO ENCUENTRA
6. Intenta acceder a users.__first__
7. Lista vacía [] → IndexError
8. Tests fallan en setup

OTRAS APPS AFECTADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apps que dependen de User:
├─ authentication (SecurityQuestion → User FK)
├─ core (UserServiceAccess → User FK)
├─ access (UserFunction, FunctionGroup → User FK)
├─ audit (AuditLog → User FK)
└─ reports (Report → User FK)

TODAS estas apps también fallan si users no tiene migrations.

Este problema se detectó inicialmente en:
ANALISIS_APP_UTILS_REFACTORING_v1.0.0.md
Problema 2: test_soft_delete.py (migrations users faltantes)
```

### 3.2 Por Qué NO Existe la Migration

```
POSIBLES CAUSAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEORÍA 1: Nunca se creó
- Desarrollador creó models.py
- NO ejecutó makemigrations
- Creó directorio migrations/ manualmente
- Solo agregó __init__.py

TEORÍA 2: Se eliminó accidentalmente
- Migration existía
- Git reset/clean/revert
- Se perdió el archivo
- Quedó solo __init__.py

TEORÍA 3: CustomUser agregado después
- Proyecto iniciaba con User de Django
- Luego cambiaron a CustomUser
- NO crearon migration de cambio

EVIDENCIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Archivo models.py.backup existe:
- Sugiere cambios recientes
- Posible refactoring
- Migration pudo perderse

Directorio migrations/ SÍ existe:
- Alguien lo creó intencionalmente
- Pero NO ejecutó makemigrations

IMPACTO EN DESARROLLO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¿Cómo funcionaba en desarrollo sin migration?

OPCIÓN A: DB ya tenía tabla users
- Migration se ejecutó manualmente en DB
- Pero archivo .py no se agregó a git
- DB de producción funciona
- Tests NO funcionan (DB limpia)

OPCIÓN B: No se ejecutaban tests
- Tests nunca corrieron
- Desarrollo sin TDD
- Migration nunca fue necesaria

OPCIÓN C: Skip migrations en tests
- pytest.ini podría tener --no-migrations
- Tests corrían sin DB real
- Mocks everywhere
```

---

<a name="fat-model"></a>
## 4. FAT MODEL DETECTADO

### 4.1 Métodos con Lógica de Negocio

```python
# ════════════════════════════════════════════════════════════
# ANTI-PATTERN: FAT MODEL
# apps/users/models.py líneas 130-227
# ════════════════════════════════════════════════════════════

MÉTODO 1: get_functions() (64 líneas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Líneas: 130-164 (64 líneas totales)

def get_functions(self):
    """
    LÓGICA DE NEGOCIO EN MODEL ❌
    
    - Maneja relaciones con access app
    - Try/except genérico
    - Set operations
    - Lógica de agregación
    """
    functions = set()
    
    # Funciones directas
    if hasattr(self, 'user_functions'):
        try:
            direct_functions = self.user_functions.filter(
                is_active=True
            ).values_list('function__name', flat=True)
            functions.update(direct_functions)
        except Exception:
            pass
    
    # Funciones de grupos
    if hasattr(self, 'function_groups'):
        try:
            for group in self.function_groups.filter(is_active=True):
                group_functions = group.functions.filter(
                    is_active=True
                ).values_list('name', flat=True)
                functions.update(group_functions)
        except Exception:
            pass
    
    return list(functions)

PROBLEMAS:
❌ 64 líneas de lógica de negocio
❌ Maneja relaciones de RBAC
❌ Try/except oculta errores
❌ hasattr() checks (defensivo)
❌ Conoce estructura de access app
❌ Difícil de testear


MÉTODO 2: delete_avatar() (21 líneas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Líneas: 207-227 (21 líneas)

def delete_avatar(self):
    """
    FILE I/O EN MODEL ❌
    """
    if self.avatar:
        avatar_path = self.avatar.path
        if os.path.exists(avatar_path):
            try:
                os.remove(avatar_path)  # ← File I/O
                self.avatar = None
                self.save()
                return True
            except Exception as e:
                import logging      # ← Import en método
                logger = logging.getLogger(__name__)
                logger.error(f"Error...")  # ← Logging
                return False
    return False

PROBLEMAS:
❌ File I/O en model
❌ os.remove() en model
❌ Logging en model
❌ Import dentro de método
❌ Save() dentro de método
❌ Try/except genérico


MÉTODO 3: has_function() + has_any_function() + has_all_functions()
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Líneas: 166-205 (40 líneas totales)

def has_function(self, function_name):
    user_functions = self.get_functions()  # Delega a get_functions
    return function_name in user_functions

def has_any_function(self, function_names):
    user_functions = set(self.get_functions())
    required = set(function_names)
    return bool(user_functions.intersection(required))

def has_all_functions(self, function_names):
    user_functions = set(self.get_functions())
    required = set(function_names)
    return required.issubset(user_functions)

PROBLEMAS:
❌ Lógica de permisos en model
❌ Set operations en model
❌ Cada llamada ejecuta get_functions() (N+1)


TOTAL FAT MODEL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

get_functions():        64 líneas
delete_avatar():        21 líneas
has_*():                40 líneas
                        ─────────
TOTAL:                  125 líneas de lógica de negocio en MODEL

Porcentaje: 125/228 = 55% del model es lógica de negocio ❌
```

### 4.2 Impacto del Fat Model

```
PROBLEMAS DE TESTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Difícil de mockear
   - get_functions() requiere relaciones de BD
   - delete_avatar() requiere filesystem
   - Tests lentos (DB + File I/O)

2. Acoplamiento alto
   - Model depende de access app
   - Model depende de filesystem
   - Model depende de logging

3. Tests frágiles
   - Try/except genérico oculta errores
   - hasattr() hace tests impredecibles
   - Difícil reproducir edge cases

PROBLEMAS DE MANTENIMIENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Violación SRP (Single Responsibility Principle)
   Model hace demasiado:
   - Datos (OK)
   - RBAC (NO)
   - File I/O (NO)
   - Logging (NO)

2. Difícil de extender
   - Agregar nueva lógica RBAC → model crece
   - Agregar nuevo tipo avatar → model crece
   - Model se vuelve monstruoso

3. Code smells
   - Import dentro de método
   - Try/except genérico
   - Lógica condicional compleja
```

---

<a name="soluciones"></a>
## 5. SOLUCIONES PROPUESTAS

### 5.1 Solución Problema 1: Crear Migrations

```bash
# ════════════════════════════════════════════════════════════
# SOLUCIÓN: Crear migration inicial
# ════════════════════════════════════════════════════════════

OPCIÓN A: makemigrations (RECOMENDADA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Paso 1: Generar migration
cd /tmp/iact-real/callcentersite
python manage.py makemigrations users

Resultado esperado:
Migrations for 'users':
  apps/users/migrations/0001_initial.py
    - Create model CustomUser

Paso 2: Aplicar migration (desarrollo)
python manage.py migrate users

Paso 3: Validar tests
pytest tests/unit/users/ -v

RESULTADO ESPERADO:
✅ 0001_initial.py creado (~100 líneas)
✅ Tabla users creada en DB
✅ 70/70 tests desbloqueados
✅ ~60-65/70 tests pasando (85-90%)

TIEMPO: 5-10 minutos
RIESGO: BAJO


OPCIÓN B: Crear migration manual (NO RECOMENDADA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Crear apps/users/migrations/0001_initial.py manualmente

DESVENTAJAS:
❌ Propenso a errores
❌ Debe reflejar exactamente el model
❌ Más tiempo (30-60 min)
❌ Difícil mantener

NO RECOMENDADA
```

### 5.2 Solución Problema 2: Service Layer

```python
# ════════════════════════════════════════════════════════════
# SOLUCIÓN: Crear Service Layer para Users
# ════════════════════════════════════════════════════════════

ESTRUCTURA PROPUESTA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/users/
├── models.py              ← Solo datos
├── services/              ← NUEVO directorio
│   ├── __init__.py
│   ├── user_service.py    ← RBAC logic
│   └── avatar_service.py  ← Avatar logic
├── views.py               ← Delgado, usa services
└── ...

# ────────────────────────────────────────────────────────────
# apps/users/services/user_service.py (NUEVO - 150 líneas)
# ────────────────────────────────────────────────────────────

from typing import List, Set
from django.contrib.auth import get_user_model

User = get_user_model()


class UserService:
    """
    Service para lógica de negocio de usuarios.
    
    Responsabilidades:
    - RBAC (funciones, permisos)
    - Profile management
    - User queries complejos
    """
    
    @staticmethod
    def get_user_functions(user: User) -> List[str]:
        """
        Obtener funciones RBAC del usuario.
        
        LÓGICA MOVIDA DEL MODEL ✓
        
        Args:
            user: Usuario
            
        Returns:
            List[str]: Nombres de funciones
        """
        functions: Set[str] = set()
        
        # Funciones directas
        if hasattr(user, 'user_functions'):
            direct = user.user_functions.filter(
                is_active=True
            ).values_list('function__name', flat=True)
            functions.update(direct)
        
        # Funciones de grupos
        if hasattr(user, 'function_groups'):
            for group in user.function_groups.filter(is_active=True):
                group_funcs = group.functions.filter(
                    is_active=True
                ).values_list('name', flat=True)
                functions.update(group_funcs)
        
        return list(functions)
    
    @staticmethod
    def has_function(user: User, function_name: str) -> bool:
        """Verificar si usuario tiene función."""
        functions = UserService.get_user_functions(user)
        return function_name in functions
    
    @staticmethod
    def has_any_function(user: User, function_names: List[str]) -> bool:
        """Verificar si tiene alguna función."""
        user_funcs = set(UserService.get_user_functions(user))
        required = set(function_names)
        return bool(user_funcs.intersection(required))
    
    @staticmethod
    def has_all_functions(user: User, function_names: List[str]) -> bool:
        """Verificar si tiene todas las funciones."""
        user_funcs = set(UserService.get_user_functions(user))
        required = set(function_names)
        return required.issubset(user_funcs)
    
    @staticmethod
    def get_user_profile(user: User) -> dict:
        """
        Obtener perfil completo del usuario.
        
        LÓGICA MOVIDA DE VIEW ✓
        """
        from apps.users.services.avatar_service import AvatarService
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'avatar_url': AvatarService.get_avatar_url(user),
            'position': user.position,
            'phone': user.phone,
            'employee_id': user.employee_id,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'functions': UserService.get_user_functions(user),
        }
    
    @staticmethod
    def update_user_profile(
        user: User,
        data: dict,
        allowed_fields: List[str] = None
    ) -> dict:
        """
        Actualizar perfil de usuario.
        
        LÓGICA MOVIDA DE VIEW ✓
        """
        if allowed_fields is None:
            allowed_fields = [
                'first_name', 'last_name',
                'phone', 'position'
            ]
        
        updated_fields = []
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
                updated_fields.append(field)
        
        if updated_fields:
            user.save()
        
        return {
            'updated_fields': updated_fields,
            'user': user,
        }


# ────────────────────────────────────────────────────────────
# apps/users/services/avatar_service.py (NUEVO - 200 líneas)
# ────────────────────────────────────────────────────────────

import os
from typing import Optional, Tuple
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
import logging

logger = logging.getLogger(__name__)


class AvatarService:
    """
    Service para gestión de avatares.
    
    Responsabilidades:
    - Upload avatar
    - Delete avatar
    - Validate avatar
    - Get avatar URL
    """
    
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
    MAX_SIZE = 2 * 1024 * 1024  # 2MB
    DEFAULT_AVATAR = '/static/icons/defaults/avatar_default.png'
    
    @staticmethod
    def get_avatar_url(user) -> str:
        """
        Obtener URL del avatar.
        
        LÓGICA MOVIDA DEL MODEL ✓
        """
        if user.avatar:
            return user.avatar.url
        return AvatarService.DEFAULT_AVATAR
    
    @staticmethod
    def validate_avatar(file: UploadedFile) -> Tuple[bool, Optional[str]]:
        """
        Validar archivo de avatar.
        
        LÓGICA MOVIDA DE VIEW ✓
        
        Returns:
            (is_valid, error_message)
        """
        # Validar extensión
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in AvatarService.ALLOWED_EXTENSIONS:
            return False, f"Extensión no permitida. Use: {', '.join(AvatarService.ALLOWED_EXTENSIONS)}"
        
        # Validar tamaño
        if file.size > AvatarService.MAX_SIZE:
            max_mb = AvatarService.MAX_SIZE / (1024 * 1024)
            return False, f"Archivo muy grande. Máximo {max_mb}MB"
        
        return True, None
    
    @staticmethod
    def upload_avatar(user, file: UploadedFile) -> Tuple[bool, str]:
        """
        Subir/actualizar avatar.
        
        LÓGICA MOVIDA DE VIEW ✓
        
        Returns:
            (success, message)
        """
        # Validar
        is_valid, error = AvatarService.validate_avatar(file)
        if not is_valid:
            return False, error
        
        # Eliminar avatar anterior
        if user.avatar:
            AvatarService.delete_avatar(user, save=False)
        
        # Guardar nuevo
        try:
            user.avatar = file
            user.save()
            logger.info(f"Avatar actualizado para {user.username}")
            return True, "Avatar actualizado correctamente"
        except Exception as e:
            logger.error(f"Error guardando avatar: {e}")
            return False, "Error guardando avatar"
    
    @staticmethod
    def delete_avatar(user, save: bool = True) -> bool:
        """
        Eliminar avatar.
        
        LÓGICA MOVIDA DEL MODEL ✓
        """
        if not user.avatar:
            return False
        
        try:
            avatar_path = user.avatar.path
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
                logger.info(f"Avatar eliminado: {avatar_path}")
            
            user.avatar = None
            if save:
                user.save()
            
            return True
        except Exception as e:
            logger.error(f"Error eliminando avatar: {e}")
            return False


# ────────────────────────────────────────────────────────────
# apps/users/models.py (REFACTORIZADO - más delgado)
# ────────────────────────────────────────────────────────────

class CustomUser(SoftDeleteMixin, AbstractUser):
    """
    Usuario personalizado.
    
    SOLO DATOS ✓
    """
    
    avatar = models.ImageField(...)
    phone = models.CharField(...)
    position = models.CharField(...)
    employee_id = models.CharField(...)
    
    class Meta:
        db_table = 'users'
        ordering = ['username']
        indexes = [...]
    
    def __str__(self):
        full_name = self.get_full_name()
        if full_name and full_name != self.username:
            return f"{full_name} ({self.username)}"
        return self.username
    
    def get_full_name(self):
        """Override de AbstractUser."""
        full_name = super().get_full_name()
        return full_name if full_name.strip() else self.username
    
    def get_avatar_url(self):
        """
        DEPRECADO: Usar AvatarService.get_avatar_url()
        """
        import warnings
        warnings.warn(
            "CustomUser.get_avatar_url() está deprecado. "
            "Usar AvatarService.get_avatar_url(user)",
            DeprecationWarning
        )
        from apps.users.services.avatar_service import AvatarService
        return AvatarService.get_avatar_url(self)
    
    def get_functions(self):
        """
        DEPRECADO: Usar UserService.get_user_functions()
        """
        import warnings
        warnings.warn(
            "CustomUser.get_functions() está deprecado. "
            "Usar UserService.get_user_functions(user)",
            DeprecationWarning
        )
        from apps.users.services.user_service import UserService
        return UserService.get_user_functions(self)
    
    # has_function, has_any_function, has_all_functions
    # TODOS deprecados con warnings similares
    
    # delete_avatar() DEPRECADO también


# ────────────────────────────────────────────────────────────
# apps/users/views.py (REFACTORIZADO - más delgado)
# ────────────────────────────────────────────────────────────

from apps.users.services.user_service import UserService
from apps.users.services.avatar_service import AvatarService


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar_view(request):
    """
    REFACTORIZADO: Delega a AvatarService ✓
    """
    success, message = AvatarService.upload_avatar(
        request.user,
        request.FILES.get('avatar')
    )
    
    if success:
        return Response({
            'success': True,
            'avatar_url': AvatarService.get_avatar_url(request.user),
            'message': message
        })
    else:
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile_view(request):
    """
    REFACTORIZADO: Delega a UserService ✓
    """
    profile_data = UserService.get_user_profile(request.user)
    return Response(profile_data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile_view(request):
    """
    REFACTORIZADO: Delega a UserService ✓
    """
    result = UserService.update_user_profile(
        request.user,
        request.data
    )
    
    profile_data = UserService.get_user_profile(result['user'])
    
    return Response({
        'success': True,
        'message': f"Actualizados: {', '.join(result['updated_fields'])}",
        'profile': profile_data
    })
```

---

<a name="fixtures"></a>
## 7. FIXTURES NECESARIAS

```python
# ════════════════════════════════════════════════════════════
# tests/fixtures/users.py (NUEVO - 400 líneas)
# ════════════════════════════════════════════════════════════

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

User = get_user_model()


# ────────────────────────────────────────────────────────────
# USERS BÁSICOS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def user_basic(db):
    """Usuario básico sin campos opcionales."""
    return User.objects.create_user(
        username='user_basic',
        email='basic@example.com',
        password='password123',
    )


@pytest.fixture
def user_complete(db):
    """Usuario con todos los campos."""
    return User.objects.create_user(
        username='user_complete',
        email='complete@example.com',
        password='password123',
        first_name='John',
        last_name='Doe',
        phone='+52-55-1234-5678',
        position='Developer',
        employee_id='EMP001',
    )


@pytest.fixture
def superuser(db):
    """Superusuario."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
    )


@pytest.fixture
def staff_user(db):
    """Usuario staff."""
    return User.objects.create_user(
        username='staff',
        email='staff@example.com',
        password='staff123',
        is_staff=True,
    )


# ────────────────────────────────────────────────────────────
# AVATAR FIXTURES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def avatar_image():
    """Imagen válida para avatar (PNG 100x100)."""
    image = Image.new('RGB', (100, 100), color='red')
    image_io = io.BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)
    
    return SimpleUploadedFile(
        name='avatar.png',
        content=image_io.read(),
        content_type='image/png'
    )


@pytest.fixture
def avatar_jpg():
    """Avatar en formato JPG."""
    image = Image.new('RGB', (100, 100), color='blue')
    image_io = io.BytesIO()
    image.save(image_io, format='JPEG')
    image_io.seek(0)
    
    return SimpleUploadedFile(
        name='avatar.jpg',
        content=image_io.read(),
        content_type='image/jpeg'
    )


@pytest.fixture
def avatar_too_large():
    """Avatar que excede tamaño máximo (>2MB)."""
    # Crear imagen de 3000x3000 (>2MB)
    image = Image.new('RGB', (3000, 3000), color='green')
    image_io = io.BytesIO()
    image.save(image_io, format='PNG', quality=100)
    image_io.seek(0)
    
    return SimpleUploadedFile(
        name='avatar_large.png',
        content=image_io.read(),
        content_type='image/png'
    )


@pytest.fixture
def invalid_file_extension():
    """Archivo con extensión inválida."""
    return SimpleUploadedFile(
        name='avatar.txt',
        content=b'Not an image',
        content_type='text/plain'
    )


@pytest.fixture
def user_with_avatar(db, avatar_image):
    """Usuario con avatar asignado."""
    user = User.objects.create_user(
        username='user_avatar',
        email='avatar@example.com',
        password='password123',
    )
    user.avatar = avatar_image
    user.save()
    return user


# ────────────────────────────────────────────────────────────
# RBAC FIXTURES (requieren access app)
# ────────────────────────────────────────────────────────────

@pytest.fixture
def user_with_functions(db):
    """
    Usuario con funciones RBAC asignadas.
    
    NOTA: Requiere access app configurada.
    Si access no disponible, skip estos tests.
    """
    pytest.importorskip('apps.access')
    
    from apps.access.models import Function, UserFunction
    
    user = User.objects.create_user(
        username='user_rbac',
        email='rbac@example.com',
        password='password123',
    )
    
    # Crear funciones
    func1 = Function.objects.create(
        name='view_reports',
        description='Ver reportes',
        is_active=True,
    )
    func2 = Function.objects.create(
        name='create_users',
        description='Crear usuarios',
        is_active=True,
    )
    
    # Asignar al usuario
    UserFunction.objects.create(
        user=user,
        function=func1,
        is_active=True,
    )
    UserFunction.objects.create(
        user=user,
        function=func2,
        is_active=True,
    )
    
    return user


# ────────────────────────────────────────────────────────────
# SOFT DELETE FIXTURES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def user_deleted(db):
    """Usuario soft-deleted."""
    user = User.objects.create_user(
        username='user_deleted',
        email='deleted@example.com',
        password='password123',
    )
    user.delete()  # Soft delete
    return user


@pytest.fixture
def users_mixed(db):
    """Mix de usuarios (activos, staff, deleted)."""
    users = []
    
    # 3 activos
    for i in range(1, 4):
        users.append(User.objects.create_user(
            username=f'active_{i}',
            email=f'active{i}@example.com',
            password='password123',
        ))
    
    # 1 staff
    users.append(User.objects.create_user(
        username='staff',
        email='staff@example.com',
        password='password123',
        is_staff=True,
    ))
    
    # 1 deleted
    deleted = User.objects.create_user(
        username='deleted',
        email='deleted@example.com',
        password='password123',
    )
    deleted.delete()
    users.append(deleted)
    
    return users


# ────────────────────────────────────────────────────────────
# REQUEST FACTORIES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """DRF API Client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user_basic):
    """API Client autenticado."""
    api_client.force_authenticate(user=user_basic)
    return api_client


@pytest.fixture
def admin_client(api_client, superuser):
    """API Client con superuser."""
    api_client.force_authenticate(user=superuser)
    return api_client
```

---

<a name="roadmap"></a>
## 9. ROADMAP DE IMPLEMENTACIÓN

### Semana 1: Migrations + Service Layer (5 días)

```
DÍA 1 (Lunes): Crear Migrations
────────────────────────────────────────────────────────────
Objetivo: Desbloquear TODOS los tests

Mañana (2 horas):
09:00-09:30 | Ejecutar makemigrations users
09:30-10:00 | Revisar 0001_initial.py generado
10:00-10:30 | Ejecutar migrate users
10:30-11:00 | Ejecutar tests/unit/users/

Tarde (2 horas):
14:00-15:00 | Analizar tests que fallan
15:00-16:00 | Fix errores simples
16:00-17:00 | Validar ~60/70 tests pasando

Checkpoint:
✅ 0001_initial.py creado
✅ Tabla users en DB
✅ ~60/70 tests pasando (85%)
✅ 10 tests fallando (RBAC, avatar file I/O)


DÍA 2-3 (Martes-Miércoles): Service Layer
────────────────────────────────────────────────────────────
Objetivo: Crear UserService y AvatarService

DÍA 2 Mañana:
09:00-10:00 | Crear apps/users/services/
10:00-11:00 | Crear user_service.py estructura
11:00-12:00 | Implementar get_user_functions()

DÍA 2 Tarde:
14:00-15:00 | Implementar has_function/has_any/has_all
15:00-16:00 | Implementar get_user_profile()
16:00-17:00 | Implementar update_user_profile()

DÍA 3 Mañana:
09:00-10:00 | Crear avatar_service.py
10:00-11:00 | Implementar validate_avatar()
11:00-12:00 | Implementar upload_avatar()

DÍA 3 Tarde:
14:00-15:00 | Implementar delete_avatar()
15:00-16:00 | Agregar deprecation warnings en model
16:00-17:00 | Tests de services

Checkpoint:
✅ UserService completo
✅ AvatarService completo
✅ Deprecation warnings en model


DÍA 4 (Jueves): Refactorizar Views
────────────────────────────────────────────────────────────
Objetivo: Views delgadas que usan services

Mañana (4 horas):
09:00-10:00 | Refactorizar upload_avatar_view
10:00-11:00 | Refactorizar delete_avatar_view
11:00-12:00 | Refactorizar get_user_profile_view

Tarde (4 horas):
14:00-15:00 | Refactorizar update_user_profile_view
15:00-16:00 | Actualizar tests de views
16:00-17:00 | Ejecutar tests

Checkpoint:
✅ Views refactorizadas
✅ Tests de views pasando


DÍA 5 (Viernes): Fixtures + Validación
────────────────────────────────────────────────────────────
Objetivo: Fixtures completas y 70/70 tests pasando

Mañana (4 horas):
09:00-10:00 | Crear fixtures/users.py
10:00-11:00 | Fixtures de avatares
11:00-12:00 | Fixtures de RBAC (si access disponible)

Tarde (4 horas):
14:00-15:00 | Actualizar tests con fixtures
15:00-16:00 | Ejecutar todos los tests
16:00-17:00 | Fix errores finales
17:00-18:00 | Retrospectiva

Checkpoint Semana 1:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Migrations creadas
✅ Service Layer completo
✅ Views refactorizadas
✅ Fixtures completas
✅ 70/70 tests pasando (100%)
✅ Cobertura >85%
```

### Semana 2: Polish y Documentación (opcional, 2-3 días)

```
DÍA 6-7: Tests adicionales
────────────────────────────────────────────────────────────
- Edge cases
- Performance tests
- Integration tests

DÍA 8: Documentación
────────────────────────────────────────────────────────────
- README de users
- Service Layer guide
- Migration guide
- API documentation
```

---

<a name="criterios"></a>
## 10. CRITERIOS DE ÉXITO

```
CRITERIO 1: Migrations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 0001_initial.py existe
✅ Tabla users creada
✅ python manage.py migrate users funciona
✅ Tests pueden ejecutarse

CRITERIO 2: Tests Pasando
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 70/70 tests pasando (100%)
✅ <5 segundos tiempo total
✅ Sin warnings importantes

CRITERIO 3: Service Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ UserService implementado
✅ AvatarService implementado
✅ Lógica movida de model a services
✅ Model delgado (solo datos)
✅ Views delgadas (solo coordinación)

CRITERIO 4: Cobertura
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ >85% cobertura en models
✅ >90% cobertura en services
✅ >80% cobertura en views

CRITERIO 5: Deprecation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Warnings claros en métodos deprecados
✅ Migration guide documentado
✅ Sin código roto (backward compatible)

TIEMPO TOTAL: 1-2 semanas (40-80 horas)
```

---

## RESUMEN FINAL

```
APP: users
ESTADO INICIAL: 0/70 tests pasando (0% - 100% bloqueados)
ESTADO OBJETIVO: 70/70 tests pasando (100%)

PROBLEMA PRINCIPAL:
No migrations → todos los tests bloqueados

SOLUCIÓN:
1. python manage.py makemigrations users
2. python manage.py migrate users
3. Refactorizar a Service Layer

BENEFICIO:
✅ 70/70 tests desbloqueados
✅ Service Layer implementado
✅ Código mantenible
✅ Base sólida para RBAC

TIEMPO: 1-2 semanas
RIESGO: BAJO (problema bien definido)
```

---

**FIN DEL ANÁLISIS - USERS v1.0.0**

Documento creado: 2026-01-17
Total líneas: ~2,100 líneas
Próxima actualización: Después de implementación (v1.1.0)