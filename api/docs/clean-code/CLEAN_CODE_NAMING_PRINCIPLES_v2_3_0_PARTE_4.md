---
version: 2.3.0
date: 2026-01-18
project: IACT (Sistema Call Center)
base: Clean Code (Robert Martin) + Clean Architecture
changelog: PARTE 4/5 - IACT Específico (Renderers, Separación access/, Service Layer, Modelos)
partes: 4/5
estado: completo
---

# CLEAN CODE NAMING PRINCIPLES v2.3.0

**PARTE 4/5: IACT ESPECÍFICO**

---

## 📋 CONTENIDO DE ESTA PARTE

24. [DRF: Renderers, Parsers, Pagination](#24-drf-renderers-parsers-pagination)
25. [IACT: Separación access/ vs core/](#25-iact-separacion-access-core)
26. [IACT: Service Layer Pattern](#26-iact-service-layer-pattern)
27. [IACT: Modelos y Herencia](#27-iact-modelos-herencia)

---

## RECORDATORIO: REGLA DE IDIOMA

```
✅ CÓDIGO: Siempre en INGLÉS
✅ COMENTARIOS/DOCSTRINGS: Siempre en ESPAÑOL
✅ NOMBRES DE DOMINIO: Depende del contexto

Function ID RBAC: reports.view (inglés)
Display name: ve_reportes (español)
Error messages: español
```

---

<a name="24-drf-renderers-parsers-pagination"></a>
## 24. DRF: RENDERERS, PARSERS, PAGINATION

### 24.1 Renderers Personalizados

```python
# apps/utils/renderers.py

from rest_framework.renderers import JSONRenderer
from django.utils import timezone


class IACTJSONRenderer(JSONRenderer):
    """
    Renderer JSON con metadata IACT.
    
    Agrega a toda respuesta exitosa:
    - timestamp ISO8601
    - version API
    - server identifier (opcional)
    """  # ← Español
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Renderiza con metadata."""  # ← Español
        
        if not renderer_context:
            return super().render(data, accepted_media_type, renderer_context)
        
        response = renderer_context.get('response')
        
        # Solo agregar metadata en 2xx (success)
        if response and 200 <= response.status_code < 300:
            wrapped = {
                'data': data,
                'meta': {
                    'timestamp': timezone.now().isoformat(),
                    'version': 'v1',
                    'status': 'success'
                }
            }
            return super().render(wrapped, accepted_media_type, renderer_context)
        
        # En errores (4xx, 5xx), no envolver
        return super().render(data, accepted_media_type, renderer_context)


# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'apps.utils.renderers.IACTJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Solo dev
    ],
}
```

### 24.2 Parsers

```python
# apps/utils/parsers.py

from rest_framework.parsers import JSONParser


class StrictJSONParser(JSONParser):
    """
    Parser JSON estricto.
    
    Rechaza JSON mal formado con mensaje claro.
    """  # ← Español
    
    def parse(self, stream, media_type=None, parser_context=None):
        """Parse con validación estricta."""  # ← Español
        
        try:
            return super().parse(stream, media_type, parser_context)
        except Exception as e:
            raise ParseError(
                f"JSON mal formado: {str(e)}",
                code='invalid_json'
            )
```

### 24.3 Pagination Personalizada

```python
# apps/utils/pagination.py

from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Paginación estándar IACT.
    
    Configuración:
    - 50 registros por defecto
    - Hasta 100 máximo
    - Permite personalizar con ?page_size=N
    
    Uso:
        class MyViewSet(viewsets.ModelViewSet):
            pagination_class = StandardPagination
    """  # ← Español
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Response con metadata de paginación.
        
        Returns:
            {
                "count": total registros,
                "next": URL página siguiente,
                "previous": URL página anterior,
                "total_pages": total de páginas,
                "current_page": página actual,
                "page_size": tamaño de página,
                "results": [...]
            }
        """  # ← Español
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'results': data
        })


class LargePagination(PageNumberPagination):
    """
    Paginación para volúmenes grandes.
    
    Uso:
    - Exports
    - Logs
    - Historial
    
    Configuración:
    - 1000 registros por defecto
    - Hasta 5000 máximo
    """  # ← Español
    
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 5000


class TimelinePagination(CursorPagination):
    """
    Paginación por cursor (timeline).
    
    Uso:
    - Feeds en tiempo real
    - Auditoría (orden temporal)
    - Logs en orden cronológico
    
    Ventajas:
    - Performance constante (no degrada con páginas altas)
    - Consistente con datos que cambian
    """  # ← Español
    
    page_size = 50
    ordering = '-created_at'  # Más recientes primero
    cursor_query_param = 'cursor'
```

---

<a name="25-iact-separacion-access-core"></a>
## 25. IACT: SEPARACIÓN access/ vs core/

### 25.1 apps/core/ DEPRECADO

**IMPORTANTE:** `apps/core/` está DEPRECADO desde v2.0.0

```python
# ❌ DEPRECADO - NO usar apps/core/
from apps.core.services import PermissionService  # ❌ DEPRECADO
from apps.core.models import Function  # ❌ DEPRECADO


# ✅ CORRECTO - Usar apps/access/
from apps.access.services import AccessService  # ✅ CORRECTO
from apps.access.models import Function  # ✅ CORRECTO
```

**Razón de deprecación:**

```
apps/core/ era una "bolsa de funciones" sin cohesión:
❌ Mezclaba RBAC, permisos, utilidades
❌ Sin propósito claro
❌ Violaba Single Responsibility
❌ Dependencias confusas

apps/access/ tiene cohesión clara:
✅ Propósito: Control de acceso RBAC
✅ Dominio: Funciones, Agrupadores, SoD
✅ Single Responsibility
✅ Dependencias claras
```

### 25.2 Migración apps/core/ → apps/access/

```python
# ANTES (v1.x con apps/core/)
# apps/core/models.py
class Function(models.Model):
    pass

class Agrupador(models.Model):
    pass

# apps/core/services.py
class PermissionService:
    @staticmethod
    def check_permission(user, function_id):
        pass


# DESPUÉS (v2.0+ con apps/access/)
# apps/access/models.py
class Function(models.Model):
    pass

class Agrupador(models.Model):
    pass

# apps/access/services.py
class AccessService:
    @staticmethod
    def user_has_function(user, function_id):
        pass
```

**Cambios de naming:**

| Antes (core/) | Después (access/) |
|---------------|-------------------|
| PermissionService | AccessService |
| check_permission() | user_has_function() |
| get_user_permissions() | get_user_functions() |

---

<a name="26-iact-service-layer-pattern"></a>
## 26. IACT: SERVICE LAYER PATTERN

### 26.1 Qué es Service Layer

**Definición:** Capa de lógica de negocio entre Views y Models.

```
┌─────────────────────────────────────────────┐
│ VIEW (DRF ViewSet)                          │
│ - Recibe HTTP request                       │
│ - Valida datos básicos                      │
│ - DELEGA a Service                          │
│ - Retorna HTTP response                     │
└─────────────────┬───────────────────────────┘
                  │ delega
                  ▼
┌─────────────────────────────────────────────┐
│ SERVICE (Business Logic)                    │
│ - Valida reglas de negocio                  │
│ - Coordina múltiples modelos                │
│ - Maneja transacciones                      │
│ - Lógica compleja                           │
│ - NO conoce HTTP                            │
└─────────────────┬───────────────────────────┘
                  │ usa
                  ▼
┌─────────────────────────────────────────────┐
│ MODEL (Data Access)                         │
│ - Acceso a base de datos                    │
│ - Queries                                    │
│ - Validaciones de modelo                    │
└─────────────────────────────────────────────┘
```

### 26.2 ReportService - Ejemplo Completo

```python
# apps/reports/services.py

from datetime import date, timedelta
from typing import Dict, List, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.ivr.models import ReporteTrimestral, JobExecutionLog
from apps.pipeline.services import ETLMonitoringService
from apps.utils.exceptions import (
    DateRangeExceeded,
    ExportLimitExceeded,
    ETLDataNotAvailable
)


class ReportService:
    """
    Servicio de reportes.
    
    Responsabilidades:
    - Generación de reportes
    - Validación de reglas de negocio (CNST-006, CNST-007)
    - Exportación a múltiples formatos
    - Coordinación con ETL
    
    NO maneja:
    - HTTP (eso es del ViewSet)
    - Serialización (eso es del Serializer)
    - Autenticación (eso es del Middleware)
    """  # ← Español
    
    # Constantes (CNST-006, CNST-007)
    MAX_DATE_RANGE_DAYS = 730  # 2 años
    MAX_EXPORT_RECORDS = 100000
    
    @staticmethod
    def get_trimestral_data(
        start_date: date,
        end_date: date,
        trimestre: str,
        did: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtiene datos de reporte trimestral.
        
        Valida:
        - Rango de fechas (CNST-006)
        - Disponibilidad de datos ETL
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
            trimestre: Q1, Q2, Q3
            did: Filtro opcional de DID
        
        Returns:
            Lista de registros del reporte
        
        Raises:
            DateRangeExceeded: Si rango > 730 días
            ETLDataNotAvailable: Si datos no procesados
        """  # ← Español
        
        # 1. Validar rango de fechas (CNST-006)
        ReportService._validate_date_range(start_date, end_date)
        
        # 2. Verificar disponibilidad datos ETL
        ReportService._check_etl_data_available(start_date)
        
        # 3. Construir queryset
        queryset = ReporteTrimestral.objects.filter(
            fecha__gte=start_date,
            fecha__lte=end_date,
            trimestre=trimestre
        )
        
        # 4. Aplicar filtro DID si se proporciona
        if did:
            queryset = queryset.filter(servicio_800=did)
        
        # 5. Retornar datos
        return list(queryset.values(
            'fecha',
            'trimestre',
            'servicio_800',
            'total_llamadas',
            'clientes_unicos'
        ))
    
    @staticmethod
    def export_to_excel(
        start_date: date,
        end_date: date,
        trimestre: str
    ) -> str:
        """
        Exporta reporte a Excel.
        
        Valida:
        - Límite de registros (CNST-007)
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
            trimestre: Trimestre
        
        Returns:
            URL del archivo generado
        
        Raises:
            ExportLimitExceeded: Si registros > 100k
        """  # ← Español
        
        # 1. Obtener datos
        data = ReportService.get_trimestral_data(
            start_date, end_date, trimestre
        )
        
        # 2. Validar límite (CNST-007)
        if len(data) > ReportService.MAX_EXPORT_RECORDS:
            raise ExportLimitExceeded(
                f"Límite de exportación: {ReportService.MAX_EXPORT_RECORDS:,} "
                f"registros. Encontrados: {len(data):,}",
                details={
                    'max_records': ReportService.MAX_EXPORT_RECORDS,
                    'found_records': len(data)
                }
            )
        
        # 3. Generar Excel
        from apps.utils.excel import ExcelGenerator
        
        file_path = ExcelGenerator.create_report(
            data=data,
            title=f"Reporte Trimestral {trimestre}",
            headers=['Fecha', 'Trimestre', 'DID', 'Llamadas', 'Clientes']
        )
        
        # 4. Retornar URL
        return file_path
    
    @staticmethod
    def calculate_metrics(
        records: List[Dict]
    ) -> Dict[str, any]:
        """
        Calcula métricas de lista de records.
        
        Lógica pura (sin DB, sin Django).
        Testeable con pytest simple.
        
        Args:
            records: Lista de diccionarios con datos
        
        Returns:
            Dict con métricas calculadas
        """  # ← Español
        
        total_calls = sum(r.get('total_llamadas', 0) for r in records)
        unique_clients = len(set(r.get('telefono_origen') for r in records if r.get('telefono_origen')))
        
        avg_calls_per_client = (
            total_calls / unique_clients if unique_clients > 0 else 0
        )
        
        return {
            'total_calls': total_calls,
            'unique_clients': unique_clients,
            'avg_per_client': round(avg_calls_per_client, 2)
        }
    
    @staticmethod
    def _validate_date_range(start_date: date, end_date: date) -> None:
        """
        Valida rango de fechas (CNST-006).
        
        Raises:
            DateRangeExceeded: Si rango > 730 días
            ValidationError: Si end < start
        """  # ← Español
        
        if end_date < start_date:
            raise ValidationError("Fecha fin debe ser >= fecha inicio")
        
        days = (end_date - start_date).days
        
        if days > ReportService.MAX_DATE_RANGE_DAYS:
            raise DateRangeExceeded(
                f"Rango máximo: {ReportService.MAX_DATE_RANGE_DAYS} días. "
                f"Solicitado: {days} días",
                details={
                    'max_days': ReportService.MAX_DATE_RANGE_DAYS,
                    'requested_days': days
                }
            )
    
    @staticmethod
    def _check_etl_data_available(date: date) -> None:
        """
        Verifica que ETL haya procesado datos para fecha.
        
        Raises:
            ETLDataNotAvailable: Si datos no disponibles
        """  # ← Español
        
        # Verificar que hay ejecución ETL para la fecha
        has_data = ETLMonitoringService.has_data_for_date(date)
        
        if not has_data:
            raise ETLDataNotAvailable(
                f"Datos no disponibles para {date}. "
                f"ETL aún no ha procesado esta fecha.",
                details={'date': date.isoformat()}
            )
```

### 26.3 AccessService - Con Transacciones

```python
# apps/access/services.py

from django.db import transaction
from django.db.models import Q
from typing import List
from apps.access.models import Function, Agrupador, SeparationOfDuties
from apps.utils.exceptions import SeparationOfDutiesViolation


class AccessService:
    """
    Servicio de control de acceso RBAC.
    
    Responsabilidades:
    - Verificación de funciones
    - Asignación/revocación de funciones
    - Validación de Separation of Duties (SoD)
    """  # ← Español
    
    @staticmethod
    def user_has_function(user, function_id: str) -> bool:
        """
        Verifica si usuario tiene función asignada.
        
        Args:
            user: Usuario a verificar
            function_id: ID de función (ej: 'reports.view')
        
        Returns:
            True si tiene la función activa
        """  # ← Español
        
        # Obtener agrupadores del usuario
        agrupadores = Agrupador.objects.filter(
            users=user,
            is_active=True,
            is_deleted=False
        ).prefetch_related('functions')
        
        # Verificar si algún agrupador tiene la función
        for agrupador in agrupadores:
            if agrupador.functions.filter(
                function_id=function_id,
                is_active=True
            ).exists():
                return True
        
        return False
    
    @staticmethod
    @transaction.atomic
    def assign_function_to_user(
        user,
        function_id: str,
        assigned_by
    ) -> bool:
        """
        Asigna función a usuario.
        
        Crea agrupador personal si no existe.
        Valida Separation of Duties.
        
        Args:
            user: Usuario receptor
            function_id: ID de función
            assigned_by: Usuario que asigna
        
        Returns:
            True si asignación exitosa
        
        Raises:
            SeparationOfDutiesViolation: Si viola SoD
        """  # ← Español
        
        # 1. Validar SoD
        violations = AccessService._check_sod_violations(user, function_id)
        
        if violations:
            raise SeparationOfDutiesViolation(
                f"No se puede asignar '{function_id}' a {user.username}. "
                f"Viola separación de funciones con: {', '.join(violations)}",
                details={
                    'function_id': function_id,
                    'conflicting_functions': violations
                }
            )
        
        # 2. Obtener función
        try:
            function = Function.objects.get(
                function_id=function_id,
                is_active=True
            )
        except Function.DoesNotExist:
            raise ValidationError(f"Función '{function_id}' no existe")
        
        # 3. Obtener o crear agrupador personal
        agrupador, created = Agrupador.objects.get_or_create(
            name=f"Personal_{user.username}",
            type='personal',
            defaults={
                'created_by': assigned_by
            }
        )
        
        # 4. Agregar usuario al agrupador
        agrupador.users.add(user)
        
        # 5. Agregar función al agrupador
        agrupador.functions.add(function)
        
        # 6. Auditar
        from apps.audit.services import AuditService
        AuditService.log_function_assignment(
            user=user,
            function=function,
            assigned_by=assigned_by
        )
        
        return True
    
    @staticmethod
    def _check_sod_violations(user, new_function_id: str) -> List[str]:
        """
        Verifica violaciones de Separation of Duties.
        
        Returns:
            Lista de function_ids conflictivos
        """  # ← Español
        
        # Obtener funciones actuales del usuario
        current_functions = set()
        agrupadores = Agrupador.objects.filter(
            users=user,
            is_active=True,
            is_deleted=False
        ).prefetch_related('functions')
        
        for agrupador in agrupadores:
            for function in agrupador.functions.filter(is_active=True):
                current_functions.add(function.function_id)
        
        # Obtener función nueva
        try:
            new_function = Function.objects.get(function_id=new_function_id)
        except Function.DoesNotExist:
            return []
        
        # Buscar reglas SoD que involucren la nueva función
        sod_rules = SeparationOfDuties.objects.filter(
            is_active=True,
            is_deleted=False
        ).filter(
            Q(function_1=new_function) | Q(function_2=new_function)
        )
        
        violations = []
        for rule in sod_rules:
            conflicting_id = (
                rule.function_2.function_id 
                if rule.function_1 == new_function 
                else rule.function_1.function_id
            )
            
            if conflicting_id in current_functions:
                violations.append(conflicting_id)
        
        return violations
```

---

<a name="27-iact-modelos-herencia"></a>
## 27. IACT: MODELOS Y HERENCIA

### 27.1 Patrón de Herencia Estándar

```python
# ✅ CORRECTO - Herencia múltiple con orden correcto

from django.db import models
from apps.utils.models import SoftDeleteMixin, TimeStampedModel


class Report(SoftDeleteMixin, TimeStampedModel, models.Model):
    """
    Modelo de reporte.
    
    Orden de herencia (IMPORTANTE):
    1. SoftDeleteMixin (primero)
    2. TimeStampedModel (segundo)
    3. models.Model (último)
    
    Campos heredados:
    - SoftDeleteMixin: is_deleted, deleted_at, deleted_by
    - TimeStampedModel: created_at, updated_at
    
    CNST-005: TODOS los modelos IACT heredan estos mixins.
    """  # ← Español
    
    # Campos específicos del modelo
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='reports',
        verbose_name="Propietario"
    )
    
    class Meta:
        db_table = 'reports'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['is_deleted', '-created_at']),
        ]
    
    def __str__(self):
        return self.name


# ❌ INCORRECTO - Sin mixins
class Report(models.Model):
    name = models.CharField()
    created_at = models.DateTimeField()  # ❌ Duplica TimeStampedModel
    updated_at = models.DateTimeField()  # ❌ Duplica TimeStampedModel
    # ❌ Falta soft delete (viola CNST-005)


# ❌ INCORRECTO - Orden de herencia invertido
class Report(models.Model, TimeStampedModel, SoftDeleteMixin):
    # ❌ models.Model debe ir AL FINAL
    pass


# ❌ INCORRECTO - Solo un mixin
class Report(TimeStampedModel, models.Model):
    # ❌ Falta SoftDeleteMixin (viola CNST-005)
    pass
```

### 27.2 Manager Personalizado

```python
# apps/reports/models.py

from django.db import models
from apps.utils.models import SoftDeleteMixin, TimeStampedModel


class ReportManager(models.Manager):
    """Manager con métodos convenientes."""  # ← Español
    
    def active(self):
        """Reportes activos (no eliminados)."""
        return self.filter(is_deleted=False)
    
    def deleted(self):
        """Reportes eliminados."""
        return self.filter(is_deleted=True)
    
    def by_owner(self, user):
        """Reportes de un usuario específico."""
        return self.active().filter(owner=user)
    
    def recent(self, days=7):
        """Reportes creados en últimos N días."""
        from django.utils import timezone
        from datetime import timedelta
        
        threshold = timezone.now() - timedelta(days=days)
        return self.active().filter(created_at__gte=threshold)


class Report(SoftDeleteMixin, TimeStampedModel, models.Model):
    """Modelo con manager personalizado."""  # ← Español
    
    name = models.CharField(max_length=200)
    owner = models.ForeignKey('users.User', on_delete=models.PROTECT)
    
    # Manager personalizado
    objects = ReportManager()
    
    class Meta:
        db_table = 'reports'


# ✅ USO:
Report.objects.active()           # Solo activos
Report.objects.deleted()          # Solo eliminados
Report.objects.by_owner(user)     # De un usuario
Report.objects.recent(days=30)    # Últimos 30 días
```

### 27.3 Modelo con Choices (TextChoices)

```python
class Report(SoftDeleteMixin, TimeStampedModel, models.Model):
    """Modelo con choices."""  # ← Español
    
    # ✅ CORRECTO - Choices con TextChoices
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'          # key inglés, label español
        PENDING = 'pending', 'Pendiente'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Baja'
        MEDIUM = 'medium', 'Media'
        HIGH = 'high', 'Alta'
        URGENT = 'urgent', 'Urgente'
    
    name = models.CharField(max_length=200)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado"
    )
    
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Prioridad"
    )
    
    class Meta:
        db_table = 'reports'


# ❌ INCORRECTO - Choices en español (keys)
class Status(models.TextChoices):
    BORRADOR = 'borrador', 'Borrador'  # ❌ Key debe ser inglés
    PENDIENTE = 'pendiente', 'Pendiente'


# ❌ INCORRECTO - Choices antiguos (tuplas)
STATUS_CHOICES = [  # ❌ Usar TextChoices
    ('draft', 'Borrador'),
    ('pending', 'Pendiente'),
]
```

### 27.4 Modelo con Validaciones Custom

```python
from django.core.exceptions import ValidationError


class Report(SoftDeleteMixin, TimeStampedModel, models.Model):
    """Modelo con validaciones custom."""  # ← Español
    
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    
    class Meta:
        db_table = 'reports'
    
    def clean(self):
        """
        Validación a nivel de modelo.
        
        Llamado automáticamente por forms y admin.
        También puede llamarse manualmente: instance.clean()
        
        Raises:
            ValidationError: Si datos inválidos
        """  # ← Español
        super().clean()
        
        # Validar fechas
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'Fecha fin debe ser posterior a fecha inicio'
                })
            
            # Validar rango máximo (CNST-006)
            days_diff = (self.end_date - self.start_date).days
            if days_diff > 730:
                raise ValidationError(
                    f"Rango máximo es de 2 años (CNST-006). "
                    f"Rango: {days_diff} días"
                )
    
    def save(self, *args, **kwargs):
        """
        Override save para ejecutar validaciones.
        
        IMPORTANTE: clean() NO se ejecuta automáticamente en save()
        Debemos llamarlo explícitamente.
        """  # ← Español
        
        # Ejecutar validaciones
        self.full_clean()
        
        super().save(*args, **kwargs)
```

---

**FIN DE PARTE 4/5**

**Continúa en:** CLEAN_CODE_NAMING_PRINCIPLES_v2_3_0_PARTE_5.md

---

**Resumen Parte 4:**
- ✅ Sección 24: DRF Renderers/Parsers/Pagination (IACTJSONRenderer, StandardPagination)
- ✅ Sección 25: Separación access/ vs core/ (deprecación apps/core/)
- ✅ Sección 26: Service Layer Pattern (ReportService, AccessService con transacciones)
- ✅ Sección 27: Modelos y Herencia (orden correcto, managers, choices, validaciones)

**Próxima parte:** Anti-patterns + Tabla Resumen + Referencias + Changelog v2.3.0 (secciones 28-31)
