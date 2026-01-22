# 🔐 FASE 1: apps/authentication/ - PLAN EN 7 PARTES

## INFORMACIÓN DEL PLAN

| Atributo | Valor |
|---|---|
| **Fecha** | 2026-01-21 |
| **Versión** | 1.0.0 |
| **Duración Total** | 8 horas |
| **Partes** | 7 partes incrementales |
| **Objetivo** | Implementar sistema de autenticación SIN email |

---

## 📋 ÍNDICE DE PARTES

- [PARTE 1](#parte-1): Models + Constants + Exceptions (2h)
- [PARTE 2](#parte-2): Utils + Services Base (1.5h)
- [PARTE 3](#parte-3): Services Recovery + Session (1.5h)
- [PARTE 4](#parte-4): Serializers (1h)
- [PARTE 5](#parte-5): ViewSets + URLs (1h)
- [PARTE 6](#parte-6): Tests Centralizados (1h)
- [PARTE 7](#parte-7): Fixtures + Integración (30min)

---

## ⚠️ IMPORTANTE: Uso de apps/core y apps/utils

```yaml
Reutilización de código existente:
  ✅ Heredar de apps.core.services.BaseService
  ✅ Usar apps.utils.helpers (get_client_ip, get_user_agent)
  ✅ NO crear utils.py en apps/authentication/
  ✅ Logging con self.log_info/warning/error de BaseService

Imports correctos:
  from apps.core.services.base_service import BaseService
  from apps.utils.helpers import get_client_ip, get_user_agent
  
  class MyService(BaseService):
      def __init__(self):
          super().__init__()
          self.log_info("Service initialized")
```

**Documento con código corregido:** `FASE_1_PARTE_2_CORREGIDA.md`

---

## 🎯 RESUMEN EJECUTIVO

### Características Principales

```yaml
CNST-001 Compliance:
  ✅ SIN email externo
  ✅ 5 preguntas de seguridad obligatorias
  ✅ Pool de 10 preguntas disponibles
  ✅ Password reset mediante preguntas

CNST-005 Compliance:
  ✅ PBKDF2 password hashing
  ✅ Token + Session dual auth
  ✅ Lockout: 5 intentos → 15 min

CNST-031 Compliance:
  ✅ LoginAttempt (todos los intentos)
  ✅ SessionLog (login/logout)
  ✅ Auditoría immutable

Nomenclatura:
  ✅ PermissionService (NO RBACService)
  ✅ permission_django (NO code)
  ✅ Clean Code v3.0.1
```

### Arquitectura

```
apps/authentication/
├── models.py (4 modelos)
├── constants.py
├── exceptions.py
├── utils.py
├── services/
│   ├── __init__.py
│   ├── authentication.py (AuthenticationService)
│   ├── lockout.py (LockoutService)
│   ├── recovery.py (RecoveryService)
│   └── session.py (SessionService)
├── serializers/
│   ├── __init__.py
│   ├── auth.py
│   ├── recovery.py
│   └── session.py
├── viewsets.py (AuthViewSet, SessionViewSet)
├── urls.py
└── fixtures/
    └── security_questions.json

tests/
└── authentication/
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    ├── test_serializers.py
    ├── test_viewsets.py
    └── test_integration.py
```

---

<a name="parte-1"></a>
## 📝 PARTE 1: Models + Constants + Exceptions (2h)

### Objetivos
1. Crear 4 modelos de authentication
2. Definir constants del módulo
3. Crear exceptions personalizadas
4. Configurar apps.py
5. Commit incremental

### Tareas Detalladas

#### 1.1 Configurar apps/authentication/apps.py (10 min)

```python
# apps/authentication/apps.py

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Configuración de app authentication."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Autenticación y Seguridad'
    
    def ready(self):
        """Importar signals cuando la app esté lista."""
        # Importar signals si se crean en el futuro
        # import apps.authentication.signals  # noqa
        pass
```

#### 1.2 Constants (15 min)

**Archivo:** `apps/authentication/constants.py`

```python
"""
Constantes para authentication.

CNST-005: Lockout configurado
CNST-001: Security questions configuradas
"""

# === LOGIN & LOCKOUT ===
MAX_LOGIN_ATTEMPTS = 5
"""Máximo de intentos fallidos antes del bloqueo."""

LOCKOUT_DURATION_MINUTES = 15
"""Duración del bloqueo en minutos."""

LOCKOUT_WINDOW_MINUTES = 15
"""Ventana de tiempo para contar intentos fallidos."""

# === SECURITY QUESTIONS ===
SECURITY_QUESTIONS_REQUIRED = 5
"""Número de preguntas que el usuario debe responder (CNST-001)."""

SECURITY_QUESTIONS_POOL_MIN = 10
"""Mínimo de preguntas en el pool disponible."""

# === PASSWORD ===
PASSWORD_MIN_LENGTH = 8
"""Longitud mínima de contraseña (CNST-005)."""

PASSWORD_MAX_LENGTH = 128
"""Longitud máxima de contraseña."""

# === SESSION ===
SESSION_TIMEOUT_SECONDS = 3600
"""Timeout de sesión en segundos (1 hora)."""

SESSION_COOKIE_AGE = 3600
"""Edad de la cookie de sesión."""

SESSION_SAVE_EVERY_REQUEST = True
"""Guardar sesión en cada request."""

# === AUDIT ===
LOG_FAILED_ATTEMPTS = True
"""Si se deben loguear intentos fallidos (CNST-031)."""

LOG_SUCCESSFUL_LOGINS = True
"""Si se deben loguear logins exitosos (CNST-031)."""

LOG_LOGOUTS = True
"""Si se deben loguear logouts (CNST-031)."""

# === CACHE KEYS ===
CACHE_KEY_LOCKOUT = 'auth:lockout:{username}'
"""Template para cache key de lockout."""

CACHE_KEY_FAILED_ATTEMPTS = 'auth:failed_attempts:{username}'
"""Template para cache key de intentos fallidos."""
```

#### 1.3 Exceptions (15 min)

**Archivo:** `apps/authentication/exceptions.py`

```python
"""
Exceptions personalizadas para authentication.
"""

from rest_framework.exceptions import APIException
from rest_framework import status


class AuthenticationError(APIException):
    """Base exception para errores de autenticación."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Error de autenticación.'
    default_code = 'authentication_error'


class InvalidCredentialsError(AuthenticationError):
    """Usuario o contraseña inválidos."""
    default_detail = 'Usuario o contraseña inválidos.'
    default_code = 'invalid_credentials'


class AccountLockedError(AuthenticationError):
    """Cuenta bloqueada por intentos fallidos."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Cuenta bloqueada temporalmente por múltiples intentos fallidos.'
    default_code = 'account_locked'


class UserInactiveError(AuthenticationError):
    """Usuario inactivo."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Usuario inactivo. Contacte al administrador.'
    default_code = 'user_inactive'


class SecurityQuestionsNotConfiguredError(APIException):
    """Usuario no tiene preguntas de seguridad configuradas."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Debe configurar sus preguntas de seguridad primero.'
    default_code = 'security_questions_not_configured'


class InvalidSecurityAnswersError(APIException):
    """Respuestas de seguridad incorrectas."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Las respuestas de seguridad son incorrectas.'
    default_code = 'invalid_security_answers'


class InsufficientSecurityQuestionsError(APIException):
    """No hay suficientes preguntas de seguridad configuradas."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Se requieren exactamente 5 preguntas de seguridad.'
    default_code = 'insufficient_security_questions'
```

#### 1.4 Models (1h 20min)

**Archivo:** `apps/authentication/models.py`

```python
"""
Modelos de autenticación y seguridad.

CNST-001: NO email externo, solo preguntas de seguridad
CNST-005: PBKDF2 password hashing
CNST-031: Auditoría immutable
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


class LoginAttempt(models.Model):
    """
    Registro de intento de login (exitoso o fallido).
    
    CNST-031: Auditoría immutable de todos los intentos.
    
    Campos:
    - user: FK a User (null si username no existe)
    - username: Username intentado
    - success: Si fue exitoso
    - ip_address: IP del intento
    - user_agent: User agent del navegador
    - attempted_at: Timestamp del intento
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_attempts',
        db_column='iIdUsuario',
        help_text='Usuario (null si no existe el username)'
    )
    
    username = models.CharField(
        'Username Intentado',
        max_length=150,
        db_column='cUsername',
        help_text='Username que se intentó usar'
    )
    
    success = models.BooleanField(
        'Exitoso',
        db_column='bExitoso',
        help_text='True si login fue exitoso'
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
        'Fecha Intento',
        auto_now_add=True,
        db_column='dtFechaIntento'
    )
    
    class Meta:
        db_table = 'tbl_intentos_login'
        verbose_name = 'Intento de Login'
        verbose_name_plural = 'Intentos de Login'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['username', '-attempted_at']),
            models.Index(fields=['ip_address', '-attempted_at']),
            models.Index(fields=['success', '-attempted_at']),
        ]
    
    def __str__(self):
        status = 'SUCCESS' if self.success else 'FAILED'
        return f"{self.username} - {status} - {self.attempted_at}"


class SecurityQuestion(models.Model):
    """
    Pregunta de seguridad predefinida.
    
    CNST-001: Pool de 10 preguntas, usuario responde 5.
    
    Campos:
    - question: Texto de la pregunta
    - is_active: Si está disponible
    - order: Orden de presentación
    """
    
    question = models.CharField(
        'Pregunta',
        max_length=255,
        unique=True,
        db_column='cPregunta',
        help_text='Texto de la pregunta de seguridad'
    )
    
    is_active = models.BooleanField(
        'Activa',
        default=True,
        db_column='bActiva',
        help_text='Si la pregunta está disponible para usar'
    )
    
    order = models.IntegerField(
        'Orden',
        default=0,
        db_column='iOrden',
        help_text='Orden de presentación en UI'
    )
    
    created_at = models.DateTimeField(
        'Fecha Creación',
        auto_now_add=True,
        db_column='dtFechaCreacion'
    )
    
    class Meta:
        db_table = 'tbl_preguntas_seguridad'
        verbose_name = 'Pregunta de Seguridad'
        verbose_name_plural = 'Preguntas de Seguridad'
        ordering = ['order', 'question']
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return self.question


class UserSecurityAnswer(models.Model):
    """
    Respuesta de usuario a pregunta de seguridad.
    
    CNST-001: Hash PBKDF2, normalización lowercase.
    
    Campos:
    - user: FK a User
    - question: FK a SecurityQuestion
    - answer_hash: Hash PBKDF2 de la respuesta
    - created_at: Fecha de creación
    - updated_at: Fecha de última actualización
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
        db_column='cHashRespuesta',
        help_text='Hash PBKDF2 de la respuesta normalizada'
    )
    
    created_at = models.DateTimeField(
        'Fecha Creación',
        auto_now_add=True,
        db_column='dtFechaCreacion'
    )
    
    updated_at = models.DateTimeField(
        'Fecha Actualización',
        auto_now=True,
        db_column='dtFechaActualizacion'
    )
    
    class Meta:
        db_table = 'tbl_respuestas_seguridad'
        verbose_name = 'Respuesta de Seguridad'
        verbose_name_plural = 'Respuestas de Seguridad'
        unique_together = [['user', 'question']]
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.question.question[:30]}..."
    
    def set_answer(self, answer: str):
        """
        Hashea y guarda la respuesta.
        
        Normalización: lowercase + strip
        Hash: PBKDF2 (mismo que passwords)
        
        Args:
            answer: Respuesta en texto plano
        """
        # Normalizar: lowercase, strip
        normalized = answer.lower().strip()
        
        # Validar que no esté vacía
        if not normalized:
            raise ValidationError("La respuesta no puede estar vacía")
        
        # Hash con PBKDF2
        self.answer_hash = make_password(normalized)
    
    def check_answer(self, answer: str) -> bool:
        """
        Verifica si la respuesta es correcta.
        
        Args:
            answer: Respuesta a verificar
        
        Returns:
            bool: True si correcta
        """
        normalized = answer.lower().strip()
        return check_password(normalized, self.answer_hash)


class SessionLog(models.Model):
    """
    Log de sesión de usuario.
    
    CNST-031: Auditoría de sesiones
    CNST-010: Sessions en DB
    
    Campos:
    - user: FK a User
    - session_key: Django session key
    - ip_address: IP del login
    - user_agent: User agent
    - login_at: Timestamp de login
    - logout_at: Timestamp de logout (null si activa)
    - is_active: Si la sesión está activa
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
        db_column='dtLogin'
    )
    
    logout_at = models.DateTimeField(
        'Logout',
        null=True,
        blank=True,
        db_column='dtLogout'
    )
    
    is_active = models.BooleanField(
        'Activa',
        default=True,
        db_column='bActiva'
    )
    
    class Meta:
        db_table = 'tbl_log_sesiones'
        verbose_name = 'Log de Sesión'
        verbose_name_plural = 'Logs de Sesiones'
        ordering = ['-login_at']
        indexes = [
            models.Index(fields=['user', '-login_at']),
            models.Index(fields=['session_key']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.login_at}"
    
    @property
    def duration(self):
        """Duración de la sesión."""
        if self.logout_at:
            return self.logout_at - self.login_at
        elif self.is_active:
            return timezone.now() - self.login_at
        return None
```

#### 1.5 Commit PARTE 1

```bash
cd /tmp/iact-real
git add callcentersite/apps/authentication/
git commit -m "FASE 1 - PARTE 1: Models + Constants + Exceptions

Implementación:
✅ 4 modelos creados:
   - LoginAttempt (CNST-031 auditoría)
   - SecurityQuestion (pool de 10)
   - UserSecurityAnswer (PBKDF2 hash)
   - SessionLog (CNST-010 sessions en DB)

✅ Constants configuradas:
   - MAX_LOGIN_ATTEMPTS = 5
   - LOCKOUT_DURATION_MINUTES = 15
   - SECURITY_QUESTIONS_REQUIRED = 5

✅ Exceptions personalizadas:
   - InvalidCredentialsError
   - AccountLockedError
   - UserInactiveError
   - SecurityQuestionsNotConfiguredError

Compliance:
- CNST-001: SIN email, 5 preguntas
- CNST-005: PBKDF2 hashing
- CNST-031: Auditoría completa

Próximo: PARTE 2 - Utils + Services Base"
```

### Verificación PARTE 1

```bash
# Verificar archivos creados
ls -la apps/authentication/models.py
ls -la apps/authentication/constants.py
ls -la apps/authentication/exceptions.py
ls -la apps/authentication/apps.py

# Verificar sintaxis
python -m py_compile apps/authentication/models.py
python -m py_compile apps/authentication/constants.py
python -m py_compile apps/authentication/exceptions.py

# ✅ Si no hay errores, PARTE 1 completa
```

---

<a name="parte-2"></a>
## 🛠️ PARTE 2: Utils + Services Base (1.5h)

### Objetivos
1. Crear utils.py con helpers
2. Implementar LockoutService
3. Implementar AuthenticationService
4. Commit incremental

### Tareas Detalladas

#### 2.1 Utils (20 min)

**Archivo:** `apps/authentication/utils.py`

```python
"""
Utilidades para authentication.
"""

from typing import Optional


def get_client_ip(request) -> str:
    """
    Obtiene la IP del cliente desde el request.
    
    Considera X-Forwarded-For para proxies.
    
    Args:
        request: HttpRequest
    
    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if x_forwarded_for:
        # Primera IP de la lista
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    
    return ip


def get_user_agent(request) -> str:
    """
    Obtiene el User Agent del request.
    
    Args:
        request: HttpRequest
    
    Returns:
        str: User agent string (max 255 chars)
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Truncar a 255 caracteres
    return user_agent[:255]


def normalize_answer(answer: str) -> str:
    """
    Normaliza respuesta de pregunta de seguridad.
    
    Reglas:
    - Lowercase
    - Strip whitespace
    
    Args:
        answer: Respuesta original
    
    Returns:
        str: Respuesta normalizada
    """
    return answer.lower().strip()


def generate_cache_key(prefix: str, identifier: str) -> str:
    """
    Genera cache key con formato estándar.
    
    Args:
        prefix: Prefijo (auth:lockout, auth:failed_attempts)
        identifier: Identificador (username, user_id)
    
    Returns:
        str: Cache key
    
    Example:
        generate_cache_key('auth:lockout', 'john')
        # 'auth:lockout:john'
    """
    return f"{prefix}:{identifier}"
```

#### 2.2 LockoutService (40 min)

**Archivo:** `apps/authentication/services/lockout.py`

```python
"""
Servicio de bloqueo de cuentas por intentos fallidos.

CNST-005: 5 intentos → 15 minutos de bloqueo
"""

from typing import Optional
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from apps.authentication.constants import (
    MAX_LOGIN_ATTEMPTS,
    LOCKOUT_DURATION_MINUTES,
    LOCKOUT_WINDOW_MINUTES,
    CACHE_KEY_LOCKOUT,
    CACHE_KEY_FAILED_ATTEMPTS
)


class LockoutService:
    """
    Servicio de bloqueo de cuentas.
    
    Responsabilidades:
    - Verificar si cuenta está bloqueada
    - Registrar intentos fallidos
    - Bloquear cuenta automáticamente
    - Desbloquear cuenta
    - Resetear contador de intentos
    
    CNST-005: 5 intentos fallidos → 15 min lockout
    """
    
    def __init__(self):
        """Initialize service."""
        self.max_attempts = MAX_LOGIN_ATTEMPTS
        self.lockout_duration = LOCKOUT_DURATION_MINUTES
        self.window_minutes = LOCKOUT_WINDOW_MINUTES
    
    def is_locked(self, username: str) -> bool:
        """
        Verifica si la cuenta está bloqueada.
        
        Args:
            username: Username a verificar
        
        Returns:
            bool: True si bloqueada
        """
        cache_key = CACHE_KEY_LOCKOUT.format(username=username)
        locked_until = cache.get(cache_key)
        
        if locked_until is None:
            return False
        
        # Verificar si aún está bloqueado
        if timezone.now() < locked_until:
            return True
        
        # Lockout expiró, limpiar cache
        cache.delete(cache_key)
        return False
    
    def get_lockout_time_remaining(self, username: str) -> Optional[timedelta]:
        """
        Obtiene tiempo restante de bloqueo.
        
        Args:
            username: Username
        
        Returns:
            timedelta: Tiempo restante, None si no está bloqueado
        """
        cache_key = CACHE_KEY_LOCKOUT.format(username=username)
        locked_until = cache.get(cache_key)
        
        if locked_until is None:
            return None
        
        now = timezone.now()
        if now < locked_until:
            return locked_until - now
        
        return None
    
    def record_failed_attempt(self, username: str) -> int:
        """
        Registra intento fallido y bloquea si alcanza el límite.
        
        Args:
            username: Username del intento fallido
        
        Returns:
            int: Número actual de intentos fallidos
        """
        cache_key = CACHE_KEY_FAILED_ATTEMPTS.format(username=username)
        
        # Incrementar contador
        attempts = cache.get(cache_key, 0) + 1
        
        # Guardar en cache por la ventana de tiempo
        cache.set(cache_key, attempts, self.window_minutes * 60)
        
        # Si alcanzó el máximo, bloquear
        if attempts >= self.max_attempts:
            self._lock_account(username)
        
        return attempts
    
    def get_failed_attempts_count(self, username: str) -> int:
        """
        Obtiene número de intentos fallidos actuales.
        
        Args:
            username: Username
        
        Returns:
            int: Número de intentos fallidos
        """
        cache_key = CACHE_KEY_FAILED_ATTEMPTS.format(username=username)
        return cache.get(cache_key, 0)
    
    def reset_failed_attempts(self, username: str):
        """
        Resetea el contador de intentos fallidos.
        
        Se llama después de login exitoso.
        
        Args:
            username: Username
        """
        cache_key = CACHE_KEY_FAILED_ATTEMPTS.format(username=username)
        cache.delete(cache_key)
    
    def unlock_account(self, username: str):
        """
        Desbloquea cuenta manualmente.
        
        Args:
            username: Username a desbloquear
        """
        lockout_key = CACHE_KEY_LOCKOUT.format(username=username)
        attempts_key = CACHE_KEY_FAILED_ATTEMPTS.format(username=username)
        
        cache.delete(lockout_key)
        cache.delete(attempts_key)
    
    def _lock_account(self, username: str):
        """
        Bloquea la cuenta por el tiempo configurado.
        
        Args:
            username: Username a bloquear
        """
        cache_key = CACHE_KEY_LOCKOUT.format(username=username)
        locked_until = timezone.now() + timedelta(minutes=self.lockout_duration)
        
        # Guardar en cache hasta que expire el bloqueo
        cache.set(cache_key, locked_until, self.lockout_duration * 60)
```

#### 2.3 AuthenticationService (50 min)

**Archivo:** `apps/authentication/services/authentication.py`

```python
"""
Servicio de autenticación de usuarios.

CNST-005: Token + Session, PBKDF2
CNST-031: Auditoría completa
"""

from typing import Dict, Optional
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token

from apps.authentication.models import LoginAttempt, SessionLog
from apps.authentication.exceptions import (
    InvalidCredentialsError,
    AccountLockedError,
    UserInactiveError
)
from apps.authentication.utils import get_client_ip, get_user_agent
from apps.authentication.services.lockout import LockoutService

User = get_user_model()


class AuthenticationService:
    """
    Servicio de autenticación de usuarios.
    
    Responsabilidades:
    - Login username/password
    - Logout
    - Registro de intentos (CNST-031)
    - Verificación de lockout
    - Gestión de tokens DRF
    - Gestión de sesiones
    
    CNST-005: PBKDF2 + Token + Session
    CNST-031: Auditoría de todos los intentos
    """
    
    def __init__(self):
        """Initialize service."""
        self.lockout_service = LockoutService()
    
    def login_user(
        self,
        request,
        username: str,
        password: str
    ) -> Dict:
        """
        Login de usuario.
        
        Flujo:
        1. Verificar lockout
        2. Autenticar con Django
        3. Verificar usuario activo
        4. Login Django
        5. Generar token DRF
        6. Registrar intento exitoso
        7. Crear SessionLog
        8. Resetear contador lockout
        
        Args:
            request: HttpRequest
            username: Username
            password: Password
        
        Returns:
            Dict con:
            - user: User object
            - token: DRF token key
            - session_key: Django session key
            - first_login: bool
        
        Raises:
            AccountLockedError: Cuenta bloqueada
            InvalidCredentialsError: Credenciales inválidas
            UserInactiveError: Usuario inactivo
        """
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # 1. Verificar lockout
        if self.lockout_service.is_locked(username):
            self._record_attempt(
                username=username,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            time_remaining = self.lockout_service.get_lockout_time_remaining(username)
            minutes = int(time_remaining.total_seconds() / 60) if time_remaining else 15
            
            raise AccountLockedError(
                f"Cuenta bloqueada. Intenta en {minutes} minutos."
            )
        
        # 2. Autenticar
        user = authenticate(
            request,
            username=username,
            password=password
        )
        
        if user is None:
            # Intento fallido
            self._record_attempt(
                username=username,
                user=None,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Incrementar contador lockout
            attempts = self.lockout_service.record_failed_attempt(username)
            remaining = self.lockout_service.max_attempts - attempts
            
            if remaining > 0:
                raise InvalidCredentialsError(
                    f"Credenciales inválidas. Te quedan {remaining} intentos."
                )
            else:
                raise AccountLockedError(
                    "Cuenta bloqueada por múltiples intentos fallidos."
                )
        
        # 3. Verificar activo
        if not user.is_active:
            self._record_attempt(
                username=username,
                user=user,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise UserInactiveError(
                f"Usuario '{username}' inactivo. Contacte al administrador."
            )
        
        # 4. Login Django
        login(request, user)
        
        # 5. Generar token DRF
        token, created = Token.objects.get_or_create(user=user)
        
        # 6. Registrar intento exitoso
        self._record_attempt(
            username=username,
            user=user,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 7. Log de sesión
        session_log = self._create_session_log(
            user=user,
            session_key=request.session.session_key,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 8. Resetear contador lockout
        self.lockout_service.reset_failed_attempts(username)
        
        # Detectar first login
        first_login = self._is_first_login(user)
        
        return {
            'user': user,
            'token': token.key,
            'session_key': request.session.session_key,
            'first_login': first_login
        }
    
    def logout_user(self, request) -> bool:
        """
        Logout de usuario.
        
        Args:
            request: HttpRequest
        
        Returns:
            bool: True si logout exitoso
        """
        if not request.user.is_authenticated:
            return False
        
        # Actualizar SessionLog
        self._update_session_log(
            session_key=request.session.session_key
        )
        
        # Logout Django
        logout(request)
        
        return True
    
    def _is_first_login(self, user) -> bool:
        """
        Detecta si es el primer login del usuario.
        
        Args:
            user: User object
        
        Returns:
            bool: True si es primer login
        """
        # Contar logins exitosos anteriores
        previous_logins = LoginAttempt.objects.filter(
            user=user,
            success=True
        ).count()
        
        # Si solo hay 1 (el actual), es el primero
        return previous_logins <= 1
    
    def _record_attempt(
        self,
        username: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        user=None
    ):
        """
        Registra intento de login (CNST-031).
        
        Args:
            username: Username intentado
            success: Si fue exitoso
            ip_address: IP
            user_agent: User agent
            user: User object (None si no existe)
        """
        LoginAttempt.objects.create(
            user=user,
            username=username,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def _create_session_log(
        self,
        user,
        session_key: str,
        ip_address: str,
        user_agent: str
    ) -> SessionLog:
        """
        Crea log de sesión.
        
        Args:
            user: User object
            session_key: Django session key
            ip_address: IP
            user_agent: User agent
        
        Returns:
            SessionLog: Log creado
        """
        return SessionLog.objects.create(
            user=user,
            session_key=session_key,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
    
    def _update_session_log(self, session_key: str):
        """
        Actualiza log al hacer logout.
        
        Args:
            session_key: Django session key
        """
        SessionLog.objects.filter(
            session_key=session_key,
            is_active=True
        ).update(
            logout_at=timezone.now(),
            is_active=False
        )
```

#### 2.4 Services __init__.py

**Archivo:** `apps/authentication/services/__init__.py`

```python
"""
Services de authentication.
"""

from apps.authentication.services.authentication import AuthenticationService
from apps.authentication.services.lockout import LockoutService

__all__ = [
    'AuthenticationService',
    'LockoutService',
]
```

#### 2.5 Commit PARTE 2

```bash
cd /tmp/iact-real
git add callcentersite/apps/authentication/
git commit -m "FASE 1 - PARTE 2: Utils + Services Base

Implementación:
✅ utils.py creado:
   - get_client_ip()
   - get_user_agent()
   - normalize_answer()

✅ LockoutService implementado:
   - is_locked()
   - record_failed_attempt()
   - unlock_account()
   - Lockout: 5 intentos → 15 min

✅ AuthenticationService implementado:
   - login_user() con lockout integration
   - logout_user()
   - Registro de LoginAttempt (CNST-031)
   - Creación de SessionLog
   - First login detection

Compliance:
- CNST-005: Token + Session
- CNST-031: Auditoría completa
- Cache: locmem para lockout

Próximo: PARTE 3 - RecoveryService + SessionService"
```

---

<a name="parte-3"></a>
## 🔄 PARTE 3: Services Recovery + Session (1.5h)

### Objetivos
1. Implementar RecoveryService (5 preguntas de seguridad)
2. Implementar SessionService
3. Actualizar services __init__.py
4. Commit incremental

### Tareas Detalladas

#### 3.1 RecoveryService (1h)

**Archivo:** `apps/authentication/services/recovery.py`

```python
"""
Servicio de recuperación de contraseñas SIN EMAIL.

CNST-001: NO email, solo preguntas de seguridad
"""

from typing import List, Dict
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.authentication.models import SecurityQuestion, UserSecurityAnswer
from apps.authentication.constants import SECURITY_QUESTIONS_REQUIRED
from apps.authentication.exceptions import (
    SecurityQuestionsNotConfiguredError,
    InvalidSecurityAnswersError,
    InsufficientSecurityQuestionsError
)

User = get_user_model()


class RecoveryService:
    """
    Servicio de recuperación de contraseñas.
    
    CNST-001: SIN email, solo preguntas de seguridad.
    Usuario debe tener 5 preguntas configuradas.
    
    Responsabilidades:
    - Obtener preguntas disponibles
    - Configurar respuestas de usuario
    - Verificar respuestas
    - Resetear password con preguntas
    """
    
    def get_available_questions(self) -> List[SecurityQuestion]:
        """
        Obtiene preguntas disponibles del pool.
        
        Returns:
            List[SecurityQuestion]: Pool de preguntas activas (10)
        """
        return list(
            SecurityQuestion.objects.filter(
                is_active=True
            ).order_by('order')
        )
    
    def has_security_answers_configured(self, user: User) -> bool:
        """
        Verifica si usuario tiene preguntas configuradas.
        
        Args:
            user: Usuario
        
        Returns:
            bool: True si tiene 5 preguntas configuradas
        """
        count = UserSecurityAnswer.objects.filter(user=user).count()
        return count >= SECURITY_QUESTIONS_REQUIRED
    
    @transaction.atomic
    def set_security_answers(
        self,
        user: User,
        answers: List[Dict[str, any]]
    ) -> bool:
        """
        Configura respuestas de seguridad del usuario.
        
        Args:
            user: Usuario
            answers: Lista de {question_id: int, answer: str}
        
        Returns:
            bool: True si configurado exitosamente
        
        Raises:
            InsufficientSecurityQuestionsError: No son 5 respuestas
            ValidationError: Pregunta inválida o respuesta vacía
        
        Example:
            answers = [
                {'question_id': 1, 'answer': 'Azul'},
                {'question_id': 3, 'answer': 'Firulais'},
                {'question_id': 5, 'answer': 'Santiago'},
                {'question_id': 7, 'answer': '2010'},
                {'question_id': 9, 'answer': 'García'},
            ]
        """
        # Validar cantidad
        if len(answers) != SECURITY_QUESTIONS_REQUIRED:
            raise InsufficientSecurityQuestionsError(
                f"Se requieren exactamente {SECURITY_QUESTIONS_REQUIRED} respuestas. "
                f"Recibidas: {len(answers)}"
            )
        
        # Validar IDs únicos
        question_ids = [a['question_id'] for a in answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValidationError("No se pueden repetir preguntas")
        
        # Eliminar respuestas anteriores
        UserSecurityAnswer.objects.filter(user=user).delete()
        
        # Crear nuevas respuestas
        for answer_data in answers:
            try:
                question = SecurityQuestion.objects.get(
                    id=answer_data['question_id'],
                    is_active=True
                )
            except SecurityQuestion.DoesNotExist:
                raise ValidationError(
                    f"Pregunta {answer_data['question_id']} no existe o no está activa"
                )
            
            # Crear respuesta
            answer_obj = UserSecurityAnswer(
                user=user,
                question=question
            )
            answer_obj.set_answer(answer_data['answer'])
            answer_obj.save()
        
        return True
    
    def verify_security_answers(
        self,
        username: str,
        answers: List[Dict[str, any]]
    ) -> bool:
        """
        Verifica respuestas de seguridad.
        
        Args:
            username: Username del usuario
            answers: Lista de {question_id: int, answer: str}
        
        Returns:
            bool: True si TODAS las respuestas son correctas
        
        Raises:
            User.DoesNotExist: Usuario no existe
            SecurityQuestionsNotConfiguredError: No tiene preguntas
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError(f"Usuario '{username}' no existe")
        
        # Verificar que tenga preguntas configuradas
        user_answers = UserSecurityAnswer.objects.filter(user=user)
        
        if user_answers.count() < SECURITY_QUESTIONS_REQUIRED:
            raise SecurityQuestionsNotConfiguredError(
                "Usuario no tiene preguntas de seguridad configuradas"
            )
        
        # Verificar cada respuesta
        correct_count = 0
        for answer_data in answers:
            try:
                user_answer = UserSecurityAnswer.objects.get(
                    user=user,
                    question_id=answer_data['question_id']
                )
                
                if user_answer.check_answer(answer_data['answer']):
                    correct_count += 1
                    
            except UserSecurityAnswer.DoesNotExist:
                # Pregunta no configurada para este usuario
                continue
        
        # TODAS deben ser correctas
        return correct_count == len(answers) == SECURITY_QUESTIONS_REQUIRED
    
    def reset_password_by_questions(
        self,
        username: str,
        answers: List[Dict[str, any]],
        new_password: str
    ) -> bool:
        """
        Resetea password usando preguntas de seguridad.
        
        CNST-001: NO email, solo preguntas
        
        Args:
            username: Username
            answers: Respuestas a las 5 preguntas
            new_password: Nueva contraseña
        
        Returns:
            bool: True si reset exitoso
        
        Raises:
            InvalidSecurityAnswersError: Respuestas incorrectas
            SecurityQuestionsNotConfiguredError: No tiene preguntas
        """
        # Verificar respuestas
        if not self.verify_security_answers(username, answers):
            raise InvalidSecurityAnswersError(
                "Las respuestas de seguridad son incorrectas"
            )
        
        # Cambiar password
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        
        # Opcional: Enviar ALERT interna (apps/alerts/)
        try:
            from apps.alerts.services import AlertService
            
            alert_service = AlertService()
            alert_service.send_system_alert(
                recipients=[user],
                subject="✅ Contraseña cambiada",
                body="Tu contraseña fue cambiada exitosamente mediante preguntas de seguridad.",
                priority='info'
            )
        except ImportError:
            # apps/alerts/ puede no existir aún
            pass
        
        return True
    
    def get_user_questions(self, user: User) -> List[SecurityQuestion]:
        """
        Obtiene preguntas configuradas por el usuario.
        
        Args:
            user: Usuario
        
        Returns:
            List[SecurityQuestion]: Preguntas configuradas
        """
        answers = UserSecurityAnswer.objects.filter(
            user=user
        ).select_related('question')
        
        return [answer.question for answer in answers]
```

#### 3.2 SessionService (30 min)

**Archivo:** `apps/authentication/services/session.py`

```python
"""
Servicio de gestión de sesiones.

CNST-010: Sessions en PostgreSQL
CNST-031: Auditoría de sesiones
"""

from typing import List, Optional
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.authentication.models import SessionLog

User = get_user_model()


class SessionService:
    """
    Servicio de gestión de sesiones.
    
    Responsabilidades:
    - Obtener sesiones activas
    - Invalidar sesiones
    - Obtener historial de sesiones
    - Gestionar logout forzado
    
    CNST-010: Sessions en DB
    CNST-031: Auditoría completa
    """
    
    def get_active_sessions(self, user: User) -> List[SessionLog]:
        """
        Obtiene sesiones activas del usuario.
        
        Args:
            user: Usuario
        
        Returns:
            List[SessionLog]: Sesiones activas
        """
        return list(
            SessionLog.objects.filter(
                user=user,
                is_active=True
            ).order_by('-login_at')
        )
    
    def get_session_history(
        self,
        user: User,
        limit: int = 10
    ) -> List[SessionLog]:
        """
        Obtiene historial de sesiones del usuario.
        
        Args:
            user: Usuario
            limit: Número máximo de sesiones
        
        Returns:
            List[SessionLog]: Historial de sesiones
        """
        return list(
            SessionLog.objects.filter(
                user=user
            ).order_by('-login_at')[:limit]
        )
    
    def invalidate_session(self, session_key: str) -> bool:
        """
        Invalida una sesión específica.
        
        Args:
            session_key: Django session key
        
        Returns:
            bool: True si invalidada
        """
        updated = SessionLog.objects.filter(
            session_key=session_key,
            is_active=True
        ).update(
            logout_at=timezone.now(),
            is_active=False
        )
        
        return updated > 0
    
    def invalidate_all_user_sessions(self, user: User) -> int:
        """
        Invalida todas las sesiones activas del usuario.
        
        Útil para logout forzado o cambio de contraseña.
        
        Args:
            user: Usuario
        
        Returns:
            int: Número de sesiones invalidadas
        """
        updated = SessionLog.objects.filter(
            user=user,
            is_active=True
        ).update(
            logout_at=timezone.now(),
            is_active=False
        )
        
        return updated
    
    def get_session_by_key(self, session_key: str) -> Optional[SessionLog]:
        """
        Obtiene sesión por session key.
        
        Args:
            session_key: Django session key
        
        Returns:
            SessionLog: Sesión o None
        """
        try:
            return SessionLog.objects.get(session_key=session_key)
        except SessionLog.DoesNotExist:
            return None
```

#### 3.3 Actualizar services/__init__.py

```python
"""
Services de authentication.
"""

from apps.authentication.services.authentication import AuthenticationService
from apps.authentication.services.lockout import LockoutService
from apps.authentication.services.recovery import RecoveryService
from apps.authentication.services.session import SessionService

__all__ = [
    'AuthenticationService',
    'LockoutService',
    'RecoveryService',
    'SessionService',
]
```

#### 3.4 Commit PARTE 3

```bash
cd /tmp/iact-real
git add callcentersite/apps/authentication/
git commit -m "FASE 1 - PARTE 3: RecoveryService + SessionService

Implementación:
✅ RecoveryService implementado:
   - get_available_questions() (pool de 10)
   - set_security_answers() (configurar 5)
   - verify_security_answers() (validar TODAS)
   - reset_password_by_questions() (SIN email)
   - CNST-001 compliant

✅ SessionService implementado:
   - get_active_sessions()
   - get_session_history()
   - invalidate_session()
   - invalidate_all_user_sessions()
   - CNST-010 + CNST-031 compliant

Compliance:
- CNST-001: Password reset SIN email
- CNST-010: Sessions en PostgreSQL
- CNST-031: SessionLog auditoría

Próximo: PARTE 4 - Serializers"
```

---

<a name="parte-4"></a>
## 📦 PARTE 4: Serializers (1h)

### Objetivos
1. Crear serializers de autenticación
2. Crear serializers de recovery
3. Crear serializers de sessions
4. Commit incremental

### Archivos a Crear
- `serializers/auth.py`
- `serializers/recovery.py`
- `serializers/session.py`
- `serializers/__init__.py`

*(Código de serializers...)*

---

<a name="parte-5"></a>
## 🎯 PARTE 5: ViewSets + URLs (1h)

### Objetivos
1. Crear AuthViewSet (9 endpoints)
2. Crear SessionViewSet (2 endpoints)
3. Configurar URLs
4. Commit incremental

### Endpoints
- POST /api/v1/auth/login/
- POST /api/v1/auth/logout/
- POST /api/v1/auth/change-password/
- GET /api/v1/auth/security-questions/
- POST /api/v1/auth/set-security-answers/
- POST /api/v1/auth/verify-security-answers/
- POST /api/v1/auth/reset-password/
- GET /api/v1/sessions/
- POST /api/v1/sessions/{id}/invalidate/

---

<a name="parte-6"></a>
## ✅ PARTE 6: Tests Centralizados (1h)

### Objetivos
1. Crear tests en `/tmp/iact-real/callcentersite/tests/authentication/`
2. Test models
3. Test services
4. Test serializers
5. Test ViewSets
6. Commit incremental

### Estructura Tests

```
tests/
└── authentication/
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    ├── test_serializers.py
    ├── test_viewsets.py
    └── test_integration.py
```

**IMPORTANTE:** Tests van en directorio centralizado, NO en apps/authentication/tests/

---

<a name="parte-7"></a>
## 🎁 PARTE 7: Fixtures + Integración (30min)

### Objetivos
1. Crear fixtures de 10 preguntas de seguridad
2. Registrar app en settings
3. Verificación final
4. Commit final

### Fixtures

**Archivo:** `apps/authentication/fixtures/security_questions.json`

10 preguntas en español:
1. ¿Cuál es tu color favorito?
2. ¿Cuál era el nombre de tu primera mascota?
3. ¿En qué ciudad naciste?
4. ¿En qué año terminaste la secundaria?
5. ¿Cuál es el apellido de soltera de tu madre?
6. ¿Cuál fue tu primer trabajo?
7. ¿Cuál es el nombre de tu mejor amigo de la infancia?
8. ¿Cuál es tu comida favorita?
9. ¿Cuál fue el modelo de tu primer automóvil?
10. ¿Cuál es el nombre de tu libro favorito?

---

## 📊 RESUMEN DE PARTES

| Parte | Nombre | Duración | Archivos | Commit |
|-------|--------|----------|----------|--------|
| 1 | Models + Constants + Exceptions | 2h | 4 archivos | ✅ |
| 2 | Utils + Services Base | 1.5h | 4 archivos | ✅ |
| 3 | Services Recovery + Session | 1.5h | 2 archivos | Pendiente |
| 4 | Serializers | 1h | 4 archivos | Pendiente |
| 5 | ViewSets + URLs | 1h | 2 archivos | Pendiente |
| 6 | Tests Centralizados | 1h | 5 archivos | Pendiente |
| 7 | Fixtures + Integración | 30min | 1 archivo | Pendiente |

**TOTAL: 8 horas**

---

## ✅ CHECKLIST COMPLETO - FASE 1

### PARTE 1: Models + Constants + Exceptions ✅
- [ ] apps/authentication/apps.py
- [ ] apps/authentication/constants.py
- [ ] apps/authentication/exceptions.py
- [ ] apps/authentication/models.py (4 modelos)
- [ ] Commit PARTE 1

### PARTE 2: Utils + Services Base ✅
- [ ] apps/authentication/utils.py
- [ ] apps/authentication/services/lockout.py
- [ ] apps/authentication/services/authentication.py
- [ ] apps/authentication/services/__init__.py
- [ ] Commit PARTE 2

### PARTE 3: Services Recovery + Session
- [ ] apps/authentication/services/recovery.py
- [ ] apps/authentication/services/session.py
- [ ] Actualizar services/__init__.py
- [ ] Commit PARTE 3

### PARTE 4: Serializers
- [ ] apps/authentication/serializers/auth.py
- [ ] apps/authentication/serializers/recovery.py
- [ ] apps/authentication/serializers/session.py
- [ ] apps/authentication/serializers/__init__.py
- [ ] Commit PARTE 4

### PARTE 5: ViewSets + URLs
- [ ] apps/authentication/viewsets.py
- [ ] apps/authentication/urls.py
- [ ] Commit PARTE 5

### PARTE 6: Tests Centralizados
- [ ] tests/authentication/__init__.py
- [ ] tests/authentication/test_models.py
- [ ] tests/authentication/test_services.py
- [ ] tests/authentication/test_serializers.py
- [ ] tests/authentication/test_viewsets.py
- [ ] tests/authentication/test_integration.py
- [ ] Commit PARTE 6

### PARTE 7: Fixtures + Integración
- [ ] apps/authentication/fixtures/security_questions.json
- [ ] Registrar en settings.INSTALLED_APPS
- [ ] python manage.py makemigrations authentication
- [ ] python manage.py loaddata security_questions
- [ ] Verificación final
- [ ] Commit final FASE 1

---

## 🚀 CÓMO EJECUTAR

### Secuencia Recomendada

```bash
# 1. Implementar PARTE 1 (2h)
# Crear models, constants, exceptions
# Commit

# 2. Implementar PARTE 2 (1.5h)
# Crear utils, LockoutService, AuthenticationService
# Commit

# 3. Implementar PARTE 3 (1.5h)
# Crear RecoveryService, SessionService
# Commit

# 4. Implementar PARTE 4 (1h)
# Crear serializers
# Commit

# 5. Implementar PARTE 5 (1h)
# Crear ViewSets y URLs
# Commit

# 6. Implementar PARTE 6 (1h)
# Crear tests en directorio centralizado
# Commit

# 7. Implementar PARTE 7 (30min)
# Fixtures, settings, migraciones
# Commit final
```

### Verificación por Parte

```bash
# Después de cada PARTE:

# 1. Verificar sintaxis
python -m py_compile apps/authentication/*.py

# 2. Ver git status
git status

# 3. Commit incremental
git add apps/authentication/
git commit -m "FASE 1 - PARTE X: ..."

# 4. Verificar commit
git log --oneline -1
```

### Al Finalizar FASE 1

```bash
# 1. Crear migraciones
python manage.py makemigrations authentication

# 2. Ver SQL (sin ejecutar)
python manage.py sqlmigrate authentication 0001

# 3. Cargar fixtures
python manage.py loaddata security_questions

# 4. Ejecutar tests
pytest tests/authentication/ -v

# 5. Tag de finalización
git tag fase1-authentication-complete

# ✅ FASE 1 COMPLETA
```

---

## 📝 NOTAS IMPORTANTES

### Tests Centralizados ⚠️
```
✅ CORRECTO:
/tmp/iact-real/callcentersite/tests/authentication/test_*.py

❌ INCORRECTO:
/tmp/iact-real/callcentersite/apps/authentication/tests/test_*.py
```

### Nomenclatura Correcta ⚠️
```python
# ✅ CORRECTO
from apps.access.services import PermissionService  # NO RBACService

permissions = PermissionService()
permissions.has_function(user, 'reports.view')  # NO 'RPT_VIEW'
```

### CNST-001 Compliance ⚠️
```python
# ❌ PROHIBIDO
def reset_password_by_email(email):
    send_mail(...)  # VIOLACIÓN CNST-001

# ✅ CORRECTO
def reset_password_by_questions(username, answers):
    recovery_service.verify_security_answers(...)
```

---

## 🎯 OBJETIVOS FINALES FASE 1

Al completar las 7 partes tendrás:

```yaml
Apps:
  ✅ apps/authentication/ funcional

Modelos:
  ✅ LoginAttempt (auditoría CNST-031)
  ✅ SecurityQuestion (pool de 10)
  ✅ UserSecurityAnswer (PBKDF2 hash)
  ✅ SessionLog (sessions en DB)

Services:
  ✅ AuthenticationService (login/logout)
  ✅ LockoutService (5 intentos → 15min)
  ✅ RecoveryService (5 preguntas SIN email)
  ✅ SessionService (gestión sesiones)

Endpoints:
  ✅ 9 endpoints REST de autenticación
  ✅ 2 endpoints de gestión de sesiones

Tests:
  ✅ Tests centralizados en tests/authentication/
  ✅ Cobertura completa

Fixtures:
  ✅ 10 preguntas de seguridad en español

Compliance:
  ✅ CNST-001 (SIN email)
  ✅ CNST-005 (PBKDF2 + Token + Session)
  ✅ CNST-010 (Sessions en PostgreSQL)
  ✅ CNST-031 (Auditoría completa)
```

---

## 📚 REFERENCIAS

- PLAN_EJECUTABLE_v2_0_0.md - Guía general
- PLAN_REMEDIACION_COMPLETO_v2_0_0.md - Código detallado
- CORRECCION_RBAC_NOMENCLATURA.md - permission_django vs code
- CLEAN_CODE_NOMENCLATURA_SERVICES.md - PermissionService vs RBACService

---

**Documento generado:** 2026-01-21  
**Versión:** 1.0.0  
**Estado:** ✅ PLAN COMPLETO EN 7 PARTES  
**Duración Total:** 8 horas  
**Próximo:** Ejecutar PARTE 1
