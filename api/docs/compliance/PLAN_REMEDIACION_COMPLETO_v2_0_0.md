# 🎯 PLAN DE REMEDIACIÓN COMPLETO v2.0.0

## INFORMACIÓN DEL DOCUMENTO

| Atributo | Valor |
|---|---|
| **Fecha** | 2026-01-21 |
| **Versión** | 2.0.0 COMPLETA |
| **Estado** | ✅ LISTO PARA EJECUTAR |
| **Correcciones Aplicadas** | permission_django + PermissionService + Clean Code |
| **Enfoque** | Reinicio limpio - Eliminar migraciones y empezar correctamente |

---

## 📋 RESUMEN EJECUTIVO

### Estrategia: Reinicio Limpio

```yaml
Razón del reinicio:
  - apps/users/ tiene código mezclado (auth, rbac, sessions)
  - Violaciones de CNST-001 (email en password reset)
  - Nomenclatura incorrecta (code vs permission_django)
  - Migraciones existentes tienen errores de diseño
  
Solución:
  1. Commit del estado actual (backup)
  2. Eliminar TODAS las migraciones
  3. Implementar arquitectura correcta (4 apps)
  4. Migraciones limpias desde cero
  5. Fixtures con datos correctos

Beneficios:
  ✅ Base de datos limpia desde inicio
  ✅ Sin conflictos de migraciones
  ✅ Arquitectura correcta desde día 1
  ✅ Nomenclatura consistente
  ✅ Compliance total con restricciones
```

---

## 🏗️ ARQUITECTURA FINAL (4 Apps)

```yaml
apps/users/ (Gestión de usuarios):
  Modelos: User, UserProfile, UserSettings (3)
  Endpoints: 9 (CRUD, profile, settings)
  Sin: AuthViewSet, SessionHistory, has_function()

apps/authentication/ (Autenticación y seguridad):
  Modelos: LoginAttempt, SecurityQuestion, UserSecurityAnswer, SessionLog (4)
  Endpoints: 9 (login, logout, security questions, sessions)
  Sin: Email (CNST-001)
  Con: 5 preguntas seguridad

apps/access/ (RBAC permisos):
  Modelos: Module, Function, Group, UserGroup, GroupFunction, PermissionLog (6)
  Servicios: PermissionService (no RBACService)
  Funciones: 46 en 11 módulos
  Primary Key: permission_django (no code)
  Endpoints: 10

apps/alerts/ (Mensajería interna):
  Modelos: InternalMessage, MessageRecipient, AlertConfiguration, AlertSubscription, AlertLog (5)
  Endpoints: 14
  Sin: Email (CNST-001)
  Con: Rate limiting, auto-archivado 90 días
```

---

## 📝 FASE 0: PREPARACIÓN Y BACKUP (30 min)

### PASO 0.1: Commit del Estado Actual

```bash
# Guardar estado actual como backup
cd /tmp/iact-real/callcentersite

# Ver estado
git status

# Agregar todos los cambios
git add .

# Commit descriptivo
git commit -m "BACKUP: Estado antes de remediación completa

- apps/core/: COMPLETO y funcional
- apps/users/: Implementado pero con violaciones
  * AuthViewSet mezclado (debe ir en authentication)
  * password_reset usa email (CNST-001 violada)
  * SessionHistory mal ubicado
  * has_function() en User model (debe ir en access)
  
- Tests: 52 passing en apps/users/
- Integration tests: 24/52 passing
- OpenAPI: 167KB documentación

PRÓXIMOS PASOS:
1. Eliminar migraciones
2. Crear apps/authentication/
3. Crear apps/access/
4. Crear apps/alerts/
5. Limpiar apps/users/
6. Migraciones limpias desde cero"

# Crear tag de backup
git tag -a backup-before-remediation -m "Backup antes de remediación v2.0.0"

# Verificar
git log --oneline -5
git tag
```

### PASO 0.2: Eliminar Migraciones Existentes

```bash
# Backup de base de datos (si existe)
python manage.py dumpdata > /tmp/backup_data.json

# Eliminar migraciones de apps/users/
rm -rf apps/users/migrations/
mkdir apps/users/migrations/
touch apps/users/migrations/__init__.py

# Eliminar migraciones de apps/core/ (opcional, si quieres reiniciar todo)
# rm -rf apps/core/migrations/
# mkdir apps/core/migrations/
# touch apps/core/migrations/__init__.py

# Eliminar base de datos SQLite (si usas SQLite)
rm -f db.sqlite3

# O si usas PostgreSQL, drop y recrear database:
# psql -U postgres
# DROP DATABASE iact_db;
# CREATE DATABASE iact_db;
# \q

# Verificar que no hay migraciones
ls -la apps/users/migrations/
ls -la apps/core/migrations/
```

### PASO 0.3: Commit de Limpieza

```bash
git add .
git commit -m "CLEAN: Eliminar migraciones existentes

Preparación para arquitectura limpia:
- Eliminadas migraciones de apps/users/
- Base de datos reiniciada
- Listo para implementación correcta"
```

---

## 📝 FASE 1: CREAR apps/authentication/ (8 horas)

### PASO 1.1: Estructura Básica

```bash
cd /tmp/iact-real/callcentersite

# Crear app
python manage.py startapp authentication apps/authentication

# Crear estructura de directorios
mkdir -p apps/authentication/services
mkdir -p apps/authentication/serializers
mkdir -p apps/authentication/management/commands
mkdir -p apps/authentication/tests
mkdir -p apps/authentication/fixtures

# Crear archivos __init__.py
touch apps/authentication/services/__init__.py
touch apps/authentication/serializers/__init__.py
touch apps/authentication/tests/__init__.py
```

### PASO 1.2: Configuración de la App

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
        import apps.authentication.signals  # noqa
```

### PASO 1.3: Models

```python
# apps/authentication/models.py

"""
Modelos de autenticación y seguridad.

CNST-001: NO email externo
CNST-005: PBKDF2 password hashing
CNST-031: Auditoría immutable
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class LoginAttempt(models.Model):
    """
    Registro de intento de login (exitoso o fallido).
    
    CNST-031: Auditoría immutable.
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
    
    Pool: 10 preguntas
    Usuario debe responder: 5 preguntas
    """
    
    question = models.CharField(
        'Pregunta',
        max_length=255,
        unique=True,
        db_column='cPregunta'
    )
    
    is_active = models.BooleanField(
        'Activa',
        default=True,
        db_column='bActiva'
    )
    
    order = models.IntegerField(
        'Orden',
        default=0,
        db_column='iOrden',
        help_text='Orden de presentación'
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
    
    def __str__(self):
        return self.question


class UserSecurityAnswer(models.Model):
    """
    Respuesta de usuario a pregunta de seguridad.
    
    Hash: PBKDF2 (mismo que passwords)
    Normalización: lowercase + strip
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
        help_text='Hash PBKDF2 de la respuesta (case-insensitive)'
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
    
    def __str__(self):
        return f"{self.user.username} - {self.question.question}"
    
    def set_answer(self, answer: str):
        """
        Hashea y guarda la respuesta.
        
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
        Verifica si la respuesta es correcta.
        
        Args:
            answer: Respuesta a verificar
        
        Returns:
            bool: True si correcta
        """
        from django.contrib.auth.hashers import check_password
        
        normalized = answer.lower().strip()
        return check_password(normalized, self.answer_hash)


class SessionLog(models.Model):
    """
    Log de sesión de usuario.
    
    CNST-031: Auditoría de sesiones
    CNST-010: Sessions en DB
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
        return None
```

### PASO 1.4: Constants

```python
# apps/authentication/constants.py

"""
Constantes para authentication.
"""

# Login attempts y lockout
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

# Security Questions (TU especificación)
SECURITY_QUESTIONS_REQUIRED = 5  # Usuario debe responder 5
SECURITY_QUESTIONS_POOL_MIN = 10  # Pool de 10 preguntas

# Audit
LOG_FAILED_ATTEMPTS = True
LOG_SUCCESSFUL_LOGINS = True
LOG_LOGOUTS = True
```

### PASO 1.5: Services

```python
# apps/authentication/services/__init__.py

from apps.authentication.services.authentication import AuthenticationService
from apps.authentication.services.recovery import RecoveryService
from apps.authentication.services.lockout import LockoutService
from apps.authentication.services.session import SessionService

__all__ = [
    'AuthenticationService',
    'RecoveryService',
    'LockoutService',
    'SessionService',
]
```

```python
# apps/authentication/services/authentication.py

"""
Service para autenticación de usuarios.

CNST-005: Token + Session, PBKDF2
CNST-031: Auditoría completa
"""

from typing import Dict
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
            Dict con user, token, session_key
        
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
            raise AccountLockedError(
                f"Cuenta '{username}' bloqueada. Intenta en 15 minutos."
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
            self.lockout_service.record_failed_attempt(username)
            
            raise InvalidCredentialsError("Username o password inválidos")
        
        # 3. Verificar activo
        if not user.is_active:
            self._record_attempt(
                username=username,
                user=user,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise UserInactiveError(f"Usuario '{username}' inactivo")
        
        # 4. Login exitoso
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
        self._create_session_log(
            user=user,
            session_key=request.session.session_key,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 8. Resetear contador lockout
        self.lockout_service.reset_failed_attempts(username)
        
        return {
            'user': user,
            'token': token.key,
            'session_key': request.session.session_key
        }
    
    def logout_user(self, request) -> bool:
        """
        Logout de usuario.
        
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
    
    def _record_attempt(
        self,
        username: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        user=None
    ):
        """Registra intento de login (CNST-031)."""
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

```python
# apps/authentication/services/recovery.py

"""
Service para recuperación de contraseñas SIN EMAIL.

CNST-001: NO email, solo preguntas de seguridad
"""

from typing import List, Dict
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.authentication.models import SecurityQuestion, UserSecurityAnswer
from apps.authentication.constants import SECURITY_QUESTIONS_REQUIRED

User = get_user_model()


class RecoveryService:
    """
    Servicio de recuperación de contraseñas.
    
    CNST-001: SIN email, solo preguntas de seguridad.
    Usuario debe tener 5 preguntas configuradas.
    """
    
    def get_available_questions(self) -> List[SecurityQuestion]:
        """
        Obtiene preguntas disponibles.
        
        Returns:
            List[SecurityQuestion]: Pool de 10 preguntas activas
        """
        return SecurityQuestion.objects.filter(
            is_active=True
        ).order_by('order')
    
    def set_security_answers(
        self,
        user: User,
        answers: List[Dict[str, any]]
    ) -> bool:
        """
        Configura respuestas de seguridad del usuario.
        
        Args:
            user: Usuario
            answers: Lista de {question_id, answer}
        
        Returns:
            bool: True si configurado exitosamente
        
        Raises:
            ValidationError: Si no son exactamente 5 respuestas
        
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
            raise ValidationError(
                f"Se requieren exactamente {SECURITY_QUESTIONS_REQUIRED} respuestas"
            )
        
        # Eliminar respuestas anteriores
        UserSecurityAnswer.objects.filter(user=user).delete()
        
        # Crear nuevas respuestas
        for answer_data in answers:
            question = SecurityQuestion.objects.get(
                id=answer_data['question_id'],
                is_active=True
            )
            
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
            answers: Lista de {question_id, answer}
        
        Returns:
            bool: True si TODAS las respuestas son correctas
        
        Raises:
            ValidationError: Si usuario no tiene preguntas configuradas
        """
        user = User.objects.get(username=username)
        
        # Verificar que tenga preguntas configuradas
        user_answers = UserSecurityAnswer.objects.filter(user=user)
        
        if user_answers.count() < SECURITY_QUESTIONS_REQUIRED:
            raise ValidationError(
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
                continue
        
        # TODAS deben ser correctas
        return correct_count == SECURITY_QUESTIONS_REQUIRED
    
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
            ValidationError: Si respuestas incorrectas o falta config
        """
        user = User.objects.get(username=username)
        
        # Verificar respuestas
        if not self.verify_security_answers(username, answers):
            raise ValidationError("Respuestas incorrectas")
        
        # Cambiar password
        user.set_password(new_password)
        user.save()
        
        # Opcional: Enviar ALERT (integración con apps/alerts/)
        try:
            from apps.alerts.services import AlertService
            
            alert_service = AlertService()
            alert_service.send_system_alert(
                recipients=[user],
                subject="✅ Contraseña cambiada",
                body="Tu contraseña fue cambiada mediante preguntas de seguridad.",
                priority='info'
            )
        except:
            pass  # apps/alerts/ puede no existir aún
        
        return True
```

*(Continúa en siguiente mensaje debido a límite de longitud...)*
