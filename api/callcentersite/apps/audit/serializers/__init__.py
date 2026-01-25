"""
Audit Serializers - Organización con SRP.

Este paquete organiza los serializers de audit aplicando el principio
de Responsabilidad Única (Single Responsibility Principle).

Estructura:
- auditlog_serializers.py: Serialización de logs de auditoría

Importaciones centralizadas para mantener compatibilidad:
    from apps.audit.serializers import AuditLogSerializer
    from apps.audit.serializers import AuditLogSummarySerializer

Características:
- READ-ONLY: Los logs de auditoría son inmutables
- Campos enriched: username, full_name
- Performance optimizado: versión summary sin campos pesados

Principios aplicados:
- SRP: Responsabilidad única (logs de auditoría)
- Immutability: Todos los campos son read-only
- Clean Code: Información de usuario enriquecida
"""

# ====================================================================================
# AUDITLOG SERIALIZERS
# ====================================================================================

from .auditlog_serializers import (
    AuditLogSerializer,
    AuditLogSummarySerializer,
)

# ====================================================================================
# __all__ - Exportaciones públicas
# ====================================================================================

__all__ = [
    # AuditLog serializers
    'AuditLogSerializer',
    'AuditLogSummarySerializer',
]

# ====================================================================================
# RESUMEN
# ====================================================================================
#
# Total Serializers: 2
#
# AuditLog (2):
#   ✅ AuditLogSerializer - Log completo con detalles
#   ✅ AuditLogSummarySerializer - Resumen para listados
#
# Características:
#   ✅ SRP aplicado (1 archivo con responsabilidad única)
#   ✅ READ-ONLY (logs inmutables)
#   ✅ Campos enriched (username, full_name)
#   ✅ Performance optimizado (summary vs detail)
#   ✅ Auditoría completa (action, resource, result, timestamp)
#   ✅ IP tracking (ip_address, user_agent)
#   ✅ Compatibilidad mantenida
#
# ====================================================================================
