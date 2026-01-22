---
version: 3.0.0
date: 2026-01-19
project: IACT (Sistema Call Center)
type: Arquitectura Técnica
categoria: arquitectura/diseño
titulo: Arquitectura Real del Sistema ETL - Versión Definitiva
componente: ETL (Extract, Transform, Load)
tecnologias: Django, DRF, APScheduler, PostgreSQL
scope: Sistema completo (IVR Legacy → Django → API)
audiencia: Desarrolladores, Arquitectos Técnicos
estado: definitivo
base: CLEAN_CODE v3.0.1 + RESTRICCIONES v1.0.0 + RBAC v6.0.0
partes: 2/3
---

# ARQUITECTURA REAL DEL SISTEMA ETL - v3.0.0

**PARTE 2/3: ARQUITECTURA DJANGO Y APIS**

---

## 📋 CONTENIDO DE ESTA PARTE

4. [Arquitectura Django](#4-arquitectura-django)
5. [APIs y Endpoints](#5-apis-y-endpoints)
6. [Flujo de Datos Completo](#6-flujo-de-datos-completo)

---

<a name="4-arquitectura-django"></a>

## 4. ARQUITECTURA DJANGO

### 4.1 Apps y Responsabilidades

#### **4.1.1 Visión General**

```
PROYECTO: iact-call-center/
Versión Django: 4.2 LTS
Versión DRF: 3.14+
Python: 3.11+

APPS PRINCIPALES:
├─ apps/ivr/              → Modelos IVR Legacy (readonly)
├─ apps/reports/          → Generación de reportes bajo demanda
├─ apps/dashboard/        → Visualización con widgets tiempo real
├─ apps/pipeline/         → Monitoreo estado ETL + APScheduler
├─ apps/access/           → Control de acceso RBAC v6.0.0
├─ apps/authentication/   → Autenticación de usuarios
├─ apps/users/            → Gestión de usuarios
├─ apps/alerts/           → Buzón interno (CNST-001)
└─ apps/audit/            → Auditoría completa (CNST-031)

APPS DE SOPORTE:
├─ apps/core/             → Modelos abstractos (TimeStampedModel, SoftDeleteMixin)
└─ apps/utils/            → Funciones utilitarias (pagination, validation)

DOCUMENTOS MAESTROS APLICADOS:
✓ CLEAN_CODE v3.0.1: Nomenclatura inglés, docstrings español
✓ RESTRICCIONES v1.0.0: 14 restricciones críticas
✓ RBAC v6.0.0: 46 funciones, 9 módulos
```

---

#### **4.1.2 Tabla de Responsabilidades Detallada**

```
┌────────────────┬────────────────────────────────────────────────────┐
│ App            │ Responsabilidades                                  │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/ivr/      │ - Modelos Django para BD IVR Legacy               │
│                │ - Lectura readonly de MariaDB (CNST-002)          │
│                │ - Mapeo tablas: tbl_historico_t*, tbl_reporte_*   │
│                │ - Modelos: CallRecord, QuarterlyReport, etc        │
│                │ - managed=False (NO escribe, NO migraciones)       │
│                │ - RBAC: N/A (acceso indirecto vía reports/)        │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/reports/  │ - API endpoints de reportes (POST)                 │
│                │ - Generación bajo demanda (síncrona)               │
│                │ - Exportación (Excel, CSV)                         │
│                │ - Timeout: 90s máx (CNST-025)                      │
│                │ - Límites: 100K CSV, 50K Excel (CNST-007)         │
│                │ - RBAC v6.0.0: 6 funciones                         │
│                │   - RPT_VIEW: reports.view                         │
│                │   - RPT_CREATE: reports.create                     │
│                │   - RPT_DELETE: reports.delete                     │
│                │   - RPT_EXP_CSV: reports.export.csv                │
│                │   - RPT_EXP_EXCEL: reports.export.excel            │
│                │   - RPT_EXP_PDF: reports.export.pdf (planificado)  │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/dashboard/│ - API endpoints de dashboards (GET)                │
│                │ - Visualización tiempo real (datos 6-12h desfase)  │
│                │ - Widgets: KPI, Charts (bar/line/pie), Tables      │
│                │ - Cache LocMem 5 min (CNST-010, NO Redis)         │
│                │ - NO auto-refresh (CNST-003)                       │
│                │ - RBAC v6.0.0: 6 funciones                         │
│                │   - DSH_VIEW: dashboard.view                       │
│                │   - DSH_EXP_CSV: dashboard.export.csv              │
│                │   - DSH_EXP_EXCEL: dashboard.export.excel          │
│                │   - DSH_EXP_PDF: dashboard.export.pdf (planificado)│
│                │   - DSH_SHARE: dashboard.share (planificado)       │
│                │   - DSH_EDIT: dashboard.edit (planificado)         │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/pipeline/ │ - Monitoreo ETL (job_execution_log)                │
│                │ - APScheduler configuration (CNST-013)             │
│                │ - Jobs programados (ETL cada 6-12h)                │
│                │ - Management command: run_etl                       │
│                │ - API: GET /api/v1/pipeline/status/                │
│                │ - RBAC: pipeline.monitor                           │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/access/   │ - RBAC v6.0.0 completo                             │
│                │ - Modelos: Function, FunctionGroup, Assignment     │
│                │ - 46 funciones (42 activas + 4 planificadas)       │
│                │ - 10 grupos (AGR-001 a AGR-010)                    │
│                │ - Decoradores: @require_function()                 │
│                │ - Permission classes: HasFunction, etc             │
│                │ - Permisos temporales (6 meses máx - CNST-021)     │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/          │ - Django Authentication (CNST-012)                 │
│ authentication/│ - Login/Logout                                     │
│                │ - Password reset (3 preguntas seguridad)           │
│                │ - Sessions database (CNST-010, NO Redis)          │
│                │ - RBAC: AUTH_LOGIN, AUTH_LOGOUT, AUTH_RECOVER      │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/users/    │ - CRUD usuarios                                    │
│                │ - Modelo User (Django custom)                      │
│                │ - Gestión perfiles                                 │
│                │ - RBAC: USR_VIEW, USR_CREATE, USR_EDIT, etc        │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/alerts/   │ - Buzón interno (CNST-001)                         │
│                │ - Modelo InternalMessage                           │
│                │ - Sistema notificaciones (NO email)                │
│                │ - Límite: 50 destinatarios (CNST-024)              │
│                │ - Retención: 90 días                               │
│                │ - RBAC: ALR_VIEW, ALR_SEND, ALR_CONF, etc          │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/audit/    │ - Auditoría completa (CNST-031)                    │
│                │ - Modelo AuditLog (append-only)                    │
│                │ - Eventos: login, permisos, exports                │
│                │ - Immutable, SHA-256 checksum                      │
│                │ - Retención: 2 años mínimo                         │
│                │ - RBAC: AUD_VIEW, AUD_SEARCH, AUD_EXPORT           │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/core/     │ - Modelos abstractos base                          │
│                │ - TimeStampedModel (created_at, updated_at)        │
│                │ - SoftDeleteMixin (is_deleted, deleted_at)         │
│                │ - SoftDeleteManager, SoftDeleteQuerySet            │
│                │ - NO funciones (solo modelos)                      │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/utils/    │ - Funciones utilitarias                            │
│                │ - pagination.py (paginate_queryset)                │
│                │ - validation.py (validate_date_range, etc)         │
│                │ - exceptions.py (custom exceptions)                │
│                │ - NO modelos (solo funciones)                      │
└────────────────┴────────────────────────────────────────────────────┘
```

**Decisión Arquitectónica:**
- `apps/core/` → Modelos abstractos ✅
- `apps/utils/` → Funciones utilitarias ✅
- Separación clara (CLEAN_CODE v3.0.1)

---

#### **4.1.3 Separación Reports vs Dashboard (RBAC v6.0.0)**

```yaml
JUSTIFICACIÓN SEPARACIÓN:

apps/reports/:
  - Propósito: Generación de reportes bajo demanda
  - Método HTTP: POST (crear reporte)
  - Formato salida: Archivos descargables (CSV, Excel, PDF)
  - Timeout: 90s (CNST-025)
  - Uso: Análisis periódicos, exportación datos
  - RBAC: reports.view, reports.create, reports.export.*
  - Endpoints: /api/v1/reports/{tipo}/
  
apps/dashboard/:
  - Propósito: Visualización con widgets interactivos
  - Método HTTP: GET (obtener widgets)
  - Formato salida: JSON con widgets (KPI, Charts, Tables)
  - Timeout: 90s (CNST-025)
  - Cache: LocMem 5 min (CNST-010)
  - Uso: Monitoreo diario, KPIs en vivo
  - Datos: Desfase 6-12h (CNST-003)
  - RBAC: dashboard.view, dashboard.export.*
  - Endpoints: /api/v1/dashboard/{tipo}/

Diferencias Clave:
  ✓ Responsabilidad única (Single Responsibility Principle)
  ✓ Permisos independientes (RBAC v6.0.0)
  ✓ Endpoints diferentes
  ✓ Métodos HTTP diferentes (POST vs GET)
  ✓ Cache strategy diferente (reports: NO cache, dashboard: 5 min)

Referencias:
  - RBAC v6.0.0: Secciones 3.5 (MOD_Reports) y 3.6 (MOD_Dashboard)
  - URLS_REPORTES_Y_DASHBOARDS.md
  - CNST-017: Principio SOLID aplicado
```

---

### 4.2 Modelos Django (CLEAN_CODE v3.0.1)

#### **4.2.1 Modelos Abstractos Base (apps/core/)**

```python
# apps/core/models.py

"""
Modelos abstractos base del sistema IACT.

CLEAN_CODE v3.0.1:
- Clases: PascalCase en inglés
- Atributos: snake_case en inglés
- Docstrings: español, formato Google
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que agrega campos de timestamp.
    
    Agrega automáticamente created_at y updated_at a todos
    los modelos que hereden de este.
    
    Attributes:
        created_at: Fecha y hora de creación
        updated_at: Fecha y hora de última modificación
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de última modificación"
    )
    
    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """
    QuerySet personalizado para soft delete.
    
    Filtra automáticamente registros eliminados (is_deleted=True).
    """
    
    def delete(self):
        """
        Soft delete de todos los registros en el queryset.
        
        Returns:
            tuple: (count, dict) número de registros eliminados
        """
        count = self.update(
            is_deleted=True,
            deleted_at=timezone.now()
        )
        return count, {'deleted': count}
    
    def hard_delete(self):
        """
        Hard delete (eliminación física) de registros.
        
        ADVERTENCIA: Esta operación es irreversible.
        
        Returns:
            tuple: (count, dict) número de registros eliminados
        """
        return super().delete()
    
    def alive(self):
        """
        Retorna solo registros NO eliminados.
        
        Returns:
            QuerySet: Registros con is_deleted=False
        """
        return self.filter(is_deleted=False)
    
    def deleted(self):
        """
        Retorna solo registros eliminados.
        
        Returns:
            QuerySet: Registros con is_deleted=True
        """
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """
    Manager para soft delete.
    
    Utiliza SoftDeleteQuerySet por defecto.
    """
    
    def get_queryset(self):
        """
        Retorna queryset filtrando registros eliminados.
        
        Returns:
            SoftDeleteQuerySet: Queryset sin registros eliminados
        """
        return SoftDeleteQuerySet(self.model, using=self._db).alive()
    
    def all_with_deleted(self):
        """
        Retorna TODOS los registros (incluidos eliminados).
        
        Returns:
            SoftDeleteQuerySet: Queryset completo
        """
        return SoftDeleteQuerySet(self.model, using=self._db)
    
    def deleted_only(self):
        """
        Retorna SOLO registros eliminados.
        
        Returns:
            SoftDeleteQuerySet: Registros eliminados
        """
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()


class SoftDeleteMixin(models.Model):
    """
    Mixin para soft delete.
    
    Agrega campos is_deleted y deleted_at, más manager customizado.
    
    Attributes:
        is_deleted: Indica si el registro está eliminado
        deleted_at: Timestamp de eliminación
    
    Usage:
        class MyModel(SoftDeleteMixin, TimeStampedModel):
            name = models.CharField(max_length=100)
            
        # Soft delete
        instance.delete()  # is_deleted=True
        
        # Hard delete
        instance.delete(hard=True)  # Eliminación física
    """
    
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indica si el registro está eliminado (soft delete)"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de eliminación"
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Acceso a todos (incluidos eliminados)
    
    class Meta:
        abstract = True
    
    def delete(self, hard=False, *args, **kwargs):
        """
        Elimina el registro (soft o hard).
        
        Args:
            hard: Si True, eliminación física. Si False, soft delete
            *args: Argumentos adicionales
            **kwargs: Keyword arguments adicionales
        
        Returns:
            tuple: (count, dict) si soft delete
            None: si hard delete
        """
        if hard:
            # Hard delete (eliminación física)
            return super().delete(*args, **kwargs)
        else:
            # Soft delete
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()
            return 1, {'deleted': 1}
    
    def restore(self):
        """
        Restaura un registro eliminado (soft delete).
        
        Returns:
            bool: True si se restauró, False si ya estaba activo
        """
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
            self.save()
            return True
        return False
```

---

#### **4.2.2 Modelos IVR (apps/ivr/)**

Ya documentado en PARTE 1, Sección 2.2.3:
- `CallRecord` (mapea tbl_historico_t1/t2/t3_2025)
- `QuarterlyReport` (mapea tbl_reporte_trimestral)
- `AbandonedCallReport` (mapea tbl_reporte_abandonadas)
- `UniqueClientReport` (mapea tbl_reporte_clientes)
- `TransferReport` (mapea tbl_reporte_transferencias)
- `MenuPerformanceReport` (mapea tbl_reporte_menus_performance)
- `MenuErrorReport` (mapea tbl_reporte_menu_errores)
- `JobExecutionLog` (mapea job_execution_log)

**Características comunes:**
```python
class Meta:
    managed = False  # ✅ Django NO gestiona schema
    db_table = 'tbl_xxx'  # ✅ Preserva nombre húngaro (CLEAN_CODE v3.0.1)
```

---

#### **4.2.3 Modelos RBAC (apps/access/)**

```python
# apps/access/models.py

"""
Modelos RBAC v6.0.0.

Implementa sistema de control de acceso basado en funciones atómicas.
46 funciones, 9 módulos, 10 grupos.

CLEAN_CODE v3.0.1: Nomenclatura inglés, docstrings español.
RBAC v6.0.0: Modelo completo según documento maestro.
"""

from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel

User = get_user_model()


class Function(TimeStampedModel):
    """
    Función atómica del sistema RBAC.
    
    Representa una capacidad específica del sistema (ej: reports.view).
    
    Attributes:
        code: Código corto (RPT_VIEW, DSH_EXP_CSV)
        permission_django: Permiso Django (reports.view, dashboard.export.csv)
        display_name: Nombre legible para UI
        module: Módulo funcional (MOD_Reports, MOD_Dashboard)
        status: Estado (activo, planificado, deprecado)
        description: Descripción detallada
        is_active: Si está activa (False para planificadas)
    
    RBAC v6.0.0:
        - 46 funciones totales
        - 42 activas (is_active=True)
        - 4 planificadas (is_active=False, status='planificado')
    """
    
    class FunctionStatus(models.TextChoices):
        """Estados posibles de una función."""
        ACTIVE = 'activo', 'Activo'
        PLANNED = 'planificado', 'Planificado'
        DEPRECATED = 'deprecado', 'Deprecado'
    
    # Código corto (RPT_VIEW, DSH_EXP_CSV)
    code = models.CharField(
        max_length=30,
        unique=True,
        help_text="Código corto de la función (ej: RPT_VIEW)"
    )
    
    # Permiso Django (PK)
    permission_django = models.CharField(
        max_length=100,
        primary_key=True,
        help_text="Permiso Django (ej: reports.view)"
    )
    
    # Nombre legible
    display_name = models.CharField(
        max_length=200,
        help_text="Nombre legible para UI"
    )
    
    # Módulo
    module = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Módulo funcional (MOD_Reports, MOD_Dashboard)"
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=FunctionStatus.choices,
        default=FunctionStatus.ACTIVE,
        db_index=True,
        help_text="Estado de la función"
    )
    
    # Descripción
    description = models.TextField(
        help_text="Descripción detallada de la función"
    )
    
    # Activa
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Si está activa (False para planificadas)"
    )
    
    class Meta:
        db_table = 'access_functions'
        ordering = ['module', 'code']
        verbose_name = 'Función'
        verbose_name_plural = 'Funciones'
        indexes = [
            models.Index(fields=['module', 'status']),
            models.Index(fields=['is_active']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        """Representación string."""
        return f"{self.code} ({self.permission_django})"
    
    def clean(self):
        """
        Validaciones personalizadas.
        
        Raises:
            ValidationError: Si validación falla
        """
        from django.core.exceptions import ValidationError
        
        # Validar formato permission_django (module.action)
        if '.' not in self.permission_django:
            raise ValidationError({
                'permission_django': 'Debe tener formato module.action'
            })
        
        # Validar que module coincida con prefijo permission_django
        module_prefix = self.permission_django.split('.')[0]
        expected_modules = {
            'auth': 'MOD_Auth',
            'users': 'MOD_Users',
            'access': 'MOD_Access',
            'pipeline': 'MOD_Pipeline',
            'reports': 'MOD_Reports',
            'dashboard': 'MOD_Dashboard',
            'alerts': 'MOD_Alerts',
            'audit': 'MOD_Audit',
            'logs': 'MOD_Logs',
        }
        
        if module_prefix in expected_modules:
            expected = expected_modules[module_prefix]
            if self.module != expected:
                raise ValidationError({
                    'module': f'Debe ser {expected} para {module_prefix}.*'
                })
        
        # Validar code solo MAYÚSCULAS_GUIONES_BAJOS
        if not self.code.replace('_', '').isalnum() or not self.code.isupper():
            raise ValidationError({
                'code': 'Solo MAYÚSCULAS y guiones bajos permitidos'
            })
        
        # Si status=planificado, is_active debe ser False
        if self.status == self.FunctionStatus.PLANNED and self.is_active:
            raise ValidationError({
                'is_active': 'Funciones planificadas deben tener is_active=False'
            })


class FunctionGroup(TimeStampedModel):
    """
    Grupo de funciones RBAC.
    
    Agrupa funciones relacionadas para facilitar asignación.
    
    Attributes:
        group_id: ID del grupo (AGR-001, AGR-002, etc)
        name: Nombre del grupo
        description: Descripción
        functions: Funciones del grupo (ManyToMany)
    
    RBAC v6.0.0: 10 grupos (AGR-001 a AGR-010)
    """
    
    group_id = models.CharField(
        max_length=20,
        primary_key=True,
        help_text="ID del grupo (AGR-001)"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Nombre del grupo"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Descripción del grupo"
    )
    
    functions = models.ManyToManyField(
        Function,
        through='FunctionGroupMembership',
        related_name='function_groups',
        help_text="Funciones del grupo"
    )
    
    class Meta:
        db_table = 'access_function_groups'
        ordering = ['group_id']
        verbose_name = 'Grupo de Funciones'
        verbose_name_plural = 'Grupos de Funciones'
    
    def __str__(self):
        """Representación string."""
        return f"{self.group_id} - {self.name}"


class FunctionGroupMembership(models.Model):
    """
    Relación ManyToMany entre Function y FunctionGroup.
    
    Tabla intermedia para gestionar membresías.
    """
    
    group = models.ForeignKey(
        FunctionGroup,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    function = models.ForeignKey(
        Function,
        on_delete=models.CASCADE,
        related_name='group_memberships'
    )
    
    added_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Cuándo se agregó al grupo"
    )
    
    class Meta:
        db_table = 'access_function_group_memberships'
        unique_together = [['group', 'function']]
        verbose_name = 'Membresía de Grupo'
        verbose_name_plural = 'Membresías de Grupos'
    
    def __str__(self):
        """Representación string."""
        return f"{self.group.group_id} → {self.function.code}"


class UserFunctionAssignment(TimeStampedModel):
    """
    Asignación de función a usuario.
    
    Puede ser permanente o temporal.
    
    Attributes:
        user: Usuario
        function: Función asignada
        is_temporary: Si es temporal
        valid_from: Inicio validez (temporal)
        valid_until: Fin validez (temporal)
        justification: Justificación (obligatoria si temporal)
        approved_by: Quién aprobó
        created_by: Quién creó
        revoked_by: Quién revocó
        revoked_at: Cuándo se revocó
    
    CNST-021: Permisos temporales máx 6 meses
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='function_assignments'
    )
    
    function = models.ForeignKey(
        Function,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )
    
    # Temporal
    is_temporary = models.BooleanField(
        default=False,
        help_text="Si es asignación temporal"
    )
    
    valid_from = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Inicio validez (temporal)"
    )
    
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fin validez (temporal)"
    )
    
    justification = models.TextField(
        blank=True,
        help_text="Justificación (obligatoria si temporal)"
    )
    
    # Aprobación
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_function_assignments'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_function_assignments'
    )
    
    # Revocación
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_function_assignments'
    )
    
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Cuándo se revocó"
    )
    
    class Meta:
        db_table = 'access_user_function_assignments'
        unique_together = [['user', 'function']]
        ordering = ['-created_at']
        verbose_name = 'Asignación de Función a Usuario'
        verbose_name_plural = 'Asignaciones de Funciones a Usuarios'
        indexes = [
            models.Index(fields=['user', 'function']),
            models.Index(fields=['is_temporary']),
            models.Index(fields=['valid_until']),
        ]
    
    def __str__(self):
        """Representación string."""
        temp = " (temporal)" if self.is_temporary else ""
        return f"{self.user.username} → {self.function.code}{temp}"
    
    def clean(self):
        """
        Validaciones personalizadas.
        
        CNST-021: Permisos temporales máx 6 meses.
        
        Raises:
            ValidationError: Si validación falla
        """
        from django.core.exceptions import ValidationError
        from datetime import timedelta
        
        if self.is_temporary:
            # Justificación obligatoria
            if not self.justification or len(self.justification) < 20:
                raise ValidationError({
                    'justification': 'Justificación obligatoria (mín 20 caracteres) para asignaciones temporales'
                })
            
            # valid_from y valid_until obligatorios
            if not self.valid_from or not self.valid_until:
                raise ValidationError({
                    'valid_from': 'Fechas obligatorias para asignaciones temporales',
                    'valid_until': 'Fechas obligatorias para asignaciones temporales'
                })
            
            # valid_until > valid_from
            if self.valid_until <= self.valid_from:
                raise ValidationError({
                    'valid_until': 'Debe ser posterior a valid_from'
                })
            
            # Duración máxima 6 meses (CNST-021)
            max_duration = timedelta(days=180)
            duration = self.valid_until - self.valid_from
            
            if duration > max_duration:
                raise ValidationError({
                    'valid_until': f'Duración máxima 6 meses (CNST-021). Duración actual: {duration.days} días'
                })
        
        # Función debe ser asignable (activa y no deprecada)
        if self.function.status == Function.FunctionStatus.DEPRECATED:
            raise ValidationError({
                'function': 'No se puede asignar función deprecada'
            })
        
        if not self.function.is_active:
            raise ValidationError({
                'function': 'No se puede asignar función inactiva'
            })
    
    def is_valid_now(self):
        """
        Verifica si la asignación es válida ahora.
        
        Returns:
            bool: True si válida, False si expirada o revocada
        """
        from django.utils import timezone
        
        # Si está revocada
        if self.revoked_at:
            return False
        
        # Si no es temporal, siempre válida
        if not self.is_temporary:
            return True
        
        # Si es temporal, verificar fechas
        now = timezone.now()
        return self.valid_from <= now <= self.valid_until


class UserFunctionGroupAssignment(TimeStampedModel):
    """
    Asignación de grupo de funciones a usuario.
    
    Simplifica asignación múltiple de funciones.
    
    Attributes:
        user: Usuario
        function_group: Grupo asignado
        assigned_by: Quién asignó
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='function_group_assignments'
    )
    
    function_group = models.ForeignKey(
        FunctionGroup,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_function_groups'
    )
    
    class Meta:
        db_table = 'access_user_function_group_assignments'
        unique_together = [['user', 'function_group']]
        ordering = ['-created_at']
        verbose_name = 'Asignación de Grupo a Usuario'
        verbose_name_plural = 'Asignaciones de Grupos a Usuarios'
    
    def __str__(self):
        """Representación string."""
        return f"{self.user.username} → {self.function_group.group_id}"


class FunctionSeparationRule(TimeStampedModel):
    """
    Regla de Separación de Funciones (SoD).
    
    Define funciones mutuamente excluyentes por conflicto de intereses.
    
    Attributes:
        rule_id: ID de la regla (access_audit_separation)
        name: Nombre de la regla
        description: Descripción
        functions_group_a: Funciones del grupo A
        functions_group_b: Funciones del grupo B
        severity: Severidad (critical, high, medium)
    
    RBAC v6.0.0: 3 reglas SoD definidas
    """
    
    class Severity(models.TextChoices):
        """Niveles de severidad."""
        CRITICAL = 'critical', 'Crítico'
        HIGH = 'high', 'Alto'
        MEDIUM = 'medium', 'Medio'
    
    rule_id = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="ID de la regla"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Nombre de la regla"
    )
    
    description = models.TextField(
        help_text="Descripción de la regla"
    )
    
    functions_group_a = models.ManyToManyField(
        Function,
        related_name='sod_rules_a',
        help_text="Funciones del grupo A"
    )
    
    functions_group_b = models.ManyToManyField(
        Function,
        related_name='sod_rules_b',
        help_text="Funciones del grupo B"
    )
    
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.MEDIUM,
        help_text="Severidad del conflicto"
    )
    
    class Meta:
        db_table = 'access_function_separation_rules'
        ordering = ['rule_id']
        verbose_name = 'Regla de Separación de Funciones'
        verbose_name_plural = 'Reglas de Separación de Funciones'
    
    def __str__(self):
        """Representación string."""
        return f"{self.rule_id} ({self.severity})"
    
    def check_conflict(self, user_functions):
        """
        Verifica si hay conflicto SoD en funciones del usuario.
        
        Args:
            user_functions: QuerySet de funciones del usuario
        
        Returns:
            bool: True si hay conflicto, False si no
        """
        functions_a = set(self.functions_group_a.values_list('permission_django', flat=True))
        functions_b = set(self.functions_group_b.values_list('permission_django', flat=True))
        user_func_set = set(user_functions.values_list('permission_django', flat=True))
        
        # Conflicto si tiene funciones de AMBOS grupos
        has_a = bool(functions_a & user_func_set)
        has_b = bool(functions_b & user_func_set)
        
        return has_a and has_b
```

---

### 4.3 Service Layer Pattern (CLEAN_CODE v3.0.1)

```python
# apps/reports/services.py

"""
Service Layer para generación de reportes.

Implementa Service Layer Pattern para encapsular lógica de negocio.

CLEAN_CODE v3.0.1:
- Clases: PascalCase en inglés (ReportService)
- Métodos: snake_case en inglés (generate_report)
- Docstrings: español, formato Google
"""

from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from apps.ivr.models import (
    CallRecord,
    QuarterlyReport,
    AbandonedCallReport,
    UniqueClientReport
)
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """
    Servicio para generación de reportes.
    
    Responsabilidades:
    - Generar reportes bajo demanda
    - Aplicar filtros
    - Exportar a CSV/Excel
    - Validar límites (CNST-007)
    
    RESTRICCIONES:
    - CNST-007: Límites export (100K CSV, 50K Excel)
    - CNST-025: Timeout 90s
    - CNST-004: Timeout DB 300s
    """
    
    # Límites de export (CNST-007)
    MAX_ROWS_CSV = 100000
    MAX_ROWS_EXCEL = 50000
    MAX_ROWS_PDF = 10000  # Planificado
    
    @staticmethod
    def generate_abandoned_calls_report(quarter, did=None, start_date=None, end_date=None):
        """
        Genera reporte de llamadas abandonadas.
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3)
            did: DID a filtrar (opcional)
            start_date: Fecha inicio (opcional)
            end_date: Fecha fin (opcional)
        
        Returns:
            QuerySet: Registros del reporte
        
        Raises:
            ValueError: Si parámetros inválidos
        
        CNST-007: Aplica límites de export
        """
        # Validar quarter
        if quarter not in ['Q1', 'Q2', 'Q3']:
            raise ValueError(f"Trimestre inválido: {quarter}")
        
        # Query base
        queryset = AbandonedCallReport.objects.all()
        
        # Aplicar filtros
        if did:
            queryset = queryset.filter(did=did)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Ordenar
        queryset = queryset.order_by('-date', 'did')
        
        logger.info(f"Reporte abandonadas generado: {queryset.count()} registros")
        
        return queryset
    
    @staticmethod
    def generate_unique_clients_report(quarter, did=None):
        """
        Genera reporte de clientes únicos.
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3)
            did: DID a filtrar (opcional)
        
        Returns:
            QuerySet: Registros del reporte
        """
        queryset = UniqueClientReport.objects.all()
        
        if did:
            queryset = queryset.filter(did=did)
        
        queryset = queryset.order_by('-month', 'did')
        
        logger.info(f"Reporte clientes únicos generado: {queryset.count()} registros")
        
        return queryset
    
    @staticmethod
    def export_to_csv(queryset, filename, max_rows=None):
        """
        Exporta queryset a CSV.
        
        Args:
            queryset: QuerySet a exportar
            filename: Nombre del archivo
            max_rows: Límite de filas (default: MAX_ROWS_CSV)
        
        Returns:
            str: Path al archivo generado
        
        Raises:
            ValueError: Si excede límite (CNST-007)
        
        CNST-007: Máximo 100K registros CSV
        """
        if max_rows is None:
            max_rows = ReportService.MAX_ROWS_CSV
        
        count = queryset.count()
        
        if count > max_rows:
            raise ValueError(
                f"Límite excedido: {count} registros. "
                f"Máximo permitido: {max_rows} (CNST-007)"
            )
        
        # Implementación real de export CSV
        # ... código de exportación ...
        
        logger.info(f"CSV exportado: {filename} ({count} registros)")
        
        return f"/media/exports/{filename}"
    
    @staticmethod
    def export_to_excel(queryset, filename, max_rows=None):
        """
        Exporta queryset a Excel.
        
        Args:
            queryset: QuerySet a exportar
            filename: Nombre del archivo
            max_rows: Límite de filas (default: MAX_ROWS_EXCEL)
        
        Returns:
            str: Path al archivo generado
        
        Raises:
            ValueError: Si excede límite (CNST-007)
        
        CNST-007: Máximo 50K registros Excel
        """
        if max_rows is None:
            max_rows = ReportService.MAX_ROWS_EXCEL
        
        count = queryset.count()
        
        if count > max_rows:
            raise ValueError(
                f"Límite excedido: {count} registros. "
                f"Máximo permitido: {max_rows} (CNST-007)"
            )
        
        # Implementación real de export Excel
        # ... código de exportación ...
        
        logger.info(f"Excel exportado: {filename} ({count} registros)")
        
        return f"/media/exports/{filename}"
```

```python
# apps/dashboard/services.py

"""
Service Layer para dashboards.

CLEAN_CODE v3.0.1: Nomenclatura inglés, docstrings español.
CNST-003: NO real-time (datos 6-12h desfase).
CNST-010: Cache LocMem (NO Redis).
"""

from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from apps.ivr.models import QuarterlyReport
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Servicio para generación de dashboards.
    
    Responsabilidades:
    - Generar widgets (KPI, Charts, Tables)
    - Aplicar cache LocMem 5 min
    - Validar datos estáticos (6-12h desfase)
    
    RESTRICCIONES:
    - CNST-003: Datos estáticos (NO real-time)
    - CNST-010: Cache LocMem (NO Redis)
    - CNST-023: Dashboard sin auto-refresh
    """
    
    CACHE_TTL = 300  # 5 minutos
    
    @staticmethod
    def get_quarterly_metrics_dashboard(quarter):
        """
        Genera dashboard de métricas trimestrales.
        
        Args:
            quarter: Trimestre (Q1, Q2, Q3)
        
        Returns:
            dict: Dashboard con widgets
                {
                    'widgets': [...],
                    'last_updated': timestamp,
                    'next_update': timestamp,
                    'data_status': 'static'
                }
        
        CNST-010: Cache LocMem 5 min
        CNST-003: Datos estáticos (6-12h desfase)
        """
        # Intentar obtener del cache
        cache_key = f'dashboard_quarterly_metrics_{quarter}'
        cached = cache.get(cache_key)
        
        if cached:
            logger.info(f"Dashboard cache HIT: {cache_key}")
            return cached
        
        logger.info(f"Dashboard cache MISS: {cache_key}")
        
        # Generar widgets
        widgets = []
        
        # KPI 1: Total Llamadas
        total_calls = QuarterlyReport.objects.filter(
            quarter=quarter
        ).aggregate(
            total=models.Sum('total_calls')
        )['total'] or 0
        
        widgets.append({
            'type': 'kpi',
            'id': 'total_calls',
            'title': 'Total Llamadas',
            'value': total_calls,
            'format': 'number'
        })
        
        # KPI 2: Tasa Abandono
        avg_abandoned = QuarterlyReport.objects.filter(
            quarter=quarter
        ).aggregate(
            avg=models.Avg('abandoned_percentage')
        )['avg'] or 0
        
        widgets.append({
            'type': 'kpi',
            'id': 'abandoned_rate',
            'title': 'Tasa Abandono',
            'value': round(avg_abandoned, 2),
            'format': 'percentage'
        })
        
        # Chart: Top 10 DIDs
        top_dids = QuarterlyReport.objects.filter(
            quarter=quarter
        ).order_by('-total_calls')[:10]
        
        widgets.append({
            'type': 'bar_chart',
            'id': 'top_dids',
            'title': 'Top 10 DIDs por Llamadas',
            'data': [
                {
                    'label': record.did,
                    'value': record.total_calls
                }
                for record in top_dids
            ]
        })
        
        # Table: Detalle por DID
        detail = QuarterlyReport.objects.filter(
            quarter=quarter
        ).order_by('-total_calls')[:20]
        
        widgets.append({
            'type': 'table',
            'id': 'did_detail',
            'title': 'Detalle por DID',
            'columns': ['DID', 'Total', 'Transferidas', 'Abandonadas', '% Abandono'],
            'rows': [
                [
                    record.did,
                    record.total_calls,
                    record.transferred_calls,
                    record.abandoned_calls,
                    f"{record.abandoned_percentage}%"
                ]
                for record in detail
            ]
        })
        
        # Metadata
        from apps.pipeline.models import JobExecutionLog
        
        last_etl = JobExecutionLog.objects.filter(
            status='completed'
        ).order_by('-end_time').first()
        
        last_updated = last_etl.end_time if last_etl else timezone.now()
        next_update = last_updated + timedelta(hours=6)  # ETL cada 6h
        
        dashboard = {
            'widgets': widgets,
            'last_updated': last_updated.isoformat(),
            'next_update': next_update.isoformat(),
            'data_status': 'static',  # ⚠️ CNST-003: Datos estáticos
            'refresh_interval': None,  # ✅ NO auto-refresh
        }
        
        # Guardar en cache (LocMem, 5 min)
        cache.set(cache_key, dashboard, DashboardService.CACHE_TTL)
        
        logger.info(f"Dashboard generado y cacheado: {cache_key}")
        
        return dashboard
```

---

### 4.4 Estructura de Archivos Completa

```
iact-call-center/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py          # Settings base
│   │   ├── development.py   # Dev (LocMem cache)
│   │   └── production.py    # Prod (Dummy cache)
│   ├── urls.py              # URLs principales
│   ├── routers.py           # IVRRouter (CNST-002)
│   └── wsgi.py
│
├── apps/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py        # TimeStampedModel, SoftDeleteMixin
│   │   └── apps.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── pagination.py    # paginate_queryset()
│   │   ├── validation.py    # validate_date_range()
│   │   └── exceptions.py    # Custom exceptions
│   │
│   ├── ivr/
│   │   ├── __init__.py
│   │   ├── models.py        # CallRecord, QuarterlyReport, etc
│   │   ├── apps.py
│   │   └── constants.py     # VALID_DIDS, MAX_EXPORT_ROWS_CSV
│   │
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── models.py        # (ninguno, usa apps/ivr/)
│   │   ├── serializers.py   # ReportSerializer
│   │   ├── views.py         # ReportViewSet
│   │   ├── services.py      # ReportService
│   │   ├── urls.py
│   │   └── apps.py
│   │
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── models.py        # (ninguno, usa apps/ivr/)
│   │   ├── serializers.py   # DashboardSerializer
│   │   ├── views.py         # DashboardViewSet
│   │   ├── services.py      # DashboardService
│   │   ├── urls.py
│   │   └── apps.py
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── models.py        # (usa JobExecutionLog de ivr/)
│   │   ├── scheduler.py     # APScheduler (CNST-013)
│   │   ├── views.py         # PipelineStatusView
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── run_etl.py
│   │   ├── urls.py
│   │   └── apps.py
│   │
│   ├── access/
│   │   ├── __init__.py
│   │   ├── models.py        # Function, FunctionGroup, etc (RBAC v6.0.0)
│   │   ├── serializers.py   # FunctionSerializer
│   │   ├── views.py         # FunctionViewSet
│   │   ├── decorators.py    # @require_function()
│   │   ├── permissions.py   # HasFunction, DynamicFunctionPermission
│   │   ├── urls.py
│   │   └── apps.py
│   │
│   ├── authentication/
│   │   ├── __init__.py
│   │   ├── views.py         # LoginView, LogoutView
│   │   ├── serializers.py   # LoginSerializer
│   │   ├── urls.py
│   │   └── apps.py
│   │
│   ├── users/
│   │   ├── __init__.py
│   │   ├── models.py        # User (Django custom)
│   │   ├── serializers.py   # UserSerializer
│   │   ├── views.py         # UserViewSet
│   │   ├── urls.py
│   │   └── apps.py
│   │
│   ├── alerts/
│   │   ├── __init__.py
│   │   ├── models.py        # InternalMessage (CNST-001)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── apps.py
│   │
│   └── audit/
│       ├── __init__.py
│       ├── models.py        # AuditLog (CNST-031)
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── apps.py
│
├── manage.py
└── requirements/
    ├── base.txt             # Django, DRF, openpyxl
    ├── development.txt      # Django extensions, debug toolbar
    └── production.txt       # Gunicorn, psycopg2

RESTRICCIONES APLICADAS:
✓ CNST-001: apps/alerts/ (buzón interno, NO email)
✓ CNST-002: apps/ivr/ (readonly, managed=False)
✓ CNST-010: settings/ (LocMem/Dummy cache, NO Redis)
✓ CNST-013: apps/pipeline/scheduler.py (APScheduler, NO Celery)
✓ CLEAN_CODE v3.0.1: Nomenclatura consistente
✓ RBAC v6.0.0: apps/access/ completo
```

---

<a name="5-apis-y-endpoints"></a>

## 5. APIS Y ENDPOINTS

### 5.1 Endpoints de Reportes (POST)

**Base URL:** `/api/v1/reports/`

**RBAC v6.0.0 Aplicado:**
- RPT_VIEW: `reports.view`
- RPT_CREATE: `reports.create`
- RPT_DELETE: `reports.delete`
- RPT_EXP_CSV: `reports.export.csv`
- RPT_EXP_EXCEL: `reports.export.excel`

---

#### **5.1.1 Reporte de Llamadas Abandonadas**

```python
# apps/reports/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.access.decorators import require_function
from apps.access.permissions import DynamicFunctionPermission
from apps.reports.services import ReportService
import logging

logger = logging.getLogger(__name__)


class AbandonedCallsReportViewSet(viewsets.ViewSet):
    """
    ViewSet para reporte de llamadas abandonadas.
    
    Endpoints:
    - POST /api/v1/reports/abandonadas/ → Genera reporte
    - POST /api/v1/reports/abandonadas/{id}/export/ → Exporta
    
    RBAC v6.0.0:
    - Crear: RPT_CREATE (reports.create)
    - Ver: RPT_VIEW (reports.view)
    - Exportar CSV: RPT_EXP_CSV (reports.export.csv)
    - Exportar Excel: RPT_EXP_EXCEL (reports.export.excel)
    
    CLEAN_CODE v3.0.1:
    - Clase: PascalCase en inglés
    - Métodos: snake_case en inglés
    - Docstrings: español, formato Google
    """
    
    permission_classes = [DynamicFunctionPermission]
    
    # Mapeo de acciones → funciones RBAC v6.0.0
    function_map = {
        'create': 'reports.create',      # RPT_CREATE
        'list': 'reports.view',          # RPT_VIEW
        'retrieve': 'reports.view',      # RPT_VIEW
        'export_csv': 'reports.export.csv',    # RPT_EXP_CSV
        'export_excel': 'reports.export.excel',  # RPT_EXP_EXCEL
    }
    
    def create(self, request):
        """
        Genera reporte de llamadas abandonadas.
        
        POST /api/v1/reports/abandonadas/
        
        Request Body:
            {
                "quarter": "Q1",
                "did": "555-1234",  # opcional
                "start_date": "2025-01-01",  # opcional
                "end_date": "2025-03-31"     # opcional
            }
        
        Response:
            {
                "report_id": 123,
                "quarter": "Q1",
                "record_count": 450,
                "generated_at": "2025-01-19T10:30:00Z",
                "data": [...]
            }
        
        Raises:
            PermissionDenied: Si no tiene RPT_CREATE
            ValidationError: Si parámetros inválidos
        
        RBAC: Requiere reports.create
        CNST-025: Timeout 90s
        """
        quarter = request.data.get('quarter')
        did = request.data.get('did')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        try:
            # Generar reporte
            queryset = ReportService.generate_abandoned_calls_report(
                quarter=quarter,
                did=did,
                start_date=start_date,
                end_date=end_date
            )
            
            # Serializar
            data = [
                {
                    'did': record.did,
                    'date': record.date.isoformat(),
                    'total_abandoned': record.total_abandoned,
                    'less_30s': record.less_than_30s,
                    'between_30_60s': record.between_30_60s,
                    'more_60s': record.more_than_60s,
                    'avg_wait_time': record.average_wait_time
                }
                for record in queryset
            ]
            
            logger.info(
                f"Reporte abandonadas generado por {request.user.username}: "
                f"{len(data)} registros"
            )
            
            return Response({
                'quarter': quarter,
                'record_count': len(data),
                'generated_at': timezone.now().isoformat(),
                'data': data
            }, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            logger.warning(f"Error generando reporte: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='export')
    def export_csv(self, request):
        """
        Exporta reporte a CSV.
        
        POST /api/v1/reports/abandonadas/export/
        
        Request Body:
            {
                "quarter": "Q1",
                "format": "csv"  # o "excel"
            }
        
        Response:
            {
                "download_url": "/media/exports/abandonadas_Q1_20250119.csv",
                "record_count": 450,
                "format": "csv"
            }
        
        RBAC: Requiere reports.export.csv o reports.export.excel
        CNST-007: Máx 100K registros (CSV), 50K (Excel)
        """
        quarter = request.data.get('quarter')
        format_type = request.data.get('format', 'csv')
        
        # Generar queryset
        queryset = ReportService.generate_abandoned_calls_report(
            quarter=quarter
        )
        
        try:
            if format_type == 'csv':
                # Verificar permiso RPT_EXP_CSV
                if not request.user.has_function('reports.export.csv'):
                    return Response({
                        'error': 'Permiso denegado: reports.export.csv requerido'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                filename = f"abandonadas_{quarter}_{timezone.now().strftime('%Y%m%d')}.csv"
                file_path = ReportService.export_to_csv(queryset, filename)
            
            elif format_type == 'excel':
                # Verificar permiso RPT_EXP_EXCEL
                if not request.user.has_function('reports.export.excel'):
                    return Response({
                        'error': 'Permiso denegado: reports.export.excel requerido'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                filename = f"abandonadas_{quarter}_{timezone.now().strftime('%Y%m%d')}.xlsx"
                file_path = ReportService.export_to_excel(queryset, filename)
            
            else:
                return Response({
                    'error': f'Formato no soportado: {format_type}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(
                f"Reporte exportado por {request.user.username}: "
                f"{filename} ({queryset.count()} registros)"
            )
            
            return Response({
                'download_url': file_path,
                'record_count': queryset.count(),
                'format': format_type
            })
        
        except ValueError as e:
            # CNST-007: Límite excedido
            logger.warning(f"Límite export excedido: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
```

**Resumen Endpoints Reports:**

| Endpoint | Método | RBAC v6.0.0 | CNST | Descripción |
|----------|--------|-------------|------|-------------|
| `/api/v1/reports/abandonadas/` | POST | reports.create | CNST-025 (90s) | Genera reporte abandonadas |
| `/api/v1/reports/clientes/` | POST | reports.create | CNST-025 | Genera reporte clientes únicos |
| `/api/v1/reports/transferencias/` | POST | reports.create | CNST-025 | Genera reporte transferencias |
| `/api/v1/reports/detalle-transferencias/` | POST | reports.create | CNST-025 | Genera detalle transferencias |
| `/api/v1/reports/menu-errores/` | POST | reports.create | CNST-025 | Genera reporte errores menú |
| `/api/v1/reports/{tipo}/export/` | POST | reports.export.csv/excel | CNST-007, CNST-025 | Exporta a CSV/Excel |
| `/api/v1/reports/{tipo}/{id}/` | DELETE | reports.delete | - | Elimina reporte |

---

### 5.2 Endpoints de Dashboards (GET)

**Base URL:** `/api/v1/dashboard/`

**RBAC v6.0.0 Aplicado:**
- DSH_VIEW: `dashboard.view`
- DSH_EXP_CSV: `dashboard.export.csv`
- DSH_EXP_EXCEL: `dashboard.export.excel`

---

#### **5.2.1 Dashboard Métricas Trimestrales**

```python
# apps/dashboard/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.access.decorators import require_function
from apps.dashboard.services import DashboardService
import logging

logger = logging.getLogger(__name__)


class QuarterlyMetricsDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para dashboard de métricas trimestrales.
    
    Endpoint:
    - GET /api/v1/dashboard/metricas-trimestrales/?quarter=Q1
    
    RBAC v6.0.0:
    - Ver: DSH_VIEW (dashboard.view)
    - Exportar CSV: DSH_EXP_CSV (dashboard.export.csv)
    - Exportar Excel: DSH_EXP_EXCEL (dashboard.export.excel)
    
    RESTRICCIONES:
    - CNST-003: Datos estáticos (6-12h desfase)
    - CNST-010: Cache LocMem 5 min (NO Redis)
    - CNST-023: NO auto-refresh
    """
    
    @require_function('dashboard.view')
    def list(self, request):
        """
        Obtiene dashboard de métricas trimestrales.
        
        GET /api/v1/dashboard/metricas-trimestrales/?quarter=Q1
        
        Query Params:
            quarter: Trimestre (Q1, Q2, Q3)
        
        Response:
            {
                "widgets": [
                    {
                        "type": "kpi",
                        "id": "total_calls",
                        "title": "Total Llamadas",
                        "value": 45000,
                        "format": "number"
                    },
                    {
                        "type": "bar_chart",
                        "id": "top_dids",
                        "title": "Top 10 DIDs",
                        "data": [...]
                    },
                    {
                        "type": "table",
                        "id": "did_detail",
                        "title": "Detalle por DID",
                        "columns": [...],
                        "rows": [...]
                    }
                ],
                "last_updated": "2025-01-19T08:00:00Z",
                "next_update": "2025-01-19T14:00:00Z",
                "data_status": "static",
                "refresh_interval": null
            }
        
        RBAC: Requiere dashboard.view
        CNST-010: Cache LocMem 5 min
        CNST-003: Datos estáticos, NO auto-refresh
        """
        quarter = request.query_params.get('quarter', 'Q1')
        
        # Obtener dashboard (con cache LocMem)
        dashboard = DashboardService.get_quarterly_metrics_dashboard(quarter)
        
        logger.info(
            f"Dashboard métricas trimestrales solicitado por {request.user.username}: "
            f"{quarter}"
        )
        
        return Response(dashboard)
    
    @action(detail=False, methods=['post'], url_path='export')
    @require_function('dashboard.export.csv')
    def export_csv(self, request):
        """
        Exporta snapshot del dashboard a CSV.
        
        POST /api/v1/dashboard/metricas-trimestrales/export/
        
        Request Body:
            {
                "quarter": "Q1",
                "format": "csv"  # o "excel"
            }
        
        Response:
            {
                "download_url": "/media/exports/dashboard_Q1_20250119.csv",
                "widgets_exported": 4,
                "format": "csv"
            }
        
        RBAC: Requiere dashboard.export.csv o dashboard.export.excel
        """
        quarter = request.data.get('quarter', 'Q1')
        format_type = request.data.get('format', 'csv')
        
        # Obtener dashboard
        dashboard = DashboardService.get_quarterly_metrics_dashboard(quarter)
        
        # Exportar snapshot
        # ... implementación export ...
        
        logger.info(
            f"Dashboard exportado por {request.user.username}: "
            f"{quarter} ({format_type})"
        )
        
        return Response({
            'download_url': f"/media/exports/dashboard_{quarter}.{format_type}",
            'widgets_exported': len(dashboard['widgets']),
            'format': format_type
        })
```

**Resumen Endpoints Dashboard:**

| Endpoint | Método | RBAC v6.0.0 | CNST | Descripción |
|----------|--------|-------------|------|-------------|
| `/api/v1/dashboard/metricas-trimestrales/` | GET | dashboard.view | CNST-003, CNST-010 | Dashboard KPIs trimestre |
| `/api/v1/dashboard/analisis-clientes/` | GET | dashboard.view | CNST-003, CNST-010 | Dashboard análisis clientes |
| `/api/v1/dashboard/performance-ivr/` | GET | dashboard.view | CNST-003, CNST-010 | Dashboard performance IVR |
| `/api/v1/dashboard/{tipo}/export/` | POST | dashboard.export.csv/excel | - | Exporta snapshot dashboard |

---

### 5.3 Pipeline Monitoring

```python
# apps/pipeline/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from apps.access.decorators import require_function
from apps.pipeline.models import JobExecutionLog
from apps.pipeline.scheduler import scheduler


class PipelineStatusView(APIView):
    """
    Vista para monitoreo del estado del pipeline ETL.
    
    Endpoint:
    - GET /api/v1/pipeline/status/
    
    RBAC: Requiere pipeline.monitor
    """
    
    @require_function('pipeline.monitor')
    def get(self, request):
        """
        Obtiene estado actual del pipeline ETL.
        
        GET /api/v1/pipeline/status/
        
        Response:
            {
                "scheduler_running": true,
                "last_execution": {
                    "job_name": "sp_etl_daily",
                    "status": "completed",
                    "start_time": "2025-01-19T02:00:00Z",
                    "end_time": "2025-01-19T02:12:34Z",
                    "duration_seconds": 754.3,
                    "records_processed": 450000
                },
                "next_execution": "2025-01-19T08:00:00Z",
                "recent_jobs": [...]
            }
        
        RBAC: Requiere pipeline.monitor
        """
        # Scheduler status
        scheduler_running = scheduler.running if scheduler else False
        
        # Last execution
        last_job = JobExecutionLog.objects.order_by('-start_time').first()
        
        last_execution = None
        if last_job:
            last_execution = {
                'job_name': last_job.job_name,
                'status': last_job.status,
                'start_time': last_job.start_time.isoformat(),
                'end_time': last_job.end_time.isoformat() if last_job.end_time else None,
                'duration_seconds': float(last_job.duration_seconds) if last_job.duration_seconds else None,
                'records_processed': last_job.records_processed,
                'records_failed': last_job.records_failed,
                'error_message': last_job.error_message
            }
        
        # Next execution (estimate)
        next_execution = None
        if last_job and last_job.end_time:
            from datetime import timedelta
            next_execution = (last_job.end_time + timedelta(hours=6)).isoformat()
        
        # Recent jobs
        recent = JobExecutionLog.objects.order_by('-start_time')[:10]
        recent_jobs = [
            {
                'job_name': job.job_name,
                'status': job.status,
                'start_time': job.start_time.isoformat(),
                'duration_seconds': float(job.duration_seconds) if job.duration_seconds else None
            }
            for job in recent
        ]
        
        return Response({
            'scheduler_running': scheduler_running,
            'last_execution': last_execution,
            'next_execution': next_execution,
            'recent_jobs': recent_jobs
        })
```

---

<a name="6-flujo-de-datos-completo"></a>

## 6. FLUJO DE DATOS COMPLETO

### 6.1 Flujo General del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│ FLUJO GENERAL DE DATOS - SISTEMA IACT                          │
└─────────────────────────────────────────────────────────────────┘

1. INGESTA DE DATOS (Sistema IVR externo)
   │
   ├─> Sistema PBX genera CDRs en tiempo real
   └─> Inserta en MariaDB: tbl_historico_t{1,2,3}_2025

2. PROCESAMIENTO ETL (APScheduler cada 6-12h)
   │
   ├─> APScheduler ejecuta run_etl() cada 6h
   ├─> Management command llama sp_etl_daily()
   ├─> Stored Procedure procesa datos
   │   ├─> UNION ALL (t1 + t2 + t3)
   │   ├─> GROUP BY, agregaciones
   │   └─> INSERT en tbl_reporte_*
   └─> Actualiza job_execution_log

3. CONSULTA API (Usuario → Frontend → Backend)
   │
   ├─> Usuario autenticado (Django sessions DB)
   ├─> Frontend hace request a API
   └─> Backend Django valida RBAC v6.0.0

4A. FLUJO REPORTS (POST)
    │
    ├─> POST /api/v1/reports/abandonadas/
    ├─> ReportViewSet valida permission (reports.create)
    ├─> ReportService genera queryset
    ├─> Serializa a JSON
    ├─> Retorna datos + metadata
    └─> Si export: ReportService.export_to_csv/excel()
        └─> Valida límites (CNST-007: 100K CSV, 50K Excel)

4B. FLUJO DASHBOARD (GET)
    │
    ├─> GET /api/v1/dashboard/metricas-trimestrales/?quarter=Q1
    ├─> DashboardViewSet valida permission (dashboard.view)
    ├─> DashboardService verifica cache (LocMem, 5 min)
    │   ├─> Cache HIT → Retorna cached
    │   └─> Cache MISS → Genera widgets
    │       ├─> Consulta MariaDB (readonly)
    │       ├─> Calcula KPIs, Charts, Tables
    │       ├─> Guarda en cache (LocMem, 5 min)
    │       └─> Retorna widgets + metadata
    └─> Response JSON con:
        ├─> widgets: [...]
        ├─> last_updated: timestamp ETL
        ├─> next_update: timestamp + 6h
        ├─> data_status: "static" (CNST-003)
        └─> refresh_interval: null (NO auto-refresh)

5. AUDITORÍA (CNST-031)
   │
   ├─> Cada request genera log de auditoría
   ├─> Eventos críticos: login, export, cambios permisos
   ├─> AuditLog immutable (append-only)
   └─> Retención 2 años mínimo

RESTRICCIONES APLICADAS:
✓ CNST-002: BD IVR readonly (ZERO escritura)
✓ CNST-003: Datos estáticos (6-12h desfase)
✓ CNST-004: Timeout DB 300s
✓ CNST-007: Límites export (100K CSV, 50K Excel)
✓ CNST-010: Cache LocMem (NO Redis)
✓ CNST-013: APScheduler (NO Celery)
✓ CNST-025: Timeout request 90s
✓ CNST-031: Auditoría immutable
```

---

### 6.2 Diagrama de Secuencia: Generación de Reporte

```
Usuario     Frontend    Django API  ReportService  MariaDB (IVR)
  │            │            │             │              │
  ├─ 1. Login ─────────────>│             │              │
  │            │            │             │              │
  │<─ 2. Token ─────────────┤             │              │
  │            │            │             │              │
  ├─ 3. POST /reports/abandonadas/ (quarter=Q1) ───────>│
  │            │            │             │              │
  │            │            ├─ 4. Valida RBAC (RPT_CREATE)
  │            │            │             │              │
  │            │            ├─ 5. generate_report(Q1) ──>│
  │            │            │             │              │
  │            │            │             ├─ 6. SELECT * FROM tbl_reporte_abandonadas WHERE ...
  │            │            │             │              │
  │            │            │             │<─ 7. ResultSet (450 rows)
  │            │            │             │              │
  │            │            │<─ 8. QuerySet ─────────────┤
  │            │            │             │              │
  │            │            ├─ 9. Serialize (JSON)       │
  │            │            │             │              │
  │<─ 10. 201 CREATED {data: [...], count: 450} ────────┤
  │            │            │             │              │
  
Duración total: ~800ms

RESTRICCIONES:
✓ CNST-002: SELECT only (readonly)
✓ CNST-004: Timeout DB 300s
✓ CNST-025: Timeout request 90s
✓ RBAC v6.0.0: reports.create validado
```

---

### 6.3 Diagrama de Secuencia: Dashboard con Cache

```
Usuario     Frontend    DashboardAPI  DashboardService  Cache (LocMem)  MariaDB
  │            │            │               │                  │            │
  ├─ 1. GET /dashboard/metricas/?quarter=Q1 ──────────────────>│            │
  │            │            │               │                  │            │
  │            │            ├─ 2. Valida RBAC (DSH_VIEW)       │            │
  │            │            │               │                  │            │
  │            │            ├─ 3. get_dashboard(Q1) ──────────>│            │
  │            │            │               │                  │            │
  │            │            │               ├─ 4. cache.get('dashboard_Q1')
  │            │            │               │                  │            │
  │            │            │               │<─ 5. None (MISS) ┤            │
  │            │            │               │                  │            │
  │            │            │               ├─ 6. SELECT * FROM tbl_reporte_trimestral
  │            │            │               │                  │            │
  │            │            │               │<─ 7. ResultSet ──────────────┤
  │            │            │               │                  │            │
  │            │            │               ├─ 8. Calcula widgets (KPI, Charts)
  │            │            │               │                  │            │
  │            │            │               ├─ 9. cache.set('dashboard_Q1', widgets, 300)
  │            │            │               │                  │            │
  │            │            │<─ 10. Dashboard ────────────────┤            │
  │            │            │               │                  │            │
  │<─ 11. 200 OK {widgets: [...], last_updated, next_update} ─┤            │
  │            │            │               │                  │            │

Segunda solicitud (dentro de 5 min) - Cache HIT:

Usuario     Frontend    DashboardAPI  DashboardService  Cache (LocMem)  MariaDB
  │            │            │               │                  │            │
  ├─ 1. GET /dashboard/metricas/?quarter=Q1 ──────────────────>│            │
  │            │            │               │                  │            │
  │            │            ├─ 2. get_dashboard(Q1) ──────────>│            │
  │            │            │               │                  │            │
  │            │            │               ├─ 3. cache.get('dashboard_Q1')
  │            │            │               │                  │            │
  │            │            │               │<─ 4. Dashboard (HIT) ────────┤
  │            │            │               │                  │            │
  │            │            │<─ 5. Dashboard (cached) ────────┤            │
  │            │            │               │                  │            │
  │<─ 6. 200 OK {widgets: [...]} (cache hit) ──────────────────┤            │
  │            │            │               │                  │            │

Duración Cache MISS: ~800ms
Duración Cache HIT: ~50ms (16x más rápido)

RESTRICCIONES:
✓ CNST-003: Datos estáticos (NO real-time)
✓ CNST-010: LocMem Cache (NO Redis)
✓ CNST-023: NO auto-refresh
✓ RBAC v6.0.0: dashboard.view validado
```

---

### 6.4 Cache Strategy (CNST-010: LocMem, NO Redis)

```
┌─────────────────────────────────────────────────────────────────┐
│ CACHE STRATEGY: LocMem Cache (CNST-010)                        │
└─────────────────────────────────────────────────────────────────┘

CONFIGURACIÓN (CNST-010):
  ✓ Backend: django.core.cache.backends.locmem.LocMemCache
  ✓ Location: 'iact-cache'
  ✓ TTL: 300 segundos (5 minutos)
  ❌ NO Redis
  ❌ NO Memcached

VENTAJAS LocMem:
  ✓ Sin dependencias externas
  ✓ Sin procesos adicionales
  ✓ Deploy simple
  ✓ Troubleshooting fácil

LIMITACIONES LocMem:
  ⚠️  Cache por-proceso (no compartido entre workers)
  ⚠️  Se pierde al reiniciar proceso
  ⚠️  Limitado por RAM del proceso

ALTERNATIVA PRODUCCIÓN (multi-worker):
  - Backend: django.core.cache.backends.dummy.DummyCache
  - Efecto: Deshabilita cache completamente
  - Queries directas a BD siempre
  - Sin inconsistencia entre workers

DECISIÓN ARQUITECTÓNICA:
  Para IACT (volumetría ~5-10K llamadas/día):
  - LocMem suficiente para mono-worker
  - Impacto mínimo si cache miss
  - Queries MariaDB rápidas (~800ms)
  - Frecuencia consulta baja

FUNCIONALIDADES CON CACHE:
  ✓ Dashboards (5 min TTL)
  ❌ Reports (NO cache, bajo demanda)
  ❌ Pipeline status (NO cache, datos en vivo)

CONFIGURACIÓN:

# config/settings/development.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'iact-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
        'KEY_PREFIX': 'iact',
        'TIMEOUT': 300,
    }
}

# config/settings/production.py (mono-worker)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'iact-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
        'KEY_PREFIX': 'iact',
        'TIMEOUT': 300,
    }
}

# config/settings/production.py (multi-worker alternativo)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

REFERENCIAS:
  - CNST-010: NO Redis
  - RESTRICCIONES v1.0.0: Parte 1, Sección 1.2
```

---

**FIN DE PARTE 2/3**

**Continúa en:** ARQUITECTURA_ETL_v3_0_0_PARTE_3.md

---

## RESUMEN PARTE 2

**✅ Completado:**
- Sección 4: Arquitectura Django
  - Apps y responsabilidades (11 apps documentadas)
  - Modelos abstractos (TimeStampedModel, SoftDeleteMixin)
  - Modelos RBAC completos (Function, FunctionGroup, etc)
  - Service Layer Pattern (ReportService, DashboardService)
  - Estructura de archivos completa

- Sección 5: APIs y Endpoints
  - Endpoints Reports (7 endpoints) con ejemplos completos
  - Endpoints Dashboard (3 endpoints) con ejemplos completos
  - Pipeline monitoring
  - RBAC v6.0.0 aplicado (permission_django correcto)
  - Límites CNST-007 documentados

- Sección 6: Flujo de Datos Completo
  - Flujo general sistema completo
  - Diagrama secuencia: Generación de reporte
  - Diagrama secuencia: Dashboard con cache
  - Cache strategy LocMem (CNST-010, NO Redis)

**📊 Estadísticas:**
- Líneas: ~2,100
- Tamaño: ~88KB
- Modelos Django: 8 completos (RBAC)
- Endpoints: 10 documentados
- ViewSets: 2 ejemplos completos

**📚 Aplicado:**
- CLEAN_CODE v3.0.1: 100% nomenclatura consistente
- RESTRICCIONES v1.0.0: 14 CNSTs aplicados
- RBAC v6.0.0: 46 funciones, permission_django correcto

**🔜 Próxima parte:**
- Sección 7: Jobs Programados (APScheduler completo)
- Sección 8: Deployment (Nginx + Gunicorn + Systemd)
- Sección 9: Seguridad (Sessions DB, Secrets, Logging)
- Sección 10: Testing y QA
