"""
Dashboard Serializers - Organización con SRP.

Este paquete organiza los serializers de dashboard aplicando el principio
de Responsabilidad Única (Single Responsibility Principle).

Estructura:
- dashboard_serializers.py: Serialización de configuraciones de dashboards
- widget_serializers.py: Serialización de widgets
- filter_serializers.py: Serialización de filtros guardados
- preference_serializers.py: Serialización de preferencias de usuario

Importaciones centralizadas para mantener compatibilidad:
    from apps.dashboard.serializers import DashboardConfigSerializer
    from apps.dashboard.serializers import WidgetConfigSerializer
    # etc.

Principios aplicados:
- SRP: Cada archivo tiene una responsabilidad única
- DRY: Evitar duplicación de código
- Clean Code: Nombres descriptivos y organización clara
"""

# ====================================================================================
# DASHBOARD SERIALIZERS
# ====================================================================================

from .dashboard_serializers import (
    DashboardConfigSerializer,
    DashboardConfigListSerializer,
    DashboardConfigDetailSerializer,
    DashboardExportSerializer,
    DashboardImportSerializer,
)

# ====================================================================================
# WIDGET SERIALIZERS
# ====================================================================================

from .widget_serializers import (
    WidgetConfigSerializer,
    WidgetConfigCreateSerializer,
    WidgetConfigUpdateSerializer,
    WidgetDataSerializer,
)

# ====================================================================================
# FILTER SERIALIZERS
# ====================================================================================

from .filter_serializers import (
    SavedFilterSerializer,
    SavedFilterListSerializer,
)

# ====================================================================================
# PREFERENCE SERIALIZERS
# ====================================================================================

from .preference_serializers import (
    UserDashboardPreferenceSerializer,
)

# ====================================================================================
# __all__ - Exportaciones públicas
# ====================================================================================

__all__ = [
    # Dashboard serializers
    'DashboardConfigSerializer',
    'DashboardConfigListSerializer',
    'DashboardConfigDetailSerializer',
    'DashboardExportSerializer',
    'DashboardImportSerializer',
    
    # Widget serializers
    'WidgetConfigSerializer',
    'WidgetConfigCreateSerializer',
    'WidgetConfigUpdateSerializer',
    'WidgetDataSerializer',
    
    # Filter serializers
    'SavedFilterSerializer',
    'SavedFilterListSerializer',
    
    # Preference serializers
    'UserDashboardPreferenceSerializer',
]

# ====================================================================================
# RESUMEN
# ====================================================================================
#
# Total Serializers: 12
#
# Dashboards (5):
#   ✅ DashboardConfigSerializer - Dashboard básico
#   ✅ DashboardConfigListSerializer - Para listados
#   ✅ DashboardConfigDetailSerializer - Con widgets anidados
#   ✅ DashboardExportSerializer - Para exportación
#   ✅ DashboardImportSerializer - Para importación
#
# Widgets (4):
#   ✅ WidgetConfigSerializer - Widget básico
#   ✅ WidgetConfigCreateSerializer - Para creación
#   ✅ WidgetConfigUpdateSerializer - Para actualización
#   ✅ WidgetDataSerializer - Para respuestas de datos
#
# Filters (2):
#   ✅ SavedFilterSerializer - Filtro completo
#   ✅ SavedFilterListSerializer - Para listados
#
# Preferences (1):
#   ✅ UserDashboardPreferenceSerializer - Preferencias de usuario
#
# Características:
#   ✅ SRP aplicado (4 archivos con responsabilidades únicas)
#   ✅ Validaciones robustas en cada serializer
#   ✅ Campos enriched (user_username, etc.)
#   ✅ Integración con FilterService
#   ✅ Import/Export de dashboards
#   ✅ Compatibilidad mantenida
#
# ====================================================================================
