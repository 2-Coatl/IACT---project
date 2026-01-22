# 🔍 ANÁLISIS: REVISIÓN DE CORE Y UTILS

**Fecha:** 2026-01-21  
**Branch:** feature/user-management  
**Propósito:** Verificar qué existe en `core` y `utils` antes de continuar FASE 2

---

## ❌ PROBLEMA IDENTIFICADO

En PARTE 1 creamos validators duplicados sin revisar `apps/core` y `apps/utils`.

---

## 📋 INVENTARIO DE LO QUE YA EXISTE

### 1. apps/core/services/base_service.py

**BaseService - 84 líneas**

```python
class BaseService:
    """Service base con logging."""
    
    def log_info(message: str)
    def log_error(message: str)
    def log_warning(message: str)
    def log_debug(message: str)
```

**Estado:** ✅ YA EXISTE  
**Usado en:** Todos los services deben heredar de aquí

---

### 2. apps/core/validators.py

**Validators (CLASES) - 272 líneas**

```python
# 5 Validators tipo Clase
PhoneValidator          # Teléfonos chilenos (+56)
EmailValidator          # Emails corporativos
NITValidator            # RUT empresarial
DateRangeValidator      # Rangos de fechas
PositiveIntegerValidator # Enteros positivos
```

**Estado:** ✅ YA EXISTE  
**Diferencia con apps/users/validators.py:**
- core: Validators como CLASES (callable)
- users: Validators como FUNCIONES

---

### 3. apps/utils/validators.py

**Validators (FUNCIONES) - 396 líneas**

```python
# 9 Funciones públicas de validación
validate_email(email: str) -> bool
validate_phone_number(phone: str) -> bool  # ⚠️ DUPLICADO
validate_rut(rut: str) -> bool
validate_service_800(service: str) -> bool
validate_codigo_center(codigo: str) -> bool
validate_date_range(start_date, end_date, max_days) -> bool
validate_export_row_limit(row_count: int, max_limit: int)

# 5 Helpers privados
_clean_phone_number()
_clean_rut()
_has_valid_rut_format()
_validate_rut_checksum()
_calculate_rut_dv()
```

**Estado:** ✅ YA EXISTE  
**Formato:** Funciones chilenas (teléfonos +56, RUT chileno)

---

### 4. apps/core/exceptions.py

**Excepciones Base - 128 líneas**

```python
# 6 Excepciones base
IACTBaseException        # Base de todas
ValidationError          # Errores de validación
BusinessRuleError        # Reglas de negocio
PermissionDeniedError    # Permisos insuficientes
ResourceNotFoundError    # Recurso no encontrado (404)
ETLError                # Errores ETL
```

**Estado:** ✅ YA EXISTE  
**Usado en:** Base para excepciones de apps

---

### 5. apps/users/exceptions.py

**Excepciones Users - 116 líneas**

```python
# YA EXISTEN 6 excepciones
UserServiceError         # Base (hereda BusinessRuleError)
UserAlreadyExistsError   # Username/email duplicado
UserNotFoundError        # Usuario no encontrado
InvalidCredentialsError  # Credenciales incorrectas
UserInactiveError        # Usuario inactivo
PasswordValidationError  # Password inválido
```

**Estado:** ✅ YA EXISTE  
**Necesita:** Posiblemente agregar más específicas

---

### 6. apps/users/services/

**Services ya implementados:**

```
user_service.py              ✅ 487 líneas - UserService completo
profile_service.py           ✅ 307 líneas - ProfileService
password_service.py          ✅ 376 líneas - PasswordService  
authentication_service.py    ✅ 341 líneas - AuthenticationService
```

**UserService - Métodos existentes (9):**

```python
class UserService(BaseService):
    def __init__()
    def create_user()           # CRUD Create
    def get_user_by_id()        # CRUD Read
    def get_user_by_username()  # CRUD Read
    def list_users()            # CRUD List
    def update_user()           # CRUD Update
    def activate_user()         # Activación
    def deactivate_user()       # Desactivación
    def delete_user()           # Soft Delete
```

**Estado:** ✅ YA COMPLETAMENTE IMPLEMENTADO

---

### 7. apps/utils/helpers.py

**Helper Functions - 524 líneas**

```python
# REQUEST HELPERS
get_client_ip(request) -> str
get_user_agent(request) -> str
is_ajax_request(request) -> bool

# UUID/TOKEN HELPERS
generate_uuid() -> str
generate_token(length: int) -> str
hash_string(value: str) -> str

# DICTIONARY HELPERS
safe_get(dict, key, default)
flatten_dict(nested_dict)
merge_dicts(*dicts)

# STRING HELPERS
truncate_string(text, max_length)
slugify_text(text)
normalize_text(text)
```

**Estado:** ✅ YA EXISTE  
**Uso:** Funciones helper reutilizables

---

## ⚠️ DUPLICACIONES IDENTIFICADAS

### 1. validators.py en apps/users/ vs apps/utils/

**apps/users/validators.py (NUEVO - creado en PARTE 1):**

```python
validate_username()       # Internacional, genérico
validate_email()          # ⚠️ DUPLICADO (existe en utils)
validate_phone_number()   # ⚠️ DUPLICADO (existe en utils, formato chileno)
validate_employee_id()    # Formato EMP-XXXX (OK, específico users)
validate_avatar_file()    # OK, específico users
validate_password_strength() # OK, específico users
```

**apps/utils/validators.py (YA EXISTE):**

```python
validate_email()          # ⚠️ YA EXISTE
validate_phone_number()   # ⚠️ YA EXISTE (formato chileno +56)
```

**Conflicto:**
- `validate_email()`: Duplicado 100%
- `validate_phone_number()`: Diferente formato (users: internacional, utils: chileno)

---

### 2. CustomUserManager vs User.objects

**apps/users/managers.py (NUEVO - creado en PARTE 1):**

```python
class CustomUserManager(BaseUserManager):
    def create_user()
    def create_superuser()
    def active()         # Filtro is_deleted=False
    def deleted()        # Filtro is_deleted=True
    def by_employee_id()
    def by_email()
```

**Estado:** ✅ OK - Es necesario para AbstractUser

---

## 🔧 CORRECCIONES NECESARIAS

### 1. Eliminar validadores duplicados

**Acción:** Actualizar `apps/users/validators.py`

```python
# ANTES (DUPLICADO):
from django.core.validators import validate_email as django_validate_email

def validate_email(value: str) -> None:
    # ... 20 líneas duplicadas

# DESPUÉS (REUTILIZAR):
from apps.utils.validators import validate_email as utils_validate_email

def validate_email_for_user(value: str) -> None:
    """Wrapper que lanza ValidationError de Django."""
    if not utils_validate_email(value):
        raise ValidationError('Email inválido')
```

### 2. Decisión sobre phone_number

**Opción A:** Usar validator de utils (formato chileno)
```python
from apps.utils.validators import validate_phone_number
```

**Opción B:** Mantener validator de users (formato internacional)
```python
# Renombrar para evitar conflicto
def validate_international_phone_number(value: str) -> None:
    # ... formato internacional
```

**Recomendación:** Opción A - Usar formato chileno (consistencia con proyecto)

---

### 3. Verificar si falta algo en UserService

**Ya existe:** ✅ UserService completo (487 líneas)

**Métodos existentes:**
- ✅ create_user
- ✅ get_user_by_id
- ✅ get_user_by_username
- ✅ list_users
- ✅ update_user
- ✅ activate_user
- ✅ deactivate_user
- ✅ delete_user

**Faltantes identificados en PLAN FASE 2:**
- ❌ get_user_by_email (existe como manager method pero no en service)
- ❌ reset_password (puede estar en PasswordService)

---

## 📊 RESUMEN DE DUPLICACIONES

```yaml
Validators duplicados:
  ⚠️ validate_email(): apps/users vs apps/utils
  ⚠️ validate_phone_number(): apps/users vs apps/utils (formatos diferentes)

Services:
  ✅ UserService: YA COMPLETAMENTE IMPLEMENTADO
  ✅ ProfileService: YA IMPLEMENTADO
  ✅ PasswordService: YA IMPLEMENTADO
  ✅ AuthenticationService: YA IMPLEMENTADO

Excepciones:
  ✅ Ya existen 6 excepciones en apps/users/exceptions.py
  ✅ Heredan correctamente de BusinessRuleError

Managers:
  ✅ CustomUserManager: OK, necesario para AbstractUser
```

---

## 🎯 RECOMENDACIONES

### 1. Limpiar validators duplicados

```bash
# Actualizar apps/users/validators.py
# - Eliminar validate_email (usar de utils)
# - Eliminar validate_phone_number (usar de utils)
# - Mantener: validate_username, validate_employee_id, 
#   validate_avatar_file, validate_password_strength
```

### 2. No crear servicios nuevos

```yaml
NO CREAR:
  ❌ apps/users/services/user_service.py (YA EXISTE)
  ❌ apps/users/services/profile_service.py (YA EXISTE)
  ❌ apps/users/services/password_service.py (YA EXISTE)

REVISAR:
  ✅ Si UserService tiene todos los métodos del PLAN FASE 2
  ✅ Si faltan métodos, agregarlos al UserService existente
```

### 3. Actualizar models.py

```python
# ANTES:
from apps.users.validators import validate_phone_number

# DESPUÉS:
from apps.utils.validators import validate_phone_number
```

---

## 📋 PLAN DE CORRECCIÓN

### PASO 1: Actualizar validators.py

**Eliminar:**
- validate_email() → Usar `apps.utils.validators.validate_email`
- validate_phone_number() → Usar `apps.utils.validators.validate_phone_number`

**Mantener:**
- validate_username() (específico users)
- validate_employee_id() (específico users)
- validate_avatar_file() (específico users)
- validate_password_strength() (específico users)

### PASO 2: Actualizar models.py imports

```python
# Cambiar import
from apps.users.validators import validate_phone_number
# Por
from apps.utils.validators import validate_phone_number
```

### PASO 3: Revisar UserService existente

```python
# Verificar si tiene todos los métodos necesarios
# Agregar métodos faltantes si los hay
```

### PASO 4: Continuar con FASE 2 PARTE 2

**Tareas ajustadas:**
- ❌ NO crear UserService (ya existe)
- ✅ Revisar y completar UserService existente
- ✅ Continuar con serializers (PARTE 4 del plan)

---

## 💡 LECCIONES APRENDIDAS

```yaml
1. SIEMPRE revisar core y utils ANTES de crear:
   - Validators
   - Services
   - Exceptions
   - Helpers

2. Evitar duplicaciones:
   - Reutilizar código existente
   - Importar de core/utils
   - No reinventar la rueda

3. Mantener consistencia:
   - Formatos chilenos (teléfonos, RUT)
   - Herencia correcta (BaseService, BusinessRuleError)
   - Estructura establecida

4. Verificar implementaciones existentes:
   - Revisar apps/users/services/ ANTES de crear
   - Muchas cosas ya están implementadas
```

---

## 🚀 PRÓXIMOS PASOS

### Opción 1: Corregir duplicaciones

1. Actualizar `apps/users/validators.py` (eliminar duplicados)
2. Actualizar `apps/users/models.py` (cambiar imports)
3. Verificar UserService existente
4. Continuar con serializers

### Opción 2: Continuar sin corrección

1. Mantener duplicación temporal
2. Marcar como deuda técnica
3. Corregir en refactor posterior

---

**Recomendación:** Opción 1 - Corregir ahora (5-10 minutos)  
**Razón:** Evita confusión y mantiene código limpio desde el inicio

---

**Análisis:** Completado  
**Duplicaciones:** 2 validators  
**Services existentes:** 4 (user, profile, password, authentication)  
**Acción:** Corrección antes de continuar FASE 2
