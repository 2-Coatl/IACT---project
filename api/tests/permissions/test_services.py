"""
Tests para PermisoService.

Sistema de Permisos Granular - Prioridad 1
TDD: Tests escritos ANTES de implementar services.py
"""

from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from callcentersite.apps.permissions.models import (
    Funcion,
    Capacidad,
    FuncionCapacidad,
    GrupoPermisos,
    GrupoCapacidad,
    UsuarioGrupo,
    PermisoExcepcional,
    AuditoriaPermiso,
)
from callcentersite.apps.permissions.services import PermisoService


User = get_user_model()


class PermisoServiceTestCase(TestCase):
    """Tests para el servicio de permisos."""

    def setUp(self):
        """Configurar datos de prueba."""
        # Crear usuarios
        self.user_agent = User.objects.create_user(
            username="agent1",
            email="agent1@test.com",
            password="testpass123"
        )
        self.user_coordinador = User.objects.create_user(
            username="coordinador1",
            email="coord1@test.com",
            password="testpass123"
        )
        self.user_sin_permisos = User.objects.create_user(
            username="user_no_perms",
            email="noperms@test.com",
            password="testpass123"
        )

        # Crear funciones
        self.funcion_llamadas = Funcion.objects.create(
            nombre="llamadas",
            nombre_completo="sistema.operaciones.llamadas",
            dominio="operaciones",
            categoria="operaciones"
        )
        self.funcion_pagos = Funcion.objects.create(
            nombre="pagos",
            nombre_completo="sistema.finanzas.pagos",
            dominio="finanzas",
            categoria="finanzas"
        )

        # Crear capacidades
        self.cap_llamadas_ver = Capacidad.objects.create(
            nombre_completo="sistema.operaciones.llamadas.ver",
            accion="ver",
            recurso="llamadas",
            dominio="operaciones",
            nivel_sensibilidad="bajo"
        )
        self.cap_llamadas_realizar = Capacidad.objects.create(
            nombre_completo="sistema.operaciones.llamadas.realizar",
            accion="realizar",
            recurso="llamadas",
            dominio="operaciones",
            nivel_sensibilidad="normal"
        )
        self.cap_pagos_aprobar = Capacidad.objects.create(
            nombre_completo="sistema.finanzas.pagos.aprobar",
            accion="aprobar",
            recurso="pagos",
            dominio="finanzas",
            nivel_sensibilidad="critico",
            requiere_auditoria=True
        )

        # Vincular capacidades a funciones
        FuncionCapacidad.objects.create(
            funcion=self.funcion_llamadas,
            capacidad=self.cap_llamadas_ver,
            requerida=True
        )
        FuncionCapacidad.objects.create(
            funcion=self.funcion_llamadas,
            capacidad=self.cap_llamadas_realizar,
            requerida=False
        )
        FuncionCapacidad.objects.create(
            funcion=self.funcion_pagos,
            capacidad=self.cap_pagos_aprobar,
            requerida=True
        )

        # Crear grupos
        self.grupo_atencion = GrupoPermisos.objects.create(
            codigo="atencion_cliente",
            nombre_display="Atencion al Cliente",
            descripcion="Grupo para agentes de atencion",
            tipo_acceso="operativo",
            activo=True
        )
        self.grupo_coordinacion = GrupoPermisos.objects.create(
            codigo="coordinacion_equipos",
            nombre_display="Coordinacion de Equipos",
            descripcion="Grupo para coordinadores",
            tipo_acceso="gestion",
            activo=True
        )

        # Vincular capacidades a grupos
        GrupoCapacidad.objects.create(
            grupo=self.grupo_atencion,
            capacidad=self.cap_llamadas_ver
        )
        GrupoCapacidad.objects.create(
            grupo=self.grupo_atencion,
            capacidad=self.cap_llamadas_realizar
        )
        GrupoCapacidad.objects.create(
            grupo=self.grupo_coordinacion,
            capacidad=self.cap_llamadas_ver
        )
        GrupoCapacidad.objects.create(
            grupo=self.grupo_coordinacion,
            capacidad=self.cap_llamadas_realizar
        )

        # Asignar usuarios a grupos
        UsuarioGrupo.objects.create(
            usuario=self.user_agent,
            grupo=self.grupo_atencion,
            activo=True
        )
        UsuarioGrupo.objects.create(
            usuario=self.user_coordinador,
            grupo=self.grupo_coordinacion,
            activo=True
        )

    def test_usuario_tiene_permiso_via_grupo(self):
        """Usuario tiene permiso si su grupo activo lo otorga."""
        tiene_permiso = PermisoService.usuario_tiene_permiso(
            usuario_id=self.user_agent.id,
            capacidad_requerida="sistema.operaciones.llamadas.ver"
        )
        self.assertTrue(tiene_permiso)

    def test_usuario_no_tiene_permiso_sin_grupo(self):
        """Usuario sin grupos no tiene permisos."""
        tiene_permiso = PermisoService.usuario_tiene_permiso(
            usuario_id=self.user_sin_permisos.id,
            capacidad_requerida="sistema.operaciones.llamadas.ver"
        )
        self.assertFalse(tiene_permiso)

    def test_usuario_no_tiene_permiso_capacidad_no_asignada(self):
        """Usuario no tiene permiso si capacidad no esta en sus grupos."""
        tiene_permiso = PermisoService.usuario_tiene_permiso(
            usuario_id=self.user_agent.id,
            capacidad_requerida="sistema.finanzas.pagos.aprobar"
        )
        self.assertFalse(tiene_permiso)

    def test_usuario_con_grupo_inactivo_no_tiene_permiso(self):
        """Usuario con grupo inactivo no tiene permisos de ese grupo."""
        # Desactivar el grupo
        asignacion = UsuarioGrupo.objects.get(
            usuario=self.user_agent,
            grupo=self.grupo_atencion
        )
        asignacion.activo = False
        asignacion.save()

        tiene_permiso = PermisoService.usuario_tiene_permiso(
            usuario_id=self.user_agent.id,
            capacidad_requerida="sistema.operaciones.llamadas.ver"
        )
        self.assertFalse(tiene_permiso)

    def test_usuario_con_grupo_expirado_no_tiene_permiso(self):
        """Usuario con grupo expirado no tiene permisos de ese grupo."""
        # Expirar el grupo
        asignacion = UsuarioGrupo.objects.get(
            usuario=self.user_agent,
            grupo=self.grupo_atencion
        )
        asignacion.fecha_expiracion = timezone.now() - timedelta(days=1)
        asignacion.save()

        tiene_permiso = PermisoService.usuario_tiene_permiso(
            usuario_id=self.user_agent.id,
            capacidad_requerida="sistema.operaciones.llamadas.ver"
        )
        self.assertFalse(tiene_permiso)

    def test_permiso_excepcional_conceder(self):
        """Permiso excepcional tipo 'conceder' otorga capacidad."""
        # Usuario no tiene permiso inicialmente
        self.assertFalse(
            PermisoService.usuario_tiene_permiso(
                usuario_id=self.user_agent.id,
                capacidad_requerida="sistema.finanzas.pagos.aprobar"
            )
        )

        # Conceder permiso excepcional
        PermisoExcepcional.objects.create(
            usuario=self.user_agent,
            capacidad=self.cap_pagos_aprobar,
            tipo="conceder",
            motivo="Proyecto especial",
            autorizado_por=self.user_coordinador,
            activo=True
        )

        # Ahora debe tener permiso
        self.assertTrue(
            PermisoService.usuario_tiene_permiso(
                usuario_id=self.user_agent.id,
                capacidad_requerida="sistema.finanzas.pagos.aprobar"
            )
        )

    def test_permiso_excepcional_revocar(self):
        """Permiso excepcional tipo 'revocar' quita capacidad."""
        # Usuario tiene permiso via grupo
        self.assertTrue(
            PermisoService.usuario_tiene_permiso(
                usuario_id=self.user_agent.id,
                capacidad_requerida="sistema.operaciones.llamadas.ver"
            )
        )

        # Revocar permiso excepcional
        PermisoExcepcional.objects.create(
            usuario=self.user_agent,
            capacidad=self.cap_llamadas_ver,
            tipo="revocar",
            motivo="Suspension temporal",
            autorizado_por=self.user_coordinador,
            activo=True
        )

        # Ahora NO debe tener permiso
        self.assertFalse(
            PermisoService.usuario_tiene_permiso(
                usuario_id=self.user_agent.id,
                capacidad_requerida="sistema.operaciones.llamadas.ver"
            )
        )

    def test_permiso_excepcional_expirado_no_aplica(self):
        """Permiso excepcional expirado no aplica."""
        # Conceder permiso excepcional expirado
        PermisoExcepcional.objects.create(
            usuario=self.user_agent,
            capacidad=self.cap_pagos_aprobar,
            tipo="conceder",
            fecha_fin=timezone.now() - timedelta(days=1),
            motivo="Proyecto ya terminado",
            autorizado_por=self.user_coordinador,
            activo=True
        )

        # No debe tener permiso porque ya expiro
        self.assertFalse(
            PermisoService.usuario_tiene_permiso(
                usuario_id=self.user_agent.id,
                capacidad_requerida="sistema.finanzas.pagos.aprobar"
            )
        )

    def test_permiso_excepcional_inactivo_no_aplica(self):
        """Permiso excepcional inactivo no aplica."""
        # Conceder permiso excepcional inactivo
        PermisoExcepcional.objects.create(
            usuario=self.user_agent,
            capacidad=self.cap_pagos_aprobar,
            tipo="conceder",
            motivo="Desactivado",
            autorizado_por=self.user_coordinador,
            activo=False
        )

        # No debe tener permiso
        self.assertFalse(
            PermisoService.usuario_tiene_permiso(
                usuario_id=self.user_agent.id,
                capacidad_requerida="sistema.finanzas.pagos.aprobar"
            )
        )

    def test_obtener_capacidades_usuario(self):
        """Obtiene todas las capacidades de un usuario."""
        capacidades = PermisoService.obtener_capacidades_usuario(
            usuario_id=self.user_agent.id
        )

        self.assertIsInstance(capacidades, list)
        self.assertGreater(len(capacidades), 0)
        self.assertIn("sistema.operaciones.llamadas.ver", capacidades)
        self.assertIn("sistema.operaciones.llamadas.realizar", capacidades)

    def test_obtener_capacidades_usuario_sin_grupos(self):
        """Usuario sin grupos retorna lista vacia."""
        capacidades = PermisoService.obtener_capacidades_usuario(
            usuario_id=self.user_sin_permisos.id
        )

        self.assertIsInstance(capacidades, list)
        self.assertEqual(len(capacidades), 0)

    def test_obtener_capacidades_incluye_excepcionales(self):
        """Capacidades incluyen permisos excepcionales concedidos."""
        # Conceder permiso excepcional
        PermisoExcepcional.objects.create(
            usuario=self.user_agent,
            capacidad=self.cap_pagos_aprobar,
            tipo="conceder",
            motivo="Proyecto especial",
            autorizado_por=self.user_coordinador,
            activo=True
        )

        capacidades = PermisoService.obtener_capacidades_usuario(
            usuario_id=self.user_agent.id
        )

        self.assertIn("sistema.finanzas.pagos.aprobar", capacidades)

    def test_obtener_capacidades_excluye_revocadas(self):
        """Capacidades excluyen permisos excepcionales revocados."""
        # Revocar permiso
        PermisoExcepcional.objects.create(
            usuario=self.user_agent,
            capacidad=self.cap_llamadas_ver,
            tipo="revocar",
            motivo="Suspension",
            autorizado_por=self.user_coordinador,
            activo=True
        )

        capacidades = PermisoService.obtener_capacidades_usuario(
            usuario_id=self.user_agent.id
        )

        self.assertNotIn("sistema.operaciones.llamadas.ver", capacidades)

    def test_obtener_funciones_accesibles(self):
        """Obtiene funciones a las que el usuario tiene acceso."""
        funciones = PermisoService.obtener_funciones_accesibles(
            usuario_id=self.user_agent.id
        )

        self.assertIsInstance(funciones, list)
        self.assertGreater(len(funciones), 0)

        # Debe incluir la funcion de llamadas
        nombres_completos = [f["nombre_completo"] for f in funciones]
        self.assertIn("sistema.operaciones.llamadas", nombres_completos)

    def test_obtener_funciones_accesibles_sin_permisos(self):
        """Usuario sin permisos no tiene funciones accesibles."""
        funciones = PermisoService.obtener_funciones_accesibles(
            usuario_id=self.user_sin_permisos.id
        )

        self.assertIsInstance(funciones, list)
        self.assertEqual(len(funciones), 0)

    def test_registrar_acceso_crea_auditoria(self):
        """Registrar acceso crea entrada en auditoria."""
        inicial_count = AuditoriaPermiso.objects.count()

        PermisoService.registrar_acceso(
            usuario_id=self.user_agent.id,
            capacidad="sistema.operaciones.llamadas.realizar",
            accion="LLAMADA_INICIADA",
            recurso_id="CALL-12345",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            metadata={"duracion": 120, "resultado": "exitosa"}
        )

        self.assertEqual(AuditoriaPermiso.objects.count(), inicial_count + 1)

        auditoria = AuditoriaPermiso.objects.latest("timestamp")
        self.assertEqual(auditoria.usuario_id, self.user_agent.id)
        self.assertEqual(auditoria.capacidad, "sistema.operaciones.llamadas.realizar")
        self.assertEqual(auditoria.accion_realizada, "LLAMADA_INICIADA")
        self.assertEqual(auditoria.recurso_accedido, "CALL-12345")
        self.assertEqual(auditoria.ip_address, "192.168.1.100")
        self.assertIsNotNone(auditoria.metadata)

    def test_registrar_acceso_capacidad_sensible(self):
        """Capacidades sensibles siempre se auditan."""
        inicial_count = AuditoriaPermiso.objects.count()

        # Capacidad critica debe auditarse
        PermisoService.registrar_acceso(
            usuario_id=self.user_coordinador.id,
            capacidad="sistema.finanzas.pagos.aprobar",
            accion="PAGO_APROBADO",
            recurso_id="PAY-12345"
        )

        self.assertEqual(AuditoriaPermiso.objects.count(), inicial_count + 1)

    def test_usuario_tiene_permiso_capacidad_inexistente(self):
        """Verificar permiso de capacidad inexistente retorna False."""
        tiene_permiso = PermisoService.usuario_tiene_permiso(
            usuario_id=self.user_agent.id,
            capacidad_requerida="sistema.dominio.recurso.inexistente"
        )
        self.assertFalse(tiene_permiso)

    def test_usuario_inexistente_no_tiene_permiso(self):
        """Usuario inexistente no tiene permisos."""
        tiene_permiso = PermisoService.usuario_tiene_permiso(
            usuario_id=99999,
            capacidad_requerida="sistema.operaciones.llamadas.ver"
        )
        self.assertFalse(tiene_permiso)

    def test_multiples_grupos_combinan_capacidades(self):
        """Usuario con multiples grupos tiene capacidades de todos."""
        # Asignar usuario a segundo grupo
        UsuarioGrupo.objects.create(
            usuario=self.user_agent,
            grupo=self.grupo_coordinacion,
            activo=True
        )

        capacidades = PermisoService.obtener_capacidades_usuario(
            usuario_id=self.user_agent.id
        )

        # Debe tener capacidades de ambos grupos (sin duplicados)
        self.assertIn("sistema.operaciones.llamadas.ver", capacidades)
        self.assertIn("sistema.operaciones.llamadas.realizar", capacidades)

        # No debe haber duplicados
        self.assertEqual(
            len(capacidades),
            len(set(capacidades))
        )

    def test_permiso_excepcional_futuro_no_aplica_aun(self):
        """Permiso excepcional con fecha_inicio futura no aplica aun."""
        # Conceder permiso que empieza en 7 dias
        PermisoExcepcional.objects.create(
            usuario=self.user_agent,
            capacidad=self.cap_pagos_aprobar,
            tipo="conceder",
            fecha_inicio=timezone.now() + timedelta(days=7),
            motivo="Proyecto futuro",
            autorizado_por=self.user_coordinador,
            activo=True
        )

        # No debe tener permiso aun
        self.assertFalse(
            PermisoService.usuario_tiene_permiso(
                usuario_id=self.user_agent.id,
                capacidad_requerida="sistema.finanzas.pagos.aprobar"
            )
        )
