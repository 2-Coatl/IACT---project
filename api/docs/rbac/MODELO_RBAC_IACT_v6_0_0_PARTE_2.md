# MODELO RBAC IACT - v6.0.0 PARTE 2/2

## Sistema IACT - IVR Analytics & Customer Tracking

---

**Proyecto:** IACT-2025-001  
**Documento:** IACT-RBAC-001-v6.0.0-PARTE-2  
**Título:** Modelo de Control de Acceso Basado en Funciones Atómicas - Parte 2  
**Versión:** 6.0.0 - Implementación y Migración  
**Fecha:** 19 de enero de 2026  
**Estado:** Listo para Implementación

---

## TABLA DE CONTENIDO - PARTE 2/2

**PARTE 1 (Documento separado):**
1. Filosofía del Modelo
2. Arquitectura IACT
3. Catálogo de 46 Funciones
4. Los 10 Grupos de Funciones
5. Separación de Funciones (SoD)
6. Permisos Temporales

**PARTE 2 (Este documento):**

7. [Modelo de Datos](#7-modelo-datos)
8. [Implementación SQL](#8-sql)
9. [Implementación Django/DRF](#9-django)
10. [Mapeo Funciones → Casos de Uso](#10-mapeo-uc)
11. [Migración desde v5.1](#11-migracion-v51)
12. [Migración v5.2 → v6.0.0](#12-migracion-v60)
13. [Roadmap de Funciones](#13-roadmap)

---

<a name="7-modelo-datos"></a>

## 7. MODELO DE DATOS

### 7.1 Diagrama Entidad-Relación

```
┌─────────────────────┐
│ User                │
│ (Django auth.User)  │
└──────────┬──────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────────────────┐
│ UserFunctionAssignment              │
├─────────────────────────────────────┤
│ user FK                             │
│ function FK ──────────┐             │
│ is_temporary          │             │
│ valid_from            │             │
│ valid_until           │             │
│ justification         │             │
│ approved_by FK        │             │
│ created_by FK         │             │
│ revoked_at            │             │
└───────────────────────┼─────────────┘
                        │
                        │ N:1
                        ▼
           ┌────────────────────────┐
           │ Function               │
           ├────────────────────────┤
           │ code (RPT_VIEW)        │
           │ permission_django PK   │
           │ display_name           │
           │ module                 │
           │ status ⭐              │
           │ description            │
           └───────┬────────────────┘
                   │
                   │ N:N
                   ▼
           ┌────────────────────────┐
           │ FunctionGroup          │
           ├────────────────────────┤
           │ group_id (AGR-001)     │
           │ name                   │
           │ description            │
           └───────┬────────────────┘
                   │
                   │ N:N
                   ▼
┌──────────────────────────────────────┐
│ UserFunctionGroupAssignment          │
├──────────────────────────────────────┤
│ user FK                              │
│ group FK                             │
│ assigned_by FK                       │
│ assigned_at                          │
└──────────────────────────────────────┘

           ┌────────────────────────┐
           │ FunctionSeparationRule │
           ├────────────────────────┤
           │ rule_id                │
           │ name                   │
           │ description            │
           │ group_a (functions)    │
           │ group_b (functions)    │
           └────────────────────────┘
```

---

### 7.2 Modelo: Function

```python
# apps/access/models.py

from django.db import models
from django.core.validators import MinLengthValidator

class FunctionStatus(models.TextChoices):
    """Estados posibles de una función."""
    ACTIVO = 'activo', 'Activo'
    PLANIFICADO = 'planificado', 'Planificado'
    DEPRECADO = 'deprecado', 'Deprecado'


class Function(models.Model):
    """
    Función atómica del sistema RBAC.
    
    Representa una capacidad específica que puede ser asignada
    a usuarios individual o grupalmente.
    
    Cambios v6.0.0:
    - Agregado: campo 'code' (referencia rápida)
    - Agregado: campo 'status' (activo/planificado/deprecado)
    - Modificado: permission_django ahora PRIMARY KEY
    - Formato: permission_django usa punto (reports.export.csv)
    """
    
    # Código referencial para comunicación (RPT_VIEW, DSH_EXP_CSV)
    code = models.CharField(
        max_length=30,
        unique=True,
        help_text="Código de referencia: RPT_VIEW, DSH_EXP_CSV, USR_CREATE"
    )
    
    # Permission Django - PRIMARY KEY (reports.view, dashboard.export.csv)
    permission_django = models.CharField(
        max_length=100,
        primary_key=True,
        help_text="Permiso Django: reports.view, dashboard.export.csv"
    )
    
    # Nombre para UI en español
    display_name = models.CharField(
        max_length=200,
        help_text="Nombre para interfaz: Ve Reportes, Exporta CSV"
    )
    
    # Módulo al que pertenece (reports, dashboard, users, etc)
    module = models.CharField(
        max_length=50,
        help_text="Módulo: reports, dashboard, users, auth, pipeline"
    )
    
    # Estado de la función ⭐ NUEVO v6.0.0
    status = models.CharField(
        max_length=20,
        choices=FunctionStatus.choices,
        default=FunctionStatus.ACTIVO,
        help_text="Estado: activo (funcional), planificado (roadmap), deprecado (obsoleto)"
    )
    
    # Descripción detallada (incluye casos de uso)
    description = models.TextField(
        help_text="Descripción completa con casos de uso y restricciones CNST"
    )
    
    # Metadatos
    is_active = models.BooleanField(
        default=True,
        help_text="Si la función está habilitada para asignación"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'access_functions'
        verbose_name = 'Función'
        verbose_name_plural = 'Funciones'
        ordering = ['module', 'code']
        indexes = [
            models.Index(fields=['module']),
            models.Index(fields=['status']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.display_name}"
    
    def clean(self):
        """Validaciones personalizadas."""
        from django.core.exceptions import ValidationError
        
        # Validar formato permission_django
        if '.' not in self.permission_django:
            raise ValidationError({
                'permission_django': 'Debe tener formato module.action (ej: reports.view)'
            })
        
        # Validar que module coincida con prefijo de permission_django
        module_prefix = self.permission_django.split('.')[0]
        if self.module != module_prefix:
            raise ValidationError({
                'module': f'Module debe coincidir con prefijo de permission_django: {module_prefix}'
            })
        
        # Validar code format (MAYÚSCULAS_GUIONES_BAJOS)
        if not self.code.replace('_', '').isalnum():
            raise ValidationError({
                'code': 'Code debe contener solo letras, números y guiones bajos'
            })
        
        # Validar que funciones planificadas estén inactivas
        if self.status == FunctionStatus.PLANIFICADO and self.is_active:
            raise ValidationError({
                'is_active': 'Funciones planificadas deben tener is_active=False'
            })
    
    def is_assignable(self):
        """Verifica si la función puede ser asignada."""
        return (
            self.is_active and 
            self.status == FunctionStatus.ACTIVO
        )
```

---

### 7.3 Modelo: FunctionGroup

```python
class FunctionGroup(models.Model):
    """
    Grupo de funciones que se asignan juntas.
    
    Ejemplo: AGR-001 (Operador Básico) agrupa 7 funciones básicas.
    """
    
    # ID del grupo (AGR-001, AGR-002, etc)
    group_id = models.CharField(
        max_length=20,
        primary_key=True,
        help_text="Identificador único: AGR-001, AGR-002"
    )
    
    # Nombre del grupo
    name = models.CharField(
        max_length=100,
        help_text="Nombre descriptivo: Operador Básico, Analista Senior"
    )
    
    # Descripción
    description = models.TextField(
        help_text="Descripción del perfil y casos de uso típicos"
    )
    
    # Funciones incluidas (ManyToMany)
    functions = models.ManyToManyField(
        Function,
        through='FunctionGroupMembership',
        related_name='groups'
    )
    
    # Metadatos
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'access_function_groups'
        verbose_name = 'Grupo de Funciones'
        verbose_name_plural = 'Grupos de Funciones'
        ordering = ['group_id']
    
    def __str__(self):
        return f"{self.group_id} - {self.name}"
    
    def get_active_functions(self):
        """Retorna solo funciones activas del grupo."""
        return self.functions.filter(
            status=FunctionStatus.ACTIVO,
            is_active=True
        )
    
    def function_count(self):
        """Cuenta total de funciones en el grupo."""
        return self.functions.count()


class FunctionGroupMembership(models.Model):
    """
    Relación entre grupos y funciones.
    
    Tabla intermedia para ManyToMany con metadatos adicionales.
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
    
    # Orden de la función dentro del grupo (opcional)
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Orden de visualización en UI"
    )
    
    # Auditoría
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='function_group_additions'
    )
    
    class Meta:
        db_table = 'access_function_group_memberships'
        unique_together = [['group', 'function']]
        ordering = ['group', 'order', 'function__code']
    
    def __str__(self):
        return f"{self.group.group_id} → {self.function.code}"
```

---

### 7.4 Modelo: UserFunctionAssignment

```python
from datetime import timedelta
from django.utils import timezone

class UserFunctionAssignment(models.Model):
    """
    Asignación de función a usuario.
    
    Puede ser permanente o temporal.
    Todas las asignaciones se auditan.
    """
    
    # Usuario y función
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='function_assignments'
    )
    
    function = models.ForeignKey(
        Function,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )
    
    # Temporal o permanente
    is_temporary = models.BooleanField(
        default=False,
        help_text="Si es permiso temporal con fecha de expiración"
    )
    
    # Vigencia
    valid_from = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha inicio de vigencia"
    )
    
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha fin de vigencia (solo si is_temporary=True)"
    )
    
    # Justificación (obligatoria si temporal)
    justification = models.TextField(
        null=True,
        blank=True,
        validators=[MinLengthValidator(20)],
        help_text="Justificación obligatoria para permisos temporales (mín 20 chars)"
    )
    
    # Aprobación
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='function_assignments_approved'
    )
    
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Creación
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='function_assignments_created'
    )
    
    # Revocación
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='function_assignments_revoked'
    )
    revoked_reason = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'access_user_function_assignments'
        unique_together = [['user', 'function']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['function']),
            models.Index(fields=['is_temporary']),
            models.Index(fields=['valid_until']),
        ]
        verbose_name = 'Asignación de Función'
        verbose_name_plural = 'Asignaciones de Funciones'
    
    def __str__(self):
        temp = " (TEMPORAL)" if self.is_temporary else ""
        return f"{self.user.username} → {self.function.code}{temp}"
    
    def clean(self):
        """Validaciones personalizadas."""
        from django.core.exceptions import ValidationError
        
        # 1. Justificación obligatoria si temporal
        if self.is_temporary and not self.justification:
            raise ValidationError({
                'justification': 'Justificación obligatoria para permisos temporales'
            })
        
        # 2. valid_until obligatorio si temporal
        if self.is_temporary and not self.valid_until:
            raise ValidationError({
                'valid_until': 'Fecha de expiración obligatoria para permisos temporales'
            })
        
        # 3. Duración máxima 6 meses (CNST-021)
        if self.is_temporary and self.valid_until:
            max_duration = timedelta(days=180)
            duration = self.valid_until - self.valid_from
            
            if duration > max_duration:
                raise ValidationError({
                    'valid_until': f'Duración máxima: 6 meses. Solicitado: {duration.days} días'
                })
        
        # 4. Validar que función sea asignable
        if not self.function.is_assignable():
            raise ValidationError({
                'function': f'Función {self.function.code} no está disponible para asignación '
                           f'(status: {self.function.status}, active: {self.function.is_active})'
            })
        
        # 5. Validar reglas SoD
        self._validate_sod_rules()
    
    def _validate_sod_rules(self):
        """Valida reglas de separación de funciones."""
        from django.core.exceptions import ValidationError
        from apps.access.services import SoDValidator
        
        validator = SoDValidator()
        conflicts = validator.check_conflicts(
            user=self.user,
            new_function=self.function
        )
        
        if conflicts:
            conflict_names = ', '.join([c['rule_name'] for c in conflicts])
            raise ValidationError({
                'function': f'Conflicto SoD detectado: {conflict_names}'
            })
    
    def is_active(self):
        """Verifica si la asignación está activa."""
        now = timezone.now()
        
        # Si fue revocada
        if self.revoked_at:
            return False
        
        # Si es temporal y expiró
        if self.is_temporary and self.valid_until:
            if now > self.valid_until:
                return False
        
        # Si aún no inicia
        if now < self.valid_from:
            return False
        
        return True
```

---

### 7.5 Modelo: UserFunctionGroupAssignment

```python
class UserFunctionGroupAssignment(models.Model):
    """
    Asignación de grupo de funciones a usuario.
    
    Al asignar un grupo, el usuario obtiene todas las funciones
    activas del grupo automáticamente.
    """
    
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='group_assignments'
    )
    
    group = models.ForeignKey(
        FunctionGroup,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )
    
    # Auditoría
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='group_assignments_created'
    )
    
    # Revocación
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='group_assignments_revoked'
    )
    
    class Meta:
        db_table = 'access_user_function_group_assignments'
        unique_together = [['user', 'group']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['group']),
        ]
    
    def __str__(self):
        return f"{self.user.username} → {self.group.group_id}"
    
    def is_active(self):
        """Verifica si la asignación está activa."""
        return self.revoked_at is None
```

---

### 7.6 Modelo: FunctionSeparationRule

```python
class FunctionSeparationRule(models.Model):
    """
    Regla de Separación de Funciones (SoD).
    
    Define qué funciones NO pueden ser asignadas al mismo usuario.
    """
    
    # Identificador de la regla
    rule_id = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="ID: access_audit_separation, user_audit_separation"
    )
    
    # Nombre descriptivo
    name = models.CharField(
        max_length=200,
        help_text="Nombre: Separación Acceso-Auditoría"
    )
    
    # Descripción de la regla
    description = models.TextField(
        help_text="Explicación del conflicto y por qué existe la regla"
    )
    
    # Grupo A de funciones conflictivas
    functions_group_a = models.ManyToManyField(
        Function,
        related_name='sod_rules_group_a',
        help_text="Primer grupo de funciones conflictivas"
    )
    
    # Grupo B de funciones conflictivas
    functions_group_b = models.ManyToManyField(
        Function,
        related_name='sod_rules_group_b',
        help_text="Segundo grupo de funciones conflictivas"
    )
    
    # Metadatos
    is_active = models.BooleanField(default=True)
    severity = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Crítica'),
            ('high', 'Alta'),
            ('medium', 'Media'),
        ],
        default='critical'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'access_function_separation_rules'
        verbose_name = 'Regla de Separación de Funciones'
        verbose_name_plural = 'Reglas de Separación de Funciones'
        ordering = ['rule_id']
    
    def __str__(self):
        return f"{self.rule_id} - {self.name}"
    
    def check_conflict(self, user_functions):
        """
        Verifica si existe conflicto SoD.
        
        Args:
            user_functions: QuerySet o lista de Functions del usuario
        
        Returns:
            bool: True si hay conflicto
        """
        user_func_set = set(user_functions)
        
        group_a_set = set(self.functions_group_a.all())
        group_b_set = set(self.functions_group_b.all())
        
        has_from_a = bool(user_func_set & group_a_set)
        has_from_b = bool(user_func_set & group_b_set)
        
        return has_from_a and has_from_b
```

---

<a name="8-sql"></a>

## 8. IMPLEMENTACIÓN SQL

### 8.1 Script de Creación de Tablas

```sql
-- ══════════════════════════════════════════════════════════
-- MODELO RBAC v6.0.0 - Creación de Tablas
-- ══════════════════════════════════════════════════════════

-- Tabla: Funciones
CREATE TABLE access_functions (
    permission_django VARCHAR(100) PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    module VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'activo',
    description TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_module (module),
    INDEX idx_status (status),
    INDEX idx_code (code),
    
    CONSTRAINT chk_status CHECK (status IN ('activo', 'planificado', 'deprecado'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: Grupos de Funciones
CREATE TABLE access_function_groups (
    group_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: Membresía Grupo-Función
CREATE TABLE access_function_group_memberships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id VARCHAR(20) NOT NULL,
    permission_django VARCHAR(100) NOT NULL,
    `order` SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    added_by_id INT NULL,
    
    FOREIGN KEY (group_id) REFERENCES access_function_groups(group_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_django) REFERENCES access_functions(permission_django) ON DELETE CASCADE,
    FOREIGN KEY (added_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    
    UNIQUE KEY unique_group_function (group_id, permission_django),
    INDEX idx_group (group_id),
    INDEX idx_function (permission_django)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: Asignaciones Usuario-Función
CREATE TABLE access_user_function_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permission_django VARCHAR(100) NOT NULL,
    is_temporary BOOLEAN NOT NULL DEFAULT FALSE,
    valid_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP NULL,
    justification TEXT NULL,
    approved_by_id INT NULL,
    approved_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_id INT NULL,
    revoked_at TIMESTAMP NULL,
    revoked_by_id INT NULL,
    revoked_reason TEXT NULL,
    
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_django) REFERENCES access_functions(permission_django) ON DELETE CASCADE,
    FOREIGN KEY (approved_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    FOREIGN KEY (revoked_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    
    UNIQUE KEY unique_user_function (user_id, permission_django),
    INDEX idx_user (user_id),
    INDEX idx_function (permission_django),
    INDEX idx_temporary (is_temporary),
    INDEX idx_valid_until (valid_until)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: Asignaciones Usuario-Grupo
CREATE TABLE access_user_function_group_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_id VARCHAR(20) NOT NULL,
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by_id INT NULL,
    revoked_at TIMESTAMP NULL,
    revoked_by_id INT NULL,
    
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES access_function_groups(group_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    FOREIGN KEY (revoked_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    
    UNIQUE KEY unique_user_group (user_id, group_id),
    INDEX idx_user (user_id),
    INDEX idx_group (group_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: Reglas de Separación de Funciones
CREATE TABLE access_function_separation_rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    severity VARCHAR(20) NOT NULL DEFAULT 'critical',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_severity CHECK (severity IN ('critical', 'high', 'medium'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla intermedia: SoD Grupo A
CREATE TABLE access_sod_rule_functions_a (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_id VARCHAR(50) NOT NULL,
    permission_django VARCHAR(100) NOT NULL,
    
    FOREIGN KEY (rule_id) REFERENCES access_function_separation_rules(rule_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_django) REFERENCES access_functions(permission_django) ON DELETE CASCADE,
    
    UNIQUE KEY unique_rule_function_a (rule_id, permission_django)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla intermedia: SoD Grupo B
CREATE TABLE access_sod_rule_functions_b (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_id VARCHAR(50) NOT NULL,
    permission_django VARCHAR(100) NOT NULL,
    
    FOREIGN KEY (rule_id) REFERENCES access_function_separation_rules(rule_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_django) REFERENCES access_functions(permission_django) ON DELETE CASCADE,
    
    UNIQUE KEY unique_rule_function_b (rule_id, permission_django)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 8.2 Script de Inserción - 46 Funciones

```sql
-- ══════════════════════════════════════════════════════════
-- INSERCIÓN DE 46 FUNCIONES v6.0.0
-- ══════════════════════════════════════════════════════════

-- MOD_Auth (4 funciones)
INSERT INTO access_functions (code, permission_django, display_name, module, status, description) VALUES
('AUTH_LOGIN', 'auth.login', 'Iniciar Sesión', 'auth', 'activo', 'Inicia sesión en el sistema. UC_001'),
('AUTH_LOGOUT', 'auth.logout', 'Cerrar Sesión', 'auth', 'activo', 'Cierra sesión activa. UC_002'),
('AUTH_RECOVER', 'auth.recover_password', 'Recuperar Contraseña', 'auth', 'activo', 'Recupera contraseña con 3 preguntas seguridad. UC_003, CNST-001'),
('AUTH_SESSIONS', 'auth.manage_sessions', 'Gestionar Sesiones', 'auth', 'activo', 'Gestiona sesiones activas del sistema. UC_004');

-- MOD_Users (9 funciones)
INSERT INTO access_functions (code, permission_django, display_name, module, status, description) VALUES
('USR_VIEW', 'users.view_user', 'Ver Usuarios', 'users', 'activo', 'Ve lista de usuarios. UC_005'),
('USR_CREATE', 'users.add_user', 'Crear Usuarios', 'users', 'activo', 'Crea nuevos usuarios. UC_006, CNST-005'),
('USR_EDIT', 'users.change_user', 'Editar Usuarios', 'users', 'activo', 'Edita información de usuarios. UC_006'),
('USR_DELETE', 'users.delete_user', 'Eliminar Usuarios', 'users', 'activo', 'Elimina usuarios (soft delete). UC_006'),
('USR_PASS', 'users.change_password', 'Cambiar Contraseña', 'users', 'activo', 'Cambia contraseña propia. UC_007'),
('USR_RESET', 'users.reset_password', 'Resetear Contraseña', 'users', 'activo', 'Resetea contraseña de otro usuario. UC_008'),
('USR_LOCK', 'users.lock_user', 'Bloquear Usuario', 'users', 'activo', 'Bloquea usuario. UC_009, CNST-005'),
('USR_UNLOCK', 'users.unlock_user', 'Desbloquear Usuario', 'users', 'activo', 'Desbloquea usuario. UC_009'),
('USR_PROFILE', 'users.view_profile', 'Ver Perfil', 'users', 'activo', 'Ve perfil de usuario. UC_010');

-- MOD_Access (5 funciones)
INSERT INTO access_functions (code, permission_django, display_name, module, status, description) VALUES
('ACC_ASSIGN', 'access.assign_functions', 'Asignar Funciones', 'access', 'activo', 'Asigna funciones RBAC. UC_011, CNST-021'),
('ACC_REVOKE', 'access.revoke_functions', 'Revocar Funciones', 'access', 'activo', 'Revoca funciones. UC_012, CNST-021'),
('ACC_VIEW_PERM', 'access.view_permissions', 'Ver Permisos', 'access', 'activo', 'Ve permisos asignados. UC_013'),
('ACC_GROUPS', 'access.manage_groups', 'Gestionar Grupos', 'access', 'activo', 'Gestiona grupos de funciones. UC_014'),
('ACC_SOD', 'access.view_separation', 'Ver Reglas SoD', 'access', 'activo', 'Ve reglas de separación. UC_015, CNST-021');

-- MOD_Pipeline (4 funciones)
INSERT INTO access_functions (code, permission_django, display_name, module, status, description) VALUES
('PIP_VIEW', 'pipeline.view_job', 'Ver Jobs ETL', 'pipeline', 'activo', 'Ve estado de jobs ETL. UC_016, CNST-019'),
('PIP_EXEC', 'pipeline.execute_job', 'Ejecutar Jobs', 'pipeline', 'activo', 'Ejecuta jobs ETL manualmente. UC_035'),
('PIP_STOP', 'pipeline.stop_job', 'Detener Jobs', 'pipeline', 'activo', 'Detiene jobs en ejecución. UC_036'),
('PIP_LOGS', 'pipeline.view_logs', 'Ver Logs Jobs', 'pipeline', 'activo', 'Ve logs de ejecución ETL. UC_016');

-- MOD_Reports (6 funciones: 5 activas + 1 planificada)
INSERT INTO access_functions (code, permission_django, display_name, module, status, description) VALUES
('RPT_VIEW', 'reports.view', 'Ver Reportes', 'reports', 'activo', 'Ve reportes tabulares. UC_017, UC_018, UC_019'),
('RPT_CREATE', 'reports.create', 'Crear Reporte', 'reports', 'activo', 'Crea configuración de reporte. UC_017'),
('RPT_DELETE', 'reports.delete', 'Eliminar Reporte', 'reports', 'activo', 'Elimina reportes antiguos'),
('RPT_EXP_CSV', 'reports.export.csv', 'Exportar CSV', 'reports', 'activo', 'Exporta a CSV (100K límite). UC_022, CNST-007'),
('RPT_EXP_EXCEL', 'reports.export.excel', 'Exportar Excel', 'reports', 'activo', 'Exporta a Excel (50K límite). UC_023, CNST-007'),
('RPT_EXP_PDF', 'reports.export.pdf', 'Exportar PDF', 'reports', 'planificado', 'Exporta a PDF (10K límite). UC_024, CNST-007. Funcionalidad planificada');

-- MOD_Dashboard (6 funciones: 3 activas + 3 planificadas)
INSERT INTO access_functions (code, permission_django, display_name, module, status, description) VALUES
('DSH_VIEW', 'dashboard.view', 'Ver Dashboard', 'dashboard', 'activo', 'Ve dashboards con widgets. UC_025, CNST-023'),
('DSH_EXP_CSV', 'dashboard.export.csv', 'Exportar Dashboard CSV', 'dashboard', 'activo', 'Exporta snapshot a CSV'),
('DSH_EXP_EXCEL', 'dashboard.export.excel', 'Exportar Dashboard Excel', 'dashboard', 'activo', 'Exporta snapshot a Excel'),
('DSH_EXP_PDF', 'dashboard.export.pdf', 'Exportar Dashboard PDF', 'dashboard', 'planificado', 'Exporta snapshot a PDF. Funcionalidad planificada'),
('DSH_SHARE', 'dashboard.share', 'Compartir Dashboard', 'dashboard', 'planificado', 'Comparte dashboard con otros usuarios. Funcionalidad planificada'),
('DSH_EDIT', 'dashboard.edit', 'Editar Dashboard', 'dashboard', 'planificado', 'Edita configuración de widgets. Funcionalidad planificada');

-- MOD_Alerts (6 funciones)
INSERT INTO access_functions (code, permission_django, display_name, module, status, description) VALUES
('ALR_VIEW', 'alerts.view_alert', 'Ver Alertas', 'alerts', 'activo', 'Ve alertas del buzón interno. UC_030, CNST-001'),
('ALR_CONF', 'alerts.configure_alert', 'Configurar Alerta', 'alerts', 'activo', 'Configura alertas automáticas. UC_031'),
('ALR_SEND', 'alerts.send_alert', 'Enviar Alerta', 'alerts', 'activo', 'Envía alertas (máx 50 dest). UC_032, CNST-024'),
('ALR_SUBS', 'alerts.manage_subscriptions', 'Gestionar Suscripciones', 'alerts', 'activo', 'Gestiona suscripciones a alertas. UC_033'),
('ALR_MARK', 'alerts.mark_read', 'Marcar Leída', 'alerts', 'activo', 'Marca alerta como leída. UC_034'),
('ALR_DELETE', 'alerts.delete_alert', 'Eliminar Alerta', 'alerts', 'activo', 'Elimina alertas antiguas. UC_037');

-- MOD_Audit (4 funciones)
INSERT INTO access_functions (code, permission_django, display_name, module, status, description) VALUES
('AUD_VIEW', 'audit.view_log', 'Ver Auditoría', 'audit', 'activo', 'Ve logs de auditoría. UC_038, CNST-031'),
('AUD_SEARCH', 'audit.search_log', 'Buscar Auditoría', 'audit', 'activo', 'Busca eventos en auditoría. UC_039'),
('AUD_EXP', 'audit.export_log', 'Exportar Auditoría', 'audit', 'activo', 'Exporta logs de auditoría. UC_040'),
('AUD_COMPLIANCE', 'audit.generate_compliance', 'Generar Compliance', 'audit', 'activo', 'Genera reporte de cumplimiento. UC_049, CNST-031');

-- MOD_Logs (2 funciones)
INSERT INTO access_functions (code, permission_django, display_name, module, status, description) VALUES
('LOG_VIEW', 'logs.view_technical', 'Ver Logs Técnicos', 'logs', 'activo', 'Ve logs técnicos. UC_041, CNST-030'),
('LOG_EXP', 'logs.export_logs', 'Exportar Logs', 'logs', 'activo', 'Exporta logs técnicos. UC_042');

-- Marcar funciones planificadas como inactivas
UPDATE access_functions 
SET is_active = FALSE 
WHERE status = 'planificado';
```

---

### 8.3 Script de Inserción - 10 Grupos

```sql
-- ══════════════════════════════════════════════════════════
-- INSERCIÓN DE 10 GRUPOS DE FUNCIONES v6.0.0
-- ══════════════════════════════════════════════════════════

INSERT INTO access_function_groups (group_id, name, description) VALUES
('AGR-001', 'Operador Básico', 'Usuario con acceso mínimo: consultar reportes, ver dashboards, revisar alertas'),
('AGR-002', 'Analista Junior', 'Analista con capacidad de generar y exportar reportes a CSV'),
('AGR-003', 'Analista Senior', 'Analista con acceso completo a reportes y dashboards, múltiples formatos export'),
('AGR-004', 'Administrador de Usuarios', 'Gestión completa de usuarios (CRUD)'),
('AGR-005', 'Gestor de Acceso', 'Administración de permisos RBAC (asignar/revocar funciones)'),
('AGR-006', 'Auditor', 'Acceso readonly a auditoría y logs del sistema'),
('AGR-007', 'Supervisor Pipeline', 'Supervisión y control del proceso ETL'),
('AGR-008', 'Gestor de Alertas', 'Administración del sistema de alertas internas'),
('AGR-009', 'Soporte Técnico', 'Soporte de primer nivel (resetear contraseñas, desbloquear usuarios)'),
('AGR-010', 'Administrador Total', 'Acceso completo al sistema (todas las funciones activas)');

-- ══════════════════════════════════════════════════════════
-- ASIGNACIÓN DE FUNCIONES A GRUPOS
-- ══════════════════════════════════════════════════════════

-- AGR-001: Operador Básico (7 funciones)
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-001', 'auth.login', 1),
('AGR-001', 'auth.logout', 2),
('AGR-001', 'reports.view', 3),
('AGR-001', 'dashboard.view', 4),
('AGR-001', 'alerts.view_alert', 5),
('AGR-001', 'alerts.mark_read', 6),
('AGR-001', 'users.view_profile', 7);

-- AGR-002: Analista Junior (12 funciones)
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-002', 'auth.login', 1),
('AGR-002', 'auth.logout', 2),
('AGR-002', 'reports.view', 3),
('AGR-002', 'reports.create', 4),
('AGR-002', 'reports.export.csv', 5),
('AGR-002', 'dashboard.view', 6),
('AGR-002', 'dashboard.export.csv', 7),
('AGR-002', 'alerts.view_alert', 8),
('AGR-002', 'alerts.mark_read', 9),
('AGR-002', 'alerts.delete_alert', 10),
('AGR-002', 'users.view_profile', 11),
('AGR-002', 'users.change_password', 12);

-- AGR-003: Analista Senior (16 funciones)
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-003', 'auth.login', 1),
('AGR-003', 'auth.logout', 2),
('AGR-003', 'auth.recover_password', 3),
('AGR-003', 'reports.view', 4),
('AGR-003', 'reports.create', 5),
('AGR-003', 'reports.delete', 6),
('AGR-003', 'reports.export.csv', 7),
('AGR-003', 'reports.export.excel', 8),
('AGR-003', 'dashboard.view', 9),
('AGR-003', 'dashboard.export.csv', 10),
('AGR-003', 'dashboard.export.excel', 11),
('AGR-003', 'pipeline.view_job', 12),
('AGR-003', 'pipeline.view_logs', 13),
('AGR-003', 'alerts.view_alert', 14),
('AGR-003', 'alerts.mark_read', 15),
('AGR-003', 'alerts.delete_alert', 16),
('AGR-003', 'users.view_profile', 17),
('AGR-003', 'users.change_password', 18);

-- AGR-004: Administrador de Usuarios (14 funciones)
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-004', 'auth.login', 1),
('AGR-004', 'auth.logout', 2),
('AGR-004', 'auth.manage_sessions', 3),
('AGR-004', 'users.view_user', 4),
('AGR-004', 'users.add_user', 5),
('AGR-004', 'users.change_user', 6),
('AGR-004', 'users.delete_user', 7),
('AGR-004', 'users.reset_password', 8),
('AGR-004', 'users.lock_user', 9),
('AGR-004', 'users.unlock_user', 10),
('AGR-004', 'users.view_profile', 11),
('AGR-004', 'users.change_password', 12),
('AGR-004', 'access.view_permissions', 13),
('AGR-004', 'alerts.view_alert', 14),
('AGR-004', 'alerts.mark_read', 15);

-- AGR-005: Gestor de Acceso (10 funciones)
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-005', 'auth.login', 1),
('AGR-005', 'auth.logout', 2),
('AGR-005', 'access.assign_functions', 3),
('AGR-005', 'access.revoke_functions', 4),
('AGR-005', 'access.view_permissions', 5),
('AGR-005', 'access.manage_groups', 6),
('AGR-005', 'access.view_separation', 7),
('AGR-005', 'users.view_user', 8),
('AGR-005', 'users.view_profile', 9),
('AGR-005', 'alerts.view_alert', 10),
('AGR-005', 'alerts.mark_read', 11);

-- AGR-006: Auditor (10 funciones)
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-006', 'auth.login', 1),
('AGR-006', 'auth.logout', 2),
('AGR-006', 'audit.view_log', 3),
('AGR-006', 'audit.search_log', 4),
('AGR-006', 'audit.export_log', 5),
('AGR-006', 'audit.generate_compliance', 6),
('AGR-006', 'logs.view_technical', 7),
('AGR-006', 'logs.export_logs', 8),
('AGR-006', 'alerts.view_alert', 9),
('AGR-006', 'alerts.mark_read', 10);

-- AGR-007: Supervisor Pipeline (9 funciones)
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-007', 'auth.login', 1),
('AGR-007', 'auth.logout', 2),
('AGR-007', 'pipeline.view_job', 3),
('AGR-007', 'pipeline.execute_job', 4),
('AGR-007', 'pipeline.stop_job', 5),
('AGR-007', 'pipeline.view_logs', 6),
('AGR-007', 'alerts.view_alert', 7),
('AGR-007', 'alerts.configure_alert', 8),
('AGR-007', 'alerts.send_alert', 9),
('AGR-007', 'users.view_profile', 10);

-- AGR-008: Gestor de Alertas (10 funciones)
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-008', 'auth.login', 1),
('AGR-008', 'auth.logout', 2),
('AGR-008', 'alerts.view_alert', 3),
('AGR-008', 'alerts.configure_alert', 4),
('AGR-008', 'alerts.send_alert', 5),
('AGR-008', 'alerts.manage_subscriptions', 6),
('AGR-008', 'alerts.mark_read', 7),
('AGR-008', 'alerts.delete_alert', 8),
('AGR-008', 'users.view_user', 9),
('AGR-008', 'users.view_profile', 10),
('AGR-008', 'reports.view', 11);

-- AGR-009: Soporte Técnico (15 funciones)
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-009', 'auth.login', 1),
('AGR-009', 'auth.logout', 2),
('AGR-009', 'auth.recover_password', 3),
('AGR-009', 'auth.manage_sessions', 4),
('AGR-009', 'users.view_user', 5),
('AGR-009', 'users.reset_password', 6),
('AGR-009', 'users.lock_user', 7),
('AGR-009', 'users.unlock_user', 8),
('AGR-009', 'users.view_profile', 9),
('AGR-009', 'reports.view', 10),
('AGR-009', 'dashboard.view', 11),
('AGR-009', 'logs.view_technical', 12),
('AGR-009', 'alerts.view_alert', 13),
('AGR-009', 'alerts.mark_read', 14);

-- AGR-010: Administrador Total (42 funciones activas)
-- Incluye TODAS las funciones con status='activo'
INSERT INTO access_function_group_memberships (group_id, permission_django)
SELECT 'AGR-010', permission_django
FROM access_functions
WHERE status = 'activo' AND is_active = TRUE;
```

---

### 8.4 Script de Inserción - 3 Reglas SoD

```sql
-- ══════════════════════════════════════════════════════════
-- INSERCIÓN DE REGLAS DE SEPARACIÓN DE FUNCIONES (SoD)
-- ══════════════════════════════════════════════════════════

INSERT INTO access_function_separation_rules (rule_id, name, description, severity) VALUES
('access_audit_separation', 
 'Separación Acceso-Auditoría',
 'Quien gestiona permisos NO debe ver auditoría de sus propias acciones',
 'critical'),

('user_audit_separation',
 'Separación Usuarios-Auditoría',
 'Quien gestiona usuarios NO debe ver auditoría de sus propias acciones',
 'critical'),

('pipeline_audit_separation',
 'Separación Pipeline-Auditoría',
 'Quien controla ETL NO debe auditar su propia ejecución',
 'critical');

-- Regla 1: access_audit_separation
-- Grupo A: Funciones de gestión de acceso
INSERT INTO access_sod_rule_functions_a (rule_id, permission_django) VALUES
('access_audit_separation', 'access.assign_functions'),
('access_audit_separation', 'access.revoke_functions'),
('access_audit_separation', 'access.manage_groups');

-- Grupo B: Funciones de auditoría
INSERT INTO access_sod_rule_functions_b (rule_id, permission_django) VALUES
('access_audit_separation', 'audit.view_log'),
('access_audit_separation', 'audit.search_log'),
('access_audit_separation', 'audit.export_log');

-- Regla 2: user_audit_separation
-- Grupo A: Funciones de gestión de usuarios
INSERT INTO access_sod_rule_functions_a (rule_id, permission_django) VALUES
('user_audit_separation', 'users.add_user'),
('user_audit_separation', 'users.change_user'),
('user_audit_separation', 'users.delete_user'),
('user_audit_separation', 'users.reset_password');

-- Grupo B: Funciones de auditoría
INSERT INTO access_sod_rule_functions_b (rule_id, permission_django) VALUES
('user_audit_separation', 'audit.view_log'),
('user_audit_separation', 'audit.search_log');

-- Regla 3: pipeline_audit_separation
-- Grupo A: Funciones de control de pipeline
INSERT INTO access_sod_rule_functions_a (rule_id, permission_django) VALUES
('pipeline_audit_separation', 'pipeline.execute_job'),
('pipeline_audit_separation', 'pipeline.stop_job');

-- Grupo B: Funciones de auditoría
INSERT INTO access_sod_rule_functions_b (rule_id, permission_django) VALUES
('pipeline_audit_separation', 'audit.view_log'),
('pipeline_audit_separation', 'audit.generate_compliance');
```

---

<a name="9-django"></a>

## 9. IMPLEMENTACIÓN DJANGO/DRF

### 9.1 Extension del Modelo User

```python
# apps/access/models.py (continuación)

from django.contrib.auth.models import User

# Extender User con métodos RBAC
class UserRBACMixin:
    """Mixin para agregar funcionalidad RBAC a User."""
    
    def has_function(self, permission_django):
        """
        Verifica si usuario tiene una función específica.
        
        Args:
            permission_django: str - 'reports.view', 'dashboard.export.csv'
        
        Returns:
            bool
        """
        # Superuser siempre tiene acceso
        if self.is_superuser:
            return True
        
        # Verificar en asignaciones directas activas
        direct = UserFunctionAssignment.objects.filter(
            user=self,
            function__permission_django=permission_django,
            function__is_active=True,
            revoked_at__isnull=True
        ).exists()
        
        if direct:
            # Verificar que no haya expirado si es temporal
            assignment = UserFunctionAssignment.objects.get(
                user=self,
                function__permission_django=permission_django
            )
            return assignment.is_active()
        
        # Verificar en grupos activos
        group_functions = Function.objects.filter(
            groups__user_assignments__user=self,
            groups__user_assignments__revoked_at__isnull=True,
            permission_django=permission_django,
            is_active=True
        )
        
        return group_functions.exists()
    
    def get_all_functions(self):
        """
        Obtiene todas las funciones activas del usuario.
        
        Returns:
            QuerySet[Function]
        """
        if self.is_superuser:
            return Function.objects.filter(
                status=FunctionStatus.ACTIVO,
                is_active=True
            )
        
        # Funciones directas activas
        direct_functions = Function.objects.filter(
            user_assignments__user=self,
            user_assignments__revoked_at__isnull=True,
            is_active=True
        ).distinct()
        
        # Filtrar las temporales expiradas
        valid_direct = []
        for func in direct_functions:
            assignment = func.user_assignments.get(user=self)
            if assignment.is_active():
                valid_direct.append(func.permission_django)
        
        # Funciones de grupos activos
        group_functions = Function.objects.filter(
            groups__user_assignments__user=self,
            groups__user_assignments__revoked_at__isnull=True,
            is_active=True
        ).distinct()
        
        # Combinar y eliminar duplicados
        all_functions = Function.objects.filter(
            models.Q(permission_django__in=valid_direct) |
            models.Q(pk__in=group_functions)
        ).distinct()
        
        return all_functions

# Inyectar métodos en User
User.add_to_class('has_function', UserRBACMixin.has_function)
User.add_to_class('get_all_functions', UserRBACMixin.get_all_functions)
```

---

### 9.2 Decoradores para Vistas

```python
# apps/access/decorators.py

from functools import wraps
from django.core.exceptions import PermissionDenied
from apps.audit.services import AuditService

def require_function(*permission_djangos):
    """
    Decorador que requiere una o más funciones RBAC.
    
    Usage:
        @require_function('reports.view')
        def list_reports(request):
            pass
        
        @require_function('reports.export.csv', 'reports.export.excel')
        def export_report(request):
            pass
    
    Args:
        *permission_djangos: Uno o más permission_django requeridos
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            user = request.user
            
            # Verificar autenticación
            if not user.is_authenticated:
                AuditService.log_access_denied(
                    user=None,
                    function=permission_djangos[0],
                    reason="Usuario no autenticado"
                )
                raise PermissionDenied("Debe iniciar sesión")
            
            # Superuser siempre puede
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar cada permiso requerido
            for perm in permission_djangos:
                if not user.has_function(perm):
                    # Auditar acceso denegado
                    AuditService.log_access_denied(
                        user=user,
                        function=perm,
                        reason="Función no asignada"
                    )
                    raise PermissionDenied(
                        f"No tiene permiso para: {perm}"
                    )
            
            # Auditar acceso exitoso
            AuditService.log_access_granted(
                user=user,
                function=permission_djangos[0],
                view=view_func.__name__
            )
            
            return view_func(request, *args, **kwargs)
        
        return wrapped
    return decorator
```

---

### 9.3 Permissions Classes para DRF

```python
# apps/access/permissions.py

from rest_framework.permissions import BasePermission
from apps.audit.services import AuditService

class HasFunction(BasePermission):
    """
    Permission class para DRF que verifica funciones RBAC.
    
    Usage en ViewSet:
        class ReportViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, HasFunction]
            required_function = 'reports.view'
    """
    
    def has_permission(self, request, view):
        """Verifica permiso a nivel de vista."""
        # Obtener función requerida del view
        required_function = getattr(view, 'required_function', None)
        
        if not required_function:
            # Si no hay required_function, denegar
            return False
        
        # Usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser siempre puede
        if request.user.is_superuser:
            return True
        
        # Verificar función RBAC
        has_perm = request.user.has_function(required_function)
        
        # Auditar
        if has_perm:
            AuditService.log_access_granted(
                user=request.user,
                function=required_function,
                view=view.__class__.__name__
            )
        else:
            AuditService.log_access_denied(
                user=request.user,
                function=required_function,
                reason="Función no asignada"
            )
        
        return has_perm


class HasAnyFunction(BasePermission):
    """
    Permission class que verifica si usuario tiene AL MENOS UNA
    de las funciones especificadas.
    
    Usage:
        class ReportViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, HasAnyFunction]
            required_functions = ['reports.view', 'reports.create']
    """
    
    def has_permission(self, request, view):
        """Verifica permiso con ANY logic."""
        required_functions = getattr(view, 'required_functions', [])
        
        if not required_functions:
            return False
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Verificar si tiene ALGUNA de las funciones
        for func in required_functions:
            if request.user.has_function(func):
                AuditService.log_access_granted(
                    user=request.user,
                    function=func,
                    view=view.__class__.__name__
                )
                return True
        
        # No tiene ninguna
        AuditService.log_access_denied(
            user=request.user,
            function=', '.join(required_functions),
            reason="No tiene ninguna de las funciones requeridas"
        )
        return False


class DynamicFunctionPermission(BasePermission):
    """
    Permission class que mapea acciones DRF a funciones RBAC.
    
    Usage:
        class ReportViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, DynamicFunctionPermission]
            function_map = {
                'list': 'reports.view',
                'retrieve': 'reports.view',
                'create': 'reports.create',
                'export_csv': 'reports.export.csv',
            }
    """
    
    def has_permission(self, request, view):
        """Mapea acción a función requerida."""
        function_map = getattr(view, 'function_map', {})
        action = view.action
        
        required_function = function_map.get(action)
        
        if not required_function:
            # Acción no mapeada = denegar
            return False
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        has_perm = request.user.has_function(required_function)
        
        if has_perm:
            AuditService.log_access_granted(
                user=request.user,
                function=required_function,
                view=f"{view.__class__.__name__}.{action}"
            )
        else:
            AuditService.log_access_denied(
                user=request.user,
                function=required_function,
                reason=f"Acción {action} no permitida"
            )
        
        return has_perm
```

---

### 9.4 Ejemplos de Uso en ViewSets

```python
# apps/reports/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.access.permissions import DynamicFunctionPermission

class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet para reportes con permisos RBAC dinámicos.
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    # Mapeo de acciones a funciones RBAC
    function_map = {
        'list': 'reports.view',
        'retrieve': 'reports.view',
        'create': 'reports.create',
        'destroy': 'reports.delete',
    }
    
    def list(self, request):
        """Lista reportes disponibles."""
        # DynamicFunctionPermission ya verificó 'reports.view'
        reports = Report.objects.filter(user=request.user)
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def export_csv(self, request, pk=None):
        """Exporta reporte a CSV."""
        # Necesitamos verificar permiso específico
        if not request.user.has_function('reports.export.csv'):
            raise PermissionDenied("No tiene permiso para exportar CSV")
        
        report = self.get_object()
        # ... lógica exportación
        return Response({'status': 'success'})


# apps/dashboard/views.py

from apps.access.decorators import require_function

class DashboardView(APIView):
    """Vista para dashboards con decorador."""
    
    @require_function('dashboard.view')
    def get(self, request, dashboard_type):
        """Obtiene datos del dashboard."""
        data = DashboardService.get_dashboard(dashboard_type)
        return Response(data)
    
    @require_function('dashboard.export.excel')
    def post(self, request, dashboard_type):
        """Exporta snapshot del dashboard."""
        file_url = DashboardService.export_snapshot(
            dashboard_type,
            format='excel'
        )
        return Response({'file_url': file_url})
```

---

<a name="10-mapeo-uc"></a>

## 10. MAPEO FUNCIONES → CASOS DE USO

### 10.1 Tabla Completa de Mapeo

| permission_django | code | use_cases | description_uc |
|-------------------|------|-----------|----------------|
| `auth.login` | AUTH_LOGIN | UC_001 | Iniciar Sesión en el Sistema |
| `auth.logout` | AUTH_LOGOUT | UC_002 | Cerrar Sesión Activa |
| `auth.recover_password` | AUTH_RECOVER | UC_003 | Recuperar Contraseña con Preguntas |
| `auth.manage_sessions` | AUTH_SESSIONS | UC_004 | Gestionar Sesiones Activas |
| `users.view_user` | USR_VIEW | UC_005 | Listar Usuarios del Sistema |
| `users.add_user` | USR_CREATE | UC_006 | Crear Nuevo Usuario |
| `users.change_user` | USR_EDIT | UC_006 | Editar Usuario Existente |
| `users.delete_user` | USR_DELETE | UC_006 | Eliminar Usuario |
| `users.change_password` | USR_PASS | UC_007 | Cambiar Contraseña Propia |
| `users.reset_password` | USR_RESET | UC_008 | Resetear Contraseña de Otro |
| `users.lock_user` | USR_LOCK | UC_009 | Bloquear Usuario |
| `users.unlock_user` | USR_UNLOCK | UC_009 | Desbloquear Usuario |
| `users.view_profile` | USR_PROFILE | UC_010 | Ver Perfil de Usuario |
| `access.assign_functions` | ACC_ASSIGN | UC_011 | Asignar Funciones a Usuario |
| `access.revoke_functions` | ACC_REVOKE | UC_012 | Revocar Funciones de Usuario |
| `access.view_permissions` | ACC_VIEW_PERM | UC_013 | Ver Permisos Asignados |
| `access.manage_groups` | ACC_GROUPS | UC_014 | Gestionar Grupos de Funciones |
| `access.view_separation` | ACC_SOD | UC_015 | Ver Reglas de Separación |
| `pipeline.view_job` | PIP_VIEW | UC_016 | Ver Estado del Pipeline ETL |
| `pipeline.execute_job` | PIP_EXEC | UC_035 | Ejecutar Pipeline Manualmente |
| `pipeline.stop_job` | PIP_STOP | UC_036 | Detener Ejecución del Pipeline |
| `pipeline.view_logs` | PIP_LOGS | UC_016 | Ver Logs de Ejecución ETL |
| `reports.view` | RPT_VIEW | UC_017, UC_018, UC_019 | Ver Reportes: Abandonadas, Clientes, Performance |
| `reports.create` | RPT_CREATE | UC_017 | Generar Nuevo Reporte |
| `reports.delete` | RPT_DELETE | - | Eliminar Reportes Antiguos |
| `reports.export.csv` | RPT_EXP_CSV | UC_022 | Exportar Reporte a CSV |
| `reports.export.excel` | RPT_EXP_EXCEL | UC_023 | Exportar Reporte a Excel |
| `reports.export.pdf` | RPT_EXP_PDF | UC_024 | Exportar Reporte a PDF (planificado) |
| `dashboard.view` | DSH_VIEW | UC_025 | Visualizar Dashboard de Métricas |
| `dashboard.export.csv` | DSH_EXP_CSV | - | Exportar Snapshot Dashboard CSV |
| `dashboard.export.excel` | DSH_EXP_EXCEL | - | Exportar Snapshot Dashboard Excel |
| `dashboard.export.pdf` | DSH_EXP_PDF | - | Exportar Snapshot Dashboard PDF (planificado) |
| `dashboard.share` | DSH_SHARE | - | Compartir Dashboard (planificado) |
| `dashboard.edit` | DSH_EDIT | - | Editar Configuración Dashboard (planificado) |
| `alerts.view_alert` | ALR_VIEW | UC_030 | Ver Alertas Recibidas |
| `alerts.configure_alert` | ALR_CONF | UC_031 | Configurar Alerta Automática |
| `alerts.send_alert` | ALR_SEND | UC_032 | Enviar Alerta Manual |
| `alerts.manage_subscriptions` | ALR_SUBS | UC_033 | Gestionar Suscripciones a Alertas |
| `alerts.mark_read` | ALR_MARK | UC_034 | Marcar Alerta como Leída |
| `alerts.delete_alert` | ALR_DELETE | UC_037 | Eliminar Alertas Antiguas |
| `audit.view_log` | AUD_VIEW | UC_038 | Consultar Log de Auditoría |
| `audit.search_log` | AUD_SEARCH | UC_039 | Buscar Eventos en Auditoría |
| `audit.export_log` | AUD_EXP | UC_040 | Exportar Log de Auditoría |
| `audit.generate_compliance` | AUD_COMPLIANCE | UC_049 | Generar Reporte de Cumplimiento |
| `logs.view_technical` | LOG_VIEW | UC_041 | Ver Logs Técnicos del Sistema |
| `logs.export_logs` | LOG_EXP | UC_042 | Exportar Logs Técnicos |

---

### 10.2 Mapeo Inverso: UC → Funciones

| Caso de Uso | Funciones Requeridas |
|-------------|---------------------|
| UC_001: Iniciar Sesión | AUTH_LOGIN |
| UC_002: Cerrar Sesión | AUTH_LOGOUT |
| UC_003: Recuperar Contraseña | AUTH_RECOVER |
| UC_004: Gestionar Sesiones | AUTH_SESSIONS |
| UC_005: Listar Usuarios | USR_VIEW |
| UC_006: Gestionar Usuarios (CRUD) | USR_VIEW + USR_CREATE + USR_EDIT + USR_DELETE |
| UC_007: Cambiar Contraseña Propia | USR_PASS |
| UC_008: Resetear Contraseña | USR_RESET |
| UC_009: Bloquear/Desbloquear Usuario | USR_LOCK + USR_UNLOCK |
| UC_010: Ver Perfil | USR_PROFILE |
| UC_011: Asignar Funciones | ACC_ASSIGN |
| UC_012: Revocar Funciones | ACC_REVOKE |
| UC_013: Ver Permisos | ACC_VIEW_PERM |
| UC_014: Gestionar Grupos | ACC_GROUPS |
| UC_015: Ver Reglas SoD | ACC_SOD |
| UC_016: Consultar Pipeline ETL | PIP_VIEW + PIP_LOGS |
| UC_017: Generar Reporte Llamadas Abandonadas | RPT_VIEW + RPT_CREATE |
| UC_018: Generar Reporte Análisis Clientes | RPT_VIEW + RPT_CREATE |
| UC_019: Generar Reporte Performance IVR | RPT_VIEW + RPT_CREATE |
| UC_020: Aplicar Filtros a Reportes | RPT_VIEW |
| UC_021: Filtrar por Período | RPT_VIEW |
| UC_022: Exportar Reporte a CSV | RPT_EXP_CSV |
| UC_023: Exportar Reporte a Excel | RPT_EXP_EXCEL |
| UC_024: Exportar Reporte a PDF | RPT_EXP_PDF (planificado) |
| UC_025: Visualizar Dashboard | DSH_VIEW |
| UC_027: Ver Gráfico de Barras | DSH_VIEW |
| UC_028: Ver Gráfico de Líneas | DSH_VIEW |
| UC_029: Ver Gráfico de Torta | DSH_VIEW |
| UC_030: Ver Alertas | ALR_VIEW |
| UC_031: Configurar Alerta | ALR_CONF |
| UC_032: Enviar Alerta | ALR_SEND |
| UC_033: Gestionar Suscripciones | ALR_SUBS |
| UC_034: Marcar Alerta Leída | ALR_MARK |
| UC_035: Ejecutar Pipeline Manual | PIP_EXEC |
| UC_036: Detener Pipeline | PIP_STOP |
| UC_037: Eliminar Alertas | ALR_DELETE |
| UC_038: Consultar Auditoría | AUD_VIEW |
| UC_039: Buscar en Auditoría | AUD_SEARCH |
| UC_040: Exportar Auditoría | AUD_EXP |
| UC_041: Ver Logs Técnicos | LOG_VIEW |
| UC_042: Exportar Logs | LOG_EXP |
| UC_049: Generar Compliance | AUD_COMPLIANCE |

---

<a name="11-migracion-v51"></a>

## 11. MIGRACIÓN DESDE v5.1

### 11.1 Cambios v5.1 → v5.2 (Histórico)

**Cambio principal:** Nomenclatura función_id de español a inglés (namespace style).

```sql
-- Migración v5.1 → v5.2 (ya aplicada)
UPDATE access_functions 
SET function_id = 'reports.view' 
WHERE function_id = 've_reportes';

UPDATE access_functions 
SET function_id = 'reports.export.csv' 
WHERE function_id = 'exporta_csv';

-- etc...
```

**Nota:** Esta migración ya fue documentada en v5.2.0 y no se repite en v6.0.0.

---

<a name="12-migracion-v60"></a>

## 12. MIGRACIÓN v5.2 → v6.0.0

### 12.1 Cambios Principales

```yaml
1. Separación MOD_Dashboard:
   - MOD_Reports: 8 → 6 funciones
   - MOD_Dashboard: 0 → 6 funciones (nuevo)

2. Nuevas funciones agregadas:
   + RPT_CREATE: reports.create
   + RPT_DELETE: reports.delete
   + DSH_EXP_CSV: dashboard.export.csv
   + DSH_EXP_EXCEL: dashboard.export.excel

3. Funciones eliminadas:
   - RPT_FILTER (integrado en RPT_VIEW)
   - RPT-002/007/008 (movidos a Dashboard)

4. Funciones planificadas:
   + RPT_EXP_PDF: reports.export.pdf
   + DSH_EXP_PDF: dashboard.export.pdf
   + DSH_SHARE: dashboard.share
   + DSH_EDIT: dashboard.edit

5. Modelo actualizado:
   + Columna: code (RPT_VIEW, DSH_EXP_CSV)
   + Columna: status (activo/planificado/deprecado)
   + PK: permission_django (antes: function_id)
```

---

### 12.2 Script de Migración SQL

```sql
-- ══════════════════════════════════════════════════════════
-- MIGRACIÓN v5.2 → v6.0.0
-- Fecha: 2026-01-19
-- ══════════════════════════════════════════════════════════

-- PASO 1: Agregar nuevas columnas
ALTER TABLE access_functions
ADD COLUMN code VARCHAR(30) AFTER function_id,
ADD COLUMN status VARCHAR(20) DEFAULT 'activo' AFTER module;

-- PASO 2: Poblar columna 'code' desde datos existentes
UPDATE access_functions SET code = 'AUTH_LOGIN' WHERE permission_django = 'auth.login';
UPDATE access_functions SET code = 'AUTH_LOGOUT' WHERE permission_django = 'auth.logout';
UPDATE access_functions SET code = 'AUTH_RECOVER' WHERE permission_django = 'auth.recover_password';
UPDATE access_functions SET code = 'AUTH_SESSIONS' WHERE permission_django = 'auth.manage_sessions';

UPDATE access_functions SET code = 'USR_VIEW' WHERE permission_django = 'users.view_user';
UPDATE access_functions SET code = 'USR_CREATE' WHERE permission_django = 'users.add_user';
UPDATE access_functions SET code = 'USR_EDIT' WHERE permission_django = 'users.change_user';
UPDATE access_functions SET code = 'USR_DELETE' WHERE permission_django = 'users.delete_user';
UPDATE access_functions SET code = 'USR_PASS' WHERE permission_django = 'users.change_password';
UPDATE access_functions SET code = 'USR_RESET' WHERE permission_django = 'users.reset_password';
UPDATE access_functions SET code = 'USR_LOCK' WHERE permission_django = 'users.lock_user';
UPDATE access_functions SET code = 'USR_UNLOCK' WHERE permission_django = 'users.unlock_user';
UPDATE access_functions SET code = 'USR_PROFILE' WHERE permission_django = 'users.view_profile';

UPDATE access_functions SET code = 'ACC_ASSIGN' WHERE permission_django = 'access.assign_functions';
UPDATE access_functions SET code = 'ACC_REVOKE' WHERE permission_django = 'access.revoke_functions';
UPDATE access_functions SET code = 'ACC_VIEW_PERM' WHERE permission_django = 'access.view_permissions';
UPDATE access_functions SET code = 'ACC_GROUPS' WHERE permission_django = 'access.manage_groups';
UPDATE access_functions SET code = 'ACC_SOD' WHERE permission_django = 'access.view_separation';

UPDATE access_functions SET code = 'PIP_VIEW' WHERE permission_django = 'pipeline.view_job';
UPDATE access_functions SET code = 'PIP_EXEC' WHERE permission_django = 'pipeline.execute_job';
UPDATE access_functions SET code = 'PIP_STOP' WHERE permission_django = 'pipeline.stop_job';
UPDATE access_functions SET code = 'PIP_LOGS' WHERE permission_django = 'pipeline.view_logs';

-- REPORTS: Actualizar códigos existentes
UPDATE access_functions SET code = 'RPT_VIEW' WHERE permission_django = 'reports.view';
UPDATE access_functions SET code = 'RPT_EXP_CSV' WHERE permission_django = 'reports.export.csv';
UPDATE access_functions SET code = 'RPT_EXP_EXCEL' WHERE permission_django = 'reports.export.excel';

UPDATE access_functions SET code = 'ALR_VIEW' WHERE permission_django = 'alerts.view_alert';
UPDATE access_functions SET code = 'ALR_CONF' WHERE permission_django = 'alerts.configure_alert';
UPDATE access_functions SET code = 'ALR_SEND' WHERE permission_django = 'alerts.send_alert';
UPDATE access_functions SET code = 'ALR_SUBS' WHERE permission_django = 'alerts.manage_subscriptions';
UPDATE access_functions SET code = 'ALR_MARK' WHERE permission_django = 'alerts.mark_read';
UPDATE access_functions SET code = 'ALR_DELETE' WHERE permission_django = 'alerts.delete_alert';

UPDATE access_functions SET code = 'AUD_VIEW' WHERE permission_django = 'audit.view_log';
UPDATE access_functions SET code = 'AUD_SEARCH' WHERE permission_django = 'audit.search_log';
UPDATE access_functions SET code = 'AUD_EXP' WHERE permission_django = 'audit.export_log';
UPDATE access_functions SET code = 'AUD_COMPLIANCE' WHERE permission_django = 'audit.generate_compliance';

UPDATE access_functions SET code = 'LOG_VIEW' WHERE permission_django = 'logs.view_technical';
UPDATE access_functions SET code = 'LOG_EXP' WHERE permission_django = 'logs.export_logs';

-- PASO 3: Hacer 'code' NOT NULL y UNIQUE
ALTER TABLE access_functions
MODIFY COLUMN code VARCHAR(30) NOT NULL,
ADD UNIQUE KEY unique_code (code);

-- PASO 4: Eliminar función RPT_FILTER (movida a RPT_VIEW)
DELETE FROM access_function_group_memberships 
WHERE permission_django = 'reports.filter';

DELETE FROM access_functions 
WHERE permission_django = 'reports.filter';

-- PASO 5: Insertar nuevas funciones ACTIVAS
INSERT INTO access_functions (code, permission_django, display_name, module, status, description, is_active) VALUES
('RPT_CREATE', 'reports.create', 'Crear Reporte', 'reports', 'activo', 'Crea configuración de reporte. UC_017', TRUE),
('RPT_DELETE', 'reports.delete', 'Eliminar Reporte', 'reports', 'activo', 'Elimina reportes antiguos', TRUE),
('DSH_VIEW', 'dashboard.view', 'Ver Dashboard', 'dashboard', 'activo', 'Ve dashboards con widgets. UC_025, CNST-023', TRUE),
('DSH_EXP_CSV', 'dashboard.export.csv', 'Exportar Dashboard CSV', 'dashboard', 'activo', 'Exporta snapshot a CSV', TRUE),
('DSH_EXP_EXCEL', 'dashboard.export.excel', 'Exportar Dashboard Excel', 'dashboard', 'activo', 'Exporta snapshot a Excel', TRUE);

-- PASO 6: Insertar nuevas funciones PLANIFICADAS
INSERT INTO access_functions (code, permission_django, display_name, module, status, description, is_active) VALUES
('RPT_EXP_PDF', 'reports.export.pdf', 'Exportar PDF', 'reports', 'planificado', 'Exporta a PDF (10K límite). UC_024, CNST-007. Planificado', FALSE),
('DSH_EXP_PDF', 'dashboard.export.pdf', 'Exportar Dashboard PDF', 'dashboard', 'planificado', 'Exporta snapshot a PDF. Planificado', FALSE),
('DSH_SHARE', 'dashboard.share', 'Compartir Dashboard', 'dashboard', 'planificado', 'Comparte dashboard. Planificado', FALSE),
('DSH_EDIT', 'dashboard.edit', 'Editar Dashboard', 'dashboard', 'planificado', 'Edita configuración de widgets. Planificado', FALSE);

-- PASO 7: Actualizar grupos afectados
-- AGR-001: Agregar DSH_VIEW
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`)
VALUES ('AGR-001', 'dashboard.view', 4);

-- AGR-002: Agregar RPT_CREATE y DSH_EXP_CSV
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-002', 'reports.create', 4),
('AGR-002', 'dashboard.export.csv', 7);

-- AGR-003: Agregar funciones Dashboard
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`) VALUES
('AGR-003', 'reports.create', 5),
('AGR-003', 'reports.delete', 6),
('AGR-003', 'dashboard.view', 9),
('AGR-003', 'dashboard.export.csv', 10),
('AGR-003', 'dashboard.export.excel', 11);

-- AGR-009: Agregar DSH_VIEW
INSERT INTO access_function_group_memberships (group_id, permission_django, `order`)
VALUES ('AGR-009', 'dashboard.view', 11);

-- AGR-010: Regenerar con todas las activas
DELETE FROM access_function_group_memberships WHERE group_id = 'AGR-010';
INSERT INTO access_function_group_memberships (group_id, permission_django)
SELECT 'AGR-010', permission_django
FROM access_functions
WHERE status = 'activo' AND is_active = TRUE;

-- PASO 8: Agregar índices para status
CREATE INDEX idx_status ON access_functions(status);

-- PASO 9: Validar integridad
SELECT 
    'Total funciones' AS check_type,
    COUNT(*) AS count
FROM access_functions
UNION ALL
SELECT 
    'Funciones activas',
    COUNT(*)
FROM access_functions
WHERE status = 'activo'
UNION ALL
SELECT 
    'Funciones planificadas',
    COUNT(*)
FROM access_functions
WHERE status = 'planificado';

-- Resultado esperado:
-- Total funciones: 46
-- Funciones activas: 42
-- Funciones planificadas: 4
```

---

### 12.3 Migración Django

```python
# apps/access/migrations/0002_v6_0_0_migration.py

from django.db import migrations, models

class Migration(migrations.Migration):
    """
    Migración v5.2 → v6.0.0
    
    Cambios:
    - Agregar campo 'code'
    - Agregar campo 'status'
    - Separar MOD_Dashboard
    - Agregar funciones planificadas
    """
    
    dependencies = [
        ('access', '0001_initial'),
    ]
    
    operations = [
        # 1. Agregar campo code
        migrations.AddField(
            model_name='function',
            name='code',
            field=models.CharField(
                max_length=30,
                null=True,  # Temporalmente nullable
                help_text="Código: RPT_VIEW, DSH_EXP_CSV"
            ),
        ),
        
        # 2. Agregar campo status
        migrations.AddField(
            model_name='function',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('activo', 'Activo'),
                    ('planificado', 'Planificado'),
                    ('deprecado', 'Deprecado'),
                ],
                default='activo'
            ),
        ),
        
        # 3. Poblar campo code (data migration)
        migrations.RunPython(populate_code_field),
        
        # 4. Hacer code NOT NULL y UNIQUE
        migrations.AlterField(
            model_name='function',
            name='code',
            field=models.CharField(
                max_length=30,
                unique=True,
                help_text="Código: RPT_VIEW, DSH_EXP_CSV"
            ),
        ),
        
        # 5. Agregar nuevas funciones
        migrations.RunPython(add_new_functions_v6),
        
        # 6. Eliminar función obsoleta
        migrations.RunPython(remove_filter_function),
        
        # 7. Actualizar grupos
        migrations.RunPython(update_groups_v6),
        
        # 8. Agregar índice
        migrations.AddIndex(
            model_name='function',
            index=models.Index(fields=['status'], name='idx_status'),
        ),
    ]

def populate_code_field(apps, schema_editor):
    """Pobla el campo code desde permission_django."""
    Function = apps.get_model('access', 'Function')
    
    code_mapping = {
        'auth.login': 'AUTH_LOGIN',
        'auth.logout': 'AUTH_LOGOUT',
        'auth.recover_password': 'AUTH_RECOVER',
        'auth.manage_sessions': 'AUTH_SESSIONS',
        'users.view_user': 'USR_VIEW',
        'users.add_user': 'USR_CREATE',
        # ... resto del mapeo
        'reports.view': 'RPT_VIEW',
        'reports.export.csv': 'RPT_EXP_CSV',
        'reports.export.excel': 'RPT_EXP_EXCEL',
        # ... etc
    }
    
    for perm, code in code_mapping.items():
        Function.objects.filter(permission_django=perm).update(code=code)

def add_new_functions_v6(apps, schema_editor):
    """Agrega nuevas funciones de v6.0.0."""
    Function = apps.get_model('access', 'Function')
    
    new_functions = [
        {
            'code': 'RPT_CREATE',
            'permission_django': 'reports.create',
            'display_name': 'Crear Reporte',
            'module': 'reports',
            'status': 'activo',
            'description': 'Crea configuración de reporte. UC_017',
            'is_active': True,
        },
        {
            'code': 'RPT_DELETE',
            'permission_django': 'reports.delete',
            'display_name': 'Eliminar Reporte',
            'module': 'reports',
            'status': 'activo',
            'description': 'Elimina reportes antiguos',
            'is_active': True,
        },
        {
            'code': 'DSH_VIEW',
            'permission_django': 'dashboard.view',
            'display_name': 'Ver Dashboard',
            'module': 'dashboard',
            'status': 'activo',
            'description': 'Ve dashboards con widgets. UC_025, CNST-023',
            'is_active': True,
        },
        # ... resto de funciones activas
        {
            'code': 'RPT_EXP_PDF',
            'permission_django': 'reports.export.pdf',
            'display_name': 'Exportar PDF',
            'module': 'reports',
            'status': 'planificado',
            'description': 'Exporta a PDF. Planificado',
            'is_active': False,
        },
        # ... resto de planificadas
    ]
    
    for func_data in new_functions:
        Function.objects.create(**func_data)

def remove_filter_function(apps, schema_editor):
    """Elimina función RPT_FILTER obsoleta."""
    Function = apps.get_model('access', 'Function')
    Function.objects.filter(permission_django='reports.filter').delete()

def update_groups_v6(apps, schema_editor):
    """Actualiza grupos con nuevas funciones."""
    FunctionGroup = apps.get_model('access', 'FunctionGroup')
    Function = apps.get_model('access', 'Function')
    
    # AGR-001: Agregar DSH_VIEW
    group_001 = FunctionGroup.objects.get(group_id='AGR-001')
    dsh_view = Function.objects.get(permission_django='dashboard.view')
    group_001.functions.add(dsh_view)
    
    # ... etc para otros grupos
```

---

<a name="13-roadmap"></a>

## 13. ROADMAP DE FUNCIONES

### 13.1 Funciones Planificadas (4)

| code | permission_django | módulo | prioridad | versión_target | dependencias |
|------|-------------------|--------|-----------|----------------|--------------|
| RPT_EXP_PDF | reports.export.pdf | reports | Media | v6.1.0 | Librería PDF (weasyprint/reportlab) |
| DSH_EXP_PDF | dashboard.export.pdf | dashboard | Media | v6.1.0 | Librería PDF + gráficos estáticos |
| DSH_SHARE | dashboard.share | dashboard | Baja | v6.2.0 | Sistema de compartir interno |
| DSH_EDIT | dashboard.edit | dashboard | Baja | v6.3.0 | Editor de layout widgets |

---

### 13.2 Detalles de Roadmap

#### v6.1.0: Exportación PDF (Q2 2026)

**Alcance:**
```yaml
Funciones a activar:
  - RPT_EXP_PDF: reports.export.pdf
  - DSH_EXP_PDF: dashboard.export.pdf

Tareas técnicas:
  1. Evaluar librería PDF (weasyprint vs reportlab)
  2. Implementar templates HTML→PDF
  3. Agregar soporte gráficos estáticos
  4. Testing con diferentes tamaños
  5. Validar límite 10K registros (CNST-007)

Tiempo estimado: 3 semanas
```

---

#### v6.2.0: Sistema de Compartir Dashboards (Q3 2026)

**Alcance:**
```yaml
Funciones a activar:
  - DSH_SHARE: dashboard.share

Tareas técnicas:
  1. Modelo: SharedDashboard (usuario, dashboard, permisos)
  2. Endpoint: POST /api/v1/dashboard/{id}/share/
  3. Notificación al destinatario (buzón interno)
  4. Vista de dashboards compartidos
  5. Control de acceso (readonly)

Tiempo estimado: 2 semanas
```

---

#### v6.3.0: Editor de Dashboards (Q4 2026)

**Alcance:**
```yaml
Funciones a activar:
  - DSH_EDIT: dashboard.edit

Tareas técnicas:
  1. Modelo: DashboardLayout (usuario, configuración JSON)
  2. Frontend: Editor drag & drop de widgets
  3. Guardar layouts personalizados
  4. Resetear a layout default
  5. Exportar configuración

Tiempo estimado: 6 semanas
Complejidad: Alta
```

---

### 13.3 Funciones Futuras (No planificadas)

Posibles adiciones para v7.0.0+:

```yaml
MOD_Reports:
  - RPT_SCHEDULE: Programar generación automática
  - RPT_TEMPLATE: Plantillas de reportes personalizados

MOD_Dashboard:
  - DSH_ALERT: Configurar alertas desde dashboard
  - DSH_DRILL: Drill-down en widgets

MOD_Analytics (nuevo módulo):
  - ANALYTICS_PREDICT: Predicciones ML
  - ANALYTICS_ANOMALY: Detección anomalías
```

---

## FIN PARTE 2/2

**Documento completado:** 2026-01-19  
**Versión:** 6.0.0 PARTE 2/2  
**Estado:** ✅ DEFINITIVO  
**Líneas:** ~1,350  

**Ubicación:** `/tmp/iact-real/docs/rbac/MODELO_RBAC_IACT_v6_0_0_PARTE_2.md`

**Documentos relacionados:**
- PARTE 1: MODELO_RBAC_IACT_v6_0_0_PARTE_1.md
- CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md
- RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
- URLS_REPORTES_Y_DASHBOARDS.md

---

**SERIE COMPLETA:**
```
MODELO_RBAC_IACT_v6_0_0_PARTE_1.md  (1,309 líneas)
MODELO_RBAC_IACT_v6_0_0_PARTE_2.md  (1,350 líneas)
────────────────────────────────────────────────
TOTAL:                              2,659 líneas
```

**Estado final:** ✅ MODELO RBAC v6.0.0 COMPLETO
