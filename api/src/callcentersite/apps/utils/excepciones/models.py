"""Modelos para excepciones."""

from django.conf import settings
from django.db import models

from callcentersite.apps.common.models import TimeStampedModel


class Excepcion(TimeStampedModel):
    """Modelo de excepción con workflow de aprobación."""

    ESTADO_CHOICES = [
        ('solicitada', 'Solicitada'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    titulo = models.CharField(max_length=200, help_text='Título de la excepción')
    justificacion = models.TextField(help_text='Justificación detallada')
    tipo = models.CharField(max_length=100, help_text='Tipo de excepción')
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='solicitada',
        help_text='Estado actual de la excepción'
    )
    
    solicitado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='excepciones_solicitadas',
        help_text='Usuario que solicitó la excepción'
    )
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='excepciones_aprobadas',
        help_text='Usuario que aprobó/rechazó la excepción'
    )

    class Meta:
        db_table = 'excepciones'
        ordering = ['-created_at']
        verbose_name = 'Excepción'
        verbose_name_plural = 'Excepciones'

    def __str__(self):
        return f'{self.titulo} - {self.estado}'
