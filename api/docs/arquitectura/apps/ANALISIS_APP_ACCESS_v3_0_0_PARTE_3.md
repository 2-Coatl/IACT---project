---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Access PARTE 3/6
categoria: arquitectura/apps
tema: apps/access/ - Permissions y Decorators
autor: Claude Technical Analysis
tags: [access, rbac, permissions, decorators, drf, templates, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
estado: definitivo
parte: 3 de 6
relacionado:
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_1.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_2.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_4.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_5.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_6.md
replaces: []
---

# ANÁLISIS DE apps/access/ v3.0.0 - PARTE 3/6
## PERMISSIONS Y DECORATORS

---

## TABLA DE CONTENIDOS

1. [Resumen Parte 3](#resumen)
2. [DRF Permission Classes](#drf-permissions)
3. [Decorators](#decorators)
4. [Mixins](#mixins)
5. [Template Tags](#template-tags)
6. [Context Processors](#context-processors)

---

<a name="resumen"></a>
## 1. RESUMEN PARTE 3

### 1.1 Alcance de esta Parte

```yaml
Componentes cubiertos:
  ✅ DRF Permission Classes (DynamicFunctionPermission)
  ✅ Decorators para views (3 decorators)
  ✅ Mixins para CBV (FunctionPermissionMixin)
  ✅ Template tags (3 tags)
  ✅ Context processors (1 processor)

Líneas de código: ~900 líneas Python
Archivos generados:
  - apps/access/permissions.py (~300 líneas)
  - apps/access/decorators.py (~250 líneas)
  - apps/access/mixins.py (~150 líneas)
  - apps/access/templatetags/access_tags.py (~150 líneas)
  - apps/access/context_processors.py (~50 líneas)

Uso:
  Esta parte es USADA por TODAS las apps del sistema.
  DynamicFunctionPermission → TODOS los ViewSets
  @require_function → TODAS las vistas
  has_function tag → TODOS los templates
```

---

<a name="drf-permissions"></a>
## 2. DRF PERMISSION CLASSES

### 2.1 Archivo: apps/access/permissions.py

```python
"""
Permission classes para Django REST Framework.

DynamicFunctionPermission es LA permission class principal
usada en TODOS los ViewSets del sistema.

CLEAN_CODE v3.0.1:
- Clases: DynamicFunctionPermission (PascalCase)
- Métodos: has_permission (snake_case)
- Docstrings: español formato Google

CNST-034: Function-based permissions
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from typing import Optional

from apps.access.services import RBACService
from apps.access.exceptions import PermissionDeniedError


class DynamicFunctionPermission(BasePermission):
    """
    Permission class principal para ViewSets.
    
    Valida permisos usando function_map definido en el ViewSet.
    
    CNST-034: Function-based RBAC
    
    Usage en ViewSet:
        class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
            permission_classes = [IsAuthenticated, DynamicFunctionPermission]
            
            function_map = {
                'list': 'audit.view',         # AUD_VIEW
                'retrieve': 'audit.view',     # AUD_VIEW
                'search': 'audit.search',     # AUD_SEARCH
                'export_csv': 'audit.export', # AUD_EXPORT
            }
    
    Flujo:
        1. Request llega al ViewSet
        2. DRF ejecuta has_permission()
        3. Busca action en function_map
        4. Obtiene permission_string
        5. Valida con RBACService.validate_permission()
        6. Allow/Deny
    
    Ventajas:
        - Centralizado en access app
        - Usa function_map del ViewSet
        - Cache-aware (300s)
        - Messages personalizados
    """
    
    def __init__(self):
        """Inicializa la permission class."""
        super().__init__()
        self.rbac_service = RBACService()
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Valida si usuario tiene permiso para la acción.
        
        Args:
            request: Request de DRF
            view: ViewSet instance
        
        Returns:
            bool: True si tiene permiso, False si no
        
        Attributes usados:
            view.action: Acción actual (list, retrieve, create, etc)
            view.function_map: Dict {action: permission_string}
        
        Example:
            # En ViewSet
            function_map = {
                'list': 'audit.view',
                'search': 'audit.search'
            }
            
            # Request: GET /api/v1/audit/logs/
            # view.action = 'list'
            # permission_string = 'audit.view'
            # Valida: rbac_service.validate_permission(user, 'audit.view')
        """
        # Usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            self.message = "Usuario no autenticado."
            return False
        
        # Obtener function_map del ViewSet
        function_map = getattr(view, 'function_map', None)
        
        if not function_map:
            # ViewSet sin function_map → deny por seguridad
            self.message = (
                "ViewSet no tiene function_map definido. "
                "Contacte al administrador."
            )
            return False
        
        # Obtener action actual
        action = getattr(view, 'action', None)
        
        if not action:
            # No se pudo determinar action → deny
            self.message = "No se pudo determinar la acción solicitada."
            return False
        
        # Buscar permission_string en function_map
        permission_string = function_map.get(action)
        
        if not permission_string:
            # Action no mapeada → deny
            self.message = (
                f"Acción '{action}' no tiene permiso definido. "
                f"Contacte al administrador."
            )
            return False
        
        # Validar permiso con RBACService
        has_perm = self.rbac_service.validate_permission(
            request.user,
            permission_string
        )
        
        if not has_perm:
            # No tiene permiso → deny con mensaje claro
            self.message = (
                f"No tiene permiso para realizar esta acción. "
                f"Se requiere: {permission_string}"
            )
            return False
        
        # Tiene permiso → allow
        return True
    
    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj
    ) -> bool:
        """
        Valida permiso a nivel de objeto.
        
        Por defecto, usa el mismo permiso que has_permission.
        
        Sobrescribir en ViewSet si necesitas lógica adicional:
            def check_object_permissions(self, request, obj):
                super().check_object_permissions(request, obj)
                # Lógica adicional (ej: solo propios registros)
                if obj.user != request.user:
                    raise PermissionDenied("Solo puede ver sus propios registros")
        """
        # Por defecto, si tiene permiso general, tiene permiso a objeto
        return self.has_permission(request, view)


class IsAdminOrReadOnly(BasePermission):
    """
    Permission class auxiliar: Admin puede todo, otros solo lectura.
    
    Útil para endpoints de configuración.
    
    Usage:
        class FunctionViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Admin tiene todos los permisos.
        Otros usuarios solo GET/HEAD/OPTIONS.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin puede todo
        if request.user.is_superuser:
            return True
        
        # Otros solo lectura
        return request.method in ['GET', 'HEAD', 'OPTIONS']


class HasAnyFunction(BasePermission):
    """
    Permission class: Requiere AL MENOS UNA de las funciones.
    
    OR logic.
    
    Usage:
        class MyViewSet(viewsets.ViewSet):
            permission_classes = [IsAuthenticated, HasAnyFunction]
            required_functions = ['AUD_VIEW', 'DSH_VIEW', 'RPT_VIEW']
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Valida que usuario tenga AL MENOS UNA función.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        required_functions = getattr(view, 'required_functions', [])
        
        if not required_functions:
            # No hay funciones requeridas → deny
            return False
        
        rbac_service = RBACService()
        
        # Verificar si tiene alguna
        for function_code in required_functions:
            if rbac_service.has_function(request.user, function_code):
                return True  # Tiene al menos una
        
        # No tiene ninguna
        self.message = (
            f"Se requiere al menos una de: {', '.join(required_functions)}"
        )
        return False


class HasAllFunctions(BasePermission):
    """
    Permission class: Requiere TODAS las funciones.
    
    AND logic.
    
    Usage:
        class SensitiveViewSet(viewsets.ViewSet):
            permission_classes = [IsAuthenticated, HasAllFunctions]
            required_functions = ['AUD_VIEW', 'AUD_EXPORT', 'SYS_ADMIN']
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Valida que usuario tenga TODAS las funciones.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        required_functions = getattr(view, 'required_functions', [])
        
        if not required_functions:
            return False
        
        rbac_service = RBACService()
        
        # Verificar todas
        missing = []
        for function_code in required_functions:
            if not rbac_service.has_function(request.user, function_code):
                missing.append(function_code)
        
        if missing:
            self.message = (
                f"Funciones faltantes: {', '.join(missing)}"
            )
            return False
        
        return True
```

---

<a name="decorators"></a>
## 3. DECORATORS

### 3.1 Archivo: apps/access/decorators.py

```python
"""
Decorators para validación de permisos en views.

CLEAN_CODE v3.0.1:
- Funciones: snake_case inglés
- Docstrings: español formato Google

CNST-034: Function-based permissions
"""

from functools import wraps
from typing import Callable, List
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages

from apps.access.services import RBACService
from apps.access.exceptions import PermissionDeniedError


def require_function(function_code: str):
    """
    Decorator: Requiere función específica.
    
    Args:
        function_code: Código de función (ej: 'AUD_VIEW')
    
    Returns:
        Decorator function
    
    Usage:
        @require_function('AUD_VIEW')
        def audit_log_view(request):
            logs = AuditLog.objects.all()
            return render(request, 'audit/logs.html', {'logs': logs})
    
    Comportamiento:
        - Si usuario no autenticado → redirect login
        - Si usuario sin permiso → 403 Forbidden
        - Si usuario con permiso → ejecuta view
    
    CNST-034: Function-based RBAC
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Usuario debe estar autenticado
            if not request.user or not request.user.is_authenticated:
                messages.error(request, "Debe iniciar sesión para acceder.")
                return redirect('login')
            
            # Validar permiso
            rbac_service = RBACService()
            
            if not rbac_service.has_function(request.user, function_code):
                messages.error(
                    request,
                    f"No tiene permiso para realizar esta acción. "
                    f"Se requiere: {function_code}"
                )
                return HttpResponseForbidden(
                    f"<h1>403 Forbidden</h1>"
                    f"<p>No tiene permiso: {function_code}</p>"
                )
            
            # Tiene permiso → ejecutar view
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_any_function(function_codes: List[str]):
    """
    Decorator: Requiere AL MENOS UNA de las funciones (OR).
    
    Args:
        function_codes: Lista de códigos de funciones
    
    Returns:
        Decorator function
    
    Usage:
        @require_any_function(['AUD_VIEW', 'DSH_VIEW', 'RPT_VIEW'])
        def dashboard_view(request):
            # Usuario tiene al menos uno de los permisos
            return render(request, 'dashboard.html')
    
    Útil para:
        - Vistas que pueden accederse con múltiples roles
        - Funcionalidad compartida entre módulos
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                messages.error(request, "Debe iniciar sesión para acceder.")
                return redirect('login')
            
            rbac_service = RBACService()
            
            # Verificar si tiene alguna
            has_any = False
            for function_code in function_codes:
                if rbac_service.has_function(request.user, function_code):
                    has_any = True
                    break
            
            if not has_any:
                messages.error(
                    request,
                    f"Se requiere al menos uno de: {', '.join(function_codes)}"
                )
                return HttpResponseForbidden(
                    f"<h1>403 Forbidden</h1>"
                    f"<p>Se requiere al menos una función de: "
                    f"{', '.join(function_codes)}</p>"
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_all_functions(function_codes: List[str]):
    """
    Decorator: Requiere TODAS las funciones (AND).
    
    Args:
        function_codes: Lista de códigos de funciones
    
    Returns:
        Decorator function
    
    Usage:
        @require_all_functions(['AUD_VIEW', 'AUD_EXPORT', 'SYS_ADMIN'])
        def sensitive_export_view(request):
            # Usuario tiene TODAS las funciones
            return render(request, 'export.html')
    
    Útil para:
        - Vistas ultra sensibles
        - Requieren múltiples permisos simultáneos
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                messages.error(request, "Debe iniciar sesión para acceder.")
                return redirect('login')
            
            rbac_service = RBACService()
            
            # Verificar todas
            missing = []
            for function_code in function_codes:
                if not rbac_service.has_function(request.user, function_code):
                    missing.append(function_code)
            
            if missing:
                messages.error(
                    request,
                    f"Funciones faltantes: {', '.join(missing)}"
                )
                return HttpResponseForbidden(
                    f"<h1>403 Forbidden</h1>"
                    f"<p>Funciones faltantes: {', '.join(missing)}</p>"
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_function_or_superuser(function_code: str):
    """
    Decorator: Requiere función O ser superuser.
    
    Útil para vistas de administración.
    
    Args:
        function_code: Código de función
    
    Usage:
        @require_function_or_superuser('USR_PERMS')
        def manage_permissions_view(request):
            # Superuser o usuario con USR_PERMS
            return render(request, 'permissions.html')
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                messages.error(request, "Debe iniciar sesión para acceder.")
                return redirect('login')
            
            # Superuser siempre puede
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Validar función
            rbac_service = RBACService()
            
            if not rbac_service.has_function(request.user, function_code):
                messages.error(
                    request,
                    f"Se requiere: {function_code} o ser superusuario"
                )
                return HttpResponseForbidden(
                    f"<h1>403 Forbidden</h1>"
                    f"<p>Se requiere: {function_code} o superuser</p>"
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def ajax_require_function(function_code: str):
    """
    Decorator: Requiere función para vistas AJAX.
    
    Returns JSON en lugar de HTML.
    
    Args:
        function_code: Código de función
    
    Usage:
        @ajax_require_function('AUD_SEARCH')
        def ajax_search_logs(request):
            # Vista AJAX
            results = search_logs(request.GET.get('q'))
            return JsonResponse({'results': results})
    """
    from django.http import JsonResponse
    
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Usuario no autenticado'},
                    status=401
                )
            
            rbac_service = RBACService()
            
            if not rbac_service.has_function(request.user, function_code):
                return JsonResponse(
                    {
                        'error': 'Sin permiso',
                        'required': function_code
                    },
                    status=403
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
```

---

<a name="mixins"></a>
## 4. MIXINS

### 4.1 Archivo: apps/access/mixins.py

```python
"""
Mixins para class-based views.

CLEAN_CODE v3.0.1:
- Clases: FunctionPermissionMixin (PascalCase)
- Métodos: dispatch (snake_case)
- Docstrings: español formato Google

CNST-034: Function-based permissions
"""

from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from typing import Optional

from apps.access.services import RBACService


class FunctionPermissionMixin(AccessMixin):
    """
    Mixin para class-based views que requieren función.
    
    Usage:
        class AuditLogListView(FunctionPermissionMixin, ListView):
            model = AuditLog
            required_function = 'AUD_VIEW'
            template_name = 'audit/logs.html'
    
    Attributes:
        required_function: Código de función requerida
        permission_denied_message: Mensaje personalizado
    
    CNST-034: Function-based RBAC
    """
    
    required_function: Optional[str] = None
    permission_denied_message: str = "No tiene permiso para acceder a esta página."
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch para validar permiso.
        
        Flujo:
            1. Verificar usuario autenticado
            2. Validar required_function definida
            3. Validar permiso con RBACService
            4. Allow/Deny
        """
        # Usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            messages.error(request, "Debe iniciar sesión para acceder.")
            return redirect('login')
        
        # required_function debe estar definida
        if not self.required_function:
            raise ValueError(
                f"{self.__class__.__name__} debe definir 'required_function'"
            )
        
        # Validar permiso
        rbac_service = RBACService()
        
        if not rbac_service.has_function(request.user, self.required_function):
            messages.error(request, self.permission_denied_message)
            return HttpResponseForbidden(
                f"<h1>403 Forbidden</h1>"
                f"<p>{self.permission_denied_message}</p>"
                f"<p>Se requiere: {self.required_function}</p>"
            )
        
        # Tiene permiso → continuar dispatch normal
        return super().dispatch(request, *args, **kwargs)


class MultipleRequiredFunctionsMixin(AccessMixin):
    """
    Mixin: Requiere múltiples funciones (AND logic).
    
    Usage:
        class SensitiveDataView(MultipleRequiredFunctionsMixin, DetailView):
            model = SensitiveData
            required_functions = ['AUD_VIEW', 'AUD_EXPORT', 'SYS_ADMIN']
            template_name = 'sensitive.html'
    """
    
    required_functions: Optional[list] = None
    permission_denied_message: str = "No tiene todos los permisos requeridos."
    
    def dispatch(self, request, *args, **kwargs):
        """Valida que usuario tenga TODAS las funciones."""
        if not request.user or not request.user.is_authenticated:
            messages.error(request, "Debe iniciar sesión para acceder.")
            return redirect('login')
        
        if not self.required_functions:
            raise ValueError(
                f"{self.__class__.__name__} debe definir 'required_functions'"
            )
        
        rbac_service = RBACService()
        
        # Verificar todas
        missing = []
        for function_code in self.required_functions:
            if not rbac_service.has_function(request.user, function_code):
                missing.append(function_code)
        
        if missing:
            messages.error(
                request,
                f"Funciones faltantes: {', '.join(missing)}"
            )
            return HttpResponseForbidden(
                f"<h1>403 Forbidden</h1>"
                f"<p>Funciones faltantes: {', '.join(missing)}</p>"
            )
        
        return super().dispatch(request, *args, **kwargs)


class AnyRequiredFunctionMixin(AccessMixin):
    """
    Mixin: Requiere AL MENOS UNA función (OR logic).
    
    Usage:
        class DashboardView(AnyRequiredFunctionMixin, TemplateView):
            required_functions = ['AUD_VIEW', 'DSH_VIEW', 'RPT_VIEW']
            template_name = 'dashboard.html'
    """
    
    required_functions: Optional[list] = None
    permission_denied_message: str = "No tiene ninguno de los permisos requeridos."
    
    def dispatch(self, request, *args, **kwargs):
        """Valida que usuario tenga AL MENOS UNA función."""
        if not request.user or not request.user.is_authenticated:
            messages.error(request, "Debe iniciar sesión para acceder.")
            return redirect('login')
        
        if not self.required_functions:
            raise ValueError(
                f"{self.__class__.__name__} debe definir 'required_functions'"
            )
        
        rbac_service = RBACService()
        
        # Verificar si tiene alguna
        has_any = False
        for function_code in self.required_functions:
            if rbac_service.has_function(request.user, function_code):
                has_any = True
                break
        
        if not has_any:
            messages.error(
                request,
                f"Se requiere al menos una de: {', '.join(self.required_functions)}"
            )
            return HttpResponseForbidden(
                f"<h1>403 Forbidden</h1>"
                f"<p>Se requiere al menos una función de: "
                f"{', '.join(self.required_functions)}</p>"
            )
        
        return super().dispatch(request, *args, **kwargs)
```

---

<a name="template-tags"></a>
## 5. TEMPLATE TAGS

### 5.1 Archivo: apps/access/templatetags/access_tags.py

```python
"""
Template tags para validación de permisos en templates.

CLEAN_CODE v3.0.1:
- Funciones: snake_case inglés
- Docstrings: español

CNST-034: Function-based permissions
"""

from django import template
from django.contrib.auth import get_user_model

from apps.access.services import RBACService
from apps.access.utils import get_functions_by_module

User = get_user_model()
register = template.Library()


@register.filter(name='has_function')
def has_function(user: User, function_code: str) -> bool:
    """
    Template filter: Verifica si usuario tiene función.
    
    Args:
        user: Usuario
        function_code: Código de función
    
    Returns:
        bool: True si tiene permiso
    
    Usage en template:
        {% load access_tags %}
        
        {% if user|has_function:'AUD_VIEW' %}
            <a href="{% url 'audit:logs' %}">Ver Auditoría</a>
        {% endif %}
        
        {% if user|has_function:'DSH_EXP_CSV' %}
            <button>Exportar CSV</button>
        {% endif %}
    
    CNST-034: Function-based RBAC
    """
    if not user or not user.is_authenticated:
        return False
    
    rbac_service = RBACService()
    return rbac_service.has_function(user, function_code)


@register.filter(name='has_any_function')
def has_any_function(user: User, function_codes: str) -> bool:
    """
    Template filter: Verifica si usuario tiene AL MENOS UNA función.
    
    Args:
        user: Usuario
        function_codes: Códigos separados por coma
    
    Returns:
        bool: True si tiene al menos una
    
    Usage:
        {% if user|has_any_function:'AUD_VIEW,DSH_VIEW,RPT_VIEW' %}
            <a href="{% url 'dashboard' %}">Dashboard</a>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    codes = [code.strip() for code in function_codes.split(',')]
    
    rbac_service = RBACService()
    
    for code in codes:
        if rbac_service.has_function(user, code):
            return True
    
    return False


@register.filter(name='has_all_functions')
def has_all_functions(user: User, function_codes: str) -> bool:
    """
    Template filter: Verifica si usuario tiene TODAS las funciones.
    
    Args:
        user: Usuario
        function_codes: Códigos separados por coma
    
    Returns:
        bool: True si tiene todas
    
    Usage:
        {% if user|has_all_functions:'AUD_VIEW,AUD_EXPORT,SYS_ADMIN' %}
            <a href="{% url 'sensitive-export' %}">Exportar Sensible</a>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    codes = [code.strip() for code in function_codes.split(',')]
    
    rbac_service = RBACService()
    
    for code in codes:
        if not rbac_service.has_function(user, code):
            return False
    
    return True


@register.simple_tag(takes_context=True)
def user_functions_by_module(context):
    """
    Template tag: Obtiene funciones del usuario agrupadas por módulo.
    
    Returns:
        Dict: {module_code: [function_codes]}
    
    Usage:
        {% load access_tags %}
        
        {% user_functions_by_module as functions %}
        
        {% for module_code, function_list in functions.items %}
            <h3>{{ module_code }}</h3>
            <ul>
            {% for function in function_list %}
                <li>{{ function }}</li>
            {% endfor %}
            </ul>
        {% endfor %}
    
    Útil para:
        - Renderizar menú por módulos
        - Mostrar permisos del usuario
    """
    user = context['request'].user
    
    if not user or not user.is_authenticated:
        return {}
    
    return get_functions_by_module(user)


@register.inclusion_tag('access/permission_badge.html')
def permission_badge(user: User, function_code: str):
    """
    Inclusion tag: Renderiza badge de permiso.
    
    Args:
        user: Usuario
        function_code: Código de función
    
    Usage:
        {% load access_tags %}
        
        {% permission_badge user 'AUD_VIEW' %}
    
    Renderiza template 'access/permission_badge.html':
        {% if has_permission %}
            <span class="badge badge-success">✓ {{ function_code }}</span>
        {% else %}
            <span class="badge badge-danger">✗ {{ function_code }}</span>
        {% endif %}
    """
    rbac_service = RBACService()
    has_permission = rbac_service.has_function(user, function_code)
    
    return {
        'user': user,
        'function_code': function_code,
        'has_permission': has_permission
    }
```

### 5.2 Template: apps/access/templates/access/permission_badge.html

```html
<!-- Template para inclusion tag permission_badge -->

{% if has_permission %}
    <span class="badge badge-success" title="Usuario tiene permiso {{ function_code }}">
        ✓ {{ function_code }}
    </span>
{% else %}
    <span class="badge badge-danger" title="Usuario NO tiene permiso {{ function_code }}">
        ✗ {{ function_code }}
    </span>
{% endif %}
```

---

<a name="context-processors"></a>
## 6. CONTEXT PROCESSORS

### 6.1 Archivo: apps/access/context_processors.py

```python
"""
Context processors para inyectar funciones en contexto de templates.

CLEAN_CODE v3.0.1:
- Funciones: snake_case inglés
- Docstrings: español

CNST-034: Function-based permissions
"""

from django.http import HttpRequest
from typing import Dict, Any

from apps.access.services import RBACService


def user_functions(request: HttpRequest) -> Dict[str, Any]:
    """
    Context processor: Inyecta funciones del usuario en templates.
    
    Args:
        request: HttpRequest
    
    Returns:
        Dict con:
        - user_functions: Set de códigos de funciones
        - has_function: Helper function
    
    Usage en settings.py:
        TEMPLATES = [
            {
                'OPTIONS': {
                    'context_processors': [
                        'apps.access.context_processors.user_functions',
                    ],
                },
            },
        ]
    
    Usage en template (sin cargar tags):
        {% if 'AUD_VIEW' in user_functions %}
            <a href="{% url 'audit:logs' %}">Auditoría</a>
        {% endif %}
    
    CNST-035: Cache-aware (300s)
    """
    if not request.user or not request.user.is_authenticated:
        return {
            'user_functions': set(),
            'user_has_function': lambda x: False
        }
    
    rbac_service = RBACService()
    functions = rbac_service.get_user_functions(request.user)
    
    # Helper function para usar en template
    def has_func(function_code: str) -> bool:
        return function_code in functions
    
    return {
        'user_functions': functions,
        'user_has_function': has_func
    }
```

### 6.2 Configuración en settings.py

```python
# config/settings/base.py

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Django defaults
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # IACT custom
                'apps.access.context_processors.user_functions',  # ← AGREGAR
            ],
        },
    },
]
```

---

## 7. EJEMPLOS DE USO

### 7.1 Uso en DRF ViewSet

```python
# apps/audit/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.access.permissions import DynamicFunctionPermission
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para logs de auditoría.
    
    RBAC: DynamicFunctionPermission con function_map
    """
    
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    # function_map define permisos por acción
    function_map = {
        'list': 'audit.view',           # AUD_VIEW
        'retrieve': 'audit.view',       # AUD_VIEW
        'search': 'audit.search',       # AUD_SEARCH
        'export_csv': 'audit.export',   # AUD_EXPORT
    }
    
    # Automáticamente validado por DynamicFunctionPermission
```

### 7.2 Uso en Function-Based View

```python
# apps/audit/views.py

from django.shortcuts import render
from apps.access.decorators import require_function
from apps.audit.models import AuditLog


@require_function('AUD_VIEW')
def audit_log_list(request):
    """
    Vista de lista de logs.
    
    Requiere: AUD_VIEW
    """
    logs = AuditLog.objects.all()[:100]
    return render(request, 'audit/logs.html', {'logs': logs})


@require_any_function(['AUD_VIEW', 'DSH_VIEW', 'RPT_VIEW'])
def dashboard_view(request):
    """
    Dashboard accesible con múltiples permisos.
    
    Requiere: AL MENOS UNO de AUD_VIEW, DSH_VIEW, RPT_VIEW
    """
    return render(request, 'dashboard.html')


@require_all_functions(['AUD_VIEW', 'AUD_EXPORT', 'SYS_ADMIN'])
def sensitive_export_view(request):
    """
    Exportación sensible.
    
    Requiere: TODAS las funciones (AND logic)
    """
    return render(request, 'export.html')
```

### 7.3 Uso en Class-Based View

```python
# apps/audit/views.py

from django.views.generic import ListView
from apps.access.mixins import FunctionPermissionMixin
from apps.audit.models import AuditLog


class AuditLogListView(FunctionPermissionMixin, ListView):
    """
    ListView con validación de función.
    
    Requiere: AUD_VIEW
    """
    
    model = AuditLog
    template_name = 'audit/logs.html'
    context_object_name = 'logs'
    required_function = 'AUD_VIEW'
    permission_denied_message = "No tiene permiso para ver logs de auditoría."
    paginate_by = 50
```

### 7.4 Uso en Templates

```html
<!-- templates/base.html -->

{% load access_tags %}

<!DOCTYPE html>
<html>
<head>
    <title>IACT Call Center</title>
</head>
<body>
    <nav>
        <ul>
            <!-- Opción 1: Con filter has_function -->
            {% if user|has_function:'AUD_VIEW' %}
                <li><a href="{% url 'audit:logs' %}">Auditoría</a></li>
            {% endif %}
            
            {% if user|has_function:'DSH_VIEW' %}
                <li><a href="{% url 'dashboard' %}">Dashboard</a></li>
            {% endif %}
            
            {% if user|has_function:'ALR_SEND' %}
                <li><a href="{% url 'alerts:send' %}">Enviar Alerta</a></li>
            {% endif %}
            
            <!-- Opción 2: Con context processor (sin cargar tags) -->
            {% if 'RPT_VIEW' in user_functions %}
                <li><a href="{% url 'reports:list' %}">Reportes</a></li>
            {% endif %}
            
            <!-- OR logic -->
            {% if user|has_any_function:'AUD_VIEW,DSH_VIEW,RPT_VIEW' %}
                <li><a href="{% url 'general-dashboard' %}">Dashboard General</a></li>
            {% endif %}
            
            <!-- AND logic -->
            {% if user|has_all_functions:'AUD_VIEW,AUD_EXPORT,SYS_ADMIN' %}
                <li><a href="{% url 'sensitive-export' %}">Exportar Sensible</a></li>
            {% endif %}
        </ul>
    </nav>
    
    <!-- Mostrar permisos del usuario (debugging) -->
    {% if user.is_staff %}
        <div class="debug-panel">
            <h4>Permisos del usuario:</h4>
            {% user_functions_by_module as functions %}
            {% for module_code, function_list in functions.items %}
                <strong>{{ module_code }}:</strong>
                {% for func in function_list %}
                    {% permission_badge user func %}
                {% endfor %}
                <br>
            {% endfor %}
        </div>
    {% endif %}
    
    {% block content %}{% endblock %}
</body>
</html>
```

---

## 8. RESUMEN PARTE 3

### 8.1 Componentes Generados

```yaml
Archivos Python:
  ✅ apps/access/permissions.py (~300 líneas)
     - DynamicFunctionPermission (LA permission class principal)
     - IsAdminOrReadOnly
     - HasAnyFunction
     - HasAllFunctions
  
  ✅ apps/access/decorators.py (~250 líneas)
     - @require_function (principal)
     - @require_any_function (OR logic)
     - @require_all_functions (AND logic)
     - @require_function_or_superuser
     - @ajax_require_function
  
  ✅ apps/access/mixins.py (~150 líneas)
     - FunctionPermissionMixin (principal)
     - MultipleRequiredFunctionsMixin (AND)
     - AnyRequiredFunctionMixin (OR)
  
  ✅ apps/access/templatetags/access_tags.py (~150 líneas)
     - has_function filter (principal)
     - has_any_function filter
     - has_all_functions filter
     - user_functions_by_module tag
     - permission_badge inclusion tag
  
  ✅ apps/access/context_processors.py (~50 líneas)
     - user_functions processor
  
  ✅ apps/access/templates/access/permission_badge.html
     - Template para inclusion tag

Total: ~900 líneas Python production-ready
```

### 8.2 Uso en TODO el Sistema

```yaml
DynamicFunctionPermission:
  Usado en: TODOS los ViewSets DRF
  - apps/audit/views.py
  - apps/dashboard/views.py
  - apps/alerts/views.py
  - apps/reports/views.py
  - ... (todas las apps)

@require_function:
  Usado en: TODAS las function-based views
  - Vistas tradicionales Django
  - Endpoints custom

FunctionPermissionMixin:
  Usado en: TODAS las class-based views
  - ListView, DetailView, etc
  - Vistas genéricas Django

has_function filter:
  Usado en: TODOS los templates
  - Menús condicionales
  - Botones según permisos
  - Links dinámicos

user_functions context processor:
  Usado en: TODOS los templates (inyectado globalmente)
  - Sin necesidad de {% load access_tags %}
  - Disponible en todo el sistema
```

---

## PRÓXIMA PARTE

**PARTE 4/6: Middleware y APIs**

Contenido:
- ✅ RBACMiddleware (attach user_functions to request)
- ✅ ViewSets REST (8 endpoints):
  - FunctionViewSet (CRUD funciones)
  - ModuleViewSet (CRUD módulos)
  - GroupViewSet (CRUD grupos)
  - UserGroupViewSet (assign users)
  - GroupFunctionViewSet (assign functions)
  - PermissionLogViewSet (audit logs)
- ✅ Serializers (8 serializers)
- ✅ URLs configuration

**Estimado:** ~1,000 líneas, 3 horas

---

**Fin de PARTE 3/6**
