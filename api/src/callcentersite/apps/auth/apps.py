"""Configuración de la app de autenticación."""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Config de autenticación."""

    name = "callcentersite.apps.authentication"
    verbose_name = "Autenticación"
