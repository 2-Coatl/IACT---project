"""Configuración base compartida para todos los ambientes."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

# **************** INSTALLED_APPS ****************

# 1. Aplicaciones de Terceros (Django y Librerías)
THIRD_PARTY_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
]

# 2. Aplicaciones Propias del Proyecto (Locales)
LOCAL_APPS = [
    "src.callcentersite.apps.access",
    "src.callcentersite.apps.alerts",
    "src.callcentersite.apps.audit",
    # "src.callcentersite.apps.auth",
    "src.callcentersite.apps.pipeline",
    "src.callcentersite.apps.reports",
    "src.callcentersite.apps.users",
    "src.callcentersite.apps.utils",

]

# Unión de todas las aplicaciones
INSTALLED_APPS = THIRD_PARTY_APPS + LOCAL_APPS

# **************** MIDDLEWARE ****************

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "src.callcentersite.middleware.session_security.SessionSecurityMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# **************** URLS y WSGI ****************

ROOT_URLCONF = "src.callcentersite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "src.callcentersite.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

# Session Configuration (RNF-002: NO Redis, use database)
SESSION_ENGINE = "django.contrib.sessions.backends.db"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME", "iact_analytics"),
        "USER": os.getenv("DJANGO_DB_USER", "django_user"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", "django_pass"),
        "HOST": os.getenv("DJANGO_DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DJANGO_DB_PORT", "15432"),
        "CONN_MAX_AGE": int(os.getenv("DJANGO_DB_CONN_MAX_AGE", "300")),
        "OPTIONS": {
            "connect_timeout": int(os.getenv("DJANGO_DB_CONNECT_TIMEOUT", "10")),
        },
    },
    "ivr_readonly": {
        "ENGINE": "mysql.connector.django",
        "NAME": os.getenv("DJANGO_IVR_NAME", "ivr_legacy"),
        "USER": os.getenv("DJANGO_IVR_USER", "django_user"),
        "PASSWORD": os.getenv("DJANGO_IVR_PASSWORD", "django_pass"),
        "HOST": os.getenv("DJANGO_IVR_HOST", "127.0.0.1"),
        "PORT": os.getenv("DJANGO_IVR_PORT", "13306"),
        "CONN_MAX_AGE": int(os.getenv("DJANGO_IVR_CONN_MAX_AGE", "300")),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
            "use_unicode": True,
        },
    },
}

# **************** DATABASE_ROUTERS ****************

DATABASE_ROUTERS = ["src.callcentersite.database_router.IVRReadOnlyRouter"]

LANGUAGE_CODE = "es-es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# **************** SPECTACULAR_SETTINGS ****************

SPECTACULAR_SETTINGS = {
    "TITLE": "IACT API",
    "DESCRIPTION": "IVR Analytics & Customer Tracking - Sistema de analítica de centros de contacto",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "CONTACT": {
        "name": "IACT Development Team",
        "email": "dev@iact.com",
    },
    "LICENSE": {
        "name": "Proprietary",
    },
    "TAGS": [
        {"name": "authentication", "description": "Autenticación y gestión de sesiones JWT"},
        {"name": "users", "description": "Gestión de usuarios del sistema"},
        {"name": "permissions", "description": "Sistema de permisos granulares"},
        {"name": "llamadas", "description": "Gestión de llamadas del call center"},
        {"name": "analytics", "description": "Analítica y métricas"},
        {"name": "reports", "description": "Generación de reportes"},
    ],
    "SERVERS": [
        {
            "url": "http://localhost:8000",
            "description": "Desarrollo Local",
        },
        {
            "url": "http://localhost:15432",
            "description": "PostgreSQL Dev",
        },
    ],
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_SPLIT_PATCH": True,
    "ENFORCE_NON_BLANK_FIELDS": True,
    "SORT_OPERATIONS": True,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
}

AUDIT_LOG_RETENTION_DAYS = 730
APPLICATION_LOG_RETENTION_DAYS = 30
ACCESS_LOG_RETENTION_DAYS = 90

ETL_FREQUENCY_HOURS = int(os.getenv("ETL_FREQUENCY_HOURS", "6"))
ETL_BATCH_SIZE = int(os.getenv("ETL_BATCH_SIZE", "1000"))
ETL_RETENTION_DAYS = int(os.getenv("ETL_RETENTION_DAYS", "730"))