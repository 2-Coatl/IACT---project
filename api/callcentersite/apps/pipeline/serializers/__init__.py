"""
Pipeline Serializers - Organización con SRP.

Este paquete organiza los serializers de pipeline aplicando el principio
de Responsabilidad Única (Single Responsibility Principle).

Estructura:
- center_serializers.py: Serialización de centros de llamadas
- service_serializers.py: Serialización de servicios
- callrecord_serializers.py: Serialización de registros de llamadas
- callnote_serializers.py: Serialización de notas de llamadas

Importaciones centralizadas para mantener compatibilidad:
    from apps.pipeline.serializers import CenterSerializer
    from apps.pipeline.serializers import ServiceSerializer
    # etc.

Principios aplicados:
- SRP: Cada archivo tiene una responsabilidad única
- DRY: Evitar duplicación de código
- Clean Code: Nombres descriptivos y organización clara
- Performance: Serializers list/detail separados
"""

# ====================================================================================
# CENTER SERIALIZERS
# ====================================================================================

from .center_serializers import (
    CenterSerializer,
    CenterListSerializer,
    CenterDetailSerializer,
)

# ====================================================================================
# SERVICE SERIALIZERS
# ====================================================================================

from .service_serializers import (
    ServiceSerializer,
    ServiceListSerializer,
    ServiceDetailSerializer,
)

# ====================================================================================
# CALLRECORD SERIALIZERS
# ====================================================================================

from .callrecord_serializers import (
    CallRecordSerializer,
    CallRecordListSerializer,
    CallRecordStatsSerializer,
)

# ====================================================================================
# CALLNOTE SERIALIZERS
# ====================================================================================

from .callnote_serializers import (
    CallNoteSerializer,
)

# ====================================================================================
# __all__ - Exportaciones públicas
# ====================================================================================

__all__ = [
    # Center serializers
    'CenterSerializer',
    'CenterListSerializer',
    'CenterDetailSerializer',
    
    # Service serializers
    'ServiceSerializer',
    'ServiceListSerializer',
    'ServiceDetailSerializer',
    
    # CallRecord serializers
    'CallRecordSerializer',
    'CallRecordListSerializer',
    'CallRecordStatsSerializer',
    
    # CallNote serializers
    'CallNoteSerializer',
]

# ====================================================================================
# RESUMEN
# ====================================================================================
#
# Total Serializers: 10
#
# Centros (3):
#   ✅ CenterSerializer - Centro con métricas de servicios
#   ✅ CenterListSerializer - Listado simplificado
#   ✅ CenterDetailSerializer - Centro con servicios anidados
#
# Servicios (3):
#   ✅ ServiceSerializer - Servicio con métricas de usuarios
#   ✅ ServiceListSerializer - Listado simplificado
#   ✅ ServiceDetailSerializer - Servicio con centro anidado
#
# Registros de llamadas (3):
#   ✅ CallRecordSerializer - Registro completo con métricas
#   ✅ CallRecordListSerializer - Listado simplificado
#   ✅ CallRecordStatsSerializer - Estadísticas agregadas
#
# Notas de llamadas (1):
#   ✅ CallNoteSerializer - Nota completa con info de usuario
#
# Características:
#   ✅ SRP aplicado (4 archivos con responsabilidades únicas)
#   ✅ Serializers list/detail separados para performance
#   ✅ Validaciones robustas (código único, centro activo, etc.)
#   ✅ Campos enriched (center_name, agent_username, etc.)
#   ✅ Métricas calculadas (answer_rate, abandonment_rate, etc.)
#   ✅ Import circular resuelto con imports locales
#   ✅ Compatibilidad mantenida
#
# ====================================================================================
