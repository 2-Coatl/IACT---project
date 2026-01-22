---
version: 3.0.0
date: 2026-01-19
project: IACT Call Center System
type: Análisis de Arquitectura - App Alerts PARTE 1/3
categoria: arquitectura/apps
tema: apps/alerts/ - Fundamentos y Arquitectura
autor: Claude Technical Analysis
tags: [alerts, internal-messaging, cnst-001, rbac, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
  - MODELO_RBAC_IACT_v6_0_0.md (2 partes)
  - ARQUITECTURA_ETL_v3_0_0.md (3 partes)
estado: definitivo
parte: 1 de 3
relacionado:
  - ANALISIS_APP_ALERTS_v3_0_0_PARTE_2.md
  - ANALISIS_APP_ALERTS_v3_0_0_PARTE_3.md
replaces: []
---

# ANÁLISIS DE apps/alerts/ v3.0.0 - PARTE 1/3
## FUNDAMENTOS Y ARQUITECTURA

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen)
2. [Propósito y Responsabilidades](#proposito)
3. [CLEAN_CODE v3.0.1 Aplicado](#clean-code)
4. [RESTRICCIONES v1.0.0 Aplicadas](#restricciones)
5. [RBAC v6.0.0 - MOD_Alerts](#rbac)
6. [Arquitectura de la App](#arquitectura)
7. [Modelos Django](#modelos)
8. [Constants y Configuración](#constants)

---

<a name="resumen"></a>
## 1. RESUMEN EJECUTIVO

### 1.1 Overview

```yaml
App: apps/alerts/
Versión: 3.0.0
Tipo: App SIMPLE (3 partes)
Estado: CRÍTICA - CNST-001
Complejidad: Baja-Media
Líneas estimadas: ~2,400 líneas
Tamaño estimado: ~85KB
Tiempo estimado: 5.5 horas

Propósito:
  Sistema de alertas y notificaciones internas
  Buzón de mensajes entre usuarios (NO email externo)
  Gestión de suscripciones a alertas automáticas
  Configuración de reglas de alertas
```

### 1.2 Restricción CRÍTICA: CNST-001

```yaml
CNST-001: NO Email Externo
  Descripción: Sistema NO puede enviar emails externos
  Razón: Seguridad, control de comunicaciones
  Solución: Buzón interno de mensajes
  Impacto: 🔴 CRÍTICO
  
  Implementación:
    ✅ InternalMessage (buzón interno)
    ✅ AlertConfiguration (reglas de alertas)
    ✅ AlertSubscription (suscripciones usuarios)
    ❌ NO SMTP, NO email libraries
    ❌ NO notificaciones externas
    ❌ NO webhooks externos
```

### 1.3 RESTRICCIONES Adicionales

```yaml
CNST-024: Límites de Alertas
  - Máximo 50 destinatarios por mensaje
  - Retención mensajes: 90 días
  - Auto-archivado después de 90 días
  - Límite adjuntos: 5MB por mensaje

CNST-026: Prioridades de Alertas
  - 4 niveles: info, warning, error, critical
  - SLA respuesta según prioridad
  - No implementado: push notifications
```

### 1.4 RBAC v6.0.0

```yaml
Módulo: MOD_Alerts
Funciones: 6 (todas activas)

ALR_VIEW:    alerts.view           (Ver alertas recibidas)
ALR_SEND:    alerts.send           (Enviar mensajes internos)
ALR_CONF:    alerts.configure      (Configurar reglas alertas)
ALR_SUBS:    alerts.subscribe      (Gestionar suscripciones)
ALR_MARK:    alerts.mark           (Marcar leído/no leído)
ALR_DELETE:  alerts.delete         (Eliminar mensajes propios)
```

---

<a name="proposito"></a>
## 2. PROPÓSITO Y RESPONSABILIDADES

### 2.1 Propósito Principal

**Sistema de mensajería y alertas internas** para comunicación entre usuarios del sistema sin depender de email externo.

### 2.2 Responsabilidades

```yaml
Responsabilidades Principales:
  1. Buzón de mensajes internos (CNST-001)
     - Enviar mensajes entre usuarios
     - Recibir notificaciones del sistema
     - Gestionar bandeja de entrada/salida
  
  2. Alertas automáticas
     - Configurar reglas de alertas
     - Suscribirse a eventos del sistema
     - Notificaciones automáticas (internas)
  
  3. Gestión de mensajes
     - Marcar leído/no leído
     - Archivar mensajes
     - Eliminar mensajes propios
     - Auto-archivado 90 días (CNST-024)
  
  4. Configuración de alertas
     - Reglas por tipo de evento
     - Filtros por servicio/centro
     - Prioridades (info/warning/error/critical)

Responsabilidades Secundarias:
  - Búsqueda de mensajes
  - Estadísticas de alertas
  - Auditoría de notificaciones
```

### 2.3 NO Responsabilidades

```yaml
❌ NO es responsable de:
  - Enviar emails externos (CNST-001)
  - Notificaciones push móviles
  - Webhooks externos
  - Integraciones con servicios de mensajería externos
  - SMS o notificaciones telefónicas
  - Calendario de eventos
```

### 2.4 Separación de Responsabilidades

```yaml
apps/alerts/:
  - Mensajería interna
  - Alertas configurables
  - Suscripciones usuarios

apps/audit/:
  - Auditoría de acciones
  - Logs immutables
  - Trazabilidad

apps/users/:
  - Gestión usuarios
  - Perfiles
  - Autenticación

apps/authentication/:
  - Login/Logout
  - Sesiones
  - Password reset
```

---

<a name="clean-code"></a>
## 3. CLEAN_CODE v3.0.1 APLICADO

### 3.1 Nomenclatura Código

```python
# CLEAN_CODE v3.0.1: Código en INGLÉS

# Clases (PascalCase)
class InternalMessage(models.Model):
    """Mensaje interno del buzón."""
    pass

class AlertConfiguration(models.Model):
    """Configuración de alerta automática."""
    pass

class AlertService:
    """Servicio de gestión de alertas."""
    pass

# Métodos y funciones (snake_case)
def send_internal_message(sender, recipients, subject, body):
    """Envía mensaje interno a destinatarios."""
    pass

def get_unread_messages(user):
    """Obtiene mensajes no leídos de usuario."""
    pass

def mark_as_read(message_id, user):
    """Marca mensaje como leído."""
    pass

# Variables (snake_case)
message_count = 0
unread_messages = []
recipient_list = [user1, user2]

# Constantes (UPPER_SNAKE_CASE)
MAX_RECIPIENTS = 50
MESSAGE_RETENTION_DAYS = 90
MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024  # 5MB
```

### 3.2 Nomenclatura Base de Datos (Húngaro Preservado)

```python
# Modelos Django: Nombres en inglés
class InternalMessage(models.Model):
    
    # Campos: Nombres en inglés
    sender = models.ForeignKey(...)
    recipients = models.ManyToManyField(...)
    subject = models.CharField(...)
    
    # db_column: Húngaro preservado (legacy)
    id = models.AutoField(
        db_column='iIdMensaje',
        primary_key=True
    )
    
    subject = models.CharField(
        db_column='cAsunto',
        max_length=200
    )
    
    body = models.TextField(
        db_column='tCuerpo'
    )
    
    priority = models.CharField(
        db_column='cPrioridad',
        max_length=20
    )
    
    is_read = models.BooleanField(
        db_column='bLeido',
        default=False
    )
    
    sent_at = models.DateTimeField(
        db_column='dFechaEnvio',
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'tbl_mensaje_interno'
```

### 3.3 Docstrings en Español

```python
"""
Service layer para gestión de alertas.

Responsabilidades:
- Enviar mensajes internos entre usuarios
- Configurar reglas de alertas automáticas
- Gestionar suscripciones a eventos
- Auto-archivado de mensajes (90 días)

CLEAN_CODE v3.0.1:
- Código: inglés PascalCase/snake_case
- Docstrings: español formato Google
- db_column: húngaro preservado

CNST-001: NO email externo, solo buzón interno
CNST-024: Máx 50 destinatarios, retención 90 días
"""

class AlertService:
    """
    Servicio principal de alertas.
    
    Responsabilidades:
    - Envío de mensajes internos
    - Gestión de alertas automáticas
    - Validación de límites (CNST-024)
    
    Atributos:
        max_recipients (int): Máximo destinatarios permitidos
        retention_days (int): Días de retención de mensajes
    """
    
    def __init__(self):
        """Inicializa el servicio de alertas."""
        self.max_recipients = MAX_RECIPIENTS
        self.retention_days = MESSAGE_RETENTION_DAYS
    
    def send_message(
        self,
        sender: User,
        recipients: List[User],
        subject: str,
        body: str,
        priority: str = 'info'
    ) -> InternalMessage:
        """
        Envía mensaje interno a destinatarios.
        
        Args:
            sender: Usuario que envía el mensaje
            recipients: Lista de usuarios destinatarios
            subject: Asunto del mensaje
            body: Cuerpo del mensaje
            priority: Prioridad (info, warning, error, critical)
        
        Returns:
            InternalMessage: Mensaje creado
        
        Raises:
            ValidationError: Si excede límite de destinatarios
            ValidationError: Si sender no tiene permiso ALR_SEND
        
        CNST-001: NO usa email, solo buzón interno
        CNST-024: Valida máximo 50 destinatarios
        """
        # Implementación...
        pass
```

---

<a name="restricciones"></a>
## 4. RESTRICCIONES v1.0.0 APLICADAS

### 4.1 CNST-001: NO Email Externo (🔴 CRÍTICO)

```yaml
Restricción: NO envío de emails externos
Categoría: Seguridad y Control
Impacto: CRÍTICO
Estado: Activo

Descripción:
  El sistema NO puede enviar emails a direcciones externas.
  Toda comunicación debe ser interna al sistema.

Razones:
  - Seguridad: Control total de comunicaciones
  - Compliance: No filtración de datos sensibles
  - Gestión: Centralización de notificaciones
  - Auditoría: Trazabilidad completa

Implementación:
  ✅ InternalMessage: Buzón interno de mensajes
  ✅ AlertConfiguration: Alertas solo internas
  ✅ NO SMTP libraries (smtplib, django.core.mail)
  ✅ NO servicios externos (SendGrid, Mailgun, etc)
  ✅ NO webhooks externos

Alternativa:
  - Buzón de mensajes internos
  - Notificaciones in-app
  - Panel de alertas en dashboard

Testing:
  - Verificar NO imports de email libraries
  - Verificar NO llamadas SMTP
  - Verificar mensajes solo en BD interna

Migración futura:
  - Si se habilita email: módulo separado con aprobación
  - Gateway de email controlado
  - Lista blanca de dominios
```

### 4.2 CNST-024: Límites de Alertas

```yaml
Restricción: Límites en mensajería interna
Categoría: Performance y Seguridad
Impacto: Medio
Estado: Activo

Límites:
  1. Destinatarios:
     - Máximo 50 destinatarios por mensaje
     - Validación en creación de mensaje
     - Error si se excede
  
  2. Retención:
     - Mensajes guardados 90 días
     - Auto-archivado después de 90 días
     - Archivados no eliminados (solo ocultos)
  
  3. Adjuntos:
     - Máximo 5MB por mensaje
     - Formatos permitidos: pdf, doc, docx, xls, xlsx, txt
     - NO imágenes (seguridad)
  
  4. Rate Limiting:
     - Máximo 100 mensajes/hora por usuario
     - Previene spam interno

Implementación:
  ✅ Validación en AlertService.send_message()
  ✅ Cronjob auto-archivado (ejecuta diario 3 AM)
  ✅ Validación tamaño adjuntos
  ✅ Rate limiting con decorador

Testing:
  - Test envío 50 destinatarios: OK
  - Test envío 51 destinatarios: ValidationError
  - Test auto-archivado >90 días
  - Test adjunto 6MB: ValidationError
```

### 4.3 CNST-026: Prioridades de Alertas

```yaml
Restricción: Sistema de prioridades
Categoría: Operacional
Impacto: Medio
Estado: Activo

Prioridades:
  1. info (azul):
     - Mensajes informativos
     - No requiere acción inmediata
     - 90% de mensajes
  
  2. warning (amarillo):
     - Advertencias
     - Revisar en 24h
     - 8% de mensajes
  
  3. error (naranja):
     - Errores que requieren atención
     - Revisar en 4h
     - 1.5% de mensajes
  
  4. critical (rojo):
     - Errores críticos
     - Acción inmediata
     - 0.5% de mensajes

SLA Respuesta (no enforced, solo sugerido):
  - critical: <1h
  - error: <4h
  - warning: <24h
  - info: sin SLA

Implementación:
  ✅ Campo priority en InternalMessage
  ✅ Colores en UI según prioridad
  ✅ Filtros por prioridad
  ✅ Estadísticas por prioridad

No Implementado:
  ❌ Push notifications (fuera de alcance)
  ❌ Escalamiento automático
  ❌ Enforcement de SLA
```

### 4.4 Otras RESTRICCIONES Aplicables

```yaml
CNST-010: Cache LocMem
  - Aplicable: NO (alerts es transaccional)
  - Razón: Mensajes deben ser real-time
  - Cache solo para estadísticas agregadas

CNST-025: Timeout 90s
  - Aplicable: SÍ
  - Endpoints deben responder <90s
  - Envío masivo (50 destinatarios) optimizado

CNST-031: Auditoría Immutable
  - Aplicable: PARCIAL
  - Mensajes eliminados se marcan deleted=True
  - NO se eliminan físicamente (auditoría)
  - Integración con apps/audit/
```

---

<a name="rbac"></a>
## 5. RBAC v6.0.0 - MOD_Alerts

### 5.1 Módulo MOD_Alerts

```yaml
Código: MOD_Alerts
Nombre: Módulo de Alertas
Descripción: Gestión de mensajería interna y alertas automáticas
Estado: Activo
Funciones: 6 (todas activas)
Grupos asociados: GRP_UserBasic, GRP_Supervisor, GRP_Admin
```

### 5.2 Funciones RBAC (6 Activas)

#### 5.2.1 ALR_VIEW

```yaml
Código: ALR_VIEW
Nombre: Ver Alertas
Descripción: Permite ver alertas recibidas en bandeja de entrada
Permission Django: alerts.view
Estado: Activo
Asignación típica:
  - GRP_UserBasic (todos los usuarios)
  - GRP_Supervisor
  - GRP_Admin

Permite:
  - GET /api/v1/alerts/ (lista mensajes recibidos)
  - GET /api/v1/alerts/{id}/ (detalle mensaje)
  - Filtrar por leído/no leído
  - Filtrar por prioridad
  - Búsqueda en mensajes

No permite:
  - Ver mensajes de otros usuarios
  - Enviar mensajes
  - Configurar alertas
```

#### 5.2.2 ALR_SEND

```yaml
Código: ALR_SEND
Nombre: Enviar Mensajes
Descripción: Permite enviar mensajes internos a otros usuarios
Permission Django: alerts.send
Estado: Activo
Asignación típica:
  - GRP_Supervisor
  - GRP_Admin

Permite:
  - POST /api/v1/alerts/send/ (enviar mensaje)
  - Seleccionar destinatarios (máx 50)
  - Adjuntar archivos (máx 5MB)
  - Establecer prioridad

Validaciones:
  - Máximo 50 destinatarios (CNST-024)
  - Rate limit 100 msg/hora
  - Validación adjuntos

No permite:
  - Enviar como otro usuario (spoofing)
  - Modificar mensajes enviados
```

#### 5.2.3 ALR_CONF

```yaml
Código: ALR_CONF
Nombre: Configurar Alertas
Descripción: Permite configurar reglas de alertas automáticas
Permission Django: alerts.configure
Estado: Activo
Asignación típica:
  - GRP_Supervisor
  - GRP_Admin

Permite:
  - POST /api/v1/alerts/configurations/ (crear regla)
  - PUT /api/v1/alerts/configurations/{id}/ (editar regla)
  - DELETE /api/v1/alerts/configurations/{id}/ (eliminar regla)
  - Configurar triggers (eventos del sistema)
  - Configurar destinatarios automáticos

Ejemplos reglas:
  - "Cuando llamadas abandonadas > 100/día → notificar supervisor"
  - "Cuando nivel servicio < 80% → notificar gerente"
  - "Cuando error ETL → notificar admin"

No permite:
  - Configurar envío email externo (CNST-001)
  - Webhooks externos
```

#### 5.2.4 ALR_SUBS

```yaml
Código: ALR_SUBS
Nombre: Gestionar Suscripciones
Descripción: Permite suscribirse/desuscribirse a alertas automáticas
Permission Django: alerts.subscribe
Estado: Activo
Asignación típica:
  - GRP_UserBasic (todos)
  - GRP_Supervisor
  - GRP_Admin

Permite:
  - GET /api/v1/alerts/subscriptions/ (ver suscripciones)
  - POST /api/v1/alerts/subscriptions/ (suscribirse)
  - DELETE /api/v1/alerts/subscriptions/{id}/ (desuscribirse)
  - Configurar frecuencia (inmediato, diario, semanal)

Ejemplos suscripciones:
  - Suscribirse a "Reporte diario de llamadas"
  - Suscribirse a "Alertas críticas del sistema"
  - Desuscribirse de "Resumen semanal"

No permite:
  - Suscribir a otros usuarios
  - Modificar configuraciones globales
```

#### 5.2.5 ALR_MARK

```yaml
Código: ALR_MARK
Nombre: Marcar Mensajes
Descripción: Permite marcar mensajes como leído/no leído
Permission Django: alerts.mark
Estado: Activo
Asignación típica:
  - GRP_UserBasic (todos)
  - GRP_Supervisor
  - GRP_Admin

Permite:
  - PATCH /api/v1/alerts/{id}/mark-read/ (marcar leído)
  - PATCH /api/v1/alerts/{id}/mark-unread/ (marcar no leído)
  - Marcar múltiples mensajes (bulk action)
  - Archivar mensajes manualmente

No permite:
  - Marcar mensajes de otros usuarios
  - Modificar contenido de mensajes
```

#### 5.2.6 ALR_DELETE

```yaml
Código: ALR_DELETE
Nombre: Eliminar Mensajes
Descripción: Permite eliminar mensajes propios (soft delete)
Permission Django: alerts.delete
Estado: Activo
Asignación típica:
  - GRP_UserBasic (todos)
  - GRP_Supervisor
  - GRP_Admin

Permite:
  - DELETE /api/v1/alerts/{id}/ (eliminar mensaje)
  - Solo mensajes propios (recibidos)
  - Soft delete (deleted=True, no físico)
  - Bulk delete (múltiples mensajes)

Validaciones:
  - Solo mensajes donde user es destinatario
  - NO elimina de sender (auditoría)
  - Eliminación permanente después de 90 días (CNST-024)

No permite:
  - Eliminar mensajes de otros usuarios
  - Eliminar mensajes enviados propios (auditoría)
  - Hard delete (físico)
```

### 5.3 function_map en ViewSets

```python
# apps/alerts/views.py

class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de alertas.
    
    RBAC v6.0.0: DynamicFunctionPermission
    """
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    # function_map para RBAC
    function_map = {
        'list': 'alerts.view',              # ALR_VIEW
        'retrieve': 'alerts.view',          # ALR_VIEW
        'send_message': 'alerts.send',      # ALR_SEND
        'mark_read': 'alerts.mark',         # ALR_MARK
        'mark_unread': 'alerts.mark',       # ALR_MARK
        'destroy': 'alerts.delete',         # ALR_DELETE
    }


class AlertConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet para configuración de alertas."""
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'list': 'alerts.view',              # ALR_VIEW
        'retrieve': 'alerts.view',          # ALR_VIEW
        'create': 'alerts.configure',       # ALR_CONF
        'update': 'alerts.configure',       # ALR_CONF
        'partial_update': 'alerts.configure', # ALR_CONF
        'destroy': 'alerts.configure',      # ALR_CONF
    }


class AlertSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet para suscripciones a alertas."""
    
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'list': 'alerts.subscribe',         # ALR_SUBS
        'retrieve': 'alerts.subscribe',     # ALR_SUBS
        'create': 'alerts.subscribe',       # ALR_SUBS
        'destroy': 'alerts.subscribe',      # ALR_SUBS
    }
```

### 5.4 Grupos y Asignaciones

```yaml
GRP_UserBasic:
  Funciones asignadas:
    - ALR_VIEW (ver mensajes propios)
    - ALR_MARK (marcar leído/no leído)
    - ALR_DELETE (eliminar propios)
    - ALR_SUBS (gestionar suscripciones)

GRP_Supervisor:
  Funciones asignadas:
    - Todas de GRP_UserBasic +
    - ALR_SEND (enviar mensajes a equipo)
    - ALR_CONF (configurar alertas de equipo)

GRP_Admin:
  Funciones asignadas:
    - Todas de GRP_Supervisor +
    - ALR_CONF (configurar alertas globales)
    - Gestión avanzada de configuraciones
```

---

<a name="arquitectura"></a>
## 6. ARQUITECTURA DE LA APP

### 6.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    apps/alerts/                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐    │
│  │              API Layer (REST)                  │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - AlertViewSet                                │    │
│  │  - AlertConfigurationViewSet                   │    │
│  │  - AlertSubscriptionViewSet                    │    │
│  │  - RBAC: DynamicFunctionPermission             │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │           Service Layer                        │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - AlertService                                │    │
│  │    * send_message()                            │    │
│  │    * get_unread_messages()                     │    │
│  │    * mark_as_read()                            │    │
│  │    * auto_archive_old_messages()               │    │
│  │  - ConfigurationService                        │    │
│  │    * create_alert_rule()                       │    │
│  │    * trigger_alert()                           │    │
│  │  - SubscriptionService                         │    │
│  │    * subscribe_user()                          │    │
│  │    * get_subscriptions()                       │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │            Data Layer (Models)                 │    │
│  ├────────────────────────────────────────────────┤    │
│  │  - InternalMessage                             │    │
│  │  - MessageRecipient (M2M)                      │    │
│  │  - AlertConfiguration                          │    │
│  │  - AlertSubscription                           │    │
│  │  - AlertLog (auditoría)                        │    │
│  └────────────────────────────────────────────────┘    │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │              Database (PostgreSQL)             │    │
│  │  - tbl_mensaje_interno                         │    │
│  │  - tbl_mensaje_destinatario                    │    │
│  │  - tbl_alerta_configuracion                    │    │
│  │  - tbl_alerta_suscripcion                      │    │
│  │  - tbl_alerta_log                              │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘

Integraciones:
  ┌─────────────────┐
  │  apps/users/    │ → User model (sender, recipients)
  └─────────────────┘
  
  ┌─────────────────┐
  │  apps/access/   │ → RBAC validation (6 funciones)
  └─────────────────┘
  
  ┌─────────────────┐
  │  apps/audit/    │ → Auditoría de mensajes enviados
  └─────────────────┘
```

### 6.2 Flujos Principales

#### 6.2.1 Flujo: Enviar Mensaje Interno

```
Usuario → POST /api/v1/alerts/send/
   ↓
DynamicFunctionPermission verifica ALR_SEND
   ↓
AlertService.send_message()
   ↓
Validaciones:
   - Máximo 50 destinatarios (CNST-024)
   - Rate limit 100 msg/hora
   - Adjuntos <5MB
   ↓
Crear InternalMessage
   ↓
Crear MessageRecipient para cada destinatario
   ↓
AlertLog (auditoría)
   ↓
Response 201 Created

CNST-001: NO email externo enviado ✅
```

#### 6.2.2 Flujo: Alerta Automática

```
Evento del Sistema (ej: llamadas_abandonadas > 100)
   ↓
AlertConfiguration.check_trigger()
   ↓
ConfigurationService.trigger_alert()
   ↓
Buscar AlertSubscription activas
   ↓
Para cada suscriptor:
   AlertService.send_message()
   ↓
Crear InternalMessage (sender=System)
   ↓
AlertLog (auditoría)

CNST-001: NO email externo ✅
```

#### 6.2.3 Flujo: Auto-Archivado (90 días)

```
Cronjob diario (3 AM)
   ↓
python manage.py auto_archive_messages
   ↓
AlertService.auto_archive_old_messages()
   ↓
SELECT mensajes WHERE sent_at < NOW() - 90 days
   ↓
UPDATE mensajes SET archived=True
   ↓
AlertLog (auditoría archivado)

CNST-024: Retención 90 días ✅
```

---

<a name="modelos"></a>
## 7. MODELOS DJANGO

### 7.1 InternalMessage

```python
"""
Modelo principal de mensajes internos.

CLEAN_CODE v3.0.1:
- Nombre clase: InternalMessage (inglés PascalCase)
- Campos: sender, recipients, subject (inglés snake_case)
- db_column: cAsunto, tCuerpo (húngaro preservado)
- db_table: tbl_mensaje_interno (húngaro preservado)

CNST-001: Buzón interno, NO email
CNST-024: Retención 90 días, auto-archivado
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.alerts.constants import (
    PRIORITY_CHOICES,
    MAX_RECIPIENTS,
    MESSAGE_RETENTION_DAYS,
)

User = get_user_model()


class InternalMessage(models.Model):
    """
    Mensaje interno del buzón.
    
    Permite comunicación entre usuarios sin email externo (CNST-001).
    
    Campos:
    - sender: Usuario que envía el mensaje
    - recipients: Usuarios destinatarios (M2M)
    - subject: Asunto del mensaje
    - body: Cuerpo del mensaje (texto o HTML)
    - priority: Prioridad (info, warning, error, critical)
    - sent_at: Fecha/hora de envío
    - archived: Si está archivado (>90 días)
    - deleted: Soft delete (auditoría)
    
    Relaciones:
    - sender: FK a User
    - recipients: M2M a User (through MessageRecipient)
    
    Validaciones:
    - Máximo 50 destinatarios (CNST-024)
    - Prioridad válida
    - Subject no vacío
    """
    
    id = models.AutoField(
        db_column='iIdMensaje',
        primary_key=True
    )
    
    sender = models.ForeignKey(
        User,
        db_column='iIdRemitente',
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="Usuario que envía el mensaje"
    )
    
    subject = models.CharField(
        db_column='cAsunto',
        max_length=200,
        help_text="Asunto del mensaje"
    )
    
    body = models.TextField(
        db_column='tCuerpo',
        help_text="Cuerpo del mensaje (texto o HTML)"
    )
    
    priority = models.CharField(
        db_column='cPrioridad',
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='info',
        help_text="Prioridad: info, warning, error, critical"
    )
    
    sent_at = models.DateTimeField(
        db_column='dFechaEnvio',
        auto_now_add=True,
        help_text="Fecha y hora de envío"
    )
    
    archived = models.BooleanField(
        db_column='bArchivado',
        default=False,
        help_text="Si está archivado (>90 días)"
    )
    
    deleted = models.BooleanField(
        db_column='bEliminado',
        default=False,
        help_text="Soft delete para auditoría"
    )
    
    created_at = models.DateTimeField(
        db_column='dFechaCreacion',
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        db_column='dFechaActualizacion',
        auto_now=True
    )
    
    class Meta:
        db_table = 'tbl_mensaje_interno'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['sender', 'sent_at']),
            models.Index(fields=['priority', 'sent_at']),
            models.Index(fields=['archived', 'deleted']),
        ]
        verbose_name = 'Mensaje Interno'
        verbose_name_plural = 'Mensajes Internos'
    
    def __str__(self):
        return f"{self.subject} (de {self.sender.username})"
    
    def clean(self):
        """
        Validaciones personalizadas.
        
        Valida:
        - Subject no vacío
        - Priority válida
        
        Raises:
            ValidationError: Si validación falla
        """
        if not self.subject or self.subject.strip() == '':
            raise ValidationError("Subject no puede estar vacío")
        
        if self.priority not in dict(PRIORITY_CHOICES):
            raise ValidationError(f"Priority inválida: {self.priority}")
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar clean()."""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def is_archived(self):
        """Verifica si mensaje debe estar archivado (>90 días)."""
        from django.utils import timezone
        from datetime import timedelta
        
        age = timezone.now() - self.sent_at
        return age.days > MESSAGE_RETENTION_DAYS
    
    @property
    def recipient_count(self):
        """Cuenta destinatarios del mensaje."""
        return self.message_recipients.count()
```

### 7.2 MessageRecipient

```python
class MessageRecipient(models.Model):
    """
    Tabla intermedia para relación M2M InternalMessage - User.
    
    Permite tracking individual por destinatario:
    - is_read: Si el destinatario leyó el mensaje
    - read_at: Cuándo lo leyó
    - deleted_by_recipient: Si el destinatario lo eliminó
    
    Through table para InternalMessage.recipients
    """
    
    id = models.AutoField(
        db_column='iIdDestinatario',
        primary_key=True
    )
    
    message = models.ForeignKey(
        InternalMessage,
        db_column='iIdMensaje',
        on_delete=models.CASCADE,
        related_name='message_recipients'
    )
    
    recipient = models.ForeignKey(
        User,
        db_column='iIdUsuario',
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    
    is_read = models.BooleanField(
        db_column='bLeido',
        default=False,
        help_text="Si el destinatario leyó el mensaje"
    )
    
    read_at = models.DateTimeField(
        db_column='dFechaLectura',
        null=True,
        blank=True,
        help_text="Fecha y hora de lectura"
    )
    
    deleted_by_recipient = models.BooleanField(
        db_column='bEliminadoPorDestinatario',
        default=False,
        help_text="Si el destinatario eliminó el mensaje (soft delete)"
    )
    
    created_at = models.DateTimeField(
        db_column='dFechaCreacion',
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'tbl_mensaje_destinatario'
        unique_together = [['message', 'recipient']]
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'deleted_by_recipient']),
        ]
        verbose_name = 'Destinatario de Mensaje'
        verbose_name_plural = 'Destinatarios de Mensajes'
    
    def __str__(self):
        status = "leído" if self.is_read else "no leído"
        return f"{self.message.subject} → {self.recipient.username} ({status})"
    
    def mark_as_read(self):
        """Marca mensaje como leído y registra timestamp."""
        from django.utils import timezone
        
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
```

### 7.3 AlertConfiguration

```python
class AlertConfiguration(models.Model):
    """
    Configuración de alerta automática.
    
    Permite definir reglas de alertas que se disparan automáticamente
    cuando ocurren eventos específicos en el sistema.
    
    Ejemplo:
    - Trigger: "llamadas_abandonadas > 100"
    - Action: Enviar mensaje a supervisor
    - Frecuencia: Diaria
    
    CNST-001: Alertas solo internas, NO email
    """
    
    id = models.AutoField(
        db_column='iIdConfiguracion',
        primary_key=True
    )
    
    name = models.CharField(
        db_column='cNombre',
        max_length=200,
        help_text="Nombre descriptivo de la alerta"
    )
    
    description = models.TextField(
        db_column='tDescripcion',
        blank=True,
        help_text="Descripción detallada"
    )
    
    trigger_type = models.CharField(
        db_column='cTipoTrigger',
        max_length=50,
        help_text="Tipo de evento: threshold, schedule, manual"
    )
    
    trigger_config = models.JSONField(
        db_column='jConfigTrigger',
        help_text="Configuración del trigger en JSON"
    )
    
    message_template = models.TextField(
        db_column='tPlantillaMensaje',
        help_text="Plantilla del mensaje a enviar"
    )
    
    priority = models.CharField(
        db_column='cPrioridad',
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='warning'
    )
    
    is_active = models.BooleanField(
        db_column='bActivo',
        default=True,
        help_text="Si la alerta está activa"
    )
    
    created_by = models.ForeignKey(
        User,
        db_column='iIdCreador',
        on_delete=models.CASCADE,
        related_name='created_alert_configs'
    )
    
    created_at = models.DateTimeField(
        db_column='dFechaCreacion',
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        db_column='dFechaActualizacion',
        auto_now=True
    )
    
    class Meta:
        db_table = 'tbl_alerta_configuracion'
        ordering = ['-created_at']
        verbose_name = 'Configuración de Alerta'
        verbose_name_plural = 'Configuraciones de Alertas'
    
    def __str__(self):
        status = "Activa" if self.is_active else "Inactiva"
        return f"{self.name} ({status})"
```

### 7.4 AlertSubscription

```python
class AlertSubscription(models.Model):
    """
    Suscripción de usuario a alerta automática.
    
    Permite a usuarios suscribirse/desuscribirse de alertas configuradas.
    
    Campos:
    - user: Usuario suscrito
    - alert_config: Configuración de alerta
    - frequency: Frecuencia (immediate, daily, weekly)
    - is_active: Si la suscripción está activa
    """
    
    id = models.AutoField(
        db_column='iIdSuscripcion',
        primary_key=True
    )
    
    user = models.ForeignKey(
        User,
        db_column='iIdUsuario',
        on_delete=models.CASCADE,
        related_name='alert_subscriptions'
    )
    
    alert_config = models.ForeignKey(
        AlertConfiguration,
        db_column='iIdConfiguracion',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    
    frequency = models.CharField(
        db_column='cFrecuencia',
        max_length=20,
        choices=[
            ('immediate', 'Inmediato'),
            ('daily', 'Diario'),
            ('weekly', 'Semanal'),
        ],
        default='immediate',
        help_text="Frecuencia de notificaciones"
    )
    
    is_active = models.BooleanField(
        db_column='bActivo',
        default=True,
        help_text="Si la suscripción está activa"
    )
    
    subscribed_at = models.DateTimeField(
        db_column='dFechaSuscripcion',
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'tbl_alerta_suscripcion'
        unique_together = [['user', 'alert_config']]
        ordering = ['-subscribed_at']
        verbose_name = 'Suscripción de Alerta'
        verbose_name_plural = 'Suscripciones de Alertas'
    
    def __str__(self):
        return f"{self.user.username} → {self.alert_config.name}"
```

---

<a name="constants"></a>
## 8. CONSTANTS Y CONFIGURACIÓN

### 8.1 Archivo: apps/alerts/constants.py

```python
"""
Constantes para sistema de alertas.

CLEAN_CODE v3.0.1:
- Constantes: UPPER_SNAKE_CASE inglés
- Docstrings: español

CNST-001: NO email
CNST-024: Límites de mensajería
CNST-026: Prioridades
"""

# ===================================================================
# LÍMITES (CNST-024)
# ===================================================================

MAX_RECIPIENTS = 50
"""Máximo destinatarios por mensaje (CNST-024)."""

MESSAGE_RETENTION_DAYS = 90
"""Días de retención de mensajes antes de auto-archivado (CNST-024)."""

MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024  # 5MB
"""Tamaño máximo de adjunto en bytes (CNST-024)."""

MAX_MESSAGES_PER_HOUR = 100
"""Máximo mensajes por hora por usuario (rate limit, CNST-024)."""

# ===================================================================
# PRIORIDADES (CNST-026)
# ===================================================================

PRIORITY_INFO = 'info'
PRIORITY_WARNING = 'warning'
PRIORITY_ERROR = 'error'
PRIORITY_CRITICAL = 'critical'

PRIORITY_CHOICES = [
    (PRIORITY_INFO, 'Informativo'),
    (PRIORITY_WARNING, 'Advertencia'),
    (PRIORITY_ERROR, 'Error'),
    (PRIORITY_CRITICAL, 'Crítico'),
]
"""Opciones de prioridad de mensajes."""

PRIORITY_COLORS = {
    PRIORITY_INFO: '#3B82F6',      # Azul
    PRIORITY_WARNING: '#F59E0B',   # Amarillo
    PRIORITY_ERROR: '#F97316',     # Naranja
    PRIORITY_CRITICAL: '#EF4444',  # Rojo
}
"""Colores UI por prioridad."""

# ===================================================================
# TIPOS DE TRIGGER
# ===================================================================

TRIGGER_THRESHOLD = 'threshold'
"""Trigger basado en umbral (ej: llamadas > 100)."""

TRIGGER_SCHEDULE = 'schedule'
"""Trigger basado en horario (ej: reporte diario)."""

TRIGGER_MANUAL = 'manual'
"""Trigger manual (activado por usuario)."""

TRIGGER_TYPES = [
    (TRIGGER_THRESHOLD, 'Umbral'),
    (TRIGGER_SCHEDULE, 'Horario'),
    (TRIGGER_MANUAL, 'Manual'),
]

# ===================================================================
# FRECUENCIAS DE SUSCRIPCIÓN
# ===================================================================

FREQUENCY_IMMEDIATE = 'immediate'
FREQUENCY_DAILY = 'daily'
FREQUENCY_WEEKLY = 'weekly'

FREQUENCY_CHOICES = [
    (FREQUENCY_IMMEDIATE, 'Inmediato'),
    (FREQUENCY_DAILY, 'Diario'),
    (FREQUENCY_WEEKLY, 'Semanal'),
]

# ===================================================================
# FORMATOS DE ADJUNTO PERMITIDOS
# ===================================================================

ALLOWED_ATTACHMENT_FORMATS = [
    'pdf', 'doc', 'docx',
    'xls', 'xlsx',
    'txt', 'csv'
]
"""Formatos de archivo permitidos para adjuntos (CNST-024)."""

# ===================================================================
# MENSAJES DEL SISTEMA
# ===================================================================

SYSTEM_SENDER_USERNAME = 'system'
"""Username para mensajes automáticos del sistema."""

DEFAULT_MESSAGE_TEMPLATES = {
    'abandoned_calls_alert': """
        Alerta: Llamadas Abandonadas
        
        Se han detectado {count} llamadas abandonadas en las últimas {hours} horas.
        DID: {did}
        
        Nivel de servicio actual: {service_level}%
        Umbral configurado: {threshold}
        
        Por favor revisar y tomar acción.
    """,
    
    'etl_error_alert': """
        Error en ETL
        
        El proceso ETL ha fallado:
        Job: {job_name}
        Error: {error_message}
        Timestamp: {timestamp}
        
        Acción requerida: Revisar logs y reintentar.
    """,
}
```

---

## 9. RESUMEN PARTE 1

### 9.1 Componentes Definidos

```yaml
Documentación:
  ✅ Resumen ejecutivo
  ✅ Propósito y responsabilidades
  ✅ CLEAN_CODE v3.0.1 aplicado
  ✅ RESTRICCIONES (CNST-001, CNST-024, CNST-026)
  ✅ RBAC v6.0.0 (6 funciones activas)
  ✅ Arquitectura completa
  ✅ 4 modelos Django definidos
  ✅ Constants y configuración

Modelos Django:
  ✅ InternalMessage (mensaje interno)
  ✅ MessageRecipient (M2M through)
  ✅ AlertConfiguration (reglas alertas)
  ✅ AlertSubscription (suscripciones usuarios)

RBAC:
  ✅ ALR_VIEW (alerts.view)
  ✅ ALR_SEND (alerts.send)
  ✅ ALR_CONF (alerts.configure)
  ✅ ALR_SUBS (alerts.subscribe)
  ✅ ALR_MARK (alerts.mark)
  ✅ ALR_DELETE (alerts.delete)

Constants:
  ✅ MAX_RECIPIENTS = 50
  ✅ MESSAGE_RETENTION_DAYS = 90
  ✅ MAX_ATTACHMENT_SIZE = 5MB
  ✅ PRIORITY_CHOICES (4 niveles)
  ✅ TRIGGER_TYPES (3 tipos)
```

---

## PRÓXIMA PARTE

**PARTE 2/3: Implementación Completa**

Contenido:
- Services completos (AlertService, ConfigurationService, SubscriptionService)
- Serializers (InternalMessageSerializer, AlertConfigurationSerializer, etc)
- ViewSets con RBAC (3 ViewSets)
- URLs configuration
- Endpoints REST documentados
- Validadores (MaxRecipientsValidator, AttachmentSizeValidator)
- Utils (send_message, auto_archive)

**Estimado:** ~1,200 líneas, 3 horas

---

**Fin de PARTE 1/3**
