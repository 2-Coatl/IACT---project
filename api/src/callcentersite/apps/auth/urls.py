"""Rutas públicas para autenticación JWT."""

from django.urls import path

from .views import LoginAPIView, RefreshTokenAPIView


urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="auth-login"),
    path("refresh/", RefreshTokenAPIView.as_view(), name="auth-refresh"),
]

