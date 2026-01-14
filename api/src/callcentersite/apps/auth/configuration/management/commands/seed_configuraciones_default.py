"""
Django management command para poblar configuraciones por defecto del sistema.

Crea configuraciones iniciales para:
- Seguridad (timeouts, politicas de password)
- Notificaciones (email, SMS, push)
- Llamadas (duraciones, grabacion)
- Tickets (auto-asignacion, SLA)
- Reportes (formatos, programacion)
- Sistema (mantenimiento, logs)

Uso:
    python manage.py seed_configuraciones_default

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 9)
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from callcentersite.apps.configuration.models import Configuracion


class Command(BaseCommand):
    help = 'Pobla configuraciones por defecto del sistema'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de configuraciones por defecto...')

        with transaction.atomic():
            self.crear_configuraciones_seguridad()
            self.crear_configuraciones_notificaciones()
            self.crear_configuraciones_llamadas()
            self.crear_configuraciones_tickets()
            self.crear_configuraciones_reportes()
            self.crear_configuraciones_sistema()
            self.crear_configuraciones_integraciones()

        total = Configuracion.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'Seed completado: {total} configuraciones creadas')
        )

    def crear_configuraciones_seguridad(self):
        """Crea configuraciones de seguridad."""
        self.stdout.write('Creando configuraciones de seguridad...')

        configs = [
            {
                'categoria': 'seguridad',
                'clave': 'seguridad.session_timeout',
                'valor': '900',
                'tipo_dato': 'integer',
                'valor_default': '900',
                'descripcion': 'Timeout de sesion en segundos (15 minutos)',
            },
            {
                'categoria': 'seguridad',
                'clave': 'seguridad.password_min_length',
                'valor': '8',
                'tipo_dato': 'integer',
                'valor_default': '8',
                'descripcion': 'Longitud minima de password',
            },
            {
                'categoria': 'seguridad',
                'clave': 'seguridad.password_require_uppercase',
                'valor': 'true',
                'tipo_dato': 'boolean',
                'valor_default': 'true',
                'descripcion': 'Requerir mayusculas en password',
            },
            {
                'categoria': 'seguridad',
                'clave': 'seguridad.password_require_numbers',
                'valor': 'true',
                'tipo_dato': 'boolean',
                'valor_default': 'true',
                'descripcion': 'Requerir numeros en password',
            },
            {
                'categoria': 'seguridad',
                'clave': 'seguridad.max_login_attempts',
                'valor': '5',
                'tipo_dato': 'integer',
                'valor_default': '5',
                'descripcion': 'Maximo de intentos de login antes de bloqueo',
            },
            {
                'categoria': 'seguridad',
                'clave': 'seguridad.lockout_duration_minutes',
                'valor': '30',
                'tipo_dato': 'integer',
                'valor_default': '30',
                'descripcion': 'Duracion de bloqueo despues de intentos fallidos',
            },
        ]

        for config_data in configs:
            Configuracion.objects.get_or_create(
                clave=config_data['clave'],
                defaults=config_data,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(configs)} configs de seguridad'))

    def crear_configuraciones_notificaciones(self):
        """Crea configuraciones de notificaciones."""
        self.stdout.write('Creando configuraciones de notificaciones...')

        configs = [
            {
                'categoria': 'notificaciones',
                'clave': 'notificaciones.email_habilitado',
                'valor': 'true',
                'tipo_dato': 'boolean',
                'valor_default': 'true',
                'descripcion': 'Habilitar notificaciones por email',
            },
            {
                'categoria': 'notificaciones',
                'clave': 'notificaciones.sms_habilitado',
                'valor': 'false',
                'tipo_dato': 'boolean',
                'valor_default': 'false',
                'descripcion': 'Habilitar notificaciones por SMS',
            },
            {
                'categoria': 'notificaciones',
                'clave': 'notificaciones.email_desde',
                'valor': 'noreply@callcenter.com',
                'tipo_dato': 'email',
                'valor_default': 'noreply@callcenter.com',
                'descripcion': 'Email remitente para notificaciones',
            },
            {
                'categoria': 'notificaciones',
                'clave': 'notificaciones.enviar_resumen_diario',
                'valor': 'true',
                'tipo_dato': 'boolean',
                'valor_default': 'true',
                'descripcion': 'Enviar resumen diario a supervisores',
            },
        ]

        for config_data in configs:
            Configuracion.objects.get_or_create(
                clave=config_data['clave'],
                defaults=config_data,
            )

        self.stdout.write(
            self.style.SUCCESS(f'  {len(configs)} configs de notificaciones')
        )

    def crear_configuraciones_llamadas(self):
        """Crea configuraciones de llamadas."""
        self.stdout.write('Creando configuraciones de llamadas...')

        configs = [
            {
                'categoria': 'llamadas',
                'clave': 'llamadas.max_duracion_segundos',
                'valor': '3600',
                'tipo_dato': 'integer',
                'valor_default': '3600',
                'descripcion': 'Duracion maxima de llamada en segundos (1 hora)',
            },
            {
                'categoria': 'llamadas',
                'clave': 'llamadas.grabar_llamadas',
                'valor': 'true',
                'tipo_dato': 'boolean',
                'valor_default': 'true',
                'descripcion': 'Grabar todas las llamadas',
            },
            {
                'categoria': 'llamadas',
                'clave': 'llamadas.retencion_grabaciones_dias',
                'valor': '90',
                'tipo_dato': 'integer',
                'valor_default': '90',
                'descripcion': 'Dias de retencion de grabaciones',
            },
            {
                'categoria': 'llamadas',
                'clave': 'llamadas.timeout_no_respuesta_segundos',
                'valor': '30',
                'tipo_dato': 'integer',
                'valor_default': '30',
                'descripcion': 'Timeout antes de considerar no respondida',
            },
        ]

        for config_data in configs:
            Configuracion.objects.get_or_create(
                clave=config_data['clave'],
                defaults=config_data,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(configs)} configs de llamadas'))

    def crear_configuraciones_tickets(self):
        """Crea configuraciones de tickets."""
        self.stdout.write('Creando configuraciones de tickets...')

        configs = [
            {
                'categoria': 'tickets',
                'clave': 'tickets.auto_asignar',
                'valor': 'false',
                'tipo_dato': 'boolean',
                'valor_default': 'false',
                'descripcion': 'Auto-asignar tickets a agentes disponibles',
            },
            {
                'categoria': 'tickets',
                'clave': 'tickets.sla_respuesta_horas',
                'valor': '24',
                'tipo_dato': 'integer',
                'valor_default': '24',
                'descripcion': 'SLA de primera respuesta en horas',
            },
            {
                'categoria': 'tickets',
                'clave': 'tickets.sla_resolucion_horas',
                'valor': '72',
                'tipo_dato': 'integer',
                'valor_default': '72',
                'descripcion': 'SLA de resolucion en horas',
            },
            {
                'categoria': 'tickets',
                'clave': 'tickets.permitir_reasignacion',
                'valor': 'true',
                'tipo_dato': 'boolean',
                'valor_default': 'true',
                'descripcion': 'Permitir reasignar tickets entre agentes',
            },
        ]

        for config_data in configs:
            Configuracion.objects.get_or_create(
                clave=config_data['clave'],
                defaults=config_data,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(configs)} configs de tickets'))

    def crear_configuraciones_reportes(self):
        """Crea configuraciones de reportes."""
        self.stdout.write('Creando configuraciones de reportes...')

        configs = [
            {
                'categoria': 'reportes',
                'clave': 'reportes.formato_default',
                'valor': 'pdf',
                'tipo_dato': 'string',
                'valor_default': 'pdf',
                'descripcion': 'Formato por defecto para reportes (pdf, excel, csv)',
            },
            {
                'categoria': 'reportes',
                'clave': 'reportes.programar_automaticos',
                'valor': 'true',
                'tipo_dato': 'boolean',
                'valor_default': 'true',
                'descripcion': 'Permitir programar reportes automaticos',
            },
            {
                'categoria': 'reportes',
                'clave': 'reportes.retencion_dias',
                'valor': '365',
                'tipo_dato': 'integer',
                'valor_default': '365',
                'descripcion': 'Dias de retencion de reportes generados',
            },
        ]

        for config_data in configs:
            Configuracion.objects.get_or_create(
                clave=config_data['clave'],
                defaults=config_data,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(configs)} configs de reportes'))

    def crear_configuraciones_sistema(self):
        """Crea configuraciones del sistema."""
        self.stdout.write('Creando configuraciones del sistema...')

        configs = [
            {
                'categoria': 'sistema',
                'clave': 'sistema.modo_mantenimiento',
                'valor': 'false',
                'tipo_dato': 'boolean',
                'valor_default': 'false',
                'descripcion': 'Activar modo de mantenimiento',
            },
            {
                'categoria': 'sistema',
                'clave': 'sistema.log_level',
                'valor': 'INFO',
                'tipo_dato': 'string',
                'valor_default': 'INFO',
                'descripcion': 'Nivel de logging (DEBUG, INFO, WARNING, ERROR)',
            },
            {
                'categoria': 'sistema',
                'clave': 'sistema.max_upload_size_mb',
                'valor': '10',
                'tipo_dato': 'integer',
                'valor_default': '10',
                'descripcion': 'Tamano maximo de archivos subidos en MB',
            },
        ]

        for config_data in configs:
            Configuracion.objects.get_or_create(
                clave=config_data['clave'],
                defaults=config_data,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(configs)} configs del sistema'))

    def crear_configuraciones_integraciones(self):
        """Crea configuraciones de integraciones."""
        self.stdout.write('Creando configuraciones de integraciones...')

        configs = [
            {
                'categoria': 'integraciones',
                'clave': 'integraciones.api_timeout_segundos',
                'valor': '30',
                'tipo_dato': 'integer',
                'valor_default': '30',
                'descripcion': 'Timeout para llamadas a APIs externas',
            },
            {
                'categoria': 'integraciones',
                'clave': 'integraciones.max_reintentos',
                'valor': '3',
                'tipo_dato': 'integer',
                'valor_default': '3',
                'descripcion': 'Maximo de reintentos para integraciones fallidas',
            },
        ]

        for config_data in configs:
            Configuracion.objects.get_or_create(
                clave=config_data['clave'],
                defaults=config_data,
            )

        self.stdout.write(
            self.style.SUCCESS(f'  {len(configs)} configs de integraciones')
        )
