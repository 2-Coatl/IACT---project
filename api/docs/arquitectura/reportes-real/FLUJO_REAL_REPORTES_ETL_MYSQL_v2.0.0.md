---
version: 2.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Flujo Real de Reportes
categoria: arquitectura/reportes-real
tema: Flujo Real - ETL en MySQL, Django solo consume datos limpios
autor: Claude Technical Analysis
tags: [reportes, etl, mysql, django-readonly, unmanaged-models]
relacionado:
  - ANALISIS_CALLRECORD_MODELO_VS_SERIALIZER_v1.0.0.md (OBSOLETO - basado en supuestos incorrectos)
  - Reporte_cMenu_180825.xlsx (ejemplo real)
estado: completado
---

# FLUJO REAL DE REPORTES - ETL en MySQL, Django READ-ONLY

**Basado en aclaración del usuario: "No guardaremos datos, solo consumiremos"**

---

## RESUMEN EJECUTIVO

### Corrección de Supuestos

```
SUPUESTO ANTERIOR (INCORRECTO):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVR_LEGACY → Django ETLService → CallRecord.save() → SQLite
            ❌ FALSO

FLUJO REAL (CORRECTO):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVR_LEGACY → ETL en MySQL → Tablas agregadas → Django query (READ-ONLY)
            ✅ VERDADERO

Django NO guarda datos
Django SOLO consume datos ya procesados
ETL corre en MySQL (stored procedures, jobs, etc)
```

---

## TABLA DE CONTENIDOS

1. [Flujo Real del Sistema](#flujo-real)
2. [Análisis del Excel](#excel)
3. [Arquitectura Django Correcta](#arquitectura)
4. [Modelos Unmanaged vs Serializers](#modelos)
5. [Ejemplo de Implementación](#implementacion)

---

<a name="flujo-real"></a>
## 1. FLUJO REAL DEL SISTEMA

### 1.1 Usuario Juan - Flujo Completo

```
PASO 1: Usuario se conecta
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usuario: Juan
Perfil: Analista de Call Center
Permiso: reports.view_cmenu_report (RBAC via ACCESS)

Juan abre navegador → https://callcenter.com/reports


PASO 2: Navega a módulo de reportes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Juan → Dashboard → Reportes → Reporte cMenu

Frontend muestra formulario:
- Fecha inicio: [01/08/2025]
- Fecha fin: [18/08/2025]
- Sucursal: [Puebla / Nacional / Todas]
- Formato: [Excel / CSV / PDF]

Juan selecciona:
- Fecha: 18/08/2025
- Sucursal: Puebla
- Formato: Excel

[Generar Reporte] ← Click


PASO 3: Request a Django API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST /api/v1/reports/cmenu/generate/

Headers:
  Authorization: Bearer {token}

Body:
{
  "fecha_inicio": "2025-08-18",
  "fecha_fin": "2025-08-18",
  "sucursal": "puebla",
  "formato": "excel"
}


PASO 4: Django VIEW procesa request
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# apps/reports/views.py

class CMenuReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, CanViewCMenuReport]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generar reporte cMenu."""
        
        # 1. Validar permissions (RBAC via ACCESS)
        if not request.user.has_function('reports.view_cmenu_report'):
            return Response({"detail": "Sin permiso"}, 403)
        
        # 2. Validar input
        serializer = CMenuReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 3. Query datos desde MySQL (TABLA YA PROCESADA POR ETL)
        from apps.reports.services import CMenuReportService
        
        data = CMenuReportService.get_cmenu_data(
            fecha_inicio=serializer.validated_data['fecha_inicio'],
            fecha_fin=serializer.validated_data['fecha_fin'],
            sucursal=serializer.validated_data['sucursal']
        )
        
        # 4. Generar Excel
        from apps.reports.exporters import ExcelExporter
        
        excel_file = ExcelExporter.generate_cmenu_excel(
            data=data,
            sucursal=serializer.validated_data['sucursal']
        )
        
        # 5. Return file
        return Response({
            "file_url": excel_file,
            "status": "completed"
        })


PASO 5: CMenuReportService QUERY MySQL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# apps/reports/services.py

class CMenuReportService:
    
    @staticmethod
    def get_cmenu_data(fecha_inicio, fecha_fin, sucursal):
        """
        Query tabla agregada en MySQL.
        
        IMPORTANTE:
        - Django NO procesa datos
        - Django NO hace ETL
        - Django SOLO query tabla ya procesada
        """
        
        # OPCIÓN A: Modelo Unmanaged (recomendado)
        from apps.reports.models import CMenuAgregado
        
        queryset = CMenuAgregado.objects.using('analytics_db').filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin,
            sucursal=sucursal
        )
        
        return list(queryset.values(
            'cmenu_opcion',
            'total_llamadas',
            'fecha',
            'sucursal'
        ))
        
        # OPCIÓN B: Raw SQL (alternativa)
        # from django.db import connection
        # 
        # with connection.cursor() as cursor:
        #     cursor.execute("""
        #         SELECT cmenu_opcion, total_llamadas, fecha, sucursal
        #         FROM reporte_cmenu_agregado
        #         WHERE fecha BETWEEN %s AND %s
        #         AND sucursal = %s
        #     """, [fecha_inicio, fecha_fin, sucursal])
        #     
        #     columns = [col[0] for col in cursor.description]
        #     return [dict(zip(columns, row)) for row in cursor.fetchall()]


PASO 6: Tabla en MySQL (CREADA POR ETL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

-- Tabla creada y mantenida por ETL en MySQL
-- Django SOLO lee, NUNCA escribe

CREATE TABLE reporte_cmenu_agregado (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    sucursal VARCHAR(50) NOT NULL,
    cmenu_opcion VARCHAR(100),
    total_llamadas INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_fecha_sucursal (fecha, sucursal),
    INDEX idx_cmenu_opcion (cmenu_opcion)
);

-- Datos insertados por ETL (stored procedure, job, etc)
-- Ejemplo de datos:

| fecha      | sucursal | cmenu_opcion         | total_llamadas |
|------------|----------|----------------------|----------------|
| 2025-08-18 | puebla   | NULL                 | 11592          |
| 2025-08-18 | puebla   | Opción Invalida      | 185            |
| 2025-08-18 | puebla   | ANI                  | 2181           |
| 2025-08-18 | puebla   | cliente_colgo        | 12075          |
| 2025-08-18 | puebla   | Desborde_Cabecera    | 11682          |
| 2025-08-18 | nacional | NULL                 | 238049         |
| 2025-08-18 | nacional | Opción Invalida      | 77             |
| ...        | ...      | ...                  | ...            |

Total Puebla: 132,473
Total Nacional: 2,567,201


PASO 7: ExcelExporter genera archivo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# apps/reports/exporters.py

class ExcelExporter:
    
    @staticmethod
    def generate_cmenu_excel(data, sucursal):
        """Generar Excel como Reporte_cMenu_180825.xlsx"""
        
        import openpyxl
        from openpyxl.styles import Font, Alignment
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = sucursal.capitalize()
        
        # Headers
        ws['A1'] = 'cMenu'
        ws['B1'] = 'Numero'
        ws['D1'] = 'Total'
        
        # Total general
        total = sum(row['total_llamadas'] for row in data)
        ws['E1'] = total
        
        # Datos
        row_num = 2
        for item in data:
            ws[f'A{row_num}'] = item['cmenu_opcion']
            ws[f'B{row_num}'] = item['total_llamadas']
            row_num += 1
        
        # Styling
        ws['A1'].font = Font(bold=True)
        ws['B1'].font = Font(bold=True)
        ws['D1'].font = Font(bold=True)
        ws['E1'].font = Font(bold=True)
        
        # Save
        filepath = f'/tmp/reports/cmenu_{sucursal}_{fecha}.xlsx'
        wb.save(filepath)
        
        return filepath


PASO 8: Response a usuario
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HTTP 200 OK
{
  "file_url": "/media/reports/cmenu_puebla_20250818.xlsx",
  "status": "completed",
  "total_records": 25,
  "total_llamadas": 132473
}

Frontend muestra:
✅ Reporte generado exitosamente
[Descargar Excel] ← Link
```

---

<a name="excel"></a>
## 2. ANÁLISIS DEL EXCEL

### 2.1 Estructura del Reporte

```
HOJA 1: Puebla
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| cMenu                        | Numero | Total | 132473 |
|------------------------------|--------|-------|--------|
| NULL                         | 11592  |       |        |
| Opción Invalida              | 185    |       |        |
| ANI                          | 2181   |       |        |
| cliente_colgo                | 12075  |       |        |
| Desborde_Cabecera            | 11682  |       |        |
| Desborde_Promocional         | 3519   |       |        |
| KIPSOLCOM                    | 491    |       |        |
| Marque3                      | 3506   |       |        |
| MenuSaldosCabecera           | 2      |       |        |
| NOTMX-CONT-Contratacion      | 2472   |       |        |
| NOTMX-CONT-Portabilidad      | 753    |       |        |
| NOTMX-SeguimientoInstalacion | 7765   |       |        |
| NoTMX_SinOp                  | 1016   |       |        |
| Numero Telmex                | 16909  |       |        |
| ... (más opciones)           |        |       |        |

Total filas: 26
Total general: 132,473 llamadas


HOJA 2: Nacional
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| cMenu                        | Numero | Total | 2567201 |
|------------------------------|--------|-------|---------|
| NULL                         | 238049 |       |         |
| Opción Invalida              | 77     |       |         |
| ANI                          | 2887   |       |         |
| cliente_colgo                | 444438 |       |         |
| ... (más opciones)           |        |       |         |

Total filas: 46
Total general: 2,567,201 llamadas
```

### 2.2 Insights del Reporte

```
DATOS AGREGADOS (NO DETALLE):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Cuenta de llamadas por opción de menú
✅ Agrupado por sucursal (Puebla, Nacional)
✅ Total general por sucursal
✅ Sin detalles individuales de llamadas

NO HAY:
❌ Registro individual de cada llamada
❌ Timestamp específico de cada evento
❌ Teléfono del cliente
❌ Duración de llamada

ESTO CONFIRMA:
✅ Reporte es AGREGADO (summary)
✅ ETL ya procesó y agrupó datos
✅ Django solo formatea para Excel
```

---

<a name="arquitectura"></a>
## 3. ARQUITECTURA DJANGO CORRECTA

### 3.1 Componentes del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│ 1. IVR_LEGACY (MariaDB) - Origen de datos                  │
│    call_logs table - Datos RAW de llamadas                 │
└────────────┬────────────────────────────────────────────────┘
             │
             │ ETL en MySQL (NO en Django)
             │ - Stored procedures
             │ - MySQL Events/Jobs
             │ - Triggers
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ANALYTICS DB (MySQL) - Datos procesados                 │
│    reporte_cmenu_agregado - Tablas agregadas               │
│    reporte_llamadas_diarias - Otras agregaciones           │
│    ... más tablas de reportes                               │
└────────────┬────────────────────────────────────────────────┘
             │
             │ Django query (READ-ONLY)
             │ - Unmanaged models
             │ - Raw SQL (opcional)
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. DJANGO APP - Solo consumo                               │
│    apps/reports/                                            │
│    ├─ models.py (unmanaged models)                         │
│    ├─ services.py (query logic)                            │
│    ├─ exporters.py (Excel/CSV generation)                  │
│    ├─ views.py (API endpoints)                             │
│    └─ permissions.py (RBAC)                                │
└────────────┬────────────────────────────────────────────────┘
             │
             │ API Response (Excel file)
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. FRONTEND - Usuario                                      │
│    Usuario Juan descarga Excel                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Responsabilidades Claras

```
ETL en MySQL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Extrae datos de IVR_LEGACY
✅ Transforma y limpia datos
✅ Agrega (SUM, COUNT, GROUP BY)
✅ Guarda en tablas de reportes
✅ Corre en schedule (cron, MySQL Event)

Herramientas:
- MySQL Stored Procedures
- MySQL Events (scheduler)
- SQL queries optimizadas


Django (apps/reports/):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Query tablas agregadas (READ-ONLY)
✅ Valida permisos (RBAC)
✅ Genera Excel/CSV
✅ API endpoints
✅ Tracking de solicitudes

NO hace:
❌ ETL (lo hace MySQL)
❌ Procesamiento de datos
❌ Agregaciones pesadas
❌ INSERT/UPDATE en analytics DB
```

---

<a name="modelos"></a>
## 4. MODELOS UNMANAGED VS SERIALIZERS

### 4.1 Opción A: Modelo Unmanaged (RECOMENDADO)

```python
# apps/reports/models.py

class CMenuAgregado(models.Model):
    """
    Modelo unmanaged para query tabla creada por ETL en MySQL.
    
    IMPORTANTE:
    - Django NO crea esta tabla (managed=False)
    - Django NO migra cambios
    - Django SOLO query (READ-ONLY)
    - Tabla es creada y mantenida por ETL en MySQL
    """
    
    id = models.BigAutoField(primary_key=True)
    fecha = models.DateField(db_index=True)
    sucursal = models.CharField(max_length=50, db_index=True)
    cmenu_opcion = models.CharField(max_length=100, null=True, blank=True)
    total_llamadas = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False  # ← CLAVE: Django NO gestiona tabla
        db_table = 'reporte_cmenu_agregado'  # ← Tabla en MySQL
        ordering = ['-fecha', 'cmenu_opcion']
        indexes = [
            models.Index(fields=['fecha', 'sucursal']),
            models.Index(fields=['cmenu_opcion']),
        ]
    
    def __str__(self):
        return f"{self.fecha} - {self.sucursal} - {self.cmenu_opcion}"


# CONFIGURACIÓN DE DATABASE

# settings.py

DATABASES = {
    'default': {
        # Django admin, users, sessions, etc
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'analytics_db': {
        # Tablas de reportes (creadas por ETL)
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'analytics',
        'USER': 'django_readonly',  # ← Usuario READ-ONLY
        'PASSWORD': 'password',
        'HOST': 'mysql-server',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# Database router
DATABASE_ROUTERS = ['apps.reports.routers.AnalyticsRouter']


# apps/reports/routers.py

class AnalyticsRouter:
    """
    Router para tablas de analytics (READ-ONLY).
    
    - Lectura: Permitida en analytics_db
    - Escritura: BLOQUEADA (retorna None)
    """
    
    analytics_models = {
        'CMenuAgregado',
        'LlamadasDiarias',
        # ... otros modelos de reportes
    }
    
    def db_for_read(self, model, **hints):
        """Redirige lectura a analytics_db."""
        if model.__name__ in self.analytics_models:
            return 'analytics_db'
        return None
    
    def db_for_write(self, model, **hints):
        """BLOQUEA escritura en analytics models."""
        if model.__name__ in self.analytics_models:
            return None  # ← Prohibe writes
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """NO permite migrations en analytics_db."""
        if db == 'analytics_db':
            return False  # ← NO migrations
        return None
```

**VENTAJAS:**

```
✅ ORM completo (filter, exclude, aggregate)
✅ QuerySet API (fácil de usar)
✅ Type hints y autocomplete
✅ Testing con fixtures
✅ Integración con Django admin (read-only)
✅ Relaciones con otros models (si existen)

EJEMPLO DE USO:

# Query simple
reportes = CMenuAgregado.objects.using('analytics_db').filter(
    fecha='2025-08-18',
    sucursal='puebla'
)

# Aggregation
total = CMenuAgregado.objects.using('analytics_db').filter(
    fecha='2025-08-18',
    sucursal='puebla'
).aggregate(
    total=Sum('total_llamadas')
)['total']

# Ordenar
reportes = reportes.order_by('-total_llamadas')[:10]  # Top 10
```

### 4.2 Opción B: Raw SQL (Alternativa)

```python
# apps/reports/services.py

class CMenuReportService:
    
    @staticmethod
    def get_cmenu_data(fecha_inicio, fecha_fin, sucursal):
        """Query con raw SQL."""
        
        from django.db import connections
        
        with connections['analytics_db'].cursor() as cursor:
            cursor.execute("""
                SELECT 
                    cmenu_opcion,
                    SUM(total_llamadas) as total,
                    fecha,
                    sucursal
                FROM reporte_cmenu_agregado
                WHERE fecha BETWEEN %s AND %s
                AND sucursal = %s
                GROUP BY cmenu_opcion, fecha, sucursal
                ORDER BY total DESC
            """, [fecha_inicio, fecha_fin, sucursal])
            
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
```

**VENTAJAS:**

```
✅ Control total sobre SQL
✅ Queries complejos optimizados
✅ No depende de ORM limitations
✅ Performance máximo

DESVENTAJAS:

❌ Sin type hints
❌ Sin QuerySet API
❌ Más código manual
❌ Testing más difícil
❌ SQL injection risk (si no se usa correctamente)
```

### 4.3 Opción C: Solo Serializer (NO RECOMENDADO)

```python
# apps/reports/serializers.py

class CMenuDataSerializer(serializers.Serializer):
    """Serializer sin modelo."""
    
    cmenu_opcion = serializers.CharField()
    total_llamadas = serializers.IntegerField()
    fecha = serializers.DateField()
    sucursal = serializers.CharField()

# Uso
data = CMenuReportService.get_cmenu_data_raw_sql(...)
serializer = CMenuDataSerializer(data=data, many=True)
serializer.is_valid()
return Response(serializer.data)
```

**DESVENTAJAS:**

```
❌ Sin ORM
❌ Queries manuales
❌ Sin validación de DB
❌ Más código boilerplate
❌ No recomendado para este caso
```

---

<a name="implementacion"></a>
## 5. EJEMPLO DE IMPLEMENTACIÓN

### 5.1 Código Completo

```python
# ════════════════════════════════════════════════════════════
# apps/reports/models.py
# ════════════════════════════════════════════════════════════

class CMenuAgregado(models.Model):
    """Reporte cMenu agregado (tabla creada por ETL)."""
    
    id = models.BigAutoField(primary_key=True)
    fecha = models.DateField(db_index=True)
    sucursal = models.CharField(max_length=50, db_index=True)
    cmenu_opcion = models.CharField(max_length=100, null=True)
    total_llamadas = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    
    class Meta:
        managed = False
        db_table = 'reporte_cmenu_agregado'
        ordering = ['-fecha', 'cmenu_opcion']


# ════════════════════════════════════════════════════════════
# apps/reports/services.py
# ════════════════════════════════════════════════════════════

class CMenuReportService:
    """Servicio para reportes cMenu."""
    
    @staticmethod
    def get_cmenu_data(fecha_inicio, fecha_fin, sucursal):
        """Query datos agregados de cMenu."""
        
        queryset = CMenuAgregado.objects.using('analytics_db').filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        )
        
        if sucursal != 'todas':
            queryset = queryset.filter(sucursal=sucursal)
        
        return list(queryset.values(
            'cmenu_opcion',
            'total_llamadas',
            'fecha',
            'sucursal'
        ))
    
    @staticmethod
    def get_total(fecha_inicio, fecha_fin, sucursal):
        """Calcular total general."""
        
        from django.db.models import Sum
        
        queryset = CMenuAgregado.objects.using('analytics_db').filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        )
        
        if sucursal != 'todas':
            queryset = queryset.filter(sucursal=sucursal)
        
        result = queryset.aggregate(total=Sum('total_llamadas'))
        return result['total'] or 0


# ════════════════════════════════════════════════════════════
# apps/reports/exporters.py
# ════════════════════════════════════════════════════════════

class ExcelExporter:
    """Generador de archivos Excel."""
    
    @staticmethod
    def generate_cmenu_excel(data, sucursal, total):
        """
        Generar Excel estilo Reporte_cMenu_180825.xlsx
        
        Args:
            data: List[Dict] con datos de cMenu
            sucursal: str nombre de sucursal
            total: int total general
        
        Returns:
            str filepath del Excel generado
        """
        import openpyxl
        from openpyxl.styles import Font
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = sucursal.capitalize()
        
        # Headers
        ws['A1'] = 'cMenu'
        ws['B1'] = 'Numero'
        ws['D1'] = 'Total'
        ws['E1'] = total
        
        # Styling headers
        for cell in ['A1', 'B1', 'D1', 'E1']:
            ws[cell].font = Font(bold=True)
        
        # Datos
        row_num = 2
        for item in data:
            ws[f'A{row_num}'] = item['cmenu_opcion']
            ws[f'B{row_num}'] = item['total_llamadas']
            row_num += 1
        
        # Save
        from django.conf import settings
        import os
        from datetime import datetime
        
        filename = f"cmenu_{sucursal}_{datetime.now().strftime('%y%m%d')}.xlsx"
        filepath = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        wb.save(filepath)
        
        return filepath


# ════════════════════════════════════════════════════════════
# apps/reports/views.py
# ════════════════════════════════════════════════════════════

class CMenuReportViewSet(viewsets.ViewSet):
    """ViewSet para reportes cMenu."""
    
    permission_classes = [IsAuthenticated, CanViewCMenuReport]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generar reporte cMenu.
        
        POST /api/v1/reports/cmenu/generate/
        
        Body:
        {
            "fecha_inicio": "2025-08-18",
            "fecha_fin": "2025-08-18",
            "sucursal": "puebla",
            "formato": "excel"
        }
        """
        # 1. Validar
        serializer = CMenuReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated = serializer.validated_data
        
        # 2. Query datos
        data = CMenuReportService.get_cmenu_data(
            fecha_inicio=validated['fecha_inicio'],
            fecha_fin=validated['fecha_fin'],
            sucursal=validated['sucursal']
        )
        
        total = CMenuReportService.get_total(
            fecha_inicio=validated['fecha_inicio'],
            fecha_fin=validated['fecha_fin'],
            sucursal=validated['sucursal']
        )
        
        # 3. Generar Excel
        if validated['formato'] == 'excel':
            filepath = ExcelExporter.generate_cmenu_excel(
                data=data,
                sucursal=validated['sucursal'],
                total=total
            )
            
            file_url = filepath.replace(settings.MEDIA_ROOT, '/media')
            
            return Response({
                "status": "completed",
                "file_url": file_url,
                "total_records": len(data),
                "total_llamadas": total
            })
        
        # 4. Formato CSV (opcional)
        elif validated['formato'] == 'csv':
            # ... implementar CSV
            pass


# ════════════════════════════════════════════════════════════
# apps/reports/serializers.py
# ════════════════════════════════════════════════════════════

class CMenuReportRequestSerializer(serializers.Serializer):
    """Validación de request para reporte cMenu."""
    
    fecha_inicio = serializers.DateField(required=True)
    fecha_fin = serializers.DateField(required=True)
    sucursal = serializers.ChoiceField(
        choices=['puebla', 'nacional', 'todas'],
        required=True
    )
    formato = serializers.ChoiceField(
        choices=['excel', 'csv', 'pdf'],
        default='excel'
    )
    
    def validate(self, data):
        """Validar rango de fechas."""
        if data['fecha_fin'] < data['fecha_inicio']:
            raise serializers.ValidationError(
                "fecha_fin debe ser >= fecha_inicio"
            )
        return data
```

---

## RESUMEN Y CONCLUSIONES

```
FLUJO REAL CONFIRMADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. IVR_LEGACY (MariaDB) - Datos RAW
   └─ call_logs table

2. ETL en MySQL - Procesamiento
   └─ Stored procedures / MySQL Events
   └─ Agrega y limpia datos

3. ANALYTICS DB (MySQL) - Datos procesados
   └─ reporte_cmenu_agregado table

4. Django - Solo consume (READ-ONLY)
   └─ Query con modelo unmanaged
   └─ Genera Excel
   └─ API endpoint

5. Usuario - Descarga Excel
   └─ Reporte_cMenu_180825.xlsx


ARQUITECTURA DJANGO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

apps/reports/
├─ models.py (unmanaged models, managed=False)
├─ services.py (query logic)
├─ exporters.py (Excel/CSV generation)
├─ views.py (API endpoints)
├─ routers.py (analytics DB router)
└─ permissions.py (RBAC)

NO HAY:
❌ ETLService en Python
❌ CallRecord.objects.create()
❌ Guardado en SQLite/Postgres Django
❌ Procesamiento de datos en Django

SÍ HAY:
✅ Query READ-ONLY a MySQL
✅ Modelo unmanaged (managed=False)
✅ Router que bloquea writes
✅ Excel generation
✅ RBAC permissions


DECISIONES CLAVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Usar modelo unmanaged (managed=False)
2. ✅ Database router que bloquea writes
3. ✅ Usuario MySQL READ-ONLY
4. ✅ ORM para queries (no raw SQL)
5. ✅ ExcelExporter para generar archivos

Django es CONSUMIDOR, no PROCESADOR ✅
```

---

**FIN DEL ANÁLISIS - FLUJO REAL v2.0.0**

Documento creado: 2026-01-17  
Supuesto anterior: INCORRECTO (Django hace ETL)  
Flujo real: CORRECTO (Django solo consume)  
Arquitectura: Modelo unmanaged + Router READ-ONLY  
Ejemplo: Reporte_cMenu_180825.xlsx
