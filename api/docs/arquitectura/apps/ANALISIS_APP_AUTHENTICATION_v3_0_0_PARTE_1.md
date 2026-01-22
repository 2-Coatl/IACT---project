---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Authentication PARTE 1/3
categoria: arquitectura/apps
tema: apps/authentication/ - Fundamentos, Models y Session Management
autor: Claude Technical Analysis
tags: [authentication, login, sessions, security, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
estado: definitivo
parte: 1 de 3
relacionado:
  - ANALISIS_APP_ACCESS_v3_0_0.md (6 partes)
  - ANALISIS_APP_USERS_v3_0_0.md (4 partes)
  - ANALISIS_APP_AUTHENTICATION_v3_0_0_PARTE_2.md
  - ANALISIS_APP_AUTHENTICATION_v3_0_0_PARTE_3.md
replaces: []
---

# ANÁLISIS DE apps/authentication/ v3.0.0 - PARTE 1/3
## FUNDAMENTOS, MODELS Y SESSION MANAGEMENT

---

## 1. RESUMEN EJECUTIVO

### 1.1 Información General

```yaml
App: apps/authentication/
Tipo: MEDIA (3 partes)
Líneas estimadas: ~3,200 líneas código
Propósito: Autenticación y gestión de sesiones
Funciones RBAC: Ninguna (app pública)
Dependencias:
  - Django contrib.auth (core)
  - apps/users/ (User model)
  - apps/access/ (RBAC post-login)
  - apps/audit/ (logs de autenticación)
Tests: 35 tests estimados
Coverage objetivo: >90%
```

### 1.2 Responsabilidades Core

```yaml
Autenticación:
  ✅ Login (username/password)
  ✅ Logout
  ✅ Session management (DB-based, CNST-010)
  ✅ Token/Session dual auth
  ✅ Password validation (PBKDF2, CNST-005)
  ✅ Failed login tracking
  ✅ Account lockout (5 intentos)

Recuperación (SIN EMAIL - CNST-001):
  ✅ 3 Preguntas de seguridad
  ✅ Validación por respuestas
  ✅ Reset password (NO email)
  ❌ NO email recovery (CNST-001)
  ❌ NO SMS/OTP

Auditoría (CNST-031):
  ✅ Login attempts (success/fail)
  ✅ Logout tracking
  ✅ Session history
  ✅ IP tracking
  ✅ User agent logging

Restricciones Aplicadas:
  - CNST-001: NO email
  - CNST-005: Auth Token/Session, PBKDF2
  - CNST-010: Sessions en DB (NO Redis)
  - CNST-031: Auditoría completa
```

### 1.3 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│              apps/authentication/                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Models:                                            │
│  ├─ LoginAttempt (intentos login)                  │
│  ├─ SecurityQuestion (preguntas)                   │
│  ├─ UserSecurityAnswer (respuestas usuario)        │
│  └─ SessionLog (historial sesiones)                │
│                                                     │
│  Services:                                          │
│  ├─ AuthenticationService (login/logout)           │
│  ├─ SessionService (gestión sesiones DB)           │
│  ├─ RecoveryService (preguntas seguridad)          │
│  └─ LockoutService (bloqueo cuentas)               │
│                                                     │
│  API (DRF):                                         │
│  ├─ POST /api/v1/auth/login/                       │
│  ├─ POST /api/v1/auth/logout/                      │
│  ├─ POST /api/v1/auth/verify-questions/            │
│  ├─ POST /api/v1/auth/reset-password/              │
│  └─ GET  /api/v1/auth/sessions/                    │
│                                                     │
│  Integration:                                       │
│  ├─ Django contrib.auth (core)                     │
│  ├─ Django sessions (DB backend)                   │
│  ├─ apps/users/ (User model)                       │
│  ├─ apps/access/ (RBAC)                            │
│  └─ apps/audit/ (logs)                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 2. CLEAN CODE v3.0.1

```python
# ============================================================================
# CLASES - PascalCase
# ============================================================================

# Modelos
class LoginAttempt(models.Model):           # ✅ Intento de login
class SecurityQuestion(models.Model):       # ✅ Pregunta seguridad
class UserSecurityAnswer(models.Model):     # ✅ Respuesta usuario
class SessionLog(models.Model):             # ✅ Log de sesión

# Services
class AuthenticationService:                # ✅ Autenticación
class SessionService:                       # ✅ Sesiones
class RecoveryService:                      # ✅ Recuperación
class LockoutService:                       # ✅ Bloqueo cuentas

# Serializers
class LoginSerializer:                      # ✅ Login
class SecurityQuestionSerializer:          # ✅ Pregunta
class PasswordResetSerializer:             # ✅ Reset password

# ViewSets
class AuthViewSet:                          # ✅ API auth
class SessionViewSet:                       # ✅ API sesiones

# ============================================================================
# MÉTODOS - snake_case (inglés técnico)
# ============================================================================

# Authentication
def login(request, username, password):        # ✅ Login
def logout(request):                            # ✅ Logout
def authenticate_user(username, password):      # ✅ Autenticar
def create_session(user, request):             # ✅ Crear sesión
def invalidate_session(session_key):           # ✅ Invalidar

# Security
def check_lockout(username):                    # ✅ Verificar bloqueo
def record_login_attempt(username, success):   # ✅ Registrar intento
def lock_account(username):                     # ✅ Bloquear cuenta
def unlock_account(username):                   # ✅ Desbloquear

# Recovery (NO email - CNST-001)
def verify_security_answers(user, answers):    # ✅ Verificar respuestas
def reset_password_by_questions(user, pwd):    # ✅ Reset por preguntas
def get_security_questions(user):              # ✅ Obtener preguntas

# ============================================================================
# CONSTANTES - UPPER_SNAKE_CASE
# ============================================================================

MAX_LOGIN_ATTEMPTS = 5              # 5 intentos antes de bloqueo
LOCKOUT_DURATION_MINUTES = 15       # 15 minutos bloqueado
SESSION_TIMEOUT_SECONDS = 3600      # 1 hora timeout
PASSWORD_MIN_LENGTH = 8             # Mínimo 8 caracteres
SECURITY_QUESTIONS_REQUIRED = 3     # 3 preguntas obligatorias

# ============================================================================
# DATABASE - Húngaro (legacy)
# ============================================================================

# Tabla: tbl_intentos_login
iIdIntento                  # PK (bigint)       # ✅ ID intento
iIdUsuario                  # FK (int, null)    # ✅ Usuario (si existe)
cUsername                   # varchar(150)      # ✅ Username intentado
bSuccess                    # tinyint(1)        # ✅ Exitoso
cIpAddress                  # varchar(45)       # ✅ IP
cUserAgent                  # varchar(255)      # ✅ User agent
dtAttemptedAt               # datetime          # ✅ Timestamp

# Tabla: tbl_preguntas_seguridad
iIdPregunta                 # PK (int)          # ✅ ID pregunta
cQuestion                   # varchar(255)      # ✅ Pregunta
bIsActive                   # tinyint(1)        # ✅ Activa
iOrder                      # int               # ✅ Orden

# Tabla: tbl_respuestas_usuario
iIdRespuesta                # PK (int)          # ✅ ID respuesta
iIdUsuario                  # FK (int)          # ✅ Usuario
iIdPregunta                 # FK (int)          # ✅ Pregunta
cAnswerHash                 # varchar(255)      # ✅ Hash respuesta
dtCreatedAt                 # datetime          # ✅ Creación

# Tabla: tbl_log_sesiones
iIdLog                      # PK (bigint)       # ✅ ID log
iIdUsuario                  # FK (int)          # ✅ Usuario
cSessionKey                 # varchar(40)       # ✅ Session key
cIpAddress                  # varchar(45)       # ✅ IP
cUserAgent                  # varchar(255)      # ✅ User agent
dtLoginAt                   # datetime          # ✅ Login
dtLogoutAt                  # datetime          # ✅ Logout
bIsActive                   # tinyint(1)        # ✅ Sesión activa
```

---

## 3. RESTRICCIONES ARQUITECTÓNICAS

### 3.1 CNST-001: NO Email (CRÍTICO)

```yaml
CNST-001: NO Email Recovery (🔴 CRÍTICO)

Descripción:
  Sistema de autenticación SIN envío de emails.
  Recuperación SOLO por preguntas de seguridad.

Reglas:
  1. ❌ NO enviar emails de recuperación
  2. ❌ NO "reset link por email"
  3. ❌ NO verificación por email
  4. ✅ SÍ 3 preguntas de seguridad
  5. ✅ SÍ validación por respuestas
  6. ✅ SÍ reset password local

Implementación:
  # NO HACER:
  send_mail(
      subject='Reset Password',
      message='Click here...',
      ...
  )
  
  # SÍ HACER:
  class RecoveryService:
      def verify_security_answers(self, user, answers):
          # Verificar 3 respuestas correctas
          if all_correct:
              return True
      
      def reset_password_by_questions(self, user, new_pwd):
          user.set_password(new_pwd)
          user.save()

Justificación:
  - Restricción de negocio del cliente
  - Sin infraestructura SMTP
  - Política corporativa

Referencias:
  - RESTRICCIONES v1.0.0 PARTE 1, Sección 1.1
```

### 3.2 CNST-010: Sessions en DB (NO Redis)

```yaml
CNST-010: Database Sessions (🔴 CRÍTICO)

Descripción:
  Sesiones almacenadas en PostgreSQL, NO Redis.

Reglas:
  1. ❌ NO Redis para sessions
  2. ❌ NO Memcached para sessions
  3. ✅ SÍ django.contrib.sessions.backends.db
  4. ✅ SÍ django_session table
  5. ✅ SÍ cleanup sessions expired (APScheduler)

Implementación:
  # settings.py
  SESSION_ENGINE = 'django.contrib.sessions.backends.db'
  SESSION_COOKIE_AGE = 3600  # 1 hora
  SESSION_SAVE_EVERY_REQUEST = True
  SESSION_EXPIRE_AT_BROWSER_CLOSE = False
  
  # NO HACER:
  SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
  SESSION_ENGINE = 'redis_sessions.session'
  
  # Cleanup sessions (APScheduler)
  @scheduler.scheduled_job('cron', hour=3)
  def cleanup_expired_sessions():
      from django.core.management import call_command
      call_command('clearsessions')

Justificación:
  - No hay Redis en infraestructura
  - Compliance con CNST-010
  - On-premise tradicional

Referencias:
  - RESTRICCIONES v1.0.0 PARTE 1, Sección 1.2
```

### 3.3 CNST-005: Auth Segura

```yaml
CNST-005: Autenticación Segura (🟡 IMPORTANTE)

Descripción:
  Autenticación con Token/Session dual y PBKDF2.

Reglas:
  1. ✅ Django authentication backend (default)
  2. ✅ PBKDF2 password hasher (default Django)
  3. ✅ Token authentication (DRF)
  4. ✅ Session authentication (Django)
  5. ✅ HTTPS obligatorio producción
  6. ✅ CSRF habilitado

Implementación:
  # settings.py
  PASSWORD_HASHERS = [
      'django.contrib.auth.hashers.PBKDF2PasswordHasher',
      'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
  ]
  
  REST_FRAMEWORK = {
      'DEFAULT_AUTHENTICATION_CLASSES': [
          'rest_framework.authentication.TokenAuthentication',
          'rest_framework.authentication.SessionAuthentication',
      ],
  }
  
  # Producción
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True

Justificación:
  - Estándar Django (PBKDF2)
  - DRF best practices
  - Compliance seguridad

Referencias:
  - RESTRICCIONES v1.0.0 PARTE 1, Sección 2.2
```

---

## 4. MODELOS DJANGO

### 4.1 LoginAttempt

```python
"""
LoginAttempt model - Registro de intentos de login.

CNST-031: Auditoría completa de autenticación.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class LoginAttempt(models.Model):
    """
    Registro de intento de login (exitoso o fallido).
    
    CNST-031: Auditoría immutable de autenticación.
    
    Fields:
    - user: Usuario (null si no existe)
    - username: Username intentado
    - success: Exitoso o fallido
    - ip_address: IP origen
    - user_agent: User agent
    - attempted_at: Timestamp del intento
    
    Indexes:
    - username, attempted_at (lockout check)
    - user, attempted_at (historial usuario)
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_attempts',
        db_column='iIdUsuario',
        help_text='Usuario (null si no existe)'
    )
    
    username = models.CharField(
        'Username',
        max_length=150,
        db_column='cUsername',
        help_text='Username intentado en login'
    )
    
    success = models.BooleanField(
        'Exitoso',
        default=False,
        db_column='bSuccess',
        help_text='True si login exitoso'
    )
    
    ip_address = models.GenericIPAddressField(
        'IP Address',
        db_column='cIpAddress',
        help_text='IP origen del intento'
    )
    
    user_agent = models.CharField(
        'User Agent',
        max_length=255,
        blank=True,
        db_column='cUserAgent',
        help_text='User agent del navegador'
    )
    
    attempted_at = models.DateTimeField(
        'Intento',
        auto_now_add=True,
        db_column='dtAttemptedAt',
        help_text='Timestamp del intento'
    )
    
    class Meta:
        db_table = 'tbl_intentos_login'
        verbose_name = 'Intento de Login'
        verbose_name_plural = 'Intentos de Login'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['username', '-attempted_at']),
            models.Index(fields=['user', '-attempted_at']),
            models.Index(fields=['ip_address', '-attempted_at']),
        ]
    
    def __str__(self):
        """String representation."""
        status = "✅" if self.success else "❌"
        return f"{status} {self.username} - {self.attempted_at}"


class LoginAttemptManager(models.Manager):
    """Manager para LoginAttempt."""
    
    def recent_failed_attempts(self, username, minutes=15):
        """
        Obtiene intentos fallidos recientes.
        
        Args:
            username: Username a verificar
            minutes: Ventana de tiempo (default 15 min)
        
        Returns:
            QuerySet: Intentos fallidos en ventana
        """
        from datetime import timedelta
        
        cutoff = timezone.now() - timedelta(minutes=minutes)
        
        return self.filter(
            username=username,
            success=False,
            attempted_at__gte=cutoff
        )
```

### 4.2 SecurityQuestion

```python
class SecurityQuestion(models.Model):
    """
    Pregunta de seguridad para recuperación.
    
    CNST-001: Recuperación SIN email, solo preguntas.
    """
    
    question = models.CharField(
        'Pregunta',
        max_length=255,
        unique=True,
        db_column='cQuestion',
        help_text='Texto de la pregunta de seguridad'
    )
    
    is_active = models.BooleanField(
        'Activa',
        default=True,
        db_column='bIsActive',
        help_text='Si la pregunta está disponible'
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
        """String representation."""
        return self.question


class UserSecurityAnswer(models.Model):
    """
    Respuesta de usuario a pregunta de seguridad.
    
    CNST-001: 3 preguntas obligatorias por usuario.
    """
    
    user = models.ForeignKey(
        User,
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
        help_text='Hash PBKDF2 de la respuesta (case-insensitive)'
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
        """String representation."""
        return f"{self.user.username} - {self.question.question}"
    
    def set_answer(self, answer):
        """
        Hashea y guarda la respuesta.
        
        Args:
            answer: Respuesta en texto plano
        """
        from django.contrib.auth.hashers import make_password
        
        # Normalizar: lowercase, strip
        normalized = answer.lower().strip()
        
        # Hash con PBKDF2 (mismo que passwords)
        self.answer_hash = make_password(normalized)
    
    def check_answer(self, answer):
        """
        Verifica si la respuesta es correcta.
        
        Args:
            answer: Respuesta a verificar
        
        Returns:
            bool: True si correcta
        """
        from django.contrib.auth.hashers import check_password
        
        normalized = answer.lower().strip()
        return check_password(normalized, self.answer_hash)
```

### 4.3 SessionLog

```python
class SessionLog(models.Model):
    """
    Log de sesión de usuario.
    
    CNST-031: Auditoría de sesiones.
    CNST-010: Sessions en DB (django_session).
    """
    
    user = models.ForeignKey(
        User,
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
        db_column='bIsActive',
        help_text='True si sesión aún activa'
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
        """String representation."""
        return f"{self.user.username} - {self.login_at}"
    
    @property
    def duration(self):
        """Duración de la sesión."""
        if self.logout_at:
            return self.logout_at - self.login_at
        return None
```

---

## 5. CONSTANTS

```python
"""
Constants para apps/authentication/.
"""

# Login attempts
MAX_LOGIN_ATTEMPTS = 5              # Máximo intentos antes de bloqueo
LOCKOUT_DURATION_MINUTES = 15       # Duración del bloqueo
LOCKOUT_WINDOW_MINUTES = 15         # Ventana para contar intentos

# Session
SESSION_TIMEOUT_SECONDS = 3600      # 1 hora
SESSION_COOKIE_AGE = 3600           # 1 hora
SESSION_SAVE_EVERY_REQUEST = True   # Actualizar en cada request

# Password
PASSWORD_MIN_LENGTH = 8             # Mínimo 8 caracteres
PASSWORD_MAX_LENGTH = 128           # Máximo 128 caracteres

# Security Questions (CNST-001)
SECURITY_QUESTIONS_REQUIRED = 3     # 3 preguntas obligatorias
SECURITY_QUESTIONS_POOL_MIN = 10    # Mínimo 10 preguntas en pool

# Audit
LOG_FAILED_ATTEMPTS = True          # Log intentos fallidos
LOG_SUCCESSFUL_LOGINS = True        # Log logins exitosos
LOG_LOGOUTS = True                  # Log logouts
```

---

## 6. RESUMEN PARTE 1

```yaml
Modelos (4):
  ✅ LoginAttempt (intentos login)
  ✅ SecurityQuestion (preguntas)
  ✅ UserSecurityAnswer (respuestas)
  ✅ SessionLog (logs sesiones)

Restricciones Aplicadas (3):
  ✅ CNST-001: NO email (preguntas seguridad)
  ✅ CNST-010: Sessions DB (NO Redis)
  ✅ CNST-031: Auditoría completa

Configuration:
  ✅ SESSION_ENGINE = db
  ✅ PBKDF2 password hasher
  ✅ Token + Session auth
  ✅ 3 preguntas seguridad

Líneas código: ~650 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 2/3: Services y Authentication Logic**

Contenido:
- ✅ AuthenticationService (login/logout)
- ✅ SessionService (gestión sesiones DB)
- ✅ RecoveryService (preguntas seguridad)
- ✅ LockoutService (bloqueo cuentas)
- ✅ Utils (8 helpers)
- ✅ Exceptions (5 custom)

**Estimado:** ~1,200 líneas, 3 horas

---

**Fin de PARTE 1/3**
