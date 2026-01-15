"""
URLs app reports.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importar después de crear ViewSet
# from .views import ReportViewSet

router = DefaultRouter()
# router.register(r'', ReportViewSet, basename='report')

app_name = 'reports'

urlpatterns = [
    path('', include(router.urls)),
]
