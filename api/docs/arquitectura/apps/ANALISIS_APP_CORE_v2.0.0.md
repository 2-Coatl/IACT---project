---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - App Core
categoria: arquitectura/apps
tema: apps/core/ - Deprecación Completa
autor: Claude Technical Analysis
tags: [core, deprecated, refactoring, cleanup]
relacionado:
  - ANALISIS_RELACIONES_v2.0.0_PARTE_1-6.md
  - MODELO_RBAC_IACT_v5_2_0.md
estado: completo-definitivo
replaces: ANALISIS_APP_CORE_v1.0.0.md
---

# ANÁLISIS DE apps/core/ v2.0.0

**Status: DEPRECADO COMPLETAMENTE**

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen)
2. [Estado Actual de apps/core/](#estado-actual)
3. [Razones para Deprecación](#razones)
4. [Plan de Eliminación](#plan-eliminacion)
5. [Migración de Funcionalidad](#migracion)
6. [Nueva Arquitectura](#nueva-arquitectura)

---

<a name="resumen"></a>
## 1. RESUMEN EJECUTIVO

```
DECISIÓN: DEPRECAR apps/core/ COMPLETAMENTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Estado:      ❌ DEPRECATED
Acción:      Eliminar completamente
Razón:       Componentes obsoletos o fuera de alcance
Migración:   apps/access/ (RBAC único)
Timeline:    Inmediato

Componentes afectados:
├─ CallRecord (modelo)                    → ❌ ELIMINAR
├─ ETLService (service)                   → ❌ ELIMINAR
├─ ServiceAccessService (service)         → ❌ ELIMINAR
├─ UserServiceAccess (modelo)             → ❌ ELIMINAR
├─ Service (modelo)                       → ❌ ELIMINAR
├─ Center (modelo)                        → ❌ ELIMINAR
├─ ServiceFilterMixin (mixin)             → ❌ ELIMINAR
├─ HasServiceAccess (permission)          → ❌ ELIMINAR
└─ navigation/ (posiblemente)             → ❌ REVISAR

ARQUITECTURA RESULTANTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sistema de control de acceso: apps/access/ (RBAC único)
Sistema de datos: apps/reports/ (reportes agregados)
ETL: Fuera de Django (DB stored procedures)
```

---

<a name="estado-actual"></a>
## 2. ESTADO ACTUAL DE apps/core/

### 2.1 Estructura de Archivos

```
apps/core/
├── models.py                    ❌ DEPRECAR
│   ├── CallRecord               ❌ Obsoleto
│   ├── Center                   ❌ No necesario
│   ├── Service                  ❌ No necesario
│   └── UserServiceAccess        ❌ No necesario
│
├── services.py                  ❌ DEPRECAR
│   └── ServiceAccessService     ❌ No queremos segmentación
│
├── services/
│   └── etl_service.py           ❌ DEPRECAR
│       └── ETLService           ❌ ETL fuera de Django
│
├── mixins.py                    ❌ DEPRECAR
│   ├── ServiceFilterMixin       ❌ No segmentación
│   └── OptionalServiceFilterMixin ❌ No segmentación
│
├── permissions.py               ❌ DEPRECAR
│   └── HasServiceAccess         ❌ No segmentación
│
├── navigation/                  ⚠️ REVISAR
│   └── builders.py              ⚠️ Si genera menú, mover a otro lado
│
└── management/commands/         ⚠️ REVISAR
    └── [commands...]            ⚠️ Si hay útiles, mover
```

### 2.2 Análisis de Componentes

```python
# ════════════════════════════════════════════════════════════
# COMPONENTE 1: CallRecord (models.py)
# ════════════════════════════════════════════════════════════

class CallRecord(SoftDeleteMixin, models.Model):
    """
    ❌ PROBLEMA: No debe existir en arquitectura v2.0
    
    Razón:
    - ETL ahora corre en DB (no en Django)
    - ETL crea tablas agregadas directamente:
      * reporte_cmenu_agregado
      * reporte_llamadas_abandonadas
      * reporte_clientes_unicos_did
      * etc.
    - CallRecord era tabla intermedia innecesaria
    
    Acción: ELIMINAR completamente
    """
    fecha = models.DateField()
    telefono = models.CharField()
    servicio_800 = models.CharField()
    # ...


# ════════════════════════════════════════════════════════════
# COMPONENTE 2: Center, Service, UserServiceAccess (models.py)
# ════════════════════════════════════════════════════════════

class Center(models.Model):
    """
    ❌ PROBLEMA: Segmentación de datos NO querida
    
    Razón:
    - Sistema diseñado para limitar QUÉ DATOS ve cada usuario
    - Solo queremos RBAC (QUÉ puede HACER)
    - Sin segmentación por servicio 800
    
    Acción: ELIMINAR completamente
    """
    nombre = models.CharField()
    codigo = models.CharField()
    # ...

class Service(models.Model):
    """❌ ELIMINAR - No segmentación"""
    numero_800 = models.CharField()
    center = models.ForeignKey(Center)
    # ...

class UserServiceAccess(models.Model):
    """❌ ELIMINAR - No segmentación"""
    user = models.ForeignKey(User)
    service = models.ForeignKey(Service)
    # ...


# ════════════════════════════════════════════════════════════
# COMPONENTE 3: ServiceAccessService (services.py)
# ════════════════════════════════════════════════════════════

class ServiceAccessService:
    """
    ❌ PROBLEMA: Implementa segmentación NO deseada
    
    Razón:
    - Filtra datos por servicios asignados
    - Solo queremos RBAC (QUÉ hace), no segmentación (QUÉ ve)
    - Todos los usuarios ven TODOS los datos
    - RBAC controla QUÉ ACCIONES puede hacer con esos datos
    
    Acción: ELIMINAR completamente
    """
    @staticmethod
    def filter_by_user_services(queryset, user, field):
        """❌ NO queremos esto"""
        # Filtra datos por servicio asignado
        pass


# ════════════════════════════════════════════════════════════
# COMPONENTE 4: ETLService (services/etl_service.py)
# ════════════════════════════════════════════════════════════

class ETLService:
    """
    ❌ PROBLEMA: ETL no debe correr en Django
    
    Razón arquitectura v2.0:
    - ETL corre en DB (stored procedures o script externo)
    - Scheduled por pg_cron / MySQL Event / system cron
    - Django NO ejecuta ETL
    - apps/pipeline/ solo MONITOREA ETL (no ejecuta)
    
    Acción: ELIMINAR completamente
    """
    def run_etl(self, fecha):
        """❌ Django no ejecuta ETL"""
        pass


# ════════════════════════════════════════════════════════════
# COMPONENTE 5: Mixins y Permissions
# ════════════════════════════════════════════════════════════

class ServiceFilterMixin:
    """❌ ELIMINAR - No segmentación"""
    def get_queryset(self):
        # Filtra por servicios del usuario
        pass

class HasServiceAccess(permissions.BasePermission):
    """❌ ELIMINAR - No segmentación"""
    def has_object_permission(self, request, view, obj):
        # Verifica acceso a servicio
        pass
```

---

<a name="razones"></a>
## 3. RAZONES PARA DEPRECACIÓN

### 3.1 Cambio de Arquitectura

```
ARQUITECTURA v1.0 (Obsoleta):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVR_LEGACY → Django ETL (apps/core/) → CallRecord → REPORTS
                    ↓
              ServiceAccessService (segmentación)

Problemas:
❌ ETL en Django (lento, acoplado)
❌ CallRecord intermedio (innecesario)
❌ Segmentación de datos (no querida)


ARQUITECTURA v2.0 (Correcta):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVR_LEGACY → ETL JOB (DB) → Tablas agregadas → REPORTS
                                      ↓
                                   PIPELINE (monitor)
                                      ↓
                                   ACCESS (RBAC)

Ventajas:
✅ ETL rápido (DB-level)
✅ Sin tablas intermedias
✅ RBAC único (apps/access/)
✅ Sin segmentación de datos
```

### 3.2 Decisión de Negocio

```
SISTEMA DE CONTROL DE ACCESO ÚNICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUEREMOS:
✅ RBAC granular (apps/access/)
   - 42 funciones atómicas
   - Control de QUÉ puede HACER el usuario
   - Ejemplos: ve_reportes, exporta_excel, ve_dashboard

NO QUEREMOS:
❌ Segmentación de datos por servicio
   - Usuarios NO limitados a "sus servicios 800"
   - TODOS ven TODOS los datos
   - RBAC controla QUÉ HACEN con esos datos

EJEMPLO:

Usuario Juan:
├─ Funciones RBAC: RPT-001 (ve_reportes)
├─ Sin RPT-005 (exporta_excel)
└─ Ve TODOS los reportes (sin filtro)
   Pero NO puede exportar (sin RPT-005)

Usuario María:
├─ Funciones RBAC: RPT-001 + RPT-005
└─ Ve TODOS los reportes
   Y SÍ puede exportar

✅ Mismo dataset para todos
✅ RBAC controla acciones
❌ SIN filtros por servicio 800
```

---

<a name="plan-eliminacion"></a>
## 4. PLAN DE ELIMINACIÓN

### 4.1 Checklist de Eliminación

```
FASE 1: ANÁLISIS DE DEPENDENCIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Buscar imports de apps.core en todo el proyecto
  grep -r "from apps.core" callcentersite/apps/
  grep -r "import.*core" callcentersite/apps/

□ Identificar ViewSets que usan ServiceFilterMixin
  grep -r "ServiceFilterMixin" callcentersite/apps/

□ Identificar permisos que usan HasServiceAccess
  grep -r "HasServiceAccess" callcentersite/apps/

□ Identificar referencias a CallRecord
  grep -r "CallRecord" callcentersite/apps/

□ Revisar management commands útiles
  ls -la callcentersite/apps/core/management/commands/


FASE 2: ELIMINAR REFERENCIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Eliminar mixins de ViewSets
  # ANTES:
  class MyViewSet(ServiceFilterMixin, viewsets.ModelViewSet):
      pass
  
  # DESPUÉS:
  class MyViewSet(viewsets.ModelViewSet):
      pass

□ Eliminar permissions de views
  # ANTES:
  permission_classes = [IsAuthenticated, HasServiceAccess]
  
  # DESPUÉS:
  permission_classes = [IsAuthenticated]
  # + agregar @require_function si necesario

□ Eliminar imports
  # ANTES:
  from apps.core.services import ServiceAccessService
  from apps.core.models import CallRecord
  
  # DESPUÉS:
  # (eliminar líneas)


FASE 3: ELIMINAR MODELOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Crear migración para eliminar tablas
  python manage.py makemigrations core --empty
  
  # En la migración:
  operations = [
      migrations.DeleteModel(name='CallRecord'),
      migrations.DeleteModel(name='UserServiceAccess'),
      migrations.DeleteModel(name='Service'),
      migrations.DeleteModel(name='Center'),
  ]

□ Aplicar migración
  python manage.py migrate core


FASE 4: ELIMINAR APP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Remover de INSTALLED_APPS
  # settings.py
  INSTALLED_APPS = [
      # ...
      # 'apps.core',  # ← Comentar o eliminar
  ]

□ Eliminar directorio
  rm -rf callcentersite/apps/core/

□ Eliminar referencias en URLs
  # urls.py principal
  # Eliminar: path('core/', include('apps.core.urls'))


FASE 5: VERIFICACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Tests pasan
  python manage.py test

□ Server arranca
  python manage.py runserver

□ Sin imports faltantes
  python manage.py check

□ Migraciones OK
  python manage.py showmigrations
```

### 4.2 Script de Eliminación

```bash
#!/bin/bash
# ════════════════════════════════════════════════════════════
# Script: remove_core_app.sh
# Elimina apps/core/ completamente
# ════════════════════════════════════════════════════════════

set -e

echo "🔍 Paso 1: Análisis de dependencias..."
echo ""
echo "=== Imports de apps.core ==="
grep -r "from apps.core" callcentersite/apps/ || echo "Ninguno"
echo ""

echo "=== Referencias a CallRecord ==="
grep -r "CallRecord" callcentersite/apps/ --exclude-dir=core || echo "Ninguno"
echo ""

echo "=== Referencias a ServiceAccessService ==="
grep -r "ServiceAccessService" callcentersite/apps/ --exclude-dir=core || echo "Ninguno"
echo ""

echo "⚠️  Revisar output arriba antes de continuar"
read -p "Presiona ENTER para continuar o Ctrl+C para cancelar..."

echo ""
echo "🗑️  Paso 2: Creando migración para eliminar modelos..."
python manage.py makemigrations core --empty --name remove_all_models

echo ""
echo "📝 Edita la migración creada para agregar:"
echo ""
echo "operations = ["
echo "    migrations.DeleteModel(name='CallRecord'),"
echo "    migrations.DeleteModel(name='UserServiceAccess'),"
echo "    migrations.DeleteModel(name='Service'),"
echo "    migrations.DeleteModel(name='Center'),"
echo "]"
echo ""
read -p "Presiona ENTER cuando hayas editado la migración..."

echo ""
echo "🚀 Paso 3: Aplicando migración..."
python manage.py migrate core

echo ""
echo "🗑️  Paso 4: Removiendo de INSTALLED_APPS..."
echo "⚠️  Edita manualmente settings.py para comentar/eliminar 'apps.core'"
read -p "Presiona ENTER cuando hayas editado settings.py..."

echo ""
echo "✅ Paso 5: Verificando..."
python manage.py check

echo ""
echo "🎉 apps/core/ removido exitosamente"
echo ""
echo "📋 Tareas manuales restantes:"
echo "  1. Eliminar físicamente: rm -rf callcentersite/apps/core/"
echo "  2. Eliminar de urls.py si aplica"
echo "  3. Ejecutar tests: python manage.py test"
```

---

<a name="migracion"></a>
## 5. MIGRACIÓN DE FUNCIONALIDAD

### 5.1 ¿Qué pasa con cada componente?

```
COMPONENTE 1: CallRecord
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Origen:    apps/core/models.py::CallRecord
Destino:   ❌ ELIMINAR (sin reemplazo)
Razón:     ETL crea tablas agregadas directamente
Alternativa: Ver apps/reports/models.py para modelos nuevos:
           - CMenuAgregado
           - LlamadasAbandonadas
           - ClientesUnicosPorDID
           - etc.


COMPONENTE 2: ETLService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Origen:    apps/core/services/etl_service.py::ETLService
Destino:   ❌ ELIMINAR
Reemplazo: Stored Procedures en DB o script Python externo
Ubicación: Fuera de Django (ejecutado por cron/scheduler)
Ejemplo:   Ver ANALISIS_RELACIONES_v2.0.0_PARTE_2.md


COMPONENTE 3: ServiceAccessService (segmentación)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Origen:    apps/core/services.py::ServiceAccessService
Destino:   ❌ ELIMINAR (sin reemplazo)
Razón:     No queremos segmentación de datos
Alternativa: Solo RBAC (apps/access/)

Antes (v1.0):
  # Filtrar datos por servicio del usuario
  data = CallRecord.objects.all()
  filtered = ServiceAccessService.filter_by_user_services(
      data, request.user
  )

Después (v2.0):
  # TODOS ven TODOS los datos
  # RBAC controla QUÉ HACEN con esos datos
  
  @require_function('RPT-001')  # ← Control de acciones
  def view_report(request):
      data = CMenuAgregado.objects.all()  # ← Sin filtro
      return Response(data)


COMPONENTE 4: Center, Service, UserServiceAccess
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Origen:    apps/core/models.py
Destino:   ❌ ELIMINAR (sin reemplazo)
Razón:     No hay segmentación de datos
Alternativa: Si necesitas catálogo de servicios 800 para
           referencia (no para control), crear modelo simple
           en apps/reports/ o apps/catalog/


COMPONENTE 5: Mixins y Permissions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Origen:    apps/core/mixins.py, permissions.py
Destino:   ❌ ELIMINAR
Reemplazo: RBAC decorators/permissions de apps/access/

Antes (v1.0):
  class MyViewSet(ServiceFilterMixin, viewsets.ModelViewSet):
      permission_classes = [IsAuthenticated, HasServiceAccess]
      service_field = 'servicio_800'

Después (v2.0):
  class MyViewSet(viewsets.ModelViewSet):
      permission_classes = [IsAuthenticated]
      
      @action(detail=False)
      @require_function('RPT-001')
      def my_action(self, request):
          pass
```

---

<a name="nueva-arquitectura"></a>
## 6. NUEVA ARQUITECTURA (Sin apps/core/)

### 6.1 Sistema de Control de Acceso Único

```
ARQUITECTURA v2.0 - CONTROL DE ACCESO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────┐
│ apps/access/ - RBAC ÚNICO                                   │
│                                                             │
│ Componentes:                                                │
│ ├─ Function (42 funciones)                                 │
│ ├─ FunctionGroup (10 grupos)                               │
│ ├─ UserFunctionAssignment                                  │
│ ├─ @require_function decorator                             │
│ └─ user.has_function() method                              │
│                                                             │
│ Control: QUÉ puede HACER el usuario                        │
│ Scope: Acciones/capacidades del sistema                    │
│                                                             │
│ Funciones REPORTS (8):                                     │
│ ├─ RPT-001: ve_reportes                                    │
│ ├─ RPT-002: ve_dashboard                                   │
│ ├─ RPT-003: filtra_reportes                                │
│ ├─ RPT-004: exporta_csv                                    │
│ ├─ RPT-005: exporta_excel                                  │
│ ├─ RPT-006: exporta_pdf                                    │
│ ├─ RPT-007: ve_kpis                                        │
│ └─ RPT-008: ve_graficos                                    │
└─────────────────────────────────────────────────────────────┘

SIN SEGMENTACIÓN DE DATOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ NO hay UserServiceAccess
❌ NO hay filtros por servicio 800
❌ NO hay Center/Service models para control

✅ TODOS los usuarios ven TODOS los datos
✅ RBAC controla QUÉ HACEN con esos datos
```

### 6.2 Apps Resultantes

```
APPS DJANGO (Sin apps/core/):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/
├─ access/                  ✅ RBAC único
│  ├─ models.py             (Function, UserFunctionAssignment)
│  ├─ decorators.py         (@require_function)
│  └─ permissions.py        (HasFunction)
│
├─ pipeline/                ✅ Monitoring ETL
│  ├─ models.py             (ETLExecution)
│  ├─ services.py           (ETLMonitoringService)
│  └─ views.py              (Dashboard ETL)
│
├─ reports/                 ✅ Consumption
│  ├─ models.py             (CMenuAgregado, LlamadasAbandonadas, ...)
│  ├─ services.py           (ReportServices)
│  ├─ views.py              (ReportViewSets con @require_function)
│  └─ exporters.py          (Excel, CSV, PDF)
│
├─ ivr_legacy/              ✅ Adapter READ-ONLY
│  ├─ models.py             (CallLog managed=False)
│  ├─ adapters.py           (IVRAdapter)
│  └─ routers.py            (READ-ONLY enforcement)
│
├─ users/                   ✅ User management
│  └─ models.py             (User extendido con has_function())
│
└─ core/                    ❌ ELIMINAR COMPLETAMENTE
   [DEPRECATED]
```

### 6.3 Ejemplo de ViewSet con Nueva Arquitectura

```python
# ════════════════════════════════════════════════════════════
# apps/reports/views.py - SIN apps/core/
# ════════════════════════════════════════════════════════════

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.access.decorators import require_function  # ← Solo RBAC
from apps.reports.models import CMenuAgregado
from apps.reports.services import CMenuReportService
from apps.reports.exporters import ExcelExporter


class CMenuReportViewSet(viewsets.ViewSet):
    """
    ViewSet para reportes cMenu.
    
    ARQUITECTURA v2.0:
    ✅ Solo RBAC (apps/access/)
    ✅ Sin segmentación de datos
    ✅ Todos ven todos los datos
    ✅ RBAC controla QUÉ HACEN
    """
    
    permission_classes = [IsAuthenticated]
    
    # ────────────────────────────────────────────────────────
    # VER DATOS - Requiere RPT-001
    # ────────────────────────────────────────────────────────
    
    @action(detail=False, methods=['get'])
    @require_function('RPT-001')  # ← RBAC: ¿Puede ver reportes?
    def data(self, request):
        """
        Obtener datos de reportes.
        
        GET /api/v1/reports/cmenu/data/
          ?fecha=2025-08-17
          &sucursal=puebla
        
        Requiere: RPT-001 (ve_reportes)
        
        ✅ Usuario ve TODOS los datos (sin filtro)
        ✅ RBAC verifica que puede VER reportes
        """
        fecha = request.query_params.get('fecha')
        sucursal = request.query_params.get('sucursal')
        
        # Query TODOS los datos (sin filtro por usuario)
        data = CMenuReportService.get_report_data(
            fecha=fecha,
            sucursal=sucursal
        )
        
        return Response({
            'count': len(data),
            'data': data
        })
    
    # ────────────────────────────────────────────────────────
    # EXPORTAR EXCEL - Requiere RPT-001 + RPT-005
    # ────────────────────────────────────────────────────────
    
    @action(detail=False, methods=['post'])
    @require_function('RPT-001', 'RPT-005')  # ← ve + exporta
    def generate_excel(self, request):
        """
        Generar Excel.
        
        POST /api/v1/reports/cmenu/generate-excel/
        
        Requiere:
        - RPT-001 (ve_reportes)
        - RPT-005 (exporta_excel)
        
        ✅ Datos sin filtrar
        ✅ RBAC verifica que puede EXPORTAR
        """
        fecha = request.data.get('fecha')
        sucursal = request.data.get('sucursal')
        
        # Query datos (todos, sin filtro)
        data = CMenuReportService.get_report_data(
            fecha=fecha,
            sucursal=sucursal
        )
        
        # Validar CNST-007
        if len(data) > 100000:
            return Response({
                "error": "Máximo 100K registros"
            }, status=400)
        
        # Generar Excel
        filepath = ExcelExporter.generate_cmenu_excel(data)
        
        return Response({
            "file_url": filepath,
            "total_records": len(data)
        })


# ════════════════════════════════════════════════════════════
# COMPARACIÓN: v1.0 vs v2.0
# ════════════════════════════════════════════════════════════

# v1.0 (Con apps/core/ - OBSOLETO):
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from apps.core.mixins import ServiceFilterMixin  # ❌ Deprecated
from apps.core.permissions import HasServiceAccess  # ❌ Deprecated

class MyViewSet(ServiceFilterMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasServiceAccess]
    service_field = 'servicio_800'
    
    # get_queryset automáticamente filtra por servicios del usuario
    # Usuarios ven SOLO sus servicios 800
"""

# v2.0 (Sin apps/core/ - CORRECTO):
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from apps.access.decorators import require_function  # ✅ Solo RBAC

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    @require_function('RPT-001')
    def list(self, request):
        # Usuarios ven TODOS los datos
        # RBAC controla QUÉ PUEDEN HACER
        queryset = self.get_queryset()  # Sin filtro
        return Response(queryset)
"""
```

---

## 7. CONCLUSIÓN

```
RESUMEN FINAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DECISIÓN:
  apps/core/ debe ser ELIMINADO COMPLETAMENTE

RAZONES:
  1. CallRecord obsoleto (ETL fuera de Django)
  2. ETLService obsoleto (ETL en DB, no Django)
  3. ServiceAccessService no deseado (sin segmentación)
  4. Center/Service/UserServiceAccess no necesarios

NUEVA ARQUITECTURA:
  ✅ apps/access/ - RBAC único (QUÉ puede HACER)
  ✅ apps/reports/ - Reportes (con datos sin filtrar)
  ✅ apps/pipeline/ - Monitoring ETL
  ❌ apps/core/ - ELIMINADO

BENEFICIOS:
  ✅ Arquitectura más simple
  ✅ Un solo sistema de control (RBAC)
  ✅ Sin confusión entre segmentación y permisos
  ✅ Código más limpio y mantenible

PRÓXIMOS PASOS:
  1. Ejecutar plan de eliminación (sección 4)
  2. Actualizar imports en apps existentes
  3. Agregar @require_function donde necesario
  4. Eliminar ServiceFilterMixin de ViewSets
  5. Tests de regresión
```

---

**FIN DEL ANÁLISIS**

**Documento:** ANALISIS_APP_CORE v2.0.0  
**Fecha:** 2026-01-17  
**Estado:** ✅ COMPLETO  
**Acción:** DEPRECAR apps/core/ completamente  
**Reemplazo:** apps/access/ (RBAC único)
