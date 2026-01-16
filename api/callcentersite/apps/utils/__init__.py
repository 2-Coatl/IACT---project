"""
Utilidades reutilizables del proyecto.

Este paquete contiene funciones auxiliares, mixins y helpers
que se usan en múltiples apps del proyecto.

Módulos:
- models: Mixins para modelos Django (SoftDeleteMixin)
- request: Utilidades HTTP/Request (get_client_ip, get_user_agent, etc)
"""

# Models utilities
from .models import (
    SoftDeleteQuerySet,
    SoftDeleteManager,
    SoftDeleteMixin,
)

# Request utilities
from .request import (
    get_client_ip,
    get_user_agent,
    should_exclude_path,
    is_ajax_request,
    get_request_info,
)

__all__ = [
    # Models
    'SoftDeleteQuerySet',
    'SoftDeleteManager',
    'SoftDeleteMixin',
    # Request
    'get_client_ip',
    'get_user_agent',
    'should_exclude_path',
    'is_ajax_request',
    'get_request_info',
]
