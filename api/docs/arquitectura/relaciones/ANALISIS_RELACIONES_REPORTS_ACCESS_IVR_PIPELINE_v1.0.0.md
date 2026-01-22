---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis de Arquitectura - Relaciones entre Apps
categoria: arquitectura/analisis-relaciones
tema: Relaciones y flujos de datos entre REPORTS, ACCESS, IVR_LEGACY y PIPELINE
autor: Claude Technical Analysis
tags: [arquitectura, relaciones, flujo-datos, etl, rbac, reports]
relacionado:
  - ANALISIS_APP_REPORTS_REFACTORING_v1.0.0.md
  - ANALISIS_APP_ACCESS_REFACTORING_v1.0.0.md
  - ANALISIS_APP_IVR_LEGACY_REFACTORING_v1.0.0.md
  - ANALISIS_APP_PIPELINE_REFACTORING_v1.0.0.md
estado: completado
---

# ANÁLISIS DE RELACIONES: REPORTS ↔ ACCESS ↔ IVR_LEGACY ↔ PIPELINE

**Flujos de Datos, Dependencias y Integraciones - Basado en Código REAL**

---

## RESUMEN EJECUTIVO

Este documento analiza las **relaciones críticas** entre 4 apps del sistema:

1. **IVR_LEGACY** - Origen de datos (MariaDB READ-ONLY)
2. **PIPELINE** - ETL que procesa datos
3. **CORE** - Almacenamiento analytics (CallRecord)
4. **REPORTS** - Generación de reportes
5. **ACCESS** - RBAC para permisos

### Flujo Principal de Datos

```
┌──────────────┐    ETL      ┌──────────┐    Save     ┌──────────┐
│  IVR_LEGACY  │ ────────→   │ PIPELINE │ ─────────→  │   CORE   │
│   MariaDB    │  READ-ONLY  │   ETL    │  CallRecord │Analytics │
│  call_logs   │             │          │             │  SQLite  │
└──────────────┘             └──────────┘             └─────┬────┘
                                                             │
                                                             │ Query
                                                             ▼
                                                      ┌──────────┐
                                                      │ REPORTS  │
                                                      │ Export   │
                                                      └──────────┘
                                                             ▲
                                                             │
                                                        Permissions
                                                             │
                                                      ┌──────────┐
                                                      │  ACCESS  │
                                                      │   RBAC   │
                                                      └──────────┘
```

---

## TABLA DE CONTENIDOS

1. [Relación 1: IVR_LEGACY → PIPELINE](#relacion-1)
2. [Relación 2: PIPELINE → CORE (CallRecord)](#relacion-2)
3. [Relación 3: CORE → REPORTS](#relacion-3)
4. [Relación 4: ACCESS → REPORTS](#relacion-4)
5. [Flujo Completo End-to-End](#flujo-completo)
6. [Dependencias y Acoplamientos](#dependencias)
7. [Compliance Standards (CNST)](#compliance)
8. [Diagrama de Arquitectura General](#diagrama)

---

<a name="relacion-1"></a>
## 1. RELACIÓN 1: IVR_LEGACY → PIPELINE

### 1.1 Conexión: IVRAdapter

```python
# ════════════════════════════════════════════════════════════
# apps/ivr_legacy/adapters.py
# ════════════════════════════════════════════════════════════

class IVRAdapter:
    """
    Adapter para acceso READ-ONLY a IVR legacy.
    
    CNST-003: Solo SELECT, NO INSERT/UPDATE/DELETE.
    """
    
    def get_calls(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> List[Dict]:
        """
        Extraer llamadas de IVR legacy.
        
        Args:
            fecha_inicio: Fecha inicio
            fecha_fin: Fecha fin
            
        Returns:
            List[Dict]: Datos de llamadas
        """
        from apps.ivr_legacy.models import CallLog
        
        try:
            # Query a MariaDB (READ-ONLY)
            queryset = CallLog.objects.using('ivr_legacy').filter(
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin
            )
            
            # Convertir a List[Dict] para desacoplar de ORM
            return list(queryset.values(
                'fecha',
                'telefono',
                'servicio_800',
                'total_llamadas',
                'llamadas_contestadas',
                'llamadas_abandonadas',
                'created_at'
            ))
            
        except Exception as e:
            logger.error(f"IVRAdapter error: {e}")
            return []  # Resiliente: devuelve [] en testing
```

### 1.2 Consumidor: ETLService (PIPELINE)

```python
# ════════════════════════════════════════════════════════════
# apps/core/services/etl_service.py (usado por PIPELINE)
# ════════════════════════════════════════════════════════════

class ETLService:
    """
    Servicio ETL para procesar datos IVR legacy.
    
    CNST-003: Acceso READ-ONLY a ivr_legacy.
    CNST-004: Ejecutar con APScheduler (NO Celery).
    """
    
    def __init__(self):
        # Inyección de dependencia: usa IVRAdapter
        self.adapter = IVRAdapter()
    
    def extract(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> List[Dict]:
        """
        STEP 1: Extract - Extraer datos de IVR legacy.
        
        Returns:
            List[Dict]: Datos raw de IVR legacy
        """
        logger.info(f"ETL Extract: {fecha_inicio} a {fecha_fin}")
        
        # Delegar a IVRAdapter (READ-ONLY)
        data = self.adapter.get_calls(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        logger.info(f"ETL Extract: {len(data)} registros extraídos")
        return data
```

### 1.3 Características de la Relación

```
TIPO DE RELACIÓN: Adapter Pattern
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIRECCIÓN: IVR_LEGACY → PIPELINE (unidireccional)

COUPLING: Bajo (via IVRAdapter interface)
- PIPELINE no conoce detalles de MariaDB
- PIPELINE no conoce detalles de CallLog model
- Solo conoce IVRAdapter.get_calls() → List[Dict]

BENEFICIOS:
✅ Abstracción de database legacy
✅ Fácil de mockear en tests
✅ Resiliente (returns [] on error)
✅ Type hints claros
✅ CNST-003 enforced (READ-ONLY)

CNST-003 COMPLIANCE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ CallLog.Meta.managed = False (NO migrations)
✅ IVRRouter.db_for_write() → None (NO writes)
✅ Database user: ivr_readonly (GRANT SELECT ONLY)
✅ IVRAdapter solo usa .filter() y .values() (READ operations)

FLUJO DE DATOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MariaDB (ivr_production)
  ├─ table: call_logs
  └─ fields: fecha, telefono, servicio_800, total_llamadas, ...
      │
      ▼ IVRRouter routes to 'ivr_legacy'
      │
  CallLog.objects.using('ivr_legacy').filter(...)
      │
      ▼ IVRAdapter.get_calls()
      │
  List[Dict] con datos raw
      │
      ▼ ETLService.extract()
      │
  Datos listos para Transform
```

---

<a name="relacion-2"></a>
## 2. RELACIÓN 2: PIPELINE → CORE (CallRecord)

### 2.1 Transform: Procesamiento de Datos

```python
# ════════════════════════════════════════════════════════════
# apps/core/services/etl_service.py
# ════════════════════════════════════════════════════════════

def transform(self, raw_data: List[Dict]) -> List[Dict]:
    """
    STEP 2: Transform - Transformar y limpiar datos raw.
    
    Args:
        raw_data: Datos raw de extract()
        
    Returns:
        List[Dict]: Datos transformados y validados
    """
    logger.info(f"ETL Transform: {len(raw_data)} registros")
    
    if not raw_data:
        return []
    
    transformed = []
    
    for record in raw_data:
        try:
            # Validar campos requeridos
            if not all(k in record for k in [
                'fecha', 'telefono', 'servicio_800'
            ]):
                logger.warning(f"Registro incompleto: {record}")
                continue
            
            # Limpiar y normalizar
            cleaned = {
                'fecha': record['fecha'],
                'telefono': str(record['telefono']).strip(),
                'servicio_800': str(record['servicio_800']).strip(),
                'total_llamadas': int(record.get('total_llamadas', 0)),
                'llamadas_contestadas': int(record.get('llamadas_contestadas', 0)),
                'llamadas_abandonadas': int(record.get('llamadas_abandonadas', 0)),
            }
            
            # Validar lógica de negocio
            if cleaned['total_llamadas'] < 0:
                logger.warning(f"Total llamadas negativo: {cleaned}")
                continue
            
            transformed.append(cleaned)
            
        except Exception as e:
            logger.error(f"Transform error en registro {record}: {e}")
            continue
    
    logger.info(f"ETL Transform: {len(transformed)} registros válidos")
    return transformed
```

### 2.2 Load: Persistencia en Analytics DB

```python
# ════════════════════════════════════════════════════════════
# apps/core/services/etl_service.py
# ════════════════════════════════════════════════════════════

def load(self, transformed_data: List[Dict]) -> int:
    """
    STEP 3: Load - Cargar datos en analytics DB.
    
    Args:
        transformed_data: Datos transformados
        
    Returns:
        int: Cantidad de registros cargados
    """
    from apps.core.models import CallRecord
    
    logger.info(f"ETL Load: {len(transformed_data)} registros a cargar")
    
    if not transformed_data:
        return 0
    
    loaded_count = 0
    
    for record in transformed_data:
        try:
            # update_or_create: actualiza si existe, crea si no
            obj, created = CallRecord.objects.update_or_create(
                # Unique together constraint
                fecha=record['fecha'],
                telefono=record['telefono'],
                servicio_800=record['servicio_800'],
                # Campos a actualizar
                defaults={
                    'total_llamadas': record['total_llamadas'],
                    'llamadas_contestadas': record['llamadas_contestadas'],
                    'llamadas_abandonadas': record['llamadas_abandonadas'],
                }
            )
            
            loaded_count += 1
            
            if created:
                logger.debug(f"CallRecord creado: {obj}")
            else:
                logger.debug(f"CallRecord actualizado: {obj}")
        
        except Exception as e:
            logger.error(f"Load error en registro {record}: {e}")
            continue
    
    logger.info(f"ETL Load: {loaded_count} registros cargados/actualizados")
    return loaded_count
```

### 2.3 Modelo de Destino: CallRecord

```python
# ════════════════════════════════════════════════════════════
# apps/core/models.py
# ════════════════════════════════════════════════════════════

class CallRecord(models.Model):
    """
    Registro de llamada en analytics DB.
    
    Cargado por ETLService desde IVR legacy.
    Usado por REPORTS para generar reportes.
    """
    
    # Campos de identificación (unique together)
    fecha = models.DateField(db_index=True)
    telefono = models.CharField(max_length=20)
    servicio_800 = models.CharField(max_length=20, db_index=True)
    
    # Métricas de llamadas
    total_llamadas = models.IntegerField(default=0)
    llamadas_contestadas = models.IntegerField(default=0)
    llamadas_abandonadas = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'call_records'
        ordering = ['-fecha']
        unique_together = [
            ('fecha', 'telefono', 'servicio_800')
        ]
        indexes = [
            models.Index(fields=['-fecha']),
            models.Index(fields=['servicio_800', '-fecha']),
        ]
    
    def __str__(self):
        return f"CallRecord {self.fecha} - {self.telefono}"
```

### 2.4 Características de la Relación

```
TIPO DE RELACIÓN: ETL Pipeline (Extract → Transform → Load)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIRECCIÓN: PIPELINE → CORE.CallRecord (unidireccional)

COUPLING: Medio (depende de CallRecord model)
- ETLService importa CallRecord
- update_or_create() usa campos específicos
- Pero: tipo de datos encapsulado en List[Dict]

SCHEDULING: APScheduler (CNST-004)
- Intervalo: 12 horas
- Automático via ETLScheduler
- NO real-time

IDEMPOTENCIA:
✅ update_or_create() permite re-ejecutar sin duplicados
✅ unique_together evita duplicados
✅ Safe para re-procesamiento

ERROR HANDLING:
✅ Try/except en cada paso (extract, transform, load)
✅ Logging detallado
✅ Continue en errores individuales
✅ Status tracking en ETLExecution

FLUJO DE DATOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVRAdapter.get_calls()
  │
  ▼ List[Dict] raw data
  │
ETLService.extract()
  │
  ▼ Raw data
  │
ETLService.transform()
  │
  ├─ Validar campos requeridos
  ├─ Limpiar y normalizar
  ├─ Validar lógica negocio
  └─ Filter out invalids
  │
  ▼ List[Dict] cleaned data
  │
ETLService.load()
  │
  ├─ CallRecord.objects.update_or_create()
  ├─ Unique together: (fecha, telefono, servicio_800)
  └─ Update metrics if exists
  │
  ▼ Saved to SQLite/Postgres
  │
CallRecord in analytics DB
```

---

<a name="relacion-3"></a>
## 3. RELACIÓN 3: CORE (CallRecord) → REPORTS

### 3.1 Query desde REPORTS

```python
# ════════════════════════════════════════════════════════════
# apps/reports/services.py - ExportService
# ════════════════════════════════════════════════════════════

class ExportService:
    """
    Servicio para exportación de reportes.
    
    CNST-007: Valida límite de 100K registros.
    """
    
    MAX_EXPORT_SIZE = 100000
    
    def _get_calls_data(self, filters: Dict) -> List[Dict]:
        """
        Obtener datos de llamadas desde CallRecord.
        
        NO accede directamente a IVR_LEGACY.
        Usa datos ya procesados por ETL.
        
        Args:
            filters: Filtros aplicados (fecha_desde, fecha_hasta, servicio_800)
            
        Returns:
            List[Dict]: Datos de llamadas para exportar
        """
        # Import desde CORE (no desde IVR_LEGACY)
        from apps.core.models import CallRecord
        
        # Query a analytics DB (no a MariaDB legacy)
        queryset = CallRecord.objects.all()
        
        # Aplicar filtros del usuario
        if 'fecha_desde' in filters:
            queryset = queryset.filter(fecha__gte=filters['fecha_desde'])
        if 'fecha_hasta' in filters:
            queryset = queryset.filter(fecha__lte=filters['fecha_hasta'])
        if 'servicio_800' in filters:
            queryset = queryset.filter(servicio_800=filters['servicio_800'])
        
        # CNST-007: Hard limit
        queryset = queryset[:self.MAX_EXPORT_SIZE]
        
        # Convertir a dict para export
        return list(queryset.values(
            'fecha',
            'telefono',
            'servicio_800',
            'total_llamadas',
            'llamadas_contestadas',
            'llamadas_abandonadas',
        ))
```

### 3.2 Count desde ReportService

```python
# ════════════════════════════════════════════════════════════
# apps/reports/services.py - ReportService
# ════════════════════════════════════════════════════════════

class ReportService:
    """
    Servicio para generación de reportes.
    
    Calcula total_records antes de exportar.
    """
    
    @staticmethod
    def _count_calls(filters: Dict) -> int:
        """
        Contar llamadas según filtros.
        
        Usa CallRecord (analytics DB), no IVR_LEGACY.
        
        Args:
            filters: Filtros aplicados
            
        Returns:
            int: Total de registros que coinciden
        """
        from apps.core.models import CallRecord
        
        queryset = CallRecord.objects.all()
        
        # Aplicar mismos filtros que en export
        if 'fecha_desde' in filters:
            queryset = queryset.filter(fecha__gte=filters['fecha_desde'])
        if 'fecha_hasta' in filters:
            queryset = queryset.filter(fecha__lte=filters['fecha_hasta'])
        if 'servicio_800' in filters:
            queryset = queryset.filter(servicio_800=filters['servicio_800'])
        
        # Count para Report.total_records
        return queryset.count()
    
    @staticmethod
    def generate_report(report: Report) -> None:
        """
        Generar reporte procesando datos.
        
        Actualiza report.total_records con count.
        """
        report.status = 'processing'
        report.save()
        
        try:
            # Obtener count según tipo de reporte
            if report.report_type == 'calls':
                count = ReportService._count_calls(report.filters)
            elif report.report_type == 'users':
                count = ReportService._count_users(report.filters)
            elif report.report_type == 'audit':
                count = ReportService._count_audit(report.filters)
            else:
                count = 0
            
            # Actualizar total_records
            report.total_records = count
            report.status = 'completed'
            report.save()
            
        except Exception as e:
            report.status = 'failed'
            report.save()
            raise
```

### 3.3 Características de la Relación

```
TIPO DE RELACIÓN: Query/Read Pattern
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIRECCIÓN: REPORTS → CORE.CallRecord (unidireccional)

COUPLING: Medio (depende de CallRecord model)
- REPORTS importa CallRecord
- Depende de campos específicos
- Depende de estructura de datos

DATA FLOW:
┌──────────┐      Query      ┌──────────┐
│ REPORTS  │ ──────────────→ │   CORE   │
│          │  .filter()      │CallRecord│
│          │  .count()       │          │
│          │  .values()      │          │
└──────────┘                 └──────────┘

IMPORTANTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ REPORTS NO accede directamente a IVR_LEGACY
⚠️ REPORTS NO usa IVRAdapter
⚠️ REPORTS solo query CallRecord (analytics DB)

RAZÓN:
✅ Separation of concerns
✅ ETL ya procesó y limpió datos
✅ Analytics DB optimizada para queries
✅ No depende de MariaDB legacy availability
✅ Datos pueden estar más frescos (ETL cada 12h)

CNST-007 ENFORCEMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CAPA 1: Serializer
- ExportJobSerializer.validate_total_records()
- Rechaza > 100,000

CAPA 2: Service
- ExportService.export() validation
- RuntimeError si excede

CAPA 3: View
- ReportViewSet.export() validation
- HTTP 400 si excede

HARD LIMIT:
- queryset[:self.MAX_EXPORT_SIZE]
- Nunca retorna más de 100K registros

BENEFICIOS:
✅ Performance: queries optimizadas en analytics DB
✅ Availability: no depende de MariaDB legacy
✅ Data quality: datos ya validados por ETL
✅ CNST-007: límite enforced en queries
```

---

<a name="relacion-4"></a>
## 4. RELACIÓN 4: ACCESS (RBAC) → REPORTS

### 4.1 Permissions Custom de REPORTS

```python
# ════════════════════════════════════════════════════════════
# apps/reports/permissions.py
# ════════════════════════════════════════════════════════════

class CanViewReports(BasePermission):
    """
    Permiso para ver reportes.
    
    Integra con sistema RBAC de ACCESS.
    Requiere función 'reports.view_report'.
    """
    
    def has_permission(self, request, view):
        """Verificar si usuario puede ver reportes."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser siempre puede
        if request.user.is_superuser:
            return True
        
        # INTEGRACIÓN CON ACCESS:
        # user.has_function() verifica permisos RBAC
        return request.user.has_function('reports.view_report')


class CanCreateReports(BasePermission):
    """Permiso para crear reportes."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # INTEGRACIÓN CON ACCESS
        return request.user.has_function('reports.create_report')


class CanExportReports(BasePermission):
    """
    Permiso para exportar reportes.
    
    CNST-007: Valida límite de exportación.
    Requiere permiso RBAC adicional.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # INTEGRACIÓN CON ACCESS
        return request.user.has_function('reports.export_report')


class IsReportOwner(BasePermission):
    """
    Permiso para acceder solo a reportes propios.
    
    Object-level permission.
    """
    
    def has_object_permission(self, request, view, obj):
        """Verificar si usuario es dueño del reporte."""
        if request.user.is_superuser:
            return True
        
        # Verificar ownership
        return obj.created_by == request.user
```

### 4.2 User.has_function() - Integración con ACCESS

```python
# ════════════════════════════════════════════════════════════
# apps/users/models.py (método en User model)
# ════════════════════════════════════════════════════════════

class User(AbstractUser, SoftDeleteMixin):
    """
    Usuario del sistema.
    
    Integra con ACCESS para RBAC.
    """
    
    # ... campos ...
    
    def has_function(self, function_code: str) -> bool:
        """
        Verificar si usuario tiene función RBAC.
        
        Integración con ACCESS app.
        
        Args:
            function_code: Código de función (ej: 'reports.view_report')
            
        Returns:
            bool: True si tiene permiso
            
        Examples:
            >>> user.has_function('reports.view_report')
            True
            >>> user.has_function('reports.export_report')
            False
        """
        # Import desde ACCESS
        from apps.access.services import ModuleAccessService
        
        # Delegar a ModuleAccessService
        return ModuleAccessService.user_has_function(
            user=self,
            function_code=function_code
        )
```

### 4.3 ModuleAccessService - Lógica RBAC

```python
# ════════════════════════════════════════════════════════════
# apps/access/services.py
# ════════════════════════════════════════════════════════════

class ModuleAccessService:
    """
    Servicio para gestión de acceso a módulos (RBAC).
    
    Centraliza lógica de permisos.
    Usado por todas las apps via user.has_function().
    """
    
    @staticmethod
    def user_has_function(user, function_code: str) -> bool:
        """
        Verificar si usuario tiene función.
        
        Lógica RBAC completa:
        1. Superuser → siempre True
        2. Usuario inactivo → False
        3. Verificar ProfileFunction assignment
        
        Args:
            user: User instance
            function_code: Código de función
            
        Returns:
            bool: True si tiene permiso
        """
        from apps.access.models import ProfileFunction, Function
        
        # Superuser siempre tiene acceso
        if user.is_superuser:
            return True
        
        # Usuario inactivo no tiene acceso
        if not user.is_active:
            return False
        
        # Usuario sin profile no tiene acceso
        if not hasattr(user, 'profile') or not user.profile:
            return False
        
        # Buscar función
        try:
            function = Function.objects.get(code=function_code)
        except Function.DoesNotExist:
            return False
        
        # Verificar ProfileFunction
        has_permission = ProfileFunction.objects.filter(
            profile=user.profile,
            function=function
        ).exists()
        
        return has_permission
```

### 4.4 Uso en ReportViewSet

```python
# ════════════════════════════════════════════════════════════
# apps/reports/views.py
# ════════════════════════════════════════════════════════════

class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de reportes.
    
    Usa permissions custom con integración RBAC.
    """
    
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    
    # Default permissions para list/retrieve
    permission_classes = [IsAuthenticated, CanViewReports]
    
    def get_permissions(self):
        """
        Permisos dinámicos según acción.
        
        Integra con ACCESS via custom permissions.
        """
        if self.action == 'create':
            # Requiere 'reports.create_report'
            return [IsAuthenticated(), CanCreateReports()]
        
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Requiere ownership
            return [IsAuthenticated(), IsReportOwner()]
        
        elif self.action == 'export':
            # Requiere 'reports.export_report' + CNST-007
            return [IsAuthenticated(), CanExportReports()]
        
        # Default: view permission
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """
        Exportar reporte.
        
        Permissions verificadas:
        1. IsAuthenticated (DRF built-in)
        2. CanExportReports (custom, integra con ACCESS)
        3. CNST-007 validation (business rule)
        """
        report = self.get_object()
        
        # Permission ya verificada por get_permissions()
        # user.has_function('reports.export_report') = True
        
        # CNST-007 validation
        if report.total_records > ExportService.MAX_EXPORT_SIZE:
            return Response({
                'detail': f'CNST-007 violation: ...'
            }, status=400)
        
        # Export...
```

### 4.5 Características de la Relación

```
TIPO DE RELACIÓN: RBAC Integration (Permissions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIRECCIÓN: REPORTS → ACCESS (via User model)

COUPLING: Bajo (via interface user.has_function())
- REPORTS define permissions custom
- Permissions llaman user.has_function()
- User delega a ModuleAccessService
- Desacoplado via método abstracto

FUNCIONES RBAC REQUERIDAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. reports.view_report
   - Usado en: CanViewReports
   - Permite: list, retrieve reportes

2. reports.create_report
   - Usado en: CanCreateReports
   - Permite: create reportes

3. reports.export_report
   - Usado en: CanExportReports
   - Permite: exportar a CSV/Excel
   - IMPORTANTE: Incluye CNST-007 compliance

FLUJO DE VERIFICACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Request: POST /api/v1/reports/{id}/export/
  │
  ▼
DRF ViewSet: ReportViewSet.export()
  │
  ▼ get_permissions()
  │
  ├─ IsAuthenticated() → OK
  │
  └─ CanExportReports().has_permission()
      │
      ▼ request.user.has_function('reports.export_report')
      │
      ▼ User.has_function() (USERS app)
      │
      ▼ ModuleAccessService.user_has_function() (ACCESS app)
      │
      ├─ if superuser → return True
      ├─ if not active → return False
      ├─ if no profile → return False
      │
      └─ Query ProfileFunction.objects.filter(
            profile=user.profile,
            function=Function(code='reports.export_report')
         ).exists()
      │
      ▼
  True/False
      │
      ▼
If True: continuar con export
If False: HTTP 403 Forbidden

BENEFICIOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Granular permissions (view, create, export)
✅ Centralizado en ACCESS app
✅ Reutilizable (todas las apps usan mismo pattern)
✅ Fácil de testear (mock user.has_function())
✅ Dynamic per-action permissions
✅ Object-level permissions (IsReportOwner)

DATA ISOLATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ReportViewSet.get_queryset():
    if user.is_superuser:
        return Report.objects.all()
    else:
        return Report.objects.filter(created_by=user)

✅ Users solo ven sus propios reportes
✅ Superuser ve todos
✅ No leak de datos entre usuarios
```

---

<a name="flujo-completo"></a>
## 5. FLUJO COMPLETO END-TO-END

### 5.1 Diagrama de Flujo Completo

```
FLUJO COMPLETO DE DATOS: IVR_LEGACY → PIPELINE → CORE → REPORTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────┐
│ ORIGEN: IVR_LEGACY (MariaDB)                                    │
│                                                                  │
│ Database: ivr_production (MariaDB)                              │
│ Table: call_logs                                                │
│ Access: READ-ONLY (CNST-003)                                    │
│   ├─ User: ivr_readonly (GRANT SELECT ONLY)                    │
│   ├─ Router: IVRRouter.db_for_write() → None                   │
│   └─ Model: CallLog.Meta.managed = False                       │
│                                                                  │
│ Model: CallLog                                                  │
│   ├─ fecha, telefono, servicio_800                             │
│   ├─ total_llamadas, llamadas_contestadas, llamadas_abandonadas│
│   └─ created_at                                                │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ IVRAdapter.get_calls(fecha_inicio, fecha_fin)
             │ Returns: List[Dict]
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ PROCESAMIENTO: PIPELINE (ETL)                                   │
│                                                                  │
│ Scheduler: APScheduler (CNST-004)                              │
│   ├─ Interval: 12 horas                                        │
│   ├─ Job: 'etl_job'                                            │
│   └─ Trigger: IntervalTrigger(hours=12)                        │
│                                                                  │
│ ETLService (CORE app):                                         │
│                                                                  │
│ 1. EXTRACT (via IVRAdapter)                                    │
│    ├─ IVRAdapter.get_calls()                                   │
│    ├─ Query a MariaDB (READ-ONLY)                              │
│    └─ Return: List[Dict] raw data                              │
│                                                                  │
│ 2. TRANSFORM                                                    │
│    ├─ Validar campos requeridos                                │
│    ├─ Limpiar y normalizar strings                             │
│    ├─ Validar lógica negocio (total >= 0)                      │
│    ├─ Filter out invalids                                      │
│    └─ Return: List[Dict] cleaned data                          │
│                                                                  │
│ 3. LOAD                                                         │
│    ├─ CallRecord.objects.update_or_create()                    │
│    ├─ Unique together: (fecha, telefono, servicio_800)        │
│    ├─ Update metrics if exists                                 │
│    └─ Save to analytics DB                                     │
│                                                                  │
│ Tracking: ETLExecution                                         │
│   ├─ status: PENDING → RUNNING → SUCCESS/FAILED                │
│   ├─ records_extracted, records_loaded                         │
│   ├─ started_at, completed_at                                  │
│   └─ error_message (if failed)                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ CallRecord.objects.update_or_create()
             │ Saves to: analytics DB (SQLite/Postgres)
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ ALMACENAMIENTO: CORE (Analytics DB)                             │
│                                                                  │
│ Database: default (SQLite in dev, Postgres in prod)            │
│ Table: call_records                                            │
│ Access: READ/WRITE                                             │
│                                                                  │
│ Model: CallRecord                                              │
│   ├─ fecha, telefono, servicio_800 (unique together)          │
│   ├─ total_llamadas, llamadas_contestadas, llamadas_abandonadas│
│   ├─ created_at, updated_at                                    │
│   └─ Indexes: fecha, servicio_800                              │
│                                                                  │
│ Características:                                                │
│   ✅ Optimizado para queries (indexes)                         │
│   ✅ Datos limpios (validados por ETL)                         │
│   ✅ Actualización incremental (update_or_create)              │
│   ✅ Idempotente (safe para re-procesamiento)                  │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ QuerySet API
             │ .filter(), .count(), .values()
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ CONSUMO: REPORTS                                                │
│                                                                  │
│ ReportService:                                                  │
│   ├─ _count_calls(filters) → int                              │
│   ├─ Query CallRecord.objects.filter()                         │
│   ├─ Apply user filters (fecha, servicio_800)                  │
│   └─ Return count → Report.total_records                       │
│                                                                  │
│ ExportService:                                                  │
│   ├─ _get_calls_data(filters) → List[Dict]                    │
│   ├─ Query CallRecord.objects.filter()                         │
│   ├─ Apply user filters                                        │
│   ├─ CNST-007: queryset[:100000] (hard limit)                  │
│   └─ Return data for export (CSV/Excel)                        │
│                                                                  │
│ Permissions (via ACCESS):                                       │
│   ├─ CanViewReports → user.has_function('reports.view_report')│
│   ├─ CanCreateReports → 'reports.create_report'                │
│   └─ CanExportReports → 'reports.export_report'                │
│                                                                  │
│ CNST-007 Validation (3 capas):                                 │
│   ├─ CAPA 1: ExportJobSerializer.validate_total_records()     │
│   ├─ CAPA 2: ExportService.export() → RuntimeError            │
│   └─ CAPA 3: ReportViewSet.export() → HTTP 400                │
│                                                                  │
│ Export Formats:                                                 │
│   ├─ CSV: DictWriter, UTF-8                                    │
│   └─ Excel: openpyxl, styling, headers                         │
└─────────────────────────────────────────────────────────────────┘
             │
             │ HTTP Response
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ USUARIO FINAL                                                   │
│                                                                  │
│ Request: POST /api/v1/reports/{id}/export/                     │
│ Body: {"format": "csv"}                                         │
│                                                                  │
│ Permissions checked:                                            │
│   ✅ IsAuthenticated                                            │
│   ✅ CanExportReports (via RBAC)                                │
│   ✅ CNST-007 (< 100K records)                                  │
│                                                                  │
│ Response:                                                       │
│   {                                                             │
│     "export_job_id": 123,                                      │
│     "file_path": "exports/report_45_20260117.csv",             │
│     "status": "completed"                                       │
│   }                                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Timeline de Ejecución

```
TIMELINE: Desde dato IVR hasta reporte exportado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

T+0h: Llamada ocurre
  │
  ├─ CallCenter recibe llamada
  ├─ Sistema IVR procesa
  └─ Guarda en MariaDB (call_logs)
  
T+12h: ETL Programado (APScheduler)
  │
  ├─ ETLScheduler.run_etl() ejecuta
  │
  ├─ EXTRACT: IVRAdapter.get_calls()
  │   └─ Query a MariaDB (últimas 24 horas)
  │
  ├─ TRANSFORM: Validar y limpiar
  │   └─ ~2-5 segundos para 10K registros
  │
  └─ LOAD: CallRecord.objects.update_or_create()
      └─ Guarda en analytics DB
      
T+12h+5s: Datos disponibles en analytics
  │
  └─ CallRecord en SQLite/Postgres
  
T+12h+1min: Usuario crea reporte
  │
  ├─ POST /api/v1/reports/
  ├─ ReportService.generate_report()
  ├─ Count: CallRecord.objects.filter(...).count()
  └─ Report.total_records = 5,234
  
T+12h+2min: Usuario exporta reporte
  │
  ├─ POST /api/v1/reports/{id}/export/
  ├─ Permissions: CanExportReports (RBAC check)
  ├─ CNST-007: 5,234 < 100,000 ✓
  ├─ ExportService.export()
  ├─ Query: CallRecord.objects.filter(...)
  ├─ Generate CSV/Excel
  └─ Response: file_path

LATENCIA DE DATOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dato en IVR → Disponible en REPORTS: 12 horas (máximo)
Razón: ETL cada 12 horas (CNST-004)

ACEPTABLE porque:
✅ Reportes son para analytics (no real-time)
✅ Decisiones de negocio basadas en tendencias
✅ No afecta operaciones call center
```

---

<a name="dependencias"></a>
## 6. DEPENDENCIAS Y ACOPLAMIENTOS

### 6.1 Matriz de Dependencias

```
MATRIZ DE DEPENDENCIAS ENTRE APPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

         │ IVR_LEGACY │ PIPELINE │ CORE │ REPORTS │ ACCESS │
─────────┼────────────┼──────────┼──────┼─────────┼────────┤
IVR_LEGACY│     -     │    ✓     │  X   │    X    │   X    │
PIPELINE  │    ✓      │    -     │  ✓   │    X    │   X    │
CORE      │    X      │    X     │  -   │    ✓    │   X    │
REPORTS   │    X      │    X     │  ✓   │    -    │   ✓    │
ACCESS    │    X      │    X     │  X   │    X    │   -    │

✓ = Depende directamente
X = No depende

INTERPRETACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVR_LEGACY:
  └─ Depende de: NINGUNA (independiente)
     Usado por: PIPELINE

PIPELINE:
  ├─ Depende de: IVR_LEGACY (IVRAdapter), CORE (CallRecord)
  └─ Usado por: NINGUNA (ejecuta automáticamente)

CORE:
  └─ Depende de: NINGUNA (modelo base)
     Usado por: PIPELINE, REPORTS

REPORTS:
  ├─ Depende de: CORE (CallRecord), ACCESS (RBAC)
  └─ Usado por: NINGUNA (endpoint final)

ACCESS:
  └─ Depende de: NINGUNA (sistema transversal)
     Usado por: REPORTS, AUTHENTICATION, otras apps
```

### 6.2 Nivel de Acoplamiento

```
ANÁLISIS DE ACOPLAMIENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVR_LEGACY ← PIPELINE:
────────────────────────────────────────────────────────────
Tipo: BAJO (Adapter Pattern)
Interface: IVRAdapter.get_calls() → List[Dict]
Ventajas:
  ✅ PIPELINE no conoce detalles de MariaDB
  ✅ Fácil de mockear
  ✅ Type hints claros
Cambio en CallLog → NO afecta PIPELINE (solo adapter)

PIPELINE → CORE:
────────────────────────────────────────────────────────────
Tipo: MEDIO (Model Dependency)
Interface: CallRecord.objects.update_or_create()
Ventajas:
  ✅ ORM abstrae DB
  ⚠️ Cambio en CallRecord fields → afecta ETL
Mejora posible:
  - Repository pattern para abstraer CallRecord

CORE → REPORTS:
────────────────────────────────────────────────────────────
Tipo: MEDIO (Model Dependency)
Interface: CallRecord.objects.filter().values()
Ventajas:
  ✅ QuerySet API estándar
  ⚠️ Cambio en CallRecord fields → afecta REPORTS
Mejora posible:
  - DTO/Serializer layer entre CORE y REPORTS

REPORTS → ACCESS:
────────────────────────────────────────────────────────────
Tipo: BAJO (Interface Method)
Interface: user.has_function(function_code) → bool
Ventajas:
  ✅ Método simple y estable
  ✅ Desacoplado via User model
  ✅ Fácil de testear (mock)
  ✅ Cambios en ACCESS → NO afectan REPORTS

RESUMEN ACOPLAMIENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BAJO:
✅ IVR_LEGACY ← PIPELINE (via Adapter)
✅ REPORTS → ACCESS (via interface method)

MEDIO:
⚠️ PIPELINE → CORE (via ORM model)
⚠️ CORE → REPORTS (via ORM model)

ALTO:
❌ NINGUNO

CALIFICACIÓN GENERAL: ✅ BUENO
- No hay acoplamiento alto
- Adapter pattern reduce acoplamiento legacy
- Interface methods para RBAC
- ORM proporciona abstracción razonable
```

### 6.3 Puntos de Integración

```
PUNTOS DE INTEGRACIÓN (SEAMS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. IVRAdapter (IVR_LEGACY → PIPELINE)
   ─────────────────────────────────────────────────────────
   Interface: get_calls(fecha_inicio, fecha_fin) → List[Dict]
   Contrato:
     - Input: 2 dates
     - Output: List of dicts con campos específicos
     - Behavior: READ-ONLY, returns [] on error
   
   Testing:
     ✅ Mock IVRAdapter en tests de PIPELINE
     ✅ No requiere MariaDB en tests

2. ETLService (PIPELINE → CORE)
   ─────────────────────────────────────────────────────────
   Interface: CallRecord.objects.update_or_create()
   Contrato:
     - unique_together: (fecha, telefono, servicio_800)
     - defaults: metrics fields
     - Behavior: idempotent, safe to retry
   
   Testing:
     ✅ Use Django test DB
     ✅ Verify update_or_create behavior

3. ReportService/ExportService (CORE → REPORTS)
   ─────────────────────────────────────────────────────────
   Interface: CallRecord.objects.filter().values()
   Contrato:
     - Filters: fecha, servicio_800
     - Returns: QuerySet → List[Dict]
     - CNST-007: hard limit [:100000]
   
   Testing:
     ✅ Create test CallRecords
     ✅ Verify filters apply correctly
     ✅ Verify CNST-007 limit

4. User.has_function() (REPORTS → ACCESS)
   ─────────────────────────────────────────────────────────
   Interface: has_function(function_code) → bool
   Contrato:
     - Input: string function code
     - Output: boolean
     - Behavior: checks RBAC via ACCESS
   
   Testing:
     ✅ Mock user.has_function() = True/False
     ✅ No requiere ProfileFunction setup en tests
```

---

<a name="compliance"></a>
## 7. COMPLIANCE STANDARDS (CNST)

### 7.1 CNST-003: IVR READ-ONLY

```
CNST-003: Acceso READ-ONLY a IVR legacy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AFECTA A:
- IVR_LEGACY (origen)
- PIPELINE (consumidor)

ENFORCEMENT (3 capas):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CAPA 1: Database Router
  IVRRouter.db_for_write(model):
    if model in ivr_legacy_apps:
      return None  # Prohibe writes
  
  ✅ Imposible hacer .save(), .create(), .update()

CAPA 2: Database User
  User: ivr_readonly
  Permissions: GRANT SELECT ONLY
  
  ✅ MariaDB rechaza INSERT/UPDATE/DELETE

CAPA 3: Model Meta
  CallLog.Meta.managed = False
  
  ✅ Django NO genera migrations
  ✅ NO intenta crear/modificar tabla

VERIFICACIÓN EN CÓDIGO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IVRAdapter solo usa:
✅ .using('ivr_legacy')
✅ .filter()
✅ .values()
✅ list()

NO usa:
❌ .save()
❌ .create()
❌ .update()
❌ .delete()

COMPLIANCE: 100% ✅
```

### 7.2 CNST-004: ETL Programado (NO Real-Time)

```
CNST-004: ETL programado cada 12 horas (NO real-time)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AFECTA A:
- PIPELINE (scheduler)

ENFORCEMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scheduler: APScheduler BackgroundScheduler
Trigger: IntervalTrigger(hours=12)
Job ID: 'etl_job'

ETLScheduler.start():
  scheduler.add_job(
    run_etl,
    trigger=IntervalTrigger(hours=12),
    ...
  )

CARACTERÍSTICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Automático (background)
✅ Idempotente (safe to call start() múltiples veces)
✅ Tracking completo (ETLExecution model)
✅ Error handling (try/except, logging)
✅ NO on-demand triggers (solo programado)

LATENCIA DE DATOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dato en IVR → Disponible en REPORTS: 12 horas máximo

ACEPTABLE:
✅ Reportes son analytics, no operacionales
✅ Decisiones basadas en tendencias, no tiempo real
✅ Reduce carga en MariaDB legacy

COMPLIANCE: 100% ✅
```

### 7.3 CNST-007: Límite Exportación 100K

```
CNST-007: Máximo 100,000 registros por exportación
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AFECTA A:
- REPORTS (exportación)

ENFORCEMENT (3 capas + hard limit):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CAPA 1: Serializer (validation temprana)
  ExportJobSerializer.validate_total_records(value):
    if value > 100000:
      raise ValidationError("CNST-007: ...")
  
  ✅ Falla rápido en API request

CAPA 2: Service (business logic)
  ExportService.export():
    if total_records > MAX_EXPORT_SIZE:
      raise RuntimeError("CNST-007 violation: ...")
  
  ✅ Protección si serializer se bypassa
  ✅ Updates export_job.status = 'failed'

CAPA 3: View (endpoint protection)
  ReportViewSet.export():
    if report.total_records > MAX_EXPORT_SIZE:
      return Response({"detail": "CNST-007 ..."}, 400)
  
  ✅ Extra layer before job creation

HARD LIMIT: Query level
  queryset = CallRecord.objects.filter(...)
  queryset = queryset[:MAX_EXPORT_SIZE]
  
  ✅ NUNCA retorna más de 100K registros
  ✅ Protección DB-level

CONSTANTE CENTRALIZADA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ExportService.MAX_EXPORT_SIZE = 100000
ExportJobSerializer.MAX_EXPORT_SIZE = 100000

✅ Mismo valor en ambos lugares
✅ Fácil de cambiar si requisito cambia

TESTS DEDICADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9 tests específicos CNST-007:
- Serializer: rechaza >100K, acepta =100K, acepta <100K
- Service: rechaza >100K, acepta =100K
- Constants: verifica valor, verifica documentación
- Integration: valida 3 capas

COMPLIANCE: 100% ✅ (Triple capa + hard limit)
```

---

<a name="diagrama"></a>
## 8. DIAGRAMA DE ARQUITECTURA GENERAL

```
═══════════════════════════════════════════════════════════════════════════════
                        ARQUITECTURA COMPLETA
                    IVR_LEGACY → PIPELINE → CORE → REPORTS
                           + ACCESS (RBAC)
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌───────────────┐                                                          │
│  │  IVR_LEGACY   │  MariaDB READ-ONLY (CNST-003)                           │
│  │   MariaDB     │                                                          │
│  │  call_logs    │  ├─ User: ivr_readonly (SELECT only)                    │
│  └───────┬───────┘  ├─ Router: IVRRouter.db_for_write() → None             │
│          │          └─ Model: CallLog (managed=False)                       │
│          │                                                                   │
│          │ IVRAdapter.get_calls(fecha_inicio, fecha_fin)                    │
│          │ Interface: List[Dict]                                            │
│          │ Adapter Pattern (desacoplado)                                    │
│          ▼                                                                   │
│  ┌───────────────┐                                                          │
│  │   PIPELINE    │  ETL Programado (CNST-004)                              │
│  │  APScheduler  │                                                          │
│  │   ETLService  │  ├─ Interval: 12 horas                                  │
│  └───────┬───────┘  ├─ ETLScheduler (BackgroundScheduler)                  │
│          │          └─ Tracking: ETLExecution model                         │
│          │                                                                   │
│          │ ETL Pipeline:                                                    │
│          │ 1. EXTRACT: IVRAdapter.get_calls()                              │
│          │ 2. TRANSFORM: Validar y limpiar                                 │
│          │ 3. LOAD: CallRecord.update_or_create()                          │
│          │                                                                   │
│          │ CallRecord.objects.update_or_create(...)                        │
│          │ ORM dependency (medio acoplamiento)                              │
│          ▼                                                                   │
│  ┌───────────────┐                                                          │
│  │     CORE      │  Analytics Database                                     │
│  │  CallRecord   │                                                          │
│  │ SQLite/Postgres│  ├─ Table: call_records                                 │
│  └───────┬───────┘  ├─ Indexes: fecha, servicio_800                        │
│          │          └─ unique_together: (fecha, telefono, servicio_800)    │
│          │                                                                   │
│          │ QuerySet API:                                                    │
│          │ - CallRecord.objects.filter()                                   │
│          │ - .count()                                                       │
│          │ - .values()                                                      │
│          ▼                                                                   │
│  ┌───────────────┐                                                          │
│  │    REPORTS    │  Reportes y Exportación                                 │
│  │               │                                                          │
│  │ ReportService │  ├─ Models: Report, ExportJob                           │
│  │ ExportService │  ├─ Services: ReportService, ExportService              │
│  │               │  ├─ Formats: CSV (DictWriter), Excel (openpyxl)         │
│  │               │  └─ CNST-007: Límite 100K (triple capa)                 │
│  └───────────────┘                                                          │
│          ▲                                                                   │
│          │                                                                   │
│          │ Permissions (RBAC):                                              │
│          │ - CanViewReports                                                 │
│          │ - CanCreateReports                                               │
│          │ - CanExportReports                                               │
│          │ - IsReportOwner                                                  │
│          │                                                                   │
│          │ user.has_function(function_code)                                 │
│          │ Interface method (bajo acoplamiento)                             │
│          │                                                                   │
│  ┌───────┴───────┐                                                          │
│  │    ACCESS     │  RBAC System                                            │
│  │  ProfileFunc  │                                                          │
│  │   Function    │  ├─ ModuleAccessService.user_has_function()             │
│  │   Profile     │  ├─ ProfileFunction (user ↔ function)                   │
│  └───────────────┘  └─ Funciones: reports.view_report, etc.                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

FLUJO DE DATOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Llamada → IVR_LEGACY (MariaDB call_logs)
   └─ CNST-003: READ-ONLY enforcement

2. PIPELINE extrae cada 12h
   ├─ IVRAdapter.get_calls()
   ├─ ETLService: Extract → Transform → Load
   └─ CNST-004: NO real-time

3. Datos en CORE (CallRecord analytics DB)
   └─ Optimizado para queries

4. REPORTS consulta y exporta
   ├─ ReportService.count()
   ├─ ExportService.export()
   └─ CNST-007: Límite 100K

5. ACCESS controla permisos
   ├─ user.has_function()
   └─ RBAC granular

COMPLIANCE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CNST-003: IVR READ-ONLY (3 capas)
✅ CNST-004: ETL 12 horas (APScheduler)
✅ CNST-007: Export 100K (3 capas + hard limit)

ACOPLAMIENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BAJO:
✅ IVR_LEGACY ← PIPELINE (via Adapter)
✅ REPORTS → ACCESS (via interface)

MEDIO:
⚠️ PIPELINE → CORE (via ORM)
⚠️ CORE → REPORTS (via ORM)

CALIFICACIÓN: ✅ BUENA arquitectura
```

---

## RESUMEN Y CONCLUSIONES

### Relaciones Identificadas

```
1. IVR_LEGACY → PIPELINE
   ─────────────────────────────────────────────────────────
   Tipo: Adapter Pattern (bajo acoplamiento)
   Interface: IVRAdapter.get_calls() → List[Dict]
   Compliance: CNST-003 (READ-ONLY)
   Calidad: ⭐⭐⭐ EXCELENTE

2. PIPELINE → CORE
   ─────────────────────────────────────────────────────────
   Tipo: ETL Pipeline (medio acoplamiento)
   Interface: CallRecord.objects.update_or_create()
   Compliance: CNST-004 (12h interval)
   Calidad: ⭐⭐⭐ EXCELENTE

3. CORE → REPORTS
   ─────────────────────────────────────────────────────────
   Tipo: Query Pattern (medio acoplamiento)
   Interface: CallRecord.objects.filter().values()
   Compliance: CNST-007 (100K limit)
   Calidad: ⭐⭐⭐ EXCELENTE

4. ACCESS → REPORTS
   ─────────────────────────────────────────────────────────
   Tipo: RBAC Integration (bajo acoplamiento)
   Interface: user.has_function() → bool
   Compliance: N/A (permissions)
   Calidad: ⭐⭐⭐ EXCELENTE
```

### Flujo End-to-End

```
Llamada (T+0) → IVR_LEGACY → PIPELINE (T+12h) → CORE → REPORTS

Latencia: 12 horas máximo (aceptable para analytics)
Compliance: 3 CNST cumplidos (003, 004, 007)
Arquitectura: ✅ Bien diseñada, bajo acoplamiento
```

### Puntos Fuertes

```
✅ Adapter Pattern desacopla IVR legacy
✅ ETL programado (no real-time apropiado)
✅ Triple capa CNST-007 (defense in depth)
✅ RBAC granular con bajo acoplamiento
✅ Error handling completo
✅ Idempotencia en ETL
✅ Data isolation por usuario
```

### Áreas de Mejora

```
⚠️ PIPELINE → CORE: considerar Repository pattern
⚠️ CORE → REPORTS: considerar DTO layer
⚠️ Job persistence en APScheduler (opcional)
```

### Recomendaciones

```
1. Mantener Adapter Pattern para legacy systems
2. Continuar con triple capa para compliance crítico
3. Considerar Repository pattern si crece complejidad
4. Documentar latencia de datos (12h) para usuarios
5. Monitorear ETL execution (ETLExecution model)
```

---

**FIN DEL ANÁLISIS DE RELACIONES**

Documento creado: 2026-01-17  
Apps analizadas: IVR_LEGACY, PIPELINE, CORE, REPORTS, ACCESS  
Total líneas: ~1,600 líneas  
Estado: ✅ COMPLETO
