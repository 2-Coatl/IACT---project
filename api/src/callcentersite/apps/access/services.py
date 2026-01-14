"""
Servicios para el sistema de permisos granular.

Sistema de Permisos Granular - Prioridad 1
REF: ADR-012-sistema-permisos-sin-roles-jerarquicos.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q
from django.utils import timezone

from callcentersite.apps.access.models import (
    Capacidad,
    Funcion,
    GrupoCapacidad,
    PermisoExcepcional,
    UsuarioGrupo,
    AuditoriaPermiso,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class PermisoService:
    """
    Servicio principal para verificacion de permisos.

    NO usa roles jerarquicos (Admin, Supervisor, Agent).
    SI usa grupos funcionales (atencion_cliente, gestion_equipos).

    Implementa:
    - Verificacion de capacidades por usuario
    - Manejo de permisos excepcionales (conceder/revocar)
    - Auditoria de accesos
    """

    @staticmethod
    def usuario_tiene_permiso(usuario_id: int, capacidad_requerida: str) -> bool:
        """
        Verifica si usuario tiene una capacidad especifica.

        Algoritmo:
        1. Obtener grupos activos del usuario
        2. Obtener capacidades de esos grupos
        3. Verificar permisos excepcionales:
           - Si existe 'revocar' activo: NO tiene permiso
           - Si existe 'conceder' activo: SI tiene permiso
        4. Verificar si capacidad esta en grupos

        Args:
            usuario_id: ID del usuario a verificar
            capacidad_requerida: Capacidad en formato sistema.dominio.recurso.accion

        Returns:
            True si usuario tiene el permiso, False en caso contrario

        Ejemplos:
            >>> PermisoService.usuario_tiene_permiso(1, "sistema.operaciones.llamadas.ver")
            True
        """
        # Verificar si usuario existe
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if not User.objects.filter(id=usuario_id).exists():
            return False

        # Verificar si capacidad existe
        try:
            capacidad_obj = Capacidad.objects.get(
                nombre_completo=capacidad_requerida,
                activa=True
            )
        except Capacidad.DoesNotExist:
            return False

        # 1. Verificar permisos excepcionales (tienen prioridad)
        ahora = timezone.now()

        # Verificar si existe revocacion activa
        revocacion = PermisoExcepcional.objects.filter(
            usuario_id=usuario_id,
            capacidad=capacidad_obj,
            tipo="revocar",
            activo=True,
            fecha_inicio__lte=ahora
        ).filter(
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=ahora)
        ).exists()

        if revocacion:
            return False

        # Verificar si existe concesion activa
        concesion = PermisoExcepcional.objects.filter(
            usuario_id=usuario_id,
            capacidad=capacidad_obj,
            tipo="conceder",
            activo=True,
            fecha_inicio__lte=ahora
        ).filter(
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=ahora)
        ).exists()

        if concesion:
            return True

        # 2. Verificar permisos por grupos
        # Obtener grupos activos del usuario (no expirados)
        grupos_activos = UsuarioGrupo.objects.filter(
            usuario_id=usuario_id,
            activo=True
        ).filter(
            Q(fecha_expiracion__isnull=True) | Q(fecha_expiracion__gte=ahora)
        ).values_list("grupo_id", flat=True)

        if not grupos_activos:
            return False

        # Verificar si alguno de los grupos tiene la capacidad
        tiene_capacidad = GrupoCapacidad.objects.filter(
            grupo_id__in=grupos_activos,
            capacidad=capacidad_obj
        ).exists()

        return tiene_capacidad

    @staticmethod
    def obtener_capacidades_usuario(usuario_id: int) -> list[str]:
        """
        Obtiene todas las capacidades que tiene un usuario.

        Combina:
        - Capacidades de grupos activos
        - Permisos excepcionales concedidos
        - EXCLUYE permisos excepcionales revocados

        Args:
            usuario_id: ID del usuario

        Returns:
            Lista de capacidades (sin duplicados)

        Ejemplos:
            >>> PermisoService.obtener_capacidades_usuario(1)
            [
                "sistema.operaciones.llamadas.ver",
                "sistema.operaciones.llamadas.realizar",
                "sistema.vistas.dashboards.ver"
            ]
        """
        ahora = timezone.now()
        capacidades = set()

        # 1. Obtener capacidades de grupos activos
        grupos_activos = UsuarioGrupo.objects.filter(
            usuario_id=usuario_id,
            activo=True
        ).filter(
            Q(fecha_expiracion__isnull=True) | Q(fecha_expiracion__gte=ahora)
        ).values_list("grupo_id", flat=True)

        if grupos_activos:
            capacidades_grupos = GrupoCapacidad.objects.filter(
                grupo_id__in=grupos_activos
            ).select_related("capacidad").values_list(
                "capacidad__nombre_completo", flat=True
            )
            capacidades.update(capacidades_grupos)

        # 2. Agregar permisos excepcionales concedidos
        concedidas = PermisoExcepcional.objects.filter(
            usuario_id=usuario_id,
            tipo="conceder",
            activo=True,
            fecha_inicio__lte=ahora
        ).filter(
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=ahora)
        ).select_related("capacidad").values_list(
            "capacidad__nombre_completo", flat=True
        )
        capacidades.update(concedidas)

        # 3. Excluir permisos excepcionales revocados
        revocadas = PermisoExcepcional.objects.filter(
            usuario_id=usuario_id,
            tipo="revocar",
            activo=True,
            fecha_inicio__lte=ahora
        ).filter(
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=ahora)
        ).select_related("capacidad").values_list(
            "capacidad__nombre_completo", flat=True
        )
        capacidades.difference_update(revocadas)

        return sorted(list(capacidades))

    @staticmethod
    def obtener_funciones_accesibles(usuario_id: int) -> list[dict]:
        """
        Obtiene funciones del sistema a las que el usuario tiene acceso.

        Una funcion es accesible si el usuario tiene AL MENOS UNA capacidad
        vinculada a esa funcion.

        Args:
            usuario_id: ID del usuario

        Returns:
            Lista de funciones con metadatos

        Ejemplos:
            >>> PermisoService.obtener_funciones_accesibles(1)
            [
                {
                    "id": 1,
                    "nombre": "llamadas",
                    "nombre_completo": "sistema.operaciones.llamadas",
                    "dominio": "operaciones",
                    "categoria": "operaciones",
                    "icono": "phone",
                    "orden_menu": 10
                }
            ]
        """
        # Obtener capacidades del usuario
        capacidades_usuario = PermisoService.obtener_capacidades_usuario(usuario_id)

        if not capacidades_usuario:
            return []

        # Obtener capacidades objetos
        capacidades_objs = Capacidad.objects.filter(
            nombre_completo__in=capacidades_usuario,
            activa=True
        ).values_list("id", flat=True)

        # Obtener funciones que tienen esas capacidades
        from callcentersite.apps.access.models import FuncionCapacidad

        funciones_ids = FuncionCapacidad.objects.filter(
            capacidad_id__in=capacidades_objs
        ).values_list("funcion_id", flat=True).distinct()

        # Obtener funciones activas
        funciones = Funcion.objects.filter(
            id__in=funciones_ids,
            activa=True
        ).order_by("orden_menu", "nombre").values(
            "id",
            "nombre",
            "nombre_completo",
            "dominio",
            "categoria",
            "icono",
            "orden_menu"
        )

        return list(funciones)

    @staticmethod
    def registrar_acceso(
        usuario_id: int,
        capacidad: str,
        accion: str,
        recurso_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict | None = None
    ) -> AuditoriaPermiso:
        """
        Registra acceso a recurso protegido en auditoria.

        Se debe llamar DESPUES de verificar permiso y PERMITIR acceso.

        Args:
            usuario_id: ID del usuario que accede
            capacidad: Capacidad utilizada (formato completo)
            accion: Accion realizada (ej: "LLAMADA_INICIADA", "PAGO_APROBADO")
            recurso_id: ID del recurso accedido (opcional)
            ip_address: IP del usuario (opcional)
            user_agent: User agent del navegador (opcional)
            metadata: Metadatos adicionales JSON (opcional)

        Returns:
            Registro de auditoria creado

        Ejemplos:
            >>> PermisoService.registrar_acceso(
            ...     usuario_id=1,
            ...     capacidad="sistema.finanzas.pagos.aprobar",
            ...     accion="PAGO_APROBADO",
            ...     recurso_id="PAY-12345",
            ...     ip_address="192.168.1.100",
            ...     metadata={"monto": 1000.00, "moneda": "USD"}
            ... )
            <AuditoriaPermiso: User 1 - PAGO_APROBADO>
        """
        return AuditoriaPermiso.objects.create(
            usuario_id=usuario_id,
            capacidad=capacidad,
            accion_realizada=accion,
            recurso_accedido=recurso_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )

    @staticmethod
    def verificar_capacidad_requiere_auditoria(capacidad: str) -> bool:
        """
        Verifica si una capacidad requiere auditoria obligatoria.

        Args:
            capacidad: Nombre completo de la capacidad

        Returns:
            True si requiere auditoria, False en caso contrario

        Ejemplos:
            >>> PermisoService.verificar_capacidad_requiere_auditoria(
            ...     "sistema.finanzas.pagos.aprobar"
            ... )
            True
        """
        try:
            cap = Capacidad.objects.get(nombre_completo=capacidad)
            return cap.requiere_auditoria
        except Capacidad.DoesNotExist:
            # Por seguridad, asumir que requiere auditoria
            return True
