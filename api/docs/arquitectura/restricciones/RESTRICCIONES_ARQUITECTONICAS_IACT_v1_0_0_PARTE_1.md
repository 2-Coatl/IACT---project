# 📜 RESTRICCIONES ARQUITECTÓNICAS - SISTEMA IACT

## PARTE 1/3: RESTRICCIONES CRÍTICAS Y SEGURIDAD

---

## 📋 INFORMACIÓN DEL DOCUMENTO

| Atributo | Valor |
|---|---|
| **Versión** | 1.0.0 - DEFINITIVA |
| **Fecha** | 19 Enero 2026 |
| **Proyecto** | Sistema IACT - IVR Analytics & Customer Tracking |
| **Propósito** | Consolidar TODAS las restricciones arquitectónicas del proyecto |
| **Audiencia** | Equipo técnico, arquitectos, desarrolladores |
| **Parte** | 1/3 - Restricciones Críticas y Seguridad |
| **Base** | CLEAN_CODE v3.0.1, ARQUITECTURA_ETL v2.0.0 |

---

## 🔄 CONTROL DE VERSIONES

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| **1.0.0** | **2026-01-19** | **Versión inicial definitiva con CNST-010 a CNST-014** | **Equipo IACT** |

### Cambios v1.0.0

```diff
+ Agregadas 5 nuevas restricciones técnicas críticas:
  + CNST-010: NO Redis (cache/sessions)
  + CNST-011: NO Cloud Services (AWS/GCP/Azure)
  + CNST-012: NO Servicios Externos (Twilio/SendGrid/etc)
  + CNST-013: NO Message Brokers (Celery/RabbitMQ/Kafka)
  + CNST-014: NO Containerización (Docker/Kubernetes)

+ Sección 1 ampliada: 4 → 8 restricciones críticas
+ Todas las restricciones con código CNST asignado
+ Justificaciones técnicas documentadas
+ Alternativas permitidas especificadas
```

---

## 📋 CONTENIDO DE ESTA PARTE

Esta parte documenta las restricciones MÁS CRÍTICAS del proyecto:

**SECCIÓN 1: RESTRICCIONES TÉCNICAS CRÍTICAS (NO NEGOCIABLES)**
- 1.1 Comunicaciones (NO email)
- 1.2 Gestión de Sesiones → **CNST-010** ⭐
- 1.3 Base de Datos Dual
- 1.4 Actualización de Datos (NO real-time)
- 1.5 Infraestructura Cloud → **CNST-011** ⭐
- 1.6 Servicios Externos → **CNST-012** ⭐
- 1.7 Message Brokers → **CNST-013** ⭐
- 1.8 Containerización → **CNST-014** ⭐

**SECCIÓN 2: RESTRICCIONES DE SEGURIDAD (DRF SECURE CODE)**
- 2.1 Configuración Django/DRF
- 2.2 Autenticación y Autorización
- 2.3 Serializers y Exposición de Datos
- 2.4 Prevención de Vulnerabilidades
- 2.5 Dependencias y SBOM

---

## 🔴 1. RESTRICCIONES TÉCNICAS CRÍTICAS (NO NEGOCIABLES)

> ⚠️ **IMPORTANTE:** Estas restricciones son **ABSOLUTAMENTE NO NEGOCIABLES**.  
> Cualquier violación de estas restricciones es un **BLOCKER** del proyecto.

---

### 1.1 Comunicaciones

**Código:** CNST-001 (implícito)

```yaml
❌ PROHIBIDO ABSOLUTO:
  - Envío de correos electrónicos
  - SMTP/SendGrid/Mailgun/cualquier servicio de email
  - Templates de email
  - Recuperación de contraseña por email
  - Notificaciones por email
  - Alertas por email

✅ OBLIGATORIO:
  - Todas las notificaciones vía buzón interno
  - Modelo InternalMessage en apps/alerts/
  - UC-037: Sistema de mensajería interno completo
  - Recuperación de contraseña solo con 3 preguntas de seguridad
```

**Justificación:** Restricción de negocio del cliente. Sistema 100% interno sin dependencias externas de comunicación.

**Aplicable a:**
- UC-003: Recuperar Contraseña
- UC-037: Recibir Notificación
- UC-036 a UC-040: Sistema de Alertas
- Todos los módulos que requieran notificar usuarios

**Alternativa Permitida:**
```python
# apps/alerts/models.py
class InternalMessage(TimeStampedModel):
    """Mensaje interno del sistema."""
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=20,
        choices=[('low', 'Baja'), ('medium', 'Media'), ('high', 'Alta')],
        default='medium'
    )
    
    class Meta:
        db_table = 'internal_messages'
        ordering = ['-created_at']
```

**Validación:**
```bash
# Verificar que NO exista configuración de email
grep -r "EMAIL_BACKEND\|SMTP_HOST\|send_mail" . && echo "❌ VIOLACIÓN: Email configurado"

# Verificar buzón interno
python manage.py shell -c "from apps.alerts.models import InternalMessage; print('✅ Buzón interno OK')"
```

---

### 1.2 Gestión de Sesiones

**Código:** **CNST-010** ⭐ NUEVO

```yaml
❌ PROHIBIDO:
  - Redis para sesiones
  - Memcached para sesiones
  - Sesiones en memoria sin respaldo (locmem)
  - Cualquier backend volátil
  - Cache basado en Redis
  - django-redis o similares

✅ OBLIGATORIO:
  - Sesiones en base de datos MySQL/MariaDB
  - Tabla: django_session (Django default)
  - SESSION_ENGINE = 'django.contrib.sessions.backends.db'
  - Timeout: 15 minutos exactos
  - Sesión única por usuario (cerrar previas automáticamente)

⚠️ VALIDACIONES:
  - Verificar IP + User-Agent en cada request
  - Cerrar sesión automática por inactividad
  - Bloquear si cambio de IP sospechoso
```

**Justificación:** 
- Infraestructura del cliente NO tiene Redis
- Política de seguridad: sesiones persistentes y auditables
- 100% on-premise, sin servicios externos
- Control total sobre sesiones en BD propia

**Aplicable a:**
- UC-001: Iniciar Sesión
- UC-002: Cerrar Sesión
- UC-005: Gestión de Sesiones
- Middleware de autenticación
- Todos los endpoints que requieran autenticación

**Configuración Obligatoria:**
```python
# settings/base.py

# ✅ SESIONES EN BASE DE DATOS
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 900  # 15 minutos
SESSION_SAVE_EVERY_REQUEST = True  # Renovar en cada request
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_SAMESITE = 'Strict'

# ❌ NO USAR REDIS
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # PROHIBIDO

# ✅ CACHE EN MEMORIA (NO REDIS)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'iact-cache',
        'TIMEOUT': 300,  # 5 minutos
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# ❌ NO USAR REDIS CACHE
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',  # PROHIBIDO
#         'LOCATION': 'redis://localhost:6379/1',
#     }
# }
```

**Middleware de Sesión Única:**
```python
# apps/authentication/middleware.py

from django.contrib.sessions.models import Session
from django.utils import timezone

class SingleSessionMiddleware:
    """Garantiza una sola sesión activa por usuario."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Obtener sesión actual
            current_session_key = request.session.session_key
            
            # Eliminar otras sesiones del mismo usuario
            Session.objects.filter(
                expire_date__gte=timezone.now()
            ).exclude(
                session_key=current_session_key
            ).filter(
                session_data__contains=str(request.user.id)
            ).delete()
        
        return self.get_response(request)
```

**Validación:**
```bash
# Verificar configuración de sesiones
python manage.py shell -c "
from django.conf import settings
assert settings.SESSION_ENGINE == 'django.contrib.sessions.backends.db', 'ERROR: Session engine incorrecto'
assert settings.SESSION_COOKIE_AGE == 900, 'ERROR: Timeout incorrecto'
print('✅ CNST-010: Sesiones correctamente configuradas')
"

# Verificar que NO exista Redis
grep -r "redis\|Redis\|REDIS" settings/ && echo "❌ VIOLACIÓN CNST-010: Redis encontrado"

# Verificar tabla django_session
python manage.py dbshell -c "SHOW TABLES LIKE 'django_session';" && echo "✅ Tabla sesiones OK"
```

**Alternativas NO Permitidas:**
```python
# ❌ PROHIBIDO - Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {'default': {'BACKEND': 'django_redis.cache.RedisCache'}}

# ❌ PROHIBIDO - Memcached
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache'}}

# ❌ PROHIBIDO - En memoria (volátil)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

# ✅ PERMITIDO - Solo base de datos
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

---

### 1.3 Base de Datos Dual

**Código:** CNST-002 (implícito)

```yaml
❌ PROHIBIDO EN BD IVR:
  - Permisos INSERT
  - Permisos UPDATE
  - Permisos DELETE
  - Permisos CREATE TABLE
  - Permisos ALTER TABLE
  - Cualquier operación de escritura
  - Conexión con usuario con privilegios

✅ OBLIGATORIO:
  - Usuario con permisos SELECT únicamente
  - Conexión 'ivr_legacy' en settings
  - ETL solo lectura de datos
  - Zero impacto en operación IVR 24/7

✅ BD ANALYTICS (Write):
  - Permisos completos
  - Modelos Django normales
  - Migraciones permitidas
  - Conexión 'default'

⚠️ CRÍTICO:
  - Protección absoluta de BD IVR
  - Cualquier escritura accidental = incidente mayor
```

**Justificación:** BD IVR en producción 24/7, no se puede afectar. Sistema legacy crítico para call center.

**Aplicable a:**
- ETL Service completo
- Adaptadores de BD Legacy
- Queries de reportes
- Todo acceso a datos del IVR

**Configuración Database Router:**
```python
# settings/base.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'iact_analytics',
        'USER': 'iact_app',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    },
    'ivr_legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ivr_database',
        'USER': 'ivr_readonly',  # ✅ Usuario READONLY
        'PASSWORD': os.getenv('IVR_DB_PASSWORD'),
        'HOST': 'ivr-server.local',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'latin1',
            'read_default_file': '/etc/mysql/my.cnf',
        }
    }
}

# Database Router
DATABASE_ROUTERS = ['apps.ivr.router.IVRRouter']
```

**Router Completo:**
```python
# apps/ivr/router.py

class IVRRouter:
    """
    Router para separar BD IVR (readonly) vs BD Analytics (write).
    
    CRÍTICO: Protege BD IVR de cualquier escritura accidental.
    """
    
    ivr_apps = {'ivr'}
    
    def db_for_read(self, model, **hints):
        """Lectura: IVR usa 'ivr_legacy', resto usa 'default'."""
        if model._meta.app_label in self.ivr_apps:
            return 'ivr_legacy'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Escritura: IVR SIEMPRE None (bloqueado), resto 'default'."""
        if model._meta.app_label in self.ivr_apps:
            return None  # ✅ Bloquea escrituras a BD IVR
        return 'default'
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Migraciones: NUNCA en BD IVR."""
        if app_label in self.ivr_apps:
            return False  # ✅ No migraciones en BD IVR
        return db == 'default'
```

**Validación:**
```bash
# Verificar permisos readonly en BD IVR
mysql -h ivr-server.local -u ivr_readonly -p -e "
SELECT 
    GRANTEE, 
    PRIVILEGE_TYPE 
FROM information_schema.user_privileges 
WHERE GRANTEE LIKE '%ivr_readonly%'
"

# Debe mostrar SOLO SELECT, NO INSERT/UPDATE/DELETE

# Verificar router
python manage.py shell -c "
from apps.ivr.models import CallRecord
from django.db import router

# Debe usar 'ivr_legacy' para lectura
assert router.db_for_read(CallRecord) == 'ivr_legacy', 'Error: Router lectura'

# Debe retornar None para escritura (bloqueado)
assert router.db_for_write(CallRecord) is None, 'Error: Router escritura'

print('✅ CNST-002: Database router correcto')
"
```

---

### 1.4 Actualización de Datos

**Código:** CNST-003 (implícito)

```yaml
❌ PROHIBIDO:
  - Real-time updates
  - WebSockets
  - Server-Sent Events (SSE)
  - Polling automático
  - Push notifications
  - Auto-refresh de dashboard
  - Streaming de datos

✅ OBLIGATORIO:
  - Dashboard actualizado según frecuencia ETL (6-12 horas)
  - Usuario debe refrescar manualmente (F5)
  - Mostrar "Última actualización: timestamp"
  - Mostrar "Próxima actualización: timestamp"
  - Indicador visual de "datos estáticos"

📊 FRECUENCIA ETL:
  - Configurable: 6-12 horas
  - No menor a 6 horas
  - Ejecutado por APScheduler (NO Celery)
  - Stored Procedure en MariaDB
```

**Justificación:** 
- Arquitectura simplificada sin real-time
- Carga en BD IVR minimizada
- No requiere infraestructura compleja (WebSockets/Redis)
- Datos de análisis, no operacionales (desfase aceptable)

**Aplicable a:**
- UC-025: Dashboard Principal
- Todos los widgets
- Gráficos y visualizaciones
- Métricas "en tiempo real" (no existen)

**Configuración ETL:**
```python
# apps/pipeline/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

def run_etl():
    """Ejecuta ETL desde stored procedure."""
    call_command('run_etl')

# Inicializar scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    run_etl,
    trigger='interval',
    hours=6,  # Cada 6 horas
    id='etl_job',
    name='ETL IVR → Analytics',
    replace_existing=True
)
scheduler.start()
```

**UI Dashboard:**
```python
# apps/dashboard/views.py

class MetricasTrimestralesViewSet(viewsets.ViewSet):
    """Dashboard con datos estáticos (6-12h desfase)."""
    
    @require_function('DSH-001')
    def list(self, request):
        # Obtener última ejecución ETL
        last_run = JobExecutionLog.objects.filter(
            status='completed'
        ).order_by('-end_time').first()
        
        # Calcular próxima ejecución
        next_run = last_run.end_time + timedelta(hours=6)
        
        return Response({
            'widgets': widgets,
            'last_updated': last_run.end_time.isoformat(),
            'next_update': next_run.isoformat(),
            'data_status': 'static',  # ⚠️ Datos estáticos
            'refresh_interval': None,  # ✅ No auto-refresh
        })
```

**Frontend:**
```javascript
// dashboard.component.ts

export class DashboardComponent {
    lastUpdated: string;
    nextUpdate: string;
    
    ngOnInit() {
        this.loadDashboard();
        
        // ❌ NO auto-refresh
        // setInterval(() => this.loadDashboard(), 60000);  // PROHIBIDO
    }
    
    loadDashboard() {
        this.dashboardService.getMetrics().subscribe(data => {
            this.widgets = data.widgets;
            this.lastUpdated = data.last_updated;
            this.nextUpdate = data.next_update;
            
            // ✅ Mostrar al usuario
            this.showDataStatus();
        });
    }
    
    showDataStatus() {
        // Mostrar banner: "Datos actualizados: hace 3 horas"
        // "Próxima actualización: en 3 horas"
    }
}
```

**Validación:**
```bash
# Verificar que NO exista WebSocket
grep -r "WebSocket\|websocket\|channels\|asyncio" . && echo "❌ VIOLACIÓN CNST-003"

# Verificar APScheduler (no Celery)
grep -r "apscheduler" requirements.txt && echo "✅ APScheduler configurado"
grep -r "celery\|Celery" requirements.txt && echo "❌ VIOLACIÓN CNST-013"
```

---

### 1.5 Infraestructura Cloud

**Código:** **CNST-011** ⭐ NUEVO

```yaml
❌ PROHIBIDO ABSOLUTO:
  AWS Services:
    - S3 (almacenamiento)
    - Lambda (serverless)
    - SQS (colas)
    - SNS (notificaciones)
    - RDS (bases de datos)
    - ElastiCache (Redis/Memcached)
    - CloudFront (CDN)
    - Route53 (DNS)
    - Cualquier otro servicio AWS

  Google Cloud Services:
    - Cloud Storage (GCS)
    - Cloud Functions
    - Pub/Sub
    - Cloud SQL
    - Memorystore (Redis)
    - Cloud CDN
    - Cualquier otro servicio GCP

  Azure Services:
    - Blob Storage
    - Functions
    - Service Bus
    - SQL Database
    - Cache for Redis
    - Cualquier otro servicio Azure

  Otros:
    - DigitalOcean Spaces
    - Cloudflare (CDN)
    - Fastly
    - Cualquier servicio cloud externo

✅ OBLIGATORIO:
  - 100% on-premise en servidores propios
  - Almacenamiento local (filesystem)
  - Base de datos local (MySQL/MariaDB on-premise)
  - DNS interno
  - Backup en servidores locales
```

**Justificación:**
- Política corporativa: 100% on-premise
- Datos sensibles de clientes (call center)
- No dependencia de servicios externos
- Control total sobre infraestructura
- Compliance y regulaciones internas

**Aplicable a:**
- Toda la infraestructura del proyecto
- Almacenamiento de archivos (reportes, exports)
- Bases de datos
- Cache y sessions
- Backups

**Alternativas Permitidas:**

**Para Almacenamiento (NO S3):**
```python
# settings/base.py

# ✅ PERMITIDO - Filesystem local
MEDIA_ROOT = '/opt/iact/media/'
MEDIA_URL = '/media/'

# File storage backend
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# ❌ PROHIBIDO - S3
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_STORAGE_BUCKET_NAME = 'my-bucket'
```

**Para Archivos Estáticos:**
```python
# ✅ PERMITIDO - Servidor local (Nginx)
STATIC_ROOT = '/opt/iact/static/'
STATIC_URL = '/static/'

# Servir con Nginx
# location /static/ {
#     alias /opt/iact/static/;
# }

# ❌ PROHIBIDO - CloudFront/CDN
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
```

**Para Colas/Jobs (NO SQS/Lambda):**
```python
# ✅ PERMITIDO - APScheduler (local)
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(my_job, trigger='interval', hours=6)

# ❌ PROHIBIDO - AWS SQS
# import boto3
# sqs = boto3.client('sqs')
# sqs.send_message(...)

# ❌ PROHIBIDO - Celery con broker externo
# (Ver CNST-013 para detalles)
```

**Validación:**
```bash
# Verificar que NO existan dependencias cloud
grep -r "boto3\|google-cloud\|azure" requirements.txt && echo "❌ VIOLACIÓN CNST-011: Dependencias cloud"

# Verificar configuración de storage
python manage.py shell -c "
from django.conf import settings
assert 'FileSystemStorage' in str(settings.DEFAULT_FILE_STORAGE), 'ERROR: Storage no local'
print('✅ CNST-011: Storage local configurado')
"

# Verificar variables de entorno
env | grep -i "AWS\|GOOGLE\|AZURE\|S3\|GCS" && echo "❌ VIOLACIÓN CNST-011: Variables cloud"
```

**Excepciones:** NINGUNA. Esta restricción es absoluta.

---

### 1.6 Servicios Externos

**Código:** **CNST-012** ⭐ NUEVO

```yaml
❌ PROHIBIDO ABSOLUTO:
  Servicios de Comunicación:
    - Twilio (SMS/WhatsApp/Voice)
    - SendGrid (Email) ← Ya cubierto en CNST-001
    - Mailgun (Email)
    - Vonage/Nexmo (SMS)
    - MessageBird
    - Plivo

  Servicios de Pago:
    - Stripe
    - PayPal
    - MercadoPago
    - Cualquier pasarela de pago

  Servicios de Autenticación:
    - Auth0
    - Okta
    - Firebase Authentication
    - OAuth providers externos (Google/Facebook/GitHub)

  Servicios de Monitoreo:
    - Sentry
    - New Relic
    - DataDog
    - Rollbar
    - LogRocket

  Servicios de Analytics:
    - Google Analytics
    - Mixpanel
    - Amplitude
    - Segment

  CDN y Assets:
    - Cloudflare CDN
    - jsDelivr
    - UNPKG
    - Google Fonts (externa)

  APIs Externas:
    - Google Maps API
    - OpenWeatherMap
    - Cualquier API de terceros

✅ OBLIGATORIO:
  - Todas las funcionalidades implementadas internamente
  - Autenticación propia (Django)
  - Logging local (filesystem/BD)
  - Assets servidos localmente
  - Sin llamadas a APIs externas
```

**Justificación:**
- Datos sensibles no pueden salir de la red interna
- No dependencia de servicios externos
- Control total sobre funcionalidad
- Compliance y privacidad
- Disponibilidad no depende de terceros

**Aplicable a:**
- Sistema de notificaciones (buzón interno)
- Autenticación (Django auth)
- Logging y monitoreo (local)
- Assets (CSS/JS/fonts locales)

**Alternativas Permitidas:**

**Para Autenticación (NO Auth0):**
```python
# ✅ PERMITIDO - Django Authentication
from django.contrib.auth import authenticate, login

def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
    
# ❌ PROHIBIDO - Auth0
# from auth0.v3.authentication import GetToken
# get_token = GetToken('domain')
```

**Para Logging (NO Sentry):**
```python
# settings/base.py

# ✅ PERMITIDO - Logging local
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/iact/django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}

# ❌ PROHIBIDO - Sentry
# import sentry_sdk
# sentry_sdk.init(dsn="https://...")
```

**Para Assets (NO Google Fonts):**
```html
<!-- ❌ PROHIBIDO - Google Fonts CDN -->
<!-- <link href="https://fonts.googleapis.com/css2?family=Roboto" rel="stylesheet"> -->

<!-- ✅ PERMITIDO - Fonts locales -->
<link href="/static/fonts/roboto.css" rel="stylesheet">
```

**Validación:**
```bash
# Verificar dependencias prohibidas
grep -r "twilio\|sendgrid\|stripe\|sentry\|auth0" requirements.txt && echo "❌ VIOLACIÓN CNST-012"

# Verificar templates HTML
grep -r "googleapis\|cloudflare\|jsdelivr" templates/ && echo "❌ VIOLACIÓN CNST-012: CDN externo"

# Verificar llamadas a APIs externas
grep -r "requests.get\|urllib.request" . | grep -v "localhost\|127.0.0.1\|internal" && echo "⚠️ Revisar llamadas HTTP"
```

**Excepción:** Si en el futuro se requiere integración con servicio externo (ej: pasarela de pago), debe:
1. Aprobación formal de arquitectura
2. Evaluación de seguridad
3. Documentación de riesgos
4. Alternativas evaluadas

---

### 1.7 Message Brokers y Procesamiento Asíncrono

**Código:** **CNST-013** ⭐ NUEVO

```yaml
❌ PROHIBIDO ABSOLUTO:
  Message Brokers:
    - Celery (con Redis/RabbitMQ)
    - RabbitMQ
    - Apache Kafka
    - Amazon SQS ← Ya cubierto en CNST-011
    - Google Pub/Sub ← Ya cubierto en CNST-011
    - Azure Service Bus ← Ya cubierto en CNST-011
    - Redis (como broker)
    - Memcached
    - ZeroMQ
    - ActiveMQ

  Task Queues:
    - Celery (cualquier backend)
    - Dramatiq
    - Huey (con Redis)
    - RQ (Redis Queue)

✅ OBLIGATORIO:
  - APScheduler para tareas programadas
  - Django commands para tareas manuales
  - Stored Procedures para procesamiento BD
  - Procesamiento síncrono cuando sea posible

✅ PERMITIDO (con limitaciones):
  - APScheduler con BackgroundScheduler
  - Django management commands
  - Cron jobs del sistema
  - Threading en casos específicos
```

**Justificación:**
- No hay Redis (CNST-010)
- No hay cloud services (CNST-011)
- Arquitectura simplificada
- ETL cada 6-12h (no requiere procesamiento real-time)
- Complejidad innecesaria para el scope del proyecto

**Aplicable a:**
- ETL (procesamiento programado)
- Reportes bajo demanda
- Tareas programadas (cleanup, backups)
- Procesamiento de datos

**Configuración Permitida:**

**APScheduler (✅ PERMITIDO):**
```python
# apps/pipeline/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

def run_etl():
    """Ejecuta ETL desde stored procedure."""
    from django.core.management import call_command
    logger.info("Iniciando ETL programado...")
    call_command('run_etl')
    logger.info("ETL completado")

def cleanup_old_sessions():
    """Limpia sesiones expiradas."""
    from django.core.management import call_command
    call_command('clearsessions')

# Inicializar scheduler
scheduler = BackgroundScheduler({
    'apscheduler.timezone': 'America/Santiago'
})

# ETL cada 6 horas
scheduler.add_job(
    run_etl,
    trigger='interval',
    hours=6,
    id='etl_job',
    name='ETL IVR → Analytics',
    replace_existing=True
)

# Cleanup diario a las 2 AM
scheduler.add_job(
    cleanup_old_sessions,
    trigger=CronTrigger(hour=2, minute=0),
    id='cleanup_job',
    name='Session Cleanup',
    replace_existing=True
)

# Iniciar scheduler
scheduler.start()
```

**Django Command (✅ PERMITIDO):**
```python
# apps/pipeline/management/commands/run_etl.py

from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Ejecuta ETL desde stored procedure'
    
    def handle(self, *args, **options):
        self.stdout.write('Iniciando ETL...')
        
        with connection.cursor() as cursor:
            cursor.execute("CALL sp_etl_daily()")
            result = cursor.fetchone()
            
        self.stdout.write(
            self.style.SUCCESS(f'ETL completado: {result}')
        )

# Ejecutar manualmente:
# python manage.py run_etl
```

**Celery (❌ PROHIBIDO):**
```python
# ❌ PROHIBIDO - No usar Celery

# requirements.txt
# celery==5.3.0  # ❌ ELIMINAR
# redis==4.5.0   # ❌ PROHIBIDO por CNST-010

# settings/base.py
# CELERY_BROKER_URL = 'redis://localhost:6379'  # ❌ PROHIBIDO

# tasks.py
# from celery import shared_task
# @shared_task
# def process_report():
#     pass
```

**Alternativa para Reportes Bajo Demanda:**
```python
# apps/reports/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class ReportViewSet(viewsets.ViewSet):
    """
    Reportes procesados síncronamente.
    
    NOTA: Sin Celery, el procesamiento es síncrono.
    Para reportes grandes, se recomienda:
    1. Timeout aumentado (90 segundos)
    2. Paginación agresiva
    3. Límites de registros (100K)
    """
    
    @action(detail=False, methods=['post'])
    def generate_abandoned_calls(self, request):
        # Procesamiento SÍNCRONO
        # Usuario espera hasta que termine
        
        # Timeout en Nginx: 90 segundos
        # Límite de registros: 100,000 (CNST-007)
        
        report = ReportService.generate_abandoned_calls(
            start_date=request.data['start_date'],
            end_date=request.data['end_date'],
            format='excel'
        )
        
        return Response({
            'file_url': report.file_url,
            'records': report.record_count,
            'generated_at': report.created_at
        })
```

**Validación:**
```bash
# Verificar que NO exista Celery
grep -r "celery\|Celery" requirements.txt && echo "❌ VIOLACIÓN CNST-013: Celery instalado"
grep -r "from celery\|import celery" . && echo "❌ VIOLACIÓN CNST-013: Celery usado"

# Verificar APScheduler
grep "apscheduler" requirements.txt && echo "✅ APScheduler OK"

# Verificar RabbitMQ
netstat -tlnp | grep 5672 && echo "❌ VIOLACIÓN CNST-013: RabbitMQ corriendo"

# Verificar configuración
python manage.py shell -c "
from apps.pipeline.scheduler import scheduler
print(f'Jobs programados: {len(scheduler.get_jobs())}')
print('✅ CNST-013: APScheduler configurado')
"
```

**Excepciones:** NINGUNA para message brokers externos. APScheduler es la única opción permitida.

---

### 1.8 Containerización y Orquestación

**Código:** **CNST-014** ⭐ NUEVO

```yaml
❌ PROHIBIDO ABSOLUTO:
  Containerización:
    - Docker
    - Docker Compose
    - Podman
    - LXC/LXD
    - Cualquier tecnología de containers

  Orquestación:
    - Kubernetes (K8s)
    - Docker Swarm
    - OpenShift
    - Nomad
    - Amazon ECS ← Ya cubierto en CNST-011
    - Google Kubernetes Engine ← Ya cubierto en CNST-011
    - Azure Kubernetes Service ← Ya cubierto en CNST-011

  CI/CD Containerizado:
    - GitLab CI con Docker
    - GitHub Actions con containers
    - Jenkins con Docker agents

✅ OBLIGATORIO:
  - Despliegue en servidor tradicional (VM o bare metal)
  - Instalación directa con pip/virtualenv
  - Servidor de aplicaciones: Gunicorn
  - Servidor web: Nginx
  - Supervisor para gestión de procesos
  - Systemd para servicios

⚠️ IMPORTANTE:
  - No usar imágenes Docker
  - No usar Dockerfiles
  - No usar docker-compose.yml
  - Despliegue tradicional Linux
```

**Justificación:**
- Política corporativa: infraestructura tradicional
- Equipo de operaciones no maneja containers
- Servidores legacy sin soporte Docker
- Seguridad: containers considerados "no seguros" por el cliente
- Complejidad innecesaria para el scope

**Aplicable a:**
- Deployment completo
- CI/CD pipeline
- Entornos de desarrollo (local OK usar Docker, prod NO)
- Documentación de instalación

**Configuración Permitida:**

**Estructura de Deployment:**
```bash
# ✅ PERMITIDO - Servidor tradicional

/opt/iact/
├── venv/                    # Virtualenv Python
├── app/                     # Código Django
├── static/                  # Archivos estáticos
├── media/                   # Archivos subidos
├── logs/                    # Logs
├── config/                  # Configuración
│   ├── gunicorn.conf.py
│   ├── nginx.conf
│   └── supervisor.conf
└── scripts/                 # Scripts de deployment
    ├── deploy.sh
    ├── backup.sh
    └── restart.sh
```

**Gunicorn Configuration:**
```python
# /opt/iact/config/gunicorn.conf.py

bind = '127.0.0.1:8000'
workers = 4
worker_class = 'sync'
timeout = 90
accesslog = '/opt/iact/logs/gunicorn-access.log'
errorlog = '/opt/iact/logs/gunicorn-error.log'
loglevel = 'info'
```

**Nginx Configuration:**
```nginx
# /etc/nginx/sites-available/iact

server {
    listen 80;
    server_name iact.company.local;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /opt/iact/static/;
    }
    
    location /media/ {
        alias /opt/iact/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 90s;
    }
}
```

**Supervisor Configuration:**
```ini
# /etc/supervisor/conf.d/iact.conf

[program:iact-gunicorn]
command=/opt/iact/venv/bin/gunicorn config.wsgi:application -c /opt/iact/config/gunicorn.conf.py
directory=/opt/iact/app
user=iact
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/iact/logs/supervisor.log

[program:iact-apscheduler]
command=/opt/iact/venv/bin/python manage.py run_scheduler
directory=/opt/iact/app
user=iact
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/iact/logs/scheduler.log
```

**Systemd Service:**
```ini
# /etc/systemd/system/iact.service

[Unit]
Description=IACT Call Center Analytics
After=network.target mysql.service

[Service]
Type=notify
User=iact
Group=iact
WorkingDirectory=/opt/iact/app
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=/opt/iact/venv/bin/gunicorn config.wsgi:application -c /opt/iact/config/gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Deployment Script:**
```bash
#!/bin/bash
# /opt/iact/scripts/deploy.sh

set -e

echo "🚀 Desplegando IACT..."

# Activar virtualenv
source /opt/iact/venv/bin/activate

# Pull código (Git)
cd /opt/iact/app
git pull origin main

# Instalar dependencias
pip install -r requirements/production.txt

# Migraciones
python manage.py migrate --no-input

# Collectstatic
python manage.py collectstatic --no-input

# Reiniciar servicios
sudo supervisorctl restart iact-gunicorn
sudo supervisorctl restart iact-apscheduler

# Verificar
curl -f http://localhost:8000/health || exit 1

echo "✅ Despliegue completado"
```

**Docker (❌ PROHIBIDO EN PRODUCCIÓN):**
```dockerfile
# ❌ PROHIBIDO - No crear Dockerfile para producción

# Dockerfile
# FROM python:3.11-slim  # ❌ NO USAR
# ...

# docker-compose.yml
# version: '3.8'  # ❌ NO USAR
# services:
#   web:
#     build: .
#     ...
```

**NOTA:** Docker permitido SOLO para desarrollo local del equipo, NUNCA en producción.

**Validación:**
```bash
# Verificar que NO exista Docker en producción
docker --version 2>/dev/null && echo "❌ VIOLACIÓN CNST-014: Docker instalado en producción"

# Verificar Gunicorn
ps aux | grep gunicorn && echo "✅ Gunicorn corriendo"

# Verificar Nginx
systemctl status nginx && echo "✅ Nginx corriendo"

# Verificar Supervisor
supervisorctl status | grep iact && echo "✅ Supervisor configurado"

# Verificar estructura
ls -la /opt/iact/ && echo "✅ Estructura correcta"
```

**Excepciones:** Docker permitido SOLO en:
- Entorno de desarrollo local del equipo
- Pruebas locales

**NUNCA** en:
- Servidor de producción
- Servidor de staging
- CI/CD deployment

---

## 🔐 2. RESTRICCIONES DE SEGURIDAD (DRF SECURE CODE)

> ⚠️ **IMPORTANTE:** Estas restricciones están basadas en las mejores prácticas de Django REST Framework y OWASP Top 10.

---

### 2.1 Configuración Django/DRF

**Código:** CNST-004 (implícito)

```yaml
✅ OBLIGATORIO EN PRODUCCIÓN:
  - DEBUG = False (nunca True)
  - SECRET_KEY desde variable de entorno
  - ALLOWED_HOSTS configurado explícitamente
  - SECURE_SSL_REDIRECT = True
  - SESSION_COOKIE_SECURE = True
  - CSRF_COOKIE_SECURE = True
  - SECURE_HSTS_SECONDS = 31536000
  - SECURE_CONTENT_TYPE_NOSNIFF = True
  - X_FRAME_OPTIONS = 'DENY'

✅ DRF SECURITY:
  - DEFAULT_AUTHENTICATION_CLASSES = [TokenAuthentication, SessionAuthentication]
  - DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]
  - DEFAULT_THROTTLE_CLASSES configurado
  - DEFAULT_RENDERER_CLASSES sin BrowsableAPIRenderer en producción

❌ PROHIBIDO:
  - DEBUG = True en producción
  - SECRET_KEY hardcodeado
  - ALLOWED_HOSTS = ['*']
  - Deshabilitar CSRF
```

**Configuración Completa:**
```python
# settings/production.py

import os
from decouple import config

# ✅ Security
DEBUG = False
SECRET_KEY = config('SECRET_KEY')  # Desde .env
ALLOWED_HOSTS = ['iact.company.local', '192.168.1.100']

# ✅ HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# ✅ DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        # ❌ NO BrowsableAPIRenderer en producción
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.utils.pagination.StandardPagination',
    'PAGE_SIZE': 50,
    'EXCEPTION_HANDLER': 'apps.utils.exceptions.custom_exception_handler',
}

# ✅ CORS (si aplica)
CORS_ALLOWED_ORIGINS = [
    'https://iact.company.local',
]
CORS_ALLOW_CREDENTIALS = True
```

**Validación:**
```bash
# Verificar configuración de seguridad
python manage.py check --deploy

# Debe pasar todas las validaciones
```

---

### 2.2 Autenticación y Autorización

**Código:** CNST-005 (implícito)

```yaml
✅ AUTENTICACIÓN:
  - Token-based (DRF TokenAuthentication)
  - Session-based para admin
  - Password hashing con PBKDF2
  - Password validation estricta
  - Máximo 3 intentos fallidos → bloqueo temporal

✅ AUTORIZACIÓN:
  - RBAC completo (ver MODELO_RBAC v6.0.0)
  - Decorador @require_function en TODOS los endpoints
  - Permisos a nivel de objeto donde aplique
  - Sin bypass de permisos

❌ PROHIBIDO:
  - Autenticación básica (BasicAuthentication)
  - JWT sin validación adecuada
  - Permisos hardcodeados
  - AllowAny en endpoints sensibles
```

**Configuración Password:**
```python
# settings/base.py

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Mínimo 12 caracteres
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]
```

**Uso de RBAC:**
```python
# apps/reports/views.py

from apps.access.decorators import require_function

class AbandonedCallsViewSet(viewsets.ViewSet):
    """Reporte de llamadas abandonadas."""
    
    permission_classes = [IsAuthenticated]
    
    @require_function('RPT-001')  # ✅ RBAC obligatorio
    def list(self, request):
        """Ve lista de reportes."""
        # Usuario debe tener función RPT-001
        pass
    
    @require_function('RPT-004')
    def export_csv(self, request):
        """Exporta a CSV."""
        # Usuario debe tener función RPT-004
        pass
```

---

### 2.3 Serializers y Exposición de Datos

**Código:** CNST-006 (implícito)

```yaml
✅ OBLIGATORIO:
  - Serializers explícitos (nunca __all__)
  - read_only_fields para campos sensibles
  - write_only_fields para passwords
  - Validaciones exhaustivas
  - No exponer PK internos (usar UUIDs)

❌ PROHIBIDO:
  - Meta.fields = '__all__'
  - Exponer passwords/tokens
  - Serializar objetos sin filtro
  - Lazy loading sin control
```

**Ejemplo Correcto:**
```python
# apps/users/serializers.py

from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer de usuario.
    
    ✅ Campos explícitos
    ✅ Password write_only
    ✅ Validaciones
    """
    
    class Meta:
        model = User
        fields = [  # ✅ Explícito, NO __all__
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']  # ✅ Read-only
        # ❌ NO exponer: password, last_login, etc
    
    def validate_email(self, value):
        """Valida email único."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email ya existe")
        return value
```

**Ejemplo Incorrecto:**
```python
# ❌ PROHIBIDO

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # ❌ Expone TODOS los campos
        # Incluye password, tokens, etc
```

---

### 2.4 Prevención de Vulnerabilidades

**Código:** CNST-007 (implícito)

```yaml
✅ SQL INJECTION:
  - ORM Django siempre (nunca raw SQL sin parametrizar)
  - Usar .filter() con Q objects
  - Evitar .raw() y .extra()

✅ XSS:
  - Templates auto-escape activado
  - Validar input del usuario
  - Content-Security-Policy headers

✅ CSRF:
  - Tokens CSRF obligatorios
  - @csrf_exempt solo si es absolutamente necesario
  - Validar origin headers

✅ MASS ASSIGNMENT:
  - Serializers con campos explícitos
  - No permitir actualización de campos sensibles

❌ PROHIBIDO:
  - SQL queries sin parametrizar
  - eval() o exec()
  - pickle sin validación
  - Archivos ejecutables en uploads
```

**SQL Seguro:**
```python
# ✅ CORRECTO - ORM parametrizado
calls = CallRecord.objects.filter(
    dFecha__gte=start_date,
    cMenu=menu
)

# ❌ INCORRECTO - SQL injection vulnerable
# query = f"SELECT * FROM tbl_historico WHERE dFecha >= '{start_date}'"
# cursor.execute(query)
```

**File Upload Seguro:**
```python
# apps/reports/views.py

from django.core.validators import FileExtensionValidator

class ReportUploadView(APIView):
    """Upload de archivos con validación."""
    
    def post(self, request):
        file = request.FILES.get('file')
        
        # ✅ Validar extensión
        validator = FileExtensionValidator(
            allowed_extensions=['csv', 'xlsx', 'pdf']
        )
        validator(file)
        
        # ✅ Validar tamaño (max 10MB)
        if file.size > 10 * 1024 * 1024:
            raise ValidationError("Archivo muy grande")
        
        # ✅ Validar content-type
        allowed_types = [
            'text/csv',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/pdf'
        ]
        if file.content_type not in allowed_types:
            raise ValidationError("Tipo de archivo no permitido")
        
        # ❌ NO ejecutables
        # Bloquear: .exe, .sh, .bat, .py, etc
```

---

### 2.5 Dependencias y SBOM

**Código:** CNST-008 (implícito)

```yaml
✅ OBLIGATORIO:
  - requirements.txt con versiones fijadas
  - safety check en cada build
  - pip-audit periódico
  - Actualizar dependencias críticas < 7 días
  - SBOM (Software Bill of Materials) generado

⚠️ MONITOREO:
  - GitHub Security Alerts habilitado
  - Dependabot configurado
  - Review manual de dependencias nuevas

❌ PROHIBIDO:
  - Versiones sin fijar (numpy>=1.0)
  - Dependencias sin mantenimiento activo
  - Usar código de fuentes no confiables
```

**requirements.txt:**
```txt
# ✅ CORRECTO - Versiones fijadas

Django==4.2.9
djangorestframework==3.14.0
django-filter==23.5
psycopg2-binary==2.9.9
mysqlclient==2.2.1
python-decouple==3.8
APScheduler==3.10.4

# ❌ INCORRECTO
# Django>=4.0  # Sin versión fija
# some-random-package  # Sin fuente confiable
```

**Safety Check:**
```bash
# Verificar vulnerabilidades
pip install safety
safety check --json

# Integrar en CI/CD
# - name: Safety check
#   run: |
#     pip install safety
#     safety check --json || exit 1
```

**SBOM Generation:**
```bash
# Generar SBOM
pip install pip-licenses
pip-licenses --format=json --output-file=sbom.json

# Incluir en documentación
```

---

## 📋 RESUMEN EJECUTIVO - PARTE 1

### Restricciones Críticas Documentadas

```
SECCIÓN 1: RESTRICCIONES TÉCNICAS CRÍTICAS
├─ 1.1 Comunicaciones → NO email (CNST-001)
├─ 1.2 Gestión de Sesiones → NO Redis (CNST-010) ⭐
├─ 1.3 Base de Datos Dual → Readonly IVR (CNST-002)
├─ 1.4 Actualización de Datos → NO real-time (CNST-003)
├─ 1.5 Infraestructura Cloud → NO AWS/GCP/Azure (CNST-011) ⭐
├─ 1.6 Servicios Externos → NO Twilio/Sentry/etc (CNST-012) ⭐
├─ 1.7 Message Brokers → NO Celery/RabbitMQ (CNST-013) ⭐
└─ 1.8 Containerización → NO Docker/K8s (CNST-014) ⭐

SECCIÓN 2: RESTRICCIONES DE SEGURIDAD
├─ 2.1 Configuración Django/DRF (CNST-004)
├─ 2.2 Autenticación y Autorización (CNST-005)
├─ 2.3 Serializers (CNST-006)
├─ 2.4 Prevención de Vulnerabilidades (CNST-007)
└─ 2.5 Dependencias y SBOM (CNST-008)

TOTAL: 13 restricciones críticas documentadas
```

### Nuevas Restricciones en v1.0.0

```
⭐ CNST-010: NO Redis (cache/sessions)
⭐ CNST-011: NO Cloud Services
⭐ CNST-012: NO Servicios Externos
⭐ CNST-013: NO Message Brokers
⭐ CNST-014: NO Containerización

IMPACTO: Arquitectura 100% on-premise tradicional
```

### Validación de Cumplimiento

```bash
# Ejecutar validaciones
./scripts/validate_restrictions_part1.sh

# Debe verificar:
✅ Sin configuración de email
✅ Sesiones en BD (no Redis)
✅ Database router correcto
✅ Sin dependencias cloud
✅ Sin servicios externos
✅ Sin Celery/RabbitMQ
✅ Sin Docker en producción
✅ Configuración seguridad Django
```

---

## 📚 REFERENCIAS

**Documentos Relacionados:**
- ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0 (3 partes)
- MODELO_RBAC_IACT_v6_0_0
- CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1 (5 partes)
- PROPUESTA_AMPLIACIONES_CNST_005-006

**Próximas Partes:**
- PARTE 2/3: Arquitectura, Base de Datos y Performance
- PARTE 3/3: Desarrollo, Auditoría y Referencias

---

**Documento generado:** 2026-01-19  
**Versión:** 1.0.0  
**Estado:** ✅ DEFINITIVO  
**Parte:** 1/3
