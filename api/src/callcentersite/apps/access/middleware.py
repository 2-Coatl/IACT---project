"""
Middleware para proteccion de endpoints con permisos granulares.

Sistema de Permisos Granular - Prioridad 1
REF: ADR-012-sistema-permisos-sin-roles-jerarquicos.md
"""

from __future__ import annotations

from functools import wraps
from typing import Callable, TYPE_CHECKING

from django.http import JsonResponse

from callcentersite.apps.access.services import PermisoService

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def verificar_permiso(
    capacidad_requerida: str | list[str],
    auditar: bool = False,
    mensaje_error: str | None = None
) -> Callable:
    """
    Decorator para proteger views con verificacion de permisos.

    Uso:
        @verificar_permiso("sistema.operaciones.llamadas.realizar")
        def realizar_llamada(request):
            # Solo usuarios con capacidad 'realizar llamadas' llegan aqui
            ...

        @verificar_permiso([
            "sistema.finanzas.pagos.aprobar",
            "sistema.finanzas.pagos.validar"
        ])
        def aprobar_pago(request, pago_id):
            # Usuario debe tener TODAS las capacidades listadas
            ...

    Args:
        capacidad_requerida: Capacidad o lista de capacidades requeridas
        auditar: Si True, registra acceso en auditoria (default: False)
        mensaje_error: Mensaje personalizado para error 403 (opcional)

    Returns:
        Decorator que envuelve la view

    Raises:
        HTTP 401: Usuario no autenticado
        HTTP 403: Usuario sin permiso requerido
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            # 1. Verificar autenticacion
            if not request.user.is_authenticated:
                return JsonResponse(
                    {
                        "error": "Autenticacion requerida",
                        "detalle": "Debe autenticarse para acceder a este recurso"
                    },
                    status=401
                )

            usuario_id = request.user.id

            # 2. Convertir capacidad_requerida a lista si es string
            capacidades = (
                [capacidad_requerida]
                if isinstance(capacidad_requerida, str)
                else capacidad_requerida
            )

            # 3. Verificar TODAS las capacidades requeridas
            permisos_faltantes = []
            for capacidad in capacidades:
                if not PermisoService.usuario_tiene_permiso(usuario_id, capacidad):
                    permisos_faltantes.append(capacidad)

            # 4. Si falta alguna capacidad, denegar acceso
            if permisos_faltantes:
                # Registrar intento de acceso denegado si auditar=True
                if auditar:
                    PermisoService.registrar_acceso(
                        usuario_id=usuario_id,
                        capacidad=", ".join(permisos_faltantes),
                        accion="ACCESO_DENEGADO",
                        ip_address=_obtener_ip_cliente(request),
                        user_agent=request.META.get("HTTP_USER_AGENT"),
                        metadata={
                            "path": request.path,
                            "method": request.method,
                            "permisos_faltantes": permisos_faltantes
                        }
                    )

                error_msg = mensaje_error or (
                    f"Permiso denegado. Requiere: {', '.join(permisos_faltantes)}"
                )

                return JsonResponse(
                    {
                        "error": error_msg,
                        "capacidades_requeridas": permisos_faltantes
                    },
                    status=403
                )

            # 5. Usuario tiene todos los permisos, registrar acceso si requerido
            if auditar:
                PermisoService.registrar_acceso(
                    usuario_id=usuario_id,
                    capacidad=", ".join(capacidades),
                    accion="ACCESO_PERMITIDO",
                    ip_address=_obtener_ip_cliente(request),
                    user_agent=request.META.get("HTTP_USER_AGENT"),
                    metadata={
                        "path": request.path,
                        "method": request.method
                    }
                )

            # 6. Ejecutar view original
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def _obtener_ip_cliente(request: HttpRequest) -> str | None:
    """
    Extrae IP del cliente desde request.

    Maneja casos de:
    - Conexion directa
    - Detras de proxy (X-Forwarded-For)
    - Detras de load balancer

    Args:
        request: HttpRequest de Django

    Returns:
        IP del cliente o None
    """
    # Intentar obtener IP real si esta detras de proxy
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # X-Forwarded-For puede contener multiples IPs separadas por coma
        # La primera es la del cliente original
        ip = x_forwarded_for.split(",")[0].strip()
        return ip

    # Si no hay proxy, usar REMOTE_ADDR
    return request.META.get("REMOTE_ADDR")


def verificar_permiso_auditable(capacidad_requerida: str | list[str]) -> Callable:
    """
    Decorator para proteger views que SIEMPRE requieren auditoria.

    Equivalente a verificar_permiso con auditar=True.

    Uso:
        @verificar_permiso_auditable("sistema.finanzas.pagos.aprobar")
        def aprobar_pago(request, pago_id):
            # Siempre se auditara el acceso
            ...

    Args:
        capacidad_requerida: Capacidad o lista de capacidades requeridas

    Returns:
        Decorator que envuelve la view
    """
    return verificar_permiso(capacidad_requerida, auditar=True)
