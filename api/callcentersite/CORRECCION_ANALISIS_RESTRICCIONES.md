# ⚠️ CORRECCIÓN ANÁLISIS - RESTRICCIONES DEL PROYECTO

**Fecha:** 16 de enero de 2026

---

## 🚫 RESTRICCIONES DEL PROYECTO (OLVIDADAS EN ANÁLISIS INICIAL)

### NO SE USA:
```
❌ Redis          - NO hay caché externo
❌ Celery         - NO hay tareas asíncronas
❌ Email          - NO se envían correos
❌ SMS            - NO se envían SMS
❌ Servicios cloud externos
❌ Webhooks
❌ Notificaciones push
```

### SÍ SE USA:
```
✅ PostgreSQL     - Base de datos principal
✅ MariaDB        - Solo IVR legacy (READ-ONLY)
✅ Django         - Framework
✅ DRF            - APIs REST
✅ JWT            - Autenticación
✅ Sistema interno - Solo usuarios internos
```

---

## 📝 CORRECCIONES AL ANÁLISIS

### ❌ ELIMINAR de dependencias:
```python
# INCORRECTO (del análisis original):
celery>=5.3.0          # ❌ NO SE USA
redis>=5.0.0           # ❌ NO SE USA
```

### ✅ DEPENDENCIAS REALES:
```python
# requirements.txt CORRECTO:

# Core
Django>=4.2
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
django-cors-headers>=4.3

# Base de datos
psycopg2-binary>=2.9.0      # PostgreSQL
mysqlclient>=2.2.0          # MariaDB (IVR legacy)

# Imágenes (CRÍTICO para avatar)
Pillow>=10.0.0

# Excel/CSV (para reports)
openpyxl>=3.1.0
pandas>=2.0.0

# PDF (para reports)
reportlab>=4.0.0

# Testing
pytest>=7.4.0
pytest-django>=4.5.0
pytest-cov>=4.1.0
factory-boy>=3.3.0
faker>=20.0.0
```

---

## 📊 REPORTS - CORRECCIÓN

### ❌ INCORRECTO (análisis original):
```python
# NO APLICABLE:
class ReportSchedule(models.Model):
    """Programación de reportes."""
    cron_expression = ...
    recipients = ...  # ❌ NO hay emails
```

### ✅ CORRECTO:
```python
# Reports se generan MANUALMENTE, no se programan
# Reports se DESCARGAN, no se envían por email

class Report(SoftDeleteMixin, models.Model):
    """Reporte generado manualmente."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50)
    parameters = models.JSONField(default=dict)
    created_by = models.ForeignKey(User, ...)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # El reporte se guarda como archivo
    result_file = models.FileField(
        upload_to='reports/%Y/%m/',
        null=True,
        blank=True
    )

class Dashboard(SoftDeleteMixin, models.Model):
    """Dashboard personalizado (vista en tiempo real)."""
    name = models.CharField(max_length=200)
    widgets = models.JSONField(default=list)
    layout = models.JSONField(default=dict)
    owner = models.ForeignKey(User, ...)
    is_shared = models.BooleanField(default=False)

# NO HAY ReportSchedule
# NO HAY envío automático
# Todo es manual y descarga directa
```

---

## 🔧 APIs REPORTS - CORRECCIÓN

### ❌ ELIMINAR:
```python
# NO APLICABLE:
POST /api/v1/reports/{id}/schedule/    # ❌ NO programación
POST /api/v1/reports/{id}/email/       # ❌ NO emails
```

### ✅ APIs CORRECTAS:
```python
# Reports - Generación manual
POST   /api/v1/reports/generate/         # Generar reporte ahora
GET    /api/v1/reports/                  # Listar reportes generados
GET    /api/v1/reports/{id}/             # Detalle reporte
DELETE /api/v1/reports/{id}/             # Eliminar reporte
GET    /api/v1/reports/{id}/download/    # Descargar archivo

# Exportación directa
POST   /api/v1/reports/export/csv/       # Exportar a CSV (descarga)
POST   /api/v1/reports/export/excel/     # Exportar a Excel (descarga)
POST   /api/v1/reports/export/pdf/       # Exportar a PDF (descarga)

# Dashboards (en tiempo real)
GET    /api/v1/dashboards/               # Listar dashboards
POST   /api/v1/dashboards/               # Crear dashboard
GET    /api/v1/dashboards/{id}/          # Ver dashboard (datos en vivo)
PUT    /api/v1/dashboards/{id}/          # Actualizar dashboard
DELETE /api/v1/dashboards/{id}/          # Eliminar dashboard

# Datos para dashboards (consultas en vivo)
POST   /api/v1/dashboards/data/          # Obtener datos para widgets
```

---

## 🔐 AUTHENTICATION - CORRECCIÓN

### ❌ ELIMINAR:
```python
# NO APLICABLE:
POST /api/v1/auth/reset-password/       # ❌ NO hay email
POST /api/v1/auth/forgot-password/      # ❌ NO hay email
POST /api/v1/auth/verify-email/         # ❌ NO hay email
POST /api/v1/auth/2fa/                   # ❌ NO hay 2FA (no SMS)
```

### ✅ APIs CORRECTAS:
```python
# Authentication (solo login/logout)
POST   /api/v1/auth/login/               # Login con username/password
POST   /api/v1/auth/logout/              # Logout
POST   /api/v1/auth/refresh/             # Refresh JWT token

# Cambio de contraseña (SOLO por administrador)
POST   /api/v1/users/{id}/reset-password-admin/  # Admin resetea password
POST   /api/v1/users/{id}/change-password/       # Usuario cambia su password

# Preguntas de seguridad (recuperación offline)
GET    /api/v1/auth/security-questions/          # Listar preguntas
POST   /api/v1/users/{id}/security-answers/      # Guardar respuestas
POST   /api/v1/auth/recover-password/            # Recuperar con preguntas

# NO hay emails, todo es manual/offline
```

---

## 📉 ESTIMACIÓN CORREGIDA

### ❌ TIEMPOS INCORRECTOS (análisis original):
```
Sprint 3: Reports con Celery/scheduling    15 horas  ❌ INCORRECTO
```

### ✅ TIEMPOS CORRECTOS:
```
Sprint 3: Reports (generación manual)       10 horas  ✅ CORRECTO
  - Modelos simplificados (sin scheduling)   2 horas
  - APIs generación manual                   4 horas
  - Exportación CSV/Excel/PDF                3 horas
  - Tests                                    1 hora
```

### TOTAL CORREGIDO:
```
Bloqueantes:     3 horas   (Migraciones + Deps)
Sprint 1:       14 horas   (Fundación - RBAC)
Sprint 2:       16 horas   (CRUD completo)
Sprint 3:       10 horas   (Reports manual) ✅ CORREGIDO
Sprint 4:       12 horas   (Deploy)
─────────────────────────
TOTAL:          55 horas   = 7-8 días laborales
```

---

## 🎯 CARACTERÍSTICAS DEL SISTEMA (CORRECTO)

### Sistema INTERNO de Call Center:

```
✅ Usuarios:      Solo empleados internos (no clientes)
✅ Acceso:        Intranet / VPN
✅ Autenticación: Username/password (JWT)
✅ Permisos:      RBAC granular (44 funciones)
✅ Datos:         PostgreSQL + MariaDB legacy
✅ Reports:       Generación manual + descarga
✅ Dashboards:    Visualización en tiempo real
✅ Auditoría:     Log de todas las operaciones
✅ Navegación:    Menú dinámico por permisos
```

### NO tiene:
```
❌ Registro público
❌ Emails automáticos
❌ Notificaciones push
❌ Tareas programadas (cron)
❌ Caché Redis
❌ Queue de trabajos
❌ Servicios externos
❌ 2FA (SMS/email)
```

---

## 🔄 FLUJO TÍPICO DE USO

### 1. Login:
```
Usuario → Login (username/password) → JWT token → Acceso
```

### 2. Navegación:
```
Usuario → MenuBuilder consulta permisos RBAC → Muestra menú personalizado
```

### 3. Generación de Reporte:
```
Usuario → Selecciona tipo reporte → Configura parámetros → Click "Generar"
  → Sistema procesa (inline, no async) → Genera archivo
  → Usuario descarga CSV/Excel/PDF
```

### 4. Dashboard:
```
Usuario → Abre dashboard → APIs consultan datos en vivo → Muestra widgets
  → Datos se actualizan en tiempo real (polling o manual)
```

### 5. Gestión de Usuarios (Admin):
```
Admin → CRUD usuarios → Asignar funciones RBAC
  → Si olvida password: Admin resetea manualmente
```

---

## 📋 PLAN DE ACCIÓN CORREGIDO

### SPRINT 0: PREPARACIÓN (4 horas)
```bash
# Dependencias CORRECTAS
pip install Pillow openpyxl pandas reportlab mysqlclient

# NO instalar:
# pip install celery redis  ❌ NO SE USA
```

### SPRINT 1: FUNDACIÓN (14 horas)
✅ Sin cambios - es correcto

### SPRINT 2: CRUD (16 horas)
✅ Sin cambios - es correcto

### SPRINT 3: REPORTS (10 horas) ✅ CORREGIDO
```python
# DÍA 5-6: Modelos Reports simplificados (4 horas)
- Report (sin scheduling)
- Dashboard
- NO ReportSchedule
- NO envío email

# DÍA 6: APIs Reports (4 horas)
- Generar manual
- Exportar CSV/Excel/PDF
- Dashboards en vivo

# DÍA 7: Tests (2 horas)
```

### SPRINT 4: DEPLOY (12 horas)
✅ Sin cambios - es correcto

---

## ✅ RESUMEN DE CORRECCIONES

### Eliminado del análisis:
- ❌ Redis
- ❌ Celery
- ❌ ReportSchedule
- ❌ Email notifications
- ❌ 2FA
- ❌ Password reset por email

### Agregado/Corregido:
- ✅ Reports generación MANUAL
- ✅ Descarga directa de archivos
- ✅ Dashboards consultas en VIVO
- ✅ Reset password por ADMIN
- ✅ Recuperación por preguntas de seguridad
- ✅ Sistema 100% interno
- ✅ mysqlclient para MariaDB legacy

### Tiempo total corregido:
```
ANTES: 61 horas (9 días)
AHORA: 55 horas (7-8 días) ✅ CORRECTO
```

---

## 🎯 PRÓXIMOS PASOS (CORRECTOS)

### DÍA 0 - AHORA:
```bash
# Dependencias REALES
pip install Pillow openpyxl pandas reportlab mysqlclient

# NO instalar celery ni redis
```

### DÍA 1:
```bash
# Migraciones (sin cambios)
python manage.py makemigrations users access core authentication audit
python manage.py migrate
```

### El resto del plan se mantiene igual, pero:
- Reports SIN programación
- Reports SIN emails
- Todo manual y descarga directa

---

**ANÁLISIS CORREGIDO - Respetando restricciones del proyecto** ✅
