"""
Tests para views/viewsets de permisos.

Sistema de Permisos Granular - Prioridad 2: API Layer
TDD: Tests escritos ANTES de implementar views.py
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from callcentersite.apps.permissions.models import (
    Funcion,
    Capacidad,
    GrupoPermisos,
    GrupoCapacidad,
    UsuarioGrupo,
    PermisoExcepcional,
)


User = get_user_model()


class FuncionViewSetTestCase(TestCase):
    """Tests para FuncionViewSet."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

        # Crear funciones de prueba
        self.funcion1 = Funcion.objects.create(
            nombre='llamadas',
            nombre_completo='sistema.operaciones.llamadas',
            dominio='operaciones',
            categoria='operaciones'
        )
        self.funcion2 = Funcion.objects.create(
            nombre='tickets',
            nombre_completo='sistema.operaciones.tickets',
            dominio='operaciones',
            categoria='operaciones'
        )

    def test_listar_funciones_requiere_autenticacion(self):
        """Listar funciones requiere autenticacion."""
        response = self.client.get('/api/permissions/funciones/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listar_funciones_autenticado(self):
        """Usuario autenticado puede listar funciones."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/permissions/funciones/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_obtener_funcion_por_id(self):
        """Usuario puede obtener funcion por ID."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/permissions/funciones/{self.funcion1.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'llamadas')

    def test_filtrar_funciones_por_dominio(self):
        """Usuario puede filtrar funciones por dominio."""
        Funcion.objects.create(
            nombre='pagos',
            nombre_completo='sistema.finanzas.pagos',
            dominio='finanzas',
            categoria='finanzas'
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/permissions/funciones/?dominio=finanzas')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['dominio'], 'finanzas')


class CapacidadViewSetTestCase(TestCase):
    """Tests para CapacidadViewSet."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

        self.capacidad = Capacidad.objects.create(
            nombre_completo='sistema.operaciones.llamadas.ver',
            accion='ver',
            recurso='llamadas',
            dominio='operaciones',
            nivel_sensibilidad='bajo'
        )

    def test_listar_capacidades_requiere_autenticacion(self):
        """Listar capacidades requiere autenticacion."""
        response = self.client.get('/api/permissions/capacidades/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listar_capacidades_autenticado(self):
        """Usuario autenticado puede listar capacidades."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/permissions/capacidades/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_filtrar_capacidades_por_sensibilidad(self):
        """Usuario puede filtrar capacidades por sensibilidad."""
        Capacidad.objects.create(
            nombre_completo='sistema.finanzas.pagos.aprobar',
            accion='aprobar',
            recurso='pagos',
            dominio='finanzas',
            nivel_sensibilidad='critico'
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/permissions/capacidades/?nivel_sensibilidad=critico')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nivel_sensibilidad'], 'critico')


class GrupoPermisosViewSetTestCase(TestCase):
    """Tests para GrupoPermisosViewSet."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

        self.grupo = GrupoPermisos.objects.create(
            codigo='atencion_cliente',
            nombre_display='Atencion al Cliente',
            tipo_acceso='operativo'
        )

    def test_listar_grupos_requiere_autenticacion(self):
        """Listar grupos requiere autenticacion."""
        response = self.client.get('/api/permissions/grupos/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listar_grupos_autenticado(self):
        """Usuario autenticado puede listar grupos."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/permissions/grupos/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_obtener_grupo_detalle_incluye_capacidades(self):
        """Detalle de grupo incluye capacidades."""
        capacidad = Capacidad.objects.create(
            nombre_completo='sistema.test.test.ver',
            accion='ver',
            recurso='test',
            dominio='test'
        )
        GrupoCapacidad.objects.create(grupo=self.grupo, capacidad=capacidad)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/permissions/grupos/{self.grupo.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('capacidades', response.data)
        self.assertGreater(len(response.data['capacidades']), 0)


class UsuarioGrupoViewSetTestCase(TestCase):
    """Tests para UsuarioGrupoViewSet."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.otro_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='testpass123'
        )

        self.grupo = GrupoPermisos.objects.create(
            codigo='atencion_cliente',
            nombre_display='Atencion al Cliente',
            tipo_acceso='operativo'
        )

        self.asignacion = UsuarioGrupo.objects.create(
            usuario=self.user,
            grupo=self.grupo,
            activo=True
        )

    def test_listar_asignaciones_requiere_autenticacion(self):
        """Listar asignaciones requiere autenticacion."""
        response = self.client.get('/api/permissions/usuarios-grupos/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listar_asignaciones_autenticado(self):
        """Usuario autenticado puede listar asignaciones."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/permissions/usuarios-grupos/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_crear_asignacion_usuario_grupo(self):
        """Usuario puede crear asignacion usuario-grupo."""
        self.client.force_authenticate(user=self.user)

        data = {
            'usuario': self.otro_user.id,
            'grupo': self.grupo.id,
            'asignado_por': self.user.id,
            'activo': True
        }

        response = self.client.post('/api/permissions/usuarios-grupos/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['usuario'], self.otro_user.id)
        self.assertEqual(response.data['grupo'], self.grupo.id)

    def test_filtrar_asignaciones_por_usuario(self):
        """Usuario puede filtrar asignaciones por usuario."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/permissions/usuarios-grupos/?usuario={self.user.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        self.assertEqual(response.data['results'][0]['usuario'], self.user.id)


class MisCapacidadesViewTestCase(TestCase):
    """Tests para MisCapacidadesView (endpoint personalizado)."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

        # Crear capacidad y grupo
        self.capacidad = Capacidad.objects.create(
            nombre_completo='sistema.operaciones.llamadas.ver',
            accion='ver',
            recurso='llamadas',
            dominio='operaciones'
        )

        self.grupo = GrupoPermisos.objects.create(
            codigo='atencion_cliente',
            nombre_display='Atencion al Cliente',
            tipo_acceso='operativo'
        )

        GrupoCapacidad.objects.create(grupo=self.grupo, capacidad=self.capacidad)
        UsuarioGrupo.objects.create(usuario=self.user, grupo=self.grupo, activo=True)

    def test_obtener_mis_capacidades_requiere_autenticacion(self):
        """Endpoint requiere autenticacion."""
        response = self.client.get('/api/permissions/mis-capacidades/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtener_mis_capacidades_autenticado(self):
        """Usuario autenticado obtiene sus capacidades."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/permissions/mis-capacidades/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('capacidades', response.data)
        self.assertIn('sistema.operaciones.llamadas.ver', response.data['capacidades'])


class VerificarPermisoViewTestCase(TestCase):
    """Tests para VerificarPermisoView (endpoint de verificacion)."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

        self.capacidad = Capacidad.objects.create(
            nombre_completo='sistema.operaciones.llamadas.ver',
            accion='ver',
            recurso='llamadas',
            dominio='operaciones'
        )

        self.grupo = GrupoPermisos.objects.create(
            codigo='atencion_cliente',
            nombre_display='Atencion al Cliente',
            tipo_acceso='operativo'
        )

        GrupoCapacidad.objects.create(grupo=self.grupo, capacidad=self.capacidad)
        UsuarioGrupo.objects.create(usuario=self.user, grupo=self.grupo, activo=True)

    def test_verificar_permiso_requiere_autenticacion(self):
        """Endpoint requiere autenticacion."""
        response = self.client.post('/api/permissions/verificar-permiso/', {
            'capacidad': 'sistema.operaciones.llamadas.ver'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verificar_permiso_que_usuario_tiene(self):
        """Usuario puede verificar permiso que tiene."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/permissions/verificar-permiso/', {
            'capacidad': 'sistema.operaciones.llamadas.ver'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['tiene_permiso'])

    def test_verificar_permiso_que_usuario_no_tiene(self):
        """Usuario puede verificar permiso que NO tiene."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/permissions/verificar-permiso/', {
            'capacidad': 'sistema.finanzas.pagos.aprobar'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['tiene_permiso'])
