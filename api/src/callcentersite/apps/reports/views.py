"""Vistas del dashboard."""

from __future__ import annotations

from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from callcentersite.apps.users.services_permisos_granular import UserManagementService

from .serializers import (
    CompartirDashboardSerializer,
    ExportarDashboardSerializer,
    PersonalizarDashboardSerializer,
)
from .services import DashboardService


class DashboardOverviewView(APIView):
    """Devuelve información general del dashboard.

    Requiere permiso: sistema.vistas.dashboards.ver

    Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 24)
    """

    def get(self, request):  # type: ignore[override]
        # Verificar permiso
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=request.user.id,
            capacidad_codigo='sistema.vistas.dashboards.ver',
        )

        if not tiene_permiso:
            raise PermissionDenied(
                'No tiene permiso para ver dashboards'
            )

        return Response(DashboardService.overview())


class DashboardExportarView(APIView):
    """Exporta dashboard a PDF o Excel.

    Requiere permiso: sistema.vistas.dashboards.exportar
    """

    def post(self, request):  # type: ignore[override]
        serializer = ExportarDashboardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            resultado = DashboardService.exportar(
                usuario_id=request.user.id,
                formato=serializer.validated_data['formato'],
            )
            return Response(resultado)

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


class DashboardPersonalizarView(APIView):
    """Personaliza configuracion de dashboard.

    Requiere permiso: sistema.vistas.dashboards.personalizar
    """

    def put(self, request):  # type: ignore[override]
        serializer = PersonalizarDashboardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            config = DashboardService.personalizar(
                usuario_id=request.user.id,
                configuracion=serializer.validated_data['configuracion'],
            )

            return Response({
                'id': config.id,
                'configuracion': config.configuracion,
                'updated_at': config.updated_at.isoformat(),
            })

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


class DashboardCompartirView(APIView):
    """Comparte dashboard con usuario o grupo.

    Requiere permiso: sistema.vistas.dashboards.compartir
    """

    def post(self, request):  # type: ignore[override]
        serializer = CompartirDashboardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            resultado = DashboardService.compartir(
                usuario_id=request.user.id,
                compartir_con_usuario_id=serializer.validated_data.get('compartir_con_usuario_id'),
                compartir_con_grupo_codigo=serializer.validated_data.get('compartir_con_grupo_codigo'),
            )

            return Response(resultado)

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
