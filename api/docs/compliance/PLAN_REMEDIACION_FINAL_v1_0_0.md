# 🎯 PLAN DE REMEDIACIÓN FINAL - Arquitectura Correcta de 4 Apps

## INFORMACIÓN DEL DOCUMENTO

| Atributo | Valor |
|---|---|
| **Fecha** | 2026-01-21 |
| **Versión** | 1.0.0 FINAL |
| **Base** | ANALISIS_APP_USERS, AUTHENTICATION, ACCESS (18 partes) |
| **Prioridad** | 🔴 CRÍTICA - BLOCKER |

---

## 📋 RESUMEN EJECUTIVO

### Arquitectura Correcta: 4 Apps Separadas

```yaml
apps/users/ (YA implementado - 80% CORRECTO):
  Responsabilidad: Gestión básica de usuarios (CRUD)
  Estado: ✅ 80% completo
  Acción: LIMPIAR (quitar auth)

apps/authentication/ (FALTA implementar - 0%):
  Responsabilidad: Autenticación y seguridad
  Estado: ❌ NO EXISTE
  Acción: CREAR desde cero

apps/access/ (FALTA implementar - 0%):
  Responsabilidad: RBAC (permisos function-based)
  Estado: ❌ NO EXISTE
  Acción: CREAR desde cero

apps/alerts/ (FALTA implementar - 0%):
  Responsabilidad: Mensajería interna
  Estado: ❌ NO EXISTE  
  Acción: CREAR después
```

---

## 🏗️ ARQUITECTURA CORRECTA DETALLADA

### 1. apps/users/ - Gestión de Usuarios

```yaml
Propósito: CRUD de usuarios, perfiles, configuración

Models (3):
  ✅ User (AbstractUser + SoftDeleteMixin)
     - username, email, password
     - employee_id, phone, position
     - avatar
     - is_active, is_staff, is_superuser
     ❌ NO first_login, NO force_password_change → van en signals de authentication
     ❌ NO security_questions_answered → va en authentication
  
  ✅ UserProfile (1-to-1 con User)
     - bio, department, hire_date
     - emergency_contact, emergency_phone
     - auto-creado vía signal
  
  ✅ UserSettings (1-to-1 con User)
     - timezone, language, date_format
     - notifications_enabled, email_alerts
     - auto-creado vía signal
  
  ❌ SessionHistory → MOVER a apps/authentication/

Services (3):
  ✅ UserService (create, update, delete, activate, deactivate)
  ✅ ProfileService (update_profile, upload_avatar, remove_avatar)
  ✅ PasswordService (change_password) ← Solo cambio cuando usuario está autenticado
  ❌ AuthenticationService → NO va aquí

Endpoints (8):
  ✅ GET/POST    /api/v1/users/users/
  ✅ GET/PUT     /api/v1/users/users/{id}/
  ✅ DELETE      /api/v1/users/users/{id}/
  ✅ GET         /api/v1/users/users/me/
  ✅ POST        /api/v1/users/users/{id}/activate/
  ✅ POST        /api/v1/users/users/{id}/deactivate/
  ✅ GET/PATCH   /api/v1/users/profile/
  ✅ POST/DELETE /api/v1/users/profile/avatar/
  ✅ GET/PATCH   /api/v1/users/settings/
  
  ❌ ELIMINAR:
     - /api/v1/users/auth/login/
     - /api/v1/users/auth/logout/
     - /api/v1/users/auth/password-reset/
     - /api/v1/users/auth/*

RBAC Functions:
  - USR_VIEW (ver usuarios)
  - USR_CREATE (crear usuarios con password genérica)
  - USR_EDIT (editar usuarios)
  - USR_DELETE (soft delete)
  - USR_PERMS (gestionar permisos) ← Usa apps/access/
```

---

### 2. apps/authentication/ - Autenticación y Seguridad

```yaml
Propósito: Login, logout, recuperación de password, first login

Models (4):
  ✅ LoginAttempt (auditoría de intentos)
     - user (FK nullable)
     - username (intentado)
     - success (bool)
     - ip_address, user_agent
     - attempted_at
  
  ✅ SecurityQuestion (preguntas predefinidas)
     - question (text)
     - is_active
     - order
     - TOTAL: 10 preguntas en pool
     - Usuario debe responder: 5 preguntas
  
  ✅ UserSecurityAnswer (respuestas hasheadas)
     - user (FK)
     - question (FK)
     - answer_hash (PBKDF2, case-insensitive)
     - created_at, updated_at
     - unique_together: (user, question)
  
  ✅ SessionLog (historial de sesiones)
     - user (FK)
     - session_key (Django session)
     - ip_address, user_agent
     - login_at, logout_at
     - is_active

Services (4):
  ✅ AuthenticationService
     - login_user(request, username, password)
     - logout_user(request)
     - Maneja first_login flow
     - Registra LoginAttempt
     - Crea SessionLog
  
  ✅ RecoveryService (CNST-001: SIN EMAIL)
     - get_available_questions() → 10 preguntas
     - set_security_answers(user, answers) → 5 respuestas
     - verify_security_answers(username, answers) → bool
     - reset_password_by_questions(username, answers, new_pwd)
  
  ✅ LockoutService
     - is_locked(username) → bool
     - record_failed_attempt(username)
     - MAX: 5 intentos
     - LOCKOUT: 15 minutos
  
  ✅ SessionService
     - get_active_sessions(user)
     - invalidate_session(session_key)

Endpoints (7):
  ✅ POST /api/v1/auth/login/
     Request: {username, password}
     Response: {
       user: {...},
       token: "...",
       session_key: "...",
       first_login: true/false,
       force_password_change: true/false,
       security_questions_pending: true/false
     }
  
  ✅ POST /api/v1/auth/logout/
  
  ✅ POST /api/v1/auth/change-password/
     Request: {old_password, new_password}
     Note: Solo para usuario autenticado
  
  ✅ GET  /api/v1/auth/security-questions/
     Response: [
       {id: 1, question: "...", order: 1},
       {id: 2, question: "...", order: 2},
       ...
     ]
  
  ✅ POST /api/v1/auth/set-security-answers/
     Request: {
       answers: [
         {question_id: 1, answer: "..."},
         {question_id: 5, answer: "..."},
         {question_id: 8, answer: "..."},
         {question_id: 3, answer: "..."},
         {question_id: 9, answer: "..."}
       ]
     }
     Note: Requiere IsAuthenticated
     Note: Exactamente 5 respuestas
  
  ✅ POST /api/v1/auth/verify-security-answers/
     Request: {username, answers: [...]}
     Response: {verified: true/false}
  
  ✅ POST /api/v1/auth/reset-password/
     Request: {
       username: "jdoe",
       answers: [
         {question_id: 1, answer: "..."},
         ...  # 5 respuestas
       ],
       new_password: "...",
       new_password_confirm: "..."
     }
     Response:
       - 200: {message: "Password reset successful"}
       - 403: {error: "No security questions configured"}
       - 400: {error: "Incorrect answers"}
  
  ✅ GET /api/v1/sessions/ (mis sesiones)
  ✅ POST /api/v1/sessions/{id}/invalidate/

Constants:
  - MAX_LOGIN_ATTEMPTS = 5
  - LOCKOUT_DURATION_MINUTES = 15
  - SESSION_TIMEOUT_SECONDS = 3600
  - SECURITY_QUESTIONS_REQUIRED = 5  ← TU especificación
  - SECURITY_QUESTIONS_POOL_MIN = 10

Flujos:
  1. First Login:
     - Usuario creado con password genérica
     - first_login signal en login
     - Force change password
     - Force configurar 5 preguntas
  
  2. Password Reset SIN EMAIL:
     - Usuario solicita reset
     - Sistema verifica si tiene 5 respuestas configuradas
     - Si SÍ: muestra formulario con 5 preguntas
     - Usuario responde
     - Sistema valida (PBKDF2 hash)
     - Si correcto: permite cambio
     - Si incorrecto: deniega + log
     - Si NO tiene preguntas: ALERT + contactar admin
```

---

### 3. apps/access/ - RBAC (Permisos)

```yaml
Propósito: Sistema de control de acceso basado en funciones

Models (6):
  ✅ Module (11 módulos)
     - code (MOD_Audit, MOD_Dashboard, etc)
     - name, description
     - is_active, order
  
  ✅ Function (46 funciones activas)
     - code (AUD_VIEW, DSH_VIEW, RPT_CREATE, etc)
     - name, description
     - module (FK)
     - permission_string (audit.view)
     - is_active
  
  ✅ Group (grupos de usuarios)
     - code (GRP_Admin, GRP_Manager, GRP_Auditor, etc)
     - name, description
     - is_active
     - users (M2M through UserGroup)
     - functions (M2M through GroupFunction)
  
  ✅ UserGroup (User ↔ Group)
     - user (FK auth.User)
     - group (FK)
     - assigned_at, assigned_by
     - unique_together: (user, group)
  
  ✅ GroupFunction (Group ↔ Function)
     - group (FK)
     - function (FK)
     - assigned_at, assigned_by
     - unique_together: (group, function)
  
  ✅ PermissionLog (auditoría RBAC)
     - user (FK)
     - action (assigned/removed/modified)
     - target_type (user/group/function)
     - target_id
     - details (JSON)
     - performed_by (FK)
     - performed_at

Services (3):
  ✅ RBACService (CORE)
     - has_function(user, function_code) → bool
     - get_user_functions(user) → Set[str]
     - validate_permission(user, permission_string) → bool
     - invalidate_user_cache(user)
     - Cache: 300s (CNST-035)
  
  ✅ GroupService
     - assign_user_to_group(user, group)
     - remove_user_from_group(user, group)
     - assign_function_to_group(group, function)
     - remove_function_from_group(group, function)
     - get_group_functions(group) → List[Function]
     - get_user_groups(user) → List[Group]
  
  ✅ PermissionCacheService
     - cache_user_functions(user)
     - invalidate_cache(user)
     - bulk_invalidate_cache(user_ids)

Permissions (2):
  ✅ DynamicFunctionPermission (DRF BasePermission)
     - Usado en TODOS los ViewSets
     - Lee function_map del ViewSet
     - Valida con RBACService.has_function()
  
  ✅ FunctionPermissionMixin (Class-based views)
     - required_function = 'AUD_VIEW'
     - Mixin para CBV

Decorators (3):
  ✅ @require_function('AUD_VIEW')
     - Para function-based views
     - Wrapper sobre RBACService.has_function()
  
  ✅ @require_any_function(['AUD_VIEW', 'DSH_VIEW'])
     - OR logic (cualquiera)
  
  ✅ @require_all_functions(['AUD_VIEW', 'AUD_EDIT'])
     - AND logic (todas)

Middleware:
  ✅ RBACMiddleware
     - Attach request.user_functions
     - Cache-aware
     - Performance optimized

Endpoints (ADMIN only - USR_PERMS):
  ✅ GET/POST   /api/v1/access/functions/
  ✅ GET/PUT    /api/v1/access/functions/{id}/
  ✅ GET/POST   /api/v1/access/modules/
  ✅ GET/POST   /api/v1/access/groups/
  ✅ POST       /api/v1/access/groups/{id}/assign-user/
  ✅ POST       /api/v1/access/groups/{id}/remove-user/
  ✅ POST       /api/v1/access/groups/{id}/assign-function/
  ✅ POST       /api/v1/access/groups/{id}/remove-function/
  ✅ GET        /api/v1/access/users/{id}/functions/
  ✅ GET        /api/v1/access/permission-logs/

46 Funciones del Sistema:
  MOD_Audit (4):      AUD_VIEW, AUD_SEARCH, AUD_REPORT, AUD_EXPORT
  MOD_Dashboard (3):  DSH_VIEW, DSH_EXP_CSV, DSH_EXP_EXCEL
  MOD_Alerts (4):     ALR_VIEW, ALR_SEND, ALR_CONF, ALR_SUBS
  MOD_Reports (6):    RPT_VIEW, RPT_CREATE, RPT_DELETE, RPT_EXP_CSV, RPT_EXP_EXCEL, RPT_EXP_PDF
  MOD_Calls (5):      CALL_VIEW, CALL_EDIT, CALL_DELETE, CALL_EXP_CSV, CALL_STATS
  MOD_Clients (4):    CLI_VIEW, CLI_EDIT, CLI_DELETE, CLI_MERGE
  MOD_Services (4):   SVC_VIEW, SVC_EDIT, SVC_DELETE, SVC_CONFIG
  MOD_IVR (3):        IVR_VIEW, IVR_EDIT, IVR_STATS
  MOD_Users (4):      USR_VIEW, USR_EDIT, USR_DELETE, USR_PERMS
  MOD_Config (2):     CFG_VIEW, CFG_EDIT
  MOD_System (2):     SYS_ADMIN, SYS_LOGS

Fixtures:
  ✅ 11 modules (JSON)
  ✅ 46 functions (JSON)
  ✅ 5 default groups (JSON)
```

---

### 4. apps/alerts/ - Mensajería Interna

```yaml
Propósito: Sistema de alertas y notificaciones INTERNAS (NO email - CNST-001)

Models (5):
  ✅ InternalMessage (mensaje principal)
     - sender (FK User)
     - subject, body
     - priority (info/warning/error/critical)
     - sent_at
     - archived (>90 días auto-archivado)
     - deleted (soft delete)
  
  ✅ MessageRecipient (M2M User ↔ Message)
     - message (FK InternalMessage)
     - recipient (FK User)
     - is_read, read_at
     - deleted_by_recipient
     - Permite tracking individual por destinatario
  
  ✅ AlertConfiguration (reglas de alertas automáticas)
     - name, description
     - event_type (llamadas_abandonadas, security_questions_pending, etc)
     - trigger_condition (JSON)
     - is_active
  
  ✅ AlertSubscription (suscripciones usuarios)
     - user (FK)
     - configuration (FK AlertConfiguration)
     - is_active
     - subscribed_at
  
  ✅ AlertLog (auditoría de alertas)
     - configuration (FK)
     - triggered_at
     - recipients_count
     - trigger_data (JSON)

Services (3):
  ✅ AlertService (CORE)
     - send_message(sender, recipients, subject, body, priority)
     - get_user_messages(user, unread_only, priority, limit)
     - mark_as_read(message_id, user)
     - mark_as_unread(message_id, user)
     - delete_message(message_id, user) → soft delete
     - auto_archive_old_messages() → >90 días
     - get_unread_count(user)
     - Validaciones: MAX 50 destinatarios (CNST-024)
     - Rate limit: 100 msg/hora
  
  ✅ ConfigurationService
     - create_alert_rule(event_type, trigger_condition)
     - trigger_alert(configuration, trigger_data)
     - get_active_configurations()
     - check_trigger(configuration, data) → bool
  
  ✅ SubscriptionService
     - subscribe_user(user, configuration)
     - unsubscribe_user(user, configuration)
     - get_user_subscriptions(user)
     - get_subscribers(configuration)

Validators (3):
  ✅ MaxRecipientsValidator
     - Valida máximo 50 destinatarios (CNST-024)
  
  ✅ RateLimitValidator
     - Valida 100 mensajes/hora por usuario
  
  ✅ AttachmentSizeValidator
     - Valida adjuntos <5MB (CNST-024)

Endpoints (12):
  ✅ GET    /api/v1/alerts/ (mis mensajes)
  ✅ GET    /api/v1/alerts/{id}/
  ✅ POST   /api/v1/alerts/send/
  ✅ PATCH  /api/v1/alerts/{id}/mark-read/
  ✅ PATCH  /api/v1/alerts/{id}/mark-unread/
  ✅ DELETE /api/v1/alerts/{id}/ (soft delete)
  ✅ GET    /api/v1/alerts/unread-count/
  
  ✅ GET    /api/v1/alerts/configurations/
  ✅ POST   /api/v1/alerts/configurations/
  ✅ PUT    /api/v1/alerts/configurations/{id}/
  ✅ DELETE /api/v1/alerts/configurations/{id}/
  
  ✅ GET    /api/v1/alerts/subscriptions/
  ✅ POST   /api/v1/alerts/subscriptions/
  ✅ DELETE /api/v1/alerts/subscriptions/{id}/

Management Commands:
  ✅ python manage.py auto_archive_messages
     - Cronjob diario (3 AM)
     - Archiva mensajes >90 días (CNST-024)

RBAC Functions (6):
  - ALR_VIEW (ver mensajes recibidos)
  - ALR_SEND (enviar mensajes)
  - ALR_MARK (marcar leído/no leído)
  - ALR_DELETE (eliminar propios)
  - ALR_CONF (configurar alertas)
  - ALR_SUBS (gestionar suscripciones)

CNST-001 Aplicado:
  ❌ NO email externo (smtplib, django.core.mail)
  ❌ NO servicios externos (SendGrid, Mailgun)
  ❌ NO webhooks externos
  ✅ Solo buzón interno en BD
  ✅ Notificaciones in-app

CNST-024 Aplicado:
  ✅ Máximo 50 destinatarios por mensaje
  ✅ Retención 90 días, auto-archivado
  ✅ Límite adjuntos 5MB
  ✅ Rate limit 100 msg/hora

Integration con authentication:
  ✅ ALERT cuando usuario intenta reset sin preguntas configuradas
  ✅ ALERT diaria (cron) a usuarios sin preguntas
  ✅ ALERT cuando admin resetea password de usuario
  ✅ Tipo de alerta: "security_questions_pending"
  ✅ Prioridad: "warning"
```

---

## 🚨 VIOLACIONES ACTUALES en apps/users/

### Violación #1: AuthViewSet en app incorrecta

**Ubicación:** `apps/users/viewsets.py` líneas 240-430

```python
# ❌ ELIMINAR COMPLETO

class AuthViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['post'])
    def login(self, request):  # → apps/authentication/
        ...
    
    @action(detail=False, methods=['post'])
    def logout(self, request):  # → apps/authentication/
        ...
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):  # → apps/authentication/
        ...
    
    @action(detail=False, methods=['post'])
    def password_reset(self, request):  # ❌ USA EMAIL (CNST-001)
        """Envía un email..."""  # → ELIMINAR, crear reset con preguntas
        ...
    
    @action(detail=False, methods=['post'])
    def password_reset_confirm(self, request):  # ❌ USA EMAIL
        """Token del email..."""  # → ELIMINAR
        ...
```

### Violación #2: SessionHistory mal ubicado

```python
# apps/users/models.py
class SessionHistory(TimeStampedModel):  # ❌ → apps/authentication/SessionLog
    ...
```

### Violación #3: has_function() en User model

```python
# apps/users/models.py - User model
def has_function(self, function_code: str) -> bool:  # ❌ → apps/access/RBACService
    """Verifica si usuario tiene función."""
    ...
```

**CORRECTO:**

```python
# apps/access/services.py - RBACService
def has_function(self, user: User, function_code: str) -> bool:
    """Verifica si usuario tiene función."""
    ...

# Uso en ViewSets:
from apps.access.services import RBACService

rbac = RBACService()
if rbac.has_function(request.user, 'AUD_VIEW'):
    ...
```

### Violación #4: URLs incorrectas

```python
# apps/users/urls.py - ELIMINAR

auth_urls = [  # ❌ TODO va en apps/authentication/
    path('login/', ...),
    path('logout/', ...),
    path('password-reset/', ...),
    ...
]
```

---

## 📝 PLAN DE REMEDIACIÓN DETALLADO

### FASE 1: Limpieza apps/users/ (2 horas)

#### Paso 1.1: Eliminar AuthViewSet

```bash
# apps/users/viewsets.py

ELIMINAR completo (líneas 240-430):
  - class AuthViewSet
  - Todos sus métodos
  - Todos sus decorators @extend_schema
```

#### Paso 1.2: Eliminar serializers de auth

```bash
# apps/users/serializers/auth_serializers.py

ELIMINAR:
  - LoginSerializer
  - PasswordResetRequestSerializer
  - PasswordResetConfirmSerializer

MANTENER:
  - ChangePasswordSerializer ← Se moverá a authentication
```

#### Paso 1.3: Actualizar URLs

```bash
# apps/users/urls.py

ELIMINAR:
  - auth_urls
  - path('auth/', include(auth_urls))

MANTENER:
  - router (UserViewSet)
  - profile_urls
  - settings_urls
```

#### Paso 1.4: Eliminar has_function() de User

```python
# apps/users/models.py - User model

ELIMINAR método:
  def has_function(self, function_code: str) -> bool:
      ...

NOTA: Se reemplazará con RBACService.has_function(user, code)
```

#### Paso 1.5: Deprecar SessionHistory

```python
# apps/users/models.py

# Marcar como deprecated (mantendremos por ahora para no romper)
class SessionHistory(TimeStampedModel):
    """
    DEPRECATED: Use apps.authentication.models.SessionLog
    
    Será removido en próxima versión.
    """
    ...
```

---

### FASE 2: Crear apps/authentication/ (8-10 horas)

Ver ANALISIS_APP_AUTHENTICATION_v3_0_0 (3 partes) para implementación completa.

```bash
# Crear app
python manage.py startapp authentication apps/authentication

# Estructura:
apps/authentication/
├── models.py (4 modelos)
├── constants.py
├── exceptions.py (4 excepciones)
├── utils.py (helpers)
├── services/
│   ├── authentication.py
│   ├── recovery.py
│   ├── lockout.py
│   └── session.py
├── serializers/
│   ├── auth.py
│   ├── recovery.py
│   └── session.py
├── viewsets.py (AuthViewSet, SessionViewSet)
├── urls.py
├── admin.py
├── tasks.py (APScheduler)
└── tests/

# Registrar en settings
INSTALLED_APPS += ['apps.authentication']

# Migraciones
python manage.py makemigrations authentication
python manage.py migrate

# Fixtures (10 preguntas de seguridad)
python manage.py loaddata security_questions.json
```

---

### FASE 3: Crear apps/access/ (12-15 horas)

Ver ANALISIS_APP_ACCESS_v3_0_0 (6 partes) para implementación completa.

```bash
# Crear app
python manage.py startapp access apps/access

# Estructura:
apps/access/
├── models.py (6 modelos)
├── constants.py
├── exceptions.py
├── services/
│   ├── rbac.py (RBACService)
│   ├── group.py (GroupService)
│   └── cache.py (PermissionCacheService)
├── permissions.py (DynamicFunctionPermission)
├── decorators.py (@require_function)
├── middleware.py (RBACMiddleware)
├── serializers/
├── viewsets.py (8 ViewSets)
├── urls.py
├── admin.py
└── tests/

# Registrar
INSTALLED_APPS += ['apps.access']
MIDDLEWARE += ['apps.access.middleware.RBACMiddleware']

# Migraciones
python manage.py makemigrations access
python manage.py migrate

# Fixtures (11 modules + 46 functions + 5 groups)
python manage.py loaddata modules.json
python manage.py loaddata functions.json
python manage.py loaddata groups.json
```

---

### FASE 4: Crear apps/alerts/ (6-8 horas)

```bash
# Crear app
python manage.py startapp alerts apps/alerts

# Estructura:
apps/alerts/
├── __init__.py
├── apps.py
├── models.py (5 modelos)
│   - InternalMessage
│   - MessageRecipient (M2M through)
│   - AlertConfiguration
│   - AlertSubscription
│   - AlertLog
├── constants.py
│   - MAX_RECIPIENTS = 50
│   - MESSAGE_RETENTION_DAYS = 90
│   - MAX_MESSAGES_PER_HOUR = 100
│   - PRIORITY_CHOICES
├── validators.py (3 validators)
│   - MaxRecipientsValidator
│   - RateLimitValidator
│   - AttachmentSizeValidator
├── services/
│   ├── __init__.py
│   ├── alert.py (AlertService)
│   ├── configuration.py (ConfigurationService)
│   └── subscription.py (SubscriptionService)
├── serializers/
│   ├── __init__.py
│   ├── message.py (InternalMessageSerializer, MessageRecipientSerializer)
│   ├── configuration.py
│   └── subscription.py
├── viewsets.py (3 ViewSets con RBAC)
│   - InternalMessageViewSet
│   - AlertConfigurationViewSet
│   - AlertSubscriptionViewSet
├── urls.py (12 endpoints)
├── admin.py
├── management/
│   └── commands/
│       └── auto_archive_messages.py (cronjob diario)
└── tests/
    ├── test_models.py
    ├── test_services.py
    ├── test_validators.py
    └── test_viewsets.py

# Registrar
INSTALLED_APPS += ['apps.alerts']

# Migraciones
python manage.py makemigrations alerts
python manage.py migrate

# Configurar cronjob
# Opción 1: crontab
0 3 * * * cd /path/to/project && python manage.py auto_archive_messages

# Opción 2: APScheduler (apps/core/scheduler.py)
from apscheduler.schedulers.background import BackgroundScheduler
scheduler.add_job(
    'apps.alerts.management.commands.auto_archive_messages:Command.handle',
    'cron',
    hour=3,
    minute=0
)
```

**Detalles de Implementación:**

```python
# apps/alerts/services/alert.py - AlertService

class AlertService:
    """
    Servicio principal de alertas (CNST-001).
    """
    
    @transaction.atomic
    def send_message(
        self,
        sender: User,
        recipients: List[User],
        subject: str,
        body: str,
        priority: str = 'info'
    ) -> InternalMessage:
        """
        Envía mensaje interno.
        
        CNST-001: NO email, solo BD
        CNST-024: Max 50 destinatarios
        """
        # Validar límites
        if len(recipients) > MAX_RECIPIENTS:
            raise ValidationError(f"Máximo {MAX_RECIPIENTS} destinatarios")
        
        # Crear mensaje
        message = InternalMessage.objects.create(
            sender=sender,
            subject=subject,
            body=body,
            priority=priority
        )
        
        # Crear destinatarios
        for recipient in recipients:
            MessageRecipient.objects.create(
                message=message,
                recipient=recipient,
                is_read=False
            )
        
        return message
    
    def send_system_alert(
        self,
        recipients: List[User],
        subject: str,
        body: str,
        priority: str = 'warning'
    ) -> InternalMessage:
        """
        Envía alerta del sistema.
        
        sender = User System (username='system')
        """
        system_user = User.objects.get(username='system')
        return self.send_message(
            sender=system_user,
            recipients=recipients,
            subject=subject,
            body=body,
            priority=priority
        )
```

**Integration con apps/authentication/:**

```python
# apps/authentication/services/recovery.py - RecoveryService

def reset_password_by_questions(self, username, answers, new_pwd):
    """Reset password con preguntas de seguridad."""
    
    user = User.objects.get(username=username)
    
    # Verificar si tiene preguntas configuradas
    if UserSecurityAnswer.objects.filter(user=user).count() < 5:
        # ✅ ENVIAR ALERT (CNST-001: NO email)
        from apps.alerts.services import AlertService
        
        alert_service = AlertService()
        alert_service.send_system_alert(
            recipients=[user],
            subject="⚠️ No se puede resetear password",
            body=(
                "No has configurado tus preguntas de seguridad.\n"
                "Contacta a un administrador con permiso USR_EDIT "
                "para resetear tu password."
            ),
            priority='warning'
        )
        
        raise ValidationError("No security questions configured")
    
    # Verificar respuestas
    if not self.verify_security_answers(user, answers):
        raise ValidationError("Incorrect answers")
    
    # Cambiar password
    user.set_password(new_pwd)
    user.save()
    
    # ✅ ENVIAR ALERT de confirmación
    alert_service.send_system_alert(
        recipients=[user],
        subject="✅ Password cambiado exitosamente",
        body="Tu password ha sido cambiado mediante preguntas de seguridad.",
        priority='info'
    )
```

**Cronjob para recordatorios diarios:**

```python
# apps/alerts/management/commands/auto_archive_messages.py

from django.core.management.base import BaseCommand
from apps.alerts.services import AlertService

class Command(BaseCommand):
    help = 'Archiva mensajes antiguos (>90 días)'
    
    def handle(self, *args, **options):
        service = AlertService()
        result = service.auto_archive_old_messages()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Archived {result['archived_count']} messages"
            )
        )
```

```python
# apps/authentication/tasks.py (para recordatorios de preguntas)

from apps.alerts.services import AlertService
from apps.users.models import User

def send_security_questions_reminders():
    """
    Recordatorio diario a usuarios sin preguntas configuradas.
    
    Cron: 9 AM daily
    """
    # Usuarios sin preguntas (o con menos de 5)
    users_without_questions = User.objects.filter(
        is_active=True
    ).exclude(
        id__in=UserSecurityAnswer.objects.values('user_id')
                .annotate(count=Count('id'))
                .filter(count__gte=5)
                .values_list('user_id', flat=True)
    )
    
    alert_service = AlertService()
    
    for user in users_without_questions:
        alert_service.send_system_alert(
            recipients=[user],
            subject="⚠️ Recordatorio: Configura preguntas de seguridad",
            body=(
                "Por tu seguridad, configura tus 5 preguntas de seguridad.\n\n"
                "Esto te permitirá recuperar tu contraseña sin contactar "
                "a un administrador.\n\n"
                "Ve a: Configuración > Seguridad > Preguntas de Seguridad"
            ),
            priority='warning'
        )
```

---

### FASE 5: Integration (3-4 horas)

#### Actualizar apps/users/ para usar apps/access/

```python
# apps/users/viewsets.py - UserViewSet

from apps.access.permissions import DynamicFunctionPermission

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    # Mapeo de acciones → funciones
    function_map = {
        'list': 'USR_VIEW',
        'retrieve': 'USR_VIEW',
        'create': 'USR_CREATE',
        'update': 'USR_EDIT',
        'partial_update': 'USR_EDIT',
        'destroy': 'USR_DELETE',
        'activate': 'USR_EDIT',
        'deactivate': 'USR_EDIT',
    }
```

#### Actualizar login para first_login

```python
# apps/authentication/viewsets.py - AuthViewSet.login()

@action(detail=False, methods=['post'])
def login(self, request):
    # ... autenticación ...
    
    response_data = {
        'user': UserSerializer(user).data,
        'token': token,
    }
    
    # Detectar first_login (signal de apps/authentication/)
    if hasattr(user, '_first_login_detected'):
        response_data['first_login'] = True
        response_data['force_password_change'] = True
        response_data['message'] = 'Debes cambiar password y configurar 5 preguntas'
    
    # Detectar falta de preguntas
    elif UserSecurityAnswer.objects.filter(user=user).count() < 5:
        response_data['security_questions_pending'] = True
        response_data['message'] = 'Configura tus preguntas de seguridad'
    
    return Response(response_data)
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Limpieza (2h)

```yaml
☐ 1.1 Eliminar AuthViewSet de apps/users/viewsets.py
☐ 1.2 Eliminar LoginSerializer, PasswordResetSerializer
☐ 1.3 Actualizar apps/users/urls.py
☐ 1.4 Eliminar has_function() de User model
☐ 1.5 Marcar SessionHistory como deprecated
☐ 1.6 Tests de users siguen pasando
```

### Fase 2: apps/authentication/ (10h)

```yaml
☐ 2.1 python manage.py startapp authentication
☐ 2.2 Crear 4 modelos (LoginAttempt, SecurityQuestion, UserSecurityAnswer, SessionLog)
☐ 2.3 Crear constants.py, exceptions.py, utils.py
☐ 2.4 Crear 4 services
☐ 2.5 Crear 3 serializers packages
☐ 2.6 Crear AuthViewSet (6 endpoints)
☐ 2.7 Crear SessionViewSet (2 endpoints)
☐ 2.8 Crear urls.py
☐ 2.9 Registrar en INSTALLED_APPS
☐ 2.10 Migraciones
☐ 2.11 Fixture: 10 security questions
☐ 2.12 Tests unitarios (20 tests)
☐ 2.13 Tests integración (15 tests)
```

### Fase 3: apps/access/ (15h)

```yaml
☐ 3.1 python manage.py startapp access
☐ 3.2 Crear 6 modelos
☐ 3.3 Crear RBACService, GroupService, CacheService
☐ 3.4 Crear DynamicFunctionPermission
☐ 3.5 Crear @require_function decorators
☐ 3.6 Crear RBACMiddleware
☐ 3.7 Crear serializers y viewsets
☐ 3.8 Registrar middleware
☐ 3.9 Migraciones
☐ 3.10 Fixtures: 11 modules + 46 functions + 5 groups
☐ 3.11 Tests (30 tests)
```

### Fase 4: apps/alerts/ (8h)

```yaml
☐ 4.1 python manage.py startapp alerts
☐ 4.2 Crear 5 modelos:
     - InternalMessage (mensaje principal)
     - MessageRecipient (M2M through)
     - AlertConfiguration (reglas)
     - AlertSubscription (suscripciones)
     - AlertLog (auditoría)
☐ 4.3 Crear constants.py (MAX_RECIPIENTS, RETENTION_DAYS, etc)
☐ 4.4 Crear validators.py (3 validators)
☐ 4.5 Crear 3 servicios:
     - AlertService (send_message, mark_as_read, auto_archive)
     - ConfigurationService (create_rule, trigger_alert)
     - SubscriptionService (subscribe, get_subscribers)
☐ 4.6 Crear serializers (6 serializers)
☐ 4.7 Crear viewsets (3 ViewSets con RBAC)
☐ 4.8 Crear urls.py (12 endpoints)
☐ 4.9 Crear management command: auto_archive_messages.py
☐ 4.10 Registrar en INSTALLED_APPS
☐ 4.11 Migraciones
☐ 4.12 Configurar cronjob (diario 3 AM)
☐ 4.13 Tests (15 tests)
☐ 4.14 Integración con authentication (ALERTS en reset password)
```

### Fase 5: Integration (4h)

```yaml
☐ 5.1 Actualizar UserViewSet con DynamicFunctionPermission
☐ 5.2 Actualizar login para first_login
☐ 5.3 Integration test: login → set questions → reset password
☐ 5.4 Integration test: create user → first login → force change
☐ 5.5 Integration test: RBAC permissions
```

---

## 📊 TIEMPO TOTAL ESTIMADO

```yaml
Fase 1: Limpieza               2 horas
Fase 2: apps/authentication/  10 horas
Fase 3: apps/access/          15 horas
Fase 4: apps/alerts/           8 horas
Fase 5: Integration            4 horas

TOTAL: 39 horas (5 días de trabajo)
```

---

## 🎯 RESULTADO FINAL ESPERADO

```yaml
Arquitectura:
  ✅ apps/users/ - Solo CRUD usuarios (limpio)
  ✅ apps/authentication/ - Login/logout/seguridad completo
  ✅ apps/access/ - RBAC con 46 funciones
  ✅ apps/alerts/ - Mensajería interna

Funcionalidades:
  ✅ Login con first_login detection
  ✅ Force password change
  ✅ 5 preguntas de seguridad (10 en pool)
  ✅ Password reset SIN email (CNST-001)
  ✅ RBAC function-based (46 funciones)
  ✅ ALERTS diarias a usuarios sin preguntas
  ✅ Session management en BD (CNST-010)
  ✅ Lockout después de 5 intentos
  ✅ Auditoría completa (CNST-031)

Endpoints Totales:
  apps/users/: 9 endpoints
  apps/authentication/: 9 endpoints (7 auth + 2 sessions)
  apps/access/: 10 endpoints
  apps/alerts/: 14 endpoints (7 messages + 4 config + 3 subs)
  
  TOTAL: 42 endpoints REST

Tests:
  apps/users/: 52 tests (existentes)
  apps/authentication/: 35 tests
  apps/access/: 30 tests
  apps/alerts/: 15 tests
  
  TOTAL: 132 tests
```

---

**Documento generado:** 2026-01-21  
**Versión:** 1.0.0 FINAL  
**Estado:** ✅ LISTO PARA IMPLEMENTAR  
**Próximo paso:** Ejecutar Fase 1 (Limpieza)
