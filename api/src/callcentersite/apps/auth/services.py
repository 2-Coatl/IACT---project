"""Servicios de autenticación."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import bcrypt
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, ValidationError
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .models import LoginAttempt
from callcentersite.apps.audit.models import AuditLog
from callcentersite.apps.notifications.models import InternalMessage
from callcentersite.apps.users.models import PasswordHistory, UserSession

if TYPE_CHECKING:
    from django.http import HttpRequest

User = get_user_model()


class LoginAttemptService:
    """Gestiona intentos de inicio de sesión."""

    @staticmethod
    def register_attempt(
        username: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        reason: str | None = None,
    ) -> None:
        LoginAttempt.objects.create(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            reason=reason,
        )

    @staticmethod
    def count_recent_failures(username: str, window: timedelta) -> int:
        threshold = timezone.now() - window
        return LoginAttempt.objects.filter(
            username=username, success=False, timestamp__gte=threshold
        ).count()


class AuthenticationService:
    """
    Servicio de autenticación con gestión de sesiones y seguridad.

    Implementa RF-005: Login con Credenciales Locales
    """

    MAX_FAILED_ATTEMPTS = 3
    LOCK_DURATION_MINUTES = 15

    @staticmethod
    def login(
        username: str,
        password: str,
        request: HttpRequest,
    ) -> dict:
        """
        UC-013: Autenticar usuario con credenciales locales.

        Args:
            username: Nombre de usuario
            password: Contraseña
            request: HttpRequest para obtener IP y user agent

        Returns:
            Dict con tokens JWT:
            {
                'access_token': str,
                'refresh_token': str,
                'token_type': 'Bearer',
                'expires_in': 900  # segundos
            }

        Raises:
            PermissionDenied: Si usuario está bloqueado o inactivo
            Exception: Si credenciales son inválidas

        Ejemplo:
            >>> result = AuthenticationService.login(
            ...     username='juan.perez',
            ...     password='SecureP@ss123',
            ...     request=request
            ... )
            >>> print(result['access_token'])
        """
        # Obtener IP y user agent del request
        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # 1. Intentar obtener usuario (sin revelar si existe o no)
        try:
            user = User.objects.get(username=username)
            user_exists = True
        except User.DoesNotExist:
            user_exists = False
            user = None

        # 2. Si usuario no existe, retornar error genérico
        if not user_exists:
            AuditLog.objects.create(
                user=None,
                event_type='LOGIN_FAILURE',
                result='FAILURE',
                ip_address=ip_address,
                user_agent=user_agent,
                details={'username': username, 'reason': 'usuario_inexistente'}
            )
            raise Exception('Credenciales inválidas')

        # 3. Verificar si usuario está activo
        if user.status != 'ACTIVO':
            AuditLog.objects.create(
                user=user,
                event_type='LOGIN_FAILURE',
                result='FAILURE',
                ip_address=ip_address,
                user_agent=user_agent,
                details={'reason': 'usuario_inactivo'}
            )
            raise PermissionDenied('Usuario inactivo')

        # 4. Verificar si usuario está bloqueado
        if user.is_locked:
            # Verificar si el bloqueo ya expiró (desbloqueo automático)
            if user.locked_until and user.locked_until < timezone.now():
                # Desbloquear automáticamente
                user.is_locked = False
                user.locked_until = None
                user.failed_login_attempts = 0
                user.lock_reason = ''
                user.save(update_fields=[
                    'is_locked', 'locked_until', 'failed_login_attempts', 'lock_reason'
                ])

                # Auditar desbloqueo automático
                AuditLog.objects.create(
                    user=user,
                    event_type='USER_UNLOCKED',
                    result='SUCCESS',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={'reason': 'automatic_timeout'}
                )
            else:
                # Usuario sigue bloqueado
                minutes_remaining = int(
                    (user.locked_until - timezone.now()).total_seconds() / 60
                ) if user.locked_until else 0

                AuditLog.objects.create(
                    user=user,
                    event_type='LOGIN_FAILURE',
                    result='FAILURE',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={'reason': 'cuenta_bloqueada', 'minutes_remaining': minutes_remaining}
                )
                raise PermissionDenied(f'Cuenta bloqueada. Tiempo restante: {minutes_remaining} minutos')

        # 5. Verificar contraseña
        if not check_password(password, user.password):
            # Contraseña incorrecta - incrementar contador
            user.failed_login_attempts += 1
            user.last_failed_login_at = timezone.now()

            # Verificar si se alcanzó el límite de intentos
            if user.failed_login_attempts >= AuthenticationService.MAX_FAILED_ATTEMPTS:
                # Bloquear usuario
                user.is_locked = True
                user.locked_until = timezone.now() + timedelta(
                    minutes=AuthenticationService.LOCK_DURATION_MINUTES
                )
                user.lock_reason = 'MAX_FAILED_ATTEMPTS'

                user.save(update_fields=[
                    'failed_login_attempts',
                    'last_failed_login_at',
                    'is_locked',
                    'locked_until',
                    'lock_reason'
                ])

                # Auditar bloqueo
                AuditLog.objects.create(
                    user=user,
                    event_type='USER_LOCKED',
                    result='SUCCESS',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={'reason': 'max_failed_attempts', 'attempts': user.failed_login_attempts}
                )

                # Enviar notificación al buzón interno
                InternalMessage.objects.create(
                    recipient=user,
                    sender=None,
                    subject='Cuenta bloqueada por seguridad',
                    body=f'Tu cuenta ha sido bloqueada temporalmente por {AuthenticationService.LOCK_DURATION_MINUTES} minutos debido a múltiples intentos fallidos de inicio de sesión.',
                    message_type='alert',
                    priority='high',
                    created_by_system=True
                )

                raise Exception('Cuenta bloqueada por múltiples intentos fallidos')
            else:
                # Solo incrementar contador
                user.save(update_fields=['failed_login_attempts', 'last_failed_login_at'])

            # Auditar intento fallido
            AuditLog.objects.create(
                user=user,
                event_type='LOGIN_FAILURE',
                result='FAILURE',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'reason': 'credenciales_invalidas',
                    'attempts': user.failed_login_attempts,
                    'attempts_remaining': AuthenticationService.MAX_FAILED_ATTEMPTS - user.failed_login_attempts
                }
            )

            raise Exception('Credenciales inválidas')

        # 6. Credenciales válidas - Login exitoso

        # Cerrar sesiones previas (sesión única)
        previous_sessions = UserSession.objects.filter(user=user, is_active=True)
        for session in previous_sessions:
            session.close(reason='NEW_SESSION')

            # Auditar cierre de sesión previa
            AuditLog.objects.create(
                user=user,
                event_type='SESSION_CLOSED',
                result='SUCCESS',
                ip_address=ip_address,
                user_agent=user_agent,
                details={'reason': 'new_session', 'old_session': session.session_key[:8]}
            )

            # Notificar sobre nueva sesión
            InternalMessage.objects.create(
                recipient=user,
                sender=None,
                subject='Nueva sesión iniciada',
                body=f'Se ha iniciado una nueva sesión en tu cuenta. Si no fuiste tú, contacta al administrador.',
                message_type='info',
                priority='medium',
                created_by_system=True
            )

        # Resetear contador de intentos fallidos
        user.failed_login_attempts = 0
        user.last_failed_login_at = None
        user.last_login_at = timezone.now()
        user.last_login_ip = ip_address
        user.save(update_fields=[
            'failed_login_attempts',
            'last_failed_login_at',
            'last_login_at',
            'last_login_ip'
        ])

        # Crear nueva sesión
        # Manejar request.session que puede no existir en tests
        if hasattr(request, 'session') and request.session:
            session_key = request.session.get('session_key', '') or f'session_{user.id}_{timezone.now().timestamp()}'
        else:
            session_key = f'session_{user.id}_{timezone.now().timestamp()}'

        UserSession.objects.create(
            user=user,
            session_key=session_key,
            is_active=True,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Generar tokens JWT
        tokens = TokenService.generate_jwt_tokens(user)

        # Auditar login exitoso
        AuditLog.objects.create(
            user=user,
            event_type='LOGIN_SUCCESS',
            result='SUCCESS',
            ip_address=ip_address,
            user_agent=user_agent,
            details={'session_key': session_key[:8]}
        )

        # Retornar tokens
        return {
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh'],
            'token_type': 'Bearer',
            'expires_in': 900  # 15 minutos en segundos
        }

    @staticmethod
    def logout(user: User, refresh_token: str | None, request: HttpRequest) -> None:
        """Cierra sesiones activas y revoca el refresh token proporcionado."""

        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        sessions = list(UserSession.objects.filter(user=user, is_active=True))
        for session in sessions:
            session.close(reason='MANUAL')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                # Token inválido o previamente en blacklist: no interrumpe el logout
                pass
            except AttributeError:
                # Blacklist no disponible en el entorno de pruebas
                pass

        AuditLog.objects.create(
            user=user,
            event_type='LOGOUT_SUCCESS',
            result='SUCCESS',
            ip_address=ip_address,
            user_agent=user_agent,
            details={'sessions_closed': len(sessions)},
        )

    @staticmethod
    def generate_jwt_tokens(user: User) -> dict:
        """Expose token generation para compatibilidad con pruebas."""

        return TokenService.generate_jwt_tokens(user)


class TokenService:
    """Gestiona generación, validación y refresh de tokens JWT."""

    @staticmethod
    def _build_claims(user: User) -> dict:
        roles = []
        if hasattr(user, "groups"):
            roles = list(user.groups.values_list("name", flat=True))
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "segment": getattr(user, "segment", ""),
            "roles": roles,
        }

    @staticmethod
    def _apply_claims(token: RefreshToken | AccessToken, user: User) -> None:
        for key, value in TokenService._build_claims(user).items():
            token[key] = value

    @staticmethod
    def generate_jwt_tokens(user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        TokenService._apply_claims(refresh, user)
        access = refresh.access_token
        TokenService._apply_claims(access, user)
        return {"access": str(access), "refresh": str(refresh)}

    @staticmethod
    def validate_access_token(request: "HttpRequest") -> User:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            raise Exception("Token no proporcionado")

        token_str = auth_header.split(" ", 1)[1]
        try:
            access_token = AccessToken(token_str)
        except TokenError as exc:  # pragma: no cover - handled in tests
            raise Exception(str(exc))

        if access_token.get("token_type") != "access":
            raise Exception("Debe usar access token")

        user_id = access_token.get("user_id")
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise Exception("Usuario no encontrado")
        if getattr(user, "status", "ACTIVO") != "ACTIVO":
            raise Exception("Usuario inactivo")
        if getattr(user, "is_locked", False):
            raise Exception("Usuario bloqueado")

        return user

    @staticmethod
    def refresh_access_token(refresh_token_str: str) -> dict:
        try:
            refresh_token = RefreshToken(refresh_token_str)
            refresh_token.check_blacklist()
        except TokenError as exc:
            message = str(exc).lower()
            if "blacklist" in message or "lista negra" in message:
                raise TokenError("Token en blacklist")
            if "expir" in message or "caduc" in message:
                raise Exception("Refresh token expirado")
            raise Exception("Token inválido o en blacklist")

        user_id = refresh_token.get("user_id")
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise Exception("Usuario no encontrado")

        try:
            refresh_token.blacklist()
        except AttributeError:
            pass
        except Exception:
            raise Exception("Token inválido o en blacklist")

        new_refresh = RefreshToken.for_user(user)
        TokenService._apply_claims(new_refresh, user)
        new_access = new_refresh.access_token
        TokenService._apply_claims(new_access, user)

        return {"access": str(new_access), "refresh": str(new_refresh)}


def _get_client_ip(request: HttpRequest) -> str:
    """Extrae la IP del cliente desde el request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def update_session_activity(user: User, request: HttpRequest) -> None:
    """Actualiza la última actividad de la sesión activa del usuario."""

    session = (
        UserSession.objects.filter(user=user, is_active=True)
        .order_by('-last_activity_at', '-created_at')
        .first()
    )

    if not session:
        return

    session.last_activity_at = timezone.now()

    ip_address = _get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    if ip_address:
        session.ip_address = ip_address
    if user_agent:
        session.user_agent = user_agent

    session.save(update_fields=['last_activity_at', 'ip_address', 'user_agent'])


def close_previous_sessions(user: User, request: HttpRequest) -> int:
    """Cierra sesiones activas para garantizar sesión única."""

    active_sessions = list(UserSession.objects.filter(user=user, is_active=True))
    for session in active_sessions:
        session.close(reason='NEW_SESSION')

        AuditLog.objects.create(
            user=user,
            event_type='SESSION_CLOSED',
            result='SUCCESS',
            details={'session_key': session.session_key},
        )

        InternalMessage.objects.create(
            recipient=user,
            sender=None,
            subject='Nueva sesión iniciada',
            body='Se cerró tu sesión anterior por iniciar en otro dispositivo.',
            message_type='info',
            priority='medium',
            created_by_system=True,
        )

    return len(active_sessions)


def create_user_session(user: User, request: HttpRequest) -> UserSession:
    """Crea una sesión activa usando el session_key disponible."""

    session_key = getattr(getattr(request, 'session', None), 'session_key', None)
    if not session_key:
        session_key = f'session_{user.id}_{timezone.now().timestamp()}'

    ip_address = _get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    return UserSession.objects.create(
        user=user,
        session_key=session_key,
        is_active=True,
        ip_address=ip_address or None,
        user_agent=user_agent,
    )


def hash_password(password: str) -> str:
    """Genera hash bcrypt con cost factor 12."""

    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica un password plano contra su hash bcrypt."""

    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False


def validate_password_history(user: User, new_password: str) -> None:
    """Evita reutilizar contraseñas recientes."""

    recent = PasswordHistory.objects.filter(user=user).order_by('-created_at')[:5]
    for entry in recent:
        if verify_password(new_password, entry.password_hash):
            raise ValidationError('La contraseña coincide con una de las últimas 5 usadas')


def handle_failed_login(username: str) -> None:
    """Incrementa contador y bloquea cuenta tras 3 intentos."""

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return

    user.failed_login_attempts += 1
    user.last_failed_login_at = timezone.now()
    update_fields = ['failed_login_attempts', 'last_failed_login_at']

    if user.failed_login_attempts >= AuthenticationService.MAX_FAILED_ATTEMPTS:
        user.is_locked = True
        user.locked_until = timezone.now() + timedelta(minutes=AuthenticationService.LOCK_DURATION_MINUTES)
        user.lock_reason = 'MAX_FAILED_ATTEMPTS'
        update_fields += ['is_locked', 'locked_until', 'lock_reason']

        AuditLog.objects.create(
            user=user,
            event_type='USER_LOCKED',
            result='SUCCESS',
            details={'attempts': user.failed_login_attempts},
        )

        InternalMessage.objects.create(
            recipient=user,
            sender=None,
            subject='Cuenta bloqueada por intentos fallidos',
            body='Tu cuenta fue bloqueada después de múltiples intentos fallidos.',
            message_type='alert',
            priority='high',
            created_by_system=True,
        )

    user.save(update_fields=update_fields)


def unlock_user_manual(admin_user: User, target_user: User) -> None:
    """Desbloqueo manual controlando rol R016 (simulado)."""

    has_privilege = admin_user.username == 'admin' or admin_user.is_staff or admin_user.is_superuser
    if not has_privilege:
        raise PermissionDenied('Se requiere el rol R016 para desbloquear usuarios')

    target_user.is_locked = False
    target_user.locked_until = None
    target_user.lock_reason = ''
    target_user.failed_login_attempts = 0
    target_user.last_failed_login_at = None
    target_user.save(update_fields=[
        'is_locked',
        'locked_until',
        'lock_reason',
        'failed_login_attempts',
        'last_failed_login_at',
    ])

    AuditLog.objects.create(
        user=target_user,
        event_type='USER_UNLOCKED',
        result='SUCCESS',
        details={'unlocked_by': admin_user.username},
    )
