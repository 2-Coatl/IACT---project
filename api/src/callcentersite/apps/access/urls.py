"""
URLs para el sistema de permisos granular.

Sistema de Permisos Granular - Prioridad 2: API Layer
REF: ADR-012-sistema-permisos-sin-roles-jerarquicos.md
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from callcentersite.apps.access import views


# Router para ViewSets
router = DefaultRouter()
router.register(r'funciones', views.FuncionViewSet, basename='funcion')
router.register(r'capacidades', views.CapacidadViewSet, basename='capacidad')
router.register(r'funcion-capacidades', views.FuncionCapacidadViewSet, basename='funcion-capacidad')
router.register(r'grupos', views.GrupoPermisosViewSet, basename='grupo-permisos')
router.register(r'grupo-capacidades', views.GrupoCapacidadViewSet, basename='grupo-capacidad')
router.register(r'usuarios-grupos', views.UsuarioGrupoViewSet, basename='usuario-grupo')
router.register(r'permisos-excepcionales', views.PermisoExcepcionalViewSet, basename='permiso-excepcional')
router.register(r'auditoria', views.AuditoriaPermisoViewSet, basename='auditoria-permiso')


# URLs adicionales (views personalizadas)
urlpatterns = [
    path('mis-capacidades/', views.MisCapacidadesView.as_view(), name='mis-capacidades'),
    path('mis-funciones/', views.MisFuncionesView.as_view(), name='mis-funciones'),
    path('verificar-permiso/', views.VerificarPermisoView.as_view(), name='verificar-permiso'),
    path('', include(router.urls)),
]
