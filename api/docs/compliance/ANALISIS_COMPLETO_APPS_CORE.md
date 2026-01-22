# ⚠️ CORRECCIONES COMPLETAS - Uso Correcto de apps/core

## 🎯 ANÁLISIS COMPLETO

He analizado TODO apps/core y encontré que el plan de FASE 1 tiene **MÚLTIPLES VIOLACIONES** al no usar los componentes ya existentes.

---

## 📊 COMPONENTES DISPONIBLES EN apps/core

### 1. Abstract Models (apps/core/models.py) ✅

```python
# Ya existen estos abstract models:
from apps.core.models import TimeStampedModel        # created_at, updated_at
from apps.core.models import SoftDeleteMixin         # is_deleted, deleted_at
from apps.core.models import AuditedModel            # created_by, updated_by
from apps.core.models import CompleteBaseModel       # Combina los 3
from apps.core.models import SoftDeleteManager       # Manager con active()/deleted()
```

### 2. Permissions DRF (apps/core/permissions.py) ✅

```python
# Ya existen estos permissions:
from apps.core.permissions import RequiresFunctionPermission  # RBAC function_map
from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.permissions import IsSuperUserOrReadOnly
from apps.core.permissions import AllowOptionsAuthentication
from apps.core.permissions import HasServiceAccess
from apps.core.permissions import IsStaffOrReadOnly
```

### 3. ViewSet Mixins (apps/core/mixins.py) ✅

```python
# Ya existen estos mixins:
from apps.core.mixins import SoftDeleteViewSetMixin   # restore/hard-delete actions
from apps.core.mixins import ServiceFilterMixin       # Filtra por servicios
from apps.core.mixins import AuditMixin               # created_by, updated_by auto
from apps.core.mixins import PaginationControlMixin   # paginate=false
from apps.core.mixins import ExportMixin              # export to CSV
```

### 4. Services (apps/core/services/base_service.py) ✅

```python
from apps.core.services.base_service import BaseService

class MyService(BaseService):
    def __init__(self):
        super().__init__()
        self.log_info("Service initialized")  # ✅ Logging automático
```

### 5. Exceptions (apps/core/exceptions.py) ✅

```python
from apps.core.exceptions import IACTBaseException
from apps.core.exceptions import ValidationError
from apps.core.exceptions import BusinessRuleError
from apps.core.exceptions import PermissionDeniedError
from apps.core.exceptions import ResourceNotFoundError
from apps.core.exceptions import ETLError
```

### 6. Validators (apps/core/validators.py) ✅

```python
from apps.core.validators import PhoneValidator
from apps.core.validators import EmailValidator
from apps.core.validators import NITValidator
from apps.core.validators import DateRangeValidator
from apps.core.validators import PositiveIntegerValidator
```

### 7. Helpers (apps/utils/helpers.py) ✅

```python
from apps.utils.helpers import get_client_ip, get_user_agent
from apps.utils.helpers import generate_uuid, generate_short_uuid
from apps.utils.helpers import hash_string, generate_random_token
from apps.utils.helpers import safe_get, merge_dicts
from apps.utils.helpers import chunk_list, flatten_list, unique_list
```

---

## ❌ VIOLACIONES EN EL PLAN FASE 1

### VIOLACIÓN #1: Models SIN Abstract Models

**INCORRECTO en PARTE 1:**
```python
# ❌ apps/authentication/models.py
class LoginAttempt(models.Model):
    user = models.ForeignKey(User, ...)
    username = models.CharField(...)
    attempted_at = models.DateTimeField(auto_now_add=True)  # ❌ Duplica TimeStampedModel
```

**CORRECTO:**
```python
# ✅ apps/authentication/models.py
from apps.core.models import TimeStampedModel

class LoginAttempt(TimeStampedModel):  # ✅ Hereda created_at, updated_at
    user = models.ForeignKey(User, ...)
    username = models.CharField(...)
    # attempted_at ya NO es necesario, usar created_at
```

### VIOLACIÓN #2: Models SIN SoftDeleteMixin

**INCORRECTO:**
```python
# ❌ SecurityQuestion sin soft delete
class SecurityQuestion(models.Model):
    question = models.CharField(...)
    is_active = models.BooleanField(default=True)  # ❌ Usar SoftDeleteMixin
```

**CORRECTO:**
```python
# ✅ Usar SoftDeleteMixin
from apps.core.models import TimeStampedModel, SoftDeleteMixin, SoftDeleteManager

class SecurityQuestion(TimeStampedModel, SoftDeleteMixin):  # ✅
    question = models.CharField(...)
    is_active = models.BooleanField(default=True)
    
    objects = SoftDeleteManager()  # ✅ Manager con active()/deleted()
    
    class Meta:
        db_table = 'tbl_preguntas_seguridad'
```

### VIOLACIÓN #3: Models SIN AuditedModel

**INCORRECTO:**
```python
# ❌ UserSecurityAnswer sin auditoría
class UserSecurityAnswer(models.Model):
    user = models.ForeignKey(User, ...)
    question = models.ForeignKey(SecurityQuestion, ...)
    created_at = models.DateTimeField(auto_now_add=True)  # ❌ Duplica
    updated_at = models.DateTimeField(auto_now=True)      # ❌ Duplica
```

**CORRECTO:**
```python
# ✅ Usar CompleteBaseModel
from apps.core.models import CompleteBaseModel, SoftDeleteManager

class UserSecurityAnswer(CompleteBaseModel):  # ✅ 
    # Automáticamente tiene:
    # - created_at, updated_at (TimeStampedModel)
    # - is_deleted, deleted_at (SoftDeleteMixin)
    # - created_by, updated_by (AuditedModel)
    
    user = models.ForeignKey(User, ...)
    question = models.ForeignKey(SecurityQuestion, ...)
    answer_hash = models.CharField(...)
    
    objects = SoftDeleteManager()
    
    class Meta:
        db_table = 'tbl_respuestas_seguridad'
```

### VIOLACIÓN #4: Exceptions DRF NO Heredan de IACTBaseException

**INCORRECTO en PARTE 1:**
```python
# ❌ apps/authentication/exceptions.py
from rest_framework.exceptions import APIException

class InvalidCredentialsError(APIException):  # ❌ No hereda de IACTBaseException
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Usuario o contraseña inválidos.'
```

**CORRECTO:**
```python
# ✅ Heredar de ambas o usar core
from rest_framework.exceptions import APIException
from apps.core.exceptions import IACTBaseException

class AuthenticationError(APIException, IACTBaseException):  # ✅ Hereda de ambas
    """Base exception para errores de autenticación."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Error de autenticación.'

class InvalidCredentialsError(AuthenticationError):
    default_detail = 'Usuario o contraseña inválidos.'
```

### VIOLACIÓN #5: Services SIN BaseService

**Ya corregido en FASE_1_PARTE_2_CORREGIDA.md** ✅

```python
# ✅ CORRECTO
from apps.core.services.base_service import BaseService

class LockoutService(BaseService):
    def __init__(self):
        super().__init__()
        self.log_info("LockoutService initialized")
```

### VIOLACIÓN #6: Utils Duplicados

**Ya corregido en FASE_1_PARTE_2_CORREGIDA.md** ✅

```python
# ✅ CORRECTO - NO crear apps/authentication/utils.py
from apps.utils.helpers import get_client_ip, get_user_agent
```

### VIOLACIÓN #7: Permissions NO Usan RequiresFunctionPermission

**INCORRECTO (si se implementara así):**
```python
# ❌ Crear custom permission desde cero
class AuthPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Lógica custom...
```

**CORRECTO:**
```python
# ✅ Usar RequiresFunctionPermission de core
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import RequiresFunctionPermission

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    function_map = {
        'login': 'auth.login',           # permission_django
        'logout': 'auth.logout',
        'change_password': 'auth.change_password',
    }
```

### VIOLACIÓN #8: ViewSets NO Usan Mixins de Core

**INCORRECTO (si se implementara así):**
```python
# ❌ ViewSet sin mixins de core
class AuthViewSet(viewsets.ViewSet):
    def list(self, request):
        # Código custom...
```

**CORRECTO:**
```python
# ✅ Usar mixins de core
from apps.core.mixins import AuditMixin, PaginationControlMixin

class SessionViewSet(AuditMixin, PaginationControlMixin, viewsets.ModelViewSet):
    queryset = SessionLog.objects.all()
    serializer_class = SessionLogSerializer
    
    # created_by y updated_by se setean automáticamente ✅
    # paginación controlable con ?paginate=false ✅
```

---

## ✅ PLAN FASE 1 CORREGIDO - PARTE 1

### Models CORRECTOS

```python
"""
apps/authentication/models.py

CORRECCIONES APLICADAS:
✅ Heredar de TimeStampedModel (NO duplicar created_at, updated_at)
✅ Heredar de SoftDeleteMixin donde aplique
✅ Heredar de AuditedModel para auditoría
✅ Usar SoftDeleteManager
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.models import (  # ✅ Importar de core
    TimeStampedModel,
    SoftDeleteMixin,
    AuditedModel,
    CompleteBaseModel,
    SoftDeleteManager
)

User = get_user_model()


# ============================================================================
# LOGIN ATTEMPT - Solo TimeStampedModel
# ============================================================================

class LoginAttempt(TimeStampedModel):  # ✅ Hereda created_at, updated_at
    """
    Registro de intento de login (exitoso o fallido).
    
    CNST-031: Auditoría immutable de todos los intentos.
    
    Hereda de TimeStampedModel:
    - created_at (attempted_at en el plan original)
    - updated_at
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_attempts',
        db_column='iIdUsuario'
    )
    
    username = models.CharField(
        'Username Intentado',
        max_length=150,
        db_column='cUsername'
    )
    
    success = models.BooleanField(
        'Exitoso',
        db_column='bExitoso'
    )
    
    ip_address = models.GenericIPAddressField(
        'IP Address',
        db_column='cIpAddress'
    )
    
    user_agent = models.CharField(
        'User Agent',
        max_length=255,
        blank=True,
        db_column='cUserAgent'
    )
    
    # ❌ NO CREAR attempted_at - usar created_at de TimeStampedModel
    
    class Meta:
        db_table = 'tbl_intentos_login'
        verbose_name = 'Intento de Login'
        verbose_name_plural = 'Intentos de Login'
        ordering = ['-created_at']  # ✅ Usar created_at en vez de attempted_at
        indexes = [
            models.Index(fields=['username', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['success', '-created_at']),
        ]
    
    def __str__(self):
        status = 'SUCCESS' if self.success else 'FAILED'
        return f"{self.username} - {status} - {self.created_at}"  # ✅ created_at


# ============================================================================
# SECURITY QUESTION - TimeStampedModel + SoftDeleteMixin
# ============================================================================

class SecurityQuestion(TimeStampedModel, SoftDeleteMixin):  # ✅
    """
    Pregunta de seguridad predefinida.
    
    CNST-001: Pool de 10 preguntas, usuario responde 5.
    
    Hereda:
    - TimeStampedModel: created_at, updated_at
    - SoftDeleteMixin: is_deleted, deleted_at, delete(), restore()
    """
    
    question = models.CharField(
        'Pregunta',
        max_length=255,
        unique=True,
        db_column='cPregunta'
    )
    
    is_active = models.BooleanField(
        'Activa',
        default=True,
        db_column='bActiva'
    )
    
    order = models.IntegerField(
        'Orden',
        default=0,
        db_column='iOrden'
    )
    
    # ❌ NO CREAR created_at - heredado de TimeStampedModel
    
    objects = SoftDeleteManager()  # ✅ Manager con active()/deleted()
    
    class Meta:
        db_table = 'tbl_preguntas_seguridad'
        verbose_name = 'Pregunta de Seguridad'
        verbose_name_plural = 'Preguntas de Seguridad'
        ordering = ['order', 'question']
        indexes = [
            models.Index(fields=['is_active', 'order']),
            models.Index(fields=['is_deleted']),  # ✅ Para queries con SoftDeleteManager
        ]
    
    def __str__(self):
        return self.question


# ============================================================================
# USER SECURITY ANSWER - CompleteBaseModel
# ============================================================================

class UserSecurityAnswer(CompleteBaseModel):  # ✅ Combina los 3
    """
    Respuesta de usuario a pregunta de seguridad.
    
    CNST-001: Hash PBKDF2, normalización lowercase.
    
    Hereda CompleteBaseModel:
    - TimeStampedModel: created_at, updated_at
    - SoftDeleteMixin: is_deleted, deleted_at, delete(), restore()
    - AuditedModel: created_by, updated_by
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='security_answers',
        db_column='iIdUsuario'
    )
    
    question = models.ForeignKey(
        SecurityQuestion,
        on_delete=models.PROTECT,
        db_column='iIdPregunta'
    )
    
    answer_hash = models.CharField(
        'Hash Respuesta',
        max_length=255,
        db_column='cHashRespuesta'
    )
    
    # ❌ NO CREAR created_at, updated_at - heredados de CompleteBaseModel
    # ❌ NO CREAR created_by, updated_by - heredados de CompleteBaseModel
    # ❌ NO CREAR is_deleted, deleted_at - heredados de CompleteBaseModel
    
    objects = SoftDeleteManager()  # ✅
    
    class Meta:
        db_table = 'tbl_respuestas_seguridad'
        verbose_name = 'Respuesta de Seguridad'
        verbose_name_plural = 'Respuestas de Seguridad'
        unique_together = [['user', 'question']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_deleted']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.question.question[:30]}..."
    
    def set_answer(self, answer: str):
        """Hashea y guarda la respuesta."""
        normalized = answer.lower().strip()
        
        if not normalized:
            raise ValidationError("La respuesta no puede estar vacía")
        
        self.answer_hash = make_password(normalized)
    
    def check_answer(self, answer: str) -> bool:
        """Verifica si la respuesta es correcta."""
        normalized = answer.lower().strip()
        return check_password(normalized, self.answer_hash)


# ============================================================================
# SESSION LOG - CompleteBaseModel
# ============================================================================

class SessionLog(CompleteBaseModel):  # ✅
    """
    Log de sesión de usuario.
    
    CNST-031: Auditoría de sesiones
    CNST-010: Sessions en DB
    
    Hereda CompleteBaseModel:
    - TimeStampedModel: created_at (login_at), updated_at
    - SoftDeleteMixin: is_deleted, deleted_at
    - AuditedModel: created_by, updated_by
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='session_logs',
        db_column='iIdUsuario'
    )
    
    session_key = models.CharField(
        'Session Key',
        max_length=40,
        db_column='cSessionKey'
    )
    
    ip_address = models.GenericIPAddressField(
        'IP Address',
        db_column='cIpAddress'
    )
    
    user_agent = models.CharField(
        'User Agent',
        max_length=255,
        blank=True,
        db_column='cUserAgent'
    )
    
    # ✅ login_at = created_at (heredado)
    # ❌ NO CREAR login_at - usar created_at de TimeStampedModel
    
    logout_at = models.DateTimeField(
        'Logout',
        null=True,
        blank=True,
        db_column='dtLogout'
    )
    
    is_active = models.BooleanField(
        'Activa',
        default=True,
        db_column='bActiva'
    )
    
    objects = SoftDeleteManager()  # ✅
    
    class Meta:
        db_table = 'tbl_log_sesiones'
        verbose_name = 'Log de Sesión'
        verbose_name_plural = 'Logs de Sesiones'
        ordering = ['-created_at']  # ✅ login_at = created_at
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_key']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_deleted']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"  # ✅
    
    @property
    def duration(self):
        """Duración de la sesión."""
        if self.logout_at:
            return self.logout_at - self.created_at  # ✅ login_at = created_at
        elif self.is_active:
            return timezone.now() - self.created_at  # ✅
        return None
```

---

## 📊 TABLA DE CORRECCIONES

| Componente | Incorrecto ❌ | Correcto ✅ |
|------------|--------------|-------------|
| **LoginAttempt** | models.Model + attempted_at | TimeStampedModel + created_at |
| **SecurityQuestion** | models.Model + created_at | TimeStampedModel + SoftDeleteMixin |
| **UserSecurityAnswer** | models.Model + created_at + updated_at | CompleteBaseModel |
| **SessionLog** | models.Model + login_at + created_at | CompleteBaseModel + created_at |
| **Exceptions** | APIException solamente | APIException + IACTBaseException |
| **Services** | Sin BaseService | BaseService con logging |
| **Utils** | Crear apps/authentication/utils.py | Importar de apps.utils |
| **Permissions** | Custom desde cero | RequiresFunctionPermission |
| **ViewSets** | Sin mixins | AuditMixin, PaginationControlMixin |

---

## ✅ CHECKLIST CORRECCIONES

### PARTE 1: Models + Constants + Exceptions

- [ ] LoginAttempt hereda de TimeStampedModel
- [ ] LoginAttempt usa created_at (NO attempted_at)
- [ ] SecurityQuestion hereda de TimeStampedModel + SoftDeleteMixin
- [ ] SecurityQuestion usa SoftDeleteManager
- [ ] UserSecurityAnswer hereda de CompleteBaseModel
- [ ] UserSecurityAnswer NO define created_at, updated_at, created_by, updated_by
- [ ] SessionLog hereda de CompleteBaseModel
- [ ] SessionLog usa created_at como login_at
- [ ] Exceptions heredan de IACTBaseException + APIException
- [ ] Todos los models con is_deleted tienen Index en ese campo

### PARTE 2: Services Base

- [ ] LockoutService hereda de BaseService
- [ ] AuthenticationService hereda de BaseService
- [ ] Usar get_client_ip() de apps.utils.helpers
- [ ] Usar get_user_agent() de apps.utils.helpers
- [ ] NO crear apps/authentication/utils.py

### PARTE 5: ViewSets + URLs

- [ ] ViewSets usan RequiresFunctionPermission
- [ ] ViewSets usan AuditMixin si aplica
- [ ] function_map usa permission_django (NO code)

---

## 🎯 BENEFICIOS

```yaml
DRY (Don't Repeat Yourself):
  ✅ NO duplicar created_at, updated_at
  ✅ NO duplicar is_deleted, deleted_at
  ✅ NO duplicar created_by, updated_by
  ✅ Reutilizar SoftDeleteManager
  ✅ Reutilizar permissions de core

Consistencia:
  ✅ Todos los models usan mismos abstract models
  ✅ Todos los services usan BaseService
  ✅ Todos los ViewSets usan mismos mixins
  ✅ Logging estandarizado

Mantenibilidad:
  ✅ Cambios en abstract models se reflejan en todos
  ✅ Menos código que mantener
  ✅ Menos tests necesarios (abstract models ya testados)
```

---

**Documento generado:** 2026-01-21  
**Versión:** 3.0.0 COMPLETA  
**Estado:** ✅ ANÁLISIS COMPLETO DE APPS/CORE
