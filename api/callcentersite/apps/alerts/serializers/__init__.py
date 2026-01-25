"""
Alerts Serializers - Organización con SRP.

Este paquete organiza los serializers de alerts aplicando el principio
de Responsabilidad Única (Single Responsibility Principle).

Estructura:
- message_serializers.py: Serialización de mensajes internos
- alert_serializers.py: Serialización de configuraciones y suscripciones

Importaciones centralizadas para mantener compatibilidad:
    from apps.alerts.serializers import InternalMessageCreateSerializer
    from apps.alerts.serializers import AlertConfigurationSerializer
    # etc.

Principios aplicados:
- SRP: Cada archivo tiene una responsabilidad única
- DRY: Evitar duplicación de código
- Clean Code: Nombres descriptivos y organización clara
- Service Layer: Uso de services para lógica de negocio
"""

# ====================================================================================
# MESSAGE SERIALIZERS
# ====================================================================================

from .message_serializers import (
    UserBasicSerializer,
    MessageRecipientSerializer,
    InternalMessageListSerializer,
    InternalMessageDetailSerializer,
    InternalMessageCreateSerializer,
    InboxMessageSerializer,
)

# ====================================================================================
# ALERT SERIALIZERS
# ====================================================================================

from .alert_serializers import (
    AlertConfigurationSerializer,
    AlertSubscriptionSerializer,
    AlertSubscriptionCreateSerializer,
)

# ====================================================================================
# __all__ - Exportaciones públicas
# ====================================================================================

__all__ = [
    # Message serializers
    'UserBasicSerializer',
    'MessageRecipientSerializer',
    'InternalMessageListSerializer',
    'InternalMessageDetailSerializer',
    'InternalMessageCreateSerializer',
    'InboxMessageSerializer',
    
    # Alert serializers
    'AlertConfigurationSerializer',
    'AlertSubscriptionSerializer',
    'AlertSubscriptionCreateSerializer',
]

# ====================================================================================
# RESUMEN
# ====================================================================================
#
# Total Serializers: 9
#
# Mensajes Internos (6):
#   ✅ UserBasicSerializer - Usuario básico para nested
#   ✅ MessageRecipientSerializer - Destinatario de mensaje
#   ✅ InternalMessageListSerializer - Listado de mensajes
#   ✅ InternalMessageDetailSerializer - Detalle de mensaje
#   ✅ InternalMessageCreateSerializer - Creación de mensaje
#   ✅ InboxMessageSerializer - Mensaje en bandeja
#
# Alertas (3):
#   ✅ AlertConfigurationSerializer - Configuración de alerta
#   ✅ AlertSubscriptionSerializer - Suscripción a alerta
#   ✅ AlertSubscriptionCreateSerializer - Creación de suscripción
#
# Características:
#   ✅ SRP aplicado (2 archivos con responsabilidades únicas)
#   ✅ Validaciones robustas (recipients, conditions)
#   ✅ Service Layer (MessageService, SubscriptionService)
#   ✅ Campos enriched (sender, user, etc.)
#   ✅ Constraint CNST-024 (máx 50 destinatarios)
#   ✅ Import circular resuelto con imports locales
#   ✅ Compatibilidad mantenida
#
# ====================================================================================
