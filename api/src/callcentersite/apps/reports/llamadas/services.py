"""
Servicios de negocio para el módulo de Llamadas.

Implementa casos de uso del call center:
- UC-010: Registrar llamada entrante
- UC-011: Finalizar llamada
- UC-012: Consultar historial de llamadas

Integrado con sistema de permisos granular.
"""

from typing import List, Optional
from datetime import datetime
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

from .models import Llamada, EstadoLlamada, TipoLlamada
from callcentersite.apps.permissions.services import PermisoService

User = get_user_model()


class LlamadaService:
    """
    Servicio principal para gestión de llamadas.

    Implementa lógica de negocio con validación de permisos.
    """

    @staticmethod
    def registrar_llamada_entrante(
        agente_id: int,
        numero_telefono: str,
        tipo_id: int,
        cliente_nombre: Optional[str] = None,
        cliente_email: Optional[str] = None,
        cliente_id: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> Llamada:
        """
        UC-010: Registrar llamada entrante.

        Args:
            agente_id: ID del agente que atiende
            numero_telefono: Número telefónico
            tipo_id: ID del tipo de llamada
            cliente_nombre: Nombre del cliente (opcional)
            cliente_email: Email del cliente (opcional)
            cliente_id: ID del cliente si existe (opcional)
            metadata: Datos adicionales JSON (opcional)

        Returns:
            Objeto Llamada creado

        Raises:
            PermissionDenied: Si agente no tiene permiso
            ObjectDoesNotExist: Si tipo no existe

        Ejemplo:
            >>> llamada = LlamadaService.registrar_llamada_entrante(
            ...     agente_id=1,
            ...     numero_telefono='+52-555-1234-567',
            ...     tipo_id=1,
            ...     cliente_nombre='Juan Pérez'
            ... )
        """
        # 1. Validar permisos
        tiene_permiso = PermisoService.usuario_tiene_permiso(
            usuario_id=agente_id,
            capacidad_requerida='sistema.operaciones.llamadas.registrar'
        )

        if not tiene_permiso:
            raise PermissionDenied(
                f'Usuario {agente_id} sin permiso para registrar llamadas'
            )

        # 2. Obtener agente y tipo
        agente = User.objects.get(id=agente_id)
        tipo = TipoLlamada.objects.get(id=tipo_id, activo=True)

        # 3. Obtener estado inicial "en_curso"
        try:
            estado_en_curso = EstadoLlamada.objects.get(
                codigo='en_curso',
                activo=True
            )
        except EstadoLlamada.DoesNotExist:
            # Crear estado si no existe (para desarrollo)
            estado_en_curso = EstadoLlamada.objects.create(
                codigo='en_curso',
                nombre='En Curso',
                descripcion='Llamada en progreso',
                es_final=False,
                activo=True,
            )

        # 4. Crear llamada
        llamada = Llamada.objects.create(
            numero_telefono=numero_telefono,
            tipo=tipo,
            estado=estado_en_curso,
            agente=agente,
            cliente_nombre=cliente_nombre or '',
            cliente_email=cliente_email or '',
            cliente_id=cliente_id,
            metadata=metadata or {},
            fecha_inicio=timezone.now(),
        )

        # 5. Registrar en auditoría
        PermisoService.registrar_acceso(
            usuario_id=agente_id,
            capacidad='sistema.operaciones.llamadas.registrar',
            accion='llamada_registrada',
            recurso_id=llamada.codigo,
            ip_address='',  # En producción se obtiene del request
            user_agent='',  # En producción se obtiene del request
            metadata={
                'llamada_id': llamada.id,
                'numero_telefono': numero_telefono,
                'tipo': tipo.codigo,
            }
        )

        return llamada

    @staticmethod
    def finalizar_llamada(
        llamada_id: int,
        agente_id: int,
        notas: Optional[str] = None,
        resolucion: Optional[str] = None,
    ) -> Llamada:
        """
        UC-011: Finalizar llamada.

        Args:
            llamada_id: ID de la llamada a finalizar
            agente_id: ID del agente que finaliza
            notas: Notas adicionales (opcional)
            resolucion: Descripción de resolución (opcional)

        Returns:
            Objeto Llamada actualizado

        Raises:
            PermissionDenied: Si agente no tiene permiso
            ObjectDoesNotExist: Si llamada no existe

        Ejemplo:
            >>> llamada = LlamadaService.finalizar_llamada(
            ...     llamada_id=123,
            ...     agente_id=1,
            ...     notas='Cliente satisfecho',
            ...     resolucion='Problema resuelto'
            ... )
        """
        # 1. Validar permisos
        tiene_permiso = PermisoService.usuario_tiene_permiso(
            usuario_id=agente_id,
            capacidad_requerida='sistema.operaciones.llamadas.finalizar'
        )

        if not tiene_permiso:
            raise PermissionDenied(
                f'Usuario {agente_id} sin permiso para finalizar llamadas'
            )

        # 2. Obtener llamada
        llamada = Llamada.objects.select_related('estado', 'tipo', 'agente').get(
            id=llamada_id
        )

        # 3. Validar que no esté ya finalizada
        if llamada.estado.es_final:
            raise ValueError(f'Llamada {llamada.codigo} ya está finalizada')

        # 4. Obtener estado "finalizada"
        try:
            estado_finalizada = EstadoLlamada.objects.get(
                codigo='finalizada',
                activo=True
            )
        except EstadoLlamada.DoesNotExist:
            # Crear estado si no existe
            estado_finalizada = EstadoLlamada.objects.create(
                codigo='finalizada',
                nombre='Finalizada',
                descripcion='Llamada finalizada exitosamente',
                es_final=True,
                activo=True,
            )

        # 5. Actualizar llamada
        llamada.estado = estado_finalizada
        llamada.fecha_fin = timezone.now()

        if notas:
            llamada.notas = notas

        if resolucion:
            if not llamada.metadata:
                llamada.metadata = {}
            llamada.metadata['resolucion'] = resolucion

        # Calcular duración en segundos
        duracion = (llamada.fecha_fin - llamada.fecha_inicio).total_seconds()
        llamada.metadata['duracion_segundos'] = int(duracion)

        llamada.save()

        # 6. Registrar en auditoría
        PermisoService.registrar_acceso(
            usuario_id=agente_id,
            capacidad='sistema.operaciones.llamadas.finalizar',
            accion='llamada_finalizada',
            recurso_id=llamada.codigo,
            ip_address='',  # En producción se obtiene del request
            user_agent='',  # En producción se obtiene del request
            metadata={
                'llamada_id': llamada.id,
                'duracion_segundos': int(duracion),
                'estado_final': estado_finalizada.codigo,
            }
        )

        return llamada

    @staticmethod
    def consultar_historial(
        agente_id: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado_codigo: Optional[str] = None,
        tipo_codigo: Optional[str] = None,
        numero_telefono: Optional[str] = None,
        limit: int = 100,
    ) -> List[Llamada]:
        """
        UC-012: Consultar historial de llamadas.

        Args:
            agente_id: Filtrar por agente (opcional)
            fecha_desde: Fecha inicio del rango (opcional)
            fecha_hasta: Fecha fin del rango (opcional)
            estado_codigo: Filtrar por estado (opcional)
            tipo_codigo: Filtrar por tipo (opcional)
            numero_telefono: Filtrar por teléfono (opcional)
            limit: Límite de resultados (default 100)

        Returns:
            Lista de objetos Llamada

        Ejemplo:
            >>> llamadas = LlamadaService.consultar_historial(
            ...     agente_id=1,
            ...     fecha_desde=datetime(2025, 11, 1),
            ...     limit=50
            ... )
        """
        # Construir query
        queryset = Llamada.objects.select_related(
            'agente', 'estado', 'tipo'
        ).all()

        # Aplicar filtros
        if agente_id:
            queryset = queryset.filter(agente_id=agente_id)

        if fecha_desde:
            queryset = queryset.filter(fecha_inicio__gte=fecha_desde)

        if fecha_hasta:
            queryset = queryset.filter(fecha_inicio__lte=fecha_hasta)

        if estado_codigo:
            queryset = queryset.filter(estado__codigo=estado_codigo)

        if tipo_codigo:
            queryset = queryset.filter(tipo__codigo=tipo_codigo)

        if numero_telefono:
            queryset = queryset.filter(
                numero_telefono__icontains=numero_telefono
            )

        # Ordenar por fecha más reciente primero
        queryset = queryset.order_by('-fecha_inicio')

        # Limitar resultados
        return list(queryset[:limit])

    @staticmethod
    def obtener_estadisticas_agente(
        agente_id: int,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> dict:
        """
        Obtener estadísticas de llamadas de un agente.

        Args:
            agente_id: ID del agente
            fecha_desde: Fecha inicio (opcional, default: hoy)
            fecha_hasta: Fecha fin (opcional, default: ahora)

        Returns:
            Dict con estadísticas:
            - total_llamadas
            - promedio_duracion
            - llamadas_finalizadas
            - llamadas_en_curso

        Ejemplo:
            >>> stats = LlamadaService.obtener_estadisticas_agente(agente_id=1)
            >>> print(stats['total_llamadas'])
            45
        """
        from django.db.models import Avg, Count, Q

        # Filtros base
        filters = Q(agente_id=agente_id)

        if fecha_desde:
            filters &= Q(fecha_inicio__gte=fecha_desde)

        if fecha_hasta:
            filters &= Q(fecha_inicio__lte=fecha_hasta)

        # Obtener llamadas
        llamadas = Llamada.objects.filter(filters)

        # Calcular estadísticas
        total = llamadas.count()

        finalizadas = llamadas.filter(estado__es_final=True).count()

        en_curso = llamadas.filter(estado__es_final=False).count()

        # Calcular duración promedio de llamadas finalizadas
        llamadas_con_duracion = llamadas.filter(
            fecha_fin__isnull=False
        )

        if llamadas_con_duracion.exists():
            duraciones = [
                (ll.fecha_fin - ll.fecha_inicio).total_seconds()
                for ll in llamadas_con_duracion
            ]
            promedio_duracion = sum(duraciones) / len(duraciones)
        else:
            promedio_duracion = 0

        return {
            'total_llamadas': total,
            'llamadas_finalizadas': finalizadas,
            'llamadas_en_curso': en_curso,
            'promedio_duracion_segundos': int(promedio_duracion),
            'promedio_duracion_minutos': round(promedio_duracion / 60, 2),
        }
