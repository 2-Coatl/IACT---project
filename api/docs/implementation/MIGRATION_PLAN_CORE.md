---
version: 1.0.0
date: 2026-01-20
type: Migration Plan
categoria: implementation
tema: Migration Plan - Refactoring apps/core/
---

# MIGRATION PLAN - apps/core/ Refactoring

**FASE 2 - PARTE 1 - TAREA 1.3**

---

## 📋 OBJETIVO

Mover modelos concretos de apps/core/ a apps correctas **SIN alterar tablas en BD**.

### Modelos a Mover

```yaml
apps/core/ → apps/pipeline/:
  - Center (db_table='core_centers')
  - Service (db_table='core_services')
  - CallRecord (db_table='core_call_records')

apps/core/ → apps/access/:
  - UserServiceAccess (db_table='core_user_service_access')
```

---

## 🎯 ESTRATEGIA: SeparateDatabaseAndState

### Concepto

Django permite declarar modelos en una app sin crear/modificar tablas usando `SeparateDatabaseAndState`:

```python
migrations.SeparateDatabaseAndState(
    database_operations=[],  # ← NADA - no tocar BD
    state_operations=[       # ← Solo actualizar Django ORM
        migrations.CreateModel(...),
        migrations.DeleteModel(...),
    ],
)
```

**Beneficios:**
- ✅ NO cambios en base de datos
- ✅ Tablas existentes siguen funcionando
- ✅ Solo cambia el código Python (imports)
- ✅ Rollback fácil

---

## 📦 MIGRATIONS REQUERIDAS (3 migrations)

### Migration 1: apps/pipeline/ - Agregar Center, Service, CallRecord

**Archivo:** `apps/pipeline/migrations/0002_add_core_models.py`

**Dependencias:**
- `('pipeline', '0001_initial')` - Migration anterior de pipeline
- `('core', '0002_current')` - Migration actual de core

**Contenido Completo:**

```python
# Generated manually for FASE 2 refactoring
# apps/pipeline/migrations/0002_add_core_models.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    
    dependencies = [
        ('pipeline', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # NADA - las tablas core_centers, core_services, 
                # core_call_records ya existen en la BD
            ],
            state_operations=[
                # ========================================
                # MODEL: Center
                # ========================================
                migrations.CreateModel(
                    name='Center',
                    fields=[
                        ('id', models.BigAutoField(
                            auto_created=True,
                            primary_key=True,
                            serialize=False,
                            verbose_name='ID'
                        )),
                        ('nombre', models.CharField(
                            max_length=200,
                            help_text='Nombre del centro de atención'
                        )),
                        ('codigo', models.CharField(
                            max_length=50,
                            unique=True,
                            help_text='Código único del centro (ej: CT_SCL)'
                        )),
                        ('descripcion', models.TextField(
                            blank=True,
                            help_text='Descripción del centro'
                        )),
                        ('direccion', models.TextField(
                            blank=True,
                            help_text='Dirección física del centro'
                        )),
                        ('activo', models.BooleanField(
                            default=True,
                            help_text='Centro activo o inactivo'
                        )),
                        ('created_at', models.DateTimeField(
                            auto_now_add=True,
                            verbose_name='Fecha creación'
                        )),
                        ('updated_at', models.DateTimeField(
                            auto_now=True,
                            verbose_name='Fecha actualización'
                        )),
                        ('is_deleted', models.BooleanField(
                            default=False,
                            help_text='Soft delete flag'
                        )),
                        ('deleted_at', models.DateTimeField(
                            null=True,
                            blank=True,
                            help_text='Fecha de eliminación'
                        )),
                    ],
                    options={
                        'db_table': 'core_centers',  # ✅ PRESERVAR
                        'verbose_name': 'Centro',
                        'verbose_name_plural': 'Centros',
                        'ordering': ['nombre'],
                        'indexes': [
                            models.Index(fields=['activo'], name='idx_center_activo'),
                            models.Index(fields=['is_deleted'], name='idx_center_deleted'),
                        ],
                    },
                ),
                
                # ========================================
                # MODEL: Service
                # ========================================
                migrations.CreateModel(
                    name='Service',
                    fields=[
                        ('id', models.BigAutoField(
                            auto_created=True,
                            primary_key=True,
                            serialize=False,
                            verbose_name='ID'
                        )),
                        ('numero_800', models.CharField(
                            max_length=20,
                            unique=True,
                            help_text='Número 800 del servicio'
                        )),
                        ('nombre', models.CharField(
                            max_length=200,
                            help_text='Nombre del servicio'
                        )),
                        ('descripcion', models.TextField(
                            blank=True,
                            help_text='Descripción del servicio'
                        )),
                        ('center', models.ForeignKey(
                            on_delete=django.db.models.deletion.PROTECT,
                            related_name='services',
                            to='pipeline.center',  # ✅ Nueva ubicación
                            help_text='Centro al que pertenece este servicio'
                        )),
                        ('activo', models.BooleanField(
                            default=True,
                            help_text='Servicio activo o inactivo'
                        )),
                        ('created_at', models.DateTimeField(
                            auto_now_add=True,
                            verbose_name='Fecha creación'
                        )),
                        ('updated_at', models.DateTimeField(
                            auto_now=True,
                            verbose_name='Fecha actualización'
                        )),
                        ('is_deleted', models.BooleanField(
                            default=False,
                            help_text='Soft delete flag'
                        )),
                        ('deleted_at', models.DateTimeField(
                            null=True,
                            blank=True,
                            help_text='Fecha de eliminación'
                        )),
                    ],
                    options={
                        'db_table': 'core_services',  # ✅ PRESERVAR
                        'verbose_name': 'Servicio',
                        'verbose_name_plural': 'Servicios',
                        'ordering': ['nombre'],
                        'indexes': [
                            models.Index(fields=['activo'], name='idx_service_activo'),
                            models.Index(fields=['center'], name='idx_service_center'),
                            models.Index(fields=['is_deleted'], name='idx_service_deleted'),
                        ],
                    },
                ),
                
                # ========================================
                # MODEL: CallRecord
                # ========================================
                migrations.CreateModel(
                    name='CallRecord',
                    fields=[
                        ('id', models.BigAutoField(
                            auto_created=True,
                            primary_key=True,
                            serialize=False,
                            verbose_name='ID'
                        )),
                        ('fecha', models.DateField(
                            help_text='Fecha del registro'
                        )),
                        ('telefono', models.CharField(
                            max_length=20,
                            help_text='Número de teléfono'
                        )),
                        ('servicio_800', models.CharField(
                            max_length=20,
                            help_text='Número 800 del servicio'
                        )),
                        ('total_llamadas', models.IntegerField(
                            default=0,
                            help_text='Total de llamadas en el día'
                        )),
                        ('llamadas_contestadas', models.IntegerField(
                            default=0,
                            help_text='Llamadas contestadas'
                        )),
                        ('llamadas_abandonadas', models.IntegerField(
                            default=0,
                            help_text='Llamadas abandonadas'
                        )),
                        ('duracion_total_segundos', models.IntegerField(
                            default=0,
                            help_text='Duración total en segundos'
                        )),
                        ('created_at', models.DateTimeField(
                            auto_now_add=True,
                            verbose_name='Fecha creación'
                        )),
                        ('updated_at', models.DateTimeField(
                            auto_now=True,
                            verbose_name='Fecha actualización'
                        )),
                        ('is_deleted', models.BooleanField(
                            default=False,
                            help_text='Soft delete flag'
                        )),
                        ('deleted_at', models.DateTimeField(
                            null=True,
                            blank=True,
                            help_text='Fecha de eliminación'
                        )),
                    ],
                    options={
                        'db_table': 'core_call_records',  # ✅ PRESERVAR
                        'verbose_name': 'Registro de Llamada',
                        'verbose_name_plural': 'Registros de Llamadas',
                        'ordering': ['-fecha'],
                        'unique_together': [('fecha', 'telefono', 'servicio_800')],
                        'indexes': [
                            models.Index(fields=['fecha'], name='idx_callrec_fecha'),
                            models.Index(fields=['servicio_800'], name='idx_callrec_servicio'),
                            models.Index(fields=['is_deleted'], name='idx_callrec_deleted'),
                        ],
                    },
                ),
            ],
        ),
    ]
```

---

### Migration 2: apps/access/ - Agregar UserServiceAccess

**Archivo:** `apps/access/migrations/0002_add_user_service_access.py`

**Dependencias:**
- `('access', '0001_initial')` - Migration anterior de access
- `('pipeline', '0002_add_core_models')` - Necesita Service

**Contenido Completo:**

```python
# Generated manually for FASE 2 refactoring
# apps/access/migrations/0002_add_user_service_access.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    
    dependencies = [
        ('access', '0001_initial'),
        ('pipeline', '0002_add_core_models'),  # Necesita Service
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # NADA - tabla core_user_service_access ya existe
            ],
            state_operations=[
                migrations.CreateModel(
                    name='UserServiceAccess',
                    fields=[
                        ('id', models.BigAutoField(
                            auto_created=True,
                            primary_key=True,
                            serialize=False,
                            verbose_name='ID'
                        )),
                        ('user', models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='service_accesses',
                            to=settings.AUTH_USER_MODEL,
                            help_text='Usuario con acceso'
                        )),
                        ('service', models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='user_accesses',
                            to='pipeline.service',  # ✅ Nueva ubicación
                            help_text='Servicio al que tiene acceso'
                        )),
                        ('granted_at', models.DateTimeField(
                            auto_now_add=True,
                            verbose_name='Fecha concesión'
                        )),
                        ('granted_by', models.ForeignKey(
                            on_delete=django.db.models.deletion.SET_NULL,
                            null=True,
                            related_name='granted_accesses',
                            to=settings.AUTH_USER_MODEL,
                            help_text='Usuario que concedió el acceso'
                        )),
                        ('reason', models.TextField(
                            blank=True,
                            help_text='Razón del acceso'
                        )),
                        ('is_active', models.BooleanField(
                            default=True,
                            help_text='Acceso activo'
                        )),
                        ('revoked_at', models.DateTimeField(
                            null=True,
                            blank=True,
                            verbose_name='Fecha revocación'
                        )),
                        ('revoked_by', models.ForeignKey(
                            on_delete=django.db.models.deletion.SET_NULL,
                            null=True,
                            blank=True,
                            related_name='revoked_accesses',
                            to=settings.AUTH_USER_MODEL,
                            help_text='Usuario que revocó el acceso'
                        )),
                        ('is_deleted', models.BooleanField(
                            default=False,
                            help_text='Soft delete flag'
                        )),
                        ('deleted_at', models.DateTimeField(
                            null=True,
                            blank=True,
                            help_text='Fecha de eliminación'
                        )),
                    ],
                    options={
                        'db_table': 'core_user_service_access',  # ✅ PRESERVAR
                        'verbose_name': 'Acceso Usuario-Servicio',
                        'verbose_name_plural': 'Accesos Usuario-Servicio',
                        'unique_together': [('user', 'service')],
                        'indexes': [
                            models.Index(fields=['user'], name='idx_usersvc_user'),
                            models.Index(fields=['service'], name='idx_usersvc_service'),
                            models.Index(fields=['is_active'], name='idx_usersvc_active'),
                        ],
                    },
                ),
            ],
        ),
    ]
```

---

### Migration 3: apps/core/ - Eliminar Modelos Concretos

**Archivo:** `apps/core/migrations/0003_remove_concrete_models.py`

**Dependencias:**
- `('core', '0002_previous')` - Migration actual de core
- `('pipeline', '0002_add_core_models')` - Modelos ya creados
- `('access', '0002_add_user_service_access')` - UserServiceAccess creado

**Contenido Completo:**

```python
# Generated manually for FASE 2 refactoring
# apps/core/migrations/0003_remove_concrete_models.py

from django.db import migrations


class Migration(migrations.Migration):
    
    dependencies = [
        ('core', '0002_previous_migration'),  # ← Ajustar al nombre real
        ('pipeline', '0002_add_core_models'),
        ('access', '0002_add_user_service_access'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # NADA - NO tocar tablas (quedan intactas)
            ],
            state_operations=[
                # Solo decirle a Django que estos modelos ya no están en core
                migrations.DeleteModel(name='Center'),
                migrations.DeleteModel(name='Service'),
                migrations.DeleteModel(name='CallRecord'),
                migrations.DeleteModel(name='UserServiceAccess'),
            ],
        ),
    ]
```

---

## 🔄 ORDEN DE EJECUCIÓN

### Paso 1: Identificar Migration Actual de core

```bash
cd /tmp/iact-real/callcentersite

# Ver última migration de core
python manage.py showmigrations core

# Output esperado:
# core
#  [X] 0001_initial
#  [X] 0002_add_some_field  ← Esta es la actual
```

**Actualizar dependencies en migration 0003:**
```python
('core', '0002_add_some_field'),  # ← Ajustar al nombre real
```

---

### Paso 2: Crear Archivos de Migration Manualmente

```bash
# IMPORTANTE: SeparateDatabaseAndState requiere migrations MANUALES
# makemigrations NO las genera automáticamente

# 1. Crear migration pipeline
cat > apps/pipeline/migrations/0002_add_core_models.py << 'EOF'
[pegar contenido Migration 1]
EOF

# 2. Crear migration access
cat > apps/access/migrations/0002_add_user_service_access.py << 'EOF'
[pegar contenido Migration 2]
EOF

# 3. Crear migration core
cat > apps/core/migrations/0003_remove_concrete_models.py << 'EOF'
[pegar contenido Migration 3]
EOF
```

---

### Paso 3: Aplicar Migrations en Orden

```bash
# 1. Pipeline primero (crea Center, Service, CallRecord)
python manage.py migrate pipeline 0002_add_core_models

# Output esperado:
# Running migration 0002_add_core_models... OK
# (0.001 seconds) ← Muy rápido porque NO toca BD

# 2. Access segundo (crea UserServiceAccess, depende de Service)
python manage.py migrate access 0002_add_user_service_access

# Output esperado:
# Running migration 0002_add_user_service_access... OK
# (0.001 seconds)

# 3. Core último (elimina modelos del ORM de core)
python manage.py migrate core 0003_remove_concrete_models

# Output esperado:
# Running migration 0003_remove_concrete_models... OK
# (0.001 seconds)
```

---

### Paso 4: Verificar Estado

```bash
# Ver estado migrations
python manage.py showmigrations pipeline access core

# Output esperado:
# pipeline
#  [X] 0001_initial
#  [X] 0002_add_core_models  ← Nueva
# access
#  [X] 0001_initial
#  [X] 0002_add_user_service_access  ← Nueva
# core
#  [X] 0001_initial
#  [X] 0002_previous
#  [X] 0003_remove_concrete_models  ← Nueva
```

---

### Paso 5: Verificar Base de Datos (NO debe haber cambios)

```bash
# Conectar a base de datos
python manage.py dbshell

# En PostgreSQL:
\d core_centers
# Debe mostrar la tabla SIN cambios

\d core_services
# Debe mostrar la tabla SIN cambios

\d core_call_records
# Debe mostrar la tabla SIN cambios

\d core_user_service_access
# Debe mostrar la tabla SIN cambios

\q
```

**Resultado Esperado:**
- ✅ Todas las tablas existen
- ✅ Todas tienen los mismos campos
- ✅ Todas tienen los mismos datos
- ✅ 0 cambios en estructura
- ✅ 0 cambios en datos

---

## ✅ VALIDACIÓN COMPLETA

### 1. Importar Modelos en Django Shell

```bash
python manage.py shell
```

```python
# Test 1: Importar desde pipeline
from apps.pipeline.models import Center, Service, CallRecord

# Verificar que funcionan
Center.objects.count()  # Debe retornar número de registros
Service.objects.count()
CallRecord.objects.count()

# Test 2: Importar desde access
from apps.access.models import UserServiceAccess

UserServiceAccess.objects.count()

# Test 3: Verificar que NO están en core
try:
    from apps.core.models import Center
    print("ERROR: Center aún está en core")
except ImportError:
    print("✅ Center NO está en core (correcto)")

# Test 4: Verificar FK
service = Service.objects.first()
print(service.center)  # Debe mostrar el Center
print(service.center.__class__)  # Debe ser pipeline.models.Center

# Exit
exit()
```

---

### 2. Ejecutar Tests

```bash
# Tests de pipeline
pytest tests/unit/pipeline/ -v

# Tests de access
pytest tests/unit/access/ -v

# Tests de core
pytest tests/unit/core/ -v

# Todos los tests
pytest tests/ -v
```

**Resultado Esperado:**
- ✅ Tests pasando
- ✅ 0 errores de imports
- ✅ 0 errores de FK
- ✅ Coverage >85%

---

### 3. Verificar Admin

```bash
python manage.py runserver

# Ir a http://localhost:8000/admin/
# Verificar:
# - PIPELINE > Centers (debe aparecer)
# - PIPELINE > Services (debe aparecer)
# - PIPELINE > Call records (debe aparecer)
# - ACCESS > User service accesses (debe aparecer)
# - CORE > NO debe tener estos modelos
```

---

## 🔙 ROLLBACK (si necesario)

### Opción 1: Rollback Migrations

```bash
# Revertir en orden inverso

# 1. Core primero
python manage.py migrate core 0002_previous_migration

# 2. Access segundo
python manage.py migrate access 0001_initial

# 3. Pipeline último
python manage.py migrate pipeline 0001_initial
```

---

### Opción 2: Rollback Código (Git)

```bash
cd /tmp/iact-real

# Ver estado
git status

# Revertir cambios
git checkout apps/core/models.py
git checkout apps/pipeline/models.py
git checkout apps/access/models.py

# Eliminar migrations creadas
rm apps/pipeline/migrations/0002_add_core_models.py
rm apps/access/migrations/0002_add_user_service_access.py
rm apps/core/migrations/0003_remove_concrete_models.py

# Revertir migrations en BD
python manage.py migrate pipeline 0001_initial
python manage.py migrate access 0001_initial
python manage.py migrate core 0002_previous_migration
```

---

## 📊 CHECKLIST FINAL

```yaml
Pre-ejecución:
  [ ] Backup de base de datos realizado
  [ ] Git commit de código actual
  [ ] Tests base pasando

Migrations Creadas:
  [ ] apps/pipeline/migrations/0002_add_core_models.py
  [ ] apps/access/migrations/0002_add_user_service_access.py
  [ ] apps/core/migrations/0003_remove_concrete_models.py

Migrations Aplicadas:
  [ ] migrate pipeline 0002 (OK)
  [ ] migrate access 0002 (OK)
  [ ] migrate core 0003 (OK)

Verificación BD:
  [ ] Tablas sin cambios
  [ ] Datos intactos
  [ ] 0 ALTER TABLE ejecutados

Verificación Django:
  [ ] Imports apps.pipeline.models funcionan
  [ ] Imports apps.access.models funcionan
  [ ] Imports apps.core.models (Center, etc) fallan (correcto)
  [ ] ForeignKeys funcionan

Tests:
  [ ] pytest tests/unit/pipeline/ (pasan)
  [ ] pytest tests/unit/access/ (pasan)
  [ ] pytest tests/unit/core/ (pasan)
  [ ] pytest tests/ (todos pasan)
  [ ] Coverage >85%

Admin Django:
  [ ] PIPELINE/Centers visible
  [ ] PIPELINE/Services visible
  [ ] PIPELINE/Call records visible
  [ ] ACCESS/User service accesses visible
  [ ] CORE sin estos modelos
```

---

## ⏱️ ESTIMACIÓN DE TIEMPO

```yaml
Identificar migration actual core: 10 min
Crear 3 archivos migration: 30 min
Aplicar migrations: 5 min
Verificar BD: 10 min
Verificar Django shell: 10 min
Ejecutar tests: 15 min
Verificar admin: 5 min
Correcciones (si necesario): 30 min

Total: ~2 horas
```

---

## 🎯 RESULTADO ESPERADO

```yaml
Después de Migrations:
  ✅ Center en apps.pipeline.models
  ✅ Service en apps.pipeline.models
  ✅ CallRecord en apps.pipeline.models
  ✅ UserServiceAccess en apps.access.models
  ✅ apps/core/models.py solo con abstract models
  ✅ 0 cambios en tablas BD
  ✅ 0 cambios en datos
  ✅ Tests pasando
  ✅ Admin funcionando
```

---

**FIN DEL MIGRATION PLAN**

**Plan Completo ✅**  
**Listo para Ejecución ✅**  
**Próximo:** PARTE 2 - Mover código Python (models.py, services/, etc)
