"""Configuración de producción para despliegue con Apache + mod_wsgi."""

from .base import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME", "iact_analytics"),
        "USER": os.getenv("DJANGO_DB_USER", "iact_app"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", ""),
        "HOST": os.getenv("DJANGO_DB_HOST", "localhost"),
        "PORT": os.getenv("DJANGO_DB_PORT", "5432"),
        "CONN_MAX_AGE": 600,
    },
    "ivr_readonly": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DJANGO_IVR_NAME", "ivr"),
        "USER": os.getenv("DJANGO_IVR_USER", "readonly_user"),
        "PASSWORD": os.getenv("DJANGO_IVR_PASSWORD", ""),
        "HOST": os.getenv("DJANGO_IVR_HOST", "ivr-db"),
        "PORT": os.getenv("DJANGO_IVR_PORT", "3306"),
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
        },
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
