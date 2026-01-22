# ARQUITECTURA ETL - CAMBIOS v1.0.0 → v2.0.0

**Fecha:** 2026-01-18  
**Tipo:** Actualización arquitectónica  
**Razón:** Alineación con CLEAN_CODE v3.0.1

---

## 🎯 RESUMEN EJECUTIVO

La versión v2.0.0 de la documentación de Arquitectura ETL corrige errores arquitectónicos identificados en v1.0.0 y se alinea con CLEAN_CODE NAMING PRINCIPLES v3.0.1.

**Cambios principales:**
1. ✅ Nomenclatura de modelos: español → inglés
2. ✅ Arquitectura apps/: core/ vs utils/ corregida
3. ✅ Importaciones corregidas
4. ✅ Referencias actualizadas a CLEAN_CODE v3.0.1

**Impacto:** ALTO (requiere refactorización de código)

---

## 📋 TABLA DE CAMBIOS

### 1. NOMENCLATURA DE MODELOS DJANGO

```
┌──────────────────────┬────────────────────────┬──────────────────────┐
│ v1.0.0 (Español)     │ v2.0.0 (Inglés)        │ Tabla MariaDB        │
├──────────────────────┼────────────────────────┼──────────────────────┤
│ HistoricoT1          │ CallRecord             │ tbl_historico_t1_*   │
│ HistoricoT2          │ CallRecord             │ tbl_historico_t2_*   │
│ HistoricoT3          │ CallRecord             │ tbl_historico_t3_*   │
│ ReporteTrimestral    │ QuarterlyReport        │ tbl_reporte_trim...  │
│ Menu2                │ IVRMenu                │ menu2                │
│ LlamadasAbandonadas  │ AbandonedCall          │ tbl_reporte_llam...  │
│ ClientesUnicos       │ UniqueClient           │ tbl_reporte_clie...  │
└──────────────────────┴────────────────────────┴──────────────────────┘

NOTA: Tablas MariaDB NO cambian (son legacy)
```

---

### 2. ARQUITECTURA apps/

#### **apps/core/ (FUNDAMENTAL - NO deprecado)**

```diff
v1.0.0 (INCORRECTO):
- ❌ apps/core/ NO documentado o mencionado como deprecado

v2.0.0 (CORRECTO):
+ ✅ apps/core/ FUNDAMENTAL para modelos abstractos
+ ✅ apps/core/models.py:
+     - TimeStampedModel
+     - SoftDeleteMixin
+     - SoftDeleteManager
+     - SoftDeleteQuerySet
+ ✅ apps/core/mixins.py:
+     - SoftDeleteViewSetMixin
```

#### **apps/utils/ (Solo funciones helper)**

```diff
v1.0.0 (INCORRECTO):
- ❌ apps/utils/models.py con clases (SoftDeleteMixin, TimeStampedModel)

v2.0.0 (CORRECTO):
+ ✅ apps/utils/ SOLO funciones + clases helper
+ ✅ apps/utils/pagination.py (StandardPagination - helper OK)
+ ✅ apps/utils/exceptions.py (funciones + exceptions)
+ ✅ apps/utils/request.py (funciones)
```

---

### 3. IMPORTACIONES CORREGIDAS

#### **Antes (v1.0.0 - INCORRECTO):**
```python
# ❌ Importación incorrecta
from apps.utils.models import SoftDeleteMixin, TimeStampedModel
from apps.ivr.models import HistoricoT1, ReporteTrimestral
```

#### **Después (v2.0.0 - CORRECTO):**
```python
# ✅ Importación correcta
from apps.core.models import SoftDeleteMixin, TimeStampedModel
from apps.ivr.models import CallRecord, QuarterlyReport
```

---

### 4. REFERENCIAS A CLEAN_CODE

```
❌ v1.0.0: CLEAN_CODE_NAMING_PRINCIPLES v2.3.0 (obsoleto)
✅ v2.0.0: CLEAN_CODE_NAMING_PRINCIPLES v3.0.1 (actual)

Secciones actualizadas:
- Sección 7 (Nomenclatura)
- Sección 10 (Referencias)
- Todos los ejemplos de código
```

---

## 🔄 GUÍA DE MIGRACIÓN

### Paso 1: Renombrar Modelos en apps/ivr/models.py

```python
# ANTES (v1.0.0)
class HistoricoT1(models.Model):
    """Histórico Q1."""
    
    class Meta:
        db_table = 'tbl_historico_t1_2025'
        managed = False


# DESPUÉS (v2.0.0)
class CallRecord(models.Model):
    """
    Registro de llamada del IVR.
    
    Mapea a tablas históricas por trimestre:
    - tbl_historico_t1_2025 (Q1)
    - tbl_historico_t2_2025 (Q2)
    - tbl_historico_t3_2025 (Q3)
    """
    
    class Meta:
        db_table = 'tbl_historico_t1_2025'  # Configurar según trimestre
        managed = False
        verbose_name = 'Registro de llamada'
        verbose_name_plural = 'Registros de llamadas'
```

---

### Paso 2: Mover Modelos Abstractos a apps/core/

```bash
# Crear apps/core/ si no existe
mkdir -p apps/core
touch apps/core/__init__.py

# Mover modelos abstractos desde apps/utils/ → apps/core/
# (o crearlos si no existen)

# apps/core/models.py
cat > apps/core/models.py << 'EOF'
from django.db import models

class TimeStampedModel(models.Model):
    """Modelo abstracto con timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class SoftDeleteMixin(models.Model):
    """Modelo abstracto con soft delete."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_deleted'
    )
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None):
        """Marca como eliminado."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()
    
    def restore(self):
        """Restaura registro eliminado."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()
EOF
```

---

### Paso 3: Actualizar Importaciones en Todo el Proyecto

```bash
# Buscar y reemplazar importaciones
grep -r "from apps.utils.models import" apps/

# Reemplazar manualmente o con script:
find apps/ -name "*.py" -exec sed -i \
  's/from apps\.utils\.models import/from apps.core.models import/g' {} \;
```

---

### Paso 4: Actualizar Referencias a Modelos

```bash
# Buscar referencias a modelos antiguos
grep -r "HistoricoT1\|ReporteTrimestral" apps/

# Actualizar a nuevos nombres:
# HistoricoT1 → CallRecord
# ReporteTrimestral → QuarterlyReport
```

---

### Paso 5: Actualizar Services

```python
# ANTES (v1.0.0)
from apps.ivr.models import HistoricoT1, ReporteTrimestral

class ReportService:
    @staticmethod
    def get_trimestral_data(trimestre):
        return HistoricoT1.objects.filter(trimestre=trimestre)


# DESPUÉS (v2.0.0)
from apps.ivr.models import CallRecord, QuarterlyReport

class ReportService:
    @staticmethod
    def get_quarterly_calls(quarter):
        """Obtiene llamadas del trimestre."""
        return CallRecord.objects.filter(quarter=quarter)
```

---

### Paso 6: Ejecutar Tests

```bash
# Verificar que todo funciona
python manage.py test

# Verificar imports
pylint apps/

# Verificar types
mypy apps/
```

---

## 📊 IMPACTO POR COMPONENTE

### **Alto Impacto (Requiere cambios):**

```
✅ apps/ivr/models.py
   - Renombrar todos los modelos

✅ apps/reports/services.py
   - Actualizar importaciones
   - Actualizar referencias a modelos

✅ apps/dashboard/services.py
   - Actualizar importaciones
   - Actualizar referencias a modelos

✅ apps/reports/views.py
   - Actualizar importaciones

✅ apps/dashboard/views.py
   - Actualizar importaciones

✅ apps/pipeline/services.py
   - Actualizar referencias a JobExecutionLog (si aplica)
```

---

### **Medio Impacto (Verificar):**

```
⚠️ apps/reports/serializers.py
   - Verificar nombres de modelos en Meta.model

⚠️ apps/dashboard/serializers.py
   - Verificar nombres de modelos

⚠️ apps/ivr/admin.py
   - Actualizar si usa modelos directamente

⚠️ Tests (apps/*/tests.py)
   - Actualizar fixtures
   - Actualizar nombres de modelos
```

---

### **Bajo Impacto (No requiere cambios):**

```
✅ Base de datos MariaDB
   - Tablas NO cambian (tbl_historico_t1_2025, etc.)

✅ Stored Procedures ETL
   - Scripts SQL NO cambian

✅ Endpoints API
   - URLs NO cambian (/api/v1/reports/*, /api/v1/dashboard/*)

✅ Frontend
   - Requests/Responses NO cambian (misma estructura JSON)
```

---

## ⚠️ PRECAUCIONES

### **1. Backups Requeridos**
```bash
# Backup de código antes de migración
git checkout -b migration-etl-v2.0.0
git commit -am "Pre-migration snapshot"

# Backup de base de datos (si aplica)
python manage.py dumpdata > backup_pre_migration.json
```

---

### **2. Migración Incremental**
```
Orden sugerido:
1. Crear apps/core/ con modelos abstractos
2. Actualizar importaciones en apps/ivr/models.py
3. Renombrar modelos en apps/ivr/models.py
4. Actualizar imports en services
5. Actualizar imports en views
6. Ejecutar tests
7. Actualizar serializers
8. Ejecutar tests completos
```

---

### **3. Compatibilidad con Database**
```python
# NO ES NECESARIO migrar base de datos
# Los modelos Django mapean a las MISMAS tablas

# ANTES:
class HistoricoT1(models.Model):
    class Meta:
        db_table = 'tbl_historico_t1_2025'

# DESPUÉS (mismo db_table):
class CallRecord(models.Model):
    class Meta:
        db_table = 'tbl_historico_t1_2025'

# ✅ No requiere makemigrations/migrate
```

---

## ✅ CHECKLIST DE MIGRACIÓN

```
PRE-MIGRACIÓN:
☐ Backup de código (branch migration-etl-v2.0.0)
☐ Backup de base de datos
☐ Tests pasando antes de cambios
☐ Linters sin errores

MIGRACIÓN:
☐ apps/core/ creado con modelos abstractos
☐ Modelos en apps/ivr/ renombrados
☐ Importaciones actualizadas en services
☐ Importaciones actualizadas en views
☐ Importaciones actualizadas en serializers
☐ Tests actualizados

POST-MIGRACIÓN:
☐ Tests pasan completamente
☐ Linters pasan (flake8, pylint)
☐ Type checker pasa (mypy)
☐ API endpoints funcionan
☐ Dashboard carga correctamente
☐ Reportes se generan correctamente
☐ ETL se ejecuta sin errores

DOCUMENTACIÓN:
☐ README.md actualizado
☐ CHANGELOG.md actualizado
☐ Documentación API actualizada (si aplica)
```

---

## 📚 DOCUMENTOS RELACIONADOS

**Nuevos (v2.0.0):**
- ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0_PARTE_1.md
- ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0_PARTE_2.md
- ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0_PARTE_3.md

**Obsoletos (v1.0.0):**
- ❌ ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_1.md
- ❌ ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_2.md
- ❌ ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_3.md

**Referencias:**
- ✅ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_*.md (5 partes)
- ✅ ANALISIS_CORE_VS_UTILS_ESTADO_REAL_v3.0.0.md
- ✅ GUIA_CORE_VS_UTILS_v2.0.0.md

---

## 🎯 PRÓXIMOS PASOS

1. **Revisar este documento de cambios**
2. **Leer las 3 partes de v2.0.0:**
   - PARTE 1: Fundamentos y Arquitectura de Datos
   - PARTE 2: Arquitectura Django y APIs
   - PARTE 3: Nomenclatura, Constantes y Referencias
3. **Planificar migración del código**
4. **Ejecutar migración incremental**
5. **Validar con tests**

---

**Documento generado:** 2026-01-18  
**Autor:** Equipo IACT  
**Versión:** 1.0.0  
**Estado:** ✅ COMPLETO
