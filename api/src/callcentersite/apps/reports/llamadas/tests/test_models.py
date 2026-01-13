"""
Tests para modelos de Llamadas.

Sistema de Permisos Granular - Prioridad 3: Módulo Operativo Llamadas
TDD: Tests escritos ANTES de implementar models.py
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from callcentersite.apps.llamadas.models import (
    Llamada,
    EstadoLlamada,
    TipoLlamada,
    LlamadaTranscripcion,
    LlamadaGrabacion,
)


User = get_user_model()


class EstadoLlamadaModelTestCase(TestCase):
    """Tests para modelo EstadoLlamada."""

    def test_crear_estado_llamada(self):
        """Crear estado de llamada exitosamente."""
        estado = EstadoLlamada.objects.create(
            codigo='EN_CURSO',
            nombre='En Curso',
            descripcion='Llamada en progreso',
            es_final=False
        )

        self.assertEqual(estado.codigo, 'EN_CURSO')
        self.assertEqual(estado.nombre, 'En Curso')
        self.assertFalse(estado.es_final)
        self.assertTrue(estado.activo)

    def test_codigo_estado_debe_ser_unico(self):
        """Codigo de estado debe ser unico."""
        EstadoLlamada.objects.create(codigo='COMPLETADA', nombre='Completada')

        with self.assertRaises(Exception):
            EstadoLlamada.objects.create(codigo='COMPLETADA', nombre='Otro')


class TipoLlamadaModelTestCase(TestCase):
    """Tests para modelo TipoLlamada."""

    def test_crear_tipo_llamada(self):
        """Crear tipo de llamada exitosamente."""
        tipo = TipoLlamada.objects.create(
            codigo='ENTRANTE',
            nombre='Llamada Entrante',
            descripcion='Cliente llama al call center'
        )

        self.assertEqual(tipo.codigo, 'ENTRANTE')
        self.assertTrue(tipo.activo)


class LlamadaModelTestCase(TestCase):
    """Tests para modelo Llamada."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.agente = User.objects.create_user(
            username='agente1',
            email='agente1@test.com',
            password='test123'
        )

        self.estado_en_curso = EstadoLlamada.objects.create(
            codigo='EN_CURSO',
            nombre='En Curso',
            es_final=False
        )

        self.estado_completada = EstadoLlamada.objects.create(
            codigo='COMPLETADA',
            nombre='Completada',
            es_final=True
        )

        self.tipo_entrante = TipoLlamada.objects.create(
            codigo='ENTRANTE',
            nombre='Entrante'
        )

    def test_crear_llamada_minima(self):
        """Crear llamada con campos minimos."""
        llamada = Llamada.objects.create(
            numero_telefono='+521234567890',
            tipo=self.tipo_entrante,
            estado=self.estado_en_curso,
            agente=self.agente
        )

        self.assertIsNotNone(llamada.id)
        self.assertEqual(llamada.numero_telefono, '+521234567890')
        self.assertEqual(llamada.agente, self.agente)
        self.assertIsNotNone(llamada.fecha_inicio)
        self.assertIsNone(llamada.fecha_fin)

    def test_llamada_genera_codigo_unico(self):
        """Llamada genera codigo unico automaticamente."""
        llamada1 = Llamada.objects.create(
            numero_telefono='+521234567890',
            tipo=self.tipo_entrante,
            estado=self.estado_en_curso,
            agente=self.agente
        )

        llamada2 = Llamada.objects.create(
            numero_telefono='+529876543210',
            tipo=self.tipo_entrante,
            estado=self.estado_en_curso,
            agente=self.agente
        )

        self.assertIsNotNone(llamada1.codigo)
        self.assertIsNotNone(llamada2.codigo)
        self.assertNotEqual(llamada1.codigo, llamada2.codigo)

    def test_calcular_duracion_llamada(self):
        """Calcular duracion de llamada correctamente."""
        llamada = Llamada.objects.create(
            numero_telefono='+521234567890',
            tipo=self.tipo_entrante,
            estado=self.estado_en_curso,
            agente=self.agente,
            fecha_inicio=timezone.now()
        )

        # Simular fin de llamada 5 minutos despues
        llamada.fecha_fin = llamada.fecha_inicio + timedelta(minutes=5)
        llamada.save()

        duracion = llamada.calcular_duracion()
        self.assertEqual(duracion, 300)  # 5 minutos = 300 segundos

    def test_llamada_sin_fecha_fin_duracion_none(self):
        """Llamada sin fecha_fin retorna None en duracion."""
        llamada = Llamada.objects.create(
            numero_telefono='+521234567890',
            tipo=self.tipo_entrante,
            estado=self.estado_en_curso,
            agente=self.agente
        )

        duracion = llamada.calcular_duracion()
        self.assertIsNone(duracion)

    def test_llamada_con_cliente_asociado(self):
        """Llamada puede tener cliente asociado."""
        llamada = Llamada.objects.create(
            numero_telefono='+521234567890',
            tipo=self.tipo_entrante,
            estado=self.estado_en_curso,
            agente=self.agente,
            cliente_nombre='Juan Perez',
            cliente_email='juan@example.com'
        )

        self.assertEqual(llamada.cliente_nombre, 'Juan Perez')
        self.assertEqual(llamada.cliente_email, 'juan@example.com')

    def test_llamada_con_metadata(self):
        """Llamada puede almacenar metadata JSON."""
        metadata = {
            'motivo': 'consulta',
            'producto': 'tarjeta_credito',
            'prioridad': 'alta'
        }

        llamada = Llamada.objects.create(
            numero_telefono='+521234567890',
            tipo=self.tipo_entrante,
            estado=self.estado_en_curso,
            agente=self.agente,
            metadata=metadata
        )

        self.assertEqual(llamada.metadata['motivo'], 'consulta')
        self.assertEqual(llamada.metadata['prioridad'], 'alta')

    def test_cambiar_estado_llamada(self):
        """Cambiar estado de llamada."""
        llamada = Llamada.objects.create(
            numero_telefono='+521234567890',
            tipo=self.tipo_entrante,
            estado=self.estado_en_curso,
            agente=self.agente
        )

        llamada.estado = self.estado_completada
        llamada.save()

        self.assertEqual(llamada.estado.codigo, 'COMPLETADA')
        self.assertTrue(llamada.estado.es_final)


class LlamadaTranscripcionModelTestCase(TestCase):
    """Tests para modelo LlamadaTranscripcion."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.agente = User.objects.create_user(
            username='agente1',
            email='agente1@test.com',
            password='test123'
        )

        estado = EstadoLlamada.objects.create(codigo='EN_CURSO', nombre='En Curso')
        tipo = TipoLlamada.objects.create(codigo='ENTRANTE', nombre='Entrante')

        self.llamada = Llamada.objects.create(
            numero_telefono='+521234567890',
            tipo=tipo,
            estado=estado,
            agente=self.agente
        )

    def test_crear_transcripcion(self):
        """Crear transcripcion de llamada."""
        transcripcion = LlamadaTranscripcion.objects.create(
            llamada=self.llamada,
            texto='Cliente: Hola, necesito ayuda con mi cuenta',
            timestamp_inicio=0,
            timestamp_fin=5,
            hablante='cliente'
        )

        self.assertEqual(transcripcion.llamada, self.llamada)
        self.assertEqual(transcripcion.hablante, 'cliente')
        self.assertIn('ayuda', transcripcion.texto)

    def test_transcripcion_con_confianza(self):
        """Transcripcion puede tener nivel de confianza."""
        transcripcion = LlamadaTranscripcion.objects.create(
            llamada=self.llamada,
            texto='Texto transcrito',
            timestamp_inicio=0,
            timestamp_fin=3,
            hablante='agente',
            confianza=0.95
        )

        self.assertEqual(transcripcion.confianza, 0.95)


class LlamadaGrabacionModelTestCase(TestCase):
    """Tests para modelo LlamadaGrabacion."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.agente = User.objects.create_user(
            username='agente1',
            email='agente1@test.com',
            password='test123'
        )

        estado = EstadoLlamada.objects.create(codigo='EN_CURSO', nombre='En Curso')
        tipo = TipoLlamada.objects.create(codigo='ENTRANTE', nombre='Entrante')

        self.llamada = Llamada.objects.create(
            numero_telefono='+521234567890',
            tipo=tipo,
            estado=estado,
            agente=self.agente
        )

    def test_crear_grabacion(self):
        """Crear grabacion de llamada."""
        grabacion = LlamadaGrabacion.objects.create(
            llamada=self.llamada,
            archivo_url='https://storage.example.com/calls/123.mp3',
            formato='mp3',
            duracion_segundos=300
        )

        self.assertEqual(grabacion.llamada, self.llamada)
        self.assertEqual(grabacion.formato, 'mp3')
        self.assertEqual(grabacion.duracion_segundos, 300)

    def test_grabacion_tamano_archivo(self):
        """Grabacion almacena tamano de archivo."""
        grabacion = LlamadaGrabacion.objects.create(
            llamada=self.llamada,
            archivo_url='https://storage.example.com/calls/123.mp3',
            formato='mp3',
            duracion_segundos=300,
            tamano_bytes=2048000  # ~2MB
        )

        self.assertEqual(grabacion.tamano_bytes, 2048000)
