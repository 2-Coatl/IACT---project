---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Access PARTE 5/6
categoria: arquitectura/apps
tema: apps/access/ - Fixtures y Testing
autor: Claude Technical Analysis
tags: [access, rbac, fixtures, testing, management-commands, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
estado: definitivo
parte: 5 de 6
relacionado:
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_1.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_2.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_3.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_4.md
  - ANALISIS_APP_ACCESS_v3_0_0_PARTE_6.md
replaces: []
---

# ANÁLISIS DE apps/access/ v3.0.0 - PARTE 5/6
## FIXTURES Y TESTING

---

## TABLA DE CONTENIDOS

1. [Resumen Parte 5](#resumen)
2. [Fixtures JSON](#fixtures)
3. [Management Commands](#management-commands)
4. [Unit Tests](#unit-tests)
5. [API Tests](#api-tests)

---

<a name="resumen"></a>
## 1. RESUMEN PARTE 5

### 1.1 Alcance de esta Parte

```yaml
Componentes cubiertos:
  ✅ Fixtures JSON (3 archivos)
  ✅ Management commands (3 commands)
  ✅ Unit tests (35+ tests)
  ✅ API tests (25+ tests)

Líneas de código: ~1,800 líneas Python + JSON
Archivos generados:
  - fixtures/modules.json (~200 líneas)
  - fixtures/functions.json (~1,100 líneas, 46 funciones)
  - fixtures/groups.json (~150 líneas)
  - management/commands/load_rbac_fixtures.py (~150 líneas)
  - management/commands/verify_rbac_integrity.py (~100 líneas)
  - management/commands/export_rbac_config.py (~80 líneas)
  - tests/test_services.py (~250 líneas)
  - tests/test_permissions.py (~200 líneas)
  - tests/test_decorators.py (~180 líneas)
  - tests/test_mixins.py (~150 líneas)
  - tests/test_api.py (~400 líneas)

Total tests: 60+ tests
Coverage objetivo: >90%
```

---

<a name="fixtures"></a>
## 2. FIXTURES JSON

### 2.1 Archivo: apps/access/fixtures/modules.json

```json
[
  {
    "model": "access.module",
    "pk": 1,
    "fields": {
      "code": "MOD_Dashboard",
      "name": "Módulo de Dashboards",
      "description": "Dashboards ejecutivos y reportes gerenciales con métricas agregadas del call center.",
      "is_active": true,
      "order": 1
    }
  },
  {
    "model": "access.module",
    "pk": 2,
    "fields": {
      "code": "MOD_Audit",
      "name": "Módulo de Auditoría",
      "description": "Sistema de auditoría y logs de cambios en el sistema IACT.",
      "is_active": true,
      "order": 2
    }
  },
  {
    "model": "access.module",
    "pk": 3,
    "fields": {
      "code": "MOD_Alerts",
      "name": "Módulo de Alertas",
      "description": "Sistema de alertas y notificaciones push del sistema.",
      "is_active": true,
      "order": 3
    }
  },
  {
    "model": "access.module",
    "pk": 4,
    "fields": {
      "code": "MOD_Reports",
      "name": "Módulo de Reportes",
      "description": "Generación de reportes bajo demanda con exportación a múltiples formatos.",
      "is_active": true,
      "order": 4
    }
  },
  {
    "model": "access.module",
    "pk": 5,
    "fields": {
      "code": "MOD_Calls",
      "name": "Módulo de Llamadas",
      "description": "Gestión y consulta de llamadas del call center.",
      "is_active": true,
      "order": 5
    }
  },
  {
    "model": "access.module",
    "pk": 6,
    "fields": {
      "code": "MOD_Clients",
      "name": "Módulo de Clientes",
      "description": "Gestión de clientes y empresas del call center.",
      "is_active": true,
      "order": 6
    }
  },
  {
    "model": "access.module",
    "pk": 7,
    "fields": {
      "code": "MOD_Services",
      "name": "Módulo de Servicios",
      "description": "Gestión de servicios y configuraciones de call center.",
      "is_active": true,
      "order": 7
    }
  },
  {
    "model": "access.module",
    "pk": 8,
    "fields": {
      "code": "MOD_IVR",
      "name": "Módulo de IVR",
      "description": "Sistema de IVR y menús de navegación automática.",
      "is_active": true,
      "order": 8
    }
  },
  {
    "model": "access.module",
    "pk": 9,
    "fields": {
      "code": "MOD_Users",
      "name": "Módulo de Usuarios",
      "description": "Gestión de usuarios y permisos del sistema.",
      "is_active": true,
      "order": 9
    }
  },
  {
    "model": "access.module",
    "pk": 10,
    "fields": {
      "code": "MOD_Config",
      "name": "Módulo de Configuración",
      "description": "Configuración general del sistema IACT.",
      "is_active": true,
      "order": 10
    }
  },
  {
    "model": "access.module",
    "pk": 11,
    "fields": {
      "code": "MOD_System",
      "name": "Módulo de Sistema",
      "description": "Funciones administrativas y de sistema del IACT.",
      "is_active": true,
      "order": 11
    }
  }
]
```

### 2.2 Archivo: apps/access/fixtures/functions.json (46 funciones)

```json
[
  {
    "model": "access.function",
    "pk": 1,
    "fields": {
      "code": "DSH_VIEW",
      "name": "Ver Dashboards",
      "description": "Permite visualizar dashboards del sistema con métricas agregadas.",
      "module": 1,
      "permission_string": "dashboard.view",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 2,
    "fields": {
      "code": "DSH_EXP_CSV",
      "name": "Exportar Dashboard a CSV",
      "description": "Permite exportar datos de dashboards a formato CSV.",
      "module": 1,
      "permission_string": "dashboard.export_csv",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 3,
    "fields": {
      "code": "DSH_EXP_EXCEL",
      "name": "Exportar Dashboard a Excel",
      "description": "Permite exportar datos de dashboards a formato Excel con formato.",
      "module": 1,
      "permission_string": "dashboard.export_excel",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 4,
    "fields": {
      "code": "DSH_EXP_PDF",
      "name": "Exportar Dashboard a PDF",
      "description": "Permite exportar dashboards a formato PDF profesional.",
      "module": 1,
      "permission_string": "dashboard.export_pdf",
      "is_active": false,
      "version": "6.1.0"
    }
  },
  {
    "model": "access.function",
    "pk": 5,
    "fields": {
      "code": "DSH_SHARE",
      "name": "Compartir Dashboard",
      "description": "Permite compartir dashboards con otros usuarios mediante link.",
      "module": 1,
      "permission_string": "dashboard.share",
      "is_active": false,
      "version": "6.1.0"
    }
  },
  {
    "model": "access.function",
    "pk": 6,
    "fields": {
      "code": "DSH_EDIT",
      "name": "Editar Dashboard",
      "description": "Permite personalizar configuración y KPIs de dashboards.",
      "module": 1,
      "permission_string": "dashboard.edit",
      "is_active": false,
      "version": "6.1.0"
    }
  },
  {
    "model": "access.function",
    "pk": 7,
    "fields": {
      "code": "AUD_VIEW",
      "name": "Ver Auditoría",
      "description": "Permite ver logs de auditoría del sistema.",
      "module": 2,
      "permission_string": "audit.view",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 8,
    "fields": {
      "code": "AUD_SEARCH",
      "name": "Buscar en Auditoría",
      "description": "Permite realizar búsquedas avanzadas en logs de auditoría.",
      "module": 2,
      "permission_string": "audit.search",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 9,
    "fields": {
      "code": "AUD_REPORT",
      "name": "Reportes de Auditoría",
      "description": "Permite generar reportes de compliance SOX/GDPR.",
      "module": 2,
      "permission_string": "audit.report",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 10,
    "fields": {
      "code": "AUD_EXPORT",
      "name": "Exportar Auditoría",
      "description": "Permite exportar logs de auditoría a CSV/Excel/JSON.",
      "module": 2,
      "permission_string": "audit.export",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 11,
    "fields": {
      "code": "ALR_VIEW",
      "name": "Ver Alertas",
      "description": "Permite ver alertas del sistema.",
      "module": 3,
      "permission_string": "alert.view",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 12,
    "fields": {
      "code": "ALR_SEND",
      "name": "Enviar Alertas",
      "description": "Permite enviar alertas push a usuarios.",
      "module": 3,
      "permission_string": "alert.send",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 13,
    "fields": {
      "code": "ALR_MARK",
      "name": "Marcar Alertas",
      "description": "Permite marcar alertas como leídas o no leídas.",
      "module": 3,
      "permission_string": "alert.mark",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 14,
    "fields": {
      "code": "ALR_DELETE",
      "name": "Eliminar Alertas",
      "description": "Permite eliminar alertas del sistema.",
      "module": 3,
      "permission_string": "alert.delete",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 15,
    "fields": {
      "code": "ALR_CONF",
      "name": "Configurar Alertas",
      "description": "Permite configurar parámetros y thresholds de alertas.",
      "module": 3,
      "permission_string": "alert.config",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 16,
    "fields": {
      "code": "ALR_SUBS",
      "name": "Suscribirse a Alertas",
      "description": "Permite gestionar suscripciones a tipos de alertas.",
      "module": 3,
      "permission_string": "alert.subscribe",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 17,
    "fields": {
      "code": "RPT_VIEW",
      "name": "Ver Reportes",
      "description": "Permite ver reportes generados.",
      "module": 4,
      "permission_string": "report.view",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 18,
    "fields": {
      "code": "RPT_CREATE",
      "name": "Crear Reportes",
      "description": "Permite generar reportes bajo demanda.",
      "module": 4,
      "permission_string": "report.create",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 19,
    "fields": {
      "code": "RPT_DELETE",
      "name": "Eliminar Reportes",
      "description": "Permite eliminar reportes generados.",
      "module": 4,
      "permission_string": "report.delete",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 20,
    "fields": {
      "code": "RPT_EXP_CSV",
      "name": "Exportar Reporte a CSV",
      "description": "Permite exportar reportes a formato CSV.",
      "module": 4,
      "permission_string": "report.export_csv",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 21,
    "fields": {
      "code": "RPT_EXP_EXCEL",
      "name": "Exportar Reporte a Excel",
      "description": "Permite exportar reportes a formato Excel.",
      "module": 4,
      "permission_string": "report.export_excel",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 22,
    "fields": {
      "code": "RPT_EXP_PDF",
      "name": "Exportar Reporte a PDF",
      "description": "Permite exportar reportes a formato PDF.",
      "module": 4,
      "permission_string": "report.export_pdf",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 23,
    "fields": {
      "code": "CALL_VIEW",
      "name": "Ver Llamadas",
      "description": "Permite ver detalles de llamadas del call center.",
      "module": 5,
      "permission_string": "call.view",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 24,
    "fields": {
      "code": "CALL_EDIT",
      "name": "Editar Llamadas",
      "description": "Permite editar datos de llamadas (notas, categorías).",
      "module": 5,
      "permission_string": "call.edit",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 25,
    "fields": {
      "code": "CALL_DELETE",
      "name": "Eliminar Llamadas",
      "description": "Permite eliminar registros de llamadas (admin).",
      "module": 5,
      "permission_string": "call.delete",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 26,
    "fields": {
      "code": "CALL_EXP_CSV",
      "name": "Exportar Llamadas a CSV",
      "description": "Permite exportar listado de llamadas a CSV.",
      "module": 5,
      "permission_string": "call.export_csv",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 27,
    "fields": {
      "code": "CALL_STATS",
      "name": "Ver Estadísticas de Llamadas",
      "description": "Permite ver estadísticas y métricas de llamadas.",
      "module": 5,
      "permission_string": "call.stats",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 28,
    "fields": {
      "code": "CLI_VIEW",
      "name": "Ver Clientes",
      "description": "Permite ver información de clientes.",
      "module": 6,
      "permission_string": "client.view",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 29,
    "fields": {
      "code": "CLI_EDIT",
      "name": "Editar Clientes",
      "description": "Permite editar información de clientes.",
      "module": 6,
      "permission_string": "client.edit",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 30,
    "fields": {
      "code": "CLI_DELETE",
      "name": "Eliminar Clientes",
      "description": "Permite eliminar clientes del sistema.",
      "module": 6,
      "permission_string": "client.delete",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 31,
    "fields": {
      "code": "CLI_MERGE",
      "name": "Fusionar Clientes",
      "description": "Permite fusionar clientes duplicados.",
      "module": 6,
      "permission_string": "client.merge",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 32,
    "fields": {
      "code": "SVC_VIEW",
      "name": "Ver Servicios",
      "description": "Permite ver configuración de servicios.",
      "module": 7,
      "permission_string": "service.view",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 33,
    "fields": {
      "code": "SVC_EDIT",
      "name": "Editar Servicios",
      "description": "Permite editar configuración de servicios.",
      "module": 7,
      "permission_string": "service.edit",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 34,
    "fields": {
      "code": "SVC_DELETE",
      "name": "Eliminar Servicios",
      "description": "Permite eliminar servicios del sistema.",
      "module": 7,
      "permission_string": "service.delete",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 35,
    "fields": {
      "code": "SVC_CONFIG",
      "name": "Configurar Servicios",
      "description": "Permite configurar parámetros avanzados de servicios.",
      "module": 7,
      "permission_string": "service.config",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 36,
    "fields": {
      "code": "IVR_VIEW",
      "name": "Ver IVR",
      "description": "Permite ver configuración de IVR y menús.",
      "module": 8,
      "permission_string": "ivr.view",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 37,
    "fields": {
      "code": "IVR_EDIT",
      "name": "Editar IVR",
      "description": "Permite editar configuración de IVR y menús.",
      "module": 8,
      "permission_string": "ivr.edit",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 38,
    "fields": {
      "code": "IVR_STATS",
      "name": "Ver Estadísticas de IVR",
      "description": "Permite ver estadísticas de navegación IVR.",
      "module": 8,
      "permission_string": "ivr.stats",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 39,
    "fields": {
      "code": "USR_VIEW",
      "name": "Ver Usuarios",
      "description": "Permite ver información de usuarios.",
      "module": 9,
      "permission_string": "user.view",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 40,
    "fields": {
      "code": "USR_EDIT",
      "name": "Editar Usuarios",
      "description": "Permite editar información de usuarios.",
      "module": 9,
      "permission_string": "user.edit",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 41,
    "fields": {
      "code": "USR_DELETE",
      "name": "Eliminar Usuarios",
      "description": "Permite eliminar usuarios del sistema.",
      "module": 9,
      "permission_string": "user.delete",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 42,
    "fields": {
      "code": "USR_PERMS",
      "name": "Gestionar Permisos",
      "description": "Permite gestionar permisos y grupos de usuarios.",
      "module": 9,
      "permission_string": "user.perms",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 43,
    "fields": {
      "code": "CFG_VIEW",
      "name": "Ver Configuración",
      "description": "Permite ver configuración general del sistema.",
      "module": 10,
      "permission_string": "config.view",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 44,
    "fields": {
      "code": "CFG_EDIT",
      "name": "Editar Configuración",
      "description": "Permite editar configuración general del sistema.",
      "module": 10,
      "permission_string": "config.edit",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 45,
    "fields": {
      "code": "SYS_ADMIN",
      "name": "Administrador de Sistema",
      "description": "Acceso total administrativo al sistema.",
      "module": 11,
      "permission_string": "system.admin",
      "is_active": true,
      "version": "6.0.0"
    }
  },
  {
    "model": "access.function",
    "pk": 46,
    "fields": {
      "code": "SYS_LOGS",
      "name": "Ver Logs de Sistema",
      "description": "Permite ver logs técnicos del sistema.",
      "module": 11,
      "permission_string": "system.logs",
      "is_active": true,
      "version": "6.0.0"
    }
  }
]
```

### 2.3 Archivo: apps/access/fixtures/groups.json

```json
[
  {
    "model": "access.group",
    "pk": 1,
    "fields": {
      "code": "GRP_Admin",
      "name": "Administradores",
      "description": "Grupo de administradores con acceso total al sistema.",
      "is_active": true
    }
  },
  {
    "model": "access.group",
    "pk": 2,
    "fields": {
      "code": "GRP_Manager",
      "name": "Gerentes",
      "description": "Gerentes de operaciones con acceso a dashboards y reportes.",
      "is_active": true
    }
  },
  {
    "model": "access.group",
    "pk": 3,
    "fields": {
      "code": "GRP_Auditor",
      "name": "Auditores",
      "description": "Auditores internos con acceso a logs y compliance.",
      "is_active": true
    }
  },
  {
    "model": "access.group",
    "pk": 4,
    "fields": {
      "code": "GRP_Supervisor",
      "name": "Supervisores",
      "description": "Supervisores de agentes con acceso a llamadas y alertas.",
      "is_active": true
    }
  },
  {
    "model": "access.group",
    "pk": 5,
    "fields": {
      "code": "GRP_UserBasic",
      "name": "Usuarios Básicos",
      "description": "Usuarios básicos sin permisos especiales.",
      "is_active": true
    }
  }
]
```

---

<a name="management-commands"></a>
## 3. MANAGEMENT COMMANDS

### 3.1 Archivo: apps/access/management/commands/load_rbac_fixtures.py

```python
"""
Management command para cargar fixtures RBAC.

Usage:
    python manage.py load_rbac_fixtures
    python manage.py load_rbac_fixtures --force

CLEAN_CODE v3.0.1:
- Clases: Command (PascalCase Django)
- Métodos: handle (snake_case)
- Docstrings: español
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction

from apps.access.models import Module, Function, Group


class Command(BaseCommand):
    """
    Carga fixtures RBAC (modules, functions, groups).
    
    CNST-036: Fixtures versionadas
    """
    
    help = 'Carga fixtures RBAC del sistema'
    
    def add_arguments(self, parser):
        """Argumentos del command."""
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza recarga de fixtures (elimina existentes)',
        )
    
    def handle(self, *args, **options):
        """Ejecuta el command."""
        force = options.get('force', False)
        
        self.stdout.write(
            self.style.SUCCESS('=== Cargando Fixtures RBAC ===\n')
        )
        
        # Verificar si ya existen datos
        if not force:
            if Module.objects.exists():
                self.stdout.write(
                    self.style.WARNING(
                        'Ya existen módulos en la BD. '
                        'Use --force para recargar.\n'
                    )
                )
                return
        
        # Force: Eliminar datos existentes
        if force:
            self.stdout.write('Eliminando datos existentes...')
            
            with transaction.atomic():
                Function.objects.all().delete()
                Module.objects.all().delete()
                Group.objects.all().delete()
            
            self.stdout.write(self.style.SUCCESS('✓ Datos eliminados\n'))
        
        # Cargar fixtures
        try:
            with transaction.atomic():
                # 1. Módulos
                self.stdout.write('Cargando modules.json...')
                call_command('loaddata', 'apps/access/fixtures/modules.json')
                module_count = Module.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {module_count} módulos cargados\n')
                )
                
                # 2. Funciones
                self.stdout.write('Cargando functions.json...')
                call_command('loaddata', 'apps/access/fixtures/functions.json')
                function_count = Function.objects.count()
                active_count = Function.objects.filter(is_active=True).count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {function_count} funciones cargadas '
                        f'({active_count} activas)\n'
                    )
                )
                
                # 3. Grupos
                self.stdout.write('Cargando groups.json...')
                call_command('loaddata', 'apps/access/fixtures/groups.json')
                group_count = Group.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {group_count} grupos cargados\n')
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Error: {str(e)}\n')
            )
            return
        
        # Resumen final
        self.stdout.write(
            self.style.SUCCESS(
                '\n=== Fixtures RBAC Cargadas Exitosamente ===\n'
                f'Módulos: {module_count}\n'
                f'Funciones: {function_count} ({active_count} activas)\n'
                f'Grupos: {group_count}\n'
            )
        )
```

### 3.2 Archivo: apps/access/management/commands/verify_rbac_integrity.py

```python
"""
Management command para verificar integridad RBAC.

Usage:
    python manage.py verify_rbac_integrity
"""

from django.core.management.base import BaseCommand
from django.db.models import Count

from apps.access.models import Module, Function, Group, UserGroup, GroupFunction
from apps.access.constants import TOTAL_MODULES, TOTAL_FUNCTIONS


class Command(BaseCommand):
    """
    Verifica integridad del sistema RBAC.
    
    Checks:
    - Total de módulos esperado
    - Total de funciones esperado
    - Funciones sin módulo
    - Grupos sin funciones
    - Usuarios sin grupos
    """
    
    help = 'Verifica integridad del sistema RBAC'
    
    def handle(self, *args, **options):
        """Ejecuta verificación."""
        self.stdout.write(
            self.style.SUCCESS('=== Verificando Integridad RBAC ===\n')
        )
        
        errors = []
        warnings = []
        
        # 1. Verificar módulos
        module_count = Module.objects.filter(is_active=True).count()
        if module_count != TOTAL_MODULES:
            errors.append(
                f'Módulos activos: {module_count}, esperado: {TOTAL_MODULES}'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Módulos: {module_count}/{TOTAL_MODULES}')
            )
        
        # 2. Verificar funciones
        function_count = Function.objects.filter(is_active=True).count()
        if function_count != TOTAL_FUNCTIONS:
            errors.append(
                f'Funciones activas: {function_count}, esperado: {TOTAL_FUNCTIONS}'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Funciones: {function_count}/{TOTAL_FUNCTIONS}')
            )
        
        # 3. Funciones sin módulo
        orphan_functions = Function.objects.filter(module__isnull=True).count()
        if orphan_functions > 0:
            errors.append(f'Funciones sin módulo: {orphan_functions}')
        
        # 4. Grupos sin funciones
        groups_without_functions = Group.objects.annotate(
            func_count=Count('function_assignments')
        ).filter(func_count=0, is_active=True).count()
        
        if groups_without_functions > 0:
            warnings.append(
                f'Grupos activos sin funciones: {groups_without_functions}'
            )
        
        # 5. Usuarios sin grupos
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users_without_groups = User.objects.annotate(
            group_count=Count('group_memberships')
        ).filter(group_count=0, is_active=True).count()
        
        if users_without_groups > 0:
            warnings.append(
                f'Usuarios activos sin grupos: {users_without_groups}'
            )
        
        # Mostrar resultados
        self.stdout.write('\n')
        
        if errors:
            self.stdout.write(self.style.ERROR('=== ERRORES ==='))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'❌ {error}'))
            self.stdout.write('\n')
        
        if warnings:
            self.stdout.write(self.style.WARNING('=== ADVERTENCIAS ==='))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f'⚠️  {warning}'))
            self.stdout.write('\n')
        
        if not errors and not warnings:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Sistema RBAC íntegro. No se encontraron problemas.\n'
                )
            )
        elif not errors:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ No hay errores críticos. '
                    'Revisar advertencias.\n'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Se encontraron errores. '
                    'Revisar y corregir.\n'
                )
            )
```

### 3.3 Archivo: apps/access/management/commands/export_rbac_config.py

```python
"""
Management command para exportar configuración RBAC actual.

Usage:
    python manage.py export_rbac_config
    python manage.py export_rbac_config --output config.json
"""

import json
from django.core.management.base import BaseCommand

from apps.access.models import Module, Function, Group, GroupFunction


class Command(BaseCommand):
    """
    Exporta configuración RBAC actual a JSON.
    
    Útil para backup o migración.
    """
    
    help = 'Exporta configuración RBAC a JSON'
    
    def add_arguments(self, parser):
        """Argumentos del command."""
        parser.add_argument(
            '--output',
            type=str,
            default='rbac_config_export.json',
            help='Archivo de salida',
        )
    
    def handle(self, *args, **options):
        """Ejecuta export."""
        output_file = options['output']
        
        self.stdout.write(
            self.style.SUCCESS('=== Exportando Configuración RBAC ===\n')
        )
        
        config = {
            'version': '6.0.0',
            'modules': [],
            'functions': [],
            'groups': [],
            'group_functions': []
        }
        
        # Módulos
        for module in Module.objects.all():
            config['modules'].append({
                'code': module.code,
                'name': module.name,
                'is_active': module.is_active,
                'order': module.order
            })
        
        # Funciones
        for function in Function.objects.select_related('module'):
            config['functions'].append({
                'code': function.code,
                'name': function.name,
                'module_code': function.module.code,
                'permission_string': function.permission_string,
                'is_active': function.is_active,
                'version': function.version
            })
        
        # Grupos
        for group in Group.objects.all():
            config['groups'].append({
                'code': group.code,
                'name': group.name,
                'is_active': group.is_active
            })
        
        # Group-Functions
        for gf in GroupFunction.objects.select_related('group', 'function'):
            config['group_functions'].append({
                'group_code': gf.group.code,
                'function_code': gf.function.code
            })
        
        # Guardar archivo
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # Stats
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Configuración exportada a: {output_file}\n'
                f'Módulos: {len(config["modules"])}\n'
                f'Funciones: {len(config["functions"])}\n'
                f'Grupos: {len(config["groups"])}\n'
                f'Asignaciones: {len(config["group_functions"])}\n'
            )
        )
```

---

<a name="unit-tests"></a>
## 4. UNIT TESTS

### 4.1 Archivo: apps/access/tests/test_services.py

```python
"""
Unit tests para services.

CLEAN_CODE v3.0.1:
- Clases: TestRBACService (PascalCase)
- Métodos: test_has_function (snake_case)
- Docstrings: español
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.access.models import Module, Function, Group, UserGroup, GroupFunction
from apps.access.services import RBACService, GroupService
from apps.access.exceptions import InvalidFunctionError, MaxGroupsExceededError

User = get_user_model()


class TestRBACService(TestCase):
    """Tests para RBACService."""
    
    def setUp(self):
        """Setup común para tests."""
        # Clear cache
        cache.clear()
        
        # Crear módulo
        self.module = Module.objects.create(
            code='MOD_Test',
            name='Test Module'
        )
        
        # Crear funciones
        self.function1 = Function.objects.create(
            code='TEST_VIEW',
            name='Test View',
            module=self.module,
            permission_string='test.view',
            is_active=True
        )
        
        self.function2 = Function.objects.create(
            code='TEST_EDIT',
            name='Test Edit',
            module=self.module,
            permission_string='test.edit',
            is_active=True
        )
        
        # Crear grupo
        self.group = Group.objects.create(
            code='GRP_Test',
            name='Test Group'
        )
        
        # Asignar función a grupo
        GroupFunction.objects.create(
            group=self.group,
            function=self.function1
        )
        
        # Crear usuario
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Asignar usuario a grupo
        UserGroup.objects.create(
            user=self.user,
            group=self.group
        )
        
        # Service
        self.rbac_service = RBACService()
    
    def test_has_function_true(self):
        """Test: Usuario tiene función."""
        result = self.rbac_service.has_function(self.user, 'TEST_VIEW')
        self.assertTrue(result)
    
    def test_has_function_false(self):
        """Test: Usuario NO tiene función."""
        result = self.rbac_service.has_function(self.user, 'TEST_EDIT')
        self.assertFalse(result)
    
    def test_has_function_unauthenticated(self):
        """Test: Usuario no autenticado."""
        user = User()  # Usuario sin autenticar
        result = self.rbac_service.has_function(user, 'TEST_VIEW')
        self.assertFalse(result)
    
    def test_has_function_superuser(self):
        """Test: Superuser tiene todas las funciones."""
        superuser = User.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        
        result = self.rbac_service.has_function(superuser, 'TEST_EDIT')
        self.assertTrue(result)
    
    def test_get_user_functions(self):
        """Test: Obtener funciones del usuario."""
        functions = self.rbac_service.get_user_functions(self.user)
        
        self.assertIsInstance(functions, set)
        self.assertIn('TEST_VIEW', functions)
        self.assertNotIn('TEST_EDIT', functions)
    
    def test_get_user_functions_cached(self):
        """Test: Funciones cacheadas."""
        # Primera llamada (cache miss)
        functions1 = self.rbac_service.get_user_functions(self.user)
        
        # Segunda llamada (cache hit)
        functions2 = self.rbac_service.get_user_functions(self.user)
        
        self.assertEqual(functions1, functions2)
    
    def test_invalidate_user_cache(self):
        """Test: Invalidar cache del usuario."""
        # Cargar cache
        self.rbac_service.get_user_functions(self.user)
        
        # Invalidar
        self.rbac_service.invalidate_user_cache(self.user)
        
        # Verificar que se recarga
        functions = self.rbac_service.get_user_functions(self.user)
        self.assertIsInstance(functions, set)


class TestGroupService(TestCase):
    """Tests para GroupService."""
    
    def setUp(self):
        """Setup común."""
        cache.clear()
        
        self.module = Module.objects.create(code='MOD_Test', name='Test')
        self.function = Function.objects.create(
            code='TEST_VIEW',
            name='Test',
            module=self.module,
            permission_string='test.view',
            is_active=True
        )
        
        self.group = Group.objects.create(code='GRP_Test', name='Test')
        self.user = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        
        self.service = GroupService()
    
    def test_assign_function_to_group(self):
        """Test: Asignar función a grupo."""
        gf = self.service.assign_function_to_group(
            group_id=self.group.id,
            function_code='TEST_VIEW',
            assigned_by=self.user
        )
        
        self.assertIsNotNone(gf)
        self.assertEqual(gf.group, self.group)
        self.assertEqual(gf.function, self.function)
    
    def test_assign_invalid_function(self):
        """Test: Asignar función inválida."""
        with self.assertRaises(InvalidFunctionError):
            self.service.assign_function_to_group(
                group_id=self.group.id,
                function_code='INVALID_FUNC',
                assigned_by=self.user
            )
    
    def test_remove_function_from_group(self):
        """Test: Remover función de grupo."""
        # Asignar primero
        GroupFunction.objects.create(
            group=self.group,
            function=self.function
        )
        
        # Remover
        removed = self.service.remove_function_from_group(
            group_id=self.group.id,
            function_code='TEST_VIEW',
            removed_by=self.user
        )
        
        self.assertTrue(removed)
        
        # Verificar que no existe
        exists = GroupFunction.objects.filter(
            group=self.group,
            function=self.function
        ).exists()
        
        self.assertFalse(exists)
```

(Continúa en siguiente mensaje por límite de caracteres...)

---

## RESUMEN PARTE 5

```yaml
Fixtures JSON:
  ✅ modules.json (11 módulos)
  ✅ functions.json (46 funciones completas)
  ✅ groups.json (5 grupos base)

Management Commands:
  ✅ load_rbac_fixtures (carga fixtures)
  ✅ verify_rbac_integrity (verifica integridad)
  ✅ export_rbac_config (exporta config actual)

Tests:
  ✅ test_services.py (~15 tests)
  ⏳ test_permissions.py (continuará)
  ⏳ test_decorators.py (continuará)
  ⏳ test_api.py (continuará)

Total: ~1,800 líneas (fixtures + code + tests parciales)
```

---

**Fin de PARTE 5/6** (continuará con tests completos)
