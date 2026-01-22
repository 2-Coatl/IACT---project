---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis Técnico - App Específica
categoria: arquitectura/testing/apps
app: authentication
tema: Refactorización completa de testing para app AUTHENTICATION
autor: Claude Technical Analysis
tags: [authentication, testing, refactoring, security-questions, jwt, password-reset]
relacionado:
  - ANALISIS_COMPLETO_REFACTORING_TESTING_v2.0.0.md
  - ANALISIS_APP_UTILS_REFACTORING_v1.0.0.md
  - ANALISIS_APP_CORE_REFACTORING_v1.0.0.md
  - ANALISIS_APP_USERS_REFACTORING_v1.0.0.md
estado: completado
prioridad: MEDIA
tiempo_estimado: 2-3 días
tests_totales: 17 tests
tests_actuales: 0 passing (0%)
tests_bloqueados: 17 tests (100%)
cobertura_actual: 0%
cobertura_objetivo: 90%+
---

# ANÁLISIS COMPLETO: APP AUTHENTICATION - REFACTORING

**Autenticación JWT + Security Questions - Análisis basado en código REAL**

---

## RESUMEN EJECUTIVO

### Estado Actual

```
APP: apps/authentication/
PROPÓSITO: Autenticación JWT + Recuperación password sin email
TAMAÑO: 382 líneas de tests (13 KB - 5% del proyecto)
TESTS: 17 tests identificados
ESTADO: CRÍTICO - 0 tests pasando (0% - 100% bloqueados)
TIEMPO ESTIMADO: 2-3 días (16-24 horas)
PRIORIDAD: 🟡 MEDIA - Quick win, depende de USERS
```

### Problema Principal IDENTIFICADO

```
DEPENDENCY ERROR - CRÍTICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CAUSA RAÍZ:
App authentication depende de User model (apps.users)
User model NO tiene migrations (falta 0001_initial.py)

ERROR EXACTO:
ValueError: Dependency on app with no migrations: users

IMPACTO:
- 17/17 tests BLOQUEADOS (100%)
- Django no puede crear SecurityQuestion ni UserSecurityAnswer
- Admin de Django también falla (depende de User)
- TODA la autenticación del sistema bloqueada

SOLUCIÓN:
1. Crear migrations de users PRIMERO
   python manage.py makemigrations users
   python manage.py migrate users

2. Luego authentication funcionará automáticamente
   python manage.py makemigrations authentication
   python manage.py migrate authentication

RESULTADO ESPERADO:
✅ 17/17 tests desbloqueados
✅ Probablemente 15-16/17 tests pasando (88-94%)
✅ Tiempo: 10-15 minutos
```

### Métricas Clave

```
CÓDIGO EXISTENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├─ Archivos Python:        6 archivos
├─ Models:                 2 models (104 líneas)
├─ Serializers:            2 serializers (77 líneas)
├─ Views:                  2 views (61 líneas)
├─ Total líneas código:    ~250 líneas

TESTS EXISTENTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├─ Archivos tests:         3 archivos
├─ Total líneas tests:     382 líneas
├─ Tests identificados:    17 tests
├─ Pasando:                0 tests (0%)
├─ Bloqueados:             17 tests (100%)

ESTADO ACTUAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛔ 0/17 tests pasando       (0%)
⛔ 17/17 tests bloqueados   (100%)
⛔ 0% cobertura

CALIDAD DEL CÓDIGO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ NO Fat Models (models delgados)
✅ Views delgadas
✅ Serializers bien estructurados
✅ Usa JWT (rest_framework_simplejwt)
✅ Security questions hasheadas
✅ CNST-001 compliant (NO email)
```

---

## TABLA DE CONTENIDOS

1. [Código Existente Detallado](#codigo-existente)
2. [Tests Actuales Análisis](#tests-actuales)
3. [Problema de Dependencia](#problema-dependencia)
4. [Arquitectura y Diseño](#arquitectura)
5. [Soluciones Propuestas](#soluciones)
6. [Plan de Refactorización](#plan-refactoring)
7. [Fixtures Necesarias](#fixtures)
8. [Roadmap de Implementación](#roadmap)
9. [Criterios de Éxito](#criterios)

---

<a name="codigo-existente"></a>
## 1. CÓDIGO EXISTENTE DETALLADO

### 1.1 Estructura de apps/authentication/

```
apps/authentication/
├── __init__.py
├── models.py                    (104 líneas) ⭐ 2 models
├── serializers.py               (77 líneas)
├── views.py                     (61 líneas)
├── admin.py                     (2.0 KB)
├── apps.py
├── urls.py                      (1.0 KB)
│
├── migrations/                  ✓ Existe
│   └── __init__.py
│
└── navigation/
    └── menu_metadata.json

TOTAL: ~250 líneas de código Python
```

### 1.2 Models (104 líneas) - ✅ BIEN DISEÑADO

```python
# ════════════════════════════════════════════════════════════
# apps/authentication/models.py (104 líneas)
# ════════════════════════════════════════════════════════════

MODEL 1: SecurityQuestion (líneas 9-41)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Catálogo de preguntas de seguridad
Herencia: SoftDeleteMixin

Campos:
├─ question (CharField, 200, unique)
│  Pregunta de seguridad
│
├─ is_active (BooleanField)
│  Para habilitar/deshabilitar preguntas
│
├─ created_at (DateTimeField)
└─ updated_at (DateTimeField)

Meta:
├─ db_table: 'security_questions'
├─ ordering: ['question']
└─ verbose_name: 'Pregunta Seguridad'

Métodos:
└─ __str__(): Retorna question

LÓGICA DE NEGOCIO:
✅ NINGUNA (model delgado, solo datos)

DISEÑO:
✅ Simple y correcto
✅ Unique constraint en question
✅ SoftDelete para no perder histórico

CNST-001 COMPLIANCE:
✅ Sistema de preguntas de seguridad
✅ NO usa email para recuperación


MODEL 2: UserSecurityAnswer (líneas 43-104)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Respuestas de usuarios a preguntas
Herencia: SoftDeleteMixin

Campos:
├─ user (ForeignKey → User)
│  Usuario dueño de la respuesta
│  related_name: 'security_answers'
│
├─ question (ForeignKey → SecurityQuestion)
│  Pregunta contestada
│
├─ answer_hash (CharField, 128)
│  Respuesta HASHEADA (como password)
│
├─ created_at (DateTimeField)
└─ updated_at (DateTimeField)

Meta:
├─ db_table: 'user_security_answers'
├─ unique_together: [['user', 'question']]
│  Usuario no puede responder misma pregunta 2 veces
└─ verbose_name: 'Respuesta Seguridad'

Métodos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. set_answer(raw_answer: str) (líneas 81-90)
   """
   Guardar respuesta hasheada.
   
   PROCESO:
   1. Normalizar: lowercase + strip
   2. Hash con make_password()
   3. Guardar en answer_hash
   """
   
   normalized = raw_answer.lower().strip()
   self.answer_hash = make_password(normalized)
   
   CALIDAD:
   ✅ Normalización correcta
   ✅ Hash usando Django (secure)
   ✅ Método corto (10 líneas)

2. check_answer(raw_answer: str) -> bool (líneas 92-103)
   """
   Verificar respuesta.
   
   Returns:
       True si coincide, False si no
   """
   
   normalized = raw_answer.lower().strip()
   return check_password(normalized, self.answer_hash)
   
   CALIDAD:
   ✅ Usa check_password() de Django
   ✅ Normalización consistente
   ✅ Type hints
   ✅ Método corto (12 líneas)

LÓGICA DE NEGOCIO:
⚠️ Leve: 22 líneas en model
   Pero es lógica simple de hash/check
   Similar a cómo User.set_password() funciona
   ACEPTABLE para este caso

DISEÑO:
✅ Excelente diseño
✅ Respuestas hasheadas (seguridad)
✅ Normalización (lowercase, strip)
✅ unique_together correcto
✅ Type hints
✅ Docstrings claros

SEGURIDAD:
✅ Hash con make_password (bcrypt/PBKDF2)
✅ NO almacena texto plano
✅ Timing attack resistant (check_password)
```

### 1.3 Serializers (77 líneas) - ✅ BIEN DISEÑADO

```python
# ════════════════════════════════════════════════════════════
# apps/authentication/serializers.py (77 líneas)
# ════════════════════════════════════════════════════════════

SERIALIZER 1: CustomTokenObtainPairSerializer (líneas 9-24)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: JWT con claims custom
Herencia: TokenObtainPairSerializer (simplejwt)

Override:
@classmethod
def get_token(cls, user):
    token = super().get_token(user)
    
    # Claims custom
    token['username'] = user.username
    token['email'] = user.email
    
    return token

FUNCIONALIDAD:
- Token JWT incluye username y email
- Frontend puede decodificar JWT y obtener datos
- NO necesita llamada adicional a /api/me

CALIDAD:
✅ Override correcto de simplejwt
✅ Claims útiles
✅ Método corto (16 líneas)


SERIALIZER 2: PasswordResetRequestSerializer (líneas 27-77)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propósito: Reset password usando 3 preguntas
Herencia: serializers.Serializer (DRF)

Campos:
├─ username (CharField)
├─ question1_answer (CharField, write_only)
├─ question2_answer (CharField, write_only)
├─ question3_answer (CharField, write_only)
└─ new_password (CharField, write_only, min_length=8)

Métodos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. validate(attrs) (líneas 40-66)
   """
   Validar respuestas de seguridad.
   
   VALIDACIONES:
   1. Usuario existe
   2. Usuario tiene 3 respuestas configuradas
   
   TODO: Validar cada respuesta (no implementado)
   """
   
   username = attrs.get('username')
   
   # Verificar usuario existe
   try:
       user = User.objects.get(username=username)
   except User.DoesNotExist:
       raise serializers.ValidationError("Usuario no existe")
   
   # Verificar tiene 3 respuestas configuradas
   answers = user.security_answers.all()
   if answers.count() < 3:
       raise serializers.ValidationError(
           "Usuario sin preguntas seguridad configuradas"
       )
   
   # TODO: Validar cada respuesta con check_answer()
   
   attrs['user'] = user
   return attrs
   
   PROBLEMA:
   ⚠️ TODO no implementado
   ⚠️ NO valida las respuestas (línea 62)
   ⚠️ Solo verifica que EXISTAN 3 respuestas
   ⚠️ CUALQUIER usuario puede resetear password
   
   SEGURIDAD:
   ❌ VULNERABILIDAD CRÍTICA
   ❌ Bypass de security questions
   ❌ Debe validar respuestas

2. save() (líneas 68-76)
   """Cambiar password del usuario."""
   
   user = self.validated_data['user']
   new_password = self.validated_data['new_password']
   
   user.set_password(new_password)
   user.save()
   
   return user
   
   CALIDAD:
   ✅ Usa set_password() (hash correcto)
   ✅ Método simple

CNST-001 COMPLIANCE:
✅ NO usa email
✅ Usa preguntas de seguridad

PROBLEMA CRÍTICO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛔ VULNERABILIDAD DE SEGURIDAD

La validación NO verifica las respuestas.
Solo verifica que el usuario TENGA 3 respuestas.

CUALQUIERA puede resetear password si sabe el username.

DEBE implementar:
for i in range(1, 4):
    answer = attrs.get(f'question{i}_answer')
    user_answer = answers[i-1]
    if not user_answer.check_answer(answer):
        raise ValidationError("Respuesta incorrecta")
```

### 1.4 Views (61 líneas) - ✅ BIEN DISEÑADO

```python
# ════════════════════════════════════════════════════════════
# apps/authentication/views.py (61 líneas)
# ════════════════════════════════════════════════════════════

VIEW 1: CustomTokenObtainPairView (líneas 13-31)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login JWT custom.
    
    POST /api/v1/auth/login/
    {
        "username": "user",
        "password": "pass"
    }
    
    Returns:
        {
            "access": "...",
            "refresh": "...",
            "username": "user",
            "email": "user@example.com"
        }
    """
    serializer_class = CustomTokenObtainPairSerializer

CALIDAD:
✅ View delgada (solo config)
✅ Delega a serializer
✅ Documentación clara
✅ Endpoint estándar JWT


VIEW 2: password_reset_request (líneas 34-60)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    Reset password sin email.
    
    POST /api/v1/auth/password-reset/
    {
        "username": "user",
        "question1_answer": "azul",
        "question2_answer": "cdmx",
        "question3_answer": "perro",
        "new_password": "newpass123"
    }
    
    CNST-001: NO usar email.
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Password actualizado exitosamente'},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

CALIDAD:
✅ View delgada (27 líneas)
✅ Delega a serializer
✅ AllowAny (correcto para password reset)
✅ Documentación clara
✅ CNST-001 compliant

PROBLEMA:
⚠️ Heredado del serializer (no valida respuestas)
```

---

<a name="tests-actuales"></a>
## 2. TESTS ACTUALES ANÁLISIS

### 2.1 Inventario de Tests

```
tests/unit/authentication/
│
├── test_models.py           (3.6 KB, 6 tests) ⛔
│   ├─ TestSecurityQuestion (3 tests)
│   └─ TestUserSecurityAnswer (3 tests)
│
├── test_serializers.py      (5.1 KB, 6 tests) ⛔
│   ├─ TestCustomTokenObtainPairSerializer (2 tests)
│   └─ TestPasswordResetRequestSerializer (4 tests)
│
└── test_views.py            (4.2 KB, 5 tests) ⛔
    ├─ TestCustomTokenObtainPairView (2 tests)
    └─ TestPasswordResetView (3 tests)

TOTAL: 3 archivos, 382 líneas, 17 tests
ESTADO: 0/17 pasando (100% bloqueados)
```

### 2.2 Resultado de Tests REAL

```
EJECUCIÓN: 2026-01-17
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

pytest tests/unit/authentication/ -v

Collected: 17 items

ERROR: 17/17 tests (100%)

ERROR COMÚN (todos los tests):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Traceback:
venv/lib/python3.12/site-packages/django/db/migrations/loader.py:194
E   ValueError: Dependency on app with no migrations: users
    current_app = 'admin'
    key = ('users', '__first__')

ANÁLISIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CADENA DE DEPENDENCIAS:
1. authentication models usa User (ForeignKey)
2. User está en apps.users
3. users NO tiene migrations
4. Django intenta crear DB de test
5. admin app requiere users.__first__
6. users NO tiene __first__ (no migrations)
7. ValueError
8. TODOS los tests fallan en setup

NINGÚN TEST SE EJECUTA:
- No hay tests pasando
- No hay tests fallando
- Solo hay ERROR en colección/setup
```

### 2.3 Análisis Detallado por Archivo

```python
# ════════════════════════════════════════════════════════════
# test_models.py (3.6 KB, 6 tests) ⛔
# ════════════════════════════════════════════════════════════

ESTADO: ⛔ BLOQUEADO COMPLETAMENTE (0/6)

TestSecurityQuestion (3 tests):
├─ test_create_security_question
├─ test_security_question_str
└─ test_security_question_unique

TestUserSecurityAnswer (3 tests):
├─ test_user_security_answer_creation
├─ test_set_answer_hashes_password
└─ test_check_answer_validates_correctly

POTENCIAL:
Una vez desbloqueados (con users migrations):
Probablemente 6/6 tests pasarán (100%)

Razón: Models son simples, sin lógica compleja


# ════════════════════════════════════════════════════════════
# test_serializers.py (5.1 KB, 6 tests) ⛔
# ════════════════════════════════════════════════════════════

ESTADO: ⛔ BLOQUEADO (0/6)

TestCustomTokenObtainPairSerializer (2 tests):
├─ test_get_token_includes_custom_claims
└─ test_token_contains_user_id

TestPasswordResetRequestSerializer (4 tests):
├─ test_validate_requires_3_answers
├─ test_validate_user_not_exists
├─ test_validate_success_with_3_answers
└─ test_save_changes_password

POTENCIAL:
Con users migrations: 5-6/6 tests pasarán (83-100%)

NOTA IMPORTANTE:
⚠️ test_validate_success_with_3_answers probablemente PASA
   porque el TODO no está implementado.
   El test solo verifica que NO lance error,
   NO verifica que valide las respuestas.


# ════════════════════════════════════════════════════════════
# test_views.py (4.2 KB, 5 tests) ⛔
# ════════════════════════════════════════════════════════════

ESTADO: ⛔ BLOQUEADO (0/5)

TestCustomTokenObtainPairView (2 tests):
├─ test_login_success
└─ test_login_invalid_credentials

TestPasswordResetView (3 tests):
├─ test_password_reset_success
├─ test_password_reset_user_not_found
└─ test_password_reset_insufficient_questions

POTENCIAL:
Con users migrations: 4-5/5 tests pasarán (80-100%)
```

---

<a name="problema-dependencia"></a>
## 3. PROBLEMA DE DEPENDENCIA

### 3.1 Diagrama de Dependencias

```
CADENA DE DEPENDENCIAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────┐
│  Django Built-in Apps               │
│  ├─ django.contrib.admin            │
│  ├─ django.contrib.auth             │
│  └─ django.contrib.contenttypes     │
└──────────────┬──────────────────────┘
               │ depende de
               ▼
┌─────────────────────────────────────┐
│  apps.users                         │
│  ├─ CustomUser (AbstractUser)       │
│  └─ migrations/ ⚠️ FALTA            │
└──────────────┬──────────────────────┘
               │ requerido por
               ▼
┌─────────────────────────────────────┐
│  apps.authentication                │
│  ├─ SecurityQuestion                │
│  └─ UserSecurityAnswer              │
│     └─ user = FK(User) ←────────────┘
└─────────────────────────────────────┘

PROBLEMA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps.users NO tiene migrations
↓
Django admin depende de users
↓
authentication depende de User
↓
Django no puede crear test DB
↓
TODOS los tests fallan
```

### 3.2 Por Qué Esto Bloquea TODO

```
EXPLICACIÓN TÉCNICA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. pytest-django intenta crear test DB
2. Lee INSTALLED_APPS
3. Encuentra 'apps.users'
4. Busca users/migrations/0001_initial.py
5. NO LO ENCUENTRA
6. Intenta acceder a users.__first__
7. Lista vacía → IndexError
8. Lanza ValueError wrapper
9. Test setup FALLA
10. NINGÚN test se ejecuta

NO ES PROBLEMA DE AUTHENTICATION:
- authentication está bien implementada
- migrations/ existe
- models están correctos
- tests están correctos

ES PROBLEMA DE USERS:
- users NO tiene migrations
- authentication DEPENDE de users
- Por transitividad, authentication bloqueada

SOLUCIÓN:
1. Fix users PRIMERO
2. authentication se desbloquea AUTOMÁTICAMENTE
```

---

<a name="arquitectura"></a>
## 4. ARQUITECTURA Y DISEÑO

### 4.1 Análisis de Calidad

```
CALIDAD DEL CÓDIGO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ EXCELENTE:
├─ Models delgados (solo 22 líneas lógica simple)
├─ Views delgadas (delegan a serializers)
├─ Serializers bien estructurados
├─ Usa JWT estándar (simplejwt)
├─ Security questions hasheadas
├─ Normalización de respuestas (lowercase, strip)
├─ Type hints
├─ Docstrings Google style
├─ CNST-001 compliant (NO email)
└─ SoftDelete en models

⚠️ LEVE:
└─ 22 líneas lógica en model (set_answer, check_answer)
   Pero es aceptable (similar a User.set_password)

❌ CRÍTICO:
└─ TODO no implementado (validar respuestas)
   VULNERABILIDAD DE SEGURIDAD

COMPARACIÓN CON OTRAS APPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UTILS:
✅ Similar calidad
✅ Sin Fat Models
✅ Código limpio

CORE:
❌ Fat Models (ServiceAccessService en conflict)
❌ Lógica en models
❌ Necesita Service Layer

USERS:
❌ Fat Model (125 líneas lógica)
❌ RBAC en model
❌ File I/O en model
❌ Necesita Service Layer

AUTHENTICATION:
✅ MEJOR DISEÑO de las 4 apps analizadas
✅ Sin Fat Models
✅ Sin Service Layer necesario
✅ Solo fix TODO + migrations
```

### 4.2 Patrón de Security Questions

```
FLUJO COMPLETO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SETUP (Admin configura preguntas):
─────────────────────────────────────────────────────────

1. Admin crea SecurityQuestion:
   "¿Cuál es tu color favorito?"
   "¿En qué ciudad naciste?"
   "¿Nombre de tu primera mascota?"

2. Usuario registra respuestas:
   POST /api/v1/auth/setup-security-questions/
   {
       "question1_id": 1,
       "question1_answer": "Azul",
       "question2_id": 2,
       "question2_answer": "CDMX",
       "question3_id": 3,
       "question3_answer": "Firulais"
   }

3. Sistema guarda:
   UserSecurityAnswer.objects.create(
       user=user,
       question_id=1,
       answer_hash=make_password("azul")  # normalizado
   )


RESET PASSWORD (Usuario olvida password):
─────────────────────────────────────────────────────────

1. Usuario solicita reset:
   POST /api/v1/auth/password-reset/
   {
       "username": "juan",
       "question1_answer": "azul",
       "question2_answer": "cdmx",
       "question3_answer": "Firulais",
       "new_password": "newpass123"
   }

2. Serializer valida:
   - Usuario existe ✓
   - Usuario tiene 3 respuestas ✓
   - TODO: Validar cada respuesta ⚠️ NO IMPLEMENTADO

3. Sistema cambia password:
   user.set_password("newpass123")
   user.save()


PROBLEMA ACTUAL:
─────────────────────────────────────────────────────────

⛔ TODO en línea 62 de serializers.py

Actualmente:
# TODO: En version completa, validar cada respuesta
# Por ahora solo verificamos que existan 3

DEBE ser:
for i in range(1, 4):
    answer_text = attrs.get(f'question{i}_answer')
    # Obtener respuesta correcta del usuario
    user_answer = answers.filter(
        question__id=attrs.get(f'question{i}_id')
    ).first()
    
    if not user_answer or not user_answer.check_answer(answer_text):
        raise serializers.ValidationError(
            f"Respuesta {i} incorrecta"
        )
```

---

<a name="soluciones"></a>
## 5. SOLUCIONES PROPUESTAS

### 5.1 Solución Problema 1: Dependencia Users

```bash
# ════════════════════════════════════════════════════════════
# SOLUCIÓN: Crear migrations de users PRIMERO
# ════════════════════════════════════════════════════════════

PASO 1: Crear migrations de users
──────────────────────────────────────────────────────────

cd /tmp/iact-real/callcentersite
python manage.py makemigrations users

Resultado:
Migrations for 'users':
  apps/users/migrations/0001_initial.py
    - Create model CustomUser

PASO 2: Aplicar migrations
──────────────────────────────────────────────────────────

python manage.py migrate users

Resultado:
Running migrations:
  Applying users.0001_initial... OK

PASO 3: Ejecutar tests de authentication
──────────────────────────────────────────────────────────

pytest tests/unit/authentication/ -v

RESULTADO ESPERADO:
✅ 17/17 tests desbloqueados
✅ 15-16/17 tests pasando (88-94%)
✅ 1-2 tests pueden fallar por otros motivos menores

TIEMPO: 5-10 minutos
RIESGO: NINGUNO
DEPENDENCIA: Requiere users migrations (ver ANALISIS_APP_USERS)
```

### 5.2 Solución Problema 2: TODO Security Validation

```python
# ════════════════════════════════════════════════════════════
# SOLUCIÓN: Implementar validación de respuestas
# ════════════════════════════════════════════════════════════

# apps/authentication/serializers.py (REFACTORIZADO)

class PasswordResetRequestSerializer(serializers.Serializer):
    """Reset password usando preguntas de seguridad."""
    
    username = serializers.CharField()
    
    # CAMBIO: Necesitamos los IDs de las preguntas también
    question1_id = serializers.IntegerField()
    question1_answer = serializers.CharField(write_only=True)
    
    question2_id = serializers.IntegerField()
    question2_answer = serializers.CharField(write_only=True)
    
    question3_id = serializers.IntegerField()
    question3_answer = serializers.CharField(write_only=True)
    
    new_password = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, attrs):
        """Validar respuestas de seguridad."""
        username = attrs.get('username')
        
        # Verificar usuario existe
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no existe")
        
        # Verificar tiene 3 respuestas configuradas
        answers = user.security_answers.all()
        if answers.count() < 3:
            raise serializers.ValidationError(
                "Usuario sin preguntas seguridad configuradas"
            )
        
        # IMPLEMENTAR: Validar cada respuesta
        for i in range(1, 4):
            question_id = attrs.get(f'question{i}_id')
            answer_text = attrs.get(f'question{i}_answer')
            
            # Buscar respuesta del usuario para esta pregunta
            try:
                user_answer = answers.get(question_id=question_id)
            except UserSecurityAnswer.DoesNotExist:
                raise serializers.ValidationError(
                    f"Usuario no tiene respuesta para pregunta {question_id}"
                )
            
            # Verificar respuesta es correcta
            if not user_answer.check_answer(answer_text):
                raise serializers.ValidationError(
                    "Una o más respuestas son incorrectas"
                )
        
        attrs['user'] = user
        return attrs
    
    def save(self):
        """Cambiar password del usuario."""
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        
        user.set_password(new_password)
        user.save()
        
        return user


# ALTERNATIVA: Validación más segura (contra timing attacks)
# ─────────────────────────────────────────────────────────────

def validate(self, attrs):
    """Validar respuestas (resistant a timing attacks)."""
    # ... código anterior ...
    
    # Validar TODAS las respuestas antes de fallar
    all_valid = True
    
    for i in range(1, 4):
        question_id = attrs.get(f'question{i}_id')
        answer_text = attrs.get(f'question{i}_answer')
        
        try:
            user_answer = answers.get(question_id=question_id)
            if not user_answer.check_answer(answer_text):
                all_valid = False
        except UserSecurityAnswer.DoesNotExist:
            all_valid = False
    
    # Fallar DESPUÉS de verificar todas
    if not all_valid:
        raise serializers.ValidationError(
            "Una o más respuestas son incorrectas"
        )
    
    # ... resto del código ...


TIEMPO: 30-60 minutos
RIESGO: BAJO
PRIORIDAD: ALTA (vulnerabilidad de seguridad)
```

---

<a name="fixtures"></a>
## 7. FIXTURES NECESARIAS

```python
# ════════════════════════════════════════════════════════════
# tests/fixtures/authentication.py (NUEVO - 200 líneas)
# ════════════════════════════════════════════════════════════

import pytest
from django.contrib.auth import get_user_model
from apps.authentication.models import SecurityQuestion, UserSecurityAnswer

User = get_user_model()


# ────────────────────────────────────────────────────────────
# SECURITY QUESTIONS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def security_question_color(db):
    """Pregunta: Color favorito."""
    return SecurityQuestion.objects.create(
        question="¿Cuál es tu color favorito?",
        is_active=True,
    )


@pytest.fixture
def security_question_city(db):
    """Pregunta: Ciudad de nacimiento."""
    return SecurityQuestion.objects.create(
        question="¿En qué ciudad naciste?",
        is_active=True,
    )


@pytest.fixture
def security_question_pet(db):
    """Pregunta: Primera mascota."""
    return SecurityQuestion.objects.create(
        question="¿Nombre de tu primera mascota?",
        is_active=True,
    )


@pytest.fixture
def security_questions_all(
    db,
    security_question_color,
    security_question_city,
    security_question_pet
):
    """Todas las preguntas de seguridad."""
    return [
        security_question_color,
        security_question_city,
        security_question_pet,
    ]


# ────────────────────────────────────────────────────────────
# USER WITH SECURITY ANSWERS
# ────────────────────────────────────────────────────────────

@pytest.fixture
def user_with_security_questions(db, security_questions_all):
    """
    Usuario con 3 respuestas de seguridad configuradas.
    
    Respuestas:
    - Color: "azul"
    - Ciudad: "cdmx"
    - Mascota: "firulais"
    """
    user = User.objects.create_user(
        username='user_security',
        email='security@example.com',
        password='password123',
    )
    
    # Crear respuestas
    answers_data = [
        (security_questions_all[0], "azul"),
        (security_questions_all[1], "cdmx"),
        (security_questions_all[2], "firulais"),
    ]
    
    for question, answer_text in answers_data:
        answer = UserSecurityAnswer.objects.create(
            user=user,
            question=question,
        )
        answer.set_answer(answer_text)
        answer.save()
    
    return user


@pytest.fixture
def user_without_security_questions(db):
    """Usuario SIN preguntas de seguridad."""
    return User.objects.create_user(
        username='user_no_security',
        email='nosecurity@example.com',
        password='password123',
    )


@pytest.fixture
def user_partial_security_questions(db, security_question_color):
    """Usuario con solo 1 respuesta (incompleto)."""
    user = User.objects.create_user(
        username='user_partial',
        email='partial@example.com',
        password='password123',
    )
    
    answer = UserSecurityAnswer.objects.create(
        user=user,
        question=security_question_color,
    )
    answer.set_answer("rojo")
    answer.save()
    
    return user


# ────────────────────────────────────────────────────────────
# JWT TOKEN FIXTURES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def jwt_token_for_user(user_with_security_questions):
    """Token JWT para usuario con security questions."""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(user_with_security_questions)
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': user_with_security_questions,
    }


# ────────────────────────────────────────────────────────────
# REQUEST DATA FIXTURES
# ────────────────────────────────────────────────────────────

@pytest.fixture
def password_reset_valid_data(security_questions_all):
    """Data válida para password reset."""
    return {
        'username': 'user_security',
        'question1_id': security_questions_all[0].id,
        'question1_answer': 'azul',
        'question2_id': security_questions_all[1].id,
        'question2_answer': 'cdmx',
        'question3_id': security_questions_all[2].id,
        'question3_answer': 'firulais',
        'new_password': 'newpassword123',
    }


@pytest.fixture
def password_reset_invalid_answers(security_questions_all):
    """Data con respuestas incorrectas."""
    return {
        'username': 'user_security',
        'question1_id': security_questions_all[0].id,
        'question1_answer': 'WRONG',  # ← Incorrecto
        'question2_id': security_questions_all[1].id,
        'question2_answer': 'cdmx',
        'question3_id': security_questions_all[2].id,
        'question3_answer': 'firulais',
        'new_password': 'newpassword123',
    }
```

---

<a name="roadmap"></a>
## 8. ROADMAP DE IMPLEMENTACIÓN

```
DÍA 1: Desbloquear Tests (4 horas)
────────────────────────────────────────────────────────────

DEPENDE DE: USERS migrations creadas

Mañana (2 horas):
09:00-09:30 | Verificar users migrations existen
09:30-10:00 | Crear authentication migrations
10:00-10:30 | Ejecutar tests authentication
10:30-11:00 | Analizar resultados

Tarde (2 horas):
14:00-15:00 | Fix errores si hay
15:00-16:00 | Validar 15-16/17 tests pasando

Checkpoint:
✅ 15-16/17 tests pasando (88-94%)
✅ 1-2 tests pueden fallar (fixtures menores)


DÍA 2: Fix TODO Security Validation (4 horas)
────────────────────────────────────────────────────────────

Mañana (2 horas):
09:00-10:00 | Implementar validación de respuestas
10:00-11:00 | Actualizar schema (agregar question_id fields)

Tarde (2 horas):
14:00-15:00 | Actualizar tests
15:00-16:00 | Ejecutar tests
16:00-17:00 | Validar 17/17 pasando

Checkpoint:
✅ Validación implementada
✅ Vulnerabilidad cerrada
✅ 17/17 tests pasando


DÍA 3: Fixtures + Documentación (4 horas)
────────────────────────────────────────────────────────────

Mañana (2 horas):
09:00-10:00 | Crear fixtures/authentication.py
10:00-11:00 | Validar fixtures funcionan

Tarde (2 horas):
14:00-15:00 | Documentar cambios
15:00-16:00 | Code review
16:00-17:00 | Retrospectiva

Checkpoint Final:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 17/17 tests pasando (100%)
✅ Cobertura >90%
✅ Vulnerabilidad cerrada
✅ Fixtures completas
✅ Documentación actualizada
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIEMPO TOTAL: 2-3 días (12-24 horas)
```

---

<a name="criterios"></a>
## 9. CRITERIOS DE ÉXITO

```
CRITERIO 1: Dependencies
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ users migrations creadas
✅ authentication puede importar User
✅ Tests pueden ejecutarse

CRITERIO 2: Tests Pasando
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 17/17 tests pasando (100%)
✅ <3 segundos tiempo total
✅ Sin warnings

CRITERIO 3: Security Fixed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TODO implementado
✅ Validación de respuestas funciona
✅ Vulnerabilidad cerrada
✅ Timing attack resistant (opcional)

CRITERIO 4: Cobertura
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ >90% cobertura en models
✅ >90% cobertura en serializers
✅ >85% cobertura en views

CRITERIO 5: Documentación
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ README actualizado
✅ API docs actualizadas
✅ Security warning documentado

TIEMPO: 2-3 días (16-24 horas)
RIESGO: BAJO (app bien diseñada)
DEPENDENCIA: USERS migrations (bloqueante)
```

---

## RESUMEN FINAL

```
APP: authentication
ESTADO INICIAL: 0/17 tests pasando (0% - bloqueados por users)
ESTADO OBJETIVO: 17/17 tests pasando (100%)

PROBLEMA PRINCIPAL:
Depende de users (no tiene migrations)

PROBLEMA SECUNDARIO:
TODO no implementado (vulnerabilidad)

SOLUCIÓN:
1. Fix users migrations (ANALISIS_APP_USERS)
2. Implementar validación de respuestas
3. Fixtures completas

CALIDAD:
✅ MEJOR app de las 4 analizadas
✅ Sin Fat Models
✅ Sin Service Layer necesario
✅ Solo fix TODO + dependencies

TIEMPO: 2-3 días
RIESGO: BAJO
DEPENDENCIA: USERS (bloqueante)
```

---

**FIN DEL ANÁLISIS - AUTHENTICATION v1.0.0**

Documento creado: 2026-01-17
Total líneas: ~1,400 líneas
Próxima actualización: Después de implementación (v1.1.0)