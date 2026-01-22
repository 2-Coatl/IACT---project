# 🔧 PLAN DE CORRECCIÓN CNST-010: Eliminar Cache y Usar Base de Datos

## 🎯 OBJETIVO

Corregir violación crítica CNST-010 reemplazando el uso de cache (LocMemCache/Redis) con almacenamiento persistente en base de datos PostgreSQL.

---

## 📋 RESUMEN EJECUTIVO

```yaml
Problema:
  LockoutService usa django.core.cache (PROHIBIDO)
  Backend: LocMemCache (volátil)
  
Solución:
  Crear modelo LoginLockout en BD
  Refactorizar LockoutService
  
Tiempo: 2h 40min
Archivos: 8 modificados, 1 nuevo
Commits: 1 commit de corrección
Tag: fix-cnst-010-v1.0.0
```

---

## 🔄 PLAN EN 6 PARTES

### ✅ PARTE A: Crear Modelo LoginLockout (30 min)

#### A.1 Agregar modelo a apps/authentication/models.py

```python
# apps/authentication/models.py

class LoginLockout(TimeStampedModel):
    """
    Tracking de bloqueo de cuentas por intentos fallidos.
    
    Reemplaza cache volátil con persistencia en BD.
    CUMPLE: CNST-010 (NO cache/Redis permitido)
    
    Attributes:
        username: Username del usuario (único)
        failed_attempts: Contador de intentos fallidos
        locked_until: Timestamp hasta cuando está bloqueado
        last_attempt_at: Último intento registrado
    
    Usage:
        # Verificar bloqueo
        lockout = LoginLockout.objects.get(username='user')
        if lockout.is_locked():
            # Usuario bloqueado
            
        # Registrar intento
        lockout.increment_attempts()
        
        # Bloquear
        lockout.lock(duration_minutes=30)
        
        # Desbloquear
        lockout.unlock()
    """
    
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        help_text="Username del usuario"
    )
    
    failed_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Número de intentos fallidos"
    )
    
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Bloqueado hasta este timestamp (None = no bloqueado)"
    )
    
    last_attempt_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp del último intento"
    )
    
    class Meta:
        db_table = 'authentication_login_lockout'
        verbose_name = 'Login Lockout'
        verbose_name_plural = 'Login Lockouts'
        indexes = [
            models.Index(fields=['username', 'locked_until'], name='idx_username_locked'),
            models.Index(fields=['last_attempt_at'], name='idx_last_attempt'),
        ]
        ordering = ['-last_attempt_at']
    
    def __str__(self):
        status = "LOCKED" if self.is_locked() else "ACTIVE"
        return f"{self.username} - {self.failed_attempts} attempts ({status})"
    
    def is_locked(self) -> bool:
        """
        Verifica si el usuario aún está bloqueado.
        
        Returns:
            True si locked_until es futuro, False si expiró o no está bloqueado
        """
        if not self.locked_until:
            return False
        
        from django.utils import timezone
        return timezone.now() < self.locked_until
    
    def increment_attempts(self) -> int:
        """
        Incrementa el contador de intentos fallidos.
        
        Returns:
            Nuevo número de intentos
        """
        self.failed_attempts += 1
        self.save(update_fields=['failed_attempts', 'last_attempt_at'])
        return self.failed_attempts
    
    def lock(self, duration_minutes: int) -> None:
        """
        Bloquea la cuenta por X minutos.
        
        Args:
            duration_minutes: Duración del bloqueo en minutos
        """
        from django.utils import timezone
        from datetime import timedelta
        
        self.locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['locked_until'])
    
    def unlock(self) -> None:
        """
        Desbloquea la cuenta y resetea contador.
        """
        self.failed_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_attempts', 'locked_until', 'last_attempt_at'])
    
    @classmethod
    def cleanup_expired(cls, days: int = 30) -> int:
        """
        Elimina registros antiguos (lockouts expirados hace > X días).
        
        Args:
            days: Días de antigüedad para eliminar
            
        Returns:
            Número de registros eliminados
        """
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff = timezone.now() - timedelta(days=days)
        
        # Eliminar registros:
        # - No bloqueados (locked_until=None)
        # - Con último intento > X días atrás
        deleted, _ = cls.objects.filter(
            locked_until__isnull=True,
            last_attempt_at__lt=cutoff
        ).delete()
        
        return deleted
```

#### A.2 Actualizar __all__ en models.py

```python
# apps/authentication/models.py

__all__ = [
    'LoginAttempt',
    'SecurityQuestion',
    'UserSecurityAnswer',
    'SessionLog',
    'LoginLockout',  # ✅ NUEVO
]
```

#### A.3 Crear migración

```bash
cd /tmp/iact-real/callcentersite
python manage.py makemigrations authentication --name add_login_lockout_model
```

**Output esperado:**
```
Migrations for 'authentication':
  apps/authentication/migrations/0002_add_login_lockout_model.py
    - Create model LoginLockout
    - Create index idx_username_locked
    - Create index idx_last_attempt
```

#### A.4 Aplicar migración

```bash
python manage.py migrate authentication
```

**Output esperado:**
```
Running migrations:
  Applying authentication.0002_add_login_lockout_model... OK
```

---

### ✅ PARTE B: Refactorizar LockoutService (1h)

#### B.1 Actualizar imports

```python
# apps/authentication/services/lockout.py

# ANTES ❌
from django.core.cache import cache

# DESPUÉS ✅
from apps.authentication.models import LoginLockout
from django.db import transaction
from django.utils import timezone
```

#### B.2 Refactorizar método `is_locked()`

```python
# ANTES (con cache) ❌
def is_locked(self, username: str) -> bool:
    cache_key = CACHE_KEY_LOCKOUT.format(username=username)
    locked_until = cache.get(cache_key)
    
    if not locked_until:
        return False
    
    # Verificar si lockout expiró
    if timezone.now() >= locked_until:
        # Lockout expiró, limpiar cache
        cache.delete(cache_key)
        return False
    
    return True

# DESPUÉS (con BD) ✅
def is_locked(self, username: str) -> bool:
    """
    Verifica si usuario está bloqueado.
    
    Args:
        username: Username a verificar
        
    Returns:
        True si bloqueado, False si no
    """
    try:
        lockout = LoginLockout.objects.get(username=username)
        
        is_locked = lockout.is_locked()
        
        # Si lockout expiró, limpiar registro
        if not is_locked and lockout.locked_until:
            lockout.unlock()
        
        return is_locked
        
    except LoginLockout.DoesNotExist:
        return False
```

#### B.3 Refactorizar método `record_failed_attempt()`

```python
# ANTES (con cache) ❌
def record_failed_attempt(self, username: str) -> int:
    cache_key = CACHE_KEY_FAILED_ATTEMPTS.format(username=username)
    
    # Incrementar contador en cache
    attempts = cache.get(cache_key, 0) + 1
    
    # Guardar en cache por la ventana de tiempo
    cache.set(cache_key, attempts, self.window_minutes * 60)
    
    self.log_warning(
        f"Failed login attempt #{attempts} for user: {username}"
    )
    
    # Si alcanzó max intentos, bloquear
    if attempts >= self.max_attempts:
        self._lock_account(username)
        self.log_warning(
            f"Account locked for {username} after {attempts} failed attempts"
        )
    
    return attempts

# DESPUÉS (con BD) ✅
@transaction.atomic
def record_failed_attempt(self, username: str) -> int:
    """
    Registra intento fallido de login.
    
    Incrementa contador y bloquea si alcanza máximo.
    
    Args:
        username: Username del intento fallido
        
    Returns:
        Número actual de intentos fallidos
    """
    # Obtener o crear registro de lockout
    lockout, created = LoginLockout.objects.get_or_create(
        username=username,
        defaults={'failed_attempts': 0}
    )
    
    # Si ya está bloqueado, no incrementar
    if lockout.is_locked():
        self.log_info(f"Account {username} already locked")
        return lockout.failed_attempts
    
    # Incrementar contador
    attempts = lockout.increment_attempts()
    
    self.log_warning(
        f"Failed login attempt #{attempts} for user: {username}"
    )
    
    # Si alcanzó máximo, bloquear
    if attempts >= self.max_attempts:
        self._lock_account(username, lockout)
        self.log_warning(
            f"Account locked for {username} after {attempts} failed attempts"
        )
    
    return attempts
```

#### B.4 Refactorizar método `get_failed_attempts_count()`

```python
# ANTES (con cache) ❌
def get_failed_attempts_count(self, username: str) -> int:
    cache_key = CACHE_KEY_FAILED_ATTEMPTS.format(username=username)
    return cache.get(cache_key, 0)

# DESPUÉS (con BD) ✅
def get_failed_attempts_count(self, username: str) -> int:
    """
    Obtiene número de intentos fallidos.
    
    Args:
        username: Username a consultar
        
    Returns:
        Número de intentos (0 si no existe)
    """
    try:
        lockout = LoginLockout.objects.get(username=username)
        return lockout.failed_attempts if not lockout.is_locked() else 0
    except LoginLockout.DoesNotExist:
        return 0
```

#### B.5 Refactorizar método `reset_failed_attempts()`

```python
# ANTES (con cache) ❌
def reset_failed_attempts(self, username: str) -> None:
    cache_key = CACHE_KEY_FAILED_ATTEMPTS.format(username=username)
    cache.delete(cache_key)
    
    self.log_info(f"Reset failed attempts counter for user: {username}")

# DESPUÉS (con BD) ✅
def reset_failed_attempts(self, username: str) -> None:
    """
    Resetea contador de intentos fallidos.
    
    Args:
        username: Username a resetear
    """
    try:
        lockout = LoginLockout.objects.get(username=username)
        lockout.failed_attempts = 0
        lockout.save(update_fields=['failed_attempts', 'last_attempt_at'])
        
        self.log_info(f"Reset failed attempts counter for user: {username}")
    except LoginLockout.DoesNotExist:
        # No existe, no hay nada que resetear
        pass
```

#### B.6 Refactorizar método `unlock_account()`

```python
# ANTES (con cache) ❌
def unlock_account(self, username: str) -> None:
    lockout_key = CACHE_KEY_LOCKOUT.format(username=username)
    attempts_key = CACHE_KEY_FAILED_ATTEMPTS.format(username=username)
    
    cache.delete(lockout_key)
    cache.delete(attempts_key)
    
    self.log_info(f"Account unlocked manually for user: {username}")

# DESPUÉS (con BD) ✅
def unlock_account(self, username: str) -> None:
    """
    Desbloquea cuenta manualmente.
    
    Resetea contador y lockout.
    
    Args:
        username: Username a desbloquear
    """
    try:
        lockout = LoginLockout.objects.get(username=username)
        lockout.unlock()
        
        self.log_info(f"Account unlocked manually for user: {username}")
    except LoginLockout.DoesNotExist:
        # No existe, crear con valores limpios
        LoginLockout.objects.create(
            username=username,
            failed_attempts=0,
            locked_until=None
        )
```

#### B.7 Refactorizar método `_lock_account()`

```python
# ANTES (con cache) ❌
def _lock_account(self, username: str) -> None:
    from datetime import timedelta
    
    locked_until = timezone.now() + timedelta(minutes=self.lockout_duration)
    
    cache_key = CACHE_KEY_LOCKOUT.format(username=username)
    
    # Guardar en cache hasta que expire el bloqueo
    cache.set(cache_key, locked_until, self.lockout_duration * 60)

# DESPUÉS (con BD) ✅
def _lock_account(self, username: str, lockout: LoginLockout = None) -> None:
    """
    Bloquea cuenta por tiempo configurado.
    
    Args:
        username: Username a bloquear
        lockout: Objeto LoginLockout existente (opcional)
    """
    if not lockout:
        try:
            lockout = LoginLockout.objects.get(username=username)
        except LoginLockout.DoesNotExist:
            lockout = LoginLockout.objects.create(
                username=username,
                failed_attempts=self.max_attempts
            )
    
    lockout.lock(duration_minutes=self.lockout_duration)
```

---

### ✅ PARTE C: Actualizar Settings (5 min)

#### C.1 Remover configuración de CACHES

**Archivo:** `config/settings/base.py`

```python
# ANTES ❌
# ==============================================================================
# CACHE
# ==============================================================================
# CNST_TECNICAS: NO Redis
# ==============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'iact-cache',
    }
}

# CNST_TECNICAS: NO Redis
# NO usar django-redis
# NO usar cache distribuido

# DESPUÉS ✅
# ==============================================================================
# CACHE
# ==============================================================================
# CNST-010: NO cache permitido
# Usar SOLO base de datos para persistencia
# ==============================================================================

# CACHES configuración removida - CUMPLE CNST-010
# Toda persistencia debe usar PostgreSQL directamente

# ❌ PROHIBIDO:
# - Redis (django-redis)
# - Memcached
# - LocMemCache (volátil)
# - Cualquier cache backend

# ✅ PERMITIDO:
# - PostgreSQL (único backend de persistencia)
```

---

### ✅ PARTE D: Actualizar Tests (30 min)

#### D.1 Actualizar test_services.py

**Archivo:** `tests/unit/authentication/test_services.py`

```python
# ANTES ❌
def setup_method(self):
    """Setup antes de cada test."""
    self.service = LockoutService()
    cache.clear()

# DESPUÉS ✅
def setup_method(self):
    """Setup antes de cada test."""
    self.service = LockoutService()
    # Limpiar registros de lockout en BD
    from apps.authentication.models import LoginLockout
    LoginLockout.objects.all().delete()
```

#### D.2 Actualizar tests de integración

**Archivo:** `tests/integration/authentication/test_auth_flow.py`

```python
# ANTES ❌
def setup_method(self):
    """Setup para cada test."""
    self.client = APIClient()
    # Implícitamente usa cache

# DESPUÉS ✅
def setup_method(self):
    """Setup para cada test."""
    self.client = APIClient()
    # Limpiar lockouts de tests anteriores
    from apps.authentication.models import LoginLockout
    LoginLockout.objects.all().delete()
```

#### D.3 Verificar que tests pasen

```bash
pytest tests/unit/authentication/test_services.py::TestLockoutService -v
pytest tests/integration/authentication/test_auth_flow.py::TestAccountLockout -v
```

---

### ✅ PARTE E: Actualizar Documentación (20 min)

#### E.1 INTEGRATION_GUIDE.md

```markdown
# ANTES ❌
### 3. Verificar Redis (para lockout)

\```bash
redis-cli ping
\```

**Output esperado:**
\```
PONG
\```

# DESPUÉS ✅
### 3. Verificar Base de Datos

\```bash
python manage.py dbshell
\```

\```sql
-- Verificar tabla de lockout
SELECT * FROM authentication_login_lockout LIMIT 5;
\```

**Nota:** El sistema NO usa Redis (prohibido por CNST-010).
Todo se persiste en PostgreSQL.
```

#### E.2 PLAN_FASE_2_v1.0.0.md

```markdown
# ANTES ❌
### Django Packages
\```python
# Ya instalados
djangorestframework
django-filter
Pillow
django-redis  # Para cache
\```

# DESPUÉS ✅
### Django Packages
\```python
# Ya instalados
djangorestframework
django-filter
Pillow
# NO django-redis (prohibido por CNST-010)
\```
```

#### E.3 FASE_2_QUICK_START.md

```markdown
# ANTES ❌
\```yaml
Pre-requisitos:
  ✅ Redis corriendo
  ✅ PostgreSQL corriendo
\```

# DESPUÉS ✅
\```yaml
Pre-requisitos:
  ✅ PostgreSQL corriendo
  ❌ NO Redis (prohibido CNST-010)
\```
```

#### E.4 FASE_1_PARTE_7_IMPLEMENTADA.md

Remover sección completa de troubleshooting de Redis.

---

### ✅ PARTE F: Cleanup y Verificación (15 min)

#### F.1 Búsqueda de referencias a cache

```bash
# Buscar imports de cache
grep -rn "from django.core.cache import cache" apps/

# Debe retornar VACÍO después de corrección
```

#### F.2 Búsqueda de referencias a Redis

```bash
# Buscar menciones de Redis
grep -ri "redis" apps/ docs/ --exclude-dir=venv

# Solo deben quedar:
# - Documentos de restricciones (explicando que está prohibido)
# - Este plan de corrección
```

#### F.3 Verificación de settings

```bash
# Verificar que NO hay CACHES
grep -n "CACHES" config/settings/base.py

# Debe retornar solo comentarios explicando prohibición
```

#### F.4 Ejecutar todos los tests

```bash
# Tests unitarios
pytest tests/unit/authentication/ -v

# Tests integración
pytest tests/integration/authentication/ -v

# Todos juntos
pytest tests/unit/authentication/ tests/integration/authentication/ -v

# Resultado esperado: 54 passed
```

#### F.5 Django check

```bash
python manage.py check

# Output esperado:
# System check identified no issues (0 silenced).
```

---

## 📊 CHECKLIST DE VERIFICACIÓN

```yaml
Código:
  ✅ Modelo LoginLockout creado
  ✅ Migración 0002 aplicada
  ✅ LockoutService refactorizado
  ✅ NO imports de django.core.cache
  ✅ Settings sin CACHES
  
Tests:
  ✅ 54 tests pasando
  ✅ setup_method() limpia LoginLockout (no cache)
  ✅ Coverage >90%
  
Documentación:
  ✅ INTEGRATION_GUIDE.md actualizado
  ✅ PLAN_FASE_2 actualizado
  ✅ FASE_2_QUICK_START actualizado
  ✅ FASE_1_PARTE_7 actualizado
  
Verificación:
  ✅ grep cache apps/ vacío
  ✅ grep redis apps/ vacío
  ✅ python manage.py check OK
  ✅ Funcionalidad lockout funciona
  
Cumplimiento:
  ✅ CNST-010 100% cumplido
  ✅ Solo PostgreSQL como persistencia
  ✅ Sin cache volátil
  ✅ Production-ready
```

---

## 🚀 COMANDOS DE EJECUCIÓN

```bash
# 1. Crear branch
git checkout -b fix/cnst-010-remove-cache

# 2. PARTE A: Crear modelo
# ... editar apps/authentication/models.py ...
python manage.py makemigrations authentication --name add_login_lockout_model
python manage.py migrate authentication

# 3. PARTE B: Refactorizar service
# ... editar apps/authentication/services/lockout.py ...

# 4. PARTE C: Settings
# ... editar config/settings/base.py ...

# 5. PARTE D: Tests
# ... editar test files ...
pytest tests/unit/authentication/ tests/integration/authentication/ -v

# 6. PARTE E: Docs
# ... editar docs ...

# 7. PARTE F: Verificación
grep -rn "from django.core.cache import cache" apps/
grep -ri "redis" apps/
python manage.py check

# 8. Commit
git add .
git commit -m "FIX: CNST-010 - Remove cache, use PostgreSQL for lockout

Corrección crítica de violación CNST-010:
- Reemplaza cache (LocMemCache) con modelo LoginLockout en BD
- Cumple restricción: Solo PostgreSQL como persistencia
- Mantiene funcionalidad de lockout idéntica
- Mejora: Datos persistentes (sobreviven restart)

Cambios:
- Nuevo modelo: LoginLockout
- Refactorizado: LockoutService (sin cache)
- Removido: CACHES de settings
- Actualizado: Tests y documentación

Tests: 54 passed
Cumplimiento CNST-010: ✅ 100%"

# 9. Tag
git tag -a fix-cnst-010-v1.0.0 -m "Corrección CNST-010: Cache → PostgreSQL"

# 10. Verificación final
pytest tests/unit/authentication/ tests/integration/authentication/ -v
python manage.py check
```

---

## 📈 MÉTRICAS ESPERADAS

```yaml
Antes de corrección:
  CNST-010: ❌ VIOLADO
  Cache Backend: LocMemCache (volátil)
  Persistencia: No (se pierde en restart)
  Multi-server: No compatible
  
Después de corrección:
  CNST-010: ✅ CUMPLIDO
  Persistencia: PostgreSQL (permanente)
  Restart-safe: ✅ Sí
  Multi-server: ✅ Compatible
  Performance: +5ms por operación (aceptable)
```

---

**Plan:** Corrección CNST-010  
**Duración:** 2h 40min  
**Archivos:** 8 modificados, 1 nuevo  
**Severidad:** 🔴 CRÍTICA  
**Estado:** 📋 LISTO PARA EJECUTAR
