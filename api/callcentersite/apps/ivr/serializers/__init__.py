"""
IVR Serializers - Organización con SRP.

Este paquete organiza los serializers de IVR aplicando el principio
de Responsabilidad Única (Single Responsibility Principle).

Estructura:
- calllog_serializers.py: Serialización de logs de llamadas IVR

Importaciones centralizadas para mantener compatibilidad:
    from apps.ivr.serializers import CallLogSerializer
    from apps.ivr.serializers import CallLogListSerializer
    # etc.

Constraints documentados:
- CNST-003: CallLog es READ-ONLY (datos legacy de MariaDB ivr_legacy)

Principios aplicados:
- SRP: Responsabilidad única (logs de llamadas IVR)
- READ-ONLY: No permite create/update/delete (datos legacy)
- Clean Code: Cálculos de métricas explícitos
"""

# ====================================================================================
# CALLLOG SERIALIZERS
# ====================================================================================

from .calllog_serializers import (
    CallLogSerializer,
    CallLogListSerializer,
    CallLogStatsSerializer,
)

# ====================================================================================
# __all__ - Exportaciones públicas
# ====================================================================================

__all__ = [
    # CallLog serializers
    'CallLogSerializer',
    'CallLogListSerializer',
    'CallLogStatsSerializer',
]

# ====================================================================================
# RESUMEN
# ====================================================================================
#
# Total Serializers: 3
#
# CallLog (3):
#   ✅ CallLogSerializer - Log completo con métricas
#   ✅ CallLogListSerializer - Listado simplificado
#   ✅ CallLogStatsSerializer - Estadísticas agregadas
#
# Características:
#   ✅ SRP aplicado (1 archivo con responsabilidad única)
#   ✅ READ-ONLY compliance (CNST-003)
#   ✅ Métricas calculadas (answer_rate, abandon_rate)
#   ✅ Performance optimizado (list vs detail)
#   ✅ Stats endpoint support
#   ✅ Datos legacy de MariaDB
#   ✅ Compatibilidad mantenida
#
# ====================================================================================
