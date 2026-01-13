"""
Modelos para gestión de Llamadas.

Sistema de Permisos Granular - Prioridad 3: Módulo Operativo Llamadas
REF: ADR-012-sistema-permisos-sin-roles-jerarquicos.md
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid


User = get_user_model()


class EstadoLlamada(models.Model):
    """Estados posibles de una llamada."""

    codigo = models.CharField(max_length=50, unique=True, help_text='Codigo unico del estado')
    nombre = models.CharField(max_length=100, help_text='Nombre del estado')
    descripcion = models.TextField(blank=True, help_text='Descripcion del estado')
    es_final = models.BooleanField(default=False, help_text='Si es un estado final')
    activo = models.BooleanField(default=True, help_text='Si esta activo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'llamadas_estados'
        verbose_name = 'Estado de Llamada'
        verbose_name_plural = 'Estados de Llamadas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class TipoLlamada(models.Model):
    """Tipos de llamadas."""

    codigo = models.CharField(max_length=50, unique=True, help_text='Codigo unico del tipo')
    nombre = models.CharField(max_length=100, help_text='Nombre del tipo')
    descripcion = models.TextField(blank=True, help_text='Descripcion del tipo')
    activo = models.BooleanField(default=True, help_text='Si esta activo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'llamadas_tipos'
        verbose_name = 'Tipo de Llamada'
        verbose_name_plural = 'Tipos de Llamadas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Llamada(models.Model):
    """Registro de llamadas telefónicas."""

    codigo = models.CharField(max_length=50, unique=True, editable=False, help_text='Codigo unico generado')
    numero_telefono = models.CharField(max_length=20, help_text='Numero telefonico')
    tipo = models.ForeignKey(TipoLlamada, on_delete=models.PROTECT, related_name='llamadas')
    estado = models.ForeignKey(EstadoLlamada, on_delete=models.PROTECT, related_name='llamadas')
    agente = models.ForeignKey(User, on_delete=models.PROTECT, related_name='llamadas_atendidas')

    # Informacion del cliente
    cliente_nombre = models.CharField(max_length=200, blank=True, null=True)
    cliente_email = models.EmailField(blank=True, null=True)
    cliente_id = models.IntegerField(blank=True, null=True, help_text='ID del cliente si existe')

    # Fechas y tiempos
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(blank=True, null=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True, help_text='Datos adicionales JSON')
    notas = models.TextField(blank=True, help_text='Notas de la llamada')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'llamadas'
        verbose_name = 'Llamada'
        verbose_name_plural = 'Llamadas'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['numero_telefono']),
            models.Index(fields=['agente', 'fecha_inicio']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_inicio']),
        ]

    def save(self, *args, **kwargs):
        """Generar codigo unico al crear."""
        if not self.codigo:
            self.codigo = f"CALL-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def calcular_duracion(self):
        """Calcular duracion de la llamada en segundos."""
        if self.fecha_fin:
            delta = self.fecha_fin - self.fecha_inicio
            return int(delta.total_seconds())
        return None

    def __str__(self):
        return f"{self.codigo} - {self.numero_telefono}"


class LlamadaTranscripcion(models.Model):
    """Transcripción de llamadas."""

    llamada = models.ForeignKey(Llamada, on_delete=models.CASCADE, related_name='transcripciones')
    texto = models.TextField(help_text='Texto transcrito')
    timestamp_inicio = models.IntegerField(help_text='Segundo de inicio en la grabacion')
    timestamp_fin = models.IntegerField(help_text='Segundo de fin en la grabacion')
    hablante = models.CharField(max_length=50, help_text='Identificador del hablante (agente/cliente)')
    confianza = models.FloatField(blank=True, null=True, help_text='Nivel de confianza de la transcripcion')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'llamadas_transcripciones'
        verbose_name = 'Transcripcion de Llamada'
        verbose_name_plural = 'Transcripciones de Llamadas'
        ordering = ['llamada', 'timestamp_inicio']

    def __str__(self):
        return f"Transcripcion {self.llamada.codigo} - {self.hablante}"


class LlamadaGrabacion(models.Model):
    """Grabaciones de llamadas."""

    llamada = models.OneToOneField(Llamada, on_delete=models.CASCADE, related_name='grabacion')
    archivo_url = models.URLField(max_length=500, help_text='URL del archivo de grabacion')
    formato = models.CharField(max_length=10, help_text='Formato del audio (mp3, wav, etc)')
    duracion_segundos = models.IntegerField(help_text='Duracion en segundos')
    tamano_bytes = models.BigIntegerField(blank=True, null=True, help_text='Tamano del archivo en bytes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'llamadas_grabaciones'
        verbose_name = 'Grabacion de Llamada'
        verbose_name_plural = 'Grabaciones de Llamadas'

    def __str__(self):
        return f"Grabacion {self.llamada.codigo}"
