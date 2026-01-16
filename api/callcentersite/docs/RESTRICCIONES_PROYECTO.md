# 🚫 RESTRICCIONES DEL PROYECTO - DOCUMENTO CONSOLIDADO

**Proyecto:** IACT Call Center System  
**Tipo:** Sistema INTERNO on-premise  
**Fecha:** 16 de enero de 2026

---

## IMPORTANTE: LEER PRIMERO

Este proyecto tiene restricciones específicas que DEBEN respetarse en toda implementación, diseño y análisis.

---

## 🚫 SERVICIOS EXTERNOS PROHIBIDOS

### NO se usa NINGÚN servicio cloud:
```
AWS (S3, Lambda, RDS, CloudWatch, SNS, SES, etc.)
Azure
Google Cloud Platform
Heroku
DigitalOcean
Cualquier hosting cloud
```

### NO se usa NINGÚN servicio SaaS externo:
```
Sentry (error tracking)
Datadog (monitoring)
New Relic
LogRocket
Bugsnag
Rollbar
CloudFlare
CDN externos
Servicios de email (SendGrid, Mailgun, etc.)
Servicios de SMS (Twilio, etc.)
Analytics externos (Google Analytics, Mixpanel, etc.)
```

### NO se usa Redis/Caché externo:
```
Redis
Memcached
Redis Cloud
ElastiCache
```

### NO se usan colas de mensajes:
```
Celery
RabbitMQ
Amazon SQS
Redis Queue
Cualquier sistema de colas
```

### NO se envían comunicaciones externas:
```
Emails
SMS
Push notifications
Webhooks
Llamadas a APIs externas
```

---

##  LO QUE SÍ SE USA (TODO LOCAL)

### Infraestructura on-premise:
```
 Servidor local (Ubuntu/Debian/CentOS)
 Red local / VPN
 Acceso solo desde intranet
 PostgreSQL local
 MariaDB local (IVR legacy - solo lectura)
```

### Stack tecnológico:
```
 Python 3.11+
 Django 4.2+
 Django REST Framework
 JWT Authentication
 PostgreSQL (local)
 Nginx (local)
 Gunicorn / uWSGI
 Supervisor / systemd
```

### Almacenamiento:
```
 Disco local para media files
 Disco local para logs
 Disco local/red local para backups
 FileField / ImageField (local storage)
```

### Logging y monitoreo:
```
 Django logging a archivos locales
 RotatingFileHandler
 logrotate
 Dashboard interno de monitoreo
 Scripts bash para monitoreo
```

---

## 📋 CARACTERÍSTICAS DEL SISTEMA

### Tipo de sistema:
```
 Sistema INTERNO de call center
 Solo usuarios empleados (no clientes)
 Acceso desde intranet/VPN
 Datos confidenciales (no pueden salir)
```

### Usuarios:
```
 Usuarios internos (empleados)
 Autenticación username/password
 Permisos RBAC granular (44 funciones)
 Gestión por administradores
NO hay registro público
NO hay usuarios externos
```

### Funcionalidades:
```
 Navegación dinámica RBAC
 Gestión de usuarios (admin)
 Auditoría en BD local
 Reportes generados MANUALMENTE
 Exportación CSV/Excel/PDF
 Dashboards en tiempo real
 Consultas a BD legacy (MariaDB)
```

### NO tiene:
```
Programación de tareas (cron/celery)
Envío automático de emails
Notificaciones push
Procesamiento asíncrono
Caché Redis
Queue de trabajos
Integración con APIs externas
2FA con SMS
Registro público
```

---

## 🔄 FLUJOS DE TRABAJO

### 1. Autenticación:
```
Usuario → Login (username/password) → JWT token → Acceso sistema
```
**NO hay:**
- Email de bienvenida
- Confirmación por email
- 2FA con SMS
- Login social (Google, Facebook, etc.)

### 2. Recuperación de contraseña:
```
Opción A: Admin resetea manualmente
Opción B: Preguntas de seguridad (offline)
```
**NO hay:**
- Email de recuperación
- Código por SMS
- Link mágico por email

### 3. Generación de reportes:
```
Usuario → Selecciona tipo → Configura parámetros → Click "Generar"
→ Sistema procesa SÍNCRONO (usuario espera)
→ Genera archivo CSV/Excel/PDF
→ Usuario descarga inmediatamente
```
**NO hay:**
- Programación automática (cron)
- Procesamiento asíncrono (celery)
- Envío por email
- Notificación cuando termina
- Cola de trabajos

### 4. Dashboards:
```
Usuario → Abre dashboard → Frontend consulta APIs
→ APIs consultan BD en TIEMPO REAL
→ Muestra datos actuales
→ Actualización: polling manual o botón refresh
```
**NO hay:**
- Caché Redis
- WebSockets
- Server-Sent Events
- Push updates

### 5. Auditoría:
```
Acción del usuario → Middleware captura
→ Guarda en AuditLog (BD local)
→ También escribe en archivo log local
```
**NO hay:**
- Envío a Sentry
- Logging externo
- Analytics cloud

---

## 💾 DATOS Y ALMACENAMIENTO

### Base de datos:
```
PostgreSQL (local)
├── Datos de usuarios
├── Configuración RBAC
├── Logs de auditoría
├── Reportes generados
└── Configuración del sistema

MariaDB (local, read-only)
└── Datos legacy IVR (solo lectura)
```

### Archivos:
```
/var/www/iact/media/
├── avatars/              # Fotos usuarios
│   └── user_{id}.jpg
├── reports/              # Reportes generados
│   └── 2026/01/
│       ├── report_001.xlsx
│       └── report_002.pdf
└── uploads/              # Otros archivos

/var/log/iact/
├── app.log              # Logs aplicación
├── error.log            # Logs errores
├── django.log           # Logs Django
├── security.log         # Logs seguridad
└── audit/               # Logs auditoría
    └── 2026-01-16.log

/var/backups/iact/
├── db_20260116.sql.gz   # Backup BD
├── media_20260116.tar.gz # Backup archivos
└── logs_20260116.tar.gz  # Backup logs
```

---

## 🔒 SEGURIDAD

### Configuración:
```
 JWT authentication (local)
 HTTPS (certificado local/auto-firmado)
 CORS configurado (solo IPs internas)
 CSRF protection
 SQL injection protection (Django ORM)
 XSS protection
 Password hashing (Django default)
 Session management (BD local)
```

### NO se implementa:
```
OAuth (Google, GitHub, etc.)
SAML
2FA con SMS/email
Rate limiting externo (Cloudflare)
WAF externo
```

---

## 🚀 DEPLOY

### Infraestructura:
```
Servidor local/on-premise:
├── OS: Ubuntu 22.04 / Debian 11 / CentOS 8
├── Python: 3.11+
├── Web server: Nginx
├── App server: Gunicorn / uWSGI
├── Process manager: Supervisor / systemd
├── PostgreSQL: 14+
└── MariaDB: 10.5+ (legacy)
```

### NO se usa:
```
Docker Hub
AWS ECR
Kubernetes cloud
PaaS (Heroku, etc.)
Serverless
CI/CD cloud (GitHub Actions con deploy a cloud)
```

### SÍ se puede usar (local):
```
 Docker (local)
 docker-compose (local)
 GitLab CI/CD (self-hosted)
 Jenkins (local)
 CI/CD que deploya a servidor local
```

---

## 📊 MONITOREO

### Sistema propio:
```python
# Dashboard interno de monitoreo
GET /api/v1/monitoring/health/
{
  "database": {"status": "ok", "connections": 5},
  "disk_space": {"free": "50GB", "used_percent": 45},
  "logs_size": {"size_mb": 250},
  "active_users": 12,
  "last_backup": "2026-01-16 02:00:00"
}
```

### Scripts locales:
```bash
# Monitoreo con cron local
*/5 * * * * /usr/local/bin/monitor_iact.sh
```

### NO se usa:
```
Sentry
Datadog
CloudWatch
New Relic
Servicios externos de monitoring
```

---

## 📦 DEPENDENCIAS (requirements.txt)

###  PERMITIDAS:
```
Django>=4.2
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
django-cors-headers>=4.3
psycopg2-binary>=2.9.0
mysqlclient>=2.2.0
Pillow>=10.0.0
openpyxl>=3.1.0
pandas>=2.0.0
reportlab>=4.0.0
pytest>=7.4.0
pytest-django>=4.5.0
pytest-cov>=4.1.0
factory-boy>=3.3.0
faker>=20.0.0
gunicorn>=21.0.0
```

### PROHIBIDAS:
```
celery                    # NO async
redis                     # NO cache
django-celery-beat        # NO scheduling
boto3                     # NO AWS
django-storages           # NO S3
sentry-sdk                # NO external logging
python-decouple           # NO necesario (settings locales)
django-anymail            # NO emails
twilio                    # NO SMS
```

---

## 🎯 CASOS DE USO VÁLIDOS

###  CORRECTO:
```
1. Usuario login → JWT → Navegación RBAC
2. Admin crea usuario → Asigna funciones
3. Usuario genera reporte → Espera → Descarga
4. Usuario ve dashboard → Consultas en vivo
5. Sistema guarda logs locales
6. Cron local hace backup a disco local
```

### INCORRECTO:
```
1. Sistema envía email cuando reporte está listo
2. Celery procesa reporte en background
3. Usuario sube foto → se guarda en S3
4. Sistema envía errores a Sentry
5. Notificaciones push cuando hay alerta
6. Integración con API externa
```

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

Antes de implementar cualquier feature, verificar:

- [ ] ¿Usa servicios cloud? → NO PERMITIDO
- [ ] ¿Envía emails/SMS? → NO PERMITIDO
- [ ] ¿Usa Redis/Celery? → NO PERMITIDO
- [ ] ¿Llama APIs externas? → NO PERMITIDO
- [ ] ¿Guarda en S3? → NO PERMITIDO
- [ ] ¿Usa Sentry/monitoring externo? → NO PERMITIDO
- [ ] ¿Todo es local/on-premise? →  REQUERIDO
- [ ] ¿Logs van a archivos locales? →  REQUERIDO
- [ ] ¿Archivos en disco local? →  REQUERIDO
- [ ] ¿BD local? →  REQUERIDO

---

## 🔍 PREGUNTAS FRECUENTES

**P: ¿Puedo usar Celery para reportes grandes?**  
R: NO. Reportes se procesan síncronamente, el usuario espera.

**P: ¿Puedo usar S3 para guardar archivos?**  
R: NO. Archivos en disco local (/var/www/iact/media/).

**P: ¿Puedo usar Sentry para logging?**  
R: NO. Django logging a archivos locales.

**P: ¿Puedo enviar email de recuperación?**  
R: NO. Admin resetea manualmente o preguntas de seguridad.

**P: ¿Puedo usar Redis para caché?**  
R: NO. Sin caché externo, consultas directas a BD.

**P: ¿Puedo programar reportes con cron?**  
R: NO. Usuario genera manualmente cuando necesita.

**P: ¿Puedo usar Docker?**  
R:  SÍ, pero deploy local (no Docker Hub cloud).

**P: ¿Puedo usar PostgreSQL en AWS RDS?**  
R: NO. PostgreSQL local en el servidor.

**P: ¿Puedo usar GitHub Actions para CI/CD?**  
R:  SÍ, si deploya a servidor local. NO si deploya a cloud.

---

##  ARQUITECTURA APROBADA

```
┌─────────────────────────────────────────┐
│    RED LOCAL / VPN CORPORATIVA          │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │   SERVIDOR ON-PREMISE (Local)    │  │
│  │                                   │  │
│  │  ┌────────┐  ┌──────────────┐   │  │
│  │  │ Nginx  │  │  Supervisor  │   │  │
│  │  └───┬────┘  └───────┬──────┘   │  │
│  │      │               │           │  │
│  │  ┌───▼───────────────▼────────┐ │  │
│  │  │   Django + Gunicorn        │ │  │
│  │  │   - APIs REST              │ │  │
│  │  │   - RBAC                   │ │  │
│  │  │   - Logging local          │ │  │
│  │  └───┬────────────────────────┘ │  │
│  │      │                          │  │
│  │  ┌───▼─────────┐  ┌──────────┐ │  │
│  │  │ PostgreSQL  │  │ MariaDB  │ │  │
│  │  │   (local)   │  │ (legacy) │ │  │
│  │  └─────────────┘  └──────────┘ │  │
│  │                                 │  │
│  │  /var/www/iact/media/  ← Archivos│  │
│  │  /var/log/iact/        ← Logs   │  │
│  │  /var/backups/iact/    ← Backups│  │
│  │                                 │  │
│  └─────────────────────────────────┘  │
│                                        │
│  SIN conexión a internet            │
│  SIN servicios cloud                │
│  SIN APIs externas                  │
│   TODO local y autocontenido         │
└────────────────────────────────────────┘
```

---

## 📌 RESUMEN

**Sistema COMPLETAMENTE local/on-premise:**
-  Sin dependencias cloud
-  Sin servicios externos
-  Sin emails/SMS
-  Sin async (celery)
-  Sin caché (redis)
-  Todo en disco local
-  Logs locales
-  Backups locales
-  Monitoreo propio

**ESTA ES LA REGLA #1 DEL PROYECTO**

---

**Última actualización:** 16 de enero de 2026  
**Versión:** 2.0 (con correcciones cloud)
