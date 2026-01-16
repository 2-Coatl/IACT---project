# Modulos y Casos de Uso - IACT Call Center System

## Estructura del Sistema

### Apps del Sistema

| App | Proposito | Modelos Principales |
|-----|-----------|---------------------|
| `access` | Control de acceso y modulos | Function, Module, UserModuleAccess |
| `audit` | Auditoria de acciones | AuditLog |
| `authentication` | Autenticacion JWT | SecurityQuestion, UserSecurityAnswer |
| `core` | Modelos core del negocio | CallRecord, Center, Service |
| `ivr_legacy` | Sistema IVR legacy | CallLog |
| `pipeline` | Pipeline ETL de datos | ETLExecution |
| `reports` | Generacion de reportes | Report, ExportJob |
| `users` | Gestion de usuarios | (usa User de Django) |

## Jerarquia de Modulos

### Nivel 1: Modulos Principales (Raiz)

```
MOD_Dashboard
MOD_Calls
MOD_Centers
MOD_Services
MOD_Users
MOD_Reports
MOD_Audit
MOD_Access
MOD_Pipeline
MOD_Settings
```

### Nivel 2: Submodulos por Funcionalidad

#### MOD_Dashboard
```
MOD_Dashboard (raiz)
   URL: /dashboard
   Descripcion: Panel principal del sistema
```

#### MOD_Calls - Gestion de Llamadas
```
MOD_Calls (raiz)
   URL: /calls
   Descripcion: Gestion de registros de llamadas
   |
   +-- MOD_Calls_View
   |   URL: /calls/view
   |   Descripcion: Visualizar llamadas
   |
   +-- MOD_Calls_Export
   |   URL: /calls/export
   |   Descripcion: Exportar registros de llamadas
   |
   +-- MOD_Calls_Stats
       URL: /calls/stats
       Descripcion: Estadisticas de llamadas
```

#### MOD_Centers - Gestion de Centros
```
MOD_Centers (raiz)
   URL: /centers
   Descripcion: Gestion de centros de atencion
   |
   +-- MOD_Centers_View
   |   URL: /centers/view
   |   Descripcion: Visualizar centros
   |
   +-- MOD_Centers_Create
   |   URL: /centers/create
   |   Descripcion: Crear centros
   |
   +-- MOD_Centers_Edit
   |   URL: /centers/edit
   |   Descripcion: Editar centros
   |
   +-- MOD_Centers_Delete
       URL: /centers/delete
       Descripcion: Eliminar centros (soft delete)
```

#### MOD_Services - Gestion de Servicios 800
```
MOD_Services (raiz)
   URL: /services
   Descripcion: Gestion de servicios 800
   |
   +-- MOD_Services_View
   |   URL: /services/view
   |   Descripcion: Visualizar servicios
   |
   +-- MOD_Services_Create
   |   URL: /services/create
   |   Descripcion: Crear servicios
   |
   +-- MOD_Services_Edit
   |   URL: /services/edit
   |   Descripcion: Editar servicios
   |
   +-- MOD_Services_Assign
       URL: /services/assign
       Descripcion: Asignar servicios a usuarios
```

#### MOD_Users - Gestion de Usuarios
```
MOD_Users (raiz)
   URL: /users
   Descripcion: Gestion de usuarios del sistema
   |
   +-- MOD_Users_View
   |   URL: /users/view
   |   Descripcion: Visualizar usuarios
   |
   +-- MOD_Users_Create
   |   URL: /users/create
   |   Descripcion: Crear usuarios
   |
   +-- MOD_Users_Edit
   |   URL: /users/edit
   |   Descripcion: Editar usuarios
   |
   +-- MOD_Users_Delete
   |   URL: /users/delete
   |   Descripcion: Eliminar usuarios (soft delete)
   |
   +-- MOD_Users_Permissions
       URL: /users/permissions
       Descripcion: Gestionar permisos de usuarios
```

#### MOD_Reports - Reportes del Sistema
```
MOD_Reports (raiz)
   URL: /reports
   Descripcion: Generacion y gestion de reportes
   |
   +-- MOD_Reports_View
   |   URL: /reports/view
   |   Descripcion: Visualizar reportes
   |
   +-- MOD_Reports_Create
   |   URL: /reports/create
   |   Descripcion: Crear reportes
   |
   +-- MOD_Reports_Export
   |   URL: /reports/export
   |   Descripcion: Exportar reportes (PDF, Excel, CSV)
   |
   +-- MOD_Reports_Schedule
       URL: /reports/schedule
       Descripcion: Programar reportes automaticos
```

#### MOD_Audit - Auditoria
```
MOD_Audit (raiz)
   URL: /audit
   Descripcion: Auditoria de acciones del sistema
   |
   +-- MOD_Audit_View
   |   URL: /audit/view
   |   Descripcion: Visualizar logs de auditoria
   |
   +-- MOD_Audit_Export
       URL: /audit/export
       Descripcion: Exportar logs de auditoria
```

#### MOD_Access - Control de Acceso
```
MOD_Access (raiz)
   URL: /access
   Descripcion: Gestion de modulos y funciones
   |
   +-- MOD_Access_Modules
   |   URL: /access/modules
   |   Descripcion: Gestionar modulos del sistema
   |
   +-- MOD_Access_Functions
   |   URL: /access/functions
   |   Descripcion: Gestionar funciones atomicas
   |
   +-- MOD_Access_Assign
       URL: /access/assign
       Descripcion: Asignar modulos/funciones a usuarios
```

#### MOD_Pipeline - Pipeline ETL
```
MOD_Pipeline (raiz)
   URL: /pipeline
   Descripcion: Pipeline ETL de datos
   |
   +-- MOD_Pipeline_View
   |   URL: /pipeline/view
   |   Descripcion: Visualizar ejecuciones ETL
   |
   +-- MOD_Pipeline_Execute
   |   URL: /pipeline/execute
   |   Descripcion: Ejecutar pipeline manualmente
   |
   +-- MOD_Pipeline_Schedule
       URL: /pipeline/schedule
       Descripcion: Configurar ejecuciones programadas
```

#### MOD_Settings - Configuracion
```
MOD_Settings (raiz)
   URL: /settings
   Descripcion: Configuracion del sistema
   |
   +-- MOD_Settings_General
   |   URL: /settings/general
   |   Descripcion: Configuracion general
   |
   +-- MOD_Settings_Security
   |   URL: /settings/security
   |   Descripcion: Configuracion de seguridad
   |
   +-- MOD_Settings_Notifications
       URL: /settings/notifications
       Descripcion: Configuracion de notificaciones
```

## Casos de Uso por Modulo

### UC-01: Dashboard Principal
**Modulo:** MOD_Dashboard  
**Actor:** Usuario autenticado  
**Descripcion:** Ver dashboard con metricas principales del sistema  

**Flujo:**
1. Usuario inicia sesion
2. Sistema muestra dashboard principal
3. Dashboard muestra:
   - Total de llamadas del dia
   - Llamadas por centro
   - Llamadas por servicio
   - Ultimas llamadas registradas

---

### UC-02: Consultar Llamadas
**Modulo:** MOD_Calls_View  
**Actor:** Supervisor, Analista  
**Descripcion:** Consultar registros de llamadas con filtros  

**Flujo:**
1. Usuario accede a MOD_Calls_View
2. Sistema muestra interfaz de consulta
3. Usuario aplica filtros (fecha, centro, servicio)
4. Sistema muestra resultados paginados

---

### UC-03: Exportar Llamadas
**Modulo:** MOD_Calls_Export  
**Actor:** Supervisor, Analista  
**Descripcion:** Exportar registros de llamadas a Excel/CSV  

**Flujo:**
1. Usuario accede a MOD_Calls_Export
2. Usuario selecciona filtros y formato
3. Sistema genera archivo
4. Usuario descarga archivo

---

### UC-04: Gestionar Centros
**Modulo:** MOD_Centers_*  
**Actor:** Administrador  
**Descripcion:** CRUD completo de centros de atencion  

**Submodu los:**
- MOD_Centers_View: Listar centros
- MOD_Centers_Create: Crear nuevo centro
- MOD_Centers_Edit: Editar centro existente
- MOD_Centers_Delete: Eliminar centro (soft delete)

---

### UC-05: Gestionar Servicios 800
**Modulo:** MOD_Services_*  
**Actor:** Administrador  
**Descripcion:** CRUD de servicios 800 y asignacion a usuarios  

**Submodulos:**
- MOD_Services_View: Listar servicios
- MOD_Services_Create: Crear nuevo servicio
- MOD_Services_Edit: Editar servicio
- MOD_Services_Assign: Asignar servicio a usuario

---

### UC-06: Gestionar Usuarios
**Modulo:** MOD_Users_*  
**Actor:** Administrador  
**Descripcion:** CRUD de usuarios y gestion de permisos  

**Submodulos:**
- MOD_Users_View: Listar usuarios
- MOD_Users_Create: Crear usuario
- MOD_Users_Edit: Editar usuario
- MOD_Users_Delete: Eliminar usuario (soft delete)
- MOD_Users_Permissions: Asignar modulos/funciones

---

### UC-07: Generar Reportes
**Modulo:** MOD_Reports_*  
**Actor:** Supervisor, Analista  
**Descripcion:** Crear, visualizar y exportar reportes  

**Submodulos:**
- MOD_Reports_View: Ver reportes existentes
- MOD_Reports_Create: Crear nuevo reporte
- MOD_Reports_Export: Exportar a PDF/Excel
- MOD_Reports_Schedule: Programar reporte automatico

---

### UC-08: Consultar Auditoria
**Modulo:** MOD_Audit_View  
**Actor:** Administrador, Auditor  
**Descripcion:** Consultar logs de auditoria del sistema  

**Flujo:**
1. Usuario accede a MOD_Audit_View
2. Sistema muestra logs con filtros
3. Usuario filtra por usuario, accion, fecha
4. Sistema muestra resultados

---

### UC-09: Gestionar Accesos
**Modulo:** MOD_Access_*  
**Actor:** Administrador  
**Descripcion:** Gestionar modulos, funciones y asignaciones  

**Submodulos:**
- MOD_Access_Modules: Gestionar modulos
- MOD_Access_Functions: Gestionar funciones atomicas
- MOD_Access_Assign: Asignar modulos/funciones a usuarios

---

### UC-10: Ejecutar Pipeline ETL
**Modulo:** MOD_Pipeline_*  
**Actor:** Administrador, Operador  
**Descripcion:** Ejecutar y monitorear pipeline ETL  

**Submodulos:**
- MOD_Pipeline_View: Ver ejecuciones
- MOD_Pipeline_Execute: Ejecutar manualmente
- MOD_Pipeline_Schedule: Configurar ejecuciones

---

## Matriz Modulos - Apps

| Modulo | Apps Relacionadas | Modelos Involucrados |
|--------|-------------------|----------------------|
| MOD_Dashboard | core, reports | CallRecord, Report |
| MOD_Calls | core | CallRecord |
| MOD_Centers | core | Center |
| MOD_Services | core | Service, UserServiceAccess |
| MOD_Users | users, access | User, UserModuleAccess, UserFunctionAssignment |
| MOD_Reports | reports | Report, ExportJob |
| MOD_Audit | audit | AuditLog |
| MOD_Access | access | Module, Function |
| MOD_Pipeline | pipeline | ETLExecution |
| MOD_Settings | todas | (configuracion general) |

## Resumen

**Total Modulos Raiz:** 10  
**Total Submodulos:** 30+  
**Total Apps:** 8  
**Total Modelos:** 13  

---

Ultima actualizacion: 2024 - Remediacion Post Sprint 3
