from django.db import models
from django.conf import settings

from apps.core.models import SoftDeleteMixin


class Function(SoftDeleteMixin, models.Model):
    """
    Funcion atomica RBAC.
    
    RBAC v5.1.1: 44 funciones atomicas.
    Reemplaza sistema de roles fijos.
    
    Usa SoftDeleteMixin para delete lógico.
    
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


class UserFunctionAssignment(SoftDeleteMixin, models.Model):
    """
    Asignacion de funcion a usuario.
    
    Sistema RBAC granular por funciones atomicas.
    Cada asignacion incluye razon y quien la asigno.
    
    Usa SoftDeleteMixin para delete lógico.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Usar string para evitar circular import
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
        settings.AUTH_USER_MODEL,  # ← Usar string para evitar circular import
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
        settings.AUTH_USER_MODEL,  # ← Usar string para evitar circular import
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


class Module(SoftDeleteMixin, models.Model):
    """
    Módulo del sistema con jerarquía padre-hijo.
    
    Sistema de módulos jerárquico para control de acceso granular.
    Cada módulo puede tener un padre y múltiples hijos.
    
    Ejemplos:
    - MOD_Dashboard (padre: None)
    - MOD_Reports (padre: None)
      - MOD_Reports_View (padre: MOD_Reports)
      - MOD_Reports_Export (padre: MOD_Reports)
    - MOD_Users (padre: None)
      - MOD_Users_Create (padre: MOD_Users)
      - MOD_Users_Edit (padre: MOD_Users)
    """
    
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name='Código',
        help_text='Código único del módulo (ej: MOD_Dashboard)',
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre',
        help_text='Nombre descriptivo del módulo',
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción detallada del módulo',
    )
    
    # Jerarquía
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Módulo padre',
        help_text='Módulo padre en la jerarquía (None para raíz)',
    )
    
    # Orden y UI
    order = models.IntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden de visualización',
    )
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Icono',
        help_text='Nombre del icono (ej: dashboard, report)',
    )
    
    url_path = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='URL Path',
        help_text='Ruta URL del módulo (ej: /dashboard)',
    )
    
    # Estado
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Módulo activo en el sistema',
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'modules'
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['order', 'code']
        indexes = [
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['code', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_ancestors(self):
        """
        Obtener todos los ancestros (padres) del módulo.
        
        Returns:
            list: Lista de módulos ancestros (de más cercano a raíz)
        """
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    def get_descendants(self):
        """
        Obtener todos los descendientes (hijos) del módulo recursivamente.
        
        Returns:
            QuerySet: Todos los módulos descendientes
        """
        descendants = []
        children = self.children.all()
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def is_root(self):
        """
        Verificar si es módulo raíz.
        
        Returns:
            bool: True si no tiene padre
        """
        return self.parent is None
    
    def get_level(self):
        """
        Obtener nivel en la jerarquía.
        
        Returns:
            int: 0 para raíz, 1 para hijo directo, etc.
        """
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level


class UserModuleAccess(SoftDeleteMixin, models.Model):
    """
    Acceso de usuario a módulo.
    
    Gestiona qué usuarios tienen acceso a qué módulos.
    Un usuario con acceso a un módulo padre automáticamente
    tiene acceso a todos sus hijos.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Usar string para evitar circular import
        on_delete=models.CASCADE,
        related_name='module_accesses',
        verbose_name='Usuario',
    )
    
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='user_accesses',
        verbose_name='Módulo',
    )
    
    # Asignación
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Otorgado en',
    )
    
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Usar string para evitar circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='module_accesses_granted',
        verbose_name='Otorgado por',
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name='Razón',
        help_text='Por qué se otorgó este acceso',
    )
    
    # Estado
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
    )
    
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Revocado en',
    )
    
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Usar string para evitar circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='module_accesses_revoked',
        verbose_name='Revocado por',
    )
    
    class Meta:
        db_table = 'user_module_accesses'
        verbose_name = 'Acceso a Módulo'
        verbose_name_plural = 'Accesos a Módulos'
        unique_together = [['user', 'module']]
        ordering = ['-granted_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['module', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} -> {self.module.code}"
    
    @classmethod
    def get_user_modules(cls, user, include_children=True):
        """
        Obtener módulos accesibles por usuario.
        
        Args:
            user: Usuario
            include_children: Si True, incluye hijos de módulos asignados
            
        Returns:
            QuerySet: Módulos accesibles
        """
        # Módulos directamente asignados
        direct_modules = Module.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            is_active=True,
        ).distinct()
        
        if not include_children:
            return direct_modules
        
        # Incluir todos los hijos recursivamente
        all_modules = set(direct_modules)
        for module in direct_modules:
            descendants = module.get_descendants()
            all_modules.update(descendants)
        
        # Filtrar activos
        module_ids = [m.id for m in all_modules if m.is_active]
        return Module.objects.filter(id__in=module_ids)
    
    def has_access_to_module(self, module):
        """
        Verificar si el usuario tiene acceso a un módulo específico.
        
        Considera jerarquía: si tiene acceso al padre, tiene acceso al hijo.
        
        Args:
            module: Módulo a verificar
            
        Returns:
            bool: True si tiene acceso
        """
        # Verificar acceso directo
        if self.module == module:
            return self.is_active
        
        # Verificar si tiene acceso a algún ancestro
        ancestors = module.get_ancestors()
        return UserModuleAccess.objects.filter(
            user=self.user,
            module__in=ancestors,
            is_active=True,
        ).exists()


# ============================================================================
# USER SERVICE ACCESS
# ============================================================================

# ====================================================================================
# REMOVED - FASE A DT-002
# ====================================================================================
#
# UserServiceAccess (eliminado 2026-01-21):
#   - Conceptualmente diferente de RBAC
#   - Mezcla permisos RBAC con acceso a servicios 800
#   - Reemplazado por RBAC puro con Functions (CALL_VIEW, CALL_EDIT, etc)
#
# Migration: Ver 000X_remove_user_service_access.py
# ====================================================================================

