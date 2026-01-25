"""
Access Serializers - Organización con SRP.

Este paquete organiza los serializers de access aplicando el principio
de Responsabilidad Única (Single Responsibility Principle).

Estructura:
- module_serializers.py: Serialización de módulos
- module_access_serializers.py: Serialización de accesos a módulos
- function_serializers.py: Serialización de funciones RBAC
- function_assignment_serializers.py: Serialización de asignaciones de funciones

Importaciones centralizadas para mantener compatibilidad:
    from apps.access.serializers import ModuleSerializer
    from apps.access.serializers import FunctionSerializer
    # etc.

Principios aplicados:
- SRP: Cada archivo tiene una responsabilidad única
- DRY: Evitar duplicación de código
- Clean Code: Nombres descriptivos y organización clara
- RBAC v6.0.0: Soporte completo de namespaces
"""

# ====================================================================================
# MODULE SERIALIZERS
# ====================================================================================

from .module_serializers import (
    ModuleSerializer,
    ModuleTreeSerializer,
    MyModulesSerializer,
)

# ====================================================================================
# MODULE ACCESS SERIALIZERS
# ====================================================================================

from .module_access_serializers import (
    UserModuleAccessSerializer,
)

# ====================================================================================
# FUNCTION SERIALIZERS (RBAC v6.0.0)
# ====================================================================================

from .function_serializers import (
    FunctionSerializer,
    FunctionListSerializer,
)

# ====================================================================================
# FUNCTION ASSIGNMENT SERIALIZERS (RBAC v6.0.0)
# ====================================================================================

from .function_assignment_serializers import (
    UserFunctionAssignmentSerializer,
    AssignFunctionSerializer,
    RevokeFunctionSerializer,
    MyFunctionsSerializer,
)

# ====================================================================================
# __all__ - Exportaciones públicas
# ====================================================================================

__all__ = [
    # Module serializers
    'ModuleSerializer',
    'ModuleTreeSerializer',
    'MyModulesSerializer',
    
    # Module access serializers
    'UserModuleAccessSerializer',
    
    # Function serializers (RBAC v6.0.0)
    'FunctionSerializer',
    'FunctionListSerializer',
    
    # Function assignment serializers (RBAC v6.0.0)
    'UserFunctionAssignmentSerializer',
    'AssignFunctionSerializer',
    'RevokeFunctionSerializer',
    'MyFunctionsSerializer',
]

# ====================================================================================
# RESUMEN
# ====================================================================================
#
# Total Serializers: 10
#
# Módulos (3):
#   ✅ ModuleSerializer - Módulo con info de jerarquía
#   ✅ ModuleTreeSerializer - Módulo en estructura de árbol
#   ✅ MyModulesSerializer - Respuesta /my-modules/
#
# Accesos a módulos (1):
#   ✅ UserModuleAccessSerializer - Accesos de usuarios a módulos
#
# Funciones RBAC v6.0.0 (2):
#   ✅ FunctionSerializer - Función completa
#   ✅ FunctionListSerializer - Función simplificada (listas)
#
# Asignaciones de funciones RBAC v6.0.0 (4):
#   ✅ UserFunctionAssignmentSerializer - Asignación de función
#   ✅ AssignFunctionSerializer - Input para asignar función
#   ✅ RevokeFunctionSerializer - Input para revocar función
#   ✅ MyFunctionsSerializer - Respuesta /my-functions/
#
# Características:
#   ✅ SRP aplicado (4 archivos con responsabilidades únicas)
#   ✅ RBAC v6.0.0 con namespaces
#   ✅ Validaciones robustas
#   ✅ Campos enriched
#   ✅ Documentación completa
#   ✅ Compatibilidad mantenida
#
# ====================================================================================
