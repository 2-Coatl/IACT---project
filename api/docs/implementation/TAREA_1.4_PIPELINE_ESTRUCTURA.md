---
version: 1.0.0
date: 2026-01-20
type: Análisis apps/pipeline/
tarea: TAREA 1.4 - Verificar apps/pipeline/
---

# TAREA 1.4 - ANÁLISIS apps/pipeline/

**Ejecutado:** 2026-01-20  
**Resultado:** ✅ COMPLETADO

---

## 📊 ESTRUCTURA ACTUAL

### Archivos Existentes

```
apps/pipeline/
├── __init__.py
├── admin.py                # ✅ Existe
├── apps.py                 # ✅ Existe (PipelineConfig)
├── models.py               # ✅ Existe (ETLExecution)
├── scheduler.py            # ✅ Existe (APScheduler)
├── urls.py                 # ✅ Existe
├── views.py                # ✅ Existe
└── migrations/
    └── __init__.py
```

### Modelos Existentes

```python
# apps/pipeline/models.py

class ETLExecution(models.Model):
    """Registro de ejecución ETL"""
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(...)
    records_extracted = models.IntegerField()
    records_loaded = models.IntegerField()
    # ... (79 líneas totales)
```

**Total modelos:** 1 (ETLExecution)

---

## 🎯 ARCHIVOS FALTANTES

Estos archivos **NO existen** en apps/pipeline/:

```yaml
❌ services/                 # Directorio
❌ serializers.py            # Archivo
❌ filters.py                # Archivo
❌ viewsets.py               # Archivo
❌ permissions.py            # Archivo
```

**Acción requerida:** Crear estos archivos en PARTE 2 cuando movamos código desde apps/core/

---

## 📋 PLAN DE INTEGRACIÓN

### Paso 1: Agregar Modelos en models.py

```python
# apps/pipeline/models.py

# Modelo existente
class ETLExecution(models.Model):
    ...

# NUEVOS MODELOS (agregar después de ETLExecution)

class Center(SoftDeleteMixin, models.Model):
    """Centro de atención"""
    nombre = models.CharField(...)
    codigo = models.CharField(...)
    # ... (movido desde apps/core/)
    
    class Meta:
        db_table = 'core_centers'  # ✅ PRESERVAR

class Service(SoftDeleteMixin, models.Model):
    """Servicio 800"""
    numero_800 = models.CharField(...)
    nombre = models.CharField(...)
    center = models.ForeignKey(Center, ...)
    # ... (movido desde apps/core/)
    
    class Meta:
        db_table = 'core_services'  # ✅ PRESERVAR

class CallRecord(SoftDeleteMixin, models.Model):
    """Registro agregado de llamadas (ETL output)"""
    fecha = models.DateField()
    telefono = models.CharField(...)
    servicio_800 = models.CharField(...)
    # ... (movido desde apps/core/)
    
    class Meta:
        db_table = 'core_call_records'  # ✅ PRESERVAR
```

---

### Paso 2: Crear services/

```bash
# Crear directorio
mkdir apps/pipeline/services/

# Crear __init__.py
touch apps/pipeline/services/__init__.py

# Mover services desde core
mv apps/core/services/center_service.py apps/pipeline/services/
mv apps/core/services/service_service.py apps/pipeline/services/
mv apps/core/services/callrecord_service.py apps/pipeline/services/

# Actualizar imports en services
# (esto se hace en PARTE 4)
```

---

### Paso 3: Crear/Ampliar serializers.py

```bash
# Opción A: Mover contenido
cat apps/core/serializers.py >> apps/pipeline/serializers.py

# Opción B: Filtrar solo Center, Service, CallRecord
# (manual - PARTE 5)
```

---

### Paso 4: Crear/Ampliar filters.py

```bash
# Similar a serializers
```

---

### Paso 5: Crear/Ampliar viewsets.py

```bash
# Similar a serializers
```

---

## ✅ COMPATIBILIDAD

```yaml
INSTALLED_APPS:
  ✅ 'apps.pipeline' ya está registrado

Migrations:
  ✅ apps/pipeline/migrations/ existe
  ✅ Listo para recibir nueva migration

DB Tables:
  ✅ core_centers existe
  ✅ core_services existe
  ✅ core_call_records existe
  ✅ NO conflictos con pipeline

Imports:
  ✅ ETLExecution no usa Center/Service/CallRecord
  ✅ NO circular dependencies
```

---

## 📊 COMPARACIÓN apps/core/ vs apps/pipeline/

```yaml
apps/core/ TIENE (a mover):
  ✅ models.py (Center, Service, CallRecord)
  ✅ services/ (3 archivos)
  ✅ serializers.py (20 serializers)
  ✅ filters.py (4 filters)
  ✅ permissions.py (6 custom)
  ✅ viewsets.py (4 viewsets)

apps/pipeline/ TIENE (actual):
  ✅ models.py (ETLExecution)
  ✅ scheduler.py (APScheduler)
  ✅ admin.py, urls.py, views.py
  ❌ NO services/
  ❌ NO serializers.py
  ❌ NO filters.py
  ❌ NO viewsets.py
  ❌ NO permissions.py

apps/pipeline/ TENDRÁ (después):
  ✅ models.py (ETLExecution + Center + Service + CallRecord)
  ✅ services/ (etl_service + center_service + service_service + callrecord_service)
  ✅ serializers.py (todos)
  ✅ filters.py (todos)
  ✅ viewsets.py (todos)
  ✅ permissions.py (custom)
  ✅ scheduler.py (sin cambios)
  ✅ admin.py (ampliar con Center/Service/CallRecord)
```

---

## ⏱️ ESTIMACIÓN SIGUIENTE PASO

```yaml
PARTE 2 - Ampliar apps/pipeline/:
  - Agregar modelos en models.py: 1 hora
  - Crear services/: 30 min
  - Crear serializers.py: 30 min
  - Crear filters.py: 20 min
  - Crear viewsets.py: 30 min
  - Actualizar admin.py: 20 min
  
  Total: ~3.5 horas
```

---

✅ **TAREA 1.4 COMPLETADA**

**Tiempo:** 20 minutos  
**apps/pipeline/ analizado ✅**  
**Plan de integración creado ✅**  
**Próximo:** TAREA 1.5 - Commit y Backup
