"""
Modelos core - IACT Call Center System.

CNST-003: Modelos analytics (PostgreSQL default DB).
"""
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.utils import SoftDeleteMixin

User = get_user_model()


class CallRecord(SoftDeleteMixin, models.Model):
    """
    Registro de llamadas procesado.
    
    Almacena datos agregados por fecha/telefono/servicio.
    Base de datos: default (PostgreSQL analytics).
    
    CNST-003: Este modelo usa 'default' DB (PostgreSQL).
    NO usa 'ivr_legacy' (MariaDB READ-ONLY).
    
    Usa SoftDeleteMixin para delete lógico.
    """
    
    fecha = models.DateField(
        db_index=True,
        help_text='Fecha de las llamadas'
    )
    
    telefono = models.CharField(
        max_length=20,
        db_index=True,
        help_text='Numero telefonico que realizo llamadas'
    )
    
    servicio_800 = models.CharField(
        max_length=20,
        db_index=True,
        help_text='Numero servicio 800 destino'
    )
    
    total_llamadas = models.IntegerField(
        default=0,
        help_text='Total de llamadas realizadas'
    )
    
    llamadas_contestadas = models.IntegerField(
        default=0,
        help_text='Llamadas contestadas por agente'
    )
    
    llamadas_abandonadas = models.IntegerField(
        default=0,
        help_text='Llamadas abandonadas (colgadas antes de contestar)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp creacion registro'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp ultima actualizacion'
    )
    
    class Meta:
        db_table = 'core_call_records'
        ordering = ['-fecha', '-created_at']
        unique_together = [['fecha', 'telefono', 'servicio_800']]
        indexes = [
            models.Index(fields=['fecha', 'servicio_800']),
            models.Index(fields=['fecha', 'telefono']),
        ]
        verbose_name = 'Registro de Llamada'
        verbose_name_plural = 'Registros de Llamadas'
    
    def __str__(self):
        """Representacion string."""
        return f"{self.fecha} - {self.telefono} -> {self.servicio_800}"
    
    def answer_rate(self):
        """
        Calcular porcentaje de respuesta.
        
        Returns:
            Decimal: Porcentaje (0-100)
        """
        if self.total_llamadas == 0:
            return Decimal('0.00')
        
        rate = (Decimal(self.llamadas_contestadas) / 
                Decimal(self.total_llamadas)) * 100
        return rate.quantize(Decimal('0.01'))


class Center(SoftDeleteMixin, models.Model):
    """
    Centro de atencion.
    
    Representa un centro fisico de call center.
    
    Usa SoftDeleteMixin para delete lógico.
    """
    
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre del centro'
    )
    
    codigo = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Codigo unico del centro'
    )
    
    activo = models.BooleanField(
        default=True,
        help_text='Centro activo'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_centers'
        ordering = ['nombre']
        verbose_name = 'Centro'
        verbose_name_plural = 'Centros'
    
    def __str__(self):
        return self.nombre



class Service(SoftDeleteMixin, models.Model):
    """
    Servicio 800.
    
    Representa un numero de servicio 800 asociado a un centro.
    
    Usa SoftDeleteMixin para delete lógico.
    """
    
    numero_800 = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Numero servicio 800'
    )
    
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre del servicio'
    )
    
    center = models.ForeignKey(
        Center,
        on_delete=models.PROTECT,
        related_name='services',
        help_text='Centro al que pertenece'
    )
    
    activo = models.BooleanField(
        default=True,
        help_text='Servicio activo'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_services'
        ordering = ['numero_800']
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
    
    def __str__(self):
        return f"{self.numero_800} - {self.nombre}"


class UserServiceAccess(SoftDeleteMixin, models.Model):
    """
    Acceso de usuario a servicios 800.
    
    Define qué servicios puede ver/gestionar cada usuario.
    Permite segmentación de datos por servicio.
    
    Ejemplos:
    - Usuario Juan: acceso a servicios [800-123-4567, 800-987-6543]
    - Usuario María: acceso a servicio [800-555-0000]
    - Usuario Admin: acceso a todos los servicios
    
    Si un usuario NO tiene ServiceAccess asignado:
    - Superusuarios: ven todos los servicios
    - Usuarios normales: no ven ningún servicio
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_accesses',
        verbose_name='Usuario',
    )
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='user_accesses',
        verbose_name='Servicio',
    )
    
    # Asignación
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Otorgado en',
    )
    
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_accesses_granted',
        verbose_name='Otorgado por',
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name='Razón',
        help_text='Por qué se otorgó este acceso',
    )
    
    # Estado
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
    )
    
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Revocado en',
    )
    
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_accesses_revoked',
        verbose_name='Revocado por',
    )
    
    class Meta:
        db_table = 'user_service_accesses'
        verbose_name = 'Acceso a Servicio'
        verbose_name_plural = 'Accesos a Servicios'
        unique_together = [['user', 'service']]
        ordering = ['-granted_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['service', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} -> {self.service.numero_800}"
    
    @classmethod
    def get_user_services(cls, user):
        """
        Obtener servicios accesibles por usuario.
        
        Args:
            user: Usuario
            
        Returns:
            QuerySet de Service accesibles
        """
        if user.is_superuser:
            # Superusuarios ven todos
            return Service.objects.filter(activo=True)
        
        # Usuarios normales: solo servicios asignados
        return Service.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            activo=True,
        ).distinct()
    
    @classmethod
    def has_service_access(cls, user, service):
        """
        Verificar si usuario tiene acceso a servicio.
        
        Args:
            user: Usuario
            service: Instancia de Service o ID
            
        Returns:
            bool: True si tiene acceso
        """
        if user.is_superuser:
            return True
        
        service_id = service.id if hasattr(service, 'id') else service
        
        return cls.objects.filter(
            user=user,
            service_id=service_id,
            is_active=True,
        ).exists()
