"""
Tests para serializers de permisos.

Sistema de Permisos Granular - Prioridad 2: API Layer
TDD: Tests escritos ANTES de implementar serializers.py
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from callcentersite.apps.permissions.models import (
    Funcion,
    Capacidad,
    GrupoPermisos,
    UsuarioGrupo,
)
from callcentersite.apps.permissions.serializers import (
    FuncionSerializer,
    CapacidadSerializer,
    GrupoPermisosSerializer,
    UsuarioGrupoSerializer,
    UsuarioGrupoCreateSerializer,
)


User = get_user_model()


class FuncionSerializerTestCase(TestCase):
    """Tests para FuncionSerializer."""

    def test_serializer_contiene_campos_esperados(self):
        """Serializer contiene todos los campos necesarios."""
        serializer = FuncionSerializer()
        campos = set(serializer.fields.keys())

        campos_esperados = {
            'id', 'nombre', 'nombre_completo', 'descripcion',
            'dominio', 'categoria', 'icono', 'orden_menu',
            'activa', 'created_at', 'updated_at'
        }

        self.assertEqual(campos, campos_esperados)

    def test_serializar_funcion_exitosamente(self):
        """Serializa funcion correctamente."""
        funcion = Funcion.objects.create(
            nombre='llamadas',
            nombre_completo='sistema.operaciones.llamadas',
            dominio='operaciones',
            categoria='operaciones'
        )

        serializer = FuncionSerializer(funcion)
        data = serializer.data

        self.assertEqual(data['nombre'], 'llamadas')
        self.assertEqual(data['nombre_completo'], 'sistema.operaciones.llamadas')
        self.assertEqual(data['dominio'], 'operaciones')

    def test_deserializar_funcion_exitosamente(self):
        """Deserializa y crea funcion correctamente."""
        data = {
            'nombre': 'tickets',
            'nombre_completo': 'sistema.operaciones.tickets',
            'descripcion': 'Gestion de tickets',
            'dominio': 'operaciones',
            'categoria': 'operaciones'
        }

        serializer = FuncionSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        funcion = serializer.save()
        self.assertEqual(funcion.nombre, 'tickets')
        self.assertTrue(funcion.activa)


class CapacidadSerializerTestCase(TestCase):
    """Tests para CapacidadSerializer."""

    def test_serializer_contiene_campos_esperados(self):
        """Serializer contiene todos los campos necesarios."""
        serializer = CapacidadSerializer()
        campos = set(serializer.fields.keys())

        campos_esperados = {
            'id', 'nombre_completo', 'descripcion', 'accion',
            'recurso', 'dominio', 'nivel_sensibilidad',
            'requiere_auditoria', 'activa', 'created_at'
        }

        self.assertEqual(campos, campos_esperados)

    def test_serializar_capacidad_exitosamente(self):
        """Serializa capacidad correctamente."""
        capacidad = Capacidad.objects.create(
            nombre_completo='sistema.operaciones.llamadas.ver',
            accion='ver',
            recurso='llamadas',
            dominio='operaciones',
            nivel_sensibilidad='bajo'
        )

        serializer = CapacidadSerializer(capacidad)
        data = serializer.data

        self.assertEqual(data['nombre_completo'], 'sistema.operaciones.llamadas.ver')
        self.assertEqual(data['accion'], 'ver')
        self.assertEqual(data['nivel_sensibilidad'], 'bajo')
        self.assertFalse(data['requiere_auditoria'])

    def test_validar_nivel_sensibilidad_invalido(self):
        """Valida que nivel_sensibilidad debe ser valor valido."""
        data = {
            'nombre_completo': 'sistema.test.test.test',
            'accion': 'test',
            'recurso': 'test',
            'dominio': 'test',
            'nivel_sensibilidad': 'invalido'
        }

        serializer = CapacidadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('nivel_sensibilidad', serializer.errors)


class GrupoPermisosSerializerTestCase(TestCase):
    """Tests para GrupoPermisosSerializer."""

    def test_serializer_contiene_campos_esperados(self):
        """Serializer contiene todos los campos necesarios."""
        serializer = GrupoPermisosSerializer()
        campos = set(serializer.fields.keys())

        campos_esperados = {
            'id', 'codigo', 'nombre_display', 'descripcion',
            'tipo_acceso', 'activo', 'created_at', 'updated_at',
            'capacidades_count'
        }

        self.assertEqual(campos, campos_esperados)

    def test_serializar_grupo_con_capacidades_count(self):
        """Serializer incluye count de capacidades."""
        from callcentersite.apps.permissions.models import GrupoCapacidad

        grupo = GrupoPermisos.objects.create(
            codigo='test_grupo',
            nombre_display='Test Grupo',
            tipo_acceso='operativo'
        )

        capacidad1 = Capacidad.objects.create(
            nombre_completo='sistema.test.test1.ver',
            accion='ver',
            recurso='test1',
            dominio='test'
        )
        capacidad2 = Capacidad.objects.create(
            nombre_completo='sistema.test.test2.ver',
            accion='ver',
            recurso='test2',
            dominio='test'
        )

        GrupoCapacidad.objects.create(grupo=grupo, capacidad=capacidad1)
        GrupoCapacidad.objects.create(grupo=grupo, capacidad=capacidad2)

        serializer = GrupoPermisosSerializer(grupo)
        data = serializer.data

        self.assertEqual(data['capacidades_count'], 2)

    def test_codigo_debe_ser_unico(self):
        """Valida que codigo debe ser unico."""
        GrupoPermisos.objects.create(
            codigo='codigo_existente',
            nombre_display='Grupo 1',
            tipo_acceso='operativo'
        )

        data = {
            'codigo': 'codigo_existente',
            'nombre_display': 'Grupo 2',
            'tipo_acceso': 'operativo'
        }

        serializer = GrupoPermisosSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('codigo', serializer.errors)


class UsuarioGrupoSerializerTestCase(TestCase):
    """Tests para UsuarioGrupoSerializer."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

        self.grupo = GrupoPermisos.objects.create(
            codigo='test_grupo',
            nombre_display='Test Grupo',
            tipo_acceso='operativo'
        )

    def test_serializer_contiene_campos_esperados(self):
        """Serializer contiene todos los campos necesarios."""
        serializer = UsuarioGrupoSerializer()
        campos = set(serializer.fields.keys())

        campos_esperados = {
            'id', 'usuario', 'grupo', 'fecha_asignacion',
            'fecha_expiracion', 'asignado_por', 'activo',
            'usuario_username', 'grupo_nombre'
        }

        self.assertEqual(campos, campos_esperados)

    def test_serializar_asignacion_usuario_grupo(self):
        """Serializa asignacion correctamente."""
        asignacion = UsuarioGrupo.objects.create(
            usuario=self.user,
            grupo=self.grupo,
            activo=True
        )

        serializer = UsuarioGrupoSerializer(asignacion)
        data = serializer.data

        self.assertEqual(data['usuario'], self.user.id)
        self.assertEqual(data['grupo'], self.grupo.id)
        self.assertEqual(data['usuario_username'], self.user.username)
        self.assertEqual(data['grupo_nombre'], self.grupo.nombre_display)
        self.assertTrue(data['activo'])


class UsuarioGrupoCreateSerializerTestCase(TestCase):
    """Tests para UsuarioGrupoCreateSerializer."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )

        self.grupo = GrupoPermisos.objects.create(
            codigo='test_grupo',
            nombre_display='Test Grupo',
            tipo_acceso='operativo'
        )

    def test_crear_asignacion_exitosamente(self):
        """Crea asignacion usuario-grupo exitosamente."""
        data = {
            'usuario': self.user.id,
            'grupo': self.grupo.id,
            'asignado_por': self.admin.id
        }

        serializer = UsuarioGrupoCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        asignacion = serializer.save()
        self.assertEqual(asignacion.usuario, self.user)
        self.assertEqual(asignacion.grupo, self.grupo)
        self.assertEqual(asignacion.asignado_por, self.admin)
        self.assertTrue(asignacion.activo)

    def test_validar_asignacion_duplicada(self):
        """Valida que no se puede asignar mismo grupo dos veces."""
        UsuarioGrupo.objects.create(
            usuario=self.user,
            grupo=self.grupo,
            activo=True
        )

        data = {
            'usuario': self.user.id,
            'grupo': self.grupo.id
        }

        serializer = UsuarioGrupoCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_crear_asignacion_con_fecha_expiracion(self):
        """Crea asignacion con fecha de expiracion."""
        from datetime import timedelta
        from django.utils import timezone

        fecha_exp = timezone.now() + timedelta(days=30)

        data = {
            'usuario': self.user.id,
            'grupo': self.grupo.id,
            'fecha_expiracion': fecha_exp.isoformat()
        }

        serializer = UsuarioGrupoCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        asignacion = serializer.save()
        self.assertIsNotNone(asignacion.fecha_expiracion)
