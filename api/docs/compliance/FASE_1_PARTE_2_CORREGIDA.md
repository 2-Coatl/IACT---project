# 🔐 FASE 1 CORREGIDA: apps/authentication/ - Usando apps/core y apps/utils

## ⚠️ CORRECCIONES APLICADAS

```yaml
ANTES (incorrecto):
  ❌ apps/authentication/utils.py (duplicado)
  ❌ Services sin BaseService
  ❌ Exceptions independientes

DESPUÉS (correcto):
  ✅ Usar apps.utils.helpers.get_client_ip()
  ✅ Usar apps.utils.helpers.get_user_agent()
  ✅ Heredar de apps.core.services.BaseService
  ✅ Exceptions DRF APIException
```

---

## 📝 PARTE 2 CORREGIDA: Services Base (1.5h)

### 2.1 ❌ NO CREAR utils.py

**ANTES (incorrecto):**
```python
# ❌ apps/authentication/utils.py
def get_client_ip(request):
    ...
def get_user_agent(request):
    ...
```

**DESPUÉS (correcto):**
```python
# ✅ Importar desde apps.utils
from apps.utils.helpers import get_client_ip, get_user_agent
```

### 2.2 LockoutService con BaseService ✅

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
        super().__init__()  # ✅ Llamar a super().__init__()
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
            self.log_warning(f"Usuario '{username}' bloqueado hasta {locked_until}")  # ✅ Usar log_warning de BaseService
            return True
        
        # Lockout expiró, limpiar cache
        cache.delete(cache_key)
        self.log_info(f"Lockout expiró para usuario '{username}'")  # ✅ Usar log_info
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
        
        self.log_warning(f"Intento fallido #{attempts} para usuario '{username}'")  # ✅ Log
        
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
        self.log_info(f"Contador de intentos reseteado para '{username}'")  # ✅ Log
    
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
        
        self.log_info(f"Cuenta '{username}' desbloqueada manualmente")  # ✅ Log
    
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
        
        self.log_error(f"Cuenta '{username}' BLOQUEADA hasta {locked_until}")  # ✅ Log error
```

### 2.3 AuthenticationService Corregido ✅

**Archivo:** `apps/authentication/services/authentication.py`

```python
"""
Servicio de autenticación de usuarios.

CNST-005: Token + Session, PBKDF2
CNST-031: Auditoría completa
"""

from typing import Dict
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token

from apps.core.services.base_service import BaseService  # ✅ BaseService
from apps.utils.helpers import get_client_ip, get_user_agent  # ✅ Usar apps.utils
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
        super().__init__()  # ✅ Llamar a super
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
        # ✅ Usar helpers de apps.utils
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        self.log_info(f"Intento de login para usuario '{username}' desde IP {ip_address}")  # ✅ Log
        
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
            
            self.log_error(f"Login bloqueado para '{username}' - {minutes} minutos restantes")  # ✅ Log
            
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
            
            self.log_warning(f"Credenciales inválidas para '{username}' - {remaining} intentos restantes")  # ✅ Log
            
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
            
            self.log_warning(f"Usuario '{username}' inactivo intentó login")  # ✅ Log
            
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
        
        self.log_info(f"Login exitoso para '{username}' - First login: {first_login}")  # ✅ Log
        
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
        
        self.log_info(f"Logout exitoso para '{username}'")  # ✅ Log
        
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

### 2.4 RecoveryService y SessionService también heredan ✅

Todos los services deben heredar de `BaseService`:

```python
# apps/authentication/services/recovery.py
from apps.core.services.base_service import BaseService

class RecoveryService(BaseService):
    def __init__(self):
        super().__init__()
    ...
```

```python
# apps/authentication/services/session.py
from apps.core.services.base_service import BaseService

class SessionService(BaseService):
    def __init__(self):
        super().__init__()
    ...
```

---

## 📝 PARTE 2 CORREGIDA - Commit

```bash
cd /tmp/iact-real
git add callcentersite/apps/authentication/
git commit -m "FASE 1 - PARTE 2: Services Base (CORREGIDO)

Implementación:
✅ LockoutService:
   - Hereda de apps.core.services.BaseService
   - Usa log_info(), log_warning(), log_error()
   - Lockout: 5 intentos → 15 min

✅ AuthenticationService:
   - Hereda de BaseService
   - Usa get_client_ip() de apps.utils.helpers
   - Usa get_user_agent() de apps.utils.helpers
   - Logging completo con BaseService
   - First login detection

✅ NO SE CREÓ utils.py (usar apps.utils)
✅ Todos los services heredan de BaseService
✅ Logging centralizado

Compliance:
- CNST-005: Token + Session
- CNST-031: Auditoría completa
- Clean Code: Reutilización apps/core y apps/utils

Próximo: PARTE 3 - RecoveryService + SessionService"
```

---

## ✅ RESUMEN DE CORRECCIONES

```yaml
Usar apps/core:
  ✅ from apps.core.services.base_service import BaseService
  ✅ class MyService(BaseService):
  ✅ super().__init__()
  ✅ self.log_info(), self.log_warning(), self.log_error()

Usar apps/utils:
  ✅ from apps.utils.helpers import get_client_ip
  ✅ from apps.utils.helpers import get_user_agent
  ✅ from apps.utils.helpers import generate_uuid (si se necesita)

NO crear:
  ❌ apps/authentication/utils.py
  ❌ Funciones duplicadas get_client_ip, get_user_agent
  ❌ Services sin heredar de BaseService
```

---

**Documento generado:** 2026-01-21  
**Versión:** 2.0.0 CORREGIDA  
**Estado:** ✅ Usando apps/core y apps/utils correctamente
