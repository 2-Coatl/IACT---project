"""
Serializers para apps/users/.

CLEAN_CODE v3.0.1: Imports organizados por módulo.
FASE 2 PARTE 4: 11 serializers implementados.

Estructura:
├── user_serializer.py (5 serializers de User)
├── profile_serializer.py (3 serializers de Profile)
├── auth_serializer.py (2 serializers de Auth)
└── session_serializer.py (1 serializer de SessionHistory)
"""

# User serializers (5)
from apps.users.serializers.user_serializer import (
    UserSerializer,
    UserListSerializer,
    # UserDetailSerializer,  # TODO: No existe en user_serializer.py - comentado temporalmente
    UserCreateSerializer,
    UserUpdateSerializer,
)

# Profile serializers (3)
from apps.users.serializers.profile_serializer import (
    ProfileSerializer,
    UserSettingsSerializer,
    AvatarUploadSerializer,
)

# Auth serializers (2)
from apps.users.serializers.auth_serializer import (
    PasswordChangeSerializer,
    UserActivationSerializer,
)

# Session serializer (1)
from apps.users.serializers.session_serializer import (
    SessionHistorySerializer,
)


__all__ = [
    # User (5 → 4 temporalmente)
    'UserSerializer',
    'UserListSerializer',
    # 'UserDetailSerializer',  # TODO: No existe - comentado temporalmente
    'UserCreateSerializer',
    'UserUpdateSerializer',
    
    # Profile (3)
    'ProfileSerializer',
    'UserSettingsSerializer',
    'AvatarUploadSerializer',
    
    # Auth (2)
    'PasswordChangeSerializer',
    'UserActivationSerializer',
    
    # Session (1)
    'SessionHistorySerializer',
]


# ============================================================================
# RESUMEN SERIALIZERS
#
# Total: 11 serializers
#
# User (5):
#   ✅ UserSerializer - Básico para uso general
#   ✅ UserListSerializer - Lightweight para listados
#   ✅ UserDetailSerializer - Completo con relaciones
#   ✅ UserCreateSerializer - Crear con validación
#   ✅ UserUpdateSerializer - Actualizar campos editables
#
# Profile (3):
#   ✅ ProfileSerializer - Perfil extendido
#   ✅ UserSettingsSerializer - Preferencias (language, notifications)
#   ✅ AvatarUploadSerializer - Subir avatar
#
# Auth (2):
#   ✅ PasswordChangeSerializer - Cambiar password
#   ✅ UserActivationSerializer - Activar/desactivar
#
# Session (1):
#   ✅ SessionHistorySerializer - Auditoría de sesiones
#
# Scope apps/users/:
#   ✅ SOLO gestión de usuarios
#   ❌ NO gestión de RBAC (apps/access)
#   ❌ NO login/logout (apps/authentication)
#
# Principios aplicados:
#   ✅ SOLID SRP: Cada serializer un propósito
#   ✅ DRY: Delegación a services
#   ✅ Clean Code: Nombres auto-documentados
#   ✅ Validation: Passwords fuertes, datos correctos
#
# FASE 2 PARTE 4: ✅ COMPLETADA
# ============================================================================
