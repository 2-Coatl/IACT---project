"""
Management command para poblar permisos iniciales.

Sistema de Permisos Granular - Prioridad 1
REF: ADR-012-sistema-permisos-sin-roles-jerarquicos.md

Uso:
    python manage.py seed_permissions
    python manage.py seed_permissions --reset  # Elimina datos existentes
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from callcentersite.apps.access.models import (
    Funcion,
    Capacidad,
    FuncionCapacidad,
    GrupoPermisos,
    GrupoCapacidad,
)


class Command(BaseCommand):
    """Comando para poblar datos iniciales de permisos."""

    help = 'Pobla funciones, capacidades y grupos de permisos iniciales'

    def add_arguments(self, parser):
        """Agregar argumentos al comando."""
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina datos existentes antes de poblar'
        )

    def handle(self, *args, **options):
        """Ejecutar comando."""
        if options['reset']:
            self.stdout.write(self.style.WARNING('Eliminando datos existentes...'))
            self._reset_data()

        self.stdout.write(self.style.SUCCESS('Poblando datos iniciales...'))

        with transaction.atomic():
            self._crear_funciones()
            self._crear_capacidades()
            self._vincular_funciones_capacidades()
            self._crear_grupos_permisos()
            self._vincular_grupos_capacidades()

        self.stdout.write(self.style.SUCCESS('Datos iniciales poblados exitosamente'))

    def _reset_data(self):
        """Elimina datos existentes."""
        GrupoCapacidad.objects.all().delete()
        FuncionCapacidad.objects.all().delete()
        GrupoPermisos.objects.all().delete()
        Capacidad.objects.all().delete()
        Funcion.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Datos eliminados'))

    def _crear_funciones(self):
        """Crea funciones del sistema."""
        funciones = [
            # Dominio: vistas
            {
                'nombre': 'dashboards',
                'nombre_completo': 'sistema.vistas.dashboards',
                'descripcion': 'Visualizacion de dashboards y paneles de control',
                'dominio': 'vistas',
                'categoria': 'vistas',
                'icono': 'dashboard',
                'orden_menu': 10
            },

            # Dominio: operaciones
            {
                'nombre': 'llamadas',
                'nombre_completo': 'sistema.operaciones.llamadas',
                'descripcion': 'Gestion de llamadas telefonicas',
                'dominio': 'operaciones',
                'categoria': 'operaciones',
                'icono': 'phone',
                'orden_menu': 20
            },
            {
                'nombre': 'tickets',
                'nombre_completo': 'sistema.operaciones.tickets',
                'descripcion': 'Gestion de tickets de soporte',
                'dominio': 'operaciones',
                'categoria': 'operaciones',
                'icono': 'ticket',
                'orden_menu': 30
            },
            {
                'nombre': 'clientes',
                'nombre_completo': 'sistema.operaciones.clientes',
                'descripcion': 'Gestion de informacion de clientes',
                'dominio': 'operaciones',
                'categoria': 'operaciones',
                'icono': 'people',
                'orden_menu': 40
            },

            # Dominio: administracion
            {
                'nombre': 'usuarios',
                'nombre_completo': 'sistema.administracion.usuarios',
                'descripcion': 'Gestion de usuarios del sistema',
                'dominio': 'administracion',
                'categoria': 'administracion',
                'icono': 'person',
                'orden_menu': 50
            },

            # Dominio: analisis
            {
                'nombre': 'metricas',
                'nombre_completo': 'sistema.analisis.metricas',
                'descripcion': 'Visualizacion de metricas y KPIs',
                'dominio': 'analisis',
                'categoria': 'analisis',
                'icono': 'chart',
                'orden_menu': 60
            },
            {
                'nombre': 'reportes',
                'nombre_completo': 'sistema.analisis.reportes',
                'descripcion': 'Generacion de reportes',
                'dominio': 'analisis',
                'categoria': 'analisis',
                'icono': 'report',
                'orden_menu': 70
            },

            # Dominio: supervision
            {
                'nombre': 'equipos',
                'nombre_completo': 'sistema.supervision.equipos',
                'descripcion': 'Gestion de equipos de trabajo',
                'dominio': 'supervision',
                'categoria': 'supervision',
                'icono': 'group',
                'orden_menu': 80
            },
            {
                'nombre': 'horarios',
                'nombre_completo': 'sistema.supervision.horarios',
                'descripcion': 'Gestion de horarios y turnos',
                'dominio': 'supervision',
                'categoria': 'supervision',
                'icono': 'schedule',
                'orden_menu': 90
            },

            # Dominio: finanzas
            {
                'nombre': 'pagos',
                'nombre_completo': 'sistema.finanzas.pagos',
                'descripcion': 'Gestion de pagos y aprobaciones',
                'dominio': 'finanzas',
                'categoria': 'finanzas',
                'icono': 'payment',
                'orden_menu': 100
            },

            # Dominio: tecnico
            {
                'nombre': 'configuracion',
                'nombre_completo': 'sistema.tecnico.configuracion',
                'descripcion': 'Configuracion del sistema',
                'dominio': 'tecnico',
                'categoria': 'tecnico',
                'icono': 'settings',
                'orden_menu': 110
            },
        ]

        for func_data in funciones:
            funcion, created = Funcion.objects.get_or_create(
                nombre_completo=func_data['nombre_completo'],
                defaults=func_data
            )
            if created:
                self.stdout.write(f'  Funcion creada: {funcion.nombre_completo}')

    def _crear_capacidades(self):
        """Crea capacidades atomicas."""
        capacidades = [
            # Dashboards
            {'nombre_completo': 'sistema.vistas.dashboards.ver', 'accion': 'ver', 'recurso': 'dashboards', 'dominio': 'vistas', 'nivel_sensibilidad': 'bajo'},

            # Llamadas
            {'nombre_completo': 'sistema.operaciones.llamadas.ver', 'accion': 'ver', 'recurso': 'llamadas', 'dominio': 'operaciones', 'nivel_sensibilidad': 'bajo'},
            {'nombre_completo': 'sistema.operaciones.llamadas.realizar', 'accion': 'realizar', 'recurso': 'llamadas', 'dominio': 'operaciones', 'nivel_sensibilidad': 'normal'},

            # Tickets
            {'nombre_completo': 'sistema.operaciones.tickets.ver', 'accion': 'ver', 'recurso': 'tickets', 'dominio': 'operaciones', 'nivel_sensibilidad': 'bajo'},
            {'nombre_completo': 'sistema.operaciones.tickets.crear', 'accion': 'crear', 'recurso': 'tickets', 'dominio': 'operaciones', 'nivel_sensibilidad': 'normal'},
            {'nombre_completo': 'sistema.operaciones.tickets.editar', 'accion': 'editar', 'recurso': 'tickets', 'dominio': 'operaciones', 'nivel_sensibilidad': 'normal'},
            {'nombre_completo': 'sistema.operaciones.tickets.eliminar', 'accion': 'eliminar', 'recurso': 'tickets', 'dominio': 'operaciones', 'nivel_sensibilidad': 'alto', 'requiere_auditoria': True},

            # Clientes
            {'nombre_completo': 'sistema.operaciones.clientes.ver', 'accion': 'ver', 'recurso': 'clientes', 'dominio': 'operaciones', 'nivel_sensibilidad': 'normal'},
            {'nombre_completo': 'sistema.operaciones.clientes.editar', 'accion': 'editar', 'recurso': 'clientes', 'dominio': 'operaciones', 'nivel_sensibilidad': 'alto', 'requiere_auditoria': True},

            # Usuarios
            {'nombre_completo': 'sistema.administracion.usuarios.ver', 'accion': 'ver', 'recurso': 'usuarios', 'dominio': 'administracion', 'nivel_sensibilidad': 'normal'},
            {'nombre_completo': 'sistema.administracion.usuarios.crear', 'accion': 'crear', 'recurso': 'usuarios', 'dominio': 'administracion', 'nivel_sensibilidad': 'alto', 'requiere_auditoria': True},
            {'nombre_completo': 'sistema.administracion.usuarios.editar', 'accion': 'editar', 'recurso': 'usuarios', 'dominio': 'administracion', 'nivel_sensibilidad': 'alto', 'requiere_auditoria': True},
            {'nombre_completo': 'sistema.administracion.usuarios.eliminar', 'accion': 'eliminar', 'recurso': 'usuarios', 'dominio': 'administracion', 'nivel_sensibilidad': 'critico', 'requiere_auditoria': True},

            # Metricas
            {'nombre_completo': 'sistema.analisis.metricas.ver', 'accion': 'ver', 'recurso': 'metricas', 'dominio': 'analisis', 'nivel_sensibilidad': 'bajo'},

            # Reportes
            {'nombre_completo': 'sistema.analisis.reportes.ver', 'accion': 'ver', 'recurso': 'reportes', 'dominio': 'analisis', 'nivel_sensibilidad': 'normal'},
            {'nombre_completo': 'sistema.analisis.reportes.generar', 'accion': 'generar', 'recurso': 'reportes', 'dominio': 'analisis', 'nivel_sensibilidad': 'normal'},

            # Equipos
            {'nombre_completo': 'sistema.supervision.equipos.ver', 'accion': 'ver', 'recurso': 'equipos', 'dominio': 'supervision', 'nivel_sensibilidad': 'normal'},
            {'nombre_completo': 'sistema.supervision.equipos.crear', 'accion': 'crear', 'recurso': 'equipos', 'dominio': 'supervision', 'nivel_sensibilidad': 'alto'},
            {'nombre_completo': 'sistema.supervision.equipos.editar', 'accion': 'editar', 'recurso': 'equipos', 'dominio': 'supervision', 'nivel_sensibilidad': 'alto'},
            {'nombre_completo': 'sistema.supervision.equipos.asignar_miembros', 'accion': 'asignar_miembros', 'recurso': 'equipos', 'dominio': 'supervision', 'nivel_sensibilidad': 'alto', 'requiere_auditoria': True},

            # Horarios
            {'nombre_completo': 'sistema.supervision.horarios.ver', 'accion': 'ver', 'recurso': 'horarios', 'dominio': 'supervision', 'nivel_sensibilidad': 'bajo'},
            {'nombre_completo': 'sistema.supervision.horarios.crear', 'accion': 'crear', 'recurso': 'horarios', 'dominio': 'supervision', 'nivel_sensibilidad': 'normal'},
            {'nombre_completo': 'sistema.supervision.horarios.editar', 'accion': 'editar', 'recurso': 'horarios', 'dominio': 'supervision', 'nivel_sensibilidad': 'alto'},
            {'nombre_completo': 'sistema.supervision.horarios.aprobar', 'accion': 'aprobar', 'recurso': 'horarios', 'dominio': 'supervision', 'nivel_sensibilidad': 'alto', 'requiere_auditoria': True},

            # Pagos
            {'nombre_completo': 'sistema.finanzas.pagos.ver', 'accion': 'ver', 'recurso': 'pagos', 'dominio': 'finanzas', 'nivel_sensibilidad': 'alto'},
            {'nombre_completo': 'sistema.finanzas.pagos.aprobar', 'accion': 'aprobar', 'recurso': 'pagos', 'dominio': 'finanzas', 'nivel_sensibilidad': 'critico', 'requiere_auditoria': True},

            # Configuracion
            {'nombre_completo': 'sistema.tecnico.configuracion.ver', 'accion': 'ver', 'recurso': 'configuracion', 'dominio': 'tecnico', 'nivel_sensibilidad': 'alto'},
            {'nombre_completo': 'sistema.tecnico.configuracion.editar', 'accion': 'editar', 'recurso': 'configuracion', 'dominio': 'tecnico', 'nivel_sensibilidad': 'critico', 'requiere_auditoria': True},
        ]

        for cap_data in capacidades:
            # Agregar descripcion automatica
            cap_data['descripcion'] = f"{cap_data['accion'].capitalize()} {cap_data['recurso']}"

            capacidad, created = Capacidad.objects.get_or_create(
                nombre_completo=cap_data['nombre_completo'],
                defaults=cap_data
            )
            if created:
                self.stdout.write(f'  Capacidad creada: {capacidad.nombre_completo}')

    def _vincular_funciones_capacidades(self):
        """Vincula capacidades a funciones."""
        vinculaciones = [
            ('sistema.vistas.dashboards', 'sistema.vistas.dashboards.ver', True),

            ('sistema.operaciones.llamadas', 'sistema.operaciones.llamadas.ver', True),
            ('sistema.operaciones.llamadas', 'sistema.operaciones.llamadas.realizar', False),

            ('sistema.operaciones.tickets', 'sistema.operaciones.tickets.ver', True),
            ('sistema.operaciones.tickets', 'sistema.operaciones.tickets.crear', False),
            ('sistema.operaciones.tickets', 'sistema.operaciones.tickets.editar', False),
            ('sistema.operaciones.tickets', 'sistema.operaciones.tickets.eliminar', False),

            ('sistema.operaciones.clientes', 'sistema.operaciones.clientes.ver', True),
            ('sistema.operaciones.clientes', 'sistema.operaciones.clientes.editar', False),

            ('sistema.administracion.usuarios', 'sistema.administracion.usuarios.ver', True),
            ('sistema.administracion.usuarios', 'sistema.administracion.usuarios.crear', False),
            ('sistema.administracion.usuarios', 'sistema.administracion.usuarios.editar', False),
            ('sistema.administracion.usuarios', 'sistema.administracion.usuarios.eliminar', False),

            ('sistema.analisis.metricas', 'sistema.analisis.metricas.ver', True),

            ('sistema.analisis.reportes', 'sistema.analisis.reportes.ver', True),
            ('sistema.analisis.reportes', 'sistema.analisis.reportes.generar', False),

            ('sistema.supervision.equipos', 'sistema.supervision.equipos.ver', True),
            ('sistema.supervision.equipos', 'sistema.supervision.equipos.crear', False),
            ('sistema.supervision.equipos', 'sistema.supervision.equipos.editar', False),
            ('sistema.supervision.equipos', 'sistema.supervision.equipos.asignar_miembros', False),

            ('sistema.supervision.horarios', 'sistema.supervision.horarios.ver', True),
            ('sistema.supervision.horarios', 'sistema.supervision.horarios.crear', False),
            ('sistema.supervision.horarios', 'sistema.supervision.horarios.editar', False),
            ('sistema.supervision.horarios', 'sistema.supervision.horarios.aprobar', False),

            ('sistema.finanzas.pagos', 'sistema.finanzas.pagos.ver', True),
            ('sistema.finanzas.pagos', 'sistema.finanzas.pagos.aprobar', False),

            ('sistema.tecnico.configuracion', 'sistema.tecnico.configuracion.ver', True),
            ('sistema.tecnico.configuracion', 'sistema.tecnico.configuracion.editar', False),
        ]

        for funcion_nc, capacidad_nc, requerida in vinculaciones:
            try:
                funcion = Funcion.objects.get(nombre_completo=funcion_nc)
                capacidad = Capacidad.objects.get(nombre_completo=capacidad_nc)

                vinc, created = FuncionCapacidad.objects.get_or_create(
                    funcion=funcion,
                    capacidad=capacidad,
                    defaults={'requerida': requerida}
                )
                if created:
                    self.stdout.write(f'  Vinculacion creada: {funcion_nc} -> {capacidad_nc}')
            except (Funcion.DoesNotExist, Capacidad.DoesNotExist) as e:
                self.stdout.write(self.style.ERROR(f'  Error vinculando: {e}'))

    def _crear_grupos_permisos(self):
        """Crea grupos funcionales de permisos."""
        grupos = [
            {
                'codigo': 'atencion_cliente',
                'nombre_display': 'Atencion al Cliente',
                'descripcion': 'Grupo para agentes de atencion al cliente. Pueden realizar llamadas, gestionar tickets y consultar clientes.',
                'tipo_acceso': 'operativo'
            },
            {
                'codigo': 'visualizacion_metricas',
                'nombre_display': 'Visualizacion de Metricas',
                'descripcion': 'Permite ver dashboards y metricas personales.',
                'tipo_acceso': 'analisis'
            },
            {
                'codigo': 'gestion_equipos',
                'nombre_display': 'Gestion de Equipos',
                'descripcion': 'Permite gestionar equipos de trabajo, asignar miembros y planificar.',
                'tipo_acceso': 'gestion'
            },
            {
                'codigo': 'gestion_horarios',
                'nombre_display': 'Gestion de Horarios',
                'descripcion': 'Permite crear, editar y aprobar horarios y turnos.',
                'tipo_acceso': 'gestion'
            },
            {
                'codigo': 'analisis_avanzado',
                'nombre_display': 'Analisis Avanzado',
                'descripcion': 'Permite generar reportes y analizar metricas avanzadas.',
                'tipo_acceso': 'analisis'
            },
            {
                'codigo': 'administracion_usuarios',
                'nombre_display': 'Administracion de Usuarios',
                'descripcion': 'Permite gestionar usuarios del sistema (crear, editar, eliminar).',
                'tipo_acceso': 'gestion'
            },
            {
                'codigo': 'finanzas_aprobaciones',
                'nombre_display': 'Finanzas - Aprobaciones',
                'descripcion': 'Permite aprobar pagos y transacciones financieras.',
                'tipo_acceso': 'finanzas'
            },
            {
                'codigo': 'configuracion_sistema',
                'nombre_display': 'Configuracion del Sistema',
                'descripcion': 'Permite configurar parametros tecnicos del sistema.',
                'tipo_acceso': 'tecnico'
            },
        ]

        for grupo_data in grupos:
            grupo, created = GrupoPermisos.objects.get_or_create(
                codigo=grupo_data['codigo'],
                defaults=grupo_data
            )
            if created:
                self.stdout.write(f'  Grupo creado: {grupo.nombre_display}')

    def _vincular_grupos_capacidades(self):
        """Vincula capacidades a grupos."""
        vinculaciones = [
            # Grupo: atencion_cliente
            ('atencion_cliente', 'sistema.operaciones.llamadas.ver'),
            ('atencion_cliente', 'sistema.operaciones.llamadas.realizar'),
            ('atencion_cliente', 'sistema.operaciones.tickets.ver'),
            ('atencion_cliente', 'sistema.operaciones.tickets.crear'),
            ('atencion_cliente', 'sistema.operaciones.tickets.editar'),
            ('atencion_cliente', 'sistema.operaciones.clientes.ver'),

            # Grupo: visualizacion_metricas
            ('visualizacion_metricas', 'sistema.vistas.dashboards.ver'),
            ('visualizacion_metricas', 'sistema.analisis.metricas.ver'),

            # Grupo: gestion_equipos
            ('gestion_equipos', 'sistema.supervision.equipos.ver'),
            ('gestion_equipos', 'sistema.supervision.equipos.crear'),
            ('gestion_equipos', 'sistema.supervision.equipos.editar'),
            ('gestion_equipos', 'sistema.supervision.equipos.asignar_miembros'),

            # Grupo: gestion_horarios
            ('gestion_horarios', 'sistema.supervision.horarios.ver'),
            ('gestion_horarios', 'sistema.supervision.horarios.crear'),
            ('gestion_horarios', 'sistema.supervision.horarios.editar'),
            ('gestion_horarios', 'sistema.supervision.horarios.aprobar'),

            # Grupo: analisis_avanzado
            ('analisis_avanzado', 'sistema.vistas.dashboards.ver'),
            ('analisis_avanzado', 'sistema.analisis.metricas.ver'),
            ('analisis_avanzado', 'sistema.analisis.reportes.ver'),
            ('analisis_avanzado', 'sistema.analisis.reportes.generar'),

            # Grupo: administracion_usuarios
            ('administracion_usuarios', 'sistema.administracion.usuarios.ver'),
            ('administracion_usuarios', 'sistema.administracion.usuarios.crear'),
            ('administracion_usuarios', 'sistema.administracion.usuarios.editar'),
            ('administracion_usuarios', 'sistema.administracion.usuarios.eliminar'),

            # Grupo: finanzas_aprobaciones
            ('finanzas_aprobaciones', 'sistema.finanzas.pagos.ver'),
            ('finanzas_aprobaciones', 'sistema.finanzas.pagos.aprobar'),

            # Grupo: configuracion_sistema
            ('configuracion_sistema', 'sistema.tecnico.configuracion.ver'),
            ('configuracion_sistema', 'sistema.tecnico.configuracion.editar'),
        ]

        for grupo_codigo, capacidad_nc in vinculaciones:
            try:
                grupo = GrupoPermisos.objects.get(codigo=grupo_codigo)
                capacidad = Capacidad.objects.get(nombre_completo=capacidad_nc)

                vinc, created = GrupoCapacidad.objects.get_or_create(
                    grupo=grupo,
                    capacidad=capacidad
                )
                if created:
                    self.stdout.write(f'  Vinculacion creada: {grupo_codigo} -> {capacidad_nc}')
            except (GrupoPermisos.DoesNotExist, Capacidad.DoesNotExist) as e:
                self.stdout.write(self.style.ERROR(f'  Error vinculando: {e}'))
