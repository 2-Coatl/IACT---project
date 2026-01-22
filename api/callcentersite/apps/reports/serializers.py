"""
Serializers para app reports.

CNST-007 compliance: validación de límites en exportación.
"""
from rest_framework import serializers
from .models import Report, ExportJob
from django.contrib.auth import get_user_model

User = get_user_model()


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer para Report.
    
    Incluye:
    - Datos básicos del reporte
    - Usuario creador (read-only)
    - Validación de filtros JSON
    """
    
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    report_type_display = serializers.CharField(
        source='get_report_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Report
        fields = [
            'id',
            'name',
            'report_type',
            'report_type_display',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at',
            'filters',
            'total_records',
            'status',
            'status_display',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_at',
            'updated_at',
            'total_records',
            'status',
        ]
    
    def validate_filters(self, value):
        """
        Validar que filters sea un dict válido.
        
        Args:
            value: Filtros en formato JSON
            
        Returns:
            dict: Filtros validados
            
        Raises:
            ValidationError: Si filters no es dict
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Filters debe ser un objeto JSON válido"
            )
        return value


class ExportJobSerializer(serializers.ModelSerializer):
    """
    Serializer para ExportJob.
    
    CNST-007: Valida límite de 100K registros.
    
    Incluye:
    - Datos del job
    - Progreso de exportación
    - Validación CNST-007
    """
    
    # Constante CNST-007
    MAX_EXPORT_SIZE = 100000
    
    report_name = serializers.CharField(
        source='report.name',
        read_only=True
    )
    format_display = serializers.CharField(
        source='get_format_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = ExportJob
        fields = [
            'id',
            'report',
            'report_name',
            'format',
            'format_display',
            'file_path',
            'total_records',
            'exported_records',
            'progress',
            'status',
            'status_display',
            'created_at',
            'started_at',
            'completed_at',
            'error_message',
        ]
        read_only_fields = [
            'id',
            'file_path',
            'exported_records',
            'status',
            'created_at',
            'started_at',
            'completed_at',
            'error_message',
        ]
    
    def get_progress(self, obj):
        """Obtener porcentaje de progreso."""
        return round(obj.progress_percentage, 2)
    
    def validate_total_records(self, value):
        """
        Validar CNST-007: máximo 100K registros.
        
        Args:
            value: Total de registros a exportar
            
        Returns:
            int: Total validado
            
        Raises:
            ValidationError: Si excede límite CNST-007
        """
        if value > self.MAX_EXPORT_SIZE:
            raise serializers.ValidationError(
                f"CNST-007: La exportación no puede exceder "
                f"{self.MAX_EXPORT_SIZE:,} registros. "
                f"Total solicitado: {value:,}"
            )
        
        if value < 0:
            raise serializers.ValidationError(
                "Total de registros debe ser positivo"
            )
        
        return value
    
    def validate(self, data):
        """
        Validación adicional del ExportJob.
        
        Verifica que el reporte asociado exista y esté completado.
        """
        report = data.get('report')
        
        if report and report.status != 'completed':
            raise serializers.ValidationError({
                'report': 'Solo se pueden exportar reportes completados'
            })
        
        return data


class ReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear reportes.
    
    Simplificado para creación, sin campos calculados.
    """
    
    class Meta:
        model = Report
        fields = [
            'name',
            'report_type',
            'filters',
        ]
    
    def validate_report_type(self, value):
        """Validar que report_type sea válido."""
        valid_types = [choice[0] for choice in Report.REPORT_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Tipo de reporte inválido. Opciones: {', '.join(valid_types)}"
            )
        return value
