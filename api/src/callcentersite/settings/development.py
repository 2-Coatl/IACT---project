"""Configuración de desarrollo."""

import os
from importlib import util
from pathlib import Path

from .base import * # noqa: F401,F403

DEBUG = True

# Configuración de Debug Toolbar
if util.find_spec("debug_toolbar"):
    if "debug_toolbar" not in INSTALLED_APPS:
        INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE,
    ]

INTERNAL_IPS = ["127.0.0.1"]

# --- CONFIGURACIÓN DE BASES DE DATOS (VAGRANT VM) ---
# Basado en logs: MariaDB (192.168.56.10) y PostgreSQL (192.168.56.11)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "iact_analytics",
        "USER": "postgres",
        "PASSWORD": "postgrespass123",
        "HOST": "192.168.56.11",
        "PORT": "5432",
    },
    "ivr_readonly": {
        # Nota: Asegúrate de tener instalado mysql-connector-python o cambia a django.db.backends.mysql
        "ENGINE": "mysql.connector.django",
        "NAME": "ivr",
        "USER": "root",
        "PASSWORD": "rootpass123",
        "HOST": "192.168.56.10",
        "PORT": "3306",
    },
}

# Mantener directorio local para logs o archivos temporales si es necesario
sqlite_dir: Path = BASE_DIR / "local_db"
sqlite_dir.mkdir(exist_ok=True)