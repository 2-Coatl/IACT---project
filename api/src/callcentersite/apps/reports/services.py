"""Servicios del dashboard."""

from __future__ import annotations

from typing import Dict, List, Optional, Union

import csv
from io import BytesIO, StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import connection
from django.utils import timezone

from callcentersite.apps.users.models_permisos_granular import AuditoriaPermiso
from callcentersite.apps.users.services_permisos_granular import UserManagementService

from .models import DashboardConfiguracion
from .widgets import WIDGET_REGISTRY, Widget

User = get_user_model()


class DashboardService:
    """Orquesta la construcción de respuestas para el dashboard."""

    @staticmethod
    def ver_dashboard(usuario_id: int) -> Dict[str, object]:
        """Retorna la configuración del dashboard del usuario.

        Si el usuario no tiene configuración personalizada se usan los widgets
        por defecto registrados en ``WIDGET_REGISTRY``.
        """
        configuracion = DashboardConfiguracion.objects.filter(
            usuario_id=usuario_id
        ).first()

        widget_keys = configuracion.configuracion.get("widgets", []) if configuracion else list(WIDGET_REGISTRY.keys())
        widgets = [WIDGET_REGISTRY[widget].__dict__ for widget in widget_keys if widget in WIDGET_REGISTRY]

        # No fallback to defaults if user's config exists but is invalid; respect explicit selection.

        return {
            "widgets": widgets,
            "last_update": timezone.now().isoformat(),
        }

    @staticmethod
    def overview() -> Dict[str, object]:
        """Retorna overview general del dashboard (legacy)."""
        now = timezone.now()
        return {
            "last_update": now.isoformat(),
            "widgets": [
                asdict(widget) for widget in DashboardService.available_widgets()
            ],
        }

    @staticmethod
    def available_widgets() -> List[Widget]:
        """Retorna todos los widgets disponibles en el sistema."""
        return list(WIDGET_REGISTRY.values())

    @staticmethod
    def _serialize_widgets(widget_keys: List[str]) -> List[Dict[str, str]]:
        """Convierte identificadores de widgets a diccionarios serializables."""

        return [asdict(WIDGET_REGISTRY[widget]) for widget in widget_keys if widget in WIDGET_REGISTRY]

    @staticmethod
    def exportar(
        usuario_id: int,
        formato: str = 'pdf',
    ) -> Dict[str, object]:
        """
        Exporta dashboard a PDF o Excel.

        Args:
            usuario_id: ID del usuario que exporta
            formato: Formato de exportacion ('pdf' o 'excel')

        Returns:
            Diccionario con datos de exportacion:
                - formato: str
                - archivo: str (path o URL del archivo)
                - timestamp: str

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si el formato es invalido

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 26)
        """
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.exportar',
        )
        if not tiene_permiso:
            raise PermissionDenied('No tiene permiso para exportar dashboards')

        # Validar formato
        if formato not in ['pdf', 'excel']:
            raise ValidationError(f'Formato invalido: {formato}. Use pdf o excel')

        # TODO: Implementar logica real de exportacion
        # Por ahora retornamos un placeholder
        archivo = f'/tmp/dashboard_{usuario_id}_{timezone.now().timestamp()}.{formato}'

        AuditoriaPermiso.objects.create(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.exportar',
            recurso_tipo='dashboard',
            accion='exportar',
            resultado='permitido',
            detalles=f'Dashboard exportado a {formato}',
        )

        return {
            'formato': formato,
            'archivo': archivo,
            'timestamp': timezone.now().isoformat(),
        }

    @staticmethod
    def personalizar_dashboard(usuario_id: int, widgets: List[str]) -> DashboardConfiguracion:
        """Guarda la lista de widgets habilitados para el usuario.

        Args:
            usuario_id: ID del usuario dueño de la configuración.
            widgets: Lista de identificadores de widgets.

        Raises:
            ValidationError: Si la lista está vacía o contiene widgets inexistentes.
        """
        if not widgets:
            raise ValidationError('Debe proporcionar al menos un widget para personalizar el dashboard')

        widgets_invalidos = [widget for widget in widgets if widget not in WIDGET_REGISTRY]
        if widgets_invalidos:
            raise ValidationError(f"Widget invalido: {', '.join(widgets_invalidos)}")

        configuracion, _ = DashboardConfiguracion.objects.update_or_create(
            usuario_id=usuario_id,
            defaults={"configuracion": {"widgets": widgets}},
        )

        return configuracion

    @staticmethod
    def exportar_dashboard(usuario_id: int, formato: str = 'csv') -> Union[str, bytes]:
        """Exporta el dashboard del usuario en formato CSV o PDF.

        Args:
            usuario_id: ID del usuario.
            formato: Formato solicitado (``csv`` o ``pdf``).

        Returns:
            Cadena CSV cuando ``formato`` es ``csv`` o bytes que representan un
            PDF cuando ``formato`` es ``pdf``.

        Raises:
            ValidationError: Si el formato es inválido.
        """
        if formato not in {"csv", "pdf"}:
            raise ValidationError("Formato inválido. Use csv o pdf")

        dashboard = DashboardService.ver_dashboard(usuario_id=usuario_id)
        widgets = dashboard.get("widgets", [])

        if formato == "csv":
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=["type", "title", "value", "change", "period"])
            writer.writeheader()
            for widget in widgets:
                writer.writerow(widget)
            return output.getvalue()

        buffer = BytesIO()
        buffer.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        buffer.write(b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n")
        buffer.write(b"2 0 obj<< /Type /Pages /Kids[3 0 R] /Count 1 >>endobj\n")
        buffer.write(b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox[0 0 300 144] /Contents 4 0 R >>endobj\n")
        buffer.write(b"4 0 obj<< /Length 44 >>stream\nBT /F1 12 Tf 72 700 Td (Dashboard Export) Tj ET\nendstream endobj\n")
        buffer.write(b"xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000113 00000 n \n0000000200 00000 n \ntrail\n<< /Size 5 /Root 1 0 R >>\nstartxref\n280\n%%EOF")
        return buffer.getvalue()

    @staticmethod
    def personalizar(
        usuario_id: int,
        configuracion: Dict,
    ) -> DashboardConfiguracion:
        """
        Guarda configuracion personalizada de dashboard.

        Args:
            usuario_id: ID del usuario
            configuracion: Diccionario con configuracion de widgets y layout

        Returns:
            Objeto DashboardConfiguracion guardado

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si la configuracion no es valida JSON

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 28)
        """
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.personalizar',
        )
        if not tiene_permiso:
            raise PermissionDenied('No tiene permiso para personalizar dashboards')

        # Validar que configuracion sea dict
        if not isinstance(configuracion, dict):
            raise ValidationError('Configuracion debe ser un objeto JSON')

        # Guardar o actualizar configuracion
        config, created = DashboardConfiguracion.objects.update_or_create(
            usuario_id=usuario_id,
            defaults={'configuracion': configuracion},
        )

        AuditoriaPermiso.objects.create(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.personalizar',
            recurso_tipo='dashboard',
            accion='personalizar',
            recurso_id=config.id,
            resultado='permitido',
            detalles=f'Dashboard personalizado. Widgets: {len(configuracion.get("widgets", []))}',
        )

        return config

    @staticmethod
    def compartir(
        usuario_id: int,
        compartir_con_usuario_id: Optional[int] = None,
        compartir_con_grupo_codigo: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Comparte dashboard con otro usuario o grupo.

        Args:
            usuario_id: ID del usuario que comparte
            compartir_con_usuario_id: ID del usuario receptor (opcional)
            compartir_con_grupo_codigo: Codigo del grupo receptor (opcional)

        Returns:
            Diccionario con resultado:
                - compartido_con: str (email o nombre de grupo)
                - tipo: str ('usuario' o 'grupo')
                - timestamp: str

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si no se especifica receptor o no existe

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 30)
        """
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.compartir',
        )
        if not tiene_permiso:
            raise PermissionDenied('No tiene permiso para compartir dashboards')

        # Validar que se especifico al menos un receptor
        if not compartir_con_usuario_id and not compartir_con_grupo_codigo:
            raise ValidationError(
                'Debe especificar compartir_con_usuario_id o compartir_con_grupo_codigo'
            )

        compartido_con = None
        tipo = None

        # Compartir con usuario
        if compartir_con_usuario_id:
            try:
                usuario_receptor = User.objects.get(
                    id=compartir_con_usuario_id,
                    is_deleted=False,
                )
                compartido_con = usuario_receptor.email
                tipo = 'usuario'
            except User.DoesNotExist:
                raise ValidationError(
                    f'Usuario receptor no encontrado: {compartir_con_usuario_id}'
                )

        # Compartir con grupo
        if compartir_con_grupo_codigo:
            from callcentersite.apps.users.models_permisos_granular import GrupoPermiso
            try:
                grupo = GrupoPermiso.objects.get(codigo=compartir_con_grupo_codigo)
                compartido_con = grupo.nombre
                tipo = 'grupo'
            except GrupoPermiso.DoesNotExist:
                raise ValidationError(
                    f'Grupo no encontrado: {compartir_con_grupo_codigo}'
                )

        # TODO: Implementar logica real de compartir
        # (crear registro en tabla compartidos, enviar notificacion, etc.)

        AuditoriaPermiso.objects.create(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.compartir',
            recurso_tipo='dashboard',
            accion='compartir',
            resultado='permitido',
            detalles=f'Dashboard compartido con {tipo}: {compartido_con}',
        )

        return {
            'compartido_con': compartido_con,
            'tipo': tipo,
            'timestamp': timezone.now().isoformat(),
        }
