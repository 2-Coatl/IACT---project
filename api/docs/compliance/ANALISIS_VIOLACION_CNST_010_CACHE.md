# 🚨 ANÁLISIS CRÍTICO: Violación CNST-010 - Uso de Cache Prohibido

## ❌ PROBLEMA IDENTIFICADO

### Restricción Violada: CNST-010

```yaml
CNST-010: NO Redis
  Descripción: "Prohibido Redis para cache y sessions"
  Severidad: 🔴 CRÍTICO
  Ubicación: RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0_PARTE_1.md
  
  Prohibido ESPECÍFICAMENTE:
    ❌ Redis (django-redis)
    ❌ Memcached
    ❌ LocMemCache (volátil, se pierde en restart)
    ❌ Cualquier cache externo
  
  ÚNICA OPCIÓN PERMITIDA:
    ✅ Base de datos PostgreSQL (persistente)
```

---

## 📍 CÓDIGO VIOLADOR ENCONTRADO

### 1. Configuración en settings (NO CRÍTICO)

**Archivo:** `config/settings/base.py:474-479`

```python
# ⚠️ VIOLACIÓN: LocMemCache está PROHIBIDO (volátil)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # ❌
        'LOCATION': 'iact-cache',
    }
}
```

**Razón de prohibición:**
- LocMemCache es volátil (se pierde con restart del servidor)
- No es persistente
- Según restricciones: "PROHIBIDO - En memoria (volátil)"

---

### 2. Uso en LockoutService (CRÍTICO)

**Archivo:** `apps/authentication/services/lockout.py`

**Líneas violadoras:**
```python
Line 11:  from django.core.cache import cache  # ❌ IMPORTACIÓN

# Uso en métodos:
Line 60-61:  cache_key = CACHE_KEY_LOCKOUT.format(username=username)
             locked_until = cache.get(cache_key)

Line 72:     cache.delete(cache_key)

Line 87:     locked_until = cache.get(cache_key)

Line 111:    attempts = cache.get(cache_key, 0) + 1

Line 114:    cache.set(cache_key, attempts, self.window_minutes * 60)

Line 135:    return cache.get(cache_key, 0)

Line 147:    cache.delete(cache_key)

Line 160-161: cache.delete(lockout_key)
              cache.delete(attempts_key)

Line 178:    cache.set(cache_key, locked_until, self.lockout_duration * 60)
```

**Funcionalidad afectada:**
1. ✅ `is_locked()` - Verifica si usuario está bloqueado
2. ✅ `record_failed_attempt()` - Registra intento fallido
3. ✅ `get_failed_attempts_count()` - Cuenta intentos
4. ✅ `reset_failed_attempts()` - Resetea contador
5. ✅ `unlock_account()` - Desbloquea cuenta
6. ✅ `_lock_account()` - Bloquea cuenta

**Todos estos métodos dependen de cache** ❌

---

### 3. Referencias en Documentación

**Archivos que mencionan Redis/cache:**
- `docs/INTEGRATION_GUIDE.md`: Menciona Redis como requisito
- `docs/plans/PLAN_FASE_2_v1.0.0.md`: Menciona Redis como dependencia
- `docs/plans/FASE_2_QUICK_START.md`: Checklist incluye "Redis corriendo"
- `docs/compliance/FASE_1_PARTE_7_IMPLEMENTADA.md`: Troubleshooting Redis

---

## 🎯 IMPACTO DEL PROBLEMA

### Funcionalidad Afectada

```yaml
Sistema de Bloqueo de Cuentas:
  Estado Actual: FUNCIONAL pero VIOLADOR
  Dependencia: django.core.cache
  Backend: LocMemCache (volátil)
  
  Problemas:
    1. ❌ Viola CNST-010 (restricción crítica)
    2. ❌ Cache volátil (se pierde en restart)
    3. ❌ No persistente
    4. ❌ No funciona en múltiples servidores
    5. ❌ Datos de lockout se pierden
```

### Escenarios Problemáticos

```yaml
Escenario 1: Restart del Servidor
  Antes: Usuario bloqueado por 30 minutos
  Restart: Cache se pierde
  Después: Usuario puede intentar login inmediatamente ❌

Escenario 2: Multiple Servers (Load Balancer)
  Server 1: Usuario tiene 3 intentos fallidos
  Server 2: Usuario tiene 0 intentos (cache separado)
  Resultado: Bypass del lockout ❌

Escenario 3: Deploy
  Antes: 100 usuarios con intentos fallidos registrados
  Deploy: Cache se limpia
  Después: Todos los contadores resetean ❌
```

---

## ✅ SOLUCIÓN: Migrar a Base de Datos

### Opción 1: Modelo en Base de Datos (RECOMENDADA)

**Crear modelo `LoginLockout`:**

```python
# apps/authentication/models.py

class LoginLockout(TimeStampedModel):
    """
    Tracking de lockout de usuarios.
    
    Reemplaza cache con persistencia en BD.
    CUMPLE: CNST-010 (NO cache)
    """
    
    username = models.CharField(max_length=150, unique=True, db_index=True)
    failed_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True, db_index=True)
    last_attempt_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'authentication_login_lockout'
        indexes = [
            models.Index(fields=['username', 'locked_until']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.failed_attempts} attempts"
    
    def is_locked(self):
        """Verifica si aún está bloqueado."""
        if not self.locked_until:
            return False
        
        from django.utils import timezone
        return timezone.now() < self.locked_until
    
    def increment_attempts(self):
        """Incrementa contador de intentos."""
        self.failed_attempts += 1
        self.save(update_fields=['failed_attempts', 'last_attempt_at'])
    
    def lock(self, duration_minutes):
        """Bloquea cuenta por X minutos."""
        from django.utils import timezone
        from datetime import timedelta
        
        self.locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['locked_until'])
    
    def unlock(self):
        """Desbloquea y resetea."""
        self.failed_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_attempts', 'locked_until'])
```

**Ventajas:**
- ✅ Cumple CNST-010 (NO cache)
- ✅ Persistente (sobrevive restart)
- ✅ Funciona en múltiples servidores
- ✅ Auditable (se puede ver historial)
- ✅ Indexado para performance
- ✅ Cleanup automático con queries

---

### Opción 2: Usar tabla django_session (ALTERNATIVA)

**Aprovechar sesiones existentes:**

```python
# Usar django.contrib.sessions
# Ya usa base de datos según CNST-010
```

**Desventaja:**
- Menos limpio
- Mezcla conceptos (sessions vs lockout)
- No recomendado

---

## 📋 PLAN DE CORRECCIÓN

### PARTE A: Crear Modelo (30 min)

**1. Crear modelo `LoginLockout`**
```yaml
Archivo: apps/authentication/models.py
Acción: Agregar clase LoginLockout
Líneas: +50
```

**2. Migración**
```bash
python manage.py makemigrations authentication
python manage.py migrate authentication
```

---

### PARTE B: Refactorizar LockoutService (1h)

**Archivo:** `apps/authentication/services/lockout.py`

**Cambios:**

```python
# ANTES (con cache) ❌
from django.core.cache import cache

def is_locked(self, username: str) -> bool:
    cache_key = CACHE_KEY_LOCKOUT.format(username=username)
    locked_until = cache.get(cache_key)
    # ...

# DESPUÉS (con BD) ✅
from apps.authentication.models import LoginLockout

def is_locked(self, username: str) -> bool:
    try:
        lockout = LoginLockout.objects.get(username=username)
        return lockout.is_locked()
    except LoginLockout.DoesNotExist:
        return False
```

**Métodos a refactorizar:**
1. ✅ `is_locked()` - Consultar BD
2. ✅ `record_failed_attempt()` - Crear/actualizar registro
3. ✅ `get_failed_attempts_count()` - Leer de BD
4. ✅ `reset_failed_attempts()` - Actualizar BD
5. ✅ `unlock_account()` - Actualizar BD
6. ✅ `_lock_account()` - Crear/actualizar BD

---

### PARTE C: Actualizar Settings (5 min)

**Archivo:** `config/settings/base.py`

```python
# ANTES ❌
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'iact-cache',
    }
}

# DESPUÉS ✅
# CNST-010: NO cache permitido
# Usar solo base de datos
# CACHES removido completamente
```

**Acción:** Comentar o eliminar configuración de CACHES

---

### PARTE D: Actualizar Tests (30 min)

**Archivos afectados:**
- `tests/unit/authentication/test_services.py`
- `tests/integration/authentication/test_auth_flow.py`

**Cambios:**

```python
# ANTES ❌
def setup_method(self):
    self.service = LockoutService()
    cache.clear()  # Limpiar cache

# DESPUÉS ✅
def setup_method(self):
    self.service = LockoutService()
    LoginLockout.objects.all().delete()  # Limpiar BD
```

---

### PARTE E: Actualizar Documentación (20 min)

**Archivos a actualizar:**

1. `docs/INTEGRATION_GUIDE.md`
   - Remover "Redis corriendo" de checklist
   - Actualizar troubleshooting

2. `docs/plans/PLAN_FASE_2_v1.0.0.md`
   - Remover Redis de dependencias

3. `docs/plans/FASE_2_QUICK_START.md`
   - Remover Redis de checklist

4. `docs/compliance/FASE_1_PARTE_7_IMPLEMENTADA.md`
   - Remover sección troubleshooting Redis

---

### PARTE F: Cleanup y Verificación (15 min)

**1. Remover imports de cache**
```bash
# Buscar todos los imports
grep -r "from django.core.cache import cache" apps/

# Verificar que solo esté en lockout.py
# Eliminar después de refactorizar
```

**2. Verificar cumplimiento**
```bash
# NO debe haber referencias a cache
grep -r "cache\." apps/authentication/

# NO debe haber Redis mencionado
grep -ri "redis" apps/authentication/

# Settings sin CACHES
grep "CACHES" config/settings/base.py
```

---

## ⏱️ ESTIMACIÓN TOTAL

```yaml
PARTE A: Crear Modelo             30 min
PARTE B: Refactorizar Service      1h
PARTE C: Actualizar Settings       5 min
PARTE D: Actualizar Tests         30 min
PARTE E: Actualizar Docs          20 min
PARTE F: Cleanup                  15 min
---
TOTAL:                           ~2h 40 min
```

---

## 📊 COMPARACIÓN ANTES/DESPUÉS

### Performance

| Operación | Cache (ANTES) | Base de Datos (DESPUÉS) | Δ |
|-----------|---------------|------------------------|---|
| is_locked() | ~0.1ms | ~2ms | +1.9ms |
| record_attempt() | ~0.2ms | ~5ms | +4.8ms |
| unlock() | ~0.1ms | ~5ms | +4.9ms |

**Impacto:** Minimal (~5ms por operación de login)

**Aceptable porque:**
- Login no es operación crítica de performance
- 5ms adicional es imperceptible
- Cumplimiento > Performance

---

### Fiabilidad

| Aspecto | Cache (ANTES) | Base de Datos (DESPUÉS) |
|---------|---------------|------------------------|
| Persistencia | ❌ Volátil | ✅ Persistente |
| Restart-safe | ❌ Se pierde | ✅ Sobrevive |
| Multi-server | ❌ No compatible | ✅ Compatible |
| Auditable | ❌ No | ✅ Sí |
| CNST-010 | ❌ Viola | ✅ Cumple |

---

## 🎯 CRITERIOS DE ACEPTACIÓN

```yaml
La corrección será exitosa si:
  ✅ NO hay imports de django.core.cache
  ✅ NO hay configuración CACHES en settings
  ✅ LoginLockout modelo creado
  ✅ Migración aplicada exitosamente
  ✅ LockoutService refactorizado
  ✅ Todos los tests pasando
  ✅ Documentación actualizada
  ✅ grep -ri "redis" apps/ retorna vacío
  ✅ Funcionalidad de lockout funciona igual
  ✅ Cumple CNST-010 100%
```

---

## 🚨 RIESGOS SI NO SE CORRIGE

```yaml
Severidad: 🔴 CRÍTICA

Riesgos Técnicos:
  1. Violación de restricción arquitectónica CNST-010
  2. Sistema no compatible con producción
  3. Lockout se resetea en cada deploy
  4. No funciona con load balancer
  5. Datos de seguridad volátiles

Riesgos de Negocio:
  1. Sistema puede rechazar deployment
  2. Auditoría fallará
  3. Problemas de seguridad (bypass lockout)
  4. No production-ready
```

---

## ✅ RECOMENDACIÓN

```yaml
Acción: CORREGIR INMEDIATAMENTE

Prioridad: 🔴 P0 (Bloqueador)

Razón:
  - Violación de restricción crítica
  - Afecta seguridad del sistema
  - Bloquea deployment a producción
  - Fácil de corregir (2-3 horas)

Momento:
  - ANTES de continuar con FASE 2
  - ANTES de merge a develop
  - ANTES de tag final
```

---

## 📋 SIGUIENTE PASO

```bash
# Opción A: Corrección Inmediata (RECOMENDADO)
1. Crear branch: git checkout -b fix/cnst-010-remove-cache
2. Implementar PARTES A-F
3. Commit y tag: fix-cnst-010-v1.0.0

# Opción B: Plan Detallado Primero
1. Revisar este análisis
2. Aprobar plan de corrección
3. Ejecutar implementación
```

---

**Análisis:** Violación CNST-010 - Uso de Cache  
**Severidad:** 🔴 CRÍTICA  
**Tiempo:** 2h 40min  
**Bloqueador:** Sí (para producción)  
**Estado:** ❌ REQUIERE CORRECCIÓN INMEDIATA
