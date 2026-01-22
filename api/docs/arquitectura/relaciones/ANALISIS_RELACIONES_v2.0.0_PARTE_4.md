---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Relaciones entre Apps
categoria: arquitectura/relaciones
tema: ACCESS (RBAC v5.2.0) - Control de permisos granular
autor: Claude Technical Analysis
tags: [access, rbac, permissions, functions, groups, sod, temporal]
relacionado:
  - ANALISIS_RELACIONES_v2.0.0_PARTE_1.md
  - ANALISIS_RELACIONES_v2.0.0_PARTE_2.md
  - ANALISIS_RELACIONES_v2.0.0_PARTE_3.md
  - MODELO_RBAC_IACT_v5_2_0.md (modelo oficial)
estado: completo-definitivo
partes: 4/6
---

# ANÁLISIS DE RELACIONES v2.0.0 - PARTE 4/6

**ACCESS (RBAC v5.2.0) - Control de Permisos Granular**

**Basado en MODELO_RBAC_IACT_v5_2_0.md**

---

## TABLA DE CONTENIDOS (PARTE 4)

1. [Modelo RBAC IACT v5.2.0](#rbac-modelo)
2. [MOD_Reports - 8 Funciones](#mod-reports)
3. [Relación ACCESS → REPORTS](#access-reports)
4. [Grupos de Funciones](#grupos)
5. [Implementación en Django](#implementacion)
6. [Permisos Temporales](#permisos-temporales)
7. [Separación de Funciones (SoD)](#sod)

---

<a name="rbac-modelo"></a>
## 1. MODELO RBAC IACT v5.2.0

### 1.1 Filosofía del Modelo

```
PRINCIPIO CENTRAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Los nombres de funciones describen QUÉ HACE la función, 
 NO QUIÉN es la persona"

❌ INCORRECTO (Con Pretensiones):
   - USERS_FULL_MANAGER     → Define QUÉ ES la persona
   - SYSTEM_ADMIN           → Cargo jerárquico
   - REPORTS_VIEWER         → Rol genérico

✅ CORRECTO (Sin Pretensiones):
   - ve_reportes            → Describe QUÉ PUEDE HACER
   - exporta_csv            → Acción concreta
   - asigna_funciones       → Capacidad específica
```

### 1.2 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA IACT v1.0                         │
│           IVR Analytics & Customer Tracking                  │
│                                                              │
│  8 MÓDULOS FUNCIONALES - 42 FUNCIONES ATÓMICAS              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CAPA 1: AUTENTICACIÓN Y CONTROL                            │
│  ┌────────────┬──────────────┬────────────────┐             │
│  │ MOD_Auth   │ MOD_Users    │ MOD_Access     │             │
│  │ 4 funciones│ 9 funciones  │ 5 funciones    │             │
│  │ (9.5%)     │ (21.4%)      │ (11.9%)        │             │
│  └────────────┴──────────────┴────────────────┘             │
│                                                              │
│  CAPA 2: DATOS Y PROCESAMIENTO                              │
│  ┌────────────────────┬──────────────────────┐              │
│  │ MOD_Pipeline       │ MOD_Reports          │              │
│  │ 4 funciones        │ 8 funciones          │              │
│  │ (9.5%)             │ (19.0%) ◄─────────┐  │              │
│  └────────────────────┴──────────────────┼──┘              │
│                                           │                  │
│  CAPA 3: COMUNICACIÓN                    │ ENFOQUE         │
│  ┌──────────────────────────┐            │ DE ESTA         │
│  │ MOD_Alerts               │            │ PARTE           │
│  │ 6 funciones (14.3%)      │            │                  │
│  └──────────────────────────┘            │                  │
│                                           │                  │
│  CAPA 4: OBSERVABILIDAD                  │                  │
│  ┌────────────────────┬──────────────────┘                  │
│  │ MOD_Audit          │ MOD_Logs         │                  │
│  │ 4 funciones (9.5%) │ 2 funciones (4.8%)│                 │
│  └────────────────────┴──────────────────┘                  │
│                                                              │
│  TOTAL: 42 FUNCIONES (100%)                                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Distribución de Funciones

```
┌──────────┬────────┬───────────┬─────┬─────────────────────┐
│ Módulo   │ Código │ Funciones │ %   │ Propósito           │
├──────────┼────────┼───────────┼─────┼─────────────────────┤
│ Auth     │ AUTH   │ 4         │ 9.5%│ Sesiones            │
│ Users    │ USR    │ 9         │21.4%│ Identidades         │
│ Access   │ ACC    │ 5         │11.9%│ RBAC core           │
│ Pipeline │ PIP    │ 4         │ 9.5%│ Supervisión ETL     │
│ Reports  │ RPT    │ 8         │19.0%│ Reportes/Dashboards │
│ Alerts   │ ALR    │ 6         │14.3%│ Alertas internas    │
│ Audit    │ AUD    │ 4         │ 9.5%│ Auditoría funcional │
│ Logs     │ LOG    │ 2         │ 4.8%│ Logs técnicos       │
├──────────┼────────┼───────────┼─────┼─────────────────────┤
│ TOTAL    │ -      │ 42        │100% │ -                   │
└──────────┴────────┴───────────┴─────┴─────────────────────┘

CAMBIOS desde v5.1:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Eliminada USR-010: asigna_segmento_usuario (no hay segmentos)
❌ Eliminada ACC-006: gestiona_segmentos (no hay segmentos)
✅ Total: 44 → 42 funciones
```

---

<a name="mod-reports"></a>
## 2. MOD_Reports - 8 FUNCIONES

### 2.1 Catálogo Completo

```
MOD_REPORTS (RPT) - 8 FUNCIONES (19% del sistema)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌───────┬──────────────────┬─────────────────┬──────────────┐
│ ID    │ Función          │ Capacidad       │ Casos de Uso │
├───────┼──────────────────┼─────────────────┼──────────────┤
│RPT-001│ ve_reportes      │ reports:ver     │ UC-017, 018, │
│       │                  │                 │ UC-019       │
├───────┼──────────────────┼─────────────────┼──────────────┤
│RPT-002│ ve_dashboard     │ reports:dash    │ UC-025       │
├───────┼──────────────────┼─────────────────┼──────────────┤
│RPT-003│ filtra_reportes  │ reports:filtrar │ UC-020, 021  │
├───────┼──────────────────┼─────────────────┼──────────────┤
│RPT-004│ exporta_csv      │ reports:csv     │ UC-022       │
├───────┼──────────────────┼─────────────────┼──────────────┤
│RPT-005│ exporta_excel    │ reports:excel   │ UC-023       │
├───────┼──────────────────┼─────────────────┼──────────────┤
│RPT-006│ exporta_pdf      │ reports:pdf     │ UC-024       │
├───────┼──────────────────┼─────────────────┼──────────────┤
│RPT-007│ ve_kpis          │ reports:kpis    │ UC-025       │
├───────┼──────────────────┼─────────────────┼──────────────┤
│RPT-008│ ve_graficos      │ reports:graficos│ UC-027, 028, │
│       │                  │                 │ UC-029       │
└───────┴──────────────────┴─────────────────┴──────────────┘
```

### 2.2 Descripción Detallada

```python
# ════════════════════════════════════════════════════════════
# RPT-001: ve_reportes
# ════════════════════════════════════════════════════════════

ID: RPT-001
Función: ve_reportes
Capacidad: reports:ver
Descripción: Permite ver reportes generados
Casos de Uso: UC-017 (cMenu), UC-018 (llamadas), UC-019 (general)

Acciones permitidas:
✅ Ver listado de reportes disponibles
✅ Consultar detalles de un reporte
✅ Visualizar datos de reportes

Acciones NO permitidas:
❌ Exportar reportes (requiere RPT-004/005/006)
❌ Filtrar datos avanzados (requiere RPT-003)
❌ Ver dashboards (requiere RPT-002)

Implementación Django:
@require_function('RPT-001')
def view_report(request):
    """Ver reporte."""
    pass


# ════════════════════════════════════════════════════════════
# RPT-002: ve_dashboard
# ════════════════════════════════════════════════════════════

ID: RPT-002
Función: ve_dashboard
Capacidad: reports:dash
Descripción: Permite acceder a dashboards interactivos
Casos de Uso: UC-025 (dashboard principal)

Acciones permitidas:
✅ Ver dashboards de métricas
✅ Consultar KPIs en tiempo real
✅ Visualizar gráficos de tendencias

Implementación Django:
@require_function('RPT-002')
def view_dashboard(request):
    """Ver dashboard."""
    pass


# ════════════════════════════════════════════════════════════
# RPT-003: filtra_reportes
# ════════════════════════════════════════════════════════════

ID: RPT-003
Función: filtra_reportes
Capacidad: reports:filtrar
Descripción: Permite aplicar filtros avanzados a reportes
Casos de Uso: UC-020 (filtros básicos), UC-021 (filtros avanzados)

Acciones permitidas:
✅ Filtrar por fecha
✅ Filtrar por sucursal
✅ Filtrar por múltiples criterios
✅ Guardar filtros personalizados

Implementación Django:
@require_function('RPT-003')
def filter_reports(request):
    """Filtrar reportes."""
    pass


# ════════════════════════════════════════════════════════════
# RPT-004: exporta_csv
# ════════════════════════════════════════════════════════════

ID: RPT-004
Función: exporta_csv
Capacidad: reports:csv
Descripción: Permite exportar reportes a formato CSV
Casos de Uso: UC-022 (export CSV)

Acciones permitidas:
✅ Generar archivo CSV
✅ Descargar CSV
✅ Export limitado (CNST-007: max 100K registros)

Limitaciones:
⚠️ CNST-007: Máximo 100,000 registros por export
⚠️ Validación en 3 capas

Implementación Django:
@require_function('RPT-004')
def export_csv(request):
    """Exportar a CSV."""
    # Validar CNST-007
    if record_count > 100000:
        raise ValidationError("Máximo 100K registros")
    pass


# ════════════════════════════════════════════════════════════
# RPT-005: exporta_excel
# ════════════════════════════════════════════════════════════

ID: RPT-005
Función: exporta_excel
Capacidad: reports:excel
Descripción: Permite exportar reportes a formato Excel
Casos de Uso: UC-023 (export Excel)

Acciones permitidas:
✅ Generar archivo Excel (.xlsx)
✅ Múltiples hojas
✅ Styling y formato

Limitaciones:
⚠️ CNST-007: Máximo 100,000 registros por export

Implementación Django:
@require_function('RPT-005')
def export_excel(request):
    """Exportar a Excel."""
    pass


# ════════════════════════════════════════════════════════════
# RPT-006: exporta_pdf
# ════════════════════════════════════════════════════════════

ID: RPT-006
Función: exporta_pdf
Capacidad: reports:pdf
Descripción: Permite exportar reportes a formato PDF
Casos de Uso: UC-024 (export PDF)

Acciones permitidas:
✅ Generar PDF con gráficos
✅ Reportes ejecutivos
✅ Documentos formales

Implementación Django:
@require_function('RPT-006')
def export_pdf(request):
    """Exportar a PDF."""
    pass


# ════════════════════════════════════════════════════════════
# RPT-007: ve_kpis
# ════════════════════════════════════════════════════════════

ID: RPT-007
Función: ve_kpis
Capacidad: reports:kpis
Descripción: Permite ver KPIs (Key Performance Indicators)
Casos de Uso: UC-025 (dashboard con KPIs)

Acciones permitidas:
✅ Ver KPIs diarios
✅ Métricas agregadas
✅ Indicadores de performance

Implementación Django:
@require_function('RPT-007')
def view_kpis(request):
    """Ver KPIs."""
    pass


# ════════════════════════════════════════════════════════════
# RPT-008: ve_graficos
# ════════════════════════════════════════════════════════════

ID: RPT-008
Función: ve_graficos
Capacidad: reports:graficos
Descripción: Permite ver gráficos y visualizaciones
Casos de Uso: UC-027, UC-028, UC-029 (diferentes tipos de gráficos)

Acciones permitidas:
✅ Ver gráficos de barras
✅ Ver gráficos de líneas
✅ Ver gráficos de pastel
✅ Visualizaciones interactivas

Implementación Django:
@require_function('RPT-008')
def view_charts(request):
    """Ver gráficos."""
    pass
```

---

<a name="access-reports"></a>
## 3. RELACIÓN ACCESS → REPORTS

### 3.1 Flujo de Autorización

```
┌─────────────────────────────────────────────────────────────┐
│ Usuario Juan solicita reporte cMenu                         │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ REQUEST: POST /api/v1/reports/cmenu/generate/               │
│                                                             │
│ Headers:                                                    │
│   Authorization: Bearer {token}                             │
│                                                             │
│ Body:                                                       │
│ {                                                           │
│   "fecha": "2025-08-17",                                    │
│   "sucursal": "puebla",                                     │
│   "formato": "excel"                                        │
│ }                                                           │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 1: Autenticación (IsAuthenticated)                    │
│                                                             │
│ DRF verifica token JWT                                      │
│ ✅ Token válido → request.user = Juan                       │
│ ❌ Token inválido → 401 Unauthorized                        │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 2: RBAC - Verificación de Funciones                   │
│         (apps/access/)                                      │
│                                                             │
│ @require_function('RPT-001')  # ve_reportes                │
│ @require_function('RPT-005')  # exporta_excel              │
│                                                             │
│ Verifica:                                                   │
│ 1. user.has_function('RPT-001') ?                          │
│ 2. user.has_function('RPT-005') ?                          │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ apps/access/models.py - UserFunctionAssignment             │
│                                                             │
│ Query:                                                      │
│ SELECT * FROM user_function_assignments                     │
│ WHERE user_id = {Juan.id}                                  │
│ AND function_id IN ('RPT-001', 'RPT-005')                  │
│ AND is_active = TRUE                                        │
│ AND (valid_until IS NULL OR valid_until > NOW())           │
│                                                             │
│ Resultado:                                                  │
│ ├─ RPT-001: ✅ Asignado (permanente)                        │
│ ├─ RPT-005: ✅ Asignado (temporal hasta 2025-12-31)         │
│ └─ Otras: No asignadas                                     │
└────────────┬────────────────────────────────────────────────┘
             │
             │ ✅ Tiene ambas funciones
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 3: Separación de Funciones (SoD)                      │
│                                                             │
│ Verificar reglas SoD:                                       │
│ ¿RPT-001 y RPT-005 son incompatibles?                      │
│                                                             │
│ Query función_separation_rules:                            │
│ - No hay regla SoD para RPT-001 + RPT-005                  │
│                                                             │
│ ✅ SoD OK (no hay conflicto)                                │
└────────────┬────────────────────────────────────────────────┘
             │
             │ ✅ Autorizado
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 4: Lógica de Negocio (apps/reports/)                  │
│                                                             │
│ CMenuReportViewSet.generate():                             │
│ 1. Verificar que ETL corrió (via PIPELINE)                 │
│ 2. Query datos                                              │
│ 3. Generar Excel                                            │
│ 4. Response                                                 │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ RESPONSE: 200 OK                                            │
│                                                             │
│ {                                                           │
│   "status": "completed",                                    │
│   "file_url": "/media/reports/cmenu_puebla_170825.xlsx"    │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Implementación en ViewSet

```python
# ════════════════════════════════════════════════════════════
# apps/reports/views.py - Integración con ACCESS
# ════════════════════════════════════════════════════════════

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.access.decorators import require_function
from apps.access.permissions import HasFunction


class CMenuReportViewSet(viewsets.ViewSet):
    """
    ViewSet para reportes cMenu.
    
    Funciones requeridas:
    - RPT-001: ve_reportes (ver)
    - RPT-003: filtra_reportes (filtrar)
    - RPT-004: exporta_csv (CSV)
    - RPT-005: exporta_excel (Excel)
    - RPT-006: exporta_pdf (PDF)
    """
    
    permission_classes = [IsAuthenticated]
    
    # ────────────────────────────────────────────────────────
    # OPCIÓN A: Decorador @require_function
    # ────────────────────────────────────────────────────────
    
    @action(detail=False, methods=['get'])
    @require_function('RPT-001')  # ← Verifica ve_reportes
    def list_reports(self, request):
        """
        Listar reportes disponibles.
        
        GET /api/v1/reports/cmenu/list/
        
        Requiere: RPT-001 (ve_reportes)
        """
        from apps.reports.services import CMenuReportService
        
        # Si llegó aquí, usuario tiene RPT-001 ✓
        
        reports = CMenuReportService.get_available_reports(
            user=request.user
        )
        
        return Response(reports)
    
    # ────────────────────────────────────────────────────────
    # OPCIÓN B: Permission class HasFunction
    # ────────────────────────────────────────────────────────
    
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated, HasFunction('RPT-001', 'RPT-005')]
    )
    def generate_excel(self, request):
        """
        Generar reporte cMenu en Excel.
        
        POST /api/v1/reports/cmenu/generate-excel/
        
        Requiere:
        - RPT-001 (ve_reportes)
        - RPT-005 (exporta_excel)
        """
        # Si llegó aquí, usuario tiene ambas funciones ✓
        
        # ... lógica de generación
        
        return Response({
            "status": "completed",
            "file_url": "/media/reports/..."
        })
    
    # ────────────────────────────────────────────────────────
    # OPCIÓN C: Verificación manual (más control)
    # ────────────────────────────────────────────────────────
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generar reporte (formato variable).
        
        POST /api/v1/reports/cmenu/generate/
        
        Body:
        {
            "formato": "excel|csv|pdf"
        }
        
        Requiere funciones según formato:
        - excel → RPT-001 + RPT-005
        - csv → RPT-001 + RPT-004
        - pdf → RPT-001 + RPT-006
        """
        formato = request.data.get('formato', 'excel')
        
        # Verificar RPT-001 (siempre requerido)
        if not request.user.has_function('RPT-001'):
            return Response({
                "error": "No tiene permiso para ver reportes",
                "required_function": "RPT-001 (ve_reportes)"
            }, status=403)
        
        # Verificar función de export según formato
        export_functions = {
            'excel': 'RPT-005',
            'csv': 'RPT-004',
            'pdf': 'RPT-006'
        }
        
        required_function = export_functions.get(formato)
        
        if not request.user.has_function(required_function):
            return Response({
                "error": f"No tiene permiso para exportar {formato}",
                "required_function": required_function
            }, status=403)
        
        # Usuario tiene permisos ✓
        # Proceder con generación...
        
        from apps.reports.services import CMenuReportService
        from apps.reports.exporters import ExcelExporter, CSVExporter, PDFExporter
        
        # Query datos
        data = CMenuReportService.get_cmenu_data(...)
        
        # Generar según formato
        if formato == 'excel':
            filepath = ExcelExporter.generate_cmenu_excel(data)
        elif formato == 'csv':
            filepath = CSVExporter.generate_csv(data)
        elif formato == 'pdf':
            filepath = PDFExporter.generate_pdf(data)
        
        return Response({
            "status": "completed",
            "file_url": filepath
        })
```

### 3.3 user.has_function() - Implementación

```python
# ════════════════════════════════════════════════════════════
# apps/users/models.py - Método has_function()
# ════════════════════════════════════════════════════════════

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Usuario extendido con RBAC."""
    
    # ... otros campos
    
    def has_function(self, function_id: str) -> bool:
        """
        Verificar si usuario tiene una función asignada.
        
        Args:
            function_id: ID de función (ej: 'RPT-001')
        
        Returns:
            bool: True si tiene la función activa
        
        Verifica:
        1. Función asignada directamente
        2. Función activa (is_active=True)
        3. No expirada (valid_until)
        4. O función asignada vía grupo
        
        Example:
            >>> user.has_function('RPT-001')
            True
            >>> user.has_function('RPT-010')
            False
        """
        from apps.access.models import UserFunctionAssignment
        
        now = timezone.now()
        
        # Verificar asignación directa
        direct_assignment = UserFunctionAssignment.objects.filter(
            user=self,
            function__function_id=function_id,
            is_active=True
        ).filter(
            models.Q(valid_until__isnull=True) |
            models.Q(valid_until__gt=now)
        ).exists()
        
        if direct_assignment:
            return True
        
        # Verificar asignación vía grupo
        from apps.access.models import UserFunctionGroupAssignment, FunctionGroupDetail
        
        # Grupos asignados al usuario
        user_groups = UserFunctionGroupAssignment.objects.filter(
            user=self,
            is_active=True
        ).filter(
            models.Q(valid_until__isnull=True) |
            models.Q(valid_until__gt=now)
        ).values_list('function_group_id', flat=True)
        
        # Verificar si función está en algún grupo
        group_assignment = FunctionGroupDetail.objects.filter(
            function_group_id__in=user_groups,
            function__function_id=function_id
        ).exists()
        
        return group_assignment
    
    def has_all_functions(self, *function_ids: str) -> bool:
        """
        Verificar si usuario tiene TODAS las funciones.
        
        Args:
            *function_ids: IDs de funciones
        
        Returns:
            bool: True si tiene todas
        
        Example:
            >>> user.has_all_functions('RPT-001', 'RPT-005')
            True
        """
        return all(
            self.has_function(func_id)
            for func_id in function_ids
        )
    
    def has_any_function(self, *function_ids: str) -> bool:
        """
        Verificar si usuario tiene AL MENOS UNA función.
        
        Args:
            *function_ids: IDs de funciones
        
        Returns:
            bool: True si tiene al menos una
        
        Example:
            >>> user.has_any_function('RPT-004', 'RPT-005', 'RPT-006')
            True  # Tiene al menos una de export
        """
        return any(
            self.has_function(func_id)
            for func_id in function_ids
        )
    
    def get_assigned_functions(self) -> list:
        """
        Obtener todas las funciones asignadas al usuario.
        
        Returns:
            List[str]: IDs de funciones activas
        
        Example:
            >>> user.get_assigned_functions()
            ['RPT-001', 'RPT-005', 'USR-004', ...]
        """
        from apps.access.models import UserFunctionAssignment
        
        now = timezone.now()
        
        # Directas
        direct = UserFunctionAssignment.objects.filter(
            user=self,
            is_active=True
        ).filter(
            models.Q(valid_until__isnull=True) |
            models.Q(valid_until__gt=now)
        ).values_list('function__function_id', flat=True)
        
        # Via grupos
        from apps.access.models import UserFunctionGroupAssignment, FunctionGroupDetail
        
        user_groups = UserFunctionGroupAssignment.objects.filter(
            user=self,
            is_active=True
        ).filter(
            models.Q(valid_until__isnull=True) |
            models.Q(valid_until__gt=now)
        ).values_list('function_group_id', flat=True)
        
        from_groups = FunctionGroupDetail.objects.filter(
            function_group_id__in=user_groups
        ).values_list('function__function_id', flat=True)
        
        # Combinar y eliminar duplicados
        all_functions = set(list(direct) + list(from_groups))
        
        return sorted(list(all_functions))
```

---

<a name="grupos"></a>
## 4. GRUPOS DE FUNCIONES

### 4.1 Grupos Relevantes para REPORTS

```
GRUPOS QUE INCLUYEN FUNCIONES DE REPORTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AGR-002: agr_operador_reportes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción: Operador que puede ver reportes básicos
Funciones (11 total):
├─ AUTH-004: ve_sesiones_activas
├─ USR-004: lista_usuarios
├─ USR-005: busca_usuarios
├─ USR-009: ve_usuarios
├─ ACC-003: ve_asignaciones
├─ PIP-001: ve_estado_etl
├─ PIP-003: ve_disponibilidad_datos
├─ RPT-001: ve_reportes          ← REPORTS
├─ RPT-002: ve_dashboard         ← REPORTS
├─ RPT-007: ve_kpis              ← REPORTS
└─ ALR-001: ve_alertas

Uso típico:
- Operadores de call center
- Personal de soporte nivel 1
- Consulta de reportes básicos

AGR-003: agr_analista_reportes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción: Analista con permisos avanzados de reportes
Funciones (18 total):
├─ AUTH-004: ve_sesiones_activas
├─ USR-004: lista_usuarios
├─ USR-005: busca_usuarios
├─ USR-009: ve_usuarios
├─ ACC-003: ve_asignaciones
├─ PIP-001: ve_estado_etl
├─ PIP-002: ve_errores_etl
├─ PIP-003: ve_disponibilidad_datos
├─ RPT-001: ve_reportes          ← REPORTS
├─ RPT-002: ve_dashboard         ← REPORTS
├─ RPT-003: filtra_reportes      ← REPORTS
├─ RPT-004: exporta_csv          ← REPORTS
├─ RPT-005: exporta_excel        ← REPORTS
├─ RPT-006: exporta_pdf          ← REPORTS
├─ RPT-007: ve_kpis              ← REPORTS
├─ RPT-008: ve_graficos          ← REPORTS
├─ ALR-001: ve_alertas
└─ ALR-006: ve_historial_alertas

Uso típico:
- Analistas de datos
- Managers de call center
- Personal que genera reportes ejecutivos

AGR-005: agr_administrador_completo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción: Administrador con todas las funciones
Funciones (42 total - TODAS):
├─ ... todas las funciones AUTH
├─ ... todas las funciones USR
├─ ... todas las funciones ACC
├─ ... todas las funciones PIP
├─ RPT-001 a RPT-008            ← TODAS REPORTS
├─ ... todas las funciones ALR
├─ ... todas las funciones AUD
└─ ... todas las funciones LOG

Uso típico:
- Administradores del sistema
- DevOps
- Personal IT senior
```

### 4.2 Asignación de Grupos

```python
# ════════════════════════════════════════════════════════════
# Asignar grupo a usuario
# ════════════════════════════════════════════════════════════

from apps.access.models import UserFunctionGroupAssignment, FunctionGroup
from apps.users.models import User
from datetime import datetime, timedelta

# Usuario analista
user = User.objects.get(username='juan_analista')

# Grupo AGR-003 (agr_analista_reportes)
group = FunctionGroup.objects.get(group_id='AGR-003')

# Asignar grupo (permanente)
assignment = UserFunctionGroupAssignment.objects.create(
    user=user,
    function_group=group,
    is_active=True,
    valid_until=None,  # Permanente
    assigned_by=request.user,
    assignment_reason="Nuevo analista de reportes"
)

# Ahora juan_analista tiene todas las funciones de AGR-003:
# - RPT-001, RPT-002, RPT-003, RPT-004, RPT-005, RPT-006, RPT-007, RPT-008
# - PIP-001, PIP-002, PIP-003
# - USR-004, USR-005, USR-009
# - Etc.

# Verificar
assert user.has_function('RPT-001')  # ✅ True (via grupo)
assert user.has_function('RPT-005')  # ✅ True (via grupo)
assert user.has_function('USR-001')  # ❌ False (no en grupo)
```

---

<a name="implementacion"></a>
## 5. IMPLEMENTACIÓN EN DJANGO

### 5.1 Decorator @require_function

```python
# ════════════════════════════════════════════════════════════
# apps/access/decorators.py
# ════════════════════════════════════════════════════════════

from functools import wraps
from django.http import JsonResponse


def require_function(*function_ids):
    """
    Decorator para requerir funciones en una view.
    
    Args:
        *function_ids: IDs de funciones requeridas
    
    Example:
        @require_function('RPT-001')
        def view_report(request):
            pass
        
        @require_function('RPT-001', 'RPT-005')
        def export_excel(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar autenticación
            if not request.user.is_authenticated:
                return JsonResponse({
                    "error": "No autenticado"
                }, status=401)
            
            # Verificar cada función
            for func_id in function_ids:
                if not request.user.has_function(func_id):
                    return JsonResponse({
                        "error": "Permiso denegado",
                        "required_function": func_id,
                        "message": f"Requiere función {func_id}"
                    }, status=403)
            
            # Usuario tiene todas las funciones requeridas
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_any_function(*function_ids):
    """
    Decorator para requerir AL MENOS UNA función.
    
    Example:
        @require_any_function('RPT-004', 'RPT-005', 'RPT-006')
        def export_report(request):
            # Puede exportar en cualquier formato
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    "error": "No autenticado"
                }, status=401)
            
            # Verificar que tiene al menos una
            if not request.user.has_any_function(*function_ids):
                return JsonResponse({
                    "error": "Permiso denegado",
                    "required_functions": function_ids,
                    "message": "Requiere al menos una función de export"
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
```

### 5.2 Permission Class

```python
# ════════════════════════════════════════════════════════════
# apps/access/permissions.py
# ════════════════════════════════════════════════════════════

from rest_framework.permissions import BasePermission


class HasFunction(BasePermission):
    """
    Permission class para DRF ViewSets.
    
    Example:
        class ReportViewSet(viewsets.ViewSet):
            permission_classes = [HasFunction('RPT-001')]
    """
    
    def __init__(self, *function_ids):
        self.function_ids = function_ids
    
    def has_permission(self, request, view):
        """Verificar que usuario tiene las funciones."""
        if not request.user.is_authenticated:
            return False
        
        return request.user.has_all_functions(*self.function_ids)
    
    def __call__(self, *args, **kwargs):
        """Permitir instanciación en permission_classes."""
        return self


class HasAnyFunction(BasePermission):
    """Permission para requerir AL MENOS UNA función."""
    
    def __init__(self, *function_ids):
        self.function_ids = function_ids
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.has_any_function(*self.function_ids)
    
    def __call__(self, *args, **kwargs):
        return self
```

---

<a name="permisos-temporales"></a>
## 6. PERMISOS TEMPORALES

### 6.1 Asignación Temporal

```python
# ════════════════════════════════════════════════════════════
# Asignar función temporal
# ════════════════════════════════════════════════════════════

from apps.access.models import UserFunctionAssignment, Function
from apps.users.models import User
from datetime import datetime, timedelta

# Usuario operador básico
user = User.objects.get(username='maria_operador')

# Normalmente solo tiene AGR-002 (operador básico)
# que incluye: RPT-001, RPT-002, RPT-007

# Necesita exportar Excel por proyecto especial (RPT-005)
function = Function.objects.get(function_id='RPT-005')

# Asignar temporalmente por 30 días
assignment = UserFunctionAssignment.objects.create(
    user=user,
    function=function,
    is_active=True,
    valid_until=datetime.now() + timedelta(days=30),
    assigned_by=request.user,
    assignment_reason="Proyecto Q4 - Reportes ejecutivos"
)

# Durante 30 días:
assert user.has_function('RPT-005')  # ✅ True

# Después de 30 días:
# → Permiso expira automáticamente
# → user.has_function('RPT-005') retorna False
```

### 6.2 Consultar Permisos Temporales

```python
# ════════════════════════════════════════════════════════════
# Listar permisos temporales activos
# ════════════════════════════════════════════════════════════

from apps.access.models import UserFunctionAssignment
from django.utils import timezone

# Asignaciones temporales activas
temporal_assignments = UserFunctionAssignment.objects.filter(
    user=user,
    is_active=True,
    valid_until__isnull=False,
    valid_until__gt=timezone.now()
).select_related('function')

for assignment in temporal_assignments:
    print(f"{assignment.function.function_id}: "
          f"{assignment.function.name} "
          f"(vence: {assignment.valid_until})")

# Output:
# RPT-005: exporta_excel (vence: 2025-09-17 00:00:00)
```

---

<a name="sod"></a>
## 7. SEPARACIÓN DE FUNCIONES (SoD)

### 7.1 Reglas SoD del Sistema

```
REGLAS DE SEPARACIÓN (3 reglas en v5.2.0):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOD-001: Separación Usuarios-Access
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción: Quien crea usuarios NO puede asignar funciones
Razón: Prevenir creación de super-usuarios sin supervisión

Funciones incompatibles:
├─ USR-001 (crea_usuarios)
└─ ACC-001 (asigna_funciones)

Impacto en Reports: NINGUNO
(No hay funciones RPT en esta regla)


SOD-002: Separación Auditoría-Logs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción: Quien ve auditoría NO puede exportar logs técnicos
Razón: Separar auditoría funcional de troubleshooting técnico

Funciones incompatibles:
├─ AUD-001 (ve_auditoria)
└─ LOG-002 (exporta_logs)

Impacto en Reports: NINGUNO


SOD-003: Separación Pipeline-Audit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descripción: Quien solicita reintentos ETL NO puede exportar auditoría
Razón: Prevenir manipulación de evidencia

Funciones incompatibles:
├─ PIP-004 (solicita_reintento_etl)
└─ AUD-003 (exporta_auditoria)

Impacto en Reports: NINGUNO

CONCLUSIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ NO hay reglas SoD que afecten funciones de REPORTS
✅ Todas las 8 funciones RPT pueden coexistir
✅ Usuario puede tener RPT-001 a RPT-008 simultáneamente
```

---

## RESUMEN PARTE 4

```
CONTENIDO CUBIERTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Modelo RBAC IACT v5.2.0
   - Filosofía "Sin Pretensiones"
   - 42 funciones atómicas
   - 8 módulos funcionales

✅ MOD_Reports - 8 funciones (19% del sistema)
   - RPT-001 a RPT-008 descritas en detalle
   - Casos de uso mapeados
   - Limitaciones (CNST-007)

✅ Relación ACCESS → REPORTS
   - Flujo de autorización (4 capas)
   - user.has_function() implementado
   - Integración en ViewSets

✅ Grupos de Funciones
   - AGR-002: agr_operador_reportes (3 RPT)
   - AGR-003: agr_analista_reportes (8 RPT - TODAS)
   - AGR-005: agr_administrador_completo (42 total)

✅ Implementación Django
   - @require_function decorator
   - HasFunction permission class
   - Ejemplos completos

✅ Permisos Temporales
   - Asignación con valid_until
   - Expiración automática
   - Consultas

✅ Separación de Funciones (SoD)
   - 3 reglas del sistema
   - Ninguna afecta REPORTS

PRÓXIMA PARTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PARTE 5/6: Ejemplos de N Reportes/Dashboards
- Patrón de implementación repetible
- Casos completos end-to-end
- Diferentes tipos de reportes
```

---

**FIN DE PARTE 4/6**

Documento: ANALISIS_RELACIONES v2.0.0 - PARTE 4/6  
Fecha: 2026-01-17  
Estado: Completo  
Basado en: MODELO_RBAC_IACT_v5_2_0.md  
Siguiente: PARTE 5/6 - Ejemplos de N Reportes
