"""Servicios para ETL."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from django.utils import timezone

from .models import ETLJob, ETLValidationError


class ETLService:
    """Servicio para manejo de jobs ETL."""

    # Centros permitidos segun arquitectura
    CENTROS_PERMITIDOS = ["19028031", "19020084"]  # Nacional y Puebla

    @staticmethod
    def crear_job(job_name: str, metadata: dict[str, Any] | None = None) -> ETLJob:
        """
        Crear nuevo job ETL.

        Args:
            job_name: Nombre del job
            metadata: Metadata adicional

        Returns:
            ETLJob creado
        """
        job = ETLJob.objects.create(
            job_name=job_name, status="pending", metadata=metadata or {}
        )
        return job

    @staticmethod
    def iniciar_job(job_id: int) -> ETLJob:
        """
        Marcar job como iniciado.

        Args:
            job_id: ID del job

        Returns:
            ETLJob actualizado
        """
        job = ETLJob.objects.get(id=job_id)
        job.mark_as_running()
        return job

    @staticmethod
    def completar_job(
        job_id: int,
        extracted: int = 0,
        transformed: int = 0,
        loaded: int = 0,
        failed: int = 0,
    ) -> ETLJob:
        """
        Marcar job como completado con metricas.

        Args:
            job_id: ID del job
            extracted: Registros extraidos
            transformed: Registros transformados
            loaded: Registros cargados
            failed: Registros fallidos

        Returns:
            ETLJob actualizado
        """
        job = ETLJob.objects.get(id=job_id)
        job.mark_as_completed(
            extracted=extracted,
            transformed=transformed,
            loaded=loaded,
            failed=failed,
        )
        return job

    @staticmethod
    def marcar_job_fallido(
        job_id: int, error_message: str, error_details: dict[str, Any] | None = None
    ) -> ETLJob:
        """
        Marcar job como fallido.

        Args:
            job_id: ID del job
            error_message: Mensaje de error
            error_details: Detalles adicionales del error

        Returns:
            ETLJob actualizado
        """
        job = ETLJob.objects.get(id=job_id)
        job.mark_as_failed(
            error_message=error_message, error_details=error_details or {}
        )
        return job

    @staticmethod
    def validar_registro(datos: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validar registro de datos.

        Args:
            datos: Diccionario con datos a validar

        Returns:
            Tupla (es_valido, lista_errores)
        """
        errores = []

        # Validar call_id
        if not datos.get("call_id"):
            errores.append("call_id es requerido")

        # Validar phone_number
        phone = datos.get("phone_number", "")
        if not phone or len(str(phone)) < 10:
            errores.append("phone_number debe tener al menos 10 digitos")

        # Validar call_duration
        duration = datos.get("call_duration")
        if duration is not None and duration < 0:
            errores.append("call_duration no puede ser negativo")

        # Validar call_date
        if not datos.get("call_date"):
            errores.append("call_date es requerido")

        es_valido = len(errores) == 0
        return es_valido, errores

    @staticmethod
    def registrar_error_validacion(
        job_id: int,
        error_type: str,
        error_message: str,
        record_data: dict[str, Any],
        field_name: str | None = None,
        severity: str = "error",
    ) -> ETLValidationError:
        """
        Registrar error de validacion.

        Args:
            job_id: ID del job
            error_type: Tipo de error
            error_message: Mensaje de error
            record_data: Datos del registro con error
            field_name: Nombre del campo con error
            severity: Severidad (warning, error, critical)

        Returns:
            ETLValidationError creado
        """
        error = ETLValidationError.objects.create(
            job_id=job_id,
            error_type=error_type,
            error_message=error_message,
            record_data=record_data,
            field_name=field_name,
            severity=severity,
        )
        return error

    @staticmethod
    def listar_jobs_recientes(limite: int = 50) -> list[ETLJob]:
        """
        Listar jobs recientes.

        Args:
            limite: Cantidad maxima de jobs

        Returns:
            Lista de jobs ordenados por fecha
        """
        jobs = ETLJob.objects.all().order_by("-created_at")[:limite]
        return list(jobs)

    @staticmethod
    def obtener_estadisticas_job(job_id: int) -> dict[str, Any]:
        """
        Obtener estadisticas de un job.

        Args:
            job_id: ID del job

        Returns:
            Diccionario con estadisticas
        """
        job = ETLJob.objects.get(id=job_id)

        stats = {
            "job_name": job.job_name,
            "status": job.status,
            "records_extracted": job.records_extracted,
            "records_transformed": job.records_transformed,
            "records_loaded": job.records_loaded,
            "records_failed": job.records_failed,
            "execution_time_seconds": job.execution_time_seconds,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "error_message": job.error_message,
        }

        # Calcular tasa de exito si hay datos
        if job.records_extracted > 0:
            stats["success_rate"] = (
                job.records_loaded / job.records_extracted
            ) * 100

        return stats

    @staticmethod
    def filtrar_por_centros_permitidos(
        datos: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Filtrar datos solo de centros permitidos.

        Args:
            datos: Lista de registros con centro_id

        Returns:
            Lista filtrada solo con centros permitidos
        """
        datos_filtrados = [
            d
            for d in datos
            if d.get("centro_id") in ETLService.CENTROS_PERMITIDOS
        ]
        return datos_filtrados

    @staticmethod
    def ejecutar_etl_completo(
        job_name: str, fecha_inicio: datetime | None = None
    ) -> ETLJob:
        """
        Ejecutar ETL completo con job tracking.

        Args:
            job_name: Nombre del job
            fecha_inicio: Fecha de inicio para extraccion

        Returns:
            ETLJob con resultado de ejecucion
        """
        # Crear job
        job = ETLService.crear_job(
            job_name=job_name,
            metadata={"fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None},
        )

        try:
            # Iniciar job
            ETLService.iniciar_job(job_id=job.id)

            # Por ahora marcar como completado exitosamente
            # En implementacion real, aqui iria el proceso ETL completo
            ETLService.completar_job(
                job_id=job.id,
                extracted=0,  # Sera actualizado por proceso real
                transformed=0,
                loaded=0,
                failed=0,
            )

        except Exception as e:
            ETLService.marcar_job_fallido(
                job_id=job.id,
                error_message=str(e),
                error_details={"exception_type": type(e).__name__},
            )

        # Refresh job from DB to get updated status
        job.refresh_from_db()
        return job
