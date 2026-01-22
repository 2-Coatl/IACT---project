# 🔐 FASE 1: apps/authentication/ - Plan Completo v1.0.0

## 📋 INFORMACIÓN DEL PLAN

| Atributo | Valor |
|---|---|
| **Versión** | 1.0.0 |
| **Fecha** | 2026-01-21 |
| **Duración Total** | 8 horas |
| **Partes** | 7 partes incrementales |
| **Estado** | ✅ TODAS LAS CORRECCIONES APLICADAS |

---

## 🎯 CORRECCIONES APLICADAS EN v1.0.0

```yaml
✅ Models heredan de abstract models de core:
  - TimeStampedModel (created_at, updated_at)
  - SoftDeleteMixin (is_deleted, deleted_at)
  - CompleteBaseModel (combina los 3)
  - SoftDeleteManager (active(), deleted())

✅ Services heredan de BaseService:
  - Logging centralizado con self.log_*()
  
✅ Helpers reutilizan apps.utils:
  - get_client_ip(), get_user_agent()
  - NO duplicar código

✅ Exceptions SOLID refactorizadas:
  - Jerarquía por dominio
  - Open/Closed Principle
  - Attributes estándar (error_code, details)
  - Helper methods (to_dict, get_user_message)

✅ Permissions usan core:
  - RequiresFunctionPermission (RBAC)
  
✅ ViewSets usan mixins de core:
  - AuditMixin (created_by, updated_by auto)
  - PaginationControlMixin
```

---

## 📝 ÍNDICE DE PARTES

- [PARTE 1](#parte-1): Models + Constants + Exceptions SOLID (2.5h)
- [PARTE 2](#parte-2): Services Base (1.5h)
- [PARTE 3](#parte-3): Services Recovery + Session (1.5h)
- [PARTE 4](#parte-4): Serializers (1h)
- [PARTE 5](#parte-5): ViewSets + Permissions + URLs (1h)
- [PARTE 6](#parte-6): Tests Centralizados (1h)
- [PARTE 7](#parte-7): Fixtures + Integración (30min)

---

<a name="parte-1"></a>
## 📝 PARTE 1: Models + Constants + Exceptions SOLID (2.5h)

### Objetivos
1. Crear 4 modelos usando abstract models de core
2. Definir constants del módulo
3. Crear exceptions con jerarquía SOLID
4. Configurar apps.py
5. Commit incremental

---

### 1.1 Configurar apps/authentication/apps.py (10 min)

**Archivo:** `apps/authentication/apps.py`

```python
"""
Configuración de app authentication.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuración de app authentication.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    
    Responsabilidades:
    - Configuración de la app
    - Carga de signals (si se necesitan)
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Autenticación y Seguridad'
    
    def ready(self):
        """
        Inicialización cuando la app esté lista.
        
        SOLID SRP: Solo importar signals si existen.
        """
        # Importar signals si se crean en el futuro
        # import apps.authentication.signals  # noqa
        pass
```

---

### 1.2 Constants (15 min)

**Archivo:** `apps/authentication/constants.py`

```python
"""
Constantes para authentication.

CLEAN_CODE v3.0.1: Nombres en UPPER_CASE.
SOLID OCP: Valores configurables centralizados.

CNST-005: Lockout configurado.
CNST-001: Security questions configuradas.
"""

# ============================================================================
# LOGIN & LOCKOUT
# ============================================================================

MAX_LOGIN_ATTEMPTS = 5
"""
Máximo de intentos fallidos antes del bloqueo.

CNST-005: 5 intentos fallidos.
"""

LOCKOUT_DURATION_MINUTES = 15
"""
Duración del bloqueo en minutos.

CNST-005: 15 minutos de bloqueo.
"""

LOCKOUT_WINDOW_MINUTES = 15
"""
Ventana de tiempo para contar intentos fallidos.

Los intentos fuera de esta ventana no se cuentan.
"""

# ============================================================================
# SECURITY QUESTIONS
# ============================================================================

SECURITY_QUESTIONS_REQUIRED = 5
"""
Número de preguntas que el usuario debe responder.

CNST-001: 5 preguntas obligatorias (NO email).
"""

SECURITY_QUESTIONS_POOL_MIN = 10
"""
Mínimo de preguntas en el pool disponible.

Debe haber al menos 10 preguntas activas.
"""

# ============================================================================
# PASSWORD
# ============================================================================

PASSWORD_MIN_LENGTH = 8
"""
Longitud mínima de contraseña.

CNST-005: Mínimo 8 caracteres.
"""

PASSWORD_MAX_LENGTH = 128
"""
Longitud máxima de contraseña.

Django limit: 128 caracteres.
"""

# ============================================================================
# SESSION
# ============================================================================

SESSION_TIMEOUT_SECONDS = 3600
"""
Timeout de sesión en segundos.

Default: 1 hora (3600 segundos).
"""

SESSION_COOKIE_AGE = 3600
"""
Edad de la cookie de sesión en segundos.

Debe coincidir con SESSION_TIMEOUT_SECONDS.
"""

SESSION_SAVE_EVERY_REQUEST = True
"""
Guardar sesión en cada request.

CNST-010: Sessions en PostgreSQL.
"""

# ============================================================================
# AUDIT
# ============================================================================

LOG_FAILED_ATTEMPTS = True
"""
Si se deben loguear intentos fallidos.

CNST-031: Auditoría completa de todos los intentos.
"""

LOG_SUCCESSFUL_LOGINS = True
"""
Si se deben loguear logins exitosos.

CNST-031: Auditoría completa.
"""

LOG_LOGOUTS = True
"""
Si se deben loguear logouts.

CNST-031: Auditoría de sesiones.
"""

# ============================================================================
# CACHE KEYS
# ============================================================================

CACHE_KEY_LOCKOUT = 'auth:lockout:{username}'
"""
Template para cache key de lockout.

Formato: 'auth:lockout:john'
"""

CACHE_KEY_FAILED_ATTEMPTS = 'auth:failed_attempts:{username}'
"""
Template para cache key de intentos fallidos.

Formato: 'auth:failed_attempts:john'
"""
```

---

### 1.3 Exceptions SOLID (45 min)

**Archivo:** `apps/authentication/exceptions.py`

```python
"""
Exceptions para authentication con jerarquía SOLID.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
SOLID OCP: Jerarquía extensible sin modificar base.
SOLID SRP: Cada exception una responsabilidad clara.

Jerarquía:
- IACTBaseException (core)
  - AuthenticationBaseError (base authentication)
    - InvalidCredentialsError
    - AccountLockedError
    - UserInactiveError
    - SessionExpiredError
  - SecurityQuestionError (base security questions)
    - SecurityQuestionsNotConfiguredError
    - InvalidSecurityAnswersError
    - InsufficientSecurityQuestionsError
"""

from typing import Optional, Dict, Any
from rest_framework import status
from rest_framework.exceptions import APIException

from apps.core.exceptions import IACTBaseException


# ============================================================================
# BASE AUTHENTICATION EXCEPTIONS
# ============================================================================

class AuthenticationBaseError(APIException, IACTBaseException):
    """
    Excepción base para errores de autenticación.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    SOLID OCP: Base extensible sin modificación.
    SOLID SRP: Solo errores de autenticación.
    
    Atributos estándar:
    - error_code: Código único del error
    - details: Detalles adicionales (dict)
    - user_message: Mensaje para mostrar al usuario
    - log_message: Mensaje para logs
    
    Métodos:
    - to_dict(): Serializa a diccionario
    - get_user_message(): Mensaje amigable
    - should_log(): Si debe loguearse
    """
    
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Error de autenticación.'
    default_code = 'authentication_error'
    
    # SOLID OCP: Atributos que subclases pueden override
    error_code: str = 'AUTH_ERROR'
    should_notify_user: bool = True
    should_log_error: bool = True
    
    def __init__(
        self,
        detail: Optional[str] = None,
        code: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa exception.
        
        SOLID SRP: Solo inicialización.
        
        Args:
            detail: Mensaje de detalle
            code: Código de error HTTP
            error_code: Código único del error
            details: Detalles adicionales
        """
        super().__init__(detail, code)
        
        if error_code:
            self.error_code = error_code
        
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa a diccionario.
        
        SOLID SRP: Solo serialización.
        
        Returns:
            dict: Exception serializada
        
        Example:
            >>> error = InvalidCredentialsError()
            >>> error.to_dict()
            {
                'error_code': 'INVALID_CREDENTIALS',
                'message': 'Usuario o contraseña inválidos.',
                'details': {},
                'status_code': 401
            }
        """
        return {
            'error_code': self.error_code,
            'message': str(self.detail),
            'details': self.details,
            'status_code': self.status_code
        }
    
    def get_user_message(self) -> str:
        """
        Obtiene mensaje amigable para el usuario.
        
        SOLID SRP: Solo genera mensaje.
        
        Returns:
            str: Mensaje para mostrar al usuario
        """
        if self.should_notify_user:
            return str(self.detail)
        return 'Ha ocurrido un error. Por favor, intenta nuevamente.'
    
    def should_log(self) -> bool:
        """
        Determina si debe loguearse.
        
        SOLID SRP: Solo verifica logging.
        
        Returns:
            bool: True si debe loguearse
        """
        return self.should_log_error


class InvalidCredentialsError(AuthenticationBaseError):
    """
    Usuario o contraseña inválidos.
    
    SOLID OCP: Extiende AuthenticationBaseError sin modificarlo.
    SOLID SRP: Solo credenciales inválidas.
    """
    
    default_detail = 'Usuario o contraseña inválidos.'
    default_code = 'invalid_credentials'
    error_code = 'INVALID_CREDENTIALS'
    should_notify_user = True
    should_log_error = True


class AccountLockedError(AuthenticationBaseError):
    """
    Cuenta bloqueada por intentos fallidos.
    
    CNST-005: 5 intentos → 15 min lockout.
    """
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Cuenta bloqueada temporalmente por múltiples intentos fallidos.'
    default_code = 'account_locked'
    error_code = 'ACCOUNT_LOCKED'
    should_notify_user = True
    should_log_error = True


class UserInactiveError(AuthenticationBaseError):
    """
    Usuario inactivo.
    
    SOLID SRP: Solo usuario inactivo.
    """
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Usuario inactivo. Contacte al administrador.'
    default_code = 'user_inactive'
    error_code = 'USER_INACTIVE'
    should_notify_user = True
    should_log_error = True


class SessionExpiredError(AuthenticationBaseError):
    """
    Sesión expirada.
    
    SOLID SRP: Solo sesiones expiradas.
    """
    
    default_detail = 'Sesión expirada. Por favor, inicia sesión nuevamente.'
    default_code = 'session_expired'
    error_code = 'SESSION_EXPIRED'
    should_notify_user = True
    should_log_error = False  # No loguear, es esperado


# ============================================================================
# SECURITY QUESTION EXCEPTIONS
# ============================================================================

class SecurityQuestionError(APIException, IACTBaseException):
    """
    Excepción base para errores de preguntas de seguridad.
    
    SOLID OCP: Base extensible.
    SOLID SRP: Solo errores de security questions.
    
    CNST-001: Password reset SIN email, solo preguntas.
    """
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error en preguntas de seguridad.'
    default_code = 'security_question_error'
    error_code = 'SECURITY_QUESTION_ERROR'
    should_notify_user = True
    should_log_error = True
    
    def __init__(
        self,
        detail: Optional[str] = None,
        code: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Inicializa exception."""
        super().__init__(detail, code)
        
        if error_code:
            self.error_code = error_code
        
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa a diccionario."""
        return {
            'error_code': self.error_code,
            'message': str(self.detail),
            'details': self.details,
            'status_code': self.status_code
        }


class SecurityQuestionsNotConfiguredError(SecurityQuestionError):
    """
    Usuario no tiene preguntas de seguridad configuradas.
    
    CNST-001: 5 preguntas obligatorias.
    """
    
    default_detail = 'Debe configurar sus preguntas de seguridad primero.'
    default_code = 'security_questions_not_configured'
    error_code = 'SECURITY_QUESTIONS_NOT_CONFIGURED'


class InvalidSecurityAnswersError(SecurityQuestionError):
    """
    Respuestas de seguridad incorrectas.
    
    SOLID SRP: Solo respuestas incorrectas.
    """
    
    default_detail = 'Las respuestas de seguridad son incorrectas.'
    default_code = 'invalid_security_answers'
    error_code = 'INVALID_SECURITY_ANSWERS'


class InsufficientSecurityQuestionsError(SecurityQuestionError):
    """
    No hay suficientes preguntas de seguridad.
    
    CNST-001: Se requieren exactamente 5 preguntas.
    """
    
    default_detail = 'Se requieren exactamente 5 preguntas de seguridad.'
    default_code = 'insufficient_security_questions'
    error_code = 'INSUFFICIENT_SECURITY_QUESTIONS'


# ============================================================================
# RESUMEN EXCEPTIONS
# 
# Jerarquía SOLID:
#   IACTBaseException (core)
#   ├── AuthenticationBaseError
#   │   ├── InvalidCredentialsError
#   │   ├── AccountLockedError
#   │   ├── UserInactiveError
#   │   └── SessionExpiredError
#   └── SecurityQuestionError
#       ├── SecurityQuestionsNotConfiguredError
#       ├── InvalidSecurityAnswersError
#       └── InsufficientSecurityQuestionsError
# 
# Principios SOLID:
#   ✅ SRP: Cada exception una responsabilidad
#   ✅ OCP: Extensible sin modificar base
#   ✅ LSP: Subclases sustituibles
#   ✅ ISP: Interface segregation (métodos específicos)
#   ✅ DIP: Dependen de abstracción (IACTBaseException)
# 
# Features:
#   ✅ error_code único por exception
#   ✅ to_dict() para serialización
#   ✅ get_user_message() para UI
#   ✅ should_log() para logging
#   ✅ details dict para contexto adicional
# ============================================================================
```

---

### 1.4 Models con Abstract Models (1h 20min)

**Archivo:** `apps/authentication/models.py`

```python
"""
Modelos de autenticación usando abstract models de core.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
SOLID SRP: Cada modelo una responsabilidad.

CNST-001: NO email externo, solo preguntas de seguridad.
CNST-005: PBKDF2 password hashing.
CNST-031: Auditoría immutable.

CORRECCIONES v1.0.0:
✅ Heredar de TimeStampedModel (NO duplicar created_at, updated_at)
✅ Heredar de SoftDeleteMixin donde aplique
✅ Heredar de CompleteBaseModel para auditoría completa
✅ Usar SoftDeleteManager
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.models import (
    TimeStampedModel,
    SoftDeleteMixin,
    AuditedModel,
    CompleteBaseModel,
    SoftDeleteManager
)

User = get_user_model()


# ============================================================================
# LOGIN ATTEMPT
# ============================================================================

class LoginAttempt(TimeStampedModel):
    """
    Registro de intento de login (exitoso o fallido).
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    SOLID SRP: Solo registra intentos de login.
    
    CNST-031: Auditoría immutable de todos los intentos.
    
    Hereda de TimeStampedModel:
    - created_at: Timestamp del intento (attempted_at en plan original)
    - updated_at: Última actualización
    
    Campos:
    - user: FK a User (null si username no existe)
    - username: Username intentado
    - success: Si fue exitoso
    - ip_address: IP del intento
    - user_agent: User agent del navegador
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_attempts',
        db_column='iIdUsuario',
        verbose_name='Usuario',
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
        db_column='cIpAddress',
        help_text='IP desde donde se intentó el login'
    )
    
    user_agent = models.CharField(
        'User Agent',
        max_length=255,
        blank=True,
        db_column='cUserAgent',
        help_text='User agent del navegador'
    )
    
    # ✅ NO CREAR attempted_at - usar created_at de TimeStampedModel
    
    class Meta:
        db_table = 'tbl_intentos_login'
        verbose_name = 'Intento de Login'
        verbose_name_plural = 'Intentos de Login'
        ordering = ['-created_at']  # ✅ Usar created_at
        indexes = [
            models.Index(fields=['username', '-created_at'], name='idx_login_username'),
            models.Index(fields=['ip_address', '-created_at'], name='idx_login_ip'),
            models.Index(fields=['success', '-created_at'], name='idx_login_success'),
        ]
    
    def __str__(self):
        """String representation."""
        status = 'SUCCESS' if self.success else 'FAILED'
        return f"{self.username} - {status} - {self.created_at}"


# ============================================================================
# SECURITY QUESTION
# ============================================================================

class SecurityQuestion(TimeStampedModel, SoftDeleteMixin):
    """
    Pregunta de seguridad predefinida.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    SOLID SRP: Solo preguntas de seguridad.
    
    CNST-001: Pool de 10 preguntas, usuario responde 5.
    
    Hereda:
    - TimeStampedModel: created_at, updated_at
    - SoftDeleteMixin: is_deleted, deleted_at, delete(), restore()
    
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
    
    # ✅ NO CREAR created_at - heredado de TimeStampedModel
    # ✅ NO CREAR is_deleted, deleted_at - heredado de SoftDeleteMixin
    
    objects = SoftDeleteManager()  # ✅ Manager con active(), deleted()
    
    class Meta:
        db_table = 'tbl_preguntas_seguridad'
        verbose_name = 'Pregunta de Seguridad'
        verbose_name_plural = 'Preguntas de Seguridad'
        ordering = ['order', 'question']
        indexes = [
            models.Index(fields=['is_active', 'order'], name='idx_secq_active'),
            models.Index(fields=['is_deleted'], name='idx_secq_deleted'),
        ]
    
    def __str__(self):
        """String representation."""
        return self.question


# ============================================================================
# USER SECURITY ANSWER
# ============================================================================

class UserSecurityAnswer(CompleteBaseModel):
    """
    Respuesta de usuario a pregunta de seguridad.
    
    CLEAN_CODE v3.0.1: Nombre auto-documentado.
    SOLID SRP: Solo respuestas de seguridad.
    
    CNST-001: Hash PBKDF2, normalización lowercase.
    
    Hereda CompleteBaseModel:
    - TimeStampedModel: created_at, updated_at
    - SoftDeleteMixin: is_deleted, deleted_at, delete(), restore()
    - AuditedModel: created_by, updated_by
    
    Campos:
    - user: FK a User
    - question: FK a SecurityQuestion
    - answer_hash: Hash PBKDF2 de la respuesta
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='security_answers',
        db_column='iIdUsuario',
        verbose_name='Usuario'
    )
    
    question = models.ForeignKey(
        SecurityQuestion,
        on_delete=models.PROTECT,
        db_column='iIdPregunta',
        verbose_name='Pregunta'
    )
    
    answer_hash = models.CharField(
        'Hash Respuesta',
        max_length=255,
        db_column='cHashRespuesta',
        help_text='Hash PBKDF2 de la respuesta normalizada'
    )
    
    # ✅ NO CREAR created_at, updated_at - heredados de CompleteBaseModel
    # ✅ NO CREAR created_by, updated_by - heredados de CompleteBaseModel
    # ✅ NO CREAR is_deleted, deleted_at - heredados de CompleteBaseModel
    
    objects = SoftDeleteManager()  # ✅ Manager
    
    class Meta:
        db_table = 'tbl_respuestas_seguridad'
        verbose_name = 'Respuesta de Seguridad'
        verbose_name_plural = 'Respuestas de Seguridad'
        unique_together = [['user', 'question']]
        indexes = [
            models.Index(fields=['user'], name='idx_secanswer_user'),
            models.Index(fields=['is_deleted'], name='idx_secanswer_deleted'),
        ]
    
    def __str__(self):
        """String representation."""
        return f"{self.user.username} - {self.question.question[:30]}..."
    
    def set_answer(self, answer: str):
        """
        Hashea y guarda la respuesta.
        
        SOLID SRP: Solo hashea respuesta.
        
        Normalización: lowercase + strip
        Hash: PBKDF2 (mismo que passwords)
        
        Args:
            answer: Respuesta en texto plano
        
        Raises:
            ValidationError: Si respuesta vacía
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
        
        SOLID SRP: Solo verifica respuesta.
        
        Args:
            answer: Respuesta a verificar
        
        Returns:
            bool: True si correcta
        """
        normalized = answer.lower().strip()
        return check_password(normalized, self.answer_hash)


# ============================================================================
# SESSION LOG
# ============================================================================

class SessionLog(CompleteBaseModel):
    """
    Log de sesión de usuario.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    SOLID SRP: Solo logs de sesión.
    
    CNST-031: Auditoría de sesiones.
    CNST-010: Sessions en PostgreSQL.
    
    Hereda CompleteBaseModel:
    - TimeStampedModel: created_at (login_at), updated_at
    - SoftDeleteMixin: is_deleted, deleted_at
    - AuditedModel: created_by, updated_by
    
    Campos:
    - user: FK a User
    - session_key: Django session key
    - ip_address: IP del login
    - user_agent: User agent
    - logout_at: Timestamp de logout (null si activa)
    - is_active: Si la sesión está activa
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='session_logs',
        db_column='iIdUsuario',
        verbose_name='Usuario'
    )
    
    session_key = models.CharField(
        'Session Key',
        max_length=40,
        db_column='cSessionKey',
        help_text='Django session key'
    )
    
    ip_address = models.GenericIPAddressField(
        'IP Address',
        db_column='cIpAddress',
        help_text='IP desde donde se hizo login'
    )
    
    user_agent = models.CharField(
        'User Agent',
        max_length=255,
        blank=True,
        db_column='cUserAgent',
        help_text='User agent del navegador'
    )
    
    # ✅ login_at = created_at (heredado de TimeStampedModel)
    # ✅ NO CREAR login_at - usar created_at
    
    logout_at = models.DateTimeField(
        'Logout',
        null=True,
        blank=True,
        db_column='dtLogout',
        help_text='Fecha y hora de logout'
    )
    
    is_active = models.BooleanField(
        'Activa',
        default=True,
        db_column='bActiva',
        help_text='Si la sesión está activa'
    )
    
    # ✅ NO CREAR created_at, updated_at - heredados
    # ✅ NO CREAR created_by, updated_by - heredados
    # ✅ NO CREAR is_deleted, deleted_at - heredados
    
    objects = SoftDeleteManager()  # ✅ Manager
    
    class Meta:
        db_table = 'tbl_log_sesiones'
        verbose_name = 'Log de Sesión'
        verbose_name_plural = 'Logs de Sesiones'
        ordering = ['-created_at']  # ✅ login_at = created_at
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_session_user'),
            models.Index(fields=['session_key'], name='idx_session_key'),
            models.Index(fields=['is_active'], name='idx_session_active'),
            models.Index(fields=['is_deleted'], name='idx_session_deleted'),
        ]
    
    def __str__(self):
        """String representation."""
        return f"{self.user.username} - {self.created_at}"  # ✅ login_at = created_at
    
    @property
    def duration(self):
        """
        Duración de la sesión.
        
        SOLID SRP: Solo calcula duración.
        
        Returns:
            timedelta: Duración o None
        """
        if self.logout_at:
            return self.logout_at - self.created_at  # ✅ login_at = created_at
        elif self.is_active:
            return timezone.now() - self.created_at  # ✅
        return None


# ============================================================================
# RESUMEN MODELS
# 
# Total: 4 modelos
# 
# Models:
#   ✅ LoginAttempt (TimeStampedModel)
#   ✅ SecurityQuestion (TimeStampedModel + SoftDeleteMixin)
#   ✅ UserSecurityAnswer (CompleteBaseModel)
#   ✅ SessionLog (CompleteBaseModel)
# 
# SOLID Compliance:
#   ✅ SRP: Cada modelo una responsabilidad
#   ✅ OCP: Extensibles vía abstract models
#   ✅ DIP: Dependen de abstract models (core)
# 
# Herencia de core:
#   ✅ TimeStampedModel: created_at, updated_at
#   ✅ SoftDeleteMixin: is_deleted, deleted_at, delete(), restore()
#   ✅ CompleteBaseModel: Combina los 3
#   ✅ SoftDeleteManager: active(), deleted()
# 
# Campos eliminados (heredados):
#   ❌ attempted_at → created_at
#   ❌ login_at → created_at
#   ❌ created_at, updated_at (4 veces)
#   ❌ created_by, updated_by (2 veces)
#   ❌ is_deleted, deleted_at (2 veces)
# 
# Total líneas eliminadas: ~40 líneas
# ============================================================================
```

---

### 1.5 Commit PARTE 1

```bash
cd /tmp/iact-real
git add callcentersite/apps/authentication/
git commit -m "FASE 1 v1.0.0 - PARTE 1: Models + Constants + Exceptions SOLID

Implementación COMPLETA con TODAS las correcciones:

✅ Models con abstract models de core:
   - LoginAttempt: TimeStampedModel (-2 campos)
   - SecurityQuestion: TimeStampedModel + SoftDeleteMixin (-4 campos)
   - UserSecurityAnswer: CompleteBaseModel (-6 campos)
   - SessionLog: CompleteBaseModel (-6 campos)
   - SoftDeleteManager en todos los que aplican
   - Total: -40 líneas duplicadas eliminadas

✅ Constants configuradas:
   - MAX_LOGIN_ATTEMPTS = 5
   - LOCKOUT_DURATION_MINUTES = 15
   - SECURITY_QUESTIONS_REQUIRED = 5
   - Documentación CNST-001, CNST-005

✅ Exceptions SOLID refactorizadas:
   - Jerarquía por dominio (Authentication, SecurityQuestion)
   - AuthenticationBaseError con métodos: to_dict(), get_user_message(), should_log()
   - Open/Closed Principle: extensible sin modificar base
   - 8 exceptions: 4 authentication + 4 security questions
   - error_code único por exception
   - details dict para contexto

Compliance:
- CNST-001: SIN email, 5 preguntas
- CNST-005: PBKDF2 hashing
- CNST-031: Auditoría completa
- SOLID: SRP, OCP, LSP, DIP

Próximo: PARTE 2 - Services Base (LockoutService, AuthenticationService)"
```

---

<a name="parte-2"></a>
## 📝 PARTE 2: Services Base (1.5h)

### Objetivos
1. Implementar LockoutService heredando de BaseService
2. Implementar AuthenticationService heredando de BaseService
3. Usar helpers de apps.utils (get_client_ip, get_user_agent)
4. Commit incremental

---

### 2.1 LockoutService (40 min)

**Archivo:** `apps/authentication/services/lockout.py`

```python
"""
Servicio de bloqueo de cuentas por intentos fallidos.

CLEAN_CODE v3.0.1: Nombre que revela intención.
SOLID SRP: Solo gestión de lockout.

CNST-005: 5 intentos → 15 minutos de bloqueo.
"""

from typing import Optional
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from apps.core.services.base_service import BaseService  # ✅ Heredar de BaseService
from apps.authentication.constants import (
    MAX_LOGIN_ATTEMPTS,
    LOCKOUT_DURATION_MINUTES,
    LOCKOUT_WINDOW_MINUTES,
    CACHE_KEY_LOCKOUT,
    CACHE_KEY_FAILED_ATTEMPTS
)


class LockoutService(BaseService):  # ✅ Hereda de BaseService
    """
    Servicio de bloqueo de cuentas.
    
    SOLID SRP: Solo gestión de lockout.
    
    Responsabilidades:
    - Verificar si cuenta está bloqueada
    - Registrar intentos fallidos
    - Bloquear cuenta automáticamente
    - Desbloquear cuenta manualmente
    - Resetear contador de intentos
    
    CNST-005: 5 intentos fallidos → 15 min lockout.
    """
    
    def __init__(self):
        """Initialize service."""
        super().__init__()  # ✅ Llamar a super().__init__()
        self.max_attempts = MAX_LOGIN_ATTEMPTS
        self.lockout_duration = LOCKOUT_DURATION_MINUTES
        self.window_minutes = LOCKOUT_WINDOW_MINUTES
        
        self.log_info(f"LockoutService initialized: {self.max_attempts} attempts, {self.lockout_duration} min lockout")
    
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
            self.log_warning(f"Account '{username}' is locked until {locked_until}")  # ✅ Logging
            return True
        
        # Lockout expiró, limpiar cache
        cache.delete(cache_key)
        self.log_info(f"Lockout expired for account '{username}'")  # ✅ Logging
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
        
        self.log_warning(f"Failed attempt #{attempts} for account '{username}'")  # ✅ Logging
        
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
        self.log_info(f"Failed attempts counter reset for '{username}'")  # ✅ Logging
    
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
        
        self.log_info(f"Account '{username}' manually unlocked")  # ✅ Logging
    
    def _lock_account(self, username: str):
        """
        Bloquea la cuenta por el tiempo configurado.
        
        SOLID SRP: Solo bloquea cuenta.
        
        Args:
            username: Username a bloquear
        """
        cache_key = CACHE_KEY_LOCKOUT.format(username=username)
        locked_until = timezone.now() + timedelta(minutes=self.lockout_duration)
        
        # Guardar en cache hasta que expire el bloqueo
        cache.set(cache_key, locked_until, self.lockout_duration * 60)
        
        self.log_error(f"Account '{username}' LOCKED until {locked_until}")  # ✅ Logging error
```

---

### 2.2 AuthenticationService (50 min)

**Archivo:** `apps/authentication/services/authentication.py`

```python
"""
Servicio de autenticación de usuarios.

CLEAN_CODE v3.0.1: Nombre descriptivo.
SOLID SRP: Solo autenticación.

CNST-005: Token + Session, PBKDF2.
CNST-031: Auditoría completa.
"""

from typing import Dict
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token

from apps.core.services.base_service import BaseService  # ✅ BaseService
from apps.utils.helpers import get_client_ip, get_user_agent  # ✅ apps.utils
from apps.authentication.models import LoginAttempt, SessionLog
from apps.authentication.exceptions import (
    InvalidCredentialsError,
    AccountLockedError,
    UserInactiveError
)
from apps.authentication.services.lockout import LockoutService

User = get_user_model()


class AuthenticationService(BaseService):  # ✅ Hereda de BaseService
    """
    Servicio de autenticación de usuarios.
    
    SOLID SRP: Solo autenticación.
    
    Responsabilidades:
    - Login username/password
    - Logout
    - Registro de intentos (CNST-031)
    - Verificación de lockout
    - Gestión de tokens DRF
    - Gestión de sesiones
    
    CNST-005: PBKDF2 + Token + Session.
    CNST-031: Auditoría de todos los intentos.
    """
    
    def __init__(self):
        """Initialize service."""
        super().__init__()  # ✅ Llamar a super
        self.lockout_service = LockoutService()
        
        self.log_info("AuthenticationService initialized")
    
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
        # ✅ Usar helpers de apps.utils
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        self.log_info(f"Login attempt for '{username}' from {ip_address}")  # ✅ Logging
        
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
            
            self.log_error(f"Login blocked for '{username}' - {minutes} minutes remaining")
            
            raise AccountLockedError(
                detail=f"Cuenta bloqueada. Intenta en {minutes} minutos.",
                details={'locked_minutes': minutes}
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
            
            self.log_warning(f"Invalid credentials for '{username}' - {remaining} attempts remaining")
            
            if remaining > 0:
                raise InvalidCredentialsError(
                    detail=f"Credenciales inválidas. Te quedan {remaining} intentos.",
                    details={'attempts_remaining': remaining}
                )
            else:
                raise AccountLockedError(
                    detail="Cuenta bloqueada por múltiples intentos fallidos."
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
            
            self.log_warning(f"Inactive user '{username}' attempted login")
            
            raise UserInactiveError(
                detail=f"Usuario '{username}' inactivo. Contacte al administrador."
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
        
        self.log_info(f"Login successful for '{username}' - First login: {first_login}")
        
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
        
        username = request.user.username
        
        # Actualizar SessionLog
        self._update_session_log(
            session_key=request.session.session_key
        )
        
        # Logout Django
        logout(request)
        
        self.log_info(f"Logout successful for '{username}'")
        
        return True
    
    def _is_first_login(self, user) -> bool:
        """
        Detecta si es el primer login del usuario.
        
        SOLID SRP: Solo detecta first login.
        
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
        
        SOLID SRP: Solo registra intento.
        
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
        
        SOLID SRP: Solo crea log.
        
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
            is_active=True,
            created_by=user  # ✅ Auditoría
        )
    
    def _update_session_log(self, session_key: str):
        """
        Actualiza log al hacer logout.
        
        SOLID SRP: Solo actualiza log.
        
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

---

### 2.3 Services __init__.py

**Archivo:** `apps/authentication/services/__init__.py`

```python
"""
Services de authentication.

CLEAN_CODE v3.0.1: Exports centralizados.
"""

from apps.authentication.services.authentication import AuthenticationService
from apps.authentication.services.lockout import LockoutService

__all__ = [
    'AuthenticationService',
    'LockoutService',
]
```

---

### 2.4 Commit PARTE 2

```bash
cd /tmp/iact-real
git add callcentersite/apps/authentication/
git commit -m "FASE 1 v1.0.0 - PARTE 2: Services con BaseService

Implementación:

✅ LockoutService(BaseService):
   - Hereda de apps.core.services.BaseService
   - Logging con self.log_info/warning/error()
   - is_locked(), record_failed_attempt(), unlock_account()
   - 5 intentos → 15 min lockout (CNST-005)

✅ AuthenticationService(BaseService):
   - Hereda de BaseService
   - Usa get_client_ip() de apps.utils.helpers ✅
   - Usa get_user_agent() de apps.utils.helpers ✅
   - login_user(), logout_user()
   - First login detection
   - SessionLog con created_by (auditoría)
   - Logging completo con BaseService

✅ NO SE CREÓ utils.py (usar apps.utils) ✅

Compliance:
- CNST-005: Token + Session
- CNST-031: Auditoría completa
- SOLID: SRP (cada service una responsabilidad)
- Clean Code: logging, type hints

Próximo: PARTE 3 - RecoveryService + SessionService"
```

---

<a name="parte-3"></a>
## 📝 PARTE 3: Services Recovery + Session (1.5h)

### Objetivos
1. Implementar RecoveryService con BaseService
2. Implementar SessionService con BaseService
3. Actualizar services/__init__.py
4. Commit incremental

---

### 3.1 RecoveryService (50 min)

**Archivo:** `apps/authentication/services/recovery.py`

```python
"""
Servicio de recuperación de contraseña mediante preguntas de seguridad.

CLEAN_CODE v3.0.1: Nombre descriptivo.
SOLID SRP: Solo recuperación de contraseña.

CNST-001: SIN email externo, solo preguntas de seguridad.
"""

from typing import List, Dict
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from apps.core.services.base_service import BaseService  # ✅ BaseService
from apps.authentication.models import SecurityQuestion, UserSecurityAnswer
from apps.authentication.constants import (
    SECURITY_QUESTIONS_REQUIRED,
    SECURITY_QUESTIONS_POOL_MIN
)
from apps.authentication.exceptions import (
    SecurityQuestionsNotConfiguredError,
    InvalidSecurityAnswersError,
    InsufficientSecurityQuestionsError
)

User = get_user_model()


class RecoveryService(BaseService):  # ✅ Hereda de BaseService
    """
    Servicio de recuperación de contraseña.
    
    SOLID SRP: Solo recuperación mediante preguntas de seguridad.
    
    Responsabilidades:
    - Obtener preguntas disponibles
    - Configurar respuestas de seguridad (primera vez)
    - Verificar respuestas de seguridad
    - Resetear contraseña
    
    CNST-001: SIN email, 5 preguntas de seguridad obligatorias.
    """
    
    def __init__(self):
        """Initialize service."""
        super().__init__()  # ✅ Llamar super
        self.required_questions = SECURITY_QUESTIONS_REQUIRED
        
        self.log_info(f"RecoveryService initialized: {self.required_questions} questions required")
    
    def get_available_questions(self) -> List[SecurityQuestion]:
        """
        Obtiene preguntas de seguridad disponibles.
        
        SOLID SRP: Solo obtiene preguntas.
        
        Returns:
            List[SecurityQuestion]: Preguntas activas y no eliminadas
        
        Raises:
            InsufficientSecurityQuestionsError: Si hay menos de 10 preguntas
        """
        # ✅ Usar SoftDeleteManager.active()
        questions = SecurityQuestion.objects.active().filter(
            is_active=True
        ).order_by('order', 'question')
        
        count = questions.count()
        
        if count < SECURITY_QUESTIONS_POOL_MIN:
            self.log_error(f"Insufficient questions in pool: {count} (required: {SECURITY_QUESTIONS_POOL_MIN})")
            
            raise InsufficientSecurityQuestionsError(
                detail=f"Pool insuficiente de preguntas. Hay {count}, se requieren {SECURITY_QUESTIONS_POOL_MIN}.",
                details={'available': count, 'required': SECURITY_QUESTIONS_POOL_MIN}
            )
        
        self.log_info(f"Retrieved {count} available questions")
        
        return list(questions)
    
    def set_security_answers(
        self,
        user,
        answers_data: List[Dict]
    ) -> bool:
        """
        Configura respuestas de seguridad del usuario.
        
        CNST-001: Usuario debe responder exactamente 5 preguntas.
        
        Args:
            user: User object
            answers_data: Lista de dicts con:
                - question_id: int
                - answer: str
        
        Returns:
            bool: True si configuradas exitosamente
        
        Raises:
            InsufficientSecurityQuestionsError: Si no son 5 preguntas
        """
        # Validar cantidad
        if len(answers_data) != self.required_questions:
            self.log_warning(
                f"Invalid number of questions for user '{user.username}': "
                f"{len(answers_data)} (required: {self.required_questions})"
            )
            
            raise InsufficientSecurityQuestionsError(
                detail=f"Debe proporcionar exactamente {self.required_questions} preguntas.",
                details={
                    'provided': len(answers_data),
                    'required': self.required_questions
                }
            )
        
        # Eliminar respuestas anteriores (soft delete)
        # ✅ delete() hace soft delete automáticamente
        UserSecurityAnswer.objects.filter(user=user).delete()
        
        self.log_info(f"Deleted previous answers for user '{user.username}'")
        
        # Crear nuevas respuestas
        for answer_data in answers_data:
            question_id = answer_data['question_id']
            answer_text = answer_data['answer']
            
            # Obtener pregunta
            try:
                question = SecurityQuestion.objects.active().get(
                    id=question_id,
                    is_active=True
                )
            except SecurityQuestion.DoesNotExist:
                self.log_error(f"Question {question_id} not found or inactive")
                continue
            
            # Crear respuesta
            user_answer = UserSecurityAnswer(
                user=user,
                question=question,
                created_by=user  # ✅ Auditoría
            )
            
            # ✅ set_answer() hashea con PBKDF2
            user_answer.set_answer(answer_text)
            user_answer.save()
            
            self.log_info(f"Saved answer for question '{question.question[:30]}...' for user '{user.username}'")
        
        self.log_info(f"Security answers configured for user '{user.username}'")
        
        return True
    
    def verify_security_answers(
        self,
        username: str,
        answers_data: List[Dict]
    ) -> bool:
        """
        Verifica respuestas de seguridad del usuario.
        
        Args:
            username: Username
            answers_data: Lista de dicts con:
                - question_id: int
                - answer: str
        
        Returns:
            bool: True si todas las respuestas son correctas
        
        Raises:
            SecurityQuestionsNotConfiguredError: Si no tiene preguntas configuradas
            InvalidSecurityAnswersError: Si respuestas incorrectas
        """
        # Obtener usuario
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.log_warning(f"User '{username}' not found")
            raise InvalidSecurityAnswersError(
                detail="Usuario o respuestas incorrectas."
            )
        
        # Verificar que tenga preguntas configuradas
        # ✅ Usar active() para excluir soft deleted
        user_answers = UserSecurityAnswer.objects.active().filter(
            user=user
        )
        
        if user_answers.count() < self.required_questions:
            self.log_warning(f"User '{username}' has insufficient security questions configured")
            
            raise SecurityQuestionsNotConfiguredError(
                detail="Debe configurar sus preguntas de seguridad primero.",
                details={
                    'configured': user_answers.count(),
                    'required': self.required_questions
                }
            )
        
        # Verificar cada respuesta
        correct_count = 0
        
        for answer_data in answers_data:
            question_id = answer_data['question_id']
            answer_text = answer_data['answer']
            
            try:
                user_answer = user_answers.get(question_id=question_id)
                
                # ✅ check_answer() verifica hash PBKDF2
                if user_answer.check_answer(answer_text):
                    correct_count += 1
                else:
                    self.log_warning(f"Incorrect answer for question {question_id} from user '{username}'")
            
            except UserSecurityAnswer.DoesNotExist:
                self.log_warning(f"Question {question_id} not configured for user '{username}'")
        
        # Todas deben ser correctas
        if correct_count == len(answers_data):
            self.log_info(f"All security answers correct for user '{username}'")
            return True
        else:
            self.log_warning(
                f"Security answers verification failed for user '{username}': "
                f"{correct_count}/{len(answers_data)} correct"
            )
            
            raise InvalidSecurityAnswersError(
                detail="Las respuestas de seguridad son incorrectas.",
                details={
                    'correct': correct_count,
                    'total': len(answers_data)
                }
            )
    
    def reset_password_by_questions(
        self,
        username: str,
        answers_data: List[Dict],
        new_password: str
    ) -> bool:
        """
        Resetea contraseña después de verificar preguntas de seguridad.
        
        CNST-001: Password reset SIN email.
        
        Args:
            username: Username
            answers_data: Respuestas de seguridad
            new_password: Nueva contraseña
        
        Returns:
            bool: True si reset exitoso
        
        Raises:
            InvalidSecurityAnswersError: Si respuestas incorrectas
        """
        # Verificar respuestas
        self.verify_security_answers(username, answers_data)
        
        # Si llegó aquí, respuestas correctas
        user = User.objects.get(username=username)
        
        # Cambiar password
        # ✅ set_password() usa PBKDF2
        user.set_password(new_password)
        user.save()
        
        self.log_info(f"Password reset successful for user '{username}'")
        
        return True
```

---

### 3.2 SessionService (40 min)

**Archivo:** `apps/authentication/services/session.py`

```python
"""
Servicio de gestión de sesiones.

CLEAN_CODE v3.0.1: Nombre descriptivo.
SOLID SRP: Solo gestión de sesiones.

CNST-031: Auditoría de sesiones.
CNST-010: Sessions en PostgreSQL.
"""

from typing import List, Optional
from django.utils import timezone
from django.contrib.sessions.models import Session as DjangoSession

from apps.core.services.base_service import BaseService  # ✅ BaseService
from apps.authentication.models import SessionLog


class SessionService(BaseService):  # ✅ Hereda de BaseService
    """
    Servicio de gestión de sesiones.
    
    SOLID SRP: Solo sesiones.
    
    Responsabilidades:
    - Listar sesiones activas de usuario
    - Obtener historial de sesiones
    - Invalidar sesión específica
    - Invalidar todas las sesiones de un usuario
    
    CNST-031: Auditoría de sesiones.
    CNST-010: Sessions en PostgreSQL.
    """
    
    def __init__(self):
        """Initialize service."""
        super().__init__()  # ✅ Llamar super
        self.log_info("SessionService initialized")
    
    def get_active_sessions(self, user) -> List[SessionLog]:
        """
        Obtiene sesiones activas del usuario.
        
        Args:
            user: User object
        
        Returns:
            List[SessionLog]: Sesiones activas
        """
        # ✅ Usar active() para excluir soft deleted
        sessions = SessionLog.objects.active().filter(
            user=user,
            is_active=True
        ).order_by('-created_at')  # ✅ login_at = created_at
        
        count = sessions.count()
        self.log_info(f"Retrieved {count} active sessions for user '{user.username}'")
        
        return list(sessions)
    
    def get_session_history(
        self,
        user,
        limit: int = 10
    ) -> List[SessionLog]:
        """
        Obtiene historial de sesiones del usuario.
        
        Args:
            user: User object
            limit: Número máximo de registros
        
        Returns:
            List[SessionLog]: Historial de sesiones
        """
        # ✅ Usar active() (excluye soft deleted)
        sessions = SessionLog.objects.active().filter(
            user=user
        ).order_by('-created_at')[:limit]  # ✅ login_at = created_at
        
        count = sessions.count()
        self.log_info(f"Retrieved {count} session history records for user '{user.username}'")
        
        return list(sessions)
    
    def invalidate_session(
        self,
        session_key: str,
        user=None
    ) -> bool:
        """
        Invalida una sesión específica.
        
        SOLID SRP: Solo invalida sesión.
        
        Args:
            session_key: Django session key
            user: User object (opcional, para verificar ownership)
        
        Returns:
            bool: True si invalidada exitosamente
        """
        # Actualizar SessionLog
        filters = {'session_key': session_key, 'is_active': True}
        
        if user:
            filters['user'] = user
        
        # ✅ Usar active() para excluir soft deleted
        session_log = SessionLog.objects.active().filter(**filters).first()
        
        if session_log:
            session_log.logout_at = timezone.now()
            session_log.is_active = False
            session_log.save()
            
            self.log_info(f"SessionLog invalidated for session_key '{session_key}'")
        
        # Invalidar sesión de Django
        try:
            django_session = DjangoSession.objects.get(session_key=session_key)
            django_session.delete()
            
            self.log_info(f"Django session deleted for session_key '{session_key}'")
            
            return True
        
        except DjangoSession.DoesNotExist:
            self.log_warning(f"Django session not found for session_key '{session_key}'")
            return False
    
    def invalidate_all_user_sessions(
        self,
        user,
        except_current: Optional[str] = None
    ) -> int:
        """
        Invalida todas las sesiones de un usuario.
        
        Útil para:
        - Cambio de contraseña
        - Logout de todos los dispositivos
        - Seguridad (sesión comprometida)
        
        Args:
            user: User object
            except_current: Session key a excluir (sesión actual)
        
        Returns:
            int: Número de sesiones invalidadas
        """
        # Obtener sesiones activas
        filters = {'user': user, 'is_active': True}
        
        if except_current:
            filters['session_key__ne'] = except_current  # Excluir actual
        
        # ✅ Usar active()
        sessions = SessionLog.objects.active().filter(**filters)
        
        count = 0
        
        for session_log in sessions:
            if self.invalidate_session(session_log.session_key, user):
                count += 1
        
        self.log_info(
            f"Invalidated {count} sessions for user '{user.username}' "
            f"(except_current: {except_current})"
        )
        
        return count
    
    def get_session_details(
        self,
        session_key: str,
        user=None
    ) -> Optional[SessionLog]:
        """
        Obtiene detalles de una sesión.
        
        Args:
            session_key: Django session key
            user: User object (opcional, para verificar ownership)
        
        Returns:
            SessionLog: Detalles de la sesión o None
        """
        filters = {'session_key': session_key}
        
        if user:
            filters['user'] = user
        
        # ✅ Usar active()
        session_log = SessionLog.objects.active().filter(**filters).first()
        
        if session_log:
            self.log_info(f"Retrieved session details for session_key '{session_key}'")
        else:
            self.log_warning(f"Session not found for session_key '{session_key}'")
        
        return session_log
```

---

### 3.3 Actualizar services/__init__.py

**Archivo:** `apps/authentication/services/__init__.py`

```python
"""
Services de authentication.

CLEAN_CODE v3.0.1: Exports centralizados.
"""

from apps.authentication.services.authentication import AuthenticationService
from apps.authentication.services.lockout import LockoutService
from apps.authentication.services.recovery import RecoveryService  # ✅ Nuevo
from apps.authentication.services.session import SessionService  # ✅ Nuevo

__all__ = [
    'AuthenticationService',
    'LockoutService',
    'RecoveryService',  # ✅
    'SessionService',  # ✅
]
```

---

### 3.4 Commit PARTE 3

```bash
cd /tmp/iact-real
git add callcentersite/apps/authentication/
git commit -m "FASE 1 v1.0.0 - PARTE 3: RecoveryService + SessionService

Implementación completa:

✅ RecoveryService(BaseService):
   - Hereda de BaseService con logging
   - get_available_questions(): Usa active() de SoftDeleteManager
   - set_security_answers(): 5 preguntas con PBKDF2
   - verify_security_answers(): Verifica hashes
   - reset_password_by_questions(): Reset SIN email (CNST-001)
   
✅ SessionService(BaseService):
   - Hereda de BaseService con logging
   - get_active_sessions(): Lista sesiones activas
   - get_session_history(): Historial con limit
   - invalidate_session(): Invalida sesión específica
   - invalidate_all_user_sessions(): Logout todos los dispositivos
   
✅ Uso correcto de abstract models:
   - active() de SoftDeleteManager
   - created_at en vez de login_at
   - Auditoría con created_by

Compliance:
- CNST-001: Password reset SIN email ✅
- CNST-031: Auditoría de sesiones ✅
- SOLID: SRP, cada service una responsabilidad
- Clean Code: logging, type hints, docstrings

Próximo: PARTE 4 - Serializers"
```

---

<a name="parte-4"></a>
## 📝 PARTE 4: Serializers (1h)

### Objetivos
1. Crear serializers para auth (login, logout, change password)
2. Crear serializers para recovery (security questions, verify, reset)
3. Crear serializers para sessions
4. Commit incremental

---

### 4.1 Auth Serializers (20 min)

**Archivo:** `apps/authentication/serializers/auth.py`

```python
"""
Serializers para autenticación.

CLEAN_CODE v3.0.1: Nombres descriptivos.
SOLID SRP: Cada serializer una responsabilidad.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.authentication.constants import PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Serializer para login.
    
    SOLID SRP: Solo validación de credenciales de login.
    
    Fields:
    - username: Username (required)
    - password: Password (required)
    """
    
    username = serializers.CharField(
        required=True,
        max_length=150,
        help_text='Username del usuario'
    )
    
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Contraseña del usuario'
    )
    
    def validate_username(self, value):
        """
        Valida username.
        
        SOLID SRP: Solo validación de username.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Username no puede estar vacío")
        
        return value.strip()
    
    def validate_password(self, value):
        """
        Valida password.
        
        SOLID SRP: Solo validación de password.
        """
        if not value:
            raise serializers.ValidationError("Password no puede estar vacío")
        
        return value


class LogoutSerializer(serializers.Serializer):
    """
    Serializer para logout.
    
    SOLID SRP: Solo logout (sin campos).
    
    No requiere campos adicionales, usa request.user.
    """
    pass


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña.
    
    SOLID SRP: Solo cambio de password.
    
    Fields:
    - current_password: Password actual (required)
    - new_password: Password nueva (required)
    - confirm_password: Confirmación (required)
    """
    
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Contraseña actual'
    )
    
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        style={'input_type': 'password'},
        help_text='Nueva contraseña'
    )
    
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Confirmar nueva contraseña'
    )
    
    def validate(self, attrs):
        """
        Valida que las contraseñas coincidan.
        
        SOLID SRP: Solo validación de coincidencia.
        """
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden'
            })
        
        return attrs
```

---

### 4.2 Recovery Serializers (25 min)

**Archivo:** `apps/authentication/serializers/recovery.py`

```python
"""
Serializers para recuperación de contraseña.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
SOLID SRP: Cada serializer una responsabilidad.

CNST-001: Password reset SIN email, solo preguntas.
"""

from rest_framework import serializers

from apps.authentication.models import SecurityQuestion, UserSecurityAnswer
from apps.authentication.constants import (
    SECURITY_QUESTIONS_REQUIRED,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH
)


class SecurityQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer para SecurityQuestion.
    
    SOLID SRP: Solo representación de pregunta.
    
    Read-only para listar preguntas disponibles.
    """
    
    class Meta:
        model = SecurityQuestion
        fields = ['id', 'question', 'order']
        read_only_fields = ['id', 'question', 'order']


class SecurityAnswerInputSerializer(serializers.Serializer):
    """
    Serializer para input de respuesta de seguridad.
    
    SOLID SRP: Solo validación de answer input.
    
    Fields:
    - question_id: ID de la pregunta
    - answer: Respuesta del usuario
    """
    
    question_id = serializers.IntegerField(
        required=True,
        help_text='ID de la pregunta de seguridad'
    )
    
    answer = serializers.CharField(
        required=True,
        max_length=255,
        help_text='Respuesta a la pregunta'
    )
    
    def validate_answer(self, value):
        """
        Valida que la respuesta no esté vacía.
        
        SOLID SRP: Solo validación de answer.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("La respuesta no puede estar vacía")
        
        return value.strip()


class SetSecurityAnswersSerializer(serializers.Serializer):
    """
    Serializer para configurar respuestas de seguridad.
    
    SOLID SRP: Solo validación de configuración de respuestas.
    
    CNST-001: Usuario debe responder exactamente 5 preguntas.
    
    Fields:
    - answers: Lista de respuestas
    """
    
    answers = serializers.ListField(
        child=SecurityAnswerInputSerializer(),
        min_length=SECURITY_QUESTIONS_REQUIRED,
        max_length=SECURITY_QUESTIONS_REQUIRED,
        help_text=f'Lista de {SECURITY_QUESTIONS_REQUIRED} respuestas'
    )
    
    def validate_answers(self, value):
        """
        Valida que sean exactamente 5 preguntas únicas.
        
        SOLID SRP: Solo validación de answers.
        """
        # Validar cantidad
        if len(value) != SECURITY_QUESTIONS_REQUIRED:
            raise serializers.ValidationError(
                f"Debe proporcionar exactamente {SECURITY_QUESTIONS_REQUIRED} respuestas"
            )
        
        # Validar que no haya IDs duplicados
        question_ids = [answer['question_id'] for answer in value]
        
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError(
                "No puede responder la misma pregunta múltiples veces"
            )
        
        # Validar que las preguntas existan y estén activas
        # ✅ Usar active() de SoftDeleteManager
        existing_questions = SecurityQuestion.objects.active().filter(
            id__in=question_ids,
            is_active=True
        )
        
        if existing_questions.count() != len(question_ids):
            raise serializers.ValidationError(
                "Una o más preguntas no son válidas"
            )
        
        return value


class VerifySecurityAnswersSerializer(serializers.Serializer):
    """
    Serializer para verificar respuestas de seguridad.
    
    SOLID SRP: Solo validación de verificación.
    
    Fields:
    - username: Username del usuario
    - answers: Lista de respuestas
    """
    
    username = serializers.CharField(
        required=True,
        max_length=150,
        help_text='Username del usuario'
    )
    
    answers = serializers.ListField(
        child=SecurityAnswerInputSerializer(),
        min_length=SECURITY_QUESTIONS_REQUIRED,
        max_length=SECURITY_QUESTIONS_REQUIRED,
        help_text=f'Lista de {SECURITY_QUESTIONS_REQUIRED} respuestas'
    )


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer para reset de contraseña mediante preguntas.
    
    SOLID SRP: Solo validación de password reset.
    
    CNST-001: Reset SIN email, solo preguntas.
    
    Fields:
    - username: Username
    - answers: Respuestas de seguridad
    - new_password: Nueva contraseña
    - confirm_password: Confirmación
    """
    
    username = serializers.CharField(
        required=True,
        max_length=150,
        help_text='Username del usuario'
    )
    
    answers = serializers.ListField(
        child=SecurityAnswerInputSerializer(),
        min_length=SECURITY_QUESTIONS_REQUIRED,
        max_length=SECURITY_QUESTIONS_REQUIRED,
        help_text=f'Lista de {SECURITY_QUESTIONS_REQUIRED} respuestas'
    )
    
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        style={'input_type': 'password'},
        help_text='Nueva contraseña'
    )
    
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Confirmar nueva contraseña'
    )
    
    def validate(self, attrs):
        """
        Valida que las contraseñas coincidan.
        
        SOLID SRP: Solo validación de coincidencia.
        """
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden'
            })
        
        return attrs
```

---

### 4.3 Session Serializers (15 min)

**Archivo:** `apps/authentication/serializers/session.py`

```python
"""
Serializers para sesiones.

CLEAN_CODE v3.0.1: Nombres descriptivos.
SOLID SRP: Cada serializer una responsabilidad.
"""

from rest_framework import serializers

from apps.authentication.models import SessionLog


class SessionLogSerializer(serializers.ModelSerializer):
    """
    Serializer básico para SessionLog.
    
    SOLID SRP: Solo representación básica de sesión.
    
    Read-only para listar sesiones.
    """
    
    username = serializers.CharField(
        source='user.username',
        read_only=True
    )
    
    # ✅ login_at = created_at (heredado de TimeStampedModel)
    login_at = serializers.DateTimeField(
        source='created_at',
        read_only=True
    )
    
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionLog
        fields = [
            'id',
            'username',
            'session_key',
            'ip_address',
            'user_agent',
            'login_at',  # ✅ created_at
            'logout_at',
            'is_active',
            'duration_seconds'
        ]
        read_only_fields = fields
    
    def get_duration_seconds(self, obj):
        """
        Calcula duración en segundos.
        
        SOLID SRP: Solo cálculo de duración.
        """
        duration = obj.duration  # ✅ Property del modelo
        
        if duration:
            return int(duration.total_seconds())
        
        return None


class SessionLogDetailSerializer(SessionLogSerializer):
    """
    Serializer detallado para SessionLog.
    
    SOLID SRP: Solo representación detallada.
    
    Incluye campos de auditoría.
    """
    
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta(SessionLogSerializer.Meta):
        fields = SessionLogSerializer.Meta.fields + [
            'created_at',  # ✅ Timestamp
            'updated_at',  # ✅ Timestamp
            'created_by_username',  # ✅ Auditoría
        ]
        read_only_fields = fields
```

---

### 4.4 Serializers __init__.py

**Archivo:** `apps/authentication/serializers/__init__.py`

```python
"""
Serializers de authentication.

CLEAN_CODE v3.0.1: Exports centralizados.
"""

from apps.authentication.serializers.auth import (
    LoginSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
)

from apps.authentication.serializers.recovery import (
    SecurityQuestionSerializer,
    SecurityAnswerInputSerializer,
    SetSecurityAnswersSerializer,
    VerifySecurityAnswersSerializer,
    ResetPasswordSerializer,
)

from apps.authentication.serializers.session import (
    SessionLogSerializer,
    SessionLogDetailSerializer,
)

__all__ = [
    # Auth
    'LoginSerializer',
    'LogoutSerializer',
    'ChangePasswordSerializer',
    
    # Recovery
    'SecurityQuestionSerializer',
    'SecurityAnswerInputSerializer',
    'SetSecurityAnswersSerializer',
    'VerifySecurityAnswersSerializer',
    'ResetPasswordSerializer',
    
    # Session
    'SessionLogSerializer',
    'SessionLogDetailSerializer',
]
```

---

### 4.5 Commit PARTE 4

```bash
cd /tmp/iact-real
git add callcentersite/apps/authentication/
git commit -m "FASE 1 v1.0.0 - PARTE 4: Serializers

Implementación completa:

✅ Auth Serializers:
   - LoginSerializer: username + password
   - LogoutSerializer: sin campos
   - ChangePasswordSerializer: current + new + confirm

✅ Recovery Serializers:
   - SecurityQuestionSerializer: read-only para listar
   - SecurityAnswerInputSerializer: question_id + answer
   - SetSecurityAnswersSerializer: 5 respuestas validadas
   - VerifySecurityAnswersSerializer: username + answers
   - ResetPasswordSerializer: username + answers + new password
   - Usa active() de SoftDeleteManager ✅

✅ Session Serializers:
   - SessionLogSerializer: básico con duration_seconds
   - SessionLogDetailSerializer: incluye auditoría
   - login_at usa created_at (abstract model) ✅

Validaciones:
- PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH
- SECURITY_QUESTIONS_REQUIRED = 5
- No preguntas duplicadas
- Preguntas existen y están activas
- Passwords coinciden

SOLID:
- SRP: Cada serializer una responsabilidad
- Validaciones específicas en métodos validate_*

Próximo: PARTE 5 - ViewSets + Permissions + URLs"
```

---

<a name="parte-5"></a>
## 📝 PARTE 5: ViewSets + Permissions + URLs (1h)

### Objetivos
1. Crear AuthViewSet con RequiresFunctionPermission
2. Crear SessionViewSet con AuditMixin
3. Configurar URLs
4. Commit incremental

**Clave:** Usar permissions y mixins de apps.core

```python
from apps.core.permissions import RequiresFunctionPermission
from apps.core.mixins import AuditMixin

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    function_map = {
        'login': 'auth.login',  # permission_django ✅
        'logout': 'auth.logout',
    }
```

---

<a name="parte-6"></a>
## 📝 PARTE 6: Tests Centralizados (1h)

### Objetivos
1. Crear tests en tests/authentication/
2. Tests de models, services, serializers, viewsets
3. Commit incremental

**Ubicación:** `/tmp/iact-real/callcentersite/tests/authentication/`

---

<a name="parte-7"></a>
## 📝 PARTE 7: Fixtures + Integración (30min)

### Objetivos
1. Crear fixtures/security_questions.json
2. Configurar settings.INSTALLED_APPS
3. makemigrations + migrate
4. loaddata
5. Commit final + tag

**Tag final:** `git tag fase1-v1.0.0`

---

## ✅ RESUMEN FINAL v1.0.0

```yaml
Versión: 1.0.0
Estado: PLAN COMPLETO

Partes Completas (código listo):
  ✅ PARTE 1: Models + Constants + Exceptions SOLID
  ✅ PARTE 2: Services con BaseService

Partes Por Implementar (guía disponible):
  📝 PARTE 3: RecoveryService + SessionService
  📝 PARTE 4: Serializers
  📝 PARTE 5: ViewSets + Permissions + URLs
  📝 PARTE 6: Tests
  📝 PARTE 7: Fixtures + Integración

Correcciones Aplicadas:
  ✅ Abstract models de core
  ✅ BaseService con logging
  ✅ Helpers de apps.utils
  ✅ Exceptions SOLID con jerarquía
  ✅ RequiresFunctionPermission
  ✅ Mixins de ViewSets

Compliance:
  ✅ CNST-001, CNST-005, CNST-010, CNST-031
  ✅ SOLID: SRP, OCP, LSP, DIP
  ✅ Clean Code v3.0.1
```

**Versión:** 1.0.0  
**Estado:** ✅ PLAN COMPLETO  
**Próximo:** Implementar o generar código de PARTES 3-7
