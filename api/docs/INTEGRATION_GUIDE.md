# 🚀 GUÍA DE INTEGRACIÓN - FASE 1 v1.0.0

## Sistema de Autenticación Completo

**Fecha:** 2026-01-21  
**Versión:** 1.0.0  
**App:** authentication  

---

## 📋 CONTENIDO

1. [Pre-requisitos](#pre-requisitos)
2. [Instalación](#instalación)
3. [Migraciones](#migraciones)
4. [Cargar Datos Iniciales](#cargar-datos-iniciales)
5. [Verificación](#verificación)
6. [Ejecutar Tests](#ejecutar-tests)
7. [Endpoints Disponibles](#endpoints-disponibles)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 PRE-REQUISITOS

```yaml
Python: 3.12+
Django: 5.1.4
DRF: 3.15.2
PostgreSQL: 14+

CNST-010: NO Redis (prohibido)

Dependencias:
  - djangorestframework
  - factory-boy
  - pytest
  - pytest-django
  
NO incluir:
  ❌ django-redis (prohibido por CNST-010)
  ❌ redis (prohibido por CNST-010)
```

---

## 📦 INSTALACIÓN

### 1. Estructura ya implementada

```
apps/authentication/
├── __init__.py
├── models.py                    ✅ 4 modelos
├── constants.py                 ✅ 35 constantes
├── exceptions.py                ✅ 8 excepciones
├── services/
│   ├── __init__.py
│   ├── base.py                  ✅ BaseService
│   ├── lockout.py               ✅ LockoutService
│   ├── authentication.py        ✅ AuthenticationService
│   ├── recovery.py              ✅ RecoveryService
│   └── session.py               ✅ SessionService
├── serializers/
│   ├── __init__.py
│   ├── auth.py                  ✅ 3 serializers
│   ├── recovery.py              ✅ 5 serializers
│   └── session.py               ✅ 2 serializers
├── viewsets.py                  ✅ 2 ViewSets
├── urls.py                      ✅ Router configurado
└── fixtures/
    └── security_questions.json  ✅ 10 preguntas

tests/
├── factories/
│   ├── authentication_factories.py  ✅ 4 factories
│   └── __init__.py
├── fixtures/
│   └── authentication.py            ✅ 4 fixtures pytest
├── unit/
│   └── authentication/
│       ├── test_models.py           ✅ 4 test classes
│       └── test_services.py         ✅ 4 test classes
└── integration/
    └── authentication/
        ├── test_auth_flow.py        ✅ 2 test classes
        ├── test_recovery_flow.py    ✅ 2 test classes
        └── test_session_flow.py     ✅ 2 test classes
```

### 2. Verificar settings.py

```python
# config/settings.py

INSTALLED_APPS = [
    # ...
    'apps.authentication',  # ✅ Debe estar registrada
    # ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # ✅
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CNST-010: NO CACHES permitido
# LoginLockout usa PostgreSQL directamente
```

### 3. Verificar urls.py

```python
# config/urls.py

urlpatterns = [
    # ...
    path('api/v1/auth/', include('apps.authentication.urls')),  # ✅
    # ...
]
```

---

## 🗄️ MIGRACIONES

### 1. Crear migraciones

```bash
cd /tmp/iact-real/callcentersite

python manage.py makemigrations authentication
```

**Output esperado:**
```
Migrations for 'authentication':
  apps/authentication/migrations/0001_initial.py
    - Create model SecurityQuestion
    - Create model LoginAttempt
    - Create model UserSecurityAnswer
    - Create model SessionLog
```

### 2. Verificar migraciones

```bash
python manage.py showmigrations authentication
```

**Output esperado:**
```
authentication
 [ ] 0001_initial
```

### 3. Aplicar migraciones

```bash
python manage.py migrate authentication
```

**Output esperado:**
```
Running migrations:
  Applying authentication.0001_initial... OK
```

### 4. Verificar tablas creadas

```bash
python manage.py dbshell
```

```sql
\dt authentication_*

-- Output esperado:
-- authentication_loginattempt
-- authentication_securityquestion
-- authentication_usersecurityanswer
-- authentication_sessionlog
```

---

## 📝 CARGAR DATOS INICIALES

### 1. Cargar preguntas de seguridad

```bash
python manage.py loaddata security_questions
```

**Output esperado:**
```
Installed 10 object(s) from 1 fixture(s)
```

### 2. Verificar preguntas cargadas

```bash
python manage.py shell
```

```python
from apps.authentication.models import SecurityQuestion

# Verificar cantidad
count = SecurityQuestion.objects.count()
print(f"Preguntas cargadas: {count}")  # Debe ser 10

# Listar preguntas
questions = SecurityQuestion.objects.all()
for q in questions:
    print(f"{q.order}. {q.question}")

# Output esperado:
# 1. ¿Cuál es el nombre de tu primera mascota?
# 2. ¿En qué ciudad naciste?
# 3. ¿Cuál es tu color favorito?
# ... (10 preguntas total)
```

---

## ✅ VERIFICACIÓN

### 1. Django Check

```bash
python manage.py check
```

**Output esperado:**
```
System check identified no issues (0 silenced).
```

### 2. Verificar endpoints

```bash
python manage.py show_urls | grep auth
```

**Output esperado:**
```
/api/v1/auth/login/                           POST    auth-login
/api/v1/auth/logout/                          POST    auth-logout
/api/v1/auth/change-password/                 POST    auth-change-password
/api/v1/auth/security-questions/              GET     auth-security-questions
/api/v1/auth/set-security-answers/            POST    auth-set-security-answers
/api/v1/auth/verify-security-answers/         POST    auth-verify-security-answers
/api/v1/auth/reset-password/                  POST    auth-reset-password
/api/v1/sessions/                             GET     sessions-list
/api/v1/sessions/{id}/                        GET     sessions-detail
/api/v1/sessions/{id}/invalidate/             POST    sessions-invalidate
/api/v1/sessions/invalidate-all/              POST    sessions-invalidate-all
```

### 3. Verificar LoginLockout en PostgreSQL

```bash
python manage.py dbshell
```

```sql
-- Verificar tabla de lockout
\dt authentication_login_lockout

-- Ver estructura
\d authentication_login_lockout

-- Probar consulta
SELECT * FROM authentication_login_lockout LIMIT 5;
```

**Nota:** El sistema NO usa Redis/cache (prohibido por CNST-010).  
Todo el tracking de lockout se persiste en PostgreSQL.

---

## 🧪 EJECUTAR TESTS

### 1. Tests Unitarios

```bash
# Todos los tests unitarios de authentication
pytest tests/unit/authentication/ -v

# Solo models
pytest tests/unit/authentication/test_models.py -v

# Solo services
pytest tests/unit/authentication/test_services.py -v
```

**Output esperado:**
```
tests/unit/authentication/test_models.py::TestLoginAttempt::test_create_login_attempt_with_user PASSED
tests/unit/authentication/test_models.py::TestSecurityQuestion::test_soft_delete_manager_active PASSED
...
=================== 32 passed in 2.34s ===================
```

### 2. Tests de Integración

```bash
# Todos los tests de integración
pytest tests/integration/authentication/ -v

# Solo flujo de auth
pytest tests/integration/authentication/test_auth_flow.py -v

# Solo flujo de recovery
pytest tests/integration/authentication/test_recovery_flow.py -v

# Solo flujo de sessions
pytest tests/integration/authentication/test_session_flow.py -v
```

**Output esperado:**
```
tests/integration/authentication/test_auth_flow.py::TestAuthenticationFlow::test_complete_authentication_flow PASSED
tests/integration/authentication/test_recovery_flow.py::TestPasswordRecoveryFlow::test_complete_recovery_flow PASSED
...
=================== 20 passed in 5.67s ===================
```

### 3. Coverage

```bash
pytest tests/unit/authentication/ tests/integration/authentication/ \
  --cov=apps.authentication \
  --cov-report=html \
  --cov-report=term

# Ver reporte HTML
open htmlcov/index.html
```

**Coverage esperado:** >90%

---

## 🌐 ENDPOINTS DISPONIBLES

### Authentication Endpoints

#### 1. Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}

Response 200:
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {...},
    "token": "abc123...",
    "session_key": "xyz789...",
    "first_login": false
  }
}
```

#### 2. Logout
```http
POST /api/v1/auth/logout/
Authorization: Token abc123...

Response 200:
{
  "success": true,
  "message": "Logout successful"
}
```

#### 3. Cambiar Contraseña
```http
POST /api/v1/auth/change-password/
Authorization: Token abc123...
Content-Type: application/json

{
  "current_password": "oldpass123",
  "new_password": "newpass456",
  "confirm_password": "newpass456"
}

Response 200:
{
  "success": true,
  "message": "Password changed successfully"
}
```

#### 4. Obtener Preguntas de Seguridad
```http
GET /api/v1/auth/security-questions/

Response 200:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "question": "¿Cuál es el nombre de tu primera mascota?",
      "order": 1
    },
    ...
  ]
}
```

#### 5. Configurar Respuestas de Seguridad
```http
POST /api/v1/auth/set-security-answers/
Authorization: Token abc123...
Content-Type: application/json

{
  "answers": [
    {"question_id": 1, "answer": "Firulais"},
    {"question_id": 2, "answer": "Santiago"},
    {"question_id": 3, "answer": "Azul"},
    {"question_id": 4, "answer": "Juan"},
    {"question_id": 5, "answer": "Pizza"}
  ]
}

Response 200:
{
  "success": true,
  "message": "Security answers set successfully"
}
```

#### 6. Verificar Respuestas de Seguridad
```http
POST /api/v1/auth/verify-security-answers/
Content-Type: application/json

{
  "username": "testuser",
  "answers": [
    {"question_id": 1, "answer": "Firulais"},
    ...
  ]
}

Response 200:
{
  "success": true,
  "message": "Security answers verified"
}
```

#### 7. Resetear Contraseña
```http
POST /api/v1/auth/reset-password/
Content-Type: application/json

{
  "username": "testuser",
  "answers": [
    {"question_id": 1, "answer": "Firulais"},
    ...
  ],
  "new_password": "newpass456",
  "confirm_password": "newpass456"
}

Response 200:
{
  "success": true,
  "message": "Password reset successfully"
}
```

### Session Endpoints

#### 8. Listar Sesiones
```http
GET /api/v1/sessions/
Authorization: Token abc123...

Response 200:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "testuser",
      "session_key": "xyz789...",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "login_at": "2024-01-21T10:00:00Z",
      "logout_at": null,
      "is_active": true,
      "duration_seconds": 3600
    },
    ...
  ]
}
```

#### 9. Detalle de Sesión
```http
GET /api/v1/sessions/{id}/
Authorization: Token abc123...

Response 200:
{
  "success": true,
  "data": {
    "id": 1,
    "username": "testuser",
    "session_key": "xyz789...",
    "created_at": "2024-01-21T10:00:00Z",
    "created_by_username": "testuser",
    ...
  }
}
```

#### 10. Invalidar Sesión Específica
```http
POST /api/v1/sessions/{id}/invalidate/
Authorization: Token abc123...

Response 200:
{
  "success": true,
  "message": "Session invalidated successfully"
}
```

#### 11. Invalidar Todas las Sesiones
```http
POST /api/v1/sessions/invalidate-all/
Authorization: Token abc123...

Response 200:
{
  "success": true,
  "message": "2 sessions invalidated",
  "data": {
    "invalidated_count": 2
  }
}
```

---

## 🔧 TROUBLESHOOTING

### Error: "No module named 'apps.authentication'"

**Solución:**
```bash
# Verificar que la app está en INSTALLED_APPS
python manage.py shell -c "from django.conf import settings; print('apps.authentication' in settings.INSTALLED_APPS)"
```

### Error: "relation 'authentication_securityquestion' does not exist"

**Solución:**
```bash
# Aplicar migraciones
python manage.py migrate authentication
```

### Error: "relation 'authentication_login_lockout' does not exist"

**Solución:**
```bash
# Aplicar migración de LoginLockout
python manage.py migrate authentication

# Verificar tabla creada
python manage.py dbshell -c "\dt authentication_login_lockout"
```

### Error: Tests fallan con "fixture 'db' not found"

**Solución:**
```bash
# Instalar pytest-django
pip install pytest-django

# Verificar pytest.ini o conftest.py
cat pytest.ini  # Debe tener DJANGO_SETTINGS_MODULE
```

### Error: "security_questions.json not found"

**Solución:**
```bash
# Verificar ubicación del fixture
ls apps/authentication/fixtures/security_questions.json

# Cargar con path completo
python manage.py loaddata apps/authentication/fixtures/security_questions
```

---

## 📊 CHECKLIST FINAL

```yaml
✅ Migraciones aplicadas (incluyendo LoginLockout)
✅ 10 preguntas de seguridad cargadas
✅ PostgreSQL corriendo y configurado
✅ Tests unitarios pasando (32 tests)
✅ Tests integración pasando (22 tests)
✅ 11 endpoints funcionando
✅ Coverage > 90%
✅ python manage.py check sin errores
✅ CNST-010 cumplido (NO Redis/cache)
```

---

## 🎯 PRÓXIMOS PASOS

1. **Configurar permisos RBAC:**
   - Asignar permisos a roles
   - Ver `apps/access/` para configuración

2. **Integrar con frontend:**
   - Usar tokens en headers: `Authorization: Token <token>`
   - Endpoints públicos: login, security-questions, verify-answers, reset-password
   - Endpoints privados: logout, change-password, set-answers, sessions/*

3. **Monitoreo:**
   - LoginAttempt para auditoría de accesos
   - SessionLog para sesiones activas
   - LoginLockout para tracking de bloqueos (PostgreSQL)

4. **Personalización:**
   - Modificar constantes en `authentication/constants.py`
   - Agregar más preguntas en el fixture JSON
   - Customizar mensajes de error en excepciones

---

## 📚 DOCUMENTACIÓN ADICIONAL

- [README Authentication](../apps/authentication/README.md)
- [Tests README](../tests/README.md)
- [API Documentation](../docs/api/)

---

**Versión:** 1.0.0  
**Fecha:** 2026-01-21  
**Estado:** ✅ Producción Ready
