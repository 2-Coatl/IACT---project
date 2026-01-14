"""
Modelos del Sistema de Permisos Granular.

Prioridad 1: Estructura Base de Datos (8 tablas core)

Filosofia: SIN roles jerarquicos (NO admin/supervisor/agent)
          SOLO grupos funcionales de capacidades combinables

Referencias:
- REQ-PERM-001: Sistema de Permisos Granular
- ADR-XXX: Decision de NO usar roles jerarquicos
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Funcion(models.Model):
    """
    Funcion: Recurso del sistema (ej: dashboards, usuarios, metricas).

    Una funcion agrupa capacidades relacionadas.
    Ejemplo: funcion 'dashboards' tiene capacidades 'ver', 'exportar', 'personalizar'
    """

    nombre = models.CharField(
        max_length=100,
        help_text="Nombre corto: 'dashboards', 'usuarios'"
    )
    nombre_completo = models.CharField(
        max_length=200,
        unique=True,
        help_text="Nombre completo: 'sistema.vistas.dashboards'"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripcion de la funcion"
    )
    dominio = models.CharField(
        max_length=100,
        help_text="Dominio: vistas, administracion, operaciones, etc"
    )
    categoria = models.CharField(
        max_length=50,
        blank=True,
        help_text="Categoria: visualizacion, gestion, analisis, etc"
    )
    icono = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icono para UI"
    )
    orden_menu = models.IntegerField(
        default=0,
        help_text="Orden en menu de navegacion"
    )
    activa = models.BooleanField(
        default=True,
        help_text="Si la funcion esta activa"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'access_funciones'
        verbose_name = 'Funcion'
        verbose_name_plural = 'Funciones'
        ordering = ['orden_menu', 'nombre']
        indexes = [
            models.Index(fields=['dominio']),
            models.Index(fields=['activa']),
            models.Index(fields=['categoria']),
        ]

    def __str__(self):
        return self.nombre_completo


class Capacidad(models.Model):
    """
    Capacidad: Accion especifica sobre un recurso.

    Formato: sistema.dominio.recurso.accion
    Ejemplo: sistema.vistas.dashboards.ver

    Niveles de sensibilidad:
    - bajo: Consultas basicas
    - normal: Operaciones estandar
    - alto: Modificaciones importantes
    - critico: Acciones de alto impacto (requieren auditoria)
    """

    SENSIBILIDAD_CHOICES = [
        ('bajo', 'Bajo'),
        ('normal', 'Normal'),
        ('alto', 'Alto'),
        ('critico', 'Critico'),
    ]

    nombre_completo = models.CharField(
        max_length=200,
        unique=True,
        help_text="sistema.dominio.recurso.accion"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripcion de la capacidad"
    )
    accion = models.CharField(
        max_length=50,
        help_text="ver, crear, editar, eliminar, aprobar, etc"
    )
    recurso = models.CharField(
        max_length=100,
        help_text="dashboards, usuarios, metricas, etc"
    )
    dominio = models.CharField(
        max_length=100,
        help_text="vistas, administracion, operaciones, etc"
    )
    nivel_sensibilidad = models.CharField(
        max_length=20,
        choices=SENSIBILIDAD_CHOICES,
        default='normal',
        help_text="Nivel de sensibilidad de la accion"
    )
    requiere_auditoria = models.BooleanField(
        default=False,
        help_text="Si se debe auditar cada uso de esta capacidad"
    )
    activa = models.BooleanField(
        default=True,
        help_text="Si la capacidad esta activa"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'access_capacidades'
        verbose_name = 'Capacidad'
        verbose_name_plural = 'Capacidades'
        ordering = ['nombre_completo']
        indexes = [
            models.Index(fields=['accion']),
            models.Index(fields=['recurso']),
            models.Index(fields=['nivel_sensibilidad']),
        ]

    def __str__(self):
        return self.nombre_completo


class FuncionCapacidad(models.Model):
    """
    FuncionCapacidad: Relacion entre Funcion y Capacidad.

    Define que capacidades tiene cada funcion.
    """

    funcion = models.ForeignKey(
        Funcion,
        on_delete=models.CASCADE,
        related_name='capacidades'
    )
    capacidad = models.ForeignKey(
        Capacidad,
        on_delete=models.CASCADE,
        related_name='funciones'
    )
    requerida = models.BooleanField(
        default=False,
        help_text="Si es capacidad obligatoria para la funcion"
    )
    visible_en_ui = models.BooleanField(
        default=True,
        help_text="Si se muestra en interfaz de usuario"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'access_funcion_capacidades'
        verbose_name = 'Funcion-Capacidad'
        verbose_name_plural = 'Funcion-Capacidades'
        unique_together = [['funcion', 'capacidad']]

    def __str__(self):
        return f"{self.funcion.nombre} -> {self.capacidad.accion}"


class GrupoPermisos(models.Model):
    """
    GrupoPermisos: Agrupacion funcional de capacidades.

    IMPORTANTE: NO son roles jerarquicos (NO admin/supervisor/agent).
    Son grupos FUNCIONALES y DESCRIPTIVOS de lo que puede hacer:
    - 'atencion_cliente': puede atender clientes
    - 'gestion_equipos': puede gestionar equipos
    - 'visualizacion_metricas': puede ver metricas

    Un usuario puede tener MULTIPLES grupos simultaneamente.
    No hay jerarquia ni niveles entre grupos.

    Tipos de acceso (NO jerarquicos):
    - operativo: Operaciones diarias
    - gestion: Gestion de equipos y recursos
    - analisis: Analisis y reportes
    - estrategico: Decisiones estrategicas
    - tecnico: Configuracion tecnica
    - finanzas: Operaciones financieras
    - calidad: Control de calidad
    """

    TIPO_ACCESO_CHOICES = [
        ('operativo', 'Operativo'),
        ('gestion', 'Gestion'),
        ('analisis', 'Analisis'),
        ('estrategico', 'Estrategico'),
        ('tecnico', 'Tecnico'),
        ('finanzas', 'Finanzas'),
        ('calidad', 'Calidad'),
    ]

    codigo = models.CharField(
        max_length=100,
        unique=True,
        help_text="Codigo unico: 'atencion_cliente', 'gestion_equipos'"
    )
    nombre_display = models.CharField(
        max_length=200,
        help_text="Nombre para mostrar: 'Atencion al Cliente'"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripcion funcional del grupo"
    )
    tipo_acceso = models.CharField(
        max_length=50,
        choices=TIPO_ACCESO_CHOICES,
        blank=True,
        help_text="Tipo de acceso (NO jerarquico)"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Si el grupo esta activo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'access_grupos_permisos'
        verbose_name = 'Grupo de Permisos'
        verbose_name_plural = 'Grupos de Permisos'
        ordering = ['nombre_display']

    def __str__(self):
        return f"{self.nombre_display} ({self.codigo})"


class GrupoCapacidad(models.Model):
    """
    GrupoCapacidad: Relacion entre Grupo y Capacidad.

    Define que capacidades tiene cada grupo.
    """

    grupo = models.ForeignKey(
        GrupoPermisos,
        on_delete=models.CASCADE,
        related_name='capacidades'
    )
    capacidad = models.ForeignKey(
        Capacidad,
        on_delete=models.CASCADE,
        related_name='grupos'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'access_grupo_capacidades'
        verbose_name = 'Grupo-Capacidad'
        verbose_name_plural = 'Grupo-Capacidades'
        unique_together = [['grupo', 'capacidad']]

    def __str__(self):
        return f"{self.grupo.codigo} -> {self.capacidad.nombre_completo}"


class UsuarioGrupo(models.Model):
    """
    UsuarioGrupo: Usuario asignado a uno o mas grupos.

    IMPORTANTE: Usuario puede tener MULTIPLES grupos simultaneamente.
    No hay jerarquia: un usuario puede tener 'atencion_cliente' +
    'visualizacion_metricas' + 'gestion_horarios' al mismo tiempo.

    Permite asignaciones temporales con fecha_expiracion.
    """

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='grupos_asignados'
    )
    grupo = models.ForeignKey(
        GrupoPermisos,
        on_delete=models.CASCADE,
        related_name='usuarios'
    )
    fecha_asignacion = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha de asignacion"
    )
    fecha_expiracion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de expiracion (NULL = permanente)"
    )
    asignado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='grupos_asignados_por'
    )
    activo = models.BooleanField(
        default=True,
        help_text="Si la asignacion esta activa"
    )

    class Meta:
        db_table = 'access_usuarios_grupos'
        verbose_name = 'Usuario-Grupo'
        verbose_name_plural = 'Usuarios-Grupos'
        unique_together = [['usuario', 'grupo']]

    def __str__(self):
        return f"{self.usuario.username} -> {self.grupo.codigo}"

    def is_expired(self):
        """Verifica si la asignacion ha expirado."""
        if self.fecha_expiracion is None:
            return False
        return timezone.now() > self.fecha_expiracion


class PermisoExcepcional(models.Model):
    """
    PermisoExcepcional: Conceder o revocar capacidad especifica a usuario.

    Permite otorgar temporalmente una capacidad que el usuario no tiene
    en sus grupos, o revocar una capacidad especifica que si tiene.

    Casos de uso:
    - Conceder: Usuario necesita capacidad temporal para proyecto especial
    - Revocar: Usuario tiene incidente y se le revoca capacidad temporalmente

    Puede ser temporal (con fecha_inicio/fecha_fin) o permanente.
    """

    TIPO_CHOICES = [
        ('conceder', 'Conceder'),
        ('revocar', 'Revocar'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='permisos_excepcionales_permissions'
    )
    capacidad = models.ForeignKey(
        Capacidad,
        on_delete=models.CASCADE,
        related_name='permisos_excepcionales'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        help_text="conceder o revocar"
    )
    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha de inicio"
    )
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha fin (NULL = permanente)"
    )
    motivo = models.TextField(
        help_text="Justificacion del permiso excepcional"
    )
    autorizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permisos_autorizados'
    )
    activo = models.BooleanField(
        default=True,
        help_text="Si el permiso excepcional esta activo"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'access_permisos_excepcionales'
        verbose_name = 'Permiso Excepcional'
        verbose_name_plural = 'Permisos Excepcionales'
        indexes = [
            models.Index(fields=['usuario', 'activo']),
        ]

    def __str__(self):
        return f"{self.tipo}: {self.usuario.username} -> {self.capacidad.nombre_completo}"

    def is_active_now(self):
        """Verifica si el permiso excepcional esta activo en este momento."""
        if not self.activo:
            return False

        now = timezone.now()

        if self.fecha_inicio > now:
            return False

        if self.fecha_fin and self.fecha_fin < now:
            return False

        return True


class AuditoriaPermiso(models.Model):
    """
    AuditoriaPermiso: Registro de cada acceso a recursos protegidos.

    Registra TODOS los intentos de acceso (concedidos y denegados)
    para capacidades que requieren auditoria.

    Almacena:
    - Quien: usuario
    - Que: capacidad requerida
    - Cuando: timestamp
    - Donde: IP, user agent
    - Resultado: acceso_concedido o acceso_denegado
    - Metadata: informacion adicional en JSONB
    """

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='auditorias'
    )
    capacidad = models.CharField(
        max_length=200,
        help_text="Capacidad que se intento usar"
    )
    accion_realizada = models.CharField(
        max_length=100,
        help_text="acceso_concedido, acceso_denegado"
    )
    recurso_accedido = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="URL o recurso especifico accedido"
    )
    ip_address = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="IP del usuario"
    )
    user_agent = models.TextField(
        blank=True,
        default='',
        help_text="User agent del navegador"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos adicionales en formato JSON"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp del acceso"
    )

    class Meta:
        db_table = 'access_auditoria_permisos'
        verbose_name = 'Auditoria de Permiso'
        verbose_name_plural = 'Auditorias de Permisos'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['accion_realizada']),
        ]

    def __str__(self):
        return f"{self.accion_realizada}: {self.usuario.username if self.usuario else 'N/A'} -> {self.capacidad}"
