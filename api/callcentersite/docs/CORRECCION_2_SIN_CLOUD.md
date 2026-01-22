# CORRECCIÓN #2 - SIN AWS NI SERVICIOS CLOUD

**Fecha:** 16 de enero de 2026

---

## 🚫 RESTRICCIONES ADICIONALES (OLVIDADAS)

### NO SE USA NINGÚN SERVICIO CLOUD:
```
AWS (S3, Lambda, CloudWatch, etc.)
Azure
Google Cloud
Sentry (error tracking externo)
CloudFlare
CDN externos
Servicios de logging externos
Servicios de storage externos
Cualquier API externa de terceros
```

### SÍ SE USA (TODO LOCAL/ON-PREMISE):
```
 Servidor local/VPN
 PostgreSQL local
 MariaDB local (legacy)
 Archivos en disco local
 Logs en archivos locales
 Backups en disco local/red local
 Sistema completamente autocontenido
```

---

## 📝 CORRECCIONES AL ANÁLISIS

### REFERENCIAS INCORRECTAS ENCONTRADAS:

#### En PARTE 3 - Configuración:
```python
# INCORRECTO (del análisis original):
### Logging:
```python
# Sentry / Error tracking (opcional)
```
```

**PROBLEMA:** Sentry es un servicio externo cloud 

#### En PARTE 5 - Configuración:
```python
# Referencias a servicios cloud en deploy
```

---

##  LOGGING CORRECTO (TODO LOCAL)

### Django Logging - SOLO archivos locales:

```python
# config/settings/base.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    
    'handlers': {
        # Logs generales de aplicación
        'file_app': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/iact/app.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 30,  # 30 archivos de respaldo
            'formatter': 'verbose',
        },
        
        # Logs de errores
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/iact/error.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 30,
            'formatter': 'verbose',
        },
        
        # Logs de Django (SQL queries, etc.)
        'file_django': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/iact/django.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 30,
            'formatter': 'verbose',
        },
        
        # Logs de seguridad
        'file_security': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/iact/security.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 30,
            'formatter': 'verbose',
        },
        
        # Console para desarrollo
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    
    'loggers': {
        # Logger de la aplicación
        'iact': {
            'handlers': ['file_app', 'file_error', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Logger de Django
        'django': {
            'handlers': ['file_django', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Logger de seguridad
        'django.security': {
            'handlers': ['file_security'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Logger de base de datos (SQL queries)
        'django.db.backends': {
            'handlers': ['file_django'],
            'level': 'DEBUG',  # Solo en desarrollo
            'propagate': False,
        },
    },
}
```

### Estructura de directorios de logs:

```bash
/var/log/iact/
├── app.log           # Logs generales de aplicación
├── app.log.1         # Rotación
├── app.log.2
├── ...
├── error.log         # Logs de errores
├── error.log.1
├── django.log        # Logs de Django framework
├── security.log      # Logs de seguridad/autenticación
└── audit/            # Logs de auditoría (por fecha)
    ├── 2026-01-16.log
    ├── 2026-01-15.log
    └── ...
```

### Rotación de logs (logrotate):

```bash
# /etc/logrotate.d/iact

/var/log/iact/*.log {
    daily                  # Rotar diariamente
    missingok             # No error si falta el archivo
    rotate 30             # Mantener 30 días
    compress              # Comprimir archivos antiguos
    delaycompress         # No comprimir el último archivo
    notifempty            # No rotar si está vacío
    create 0640 www-data www-data
    sharedscripts
    postrotate
        # Recargar aplicación si es necesario
        systemctl reload iact.service > /dev/null 2>&1 || true
    endscript
}
```

---

##  ALMACENAMIENTO DE ARCHIVOS (TODO LOCAL)

### Media files (avatars, reports):

```python
# config/settings/base.py

# Archivos en servidor local
MEDIA_ROOT = '/var/www/iact/media/'
MEDIA_URL = '/media/'

# Estructura:
# /var/www/iact/media/
# ├── avatars/
# │   ├── user_1.jpg
# │   ├── user_2.png
# │   └── ...
# ├── reports/
# │   ├── 2026/
# │   │   ├── 01/
# │   │   │   ├── report_001.xlsx
# │   │   │   ├── report_002.pdf
# │   │   │   └── ...
# │   │   └── 02/
# │   └── 2025/
# └── uploads/
```

### Static files:

```python
# Archivos estáticos en servidor local
STATIC_ROOT = '/var/www/iact/static/'
STATIC_URL = '/static/'
```

### NO SE USA:
```python
# NO usar:
# AWS_STORAGE_BUCKET_NAME
# AWS_S3_REGION_NAME
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# django-storages (para S3)
```

---

##  BACKUPS (TODO LOCAL)

### Script de backup local:

```bash
#!/bin/bash
# /usr/local/bin/backup_iact.sh

BACKUP_DIR="/var/backups/iact"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup base de datos PostgreSQL
pg_dump -U iact_user iact_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup archivos media
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /var/www/iact/media/

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" /var/log/iact/

# Mantener solo últimos 30 días
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completado: $DATE"
```

### Cron para backups automáticos:

```bash
# Crontab
# Backup diario a las 2 AM
0 2 * * * /usr/local/bin/backup_iact.sh >> /var/log/iact/backup.log 2>&1

# Backup semanal completo los domingos a las 3 AM
0 3 * * 0 /usr/local/bin/backup_full_iact.sh >> /var/log/iact/backup.log 2>&1
```

### Estructura de backups:

```bash
/var/backups/iact/
├── db_20260116_020000.sql.gz
├── db_20260115_020000.sql.gz
├── media_20260116_020000.tar.gz
├── media_20260115_020000.tar.gz
├── logs_20260116_020000.tar.gz
└── ...
```

---

##  AUDITORÍA (BASE DE DATOS LOCAL)

### Modelo AuditLog (YA EXISTE):

```python
# apps/audit/models.py

class AuditLog(models.Model):
    """
    Registro de auditoría en BASE DE DATOS LOCAL.
    NO usa servicios externos.
    """
    user = models.ForeignKey(User, ...)
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500)
    changes = models.JSONField(default=dict)  # Cambios realizados
    
    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['timestamp']),
        ]
```

### Logs de auditoría también en archivos:

```python
# Configuración adicional para auditoría
LOGGING['handlers']['file_audit'] = {
    'level': 'INFO',
    'class': 'logging.handlers.TimedRotatingFileHandler',
    'filename': '/var/log/iact/audit/audit.log',
    'when': 'midnight',
    'interval': 1,
    'backupCount': 365,  # 1 año de auditoría
    'formatter': 'verbose',
}
```

---

##  MONITOREO (TODO LOCAL)

### Dashboard de monitoreo interno:

```python
# apps/monitoring/views.py (a crear)

class SystemHealthView(APIView):
    """
    Dashboard de salud del sistema.
    Consulta local, NO servicios externos.
    """
    
    def get(self, request):
        return Response({
            'database': self.check_database(),
            'disk_space': self.check_disk(),
            'logs_size': self.check_logs(),
            'active_users': self.count_active_users(),
            'last_backup': self.get_last_backup(),
        })
    
    def check_database(self):
        """Verificar conexión a BD."""
        try:
            from django.db import connection
            connection.ensure_connection()
            return {'status': 'ok'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def check_disk(self):
        """Verificar espacio en disco."""
        import shutil
        usage = shutil.disk_usage('/var/www/iact')
        return {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': (usage.used / usage.total) * 100
        }
    
    def check_logs(self):
        """Tamaño de logs."""
        import os
        total_size = 0
        for root, dirs, files in os.walk('/var/log/iact'):
            total_size += sum(os.path.getsize(os.path.join(root, name)) 
                            for name in files)
        return {'size_mb': total_size / (1024 * 1024)}
```

### Script de monitoreo local:

```bash
#!/bin/bash
# /usr/local/bin/monitor_iact.sh

# Verificar que el servicio está corriendo
if ! systemctl is-active --quiet iact.service; then
    echo "ERROR: Servicio IACT no está corriendo" >> /var/log/iact/monitor.log
    # Intentar reiniciar
    systemctl restart iact.service
fi

# Verificar espacio en disco
DISK_USAGE=$(df -h /var/www/iact | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "WARNING: Disco al $DISK_USAGE%" >> /var/log/iact/monitor.log
fi

# Verificar conexión a BD
if ! psql -U iact_user -d iact_db -c "SELECT 1" > /dev/null 2>&1; then
    echo "ERROR: No se puede conectar a PostgreSQL" >> /var/log/iact/monitor.log
fi
```

---

##  ERROR HANDLING (SIN SENTRY)

### Manejo de errores local:

```python
# config/settings/base.py

# Middleware para capturar errores
MIDDLEWARE = [
    # ... otros middlewares
    'apps.core.middleware.ErrorLoggingMiddleware',
]
```

```python
# apps/core/middleware.py

import logging
import traceback

logger = logging.getLogger('iact')

class ErrorLoggingMiddleware:
    """
    Middleware para logging de errores.
    Reemplaza Sentry con logging local.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """Log de excepciones no manejadas."""
        logger.error(
            f"Unhandled exception",
            extra={
                'request': {
                    'path': request.path,
                    'method': request.method,
                    'user': str(request.user),
                    'ip': self.get_client_ip(request),
                },
                'exception': {
                    'type': type(exception).__name__,
                    'message': str(exception),
                    'traceback': traceback.format_exc(),
                }
            },
            exc_info=True
        )
        return None
    
    def get_client_ip(self, request):
        """Obtener IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

---

##  DEPLOY (SIN CLOUD)

### Servidor local/on-premise:

```bash
# Instalación en servidor local Ubuntu/Debian

# 1. Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    supervisor

# 2. Crear usuario y directorios
sudo useradd -m -s /bin/bash iact
sudo mkdir -p /var/www/iact
sudo mkdir -p /var/log/iact
sudo mkdir -p /var/backups/iact
sudo chown -R iact:iact /var/www/iact /var/log/iact /var/backups/iact

# 3. Configurar PostgreSQL (local)
sudo -u postgres psql
CREATE DATABASE iact_db;
CREATE USER iact_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE iact_db TO iact_user;

# 4. Deploy aplicación
cd /var/www/iact
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# 5. Configurar Nginx (servidor local)
# Ver archivo de configuración abajo

# 6. Configurar Supervisor (para mantener app corriendo)
# Ver archivo de configuración abajo
```

### Nginx config (local):

```nginx
# /etc/nginx/sites-available/iact

server {
    listen 80;
    server_name iact.local;  # Dominio local/intranet
    
    client_max_body_size 10M;
    
    location /static/ {
        alias /var/www/iact/static/;
    }
    
    location /media/ {
        alias /var/www/iact/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Supervisor config:

```ini
# /etc/supervisor/conf.d/iact.conf

[program:iact]
command=/var/www/iact/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 4
directory=/var/www/iact
user=iact
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/iact/app.log
```

---

## 📊 RESUMEN DE CORRECCIONES

### ELIMINADO del análisis:
- Sentry / Error tracking externo
- AWS S3
- CloudWatch
- Servicios cloud de logging
- django-storages
- Referencias a CDN externos

###  AGREGADO/CORREGIDO:
- Django logging a archivos locales
- RotatingFileHandler para rotación de logs
- Backups locales (script bash)
- Almacenamiento local de media files
- Monitoreo interno (dashboard propio)
- Error logging middleware local
- Deploy on-premise (servidor local)
- Configuración Nginx/Supervisor

### NO HAY DEPENDENCIAS EXTERNAS:
```
Sistema completamente autocontenido:
- Base de datos: PostgreSQL local
- Archivos: Disco local
- Logs: Archivos locales
- Backups: Disco local/red local
- Monitoreo: Dashboard interno
- Deploy: Servidor local/VPN
```

---

## 🎯 ARQUITECTURA FINAL (CORRECTA)

```
┌─────────────────────────────────────────────────┐
│         SERVIDOR LOCAL / ON-PREMISE             │
│                                                 │
│  ┌─────────────┐  ┌──────────────┐            │
│  │   Nginx     │  │  Supervisor  │            │
│  │   (proxy)   │  │  (procesos)  │            │
│  └──────┬──────┘  └──────┬───────┘            │
│         │                 │                     │
│  ┌──────▼─────────────────▼────────┐           │
│  │   Django App (Gunicorn)         │           │
│  │   - APIs REST                   │           │
│  │   - Logging local               │           │
│  │   - Error handling              │           │
│  └──────┬──────────────────────────┘           │
│         │                                       │
│  ┌──────▼──────────┐  ┌───────────────┐       │
│  │  PostgreSQL     │  │  MariaDB      │       │
│  │  (local)        │  │  (legacy)     │       │
│  └─────────────────┘  └───────────────┘       │
│                                                 │
│  ┌────────────────────────────────────┐        │
│  │  Sistema de Archivos Local        │        │
│  │  - /var/www/iact/media/            │        │
│  │  - /var/log/iact/                  │        │
│  │  - /var/backups/iact/              │        │
│  └────────────────────────────────────┘        │
│                                                 │
│  NO AWS, NO Sentry, NO servicios cloud      │
└─────────────────────────────────────────────────┘
```

---

##  PRÓXIMOS PASOS (CORREGIDOS)

### 1. Eliminar referencias cloud del análisis 
### 2. Configurar logging local
### 3. Configurar backups locales
### 4. Deploy on-premise

**TODO LOCAL, SIN SERVICIOS EXTERNOS** 

---

**CORRECCIÓN #2 COMPLETADA**
