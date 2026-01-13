"""
Tests para modelos del sistema de permisos granular.

Prioridad 1: Estructura Base de Datos (8 tablas core)
- funciones
- capacidades
- funcion_capacidades
- grupos_permisos
- grupo_capacidades
- usuarios_grupos
- permisos_excepcionales
- auditoria_permisos

Filosofia: SIN roles jerarquicos, solo grupos funcionales de capacidades.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

from ..models import (
    Funcion,
    Capacidad,
    FuncionCapacidad,
    GrupoPermisos,
    GrupoCapacidad,
    UsuarioGrupo,
    PermisoExcepcional,
    AuditoriaPermiso
)

User = get_user_model()


class FuncionModelTest(TestCase):
    """Tests para modelo Funcion (Recursos del sistema)."""

    def setUp(self):
        """Setup para tests."""
        self.funcion_data = {
            'nombre': 'dashboards',
            'nombre_completo': 'sistema.vistas.dashboards',
            'descripcion': 'Visualizacion de dashboards del sistema',
            'dominio': 'vistas',
            'categoria': 'visualizacion',
            'icono': 'dashboard-icon',
            'orden_menu': 1,
            'activa': True
        }

    def test_crear_funcion(self):
        """Test: Crear funcion basica."""
        funcion = Funcion.objects.create(**self.funcion_data)

        self.assertEqual(funcion.nombre, 'dashboards')
        self.assertEqual(funcion.nombre_completo, 'sistema.vistas.dashboards')
        self.assertEqual(funcion.dominio, 'vistas')
        self.assertTrue(funcion.activa)
        self.assertIsNotNone(funcion.created_at)
        self.assertIsNotNone(funcion.updated_at)

    def test_nombre_completo_unico(self):
        """Test: nombre_completo debe ser unico."""
        Funcion.objects.create(**self.funcion_data)

        with self.assertRaises(IntegrityError):
            Funcion.objects.create(**self.funcion_data)

    def test_funcion_str_representation(self):
        """Test: Representacion string de funcion."""
        funcion = Funcion.objects.create(**self.funcion_data)

        self.assertEqual(str(funcion), 'sistema.vistas.dashboards')

    def test_funcion_defaults(self):
        """Test: Valores por defecto de funcion."""
        funcion = Funcion.objects.create(
            nombre='usuarios',
            nombre_completo='sistema.administracion.usuarios'
        )

        self.assertTrue(funcion.activa)
        self.assertIsNotNone(funcion.created_at)


class CapacidadModelTest(TestCase):
    """Tests para modelo Capacidad (Acciones sobre recursos)."""

    def setUp(self):
        """Setup para tests."""
        self.capacidad_data = {
            'nombre_completo': 'sistema.vistas.dashboards.ver',
            'descripcion': 'Permite visualizar dashboards',
            'accion': 'ver',
            'recurso': 'dashboards',
            'dominio': 'vistas',
            'nivel_sensibilidad': 'bajo',
            'requiere_auditoria': False,
            'activa': True
        }

    def test_crear_capacidad(self):
        """Test: Crear capacidad basica."""
        capacidad = Capacidad.objects.create(**self.capacidad_data)

        self.assertEqual(capacidad.nombre_completo, 'sistema.vistas.dashboards.ver')
        self.assertEqual(capacidad.accion, 'ver')
        self.assertEqual(capacidad.recurso, 'dashboards')
        self.assertEqual(capacidad.nivel_sensibilidad, 'bajo')
        self.assertFalse(capacidad.requiere_auditoria)
        self.assertTrue(capacidad.activa)

    def test_nombre_completo_unico(self):
        """Test: nombre_completo debe ser unico."""
        Capacidad.objects.create(**self.capacidad_data)

        with self.assertRaises(IntegrityError):
            Capacidad.objects.create(**self.capacidad_data)

    def test_capacidad_sensibilidad_critica_requiere_auditoria(self):
        """Test: Capacidades criticas deben requerir auditoria."""
        capacidad = Capacidad.objects.create(
            nombre_completo='sistema.finanzas.pagos.aprobar',
            accion='aprobar',
            recurso='pagos',
            dominio='finanzas',
            nivel_sensibilidad='critico',
            requiere_auditoria=True
        )

        self.assertEqual(capacidad.nivel_sensibilidad, 'critico')
        self.assertTrue(capacidad.requiere_auditoria)

    def test_capacidad_str_representation(self):
        """Test: Representacion string de capacidad."""
        capacidad = Capacidad.objects.create(**self.capacidad_data)

        self.assertEqual(str(capacidad), 'sistema.vistas.dashboards.ver')


class FuncionCapacidadModelTest(TestCase):
    """Tests para modelo FuncionCapacidad (Relacion Funcion-Capacidad)."""

    def setUp(self):
        """Setup para tests."""
        self.funcion = Funcion.objects.create(
            nombre='dashboards',
            nombre_completo='sistema.vistas.dashboards'
        )
        self.capacidad = Capacidad.objects.create(
            nombre_completo='sistema.vistas.dashboards.ver',
            accion='ver',
            recurso='dashboards',
            dominio='vistas'
        )

    def test_crear_relacion_funcion_capacidad(self):
        """Test: Crear relacion entre funcion y capacidad."""
        relacion = FuncionCapacidad.objects.create(
            funcion=self.funcion,
            capacidad=self.capacidad,
            requerida=True,
            visible_en_ui=True
        )

        self.assertEqual(relacion.funcion, self.funcion)
        self.assertEqual(relacion.capacidad, self.capacidad)
        self.assertTrue(relacion.requerida)
        self.assertTrue(relacion.visible_en_ui)

    def test_unique_together_funcion_capacidad(self):
        """Test: Combinacion funcion+capacidad debe ser unica."""
        FuncionCapacidad.objects.create(
            funcion=self.funcion,
            capacidad=self.capacidad
        )

        with self.assertRaises(IntegrityError):
            FuncionCapacidad.objects.create(
                funcion=self.funcion,
                capacidad=self.capacidad
            )


class GrupoPermisosModelTest(TestCase):
    """Tests para modelo GrupoPermisos (Grupos funcionales, NO roles jerarquicos)."""

    def setUp(self):
        """Setup para tests."""
        self.grupo_data = {
            'codigo': 'atencion_cliente',
            'nombre_display': 'Atencion al Cliente',
            'descripcion': 'Capacidades para atender clientes directamente',
            'tipo_acceso': 'operativo',
            'activo': True
        }

    def test_crear_grupo_permisos(self):
        """Test: Crear grupo de permisos funcional (sin jerarquia)."""
        grupo = GrupoPermisos.objects.create(**self.grupo_data)

        self.assertEqual(grupo.codigo, 'atencion_cliente')
        self.assertEqual(grupo.nombre_display, 'Atencion al Cliente')
        self.assertEqual(grupo.tipo_acceso, 'operativo')
        self.assertTrue(grupo.activo)
        # IMPORTANTE: NO hay campo 'nivel' o 'jerarquia'
        self.assertFalse(hasattr(grupo, 'nivel'))
        self.assertFalse(hasattr(grupo, 'jerarquia'))

    def test_codigo_unico(self):
        """Test: codigo debe ser unico."""
        GrupoPermisos.objects.create(**self.grupo_data)

        with self.assertRaises(IntegrityError):
            GrupoPermisos.objects.create(**self.grupo_data)

    def test_grupo_sin_roles_jerarquicos(self):
        """Test: Grupos son funcionales, NO jerarquicos (no admin/supervisor/agent)."""
        # Correcto: grupos funcionales descriptivos
        grupo_correcto = GrupoPermisos.objects.create(
            codigo='gestion_equipos',
            nombre_display='Gestion de Equipos',
            tipo_acceso='gestion'
        )
        self.assertEqual(grupo_correcto.codigo, 'gestion_equipos')

        # Verificar que NO usamos roles tradicionales
        # (esto es conceptual, no hay restriccion en DB, pero documentamos el patron)
        self.assertNotIn('admin', grupo_correcto.codigo.lower())
        self.assertNotIn('supervisor', grupo_correcto.codigo.lower())
        self.assertNotIn('agent', grupo_correcto.codigo.lower())

    def test_grupo_str_representation(self):
        """Test: Representacion string de grupo."""
        grupo = GrupoPermisos.objects.create(**self.grupo_data)

        self.assertEqual(str(grupo), 'Atencion al Cliente (atencion_cliente)')


class GrupoCapacidadModelTest(TestCase):
    """Tests para modelo GrupoCapacidad (Relacion Grupo-Capacidad)."""

    def setUp(self):
        """Setup para tests."""
        self.grupo = GrupoPermisos.objects.create(
            codigo='atencion_cliente',
            nombre_display='Atencion al Cliente'
        )
        self.capacidad = Capacidad.objects.create(
            nombre_completo='sistema.operaciones.llamadas.ver',
            accion='ver',
            recurso='llamadas',
            dominio='operaciones'
        )

    def test_crear_relacion_grupo_capacidad(self):
        """Test: Asignar capacidad a grupo."""
        relacion = GrupoCapacidad.objects.create(
            grupo=self.grupo,
            capacidad=self.capacidad
        )

        self.assertEqual(relacion.grupo, self.grupo)
        self.assertEqual(relacion.capacidad, self.capacidad)
        self.assertIsNotNone(relacion.created_at)

    def test_unique_together_grupo_capacidad(self):
        """Test: Combinacion grupo+capacidad debe ser unica."""
        GrupoCapacidad.objects.create(
            grupo=self.grupo,
            capacidad=self.capacidad
        )

        with self.assertRaises(IntegrityError):
            GrupoCapacidad.objects.create(
                grupo=self.grupo,
                capacidad=self.capacidad
            )


class UsuarioGrupoModelTest(TestCase):
    """Tests para modelo UsuarioGrupo (Usuario puede tener MULTIPLES grupos)."""

    def setUp(self):
        """Setup para tests."""
        self.usuario = User.objects.create_user(
            username='maria',
            email='maria@example.com',
            password='testpass123'
        )
        self.grupo1 = GrupoPermisos.objects.create(
            codigo='atencion_cliente',
            nombre_display='Atencion al Cliente'
        )
        self.grupo2 = GrupoPermisos.objects.create(
            codigo='visualizacion_metricas',
            nombre_display='Visualizacion de Metricas'
        )
        self.asignador = User.objects.create_user(
            username='admin',
            email='admin@example.com'
        )

    def test_asignar_grupo_a_usuario(self):
        """Test: Asignar un grupo a un usuario."""
        asignacion = UsuarioGrupo.objects.create(
            usuario=self.usuario,
            grupo=self.grupo1,
            asignado_por=self.asignador
        )

        self.assertEqual(asignacion.usuario, self.usuario)
        self.assertEqual(asignacion.grupo, self.grupo1)
        self.assertTrue(asignacion.activo)
        self.assertIsNone(asignacion.fecha_expiracion)

    def test_usuario_multiples_grupos(self):
        """Test: Usuario puede tener MULTIPLES grupos (sin jerarquia)."""
        # Maria tiene grupos de atencion + visualizacion
        asig1 = UsuarioGrupo.objects.create(
            usuario=self.usuario,
            grupo=self.grupo1,
            asignado_por=self.asignador
        )
        asig2 = UsuarioGrupo.objects.create(
            usuario=self.usuario,
            grupo=self.grupo2,
            asignado_por=self.asignador
        )

        grupos_usuario = UsuarioGrupo.objects.filter(
            usuario=self.usuario,
            activo=True
        )

        self.assertEqual(grupos_usuario.count(), 2)
        self.assertIn(asig1, grupos_usuario)
        self.assertIn(asig2, grupos_usuario)

    def test_unique_together_usuario_grupo(self):
        """Test: Combinacion usuario+grupo debe ser unica."""
        UsuarioGrupo.objects.create(
            usuario=self.usuario,
            grupo=self.grupo1,
            asignado_por=self.asignador
        )

        with self.assertRaises(IntegrityError):
            UsuarioGrupo.objects.create(
                usuario=self.usuario,
                grupo=self.grupo1,
                asignado_por=self.asignador
            )

    def test_asignacion_temporal(self):
        """Test: Grupo puede asignarse temporalmente con fecha_expiracion."""
        fecha_exp = timezone.now() + timedelta(days=30)

        asignacion = UsuarioGrupo.objects.create(
            usuario=self.usuario,
            grupo=self.grupo1,
            fecha_expiracion=fecha_exp,
            asignado_por=self.asignador
        )

        self.assertEqual(asignacion.fecha_expiracion, fecha_exp)

    def test_asignacion_expirada(self):
        """Test: Asignaciones expiradas no deben considerarse activas."""
        fecha_pasada = timezone.now() - timedelta(days=1)

        asignacion = UsuarioGrupo.objects.create(
            usuario=self.usuario,
            grupo=self.grupo1,
            fecha_expiracion=fecha_pasada,
            asignado_por=self.asignador
        )

        # Verificar que hay logica para filtrar expiradas
        ahora = timezone.now()
        grupos_activos = UsuarioGrupo.objects.filter(
            usuario=self.usuario,
            activo=True
        ).exclude(
            fecha_expiracion__lt=ahora
        )

        self.assertEqual(grupos_activos.count(), 0)


class PermisoExcepcionalModelTest(TestCase):
    """Tests para modelo PermisoExcepcional (Conceder/Revocar capacidades especificas)."""

    def setUp(self):
        """Setup para tests."""
        self.usuario = User.objects.create_user(
            username='carlos',
            email='carlos@example.com'
        )
        self.capacidad = Capacidad.objects.create(
            nombre_completo='sistema.direccion.presupuestos.aprobar',
            accion='aprobar',
            recurso='presupuestos',
            dominio='direccion',
            nivel_sensibilidad='critico'
        )
        self.autorizador = User.objects.create_user(
            username='director',
            email='director@example.com'
        )

    def test_conceder_permiso_excepcional(self):
        """Test: Conceder permiso excepcional temporal a usuario."""
        permiso = PermisoExcepcional.objects.create(
            usuario=self.usuario,
            capacidad=self.capacidad,
            tipo='conceder',
            fecha_inicio=timezone.now(),
            fecha_fin=timezone.now() + timedelta(days=7),
            motivo='Proyecto especial de fin de año',
            autorizado_por=self.autorizador
        )

        self.assertEqual(permiso.tipo, 'conceder')
        self.assertEqual(permiso.usuario, self.usuario)
        self.assertEqual(permiso.capacidad, self.capacidad)
        self.assertTrue(permiso.activo)

    def test_revocar_permiso_excepcional(self):
        """Test: Revocar capacidad especifica de usuario."""
        permiso = PermisoExcepcional.objects.create(
            usuario=self.usuario,
            capacidad=self.capacidad,
            tipo='revocar',
            motivo='Incidente de seguridad',
            autorizado_por=self.autorizador
        )

        self.assertEqual(permiso.tipo, 'revocar')
        self.assertEqual(permiso.motivo, 'Incidente de seguridad')

    def test_permiso_temporal(self):
        """Test: Permiso excepcional con fecha_inicio y fecha_fin."""
        inicio = timezone.now()
        fin = inicio + timedelta(days=14)

        permiso = PermisoExcepcional.objects.create(
            usuario=self.usuario,
            capacidad=self.capacidad,
            tipo='conceder',
            fecha_inicio=inicio,
            fecha_fin=fin,
            motivo='Temporal para proyecto',
            autorizado_por=self.autorizador
        )

        self.assertEqual(permiso.fecha_inicio, inicio)
        self.assertEqual(permiso.fecha_fin, fin)

    def test_permiso_permanente(self):
        """Test: Permiso excepcional sin fecha_fin (permanente)."""
        permiso = PermisoExcepcional.objects.create(
            usuario=self.usuario,
            capacidad=self.capacidad,
            tipo='conceder',
            motivo='Rol especial permanente',
            autorizado_por=self.autorizador
        )

        self.assertIsNone(permiso.fecha_fin)


class AuditoriaPermisoModelTest(TestCase):
    """Tests para modelo AuditoriaPermiso (Trazabilidad de accesos)."""

    def setUp(self):
        """Setup para tests."""
        self.usuario = User.objects.create_user(
            username='laura',
            email='laura@example.com'
        )
        self.capacidad_consultada = 'sistema.finanzas.pagos.ver'

    def test_registrar_acceso_concedido(self):
        """Test: Registrar acceso concedido en auditoria."""
        auditoria = AuditoriaPermiso.objects.create(
            usuario=self.usuario,
            capacidad=self.capacidad_consultada,
            accion_realizada='acceso_concedido',
            recurso_accedido='/api/finanzas/pagos',
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0',
            metadata={'metodo': 'GET', 'status': 200}
        )

        self.assertEqual(auditoria.accion_realizada, 'acceso_concedido')
        self.assertEqual(auditoria.usuario, self.usuario)
        self.assertEqual(auditoria.capacidad, self.capacidad_consultada)

    def test_registrar_acceso_denegado(self):
        """Test: Registrar acceso denegado en auditoria."""
        auditoria = AuditoriaPermiso.objects.create(
            usuario=self.usuario,
            capacidad='sistema.direccion.politicas.publicar',
            accion_realizada='acceso_denegado',
            recurso_accedido='/api/politicas/123/publicar',
            ip_address='192.168.1.100',
            metadata={'razon': 'usuario no tiene capacidad requerida'}
        )

        self.assertEqual(auditoria.accion_realizada, 'acceso_denegado')

    def test_auditoria_timestamp_automatico(self):
        """Test: Timestamp se asigna automaticamente."""
        auditoria = AuditoriaPermiso.objects.create(
            usuario=self.usuario,
            capacidad=self.capacidad_consultada,
            accion_realizada='acceso_concedido'
        )

        self.assertIsNotNone(auditoria.timestamp)
        self.assertLessEqual(
            auditoria.timestamp,
            timezone.now()
        )

    def test_auditoria_metadata_jsonb(self):
        """Test: metadata se almacena como JSONB."""
        metadata_compleja = {
            'request': {
                'method': 'POST',
                'path': '/api/finanzas/pagos/procesar',
                'body': {'monto': 1000}
            },
            'response': {
                'status': 200,
                'duration_ms': 234
            }
        }

        auditoria = AuditoriaPermiso.objects.create(
            usuario=self.usuario,
            capacidad='sistema.finanzas.pagos.procesar',
            accion_realizada='acceso_concedido',
            metadata=metadata_compleja
        )

        self.assertEqual(auditoria.metadata['request']['method'], 'POST')
        self.assertEqual(auditoria.metadata['response']['status'], 200)
