"""
Tests para middleware de permisos.

Sistema de Permisos Granular - Prioridad 1
TDD: Tests escritos ANTES de implementar middleware.py
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from unittest.mock import Mock, patch

from callcentersite.apps.permissions.models import (
    Capacidad,
    GrupoPermisos,
    GrupoCapacidad,
    UsuarioGrupo,
)
from callcentersite.apps.permissions.middleware import verificar_permiso


User = get_user_model()


class VerificarPermisoMiddlewareTestCase(TestCase):
    """Tests para el decorator verificar_permiso."""

    def setUp(self):
        """Configurar datos de prueba."""
        self.factory = RequestFactory()

        # Crear usuarios
        self.user_con_permiso = User.objects.create_user(
            username="user_con_permiso",
            email="conpermiso@test.com",
            password="testpass123"
        )
        self.user_sin_permiso = User.objects.create_user(
            username="user_sin_permiso",
            email="sinpermiso@test.com",
            password="testpass123"
        )

        # Crear capacidad
        self.capacidad = Capacidad.objects.create(
            nombre_completo="sistema.operaciones.llamadas.realizar",
            accion="realizar",
            recurso="llamadas",
            dominio="operaciones",
            nivel_sensibilidad="normal"
        )

        # Crear grupo
        self.grupo = GrupoPermisos.objects.create(
            codigo="atencion_cliente",
            nombre_display="Atencion al Cliente",
            tipo_acceso="operativo",
            activo=True
        )

        # Vincular capacidad a grupo
        GrupoCapacidad.objects.create(
            grupo=self.grupo,
            capacidad=self.capacidad
        )

        # Asignar usuario a grupo
        UsuarioGrupo.objects.create(
            usuario=self.user_con_permiso,
            grupo=self.grupo,
            activo=True
        )

    def test_decorator_permite_acceso_con_permiso(self):
        """Decorator permite acceso si usuario tiene permiso."""
        @verificar_permiso("sistema.operaciones.llamadas.realizar")
        def view_protegida(request):
            return JsonResponse({"status": "ok"})

        request = self.factory.get("/api/llamadas/realizar")
        request.user = self.user_con_permiso

        response = view_protegida(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_decorator_bloquea_acceso_sin_permiso(self):
        """Decorator bloquea acceso si usuario no tiene permiso."""
        @verificar_permiso("sistema.operaciones.llamadas.realizar")
        def view_protegida(request):
            return JsonResponse({"status": "ok"})

        request = self.factory.get("/api/llamadas/realizar")
        request.user = self.user_sin_permiso

        response = view_protegida(request)

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("permiso denegado", data["error"].lower())

    def test_decorator_bloquea_usuario_anonimo(self):
        """Decorator bloquea acceso a usuario no autenticado."""
        from django.contrib.auth.models import AnonymousUser

        @verificar_permiso("sistema.operaciones.llamadas.realizar")
        def view_protegida(request):
            return JsonResponse({"status": "ok"})

        request = self.factory.get("/api/llamadas/realizar")
        request.user = AnonymousUser()

        response = view_protegida(request)

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("autenticacion", data["error"].lower())

    def test_decorator_registra_auditoria_en_acceso_exitoso(self):
        """Decorator registra en auditoria cuando permite acceso."""
        from callcentersite.apps.permissions.models import AuditoriaPermiso

        @verificar_permiso("sistema.operaciones.llamadas.realizar", auditar=True)
        def view_protegida(request):
            return JsonResponse({"status": "ok"})

        request = self.factory.get("/api/llamadas/realizar")
        request.user = self.user_con_permiso
        request.META["REMOTE_ADDR"] = "192.168.1.100"
        request.META["HTTP_USER_AGENT"] = "Mozilla/5.0"

        inicial_count = AuditoriaPermiso.objects.count()
        response = view_protegida(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AuditoriaPermiso.objects.count(), inicial_count + 1)

        auditoria = AuditoriaPermiso.objects.latest("timestamp")
        self.assertEqual(auditoria.usuario, self.user_con_permiso)
        self.assertEqual(auditoria.capacidad, "sistema.operaciones.llamadas.realizar")
        self.assertEqual(auditoria.ip_address, "192.168.1.100")

    def test_decorator_registra_auditoria_en_acceso_denegado(self):
        """Decorator registra en auditoria cuando deniega acceso."""
        from callcentersite.apps.permissions.models import AuditoriaPermiso

        @verificar_permiso("sistema.operaciones.llamadas.realizar", auditar=True)
        def view_protegida(request):
            return JsonResponse({"status": "ok"})

        request = self.factory.get("/api/llamadas/realizar")
        request.user = self.user_sin_permiso
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        inicial_count = AuditoriaPermiso.objects.count()
        response = view_protegida(request)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AuditoriaPermiso.objects.count(), inicial_count + 1)

        auditoria = AuditoriaPermiso.objects.latest("timestamp")
        self.assertEqual(auditoria.usuario, self.user_sin_permiso)
        self.assertEqual(auditoria.accion_realizada, "ACCESO_DENEGADO")

    def test_decorator_no_audita_si_no_requerido(self):
        """Decorator no audita si auditar=False."""
        from callcentersite.apps.permissions.models import AuditoriaPermiso

        @verificar_permiso("sistema.operaciones.llamadas.realizar", auditar=False)
        def view_protegida(request):
            return JsonResponse({"status": "ok"})

        request = self.factory.get("/api/llamadas/realizar")
        request.user = self.user_con_permiso

        inicial_count = AuditoriaPermiso.objects.count()
        response = view_protegida(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AuditoriaPermiso.objects.count(), inicial_count)

    def test_decorator_funciona_con_parametros_view(self):
        """Decorator pasa correctamente parametros a la view."""
        @verificar_permiso("sistema.operaciones.llamadas.realizar")
        def view_con_parametros(request, llamada_id, tipo=None):
            return JsonResponse({
                "llamada_id": llamada_id,
                "tipo": tipo
            })

        request = self.factory.get("/api/llamadas/123")
        request.user = self.user_con_permiso

        response = view_con_parametros(request, llamada_id=123, tipo="entrante")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["llamada_id"], 123)
        self.assertEqual(data["tipo"], "entrante")

    def test_decorator_mensaje_personalizado(self):
        """Decorator permite mensaje de error personalizado."""
        @verificar_permiso(
            "sistema.operaciones.llamadas.realizar",
            mensaje_error="No puedes realizar llamadas en este momento"
        )
        def view_protegida(request):
            return JsonResponse({"status": "ok"})

        request = self.factory.get("/api/llamadas/realizar")
        request.user = self.user_sin_permiso

        response = view_protegida(request)

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("No puedes realizar llamadas", data["error"])

    def test_decorator_multiples_capacidades_require_todas(self):
        """Decorator con lista de capacidades requiere TODAS."""
        # Crear segunda capacidad
        cap2 = Capacidad.objects.create(
            nombre_completo="sistema.operaciones.tickets.crear",
            accion="crear",
            recurso="tickets",
            dominio="operaciones",
            nivel_sensibilidad="normal"
        )

        # Usuario solo tiene una de las dos capacidades
        @verificar_permiso([
            "sistema.operaciones.llamadas.realizar",
            "sistema.operaciones.tickets.crear"
        ])
        def view_protegida(request):
            return JsonResponse({"status": "ok"})

        request = self.factory.get("/api/operacion")
        request.user = self.user_con_permiso

        # Debe denegar porque no tiene tickets.crear
        response = view_protegida(request)
        self.assertEqual(response.status_code, 403)

    def test_decorator_captura_ip_desde_request(self):
        """Decorator captura IP desde request.META."""
        from callcentersite.apps.permissions.models import AuditoriaPermiso

        @verificar_permiso("sistema.operaciones.llamadas.realizar", auditar=True)
        def view_protegida(request):
            return JsonResponse({"status": "ok"})

        request = self.factory.get("/api/llamadas/realizar")
        request.user = self.user_con_permiso
        request.META["REMOTE_ADDR"] = "203.0.113.42"

        view_protegida(request)

        auditoria = AuditoriaPermiso.objects.latest("timestamp")
        self.assertEqual(auditoria.ip_address, "203.0.113.42")

    def test_decorator_captura_user_agent_desde_request(self):
        """Decorator captura User-Agent desde request.META."""
        from callcentersite.apps.permissions.models import AuditoriaPermiso

        @verificar_permiso("sistema.operaciones.llamadas.realizar", auditar=True)
        def view_protegida(request):
            return JsonResponse({"status": "ok"})

        request = self.factory.get("/api/llamadas/realizar")
        request.user = self.user_con_permiso
        request.META["HTTP_USER_AGENT"] = "Custom Agent/1.0"

        view_protegida(request)

        auditoria = AuditoriaPermiso.objects.latest("timestamp")
        self.assertEqual(auditoria.user_agent, "Custom Agent/1.0")
