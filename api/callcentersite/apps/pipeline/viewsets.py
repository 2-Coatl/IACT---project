"""
ViewSets para apps/pipeline/.

Django REST Framework ViewSets para API REST.

Movido desde apps/core/ - FASE 2 PARTE 2.
CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions as drf_permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from datetime import date, datetime

from apps.pipeline.models import Center, Service, CallRecord
# REMOVED FASE A DT-002: from apps.access.models import UserServiceAccess

from apps.pipeline.serializers import (
    # Center
    CenterSerializer,
    CenterListSerializer,
    CenterDetailSerializer,
    # Service
    ServiceSerializer,
    ServiceListSerializer,
    ServiceDetailSerializer,
    # CallRecord
    CallRecordSerializer,
    CallRecordListSerializer,
    CallRecordStatsSerializer,
)
# REMOVED FASE A DT-002: UserServiceAccess serializers
# from apps.access.serializers import (
#     UserServiceAccessSerializer,
#     GrantAccessSerializer,
#     BulkGrantAccessSerializer,
#     RevokeAccessSerializer,
# )
from apps.pipeline.filters import (
    CenterFilter,
    ServiceFilter,
    CallRecordFilter,
)
# REMOVED FASE A DT-002: UserServiceAccessFilter
# from apps.access.filters import UserServiceAccessFilter
from apps.pipeline.permissions import (
    IsCenterManager,
    IsServiceManager,
    # HasServiceAccess,  # REMOVED - FASE A DT-002
    CanGrantAccess,
    CanRevokeAccess,
    IsActiveUser,
)
from apps.core.permissions import RequiresFunctionPermission  # ADDED - FASE A DT-002
from apps.pipeline.services import (
    CenterService,
    ServiceService,
    CallRecordService,
)

User = get_user_model()


# ============================================================================
# CENTER VIEWSET
# ============================================================================

class CenterViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Center.
    
    Endpoints:
        GET    /centers/          - Listar centros
        POST   /centers/          - Crear centro
        GET    /centers/{id}/     - Detalle centro
        PUT    /centers/{id}/     - Actualizar centro
        PATCH  /centers/{id}/     - Actualizar parcial
        DELETE /centers/{id}/     - Eliminar centro (soft delete)
        
        POST   /centers/{id}/deactivate/  - Desactivar centro
        POST   /centers/{id}/activate/    - Activar centro
        GET    /centers/{id}/stats/       - Estadísticas centro
    
    Permissions:
        - IsAuthenticated
        - IsActiveUser
        - IsCenterManager (POST/PUT/PATCH/DELETE)
    
    Filters:
        - codigo (exact, icontains)
        - nombre (icontains)
        - activo
        - search
    """
    
    queryset = Center.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CenterFilter
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['nombre', 'codigo', 'created_at']
    ordering = ['nombre']
    
    permission_classes = [
        drf_permissions.IsAuthenticated,
        IsActiveUser,
        IsCenterManager,
    ]
    
    def get_serializer_class(self):
        """
        Retornar serializer según action.
        
        - list: CenterListSerializer (ligero)
        - retrieve: CenterDetailSerializer (nested)
        - default: CenterSerializer
        """
        if self.action == 'list':
            return CenterListSerializer
        elif self.action == 'retrieve':
            return CenterDetailSerializer
        return CenterSerializer
    
    def perform_create(self, serializer):
        """Crear centro usando CenterService."""
        data = serializer.validated_data
        center = CenterService.create_center(data)
        serializer.instance = center
    
    def perform_update(self, serializer):
        """Actualizar centro usando CenterService."""
        center = self.get_object()
        data = serializer.validated_data
        updated_center = CenterService.update_center(center, data)
        serializer.instance = updated_center
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Desactivar centro y todos sus servicios.
        
        POST /centers/{id}/deactivate/
        
        Returns:
            {
                'message': str,
                'services_deactivated': int,
                'user_accesses_affected': int
            }
        """
        center = self.get_object()
        
        if not center.activo:
            return Response(
                {'error': 'Centro ya está inactivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = CenterService.deactivate_center(center, user=request.user)
        
        return Response({
            'message': f"Centro '{center.nombre}' desactivado exitosamente",
            'services_deactivated': result['services_deactivated'],
            'user_accesses_affected': result['user_accesses_affected']
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activar centro.
        
        POST /centers/{id}/activate/
        
        NOTA: Los servicios NO se activan automáticamente.
        """
        center = self.get_object()
        
        if center.activo:
            return Response(
                {'error': 'Centro ya está activo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        activated = CenterService.activate_center(center)
        serializer = self.get_serializer(activated)
        
        return Response({
            'message': f"Centro '{center.nombre}' activado exitosamente",
            'center': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Obtener estadísticas del centro.
        
        GET /centers/{id}/stats/
        
        Returns:
            {
                'total_services': int,
                'active_services': int,
                'inactive_services': int,
                'total_users_with_access': int,
                'is_active': bool
            }
        """
        center = self.get_object()
        stats = CenterService.get_center_stats(center)
        
        return Response(stats)


# ============================================================================
# SERVICE VIEWSET
# ============================================================================

class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Service.
    
    Endpoints:
        GET    /services/          - Listar servicios
        POST   /services/          - Crear servicio
        GET    /services/{id}/     - Detalle servicio
        PUT    /services/{id}/     - Actualizar servicio
        PATCH  /services/{id}/     - Actualizar parcial
        DELETE /services/{id}/     - Eliminar servicio (soft delete)
        
        POST   /services/{id}/deactivate/       - Desactivar servicio
        POST   /services/{id}/activate/         - Activar servicio
        POST   /services/{id}/grant_access/     - Otorgar acceso a usuario
        POST   /services/{id}/bulk_grant_access/ - Otorgar acceso a múltiples usuarios
        POST   /services/{id}/revoke_access/    - Revocar acceso
        GET    /services/{id}/users/            - Usuarios con acceso
    
    Permissions:
        - IsAuthenticated
        - IsActiveUser
        - IsServiceManager (POST/PUT/PATCH/DELETE)
        - CanGrantAccess (grant_access, bulk_grant_access)
        - CanRevokeAccess (revoke_access)
    
    Filters:
        - numero_800 (exact, icontains)
        - nombre (icontains)
        - center (id)
        - center_codigo
        - activo
        - search
    """
    
    queryset = Service.objects.select_related('center').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['numero_800', 'nombre', 'descripcion', 'center__nombre']
    ordering_fields = ['numero_800', 'nombre', 'created_at']
    ordering = ['numero_800']
    
    permission_classes = [
        drf_permissions.IsAuthenticated,
        IsActiveUser,
        IsServiceManager,
    ]
    
    def get_serializer_class(self):
        """Retornar serializer según action."""
        if self.action == 'list':
            return ServiceListSerializer
        elif self.action == 'retrieve':
            return ServiceDetailSerializer
        elif self.action == 'grant_access':
            return GrantAccessSerializer
        elif self.action == 'bulk_grant_access':
            return BulkGrantAccessSerializer
        elif self.action == 'revoke_access':
            return RevokeAccessSerializer
        return ServiceSerializer
    
    def perform_create(self, serializer):
        """Crear servicio usando ServiceService."""
        data = serializer.validated_data
        data['center_id'] = data.pop('center').id
        service = ServiceService.create_service(data)
        serializer.instance = service
    
    def perform_update(self, serializer):
        """Actualizar servicio usando ServiceService."""
        service = self.get_object()
        data = serializer.validated_data
        if 'center' in data:
            data['center_id'] = data.pop('center').id
        updated_service = ServiceService.update_service(service, data)
        serializer.instance = updated_service
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Desactivar servicio.
        
        POST /services/{id}/deactivate/
        """
        service = self.get_object()
        
        if not service.activo:
            return Response(
                {'error': 'Servicio ya está inactivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = ServiceService.deactivate_service(service)
        
        return Response({
            'message': f"Servicio '{service.numero_800}' desactivado exitosamente",
            'user_accesses_affected': result['user_accesses_affected']
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activar servicio.
        
        POST /services/{id}/activate/
        """
        service = self.get_object()
        
        if service.activo:
            return Response(
                {'error': 'Servicio ya está activo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            activated = ServiceService.activate_service(service)
            serializer = self.get_serializer(activated)
            
            return Response({
                'message': f"Servicio '{service.numero_800}' activado exitosamente",
                'service': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[CanGrantAccess])
    def grant_access(self, request, pk=None):
        """
        Otorgar acceso a usuario.
        
        POST /services/{id}/grant_access/
        Body: {'user_id': int, 'reason': str}
        """
        service = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(id=serializer.validated_data['user_id'])
        reason = serializer.validated_data.get('reason', '')
        
        access = ServiceService.grant_access(
            service=service,
            user=user,
            granted_by=request.user,
            reason=reason
        )
        
        return Response({
            'message': f"Acceso otorgado a '{user.username}'",
            'access': UserServiceAccessSerializer(access).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[CanGrantAccess])
    def bulk_grant_access(self, request, pk=None):
        """
        Otorgar acceso a múltiples usuarios.
        
        POST /services/{id}/bulk_grant_access/
        Body: {'user_ids': [int, ...], 'reason': str}
        """
        service = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_ids = serializer.validated_data['user_ids']
        reason = serializer.validated_data.get('reason', '')
        users = User.objects.filter(id__in=user_ids)
        
        accesses, created, reactivated = ServiceService.bulk_grant_access(
            service=service,
            users=users,
            granted_by=request.user,
            reason=reason
        )
        
        return Response({
            'message': f"Acceso otorgado a {len(accesses)} usuarios",
            'created': created,
            'reactivated': reactivated,
            'total': len(accesses)
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[CanRevokeAccess])
    def revoke_access(self, request, pk=None):
        """
        Revocar acceso de usuario.
        
        POST /services/{id}/revoke_access/
        Body: {'user_id': int}
        """
        service = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(id=serializer.validated_data['user_id'])
        
        # Obtener acceso activo
        try:
            access = UserServiceAccess.objects.get(
                user=user,
                service=service,
                is_active=True
            )
        except UserServiceAccess.DoesNotExist:
            return Response(
                {'error': f"Usuario '{user.username}' no tiene acceso activo"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        revoked = ServiceService.revoke_access(access, revoked_by=request.user)
        
        return Response({
            'message': f"Acceso revocado a '{user.username}'",
            'access': UserServiceAccessSerializer(revoked).data
        })
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        Listar usuarios con acceso al servicio.
        
        GET /services/{id}/users/
        Query params: ?include_inactive=true
        """
        service = self.get_object()
        include_inactive = request.query_params.get('include_inactive', 'false').lower() == 'true'
        
        users = ServiceService.get_service_users(service, include_inactive=include_inactive)
        
        return Response({
            'service': service.numero_800,
            'users_count': len(users),
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
                for user in users
            ]
        })


# ============================================================================
# CALLRECORD VIEWSET
# ============================================================================

class CallRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CallRecord.
    
    Endpoints:
        GET    /call-records/          - Listar registros
        POST   /call-records/          - Crear registro
        GET    /call-records/{id}/     - Detalle registro
        PUT    /call-records/{id}/     - Actualizar registro
        PATCH  /call-records/{id}/     - Actualizar parcial
        DELETE /call-records/{id}/     - Eliminar registro (soft delete)
        
        POST   /call-records/bulk_create/  - Crear múltiples registros
        GET    /call-records/stats/         - Estadísticas agregadas
        GET    /call-records/daily_stats/   - Estadísticas diarias
        GET    /call-records/top_callers/   - Top callers
    
    Permissions:
        - IsAuthenticated
        - IsActiveUser
        - RequiresFunctionPermission (RBAC con MOD_Calls)
    
    FASE A DT-002:
        - Removido: HasServiceAccess (UserServiceAccess)
        - Agregado: RequiresFunctionPermission (RBAC puro)
        - Functions: CALL_VIEW, CALL_EDIT, CALL_DELETE, CALL_EXP_CSV, CALL_STATS
    
    Filters:
        - fecha (exact, gte, lte, range)
        - year, month
        - telefono (exact, icontains)
        - servicio_800 (exact, icontains)
        - total_llamadas (gte, lte)
        - has_abandoned
        - high_abandonment
    
    QuerySet Filtering:
        Los usuarios solo ven registros de servicios a los que tienen acceso.
        Superusers ven todos.
    """
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CallRecordFilter
    search_fields = ['telefono', 'servicio_800']
    ordering_fields = ['fecha', 'total_llamadas', 'created_at']
    ordering = ['-fecha', '-created_at']
    
    permission_classes = [
        drf_permissions.IsAuthenticated,
        IsActiveUser,
        RequiresFunctionPermission,  # FASE A DT-002: RBAC puro
    ]
    
    # FASE A DT-002: Function map para RBAC
    function_map = {
        'list': 'CALL_VIEW',
        'retrieve': 'CALL_VIEW',
        'create': 'CALL_EDIT',
        'update': 'CALL_EDIT',
        'partial_update': 'CALL_EDIT',
        'destroy': 'CALL_DELETE',
        'bulk_create': 'CALL_EDIT',
        'stats': 'CALL_STATS',
        'daily_stats': 'CALL_STATS',
        'top_callers': 'CALL_STATS',
    }
    
    def get_queryset(self):
        """
        Filtrar queryset por servicios del usuario.
        
        - Superusers: ven todos los registros
        - Usuarios normales: solo registros de sus servicios
        """
        user = self.request.user
        
        if user.is_superuser:
            return CallRecord.objects.all()
        
        # Obtener servicios del usuario
        user_services = ServiceService.get_user_services(user, include_inactive=False)
        service_800_numbers = user_services.values_list('numero_800', flat=True)
        
        return CallRecord.objects.filter(servicio_800__in=service_800_numbers)
    
    def get_serializer_class(self):
        """Retornar serializer según action."""
        if self.action == 'list':
            return CallRecordListSerializer
        elif self.action == 'bulk_create':
            return CallRecordBulkCreateSerializer
        elif self.action == 'stats':
            return ServiceStatsSerializer
        elif self.action == 'daily_stats':
            return DailyStatsSerializer
        elif self.action == 'top_callers':
            return TopCallerSerializer
        return CallRecordSerializer
    
    def perform_create(self, serializer):
        """Crear registro usando CallRecordService."""
        data = serializer.validated_data
        record = CallRecordService.create_record(data)
        serializer.instance = record
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Crear múltiples registros en bulk.
        
        POST /call-records/bulk_create/
        Body: {'records': [{...}, {...}, ...]}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        
        return Response({
            'message': 'Registros creados exitosamente',
            'created_count': result['created_count'],
            'duplicates_ignored': result['duplicates_ignored']
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtener estadísticas agregadas de servicio.
        
        GET /call-records/stats/
        Query params:
            - service_800 (required)
            - start_date (YYYY-MM-DD, required)
            - end_date (YYYY-MM-DD, required)
        """
        service_800 = request.query_params.get('service_800')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not all([service_800, start_date, end_date]):
            return Response(
                {'error': 'service_800, start_date y end_date son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stats = CallRecordService.get_service_stats(service_800, start, end)
        serializer = self.get_serializer(stats)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def daily_stats(self, request):
        """
        Obtener estadísticas diarias.
        
        GET /call-records/daily_stats/
        Query params:
            - fecha (YYYY-MM-DD, required)
            - service_800 (optional)
        """
        fecha_str = request.query_params.get('fecha')
        service_800 = request.query_params.get('service_800')
        
        if not fecha_str:
            return Response(
                {'error': 'fecha es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stats = CallRecordService.get_daily_stats(fecha, service_800)
        serializer = self.get_serializer(stats)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_callers(self, request):
        """
        Obtener top callers.
        
        GET /call-records/top_callers/
        Query params:
            - service_800 (required)
            - start_date (YYYY-MM-DD, required)
            - end_date (YYYY-MM-DD, required)
            - limit (int, optional, default=10)
        """
        service_800 = request.query_params.get('service_800')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit = int(request.query_params.get('limit', 10))
        
        if not all([service_800, start_date, end_date]):
            return Response(
                {'error': 'service_800, start_date y end_date son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        top_callers = CallRecordService.get_top_callers(service_800, start, end, limit)
        serializer = self.get_serializer(top_callers, many=True)
        
        return Response({
            'service_800': service_800,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit,
            'results': serializer.data
        })


# ============================================================================
# USERSERVICEACCESS VIEWSET
# ============================================================================

class UserServiceAccessViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para UserServiceAccess.
    
    NOTA: Este ViewSet es ReadOnly.
    Para crear/modificar accesos, usar ServiceViewSet actions:
        - POST /services/{id}/grant_access/
        - POST /services/{id}/bulk_grant_access/
        - POST /services/{id}/revoke_access/
    
    Endpoints:
        GET    /user-service-accesses/      - Listar accesos
        GET    /user-service-accesses/{id}/ - Detalle acceso
    
    Permissions:
        - IsAuthenticated
        - IsActiveUser
    
    Filters:
        - user (id)
        - user_username (icontains)
        - service (id)
        - service_numero (icontains)
        - is_active
        - granted_at (gte, lte)
    """
    
    queryset = UserServiceAccess.objects.select_related(
        'user',
        'service',
        'granted_by',
        'revoked_by'
    ).all()
    serializer_class = UserServiceAccessSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserServiceAccessFilter
    search_fields = ['user__username', 'service__numero_800']
    ordering_fields = ['granted_at', 'revoked_at']
    ordering = ['-granted_at']
    
    permission_classes = [
        drf_permissions.IsAuthenticated,
        IsActiveUser,
    ]


# ============================================================================
# TOTAL VIEWSETS: 4
# 
# ViewSets:
#   - CenterViewSet (ModelViewSet)
#   - ServiceViewSet (ModelViewSet)
#   - CallRecordViewSet (ModelViewSet)
#   - UserServiceAccessViewSet (ReadOnlyModelViewSet)
# 
# Total Actions: 16
#   - Standard CRUD: 20 (5 per ViewSet x 4)
#   - Custom Actions: 16
# 
# Características:
#   ✅ DRF ViewSets completos
#   ✅ CRUD operations
#   ✅ Custom actions (@action)
#   ✅ Filters (django-filter)
#   ✅ Search & Ordering
#   ✅ Permissions granulares
#   ✅ get_queryset() personalizado
#   ✅ get_serializer_class() dinámico
#   ✅ Service Layer integration
#   ✅ Bulk operations
#   ✅ Statistics endpoints
#   ✅ CLEAN_CODE v3.0.1
# ============================================================================
