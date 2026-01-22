---
version: 3.0.0
date: 2026-01-19
project: IACT Call Center System
type: Análisis de Arquitectura - App Audit PARTE 1/3
categoria: arquitectura/apps
tema: apps/audit/ - Fundamentos y Arquitectura
autor: Claude Technical Analysis
tags: [audit, immutable-logs, cnst-031, rbac, clean-code, compliance]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
estado: definitivo
parte: 1 de 3
relacionado:
  - ANALISIS_APP_AUDIT_v3_0_0_PARTE_2.md
  - ANALISIS_APP_AUDIT_v3_0_0_PARTE_3.md
replaces: []
---

# ANÁLISIS DE apps/audit/ v3.0.0 - PARTE 1/3
## FUNDAMENTOS Y ARQUITECTURA

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen)
2. [Propósito y Responsabilidades](#proposito)
3. [CLEAN_CODE v3.0.1 Aplicado](#clean-code)
4. [RESTRICCIONES v1.0.0 Aplicadas](#restricciones)
5. [RBAC v6.0.0 - MOD_Audit](#rbac)
6. [Arquitectura de la App](#arquitectura)
7. [Modelos Django](#modelos)
8. [Constants y Configuración](#constants)

---

<a name="resumen"></a>
## 1. RESUMEN EJECUTIVO

### 1.1 Overview

```yaml
App: apps/audit/
Versión: 3.0.0
Tipo: App SIMPLE (3 partes)
Estado: CRÍTICA - CNST-031
Complejidad: Media
Líneas estimadas: ~2,200 líneas
Tamaño estimado: ~80KB
Tiempo estimado: 5 horas

Propósito:
  Sistema de auditoría completo e immutable
  Registro de todas las acciones críticas del sistema
  Trazabilidad completa para compliance
  Reportes y análisis de logs de auditoría
```

### 1.2 Restricción CRÍTICA: CNST-031

```yaml
CNST-031: Auditoría Immutable
  Descripción: Logs de auditoría NO pueden modificarse/eliminarse
  Razón: Compliance, trazabilidad, legal
  Solución: Modelos managed=False en tablas append-only
  Impacto: 🔴 CRÍTICO
  
  Implementación:
    ✅ AuditLog (tabla immutable append-only)
    ✅ LoginLog (registro de accesos)
    ✅ ActionLog (acciones de usuarios)
    ✅ DataChangeLog (cambios en datos)
    ❌ NO UPDATE/DELETE en tablas de auditoría
    ❌ NO soft delete (registros permanentes)
    ✅ Retención indefinida (compliance)
```

### 1.3 RESTRICCIONES Adicionales

```yaml
CNST-032: Performance en Queries
  - Índices en tablas de auditoría
  - Particionamiento por fecha (mensual)
  - Queries optimizadas con EXPLAIN
  - Cache read-only para reportes

CNST-033: Almacenamiento Logs
  - Compresión de logs antiguos (>6 meses)
  - Archivado a storage externo (>1 año)
  - Backup incremental diario
  - Integridad verificada (checksums)
```

### 1.4 RBAC v6.0.0

```yaml
Módulo: MOD_Audit
Funciones: 4 (todas activas)

AUD_VIEW:    audit.view             (Ver logs de auditoría)
AUD_SEARCH:  audit.search           (Buscar en logs)
AUD_REPORT:  audit.report           (Generar reportes)
AUD_EXPORT:  audit.export           (Exportar logs)

Nota: NO existe AUD_DELETE (CNST-031 immutable)
```

---

<a name="proposito"></a>
## 2. PROPÓSITO Y RESPONSABILIDADES

### 2.1 Propósito Principal

**Sistema de auditoría completo e immutable** para registrar todas las acciones críticas del sistema con fines de compliance y trazabilidad.

### 2.2 Responsabilidades

```yaml
Responsabilidades Principales:
  1. Registro immutable de eventos (CNST-031)
     - Login/logout de usuarios
     - Acciones de usuarios (create/update/delete)
     - Cambios en datos sensibles
     - Accesos a información confidencial
  
  2. Trazabilidad completa
     - Quién: user_id, username, IP
     - Qué: acción, modelo, registro
     - Cuándo: timestamp preciso
     - Dónde: endpoint, vista
     - Cómo: before/after values
  
  3. Reportes de auditoría
     - Actividad por usuario
     - Cambios en período de tiempo
     - Accesos a datos sensibles
     - Compliance reports
  
  4. Búsqueda y análisis
     - Filtros avanzados
     - Full-text search
     - Exportación de resultados
     - Alertas sobre patrones

Responsabilidades Secundarias:
  - Integración con apps/alerts/ (alertas de auditoría)
  - Métricas de uso del sistema
  - Estadísticas de actividad
```

### 2.3 NO Responsabilidades

```yaml
❌ NO es responsable de:
  - Modificar/eliminar logs (CNST-031)
  - Auditoría de sistemas externos
  - Logs de aplicación (usar logging Python)
  - Logs de infraestructura (Nginx, Gunicorn)
  - Métricas de performance (usar monitoring)
  - Backup de logs (responsabilidad de ops)
```

### 2.4 Separación de Responsabilidades

```yaml
apps/audit/:
  - Auditoría de acciones de usuarios
  - Logs immutables de cambios
  - Reportes de compliance

apps/alerts/:
  - Notificaciones de eventos
  - Mensajería interna
  - Alertas configurables

Python logging:
  - Logs de aplicación (debug, info, error)
  - Logs de desarrollo
  - Logs de errores técnicos

Infrastructure logs:
  - Nginx access/error logs
  - Gunicorn logs
  - Sistema operativo logs
```

---

<a name="clean-code"></a>
## 3. CLEAN_CODE v3.0.1 APLICADO

### 3.1 Nomenclatura Código

```python
# CLEAN_CODE v3.0.1: Código en INGLÉS

# Clases (PascalCase)
class AuditLog(models.Model):
    """Log de auditoría immutable."""
    pass

class LoginLog(models.Model):
    """Log de login/logout."""
    pass

class AuditService:
    """Servicio de auditoría."""
    pass

# Métodos y funciones (snake_case)
def log_action(user, action, model, instance_id, data=None):
    """Registra acción de usuario."""
    pass

def get_user_actions(user, date_from, date_to):
    """Obtiene acciones de usuario en período."""
    pass

def generate_compliance_report(start_date, end_date):
    """Genera reporte de compliance."""
    pass

# Variables (snake_case)
action_count = 0
audit_logs = []
user_activity = {}

# Constantes (UPPER_SNAKE_CASE)
ACTION_CREATE = 'CREATE'
ACTION_UPDATE = 'UPDATE'
ACTION_DELETE = 'DELETE'
LOG_RETENTION_YEARS = 7  # Compliance requirement
```

### 3.2 Nomenclatura Base de Datos (Húngaro Preservado)

```python
# Modelos Django: Nombres en inglés
class AuditLog(models.Model):
    
    # Campos: Nombres en inglés
    user = models.ForeignKey(...)
    action = models.CharField(...)
    model_name = models.CharField(...)
    
    # db_column: Húngaro preservado (legacy)
    id = models.BigAutoField(
        db_column='iIdAuditoria',
        primary_key=True
    )
    
    user = models.ForeignKey(
        db_column='iIdUsuario',
        on_delete=models.PROTECT
    )
    
    action = models.CharField(
        db_column='cAccion',
        max_length=20
    )
    
    model_name = models.CharField(
        db_column='cModelo',
        max_length=100
    )
    
    instance_id = models.BigIntegerField(
        db_column='iIdInstancia'
    )
    
    data_before = models.JSONField(
        db_column='jDatosAntes',
        null=True
    )
    
    data_after = models.JSONField(
        db_column='jDatosDespues',
        null=True
    )
    
    timestamp = models.DateTimeField(
        db_column='dFechaHora',
        auto_now_add=True
    )
    
    ip_address = models.GenericIPAddressField(
        db_column='cDireccionIP'
    )
    
    class Meta:
        db_table = 'tbl_auditoria'
        managed = False  # CNST-031: Immutable
```

### 3.3 Docstrings en Español

```python
"""
Service layer para sistema de auditoría.

Responsabilidades:
- Registrar acciones de usuarios (immutable)
- Generar reportes de auditoría
- Búsqueda y filtrado de logs
- Exportación para compliance

CLEAN_CODE v3.0.1:
- Código: inglés PascalCase/snake_case
- Docstrings: español formato Google
- db_column: húngaro preservado

CNST-031: Logs immutables, NO UPDATE/DELETE
CNST-032: Queries optimizadas con índices
"""

class AuditService:
    """
    Servicio principal de auditoría.
    
    Responsabilidades:
    - Logging de acciones
    - Consultas de logs
    - Generación de reportes
    
    Atributos:
        retention_years (int): Años de retención de logs
    """
    
    def __init__(self):
        """Inicializa el servicio de auditoría."""
        self.retention_years = LOG_RETENTION_YEARS
    
    def log_action(
        self,
        user: User,
        action: str,
        model_name: str,
        instance_id: int,
        data_before: Optional[Dict] = None,
        data_after: Optional[Dict] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Registra acción de usuario en auditoría.
        
        Args:
            user: Usuario que realizó la acción
            action: Tipo de acción (CREATE, UPDATE, DELETE, VIEW)
            model_name: Nombre del modelo Django
            instance_id: ID de la instancia afectada
            data_before: Datos antes del cambio (para UPDATE)
            data_after: Datos después del cambio (para UPDATE/CREATE)
            ip_address: Dirección IP del usuario
        
        Returns:
            AuditLog: Registro de auditoría creado
        
        CNST-031: Log es immutable, NO se puede modificar
        CNST-032: INSERT optimizado con índices
        
        Example:
            >>> audit_service.log_action(
            ...     user=request.user,
            ...     action='UPDATE',
            ...     model_name='User',
            ...     instance_id=123,
            ...     data_before={'email': 'old@example.com'},
            ...     data_after={'email': 'new@example.com'},
            ...     ip_address='192.168.1.100'
            ... )
        """
        # Implementación...
        pass
```

---

<a name="restricciones"></a>
## 4. RESTRICCIONES v1.0.0 APLICADAS

### 4.1 CNST-031: Auditoría Immutable (🔴 CRÍTICO)

```yaml
Restricción: Logs de auditoría NO modificables/eliminables
Categoría: Compliance y Legal
Impacto: CRÍTICO
Estado: Activo

Descripción:
  Los registros de auditoría son permanentes e immutables.
  NO se pueden modificar, actualizar ni eliminar bajo ninguna
  circunstancia.

Razones:
  - Compliance: Regulaciones SOX, GDPR, ISO 27001
  - Legal: Evidencia en investigaciones
  - Trazabilidad: Histórico completo de acciones
  - Integridad: Prevenir manipulación de logs

Implementación:
  ✅ managed=False en Meta de modelos
  ✅ NO métodos update()/delete() en modelos
  ✅ Database triggers BEFORE UPDATE/DELETE → RAISE ERROR
  ✅ Permisos BD: solo INSERT/SELECT
  ✅ NO existe función RBAC AUD_DELETE

Database Triggers:
  ```sql
  -- Trigger para prevenir UPDATE
  CREATE OR REPLACE FUNCTION prevent_audit_update()
  RETURNS TRIGGER AS $$
  BEGIN
    RAISE EXCEPTION 'Audit logs are immutable (CNST-031)';
  END;
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER no_update_audit_log
  BEFORE UPDATE ON tbl_auditoria
  FOR EACH ROW EXECUTE FUNCTION prevent_audit_update();

  -- Trigger para prevenir DELETE
  CREATE OR REPLACE FUNCTION prevent_audit_delete()
  RETURNS TRIGGER AS $$
  BEGIN
    RAISE EXCEPTION 'Audit logs cannot be deleted (CNST-031)';
  END;
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER no_delete_audit_log
  BEFORE DELETE ON tbl_auditoria
  FOR EACH ROW EXECUTE FUNCTION prevent_audit_delete();
  ```

Testing:
  - Verificar que UPDATE lanza excepción
  - Verificar que DELETE lanza excepción
  - Verificar que solo INSERT funciona
  - Verificar managed=False en modelos

Retención:
  - Retención mínima: 7 años (compliance)
  - Retención práctica: Indefinida
  - Archivado: >1 año a storage externo
  - Backup: Diario incremental
```

### 4.2 CNST-032: Performance en Queries

```yaml
Restricción: Queries optimizadas de auditoría
Categoría: Performance
Impacto: Alto
Estado: Activo

Problema:
  Tablas de auditoría crecen rápidamente (millones de registros).
  Queries sin optimización causan timeouts y carga en BD.

Soluciones:
  1. Índices estratégicos:
     - idx_audit_user (user_id, timestamp DESC)
     - idx_audit_model (model_name, timestamp DESC)
     - idx_audit_action (action, timestamp DESC)
     - idx_audit_timestamp (timestamp DESC)
     - idx_audit_ip (ip_address)
  
  2. Particionamiento por fecha:
     - Particiones mensuales automáticas
     - Queries usan partition pruning
     - Mejor performance en rangos de fechas
  
  3. Materialzed views para reportes:
     - daily_user_activity
     - monthly_action_summary
     - sensitive_data_access
  
  4. Query optimization:
     - LIMIT obligatorio en queries sin filtros
     - EXPLAIN ANALYZE para queries complejas
     - Connection pooling
     - Read replicas para reportes

Límites:
  - Max 10,000 registros por query
  - Timeout queries: 30s
  - Reportes grandes: async tasks

Monitoreo:
  - pg_stat_statements para queries lentas
  - Alert si query >5s
  - Índices actualizados semanalmente
```

### 4.3 CNST-033: Almacenamiento Logs

```yaml
Restricción: Gestión de almacenamiento de logs
Categoría: Operacional
Impacto: Medio
Estado: Activo

Crecimiento esperado:
  - ~10,000 logs/día (estimado)
  - ~300KB/día (promedio)
  - ~110MB/año
  - ~770MB/7 años

Estrategia de almacenamiento:
  1. Logs recientes (<6 meses):
     - PostgreSQL principal
     - Acceso rápido
     - Sin compresión
  
  2. Logs 6-12 meses:
     - Compresión gzip
     - Índices mantenidos
     - Acceso medio
  
  3. Logs >1 año:
     - Archivado a S3/storage externo
     - Compresión máxima
     - Acceso bajo
     - Recuperación bajo demanda

Backup:
  - Backup incremental diario
  - Backup completo semanal
  - Retención backups: 90 días
  - Checksums verificados

Integridad:
  - SHA256 checksums de archivos
  - Verificación mensual
  - Alert si checksum falla
```

### 4.4 Otras RESTRICCIONES Aplicables

```yaml
CNST-025: Timeout 90s
  - Aplicable: SÍ
  - Queries de auditoría <90s
  - Reportes pesados: async tasks

CNST-010: Cache LocMem
  - Aplicable: PARCIAL
  - Cache solo para reportes agregados
  - NO cache de logs individuales (siempre fresh)
  - TTL corto: 60s

CNST-001: NO Email
  - Aplicable: NO directamente
  - Integración con apps/alerts/ para notificaciones
  - Alertas sobre patrones sospechosos
```

---

<a name="rbac"></a>
## 5. RBAC v6.0.0 - MOD_Audit

### 5.1 Módulo MOD_Audit

```yaml
Código: MOD_Audit
Nombre: Módulo de Auditoría
Descripción: Gestión de logs de auditoría y compliance
Estado: Activo
Funciones: 4 (todas activas)
Grupos asociados: GRP_Auditor, GRP_Admin, GRP_Compliance

Nota importante:
  NO existe función AUD_DELETE (CNST-031 immutable)
```

### 5.2 Funciones RBAC (4 Activas)

#### 5.2.1 AUD_VIEW

```yaml
Código: AUD_VIEW
Nombre: Ver Auditoría
Descripción: Permite ver logs de auditoría del sistema
Permission Django: audit.view
Estado: Activo
Asignación típica:
  - GRP_Auditor (auditores internos)
  - GRP_Admin
  - GRP_Compliance

Permite:
  - GET /api/v1/audit/logs/ (lista logs)
  - GET /api/v1/audit/logs/{id}/ (detalle log)
  - Filtrar por usuario, acción, fecha
  - Ver datos before/after

Restricciones:
  - Solo logs propios (usuarios normales)
  - Todos los logs (auditores/admin)
  - Límite 10,000 registros por query

No permite:
  - Modificar logs (CNST-031)
  - Eliminar logs (CNST-031)
  - Ver logs de auditores (segregación)
```

#### 5.2.2 AUD_SEARCH

```yaml
Código: AUD_SEARCH
Nombre: Buscar en Auditoría
Descripción: Permite búsquedas avanzadas en logs
Permission Django: audit.search
Estado: Activo
Asignación típica:
  - GRP_Auditor
  - GRP_Admin
  - GRP_Compliance

Permite:
  - POST /api/v1/audit/search/ (búsqueda avanzada)
  - Filtros complejos (AND/OR)
  - Full-text search en JSON data
  - Búsqueda por rangos de fechas
  - Búsqueda por IP address
  - Búsqueda por modelo/acción

Ejemplos búsquedas:
  - "Buscar todos los UPDATE en User en últimos 30 días"
  - "Buscar accesos desde IP sospechosa"
  - "Buscar cambios en campo 'email'"
  - "Buscar acciones de usuario específico"

No permite:
  - Modificar resultados (CNST-031)
  - Exportar sin permiso AUD_EXPORT
```

#### 5.2.3 AUD_REPORT

```yaml
Código: AUD_REPORT
Nombre: Generar Reportes
Descripción: Permite generar reportes de auditoría
Permission Django: audit.report
Estado: Activo
Asignación típica:
  - GRP_Auditor
  - GRP_Admin
  - GRP_Compliance

Permite:
  - GET /api/v1/audit/reports/user-activity/
  - GET /api/v1/audit/reports/data-changes/
  - GET /api/v1/audit/reports/sensitive-access/
  - GET /api/v1/audit/reports/compliance/
  - Reportes agregados
  - Gráficos de tendencias
  - Estadísticas de uso

Reportes disponibles:
  - Actividad por usuario (período)
  - Cambios en datos sensibles
  - Accesos a información confidencial
  - Compliance SOX/GDPR
  - Top usuarios más activos
  - Acciones por tipo (CREATE/UPDATE/DELETE)

No permite:
  - Modificar datos del reporte (CNST-031)
  - Generar reportes >1 año (performance)
```

#### 5.2.4 AUD_EXPORT

```yaml
Código: AUD_EXPORT
Nombre: Exportar Logs
Descripción: Permite exportar logs para análisis externo
Permission Django: audit.export
Estado: Activo
Asignación típica:
  - GRP_Auditor
  - GRP_Compliance

Permite:
  - POST /api/v1/audit/export/csv/
  - POST /api/v1/audit/export/excel/
  - POST /api/v1/audit/export/json/
  - Exportar resultados de búsquedas
  - Exportar reportes completos
  - Download seguro de archivos

Formatos soportados:
  - CSV (para análisis en Excel)
  - Excel (formato nativo)
  - JSON (para integración con otros sistemas)

Límites:
  - Max 50,000 registros por exportación
  - Archivos >10MB: async task
  - Retención archivos: 24 horas

Validaciones:
  - Usuario debe tener AUD_VIEW + AUD_EXPORT
  - Logs sensibles requieren aprobación adicional
  - Exportaciones auditadas (meta-audit)

No permite:
  - Exportar sin filtros (debe especificar rango)
  - Modificar durante exportación (CNST-031)
```

### 5.3 function_map en ViewSets

```python
# apps/audit/views.py

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para logs de auditoría.
    
    RBAC v6.0.0: DynamicFunctionPermission
    CNST-031: ReadOnly (immutable)
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    # function_map para RBAC
    function_map = {
        'list': 'audit.view',              # AUD_VIEW
        'retrieve': 'audit.view',          # AUD_VIEW
        'search': 'audit.search',          # AUD_SEARCH
        'export_csv': 'audit.export',      # AUD_EXPORT
        'export_excel': 'audit.export',    # AUD_EXPORT
        'export_json': 'audit.export',     # AUD_EXPORT
    }
    
    # NO create/update/destroy (CNST-031)


class AuditReportViewSet(viewsets.ViewSet):
    """ViewSet para reportes de auditoría."""
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'user_activity': 'audit.report',        # AUD_REPORT
        'data_changes': 'audit.report',         # AUD_REPORT
        'sensitive_access': 'audit.report',     # AUD_REPORT
        'compliance': 'audit.report',           # AUD_REPORT
    }
```

### 5.4 Grupos y Asignaciones

```yaml
GRP_Auditor:
  Funciones asignadas:
    - AUD_VIEW (ver todos los logs)
    - AUD_SEARCH (búsquedas avanzadas)
    - AUD_REPORT (generar reportes)
    - AUD_EXPORT (exportar logs)

GRP_Compliance:
  Funciones asignadas:
    - AUD_VIEW (compliance reviews)
    - AUD_REPORT (reportes regulatorios)
    - AUD_EXPORT (evidencia compliance)

GRP_Admin:
  Funciones asignadas:
    - Todas de GRP_Auditor +
    - Acceso sin restricciones
    - Reportes avanzados

GRP_UserBasic:
  Funciones asignadas:
    - AUD_VIEW (solo logs propios)
    - Limitado a sus propias acciones
```

---

<a name="arquitectura"></a>
## 6. ARQUITECTURA DE LA APP

### 6.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    apps/audit/                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐    │
│  │              API Layer (REST)                  │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - AuditLogViewSet (ReadOnly)                  │    │
│  │  - AuditReportViewSet                          │    │
│  │  - RBAC: DynamicFunctionPermission             │    │
│  │  - NO create/update/destroy (CNST-031)         │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │           Service Layer                        │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - AuditService                                │    │
│  │    * log_action()                              │    │
│  │    * log_login()                               │    │
│  │    * log_logout()                              │    │
│  │    * get_user_actions()                        │    │
│  │  - ReportService                               │    │
│  │    * user_activity_report()                    │    │
│  │    * data_changes_report()                     │    │
│  │    * compliance_report()                       │    │
│  │  - SearchService                               │    │
│  │    * search_logs()                             │    │
│  │    * advanced_search()                         │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │      Data Layer (Immutable Models)             │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - AuditLog (managed=False)                    │    │
│  │  - LoginLog (managed=False)                    │    │
│  │  - ActionLog (managed=False)                   │    │
│  │  - DataChangeLog (managed=False)               │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │       Database (PostgreSQL + Triggers)         │    │
│  │  - tbl_auditoria (BEFORE UPDATE → ERROR)       │    │
│  │  - tbl_log_login (BEFORE DELETE → ERROR)       │    │
│  │  - Partitioned by month                        │    │
│  │  - Indexes optimized (CNST-032)                │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘

Integraciones:
  ┌─────────────────┐
  │  ALL apps/      │ → Llaman AuditService.log_action()
  └─────────────────┘
  
  ┌─────────────────┐
  │  apps/alerts/   │ → Alertas sobre patrones sospechosos
  └─────────────────┘
  
  ┌─────────────────┐
  │  apps/access/   │ → RBAC validation (4 funciones)
  └─────────────────┘
```

### 6.2 Flujos Principales

#### 6.2.1 Flujo: Log de Acción

```
Usuario realiza acción (ej: actualiza perfil)
   ↓
View/API llama AuditService.log_action()
   ↓
Capturar datos:
   - user_id, username
   - action (UPDATE)
   - model_name (User)
   - instance_id (123)
   - data_before (email: old@example.com)
   - data_after (email: new@example.com)
   - ip_address (request.META['REMOTE_ADDR'])
   - timestamp (auto)
   ↓
Crear AuditLog (INSERT)
   ↓
CNST-031: Registro immutable ✅
   ↓
Response (log_id)

NO se puede modificar/eliminar ✅
```

#### 6.2.2 Flujo: Login Audit

```
Usuario hace login
   ↓
Authentication backend exitoso
   ↓
Signal post_login dispara
   ↓
AuditService.log_login()
   ↓
Crear LoginLog:
   - user_id
   - success=True
   - ip_address
   - user_agent
   - timestamp
   ↓
CNST-031: Inmutable ✅

Si login falla:
   ↓
   - success=False
   - attempted_username
   - failure_reason
```

#### 6.2.3 Flujo: Generar Reporte

```
Auditor solicita reporte
   ↓
GET /api/v1/audit/reports/user-activity/?user_id=123&from=2026-01-01&to=2026-01-31
   ↓
DynamicFunctionPermission verifica AUD_REPORT
   ↓
ReportService.user_activity_report()
   ↓
Query optimizada con índices (CNST-032)
   ↓
Agregación de datos:
   - Total acciones por tipo
   - Acciones por día
   - Modelos más modificados
   - Gráficos de tendencia
   ↓
Response JSON con reporte
   ↓
Opcionalmente: Exportar (AUD_EXPORT)

CNST-031: Datos son read-only ✅
CNST-032: Query optimizada ✅
```

---

<a name="modelos"></a>
## 7. MODELOS DJANGO

### 7.1 AuditLog

```python
"""
Modelo principal de auditoría.

CLEAN_CODE v3.0.1:
- Nombre clase: AuditLog (inglés PascalCase)
- Campos: user, action, model_name (inglés snake_case)
- db_column: iIdAuditoria, cAccion (húngaro preservado)
- db_table: tbl_auditoria (húngaro preservado)

CNST-031: managed=False, immutable
CNST-032: Índices optimizados
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from apps.audit.constants import (
    ACTION_CHOICES,
    ACTION_CREATE,
    ACTION_UPDATE,
    ACTION_DELETE,
    ACTION_VIEW,
)

User = get_user_model()


class AuditLog(models.Model):
    """
    Log de auditoría immutable.
    
    Registra todas las acciones de usuarios en el sistema.
    
    Campos:
    - user: Usuario que realizó la acción
    - action: Tipo de acción (CREATE, UPDATE, DELETE, VIEW)
    - model_name: Nombre del modelo Django afectado
    - instance_id: ID de la instancia afectada
    - data_before: Datos antes del cambio (JSON)
    - data_after: Datos después del cambio (JSON)
    - timestamp: Fecha/hora de la acción
    - ip_address: Dirección IP del usuario
    - endpoint: URL del endpoint llamado
    - user_agent: User-Agent del navegador
    
    CNST-031: Immutable, NO UPDATE/DELETE
    CNST-032: Índices en user, timestamp, model_name, action
    """
    
    id = models.BigAutoField(
        db_column='iIdAuditoria',
        primary_key=True
    )
    
    user = models.ForeignKey(
        User,
        db_column='iIdUsuario',
        on_delete=models.PROTECT,  # NO CASCADE (CNST-031)
        related_name='audit_logs',
        help_text="Usuario que realizó la acción"
    )
    
    action = models.CharField(
        db_column='cAccion',
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Tipo de acción: CREATE, UPDATE, DELETE, VIEW"
    )
    
    model_name = models.CharField(
        db_column='cModelo',
        max_length=100,
        help_text="Nombre del modelo Django (ej: User, Call)"
    )
    
    instance_id = models.BigIntegerField(
        db_column='iIdInstancia',
        help_text="ID del registro afectado"
    )
    
    data_before = models.JSONField(
        db_column='jDatosAntes',
        null=True,
        blank=True,
        help_text="Datos antes del cambio (para UPDATE)"
    )
    
    data_after = models.JSONField(
        db_column='jDatosDespues',
        null=True,
        blank=True,
        help_text="Datos después del cambio (para UPDATE/CREATE)"
    )
    
    timestamp = models.DateTimeField(
        db_column='dFechaHora',
        auto_now_add=True,
        help_text="Fecha y hora exacta de la acción"
    )
    
    ip_address = models.GenericIPAddressField(
        db_column='cDireccionIP',
        null=True,
        blank=True,
        help_text="Dirección IP del usuario"
    )
    
    endpoint = models.CharField(
        db_column='cEndpoint',
        max_length=255,
        null=True,
        blank=True,
        help_text="URL del endpoint llamado"
    )
    
    user_agent = models.TextField(
        db_column='tUserAgent',
        null=True,
        blank=True,
        help_text="User-Agent del navegador"
    )
    
    class Meta:
        db_table = 'tbl_auditoria'
        managed = False  # CNST-031: Immutable
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['ip_address']),
        ]
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
    
    def __str__(self):
        return f"{self.user.username} - {self.action} {self.model_name}#{self.instance_id}"
    
    def save(self, *args, **kwargs):
        """
        Override save para prevenir UPDATE.
        
        CNST-031: Solo permite INSERT
        """
        if self.pk:
            raise ValueError("Audit logs are immutable (CNST-031)")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete para prevenir DELETE.
        
        CNST-031: Logs no se pueden eliminar
        """
        raise ValueError("Audit logs cannot be deleted (CNST-031)")
    
    @property
    def changed_fields(self):
        """
        Obtiene lista de campos que cambiaron.
        
        Returns:
            List[str]: Nombres de campos modificados
        """
        if not self.data_before or not self.data_after:
            return []
        
        changed = []
        for key in self.data_after.keys():
            if key in self.data_before:
                if self.data_before[key] != self.data_after[key]:
                    changed.append(key)
            else:
                changed.append(key)
        
        return changed


class LoginLog(models.Model):
    """
    Log de login/logout de usuarios.
    
    Registra intentos de autenticación.
    
    CNST-031: Immutable
    """
    
    id = models.BigAutoField(
        db_column='iIdLogLogin',
        primary_key=True
    )
    
    user = models.ForeignKey(
        User,
        db_column='iIdUsuario',
        on_delete=models.PROTECT,
        related_name='login_logs',
        null=True,  # NULL si login falló
        help_text="Usuario (NULL si login falló)"
    )
    
    attempted_username = models.CharField(
        db_column='cUsuarioIntentado',
        max_length=150,
        help_text="Username ingresado (para logins fallidos)"
    )
    
    success = models.BooleanField(
        db_column='bExitoso',
        help_text="Si el login fue exitoso"
    )
    
    failure_reason = models.CharField(
        db_column='cRazonFallo',
        max_length=255,
        null=True,
        blank=True,
        help_text="Razón del fallo (credenciales inválidas, etc)"
    )
    
    ip_address = models.GenericIPAddressField(
        db_column='cDireccionIP',
        help_text="Dirección IP del intento"
    )
    
    user_agent = models.TextField(
        db_column='tUserAgent',
        null=True,
        blank=True,
        help_text="User-Agent del navegador"
    )
    
    timestamp = models.DateTimeField(
        db_column='dFechaHora',
        auto_now_add=True,
        help_text="Fecha/hora del intento"
    )
    
    session_key = models.CharField(
        db_column='cSessionKey',
        max_length=40,
        null=True,
        blank=True,
        help_text="Django session key"
    )
    
    class Meta:
        db_table = 'tbl_log_login'
        managed = False  # CNST-031
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['success', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
        verbose_name = 'Log de Login'
        verbose_name_plural = 'Logs de Login'
    
    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"{self.attempted_username} - {status} - {self.timestamp}"
    
    def save(self, *args, **kwargs):
        """CNST-031: Solo INSERT."""
        if self.pk:
            raise ValueError("Login logs are immutable (CNST-031)")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """CNST-031: NO DELETE."""
        raise ValueError("Login logs cannot be deleted (CNST-031)")
```

---

<a name="constants"></a>
## 8. CONSTANTS Y CONFIGURACIÓN

### 8.1 Archivo: apps/audit/constants.py

```python
"""
Constantes para sistema de auditoría.

CLEAN_CODE v3.0.1:
- Constantes: UPPER_SNAKE_CASE inglés
- Docstrings: español

CNST-031: Immutable logs
CNST-032: Performance optimizations
"""

# ===================================================================
# ACCIONES DE AUDITORÍA
# ===================================================================

ACTION_CREATE = 'CREATE'
"""Acción de creación de registro."""

ACTION_UPDATE = 'UPDATE'
"""Acción de actualización de registro."""

ACTION_DELETE = 'DELETE'
"""Acción de eliminación de registro."""

ACTION_VIEW = 'VIEW'
"""Acción de visualización de datos sensibles."""

ACTION_LOGIN = 'LOGIN'
"""Acción de login exitoso."""

ACTION_LOGOUT = 'LOGOUT'
"""Acción de logout."""

ACTION_EXPORT = 'EXPORT'
"""Acción de exportación de datos."""

ACTION_CHOICES = [
    (ACTION_CREATE, 'Crear'),
    (ACTION_UPDATE, 'Actualizar'),
    (ACTION_DELETE, 'Eliminar'),
    (ACTION_VIEW, 'Ver'),
    (ACTION_LOGIN, 'Login'),
    (ACTION_LOGOUT, 'Logout'),
    (ACTION_EXPORT, 'Exportar'),
]
"""Opciones de acciones para campo Django."""

# ===================================================================
# RETENCIÓN Y COMPLIANCE
# ===================================================================

LOG_RETENTION_YEARS = 7
"""Años de retención de logs (compliance SOX/GDPR)."""

LOG_COMPRESSION_MONTHS = 6
"""Meses antes de comprimir logs antiguos."""

LOG_ARCHIVE_MONTHS = 12
"""Meses antes de archivar a storage externo."""

# ===================================================================
# LÍMITES DE PERFORMANCE (CNST-032)
# ===================================================================

MAX_LOGS_PER_QUERY = 10000
"""Máximo registros retornados por query."""

QUERY_TIMEOUT_SECONDS = 30
"""Timeout de queries de auditoría."""

DEFAULT_PAGE_SIZE = 100
"""Tamaño de página por defecto en API."""

MAX_PAGE_SIZE = 1000
"""Tamaño máximo de página en API."""

# ===================================================================
# EXPORTACIÓN
# ===================================================================

MAX_EXPORT_RECORDS = 50000
"""Máximo registros por exportación."""

EXPORT_FILE_RETENTION_HOURS = 24
"""Horas de retención de archivos exportados."""

EXPORT_FORMATS = ['csv', 'excel', 'json']
"""Formatos de exportación soportados."""

# ===================================================================
# MODELOS AUDITABLES
# ===================================================================

AUDITABLE_MODELS = [
    'User',
    'Call',
    'Client',
    'Service',
    'Center',
    'InternalMessage',
    'AlertConfiguration',
    # ... todos los modelos críticos
]
"""Lista de modelos que se auditan automáticamente."""

SENSITIVE_FIELDS = [
    'password',
    'email',
    'phone',
    'address',
    'credit_card',
    'ssn',
]
"""Campos sensibles que requieren auditoría especial."""

# ===================================================================
# REPORTES
# ===================================================================

REPORT_TYPES = [
    'user_activity',
    'data_changes',
    'sensitive_access',
    'compliance_sox',
    'compliance_gdpr',
    'login_history',
    'failed_logins',
]
"""Tipos de reportes disponibles."""

# ===================================================================
# ALERTAS DE AUDITORÍA
# ===================================================================

ALERT_PATTERNS = {
    'multiple_failed_logins': {
        'threshold': 5,
        'window_minutes': 15,
        'action': 'alert_security_team'
    },
    'sensitive_data_access': {
        'threshold': 100,
        'window_minutes': 60,
        'action': 'alert_compliance'
    },
    'mass_deletion': {
        'threshold': 50,
        'window_minutes': 5,
        'action': 'alert_admin'
    },
}
"""Patrones de alertas automáticas."""
```

---

## 9. RESUMEN PARTE 1

### 9.1 Componentes Definidos

```yaml
Documentación:
  ✅ Resumen ejecutivo
  ✅ Propósito y responsabilidades
  ✅ CLEAN_CODE v3.0.1 aplicado
  ✅ RESTRICCIONES (CNST-031 crítico, CNST-032, CNST-033)
  ✅ RBAC v6.0.0 (4 funciones activas)
  ✅ Arquitectura completa
  ✅ 2 modelos Django inmutables
  ✅ Constants y configuración

Modelos Django:
  ✅ AuditLog (managed=False, immutable)
  ✅ LoginLog (managed=False, immutable)

RBAC:
  ✅ AUD_VIEW (audit.view)
  ✅ AUD_SEARCH (audit.search)
  ✅ AUD_REPORT (audit.report)
  ✅ AUD_EXPORT (audit.export)
  ❌ NO AUD_DELETE (CNST-031)

Constants:
  ✅ ACTION_CHOICES (7 acciones)
  ✅ LOG_RETENTION_YEARS = 7
  ✅ MAX_LOGS_PER_QUERY = 10,000
  ✅ AUDITABLE_MODELS lista
  ✅ ALERT_PATTERNS dict
```

---

## PRÓXIMA PARTE

**PARTE 2/3: Implementación Completa**

Contenido:
- Services completos (AuditService, ReportService, SearchService)
- Serializers (AuditLogSerializer, ReportSerializer)
- ViewSets ReadOnly con RBAC
- URLs configuration
- Endpoints REST documentados
- Utils (get_client_ip, sanitize_data)
- Signals para auto-logging

**Estimado:** ~1,100 líneas, 2.5 horas

---

**Fin de PARTE 1/3**
