"""
Servicio de gestion de configuraciones del sistema.

Este servicio implementa operaciones CRUD para configuraciones
del sistema con verificacion de permisos granulares.

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tareas 33-41)
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from callcentersite.apps.users.models_permisos_granular import AuditoriaPermiso
from callcentersite.apps.users.service_helpers import (
    auditar_accion_exitosa,
    verificar_permiso_y_auditar,
)
from callcentersite.apps.users.services_permisos_granular import UserManagementService

from .models import Configuracion, ConfiguracionHistorial


class ConfiguracionService:
    """Servicio para operaciones CRUD de configuraciones del sistema."""

    @staticmethod
    def obtener_configuracion(
        usuario_id: int,
        categoria: Optional[str] = None,
    ) -> List[Dict]:
        """
        Obtiene configuraciones del sistema.

        Args:
            usuario_id: ID del usuario que consulta
            categoria: Filtrar por categoria (opcional)

        Returns:
            Lista de configuraciones con sus valores

        Raises:
            PermissionDenied: Si el usuario no tiene permiso

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 35)
        """
        # Verificar permiso y auditar
        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.ver',
            recurso_tipo='configuracion',
            accion='ver',
            mensaje_error='No tiene permiso para ver configuraciones',
        )

        # Auditar acceso con detalles
        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.ver',
            recurso_tipo='configuracion',
            accion='ver',
            detalles=f'Categoria: {categoria or "todas"}',
        )

        # Construir query
        queryset = Configuracion.objects.filter(activa=True)

        if categoria:
            queryset = queryset.filter(categoria=categoria)

        # Retornar configuraciones
        configuraciones = list(
            queryset.order_by('categoria', 'clave').values(
                'id',
                'categoria',
                'clave',
                'valor',
                'tipo_dato',
                'descripcion',
                'updated_at',
            )
        )

        return configuraciones

    @staticmethod
    def obtener_configuracion_detalle(
        usuario_id: int,
        clave: str,
    ) -> Configuracion:
        """Obtiene una configuracion puntual.

        Usa el mismo permiso de consulta que el listado general
        para mantener una unica superficie de autorizacion.
        """

        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.ver',
            recurso_tipo='configuracion',
            accion='ver',
            mensaje_error='No tiene permiso para ver configuraciones',
        )

        try:
            configuracion = Configuracion.objects.get(clave=clave, activa=True)
        except Configuracion.DoesNotExist:
            raise ValidationError(f'Configuracion no encontrada: {clave}')

        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.ver',
            recurso_tipo='configuracion',
            accion='ver',
            recurso_id=configuracion.id,
            detalles=f'Detalle de {clave}',
        )

        return configuracion

    @staticmethod
    def editar_configuracion(
        usuario_id: int,
        clave: str,
        nuevo_valor: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Configuracion:
        """
        Edita una configuracion del sistema.

        Args:
            usuario_id: ID del usuario que edita
            clave: Clave de la configuracion
            nuevo_valor: Nuevo valor
            ip_address: IP del usuario (opcional)
            user_agent: User agent del navegador (opcional)

        Returns:
            Configuracion actualizada

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si la configuracion no existe

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 37)
        """
        # Verificar permiso y auditar
        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.editar',
            recurso_tipo='configuracion',
            accion='editar',
            mensaje_error='No tiene permiso para editar configuraciones',
        )

        # Validar configuracion existe
        try:
            configuracion = Configuracion.objects.get(clave=clave, activa=True)
        except Configuracion.DoesNotExist:
            raise ValidationError(f'Configuracion no encontrada: {clave}')

        # Guardar valor anterior para historial
        valor_anterior = configuracion.valor

        # Actualizar configuracion
        with transaction.atomic():
            configuracion.valor = nuevo_valor
            configuracion.updated_by_id = usuario_id
            configuracion.save()

            # Crear registro de historial
            ConfiguracionHistorial.objects.create(
                configuracion=configuracion,
                clave=clave,
                valor_anterior=valor_anterior,
                valor_nuevo=nuevo_valor,
                modificado_por_id=usuario_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        # Auditar acción exitosa
        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.editar',
            recurso_tipo='configuracion',
            accion='editar',
            recurso_id=configuracion.id,
            detalles=f'{clave}: {valor_anterior} -> {nuevo_valor}',
        )

        return configuracion

    @staticmethod
    def obtener_historial_configuracion(
        usuario_id: int,
        clave: str,
    ) -> List[ConfiguracionHistorial]:
        """Recupera el historial de una configuracion especifica."""

        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.ver',
            recurso_tipo='configuracion',
            accion='ver',
            mensaje_error='No tiene permiso para ver configuraciones',
        )

        try:
            configuracion = Configuracion.objects.get(clave=clave, activa=True)
        except Configuracion.DoesNotExist:
            raise ValidationError(f'Configuracion no encontrada: {clave}')

        historial = list(
            ConfiguracionHistorial.objects.filter(configuracion=configuracion)
            .order_by('-timestamp')
        )

        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.ver',
            recurso_tipo='configuracion',
            accion='ver',
            recurso_id=configuracion.id,
            detalles=f'Historial de {clave} ({len(historial)} eventos)',
        )

        return historial

    @staticmethod
    def exportar_configuracion(
        usuario_id: int,
        formato: str = 'json',
    ) -> Dict[str, object]:
        """
        Exporta todas las configuraciones del sistema.

        Args:
            usuario_id: ID del usuario que exporta
            formato: Formato de exportacion ('json')

        Returns:
            Diccionario con configuraciones exportadas

        Raises:
            PermissionDenied: Si el usuario no tiene permiso

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 39)
        """
        # Verificar permiso y auditar
        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.exportar',
            recurso_tipo='configuracion',
            accion='exportar',
            mensaje_error='No tiene permiso para exportar configuraciones',
        )

        # Obtener todas las configuraciones
        configuraciones = Configuracion.objects.filter(activa=True).values(
            'categoria',
            'clave',
            'valor',
            'tipo_dato',
            'valor_default',
            'descripcion',
        )

        # Convertir a dict por categoria
        export_data = {}
        for config in configuraciones:
            categoria = config['categoria']
            if categoria not in export_data:
                export_data[categoria] = []
            export_data[categoria].append(config)

        # Auditar acción exitosa
        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.exportar',
            recurso_tipo='configuracion',
            accion='exportar',
            detalles=f'Exportadas {len(configuraciones)} configuraciones',
        )

        return export_data

    @staticmethod
    def importar_configuracion(
        usuario_id: int,
        configuraciones_json: Dict,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        Importa configuraciones desde JSON.

        Args:
            usuario_id: ID del usuario que importa
            configuraciones_json: Diccionario con configuraciones
            ip_address: IP del usuario (opcional)
            user_agent: User agent del navegador (opcional)

        Returns:
            Diccionario con estadisticas:
                - importadas: int
                - actualizadas: int
                - errores: int

        Raises:
            PermissionDenied: Si el usuario no tiene permiso

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 40)
        """
        # Verificar permiso y auditar
        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.importar',
            recurso_tipo='configuracion',
            accion='importar',
            mensaje_error='No tiene permiso para importar configuraciones',
        )

        importadas = 0
        actualizadas = 0
        errores = 0

        # Procesar configuraciones por categoria
        with transaction.atomic():
            for categoria, configs in configuraciones_json.items():
                for config_data in configs:
                    try:
                        clave = config_data['clave']
                        nuevo_valor = config_data['valor']

                        # Buscar configuracion existente
                        try:
                            config = Configuracion.objects.get(clave=clave)
                            valor_anterior = config.valor
                            config.valor = nuevo_valor
                            config.updated_by_id = usuario_id
                            config.save()

                            # Crear historial
                            ConfiguracionHistorial.objects.create(
                                configuracion=config,
                                clave=clave,
                                valor_anterior=valor_anterior,
                                valor_nuevo=nuevo_valor,
                                modificado_por_id=usuario_id,
                                ip_address=ip_address,
                                user_agent=user_agent,
                            )

                            actualizadas += 1

                        except Configuracion.DoesNotExist:
                            # Crear nueva configuracion
                            Configuracion.objects.create(
                                categoria=categoria,
                                clave=clave,
                                valor=nuevo_valor,
                                tipo_dato=config_data.get('tipo_dato', 'string'),
                                valor_default=config_data.get('valor_default', nuevo_valor),
                                descripcion=config_data.get('descripcion', ''),
                                updated_by_id=usuario_id,
                            )
                            importadas += 1

                    except (KeyError, ValueError) as e:
                        errores += 1

        # Auditar acción exitosa
        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.importar',
            recurso_tipo='configuracion',
            accion='importar',
            detalles=f'Importadas: {importadas}, Actualizadas: {actualizadas}, Errores: {errores}',
        )

        return {
            'importadas': importadas,
            'actualizadas': actualizadas,
            'errores': errores,
        }

    @staticmethod
    def obtener_historial_general(usuario_id: int) -> List[ConfiguracionHistorial]:
        """Devuelve el historial completo de configuraciones."""

        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.ver',
            recurso_tipo='configuracion',
            accion='ver',
            mensaje_error='No tiene permiso para ver configuraciones',
        )

        historial = list(
            ConfiguracionHistorial.objects.all().order_by('-timestamp')
        )

        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.ver',
            recurso_tipo='configuracion',
            accion='ver',
            detalles=f'Historial completo ({len(historial)} eventos)',
        )

        return historial

    @staticmethod
    def restaurar_configuracion(
        usuario_id: int,
        clave: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Configuracion:
        """
        Restaura una configuracion a su valor por defecto.

        Args:
            usuario_id: ID del usuario que restaura
            clave: Clave de la configuracion a restaurar
            ip_address: IP del usuario (opcional)
            user_agent: User agent del navegador (opcional)

        Returns:
            Configuracion restaurada

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si la configuracion no existe

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 41)
        """
        # Verificar permiso y auditar
        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.restaurar',
            recurso_tipo='configuracion',
            accion='restaurar',
            mensaje_error='No tiene permiso para restaurar configuraciones',
        )

        # Validar configuracion existe
        try:
            configuracion = Configuracion.objects.get(clave=clave, activa=True)
        except Configuracion.DoesNotExist:
            raise ValidationError(f'Configuracion no encontrada: {clave}')

        # Guardar valor anterior
        valor_anterior = configuracion.valor

        # Restaurar a valor default
        with transaction.atomic():
            configuracion.valor = configuracion.valor_default
            configuracion.updated_by_id = usuario_id
            configuracion.save()

            # Crear registro de historial
            ConfiguracionHistorial.objects.create(
                configuracion=configuracion,
                clave=clave,
                valor_anterior=valor_anterior,
                valor_nuevo=configuracion.valor_default,
                modificado_por_id=usuario_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        # Auditar acción exitosa
        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.tecnico.configuracion.restaurar',
            recurso_tipo='configuracion',
            accion='restaurar',
            recurso_id=configuracion.id,
            detalles=f'{clave} restaurada a valor default: {configuracion.valor_default}',
        )

        return configuracion
