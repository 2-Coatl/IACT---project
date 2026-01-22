"""
Serializers DRF para apps/pipeline/.

Django REST Framework serializers para Center, Service, CallRecord.

Movido desde apps/core/ - FASE 2 PARTE 2.
CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.pipeline.models import Center, Service, CallRecord
# TODO PARTE 7: Mover UserServiceAccess a apps.access
from apps.access.models import UserServiceAccess

User = get_user_model()


# ============================================================================
# CENTER SERIALIZERS
# ============================================================================

class CenterSerializer(serializers.ModelSerializer):
    """
    Serializer para Center.
    
    Campos adicionales:
        - active_services_count (read-only): Cantidad de servicios activos
        - total_services_count (read-only): Total de servicios
    """
    
    active_services_count = serializers.SerializerMethodField()
    total_services_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Center
        fields = [
            'id',
            'nombre',
            'codigo',
            'descripcion',
            'direccion',
            'activo',
            'active_services_count',
            'total_services_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_active_services_count(self, obj):
        """Cantidad de servicios activos del centro."""
        return obj.get_active_services_count()
    
    def get_total_services_count(self, obj):
        """Total de servicios del centro."""
        return obj.services.count()
    
    def validate_codigo(self, value):
        """Validar que código sea único."""
        instance = self.instance
        
        # Si es update y código no cambió, OK
        if instance and instance.codigo == value:
            return value
        
        # Verificar si ya existe
        if Center.objects.filter(codigo=value).exists():
            raise serializers.ValidationError(
                f"Ya existe un centro con código '{value}'"
            )
        
        return value


class CenterListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de centros.
    
    Solo campos esenciales para optimizar queries.
    """
    
    active_services_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Center
        fields = [
            'id',
            'nombre',
            'codigo',
            'activo',
            'active_services_count',
        ]


class CenterDetailSerializer(CenterSerializer):
    """
    Serializer detallado para Center.
    
    Incluye lista de servicios anidados.
    """
    
    services = serializers.SerializerMethodField()
    
    class Meta(CenterSerializer.Meta):
        fields = CenterSerializer.Meta.fields + ['services']
    
    def get_services(self, obj):
        """Lista de servicios del centro."""
        services = obj.services.all()[:20]  # Limitar a 20
        return ServiceListSerializer(services, many=True).data


# ============================================================================
# SERVICE SERIALIZERS
# ============================================================================

class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer para Service.
    
    Campos adicionales:
        - center_name (read-only): Nombre del centro
        - users_with_access_count (read-only): Cantidad de usuarios con acceso
    """
    
    center_name = serializers.CharField(source='center.nombre', read_only=True)
    users_with_access_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id',
            'numero_800',
            'nombre',
            'descripcion',
            'center',
            'center_name',
            'activo',
            'users_with_access_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_users_with_access_count(self, obj):
        """Cantidad de usuarios con acceso al servicio."""
        return obj.get_users_with_access_count()
    
    def validate_numero_800(self, value):
        """Validar que número 800 sea único."""
        instance = self.instance
        
        # Si es update y número no cambió, OK
        if instance and instance.numero_800 == value:
            return value
        
        # Verificar si ya existe
        if Service.objects.filter(numero_800=value).exists():
            raise serializers.ValidationError(
                f"Ya existe un servicio con número '{value}'"
            )
        
        return value
    
    def validate_center(self, value):
        """Validar que centro esté activo."""
        if not value.activo:
            raise serializers.ValidationError(
                f"Centro '{value.nombre}' está inactivo"
            )
        return value


class ServiceListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de servicios.
    """
    
    center_name = serializers.CharField(source='center.nombre', read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id',
            'numero_800',
            'nombre',
            'center_name',
            'activo',
        ]


class ServiceDetailSerializer(ServiceSerializer):
    """
    Serializer detallado para Service.
    
    Incluye información del centro.
    """
    
    center_detail = CenterListSerializer(source='center', read_only=True)
    
    class Meta(ServiceSerializer.Meta):
        fields = ServiceSerializer.Meta.fields + ['center_detail']


# ============================================================================
# CALLRECORD SERIALIZERS
# ============================================================================

class CallRecordSerializer(serializers.ModelSerializer):
    """
    Serializer para CallRecord.
    
    Campos adicionales calculados:
        - answer_rate (read-only): Tasa de respuesta %
        - abandonment_rate (read-only): Tasa de abandono %
        - avg_duration_seconds (read-only): Duración promedio
    """
    
    answer_rate = serializers.SerializerMethodField()
    abandonment_rate = serializers.SerializerMethodField()
    avg_duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = CallRecord
        fields = [
            'id',
            'fecha',
            'telefono',
            'servicio_800',
            'total_llamadas',
            'llamadas_contestadas',
            'llamadas_abandonadas',
            'duracion_total_segundos',
            'answer_rate',
            'abandonment_rate',
            'avg_duration_seconds',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_answer_rate(self, obj):
        """Tasa de respuesta en porcentaje."""
        return float(obj.answer_rate())
    
    def get_abandonment_rate(self, obj):
        """Tasa de abandono en porcentaje."""
        return float(obj.abandonment_rate())
    
    def get_avg_duration_seconds(self, obj):
        """Duración promedio por llamada contestada."""
        return float(obj.avg_duration_seconds())
    
    def validate(self, data):
        """
        Validar consistencia de datos.
        
        Valida que suma de contestadas + abandonadas <= total.
        """
        total = data.get('total_llamadas', 0)
        contestadas = data.get('llamadas_contestadas', 0)
        abandonadas = data.get('llamadas_abandonadas', 0)
        
        if contestadas + abandonadas > total:
            raise serializers.ValidationError(
                'La suma de llamadas contestadas y abandonadas no puede '
                'ser mayor al total de llamadas'
            )
        
        return data


class CallRecordListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de registros.
    """
    
    answer_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = CallRecord
        fields = [
            'id',
            'fecha',
            'telefono',
            'servicio_800',
            'total_llamadas',
            'llamadas_contestadas',
            'llamadas_abandonadas',
            'answer_rate',
        ]
    
    def get_answer_rate(self, obj):
        return float(obj.answer_rate())


class CallRecordStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas agregadas de CallRecord.
    
    No vinculado a modelo, usado para stats endpoints.
    """
    
    total_calls = serializers.IntegerField()
    total_answered = serializers.IntegerField()
    total_abandoned = serializers.IntegerField()
    answer_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    abandonment_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    unique_callers = serializers.IntegerField()
    avg_duration_seconds = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_duration_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    days_with_data = serializers.IntegerField()


# ============================================================================
# NOTA: UserServiceAccess Serializers MOVIDOS a apps/access/serializers.py
# 
# Los siguientes serializers fueron movidos a apps.access (refactor organizacional):
#   - UserServiceAccessSerializer
#   - UserServiceAccessListSerializer
#   - GrantAccessSerializer
#   - BulkGrantAccessSerializer
#   - RevokeAccessSerializer
# 
# Razón: UserServiceAccess es parte del sistema RBAC (apps/access)
# ============================================================================


# ============================================================================
# TOTAL SERIALIZERS: 12 (pipeline only)
# 
# Center (3):
#   - CenterSerializer
#   - CenterListSerializer
#   - CenterDetailSerializer
# 
# Service (3):
#   - ServiceSerializer
#   - ServiceListSerializer
#   - ServiceDetailSerializer
# 
# CallRecord (3):
#   - CallRecordSerializer
#   - CallRecordListSerializer
#   - CallRecordStatsSerializer
# 
# Características:
#   ✅ Serializers list/detail separados (optimización)
#   ✅ Campos calculados (SerializerMethodField)
#   ✅ Validaciones personalizadas
#   ✅ Serializers para acciones custom
#   ✅ Type hints implícitos (DRF)
#   ✅ Docstrings completos
#   ✅ CLEAN_CODE v3.0.1
# ============================================================================
