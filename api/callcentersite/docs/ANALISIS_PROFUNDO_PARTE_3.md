# ANÁLISIS PROFUNDO DEL PROYECTO - PARTE 3 DE 5
## GAP ANALYSIS - QUÉ FALTA ESPECÍFICAMENTE

**Proyecto:** IACT Call Center System  
**Fecha Análisis:** 16 de enero de 2026  

---

## 3.1 MIGRACIONES (CRÍTICO - PRIORIDAD 1)

### Estado: 0 MIGRACIONES EN TODAS LAS APPS

**Impacto:** El sistema NO puede funcionar. Los modelos existen pero no están en la BD.

### Apps que necesitan migraciones URGENTES:

```bash
# 1. users (CRÍTICO - modelo modificado)
python manage.py makemigrations users
# Campos: avatar, phone, position, employee_id

# 2. access (CRÍTICO - sistema RBAC)
python manage.py makemigrations access
# Modelos: Function, UserFunctionAssignment, Module, UserModuleAccess

# 3. core (CRÍTICO - modelos base)
python manage.py makemigrations core
# Modelos: CallRecord, Center, Service, UserServiceAccess

# 4. authentication
python manage.py makemigrations authentication
# Modelos: SecurityQuestion, UserSecurityAnswer

# 5. audit
python manage.py makemigrations audit
# Modelo: AuditLog

# 6. pipeline
python manage.py makemigrations pipeline

# 7. Aplicar todas
python manage.py migrate
```

**Estimación:** 2 horas  
**Riesgo:** BLOQUEANTE - nada funciona sin esto

---

## 3.2 DEPENDENCIAS (PRIORIDAD 1)

### Dependencias sin verificar/instalar:

```python
# requirements.txt debe incluir:

# Core
Django>=4.2
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
django-cors-headers>=4.3

# Base de datos
psycopg2-binary>=2.9.0  # PostgreSQL
mysqlclient>=2.2.0      # MariaDB (IVR legacy)

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
factory-boy>=3.3.0  # Factories
faker>=20.0.0  # Datos fake

# NO SE USA:
# celery (no tareas asíncronas)
# redis (no caché)
# email libraries (no se envían emails)
```

**Acción:**
```bash
cd /tmp/iact-project/callcentersite
pip list | grep -E "(Pillow|openpyxl|reportlab|celery)"
# Si no están: pip install -r requirements.txt
```

**Estimación:** 1 hora  
**Riesgo:** BLOQUEANTE para funcionalidades específicas

---

## 3.3 MODELOS FALTANTES (PRIORIDAD 2)

### APP: REPORTS (completamente faltante)

```python
# apps/reports/models.py (a crear)

class Report(SoftDeleteMixin, models.Model):
    """Reporte generado manualmente (NO programado)."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50)  # daily, weekly, monthly, custom
    parameters = models.JSONField(default=dict)
    created_by = models.ForeignKey(User, ...)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    
    # Archivo generado (descarga directa)
    result_file = models.FileField(
        upload_to='reports/%Y/%m/',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('processing', 'Procesando'),
            ('completed', 'Completado'),
            ('failed', 'Fallido'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True)
    # ... campos

# NO HAY ReportSchedule - reportes se generan MANUALMENTE
# NO hay envío por email
# Usuario genera y descarga directamente

class Dashboard(SoftDeleteMixin, models.Model):
    """Dashboard personalizado con widgets en tiempo real."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    widgets = models.JSONField(default=list)  # Configuración widgets
    layout = models.JSONField(default=dict)   # Grid layout
    owner = models.ForeignKey(User, ...)
    is_shared = models.BooleanField(default=False)
    refresh_interval = models.IntegerField(
        default=60,
        help_text='Segundos entre actualizaciones (frontend polling)'
    )
    # ... campos

class SavedQuery(SoftDeleteMixin, models.Model):
    """Query guardada para reutilizar en reportes."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    query_type = models.CharField(max_length=50)
    parameters = models.JSONField(default=dict)
    created_by = models.ForeignKey(User, ...)
    is_public = models.BooleanField(default=False)
    # ... campos
```

**Estimación:** 2-3 horas (SIN scheduling, sin emails)  
**Riesgo:** Medio (no bloqueante inmediato)

---

## 3.4 APIs FALTANTES (PRIORIDAD 2-3)

### APP: ACCESS (RBAC)

```python
# apps/access/views.py (a completar)

# Funciones
POST   /api/v1/access/functions/              # Crear función
GET    /api/v1/access/functions/              # Listar funciones
GET    /api/v1/access/functions/{id}/         # Detalle función
PUT    /api/v1/access/functions/{id}/         # Actualizar
DELETE /api/v1/access/functions/{id}/         # Eliminar

# Asignaciones
POST   /api/v1/access/users/{id}/functions/   # Asignar función a user
DELETE /api/v1/access/users/{id}/functions/{func_id}/  # Revocar
GET    /api/v1/access/users/{id}/functions/   # Listar funciones de user

# Módulos  
# Ya existen parcialmente, completar CRUD

# Grupos (a implementar)
POST   /api/v1/access/groups/                 # Crear grupo
GET    /api/v1/access/groups/                 # Listar grupos
# ... CRUD completo
```

**Estimación:** 6-8 horas  
**Riesgo:** Alto (core del sistema)

### APP: USERS (Completar)

```python
# apps/users/views.py (a agregar)

POST   /api/v1/users/                         # Crear usuario  (existe)
GET    /api/v1/users/                         # Listar usuarios  (existe)
GET    /api/v1/users/{id}/                    # Detalle  (existe)
PUT    /api/v1/users/{id}/                    # Actualizar  (existe)
DELETE /api/v1/users/{id}/                    # Eliminar  (existe)

# Faltantes:
POST   /api/v1/users/{id}/change-password/    # Cambiar contraseña 
POST   /api/v1/users/reset-password/          # Reset contraseña 
POST   /api/v1/users/{id}/deactivate/         # Desactivar usuario 
POST   /api/v1/users/{id}/activate/           # Activar usuario 
```

**Estimación:** 4-5 horas  
**Riesgo:** Medio

### APP: REPORTS (Completar)

```python
# apps/reports/views.py (a crear completo)

# Reportes (generación MANUAL)
POST   /api/v1/reports/generate/              # Generar reporte ahora 
GET    /api/v1/reports/                       # Listar reportes generados 
GET    /api/v1/reports/{id}/                  # Detalle 
DELETE /api/v1/reports/{id}/                  # Eliminar 
GET    /api/v1/reports/{id}/download/         # Descargar archivo 
GET    /api/v1/reports/{id}/status/           # Estado generación 

# Exportación directa (sin guardar)
POST   /api/v1/reports/export/csv/            # Exportar CSV (descarga inmediata) 
POST   /api/v1/reports/export/excel/          # Exportar Excel (descarga inmediata) 
POST   /api/v1/reports/export/pdf/            # Exportar PDF (descarga inmediata) 

# Dashboards (consultas en tiempo real)
GET    /api/v1/dashboards/                    # Listar dashboards 
POST   /api/v1/dashboards/                    # Crear dashboard 
GET    /api/v1/dashboards/{id}/               # Detalle dashboard 
PUT    /api/v1/dashboards/{id}/               # Actualizar 
DELETE /api/v1/dashboards/{id}/               # Eliminar 
POST   /api/v1/dashboards/{id}/data/          # Obtener datos widgets (en vivo) 

# Queries guardadas (para reutilizar)
GET    /api/v1/saved-queries/                 # Listar queries 
POST   /api/v1/saved-queries/                 # Guardar query 
GET    /api/v1/saved-queries/{id}/            # Detalle 
PUT    /api/v1/saved-queries/{id}/            # Actualizar 
DELETE /api/v1/saved-queries/{id}/            # Eliminar 

# NO HAY:
# Programación (scheduling)
# Envío por email
# Notificaciones
```

**Estimación:** 10-12 horas (generación manual, sin scheduling)  
**Riesgo:** Medio (funcionalidad completa)

### APP: CORE (Completar)

```python
# apps/core/views.py (convertir de ReadOnly a CRUD completo)

# Centers (actualmente ReadOnly)
POST   /api/v1/core/centers/                  # Crear center 
PUT    /api/v1/core/centers/{id}/             # Actualizar 
DELETE /api/v1/core/centers/{id}/             # Eliminar 

# Services (actualmente ReadOnly)
POST   /api/v1/core/services/                 # Crear service 
PUT    /api/v1/core/services/{id}/            # Actualizar 
DELETE /api/v1/core/services/{id}/            # Eliminar 

# CallRecords (actualmente ReadOnly)
POST   /api/v1/core/call-records/             # Crear record 
```

**Estimación:** 4-5 horas  
**Riesgo:** Medio

---

## 3.5 MANAGEMENT COMMANDS FALTANTES (PRIORIDAD 3)

```python
# apps/access/management/commands/

# populate_functions.py
python manage.py populate_functions
# Poblar 44 funciones RBAC iniciales

# populate_modules.py  
python manage.py populate_modules
# Poblar módulos desde metadata JSON

# apps/core/management/commands/

# create_modules.py  (YA EXISTE)

# populate_initial_data.py
python manage.py populate_initial_data
# Poblar centers, services iniciales

# apps/users/management/commands/

# createsuperuser_with_functions.py
python manage.py createsuperuser_with_functions
# Crear superuser con todas las funciones
```

**Estimación:** 3-4 horas  
**Riesgo:** Bajo (no bloqueante)

---

## 3.6 SERIALIZERS FALTANTES (PRIORIDAD 2)

### REPORTS:
```python
# apps/reports/serializers.py (a crear)
ReportSerializer
ReportScheduleSerializer
DashboardSerializer
ReportExecutionSerializer
```

### ACCESS:
```python
# apps/access/serializers.py (completar)
FunctionSerializer  # Mejorar existente
UserFunctionAssignmentSerializer  # Crear
GroupSerializer  # Crear
```

**Estimación:** 3-4 horas  
**Riesgo:** Bajo (depende de modelos)

---

## 3.7 TESTS FALTANTES (PRIORIDAD 3)

```
tests/unit/reports/              # 0 tests 
  - test_models.py
  - test_views.py
  - test_serializers.py
  - test_export.py

tests/unit/access/               # Solo 2 tests parciales ⚠️
  - test_function_assignment.py  # Agregar
  - test_rbac_integration.py     # Agregar

tests/unit/core/                 # Completar
  - test_call_records.py         # Agregar
  - test_centers.py              # Agregar
  - test_services.py             # Agregar

tests/integration/               # Crear desde 0
  - test_rbac_flow.py
  - test_report_generation.py
  - test_user_workflow.py

tests/e2e/                       # Opcional
  - test_login_to_report.py
```

**Estimación:** 8-10 horas  
**Riesgo:** Bajo (calidad de código)

---

## 3.8 CONFIGURACIÓN FALTANTE (PRIORIDAD 3)

### Docker:
```dockerfile
# Dockerfile (a crear)
# docker-compose.yml (a crear)
# .dockerignore (a crear)
```

### CI/CD:
```yaml
# .github/workflows/tests.yml (a crear)
# .github/workflows/deploy.yml (a crear)
```

### Environment:
```bash
# .env.example (a crear)
# Documentar variables de entorno
```

### Logging:
```python
# Django logging a archivos locales
# Rotación de logs con RotatingFileHandler
# Monitoreo interno (sin servicios externos)
```

**Estimación:** 2-3 horas (logging local)  
**Riesgo:** Medio (deploy)

---

## 3.9 DOCUMENTACIÓN FALTANTE (PRIORIDAD 4)

```
README.md                 # Actualizar
CHANGELOG.md              # Crear
CONTRIBUTING.md           # Crear
API_DOCUMENTATION.md      # Crear (o Swagger)
DEPLOYMENT.md             # Crear
ARCHITECTURE.md           # Crear con diagramas
```

**Estimación:** 3-4 horas  
**Riesgo:** Bajo

---

## RESUMEN GAP ANALYSIS

### CRÍTICO (Prioridad 1 - Bloqueante):
```
Migraciones (0%)                 2 horas   BLOQUEANTE
Dependencias (Pillow, etc.)      1 hora    BLOQUEANTE
```

### ALTO (Prioridad 2 - Core funcionalidad):
```
Modelos Reports                  4 horas
APIs RBAC completas              8 horas
APIs Users completas             5 horas
APIs Core CRUD                   5 horas
Serializers faltantes            4 horas
```

### MEDIO (Prioridad 3 - Funcionalidad completa):
```
APIs Reports completas          15 horas
Management commands              4 horas
Tests faltantes                 10 horas
Configuración (Docker, CI/CD)    5 horas
```

### BAJO (Prioridad 4 - Calidad):
```
Documentación completa           4 horas
```

### TOTAL ESTIMADO:
```
Horas totales: 60-64 horas (corregido sin celery/emails)
Días (8h/día): 7.5-8 días
Semanas: 1.5-2 semanas
```

---

## PRÓXIMA PARTE

**PARTE 4:** Dependencias entre tareas y priorización

**PARTE 5:** Plan de acción dividido en sprints
