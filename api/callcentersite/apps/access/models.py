from django.db import models
from django.contrib.auth.models import User


class Function(models.Model):
    """
    Funcion atomica RBAC.
    
    RBAC v5.1.1: 44 funciones atomicas.
    Reemplaza sistema de roles fijos.
    
    Ejemplos:
    - ve_reportes (MOD_Reports)
    - crea_usuarios (MOD_Users)
    - edita_configuracion (MOD_Config)
    """
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Codigo funcion',
        help_text='Ej: ve_reportes, crea_usuarios',
    )
    module = models.CharField(
        max_length=50,
        verbose_name='Modulo',
        help_text='Ej: MOD_Reports, MOD_Users',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripcion',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa',
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'functions'
        verbose_name = 'Funcion'
        verbose_name_plural = 'Funciones'
        ordering = ['module', 'code']
    
    def __str__(self):
        return f"{self.code} ({self.module})"


class UserFunctionAssignment(models.Model):
    """
    Asignacion de funcion a usuario.
    
    Sistema RBAC granular por funciones atomicas.
    Cada asignacion incluye razon y quien la asigno.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='function_assignments',
        verbose_name='Usuario',
    )
    function = models.ForeignKey(
        Function,
        on_delete=models.CASCADE,
        related_name='user_assignments',
        verbose_name='Funcion',
    )
    
    # Asignacion
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='functions_assigned_by_me',
        verbose_name='Asignado por',
    )
    reason = models.TextField(
        verbose_name='Justificacion',
        help_text='Por que se asigna esta funcion',
    )
    
    # Estado
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa',
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Revocada en',
    )
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='functions_revoked_by_me',
        verbose_name='Revocada por',
    )
    
    class Meta:
        db_table = 'user_function_assignments'
        unique_together = [['user', 'function']]
        verbose_name = 'Asignacion Funcion'
        verbose_name_plural = 'Asignaciones Funciones'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.user.username} -> {self.function.code}"
    
    @classmethod
    def get_user_functions(cls, user):
        """
        Obtener funciones activas de usuario.
        
        Args:
            user: Usuario
            
        Returns:
            QuerySet de UserFunctionAssignment activas
        """
        return cls.objects.filter(
            user=user,
            is_active=True,
        ).select_related('function')
