# URLS REPORTES Y DASHBOARDS - Separación Arquitectónica

**Versión:** 1.0.0  
**Fecha:** 2026-01-21  
**Relacionado con:** MODELO_RBAC_IACT_v6_0_0 (Separación MOD_Reports y MOD_Dashboard)

---

## 📋 RESUMEN

Este documento explica la **separación arquitectónica** entre:
- **apps/reports/**: Generación de reportes tabulares
- **apps/dashboard/**: Visualización de métricas y widgets

**Cambio desde v5.2.1 → v6.0.0:**
- ❌ ANTES: Todo en `apps/reports/`
- ✅ AHORA: `apps/reports/` + `apps/dashboard/` separados

---

## 🎯 JUSTIFICACIÓN SEPARACIÓN

### Razones Técnicas

```yaml
1. Apps Django separadas:
   ✅ apps/reports/: Generación y exportación
   ✅ apps/dashboard/: Visualización y widgets

2. Endpoints diferentes:
   ✅ /api/v1/reports/: CRUD de reportes
   ✅ /api/v1/dashboard/: GET visualizaciones

3. Permisos independientes:
   ✅ reports.*: create, view, delete, export
   ✅ dashboard.*: view, export, share, edit

4. Responsabilidad única (SOLID):
   ✅ Reports: Genera datos tabulares
   ✅ Dashboard: Muestra métricas visuales

5. Flujo de datos diferente:
   ✅ Reports: Create → Filter → Export
   ✅ Dashboard: View (datos pre-calculados)
```

### Antes (v5.2.1) - MEZCLADO

```python
# apps/reports/views.py
class ReportViewSet(viewsets.ModelViewSet):
    """Mezclaba reportes + dashboards."""
    
    @action(methods=['get'], detail=False)
    def generate(self, request):
        """Genera reporte tabular."""
        pass
    
    @action(methods=['get'], detail=False)  # ❌ MEZCLADO
    def dashboard_view(self, request):
        """Muestra dashboard."""
        pass
    
    @action(methods=['get'], detail=False)  # ❌ MEZCLADO
    def kpis(self, request):
        """Retorna KPIs."""
        pass
```

### Después (v6.0.0) - SEPARADO

```python
# apps/reports/views.py
class ReportViewSet(viewsets.ModelViewSet):
    """Solo reportes tabulares."""
    
    @action(methods=['post'], detail=False)
    def create_report(self, request):
        """Crea configuración de reporte."""
        pass
    
    @action(methods=['post'], detail=True)
    def export(self, request, pk=None):
        """Exporta reporte a CSV/Excel/PDF."""
        pass

# apps/dashboard/views.py ⭐ NUEVO
class DashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """Solo dashboards visuales."""
    
    def retrieve(self, request, tipo=None):
        """Retorna dashboard con widgets."""
        pass
    
    @action(methods=['post'], detail=True)
    def export(self, request, tipo=None):
        """Exporta snapshot dashboard."""
        pass
```

---

## 🌐 ARQUITECTURA URLS

### apps/reports/ - Reportes Tabulares

**Base URL:** `/api/v1/reports/`

**Endpoints:**

```yaml
POST   /api/v1/reports/{tipo}/
  Crea configuración de reporte
  Requiere: reports.create
  Body:
    trimestre: Q1 | Q2 | Q3 | Q4
    año: 2025
    did: opcional
    menu: opcional
    fecha_inicio: opcional (YYYY-MM-DD)
    fecha_fin: opcional (YYYY-MM-DD)
  Response:
    id: 123
    tipo: "llamadas-abandonadas"
    estado: "pendiente"
    created_at: "2026-01-21T10:00:00Z"

GET    /api/v1/reports/{tipo}/
  Lista reportes del tipo especificado
  Requiere: reports.view
  Filtros: trimestre, año, estado
  Response:
    count: 10
    results: [
      {id: 123, tipo: "llamadas-abandonadas", ...},
      ...
    ]

GET    /api/v1/reports/{tipo}/{id}/
  Detalle de reporte específico
  Requiere: reports.view
  Response:
    id: 123
    tipo: "llamadas-abandonadas"
    data: [...] # Datos tabulares
    filtros: {...}
    created_at: "..."

POST   /api/v1/reports/{tipo}/{id}/export/
  Exporta reporte a formato especificado
  Requiere: reports.export.{format}
  Body:
    format: csv | excel | pdf
  Response:
    file_url: "/media/exports/reporte_123.csv"
    expires_at: "2026-01-22T10:00:00Z"

DELETE /api/v1/reports/{tipo}/{id}/
  Elimina reporte
  Requiere: reports.delete
  Response: 204 No Content
```

**Tipos de reportes soportados:**

```yaml
llamadas-abandonadas:
  permission_django: reports.view
  Tipo: RPT-TR-021 (trimestral)
  Filtros: trimestre, año, did opcional

clientes-unicos:
  permission_django: reports.view
  Tipo: RPT-TR-011 (trimestral)
  Filtros: trimestre, año, did

promedio-clientes:
  permission_django: reports.view
  Tipo: RPT-TR-031 (trimestral)
  Filtros: trimestre, año

clientes-menu:
  permission_django: reports.view
  Tipo: RPT-TR-041 (trimestral)
  Filtros: trimestre, año, menu opcional

llamadas-menu:
  permission_django: reports.view
  Tipo: RPT-TR-121 (trimestral)
  Filtros: trimestre, año, menu opcional

detalle-transferencias:
  permission_django: reports.view
  Tipo: RPT-DET-001 (mensual)
  Filtros: mes, año

menu-errores:
  permission_django: reports.view
  Tipo: RPT-ERR-001 (anual)
  Filtros: año
```

### apps/dashboard/ - Dashboards Visuales

**Base URL:** `/api/v1/dashboard/`

**Endpoints:**

```yaml
GET    /api/v1/dashboard/{tipo}/
  Retorna dashboard con widgets pre-calculados
  Requiere: dashboard.view
  Parámetros query opcionales:
    refresh: true | false (fuerza recálculo)
  Response:
    tipo: "metricas-trimestrales"
    kpis: [
      {nombre: "Total Llamadas", valor: 15234, cambio: "+5.2%"},
      {nombre: "Tasa Abandono", valor: "12.3%", cambio: "-2.1%"},
      ...
    ]
    charts: [
      {
        tipo: "bar",
        nombre: "Top 10 Menús",
        data: [...],
        config: {...}
      },
      ...
    ]
    tables: [
      {
        nombre: "Detalle por DID",
        headers: ["DID", "Llamadas", "Abandono"],
        rows: [[...], ...]
      }
    ]
    metadata:
      generado_at: "2026-01-21T10:00:00Z"
      desfase_horas: 8
      cache_expires: "2026-01-21T10:05:00Z"

POST   /api/v1/dashboard/{tipo}/export/
  Exporta snapshot actual del dashboard
  Requiere: dashboard.export.{format}
  Body:
    format: csv | excel | pdf
  Response:
    file_url: "/media/exports/dashboard_TRIM_2026-01-21.xlsx"
    expires_at: "2026-01-22T10:00:00Z"
```

**Tipos de dashboards disponibles:**

```yaml
metricas-trimestrales:
  permission_django: dashboard.view
  Tipo: DASH-TRIM
  Contenido:
    KPIs (3): Total llamadas, Tasa abandono, Clientes únicos
    Charts (2): Top 10 menús (bar), Tendencia trimestral (line)
    Tables (1): Detalle por DID
  Actualización: Cada 6-12h

analisis-clientes:
  permission_django: dashboard.view
  Tipo: DASH-CLI
  Contenido:
    KPIs (3): Clientes únicos, Promedio por menú, Recurrentes
    Charts (2): Distribución por menú (pie), Tendencia clientes (line)
    Tables (1): Top clientes
  Actualización: Cada 6-12h

performance-ivr:
  permission_django: dashboard.view
  Tipo: DASH-IVR
  Contenido:
    KPIs (2): Total llamadas, Tasa éxito transferencia
    Charts (2): Llamadas por menú (bar), Distribución transferencias (pie)
    Tables (2): Errores detectados, Últimos errores
  Actualización: Cada 6-12h
```

---

## 🔀 COMPARACIÓN ENDPOINTS

### Reportes (apps/reports/)

```yaml
Características:
  - Modelo: CREATE → READ → EXPORT → DELETE
  - Usuario CREA reporte con filtros
  - Sistema GENERA datos según filtros
  - Usuario EXPORTA resultado
  
Flujo típico:
  1. POST /api/v1/reports/llamadas-abandonadas/
     → Crea configuración con trimestre, año
  2. GET /api/v1/reports/llamadas-abandonadas/123/
     → Ve datos tabulares generados
  3. POST /api/v1/reports/llamadas-abandonadas/123/export/
     → Exporta a CSV/Excel/PDF

Datos:
  ✅ Dinámicos (según filtros)
  ✅ Generados on-demand
  ✅ Históricos (cualquier período)
  ✅ Tabulares (filas y columnas)
  
Permisos:
  - reports.create
  - reports.view
  - reports.delete
  - reports.export.csv
  - reports.export.excel
  - reports.export.pdf
```

### Dashboards (apps/dashboard/)

```yaml
Características:
  - Modelo: READ-ONLY
  - Usuario solo VE dashboard pre-calculado
  - Sistema ACTUALIZA cada 6-12h automáticamente
  - Usuario puede EXPORTAR snapshot
  
Flujo típico:
  1. GET /api/v1/dashboard/metricas-trimestrales/
     → Ve widgets, KPIs, gráficos
  2. POST /api/v1/dashboard/metricas-trimestrales/export/
     → Exporta snapshot actual

Datos:
  ✅ Estáticos (pre-calculados)
  ✅ Cache 5 minutos
  ✅ Período fijo (último trimestre)
  ✅ Visuales (KPIs, charts, tables)
  
Permisos:
  - dashboard.view
  - dashboard.export.csv
  - dashboard.export.excel
  - dashboard.export.pdf
  - dashboard.share (planificado)
  - dashboard.edit (planificado)
```

---

## 📊 EJEMPLOS

### Ejemplo 1: Generar Reporte

```python
# Cliente hace request
POST /api/v1/reports/llamadas-abandonadas/
Content-Type: application/json
Authorization: Bearer {token}  # User con reports.create

{
  "trimestre": "Q3",
  "año": 2025,
  "did": "600123456"  // opcional
}

# Sistema responde
{
  "id": 789,
  "tipo": "llamadas-abandonadas",
  "estado": "procesando",
  "filtros": {
    "trimestre": "Q3",
    "año": 2025,
    "did": "600123456"
  },
  "created_at": "2026-01-21T14:30:00Z",
  "estimated_completion": "2026-01-21T14:32:00Z"
}

# Cliente consulta resultado
GET /api/v1/reports/llamadas-abandonadas/789/
Authorization: Bearer {token}  # User con reports.view

# Sistema responde
{
  "id": 789,
  "tipo": "llamadas-abandonadas",
  "estado": "completado",
  "data": [
    {
      "did": "600123456",
      "menu": "Ventas",
      "total_llamadas": 1234,
      "abandonadas": 152,
      "tasa_abandono": 0.123
    },
    ...
  ],
  "total_rows": 45,
  "filtros": {...},
  "generated_at": "2026-01-21T14:31:45Z"
}

# Cliente exporta
POST /api/v1/reports/llamadas-abandonadas/789/export/
Authorization: Bearer {token}  # User con reports.export.csv

{
  "format": "csv"
}

# Sistema responde
{
  "file_url": "/media/exports/reporte_789_2026-01-21.csv",
  "file_size": "125KB",
  "expires_at": "2026-01-22T14:30:00Z"
}
```

### Ejemplo 2: Ver Dashboard

```python
# Cliente hace request
GET /api/v1/dashboard/metricas-trimestrales/
Authorization: Bearer {token}  # User con dashboard.view

# Sistema responde (datos pre-calculados)
{
  "tipo": "metricas-trimestrales",
  "periodo": {
    "trimestre": "Q4",
    "año": 2025
  },
  "kpis": [
    {
      "nombre": "Total Llamadas",
      "valor": 15234,
      "formato": "número",
      "cambio_porcentaje": "+5.2%",
      "tendencia": "up"
    },
    {
      "nombre": "Tasa Abandono",
      "valor": 12.3,
      "formato": "porcentaje",
      "cambio_porcentaje": "-2.1%",
      "tendencia": "down"
    },
    {
      "nombre": "Clientes Únicos",
      "valor": 3456,
      "formato": "número",
      "cambio_porcentaje": "+8.5%",
      "tendencia": "up"
    }
  ],
  "charts": [
    {
      "id": "chart-top-menus",
      "tipo": "bar",
      "nombre": "Top 10 Menús por Llamadas",
      "data": {
        "labels": ["Ventas", "Soporte", "Info", ...],
        "series": [1234, 987, 876, ...]
      },
      "config": {
        "height": 400,
        "colors": ["#3498db", "#2ecc71", ...]
      }
    },
    {
      "id": "chart-tendencia",
      "tipo": "line",
      "nombre": "Tendencia Trimestral",
      "data": {
        "labels": ["Oct", "Nov", "Dic"],
        "series": [4500, 5234, 5500]
      },
      "config": {
        "height": 300,
        "showPoints": true
      }
    }
  ],
  "tables": [
    {
      "id": "table-detalle-did",
      "nombre": "Detalle por DID",
      "headers": ["DID", "Llamadas", "Abandonadas", "% Abandono"],
      "rows": [
        ["600123456", "1234", "152", "12.3%"],
        ["600789012", "987", "98", "9.9%"],
        ...
      ],
      "total_rows": 15
    }
  ],
  "metadata": {
    "generado_at": "2026-01-21T08:00:00Z",
    "desfase_horas": 8,
    "cache_expires": "2026-01-21T14:05:00Z",
    "siguiente_actualizacion": "2026-01-21T20:00:00Z"
  }
}

# Cliente exporta snapshot
POST /api/v1/dashboard/metricas-trimestrales/export/
Authorization: Bearer {token}  # User con dashboard.export.excel

{
  "format": "excel"
}

# Sistema responde
{
  "file_url": "/media/exports/dashboard_TRIM_2026-01-21.xlsx",
  "file_size": "245KB",
  "contenido": [
    "Hoja 1: KPIs",
    "Hoja 2: Top 10 Menús",
    "Hoja 3: Tendencia Trimestral",
    "Hoja 4: Detalle por DID"
  ],
  "expires_at": "2026-01-22T14:30:00Z"
}
```

---

## 🔒 PERMISOS

### Matriz de Permisos

| Operación | Reporte | Dashboard | permission_django |
|-----------|---------|-----------|-------------------|
| **Ver datos** | ✅ | ✅ | reports.view, dashboard.view |
| **Crear configuración** | ✅ | ❌ | reports.create |
| **Editar configuración** | ❌ | ❌ (planificado) | - |
| **Eliminar** | ✅ | ❌ | reports.delete |
| **Exportar CSV** | ✅ | ✅ | reports.export.csv, dashboard.export.csv |
| **Exportar Excel** | ✅ | ✅ | reports.export.excel, dashboard.export.excel |
| **Exportar PDF** | ⏳ Planif | ⏳ Planif | reports.export.pdf, dashboard.export.pdf |
| **Compartir** | ❌ | ⏳ Planif | dashboard.share |

### Separación de Permisos

```yaml
Usuario Analista:
  Tiene: reports.view, reports.create, reports.export.csv
  Puede:
    ✅ Crear reportes con filtros personalizados
    ✅ Ver datos tabulares
    ✅ Exportar a CSV
  NO puede:
    ❌ Ver dashboards (necesita dashboard.view)
    ❌ Exportar dashboards

Usuario Gerente:
  Tiene: dashboard.view, dashboard.export.excel
  Puede:
    ✅ Ver dashboards pre-calculados
    ✅ Exportar dashboards a Excel
  NO puede:
    ❌ Crear reportes personalizados (necesita reports.create)
    ❌ Ver datos tabulares de reportes

Usuario Completo:
  Tiene: reports.*, dashboard.*
  Puede:
    ✅ TODO lo anterior
```

---

## 🏗️ ARQUITECTURA APPS

```
src/callcentersite/apps/

reports/
├── models/
│   └── report.py              # Report model (configuración + data)
├── serializers/
│   ├── report_serializer.py
│   └── export_serializer.py
├── viewsets/
│   └── report_viewset.py      # CRUD + export
├── services/
│   ├── report_generator.py    # Genera datos según filtros
│   └── export_service.py      # CSV, Excel, PDF
└── urls.py → /api/v1/reports/

dashboard/
├── models/
│   └── dashboard_cache.py     # Cache de dashboards
├── serializers/
│   └── dashboard_serializer.py
├── viewsets/
│   └── dashboard_viewset.py   # Read-only + export
├── services/
│   ├── dashboard_builder.py   # Construye widgets
│   ├── kpi_calculator.py      # Calcula KPIs
│   └── chart_builder.py       # Genera configs charts
└── urls.py → /api/v1/dashboard/
```

---

## 📝 RESTRICCIONES

```yaml
Reportes (CNST-007):
  - Límite CSV: 100K registros
  - Límite Excel: 50K registros
  - Límite PDF: 10K registros
  - Timeout generación: 30s
  - SLA reportes ligeros: <5s
  - SLA reportes pesados: <30s

Dashboards (CNST-023):
  - Datos estáticos (desfase 6-12h)
  - Cache locmem: 5 minutos
  - NO auto-refresh
  - NO real-time (sin WebSockets/SSE/polling)
  - Actualización: Scheduler cada 6-12h
```

---

## 📚 DOCUMENTOS RELACIONADOS

```yaml
Modelo RBAC:
  - MODELO_RBAC_IACT_v6_0_0_PARTE_1.md (Sección 3.5 y 3.6)

Apps Access:
  - apps/access/README.md (Funciones reports.* y dashboard.*)

Arquitectura:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md
```

---

**Versión:** 1.0.0  
**Fecha:** 2026-01-21  
**Estado:** ✅ DEFINITIVO  
**Ubicación:** `/tmp/iact-real/docs/arquitectura/URLS_REPORTES_Y_DASHBOARDS.md`
