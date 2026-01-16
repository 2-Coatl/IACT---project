"""
Serializers para AuditLog.
"""
from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer para AuditLog (readonly).
    
    Muestra información completa del log de auditoría.
    """
    
    user_username = serializers.CharField(
        source='user.username',
        read_only=True,
        allow_null=True
    )
    user_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'user_username',
            'user_full_name',
            'action',
            'resource',
            'result',
            'timestamp',
            'ip_address',
            'user_agent',
            'details',
        ]
        read_only_fields = fields  # Todos readonly (inmutable)
    
    def get_user_full_name(self, obj):
        """Obtener nombre completo del usuario."""
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return None


class AuditLogSummarySerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listados.
    
    Omite detalles pesados como user_agent.
    """
    
    user_username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user_username',
            'action',
            'resource',
            'result',
            'timestamp',
            'ip_address',
        ]
        read_only_fields = fields
