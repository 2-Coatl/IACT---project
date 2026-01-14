"""Views para reportes IVR."""

from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    ReporteClientesUnicos,
    ReporteLlamadasDia,
    ReporteMenuProblemas,
    ReporteTransferencias,
    ReporteTrimestral,
)
from .serializers import (
    ExportarReporteSerializer,
    ReporteClientesUnicosSerializer,
    ReporteLlamadasDiaSerializer,
    ReporteMenuProblemasSerializer,
    ReporteTransferenciasSerializer,
    ReporteTrimestralSerializer,
)
from .services import ReporteIVRService


class ReporteTrimestralViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para reportes trimestrales."""

    queryset = ReporteTrimestral.objects.all()
    serializer_class = ReporteTrimestralSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["trimestre", "anio"]
    search_fields = ["trimestre"]
    ordering_fields = ["anio", "trimestre", "created_at"]
    ordering = ["-anio", "-trimestre"]

    def get_queryset(self):
        """Filtrar queryset usando servicio."""
        queryset = super().get_queryset()

        # Obtener parametros de query
        trimestre = self.request.query_params.get("trimestre")
        anio = self.request.query_params.get("anio")

        if trimestre or anio:
            anio_int = int(anio) if anio else None
            queryset = ReporteIVRService.consultar_trimestral(
                trimestre=trimestre, anio=anio_int
            )

        return queryset


class ReporteTransferenciasViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para reportes de transferencias."""

    queryset = ReporteTransferencias.objects.all()
    serializer_class = ReporteTransferenciasSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["fecha", "centro_origen", "centro_destino"]
    search_fields = ["centro_origen", "centro_destino"]
    ordering_fields = ["fecha", "total_transferencias", "created_at"]
    ordering = ["-fecha"]

    def get_queryset(self):
        """Filtrar queryset usando servicio."""
        queryset = super().get_queryset()

        # Obtener parametros de query
        fecha_inicio = self.request.query_params.get("fecha_inicio")
        fecha_fin = self.request.query_params.get("fecha_fin")
        centro_origen = self.request.query_params.get("centro_origen")
        centro_destino = self.request.query_params.get("centro_destino")

        if any([fecha_inicio, fecha_fin, centro_origen, centro_destino]):
            queryset = ReporteIVRService.consultar_transferencias(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                centro_origen=centro_origen,
                centro_destino=centro_destino,
            )

        return queryset


class ReporteMenuProblemasViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para reportes de menus problematicos."""

    queryset = ReporteMenuProblemas.objects.all()
    serializer_class = ReporteMenuProblemasSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["fecha", "menu_id"]
    search_fields = ["menu_nombre", "menu_id"]
    ordering_fields = ["fecha", "tasa_abandono", "abandonos", "created_at"]
    ordering = ["-tasa_abandono"]

    def get_queryset(self):
        """Filtrar queryset usando servicio."""
        queryset = super().get_queryset()

        # Obtener parametros de query
        fecha_inicio = self.request.query_params.get("fecha_inicio")
        fecha_fin = self.request.query_params.get("fecha_fin")
        menu_id = self.request.query_params.get("menu_id")
        tasa_abandono_minima = self.request.query_params.get("tasa_abandono_minima")

        if any([fecha_inicio, fecha_fin, menu_id, tasa_abandono_minima]):
            tasa_float = (
                float(tasa_abandono_minima) if tasa_abandono_minima else None
            )
            queryset = ReporteIVRService.consultar_menus_problematicos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                menu_id=menu_id,
                tasa_abandono_minima=tasa_float,
            )

        return queryset


class ReporteLlamadasDiaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para reportes de llamadas por dia."""

    queryset = ReporteLlamadasDia.objects.all()
    serializer_class = ReporteLlamadasDiaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["fecha", "hora"]
    search_fields = []
    ordering_fields = ["fecha", "hora", "total_llamadas", "created_at"]
    ordering = ["-fecha", "hora"]

    def get_queryset(self):
        """Filtrar queryset usando servicio."""
        queryset = super().get_queryset()

        # Obtener parametros de query
        fecha_inicio = self.request.query_params.get("fecha_inicio")
        fecha_fin = self.request.query_params.get("fecha_fin")
        hora = self.request.query_params.get("hora")

        if any([fecha_inicio, fecha_fin, hora]):
            hora_int = int(hora) if hora else None
            queryset = ReporteIVRService.consultar_llamadas_dia(
                fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, hora=hora_int
            )

        return queryset


class ReporteClientesUnicosViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para reportes de clientes unicos."""

    queryset = ReporteClientesUnicos.objects.all()
    serializer_class = ReporteClientesUnicosSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["fecha_inicio", "fecha_fin"]
    search_fields = []
    ordering_fields = ["fecha_inicio", "total_clientes_unicos", "created_at"]
    ordering = ["-fecha_inicio"]

    def get_queryset(self):
        """Filtrar queryset usando servicio."""
        queryset = super().get_queryset()

        # Obtener parametros de query
        fecha_inicio = self.request.query_params.get("fecha_inicio")
        fecha_fin = self.request.query_params.get("fecha_fin")

        if fecha_inicio or fecha_fin:
            queryset = ReporteIVRService.consultar_clientes_unicos(
                fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
            )

        return queryset


class ExportarReporteViewSet(viewsets.ViewSet):
    """ViewSet para exportar reportes en diferentes formatos."""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def exportar(self, request):
        """Exportar reporte en el formato especificado."""
        serializer = ExportarReporteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tipo_reporte = serializer.validated_data["tipo_reporte"]
        formato = serializer.validated_data["formato"]
        filtros = serializer.validated_data.get("filtros", {})

        try:
            resultado = ReporteIVRService.exportar_reporte(
                tipo_reporte=tipo_reporte, formato=formato, filtros=filtros
            )
            return Response(resultado, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
