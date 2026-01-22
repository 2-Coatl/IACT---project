---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Users PARTE 2/4
categoria: arquitectura/apps
tema: apps/users/ - Services y User Management
autor: Claude Technical Analysis
tags: [users, services, authentication, password-management, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - ANALISIS_APP_USERS_v3_0_0_PARTE_1.md
estado: definitivo
parte: 2 de 4
relacionado:
  - ANALISIS_APP_USERS_v3_0_0_PARTE_1.md
  - ANALISIS_APP_USERS_v3_0_0_PARTE_3.md
  - ANALISIS_APP_USERS_v3_0_0_PARTE_4.md
replaces: []
---

# ANÁLISIS DE apps/users/ v3.0.0 - PARTE 2/4
## SERVICES Y USER MANAGEMENT

---

## TABLA DE CONTENIDOS

1. [Resumen Parte 2](#resumen)
2. [UserService](#user-service)
3. [AuthenticationService](#auth-service)
4. [ProfileService](#profile-service)
5. [PasswordService](#password-service)
6. [Utils](#utils)
7. [Exceptions](#exceptions)

---

<a name="resumen"></a>
## 1. RESUMEN PARTE 2

### 1.1 Alcance

```yaml
Componentes:
  ✅ UserService (CRUD, activation)
  ✅ AuthenticationService (login, logout, tokens)
  ✅ ProfileService (perfil, avatar)
  ✅ PasswordService (change, reset, validate)
  ✅ Utils (8 helpers)
  ✅ Exceptions (5 custom exceptions)

Líneas código: ~1,400 líneas Python
```

---

<a name="user-service"></a>
## 2. USERSERVICE

### 2.1 Archivo: apps/users/services.py

```python
"""
Service layer para gestión de usuarios.

CLEAN_CODE v3.0.1:
- Clases: UserService (PascalCase)
- Métodos: create_user (snake_case)
"""

from typing import Optional, Dict, List
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.users.models import UserProfile, UserSettings
from apps.users.exceptions import (
    UserNotFoundError,
    UsernameAlreadyExistsError,
    EmailAlreadyExistsError
)

User = get_user_model()


class UserService:
    """
    Service para gestión de usuarios.
    
    Responsabilidades:
    - CRUD usuarios
    - Activación/desactivación
    - Validaciones
    - Integración con apps/access/ para permisos
    """
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = '',
        last_name: str = '',
        **extra_fields
    ) -> User:
        """
        Crea un nuevo usuario.
        
        Args:
            username: Username único
            email: Email único
            password: Contraseña (será hasheada)
            first_name: Nombre
            last_name: Apellido
            **extra_fields: Campos adicionales
        
        Returns:
            User: Usuario creado
        
        Raises:
            UsernameAlreadyExistsError: Username ya existe
            EmailAlreadyExistsError: Email ya existe
        
        Example:
            user_service = UserService()
            user = user_service.create_user(
                username='jdoe',
                email='jdoe@company.com',
                password='SecurePass123',
                first_name='John',
                last_name='Doe'
            )
        """
        # Validar username único
        if User.objects.filter(username=username).exists():
            raise UsernameAlreadyExistsError(
                f"Username '{username}' ya existe"
            )
        
        # Validar email único
        if User.objects.filter(email=email).exists():
            raise EmailAlreadyExistsError(
                f"Email '{email}' ya está registrado"
            )
        
        # Crear usuario (transacción)
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,  # Django hashea automáticamente
                first_name=first_name,
                last_name=last_name,
                **extra_fields
            )
            
            # Profile y Settings se crean automáticamente vía signals
            # (ver apps/users/signals.py)
        
        return user
    
    def get_user(self, user_id: int) -> User:
        """
        Obtiene usuario por ID.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            User: Usuario encontrado
        
        Raises:
            UserNotFoundError: Usuario no existe
        """
        try:
            user = User.objects.select_related('profile', 'settings').get(
                pk=user_id
            )
            return user
        except User.DoesNotExist:
            raise UserNotFoundError(f"Usuario con ID {user_id} no existe")
    
    def get_user_by_username(self, username: str) -> User:
        """
        Obtiene usuario por username.
        
        Args:
            username: Username del usuario
        
        Returns:
            User: Usuario encontrado
        
        Raises:
            UserNotFoundError: Usuario no existe
        """
        try:
            user = User.objects.select_related('profile', 'settings').get(
                username=username
            )
            return user
        except User.DoesNotExist:
            raise UserNotFoundError(f"Usuario '{username}' no existe")
    
    def update_user(
        self,
        user_id: int,
        data: Dict
    ) -> User:
        """
        Actualiza datos del usuario.
        
        Args:
            user_id: ID del usuario
            data: Dict con campos a actualizar
        
        Returns:
            User: Usuario actualizado
        
        Example:
            data = {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jsmith@company.com'
            }
            user = user_service.update_user(5, data)
        """
        user = self.get_user(user_id)
        
        # Actualizar campos permitidos
        allowed_fields = [
            'first_name', 'last_name', 'email', 'employee_id'
        ]
        
        for field, value in data.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        user.save()
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """
        Elimina usuario (soft delete - is_active=False).
        
        Args:
            user_id: ID del usuario
        
        Returns:
            bool: True si se eliminó
        
        Note:
            No se elimina físicamente por compliance.
            Solo se desactiva (is_active=False).
        """
        user = self.get_user(user_id)
        user.is_active = False
        user.save()
        
        # Log en apps/audit/
        from apps.audit.services import AuditService
        audit_service = AuditService()
        audit_service.log_action(
            action='USER_DELETED',
            user=user,
            details={'user_id': user_id}
        )
        
        return True
    
    def activate_user(self, user_id: int) -> User:
        """
        Activa un usuario desactivado.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            User: Usuario activado
        """
        user = self.get_user(user_id)
        user.is_active = True
        user.save()
        
        return user
    
    def deactivate_user(self, user_id: int) -> User:
        """
        Desactiva un usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            User: Usuario desactivado
        """
        user = self.get_user(user_id)
        user.is_active = False
        user.save()
        
        return user
    
    def list_users(
        self,
        filters: Optional[Dict] = None,
        order_by: str = 'username'
    ) -> List[User]:
        """
        Lista usuarios con filtros opcionales.
        
        Args:
            filters: Dict con filtros (is_active, is_staff, etc)
            order_by: Campo para ordenar
        
        Returns:
            List[User]: Lista de usuarios
        
        Example:
            # Usuarios activos staff
            filters = {'is_active': True, 'is_staff': True}
            users = user_service.list_users(filters)
        """
        queryset = User.objects.select_related('profile', 'settings')
        
        if filters:
            queryset = queryset.filter(**filters)
        
        return list(queryset.order_by(order_by))
    
    def search_users(self, query: str) -> List[User]:
        """
        Busca usuarios por username, email, nombre.
        
        Args:
            query: Término de búsqueda
        
        Returns:
            List[User]: Usuarios que coinciden
        """
        from django.db.models import Q
        
        queryset = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        
        return list(queryset.select_related('profile'))
```

---

<a name="auth-service"></a>
## 3. AUTHENTICATIONSERVICE

```python
"""
Service para autenticación.
"""

from typing import Optional
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from apps.users.models import User, SessionHistory
from apps.users.exceptions import InvalidCredentialsError, UserInactiveError


class AuthenticationService:
    """
    Service para autenticación y gestión de sesiones.
    
    Responsabilidades:
    - Login/logout
    - Password reset
    - Email verification
    - Session management
    """
    
    def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Autentica usuario.
        
        Args:
            username: Username o email
            password: Contraseña
        
        Returns:
            User: Usuario autenticado o None
        
        Raises:
            InvalidCredentialsError: Credenciales inválidas
            UserInactiveError: Usuario inactivo
        
        CNST-039: Logs en SessionHistory via signals
        """
        # Intentar autenticar
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Intento fallido
            raise InvalidCredentialsError("Username o contraseña incorrectos")
        
        if not user.is_active:
            raise UserInactiveError("Usuario inactivo")
        
        return user
    
    def login_user(self, request, username: str, password: str) -> User:
        """
        Login de usuario.
        
        Args:
            request: HttpRequest
            username: Username
            password: Contraseña
        
        Returns:
            User: Usuario logueado
        
        Side effects:
            - Crea sesión Django
            - Log en SessionHistory (via signal)
            - Actualiza last_login
        """
        user = self.authenticate_user(username, password)
        
        # Login Django session
        login(request, user)
        
        return user
    
    def logout_user(self, request):
        """
        Logout de usuario.
        
        Args:
            request: HttpRequest
        
        Side effects:
            - Cierra sesión Django
            - Log en SessionHistory (via signal)
        """
        logout(request)
    
    def generate_password_reset_token(self, email: str) -> str:
        """
        Genera token para reset de contraseña.
        
        Args:
            email: Email del usuario
        
        Returns:
            str: Token único
        
        Raises:
            UserNotFoundError: Email no registrado
        """
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            from apps.users.exceptions import UserNotFoundError
            raise UserNotFoundError(f"Email '{email}' no registrado")
        
        # Generar token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Enviar email
        reset_link = f"{settings.SITE_URL}/users/reset-password/{uid}/{token}/"
        
        send_mail(
            subject='Reset de Contraseña - IACT',
            message=f'Para resetear tu contraseña, haz clic en: {reset_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return token
    
    def reset_password(
        self,
        uidb64: str,
        token: str,
        new_password: str
    ) -> bool:
        """
        Resetea contraseña con token.
        
        Args:
            uidb64: UID codificado
            token: Token de reset
            new_password: Nueva contraseña
        
        Returns:
            bool: True si se reseteo exitosamente
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return False
        
        # Validar token
        if not default_token_generator.check_token(user, token):
            return False
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        return True
    
    def get_user_sessions(self, user: User) -> List[SessionHistory]:
        """
        Obtiene sesiones del usuario.
        
        Args:
            user: Usuario
        
        Returns:
            List[SessionHistory]: Lista de sesiones
        """
        return list(
            SessionHistory.objects.filter(user=user).order_by('-login_at')[:10]
        )
    
    def revoke_all_sessions(self, user: User) -> int:
        """
        Revoca todas las sesiones activas del usuario.
        
        Args:
            user: Usuario
        
        Returns:
            int: Número de sesiones revocadas
        """
        from django.utils import timezone
        
        count = SessionHistory.objects.filter(
            user=user,
            is_active=True
        ).update(
            logout_at=timezone.now(),
            is_active=False
        )
        
        return count
```

---

<a name="profile-service"></a>
## 4. PROFILESERVICE

```python
"""
Service para gestión de perfiles.
"""

from typing import Dict, Optional
from django.core.files.uploadedfile import UploadedFile

from apps.users.models import User, UserProfile
from apps.users.exceptions import InvalidFileTypeError, FileTooLargeError
from apps.users.constants import AVATAR_MAX_SIZE_MB, AVATAR_ALLOWED_FORMATS


class ProfileService:
    """
    Service para gestión de perfiles de usuario.
    
    Responsabilidades:
    - Actualizar perfil
    - Gestión de avatar
    - Campos adicionales
    """
    
    def get_profile(self, user: User) -> UserProfile:
        """
        Obtiene perfil del usuario.
        
        Args:
            user: Usuario
        
        Returns:
            UserProfile: Perfil del usuario
        
        Note:
            Profile se crea automáticamente via signals.
        """
        # Profile siempre existe (signal)
        return user.profile
    
    def update_profile(
        self,
        user: User,
        data: Dict
    ) -> UserProfile:
        """
        Actualiza perfil del usuario.
        
        Args:
            user: Usuario
            data: Dict con campos a actualizar
        
        Returns:
            UserProfile: Perfil actualizado
        
        Example:
            data = {
                'phone_number': '+56912345678',
                'position': 'Senior Developer',
                'department': 'Engineering',
                'bio': 'Full-stack developer...'
            }
            profile = profile_service.update_profile(user, data)
        """
        profile = self.get_profile(user)
        
        # Actualizar campos permitidos
        allowed_fields = [
            'phone_number', 'position', 'department', 'bio'
        ]
        
        for field, value in data.items():
            if field in allowed_fields:
                setattr(profile, field, value)
        
        profile.save()
        return profile
    
    def upload_avatar(
        self,
        user: User,
        file: UploadedFile
    ) -> UserProfile:
        """
        Sube avatar del usuario.
        
        Args:
            user: Usuario
            file: Archivo de imagen
        
        Returns:
            UserProfile: Perfil actualizado
        
        Raises:
            InvalidFileTypeError: Formato no permitido
            FileTooLargeError: Archivo muy grande
        
        CNST: AVATAR_MAX_SIZE_MB=5, AVATAR_ALLOWED_FORMATS
        """
        # Validar tamaño
        max_size = AVATAR_MAX_SIZE_MB * 1024 * 1024  # MB to bytes
        if file.size > max_size:
            raise FileTooLargeError(
                f"Avatar no puede exceder {AVATAR_MAX_SIZE_MB}MB"
            )
        
        # Validar formato
        extension = file.name.split('.')[-1].lower()
        if extension not in AVATAR_ALLOWED_FORMATS:
            raise InvalidFileTypeError(
                f"Formato no permitido. Permitidos: {', '.join(AVATAR_ALLOWED_FORMATS)}"
            )
        
        # Guardar avatar
        profile = self.get_profile(user)
        profile.avatar = file
        profile.save()
        
        return profile
    
    def delete_avatar(self, user: User) -> UserProfile:
        """
        Elimina avatar del usuario (vuelve a default).
        
        Args:
            user: Usuario
        
        Returns:
            UserProfile: Perfil actualizado
        """
        profile = self.get_profile(user)
        
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save()
        
        return profile
```

---

<a name="password-service"></a>
## 5. PASSWORDSERVICE

```python
"""
Service para gestión de contraseñas.
"""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from apps.users.models import User
from apps.users.exceptions import WeakPasswordError, IncorrectPasswordError


class PasswordService:
    """
    Service para gestión de contraseñas.
    
    Responsabilidades:
    - Cambio de contraseña
    - Validación de contraseñas
    - Políticas de contraseñas (CNST-038)
    """
    
    def change_password(
        self,
        user: User,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Cambia contraseña del usuario.
        
        Args:
            user: Usuario
            old_password: Contraseña actual
            new_password: Nueva contraseña
        
        Returns:
            bool: True si cambió exitosamente
        
        Raises:
            IncorrectPasswordError: Contraseña actual incorrecta
            WeakPasswordError: Nueva contraseña no cumple políticas
        
        CNST-038: Password policies
        """
        # Verificar contraseña actual
        if not user.check_password(old_password):
            raise IncorrectPasswordError("Contraseña actual incorrecta")
        
        # Validar nueva contraseña (Django validators)
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise WeakPasswordError(str(e))
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        return True
    
    def validate_password_strength(
        self,
        password: str,
        user: Optional[User] = None
    ) -> bool:
        """
        Valida fortaleza de contraseña.
        
        Args:
            password: Contraseña a validar
            user: Usuario (opcional, para validar similitud)
        
        Returns:
            bool: True si es válida
        
        Raises:
            WeakPasswordError: Contraseña débil
        
        CNST-038: Min 8 chars, uppercase, lowercase, number
        """
        try:
            validate_password(password, user)
            return True
        except ValidationError as e:
            raise WeakPasswordError(str(e))
```

---

<a name="utils"></a>
## 6. UTILS

### 6.1 Archivo: apps/users/utils.py

```python
"""
Utility functions para users.

CLEAN_CODE v3.0.1: snake_case inglés.
"""

from typing import Optional
from django.contrib.auth import get_user_model

User = get_user_model()


def get_full_name(user: User) -> str:
    """
    Obtiene nombre completo del usuario.
    
    Args:
        user: Usuario
    
    Returns:
        str: Nombre completo o username
    """
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name if full_name else user.username


def get_user_initials(user: User) -> str:
    """
    Obtiene iniciales del usuario.
    
    Args:
        user: Usuario
    
    Returns:
        str: Iniciales (ej: 'JD' para John Doe)
    """
    if user.first_name and user.last_name:
        return f"{user.first_name[0]}{user.last_name[0]}".upper()
    elif user.first_name:
        return user.first_name[0].upper()
    else:
        return user.username[0].upper()


def is_email_unique(email: str, exclude_user: Optional[User] = None) -> bool:
    """
    Verifica si email es único.
    
    Args:
        email: Email a verificar
        exclude_user: Usuario a excluir de la búsqueda
    
    Returns:
        bool: True si es único
    """
    queryset = User.objects.filter(email=email)
    
    if exclude_user:
        queryset = queryset.exclude(pk=exclude_user.pk)
    
    return not queryset.exists()


def is_username_unique(username: str, exclude_user: Optional[User] = None) -> bool:
    """
    Verifica si username es único.
    
    Args:
        username: Username a verificar
        exclude_user: Usuario a excluir
    
    Returns:
        bool: True si es único
    """
    queryset = User.objects.filter(username=username)
    
    if exclude_user:
        queryset = queryset.exclude(pk=exclude_user.pk)
    
    return not queryset.exists()


def format_user_display(user: User) -> str:
    """
    Formatea usuario para display.
    
    Args:
        user: Usuario
    
    Returns:
        str: Formato 'John Doe (jdoe)'
    """
    full_name = get_full_name(user)
    
    if full_name != user.username:
        return f"{full_name} ({user.username})"
    else:
        return user.username


def get_user_avatar_url(user: User) -> str:
    """
    Obtiene URL del avatar del usuario.
    
    Args:
        user: Usuario
    
    Returns:
        str: URL del avatar o default
    """
    if hasattr(user, 'profile') and user.profile.avatar:
        return user.profile.avatar.url
    
    from apps.users.constants import DEFAULT_AVATAR
    return f'/static/{DEFAULT_AVATAR}'


def sanitize_username(username: str) -> str:
    """
    Sanitiza username (lowercase, sin espacios).
    
    Args:
        username: Username a sanitizar
    
    Returns:
        str: Username sanitizado
    """
    return username.lower().strip().replace(' ', '')


def generate_username_from_email(email: str) -> str:
    """
    Genera username desde email.
    
    Args:
        email: Email
    
    Returns:
        str: Username sugerido
    
    Example:
        >>> generate_username_from_email('john.doe@company.com')
        'johndoe'
    """
    username = email.split('@')[0]
    username = username.replace('.', '').replace('_', '')
    return sanitize_username(username)
```

---

<a name="exceptions"></a>
## 7. EXCEPTIONS

### 7.1 Archivo: apps/users/exceptions.py

```python
"""
Custom exceptions para users.

CLEAN_CODE v3.0.1: PascalCase con sufijo Error.
"""


class UserBaseException(Exception):
    """Base exception para users."""
    pass


class UserNotFoundError(UserBaseException):
    """Usuario no encontrado."""
    pass


class UsernameAlreadyExistsError(UserBaseException):
    """Username ya existe."""
    pass


class EmailAlreadyExistsError(UserBaseException):
    """Email ya registrado."""
    pass


class InvalidCredentialsError(UserBaseException):
    """Credenciales inválidas."""
    pass


class UserInactiveError(UserBaseException):
    """Usuario inactivo."""
    pass


class WeakPasswordError(UserBaseException):
    """Contraseña no cumple políticas."""
    pass


class IncorrectPasswordError(UserBaseException):
    """Contraseña incorrecta."""
    pass


class InvalidFileTypeError(UserBaseException):
    """Tipo de archivo no permitido."""
    pass


class FileTooLargeError(UserBaseException):
    """Archivo demasiado grande."""
    pass
```

---

## 8. RESUMEN PARTE 2

### 8.1 Componentes Generados

```yaml
Services (4):
  ✅ UserService (~400 líneas)
     - create_user, get_user, update_user, delete_user
     - activate_user, deactivate_user
     - list_users, search_users
  
  ✅ AuthenticationService (~250 líneas)
     - authenticate_user, login_user, logout_user
     - generate_password_reset_token, reset_password
     - get_user_sessions, revoke_all_sessions
  
  ✅ ProfileService (~150 líneas)
     - get_profile, update_profile
     - upload_avatar, delete_avatar
  
  ✅ PasswordService (~100 líneas)
     - change_password
     - validate_password_strength

Utils (8 funciones) (~100 líneas):
  ✅ get_full_name, get_user_initials
  ✅ is_email_unique, is_username_unique
  ✅ format_user_display, get_user_avatar_url
  ✅ sanitize_username, generate_username_from_email

Exceptions (10):
  ✅ UserBaseException (base)
  ✅ UserNotFoundError
  ✅ UsernameAlreadyExistsError
  ✅ EmailAlreadyExistsError
  ✅ InvalidCredentialsError
  ✅ UserInactiveError
  ✅ WeakPasswordError
  ✅ IncorrectPasswordError
  ✅ InvalidFileTypeError
  ✅ FileTooLargeError

Total: ~1,100 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 3/4: API REST y Serializers**

Contenido:
- ✅ Serializers (8 serializers)
- ✅ ViewSets (4 viewsets)
- ✅ URLs configuration
- ✅ 15 endpoints REST

**Estimado:** ~1,000 líneas, 3 horas

---

**Fin de PARTE 2/4**
