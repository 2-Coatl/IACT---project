"""Serializers para ETL."""

from __future__ import annotations

from rest_framework import serializers

from .models import ETLJob, ETLValidationError


class ETLJobSerializer(serializers.ModelSerializer):
    """Serializer para jobs ETL."""

    class Meta:
        model = ETLJob
        fields = [
            "id",
            "job_name",
            "status",
            "started_at",
            "completed_at",
            "records_extracted",
            "records_transformed",
            "records_loaded",
            "records_failed",
            "error_message",
            "error_details",
            "execution_time_seconds",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ETLValidationErrorSerializer(serializers.ModelSerializer):
    """Serializer para errores de validacion ETL."""

    job_name = serializers.CharField(source="job.job_name", read_only=True)

    class Meta:
        model = ETLValidationError
        fields = [
            "id",
            "job",
            "job_name",
            "error_type",
            "error_message",
            "record_data",
            "field_name",
            "severity",
            "created_at",
        ]
        read_only_fields = fields


class ETLStatsSerializer(serializers.Serializer):
    """Serializer para estadisticas de ETL."""

    total_jobs = serializers.IntegerField()
    completed_jobs = serializers.IntegerField()
    failed_jobs = serializers.IntegerField()
    running_jobs = serializers.IntegerField()
    total_records_processed = serializers.IntegerField()
    average_execution_time = serializers.FloatField()
