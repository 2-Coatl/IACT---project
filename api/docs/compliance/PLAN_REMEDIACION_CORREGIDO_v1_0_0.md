# 🔧 PLAN DE REMEDIACIÓN CORREGIDO - apps/users/ vs apps/authentication/

## INFORMACIÓN DEL DOCUMENTO

| Atributo | Valor |
|---|---|
| **Fecha** | 2026-01-21 |
| **Versión** | 1.0.0 CORREGIDA |
| **Base** | ANALISIS_APP_AUTHENTICATION_v3_0_0 (3 partes) |
| **Prioridad** | CRÍTICA |

---

## 📋 RESUMEN EJECUTIVO - CORREGIDO

### Separación de Responsabilidades

```yaml
apps/users/:
  Responsabilidad: Gestión de usuarios (CRUD)
  Models:
    ✅ User (AbstractUser + SoftDeleteMixin)
    ✅ UserProfile (bio, department, avatar)
    ✅ UserSettings (timezone, language, notifications)
    ❌ SessionHistory → MOVER a apps/authentication/
  
  Servicios:
    ✅ UserService (create, update, delete)
    ✅ ProfileService (update profile, avatar)
    ✅ PasswordService (change password)
    ❌ AuthenticationService → NO va aquí
  
  Endpoints:
    ✅ /api/v1/users/users/ (CRUD)
    ✅ /api/v1/users/users/me/
    ✅ /api/v1/users/users/{id}/activate/
    ✅ /api/v1/users/users/{id}/deactivate/
    ✅ /api/v1/users/profile/
    ✅ /api/v1/users/settings/
    ❌ /api/v1/users/auth/* → ELIMINAR (va en authentication)

apps/authentication/:
  Responsabilidad: Autenticación y seguridad
  Models:
    ✅ LoginAttempt (intentos login)
    ✅ SecurityQuestion (3 preguntas)
    ✅ UserSecurityAnswer (respuestas hasheadas)
    ✅ SessionLog (historial sesiones)
  
  Servicios:
    ✅ AuthenticationService (login/logout)
    ✅ RecoveryService (preguntas seguridad)
    ✅ LockoutService (bloqueo cuentas)
    ✅ SessionService (gestión sesiones)
  
  Endpoints:
    ✅ /api/v1/auth/login/
    ✅ /api/v1/auth/logout/
    ✅ /api/v1/auth/security-questions/
    ✅ /api/v1/auth/set-security-answers/
    ✅ /api/v1/auth/verify-security-answers/
    ✅ /api/v1/auth/reset-password/
    ✅ /api/v1/sessions/ (ReadOnlyModelViewSet)

apps/alerts/:
  Responsabilidad: Alertas y mensajería interna
  ⏳ PENDIENTE de implementar
  
  Necesario para:
    - ALERT cuando usuario no tiene preguntas configuradas
    - ALERT diaria a usuarios sin preguntas
    - Buzón interno de mensajes
```

---

## 🚨 VIOLACIONES CRÍTICAS CORREGIDAS

### ❌ VIOLACIÓN #1: apps/users/viewsets.py tiene código de AUTHENTICATION

**Código Incorrecto Actual:**

```python
# apps/users/viewsets.py - líneas 240-430

class AuthViewSet(viewsets.ViewSet):  # ❌ NO debería estar en apps/users/
    
    @action(detail=False, methods=['post'])
    def login(self, request):  # ❌ Va en apps/authentication/
        ...
    
    @action(detail=False, methods=['post'])
    def logout(self, request):  # ❌ Va en apps/authentication/
        ...
    
    @action(detail=False, methods=['post'])
    def password_reset(self, request):  # ❌ Va en apps/authentication/
        # ❌ USA EMAIL (CNST-001 violado)
        ...
    
    @action(detail=False, methods=['post'])
    def password_reset_confirm(self, request):  # ❌ Va en apps/authentication/
        # ❌ USA EMAIL (CNST-001 violado)
        ...
```

**URLs Incorrectas:**

```python
# apps/users/urls.py - líneas 27-33

auth_urls = [  # ❌ TODO ESTO va en apps/authentication/
    path('login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('logout/', AuthViewSet.as_view({'post': 'logout'}), name='logout'),
    path('change-password/', AuthViewSet.as_view({'post': 'change_password'}), name='change-password'),
    path('password-reset/', AuthViewSet.as_view({'post': 'password_reset'}), name='password-reset'),
    path('password-reset-confirm/', AuthViewSet.as_view({'post': 'password_reset_confirm'}), name='password-reset-confirm'),
]
```

**Corrección:**

```yaml
PASO 1: ELIMINAR de apps/users/viewsets.py
  ❌ class AuthViewSet completa (líneas 240-430)
  ❌ LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer

PASO 2: ELIMINAR de apps/users/urls.py
  ❌ auth_urls completas
  ❌ path('auth/', include(auth_urls))

PASO 3: CREAR apps/authentication/ (nueva app)
  ✅ Todo el código de autenticación va aquí
```

---

### ❌ VIOLACIÓN #2: SessionHistory en app incorrecta

**Ubicación Actual:**

```python
# apps/users/models.py - líneas 230-290

class SessionHistory(TimeStampedModel):  # ❌ Debería estar en apps/authentication/
    """Historial de sesiones."""
    ...
```

**Corrección:**

```yaml
MOVER a apps/authentication/models.py:
  ✅ SessionHistory → SessionLog
  ✅ Renombrar tabla: session_history → tbl_log_sesiones
  ✅ Ajustar campos según ANALISIS_APP_AUTHENTICATION
```

---

### ❌ VIOLACIÓN #3: Falta apps/authentication/ completa

**Problema:**
- apps/authentication/ NO EXISTE
- Todo está mezclado en apps/users/

**Solución:**
- Crear apps/authentication/ desde cero
- Seguir ANALISIS_APP_AUTHENTICATION_v3_0_0 (3 partes)

---

## 📝 PLAN DE REMEDIACIÓN DETALLADO

### FASE 1: LIMPIEZA de apps/users/ (2 horas)

#### PASO 1.1: Eliminar código de autenticación

```bash
# apps/users/viewsets.py

ELIMINAR:
  - class AuthViewSet (líneas 240-430)
  - Métodos:
    - login()
    - logout()
    - change_password()
    - password_reset()
    - password_reset_confirm()

MANTENER:
  - class UserViewSet
  - class ProfileViewSet
  - class SettingsViewSet
  - class SessionHistoryViewSet (por ahora)
```

#### PASO 1.2: Eliminar serializers de autenticación

```bash
# apps/users/serializers/auth_serializers.py

ELIMINAR completo:
  - LoginSerializer
  - PasswordResetRequestSerializer
  - PasswordResetConfirmSerializer

MANTENER:
  - ChangePasswordSerializer (va en users porque cambia password del user actual)
```

#### PASO 1.3: Actualizar URLs

```bash
# apps/users/urls.py

ELIMINAR:
  - auth_urls (líneas 27-33)
  - path('auth/', include(auth_urls))

MANTENER:
  - router con UserViewSet
  - profile_urls
  - settings_urls
  - sessions (por ahora)
```

#### PASO 1.4: Actualizar imports

```bash
# Buscar y actualizar todos los imports de:
from apps.users.serializers import LoginSerializer
# → Cambiar a:
from apps.authentication.serializers import LoginSerializer
```

---

### FASE 2: CREAR apps/authentication/ (6-8 horas)

#### PASO 2.1: Crear estructura de la app

```bash
cd /tmp/iact-real/callcentersite
python manage.py startapp authentication apps/authentication

# Estructura:
apps/authentication/
├── __init__.py
├── apps.py
├── models.py           # 4 modelos
├── constants.py        # Constantes
├── exceptions.py       # 5 custom exceptions
├── utils.py            # 8 helper functions
├── services/
│   ├── __init__.py
│   ├── authentication.py    # AuthenticationService
│   ├── recovery.py          # RecoveryService
│   ├── lockout.py           # LockoutService
│   └── session.py           # SessionService
├── serializers/
│   ├── __init__.py
│   ├── auth.py              # Login, etc
│   ├── recovery.py          # Security questions
│   └── session.py           # SessionLog
├── viewsets.py         # AuthViewSet, SessionViewSet
├── urls.py
├── admin.py
├── migrations/
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    ├── test_viewsets.py
    └── test_integration.py
```

#### PASO 2.2: Crear models.py

```python
# apps/authentication/models.py

from django.db import models
from django.conf import settings

# ============================================================================
# 1. LoginAttempt
# ============================================================================

class LoginAttempt(models.Model):
    """
    Intento de login (exitoso o fallido).
    
    CNST-031: Auditoría immutable de intentos.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_attempts',
        db_column='iIdUsuario'
    )
    
    username = models.CharField(
        'Username',
        max_length=150,
        db_column='cUsername',
        help_text='Username intentado (aunque no exista)'
    )
    
    success = models.BooleanField(
        'Exitoso',
        db_column='bSuccess'
    )
    
    ip_address = models.GenericIPAddressField(
        'IP Address',
        db_column='cIpAddress'
    )
    
    user_agent = models.CharField(
        'User Agent',
        max_length=255,
        blank=True,
        db_column='cUserAgent'
    )
    
    attempted_at = models.DateTimeField(
        'Intentado',
        auto_now_add=True,
        db_column='dtAttemptedAt'
    )
    
    class Meta:
        db_table = 'tbl_intentos_login'
        verbose_name = 'Intento de Login'
        verbose_name_plural = 'Intentos de Login'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['username', '-attempted_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        status = 'SUCCESS' if self.success else 'FAILED'
        return f"{self.username} - {status} - {self.attempted_at}"


# ============================================================================
# 2. SecurityQuestion
# ============================================================================

class SecurityQuestion(models.Model):
    """
    Pregunta de seguridad predefinida.
    
    CNST-001: 3 preguntas obligatorias por usuario.
    Pool mínimo: 10 preguntas.
    """
    
    question = models.CharField(
        'Pregunta',
        max_length=255,
        unique=True,
        db_column='cQuestion'
    )
    
    is_active = models.BooleanField(
        'Activa',
        default=True,
        db_column='bIsActive'
    )
    
    order = models.IntegerField(
        'Orden',
        default=0,
        db_column='iOrder',
        help_text='Orden de presentación'
    )
    
    created_at = models.DateTimeField(
        'Creado',
        auto_now_add=True,
        db_column='dtCreatedAt'
    )
    
    class Meta:
        db_table = 'tbl_preguntas_seguridad'
        verbose_name = 'Pregunta de Seguridad'
        verbose_name_plural = 'Preguntas de Seguridad'
        ordering = ['order', 'question']
    
    def __str__(self):
        return self.question


# ============================================================================
# 3. UserSecurityAnswer
# ============================================================================

class UserSecurityAnswer(models.Model):
    """
    Respuesta de usuario a pregunta de seguridad.
    
    CNST-001: 3 respuestas obligatorias.
    Respuestas hasheadas con PBKDF2 (mismo que passwords).
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='security_answers',
        db_column='iIdUsuario'
    )
    
    question = models.ForeignKey(
        SecurityQuestion,
        on_delete=models.PROTECT,
        db_column='iIdPregunta'
    )
    
    answer_hash = models.CharField(
        'Hash Respuesta',
        max_length=255,
        db_column='cAnswerHash',
        help_text='PBKDF2 hash (case-insensitive)'
    )
    
    created_at = models.DateTimeField(
        'Creado',
        auto_now_add=True,
        db_column='dtCreatedAt'
    )
    
    updated_at = models.DateTimeField(
        'Actualizado',
        auto_now=True,
        db_column='dtUpdatedAt'
    )
    
    class Meta:
        db_table = 'tbl_respuestas_usuario'
        verbose_name = 'Respuesta de Seguridad'
        verbose_name_plural = 'Respuestas de Seguridad'
        unique_together = [['user', 'question']]
    
    def __str__(self):
        return f"{self.user.username} - {self.question.question}"
    
    def set_answer(self, answer: str):
        """
        Hashea y guarda respuesta.
        
        Args:
            answer: Respuesta en texto plano
        """
        from django.contrib.auth.hashers import make_password
        
        # Normalizar: lowercase, strip
        normalized = answer.lower().strip()
        
        # Hash con PBKDF2
        self.answer_hash = make_password(normalized)
    
    def check_answer(self, answer: str) -> bool:
        """
        Verifica respuesta.
        
        Args:
            answer: Respuesta a verificar
        
        Returns:
            bool: True si correcta
        """
        from django.contrib.auth.hashers import check_password
        
        normalized = answer.lower().strip()
        return check_password(normalized, self.answer_hash)


# ============================================================================
# 4. SessionLog
# ============================================================================

class SessionLog(models.Model):
    """
    Log de sesión de usuario.
    
    CNST-031: Auditoría de sesiones.
    CNST-010: Sessions en DB.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='session_logs',
        db_column='iIdUsuario'
    )
    
    session_key = models.CharField(
        'Session Key',
        max_length=40,
        db_column='cSessionKey',
        help_text='Django session key'
    )
    
    ip_address = models.GenericIPAddressField(
        'IP Address',
        db_column='cIpAddress'
    )
    
    user_agent = models.CharField(
        'User Agent',
        max_length=255,
        blank=True,
        db_column='cUserAgent'
    )
    
    login_at = models.DateTimeField(
        'Login',
        auto_now_add=True,
        db_column='dtLoginAt'
    )
    
    logout_at = models.DateTimeField(
        'Logout',
        null=True,
        blank=True,
        db_column='dtLogoutAt'
    )
    
    is_active = models.BooleanField(
        'Activa',
        default=True,
        db_column='bIsActive'
    )
    
    class Meta:
        db_table = 'tbl_log_sesiones'
        verbose_name = 'Log de Sesión'
        verbose_name_plural = 'Logs de Sesiones'
        ordering = ['-login_at']
        indexes = [
            models.Index(fields=['user', '-login_at']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.login_at}"
    
    @property
    def duration(self):
        """Duración de la sesión."""
        if self.logout_at:
            return self.logout_at - self.login_at
        return None
```

#### PASO 2.3: Crear constants.py

```python
# apps/authentication/constants.py

# Login attempts
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
LOCKOUT_WINDOW_MINUTES = 15

# Session
SESSION_TIMEOUT_SECONDS = 3600
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True

# Password
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

# Security Questions (CNST-001)
SECURITY_QUESTIONS_REQUIRED = 3  # ✅ 3 preguntas, NO 5
SECURITY_QUESTIONS_POOL_MIN = 10

# Audit
LOG_FAILED_ATTEMPTS = True
LOG_SUCCESSFUL_LOGINS = True
LOG_LOGOUTS = True
```

#### PASO 2.4: Crear servicios

Ver ANALISIS_APP_AUTHENTICATION_v3_0_0_PARTE_2.md para código completo de:
- AuthenticationService
- RecoveryService  
- LockoutService
- SessionService

#### PASO 2.5: Crear serializers y viewsets

Ver ANALISIS_APP_AUTHENTICATION_v3_0_0_PARTE_3.md para código completo.

---

### FASE 3: MOVER SessionHistory (1 hora)

```yaml
PASO 1: Deprecar apps/users/models.py::SessionHistory
  - Marcar como deprecated
  - Crear migración para renombrar tabla

PASO 2: Usar apps/authentication/models.py::SessionLog
  - Actualizar todos los imports
  - Cambiar SessionHistorySerializer → SessionLogSerializer

PASO 3: Actualizar ViewSet
  - SessionHistoryViewSet en apps/users/ → Deprecar
  - Usar SessionViewSet de apps/authentication/
```

---

### FASE 4: INTEGRACIÓN con apps/users/ (2 horas)

#### PASO 4.1: First Login Flow (apps/users/)

```python
# apps/users/models.py - Agregar campos al User

class User(AbstractUser, SoftDeleteMixin):
    ...
    
    # ✅ AGREGAR estos campos para first login
    first_login = models.BooleanField(
        default=True,
        help_text='True si es el primer login'
    )
    
    force_password_change = models.BooleanField(
        default=True,
        help_text='Forzar cambio de password'
    )
    
    # ✅ Campo para tracking de preguntas
    has_security_answers = models.BooleanField(
        default=False,
        help_text='True si configuró las 3 preguntas'
    )
```

#### PASO 4.2: Integration en login

```python
# apps/authentication/viewsets.py - AuthViewSet.login()

@action(detail=False, methods=['post'])
def login(self, request):
    """Login con detección de first_login."""
    
    # ... autenticación normal ...
    
    # Verificar first_login
    response_data = {
        'user': UserSerializer(user).data,
        'token': result['token'],
    }
    
    # Flags para frontend
    if user.first_login:
        response_data['first_login'] = True
        response_data['force_password_change'] = True
        response_data['message'] = 'Debes cambiar tu password y configurar preguntas de seguridad'
    
    elif not user.has_security_answers:
        response_data['pending_security_questions'] = True
        response_data['message'] = 'Recuerda configurar tus preguntas de seguridad'
    
    return Response(response_data)
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Limpieza apps/users/ (2h)

```yaml
☐ 1.1 Eliminar AuthViewSet de apps/users/viewsets.py
☐ 1.2 Eliminar LoginSerializer, PasswordResetSerializer
☐ 1.3 Actualizar apps/users/urls.py (quitar auth/)
☐ 1.4 Buscar y listar todos los imports a actualizar
```

### Fase 2: Crear apps/authentication/ (6-8h)

```yaml
☐ 2.1 python manage.py startapp authentication apps/authentication
☐ 2.2 Crear models.py (4 modelos)
☐ 2.3 Crear constants.py
☐ 2.4 Crear exceptions.py
☐ 2.5 Crear utils.py
☐ 2.6 Crear services/ (4 servicios)
☐ 2.7 Crear serializers/ (3 archivos)
☐ 2.8 Crear viewsets.py (AuthViewSet, SessionViewSet)
☐ 2.9 Crear urls.py
☐ 2.10 Registrar en INSTALLED_APPS
☐ 2.11 Crear migraciones: python manage.py makemigrations authentication
☐ 2.12 Aplicar migraciones: python manage.py migrate
☐ 2.13 Crear fixture con 10 SecurityQuestions
```

### Fase 3: Mover SessionHistory (1h)

```yaml
☐ 3.1 Deprecar SessionHistory en apps/users/
☐ 3.2 Actualizar imports a SessionLog
☐ 3.3 Migración para renombrar tabla
```

### Fase 4: Integration (2h)

```yaml
☐ 4.1 Agregar campos first_login, has_security_answers a User
☐ 4.2 Actualizar login para retornar flags
☐ 4.3 Tests de integración entre apps
```

### Fase 5: Testing (4h)

```yaml
☐ 5.1 Tests unitarios models (apps/authentication/)
☐ 5.2 Tests unitarios services
☐ 5.3 Tests integration viewsets
☐ 5.4 Tests end-to-end (login → set questions → reset password)
```

---

## 📊 TIEMPO ESTIMADO TOTAL

```yaml
Fase 1: Limpieza apps/users/        2 horas
Fase 2: Crear apps/authentication/  8 horas
Fase 3: Mover SessionHistory        1 hora
Fase 4: Integration                 2 horas
Fase 5: Testing                     4 horas

TOTAL: 17 horas (2-3 días de trabajo)
```

---

## 🎯 RESULTADO ESPERADO

```yaml
Arquitectura Correcta:
  ✅ apps/users/ solo gestión de usuarios
  ✅ apps/authentication/ autenticación completa
  ✅ Separación de responsabilidades clara
  ✅ CNST-001 cumplida (sin email)
  ✅ 3 preguntas de seguridad (NO 5)
  ✅ First login flow completo
  ✅ ALERTS pendientes (apps/alerts/ futuro)

Endpoints:
  apps/users/:
    ✅ /api/v1/users/users/ (CRUD)
    ✅ /api/v1/users/profile/
    ✅ /api/v1/users/settings/
  
  apps/authentication/:
    ✅ /api/v1/auth/login/
    ✅ /api/v1/auth/logout/
    ✅ /api/v1/auth/security-questions/
    ✅ /api/v1/auth/set-security-answers/
    ✅ /api/v1/auth/reset-password/
    ✅ /api/v1/sessions/
```

---

**Documento generado:** 2026-01-21  
**Versión:** 1.0.0 CORREGIDA  
**Estado:** ✅ LISTO PARA IMPLEMENTAR  
**Próximo paso:** Ejecutar Fase 1
