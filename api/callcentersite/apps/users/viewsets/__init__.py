"""
ViewSets para apps/users/.

CLEAN_CODE v3.0.1: Imports organizados por módulo.
FASE 2 PARTE 5: 4 ViewSets implementados.

Estructura:
├── user_viewset.py - CRUD usuarios con RBAC
├── profile_viewset.py - Gestión perfil propio
├── auth_viewset.py - Cambio de password
└── session_viewset.py - Auditoría sesiones
"""

from apps.users.viewsets.user_viewset import UserViewSet
from apps.users.viewsets.profile_viewset import ProfileViewSet
from apps.users.viewsets.auth_viewset import AuthViewSet
from apps.users.viewsets.session_viewset import SessionHistoryViewSet


__all__ = [
    'UserViewSet',
    'ProfileViewSet',
    'AuthViewSet',
    'SessionHistoryViewSet',
]


# ============================================================================
# RESUMEN VIEWSETS
#
# Total: 4 ViewSets
#
# UserViewSet:
#   ✅ CRUD completo de usuarios
#   ✅ Permissions vía function_map
#   ✅ Custom actions: activate, deactivate
#   ✅ Soft delete
#
# ProfileViewSet:
#   ✅ Gestión de perfil propio (/me/)
#   ✅ Settings (language, notifications)
#   ✅ Avatar (upload, remove)
#   ✅ Sin RBAC (perfil propio)
#
# AuthViewSet:
#   ✅ Cambio de password
#   ✅ Sin RBAC (password propio)
#   ❌ NO Login/Logout (apps/authentication)
#
# SessionHistoryViewSet:
#   ✅ Auditoría de sesiones
#   ✅ Read-only
#   ✅ Permissions vía function_map
#   ✅ Queryset por rol (staff vs usuario)
#
# Namespaces Django usados:
#   ✅ 'users.view'
#   ✅ 'users.create'
#   ✅ 'users.edit'
#   ✅ 'users.delete'
#   ✅ 'sessions.view'
#
# Permissions:
#   ✅ RequiresFunctionPermission (apps/core)
#   ✅ IsAuthenticated
#   ✅ function_map para RBAC
#
# Scope apps/users/:
#   ✅ SOLO gestión de usuarios
#   ❌ NO gestión de RBAC (apps/access)
#   ❌ NO Login/Logout (apps/authentication)
#
# FASE 2 PARTE 5: ✅ COMPLETADA
# ============================================================================
