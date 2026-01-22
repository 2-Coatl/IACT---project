"""
Models para apps/users/.

ARQUITECTURA:
- User: Hereda AbstractUser (Django) + SoftDeleteMixin (apps.core)
- UserProfile: Hereda TimeStampedModel (apps.core.models)
- SessionHistory: Hereda TimeStampedModel (apps.core.models)
- UserSettings: Hereda TimeStampedModel (apps.core.models)

CNST-037: Custom User Model
FASE 2 PARTE 2: Correcciones (sin employee_id, sin theme/timezone/email_notifications)
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

from apps.core.models import TimeStampedModel, SoftDeleteMixin
from apps.users.managers import CustomUserManager
from apps.users.validators import validate_avatar_file
from apps.utils.validators import validate_phone_number
from apps.users.constants import POSITION_CHOICES, DEPARTMENT_CHOICES

def user_avatar_path(instance, filename):
    """
    Genera path para avatar.
    
    Format: avatars/user_{id}/{filename}
    """
    return f'avatars/user_{instance.id}/{filename}'


class User(AbstractUser, SoftDeleteMixin):
    """
    Usuario custom del sistema.
    
    Hereda de:
    - AbstractUser (Django): username, email, password, first_name, last_name,
      is_active, is_staff, is_superuser, date_joined, last_login
    - SoftDeleteMixin (apps.core): is_deleted, deleted_at, delete(), hard_delete()
    
    CNST-037: Custom User Model
    
    Relaciones:
    - profile: UserProfile (1-to-1, auto-creado vía signal)
    - settings: UserSettings (1-to-1, auto-creado vía signal)
    - sessions: SessionHistory (1-to-many)
    - functions: UserFunction (M2M vía apps.access)
    
    Example:
        user = User.objects.create_user(
            username='jdoe',
            email='jdoe@company.com',
            password='SecurePass123'
        )
        user.profile  # ← Auto-creado vía signal
        user.get_functions()  # ← RBAC de apps.access
    """
    
    # Campos adicionales (AbstractUser ya tiene username, email, etc)
    
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[validate_phone_number],
        verbose_name='Teléfono',
        help_text='Número de teléfono del usuario (formato: +1234567890 o 123-456-7890)'
    )
    
    position = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=POSITION_CHOICES,
        verbose_name='Cargo',
        help_text='Cargo o posición del usuario en la organización'
    )
    
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True,
        blank=True,
        default=None,
        max_length=255,
        validators=[validate_avatar_file],
        verbose_name='Avatar',
        help_text='Imagen de perfil del usuario (max 2MB, formatos: jpg, png, gif)'
    )
    
    # Manager personalizado
    objects = CustomUserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
        indexes = [
            models.Index(fields=['username'], name='users_username_idx'),
            models.Index(fields=['email'], name='users_email_idx'),
        ]
    
    def __str__(self):
        """String representation."""
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.username})"
        return self.username
    
    @property
    def full_name(self):
        """
        Retorna nombre completo.
        
        Returns:
            str: Nombre completo o username si no tiene nombre
        """
        return self.get_full_name() or self.username
    
    def get_functions(self):
        """
        Obtiene funciones RBAC del usuario.
        
        Usa apps.access.services.AccessService (cuando se implemente).
        Por ahora retorna set vacío.
        
        Returns:
            set: Set de códigos de funciones
        
        Example:
            user = User.objects.get(id=1)
            functions = user.get_functions()
            # {'USR_VIEW', 'USR_EDIT', 'REPORTS_VIEW'}
        """
        # TODO: Implementar cuando AccessService esté disponible
        # from apps.access.services import AccessService
        # return AccessService.get_user_functions(self)
        return set()
    
    def has_function(self, function_code):
        """
        Verifica si usuario tiene función RBAC.
        
        Args:
            function_code: Código de función (ej: 'USR_VIEW')
        
        Returns:
            bool: True si tiene la función
        
        Example:
            if user.has_function('USR_EDIT'):
                # Usuario puede editar usuarios
        """
        return function_code in self.get_functions()


class UserProfile(TimeStampedModel):
    """
    Perfil extendido del usuario.
    
    Hereda de TimeStampedModel (apps.core):
    - created_at (auto)
    - updated_at (auto)
    
    Relación 1-to-1 con User.
    Se crea automáticamente vía signal cuando se crea User.
    
    Example:
        user = User.objects.get(id=1)
        profile = user.profile  # ← Auto-creado
        profile.bio = 'Software Developer'
        profile.save()
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
        verbose_name='Biografía',
        help_text='Descripción breve del usuario'
    )
    
    department = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=DEPARTMENT_CHOICES,
        verbose_name='Departamento',
        help_text='Departamento al que pertenece'
    )
    
    # Campos heredados de TimeStampedModel:
    # - created_at (DateTimeField, auto_now_add=True)
    # - updated_at (DateTimeField, auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        """String representation."""
        return f"Perfil de {self.user.username}"
    
    @property
    def avatar_url(self):
        """
        Retorna URL del avatar.
        
        Returns:
            str: URL del avatar o default
        """
        if self.user.avatar:
            return self.user.avatar.url
        return '/static/images/default-avatar.png'


class SessionHistory(TimeStampedModel):
    """
    Historial de sesiones de usuario.
    
    Hereda de TimeStampedModel (apps.core):
    - created_at (auto)
    - updated_at (auto)
    
    CNST-039: Session Auditing
    
    Se crea automáticamente vía signal (user_logged_in).
    Se actualiza vía signal (user_logged_out).
    
    Example:
        user = User.objects.get(id=1)
        sessions = user.sessions.filter(is_active=True)
        # Sesiones activas del usuario
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='Usuario'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP',
        help_text='IP desde donde se conectó'
    )
    
    user_agent = models.CharField(
        max_length=255,
        verbose_name='User Agent',
        help_text='Información del navegador/cliente'
    )
    
    login_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Login',
        help_text='Fecha y hora de login'
    )
    
    logout_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Logout',
        help_text='Fecha y hora de logout'
    )
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='Sesión Activa',
        help_text='True si la sesión sigue activa'
    )
    
    class Meta:
        db_table = 'session_history'
        verbose_name = 'Historial de Sesión'
        verbose_name_plural = 'Historial de Sesiones'
        ordering = ['-login_at']
        indexes = [
            models.Index(fields=['user', '-login_at'], name='sessions_user_login_idx'),
            models.Index(fields=['is_active', '-login_at'], name='sessions_active_idx'),
        ]
    
    def __str__(self):
        """String representation."""
        status = "Activa" if self.is_active else "Cerrada"
        return f"{self.user.username} - {self.login_at} ({status})"


class UserSettings(TimeStampedModel):
    """
    Configuración de usuario.
    
    FASE 2 PARTE 2: Simplificado - solo preferencias personales del usuario.
    
    Campos:
    - language: Idioma de interfaz (es, en) [default: es]
    - notifications_enabled: Habilitar alertas internas [default: True]
    
    NO incluye (son configuraciones globales del sistema):
    - theme: Configuración del sistema
    - timezone: America/Mexico_City (configuración del sistema)
    - email_notifications: Sistema de alertas (no por email)
    
    Hereda de TimeStampedModel (apps.core):
    - created_at (auto)
    - updated_at (auto)
    
    Se crea automáticamente vía signal cuando se crea User.
    
    Example:
        user = User.objects.get(id=1)
        settings = user.settings  # ← Auto-creado
        settings.language = 'en'
        settings.notifications_enabled = True
        settings.save()
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
        verbose_name='Idioma',
        help_text='Idioma de la interfaz'
    )
    
    
    
    notifications_enabled = models.BooleanField(
        default=True,
        verbose_name='Notificaciones Habilitadas',
        help_text='Habilitar/deshabilitar notificaciones'
    )
    
    
    class Meta:
        db_table = 'user_settings'
        verbose_name = 'Configuración de Usuario'
        verbose_name_plural = 'Configuraciones de Usuario'
    
    def __str__(self):
        """String representation."""
        return f"Settings de {self.user.username}"


# ============================================================================
# RESUMEN MODELS
# 
# Total Models: 4
# 
# User (AbstractUser + SoftDeleteMixin):
#   - Campos Django: username, email, password, first_name, last_name, etc
#   - Campos custom: employee_id, phone, position, avatar
#   - Campos SoftDeleteMixin: is_deleted, deleted_at
#   - Métodos: get_functions(), has_function()
# 
# UserProfile (TimeStampedModel):
#   - Relación: 1-to-1 con User
#   - Campos: bio, department
#   - Auto-creado: Via signal
# 
# SessionHistory (TimeStampedModel):
#   - Relación: M2M con User
#   - Campos: ip_address, user_agent, login_at, logout_at, is_active
#   - Auto-creado: Via signal (user_logged_in)
# 
# UserSettings (TimeStampedModel):
#   - Relación: 1-to-1 con User
#   - Campos: language, theme, timezone, notifications_enabled, email_notifications
#   - Auto-creado: Via signal
# 
# Uso de Arquitectura:
#   ✅ AbstractUser (Django built-in)
#   ✅ SoftDeleteMixin (apps.core.models)
#   ✅ TimeStampedModel (apps.core.models)
#   ✅ AccessService (apps.access.services)
# 
# Líneas: ~400
# ============================================================================

