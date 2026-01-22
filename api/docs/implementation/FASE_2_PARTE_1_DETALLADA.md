---
version: 1.0.0
date: 2026-01-20
project: IACT Call Center System
type: Plan de Implementación - FASE 2
categoria: implementacion/fase-2
tema: FASE 2 - Refactoring apps/core/ + Renombre IVR (8 Partes)
autor: Claude Technical Analysis
tags: [fase-2, refactoring, core, pipeline, ivr, migrations]
plan_base: PLAN_IMPLEMENTACION_v3_1_0.md
estado: ready-to-execute
---

# FASE 2: REFACTORING apps/core/ + RENOMBRE IVR
## 8 PARTES - 7 DÍAS DE IMPLEMENTACIÓN

**Objetivo General:**
Limpiar apps/core/ dejando SOLO componentes abstractos, mover modelos concretos a apps correctas, y renombrar apps/ivr_legacy/ → apps/ivr/.

**Duración:** 7 días (Día 15-21)
**Partes:** 8
**Estado:** Listo para ejecutar

---

## 📊 ESTADO ACTUAL (Punto de Partida)

```yaml
Código Actual:
  apps/core/models.py:
    ❌ Center (db_table='core_centers')
    ❌ Service (db_table='core_services')
    ❌ CallRecord (db_table='core_call_records')
    ❌ UserServiceAccess (db_table='core_user_service_access')
    ✅ TimeStampedModel (abstract=True)
    ✅ SoftDeleteMixin (abstract=True)
    ✅ AuditedModel (abstract=True)
  
  apps/core/services/:
    ❌ center_service.py (9 métodos)
    ❌ service_service.py (12 métodos)
    ❌ call_record_service.py (11 métodos)
  
  apps/core/:
    ❌ serializers.py (20 serializers)
    ❌ filters.py (4 filters)
    ❌ permissions.py (6 custom permissions)
    ❌ viewsets.py (pausado, no completado)
  
  apps/ivr_legacy/:
    ⚠️  Nombre incorrecto (debe ser apps/ivr/)

Tests:
  ✅ tests/factories/ (137 factories)
  ✅ tests/mocks/ (81 mocks)
  ✅ tests/conftest.py (246+ fixtures)

Apps Destino:
  ✅ apps/pipeline/ (existe)
  ✅ apps/access/ (existe)
  ❌ apps/ivr/ (renombrar desde ivr_legacy)
```

---

## 🎯 ESTADO OBJETIVO (Al Finalizar FASE 2)

```yaml
apps/core/models.py:
  ✅ TimeStampedModel (abstract=True)
  ✅ SoftDeleteMixin (abstract=True)
  ✅ AuditedModel (abstract=True)
  ❌ NINGÚN modelo concreto

apps/pipeline/models.py:
  ✅ Center (movido, db_table='core_centers')
  ✅ Service (movido, db_table='core_services')
  ✅ CallRecord (movido, db_table='core_call_records')
  ✅ JobExecution, JobLog, ScheduledJob (ya existen)

apps/pipeline/services/:
  ✅ center_service.py (movido)
  ✅ service_service.py (movido)
  ✅ call_record_service.py (movido)

apps/pipeline/:
  ✅ serializers.py (movido, filtrado)
  ✅ filters.py (movido, filtrado)
  ✅ permissions.py (movido, filtrado)
  ✅ viewsets.py (completado)

apps/access/models.py:
  ✅ UserServiceAccess (movido, db_table='core_user_service_access')

apps/ivr/:
  ✅ Renombrado desde apps/ivr_legacy/
  ✅ Imports actualizados

Migrations:
  ✅ SeparateDatabaseAndState (sin cambios BD)
  ✅ Tests pasando >85%

Resultado:
  ✅ apps/core/ limpio (solo abstract)
  ✅ Arquitectura correcta
  ✅ Flujo ETL preservado
  ✅ 0 cambios en base de datos
```

---

## 📋 ÍNDICE DE PARTES

```yaml
PARTE 1 (Día 15): Preparación y Renombre IVR
  - Documentar estado actual
  - Renombrar apps/ivr_legacy/ → apps/ivr/
  - Plan de migrations
  
PARTE 2 (Día 16): Preparar apps/pipeline/
  - Verificar estructura
  - Planificar integración

PARTE 3 (Día 17): Mover Modelos a apps/pipeline/
  - Center, Service, CallRecord
  - Migrations SeparateDatabaseAndState

PARTE 4 (Día 18): Actualizar Imports
  - ~50 archivos Python
  - Script automatizado

PARTE 5 (Día 19): Mover Services/Serializers
  - Services → apps/pipeline/services/
  - Serializers, filters, permissions

PARTE 6 (Día 20): Limpiar apps/core/
  - Eliminar modelos concretos
  - Solo abstract models

PARTE 7 (Día 21 - AM): Mover UserServiceAccess
  - UserServiceAccess → apps/access/

PARTE 8 (Día 21 - PM): Testing y Validación
  - Migrations
  - Tests >85%
  - Smoke tests
```

---

# PARTE 1: PREPARACIÓN Y RENOMBRE IVR (Día 15)

## Objetivo
Documentar estado actual, renombrar apps/ivr_legacy/ → apps/ivr/, y crear plan de migrations.

## Duración
1 día completo (8 horas)

---

## TAREA 1.1: Documentar Estado Actual (1 hora)

### Objetivo
Crear inventario completo de imports y dependencias.

### Comandos
```bash
# 1. Listar todos los imports de Center, Service, CallRecord
cd /tmp/iact-real/callcentersite

grep -r "from apps.core.models import Center" apps/ > /tmp/imports_center.txt
grep -r "from apps.core.models import Service" apps/ > /tmp/imports_service.txt
grep -r "from apps.core.models import CallRecord" apps/ > /tmp/imports_callrecord.txt
grep -r "from apps.core.models import UserServiceAccess" apps/ > /tmp/imports_userserviceaccess.txt

# 2. Contar archivos afectados
echo "=== IMPORTS A ACTUALIZAR ==="
echo "Center: $(grep -r "from apps.core.models import Center" apps/ | wc -l) archivos"
echo "Service: $(grep -r "from apps.core.models import Service" apps/ | wc -l) archivos"
echo "CallRecord: $(grep -r "from apps.core.models import CallRecord" apps/ | wc -l) archivos"
echo "UserServiceAccess: $(grep -r "from apps.core.models import UserServiceAccess" apps/ | wc -l) archivos"

# 3. Listar imports de ivr_legacy
grep -r "from apps.ivr_legacy" . --include="*.py" > /tmp/imports_ivr_legacy.txt
echo "ivr_legacy: $(grep -r "from apps.ivr_legacy" . --include="*.py" | wc -l) archivos"

# 4. Verificar estructura apps/pipeline/
ls -la apps/pipeline/
cat apps/pipeline/models.py | head -50
```

### Deliverable
```bash
# Crear reporte
cat > /tmp/iact-real/docs/implementation/FASE_2_ESTADO_ACTUAL.md << 'EOF'
# FASE 2 - ESTADO ACTUAL

## Imports a Actualizar

### Center
[Pegar contenido de /tmp/imports_center.txt]

### Service
[Pegar contenido de /tmp/imports_service.txt]

### CallRecord
[Pegar contenido de /tmp/imports_callrecord.txt]

### UserServiceAccess
[Pegar contenido de /tmp/imports_userserviceaccess.txt]

### ivr_legacy
[Pegar contenido de /tmp/imports_ivr_legacy.txt]

## apps/pipeline/ Actual
[Pegar estructura]

## Total Archivos a Modificar
- Center: X archivos
- Service: Y archivos
- CallRecord: Z archivos
- UserServiceAccess: W archivos
- ivr_legacy: V archivos
EOF
```

**Checklist:**
- [ ] Inventario de imports completo
- [ ] Archivos contados
- [ ] Reporte creado

---

## TAREA 1.2: Renombrar apps/ivr_legacy/ → apps/ivr/ (2 horas)

### Objetivo
Renombrar directorio y actualizar todos los imports.

### Script de Renombre

```bash
#!/bin/bash
# /tmp/iact-real/scripts/rename_ivr_legacy.sh

set -e  # Exit on error

echo "=== FASE 2 PARTE 1 - Renombre IVR Legacy ==="
echo ""

cd /tmp/iact-real/callcentersite

# 1. BACKUP
echo "1. Creando backup..."
cp -r apps/ivr_legacy apps/ivr_legacy.backup
echo "✅ Backup creado: apps/ivr_legacy.backup"
echo ""

# 2. RENOMBRAR DIRECTORIO
echo "2. Renombrando directorio..."
mv apps/ivr_legacy apps/ivr
echo "✅ apps/ivr_legacy → apps/ivr"
echo ""

# 3. ACTUALIZAR IMPORTS EN apps/
echo "3. Actualizando imports en apps/..."

find apps -name "*.py" -type f -exec sed -i \
  's/from apps\.ivr_legacy/from apps.ivr/g' {} \;

find apps -name "*.py" -type f -exec sed -i \
  's/import apps\.ivr_legacy/import apps.ivr/g' {} \;

find apps -name "*.py" -type f -exec sed -i \
  's/apps\.ivr_legacy\./apps.ivr./g' {} \;

echo "✅ Imports actualizados en apps/"
echo ""

# 4. ACTUALIZAR IMPORTS EN tests/
echo "4. Actualizando imports en tests/..."

find ../tests -name "*.py" -type f -exec sed -i \
  's/from apps\.ivr_legacy/from apps.ivr/g' {} \;

find ../tests -name "*.py" -type f -exec sed -i \
  's/import apps\.ivr_legacy/import apps.ivr/g' {} \;

echo "✅ Imports actualizados en tests/"
echo ""

# 5. ACTUALIZAR SETTINGS
echo "5. Actualizando settings..."

sed -i "s/'apps\.ivr_legacy'/'apps.ivr'/g" config/settings/base.py

echo "✅ INSTALLED_APPS actualizado"
echo ""

# 6. ACTUALIZAR DATABASE ROUTER
echo "6. Actualizando database router..."

find . -name "*.py" -type f -exec sed -i \
  's/ivr_legacy/ivr/g' {} \;

echo "✅ Database router actualizado"
echo ""

# 7. VERIFICAR
echo "7. Verificando cambios..."
echo "Verificar INSTALLED_APPS:"
grep "apps.ivr" config/settings/base.py

echo ""
echo "Verificar que no queden referencias a ivr_legacy:"
LEGACY_COUNT=$(grep -r "ivr_legacy" apps --include="*.py" | wc -l)
echo "Referencias restantes: $LEGACY_COUNT (debe ser 0)"

if [ "$LEGACY_COUNT" -eq 0 ]; then
    echo "✅ Renombre completado exitosamente"
else
    echo "⚠️  Aún hay $LEGACY_COUNT referencias a ivr_legacy"
fi

echo ""
echo "=== SIGUIENTE PASO ==="
echo "Ejecutar tests para validar:"
echo "pytest tests/unit/ivr/ -v"
```

### Ejecución

```bash
# 1. Crear script
mkdir -p /tmp/iact-real/scripts
cat > /tmp/iact-real/scripts/rename_ivr_legacy.sh << 'EOF'
[pegar script de arriba]
EOF

# 2. Dar permisos
chmod +x /tmp/iact-real/scripts/rename_ivr_legacy.sh

# 3. Ejecutar
/tmp/iact-real/scripts/rename_ivr_legacy.sh

# 4. Validar
cd /tmp/iact-real/callcentersite
pytest tests/unit/ivr/ -v --tb=short
```

**Checklist:**
- [ ] Script creado
- [ ] Backup realizado
- [ ] Directorio renombrado
- [ ] Imports actualizados (apps/)
- [ ] Imports actualizados (tests/)
- [ ] INSTALLED_APPS actualizado
- [ ] Database router actualizado
- [ ] 0 referencias a ivr_legacy
- [ ] Tests pasando

---

## TAREA 1.3: Crear Plan de Migrations (2 horas)

### Objetivo
Planificar migrations SeparateDatabaseAndState para mover modelos sin alterar BD.

### Documento de Plan

```bash
cat > /tmp/iact-real/docs/implementation/MIGRATION_PLAN_CORE.md << 'EOF'
---
version: 1.0.0
date: 2026-01-20
type: Migration Plan
---

# MIGRATION PLAN - apps/core/ Refactoring

## Objetivo
Mover modelos concretos de apps/core/ a apps correctas SIN alterar tablas BD.

## Estrategia: SeparateDatabaseAndState

### Concepto
```python
migrations.SeparateDatabaseAndState(
    database_operations=[],  # NADA - no tocar BD
    state_operations=[       # Solo actualizar Django ORM
        migrations.CreateModel(...),
    ],
)
```

## Migrations Requeridas

### 1. apps/pipeline/ - Agregar Center, Service, CallRecord

**Archivo:** `apps/pipeline/migrations/0002_add_core_models.py`

```python
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('pipeline', '0001_initial'),
        ('core', 'XXXX_current_migration'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # NADA - tablas ya existen
            ],
            state_operations=[
                migrations.CreateModel(
                    name='Center',
                    fields=[
                        ('id', models.BigAutoField(primary_key=True)),
                        ('nombre', models.CharField(max_length=200)),
                        ('codigo', models.CharField(max_length=50, unique=True)),
                        ('descripcion', models.TextField(blank=True)),
                        ('direccion', models.TextField(blank=True)),
                        ('activo', models.BooleanField(default=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('is_deleted', models.BooleanField(default=False)),
                        ('deleted_at', models.DateTimeField(null=True, blank=True)),
                    ],
                    options={
                        'db_table': 'core_centers',  # ✅ PRESERVAR
                        'verbose_name': 'Centro',
                        'verbose_name_plural': 'Centros',
                        'ordering': ['nombre'],
                    },
                ),
                migrations.CreateModel(
                    name='Service',
                    fields=[
                        ('id', models.BigAutoField(primary_key=True)),
                        ('numero_800', models.CharField(max_length=20, unique=True)),
                        ('nombre', models.CharField(max_length=200)),
                        ('descripcion', models.TextField(blank=True)),
                        ('center', models.ForeignKey(
                            on_delete=django.db.models.deletion.PROTECT,
                            related_name='services',
                            to='pipeline.center',  # ✅ Nueva ubicación
                        )),
                        ('activo', models.BooleanField(default=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('is_deleted', models.BooleanField(default=False)),
                        ('deleted_at', models.DateTimeField(null=True, blank=True)),
                    ],
                    options={
                        'db_table': 'core_services',  # ✅ PRESERVAR
                        'verbose_name': 'Servicio',
                        'verbose_name_plural': 'Servicios',
                        'ordering': ['nombre'],
                    },
                ),
                migrations.CreateModel(
                    name='CallRecord',
                    fields=[
                        ('id', models.BigAutoField(primary_key=True)),
                        ('fecha', models.DateField()),
                        ('telefono', models.CharField(max_length=20)),
                        ('servicio_800', models.CharField(max_length=20)),
                        ('total_llamadas', models.IntegerField(default=0)),
                        ('llamadas_contestadas', models.IntegerField(default=0)),
                        ('llamadas_abandonadas', models.IntegerField(default=0)),
                        ('duracion_total_segundos', models.IntegerField(default=0)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('is_deleted', models.BooleanField(default=False)),
                        ('deleted_at', models.DateTimeField(null=True, blank=True)),
                    ],
                    options={
                        'db_table': 'core_call_records',  # ✅ PRESERVAR
                        'verbose_name': 'Registro de Llamada',
                        'verbose_name_plural': 'Registros de Llamadas',
                        'unique_together': [['fecha', 'telefono', 'servicio_800']],
                        'ordering': ['-fecha'],
                    },
                ),
            ],
        ),
    ]
```

### 2. apps/access/ - Agregar UserServiceAccess

**Archivo:** `apps/access/migrations/0002_add_user_service_access.py`

```python
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('access', '0001_initial'),
        ('pipeline', '0002_add_core_models'),  # Depende de Service
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='UserServiceAccess',
                    fields=[
                        ('id', models.BigAutoField(primary_key=True)),
                        ('user', models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='service_accesses',
                            to=settings.AUTH_USER_MODEL,
                        )),
                        ('service', models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='user_accesses',
                            to='pipeline.service',  # ✅ Nueva ubicación
                        )),
                        ('granted_at', models.DateTimeField(auto_now_add=True)),
                        ('granted_by', models.ForeignKey(
                            on_delete=django.db.models.deletion.SET_NULL,
                            null=True,
                            related_name='granted_accesses',
                            to=settings.AUTH_USER_MODEL,
                        )),
                        ('reason', models.TextField(blank=True)),
                        ('is_active', models.BooleanField(default=True)),
                        ('revoked_at', models.DateTimeField(null=True, blank=True)),
                        ('revoked_by', models.ForeignKey(
                            on_delete=django.db.models.deletion.SET_NULL,
                            null=True,
                            blank=True,
                            related_name='revoked_accesses',
                            to=settings.AUTH_USER_MODEL,
                        )),
                        ('is_deleted', models.BooleanField(default=False)),
                        ('deleted_at', models.DateTimeField(null=True, blank=True)),
                    ],
                    options={
                        'db_table': 'core_user_service_access',  # ✅ PRESERVAR
                        'verbose_name': 'Acceso Usuario-Servicio',
                        'verbose_name_plural': 'Accesos Usuario-Servicio',
                        'unique_together': [['user', 'service']],
                    },
                ),
            ],
        ),
    ]
```

### 3. apps/core/ - Eliminar Modelos Concretos

**Archivo:** `apps/core/migrations/0003_remove_concrete_models.py`

```python
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_previous_migration'),
        ('pipeline', '0002_add_core_models'),
        ('access', '0002_add_user_service_access'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # NADA - no tocar tablas
            ],
            state_operations=[
                migrations.DeleteModel(name='Center'),
                migrations.DeleteModel(name='Service'),
                migrations.DeleteModel(name='CallRecord'),
                migrations.DeleteModel(name='UserServiceAccess'),
            ],
        ),
    ]
```

## Orden de Ejecución

```bash
# 1. Crear migrations (makemigrations NO las crea, hacerlas manual)
# NOTA: SeparateDatabaseAndState requiere migrations manuales

# 2. Aplicar en orden
python manage.py migrate pipeline 0002_add_core_models
python manage.py migrate access 0002_add_user_service_access
python manage.py migrate core 0003_remove_concrete_models

# 3. Verificar estado
python manage.py showmigrations pipeline
python manage.py showmigrations access
python manage.py showmigrations core

# 4. Verificar BD (NO debe tener cambios)
python manage.py dbshell
\d core_centers    # Debe existir sin cambios
\d core_services   # Debe existir sin cambios
\d core_call_records  # Debe existir sin cambios
\d core_user_service_access  # Debe existir sin cambios
```

## Validación

```bash
# 1. Tests
pytest tests/unit/pipeline/ -v
pytest tests/unit/access/ -v
pytest tests/unit/core/ -v

# 2. Smoke test
python manage.py shell
>>> from apps.pipeline.models import Center, Service, CallRecord
>>> Center.objects.count()  # Debe retornar datos existentes
>>> Service.objects.count()
>>> CallRecord.objects.count()
>>> from apps.access.models import UserServiceAccess
>>> UserServiceAccess.objects.count()

# 3. Verificar imports
python manage.py check
```

## Rollback (si necesario)

```bash
# 1. Rollback migrations
python manage.py migrate core 0002_previous_migration
python manage.py migrate access 0001_initial
python manage.py migrate pipeline 0001_initial

# 2. Restaurar backup código
git checkout apps/core/models.py
git checkout apps/pipeline/models.py
git checkout apps/access/models.py
```

## Checklist Final

- [ ] Migrations creadas manualmente
- [ ] Orden de dependencias correcto
- [ ] db_table preservado en todos
- [ ] ForeignKeys apuntan a nueva ubicación
- [ ] Migrations aplicadas sin errores
- [ ] 0 cambios en base de datos
- [ ] Tests pasando
- [ ] Smoke tests OK
EOF
```

**Checklist:**
- [ ] Plan de migrations creado
- [ ] Migrations SeparateDatabaseAndState diseñadas
- [ ] Orden de ejecución definido
- [ ] Validaciones planificadas

---

## TAREA 1.4: Verificar apps/pipeline/ (1 hora)

### Objetivo
Verificar estructura actual de apps/pipeline/ para planificar integración.

### Comandos

```bash
cd /tmp/iact-real/callcentersite

# 1. Estructura completa
tree apps/pipeline/

# 2. Ver models.py actual
cat apps/pipeline/models.py

# 3. Ver services/ actual
ls -la apps/pipeline/services/

# 4. Verificar si tiene serializers, filters, viewsets
ls -la apps/pipeline/ | grep -E "serializers|filters|viewsets"

# 5. Verificar INSTALLED_APPS
grep "apps.pipeline" config/settings/base.py
```

### Análisis

```bash
# Crear reporte de estructura
cat > /tmp/pipeline_structure.md << 'EOF'
# apps/pipeline/ - Estructura Actual

## Archivos Existentes
[Listar archivos]

## models.py Actual
[Pegar contenido]

## services/ Actual
[Listar services existentes]

## API Components
- serializers.py: [existe/no existe]
- filters.py: [existe/no existe]
- viewsets.py: [existe/no existe]
- permissions.py: [existe/no existe]

## Plan de Integración
1. Agregar modelos en models.py (después de modelos existentes)
2. Crear/ampliar services/
3. Crear/ampliar serializers.py
4. Crear/ampliar filters.py
5. Crear/ampliar viewsets.py
EOF
```

**Checklist:**
- [ ] Estructura pipeline verificada
- [ ] models.py revisado
- [ ] services/ revisados
- [ ] Plan de integración creado

---

## TAREA 1.5: Commit y Backup (30 min)

### Objetivo
Guardar cambios de PARTE 1 antes de continuar.

### Comandos

```bash
cd /tmp/iact-real

# 1. Git status
git status

# 2. Add cambios
git add callcentersite/apps/ivr/
git add callcentersite/apps/
git add callcentersite/config/settings/base.py
git add docs/implementation/
git add scripts/

# 3. Commit
git commit -m "FASE 2 PARTE 1: Renombre ivr_legacy → ivr + preparación

- Renombrado apps/ivr_legacy/ → apps/ivr/
- Actualizados imports en ~20 archivos
- Actualizado INSTALLED_APPS
- Actualizado database router
- Documentado estado actual
- Creado MIGRATION_PLAN_CORE.md
- Script de renombre creado
- Tests pasando

Siguiente: PARTE 2 - Preparar apps/pipeline/"

# 4. Tag
git tag fase-2-parte-1-complete

# 5. Backup
tar -czf /tmp/iact-real-fase2-parte1-backup.tar.gz /tmp/iact-real/
```

**Checklist:**
- [ ] Cambios committed
- [ ] Tag creado
- [ ] Backup realizado

---

## ✅ CHECKLIST PARTE 1 COMPLETA

```yaml
Documentación:
  [ ] Estado actual documentado
  [ ] Imports inventariados
  [ ] FASE_2_ESTADO_ACTUAL.md creado

Renombre IVR:
  [ ] apps/ivr_legacy/ → apps/ivr/
  [ ] Imports actualizados (apps/)
  [ ] Imports actualizados (tests/)
  [ ] INSTALLED_APPS actualizado
  [ ] Database router actualizado
  [ ] 0 referencias a ivr_legacy
  [ ] Tests ivr/ pasando

Plan Migrations:
  [ ] MIGRATION_PLAN_CORE.md creado
  [ ] Migrations SeparateDatabaseAndState diseñadas
  [ ] Orden de ejecución planificado

Verificación apps/pipeline/:
  [ ] Estructura revisada
  [ ] models.py analizado
  [ ] Plan de integración creado

Git:
  [ ] Cambios committed
  [ ] Tag fase-2-parte-1-complete
  [ ] Backup creado

Tiempo Total: 1 día (8 horas)
```

---

## 📋 DELIVERABLES PARTE 1

```yaml
Documentos:
  ✅ /tmp/iact-real/docs/implementation/FASE_2_ESTADO_ACTUAL.md
  ✅ /tmp/iact-real/docs/implementation/MIGRATION_PLAN_CORE.md
  ✅ /tmp/pipeline_structure.md

Scripts:
  ✅ /tmp/iact-real/scripts/rename_ivr_legacy.sh

Código:
  ✅ apps/ivr/ (renombrado)
  ✅ Imports actualizados
  ✅ Tests pasando

Backup:
  ✅ apps/ivr_legacy.backup/
  ✅ /tmp/iact-real-fase2-parte1-backup.tar.gz

Git:
  ✅ Commit "FASE 2 PARTE 1: Renombre ivr_legacy → ivr + preparación"
  ✅ Tag fase-2-parte-1-complete
```

---

## 🎯 SIGUIENTE PASO

**PARTE 2: Preparar apps/pipeline/** (Día 16)
- Ampliar models.py para recibir Center, Service, CallRecord
- Preparar services/
- Preparar serializers.py, filters.py

---

**FIN DE PARTE 1**

**Duración:** 1 día  
**Estado:** Listo para ejecutar  
**Siguiente:** PARTE 2 - Preparar apps/pipeline/
