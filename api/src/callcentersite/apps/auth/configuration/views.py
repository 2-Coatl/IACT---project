"""
Vistas API REST para gestion de configuraciones del sistema.

Endpoints:
    - GET    /api/v1/configuracion/                  (obtener)
    - GET    /api/v1/configuracion/:clave/           (detalle)
    - PUT    /api/v1/configuracion/:clave/           (editar)
    - GET    /api/v1/configuracion/:clave/historial/ (historial)
    - GET    /api/v1/configuracion/auditar/          (auditoria)
    - GET    /api/v1/configuracion/exportar/         (exportar)
    - POST   /api/v1/configuracion/importar/         (importar)
    - POST   /api/v1/configuracion/:clave/restaurar/ (restaurar)

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (FASE 3)
"""

from __future__ import annotations

from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ConfiguracionSerializer,
    ConfiguracionHistorialSerializer,
    EditarConfiguracionSerializer,
    ImportarConfiguracionSerializer,
)
from .services import ConfiguracionService


class ConfiguracionListView(APIView):
    """
    Obtiene configuraciones del sistema.

    Query params:
        - categoria: str (opcional)

    Permiso: sistema.tecnico.configuracion.ver
    """

    def get(self, request):  # type: ignore[override]
        try:
            categoria = request.query_params.get('categoria', None)

            configuraciones = ConfiguracionService.obtener_configuracion(
                usuario_id=request.user.id,
                categoria=categoria,
            )

            return Response(configuraciones)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )


class ConfiguracionEditarView(APIView):
    """
    Edita una configuracion del sistema.

    Permiso: sistema.tecnico.configuracion.editar
    """

    def get(self, request, clave):  # type: ignore[override]
        try:
            configuracion = ConfiguracionService.obtener_configuracion_detalle(
                usuario_id=request.user.id,
                clave=clave,
            )

            output_serializer = ConfiguracionSerializer(configuracion)
            return Response(output_serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, clave):  # type: ignore[override]
        serializer = EditarConfiguracionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Obtener IP del request
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            configuracion = ConfiguracionService.editar_configuracion(
                usuario_id=request.user.id,
                clave=clave,
                nuevo_valor=serializer.validated_data['nuevo_valor'],
                ip_address=ip_address,
                user_agent=user_agent,
            )

            output_serializer = ConfiguracionSerializer(configuracion)
            return Response(output_serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ConfiguracionExportarView(APIView):
    """
    Exporta todas las configuraciones del sistema.

    Permiso: sistema.tecnico.configuracion.exportar
    """

    def get(self, request):  # type: ignore[override]
        try:
            export_data = ConfiguracionService.exportar_configuracion(
                usuario_id=request.user.id,
                formato='json',
            )

            return Response(export_data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )


class ConfiguracionImportarView(APIView):
    """
    Importa configuraciones desde JSON.

    Permiso: sistema.tecnico.configuracion.importar
    """

    def post(self, request):  # type: ignore[override]
        serializer = ImportarConfiguracionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Obtener IP del request
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            resultado = ConfiguracionService.importar_configuracion(
                usuario_id=request.user.id,
                configuraciones_json=serializer.validated_data['configuraciones_json'],
                ip_address=ip_address,
                user_agent=user_agent,
            )

            return Response(resultado)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )


class ConfiguracionRestaurarView(APIView):
    """
    Restaura una configuracion a su valor por defecto.

    Permiso: sistema.tecnico.configuracion.restaurar
    """

    def post(self, request, clave):  # type: ignore[override]
        try:
            # Obtener IP del request
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            configuracion = ConfiguracionService.restaurar_configuracion(
                usuario_id=request.user.id,
                clave=clave,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            output_serializer = ConfiguracionSerializer(configuracion)
            return Response(output_serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ConfiguracionHistorialView(APIView):
    """Expone el historial de cambios de una configuracion."""

    def get(self, request, clave):  # type: ignore[override]
        try:
            historial = ConfiguracionService.obtener_historial_configuracion(
                usuario_id=request.user.id,
                clave=clave,
            )

            serializer = ConfiguracionHistorialSerializer(historial, many=True)
            return Response(serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ConfiguracionAuditoriaView(APIView):
    """Devuelve el historial completo de configuraciones."""

    def get(self, request):  # type: ignore[override]
        try:
            historial = ConfiguracionService.obtener_historial_general(
                usuario_id=request.user.id,
            )

            serializer = ConfiguracionHistorialSerializer(historial, many=True)
            return Response(serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
