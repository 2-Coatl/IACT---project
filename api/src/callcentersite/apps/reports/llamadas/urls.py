"""
URLs para Llamadas.

Sistema de Permisos Granular - Prioridad 3: Módulo Operativo Llamadas
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from callcentersite.apps.llamadas import views


router = DefaultRouter()
router.register(r'estados', views.EstadoLlamadaViewSet, basename='estado-llamada')
router.register(r'tipos', views.TipoLlamadaViewSet, basename='tipo-llamada')
router.register(r'llamadas', views.LlamadaViewSet, basename='llamada')
router.register(r'transcripciones', views.LlamadaTranscripcionViewSet, basename='llamada-transcripcion')
router.register(r'grabaciones', views.LlamadaGrabacionViewSet, basename='llamada-grabacion')


urlpatterns = [
    path('', include(router.urls)),
]
