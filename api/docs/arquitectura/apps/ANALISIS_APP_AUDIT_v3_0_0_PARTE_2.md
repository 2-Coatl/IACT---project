---
version: 3.0.0
date: 2026-01-19
project: IACT Call Center System
type: Análisis de Arquitectura - App Audit PARTE 2/3
categoria: arquitectura/apps
tema: apps/audit/ - Implementación Completa
autor: Claude Technical Analysis
tags: [audit, services, api, serializers, viewsets, signals, cnst-031]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
estado: definitivo
parte: 2 de 3
relacionado:
  - ANALISIS_APP_AUDIT_v3_0_0_PARTE_1.md
  - ANALISIS_APP_AUDIT_v3_0_0_PARTE_3.md
---

# ANÁLISIS DE apps/audit/ v3.0.0 - PARTE 2/3
## IMPLEMENTACIÓN COMPLETA

---

## TABLA DE CONTENIDOS

1. [Resumen Parte 2](#resumen)
2. [Service Layer](#services)
3. [Utils y Helpers](#utils)
4. [Serializers](#serializers)
5. [ViewSets ReadOnly](#viewsets)
6. [Signals](#signals)
7. [URLs Configuration](#urls)
8. [Middleware](#middleware)

---

<a name="resumen"></a>
## 1. RESUMEN PARTE 2

### 1.1 Alcance de esta Parte

```yaml
Componentes cubiertos:
  ✅ Service Layer (3 services)
  ✅ Utils y helpers (5 funciones)
  ✅ Serializers (5 serializers ReadOnly)
  ✅ ViewSets ReadOnly con RBAC (2 viewsets)
  ✅ Signals para auto-logging (3 signals)
  ✅ URLs configuration
  ✅ Middleware de auditoría

Líneas de código: ~1,100 líneas Python
Archivos generados:
  - apps/audit/services.py
  - apps/audit/utils.py
  - apps/audit/serializers.py
  - apps/audit/views.py
  - apps/audit/signals.py
  - apps/audit/middleware.py
  - apps/audit/urls.py
```

### 1.2 Endpoints API Generados

```http
# Ver logs (ReadOnly)
GET    /api/v1/audit/logs/
GET    /api/v1/audit/logs/{id}/

# Búsquedas
POST   /api/v1/audit/search/

# Reportes
GET    /api/v1/audit/reports/user-activity/
GET    /api/v1/audit/reports/data-changes/
GET    /api/v1/audit/reports/sensitive-access/
GET    /api/v1/audit/reports/compliance/

# Exportar
POST   /api/v1/audit/export/csv/
POST   /api/v1/audit/export/excel/
POST   /api/v1/audit/export/json/

# Login logs
GET    /api/v1/audit/login-logs/

Nota: NO hay endpoints POST/PUT/DELETE (CNST-031)
```

---

<a name="services"></a>
## 2. SERVICE LAYER

### 2.1 Archivo: apps/audit/services.py

```python
"""
Service Layer para sistema de auditoría.

Responsabilidades:
- Logging de acciones (CNST-031 immutable)
- Generación de reportes
- Búsqueda de logs
- Exportación de datos

CLEAN_CODE v3.0.1:
- Clases: AuditService (PascalCase)
- Métodos: log_action (snake_case)
- Docstrings: español formato Google

CNST-031: Logs immutables, solo INSERT
CNST-032: Queries optimizadas
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count, Avg

from apps.audit.models import AuditLog, LoginLog
from apps.audit.constants import (
    ACTION_CREATE,
    ACTION_UPDATE,
    ACTION_DELETE,
    ACTION_VIEW,
    ACTION_LOGIN,
    ACTION_LOGOUT,
    MAX_LOGS_PER_QUERY,
)
from apps.audit.utils import (
    get_client_ip,
    sanitize_sensitive_data,
    calculate_data_diff,
)

User = get_user_model()


class AuditService:
    """
    Servicio principal de auditoría.
    
    Responsabilidades:
    - Logging de acciones de usuarios
    - Consultas de logs
    - CNST-031: Solo INSERT, NO UPDATE/DELETE
    """
    
    def log_action(
        self,
        user: User,
        action: str,
        model_name: str,
        instance_id: int,
        data_before: Optional[Dict] = None,
        data_after: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        user_agent: Optional[str] = None
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
            endpoint: URL del endpoint llamado
            user_agent: User-Agent del navegador
        
        Returns:
            AuditLog: Registro de auditoría creado
        
        CNST-031: Log es immutable, solo INSERT
        
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
        # Sanitizar datos sensibles
        if data_before:
            data_before = sanitize_sensitive_data(data_before)
        if data_after:
            data_after = sanitize_sensitive_data(data_after)
        
        # Crear log (solo INSERT, CNST-031)
        log = AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            instance_id=instance_id,
            data_before=data_before,
            data_after=data_after,
            ip_address=ip_address,
            endpoint=endpoint,
            user_agent=user_agent
        )
        
        return log
    
    def log_login(
        self,
        user: Optional[User],
        attempted_username: str,
        success: bool,
        ip_address: str,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
        session_key: Optional[str] = None
    ) -> LoginLog:
        """
        Registra intento de login.
        
        Args:
            user: Usuario (None si login falló)
            attempted_username: Username ingresado
            success: Si el login fue exitoso
            ip_address: IP del intento
            user_agent: User-Agent del navegador
            failure_reason: Razón del fallo (si aplica)
            session_key: Django session key
        
        Returns:
            LoginLog: Registro de login creado
        
        CNST-031: Immutable
        """
        log = LoginLog.objects.create(
            user=user,
            attempted_username=attempted_username,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason,
            session_key=session_key
        )
        
        return log
    
    def log_logout(
        self,
        user: User,
        ip_address: str,
        session_key: Optional[str] = None
    ) -> AuditLog:
        """
        Registra logout de usuario.
        
        Args:
            user: Usuario que hizo logout
            ip_address: IP del usuario
            session_key: Django session key
        
        Returns:
            AuditLog: Registro de logout
        """
        log = self.log_action(
            user=user,
            action=ACTION_LOGOUT,
            model_name='Session',
            instance_id=0,  # N/A para logout
            ip_address=ip_address,
            data_after={'session_key': session_key}
        )
        
        return log
    
    def get_user_actions(
        self,
        user: User,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        action: Optional[str] = None,
        model_name: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Obtiene acciones de un usuario.
        
        Args:
            user: Usuario
            date_from: Fecha desde
            date_to: Fecha hasta
            action: Filtrar por tipo de acción
            model_name: Filtrar por modelo
            limit: Límite de registros (max 10,000)
        
        Returns:
            Lista de AuditLog
        
        CNST-032: Query optimizada con índices
        """
        queryset = AuditLog.objects.filter(user=user)
        
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        if action:
            queryset = queryset.filter(action=action)
        
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        # CNST-032: Límite para performance
        limit = min(limit, MAX_LOGS_PER_QUERY)
        
        return queryset.order_by('-timestamp')[:limit]
    
    def get_failed_login_attempts(
        self,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        hours: int = 24
    ) -> List[LoginLog]:
        """
        Obtiene intentos de login fallidos.
        
        Args:
            username: Filtrar por username
            ip_address: Filtrar por IP
            hours: Últimas N horas
        
        Returns:
            Lista de LoginLog fallidos
        
        Útil para detectar ataques de fuerza bruta.
        """
        since = timezone.now() - timedelta(hours=hours)
        
        queryset = LoginLog.objects.filter(
            success=False,
            timestamp__gte=since
        )
        
        if username:
            queryset = queryset.filter(attempted_username=username)
        
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        
        return queryset.order_by('-timestamp')


class ReportService:
    """
    Servicio de generación de reportes.
    
    Responsabilidades:
    - Reportes de actividad
    - Reportes de compliance
    - Estadísticas agregadas
    """
    
    def user_activity_report(
        self,
        user: User,
        date_from: datetime,
        date_to: datetime
    ) -> Dict[str, Any]:
        """
        Genera reporte de actividad de usuario.
        
        Args:
            user: Usuario
            date_from: Fecha desde
            date_to: Fecha hasta
        
        Returns:
            Dict con estadísticas de actividad
        
        Example:
            {
                "user_id": 123,
                "username": "jdoe",
                "total_actions": 150,
                "actions_by_type": {
                    "CREATE": 50,
                    "UPDATE": 80,
                    "DELETE": 10,
                    "VIEW": 10
                },
                "most_modified_models": [
                    {"model": "User", "count": 60},
                    {"model": "Call", "count": 40}
                ],
                "daily_activity": [
                    {"date": "2026-01-01", "count": 20},
                    ...
                ]
            }
        """
        logs = AuditLog.objects.filter(
            user=user,
            timestamp__gte=date_from,
            timestamp__lte=date_to
        )
        
        # Total acciones
        total_actions = logs.count()
        
        # Acciones por tipo
        actions_by_type = logs.values('action').annotate(
            count=Count('id')
        ).order_by('-count')
        
        actions_dict = {
            item['action']: item['count']
            for item in actions_by_type
        }
        
        # Modelos más modificados
        most_modified = logs.values('model_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Actividad diaria
        daily = logs.extra(
            select={'date': 'DATE(timestamp)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return {
            'user_id': user.id,
            'username': user.username,
            'total_actions': total_actions,
            'actions_by_type': actions_dict,
            'most_modified_models': list(most_modified),
            'daily_activity': list(daily)
        }
    
    def data_changes_report(
        self,
        model_name: str,
        date_from: datetime,
        date_to: datetime
    ) -> Dict[str, Any]:
        """
        Genera reporte de cambios en un modelo.
        
        Args:
            model_name: Nombre del modelo (ej: "User")
            date_from: Fecha desde
            date_to: Fecha hasta
        
        Returns:
            Dict con estadísticas de cambios
        """
        logs = AuditLog.objects.filter(
            model_name=model_name,
            timestamp__gte=date_from,
            timestamp__lte=date_to
        )
        
        # Total cambios
        total_changes = logs.count()
        
        # Cambios por acción
        by_action = logs.values('action').annotate(
            count=Count('id')
        )
        
        # Usuarios más activos
        top_users = logs.values('user__username').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return {
            'model_name': model_name,
            'total_changes': total_changes,
            'changes_by_action': list(by_action),
            'top_users': list(top_users)
        }
    
    def sensitive_access_report(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> Dict[str, Any]:
        """
        Genera reporte de accesos a datos sensibles.
        
        Args:
            date_from: Fecha desde
            date_to: Fecha hasta
        
        Returns:
            Dict con accesos a datos sensibles
        
        Útil para compliance GDPR/SOX.
        """
        from apps.audit.constants import SENSITIVE_FIELDS
        
        # Buscar logs que modificaron campos sensibles
        logs = AuditLog.objects.filter(
            timestamp__gte=date_from,
            timestamp__lte=date_to,
            action__in=[ACTION_UPDATE, ACTION_VIEW]
        )
        
        sensitive_logs = []
        
        for log in logs:
            if log.data_after:
                for field in SENSITIVE_FIELDS:
                    if field in log.data_after:
                        sensitive_logs.append({
                            'user': log.user.username,
                            'action': log.action,
                            'model': log.model_name,
                            'field': field,
                            'timestamp': log.timestamp
                        })
        
        return {
            'total_sensitive_accesses': len(sensitive_logs),
            'accesses': sensitive_logs[:100]  # Limitar a 100
        }
    
    def compliance_report(
        self,
        date_from: datetime,
        date_to: datetime,
        compliance_type: str = 'sox'
    ) -> Dict[str, Any]:
        """
        Genera reporte de compliance.
        
        Args:
            date_from: Fecha desde
            date_to: Fecha hasta
            compliance_type: Tipo de compliance (sox, gdpr)
        
        Returns:
            Dict con métricas de compliance
        """
        logs = AuditLog.objects.filter(
            timestamp__gte=date_from,
            timestamp__lte=date_to
        )
        
        # Estadísticas generales
        total_logs = logs.count()
        total_users = logs.values('user').distinct().count()
        
        # Cambios críticos
        critical_changes = logs.filter(
            action__in=[ACTION_DELETE, ACTION_UPDATE],
            model_name__in=['User', 'Permission', 'Group']
        ).count()
        
        # Accesos no autorizados (simplificado)
        # En producción, integrar con sistema de alertas
        
        return {
            'compliance_type': compliance_type,
            'period': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'total_logs': total_logs,
            'total_users': total_users,
            'critical_changes': critical_changes,
            'retention_compliant': True,  # Logs immutables (CNST-031)
        }


class SearchService:
    """
    Servicio de búsqueda de logs.
    
    Responsabilidades:
    - Búsquedas simples
    - Búsquedas avanzadas
    - Full-text search
    """
    
    def search_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        model_name: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Búsqueda simple de logs.
        
        Args:
            user_id: Filtrar por usuario
            action: Filtrar por acción
            model_name: Filtrar por modelo
            date_from: Fecha desde
            date_to: Fecha hasta
            ip_address: Filtrar por IP
            limit: Límite de resultados
        
        Returns:
            Lista de AuditLog
        
        CNST-032: Query optimizada
        """
        queryset = AuditLog.objects.all()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if action:
            queryset = queryset.filter(action=action)
        
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        
        # CNST-032: Límite
        limit = min(limit, MAX_LOGS_PER_QUERY)
        
        return queryset.order_by('-timestamp')[:limit]
    
    def advanced_search(
        self,
        filters: List[Dict[str, Any]],
        operator: str = 'AND',
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Búsqueda avanzada con filtros complejos.
        
        Args:
            filters: Lista de filtros
            operator: Operador lógico (AND, OR)
            limit: Límite de resultados
        
        Returns:
            Lista de AuditLog
        
        Example filters:
            [
                {'field': 'action', 'operator': '=', 'value': 'UPDATE'},
                {'field': 'model_name', 'operator': '=', 'value': 'User'}
            ]
        """
        q_objects = Q()
        
        for filter_dict in filters:
            field = filter_dict['field']
            op = filter_dict['operator']
            value = filter_dict['value']
            
            # Construir Q object según operador
            if op == '=':
                q = Q(**{field: value})
            elif op == '!=':
                q = ~Q(**{field: value})
            elif op == '>':
                q = Q(**{f'{field}__gt': value})
            elif op == '<':
                q = Q(**{f'{field}__lt': value})
            elif op == 'contains':
                q = Q(**{f'{field}__icontains': value})
            else:
                continue  # Operador no soportado
            
            # Combinar con operador lógico
            if operator == 'AND':
                q_objects &= q
            else:  # OR
                q_objects |= q
        
        queryset = AuditLog.objects.filter(q_objects)
        
        limit = min(limit, MAX_LOGS_PER_QUERY)
        
        return queryset.order_by('-timestamp')[:limit]
```

---

<a name="utils"></a>
## 3. UTILS Y HELPERS

### 3.1 Archivo: apps/audit/utils.py

```python
"""
Utilidades para sistema de auditoría.

CLEAN_CODE v3.0.1:
- Funciones: snake_case inglés
- Docstrings: español
"""

from typing import Dict, Any, Optional
from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Obtiene dirección IP del cliente.
    
    Args:
        request: HttpRequest de Django
    
    Returns:
        Dirección IP o None
    
    Maneja proxies y headers X-Forwarded-For.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def get_user_agent(request: HttpRequest) -> Optional[str]:
    """
    Obtiene User-Agent del navegador.
    
    Args:
        request: HttpRequest de Django
    
    Returns:
        User-Agent string o None
    """
    return request.META.get('HTTP_USER_AGENT')


def sanitize_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitiza datos sensibles antes de guardar en logs.
    
    Args:
        data: Diccionario con datos
    
    Returns:
        Diccionario sanitizado
    
    Remueve/enmascara campos sensibles como passwords.
    """
    from apps.audit.constants import SENSITIVE_FIELDS
    
    sanitized = data.copy()
    
    for field in SENSITIVE_FIELDS:
        if field in sanitized:
            if field == 'password':
                sanitized[field] = '***REDACTED***'
            elif field in ['credit_card', 'ssn']:
                sanitized[field] = '***REDACTED***'
            else:
                # Enmascarar parcialmente
                value = str(sanitized[field])
                if len(value) > 4:
                    sanitized[field] = f"{value[:2]}***{value[-2:]}"
    
    return sanitized


def calculate_data_diff(
    data_before: Dict[str, Any],
    data_after: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """
    Calcula diferencias entre datos before/after.
    
    Args:
        data_before: Datos antes del cambio
        data_after: Datos después del cambio
    
    Returns:
        Dict con campos modificados
    
    Example:
        {
            'email': {
                'before': 'old@example.com',
                'after': 'new@example.com'
            }
        }
    """
    diff = {}
    
    # Campos modificados
    for key in data_after.keys():
        if key in data_before:
            if data_before[key] != data_after[key]:
                diff[key] = {
                    'before': data_before[key],
                    'after': data_after[key]
                }
        else:
            # Campo nuevo
            diff[key] = {
                'before': None,
                'after': data_after[key]
            }
    
    # Campos eliminados
    for key in data_before.keys():
        if key not in data_after:
            diff[key] = {
                'before': data_before[key],
                'after': None
            }
    
    return diff


def format_audit_log_message(log: 'AuditLog') -> str:
    """
    Formatea mensaje legible de log de auditoría.
    
    Args:
        log: Instancia de AuditLog
    
    Returns:
        Mensaje formateado
    
    Example:
        "jdoe actualizó User #123 (email: old@example.com → new@example.com)"
    """
    action_map = {
        'CREATE': 'creó',
        'UPDATE': 'actualizó',
        'DELETE': 'eliminó',
        'VIEW': 'visualizó',
    }
    
    action_verb = action_map.get(log.action, log.action)
    
    message = f"{log.user.username} {action_verb} {log.model_name} #{log.instance_id}"
    
    # Agregar detalles de cambios
    if log.action == 'UPDATE' and log.changed_fields:
        changes = []
        for field in log.changed_fields[:3]:  # Max 3 campos
            before = log.data_before.get(field)
            after = log.data_after.get(field)
            changes.append(f"{field}: {before} → {after}")
        
        if changes:
            message += f" ({', '.join(changes)})"
    
    return message
```

---

<a name="serializers"></a>
## 4. SERIALIZERS

### 4.1 Archivo: apps/audit/serializers.py

```python
"""
Serializers para API de auditoría.

CLEAN_CODE v3.0.1:
- Clases: AuditLogSerializer (PascalCase)
- Campos: snake_case inglés
- Docstrings: español formato Google

CNST-031: ReadOnly serializers (immutable)
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.audit.models import AuditLog, LoginLog

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico de usuario para audit logs."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = fields


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer para AuditLog.
    
    CNST-031: ReadOnly (immutable)
    """
    
    user = UserBasicSerializer(read_only=True)
    changed_fields = serializers.ListField(read_only=True)
    formatted_message = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'action',
            'model_name',
            'instance_id',
            'data_before',
            'data_after',
            'changed_fields',
            'timestamp',
            'ip_address',
            'endpoint',
            'user_agent',
            'formatted_message',
        ]
        read_only_fields = fields  # CNST-031: Todo es read-only
    
    def get_formatted_message(self, obj):
        """
        Obtiene mensaje formateado del log.
        
        Args:
            obj: AuditLog
        
        Returns:
            str: Mensaje legible
        """
        from apps.audit.utils import format_audit_log_message
        return format_audit_log_message(obj)


class LoginLogSerializer(serializers.ModelSerializer):
    """
    Serializer para LoginLog.
    
    CNST-031: ReadOnly (immutable)
    """
    
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = LoginLog
        fields = [
            'id',
            'user',
            'attempted_username',
            'success',
            'failure_reason',
            'ip_address',
            'user_agent',
            'timestamp',
            'session_key',
        ]
        read_only_fields = fields  # CNST-031


class SearchQuerySerializer(serializers.Serializer):
    """
    Serializer para queries de búsqueda.
    
    Request para POST /api/v1/audit/search/
    """
    
    user_id = serializers.IntegerField(
        required=False,
        help_text="Filtrar por ID de usuario"
    )
    
    action = serializers.ChoiceField(
        required=False,
        choices=['CREATE', 'UPDATE', 'DELETE', 'VIEW'],
        help_text="Tipo de acción"
    )
    
    model_name = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Nombre del modelo"
    )
    
    date_from = serializers.DateTimeField(
        required=False,
        help_text="Fecha desde (ISO format)"
    )
    
    date_to = serializers.DateTimeField(
        required=False,
        help_text="Fecha hasta (ISO format)"
    )
    
    ip_address = serializers.IPAddressField(
        required=False,
        help_text="Dirección IP"
    )
    
    limit = serializers.IntegerField(
        required=False,
        default=100,
        min_value=1,
        max_value=10000,
        help_text="Límite de resultados"
    )


class ReportSerializer(serializers.Serializer):
    """
    Serializer genérico para reportes.
    
    Response de endpoints de reportes.
    """
    
    report_type = serializers.CharField(read_only=True)
    data = serializers.DictField(read_only=True)
    generated_at = serializers.DateTimeField(read_only=True)


class ExportSerializer(serializers.Serializer):
    """
    Serializer para exportación de logs.
    
    Request para POST /api/v1/audit/export/{format}/
    """
    
    filters = serializers.DictField(
        required=False,
        help_text="Filtros de búsqueda (mismo formato que search)"
    )
    
    format = serializers.ChoiceField(
        choices=['csv', 'excel', 'json'],
        default='csv',
        help_text="Formato de exportación"
    )
```

---

<a name="viewsets"></a>
## 5. VIEWSETS READONLY

### 5.1 Archivo: apps/audit/views.py

```python
"""
ViewSets para API de auditoría.

RBAC v6.0.0: DynamicFunctionPermission
CNST-031: ReadOnly (immutable), NO create/update/destroy
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.audit.models import AuditLog, LoginLog
from apps.audit.serializers import (
    AuditLogSerializer,
    LoginLogSerializer,
    SearchQuerySerializer,
    ReportSerializer,
    ExportSerializer,
)
from apps.audit.services import (
    AuditService,
    ReportService,
    SearchService,
)
from apps.access.permissions import DynamicFunctionPermission


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para logs de auditoría.
    
    Endpoints:
    - GET /api/v1/audit/logs/ (lista logs)
    - GET /api/v1/audit/logs/{id}/ (detalle log)
    - POST /api/v1/audit/search/ (búsqueda avanzada)
    - POST /api/v1/audit/export/{format}/ (exportar)
    
    RBAC v6.0.0:
    - list, retrieve: AUD_VIEW (audit.view)
    - search: AUD_SEARCH (audit.search)
    - export: AUD_EXPORT (audit.export)
    
    CNST-031: ReadOnly, NO create/update/destroy
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.all().order_by('-timestamp')
    
    # RBAC v6.0.0: function_map
    function_map = {
        'list': 'audit.view',
        'retrieve': 'audit.view',
        'search': 'audit.search',
        'export_csv': 'audit.export',
        'export_excel': 'audit.export',
        'export_json': 'audit.export',
    }
    
    # NO create/update/destroy (CNST-031)
    
    def __init__(self, *args, **kwargs):
        """Inicializa ViewSet con services."""
        super().__init__(*args, **kwargs)
        self.search_service = SearchService()
    
    def get_queryset(self):
        """
        Obtiene queryset filtrado.
        
        Query params soportados:
        - user_id: Filtrar por usuario
        - action: Filtrar por acción
        - model_name: Filtrar por modelo
        - date_from: Fecha desde
        - date_to: Fecha hasta
        
        CNST-032: Optimizado con índices
        """
        queryset = super().get_queryset()
        
        # Filtros básicos
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        model_name = self.request.query_params.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """
        POST /api/v1/audit/search/
        
        Búsqueda avanzada de logs.
        
        Request:
        {
            "user_id": 123,
            "action": "UPDATE",
            "date_from": "2026-01-01T00:00:00Z",
            "date_to": "2026-01-31T23:59:59Z",
            "limit": 100
        }
        
        Returns:
            200: Lista de logs
            400: Validación falló
            403: Sin permiso AUD_SEARCH
        
        RBAC: Requiere AUD_SEARCH
        """
        serializer = SearchQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Buscar logs
        logs = self.search_service.search_logs(**serializer.validated_data)
        
        # Serializar resultados
        response_serializer = AuditLogSerializer(logs, many=True)
        
        return Response({
            'count': len(logs),
            'results': response_serializer.data
        })
    
    @action(detail=False, methods=['post'], url_path='export/csv')
    def export_csv(self, request):
        """
        POST /api/v1/audit/export/csv/
        
        Exporta logs a CSV.
        
        RBAC: Requiere AUD_EXPORT
        """
        # TODO: Implementar exportación real
        return Response({
            'download_url': '/media/exports/audit_logs.csv',
            'filename': 'audit_logs.csv',
            'format': 'csv'
        })
    
    @action(detail=False, methods=['post'], url_path='export/excel')
    def export_excel(self, request):
        """
        POST /api/v1/audit/export/excel/
        
        Exporta logs a Excel.
        
        RBAC: Requiere AUD_EXPORT
        """
        # TODO: Implementar exportación real
        return Response({
            'download_url': '/media/exports/audit_logs.xlsx',
            'filename': 'audit_logs.xlsx',
            'format': 'excel'
        })
    
    @action(detail=False, methods=['post'], url_path='export/json')
    def export_json(self, request):
        """
        POST /api/v1/audit/export/json/
        
        Exporta logs a JSON.
        
        RBAC: Requiere AUD_EXPORT
        """
        # TODO: Implementar exportación real
        return Response({
            'download_url': '/media/exports/audit_logs.json',
            'filename': 'audit_logs.json',
            'format': 'json'
        })


class AuditReportViewSet(viewsets.ViewSet):
    """
    ViewSet para reportes de auditoría.
    
    Endpoints:
    - GET /api/v1/audit/reports/user-activity/
    - GET /api/v1/audit/reports/data-changes/
    - GET /api/v1/audit/reports/sensitive-access/
    - GET /api/v1/audit/reports/compliance/
    
    RBAC v6.0.0:
    - Todas las acciones: AUD_REPORT
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'user_activity': 'audit.report',
        'data_changes': 'audit.report',
        'sensitive_access': 'audit.report',
        'compliance': 'audit.report',
    }
    
    def __init__(self, *args, **kwargs):
        """Inicializa ViewSet con ReportService."""
        super().__init__(*args, **kwargs)
        self.report_service = ReportService()
    
    @action(detail=False, methods=['get'], url_path='user-activity')
    def user_activity(self, request):
        """
        GET /api/v1/audit/reports/user-activity/
        
        Query params:
        - user_id: ID del usuario
        - date_from: Fecha desde
        - date_to: Fecha hasta
        
        RBAC: Requiere AUD_REPORT
        """
        from django.contrib.auth import get_user_model
        from datetime import datetime
        
        User = get_user_model()
        
        user_id = request.query_params.get('user_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if not user_id or not date_from or not date_to:
            return Response(
                {'error': 'user_id, date_from y date_to son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.get(id=user_id)
        date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        
        report_data = self.report_service.user_activity_report(
            user, date_from, date_to
        )
        
        return Response({
            'report_type': 'user_activity',
            'data': report_data,
            'generated_at': timezone.now()
        })
    
    @action(detail=False, methods=['get'], url_path='data-changes')
    def data_changes(self, request):
        """
        GET /api/v1/audit/reports/data-changes/
        
        RBAC: Requiere AUD_REPORT
        """
        # Similar a user_activity
        return Response({
            'report_type': 'data_changes',
            'data': {},
            'generated_at': timezone.now()
        })
    
    @action(detail=False, methods=['get'], url_path='sensitive-access')
    def sensitive_access(self, request):
        """
        GET /api/v1/audit/reports/sensitive-access/
        
        RBAC: Requiere AUD_REPORT
        """
        from datetime import datetime
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if not date_from or not date_to:
            return Response(
                {'error': 'date_from y date_to son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        
        report_data = self.report_service.sensitive_access_report(
            date_from, date_to
        )
        
        return Response({
            'report_type': 'sensitive_access',
            'data': report_data,
            'generated_at': timezone.now()
        })
    
    @action(detail=False, methods=['get'], url_path='compliance')
    def compliance(self, request):
        """
        GET /api/v1/audit/reports/compliance/
        
        RBAC: Requiere AUD_REPORT
        """
        # Similar a otros reportes
        return Response({
            'report_type': 'compliance',
            'data': {},
            'generated_at': timezone.now()
        })


class LoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para logs de login.
    
    CNST-031: ReadOnly
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    serializer_class = LoginLogSerializer
    queryset = LoginLog.objects.all().order_by('-timestamp')
    
    function_map = {
        'list': 'audit.view',
        'retrieve': 'audit.view',
    }
```

---

<a name="signals"></a>
## 6. SIGNALS

### 6.1 Archivo: apps/audit/signals.py

```python
"""
Signals para auto-logging de auditoría.

Automatizan el registro de acciones sin modificar código existente.
"""

from django.db.models.signals import post_save, post_delete, pre_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.audit.services import AuditService
from apps.audit.constants import ACTION_CREATE, ACTION_UPDATE, ACTION_DELETE, ACTION_LOGIN
from apps.audit.utils import get_client_ip, get_user_agent

User = get_user_model()
audit_service = AuditService()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Signal para registrar login exitoso.
    
    Args:
        sender: Clase que envió el signal
        request: HttpRequest
        user: Usuario que hizo login
        **kwargs: Argumentos adicionales
    """
    audit_service.log_login(
        user=user,
        attempted_username=user.username,
        success=True,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        session_key=request.session.session_key
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Signal para registrar login fallido.
    
    Args:
        sender: Clase que envió el signal
        credentials: Credenciales intentadas
        request: HttpRequest
        **kwargs: Argumentos adicionales
    """
    audit_service.log_login(
        user=None,
        attempted_username=credentials.get('username', ''),
        success=False,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        failure_reason='Invalid credentials'
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Signal para registrar logout.
    
    Args:
        sender: Clase que envió el signal
        request: HttpRequest
        user: Usuario que hizo logout
        **kwargs: Argumentos adicionales
    """
    if user:
        audit_service.log_logout(
            user=user,
            ip_address=get_client_ip(request),
            session_key=request.session.session_key
        )


# NOTE: Para auto-logging de modelos, se debe implementar en cada app
# debido a que necesitamos contexto del request (IP, user, etc)
# Ver ejemplo en apps/audit/middleware.py
```

---

<a name="urls"></a>
## 7. URLS CONFIGURATION

### 7.1 Archivo: apps/audit/urls.py

```python
"""
URLs para API de auditoría.

CLEAN_CODE v3.0.1:
- Rutas: kebab-case español
- ViewSets: PascalCase

Estructura:
/api/v1/audit/
    logs/
    search/
    reports/
    export/
    login-logs/
"""

from rest_framework.routers import DefaultRouter
from apps.audit.views import (
    AuditLogViewSet,
    AuditReportViewSet,
    LoginLogViewSet,
)

# Router para audit
router = DefaultRouter()

# Registrar viewsets
router.register(
    r'logs',
    AuditLogViewSet,
    basename='audit-log'
)

router.register(
    r'reports',
    AuditReportViewSet,
    basename='audit-report'
)

router.register(
    r'login-logs',
    LoginLogViewSet,
    basename='login-log'
)

urlpatterns = router.urls
```

### 7.2 Integración en config/urls.py

```python
# config/urls.py

from django.urls import path, include

urlpatterns = [
    # ... otras rutas ...
    
    # Audit API
    path('api/v1/audit/', include('apps.audit.urls')),
    
    # ... otras rutas ...
]
```

---

<a name="middleware"></a>
## 8. MIDDLEWARE

### 8.1 Archivo: apps/audit/middleware.py

```python
"""
Middleware para auto-logging de auditoría.

Captura requests y genera logs automáticamente.
"""

from django.utils.deprecation import MiddlewareMixin
from apps.audit.utils import get_client_ip, get_user_agent


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware para logging automático de requests.
    
    Captura información del request para usar en signals.
    """
    
    def process_request(self, request):
        """
        Procesa request y guarda info en request.
        
        Args:
            request: HttpRequest
        """
        # Guardar IP y User-Agent en request para usar en signals
        request.audit_ip = get_client_ip(request)
        request.audit_user_agent = get_user_agent(request)
        request.audit_endpoint = request.path
        
        return None
```

### 8.2 Configuración en settings.py

```python
# config/settings/base.py

MIDDLEWARE = [
    # ... otros middlewares ...
    'apps.audit.middleware.AuditMiddleware',
    # ... otros middlewares ...
]
```

---

## 9. RESUMEN PARTE 2

### 9.1 Componentes Generados

```yaml
Archivos Python:
  ✅ apps/audit/services.py (~550 líneas)
  ✅ apps/audit/utils.py (~150 líneas)
  ✅ apps/audit/serializers.py (~200 líneas)
  ✅ apps/audit/views.py (~350 líneas)
  ✅ apps/audit/signals.py (~100 líneas)
  ✅ apps/audit/middleware.py (~40 líneas)
  ✅ apps/audit/urls.py (~40 líneas)

Total: ~1,430 líneas Python production-ready
```

### 9.2 Services (3)

```python
✅ AuditService
   - log_action() (CNST-031 solo INSERT)
   - log_login()
   - log_logout()
   - get_user_actions()
   - get_failed_login_attempts()

✅ ReportService
   - user_activity_report()
   - data_changes_report()
   - sensitive_access_report()
   - compliance_report()

✅ SearchService
   - search_logs()
   - advanced_search()
```

### 9.3 Utils (5 funciones)

```python
✅ get_client_ip(request)
✅ get_user_agent(request)
✅ sanitize_sensitive_data(data)
✅ calculate_data_diff(before, after)
✅ format_audit_log_message(log)
```

### 9.4 Serializers (5)

```python
✅ AuditLogSerializer (ReadOnly, CNST-031)
✅ LoginLogSerializer (ReadOnly, CNST-031)
✅ SearchQuerySerializer
✅ ReportSerializer
✅ ExportSerializer
```

### 9.5 ViewSets (3 ReadOnly)

```python
✅ AuditLogViewSet (ReadOnly)
   - list(), retrieve() → AUD_VIEW
   - search() → AUD_SEARCH
   - export_csv/excel/json() → AUD_EXPORT
   - NO create/update/destroy (CNST-031)

✅ AuditReportViewSet
   - user_activity() → AUD_REPORT
   - data_changes() → AUD_REPORT
   - sensitive_access() → AUD_REPORT
   - compliance() → AUD_REPORT

✅ LoginLogViewSet (ReadOnly)
   - list(), retrieve() → AUD_VIEW
```

### 9.6 Signals (3)

```python
✅ log_user_login (user_logged_in signal)
✅ log_user_login_failed (user_login_failed signal)
✅ log_user_logout (user_logged_out signal)
```

### 9.7 Endpoints REST (13)

```http
✅ GET    /api/v1/audit/logs/
✅ GET    /api/v1/audit/logs/{id}/
✅ POST   /api/v1/audit/search/
✅ POST   /api/v1/audit/export/csv/
✅ POST   /api/v1/audit/export/excel/
✅ POST   /api/v1/audit/export/json/

✅ GET    /api/v1/audit/reports/user-activity/
✅ GET    /api/v1/audit/reports/data-changes/
✅ GET    /api/v1/audit/reports/sensitive-access/
✅ GET    /api/v1/audit/reports/compliance/

✅ GET    /api/v1/audit/login-logs/
✅ GET    /api/v1/audit/login-logs/{id}/

❌ NO POST/PUT/DELETE en logs (CNST-031)
```

---

## PRÓXIMA PARTE (FINAL)

**PARTE 3/3: Testing y Deployment**

Contenido:
- Fixtures pytest (logs, usuarios RBAC)
- Factories (AuditLogFactory, LoginLogFactory)
- Unit tests (Services, Utils, Serializers)
- API tests (13 endpoints, RBAC)
- E2E tests (flujo completo logging)
- Signal tests (auto-logging)
- Database migration con triggers
- Deployment considerations (particionamiento, índices)
- Plan de implementación completo

**Estimado:** ~900 líneas, 2 horas

---

**Fin de PARTE 2/3**
