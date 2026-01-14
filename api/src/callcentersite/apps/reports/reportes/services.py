"""Servicios para reportes IVR."""

from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import QuerySet

from .models import (
    ReporteClientesUnicos,
    ReporteLlamadasDia,
    ReporteMenuProblemas,
    ReporteTransferencias,
    ReporteTrimestral,
)


class ReporteIVRService:
    """Servicio para consultar y generar reportes IVR."""

    @staticmethod
    def consultar_trimestral(
        fecha_inicio: date | None = None,
        fecha_fin: date | None = None,
        trimestre: str | None = None,
        anio: int | None = None,
    ) -> QuerySet[ReporteTrimestral]:
        """
        Consultar reportes trimestrales con filtros opcionales.

        Args:
            fecha_inicio: Fecha de inicio para filtrar
            fecha_fin: Fecha de fin para filtrar
            trimestre: Trimestre especifico (Q1, Q2, Q3, Q4)
            anio: Anio especifico

        Returns:
            QuerySet con reportes trimestrales filtrados
        """
        queryset = ReporteTrimestral.objects.all()

        if trimestre:
            queryset = queryset.filter(trimestre=trimestre)

        if anio:
            queryset = queryset.filter(anio=anio)

        return queryset

    @staticmethod
    def consultar_transferencias(
        fecha_inicio: date | None = None,
        fecha_fin: date | None = None,
        centro_origen: str | None = None,
        centro_destino: str | None = None,
    ) -> QuerySet[ReporteTransferencias]:
        """
        Consultar reportes de transferencias entre centros.

        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            centro_origen: Centro de atención origen
            centro_destino: Centro de atención destino

        Returns:
            QuerySet con reportes de transferencias filtrados
        """
        queryset = ReporteTransferencias.objects.all()

        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)

        if centro_origen:
            queryset = queryset.filter(centro_origen=centro_origen)

        if centro_destino:
            queryset = queryset.filter(centro_destino=centro_destino)

        return queryset

    @staticmethod
    def consultar_menus_problematicos(
        fecha_inicio: date | None = None,
        fecha_fin: date | None = None,
        menu_id: str | None = None,
        tasa_abandono_minima: float | None = None,
    ) -> QuerySet[ReporteMenuProblemas]:
        """
        Consultar reportes de menús problemáticos del IVR.

        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            menu_id: ID del menú específico
            tasa_abandono_minima: Filtrar por tasa de abandono mínima

        Returns:
            QuerySet con reportes de menús problemáticos filtrados
        """
        queryset = ReporteMenuProblemas.objects.all()

        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)

        if menu_id:
            queryset = queryset.filter(menu_id=menu_id)

        if tasa_abandono_minima is not None:
            queryset = queryset.filter(tasa_abandono__gte=tasa_abandono_minima)

        return queryset.order_by("-tasa_abandono")

    @staticmethod
    def consultar_llamadas_dia(
        fecha_inicio: date | None = None,
        fecha_fin: date | None = None,
        hora: int | None = None,
    ) -> QuerySet[ReporteLlamadasDia]:
        """
        Consultar reportes de llamadas por día y hora.

        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            hora: Hora específica del día (0-23)

        Returns:
            QuerySet con reportes de llamadas por día filtrados
        """
        queryset = ReporteLlamadasDia.objects.all()

        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)

        if hora is not None:
            queryset = queryset.filter(hora=hora)

        return queryset

    @staticmethod
    def consultar_clientes_unicos(
        fecha_inicio: date | None = None,
        fecha_fin: date | None = None,
    ) -> QuerySet[ReporteClientesUnicos]:
        """
        Consultar reportes de clientes únicos.

        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período

        Returns:
            QuerySet con reportes de clientes únicos filtrados
        """
        queryset = ReporteClientesUnicos.objects.all()

        if fecha_inicio:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(fecha_fin__lte=fecha_fin)

        return queryset

    @staticmethod
    def exportar_reporte(
        tipo_reporte: str,
        formato: str = "csv",
        filtros: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Exportar reporte en el formato especificado.

        Args:
            tipo_reporte: Tipo de reporte (trimestral, transferencias, etc.)
            formato: Formato de exportación (csv, excel, pdf)
            filtros: Diccionario con filtros a aplicar

        Returns:
            Diccionario con información del reporte exportado
        """
        if filtros is None:
            filtros = {}

        # Mapeo de tipos de reporte a métodos de consulta
        metodos_consulta = {
            "trimestral": ReporteIVRService.consultar_trimestral,
            "transferencias": ReporteIVRService.consultar_transferencias,
            "menus_problematicos": ReporteIVRService.consultar_menus_problematicos,
            "llamadas_dia": ReporteIVRService.consultar_llamadas_dia,
            "clientes_unicos": ReporteIVRService.consultar_clientes_unicos,
        }

        if tipo_reporte not in metodos_consulta:
            msg = f"Tipo de reporte '{tipo_reporte}' no válido"
            raise ValueError(msg)

        # Obtener datos según el tipo de reporte
        metodo = metodos_consulta[tipo_reporte]
        datos = metodo(**filtros)

        # Por ahora retornamos metadata del reporte
        # La generación del archivo será implementada en una tarea posterior
        return {
            "tipo_reporte": tipo_reporte,
            "formato": formato,
            "total_registros": datos.count(),
            "filtros": filtros,
            "status": "pending",
        }
