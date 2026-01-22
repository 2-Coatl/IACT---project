# MODELO RBAC IACT - v6.0.0 PARTE 1/2

## Sistema IACT - IVR Analytics & Customer Tracking

---

**Proyecto:** IACT-2025-001  
**Documento:** IACT-RBAC-001-v6.0.0-PARTE-1  
**Título:** Modelo de Control de Acceso Basado en Funciones Atómicas - Parte 1  
**Versión:** 6.0.0 - Dashboard Separado + Roadmap Funciones  
**Fecha:** 19 de enero de 2026  
**Estado:** Listo para Implementación

---

## CONTROL DE CAMBIOS

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0-3.0 | 17-18 Oct 2025 | Versiones preliminares | Equipo |
| 4.0 | 19 Oct 2025 | Modelo híbrido con 18 roles | Equipo |
| 5.0 | 03 Ene 2026 | Enfoque Sin Pretensiones | Equipo |
| 5.1 | 03 Ene 2026 | Adaptación a 8 módulos IACT | Equipo |
| 5.2.0 | 13 Ene 2026 | Clean Code + 42 funciones + Sin segmentos | Equipo |
| 5.2.1 | 13 Ene 2026 | Funciones en inglés (namespace style) | Equipo |
| **6.0.0** | **19 Ene 2026** | **Separación MOD_Dashboard + Roadmap funciones** | **Equipo** |

### Cambios v5.2.1 → v6.0.0

| Aspecto | v5.2.1 | v6.0.0 |
|---------|--------|--------|
| Módulos | 8 | **9** (MOD_Dashboard separado) |
| Funciones totales | 42 | **46** (+4 nuevas) |
| Funciones activas | 42 | **42** (sin cambio) |
| Funciones planificadas | 0 | **4** (roadmap) |
| MOD_Reports | 8 funciones | **6** funciones (replanteadas) |
| MOD_Dashboard | N/A (dentro Reports) | **6** funciones (nuevo módulo) |
| permission_django | `reports.view_report` | `reports.view` (formato simplificado) |
| Exportación dashboard | NO | **SÍ** (export.csv, export.excel) |
| Columna status | NO | **SÍ** (activo/planificado/deprecado) |

**Documentos referenciados:**
- CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md
- RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
- URLS_REPORTES_Y_DASHBOARDS.md ⭐ NUEVO

---

## TABLA DE CONTENIDO - PARTE 1/2

**PARTE 1 (Este documento):**

1. [Filosofía del Modelo](#1-filosofia)
2. [Arquitectura IACT](#2-arquitectura)
3. [Catálogo de 46 Funciones](#3-catalogo-funciones)
4. [Los 10 Grupos de Funciones](#4-grupos)
5. [Separación de Funciones (SoD)](#5-sod)
6. [Permisos Temporales](#6-permisos-temporales)

**PARTE 2 (Documento separado):**

7. Modelo de Datos
8. Implementación SQL
9. Implementación Django/DRF
10. Mapeo Funciones → Casos de Uso
11. Migración desde v5.1
12. Migración v5.2 → v6.0.0
13. Roadmap de Funciones

---

<a name="1-filosofia"></a>

## 1. FILOSOFÍA DEL MODELO

### 1.1 Principio Central

> **Los nombres de funciones describen QUÉ HACE la función, NO QUIÉN es la persona**

### 1.2 Enfoque Sin Pretensiones

**❌ INCORRECTO - Con Pretensiones:**

```
Roles basados en títulos:
- USERS_FULL_MANAGER      → Define QUÉ ES la persona
- SYSTEM_ADMIN            → Cargo jerárquico
- REPORTS_SUPERVISOR      → Título organizacional
```

**✅ CORRECTO - Sin Pretensiones:**

```
Funciones basadas en acciones:
- users.view              → Describe QUÉ PUEDE HACER
- reports.export.csv      → Acción concreta
- dashboard.view          → Capacidad específica
```

### 1.3 Estándar de Nomenclatura v6.0.0

**REGLA FUNDAMENTAL (CLEAN_CODE v3.0.1):**

```
✅ CÓDIGO Python:           Inglés (clases, métodos, variables)
✅ permission_django:       Inglés (reports.view, dashboard.export.csv)
✅ code (referencial):      Inglés (RPT_VIEW, DSH_EXP_CSV)
✅ COMENTARIOS/Docstrings:  Español
✅ display_name (UI):       Español (Ve Reportes, Exporta CSV)
✅ description:             Español (con casos de uso)
```

**Ejemplo completo:**

```python
class Function(models.Model):
    """Función atómica del sistema RBAC."""  # ← Español
    
    code = models.CharField(
        max_length=30,
        help_text="Código: RPT_VIEW, DSH_EXP_CSV"  # ← Español
    )
    
    permission_django = models.CharField(
        max_length=100,
        primary_key=True,
        help_text="reports.view, dashboard.export.csv"  # ← Español
    )
    
    display_name = models.CharField(
        max_length=200,
        help_text="Ve Reportes, Exporta CSV"  # ← Español
    )
    
    module = models.CharField(
        max_length=50,
        help_text="reports, dashboard, users"  # ← Español
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('planificado', 'Planificado'),
            ('deprecado', 'Deprecado'),
        ],
        default='activo',
        help_text="Estado de la función"  # ← Español
    )
```

### 1.4 Convención de Códigos Referenciales

**Patrón:**
```
[MÓDULO]_[PREFIJO]_[ACCIÓN]

Donde:
- MÓDULO: 3-4 letras (RPT, DSH, USR, AUTH)
- PREFIJO: Tipo de operación (VIEW, EXP, CONF, EXEC)
- ACCIÓN: Específica (CSV, EXCEL, PDF, KPI)
```

**Prefijos estándar:**

```yaml
VIEW_:   Ver/Visualizar algo
EXP_:    Exportar a formato
CONF_:   Configurar
EXEC_:   Ejecutar/Procesar
SEND_:   Enviar
MARK_:   Marcar estado
GEN_:    Generar
SEARCH_: Buscar
```

**Ejemplos:**

```
RPT_VIEW          → reports.view (ver reportes)
RPT_EXP_CSV       → reports.export.csv (exportar CSV)
DSH_VIEW          → dashboard.view (ver dashboard)
DSH_EXP_EXCEL     → dashboard.export.excel (exportar Excel)
USR_CREATE        → users.add_user (crear usuarios)
AUTH_LOGIN        → auth.login (iniciar sesión)
```

### 1.5 Integración con Django REST Framework

**DRF usa DjangoModelPermissions:**

```python
from rest_framework.permissions import DjangoModelPermissions

class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet de reportes con permisos Django."""
    
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Report.objects.all()
    
    # DRF mapea automáticamente:
    # GET    → reports.view_report (si VIEW_PERMS habilitado)
    # POST   → reports.add_report
    # PUT    → reports.change_report
    # DELETE → reports.delete_report
```

**Nuestro sistema usa formato simplificado:**

```python
# Formato estándar Django
reports.view_report   ❌ NO usamos

# Formato simplificado IACT
reports.view          ✅ SÍ usamos

# Con puntos intermedios para exportación
reports.export.csv    ✅ SÍ usamos
dashboard.export.excel ✅ SÍ usamos
```

---

<a name="2-arquitectura"></a>

## 2. ARQUITECTURA IACT

### 2.1 Visión General

El sistema IACT implementa **Flat RBAC** (Role-Based Access Control) sin jerarquías, basado en:

- ✅ **46 funciones atómicas** (42 activas + 4 planificadas)
- ✅ **9 módulos funcionales** (antes 8 en v5.2.1)
- ✅ **10 grupos de funciones** (sin cambio)
- ✅ **3 reglas de separación de funciones (SoD)**
- ✅ **Permisos temporales** con justificación y auditoría

### 2.2 Distribución de Funciones por Módulo

| Módulo | Código | Funciones | % | Activas | Planificadas | Propósito |
|--------|--------|-----------|---|---------|--------------|-----------|
| MOD_Auth | AUTH | 4 | 8.7% | 4 | 0 | Sesiones y autenticación |
| MOD_Users | USR | 9 | 19.6% | 9 | 0 | Gestión de identidades |
| MOD_Access | ACC | 5 | 10.9% | 5 | 0 | RBAC core + Reglas SoD |
| MOD_Pipeline | PIP | 4 | 8.7% | 4 | 0 | Supervisión ETL |
| **MOD_Reports** | **RPT** | **6** | **13.0%** | **5** | **1** | **Generación reportes** |
| **MOD_Dashboard** | **DSH** | **6** | **13.0%** | **3** | **3** | **Visualización widgets** |
| MOD_Alerts | ALR | 6 | 13.0% | 6 | 0 | Alertas internas |
| MOD_Audit | AUD | 4 | 8.7% | 4 | 0 | Auditoría funcional |
| MOD_Logs | LOG | 2 | 4.3% | 2 | 0 | Logs técnicos |
| **TOTAL** | - | **46** | **100%** | **42** | **4** | - |

**Cambios v5.2.1 → v6.0.0:**
- ⭐ **MOD_Dashboard separado** (antes parte de MOD_Reports)
- ⭐ **MOD_Reports redefinido** (6 funciones con enfoque CRUD)
- ⭐ **4 funciones planificadas** documentadas en roadmap

### 2.3 Arquitectura de Apps Django

```
src/callcentersite/
├── apps/
│   ├── auth/              # MOD_Auth (4 funciones)
│   ├── users/             # MOD_Users (9 funciones)
│   ├── access/            # MOD_Access (5 funciones) - RBAC core
│   ├── pipeline/          # MOD_Pipeline (4 funciones)
│   ├── reports/           # MOD_Reports (6 funciones) ⭐
│   ├── dashboard/         # MOD_Dashboard (6 funciones) ⭐ NUEVO
│   ├── alerts/            # MOD_Alerts (6 funciones)
│   ├── audit/             # MOD_Audit (4 funciones)
│   └── logs/              # MOD_Logs (2 funciones)
│
├── middleware/            # RBAC middleware
└── settings/              # Configuración
```

**Nota:** Según RESTRICCIONES_IACT v1.0.0:
- ✅ Arquitectura 100% on-premise tradicional (CNST-014)
- ✅ Sin Redis (CNST-010)
- ✅ Sin Celery (CNST-013)
- ✅ Sin Docker en producción (CNST-014)

---

<a name="3-catalogo-funciones"></a>

## 3. CATÁLOGO DE 46 FUNCIONES

### 3.1 MOD_Auth (4 funciones)

**Propósito:** Gestión de sesiones y autenticación del sistema.

**Restricciones aplicables:**
- CNST-005: Autenticación (Token/Session, PBKDF2)
- CNST-001: NO Email (recuperación con 3 preguntas seguridad)

| code | permission_django | display_name | status | use_cases | description |
|------|-------------------|--------------|--------|-----------|-------------|
| **AUTH_LOGIN** | `auth.login` | Iniciar Sesión | activo | UC_001 | Inicia sesión en el sistema con usuario y contraseña. Valida credenciales con PBKDF2 y genera token de sesión |
| **AUTH_LOGOUT** | `auth.logout` | Cerrar Sesión | activo | UC_002 | Cierra la sesión activa del usuario. Invalida token y registra en auditoría |
| **AUTH_RECOVER** | `auth.recover_password` | Recuperar Contraseña | activo | UC_003 | Recupera contraseña mediante 3 preguntas de seguridad. NO usa email (CNST-001) |
| **AUTH_SESSIONS** | `auth.manage_sessions` | Gestionar Sesiones | activo | UC_004 | Gestiona sesiones activas del sistema. Puede cerrar sesiones de otros usuarios (solo admin) |

**Casos de Uso relacionados:**
- UC_001: Iniciar Sesión
- UC_002: Cerrar Sesión
- UC_003: Recuperar Contraseña
- UC_004: Gestionar Sesiones Activas

---

### 3.2 MOD_Users (9 funciones)

**Propósito:** Gestión completa del ciclo de vida de usuarios.

**Restricciones aplicables:**
- CNST-005: Bloqueo por intentos fallidos (3 intentos → 15 min)
- CNST-021: RBAC obligatorio en todas las operaciones

| code | permission_django | display_name | status | use_cases | description |
|------|-------------------|--------------|--------|-----------|-------------|
| **USR_VIEW** | `users.view_user` | Ver Usuarios | activo | UC_005 | Ve lista de usuarios del sistema con filtros por estado, rol, fecha creación |
| **USR_CREATE** | `users.add_user` | Crear Usuarios | activo | UC_006 | Crea nuevos usuarios. Valida contraseña mínimo 12 caracteres (CNST-005) |
| **USR_EDIT** | `users.change_user` | Editar Usuarios | activo | UC_006 | Edita información de usuarios existentes (nombre, email, estado, etc) |
| **USR_DELETE** | `users.delete_user` | Eliminar Usuarios | activo | UC_006 | Elimina usuarios del sistema (soft delete). Audita la operación |
| **USR_PASS** | `users.change_password` | Cambiar Contraseña | activo | UC_007 | Cambia la contraseña propia del usuario autenticado |
| **USR_RESET** | `users.reset_password` | Resetear Contraseña | activo | UC_008 | Resetea contraseña de otro usuario (solo admin). Genera contraseña temporal |
| **USR_LOCK** | `users.lock_user` | Bloquear Usuario | activo | UC_009 | Bloquea usuario manualmente o por intentos fallidos (CNST-005: 3 intentos → 15 min) |
| **USR_UNLOCK** | `users.unlock_user` | Desbloquear Usuario | activo | UC_009 | Desbloquea usuario previamente bloqueado. Resetea contador de intentos |
| **USR_PROFILE** | `users.view_profile` | Ver Perfil | activo | UC_010 | Ve perfil completo de usuario (propio o de otros según permisos) |

**Casos de Uso relacionados:**
- UC_005: Listar Usuarios
- UC_006: Gestionar Usuarios (CRUD)
- UC_007: Cambiar Contraseña Propia
- UC_008: Resetear Contraseña de Otro
- UC_009: Bloquear/Desbloquear Usuario
- UC_010: Ver Perfil de Usuario

---

### 3.3 MOD_Access (5 funciones)

**Propósito:** Core del sistema RBAC. Gestión de funciones, grupos y reglas SoD.

**Restricciones aplicables:**
- CNST-021: RBAC con 46 funciones, 9 módulos, 3 reglas SoD
- CNST-031: Auditoría immutable de cambios de permisos

| code | permission_django | display_name | status | use_cases | description |
|------|-------------------|--------------|--------|-----------|-------------|
| **ACC_ASSIGN** | `access.assign_functions` | Asignar Funciones | activo | UC_011 | Asigna funciones RBAC a usuarios. Valida reglas SoD antes de asignar. Audita cambio |
| **ACC_REVOKE** | `access.revoke_functions` | Revocar Funciones | activo | UC_012 | Revoca funciones previamente asignadas. Audita cambio |
| **ACC_VIEW_PERM** | `access.view_permissions` | Ver Permisos | activo | UC_013 | Ve permisos asignados a usuarios. Muestra funciones activas y grupos |
| **ACC_GROUPS** | `access.manage_groups` | Gestionar Grupos | activo | UC_014 | Gestiona grupos de funciones (AGR-001 a AGR-010). Puede crear/editar/eliminar grupos |
| **ACC_SOD** | `access.view_separation` | Ver Reglas SoD | activo | UC_015 | Ve reglas de separación de funciones. Muestra conflictos detectados |

**Casos de Uso relacionados:**
- UC_011: Asignar Funciones a Usuario
- UC_012: Revocar Funciones de Usuario
- UC_013: Ver Permisos de Usuario
- UC_014: Gestionar Grupos de Funciones
- UC_015: Ver Reglas de Separación (SoD)

---

### 3.4 MOD_Pipeline (4 funciones)

**Propósito:** Supervisión y control del proceso ETL del sistema.

**Restricciones aplicables:**
- CNST-019: ETL con APScheduler (6-12h), timeout 30 min, proceso idempotente
- CNST-002: BD IVR readonly, BD Analytics write

| code | permission_django | display_name | status | use_cases | description |
|------|-------------------|--------------|--------|-----------|-------------|
| **PIP_VIEW** | `pipeline.view_job` | Ver Jobs ETL | activo | UC_016 | Ve estado de jobs ETL (pendiente, ejecutando, completado, fallido). Muestra última ejecución |
| **PIP_EXEC** | `pipeline.execute_job` | Ejecutar Jobs | activo | UC_035 | Ejecuta jobs ETL manualmente. Valida que no haya otro job corriendo (CNST-019) |
| **PIP_STOP** | `pipeline.stop_job` | Detener Jobs | activo | UC_036 | Detiene jobs ETL en ejecución. Marca como "cancelado" y audita |
| **PIP_LOGS** | `pipeline.view_logs` | Ver Logs Jobs | activo | UC_016 | Ve logs detallados de ejecución ETL. Muestra errores, warnings y estadísticas |

**Casos de Uso relacionados:**
- UC_016: Consultar Estado del Pipeline ETL
- UC_035: Ejecutar Pipeline ETL Manualmente
- UC_036: Detener Ejecución del Pipeline

---

### 3.5 MOD_Reports (6 funciones) ⭐ ACTUALIZADO

**Propósito:** Generación y exportación de reportes del sistema.

**Restricciones aplicables:**
- CNST-007: Límites de exportación (CSV: 100K, Excel: 50K, PDF: 10K)
- CNST-022: 3 tipos de reportes (Abandonadas, Clientes, Performance)
- CNST-025: SLA (reportes ligeros <5s, pesados <30s)

**Arquitectura:** Según documento URLS_REPORTES_Y_DASHBOARDS.md

```
apps/reports/
  Endpoints: POST /api/v1/reports/{tipo}/
             GET  /api/v1/reports/{tipo}/
             GET  /api/v1/reports/{tipo}/{id}/
             POST /api/v1/reports/{tipo}/{id}/export/
```

| code | permission_django | display_name | status | use_cases | description |
|------|-------------------|--------------|--------|-----------|-------------|
| **RPT_VIEW** | `reports.view` | Ver Reportes | activo | UC_017, UC_018, UC_019 | Ve reportes tabulares del sistema. Incluye: Llamadas Abandonadas (RPT-TR-021), Clientes Únicos (RPT-TR-011), Promedio Clientes (RPT-TR-031), Clientes Menú (RPT-TR-041), Llamadas por Menú (RPT-TR-121), Detalle Transferencias (RPT-DET-001), Menú con Errores (RPT-ERR-001) |
| **RPT_CREATE** | `reports.create` | Crear Reporte | activo | UC_017 | Crea configuración de reporte. Define filtros (trimestre, DID, menú, rango fechas). POST /api/v1/reports/{tipo}/ |
| **RPT_DELETE** | `reports.delete` | Eliminar Reporte | activo | - | Elimina reportes antiguos del sistema. Solo reportes propios o con permisos admin |
| **RPT_EXP_CSV** | `reports.export.csv` | Exportar CSV | activo | UC_022 | Exporta reportes a formato CSV. Límite: 100K registros (CNST-007). POST /api/v1/reports/{tipo}/{id}/export/ con format=csv |
| **RPT_EXP_EXCEL** | `reports.export.excel` | Exportar Excel | activo | UC_023 | Exporta reportes a formato Excel. Límite: 50K registros (CNST-007). POST /api/v1/reports/{tipo}/{id}/export/ con format=excel |
| **RPT_EXP_PDF** | `reports.export.pdf` | Exportar PDF | planificado | UC_024 | Exporta reportes a formato PDF. Límite: 10K registros (CNST-007). Funcionalidad planificada para versión futura |

**Tipos de reportes soportados:**
1. **RPT-TR-021:** Llamadas Abandonadas (trimestral)
2. **RPT-TR-011:** Clientes Únicos por DID (trimestral)
3. **RPT-TR-031:** Promedio Clientes Únicos (trimestral)
4. **RPT-TR-041:** Promedio Clientes Menú (trimestral)
5. **RPT-TR-121:** Llamadas por Menú (trimestral)
6. **RPT-DET-001:** Detalle Transferencias (mensual)
7. **RPT-ERR-001:** cMenu con Errores (anual)

**Casos de Uso relacionados:**
- UC_017: Generar Reporte de Llamadas Abandonadas
- UC_018: Generar Reporte de Análisis de Clientes
- UC_019: Generar Reporte de Performance IVR
- UC_020: Aplicar Filtros a Reportes
- UC_021: Filtrar por Período de Tiempo
- UC_022: Exportar Reporte a CSV
- UC_023: Exportar Reporte a Excel
- UC_024: Exportar Reporte a PDF (planificado)

**Cambios respecto a v5.2.1:**
- ❌ Eliminado: `RPT_FILTER` (filtrado integrado en RPT_VIEW)
- ✅ Agregado: `RPT_CREATE` (creación explícita de reporte)
- ✅ Agregado: `RPT_DELETE` (gestión CRUD completa)
- ✅ Actualizado: permission_django usa formato `reports.export.csv` (con punto)

---

### 3.6 MOD_Dashboard (6 funciones) ⭐ NUEVO MÓDULO

**Propósito:** Visualización de métricas y widgets interactivos.

**Restricciones aplicables:**
- CNST-023: Dashboards con datos estáticos (6-12h desfase), cache 5 min locmem, NO auto-refresh
- CNST-003: NO real-time (no WebSockets, no SSE, no polling)

**Arquitectura:** Según documento URLS_REPORTES_Y_DASHBOARDS.md

```
apps/dashboard/
  Endpoints: GET  /api/v1/dashboard/{tipo}/
             POST /api/v1/dashboard/{tipo}/export/
```

| code | permission_django | display_name | status | use_cases | description |
|------|-------------------|--------------|--------|-----------|-------------|
| **DSH_VIEW** | `dashboard.view` | Ver Dashboard | activo | UC_025 | Ve dashboards del sistema con widgets predefinidos. Incluye KPIs estáticos, gráficos (barras, líneas, torta) y tablas. Dashboards disponibles: Métricas Trimestrales (DASH-TRIM), Análisis Clientes (DASH-CLI), Performance IVR (DASH-IVR). Datos desfasados 6-12h (CNST-023) |
| **DSH_EXP_CSV** | `dashboard.export.csv` | Exportar Dashboard CSV | activo | - | Exporta snapshot actual del dashboard a formato CSV. Incluye todos los widgets visibles. POST /api/v1/dashboard/{tipo}/export/ con format=csv |
| **DSH_EXP_EXCEL** | `dashboard.export.excel` | Exportar Dashboard Excel | activo | - | Exporta snapshot actual del dashboard a formato Excel con formato y gráficos. POST /api/v1/dashboard/{tipo}/export/ con format=excel |
| **DSH_EXP_PDF** | `dashboard.export.pdf` | Exportar Dashboard PDF | planificado | - | Exporta snapshot actual del dashboard a formato PDF. Funcionalidad planificada para versión futura |
| **DSH_SHARE** | `dashboard.share` | Compartir Dashboard | planificado | - | Comparte dashboard con otros usuarios mediante enlace interno. Funcionalidad planificada para versión futura |
| **DSH_EDIT** | `dashboard.edit` | Editar Dashboard | planificado | - | Edita configuración de widgets del dashboard (posición, tamaño, filtros). Funcionalidad planificada para versión futura |

**Dashboards disponibles:**
1. **DASH-TRIM:** Métricas Trimestrales
   - KPIs: Total llamadas, tasa abandono, clientes únicos
   - Charts: Top 10 menús, tendencia trimestral
   - Table: Detalle por DID

2. **DASH-CLI:** Análisis de Clientes
   - KPIs: Clientes únicos, promedio por menú, recurrentes
   - Charts: Distribución por menú (pie), tendencia clientes (line)
   - Table: Top clientes

3. **DASH-IVR:** Performance IVR
   - KPIs: Total llamadas, tasa éxito transferencia, menús con error
   - Charts: Llamadas por menú (bar), distribución transferencias (pie)
   - Table: Errores detectados, últimos errores

**Casos de Uso relacionados:**
- UC_025: Visualizar Dashboard de Métricas
- UC_027: Ver Gráfico de Barras
- UC_028: Ver Gráfico de Líneas
- UC_029: Ver Gráfico de Torta

**Separación de MOD_Reports:**
```
ANTES v5.2.1 (MOD_Reports):
  - RPT-002: ve_dashboard
  - RPT-007: ve_kpis
  - RPT-008: ve_graficos

DESPUÉS v6.0.0 (MOD_Dashboard):
  - DSH_VIEW: dashboard.view (incluye KPIs y gráficos)
  - DSH_EXP_CSV: dashboard.export.csv (nueva funcionalidad)
  - DSH_EXP_EXCEL: dashboard.export.excel (nueva funcionalidad)
```

**Justificación separación:**
- ✅ Apps Django separadas (apps/reports/ vs apps/dashboard/)
- ✅ Endpoints diferentes (/api/v1/reports/ vs /api/v1/dashboard/)
- ✅ Permisos independientes (reports.* vs dashboard.*)
- ✅ Responsabilidad única (generación vs visualización)
- ✅ Cumplimiento principio SOLID (CNST-017)

---

### 3.7 MOD_Alerts (6 funciones)

**Propósito:** Sistema de alertas internas (buzón interno).

**Restricciones aplicables:**
- CNST-001: NO Email (solo buzón interno)
- CNST-024: Límite 50 destinatarios por alerta, retención 90 días

| code | permission_django | display_name | status | use_cases | description |
|------|-------------------|--------------|--------|-----------|-------------|
| **ALR_VIEW** | `alerts.view_alert` | Ver Alertas | activo | UC_030 | Ve alertas del buzón interno del usuario. Muestra alertas no leídas con prioridad |
| **ALR_CONF** | `alerts.configure_alert` | Configurar Alerta | activo | UC_031 | Configura alertas automáticas del sistema (umbrales, condiciones). Solo admin |
| **ALR_SEND** | `alerts.send_alert` | Enviar Alerta | activo | UC_032 | Envía alertas manuales a destinatarios (máx 50, CNST-024). Solo buzón interno (CNST-001) |
| **ALR_SUBS** | `alerts.manage_subscriptions` | Gestionar Suscripciones | activo | UC_033 | Gestiona suscripciones a tipos de alertas (informativa, advertencia, crítica) |
| **ALR_MARK** | `alerts.mark_read` | Marcar Leída | activo | UC_034 | Marca alerta como leída. Actualiza timestamp de lectura |
| **ALR_DELETE** | `alerts.delete_alert` | Eliminar Alerta | activo | UC_037 | Elimina alertas antiguas (>90 días automático, manual con permisos) |

**Casos de Uso relacionados:**
- UC_030: Ver Alertas Recibidas
- UC_031: Configurar Alerta Automática
- UC_032: Enviar Alerta Manual
- UC_033: Gestionar Suscripciones a Alertas
- UC_034: Marcar Alerta como Leída
- UC_037: Eliminar Alertas Antiguas

---

### 3.8 MOD_Audit (4 funciones)

**Propósito:** Auditoría funcional del sistema con log immutable.

**Restricciones aplicables:**
- CNST-031: Auditoría immutable (append-only), retención 2 años mínimo, checksum SHA-256

| code | permission_django | display_name | status | use_cases | description |
|------|-------------------|--------------|--------|-----------|-------------|
| **AUD_VIEW** | `audit.view_log` | Ver Auditoría | activo | UC_038 | Ve logs de auditoría del sistema. Muestra eventos críticos (login, cambios permisos, exportaciones) |
| **AUD_SEARCH** | `audit.search_log` | Buscar Auditoría | activo | UC_039 | Busca eventos específicos en auditoría por usuario, fecha, acción, resultado |
| **AUD_EXP** | `audit.export_log` | Exportar Auditoría | activo | UC_040 | Exporta logs de auditoría a CSV/Excel para análisis externo. Mantiene checksums (CNST-031) |
| **AUD_COMPLIANCE** | `audit.generate_compliance` | Generar Compliance | activo | UC_049 | Genera reporte de cumplimiento normativo. Valida integridad con checksums SHA-256 |

**Casos de Uso relacionados:**
- UC_038: Consultar Log de Auditoría
- UC_039: Buscar Eventos en Auditoría
- UC_040: Exportar Log de Auditoría
- UC_049: Generar Reporte de Cumplimiento

---

### 3.9 MOD_Logs (2 funciones)

**Propósito:** Logs técnicos del sistema (errores, warnings, debug).

**Restricciones aplicables:**
- CNST-030: Logging en filesystem rotating (10MB x 10 archivos), formato JSON, sin PII

| code | permission_django | display_name | status | use_cases | description |
|------|-------------------|--------------|--------|-----------|-------------|
| **LOG_VIEW** | `logs.view_technical` | Ver Logs Técnicos | activo | UC_041 | Ve logs técnicos del sistema (ERROR, WARNING, INFO). No incluye DEBUG en producción (CNST-030) |
| **LOG_EXP** | `logs.export_logs` | Exportar Logs | activo | UC_042 | Exporta logs técnicos para análisis externo. Sanitiza PII antes de exportar |

**Casos de Uso relacionados:**
- UC_041: Ver Logs Técnicos
- UC_042: Exportar Logs Técnicos

---

### 3.10 Resumen del Catálogo

```
┌────────────────────────────────────────────────────────────────┐
│           CATÁLOGO COMPLETO DE FUNCIONES v6.0.0                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Total Funciones:         46                                   │
│  ├─ Activas:              42 (91.3%)                          │
│  └─ Planificadas:         4  (8.7%)                           │
│                                                                │
│  Por Módulo:                                                   │
│  ├─ MOD_Auth:             4  (8.7%)                           │
│  ├─ MOD_Users:            9  (19.6%)                          │
│  ├─ MOD_Access:           5  (10.9%)                          │
│  ├─ MOD_Pipeline:         4  (8.7%)                           │
│  ├─ MOD_Reports:          6  (13.0%) - 5 activas, 1 planif   │
│  ├─ MOD_Dashboard:        6  (13.0%) - 3 activas, 3 planif   │
│  ├─ MOD_Alerts:           6  (13.0%)                          │
│  ├─ MOD_Audit:            4  (8.7%)                           │
│  └─ MOD_Logs:             2  (4.3%)                           │
│                                                                │
│  Funciones Planificadas:                                       │
│  ├─ RPT_EXP_PDF:          reports.export.pdf                  │
│  ├─ DSH_EXP_PDF:          dashboard.export.pdf                │
│  ├─ DSH_SHARE:            dashboard.share                     │
│  └─ DSH_EDIT:             dashboard.edit                      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

<a name="4-grupos"></a>

## 4. LOS 10 GRUPOS DE FUNCIONES

### 4.1 Concepto de Grupos

Los **Grupos de Funciones (Function Groups)** agrupan funciones relacionadas para asignación masiva a usuarios. Simplifican la gestión de permisos.

**Características:**
- ✅ **No son roles jerárquicos** (Flat RBAC)
- ✅ **Composables:** Un usuario puede tener múltiples grupos
- ✅ **Transparentes:** Usuario no ve "grupos", solo funciones efectivas
- ✅ **Auditables:** Cambios en grupos se auditan

### 4.2 Catálogo de Grupos

#### AGR-001: Operador Básico

**Perfil:** Usuario con acceso mínimo al sistema.

**Funciones incluidas (7):**
```yaml
Auth:
  - AUTH_LOGIN: Iniciar sesión
  - AUTH_LOGOUT: Cerrar sesión

Reports:
  - RPT_VIEW: Ver reportes

Dashboard:
  - DSH_VIEW: Ver dashboards ⭐ ACTUALIZADO

Alerts:
  - ALR_VIEW: Ver alertas
  - ALR_MARK: Marcar alertas leídas

Users:
  - USR_PROFILE: Ver perfil propio
```

**Casos de Uso típicos:**
- Consultar reportes ya generados
- Ver dashboards del sistema
- Revisar alertas recibidas

**Cambio v5.2.1 → v6.0.0:**
- ✅ Agregado: `DSH_VIEW` (antes `RPT-002`)

---

#### AGR-002: Analista Junior

**Perfil:** Analista con capacidad de generar y exportar reportes.

**Funciones incluidas (12):**
```yaml
Auth:
  - AUTH_LOGIN, AUTH_LOGOUT

Reports:
  - RPT_VIEW: Ver reportes
  - RPT_CREATE: Crear reportes ⭐ NUEVO
  - RPT_EXP_CSV: Exportar CSV ⭐ ACTUALIZADO

Dashboard:
  - DSH_VIEW: Ver dashboards ⭐ ACTUALIZADO
  - DSH_EXP_CSV: Exportar dashboard CSV ⭐ NUEVO

Alerts:
  - ALR_VIEW, ALR_MARK, ALR_DELETE

Users:
  - USR_PROFILE, USR_PASS
```

**Casos de Uso típicos:**
- Generar reportes trimestrales
- Exportar datos a CSV
- Exportar snapshots de dashboards

**Cambios v5.2.1 → v6.0.0:**
- ✅ Agregado: `RPT_CREATE`
- ✅ Agregado: `DSH_VIEW`, `DSH_EXP_CSV`
- ✅ Actualizado: `RPT_EXP_CSV` (antes `RPT-004`)

---

#### AGR-003: Analista Senior

**Perfil:** Analista con acceso completo a reportes y dashboards.

**Funciones incluidas (16):**
```yaml
Auth:
  - AUTH_LOGIN, AUTH_LOGOUT, AUTH_RECOVER

Reports (todas activas):
  - RPT_VIEW: Ver reportes
  - RPT_CREATE: Crear reportes
  - RPT_DELETE: Eliminar reportes ⭐ NUEVO
  - RPT_EXP_CSV: Exportar CSV
  - RPT_EXP_EXCEL: Exportar Excel ⭐ ACTUALIZADO

Dashboard (todas activas):
  - DSH_VIEW: Ver dashboards ⭐ ACTUALIZADO
  - DSH_EXP_CSV: Exportar CSV ⭐ NUEVO
  - DSH_EXP_EXCEL: Exportar Excel ⭐ NUEVO

Pipeline:
  - PIP_VIEW: Ver jobs ETL
  - PIP_LOGS: Ver logs ETL

Alerts:
  - ALR_VIEW, ALR_MARK, ALR_DELETE

Users:
  - USR_PROFILE, USR_PASS
```

**Casos de Uso típicos:**
- Generar y exportar reportes complejos
- Analizar performance del sistema ETL
- Exportar dashboards en múltiples formatos

**Cambios v5.2.1 → v6.0.0:**
- ✅ Agregado: `RPT_DELETE`, `DSH_VIEW`, `DSH_EXP_CSV`, `DSH_EXP_EXCEL`
- ✅ Actualizado: `RPT_EXP_EXCEL` (antes `RPT-005`)

---

#### AGR-004: Administrador de Usuarios

**Perfil:** Gestiona usuarios del sistema (CRUD completo).

**Funciones incluidas (14):**
```yaml
Auth:
  - AUTH_LOGIN, AUTH_LOGOUT, AUTH_SESSIONS

Users (todas):
  - USR_VIEW, USR_CREATE, USR_EDIT, USR_DELETE
  - USR_RESET, USR_LOCK, USR_UNLOCK
  - USR_PROFILE, USR_PASS

Access:
  - ACC_VIEW_PERM: Ver permisos

Alerts:
  - ALR_VIEW, ALR_MARK
```

**Casos de Uso típicos:**
- Crear y editar usuarios
- Resetear contraseñas
- Bloquear/desbloquear usuarios

**Regla SoD aplicable:**
- ⚠️ **NO puede tener:** `AUD_VIEW` (user_audit_separation)

---

#### AGR-005: Gestor de Acceso

**Perfil:** Administra permisos RBAC (asignar/revocar funciones).

**Funciones incluidas (10):**
```yaml
Auth:
  - AUTH_LOGIN, AUTH_LOGOUT

Access (todas):
  - ACC_ASSIGN, ACC_REVOKE, ACC_VIEW_PERM
  - ACC_GROUPS, ACC_SOD

Users:
  - USR_VIEW, USR_PROFILE

Alerts:
  - ALR_VIEW, ALR_MARK
```

**Casos de Uso típicos:**
- Asignar funciones a usuarios
- Gestionar grupos de funciones
- Validar reglas SoD

**Regla SoD aplicable:**
- ⚠️ **NO puede tener:** `AUD_VIEW` (access_audit_separation)

---

#### AGR-006: Auditor

**Perfil:** Acceso readonly a auditoría y logs.

**Funciones incluidas (10):**
```yaml
Auth:
  - AUTH_LOGIN, AUTH_LOGOUT

Audit (todas):
  - AUD_VIEW, AUD_SEARCH, AUD_EXP
  - AUD_COMPLIANCE

Logs (todas):
  - LOG_VIEW, LOG_EXP

Alerts:
  - ALR_VIEW, ALR_MARK
```

**Casos de Uso típicos:**
- Revisar logs de auditoría
- Generar reportes de cumplimiento
- Exportar logs para análisis

**Reglas SoD aplicables:**
- ⚠️ **NO puede tener:** `ACC_ASSIGN`, `ACC_REVOKE` (access_audit_separation)
- ⚠️ **NO puede tener:** `USR_CREATE`, `USR_EDIT` (user_audit_separation)
- ⚠️ **NO puede tener:** `PIP_EXEC`, `PIP_STOP` (pipeline_audit_separation)

---

#### AGR-007: Supervisor Pipeline

**Perfil:** Supervisa y controla proceso ETL.

**Funciones incluidas (9):**
```yaml
Auth:
  - AUTH_LOGIN, AUTH_LOGOUT

Pipeline (todas):
  - PIP_VIEW, PIP_EXEC, PIP_STOP, PIP_LOGS

Alerts:
  - ALR_VIEW, ALR_CONF, ALR_SEND

Users:
  - USR_PROFILE
```

**Casos de Uso típicos:**
- Monitorear ejecución ETL
- Ejecutar/detener jobs manualmente
- Configurar alertas de pipeline

**Regla SoD aplicable:**
- ⚠️ **NO puede tener:** `AUD_VIEW` (pipeline_audit_separation)

---

#### AGR-008: Gestor de Alertas

**Perfil:** Administra sistema de alertas internas.

**Funciones incluidas (10):**
```yaml
Auth:
  - AUTH_LOGIN, AUTH_LOGOUT

Alerts (todas):
  - ALR_VIEW, ALR_CONF, ALR_SEND
  - ALR_SUBS, ALR_MARK, ALR_DELETE

Users:
  - USR_VIEW, USR_PROFILE

Reports:
  - RPT_VIEW
```

**Casos de Uso típicos:**
- Configurar alertas automáticas
- Enviar alertas manuales
- Gestionar suscripciones

---

#### AGR-009: Soporte Técnico

**Perfil:** Soporte de primer nivel.

**Funciones incluidas (15):**
```yaml
Auth:
  - AUTH_LOGIN, AUTH_LOGOUT, AUTH_RECOVER
  - AUTH_SESSIONS

Users:
  - USR_VIEW, USR_RESET, USR_LOCK
  - USR_UNLOCK, USR_PROFILE

Reports:
  - RPT_VIEW

Dashboard:
  - DSH_VIEW ⭐ ACTUALIZADO

Logs:
  - LOG_VIEW

Alerts:
  - ALR_VIEW, ALR_MARK
```

**Casos de Uso típicos:**
- Resetear contraseñas de usuarios
- Desbloquear usuarios
- Ver logs técnicos

**Cambios v5.2.1 → v6.0.0:**
- ✅ Agregado: `DSH_VIEW` (antes `RPT-002`)

---

#### AGR-010: Administrador Total

**Perfil:** Acceso completo al sistema (excepto restricciones SoD).

**Funciones incluidas (42 activas):**
```yaml
Todas las funciones activas de los 9 módulos.
NO incluye funciones planificadas.
```

**Casos de Uso típicos:**
- Administración completa del sistema
- Gestión de crisis
- Configuración global

**Restricciones:**
- ⚠️ Debe respetar reglas SoD
- ⚠️ Todas las acciones se auditan
- ⚠️ Permisos temporales si es necesario

**Cambios v5.2.1 → v6.0.0:**
- ✅ Incluye nuevas funciones activas de MOD_Reports y MOD_Dashboard

---

### 4.3 Tabla Resumen de Grupos

| Grupo | Código | Funciones | Módulos | Perfil |
|-------|--------|-----------|---------|--------|
| Operador Básico | AGR-001 | 7 | Auth, Reports, Dashboard, Alerts, Users | Consulta básica |
| Analista Junior | AGR-002 | 12 | +Reports (export), +Dashboard (export) | Análisis con exportación |
| Analista Senior | AGR-003 | 16 | +Pipeline, más exportaciones | Análisis avanzado |
| Admin Usuarios | AGR-004 | 14 | Auth, Users (todas), Access | CRUD usuarios |
| Gestor Acceso | AGR-005 | 10 | Access (todas), Users | RBAC management |
| Auditor | AGR-006 | 10 | Audit, Logs | Solo lectura auditoría |
| Supervisor Pipeline | AGR-007 | 9 | Pipeline (todas), Alerts | Control ETL |
| Gestor Alertas | AGR-008 | 10 | Alerts (todas) | Config alertas |
| Soporte Técnico | AGR-009 | 15 | Auth, Users, Logs | Soporte nivel 1 |
| Admin Total | AGR-010 | 42 | Todos | Admin completo |

---

<a name="5-sod"></a>

## 5. SEPARACIÓN DE FUNCIONES (SoD)

### 5.1 Concepto de Separación de Funciones

**Separation of Duties (SoD)** previene que un usuario tenga funciones conflictivas que juntas podrían permitir fraude o abuso.

**Ejemplo clásico:**
```
❌ Usuario NO puede tener:
   - ACC_ASSIGN (asignar permisos) Y
   - AUD_VIEW (ver auditoría)

Razón: Podría asignarse permisos y ocultar el cambio en auditoría
```

### 5.2 Reglas SoD Implementadas

#### Regla 1: access_audit_separation

**Conflicto:** Gestión de acceso + Auditoría

```yaml
Grupo A (Access):
  - ACC_ASSIGN: Asignar funciones
  - ACC_REVOKE: Revocar funciones
  - ACC_GROUPS: Gestionar grupos

Grupo B (Audit):
  - AUD_VIEW: Ver auditoría
  - AUD_SEARCH: Buscar en auditoría
  - AUD_EXP: Exportar auditoría

Regla: Usuario NO puede tener funciones de ambos grupos
```

**Razón:** Quien gestiona permisos NO debe ver su propia auditoría (conflicto de interés).

**Grupos afectados:**
- AGR-005 (Gestor Acceso): Tiene Grupo A → ❌ NO puede tener Grupo B
- AGR-006 (Auditor): Tiene Grupo B → ❌ NO puede tener Grupo A

---

#### Regla 2: user_audit_separation

**Conflicto:** Gestión de usuarios + Auditoría

```yaml
Grupo A (Users):
  - USR_CREATE: Crear usuarios
  - USR_EDIT: Editar usuarios
  - USR_DELETE: Eliminar usuarios
  - USR_RESET: Resetear contraseñas

Grupo B (Audit):
  - AUD_VIEW: Ver auditoría
  - AUD_SEARCH: Buscar en auditoría

Regla: Usuario NO puede tener funciones de ambos grupos
```

**Razón:** Quien gestiona usuarios NO debe ver auditoría de sus propias acciones.

**Grupos afectados:**
- AGR-004 (Admin Usuarios): Tiene Grupo A → ❌ NO puede tener Grupo B
- AGR-006 (Auditor): Tiene Grupo B → ❌ NO puede tener Grupo A

---

#### Regla 3: pipeline_audit_separation

**Conflicto:** Control de pipeline + Auditoría

```yaml
Grupo A (Pipeline):
  - PIP_EXEC: Ejecutar jobs ETL
  - PIP_STOP: Detener jobs ETL

Grupo B (Audit):
  - AUD_VIEW: Ver auditoría
  - AUD_COMPLIANCE: Generar compliance

Regla: Usuario NO puede tener funciones de ambos grupos
```

**Razón:** Quien controla ETL NO debe auditar su propia ejecución.

**Grupos afectados:**
- AGR-007 (Supervisor Pipeline): Tiene Grupo A → ❌ NO puede tener Grupo B
- AGR-006 (Auditor): Tiene Grupo B → ❌ NO puede tener Grupo A

---

### 5.3 Validación de Reglas SoD

**Cuándo se valida:**
```python
# Al asignar funciones individuales
UserFunctionAssignment.objects.create(
    user=user,
    function=function
)
# → Valida SoD antes de guardar

# Al asignar grupos
UserFunctionGroupAssignment.objects.create(
    user=user,
    group=group
)
# → Valida SoD considerando funciones del grupo
```

**Comportamiento:**
```python
if sod_conflict_detected:
    raise ValidationError(
        f"Conflicto SoD detectado: {rule_name}. "
        f"Usuario ya tiene funciones del grupo conflictivo."
    )
```

**Auditoría:**
```python
# Todos los intentos de violación SoD se auditan
AuditLog.objects.create(
    user=requesting_user,
    action='assign_function',
    success=False,
    error_message=f'SoD violation: {rule_name}'
)
```

---

<a name="6-permisos-temporales"></a>

## 6. PERMISOS TEMPORALES

### 6.1 Concepto

Los **permisos temporales** permiten asignar funciones a un usuario por un período limitado con justificación obligatoria.

**Casos de uso:**
- Reemplazo temporal de empleado ausente
- Proyecto específico con duración definida
- Acceso de auditoría externa temporal

### 6.2 Características

```yaml
Duración máxima: 6 meses (CNST-021)
Justificación: Obligatoria, mínimo 20 caracteres
Aprobación: Requiere aprobador con ACC_ASSIGN
Auditoría: Se registra inicio, fin y razón
Renovación: Requiere nueva justificación
Revocación: Automática al expirar o manual
```

### 6.3 Modelo de Datos

```python
class UserFunctionAssignment(models.Model):
    """Asignación de función a usuario (puede ser temporal)."""
    
    user = models.ForeignKey(User)
    function = models.ForeignKey(Function)
    
    # Temporal
    is_temporary = models.BooleanField(default=False)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Justificación
    justification = models.TextField(
        null=True,
        blank=True,
        help_text="Obligatorio si is_temporary=True. Mínimo 20 caracteres."
    )
    
    # Aprobación
    approved_by = models.ForeignKey(
        User,
        related_name='permissions_approved',
        null=True
    )
    approved_at = models.DateTimeField(null=True)
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        related_name='permissions_created'
    )
    
    revoked_at = models.DateTimeField(null=True)
    revoked_by = models.ForeignKey(
        User,
        related_name='permissions_revoked',
        null=True
    )
    revoked_reason = models.TextField(null=True)
    
    class Meta:
        db_table = 'access_user_function_assignments'
        unique_together = [['user', 'function']]
```

### 6.4 Validaciones

```python
def clean(self):
    """Validaciones antes de guardar."""
    
    # 1. Justificación obligatoria si temporal
    if self.is_temporary and not self.justification:
        raise ValidationError(
            "Justificación obligatoria para permisos temporales"
        )
    
    # 2. Justificación mínimo 20 caracteres
    if self.justification and len(self.justification) < 20:
        raise ValidationError(
            "Justificación debe tener mínimo 20 caracteres"
        )
    
    # 3. Duración máxima 6 meses
    if self.is_temporary and self.valid_until:
        max_duration = timedelta(days=180)  # 6 meses
        duration = self.valid_until - self.valid_from
        
        if duration > max_duration:
            raise ValidationError(
                f"Duración máxima: 6 meses. "
                f"Solicitado: {duration.days} días"
            )
    
    # 4. Validar SoD
    self._validate_sod_rules()
```

### 6.5 Proceso de Asignación Temporal

```python
# 1. Usuario con ACC_ASSIGN solicita permiso temporal
assignment = UserFunctionAssignment(
    user=target_user,
    function=Function.objects.get(permission_django='reports.export.excel'),
    is_temporary=True,
    valid_until=timezone.now() + timedelta(days=90),  # 3 meses
    justification="Reemplazo de analista durante licencia médica. "
                  "Necesita exportar reportes mensuales.",
    created_by=requesting_user
)

# 2. Sistema valida
assignment.full_clean()  # Valida duración, justificación, SoD

# 3. Sistema aprueba automáticamente si requesting_user tiene ACC_ASSIGN
assignment.approved_by = requesting_user
assignment.approved_at = timezone.now()

# 4. Guarda y audita
assignment.save()
AuditService.log_permission_change(
    user=requesting_user,
    action='assign_temporary_function',
    target_user=target_user,
    function=assignment.function,
    duration_days=90,
    justification=assignment.justification
)

# 5. Job automático revoca al expirar
# (Scheduler diario ejecuta cleanup)
```

### 6.6 Expiración Automática

```python
# Management command ejecutado diariamente
# python manage.py revoke_expired_permissions

from django.core.management.base import BaseCommand
from apps.access.models import UserFunctionAssignment

class Command(BaseCommand):
    """Revoca permisos temporales expirados."""
    
    def handle(self, *args, **options):
        now = timezone.now()
        
        expired = UserFunctionAssignment.objects.filter(
            is_temporary=True,
            valid_until__lte=now,
            revoked_at__isnull=True
        )
        
        for assignment in expired:
            assignment.revoked_at = now
            assignment.revoked_reason = "Expiración automática"
            assignment.save()
            
            # Auditar
            AuditService.log_permission_change(
                action='auto_revoke_expired',
                user=assignment.user,
                function=assignment.function
            )
        
        self.stdout.write(
            f"Revocados {expired.count()} permisos expirados"
        )
```

---

## FIN PARTE 1/2

**Continúa en:** MODELO_RBAC_IACT_v6_0_0_PARTE_2.md

**Parte 2 incluye:**
- Sección 7: Modelo de Datos
- Sección 8: Implementación SQL
- Sección 9: Implementación Django/DRF
- Sección 10: Mapeo Funciones → Casos de Uso
- Sección 11: Migración v5.1 → v5.2
- Sección 12: Migración v5.2 → v6.0.0
- Sección 13: Roadmap de Funciones

---

**Documento generado:** 2026-01-19  
**Versión:** 6.0.0 PARTE 1/2  
**Estado:** ✅ DEFINITIVO  
**Líneas:** ~1,300  

**Ubicación:** `/tmp/iact-real/docs/rbac/MODELO_RBAC_IACT_v6_0_0_PARTE_1.md`
