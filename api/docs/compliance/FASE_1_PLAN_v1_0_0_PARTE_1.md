# 🔐 FASE 1 v1.0.0: apps/authentication/ - PLAN COMPLETO CORREGIDO

## 📋 INFORMACIÓN DEL PLAN

| Atributo | Valor |
|---|---|
| **Versión** | 1.0.0 |
| **Fecha** | 2026-01-21 |
| **Duración Total** | 8 horas |
| **Partes** | 7 partes incrementales |
| **Estado** | ✅ TODAS LAS CORRECCIONES APLICADAS |

**Versión Semántica:**
- **1** (Major): Primera versión completa con todas las correcciones
- **0** (Minor): Sin características adicionales sobre el plan base
- **0** (Patch): Sin correcciones de bugs

---

## 🎯 CORRECCIONES APLICADAS

```yaml
✅ Abstract Models:
  - LoginAttempt hereda TimeStampedModel
  - SecurityQuestion hereda TimeStampedModel + SoftDeleteMixin
  - UserSecurityAnswer hereda CompleteBaseModel
  - SessionLog hereda CompleteBaseModel

✅ Services:
  - Todos heredan de BaseService
  - Logging centralizado con self.log_*()

✅ Helpers:
  - get_client_ip() de apps.utils.helpers
  - get_user_agent() de apps.utils.helpers

✅ Exceptions SOLID:
  - Jerarquía mejorada con IACTBaseException
  - Open/Closed Principle aplicado
  - Context y metadata support

✅ Permissions:
  - RequiresFunctionPermission de apps.core
  - function_map con permission_django

✅ ViewSets:
  - AuditMixin de apps.core
  - Mixins reutilizables
```

---

## 📝 ÍNDICE DE PARTES

- [PARTE 1](#parte-1): Models + Constants + Exceptions SOLID (2h)
- [PARTE 2](#parte-2): Services Base con BaseService (1.5h)
- [PARTE 3](#parte-3): Services Recovery + Session (1.5h)
- [PARTE 4](#parte-4): Serializers (1h)
- [PARTE 5](#parte-5): ViewSets + URLs + Permissions (1h)
- [PARTE 6](#parte-6): Tests Centralizados (1h)
- [PARTE 7](#parte-7): Fixtures + Integración (30min)

---

<a name="parte-1"></a>
## 📝 PARTE 1: Models + Constants + Exceptions SOLID (2h)

### Objetivos
1. Crear 4 modelos usando **Abstract Models de apps/core**
2. Definir constants del módulo
3. Crear exceptions con **SOLID principles**
4. Configurar apps.py
5. Commit incremental

---

### 1.1 Configurar apps.py (10 min)

**Archivo:** `apps/authentication/apps.py`

```python
"""
Configuración de app authentication.

CLEAN_CODE v3.0.1: AppConfig auto-documentado.
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuración de app authentication.
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    SOLID SRP: Solo configuración de app.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Autenticación y Seguridad'
    
    def ready(self):
        """
        Inicialización cuando app está lista.
        
        SOLID OCP: Extensible sin modificar.
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

CLEAN_CODE v3.0.1: Nombres descriptivos, valores centralizados.
SOLID SRP: Solo definición de constantes.

CNST-005: Lockout configurado
CNST-001: Security questions configuradas
"""

# ============================================================================
# LOGIN & LOCKOUT
# ============================================================================

MAX_LOGIN_ATTEMPTS = 5
"""
Máximo de intentos fallidos antes del bloqueo.

CNST-005: Política de seguridad - 5 intentos.
"""

LOCKOUT_DURATION_MINUTES = 15
"""
Duración del bloqueo en minutos.

CNST-005: 15 minutos de bloqueo.
"""

LOCKOUT_WINDOW_MINUTES = 15
"""
Ventana de tiempo para contar intentos fallidos.

Los intentos fallidos se resetean después de esta ventana.
"""

# ============================================================================
# SECURITY QUESTIONS
# ============================================================================

SECURITY_QUESTIONS_REQUIRED = 5
"""
Número de preguntas que el usuario debe responder.

CNST-001: SIN email, 5 preguntas de seguridad obligatorias.
"""

SECURITY_QUESTIONS_POOL_MIN = 10
"""
Mínimo de preguntas en el pool disponible.

Debe haber al menos 10 preguntas para que el usuario elija 5.
"""

# ============================================================================
# PASSWORD
# ============================================================================

PASSWORD_MIN_LENGTH = 8
"""
Longitud mínima de contraseña.

CNST-005: Política de seguridad.
"""

PASSWORD_MAX_LENGTH = 128
"""Longitud máxima de contraseña."""

# ============================================================================
# SESSION
# ============================================================================

SESSION_TIMEOUT_SECONDS = 3600
"""
Timeout de sesión en segundos (1 hora).

CNST-010: Sessions en PostgreSQL.
"""

SESSION_COOKIE_AGE = 3600
"""Edad de la cookie de sesión."""

SESSION_SAVE_EVERY_REQUEST = True
"""Guardar sesión en cada request."""

# ============================================================================
# AUDIT
# ============================================================================

LOG_FAILED_ATTEMPTS = True
"""
Si se deben loguear intentos fallidos.

CNST-031: Auditoría immutable.
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
"""Template para cache key de lockout."""

CACHE_KEY_FAILED_ATTEMPTS = 'auth:failed_attempts:{username}'
"""Template para cache key de intentos fallidos."""

# ============================================================================
# ERROR CODES
# ============================================================================

ERROR_CODE_INVALID_CREDENTIALS = 'AUTH001'
"""Código de error: Credenciales inválidas."""

ERROR_CODE_ACCOUNT_LOCKED = 'AUTH002'
"""Código de error: Cuenta bloqueada."""

ERROR_CODE_USER_INACTIVE = 'AUTH003'
"""Código de error: Usuario inactivo."""

ERROR_CODE_SECURITY_QUESTIONS_NOT_CONFIGURED = 'AUTH004'
"""Código de error: Preguntas de seguridad no configuradas."""

ERROR_CODE_INVALID_SECURITY_ANSWERS = 'AUTH005'
"""Código de error: Respuestas de seguridad incorrectas."""

ERROR_CODE_INSUFFICIENT_SECURITY_QUESTIONS = 'AUTH006'
"""Código de error: Preguntas insuficientes."""
```

---

### 1.3 Exceptions SOLID (30 min)

**Archivo:** `apps/authentication/exceptions.py`

```python
"""
Exceptions para authentication con SOLID principles.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
SOLID OCP: Abierto para extensión, cerrado para modificación.
SOLID SRP: Cada exception una responsabilidad clara.
"""

from typing import Dict, Any, Optional
from rest_framework import status
from rest_framework.exceptions import APIException

from apps.core.exceptions import IACTBaseException


# ============================================================================
# BASE AUTHENTICATION EXCEPTION
# ============================================================================

class AuthenticationError(APIException, IACTBaseException):
    """
    Exception base para errores de autenticación.
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    SOLID OCP: Extensible mediante herencia.
    SOLID SRP: Solo representa error de autenticación.
    
    Hereda de:
    - APIException (DRF): Para respuestas HTTP automáticas
    - IACTBaseException: Para jerarquía consistente IACT
    
    Attributes:
        status_code (int): Código HTTP por defecto
        default_detail (str): Mensaje por defecto
        default_code (str): Código de error por defecto
        error_code (str): Código de error estructurado (ej: AUTH001)
        context (dict): Metadata adicional del error
    
    SOLID OCP: Subclases pueden extender sin modificar esta clase.
    
    Uso:
        raise AuthenticationError(
            detail="Error de autenticación",
            error_code="AUTH000",
            context={'username': 'john'}
        )
    """
    
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Error de autenticación.'
    default_code = 'authentication_error'
    error_code = 'AUTH000'
    
    def __init__(
        self,
        detail: Optional[str] = None,
        code: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa exception.
        
        SOLID OCP: Permite extensión mediante parámetros opcionales.
        SOLID LSP: Signature compatible con Exception base.
        
        Args:
            detail: Mensaje de error (usa default_detail si None)
            code: Código de error interno
            error_code: Código de error estructurado (ej: AUTH001)
            context: Metadata adicional
        """
        super().__init__(detail, code)
        
        if error_code:
            self.error_code = error_code
        
        self.context = context or {}
    
    def get_full_details(self) -> Dict[str, Any]:
        """
        Obtiene detalles completos del error.
        
        SOLID OCP: Subclases pueden extender este método.
        SOLID SRP: Solo construye diccionario de detalles.
        
        Returns:
            dict: Detalles completos con error_code y context
        
        Example:
            {
                'detail': 'Credenciales inválidas',
                'code': 'invalid_credentials',
                'error_code': 'AUTH001',
                'context': {'attempts_remaining': 3}
            }
        """
        details = super().get_full_details()
        
        # SOLID OCP: Agregar metadata sin modificar comportamiento base
        details['error_code'] = self.error_code
        
        if self.context:
            details['context'] = self.context
        
        return details


# ============================================================================
# SPECIFIC AUTHENTICATION EXCEPTIONS
# ============================================================================

class InvalidCredentialsError(AuthenticationError):
    """
    Credenciales de usuario inválidas.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    SOLID LSP: Completamente sustituible por AuthenticationError.
    
    Uso:
        raise InvalidCredentialsError(
            context={'attempts_remaining': 3}
        )
    """
    
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Usuario o contraseña inválidos.'
    default_code = 'invalid_credentials'
    error_code = 'AUTH001'


class AccountLockedError(AuthenticationError):
    """
    Cuenta bloqueada por intentos fallidos.
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    SOLID LSP: Sustituible por AuthenticationError.
    SOLID SRP: Solo representa bloqueo de cuenta.
    
    Uso:
        raise AccountLockedError(
            context={'locked_until': datetime_obj, 'minutes': 15}
        )
    """
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Cuenta bloqueada temporalmente por múltiples intentos fallidos.'
    default_code = 'account_locked'
    error_code = 'AUTH002'


class UserInactiveError(AuthenticationError):
    """
    Usuario inactivo en el sistema.
    
    CLEAN_CODE v3.0.1: Nombre auto-documentado.
    SOLID LSP: Sustituible por AuthenticationError.
    
    Uso:
        raise UserInactiveError(
            context={'username': 'john', 'deactivated_at': datetime_obj}
        )
    """
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Usuario inactivo. Contacte al administrador.'
    default_code = 'user_inactive'
    error_code = 'AUTH003'


class SecurityQuestionsNotConfiguredError(AuthenticationError):
    """
    Usuario no tiene preguntas de seguridad configuradas.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    SOLID LSP: Sustituible por AuthenticationError.
    SOLID SRP: Solo representa falta de configuración.
    
    CNST-001: Preguntas de seguridad son requeridas.
    
    Uso:
        raise SecurityQuestionsNotConfiguredError(
            context={'required': 5, 'configured': 0}
        )
    """
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Debe configurar sus preguntas de seguridad primero.'
    default_code = 'security_questions_not_configured'
    error_code = 'AUTH004'


class InvalidSecurityAnswersError(AuthenticationError):
    """
    Respuestas de seguridad incorrectas.
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    SOLID LSP: Sustituible por AuthenticationError.
    
    Uso:
        raise InvalidSecurityAnswersError(
            context={'attempts_remaining': 2}
        )
    """
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Las respuestas de seguridad son incorrectas.'
    default_code = 'invalid_security_answers'
    error_code = 'AUTH005'


class InsufficientSecurityQuestionsError(AuthenticationError):
    """
    No hay suficientes preguntas de seguridad configuradas.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    SOLID LSP: Sustituible por AuthenticationError.
    SOLID SRP: Solo representa insuficiencia de preguntas.
    
    CNST-001: Se requieren exactamente 5 preguntas.
    
    Uso:
        raise InsufficientSecurityQuestionsError(
            context={'required': 5, 'provided': 3}
        )
    """
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Se requieren exactamente 5 preguntas de seguridad.'
    default_code = 'insufficient_security_questions'
    error_code = 'AUTH006'


# ============================================================================
# RESUMEN EXCEPTIONS
# 
# SOLID Principles Aplicados:
# 
# SRP (Single Responsibility):
#   ✅ Cada exception representa un tipo de error específico
#   ✅ get_full_details() solo construye diccionario
# 
# OCP (Open/Closed):
#   ✅ AuthenticationError abierta para extensión (herencia)
#   ✅ Cerrada para modificación (no se cambia la clase base)
#   ✅ context permite agregar metadata sin modificar código
# 
# LSP (Liskov Substitution):
#   ✅ Todas las subclasses son sustituibles por AuthenticationError
#   ✅ Signature compatible con Exception base
#   ✅ Comportamiento consistente
# 
# ISP (Interface Segregation):
#   ✅ No se fuerzan métodos innecesarios en subclasses
#   ✅ Cada exception solo implementa lo que necesita
# 
# DIP (Dependency Inversion):
#   ✅ Depende de abstracciones (APIException, IACTBaseException)
#   ✅ No depende de implementaciones concretas
# 
# CLEAN_CODE v3.0.1:
#   ✅ Nombres auto-documentados
#   ✅ Docstrings completos
#   ✅ Ejemplos de uso
#   ✅ Type hints donde aplica
# ============================================================================
```

---

### 1.4 Models con Abstract Models (1h)

**Archivo:** `apps/authentication/models.py`

```python
"""
Modelos de autenticación y seguridad.

CLEAN_CODE v3.0.1: Nombres auto-documentados, reutilización.
SOLID SRP: Cada modelo una responsabilidad.
SOLID DRY: Usar abstract models de apps.core.

CNST-001: NO email externo, solo preguntas de seguridad
CNST-005: PBKDF2 password hashing
CNST-031: Auditoría immutable
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.utils import timezone

# ✅ Importar abstract models de core
from apps.core.models import (
    TimeStampedModel,
    SoftDeleteMixin,
    CompleteBaseModel,
    SoftDeleteManager
)

User = get_user_model()


# ============================================================================
# LOGIN ATTEMPT
# ============================================================================

class LoginAttempt(TimeStampedModel):  # ✅ Hereda created_at, updated_at
    """
    Registro de intento de login (exitoso o fallido).
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    SOLID SRP: Solo registra intentos de login.
    SOLID DRY: Reutiliza TimeStampedModel (NO duplicar timestamps).
    
    CNST-031: Auditoría immutable de todos los intentos.
    
    Hereda de TimeStampedModel:
    - created_at: Timestamp del intento (equivalente a attempted_at)
    - updated_at: Timestamp de última actualización
    
    Campos:
    - user: FK a User (null si username no existe)
    - username: Username que se intentó usar
    - success: Si fue exitoso
    - ip_address: IP del intento
    - user_agent: User agent del navegador
    
    Uso:
        LoginAttempt.objects.create(
            username='john',
            success=False,
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0...'
        )
        
        # created_at se setea automáticamente ✅
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
    # ✅ NO CREAR updated_at - heredado de TimeStampedModel
    
    class Meta:
        db_table = 'tbl_intentos_login'
        verbose_name = 'Intento de Login'
        verbose_name_plural = 'Intentos de Login'
        ordering = ['-created_at']  # ✅ Usar created_at (NO attempted_at)
        indexes = [
            models.Index(fields=['username', '-created_at'], name='idx_login_username'),
            models.Index(fields=['ip_address', '-created_at'], name='idx_login_ip'),
            models.Index(fields=['success', '-created_at'], name='idx_login_success'),
        ]
    
    def __str__(self):
        """String representation."""
        status_text = 'SUCCESS' if self.success else 'FAILED'
        return f"{self.username} - {status_text} - {self.created_at}"  # ✅


# ============================================================================
# SECURITY QUESTION
# ============================================================================

class SecurityQuestion(TimeStampedModel, SoftDeleteMixin):  # ✅
    """
    Pregunta de seguridad predefinida.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    SOLID SRP: Solo representa pregunta de seguridad.
    SOLID DRY: Reutiliza TimeStampedModel + SoftDeleteMixin.
    
    CNST-001: Pool de 10 preguntas, usuario responde 5.
    
    Hereda de TimeStampedModel:
    - created_at: Fecha de creación
    - updated_at: Fecha de actualización
    
    Hereda de SoftDeleteMixin:
    - is_deleted: Flag de eliminación lógica
    - deleted_at: Timestamp de eliminación
    - delete(): Método de soft delete
    - restore(): Método de restauración
    - hard_delete(): Eliminación física
    
    Campos:
    - question: Texto de la pregunta
    - is_active: Si está disponible para usar
    - order: Orden de presentación en UI
    
    Manager:
    - objects: SoftDeleteManager con active(), deleted()
    
    Uso:
        # Crear pregunta
        question = SecurityQuestion.objects.create(
            question="¿Cuál es tu color favorito?",
            is_active=True,
            order=1
        )
        
        # Soft delete
        question.delete()  # is_deleted=True ✅
        
        # Restaurar
        question.restore()  # is_deleted=False ✅
        
        # Query solo activas
        SecurityQuestion.objects.active()  # ✅
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
            models.Index(fields=['is_active', 'order'], name='idx_question_active'),
            models.Index(fields=['is_deleted'], name='idx_question_deleted'),  # ✅
        ]
    
    def __str__(self):
        """String representation."""
        return self.question


# ============================================================================
# USER SECURITY ANSWER
# ============================================================================

class UserSecurityAnswer(CompleteBaseModel):  # ✅ Hereda TODO
    """
    Respuesta de usuario a pregunta de seguridad.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    SOLID SRP: Solo representa respuesta de seguridad.
    SOLID DRY: Reutiliza CompleteBaseModel (timestamps + audit + soft delete).
    
    CNST-001: Hash PBKDF2, normalización lowercase.
    
    Hereda de CompleteBaseModel:
    - TimeStampedModel: created_at, updated_at
    - SoftDeleteMixin: is_deleted, deleted_at, delete(), restore()
    - AuditedModel: created_by, updated_by
    
    Campos:
    - user: FK a User
    - question: FK a SecurityQuestion
    - answer_hash: Hash PBKDF2 de la respuesta
    
    Manager:
    - objects: SoftDeleteManager
    
    Métodos:
    - set_answer(answer): Hashea y guarda respuesta
    - check_answer(answer): Verifica si respuesta es correcta
    
    Uso:
        # Crear respuesta
        answer = UserSecurityAnswer.objects.create(
            user=user,
            question=question,
            created_by=request.user  # ✅ Auto-audit
        )
        answer.set_answer("azul")
        answer.save()
        
        # Verificar
        is_correct = answer.check_answer("azul")  # True
        
        # Soft delete
        answer.delete()  # ✅ is_deleted=True
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
    
    # ✅ NO CREAR created_at, updated_at - heredado de TimeStampedModel
    # ✅ NO CREAR created_by, updated_by - heredado de AuditedModel
    # ✅ NO CREAR is_deleted, deleted_at - heredado de SoftDeleteMixin
    
    objects = SoftDeleteManager()  # ✅
    
    class Meta:
        db_table = 'tbl_respuestas_seguridad'
        verbose_name = 'Respuesta de Seguridad'
        verbose_name_plural = 'Respuestas de Seguridad'
        unique_together = [['user', 'question']]
        indexes = [
            models.Index(fields=['user'], name='idx_answer_user'),
            models.Index(fields=['is_deleted'], name='idx_answer_deleted'),
        ]
    
    def __str__(self):
        """String representation."""
        return f"{self.user.username} - {self.question.question[:30]}..."
    
    def set_answer(self, answer: str):
        """
        Hashea y guarda la respuesta.
        
        CLEAN_CODE v3.0.1: Nombre que revela intención.
        SOLID SRP: Solo hashea respuesta.
        
        Normalización: lowercase + strip
        Hash: PBKDF2 (mismo que passwords)
        
        Args:
            answer: Respuesta en texto plano
        
        Raises:
            ValidationError: Si respuesta vacía
        
        Example:
            answer.set_answer("Azul")
            # Guarda hash de "azul" (normalizado)
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
        
        CLEAN_CODE v3.0.1: Nombre auto-documentado.
        SOLID SRP: Solo verifica respuesta.
        
        Args:
            answer: Respuesta a verificar
        
        Returns:
            bool: True si correcta
        
        Example:
            is_correct = answer.check_answer("azul")  # True
            is_correct = answer.check_answer("rojo")  # False
        """
        normalized = answer.lower().strip()
        return check_password(normalized, self.answer_hash)


# ============================================================================
# SESSION LOG
# ============================================================================

class SessionLog(CompleteBaseModel):  # ✅ Hereda TODO
    """
    Log de sesión de usuario.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    SOLID SRP: Solo registra sesiones.
    SOLID DRY: Reutiliza CompleteBaseModel.
    
    CNST-031: Auditoría de sesiones
    CNST-010: Sessions en PostgreSQL
    
    Hereda de CompleteBaseModel:
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
    
    Manager:
    - objects: SoftDeleteManager
    
    Properties:
    - duration: Duración de la sesión
    
    Uso:
        # Crear log de sesión
        session_log = SessionLog.objects.create(
            user=user,
            session_key=request.session.session_key,
            ip_address='192.168.1.100',
            user_agent='Mozilla...',
            is_active=True,
            created_by=user  # ✅ Auto-audit
        )
        # created_at se setea automáticamente (login_at) ✅
        
        # Al hacer logout
        session_log.logout_at = timezone.now()
        session_log.is_active = False
        session_log.save()
        
        # Duración
        duration = session_log.duration  # timedelta ✅
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
        help_text='Timestamp de logout (null si activa)'
    )
    
    is_active = models.BooleanField(
        'Activa',
        default=True,
        db_column='bActiva',
        help_text='Si la sesión está activa'
    )
    
    # ✅ NO CREAR created_at, updated_at - heredado
    # ✅ NO CREAR created_by, updated_by - heredado
    # ✅ NO CREAR is_deleted, deleted_at - heredado
    
    objects = SoftDeleteManager()  # ✅
    
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
        return f"{self.user.username} - {self.created_at}"  # ✅ login_at
    
    @property
    def duration(self):
        """
        Duración de la sesión.
        
        CLEAN_CODE v3.0.1: Nombre auto-documentado.
        SOLID SRP: Solo calcula duración.
        
        Returns:
            timedelta: Duración o None
        
        Example:
            duration = session_log.duration
            minutes = duration.total_seconds() / 60
        """
        if self.logout_at:
            return self.logout_at - self.created_at  # ✅ login_at
        elif self.is_active:
            return timezone.now() - self.created_at  # ✅
        return None


# ============================================================================
# RESUMEN MODELS
# 
# Total: 4 modelos
# 
# Abstract Models Usados:
#   ✅ TimeStampedModel (created_at, updated_at)
#   ✅ SoftDeleteMixin (is_deleted, deleted_at, delete, restore)
#   ✅ CompleteBaseModel (timestamps + soft delete + audit)
#   ✅ SoftDeleteManager (active, deleted, with_deleted)
# 
# SOLID Principles:
#   ✅ SRP: Cada modelo una responsabilidad
#   ✅ DRY: NO duplicar timestamps, soft delete, audit
#   ✅ OCP: Extensible mediante abstract models
#   ✅ LSP: Abstract models sustituibles
# 
# CLEAN_CODE v3.0.1:
#   ✅ Nombres descriptivos
#   ✅ Docstrings completos
#   ✅ Type hints
#   ✅ Ejemplos de uso
# 
# Campos Eliminados (heredados):
#   ❌ attempted_at → usar created_at
#   ❌ login_at → usar created_at
#   ❌ created_at, updated_at (en 3 modelos)
#   ❌ created_by, updated_by (en 2 modelos)
#   ❌ is_deleted, deleted_at (en 3 modelos)
# 
# Total líneas ahorradas: ~60 líneas
# ============================================================================
```

---

### 1.5 Commit PARTE 1

```bash
cd /tmp/iact-real
git add callcentersite/apps/authentication/
git commit -m "FASE 1 v1.0.0 - PARTE 1: Models + Constants + Exceptions SOLID

Implementación COMPLETA con TODAS las correcciones:

✅ Models usando Abstract Models:
   - LoginAttempt: TimeStampedModel (created_at, NO attempted_at)
   - SecurityQuestion: TimeStampedModel + SoftDeleteMixin
   - UserSecurityAnswer: CompleteBaseModel (timestamps + audit + soft delete)
   - SessionLog: CompleteBaseModel (created_at = login_at)
   - SoftDeleteManager en todos los que aplica

✅ Constants centralizadas:
   - MAX_LOGIN_ATTEMPTS = 5
   - LOCKOUT_DURATION_MINUTES = 15
   - SECURITY_QUESTIONS_REQUIRED = 5
   - Error codes: AUTH001-AUTH006

✅ Exceptions SOLID:
   - AuthenticationError base con OCP (context, error_code)
   - 6 exceptions específicas (LSP compliant)
   - get_full_details() extensible
   - Hereda: APIException + IACTBaseException

SOLID Compliance:
- SRP: Cada clase una responsabilidad
- OCP: Abierto extensión, cerrado modificación
- LSP: Todas las exceptions sustituibles
- DRY: Reutilizar abstract models (-60 líneas)

Clean Code v3.0.1:
- Nombres auto-documentados
- Docstrings completos
- Type hints
- Ejemplos de uso

Próximo: PARTE 2 - Services con BaseService"
```

---

### Verificación PARTE 1

```bash
# Verificar archivos creados
ls -la apps/authentication/apps.py
ls -la apps/authentication/constants.py
ls -la apps/authentication/exceptions.py
ls -la apps/authentication/models.py

# Verificar sintaxis
python -m py_compile apps/authentication/apps.py
python -m py_compile apps/authentication/constants.py
python -m py_compile apps/authentication/exceptions.py
python -m py_compile apps/authentication/models.py

# Verificar imports
python manage.py check apps.authentication

# ✅ Si no hay errores, PARTE 1 completa
```

---

**Continúa en siguiente mensaje...**

PARTE 2: Services Base con BaseService
PARTE 3: Services Recovery + Session
PARTE 4: Serializers
PARTE 5: ViewSets + URLs + Permissions
PARTE 6: Tests Centralizados
PARTE 7: Fixtures + Integración

**Versión:** 1.0.0  
**Estado:** PARTE 1 DOCUMENTADA  
**Próximo:** Generar PARTES 2-7