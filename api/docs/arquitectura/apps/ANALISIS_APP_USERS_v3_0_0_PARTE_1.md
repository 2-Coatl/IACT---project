---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Users PARTE 1/4
categoria: arquitectura/apps
tema: apps/users/ - Fundamentos, Models y Autenticación
autor: Claude Technical Analysis
tags: [users, authentication, profiles, django-auth, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
estado: definitivo
parte: 1 de 4
relacionado:
  - ANALISIS_APP_ACCESS_v3_0_0.md (6 partes)
  - ANALISIS_APP_USERS_v3_0_0_PARTE_2.md
  - ANALISIS_APP_USERS_v3_0_0_PARTE_3.md
  - ANALISIS_APP_USERS_v3_0_0_PARTE_4.md
replaces: []
---

# ANÁLISIS DE apps/users/ v3.0.0 - PARTE 1/4
## FUNDAMENTOS, MODELS Y AUTENTICACIÓN

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen)
2. [Clean Code v3.0.1](#clean-code)
3. [Restricciones Arquitectónicas](#restricciones)
4. [Modelos Django](#modelos)
5. [Autenticación](#autenticacion)
6. [Constants](#constants)

---

<a name="resumen"></a>
## 1. RESUMEN EJECUTIVO

### 1.1 Información General

```yaml
App: apps/users/
Tipo: COMPLEJA (4 partes)
Líneas estimadas: ~4,500 líneas código
Propósito: Gestión de usuarios y autenticación
Funciones RBAC: 4 funciones (USR_VIEW, USR_EDIT, USR_DELETE, USR_PERMS)
Dependencias: apps/access/ (RBAC)
Tests: 45 tests estimados
Coverage objetivo: >90%
```

### 1.2 Responsabilidades

```yaml
Core:
  ✅ Gestión de usuarios (CRUD)
  ✅ Autenticación (login/logout)
  ✅ Perfiles de usuario
  ✅ Cambio de contraseña
  ✅ Recuperación de contraseña
  ✅ Integración con RBAC (apps/access)
  ✅ Historial de sesiones
  ✅ Configuración de usuario

Funcionalidades:
  - Custom User model (AbstractUser)
  - UserProfile (1-to-1)
  - SessionHistory (auditoría de sesiones)
  - UserSettings (preferencias)
  - Password policies
  - Email verification
  - Two-factor auth (planificado v6.1.0)

Integraciones:
  - apps/access/ (grupos, permisos)
  - apps/audit/ (logs de cambios)
  - Django auth system
  - Email backend
```

### 1.3 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                  apps/users/                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Models:                                            │
│  ├─ User (CustomUser)                              │
│  ├─ UserProfile (1-to-1)                           │
│  ├─ SessionHistory (auditoría)                     │
│  └─ UserSettings (preferencias)                    │
│                                                     │
│  Services:                                          │
│  ├─ UserService (CRUD, activation)                 │
│  ├─ AuthenticationService (login, logout)          │
│  ├─ ProfileService (gestión de perfiles)           │
│  └─ PasswordService (cambio, reset)                │
│                                                     │
│  API:                                               │
│  ├─ UserViewSet (CRUD users)                       │
│  ├─ ProfileViewSet (gestión perfil)                │
│  ├─ AuthViewSet (login, logout, cambio pass)       │
│  └─ SessionHistoryViewSet (auditoría)              │
│                                                     │
│  Integration:                                       │
│  ├─ apps/access/ (RBAC)                            │
│  ├─ apps/audit/ (logs)                             │
│  └─ Django auth backend                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

<a name="clean-code"></a>
## 2. CLEAN CODE v3.0.1

### 2.1 Naming Conventions

```python
# CLEAN_CODE v3.0.1 - apps/users/

# ============================================================================
# CLASES - PascalCase
# ============================================================================

# Modelos Django
class User(AbstractUser):               # ✅ Modelo principal
class UserProfile(models.Model):        # ✅ Perfil extendido
class SessionHistory(models.Model):     # ✅ Historial sesiones
class UserSettings(models.Model):       # ✅ Configuración usuario

# Services
class UserService:                      # ✅ Gestión usuarios
class AuthenticationService:            # ✅ Autenticación
class ProfileService:                   # ✅ Gestión perfiles
class PasswordService:                  # ✅ Gestión contraseñas

# Serializers
class UserSerializer:                   # ✅ User CRUD
class UserProfileSerializer:            # ✅ Profile
class LoginSerializer:                  # ✅ Login
class ChangePasswordSerializer:         # ✅ Cambio password

# ViewSets
class UserViewSet:                      # ✅ API usuarios
class ProfileViewSet:                   # ✅ API perfiles
class AuthViewSet:                      # ✅ API autenticación

# Exceptions
class UserNotFoundError:                # ✅ Usuario no existe
class InvalidCredentialsError:          # ✅ Credenciales inválidas
class WeakPasswordError:                # ✅ Contraseña débil

# ============================================================================
# MÉTODOS - snake_case (inglés técnico)
# ============================================================================

# CRUD
def create_user(username, email, password):     # ✅ Crear
def get_user(user_id):                          # ✅ Obtener
def update_user(user_id, data):                 # ✅ Actualizar
def delete_user(user_id):                       # ✅ Eliminar
def activate_user(user_id):                     # ✅ Activar
def deactivate_user(user_id):                   # ✅ Desactivar

# Autenticación
def authenticate_user(username, password):      # ✅ Autenticar
def login(request, username, password):         # ✅ Login
def logout(request):                            # ✅ Logout
def change_password(user, old_pass, new_pass):  # ✅ Cambiar contraseña
def reset_password(email):                      # ✅ Reset contraseña
def verify_email(token):                        # ✅ Verificar email

# Perfil
def get_user_profile(user):                     # ✅ Obtener perfil
def update_profile(user, data):                 # ✅ Actualizar perfil
def upload_avatar(user, file):                  # ✅ Subir avatar

# Sesiones
def create_session_log(user, ip, user_agent):   # ✅ Log sesión
def get_user_sessions(user):                    # ✅ Sesiones usuario
def revoke_session(session_id):                 # ✅ Revocar sesión

# ============================================================================
# VARIABLES - snake_case (español descriptivo)
# ============================================================================

user = get_user(1)                              # ✅ Usuario
user_profile = user.profile                     # ✅ Perfil
is_active = user.is_active                      # ✅ Estado
last_login = user.last_login                    # ✅ Último login
session_history = get_user_sessions(user)       # ✅ Historial
user_settings = user.settings                   # ✅ Configuración

# ============================================================================
# CONSTANTES - UPPER_SNAKE_CASE
# ============================================================================

MIN_PASSWORD_LENGTH = 8                         # ✅ Longitud mínima
MAX_LOGIN_ATTEMPTS = 5                          # ✅ Intentos máximos
SESSION_TIMEOUT = 3600                          # ✅ Timeout sesión
PASSWORD_RESET_TIMEOUT = 86400                  # ✅ Timeout reset
AVATAR_MAX_SIZE_MB = 5                          # ✅ Tamaño avatar
DEFAULT_AVATAR = 'avatars/default.png'          # ✅ Avatar por defecto

# ============================================================================
# DATABASE - Húngaro (heredado legacy)
# ============================================================================

# Tabla: tbl_usuarios
iIdUsuario                  # PK (int)           # ✅ ID usuario
cUsername                   # varchar(150)       # ✅ Username
cEmail                      # varchar(254)       # ✅ Email
cPassword                   # varchar(128)       # ✅ Password hash
cFirstName                  # varchar(150)       # ✅ Nombre
cLastName                   # varchar(150)       # ✅ Apellido
bIsActive                   # tinyint(1)         # ✅ Activo
bIsStaff                    # tinyint(1)         # ✅ Staff
bIsSuperuser                # tinyint(1)         # ✅ Superuser
dtDateJoined                # datetime           # ✅ Fecha registro
dtLastLogin                 # datetime           # ✅ Último login

# Tabla: tbl_perfil_usuario
iIdPerfil                   # PK (int)           # ✅ ID perfil
iIdUsuario                  # FK (int)           # ✅ Usuario
cAvatar                     # varchar(255)       # ✅ Avatar URL
cPhoneNumber                # varchar(20)        # ✅ Teléfono
cPosition                   # varchar(100)       # ✅ Cargo
cDepartment                 # varchar(100)       # ✅ Departamento
tBio                        # text               # ✅ Biografía
dtCreatedAt                 # datetime           # ✅ Fecha creación
dtUpdatedAt                 # datetime           # ✅ Fecha actualización

# Tabla: tbl_historial_sesiones
iIdSesion                   # PK (int)           # ✅ ID sesión
iIdUsuario                  # FK (int)           # ✅ Usuario
cIpAddress                  # varchar(45)        # ✅ IP
cUserAgent                  # varchar(255)       # ✅ User agent
dtLoginAt                   # datetime           # ✅ Login
dtLogoutAt                  # datetime           # ✅ Logout
bIsActive                   # tinyint(1)         # ✅ Sesión activa

# ============================================================================
# PERMISSIONS - apps/access/
# ============================================================================

# Módulo: MOD_Users (iIdModulo=9)
USR_VIEW    = 'USR_VIEW'       # Ver usuarios
USR_EDIT    = 'USR_EDIT'       # Editar usuarios
USR_DELETE  = 'USR_DELETE'     # Eliminar usuarios
USR_PERMS   = 'USR_PERMS'      # Gestionar permisos

# Permission strings (function.permission_string)
'user.view'                    # USR_VIEW
'user.edit'                    # USR_EDIT
'user.delete'                  # USR_DELETE
'user.perms'                   # USR_PERMS
```

---

<a name="restricciones"></a>
## 3. RESTRICCIONES ARQUITECTÓNICAS

### 3.1 CNST-037: Custom User Model

```yaml
CNST-037: Custom User Model (🔴 CRÍTICO)

Descripción:
  Django permite extender el User model mediante AbstractUser o AbstractBaseUser.
  IACT usa AbstractUser para mantener compatibilidad con Django admin.

Reglas:
  1. User model DEBE heredar de AbstractUser
  2. UserProfile DEBE ser 1-to-1 con User
  3. NO modificar campos core de Django (username, password, etc)
  4. SÍ agregar campos adicionales en UserProfile
  5. AUTH_USER_MODEL debe apuntar a apps.users.User

Implementación:
  # settings.py
  AUTH_USER_MODEL = 'users.User'
  
  # models.py
  class User(AbstractUser):
      # Campos adicionales opcionales
      employee_id = models.CharField(max_length=50, unique=True, null=True)
      
      class Meta:
          db_table = 'tbl_usuarios'
  
  class UserProfile(models.Model):
      user = models.OneToOneField(User, on_delete=models.CASCADE)
      avatar = models.ImageField(upload_to='avatars/')
      # ... más campos

Justificación:
  - Compatibilidad con Django ecosystem
  - Facilita migraciones
  - Admin panel funciona out-of-box
  - apps/access/ integra directamente
```

### 3.2 CNST-038: Password Policies

```yaml
CNST-038: Password Policies (🔴 CRÍTICO)

Descripción:
  Políticas de contraseñas para compliance y seguridad.

Reglas:
  1. Longitud mínima: 8 caracteres
  2. DEBE contener: mayúscula, minúscula, número
  3. NO usar contraseñas comunes (Django CommonPasswordValidator)
  4. NO usar username en password (Django UserAttributeSimilarityValidator)
  5. Cambio de contraseña cada 90 días (recomendado)
  6. Historial de 5 contraseñas (no reutilizar)

Implementación:
  # settings.py
  AUTH_PASSWORD_VALIDATORS = [
      {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
      {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
      {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
      {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
  ]
  
  # Custom validator
  class PasswordHistoryValidator:
      def validate(self, password, user):
          # Check últimas 5 contraseñas
          pass

Justificación:
  - Compliance SOX/GDPR
  - Prevención de ataques
  - Estándar industria
```

### 3.3 CNST-039: Session Auditing

```yaml
CNST-039: Session Auditing (⚠️ IMPORTANTE)

Descripción:
  Auditoría de sesiones para compliance y seguridad.

Reglas:
  1. Log TODOS los login/logout
  2. Registrar IP, user agent, timestamp
  3. Detectar intentos fallidos (max 5)
  4. Bloquear cuenta tras N intentos
  5. Sesiones expiradas tras inactividad (30 min)
  6. Revocación de sesiones activas

Implementación:
  # SessionHistory model
  class SessionHistory(models.Model):
      user = models.ForeignKey(User)
      ip_address = models.GenericIPAddressField()
      user_agent = models.CharField(max_length=255)
      login_at = models.DateTimeField(auto_now_add=True)
      logout_at = models.DateTimeField(null=True)
      is_active = models.BooleanField(default=True)
  
  # Signal post_login
  @receiver(user_logged_in)
  def log_user_login(sender, request, user, **kwargs):
      SessionHistory.objects.create(
          user=user,
          ip_address=get_client_ip(request),
          user_agent=request.META.get('HTTP_USER_AGENT')
      )

Justificación:
  - Compliance auditoría
  - Detección de intrusiones
  - Debugging sesiones
```

---

<a name="modelos"></a>
## 4. MODELOS DJANGO

### 4.1 User Model (Custom)

```python
"""
Custom User model para IACT.

Hereda de AbstractUser (CNST-037).
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    User model personalizado.
    
    CNST-037: Hereda de AbstractUser para compatibilidad.
    
    Campos heredados de AbstractUser:
    - username, first_name, last_name, email
    - password, is_staff, is_active, is_superuser
    - date_joined, last_login
    
    Campos adicionales:
    - employee_id: ID de empleado (opcional)
    
    Relations:
    - profile (1-to-1 UserProfile)
    - sessions (1-to-many SessionHistory)
    - settings (1-to-1 UserSettings)
    - group_memberships (many-to-many UserGroup via apps/access)
    """
    
    # Campo adicional opcional
    employee_id = models.CharField(
        'ID Empleado',
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_column='cEmployeeId'
    )
    
    class Meta:
        db_table = 'tbl_usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
    
    def __str__(self):
        """String representation."""
        return self.username
    
    @property
    def full_name(self):
        """Nombre completo del usuario."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def has_function(self, function_code):
        """
        Verifica si usuario tiene función RBAC.
        
        Delegado a apps.access.services.RBACService.
        
        Args:
            function_code: Código de función (ej: 'USR_VIEW')
        
        Returns:
            bool: True si tiene función
        """
        from apps.access.services import RBACService
        
        rbac_service = RBACService()
        return rbac_service.has_function(self, function_code)
    
    def get_functions(self):
        """
        Obtiene funciones RBAC del usuario.
        
        Returns:
            Set[str]: Set de códigos de funciones
        """
        from apps.access.services import RBACService
        
        rbac_service = RBACService()
        return rbac_service.get_user_functions(self)


class UserProfile(models.Model):
    """
    Perfil extendido del usuario.
    
    CNST-037: Relación 1-to-1 con User.
    
    Campos adicionales que no están en User base.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        db_column='iIdUsuario'
    )
    
    avatar = models.ImageField(
        'Avatar',
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True,
        db_column='cAvatar'
    )
    
    phone_number = models.CharField(
        'Teléfono',
        max_length=20,
        blank=True,
        db_column='cPhoneNumber'
    )
    
    position = models.CharField(
        'Cargo',
        max_length=100,
        blank=True,
        db_column='cPosition'
    )
    
    department = models.CharField(
        'Departamento',
        max_length=100,
        blank=True,
        db_column='cDepartment'
    )
    
    bio = models.TextField(
        'Biografía',
        blank=True,
        db_column='tBio'
    )
    
    created_at = models.DateTimeField(
        'Fecha Creación',
        auto_now_add=True,
        db_column='dtCreatedAt'
    )
    
    updated_at = models.DateTimeField(
        'Fecha Actualización',
        auto_now=True,
        db_column='dtUpdatedAt'
    )
    
    class Meta:
        db_table = 'tbl_perfil_usuario'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
    
    def __str__(self):
        """String representation."""
        return f"Perfil de {self.user.username}"
    
    @property
    def avatar_url(self):
        """URL del avatar o default."""
        if self.avatar:
            return self.avatar.url
        return '/static/images/avatars/default.png'


class SessionHistory(models.Model):
    """
    Historial de sesiones de usuario.
    
    CNST-039: Auditoría de sesiones.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        db_column='iIdUsuario'
    )
    
    ip_address = models.GenericIPAddressField(
        'Dirección IP',
        db_column='cIpAddress'
    )
    
    user_agent = models.CharField(
        'User Agent',
        max_length=255,
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
        'Sesión Activa',
        default=True,
        db_column='bIsActive'
    )
    
    class Meta:
        db_table = 'tbl_historial_sesiones'
        verbose_name = 'Sesión'
        verbose_name_plural = 'Historial de Sesiones'
        ordering = ['-login_at']
    
    def __str__(self):
        """String representation."""
        return f"{self.user.username} - {self.login_at}"
    
    @property
    def duration(self):
        """Duración de la sesión."""
        if self.logout_at:
            return self.logout_at - self.login_at
        return None


class UserSettings(models.Model):
    """
    Configuración personal del usuario.
    
    Preferencias, idioma, tema, etc.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='settings',
        db_column='iIdUsuario'
    )
    
    language = models.CharField(
        'Idioma',
        max_length=10,
        default='es',
        choices=[
            ('es', 'Español'),
            ('en', 'English'),
        ],
        db_column='cLanguage'
    )
    
    theme = models.CharField(
        'Tema',
        max_length=20,
        default='light',
        choices=[
            ('light', 'Claro'),
            ('dark', 'Oscuro'),
        ],
        db_column='cTheme'
    )
    
    timezone = models.CharField(
        'Zona Horaria',
        max_length=50,
        default='America/Santiago',
        db_column='cTimezone'
    )
    
    notifications_enabled = models.BooleanField(
        'Notificaciones',
        default=True,
        db_column='bNotificationsEnabled'
    )
    
    email_notifications = models.BooleanField(
        'Notificaciones Email',
        default=True,
        db_column='bEmailNotifications'
    )
    
    created_at = models.DateTimeField(
        'Fecha Creación',
        auto_now_add=True,
        db_column='dtCreatedAt'
    )
    
    updated_at = models.DateTimeField(
        'Fecha Actualización',
        auto_now=True,
        db_column='dtUpdatedAt'
    )
    
    class Meta:
        db_table = 'tbl_configuracion_usuario'
        verbose_name = 'Configuración de Usuario'
        verbose_name_plural = 'Configuraciones de Usuarios'
    
    def __str__(self):
        """String representation."""
        return f"Config de {self.user.username}"
```

---

<a name="autenticacion"></a>
## 5. AUTENTICACIÓN

### 5.1 Settings Configuration

```python
# config/settings/base.py

# User model custom (CNST-037)
AUTH_USER_MODEL = 'users.User'

# Password validators (CNST-038)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Session configuration
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Login/Logout URLs
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/users/login/'

# Email backend (para password reset)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@iact.com'
EMAIL_HOST_PASSWORD = '***'

# Media files (avatars)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 5.2 Signals

```python
"""
Signals para User model.

Auto-creación de Profile y Settings.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out

from apps.users.models import User, UserProfile, UserSettings, SessionHistory


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
    """
    ip_address = get_client_ip(request)
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
        # Buscar sesión activa y cerrarla
        from django.utils import timezone
        
        SessionHistory.objects.filter(
            user=user,
            is_active=True
        ).update(
            logout_at=timezone.now(),
            is_active=False
        )


def get_client_ip(request):
    """Obtiene IP del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

---

<a name="constants"></a>
## 6. CONSTANTS

### 6.1 Archivo: apps/users/constants.py

```python
"""
Constants para apps/users/.

CLEAN_CODE v3.0.1: UPPER_SNAKE_CASE.
"""

# Password policies (CNST-038)
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
PASSWORD_RESET_TIMEOUT = 86400  # 24 horas
PASSWORD_HISTORY_COUNT = 5  # No reutilizar últimas 5

# Login
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_DURATION = 900  # 15 minutos
SESSION_TIMEOUT = 3600  # 1 hora

# Avatar
AVATAR_MAX_SIZE_MB = 5
AVATAR_ALLOWED_FORMATS = ['jpg', 'jpeg', 'png', 'gif']
DEFAULT_AVATAR = 'avatars/default.png'

# Email verification
EMAIL_VERIFICATION_TIMEOUT = 86400  # 24 horas

# User status
USER_STATUS_ACTIVE = 'active'
USER_STATUS_INACTIVE = 'inactive'
USER_STATUS_LOCKED = 'locked'
USER_STATUS_PENDING = 'pending'

# Funciones RBAC (referencia)
# Definidas en apps/access/fixtures/functions.json
USR_VIEW = 'USR_VIEW'       # Ver usuarios
USR_EDIT = 'USR_EDIT'       # Editar usuarios
USR_DELETE = 'USR_DELETE'   # Eliminar usuarios
USR_PERMS = 'USR_PERMS'     # Gestionar permisos

# Permission strings
PERM_USER_VIEW = 'user.view'
PERM_USER_EDIT = 'user.edit'
PERM_USER_DELETE = 'user.delete'
PERM_USER_PERMS = 'user.perms'
```

---

## 7. RESUMEN PARTE 1

### 7.1 Componentes Generados

```yaml
Modelos Django (4):
  ✅ User (CustomUser, AbstractUser)
  ✅ UserProfile (1-to-1)
  ✅ SessionHistory (auditoría)
  ✅ UserSettings (preferencias)

Signals (4):
  ✅ create_user_profile (post_save User)
  ✅ save_user_profile (post_save User)
  ✅ create_user_settings (post_save User)
  ✅ log_user_login (user_logged_in)

Configuration:
  ✅ AUTH_USER_MODEL = 'users.User'
  ✅ AUTH_PASSWORD_VALIDATORS (4 validators)
  ✅ SESSION settings
  ✅ MEDIA settings (avatars)

Constants:
  ✅ Password policies
  ✅ Login/session
  ✅ Avatar settings
  ✅ RBAC functions

Líneas código: ~850 líneas Python
```

### 7.2 Restricciones Aplicadas

```yaml
✅ CNST-037: Custom User Model
   - Hereda de AbstractUser
   - AUTH_USER_MODEL configurado
   - UserProfile 1-to-1

✅ CNST-038: Password Policies
   - 4 validadores Django
   - MIN_PASSWORD_LENGTH = 8
   - No contraseñas comunes

✅ CNST-039: Session Auditing
   - SessionHistory model
   - Signals login/logout
   - IP + user agent logged
```

---

## PRÓXIMA PARTE

**PARTE 2/4: Services y User Management**

Contenido:
- ✅ UserService (CRUD completo)
- ✅ AuthenticationService (login/logout/reset)
- ✅ ProfileService (gestión perfil)
- ✅ PasswordService (cambio/reset/validación)
- ✅ Utils (helpers)
- ✅ Exceptions (5 exceptions)

**Estimado:** ~1,100 líneas, 3 horas

---

**Fin de PARTE 1/4**
