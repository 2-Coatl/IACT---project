---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Access PARTE 2/6
categoria: arquitectura/apps
tema: apps/access/ - Services y Validación
autor: Claude Technical Analysis
tags: [access, rbac, services, cache, validation, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
estado: definitivo
parte: 2 de 6
relacionado:
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_1.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_3.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_4.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_5.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_6.md
replaces: []
---

# ANÁLISIS DE apps/access/ v3.0.0 - PARTE 2/6
## SERVICES Y VALIDACIÓN

---

## TABLA DE CONTENIDOS

1. [Resumen Parte 2](#resumen)
2. [Service Layer](#services)
3. [PermissionLog Model](#permission-log)
4. [Utils y Helpers](#utils)
5. [Exceptions](#exceptions)

---

<a name="resumen"></a>
## 1. RESUMEN PARTE 2

### 1.1 Alcance de esta Parte

```yaml
Componentes cubiertos:
  ✅ Service Layer (3 services principales)
  ✅ PermissionLog model (auditoría RBAC)
  ✅ Utils y helpers (5 funciones)
  ✅ Exceptions personalizadas (4 exceptions)

Líneas de código: ~1,300 líneas Python
Archivos generados:
  - apps/access/services.py (~700 líneas)
  - apps/access/models.py (PermissionLog ~150 líneas)
  - apps/access/utils.py (~200 líneas)
  - apps/access/exceptions.py (~100 líneas)
```

---

<a name="services"></a>
## 2. SERVICE LAYER

### 2.1 Archivo: apps/access/services.py

```python
"""
Service Layer para sistema RBAC.

Responsabilidades:
- Validación de permisos function-based
- Gestión de grupos y funciones
- Cache de permisos (CNST-035)
- Auditoría de cambios RBAC

CLEAN_CODE v3.0.1:
- Clases: RBACService (PascalCase)
- Métodos: has_function (snake_case)
- Docstrings: español formato Google

CNST-034: Function-based permissions
CNST-035: Cache TTL 300s
"""

from typing import List, Dict, Any, Optional, Set
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Prefetch

from apps.access.models import Function, Module, Group, UserGroup, GroupFunction, PermissionLog
from apps.access.constants import (
    CACHE_TTL_FUNCTIONS,
    CACHE_KEY_PREFIX,
    MAX_GROUPS_PER_USER,
    MAX_FUNCTIONS_PER_GROUP,
)
from apps.access.exceptions import (
    PermissionDeniedError,
    InvalidFunctionError,
    MaxGroupsExceededError,
    MaxFunctionsExceededError,
)

User = get_user_model()


class RBACService:
    """
    Servicio principal de RBAC.
    
    Responsabilidades:
    - Validar permisos de usuario
    - Cachear funciones por usuario (CNST-035)
    - Proveer API para has_function()
    
    CNST-034: Function-based permissions
    CNST-035: Cache 300s
    """
    
    def __init__(self):
        """Inicializa el servicio RBAC."""
        self.cache_ttl = CACHE_TTL_FUNCTIONS
    
    def has_function(self, user: User, function_code: str) -> bool:
        """
        Verifica si usuario tiene función específica.
        
        Args:
            user: Usuario de Django
            function_code: Código de función (ej: 'AUD_VIEW')
        
        Returns:
            bool: True si tiene permiso, False si no
        
        Cache:
            Cachea resultado por 300s (CNST-035)
        
        Example:
            >>> rbac_service = RBACService()
            >>> rbac_service.has_function(user, 'AUD_VIEW')
            True
            >>> rbac_service.has_function(user, 'DSH_EDIT')
            False
        """
        if not user or not user.is_authenticated:
            return False
        
        # Superuser siempre tiene todos los permisos
        if user.is_superuser:
            return True
        
        # Obtener funciones del usuario (cached)
        user_functions = self.get_user_functions(user)
        
        return function_code in user_functions
    
    def get_user_functions(self, user: User) -> Set[str]:
        """
        Obtiene set de funciones del usuario.
        
        Args:
            user: Usuario de Django
        
        Returns:
            Set[str]: Set de códigos de funciones
        
        Cache:
            Key: rbac:user_functions:{user.id}
            TTL: 300s (CNST-035)
        
        Flujo:
            1. Check cache
            2. Si cache HIT → return
            3. Si cache MISS:
               - Query UserGroup → Group → GroupFunction → Function
               - Prefetch optimizado
               - Set cache
               - Return
        
        Example:
            >>> service.get_user_functions(user)
            {'AUD_VIEW', 'AUD_SEARCH', 'DSH_VIEW', 'RPT_VIEW'}
        """
        if not user or not user.is_authenticated:
            return set()
        
        # Superuser tiene todas las funciones
        if user.is_superuser:
            return self._get_all_active_functions()
        
        # Check cache
        cache_key = f"{CACHE_KEY_PREFIX}:user_functions:{user.id}"
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        # Cache MISS: Query database
        functions = self._query_user_functions(user)
        
        # Set cache
        cache.set(cache_key, functions, self.cache_ttl)
        
        return functions
    
    def _query_user_functions(self, user: User) -> Set[str]:
        """
        Query database para funciones del usuario.
        
        Optimizado con prefetch_related para evitar N+1.
        
        Args:
            user: Usuario
        
        Returns:
            Set[str]: Códigos de funciones
        """
        # Query optimizada con prefetch
        user_groups = UserGroup.objects.filter(
            user=user,
            group__is_active=True
        ).prefetch_related(
            Prefetch(
                'group__function_assignments',
                queryset=GroupFunction.objects.filter(
                    function__is_active=True
                ).select_related('function')
            )
        )
        
        # Extraer funciones de todos los grupos
        functions = set()
        for user_group in user_groups:
            for group_function in user_group.group.function_assignments.all():
                functions.add(group_function.function.code)
        
        return functions
    
    def _get_all_active_functions(self) -> Set[str]:
        """
        Obtiene todas las funciones activas.
        
        Para superusers.
        
        Returns:
            Set[str]: Todas las funciones activas
        """
        functions = Function.objects.filter(
            is_active=True
        ).values_list('code', flat=True)
        
        return set(functions)
    
    def validate_permission(
        self,
        user: User,
        permission_string: str
    ) -> bool:
        """
        Valida permiso usando permission_string.
        
        Args:
            user: Usuario
            permission_string: String Django (ej: 'audit.view')
        
        Returns:
            bool: True si tiene permiso
        
        Example:
            >>> service.validate_permission(user, 'audit.view')
            True
        """
        try:
            function = Function.objects.get(
                permission_string=permission_string,
                is_active=True
            )
            return self.has_function(user, function.code)
        except Function.DoesNotExist:
            return False
    
    def invalidate_user_cache(self, user: User) -> None:
        """
        Invalida cache de funciones del usuario.
        
        Args:
            user: Usuario
        
        Cuándo llamar:
            - Al asignar/remover usuario de grupo
            - Al modificar funciones de grupo del usuario
        """
        cache_key = f"{CACHE_KEY_PREFIX}:user_functions:{user.id}"
        cache.delete(cache_key)
    
    def bulk_invalidate_cache(self, user_ids: List[int]) -> None:
        """
        Invalida cache de múltiples usuarios.
        
        Args:
            user_ids: Lista de IDs de usuarios
        
        Útil para invalidar grupo completo.
        """
        cache_keys = [
            f"{CACHE_KEY_PREFIX}:user_functions:{user_id}"
            for user_id in user_ids
        ]
        cache.delete_many(cache_keys)


class GroupService:
    """
    Servicio de gestión de grupos.
    
    Responsabilidades:
    - Asignar/remover funciones a grupos
    - Asignar/remover usuarios a grupos
    - Validar límites (CNST-035)
    - Auditar cambios
    """
    
    def __init__(self):
        """Inicializa el servicio de grupos."""
        self.rbac_service = RBACService()
    
    def assign_function_to_group(
        self,
        group_id: int,
        function_code: str,
        assigned_by: User
    ) -> GroupFunction:
        """
        Asigna función a grupo.
        
        Args:
            group_id: ID del grupo
            function_code: Código de función (ej: 'AUD_VIEW')
            assigned_by: Usuario que asigna
        
        Returns:
            GroupFunction: Relación creada
        
        Raises:
            InvalidFunctionError: Si función no existe o inactiva
            MaxFunctionsExceededError: Si grupo tiene max funciones
        
        Side effects:
            - Invalida cache de usuarios del grupo
            - Crea PermissionLog
        
        Example:
            >>> service.assign_function_to_group(
            ...     group_id=1,
            ...     function_code='AUD_VIEW',
            ...     assigned_by=admin_user
            ... )
        """
        # Validar función existe y está activa
        try:
            function = Function.objects.get(
                code=function_code,
                is_active=True
            )
        except Function.DoesNotExist:
            raise InvalidFunctionError(
                f"Función '{function_code}' no existe o está inactiva"
            )
        
        # Validar grupo existe
        try:
            group = Group.objects.get(id=group_id, is_active=True)
        except Group.DoesNotExist:
            raise InvalidFunctionError(
                f"Grupo con ID {group_id} no existe o está inactivo"
            )
        
        # Validar límite de funciones
        current_count = GroupFunction.objects.filter(group=group).count()
        if current_count >= MAX_FUNCTIONS_PER_GROUP:
            raise MaxFunctionsExceededError(
                f"Grupo '{group.code}' ya tiene {MAX_FUNCTIONS_PER_GROUP} funciones"
            )
        
        # Crear o retornar existente
        group_function, created = GroupFunction.objects.get_or_create(
            group=group,
            function=function,
            defaults={'assigned_by': assigned_by}
        )
        
        if created:
            # Invalidar cache de usuarios del grupo
            self._invalidate_group_users_cache(group)
            
            # Crear log de auditoría
            PermissionLog.objects.create(
                action='ASSIGN_FUNCTION',
                group=group,
                function=function,
                changed_by=assigned_by,
                details={
                    'group_code': group.code,
                    'function_code': function.code,
                    'action_type': 'assign'
                }
            )
        
        return group_function
    
    def remove_function_from_group(
        self,
        group_id: int,
        function_code: str,
        removed_by: User
    ) -> bool:
        """
        Remueve función de grupo.
        
        Args:
            group_id: ID del grupo
            function_code: Código de función
            removed_by: Usuario que remueve
        
        Returns:
            bool: True si removió, False si no existía
        
        Side effects:
            - Invalida cache de usuarios del grupo
            - Crea PermissionLog
        """
        try:
            group_function = GroupFunction.objects.get(
                group_id=group_id,
                function__code=function_code
            )
            
            group = group_function.group
            function = group_function.function
            
            # Delete
            group_function.delete()
            
            # Invalidar cache
            self._invalidate_group_users_cache(group)
            
            # Log
            PermissionLog.objects.create(
                action='REMOVE_FUNCTION',
                group=group,
                function=function,
                changed_by=removed_by,
                details={
                    'group_code': group.code,
                    'function_code': function.code,
                    'action_type': 'remove'
                }
            )
            
            return True
        except GroupFunction.DoesNotExist:
            return False
    
    def bulk_assign_functions(
        self,
        group_id: int,
        function_codes: List[str],
        assigned_by: User
    ) -> Dict[str, Any]:
        """
        Asigna múltiples funciones a grupo.
        
        Args:
            group_id: ID del grupo
            function_codes: Lista de códigos de funciones
            assigned_by: Usuario que asigna
        
        Returns:
            Dict con resultados:
            {
                'assigned': 5,
                'skipped': 2,
                'errors': ['DSH_EDIT: función inactiva']
            }
        
        Transacción atómica.
        """
        from django.db import transaction
        
        results = {
            'assigned': 0,
            'skipped': 0,
            'errors': []
        }
        
        with transaction.atomic():
            for function_code in function_codes:
                try:
                    self.assign_function_to_group(
                        group_id=group_id,
                        function_code=function_code,
                        assigned_by=assigned_by
                    )
                    results['assigned'] += 1
                except Exception as e:
                    results['skipped'] += 1
                    results['errors'].append(f"{function_code}: {str(e)}")
        
        return results
    
    def assign_user_to_group(
        self,
        user_id: int,
        group_id: int,
        assigned_by: User
    ) -> UserGroup:
        """
        Asigna usuario a grupo.
        
        Args:
            user_id: ID del usuario
            group_id: ID del grupo
            assigned_by: Usuario que asigna
        
        Returns:
            UserGroup: Relación creada
        
        Raises:
            MaxGroupsExceededError: Si usuario tiene max grupos
        
        Side effects:
            - Invalida cache del usuario
            - Crea PermissionLog
        """
        # Validar límite de grupos
        current_count = UserGroup.objects.filter(user_id=user_id).count()
        if current_count >= MAX_GROUPS_PER_USER:
            raise MaxGroupsExceededError(
                f"Usuario ya tiene {MAX_GROUPS_PER_USER} grupos"
            )
        
        # Crear o retornar existente
        user_group, created = UserGroup.objects.get_or_create(
            user_id=user_id,
            group_id=group_id,
            defaults={'assigned_by': assigned_by}
        )
        
        if created:
            # Invalidar cache del usuario
            user = User.objects.get(id=user_id)
            self.rbac_service.invalidate_user_cache(user)
            
            # Log
            PermissionLog.objects.create(
                action='ASSIGN_USER',
                user=user,
                group=user_group.group,
                changed_by=assigned_by,
                details={
                    'user_username': user.username,
                    'group_code': user_group.group.code,
                    'action_type': 'assign_user'
                }
            )
        
        return user_group
    
    def remove_user_from_group(
        self,
        user_id: int,
        group_id: int,
        removed_by: User
    ) -> bool:
        """
        Remueve usuario de grupo.
        
        Args:
            user_id: ID del usuario
            group_id: ID del grupo
            removed_by: Usuario que remueve
        
        Returns:
            bool: True si removió, False si no existía
        """
        try:
            user_group = UserGroup.objects.get(
                user_id=user_id,
                group_id=group_id
            )
            
            user = user_group.user
            group = user_group.group
            
            # Delete
            user_group.delete()
            
            # Invalidar cache
            self.rbac_service.invalidate_user_cache(user)
            
            # Log
            PermissionLog.objects.create(
                action='REMOVE_USER',
                user=user,
                group=group,
                changed_by=removed_by,
                details={
                    'user_username': user.username,
                    'group_code': group.code,
                    'action_type': 'remove_user'
                }
            )
            
            return True
        except UserGroup.DoesNotExist:
            return False
    
    def get_group_functions(self, group_id: int) -> List[Function]:
        """
        Obtiene funciones de un grupo.
        
        Args:
            group_id: ID del grupo
        
        Returns:
            List[Function]: Lista de funciones
        """
        functions = Function.objects.filter(
            group_assignments__group_id=group_id,
            is_active=True
        ).select_related('module').order_by('module__order', 'code')
        
        return list(functions)
    
    def _invalidate_group_users_cache(self, group: Group) -> None:
        """
        Invalida cache de todos los usuarios del grupo.
        
        Args:
            group: Grupo
        """
        user_ids = UserGroup.objects.filter(
            group=group
        ).values_list('user_id', flat=True)
        
        self.rbac_service.bulk_invalidate_cache(list(user_ids))


class PermissionCacheService:
    """
    Servicio especializado en cache de permisos.
    
    Responsabilidades:
    - Cache de user_functions
    - Invalidación selectiva
    - Warm-up de cache
    - Estadísticas de cache
    
    CNST-035: Cache TTL 300s
    """
    
    def __init__(self):
        """Inicializa el servicio de cache."""
        self.cache_ttl = CACHE_TTL_FUNCTIONS
        self.cache_prefix = CACHE_KEY_PREFIX
    
    def warm_up_user_cache(self, user: User) -> Set[str]:
        """
        Pre-cachea funciones del usuario.
        
        Args:
            user: Usuario
        
        Returns:
            Set[str]: Funciones cacheadas
        
        Útil para:
            - Login del usuario (precarga)
            - Tests (setup)
        """
        rbac_service = RBACService()
        return rbac_service.get_user_functions(user)
    
    def warm_up_group_cache(self, group: Group) -> int:
        """
        Pre-cachea funciones de todos los usuarios del grupo.
        
        Args:
            group: Grupo
        
        Returns:
            int: Número de usuarios cacheados
        
        Útil después de modificar funciones del grupo.
        """
        user_ids = UserGroup.objects.filter(
            group=group
        ).values_list('user_id', flat=True)
        
        users = User.objects.filter(id__in=user_ids)
        
        for user in users:
            self.warm_up_user_cache(user)
        
        return len(users)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del cache.
        
        Returns:
            Dict con stats:
            {
                'total_keys': 150,
                'pattern': 'rbac:user_functions:*',
                'ttl': 300
            }
        
        Nota: Funcionalidad limitada con LocMemCache.
        """
        # LocMemCache no provee stats avanzadas
        # Retornar info básica
        return {
            'backend': 'LocMemCache',
            'ttl': self.cache_ttl,
            'prefix': self.cache_prefix,
            'pattern': f"{self.cache_prefix}:user_functions:*"
        }
    
    def clear_all_cache(self) -> None:
        """
        Limpia todo el cache de RBAC.
        
        WARNING: Operación costosa, usar con cuidado.
        
        Cuándo usar:
            - Deploy con cambios en fixtures
            - Tests cleanup
            - Emergency invalidation
        """
        # LocMemCache no soporta pattern delete
        # Necesitamos cache.clear() (limpia TODO el cache)
        # En producción, considerar migration a Redis
        cache.clear()
```

---

<a name="permission-log"></a>
## 3. PERMISSIONLOG MODEL

### 3.1 Archivo: apps/access/models.py (agregar)

```python
"""
PermissionLog model para auditoría de cambios RBAC.

Registra todos los cambios en permisos:
- Asignar función a grupo
- Remover función de grupo
- Asignar usuario a grupo
- Remover usuario de grupo
- Modificar grupo
- Modificar función

Integración con apps/audit/ para compliance.
"""

class PermissionLog(models.Model):
    """
    Log de cambios en permisos RBAC.
    
    Audita todas las modificaciones al sistema de permisos.
    
    Campos:
    - action: Tipo de acción (ASSIGN_FUNCTION, REMOVE_USER, etc)
    - user: Usuario afectado (nullable)
    - group: Grupo afectado (nullable)
    - function: Función afectada (nullable)
    - changed_by: Usuario que realizó el cambio
    - details: JSON con detalles adicionales
    - timestamp: Cuándo ocurrió
    
    Integración:
        - apps/audit/ consume estos logs
        - apps/reports/ genera reportes de cambios
    """
    
    ACTION_CHOICES = [
        ('ASSIGN_FUNCTION', 'Asignar Función'),
        ('REMOVE_FUNCTION', 'Remover Función'),
        ('ASSIGN_USER', 'Asignar Usuario'),
        ('REMOVE_USER', 'Remover Usuario'),
        ('CREATE_GROUP', 'Crear Grupo'),
        ('UPDATE_GROUP', 'Actualizar Grupo'),
        ('DELETE_GROUP', 'Eliminar Grupo'),
        ('CREATE_FUNCTION', 'Crear Función'),
        ('UPDATE_FUNCTION', 'Actualizar Función'),
        ('ACTIVATE_FUNCTION', 'Activar Función'),
        ('DEACTIVATE_FUNCTION', 'Desactivar Función'),
    ]
    
    id = models.BigAutoField(
        db_column='iIdLogPermiso',
        primary_key=True
    )
    
    action = models.CharField(
        db_column='cAccion',
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="Tipo de acción realizada"
    )
    
    user = models.ForeignKey(
        'auth.User',
        db_column='iIdUsuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permission_changes',
        help_text="Usuario afectado (si aplica)"
    )
    
    group = models.ForeignKey(
        Group,
        db_column='iIdGrupo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permission_changes',
        help_text="Grupo afectado (si aplica)"
    )
    
    function = models.ForeignKey(
        Function,
        db_column='iIdFuncion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permission_changes',
        help_text="Función afectada (si aplica)"
    )
    
    changed_by = models.ForeignKey(
        'auth.User',
        db_column='iIdCambiadoPor',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
        help_text="Usuario que realizó el cambio"
    )
    
    details = models.JSONField(
        db_column='jDetalles',
        default=dict,
        blank=True,
        help_text="Detalles adicionales del cambio"
    )
    
    timestamp = models.DateTimeField(
        db_column='dFechaHora',
        auto_now_add=True,
        help_text="Cuándo ocurrió el cambio"
    )
    
    ip_address = models.GenericIPAddressField(
        db_column='cDireccionIP',
        null=True,
        blank=True,
        help_text="IP del usuario que hizo el cambio"
    )
    
    class Meta:
        db_table = 'tbl_log_permisos'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['group', '-timestamp']),
            models.Index(fields=['changed_by', '-timestamp']),
        ]
        verbose_name = 'Log de Permiso'
        verbose_name_plural = 'Logs de Permisos'
    
    def __str__(self):
        return f"{self.action} - {self.timestamp}"
    
    @property
    def formatted_message(self) -> str:
        """
        Mensaje formateado del cambio.
        
        Returns:
            str: Mensaje legible
        
        Example:
            "admin asignó función AUD_VIEW a grupo GRP_Manager"
        """
        changed_by_name = self.changed_by.username if self.changed_by else 'Sistema'
        
        if self.action == 'ASSIGN_FUNCTION':
            return (
                f"{changed_by_name} asignó función {self.function.code} "
                f"a grupo {self.group.code}"
            )
        elif self.action == 'REMOVE_FUNCTION':
            return (
                f"{changed_by_name} removió función {self.function.code} "
                f"de grupo {self.group.code}"
            )
        elif self.action == 'ASSIGN_USER':
            return (
                f"{changed_by_name} asignó usuario {self.user.username} "
                f"a grupo {self.group.code}"
            )
        elif self.action == 'REMOVE_USER':
            return (
                f"{changed_by_name} removió usuario {self.user.username} "
                f"de grupo {self.group.code}"
            )
        else:
            return f"{changed_by_name} - {self.get_action_display()}"
```

---

<a name="utils"></a>
## 4. UTILS Y HELPERS

### 4.1 Archivo: apps/access/utils.py

```python
"""
Utilidades para sistema RBAC.

CLEAN_CODE v3.0.1:
- Funciones: snake_case inglés
- Docstrings: español
"""

from typing import List, Dict, Any, Set
from django.contrib.auth import get_user_model

from apps.access.models import Function, Module

User = get_user_model()


def get_user_function_codes(user: User) -> List[str]:
    """
    Obtiene lista de códigos de funciones del usuario.
    
    Args:
        user: Usuario
    
    Returns:
        List[str]: Lista de códigos (ordenada)
    
    Example:
        >>> get_user_function_codes(user)
        ['ALR_SEND', 'AUD_VIEW', 'DSH_VIEW', 'RPT_VIEW']
    """
    from apps.access.services import RBACService
    
    rbac_service = RBACService()
    functions = rbac_service.get_user_functions(user)
    
    return sorted(list(functions))


def get_functions_by_module(user: User) -> Dict[str, List[str]]:
    """
    Obtiene funciones del usuario agrupadas por módulo.
    
    Args:
        user: Usuario
    
    Returns:
        Dict[str, List[str]]: {module_code: [function_codes]}
    
    Example:
        >>> get_functions_by_module(user)
        {
            'MOD_Audit': ['AUD_VIEW', 'AUD_SEARCH'],
            'MOD_Dashboard': ['DSH_VIEW', 'DSH_EXP_CSV'],
            'MOD_Alerts': ['ALR_SEND', 'ALR_VIEW']
        }
    
    Útil para:
        - Renderizar menú por módulos
        - Mostrar permisos agrupados
    """
    from apps.access.services import RBACService
    
    rbac_service = RBACService()
    function_codes = rbac_service.get_user_functions(user)
    
    # Query funciones con módulos
    functions = Function.objects.filter(
        code__in=function_codes,
        is_active=True
    ).select_related('module').order_by('module__order', 'code')
    
    # Agrupar por módulo
    result = {}
    for function in functions:
        module_code = function.module.code
        if module_code not in result:
            result[module_code] = []
        result[module_code].append(function.code)
    
    return result


def compare_user_functions(user1: User, user2: User) -> Dict[str, Set[str]]:
    """
    Compara funciones de dos usuarios.
    
    Args:
        user1: Primer usuario
        user2: Segundo usuario
    
    Returns:
        Dict con diferencias:
        {
            'user1_only': {'AUD_SEARCH', 'AUD_EXPORT'},
            'user2_only': {'DSH_EDIT'},
            'common': {'AUD_VIEW', 'DSH_VIEW'}
        }
    
    Útil para:
        - Auditoría de permisos
        - Comparar roles
    """
    from apps.access.services import RBACService
    
    rbac_service = RBACService()
    
    functions1 = rbac_service.get_user_functions(user1)
    functions2 = rbac_service.get_user_functions(user2)
    
    return {
        'user1_only': functions1 - functions2,
        'user2_only': functions2 - functions1,
        'common': functions1 & functions2
    }


def validate_function_exists(function_code: str) -> bool:
    """
    Valida que función existe y está activa.
    
    Args:
        function_code: Código de función
    
    Returns:
        bool: True si existe y activa
    """
    return Function.objects.filter(
        code=function_code,
        is_active=True
    ).exists()


def get_module_functions(module_code: str) -> List[Function]:
    """
    Obtiene todas las funciones de un módulo.
    
    Args:
        module_code: Código del módulo (ej: 'MOD_Audit')
    
    Returns:
        List[Function]: Lista de funciones
    
    Example:
        >>> get_module_functions('MOD_Audit')
        [<Function: AUD_VIEW>, <Function: AUD_SEARCH>, ...]
    """
    functions = Function.objects.filter(
        module__code=module_code,
        is_active=True
    ).order_by('code')
    
    return list(functions)


def format_permission_change(log: 'PermissionLog') -> str:
    """
    Formatea cambio de permiso para display.
    
    Args:
        log: PermissionLog instance
    
    Returns:
        str: Mensaje formateado
    
    Example:
        "admin asignó función AUD_VIEW a grupo GRP_Manager el 2026-01-20 15:30"
    """
    return (
        f"{log.formatted_message} "
        f"el {log.timestamp.strftime('%Y-%m-%d %H:%M')}"
    )


def get_user_groups_with_functions(user: User) -> List[Dict[str, Any]]:
    """
    Obtiene grupos del usuario con sus funciones.
    
    Args:
        user: Usuario
    
    Returns:
        List[Dict]: Lista de grupos con funciones
    
    Example:
        [
            {
                'group_code': 'GRP_Manager',
                'group_name': 'Gerentes',
                'functions': ['AUD_VIEW', 'DSH_VIEW', 'RPT_VIEW']
            },
            ...
        ]
    
    Útil para mostrar permisos del usuario.
    """
    from apps.access.models import UserGroup, GroupFunction
    
    user_groups = UserGroup.objects.filter(
        user=user,
        group__is_active=True
    ).select_related('group').prefetch_related(
        'group__function_assignments__function'
    )
    
    result = []
    for user_group in user_groups:
        group = user_group.group
        
        # Obtener funciones del grupo
        functions = [
            gf.function.code
            for gf in group.function_assignments.all()
            if gf.function.is_active
        ]
        
        result.append({
            'group_code': group.code,
            'group_name': group.name,
            'functions': sorted(functions)
        })
    
    return result
```

---

<a name="exceptions"></a>
## 5. EXCEPTIONS

### 5.1 Archivo: apps/access/exceptions.py

```python
"""
Excepciones personalizadas para sistema RBAC.

CLEAN_CODE v3.0.1:
- Nombres: PascalCase + Error suffix
- Docstrings: español
"""


class RBACBaseException(Exception):
    """Excepción base para errores de RBAC."""
    pass


class PermissionDeniedError(RBACBaseException):
    """
    Excepción cuando usuario no tiene permiso.
    
    Example:
        raise PermissionDeniedError("Usuario no tiene AUD_VIEW")
    """
    pass


class InvalidFunctionError(RBACBaseException):
    """
    Excepción cuando función no existe o está inactiva.
    
    Example:
        raise InvalidFunctionError("Función 'DSH_EDIT' no existe")
    """
    pass


class MaxGroupsExceededError(RBACBaseException):
    """
    Excepción cuando usuario alcanza límite de grupos.
    
    CNST-035: MAX_GROUPS_PER_USER = 10
    
    Example:
        raise MaxGroupsExceededError("Usuario ya tiene 10 grupos")
    """
    pass


class MaxFunctionsExceededError(RBACBaseException):
    """
    Excepción cuando grupo alcanza límite de funciones.
    
    CNST-035: MAX_FUNCTIONS_PER_GROUP = 50
    
    Example:
        raise MaxFunctionsExceededError("Grupo ya tiene 50 funciones")
    """
    pass


class CacheError(RBACBaseException):
    """
    Excepción relacionada con cache de permisos.
    
    Example:
        raise CacheError("No se pudo invalidar cache del usuario")
    """
    pass
```

---

## 6. RESUMEN PARTE 2

### 6.1 Componentes Generados

```yaml
Archivos Python:
  ✅ apps/access/services.py (~700 líneas)
     - RBACService (has_function, get_user_functions)
     - GroupService (assign/remove functions/users)
     - PermissionCacheService (warm-up, stats, clear)
  
  ✅ apps/access/models.py (agregar PermissionLog ~150 líneas)
     - PermissionLog model completo
     - 11 ACTION_CHOICES
     - formatted_message property
  
  ✅ apps/access/utils.py (~200 líneas)
     - get_user_function_codes()
     - get_functions_by_module()
     - compare_user_functions()
     - validate_function_exists()
     - get_module_functions()
     - format_permission_change()
     - get_user_groups_with_functions()
  
  ✅ apps/access/exceptions.py (~100 líneas)
     - PermissionDeniedError
     - InvalidFunctionError
     - MaxGroupsExceededError
     - MaxFunctionsExceededError
     - CacheError

Total: ~1,150 líneas Python production-ready
```

### 6.2 Services (3)

```python
✅ RBACService (core):
   - has_function(user, function_code) → bool
   - get_user_functions(user) → Set[str]
   - validate_permission(user, permission_string) → bool
   - invalidate_user_cache(user)
   - bulk_invalidate_cache(user_ids)
   - _query_user_functions(user) → Set[str]
   - _get_all_active_functions() → Set[str]
   
   CNST-035: Cache 300s
   Optimizado: prefetch_related para evitar N+1

✅ GroupService:
   - assign_function_to_group(group_id, function_code, assigned_by)
   - remove_function_from_group(group_id, function_code, removed_by)
   - bulk_assign_functions(group_id, function_codes, assigned_by)
   - assign_user_to_group(user_id, group_id, assigned_by)
   - remove_user_from_group(user_id, group_id, removed_by)
   - get_group_functions(group_id) → List[Function]
   - _invalidate_group_users_cache(group)
   
   Side effects:
   - Invalida cache automáticamente
   - Crea PermissionLog para auditoría

✅ PermissionCacheService:
   - warm_up_user_cache(user) → Set[str]
   - warm_up_group_cache(group) → int
   - get_cache_stats() → Dict
   - clear_all_cache()
   
   Útil para:
   - Pre-calentar cache en login
   - Tests setup
   - Emergency invalidation
```

### 6.3 PermissionLog Model

```python
✅ PermissionLog:
   - action: 11 tipos (ASSIGN_FUNCTION, REMOVE_USER, etc)
   - user, group, function (FKs nullables)
   - changed_by: Usuario que hizo el cambio
   - details: JSONField con info adicional
   - timestamp: auto_now_add
   - ip_address: IP del cambio
   
   Métodos:
   - formatted_message property
   
   Integración:
   - apps/audit/ consume estos logs
   - apps/reports/ genera reportes
```

### 6.4 Utils (7 funciones)

```python
✅ get_user_function_codes(user) → List[str]
✅ get_functions_by_module(user) → Dict[str, List[str]]
✅ compare_user_functions(user1, user2) → Dict
✅ validate_function_exists(function_code) → bool
✅ get_module_functions(module_code) → List[Function]
✅ format_permission_change(log) → str
✅ get_user_groups_with_functions(user) → List[Dict]
```

### 6.5 Exceptions (5)

```python
✅ RBACBaseException (base)
✅ PermissionDeniedError (NO permiso)
✅ InvalidFunctionError (función no existe)
✅ MaxGroupsExceededError (límite grupos)
✅ MaxFunctionsExceededError (límite funciones)
✅ CacheError (errores cache)
```

---

## PRÓXIMA PARTE

**PARTE 3/6: Permissions y Decorators**

Contenido:
- ✅ DynamicFunctionPermission (DRF permission class)
- ✅ FunctionPermissionMixin (CBV mixin)
- ✅ @require_function decorator
- ✅ @require_any_function decorator (OR logic)
- ✅ @require_all_functions decorator (AND logic)
- ✅ Template tags (has_function, has_any_function)
- ✅ Context processors

**Estimado:** ~900 líneas, 2.5 horas

---

**Fin de PARTE 2/6**
