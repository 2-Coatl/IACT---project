"""
Custom User model con SoftDeleteMixin, Avatar y RBAC.

Extiende AbstractUser de Django para agregar:
- SoftDeleteMixin (delete lógico)
- Avatar (imagen de perfil)
- Metodos RBAC (get_functions, has_function)
- Campos personalizados (phone, position, employee_id)
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.utils import SoftDeleteMixin
import os


def user_avatar_path(instance, filename):
    """
    Genera ruta de almacenamiento para avatar de usuario.
    
    Formato: media/profiles/user_{id}/{filename}
    Ejemplo: media/profiles/user_123/avatar.jpg
    """
    ext = os.path.splitext(filename)[1]
    return f'profiles/user_{instance.id}/avatar{ext}'


class CustomUser(SoftDeleteMixin, AbstractUser):
    """
    Usuario personalizado del sistema IACT.
    
    Hereda de:
    - AbstractUser: Funcionalidad completa de usuario Django
    - SoftDeleteMixin: Delete lógico
    
    Campos heredados de AbstractUser:
    - username, password, email
    - first_name, last_name
    - is_staff, is_active, is_superuser
    - date_joined, last_login
    - groups, user_permissions
    
    Campos de SoftDeleteMixin:
    - is_deleted, deleted_at
    
    Campos adicionales:
    - avatar: Imagen de perfil
    - phone: Telefono
    - position: Cargo
    - employee_id: ID de empleado
    
    Manager:
    - objects: SoftDeleteManager (excluye eliminados por defecto)
    """
    
    # Campos personalizados
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        default=None,
        max_length=255,
        verbose_name='Avatar',
        help_text='Imagen de perfil del usuario (max 2MB, formatos: jpg, png, gif)'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Telefono',
        help_text='Numero de telefono del usuario'
    )
    
    position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Cargo',
        help_text='Cargo o posicion del usuario en la organizacion'
    )
    
    employee_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name='ID Empleado',
        help_text='Identificador unico del empleado'
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
        full_name = self.get_full_name()
        if full_name and full_name != self.username:
            return f"{full_name} ({self.username})"
        return self.username
    
    def get_full_name(self):
        """
        Retorna nombre completo del usuario.
        
        Returns:
            str: "first_name last_name" o username si no hay nombre
        """
        full_name = super().get_full_name()
        return full_name if full_name.strip() else self.username
    
    def get_avatar_url(self):
        """
        Retorna URL completa del avatar del usuario.
        Si no tiene avatar, retorna el icono por defecto.
        
        Returns:
            str: URL del avatar o default
        """
        if self.avatar:
            return self.avatar.url
        return '/static/icons/defaults/avatar_default.png'
    
    def get_functions(self):
        """
        Obtiene lista de funciones RBAC del usuario.
        
        Incluye:
        - Funciones directas asignadas
        - Funciones heredadas de grupos
        
        Returns:
            List[str]: Lista de nombres de funciones
        """
        functions = set()
        
        # Funciones directas (UserFunction)
        if hasattr(self, 'user_functions'):
            try:
                direct_functions = self.user_functions.filter(
                    is_active=True
                ).values_list('function__name', flat=True)
                functions.update(direct_functions)
            except Exception:
                pass
        
        # Funciones de grupos (FunctionGroup)
        if hasattr(self, 'function_groups'):
            try:
                for group in self.function_groups.filter(is_active=True):
                    group_functions = group.functions.filter(
                        is_active=True
                    ).values_list('name', flat=True)
                    functions.update(group_functions)
            except Exception:
                pass
        
        return list(functions)
    
    def has_function(self, function_name):
        """
        Verifica si el usuario tiene una funcion especifica.
        
        Args:
            function_name (str): Nombre de la funcion (ej: 'view_reports')
        
        Returns:
            bool: True si tiene la funcion
        """
        user_functions = self.get_functions()
        return function_name in user_functions
    
    def has_any_function(self, function_names):
        """
        Verifica si el usuario tiene alguna de las funciones.
        
        Args:
            function_names (list): Lista de nombres de funciones
        
        Returns:
            bool: True si tiene al menos una funcion
        """
        user_functions = set(self.get_functions())
        required = set(function_names)
        return bool(user_functions.intersection(required))
    
    def has_all_functions(self, function_names):
        """
        Verifica si el usuario tiene todas las funciones.
        
        Args:
            function_names (list): Lista de nombres de funciones
        
        Returns:
            bool: True si tiene todas las funciones
        """
        user_functions = set(self.get_functions())
        required = set(function_names)
        return required.issubset(user_functions)
    
    def delete_avatar(self):
        """
        Elimina el archivo fisico del avatar.
        
        Returns:
            bool: True si se elimino correctamente
        """
        if self.avatar:
            avatar_path = self.avatar.path
            if os.path.exists(avatar_path):
                try:
                    os.remove(avatar_path)
                    self.avatar = None
                    self.save()
                    return True
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error eliminando avatar de {self.username}: {e}")
                    return False
        return False
