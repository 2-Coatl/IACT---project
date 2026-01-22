---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Calls PARTE 1/4
categoria: arquitectura/apps
tema: apps/calls/ - Fundamentos, Models y Business Logic
autor: Claude Technical Analysis
tags: [calls, core-business, telephony, call-center, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes)
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md (3 partes)
estado: definitivo
parte: 1 de 4
relacionado:
  - ANALISIS_APP_ACCESS_v3_0_0.md (6 partes)
  - ANALISIS_APP_USERS_v3_0_0.md (4 partes)
  - ANALISIS_APP_CALLS_v3_0_0_PARTE_2.md
  - ANALISIS_APP_CALLS_v3_0_0_PARTE_3.md
  - ANALISIS_APP_CALLS_v3_0_0_PARTE_4.md
replaces: []
---

# ANÁLISIS DE apps/calls/ v3.0.0 - PARTE 1/4
## FUNDAMENTOS, MODELS Y BUSINESS LOGIC

---

## 1. RESUMEN EJECUTIVO

### 1.1 Información General

```yaml
App: apps/calls/
Tipo: COMPLEJA (4 partes) 🔴 CORE BUSINESS
Líneas estimadas: ~5,500 líneas código
Propósito: Gestión completa de llamadas del call center
Funciones RBAC: 5 (CALL_VIEW, CALL_EDIT, CALL_DELETE, CALL_EXP_CSV, CALL_STATS)
Dependencias:
  - apps/access/ (RBAC)
  - apps/users/ (usuarios/agentes)
  - apps/clients/ (clientes)
  - apps/services/ (servicios call center)
  - apps/ivr/ (IVR integration)
Tests: 60 tests estimados
Coverage objetivo: >90%
```

### 1.2 Responsabilidades Core

```yaml
Gestión de Llamadas:
  ✅ CRUD completo de llamadas
  ✅ Estados (ringing, answered, ended, failed)
  ✅ Tipos (inbound, outbound, internal, transfer)
  ✅ Duración y timing
  ✅ Caller ID / ANI
  ✅ DNIS (número marcado)
  ✅ Recording paths
  ✅ Notas y categorización

Métricas y Stats:
  ✅ Total de llamadas
  ✅ Llamadas por tipo
  ✅ Duración promedio
  ✅ Tasa de abandono
  ✅ Nivel de servicio (SLA)
  ✅ Tiempo de espera promedio
  ✅ Estadísticas por agente
  ✅ Estadísticas por servicio

Integraciones:
  - PBX/Asterisk (telefonía)
  - IVR system
  - CRM (clientes)
  - Recording system
  - Queue management
```

### 1.3 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                  apps/calls/                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Models:                                            │
│  ├─ Call (modelo principal)                        │
│  ├─ CallStatus (estados)                           │
│  ├─ CallType (tipos)                               │
│  ├─ CallRecording (grabaciones)                    │
│  ├─ CallNote (notas/comentarios)                   │
│  └─ CallMetrics (métricas agregadas)               │
│                                                     │
│  Services:                                          │
│  ├─ CallService (CRUD, gestión)                    │
│  ├─ CallStatsService (estadísticas)                │
│  ├─ RecordingService (grabaciones)                 │
│  └─ QueueService (colas de espera)                 │
│                                                     │
│  API:                                               │
│  ├─ CallViewSet (CRUD, stats, export)              │
│  ├─ RecordingViewSet (manage recordings)           │
│  ├─ StatsViewSet (dashboards, metrics)             │
│  └─ QueueViewSet (queue management)                │
│                                                     │
│  Integration:                                       │
│  ├─ PBX/Asterisk (AMI/AGI)                         │
│  ├─ apps/clients/ (customer data)                  │
│  ├─ apps/services/ (call routing)                  │
│  ├─ apps/ivr/ (IVR flows)                          │
│  └─ apps/users/ (agents)                           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 2. CLEAN CODE v3.0.1

```python
# ============================================================================
# CLASES - PascalCase
# ============================================================================

# Modelos
class Call(models.Model):                   # ✅ Llamada principal
class CallStatus(models.Model):             # ✅ Estado de llamada
class CallType(models.Model):               # ✅ Tipo de llamada
class CallRecording(models.Model):          # ✅ Grabación
class CallNote(models.Model):               # ✅ Nota/comentario
class CallMetrics(models.Model):            # ✅ Métricas agregadas

# Services
class CallService:                          # ✅ Gestión llamadas
class CallStatsService:                     # ✅ Estadísticas
class RecordingService:                     # ✅ Grabaciones
class QueueService:                         # ✅ Colas

# Serializers
class CallSerializer:                       # ✅ Call CRUD
class CallDetailSerializer:                 # ✅ Call detail
class CallStatsSerializer:                  # ✅ Stats
class RecordingSerializer:                  # ✅ Recording

# ViewSets
class CallViewSet:                          # ✅ API llamadas
class RecordingViewSet:                     # ✅ API grabaciones
class StatsViewSet:                         # ✅ API estadísticas

# ============================================================================
# MÉTODOS - snake_case (inglés técnico)
# ============================================================================

# CRUD
def create_call(caller, callee, service):       # ✅ Crear
def get_call(call_id):                          # ✅ Obtener
def update_call(call_id, data):                 # ✅ Actualizar
def end_call(call_id, status):                  # ✅ Finalizar

# Stats
def get_call_stats(filters):                    # ✅ Estadísticas
def calculate_metrics(period):                  # ✅ Calcular métricas
def get_agent_stats(agent_id):                  # ✅ Stats por agente
def get_service_stats(service_id):              # ✅ Stats por servicio

# Recording
def get_recording(call_id):                     # ✅ Obtener grabación
def upload_recording(call_id, file):            # ✅ Subir grabación
def delete_recording(recording_id):             # ✅ Eliminar grabación

# ============================================================================
# CONSTANTES - UPPER_SNAKE_CASE
# ============================================================================

# Call Status
STATUS_RINGING = 'ringing'
STATUS_ANSWERED = 'answered'
STATUS_ENDED = 'ended'
STATUS_FAILED = 'failed'
STATUS_BUSY = 'busy'
STATUS_NO_ANSWER = 'no_answer'

# Call Types
TYPE_INBOUND = 'inbound'
TYPE_OUTBOUND = 'outbound'
TYPE_INTERNAL = 'internal'
TYPE_TRANSFER = 'transfer'

# Metrics
MAX_WAIT_TIME = 300         # 5 minutos
SLA_TARGET = 0.80          # 80%
ABANDON_THRESHOLD = 30      # 30 segundos

# ============================================================================
# DATABASE - Húngaro (legacy)
# ============================================================================

# Tabla: tbl_llamadas
iIdLlamada                  # PK (bigint)       # ✅ ID llamada
iIdServicio                 # FK (int)          # ✅ Servicio
iIdCliente                  # FK (int)          # ✅ Cliente
iIdAgente                   # FK (int)          # ✅ Agente
cCallerNumber               # varchar(20)       # ✅ Número origen
cCalleeNumber               # varchar(20)       # ✅ Número destino
cDNIS                       # varchar(20)       # ✅ DNIS
cCallType                   # varchar(20)       # ✅ Tipo
cStatus                     # varchar(20)       # ✅ Estado
dtStartTime                 # datetime          # ✅ Inicio
dtAnswerTime                # datetime          # ✅ Respuesta
dtEndTime                   # datetime          # ✅ Fin
iDurationSeconds            # int               # ✅ Duración
iWaitSeconds                # int               # ✅ Espera
cRecordingPath              # varchar(255)      # ✅ Grabación
tNotes                      # text              # ✅ Notas

# ============================================================================
# PERMISSIONS - apps/access/
# ============================================================================

CALL_VIEW = 'CALL_VIEW'         # Ver llamadas
CALL_EDIT = 'CALL_EDIT'         # Editar llamadas
CALL_DELETE = 'CALL_DELETE'     # Eliminar llamadas
CALL_EXP_CSV = 'CALL_EXP_CSV'   # Exportar CSV
CALL_STATS = 'CALL_STATS'       # Ver estadísticas
```

---

## 3. RESTRICCIONES ARQUITECTÓNICAS

### 3.1 CNST-040: Call Immutability

```yaml
CNST-040: Call Immutability (🔴 CRÍTICO)

Descripción:
  Llamadas finalizadas son INMUTABLES por compliance.
  Solo se permiten agregar notas, no modificar datos core.

Reglas:
  1. Call finalizado (status=ended) NO puede modificar:
     - start_time, answer_time, end_time
     - caller_number, callee_number
     - duration_seconds, wait_seconds
     - agent, service, client
  
  2. SÍ se puede modificar después de finalizar:
     - notes (agregar, no eliminar)
     - category/tags
     - recording metadata
  
  3. Soft delete: is_deleted flag, no DELETE físico

Implementación:
  class Call(models.Model):
      def save(self, *args, **kwargs):
          if self.pk and self.status == 'ended':
              # Check only mutable fields changed
              old = Call.objects.get(pk=self.pk)
              if old.start_time != self.start_time:
                  raise ValidationError("Cannot modify ended call")
          super().save(*args, **kwargs)

Justificación:
  - Compliance legal (grabaciones/billing)
  - Auditoría SOX/GDPR
  - Prevención de fraude
```

### 3.2 CNST-041: Recording Retention

```yaml
CNST-041: Recording Retention (⚠️ IMPORTANTE)

Descripción:
  Grabaciones deben retenerse según política legal.

Reglas:
  1. Retención mínima: 90 días
  2. Retención máxima: 7 años (configurable)
  3. Auto-delete después de retention period
  4. Encryption at rest (AES-256)
  5. Access logging (quién escuchó qué)

Implementación:
  # Task celery diaria
  @shared_task
  def delete_expired_recordings():
      expiry_date = now() - timedelta(days=RETENTION_DAYS)
      recordings = CallRecording.objects.filter(
          created_at__lt=expiry_date
      )
      for rec in recordings:
          rec.delete()  # Elimina archivo físico

Justificación:
  - Compliance GDPR (data retention)
  - Storage costs
  - Privacy regulations
```

### 3.3 CNST-042: Real-time Events

```yaml
CNST-042: Real-time Call Events (⚠️ IMPORTANTE)

Descripción:
  Eventos de llamadas en tiempo real via WebSockets.

Reglas:
  1. Evento al crear llamada: call.created
  2. Evento al contestar: call.answered
  3. Evento al finalizar: call.ended
  4. Evento al transferir: call.transferred
  5. Django Channels para WebSockets

Implementación:
  # signals.py
  @receiver(post_save, sender=Call)
  def broadcast_call_event(sender, instance, created, **kwargs):
      channel_layer = get_channel_layer()
      async_to_sync(channel_layer.group_send)(
          'calls',
          {
              'type': 'call_event',
              'call_id': instance.id,
              'status': instance.status
          }
      )

Justificación:
  - Real-time dashboards
  - Agent notifications
  - Supervisor monitoring
```

---

## 4. MODELOS DJANGO

### 4.1 Call (Modelo Principal)

```python
"""
Call model - Llamada telefónica.

CNST-040: Inmutabilidad de llamadas finalizadas.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


class Call(models.Model):
    """
    Llamada telefónica del call center.
    
    Modelo central de apps/calls/.
    
    CNST-040: Llamadas finalizadas son inmutables.
    
    Fields:
    - service: Servicio del call center
    - client: Cliente (opcional)
    - agent: Agente que atendió
    - caller_number: Número origen (ANI)
    - callee_number: Número destino
    - dnis: DNIS (número marcado)
    - call_type: Tipo (inbound/outbound/internal/transfer)
    - status: Estado (ringing/answered/ended/failed)
    - start_time: Inicio de llamada
    - answer_time: Tiempo de respuesta
    - end_time: Fin de llamada
    - duration_seconds: Duración total
    - wait_seconds: Tiempo de espera
    - recording_path: Path a grabación
    - notes: Notas/comentarios
    - is_deleted: Soft delete
    
    Relations:
    - service (FK to Service)
    - client (FK to Client, nullable)
    - agent (FK to User, nullable)
    - recordings (1-to-many CallRecording)
    - notes_list (1-to-many CallNote)
    """
    
    # Foreign Keys
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.PROTECT,
        related_name='calls',
        db_column='iIdServicio',
        help_text='Servicio del call center'
    )
    
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calls',
        db_column='iIdCliente',
        help_text='Cliente asociado'
    )
    
    agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calls_handled',
        db_column='iIdAgente',
        help_text='Agente que atendió'
    )
    
    # Call identification
    caller_number = models.CharField(
        'Número Origen',
        max_length=20,
        db_column='cCallerNumber',
        help_text='ANI - Caller ID'
    )
    
    callee_number = models.CharField(
        'Número Destino',
        max_length=20,
        db_column='cCalleeNumber',
        help_text='Número marcado'
    )
    
    dnis = models.CharField(
        'DNIS',
        max_length=20,
        blank=True,
        db_column='cDNIS',
        help_text='Dialed Number Identification Service'
    )
    
    # Call metadata
    call_type = models.CharField(
        'Tipo',
        max_length=20,
        choices=[
            ('inbound', 'Entrante'),
            ('outbound', 'Saliente'),
            ('internal', 'Interna'),
            ('transfer', 'Transferida'),
        ],
        default='inbound',
        db_column='cCallType'
    )
    
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=[
            ('ringing', 'Sonando'),
            ('answered', 'Contestada'),
            ('ended', 'Finalizada'),
            ('failed', 'Fallida'),
            ('busy', 'Ocupado'),
            ('no_answer', 'Sin Respuesta'),
        ],
        default='ringing',
        db_column='cStatus'
    )
    
    # Timing
    start_time = models.DateTimeField(
        'Inicio',
        db_column='dtStartTime',
        help_text='Timestamp inicio de llamada'
    )
    
    answer_time = models.DateTimeField(
        'Respuesta',
        null=True,
        blank=True,
        db_column='dtAnswerTime',
        help_text='Timestamp cuando se contestó'
    )
    
    end_time = models.DateTimeField(
        'Fin',
        null=True,
        blank=True,
        db_column='dtEndTime',
        help_text='Timestamp fin de llamada'
    )
    
    duration_seconds = models.IntegerField(
        'Duración (seg)',
        default=0,
        db_column='iDurationSeconds',
        help_text='Duración total en segundos'
    )
    
    wait_seconds = models.IntegerField(
        'Espera (seg)',
        default=0,
        db_column='iWaitSeconds',
        help_text='Tiempo de espera en segundos'
    )
    
    # Recording
    recording_path = models.CharField(
        'Grabación',
        max_length=255,
        blank=True,
        db_column='cRecordingPath',
        help_text='Path a archivo de grabación'
    )
    
    # Notes
    notes = models.TextField(
        'Notas',
        blank=True,
        db_column='tNotes',
        help_text='Notas sobre la llamada'
    )
    
    # Soft delete
    is_deleted = models.BooleanField(
        'Eliminado',
        default=False,
        db_column='bIsDeleted'
    )
    
    # Metadata
    created_at = models.DateTimeField(
        'Creado',
        auto_now_add=True,
        db_column='dtCreatedAt'
    )
    
    updated_at = models.DateTimeField(
        'Actualizado',
        auto_now=True,
        db_column='dtUpdatedAt'
    )
    
    class Meta:
        db_table = 'tbl_llamadas'
        verbose_name = 'Llamada'
        verbose_name_plural = 'Llamadas'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['status']),
            models.Index(fields=['call_type']),
            models.Index(fields=['service', 'start_time']),
            models.Index(fields=['agent', 'start_time']),
        ]
    
    def __str__(self):
        """String representation."""
        return f"Call {self.id} - {self.caller_number} ({self.status})"
    
    def save(self, *args, **kwargs):
        """
        Custom save con validación CNST-040.
        
        CNST-040: Llamadas finalizadas son inmutables.
        """
        if self.pk and self.status == 'ended':
            # Verificar inmutabilidad
            old = Call.objects.get(pk=self.pk)
            
            immutable_fields = [
                'start_time', 'answer_time', 'end_time',
                'caller_number', 'callee_number',
                'duration_seconds', 'wait_seconds',
                'agent_id', 'service_id', 'client_id'
            ]
            
            for field in immutable_fields:
                old_value = getattr(old, field)
                new_value = getattr(self, field)
                if old_value != new_value:
                    raise ValidationError(
                        f"Cannot modify '{field}' on ended call (CNST-040)"
                    )
        
        super().save(*args, **kwargs)
    
    def end(self):
        """Finaliza la llamada."""
        if self.status != 'ended':
            self.end_time = timezone.now()
            self.status = 'ended'
            
            # Calcular duración
            if self.answer_time:
                self.duration_seconds = int(
                    (self.end_time - self.answer_time).total_seconds()
                )
            
            # Calcular espera
            if self.answer_time:
                self.wait_seconds = int(
                    (self.answer_time - self.start_time).total_seconds()
                )
            
            self.save()
    
    @property
    def formatted_duration(self):
        """Duración formateada HH:MM:SS."""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @property
    def was_answered(self):
        """Indica si la llamada fue contestada."""
        return self.answer_time is not None
    
    @property
    def is_active(self):
        """Indica si la llamada está activa."""
        return self.status in ['ringing', 'answered']
```

### 4.2 CallRecording

```python
class CallRecording(models.Model):
    """
    Grabación de llamada.
    
    CNST-041: Retention policy aplicada.
    """
    
    call = models.ForeignKey(
        Call,
        on_delete=models.CASCADE,
        related_name='recordings',
        db_column='iIdLlamada'
    )
    
    file = models.FileField(
        'Archivo',
        upload_to='recordings/%Y/%m/%d/',
        db_column='cFile'
    )
    
    duration_seconds = models.IntegerField(
        'Duración',
        default=0,
        db_column='iDurationSeconds'
    )
    
    format = models.CharField(
        'Formato',
        max_length=10,
        default='wav',
        db_column='cFormat'
    )
    
    size_bytes = models.BigIntegerField(
        'Tamaño',
        default=0,
        db_column='iBigSizeBytes'
    )
    
    is_encrypted = models.BooleanField(
        'Encriptado',
        default=True,
        db_column='bIsEncrypted'
    )
    
    created_at = models.DateTimeField(
        'Creado',
        auto_now_add=True,
        db_column='dtCreatedAt'
    )
    
    class Meta:
        db_table = 'tbl_grabaciones'
        verbose_name = 'Grabación'
        verbose_name_plural = 'Grabaciones'
```

### 4.3 CallNote

```python
class CallNote(models.Model):
    """Nota sobre llamada."""
    
    call = models.ForeignKey(
        Call,
        on_delete=models.CASCADE,
        related_name='notes_list',
        db_column='iIdLlamada'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        db_column='iIdUsuario'
    )
    
    note = models.TextField(
        'Nota',
        db_column='tNota'
    )
    
    created_at = models.DateTimeField(
        'Creado',
        auto_now_add=True,
        db_column='dtCreatedAt'
    )
    
    class Meta:
        db_table = 'tbl_notas_llamadas'
        verbose_name = 'Nota de Llamada'
        ordering = ['-created_at']
```

---

## 5. CONSTANTS

```python
"""
Constants para apps/calls/.
"""

# Call Status
STATUS_RINGING = 'ringing'
STATUS_ANSWERED = 'answered'
STATUS_ENDED = 'ended'
STATUS_FAILED = 'failed'
STATUS_BUSY = 'busy'
STATUS_NO_ANSWER = 'no_answer'

CALL_STATUSES = [
    STATUS_RINGING,
    STATUS_ANSWERED,
    STATUS_ENDED,
    STATUS_FAILED,
    STATUS_BUSY,
    STATUS_NO_ANSWER,
]

# Call Types
TYPE_INBOUND = 'inbound'
TYPE_OUTBOUND = 'outbound'
TYPE_INTERNAL = 'internal'
TYPE_TRANSFER = 'transfer'

CALL_TYPES = [
    TYPE_INBOUND,
    TYPE_OUTBOUND,
    TYPE_INTERNAL,
    TYPE_TRANSFER,
]

# Metrics
MAX_WAIT_TIME_SECONDS = 300     # 5 min
SLA_TARGET_PERCENTAGE = 0.80    # 80%
ABANDON_THRESHOLD_SECONDS = 30  # 30 seg

# Recording
RECORDING_RETENTION_DAYS = 90   # 90 días mínimo
RECORDING_FORMAT_DEFAULT = 'wav'
RECORDING_ENCRYPTION = True

# Funciones RBAC
CALL_VIEW = 'CALL_VIEW'
CALL_EDIT = 'CALL_EDIT'
CALL_DELETE = 'CALL_DELETE'
CALL_EXP_CSV = 'CALL_EXP_CSV'
CALL_STATS = 'CALL_STATS'
```

---

## 6. RESUMEN PARTE 1

```yaml
Modelos (3):
  ✅ Call (modelo principal, ~250 líneas)
  ✅ CallRecording (grabaciones)
  ✅ CallNote (notas)

Restricciones (3):
  ✅ CNST-040: Call Immutability
  ✅ CNST-041: Recording Retention
  ✅ CNST-042: Real-time Events

Constants:
  ✅ Call statuses (6)
  ✅ Call types (4)
  ✅ Metrics thresholds
  ✅ Recording config
  ✅ RBAC functions (5)

Líneas código: ~850 líneas Python

Funciones RBAC: 5 funciones
```

---

## PRÓXIMA PARTE

**PARTE 2/4: Services y Call Management**

Contenido:
- ✅ CallService (CRUD completo)
- ✅ CallStatsService (métricas)
- ✅ RecordingService (grabaciones)
- ✅ QueueService (colas)
- ✅ Utils (8+ helpers)
- ✅ Exceptions (6 custom)

**Estimado:** ~1,400 líneas, 3 horas

---

**Fin de PARTE 1/4**
