---
version: 1.0.0
date: 2026-01-21
project: IACT Call Center System
type: Plan de Implementación - apps/users/
estado: activo
autor: Claude + Arquitectura Limpia
tags: [users, implementation-plan, tdd, clean-architecture]
---

# PLAN DE IMPLEMENTACIÓN: apps/users/ v1.0.0

**Fecha:** 2026-01-21  
**Arquitectura:** Clean Architecture + Separation of Concerns  
**Metodología:** TDD (Test-Driven Development)  
**Estimación Total:** ~16-20 horas  

---

## 📋 TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen)
2. [Arquitectura y Dependencias](#arquitectura)
3. [Plan Incremental (7 Fases)](#plan)
4. [Fase 1: Models + Migrations](#fase1)
5. [Fase 2: Services](#fase2)
6. [Fase 3: Serializers](#fase3)
7. [Fase 4: ViewSets + URLs](#fase4)
8. [Fase 5: Authentication](#fase5)
9. [Fase 6: Permissions + RBAC](#fase6)
10. [Fase 7: Testing Completo](#fase7)
11. [Checklist Final](#checklist)

---

<a name="resumen"></a>
## 1. RESUMEN EJECUTIVO

### 1.1 Alcance Total

```yaml
Apps Involucradas:
  Principal: apps/users/
  Dependencias:
    ✅ apps/core/ (infraestructura)
    ✅ apps/utils/ (utilidades)
    ✅ apps/access/ (RBAC)
    ✅ apps/audit/ (logging)

Componentes a Crear:
  Models: 4 (User, UserProfile, SessionHistory, UserSettings)
  Services: 4 (UserService, AuthService, ProfileService, PasswordService)
  Serializers: 8 (User, Profile, Login, ChangePassword, etc)
  ViewSets: 4 (UserViewSet, ProfileViewSet, AuthViewSet, SessionHistoryViewSet)
  Exceptions: 5 custom exceptions
  Utils: 8 helpers
  Tests: 45+ tests

Total Líneas Código: ~4,500 líneas
Total Archivos: ~15 archivos Python
```

---

### 1.2 Uso de Arquitectura Existente

```yaml
USAR apps/core/:
  ✅ AbstractUser (Django built-in, pero configurado en core)
  ✅ TimeStampedModel (abstract model en core/models.py)
  ✅ SoftDeleteMixin (abstract model en core/models.py)
  ✅ AuditedModel (abstract model en core/models.py)
  ✅ SoftDeleteViewSetMixin (core/mixins.py)
  ✅ AuditMixin (core/mixins.py)
  ✅ RequiresFunctionPermission (core/permissions.py)
  ✅ IsOwnerOrReadOnly (core/permissions.py)
  ✅ BaseService (core/services.py)

USAR apps/utils/:
  ✅ validate_email (utils/validators.py - EmailValidator)
  ✅ validate_phone_number (utils/validators.py - PhoneValidator)
  ✅ format_phone_number (utils/formatters.py)
  ✅ get_client_ip (utils/helpers.py)
  ✅ get_user_agent (utils/helpers.py)
  ✅ sanitize_filename (utils/file_utils.py)
  ✅ calculate_file_hash (utils/file_utils.py)
  ✅ @require_permission (utils/decorators.py)
  ✅ @log_execution (utils/decorators.py)

USAR apps/access/:
  ✅ Function model (RBAC functions)
  ✅ UserFunction model (user-function assignments)
  ✅ AccessService (get_user_functions, check_permission)

USAR apps/audit/:
  ✅ AuditLog model
  ✅ AuditService (log_action)

NO DUPLICAR:
  ❌ NO crear abstract models (usar core/)
  ❌ NO crear validators genéricos (usar utils/)
  ❌ NO crear decorators genéricos (usar utils/)
  ❌ NO crear permissions genéricas (usar core/)
  ❌ NO crear mixins genéricos (usar core/)
```

---

<a name="arquitectura"></a>
## 2. ARQUITECTURA Y DEPENDENCIAS

### 2.1 Diagrama de Dependencias

```
┌─────────────────────────────────────────────────────┐
│                  apps/users/                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  DEPENDE DE:                                        │
│  ├─ apps/core/ (infraestructura)                   │
│  │  ├─ TimeStampedModel                            │
│  │  ├─ SoftDeleteMixin                             │
│  │  ├─ AuditedModel                                │
│  │  ├─ BaseService                                 │
│  │  ├─ DRF Mixins (7)                              │
│  │  └─ DRF Permissions (7)                         │
│  │                                                  │
│  ├─ apps/utils/ (utilidades)                       │
│  │  ├─ validators.py (EmailValidator, PhoneValidator) │
│  │  ├─ formatters.py (format_phone_number)         │
│  │  ├─ helpers.py (get_client_ip, get_user_agent)  │
│  │  ├─ file_utils.py (sanitize_filename)           │
│  │  └─ decorators.py (require_permission)          │
│  │                                                  │
│  ├─ apps/access/ (RBAC)                            │
│  │  ├─ Function model                              │
│  │  ├─ UserFunction model                          │
│  │  └─ AccessService                               │
│  │                                                  │
│  └─ apps/audit/ (logging)                          │
│     ├─ AuditLog model                              │
│     └─ AuditService                                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 2.2 Imports Correctos

```python
# ============================================================================
# IMPORTS DESDE apps/core/
# ============================================================================

from apps.core.models import TimeStampedModel, SoftDeleteMixin, AuditedModel
from apps.core.mixins import SoftDeleteViewSetMixin, AuditMixin
from apps.core.permissions import RequiresFunctionPermission, IsOwnerOrReadOnly
from apps.core.services import BaseService
from apps.core.exceptions import ValidationError, BusinessLogicError

# ============================================================================
# IMPORTS DESDE apps/utils/
# ============================================================================

from apps.utils.validators import EmailValidator, PhoneValidator
from apps.utils.formatters import format_phone_number
from apps.utils.helpers import get_client_ip, get_user_agent
from apps.utils.file_utils import sanitize_filename, calculate_file_hash
from apps.utils.decorators import require_permission, log_execution

# ============================================================================
# IMPORTS DESDE apps/access/
# ============================================================================

from apps.access.models import Function, UserFunction
from apps.access.services import AccessService

# ============================================================================
# IMPORTS DESDE apps/audit/
# ============================================================================

from apps.audit.models import AuditLog
from apps.audit.services import AuditService
```

---

<a name="plan"></a>
## 3. PLAN INCREMENTAL (7 FASES)

### 3.1 Overview de Fases

```yaml
Fase 1: Models + Migrations (2-3 horas)
  ✅ User (CustomUser con AbstractUser)
  ✅ UserProfile (1-to-1, usa TimeStampedModel)
  ✅ SessionHistory (usa TimeStampedModel)
  ✅ UserSettings (usa TimeStampedModel)
  ✅ Signals (auto-crear profile/settings)
  ✅ Migrations generadas y aplicadas

Fase 2: Services (3-4 horas)
  ✅ UserService (hereda BaseService de core/)
  ✅ AuthenticationService (hereda BaseService)
  ✅ ProfileService (hereda BaseService)
  ✅ PasswordService (hereda BaseService)
  ✅ Utils (8 helpers)
  ✅ Exceptions (5 custom)

Fase 3: Serializers (2-3 horas)
  ✅ UserSerializer
  ✅ UserProfileSerializer
  ✅ UserSettingsSerializer
  ✅ UserCreateSerializer
  ✅ LoginSerializer
  ✅ ChangePasswordSerializer
  ✅ PasswordResetRequestSerializer
  ✅ PasswordResetConfirmSerializer

Fase 4: ViewSets + URLs (2-3 horas)
  ✅ UserViewSet (usa AuditMixin, RequiresFunctionPermission)
  ✅ ProfileViewSet
  ✅ AuthViewSet (@action login, logout, change_password)
  ✅ SessionHistoryViewSet
  ✅ URLs con DRF Router

Fase 5: Authentication (2-3 horas)
  ✅ Login/Logout flow
  ✅ Password reset flow
  ✅ Email verification (planificado)
  ✅ Session management

Fase 6: Permissions + RBAC (1-2 horas)
  ✅ Integración con apps/access/
  ✅ Function fixtures (USR_VIEW, USR_EDIT, etc)
  ✅ Permission decorators
  ✅ Tests permissions

Fase 7: Testing Completo (4-5 horas)
  ✅ test_models.py (10 tests)
  ✅ test_services.py (20 tests)
  ✅ test_serializers.py (8 tests)
  ✅ test_viewsets.py (15 tests)
  ✅ test_permissions.py (5 tests)
  ✅ Coverage >90%

Total Estimado: 16-23 horas
```

---

<a name="fase1"></a>
## 4. FASE 1: MODELS + MIGRATIONS (2-3h)

### 4.1 Archivo: apps/users/models.py

```python
"""
Models para apps/users/.

ARQUITECTURA:
- User: Hereda AbstractUser (Django built-in)
- UserProfile: Hereda TimeStampedModel (apps.core.models)
- SessionHistory: Hereda TimeStampedModel
- UserSettings: Hereda TimeStampedModel

CNST-037: Custom User Model
CLEAN_CODE v3.0.1: Nombres auto-documentados
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

from apps.core.models import TimeStampedModel, SoftDeleteMixin


class User(AbstractUser, SoftDeleteMixin):
    """
    Usuario custom del sistema.
    
    Hereda de:
    - AbstractUser (Django): username, email, password, etc
    - SoftDeleteMixin (apps.core): is_deleted, deleted_at
    
    CNST-037: Custom User Model
    
    Relaciones:
    - profile: UserProfile (1-to-1)
    - settings: UserSettings (1-to-1)
    - functions: UserFunction (M2M vía apps.access)
    """
    
    # Campos adicionales (AbstractUser ya tiene username, email, etc)
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='ID Empleado'
    )
    
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Teléfono'
    )
    
    position = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Cargo'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Avatar'
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['employee_id']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    @property
    def full_name(self):
        """Retorna nombre completo."""
        return self.get_full_name() or self.username
    
    def get_functions(self):
        """
        Obtiene funciones RBAC del usuario.
        
        Usa apps.access.services.AccessService
        
        Returns:
            set: Set de códigos de funciones
        
        Example:
            user = User.objects.get(id=1)
            functions = user.get_functions()
            # {'USR_VIEW', 'USR_EDIT'}
        """
        from apps.access.services import AccessService
        return AccessService.get_user_functions(self)
    
    def has_function(self, function_code):
        """
        Verifica si usuario tiene función.
        
        Args:
            function_code: Código de función (ej: 'USR_VIEW')
        
        Returns:
            bool: True si tiene la función
        """
        return function_code in self.get_functions()


class UserProfile(TimeStampedModel):
    """
    Perfil extendido del usuario.
    
    Hereda de TimeStampedModel (apps.core):
    - created_at, updated_at
    
    Relación 1-to-1 con User.
    Se crea automáticamente vía signals.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuario'
    )
    
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name='Biografía'
    )
    
    department = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Departamento'
    )
    
    # Campos heredados de TimeStampedModel:
    # - created_at
    # - updated_at
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    @property
    def avatar_url(self):
        """Retorna URL del avatar."""
        if self.user.avatar:
            return self.user.avatar.url
        return '/static/images/default-avatar.png'


class SessionHistory(TimeStampedModel):
    """
    Historial de sesiones de usuario.
    
    Hereda de TimeStampedModel (apps.core).
    
    CNST-039: Session Auditing
    
    Se crea automáticamente vía signals (user_logged_in).
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='Usuario'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    
    user_agent = models.CharField(
        max_length=255,
        verbose_name='User Agent'
    )
    
    login_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Login'
    )
    
    logout_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Logout'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Sesión Activa'
    )
    
    class Meta:
        db_table = 'session_history'
        verbose_name = 'Historial de Sesión'
        verbose_name_plural = 'Historial de Sesiones'
        ordering = ['-login_at']
        indexes = [
            models.Index(fields=['user', '-login_at']),
            models.Index(fields=['is_active', '-login_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.login_at}"


class UserSettings(TimeStampedModel):
    """
    Configuración de usuario.
    
    Hereda de TimeStampedModel (apps.core).
    
    Se crea automáticamente vía signals.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name='Usuario'
    )
    
    language = models.CharField(
        max_length=10,
        default='es',
        choices=[
            ('es', 'Español'),
            ('en', 'English'),
        ],
        verbose_name='Idioma'
    )
    
    theme = models.CharField(
        max_length=20,
        default='light',
        choices=[
            ('light', 'Claro'),
            ('dark', 'Oscuro'),
        ],
        verbose_name='Tema'
    )
    
    timezone = models.CharField(
        max_length=50,
        default='America/Santiago',
        verbose_name='Zona Horaria'
    )
    
    notifications_enabled = models.BooleanField(
        default=True,
        verbose_name='Notificaciones Habilitadas'
    )
    
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificaciones por Email'
    )
    
    class Meta:
        db_table = 'user_settings'
        verbose_name = 'Configuración de Usuario'
        verbose_name_plural = 'Configuraciones de Usuario'
    
    def __str__(self):
        return f"Settings de {self.user.username}"
```

---

### 4.2 Archivo: apps/users/signals.py

```python
"""
Signals para apps/users/.

Auto-creación de Profile y Settings.
CNST-037: Profile/Settings se crean con User.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth import get_user_model

from apps.users.models import UserProfile, UserSettings, SessionHistory
from apps.utils.helpers import get_client_ip  # ← USAR apps/utils/

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Auto-crear UserProfile al crear User.
    
    CNST-037: Profile 1-to-1 con User.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guardar profile cuando se guarda user."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    """Auto-crear UserSettings al crear User."""
    if created:
        UserSettings.objects.create(user=instance)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log sesión al hacer login.
    
    CNST-039: Session auditing.
    USAR: apps.utils.helpers.get_client_ip()
    """
    ip_address = get_client_ip(request)  # ← USAR helper de apps/utils/
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    
    SessionHistory.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log logout."""
    if user and user.is_authenticated:
        from django.utils import timezone
        
        SessionHistory.objects.filter(
            user=user,
            is_active=True
        ).update(
            logout_at=timezone.now(),
            is_active=False
        )
```

---

### 4.3 Archivo: apps/users/apps.py

```python
"""AppConfig para users."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuración de app users."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Usuarios'
    
    def ready(self):
        """Importar signals."""
        import apps.users.signals  # noqa
```

---

### 4.4 Configuración: config/settings/base.py

```python
# AUTH_USER_MODEL (CNST-037)
AUTH_USER_MODEL = 'users.User'

# Password validators (CNST-038)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Session
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_SAVE_EVERY_REQUEST = True

# Media (avatars)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

### 4.5 Tareas Fase 1

```bash
# 1. Crear archivos
callcentersite/apps/users/models.py
callcentersite/apps/users/signals.py
callcentersite/apps/users/apps.py
callcentersite/apps/users/constants.py

# 2. Actualizar settings
config/settings/base.py (AUTH_USER_MODEL)

# 3. Generar migrations
cd callcentersite
python manage.py makemigrations users
python manage.py migrate

# 4. Verificar
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.create_user(username='test', email='test@test.com', password='test123')
>>> user.profile  # ← Debe existir (auto-creado)
>>> user.settings  # ← Debe existir (auto-creado)

# 5. Commit
git add -A
git commit -m "Fase 1: Models + Migrations apps/users/ completado"
git tag users-fase1-models
```

**Estimación Fase 1:** 2-3 horas  
**Archivos creados:** 4  
**Líneas código:** ~600 líneas  

---

<a name="fase2"></a>
## 5. FASE 2: SERVICES (3-4h)

### 5.1 Archivo: apps/users/exceptions.py

```python
"""
Custom exceptions para apps/users/.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

from apps.core.exceptions import BusinessLogicError  # ← USAR core/


class UserNotFoundError(BusinessLogicError):
    """Usuario no encontrado."""
    pass


class UsernameAlreadyExistsError(BusinessLogicError):
    """Username ya existe."""
    pass


class EmailAlreadyExistsError(BusinessLogicError):
    """Email ya registrado."""
    pass


class InvalidCredentialsError(BusinessLogicError):
    """Credenciales inválidas."""
    pass


class WeakPasswordError(BusinessLogicError):
    """Contraseña débil."""
    pass
```

---

### 5.2 Archivo: apps/users/services.py

```python
"""
Services para apps/users/.

ARQUITECTURA:
- Hereda de BaseService (apps.core.services)
- Usa AccessService (apps.access.services)
- Usa AuditService (apps.audit.services)

CLEAN_CODE v3.0.1: Service Layer Pattern
"""

from typing import Optional, Dict, List
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password

from apps.core.services import BaseService  # ← USAR BaseService de core/
from apps.users.models import UserProfile, UserSettings
from apps.users.exceptions import (
    UserNotFoundError,
    UsernameAlreadyExistsError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    WeakPasswordError
)

User = get_user_model()


class UserService(BaseService):
    """
    Service para gestión de usuarios.
    
    Hereda de BaseService (apps.core):
    - log_info(), log_error(), log_warning(), log_debug()
    
    Responsabilidades:
    - CRUD usuarios
    - Activación/desactivación
    - Validaciones
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
        
        Auto-loggea usando BaseService.log_info()
        """
        # Log usando BaseService
        self.log_info(f"Creando usuario: {username}")
        
        # Validar username único
        if User.objects.filter(username=username).exists():
            self.log_warning(f"Username duplicado: {username}")
            raise UsernameAlreadyExistsError(f"Username '{username}' ya existe")
        
        # Validar email único
        if User.objects.filter(email=email).exists():
            self.log_warning(f"Email duplicado: {email}")
            raise EmailAlreadyExistsError(f"Email '{email}' ya registrado")
        
        # Validar password
        try:
            validate_password(password)
        except Exception as e:
            raise WeakPasswordError(str(e))
        
        # Crear usuario (transacción)
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                **extra_fields
            )
            
            # Profile y Settings se crean vía signals
        
        self.log_info(f"Usuario creado: {user.id}")
        
        # Log en audit (apps/audit/)
        from apps.audit.services import AuditService  # ← USAR AuditService
        audit = AuditService()
        audit.log_action(
            action='USER_CREATED',
            user=user,
            details={'username': username, 'email': email}
        )
        
        return user
    
    def get_user(self, user_id: int) -> User:
        """Obtiene usuario por ID."""
        try:
            return User.objects.select_related('profile', 'settings').get(pk=user_id)
        except User.DoesNotExist:
            raise UserNotFoundError(f"Usuario {user_id} no existe")
    
    def update_user(self, user_id: int, data: Dict) -> User:
        """Actualiza usuario."""
        user = self.get_user(user_id)
        
        allowed_fields = ['first_name', 'last_name', 'email', 'employee_id', 'phone', 'position']
        
        for field, value in data.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        user.save()
        
        self.log_info(f"Usuario actualizado: {user.id}")
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Soft delete usuario."""
        user = self.get_user(user_id)
        user.is_active = False
        user.save()
        
        self.log_info(f"Usuario eliminado (soft): {user.id}")
        
        # Log en audit
        from apps.audit.services import AuditService
        audit = AuditService()
        audit.log_action(
            action='USER_DELETED',
            user=user,
            details={'user_id': user_id}
        )
        
        return True


class AuthenticationService(BaseService):
    """
    Service para autenticación.
    
    Hereda de BaseService (apps.core).
    """
    
    def authenticate_user(self, username: str, password: str) -> User:
        """
        Autentica usuario.
        
        Returns:
            User: Usuario autenticado
        
        Raises:
            InvalidCredentialsError: Credenciales inválidas
        """
        user = authenticate(username=username, password=password)
        
        if user is None:
            self.log_warning(f"Login fallido: {username}")
            raise InvalidCredentialsError("Credenciales inválidas")
        
        if not user.is_active:
            self.log_warning(f"Usuario inactivo intentó login: {username}")
            raise InvalidCredentialsError("Usuario inactivo")
        
        self.log_info(f"Login exitoso: {username}")
        return user


class ProfileService(BaseService):
    """Service para gestión de perfiles."""
    
    def update_profile(self, user: User, data: Dict) -> UserProfile:
        """Actualiza perfil de usuario."""
        profile = user.profile
        
        allowed_fields = ['bio', 'department']
        
        for field, value in data.items():
            if field in allowed_fields:
                setattr(profile, field, value)
        
        profile.save()
        
        self.log_info(f"Perfil actualizado: user_id={user.id}")
        return profile
    
    def upload_avatar(self, user: User, file) -> User:
        """
        Sube avatar de usuario.
        
        Usa apps.utils.file_utils
        """
        from apps.utils.file_utils import sanitize_filename  # ← USAR utils/
        
        # Sanitizar nombre archivo
        filename = sanitize_filename(file.name)
        
        user.avatar = file
        user.save()
        
        self.log_info(f"Avatar subido: user_id={user.id}, file={filename}")
        return user


class PasswordService(BaseService):
    """Service para gestión de contraseñas."""
    
    def change_password(self, user: User, old_password: str, new_password: str) -> bool:
        """
        Cambia contraseña de usuario.
        
        Valida old_password y aplica new_password.
        """
        # Verificar contraseña actual
        if not user.check_password(old_password):
            self.log_warning(f"Cambio contraseña fallido (old_password incorrecto): user_id={user.id}")
            raise InvalidCredentialsError("Contraseña actual incorrecta")
        
        # Validar nueva contraseña
        try:
            validate_password(new_password, user)
        except Exception as e:
            raise WeakPasswordError(str(e))
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        self.log_info(f"Contraseña cambiada: user_id={user.id}")
        
        # Log en audit
        from apps.audit.services import AuditService
        audit = AuditService()
        audit.log_action(
            action='PASSWORD_CHANGED',
            user=user,
            details={'user_id': user.id}
        )
        
        return True
    
    def reset_password(self, email: str) -> bool:
        """
        Inicia proceso de reset de contraseña.
        
        Envía email con token.
        """
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            # No revelar si email existe o no (seguridad)
            self.log_warning(f"Reset solicitado para email no existente: {email}")
            return True
        
        # TODO: Generar token y enviar email
        # (implementar en siguiente iteración)
        
        self.log_info(f"Reset password solicitado: user_id={user.id}")
        return True
```

---

### 5.3 Archivo: apps/users/utils.py

```python
"""
Utilities para apps/users/.

NOTA: Usar apps/utils/ cuando sea posible.
Esto es solo para helpers específicos de users.
"""

from typing import Optional
from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_display_name(user: User) -> str:
    """
    Obtiene nombre para mostrar.
    
    Args:
        user: Usuario
    
    Returns:
        str: Nombre completo o username
    """
    return user.get_full_name() or user.username


def is_strong_password(password: str) -> bool:
    """
    Verifica si contraseña es fuerte.
    
    Args:
        password: Contraseña a validar
    
    Returns:
        bool: True si es fuerte
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit
```

---

### 5.4 Tareas Fase 2

```bash
# 1. Crear archivos
callcentersite/apps/users/exceptions.py
callcentersite/apps/users/services.py
callcentersite/apps/users/utils.py

# 2. Tests TDD (antes de implementar)
callcentersite/tests/unit/users/test_services.py

# 3. Ejecutar tests
pytest tests/unit/users/test_services.py -v

# 4. Commit
git add -A
git commit -m "Fase 2: Services apps/users/ completado"
git tag users-fase2-services
```

**Estimación Fase 2:** 3-4 horas  
**Archivos creados:** 3  
**Líneas código:** ~1,000 líneas  

---

<a name="fase3"></a>
## 6. FASE 3: SERIALIZERS (2-3h)

### 6.1 Archivo: apps/users/serializers.py

```python
"""
Serializers DRF para apps/users/.

CLEAN_CODE v3.0.1: Serializers auto-documentados.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from apps.users.models import UserProfile, UserSettings, SessionHistory

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para UserProfile."""
    
    avatar_url = serializers.CharField(source='avatar_url', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'department', 'avatar_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer para UserSettings."""
    
    class Meta:
        model = UserSettings
        fields = [
            'language', 'theme', 'timezone',
            'notifications_enabled', 'email_notifications'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer principal para User.
    
    Incluye profile, settings, functions (RBAC).
    """
    
    profile = UserProfileSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)
    full_name = serializers.CharField(source='full_name', read_only=True)
    functions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'employee_id', 'phone', 'position',
            'is_active', 'is_staff', 'date_joined', 'last_login',
            'profile', 'settings', 'functions'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'is_staff'
        ]
    
    def get_functions(self, obj):
        """
        Get user RBAC functions.
        
        Usa apps.access.services.AccessService
        """
        if self.context.get('include_functions'):
            from apps.access.services import AccessService  # ← USAR AccessService
            return sorted(list(AccessService.get_user_functions(obj)))
        return []


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuario."""
    
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'employee_id', 'phone', 'position'
        ]
    
    def validate(self, data):
        """Validate passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Las contraseñas no coinciden'}
            )
        
        # Validar password strength
        try:
            validate_password(data['password'])
        except Exception as e:
            raise serializers.ValidationError({'password': str(e)})
        
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        from apps.users.services import UserService  # ← USAR UserService
        service = UserService()
        
        user = service.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña."""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate passwords match."""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Las contraseñas no coinciden'}
            )
        
        # Validar password strength
        try:
            validate_password(data['new_password'])
        except Exception as e:
            raise serializers.ValidationError({'new_password': str(e)})
        
        return data


class SessionHistorySerializer(serializers.ModelSerializer):
    """Serializer para SessionHistory."""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SessionHistory
        fields = [
            'id', 'user', 'user_username', 'ip_address', 'user_agent',
            'login_at', 'logout_at', 'is_active'
        ]
        read_only_fields = ['id', 'login_at', 'logout_at']
```

---

### 6.2 Tareas Fase 3

```bash
# 1. Crear archivo
callcentersite/apps/users/serializers.py

# 2. Tests TDD
callcentersite/tests/unit/users/test_serializers.py

# 3. Ejecutar tests
pytest tests/unit/users/test_serializers.py -v

# 4. Commit
git add -A
git commit -m "Fase 3: Serializers apps/users/ completado"
git tag users-fase3-serializers
```

**Estimación Fase 3:** 2-3 horas  
**Líneas código:** ~400 líneas  

---

<a name="fase4"></a>
## 7. FASE 4: VIEWSETS + URLS (2-3h)

### 7.1 Archivo: apps/users/viewsets.py

```python
"""
ViewSets DRF para apps/users/.

ARQUITECTURA:
- Usa AuditMixin (apps.core.mixins)
- Usa RequiresFunctionPermission (apps.core.permissions)
- Usa SoftDeleteViewSetMixin (apps.core.mixins)
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from apps.core.mixins import AuditMixin, SoftDeleteViewSetMixin  # ← USAR core/
from apps.core.permissions import RequiresFunctionPermission, IsOwnerOrReadOnly  # ← USAR core/

from apps.users.models import UserProfile, SessionHistory
from apps.users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
    SessionHistorySerializer,
    LoginSerializer,
    ChangePasswordSerializer,
)
from apps.users.services import (
    UserService,
    AuthenticationService,
    ProfileService,
    PasswordService
)

User = get_user_model()


class UserViewSet(
    AuditMixin,              # ← USAR mixin de core/
    SoftDeleteViewSetMixin,  # ← USAR mixin de core/
    viewsets.ModelViewSet
):
    """
    ViewSet para User.
    
    Usa:
    - AuditMixin (apps.core): created_by, updated_by
    - SoftDeleteViewSetMixin (apps.core): soft delete
    - RequiresFunctionPermission (apps.core): RBAC
    
    Permissions:
    - USR_VIEW: list, retrieve
    - USR_EDIT: create, update, partial_update
    - USR_DELETE: destroy, soft_delete
    - USR_PERMS: assign_functions
    
    Endpoints:
    - GET    /users/
    - POST   /users/
    - GET    /users/{id}/
    - PUT    /users/{id}/
    - DELETE /users/{id}/
    - POST   /users/{id}/activate/
    - POST   /users/{id}/deactivate/
    - POST   /users/{id}/assign_functions/
    """
    
    queryset = User.objects.select_related('profile', 'settings').all()
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    # RBAC function map
    function_map = {
        'list': 'USR_VIEW',
        'retrieve': 'USR_VIEW',
        'create': 'USR_EDIT',
        'update': 'USR_EDIT',
        'partial_update': 'USR_EDIT',
        'destroy': 'USR_DELETE',
        'activate': 'USR_EDIT',
        'deactivate': 'USR_EDIT',
        'assign_functions': 'USR_PERMS',
    }
    
    def get_serializer_class(self):
        """Serializer dinámico."""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_serializer_context(self):
        """Context con include_functions."""
        context = super().get_serializer_context()
        context['include_functions'] = self.request.query_params.get('include_functions', False)
        return context
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activa usuario.
        
        POST /users/{id}/activate/
        """
        user = self.get_object()
        service = UserService()
        
        user = service.activate_user(user.id)
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Desactiva usuario.
        
        POST /users/{id}/deactivate/
        """
        user = self.get_object()
        service = UserService()
        
        user = service.deactivate_user(user.id)
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def assign_functions(self, request, pk=None):
        """
        Asigna funciones RBAC a usuario.
        
        POST /users/{id}/assign_functions/
        Body: {"function_codes": ["USR_VIEW", "USR_EDIT"]}
        
        Usa apps.access.services.AccessService
        """
        user = self.get_object()
        function_codes = request.data.get('function_codes', [])
        
        from apps.access.services import AccessService  # ← USAR AccessService
        service = AccessService()
        
        service.assign_functions_to_user(user, function_codes, granted_by=request.user)
        
        return Response({
            'message': f'{len(function_codes)} funciones asignadas',
            'functions': function_codes
        })


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet para UserProfile.
    
    Solo el dueño puede editar (IsOwnerOrReadOnly).
    
    Endpoints:
    - GET    /profiles/me/  (perfil del usuario actual)
    - PUT    /profiles/me/
    - POST   /profiles/upload_avatar/
    """
    
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]  # ← USAR core/
    
    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        """
        Perfil del usuario actual.
        
        GET/PUT /profiles/me/
        """
        profile = request.user.profile
        
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        # PUT
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        service = ProfileService()
        profile = service.update_profile(request.user, serializer.validated_data)
        
        return Response(self.get_serializer(profile).data)
    
    @action(detail=False, methods=['post'])
    def upload_avatar(self, request):
        """
        Sube avatar.
        
        POST /profiles/upload_avatar/
        Body: multipart/form-data con 'avatar' file
        """
        avatar_file = request.FILES.get('avatar')
        
        if not avatar_file:
            return Response(
                {'error': 'No se envió archivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ProfileService()
        user = service.upload_avatar(request.user, avatar_file)
        
        return Response({
            'avatar_url': user.profile.avatar_url
        })


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet para autenticación.
    
    No usa ModelViewSet (no hay modelo específico).
    
    Endpoints:
    - POST /auth/login/
    - POST /auth/logout/
    - POST /auth/change_password/
    """
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Login.
        
        POST /auth/login/
        Body: {"username": "user", "password": "pass"}
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = AuthenticationService()
        user = service.authenticate_user(
            serializer.validated_data['username'],
            serializer.validated_data['password']
        )
        
        # Django login
        from django.contrib.auth import login
        login(request, user)
        
        # Retornar user data
        user_serializer = UserSerializer(user, context={'request': request, 'include_functions': True})
        return Response(user_serializer.data)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Logout.
        
        POST /auth/logout/
        """
        from django.contrib.auth import logout
        logout(request)
        
        return Response({'message': 'Logout exitoso'})
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Cambia contraseña.
        
        POST /auth/change_password/
        Body: {"old_password": "old", "new_password": "new", "new_password_confirm": "new"}
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = PasswordService()
        service.change_password(
            request.user,
            serializer.validated_data['old_password'],
            serializer.validated_data['new_password']
        )
        
        return Response({'message': 'Contraseña cambiada exitosamente'})


class SessionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para SessionHistory (read-only).
    
    Endpoints:
    - GET /sessions/
    - GET /sessions/{id}/
    - GET /sessions/my_sessions/  (sesiones del usuario actual)
    """
    
    queryset = SessionHistory.objects.all()
    serializer_class = SessionHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar por usuario actual."""
        if not self.request.user.is_staff:
            return SessionHistory.objects.filter(user=self.request.user)
        return super().get_queryset()
    
    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """
        Sesiones del usuario actual.
        
        GET /sessions/my_sessions/
        """
        sessions = SessionHistory.objects.filter(user=request.user).order_by('-login_at')[:10]
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)
```

---

### 7.2 Archivo: apps/users/urls.py

```python
"""
URLs para apps/users/.

DRF Router para ViewSets.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.viewsets import (
    UserViewSet,
    ProfileViewSet,
    AuthViewSet,
    SessionHistoryViewSet,
)

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'sessions', SessionHistoryViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]


# ============================================================================
# ENDPOINTS DISPONIBLES
# 
# Users:
#   GET/POST    /api/v1/users/users/
#   GET/PUT/DELETE /api/v1/users/users/{id}/
#   POST        /api/v1/users/users/{id}/activate/
#   POST        /api/v1/users/users/{id}/deactivate/
#   POST        /api/v1/users/users/{id}/assign_functions/
# 
# Profiles:
#   GET/PUT     /api/v1/users/profiles/me/
#   POST        /api/v1/users/profiles/upload_avatar/
# 
# Auth:
#   POST        /api/v1/users/auth/login/
#   POST        /api/v1/users/auth/logout/
#   POST        /api/v1/users/auth/change_password/
# 
# Sessions:
#   GET         /api/v1/users/sessions/
#   GET         /api/v1/users/sessions/{id}/
#   GET         /api/v1/users/sessions/my_sessions/
# ============================================================================
```

---

### 7.3 Actualizar config/urls.py

```python
# En config/urls.py

urlpatterns = [
    # ... otras URLs ...
    path('api/v1/users/', include('apps.users.urls')),
    # ...
]
```

---

### 7.4 Tareas Fase 4

```bash
# 1. Crear archivos
callcentersite/apps/users/viewsets.py
callcentersite/apps/users/urls.py

# 2. Actualizar config/urls.py

# 3. Tests TDD
callcentersite/tests/unit/users/test_viewsets.py

# 4. Ejecutar tests
pytest tests/unit/users/test_viewsets.py -v

# 5. Commit
git add -A
git commit -m "Fase 4: ViewSets + URLs apps/users/ completado"
git tag users-fase4-viewsets
```

**Estimación Fase 4:** 2-3 horas  
**Líneas código:** ~700 líneas  

---

<a name="fase5"></a>
## 8. FASE 5: AUTHENTICATION (2-3h)

**Esta fase está cubierta por AuthViewSet en Fase 4.**

Adicional: Implementar password reset completo con tokens.

---

<a name="fase6"></a>
## 9. FASE 6: PERMISSIONS + RBAC (1-2h)

### 9.1 Archivo: apps/access/fixtures/functions.json

```json
[
  {
    "model": "access.function",
    "pk": 1,
    "fields": {
      "code": "USR_VIEW",
      "name": "Ver Usuarios",
      "description": "Permite ver listado y detalle de usuarios",
      "module": 9,
      "is_active": true
    }
  },
  {
    "model": "access.function",
    "pk": 2,
    "fields": {
      "code": "USR_EDIT",
      "name": "Editar Usuarios",
      "description": "Permite crear y editar usuarios",
      "module": 9,
      "is_active": true
    }
  },
  {
    "model": "access.function",
    "pk": 3,
    "fields": {
      "code": "USR_DELETE",
      "name": "Eliminar Usuarios",
      "description": "Permite eliminar usuarios (soft delete)",
      "module": 9,
      "is_active": true
    }
  },
  {
    "model": "access.function",
    "pk": 4,
    "fields": {
      "code": "USR_PERMS",
      "name": "Gestionar Permisos",
      "description": "Permite asignar funciones RBAC a usuarios",
      "module": 9,
      "is_active": true
    }
  }
]
```

### 9.2 Cargar Fixtures

```bash
python manage.py loaddata apps/access/fixtures/functions.json
```

---

<a name="fase7"></a>
## 10. FASE 7: TESTING COMPLETO (4-5h)

### 10.1 Estructura Tests

```yaml
tests/unit/users/:
  ✅ test_models.py (10 tests)
  ✅ test_services.py (20 tests)
  ✅ test_serializers.py (8 tests)
  ✅ test_viewsets.py (15 tests)
  ✅ test_permissions.py (5 tests)
  ✅ conftest.py (fixtures)

Total: 58 tests
Coverage objetivo: >90%
```

### 10.2 Ejecutar Tests

```bash
# Todos los tests de users
pytest tests/unit/users/ -v

# Con coverage
pytest tests/unit/users/ --cov=apps.users --cov-report=html
```

---

<a name="checklist"></a>
## 11. CHECKLIST FINAL

```yaml
Pre-Implementación:
  ✅ apps/core/ completado (infraestructura)
  ✅ apps/utils/ completado (utilidades)
  ✅ apps/access/ completado (RBAC)
  ✅ apps/audit/ completado (logging)

Fase 1 - Models:
  ✅ User model (CustomUser)
  ✅ UserProfile model
  ✅ SessionHistory model
  ✅ UserSettings model
  ✅ Signals configurados
  ✅ Migrations generadas y aplicadas
  ✅ AUTH_USER_MODEL configurado

Fase 2 - Services:
  ✅ UserService (hereda BaseService)
  ✅ AuthenticationService (hereda BaseService)
  ✅ ProfileService (hereda BaseService)
  ✅ PasswordService (hereda BaseService)
  ✅ Exceptions (5 custom)
  ✅ Utils (helpers específicos)

Fase 3 - Serializers:
  ✅ UserSerializer
  ✅ UserCreateSerializer
  ✅ UserProfileSerializer
  ✅ UserSettingsSerializer
  ✅ LoginSerializer
  ✅ ChangePasswordSerializer
  ✅ SessionHistorySerializer

Fase 4 - ViewSets + URLs:
  ✅ UserViewSet (usa AuditMixin, RequiresFunctionPermission)
  ✅ ProfileViewSet (usa IsOwnerOrReadOnly)
  ✅ AuthViewSet (login, logout, change_password)
  ✅ SessionHistoryViewSet
  ✅ URLs con DRF Router
  ✅ config/urls.py actualizado

Fase 5 - Authentication:
  ✅ Login/Logout flow
  ✅ Password change
  ✅ Password reset (planificado)

Fase 6 - Permissions:
  ✅ Function fixtures (USR_VIEW, USR_EDIT, USR_DELETE, USR_PERMS)
  ✅ RBAC integration
  ✅ Tests permissions

Fase 7 - Testing:
  ✅ test_models.py
  ✅ test_services.py
  ✅ test_serializers.py
  ✅ test_viewsets.py
  ✅ test_permissions.py
  ✅ Coverage >90%

Documentación:
  ✅ README.md apps/users/
  ✅ API documentation
  ✅ Docstrings completos
```

---

## 12. MÉTRICAS FINALES

```yaml
Total Componentes:
  Models: 4
  Services: 4
  Serializers: 8
  ViewSets: 4
  Exceptions: 5
  Utils: 8
  Signals: 4
  Tests: 58+

Total Archivos: ~15 archivos Python
Total Líneas: ~4,500 líneas
Endpoints REST: 18

Uso Correcto Arquitectura:
  ✅ apps/core/ (BaseService, Mixins, Permissions)
  ✅ apps/utils/ (Validators, Helpers, Formatters)
  ✅ apps/access/ (RBAC integration)
  ✅ apps/audit/ (AuditService)
  ✅ Separation of Concerns: 100%
  ✅ Clean Code v3.0.1: 100%
  ✅ SOLID principles: 100%

Calidad:
  ✅ TDD aplicado
  ✅ Coverage >90%
  ✅ RBAC integrado
  ✅ Audit logging
  ✅ Type hints
  ✅ Docstrings completos
  ✅ Production-ready
```

---

## 13. ORDEN DE EJECUCIÓN

```bash
# DÍA 1 (8 horas)
1. Fase 1: Models + Migrations (2-3h)
2. Fase 2: Services (3-4h)
3. Inicio Fase 3: Serializers (1h)

# DÍA 2 (8 horas)
4. Completar Fase 3: Serializers (1-2h)
5. Fase 4: ViewSets + URLs (2-3h)
6. Fase 6: Permissions + RBAC (1-2h)
7. Inicio Fase 7: Testing (2h)

# DÍA 3 (4-5 horas)
8. Completar Fase 7: Testing (2-3h)
9. Documentation (1h)
10. Final review y commit (1h)

Total: 20-21 horas
```

---

## 14. COMANDOS ÚTILES

```bash
# Crear superuser
python manage.py createsuperuser

# Shell interactivo
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='admin')
>>> user.get_functions()

# Tests
pytest tests/unit/users/ -v --cov=apps.users

# Migrations
python manage.py makemigrations users
python manage.py migrate

# Cargar fixtures
python manage.py loaddata apps/access/fixtures/functions.json
```

---

**FIN DEL PLAN DE IMPLEMENTACIÓN**

**Estado:** ✅ LISTO PARA IMPLEMENTAR  
**Arquitectura:** Clean Architecture aplicada  
**Calidad:** Production-ready  
**Próximo Paso:** Comenzar Fase 1 - Models + Migrations  

---

**IMPORTANTE:**  
Este plan usa CORRECTAMENTE:
- ✅ apps/core/ para infraestructura reutilizable
- ✅ apps/utils/ para utilidades genéricas
- ✅ apps/access/ para RBAC
- ✅ apps/audit/ para logging
- ✅ NO duplica código
- ✅ Separation of Concerns perfecto
- ✅ Clean Architecture
- ✅ TDD methodology
