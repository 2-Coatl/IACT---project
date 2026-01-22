---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Authentication PARTE 2/3
categoria: arquitectura/apps
tema: apps/authentication/ - Services y Authentication Logic
autor: Claude Technical Analysis
tags: [authentication, services, recovery, lockout, security]
estado: definitivo
parte: 2 de 3
relacionado:
  - ANALISIS_APP_AUTHENTICATION_v3_0_0_PARTE_1.md
  - ANALISIS_APP_AUTHENTICATION_v3_0_0_PARTE_3.md
replaces: []
---

# ANÁLISIS DE apps/authentication/ v3.0.0 - PARTE 2/3
## SERVICES Y AUTHENTICATION LOGIC

---

## 1. SERVICES

### 1.1 AuthenticationService

```python
"""
Service para autenticación de usuarios.

CNST-005: Auth Token/Session, PBKDF2
CNST-031: Auditoría completa
"""

from typing import Optional, Dict
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token

from apps.authentication.models import LoginAttempt, SessionLog
from apps.authentication.exceptions import (
    InvalidCredentialsError,
    AccountLockedError,
    UserInactiveError
)
from apps.authentication.utils import get_client_ip, get_user_agent

User = get_user_model()


class AuthenticationService:
    """
    Service para login/logout.
    
    Responsabilidades:
    - Autenticación username/password
    - Creación de sesiones
    - Registro de intentos (CNST-031)
    - Verificación de bloqueos
    - Token/Session dual (CNST-005)
    """
    
    def __init__(self):
        """Initialize service."""
        from apps.authentication.services.lockout import LockoutService
        self.lockout_service = LockoutService()
    
    def login_user(
        self,
        request,
        username: str,
        password: str
    ) -> Dict:
        """
        Login de usuario.
        
        Args:
            request: HttpRequest
            username: Username
            password: Password
        
        Returns:
            Dict con:
            - user: User object
            - token: Auth token (DRF)
            - session_key: Session key
        
        Raises:
            AccountLockedError: Cuenta bloqueada
            InvalidCredentialsError: Credenciales inválidas
            UserInactiveError: Usuario inactivo
        
        Side effects:
            - Crea LoginAttempt (CNST-031)
            - Crea SessionLog (CNST-031)
            - Crea session en DB (CNST-010)
            - Genera token DRF
        
        Example:
            auth_service = AuthenticationService()
            result = auth_service.login_user(
                request,
                'jdoe',
                'SecurePass123'
            )
            # result = {
            #     'user': <User: jdoe>,
            #     'token': 'abc123...',
            #     'session_key': 'xyz789...'
            # }
        """
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # 1. Verificar bloqueo (CNST lockout)
        if self.lockout_service.is_locked(username):
            # Registrar intento durante bloqueo
            self._record_attempt(
                username=username,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            raise AccountLockedError(
                f"Account '{username}' is locked. Try again later."
            )
        
        # 2. Autenticar con Django
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
            
            # Incrementar contador de bloqueo
            self.lockout_service.record_failed_attempt(username)
            
            raise InvalidCredentialsError("Invalid username or password")
        
        # 3. Verificar usuario activo
        if not user.is_active:
            self._record_attempt(
                username=username,
                user=user,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            raise UserInactiveError(f"User '{username}' is inactive")
        
        # 4. Login exitoso - crear sesión (CNST-010: DB session)
        login(request, user)
        
        # 5. Generar/obtener token DRF (CNST-005)
        token, created = Token.objects.get_or_create(user=user)
        
        # 6. Registrar intento exitoso (CNST-031)
        self._record_attempt(
            username=username,
            user=user,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 7. Log de sesión (CNST-031)
        self._create_session_log(
            user=user,
            session_key=request.session.session_key,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 8. Resetear contador de bloqueo
        self.lockout_service.reset_failed_attempts(username)
        
        return {
            'user': user,
            'token': token.key,
            'session_key': request.session.session_key
        }
    
    def logout_user(self, request) -> bool:
        """
        Logout de usuario.
        
        Args:
            request: HttpRequest
        
        Returns:
            bool: True si logout exitoso
        
        Side effects:
            - Actualiza SessionLog (logout_at)
            - Invalida sesión Django
        
        CNST-010: Session en DB (django_session)
        CNST-031: Log de logout
        """
        if not request.user.is_authenticated:
            return False
        
        # 1. Actualizar SessionLog
        self._update_session_log(
            session_key=request.session.session_key
        )
        
        # 2. Logout Django (invalida session en DB)
        logout(request)
        
        return True
    
    def _record_attempt(
        self,
        username: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        user: Optional[User] = None
    ):
        """
        Registra intento de login.
        
        CNST-031: Auditoría immutable.
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
        user: User,
        session_key: str,
        ip_address: str,
        user_agent: str
    ):
        """Crea log de sesión."""
        SessionLog.objects.create(
            user=user,
            session_key=session_key,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
    
    def _update_session_log(self, session_key: str):
        """Actualiza log al hacer logout."""
        SessionLog.objects.filter(
            session_key=session_key,
            is_active=True
        ).update(
            logout_at=timezone.now(),
            is_active=False
        )
```

### 1.2 LockoutService

```python
"""
Service para bloqueo de cuentas.

CNST: MAX_LOGIN_ATTEMPTS = 5, LOCKOUT_DURATION = 15min
"""

from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache

from apps.authentication.models import LoginAttempt
from apps.authentication.constants import (
    MAX_LOGIN_ATTEMPTS,
    LOCKOUT_DURATION_MINUTES,
    LOCKOUT_WINDOW_MINUTES
)


class LockoutService:
    """
    Service para gestión de bloqueos de cuenta.
    
    Responsabilidades:
    - Contar intentos fallidos
    - Bloquear/desbloquear cuentas
    - Verificar estado de bloqueo
    
    CNST-010: Cache en locmem (NO Redis)
    """
    
    def is_locked(self, username: str) -> bool:
        """
        Verifica si cuenta está bloqueada.
        
        Args:
            username: Username a verificar
        
        Returns:
            bool: True si bloqueada
        
        Note:
            Cache key: lockout_{username}
            TTL: LOCKOUT_DURATION_MINUTES
        """
        cache_key = f'lockout_{username}'
        locked_until = cache.get(cache_key)
        
        if locked_until:
            if timezone.now() < locked_until:
                return True
            else:
                # Expiró, limpiar cache
                cache.delete(cache_key)
                return False
        
        return False
    
    def record_failed_attempt(self, username: str):
        """
        Registra intento fallido.
        
        Si alcanza MAX_LOGIN_ATTEMPTS, bloquea cuenta.
        
        Args:
            username: Username
        """
        # Contar intentos recientes
        attempts_count = self._count_recent_attempts(username)
        
        if attempts_count >= MAX_LOGIN_ATTEMPTS:
            self._lock_account(username)
    
    def reset_failed_attempts(self, username: str):
        """
        Resetea contador de intentos fallidos.
        
        Se llama después de login exitoso.
        
        Args:
            username: Username
        """
        cache_key = f'failed_attempts_{username}'
        cache.delete(cache_key)
    
    def _count_recent_attempts(self, username: str) -> int:
        """
        Cuenta intentos fallidos recientes.
        
        Ventana: LOCKOUT_WINDOW_MINUTES (15 min)
        
        Args:
            username: Username
        
        Returns:
            int: Número de intentos fallidos
        """
        cutoff = timezone.now() - timedelta(
            minutes=LOCKOUT_WINDOW_MINUTES
        )
        
        count = LoginAttempt.objects.filter(
            username=username,
            success=False,
            attempted_at__gte=cutoff
        ).count()
        
        return count
    
    def _lock_account(self, username: str):
        """
        Bloquea cuenta.
        
        Args:
            username: Username a bloquear
        """
        locked_until = timezone.now() + timedelta(
            minutes=LOCKOUT_DURATION_MINUTES
        )
        
        cache_key = f'lockout_{username}'
        cache.set(
            cache_key,
            locked_until,
            timeout=LOCKOUT_DURATION_MINUTES * 60
        )
```

### 1.3 RecoveryService

```python
"""
Service para recuperación de contraseña.

CNST-001: SIN email, SOLO preguntas de seguridad.
"""

from typing import List, Dict
from django.contrib.auth import get_user_model

from apps.authentication.models import (
    SecurityQuestion,
    UserSecurityAnswer
)
from apps.authentication.exceptions import (
    SecurityAnswersNotSetError,
    InvalidSecurityAnswersError
)
from apps.authentication.constants import SECURITY_QUESTIONS_REQUIRED

User = get_user_model()


class RecoveryService:
    """
    Service para recuperación SIN email.
    
    CNST-001: Recuperación por 3 preguntas de seguridad.
    
    Responsabilidades:
    - Configurar preguntas de usuario
    - Verificar respuestas
    - Reset password por preguntas
    """
    
    def get_available_questions(self) -> List[SecurityQuestion]:
        """
        Obtiene preguntas de seguridad disponibles.
        
        Returns:
            List[SecurityQuestion]: Preguntas activas
        """
        questions = SecurityQuestion.objects.filter(
            is_active=True
        ).order_by('order')
        
        return list(questions)
    
    def set_security_answers(
        self,
        user: User,
        answers: List[Dict]
    ) -> bool:
        """
        Configura respuestas de seguridad del usuario.
        
        Args:
            user: Usuario
            answers: Lista de {question_id, answer}
        
        Returns:
            bool: True si configuró exitosamente
        
        Raises:
            ValueError: Si no son exactamente 3 respuestas
        
        Example:
            answers = [
                {'question_id': 1, 'answer': 'Firulais'},
                {'question_id': 5, 'answer': 'Santiago'},
                {'question_id': 8, 'answer': 'Verde'}
            ]
            recovery_service.set_security_answers(user, answers)
        """
        if len(answers) != SECURITY_QUESTIONS_REQUIRED:
            raise ValueError(
                f"Exactly {SECURITY_QUESTIONS_REQUIRED} answers required"
            )
        
        # Eliminar respuestas previas
        UserSecurityAnswer.objects.filter(user=user).delete()
        
        # Crear nuevas respuestas
        for item in answers:
            question = SecurityQuestion.objects.get(
                pk=item['question_id']
            )
            
            answer_obj = UserSecurityAnswer(
                user=user,
                question=question
            )
            answer_obj.set_answer(item['answer'])
            answer_obj.save()
        
        return True
    
    def verify_security_answers(
        self,
        username: str,
        answers: List[Dict]
    ) -> bool:
        """
        Verifica respuestas de seguridad.
        
        Args:
            username: Username
            answers: Lista de {question_id, answer}
        
        Returns:
            bool: True si TODAS correctas
        
        Raises:
            SecurityAnswersNotSetError: Usuario no tiene respuestas
            InvalidSecurityAnswersError: Respuestas incorrectas
        
        CNST-001: Recuperación SIN email.
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # No revelar si usuario existe
            raise InvalidSecurityAnswersError("Invalid answers")
        
        # Verificar que tenga respuestas configuradas
        user_answers = UserSecurityAnswer.objects.filter(user=user)
        
        if user_answers.count() < SECURITY_QUESTIONS_REQUIRED:
            raise SecurityAnswersNotSetError(
                "Security answers not configured"
            )
        
        # Verificar cada respuesta
        correct_count = 0
        
        for item in answers:
            try:
                user_answer = UserSecurityAnswer.objects.get(
                    user=user,
                    question_id=item['question_id']
                )
                
                if user_answer.check_answer(item['answer']):
                    correct_count += 1
            
            except UserSecurityAnswer.DoesNotExist:
                continue
        
        # Requiere TODAS correctas
        if correct_count == SECURITY_QUESTIONS_REQUIRED:
            return True
        else:
            raise InvalidSecurityAnswersError("Invalid answers")
    
    def reset_password_by_questions(
        self,
        username: str,
        answers: List[Dict],
        new_password: str
    ) -> bool:
        """
        Reset password verificando preguntas.
        
        Args:
            username: Username
            answers: Respuestas de seguridad
            new_password: Nueva contraseña
        
        Returns:
            bool: True si reset exitoso
        
        CNST-001: Recuperación SIN email.
        """
        # 1. Verificar respuestas
        self.verify_security_answers(username, answers)
        
        # 2. Reset password
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        
        # 3. Log en audit
        from apps.audit.services import AuditService
        audit_service = AuditService()
        audit_service.log_action(
            action='PASSWORD_RESET',
            user=user,
            details={'method': 'security_questions'}
        )
        
        return True
```

### 1.4 SessionService

```python
"""
Service para gestión de sesiones.

CNST-010: Sessions en DB (NO Redis).
"""

from typing import List
from django.contrib.sessions.models import Session
from django.utils import timezone

from apps.authentication.models import SessionLog


class SessionService:
    """
    Service para gestión de sesiones.
    
    CNST-010: Sessions en django_session table (PostgreSQL).
    
    Responsabilidades:
    - Listar sesiones activas
    - Invalidar sesiones
    - Cleanup sesiones expiradas
    """
    
    def get_active_sessions(self, user) -> List[SessionLog]:
        """
        Obtiene sesiones activas del usuario.
        
        Args:
            user: Usuario
        
        Returns:
            List[SessionLog]: Sesiones activas
        """
        sessions = SessionLog.objects.filter(
            user=user,
            is_active=True
        ).order_by('-login_at')
        
        return list(sessions)
    
    def invalidate_session(self, session_key: str) -> bool:
        """
        Invalida una sesión específica.
        
        Args:
            session_key: Session key a invalidar
        
        Returns:
            bool: True si invalidó
        
        Side effects:
            - Elimina de django_session
            - Actualiza SessionLog
        """
        # 1. Eliminar de django_session (CNST-010)
        try:
            session = Session.objects.get(session_key=session_key)
            session.delete()
        except Session.DoesNotExist:
            pass
        
        # 2. Actualizar SessionLog
        SessionLog.objects.filter(
            session_key=session_key,
            is_active=True
        ).update(
            logout_at=timezone.now(),
            is_active=False
        )
        
        return True
    
    def invalidate_all_user_sessions(self, user) -> int:
        """
        Invalida TODAS las sesiones del usuario.
        
        Args:
            user: Usuario
        
        Returns:
            int: Número de sesiones invalidadas
        """
        # Obtener session_keys activas
        active_sessions = SessionLog.objects.filter(
            user=user,
            is_active=True
        )
        
        count = 0
        for session_log in active_sessions:
            self.invalidate_session(session_log.session_key)
            count += 1
        
        return count
    
    def cleanup_expired_sessions(self) -> int:
        """
        Limpia sesiones expiradas.
        
        Llama a: python manage.py clearsessions
        
        Returns:
            int: Número de sesiones eliminadas
        
        Note:
            Este método debe ejecutarse vía APScheduler
            (NO Celery - CNST-013)
        """
        from django.core.management import call_command
        
        # Django command para limpiar sessions
        call_command('clearsessions')
        
        # Actualizar SessionLog para sesiones expiradas
        expired_sessions = SessionLog.objects.filter(
            is_active=True,
            login_at__lt=timezone.now() - timezone.timedelta(hours=24)
        )
        
        count = expired_sessions.update(
            logout_at=timezone.now(),
            is_active=False
        )
        
        return count
```

---

## 2. UTILS

```python
"""
Utility functions para authentication.
"""

from typing import Optional


def get_client_ip(request) -> str:
    """
    Obtiene IP del cliente.
    
    Args:
        request: HttpRequest
    
    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


def get_user_agent(request) -> str:
    """
    Obtiene User Agent.
    
    Args:
        request: HttpRequest
    
    Returns:
        str: User agent (max 255 chars)
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    return user_agent[:255]


def normalize_username(username: str) -> str:
    """
    Normaliza username.
    
    Args:
        username: Username
    
    Returns:
        str: Username normalizado (lowercase, strip)
    """
    return username.lower().strip()


def is_strong_password(password: str) -> bool:
    """
    Verifica fortaleza de contraseña.
    
    Args:
        password: Password
    
    Returns:
        bool: True si fuerte
    
    Criteria:
    - Mínimo 8 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 minúscula
    - Al menos 1 número
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit
```

---

## 3. EXCEPTIONS

```python
"""
Custom exceptions para authentication.
"""


class AuthenticationBaseException(Exception):
    """Base exception."""
    pass


class InvalidCredentialsError(AuthenticationBaseException):
    """Credenciales inválidas."""
    pass


class AccountLockedError(AuthenticationBaseException):
    """Cuenta bloqueada."""
    pass


class UserInactiveError(AuthenticationBaseException):
    """Usuario inactivo."""
    pass


class SecurityAnswersNotSetError(AuthenticationBaseException):
    """Preguntas de seguridad no configuradas."""
    pass


class InvalidSecurityAnswersError(AuthenticationBaseException):
    """Respuestas de seguridad incorrectas."""
    pass
```

---

## 4. RESUMEN PARTE 2

```yaml
Services (4):
  ✅ AuthenticationService (~350 líneas)
     - login_user, logout_user
     - Token + Session dual
     - Auditoría completa
  
  ✅ LockoutService (~150 líneas)
     - is_locked, record_failed_attempt
     - Cache locmem (NO Redis)
     - 5 intentos, 15 min bloqueo
  
  ✅ RecoveryService (~250 líneas)
     - verify_security_answers
     - reset_password_by_questions
     - SIN email (CNST-001)
  
  ✅ SessionService (~150 líneas)
     - invalidate_session
     - cleanup_expired_sessions
     - Sessions DB (CNST-010)

Utils (4 funciones):
  ✅ get_client_ip, get_user_agent
  ✅ normalize_username, is_strong_password

Exceptions (6):
  ✅ InvalidCredentialsError
  ✅ AccountLockedError
  ✅ UserInactiveError
  ✅ SecurityAnswersNotSetError
  ✅ InvalidSecurityAnswersError

Total: ~1,050 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 3/3: API REST, Testing y Deployment (FINAL)**

Contenido:
- ✅ Serializers DRF (5 serializers)
- ✅ ViewSets REST (2 viewsets)
- ✅ URLs configuration
- ✅ Tests (35 tests)
- ✅ Deployment checklist
- ✅ APScheduler job (session cleanup)

**Estimado:** ~1,300 líneas, 3 horas

---

**Fin de PARTE 2/3**
