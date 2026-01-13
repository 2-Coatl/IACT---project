"""
Views para Llamadas.

Sistema de Permisos Granular - Prioridad 3: Módulo Operativo Llamadas
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from callcentersite.apps.llamadas.models import (
    EstadoLlamada,
    TipoLlamada,
    Llamada,
    LlamadaTranscripcion,
    LlamadaGrabacion,
)
from callcentersite.apps.llamadas.serializers import (
    EstadoLlamadaSerializer,
    TipoLlamadaSerializer,
    LlamadaSerializer,
    LlamadaTranscripcionSerializer,
    LlamadaGrabacionSerializer,
)
from callcentersite.apps.permissions.middleware import verificar_permiso


class EstadoLlamadaViewSet(viewsets.ModelViewSet):
    """ViewSet para EstadoLlamada."""

    queryset = EstadoLlamada.objects.all()
    serializer_class = EstadoLlamadaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['activo', 'es_final']
    search_fields = ['codigo', 'nombre']


class TipoLlamadaViewSet(viewsets.ModelViewSet):
    """ViewSet para TipoLlamada."""

    queryset = TipoLlamada.objects.all()
    serializer_class = TipoLlamadaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['activo']
    search_fields = ['codigo', 'nombre']


class LlamadaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Llamadas.

    Requiere permisos:
    - ver: sistema.operaciones.llamadas.ver
    - realizar: sistema.operaciones.llamadas.realizar
    """

    queryset = Llamada.objects.select_related('tipo', 'estado', 'agente').all()
    serializer_class = LlamadaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['estado', 'tipo', 'agente', 'cliente_id']
    search_fields = ['codigo', 'numero_telefono', 'cliente_nombre']
    ordering_fields = ['fecha_inicio', 'fecha_fin']
    ordering = ['-fecha_inicio']

    @verificar_permiso("sistema.operaciones.llamadas.ver")
    def list(self, request, *args, **kwargs):
        """Listar llamadas requiere permiso ver."""
        return super().list(request, *args, **kwargs)

    @verificar_permiso("sistema.operaciones.llamadas.ver")
    def retrieve(self, request, *args, **kwargs):
        """Ver detalle requiere permiso ver."""
        return super().retrieve(request, *args, **kwargs)

    @verificar_permiso("sistema.operaciones.llamadas.realizar")
    def create(self, request, *args, **kwargs):
        """Crear llamada requiere permiso realizar."""
        return super().create(request, *args, **kwargs)

    @verificar_permiso("sistema.operaciones.llamadas.realizar")
    def update(self, request, *args, **kwargs):
        """Actualizar llamada requiere permiso realizar."""
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    @verificar_permiso("sistema.operaciones.llamadas.realizar")
    def finalizar(self, request, pk=None):
        """Finalizar llamada."""
        from django.utils import timezone

        llamada = self.get_object()

        if llamada.fecha_fin:
            return Response(
                {'error': 'Llamada ya finalizada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        estado_completada = EstadoLlamada.objects.filter(
            codigo='COMPLETADA',
            es_final=True
        ).first()

        if not estado_completada:
            return Response(
                {'error': 'Estado COMPLETADA no existe'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        llamada.fecha_fin = timezone.now()
        llamada.estado = estado_completada
        llamada.save()

        serializer = self.get_serializer(llamada)
        return Response(serializer.data)


class LlamadaTranscripcionViewSet(viewsets.ModelViewSet):
    """ViewSet para LlamadaTranscripcion."""

    queryset = LlamadaTranscripcion.objects.select_related('llamada').all()
    serializer_class = LlamadaTranscripcionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['llamada', 'hablante']
    ordering = ['timestamp_inicio']


class LlamadaGrabacionViewSet(viewsets.ModelViewSet):
    """ViewSet para LlamadaGrabacion."""

    queryset = LlamadaGrabacion.objects.select_related('llamada').all()
    serializer_class = LlamadaGrabacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['llamada', 'formato']
