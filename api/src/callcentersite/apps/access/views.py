"""
Views y ViewSets para el sistema de permisos granular.

Sistema de Permisos Granular - Prioridad 2: API Layer
REF: ADR-012-sistema-permisos-sin-roles-jerarquicos.md
"""

from __future__ import annotations

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.access import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from callcentersite.apps.access.models import (
    Funcion,
    Capacidad,
    FuncionCapacidad,
    GrupoPermisos,
    GrupoCapacidad,
    UsuarioGrupo,
    PermisoExcepcional,
    AuditoriaPermiso,
)
from callcentersite.apps.access.serializers import (
    FuncionSerializer,
    CapacidadSerializer,
    FuncionCapacidadSerializer,
    GrupoPermisosSerializer,
    GrupoPermisosDetailSerializer,
    GrupoCapacidadSerializer,
    UsuarioGrupoSerializer,
    UsuarioGrupoCreateSerializer,
    PermisoExcepcionalSerializer,
    PermisoExcepcionalCreateSerializer,
    AuditoriaPermisoSerializer,
)
from callcentersite.apps.access.services import PermisoService


class FuncionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Funciones del sistema.

    Operaciones CRUD para funciones (dashboards, usuarios, llamadas, etc).
    """

    queryset = Funcion.objects.all()
    serializer_class = FuncionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['dominio', 'categoria', 'activa']
    search_fields = ['nombre', 'nombre_completo', 'descripcion']
    ordering_fields = ['orden_menu', 'nombre', 'created_at']
    ordering = ['orden_menu', 'nombre']


class CapacidadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Capacidades.

    Operaciones CRUD para capacidades atomicas.
    """

    queryset = Capacidad.objects.all()
    serializer_class = CapacidadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['dominio', 'recurso', 'accion', 'nivel_sensibilidad', 'activa']
    search_fields = ['nombre_completo', 'descripcion']
    ordering_fields = ['dominio', 'recurso', 'accion', 'created_at']
    ordering = ['dominio', 'recurso', 'accion']


class FuncionCapacidadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para relaciones Funcion-Capacidad.

    Gestiona que capacidades estan vinculadas a que funciones.
    """

    queryset = FuncionCapacidad.objects.select_related('funcion', 'capacidad').all()
    serializer_class = FuncionCapacidadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['funcion', 'capacidad', 'requerida']
    ordering = ['funcion__orden_menu', 'funcion__nombre']


class GrupoPermisosViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Grupos de Permisos.

    Gestiona grupos funcionales (NO roles jerarquicos).
    """

    queryset = GrupoPermisos.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo_acceso', 'activo']
    search_fields = ['codigo', 'nombre_display', 'descripcion']
    ordering_fields = ['nombre_display', 'created_at']
    ordering = ['nombre_display']

    def get_serializer_class(self):
        """Usa serializer detallado para retrieve."""
        if self.action == 'retrieve':
            return GrupoPermisosDetailSerializer
        return GrupoPermisosSerializer

    @action(detail=True, methods=['get'])
    def capacidades(self, request, pk=None):
        """
        Endpoint para obtener capacidades de un grupo.

        GET /api/access/grupos/{id}/capacidades/
        """
        grupo = self.get_object()
        grupo_caps = grupo.grupo_capacidades.select_related('capacidad').all()

        capacidades_data = [
            CapacidadSerializer(gc.capacidad).data
            for gc in grupo_caps
        ]

        return Response({'capacidades': capacidades_data})

    @action(detail=True, methods=['post'])
    def agregar_capacidad(self, request, pk=None):
        """
        Agrega capacidad a grupo.

        POST /api/access/grupos/{id}/agregar_capacidad/
        Body: {"capacidad_id": 123}
        """
        grupo = self.get_object()
        capacidad_id = request.data.get('capacidad_id')

        if not capacidad_id:
            return Response(
                {'error': 'capacidad_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            capacidad = Capacidad.objects.get(id=capacidad_id)
        except Capacidad.DoesNotExist:
            return Response(
                {'error': 'Capacidad no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear vinculacion si no existe
        vinc, created = GrupoCapacidad.objects.get_or_create(
            grupo=grupo,
            capacidad=capacidad
        )

        if created:
            return Response(
                {'message': 'Capacidad agregada exitosamente'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Capacidad ya existe en el grupo'},
                status=status.HTTP_200_OK
            )


class GrupoCapacidadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para relaciones Grupo-Capacidad.

    Gestiona que capacidades estan asignadas a que grupos.
    """

    queryset = GrupoCapacidad.objects.select_related('grupo', 'capacidad').all()
    serializer_class = GrupoCapacidadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['grupo', 'capacidad']
    ordering = ['grupo__nombre_display', 'capacidad__nombre_completo']


class UsuarioGrupoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para asignaciones Usuario-Grupo.

    Gestiona a que grupos pertenecen los usuarios.
    """

    queryset = UsuarioGrupo.objects.select_related('usuario', 'grupo', 'asignado_por').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['usuario', 'grupo', 'activo']
    ordering = ['-fecha_asignacion']

    def get_serializer_class(self):
        """Usa serializer de creacion para POST."""
        if self.action == 'create':
            return UsuarioGrupoCreateSerializer
        return UsuarioGrupoSerializer

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """
        Desactiva asignacion de usuario a grupo.

        POST /api/access/usuarios-grupos/{id}/desactivar/
        """
        asignacion = self.get_object()
        asignacion.activo = False
        asignacion.save()

        return Response({'message': 'Asignacion desactivada'})


class PermisoExcepcionalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Permisos Excepcionales.

    Gestiona concesiones y revocaciones temporales de capacidades.
    """

    queryset = PermisoExcepcional.objects.select_related(
        'usuario', 'capacidad', 'autorizado_por'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['usuario', 'capacidad', 'tipo', 'activo']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Usa serializer de creacion para POST."""
        if self.action == 'create':
            return PermisoExcepcionalCreateSerializer
        return PermisoExcepcionalSerializer


class AuditoriaPermisoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Auditoria de Permisos (solo lectura).

    Consulta logs de auditoria de accesos a recursos protegidos.
    """

    queryset = AuditoriaPermiso.objects.select_related('usuario').all()
    serializer_class = AuditoriaPermisoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['usuario', 'capacidad', 'accion_realizada']
    ordering = ['-timestamp']


class MisCapacidadesView(APIView):
    """
    Endpoint personalizado para obtener capacidades del usuario actual.

    GET /api/access/mis-capacidades/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna capacidades del usuario autenticado."""
        capacidades = PermisoService.obtener_capacidades_usuario(
            usuario_id=request.user.id
        )

        return Response({
            'usuario_id': request.user.id,
            'username': request.user.username,
            'capacidades': capacidades
        })


class MisFuncionesView(APIView):
    """
    Endpoint personalizado para obtener funciones accesibles del usuario.

    GET /api/access/mis-funciones/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna funciones accesibles para el usuario autenticado."""
        funciones = PermisoService.obtener_funciones_accesibles(
            usuario_id=request.user.id
        )

        return Response({
            'usuario_id': request.user.id,
            'username': request.user.username,
            'funciones': funciones
        })


class VerificarPermisoView(APIView):
    """
    Endpoint para verificar si usuario tiene una capacidad especifica.

    POST /api/access/verificar-permiso/
    Body: {"capacidad": "sistema.operaciones.llamadas.ver"}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Verifica si usuario tiene la capacidad solicitada."""
        capacidad = request.data.get('capacidad')

        if not capacidad:
            return Response(
                {'error': 'Campo "capacidad" requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tiene_permiso = PermisoService.usuario_tiene_permiso(
            usuario_id=request.user.id,
            capacidad_requerida=capacidad
        )

        return Response({
            'usuario_id': request.user.id,
            'capacidad': capacidad,
            'tiene_permiso': tiene_permiso
        })
