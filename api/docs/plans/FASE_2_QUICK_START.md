# 🚀 INICIO RÁPIDO - FASE 2 v1.0.0

## ⚡ Quick Start

```bash
# 1. Crear branch
git checkout -b feature/user-management

# 2. Revisar estado actual
cat apps/users/models.py
ls tests/unit/users/

# 3. Comenzar PARTE 1
# ... seguir plan FASE_2_v1.0.0.md
```

---

## 📋 FASE 2 EN 3 MINUTOS

### 🎯 Objetivo
Implementar **sistema completo de gestión de usuarios** con CRUD, perfiles, avatares y roles.

### ⏱️ Duración
**11 horas** divididas en **7 partes**

### 📊 Output Esperado
- **26 archivos** nuevos/actualizados
- **5,580 líneas** de código
- **70 tests** (40 unit + 30 integration)
- **15+ endpoints** REST
- **Tag:** fase2-v1.0.0

---

## 🗺️ ROADMAP VISUAL

```
┌─────────────────────────────────────────────────────────────┐
│                    FASE 2 v1.0.0                            │
│              Sistema de Gestión de Usuarios                 │
└─────────────────────────────────────────────────────────────┘

PARTE 1 (1h)          PARTE 2 (1.5h)       PARTE 3 (1h)
┌─────────────┐       ┌─────────────┐      ┌─────────────┐
│  Models +   │──────▶│ UserService │─────▶│  Profile +  │
│ Validators  │       │ Exceptions  │      │   Avatar    │
└─────────────┘       └─────────────┘      │  Services   │
                                           └─────────────┘
                                                  │
                      ┌─────────────┐            │
                      │Serializers  │◀───────────┘
                      │    (11)     │
                      └─────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
┌─────────────┐                        ┌─────────────┐
│ ViewSets +  │                        │   Tests     │
│ Permissions │                        │  Unit (40)  │
│   + URLs    │                        │  Integ (30) │
└─────────────┘                        └─────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            ▼
                    ┌─────────────┐
                    │    Docs +   │
                    │     Tag     │
                    │fase2-v1.0.0 │
                    └─────────────┘
```

---

## 📅 PLANIFICACIÓN DÍA A DÍA

### Día 1 (4h) - Foundation
```
09:00 - 10:00  PARTE 1: Models + Validators
10:00 - 11:30  PARTE 2: UserService
11:30 - 12:30  PARTE 3: Profile + Avatar Services
```

### Día 2 (4h) - API Layer
```
09:00 - 10:30  PARTE 4: Serializers (11)
10:30 - 12:30  PARTE 5: ViewSets + Permissions
```

### Día 3 (3h) - Testing & Docs
```
09:00 - 11:00  PARTE 6: Tests Unitarios
11:00 - 12:30  PARTE 7: Tests Integración + Docs
```

---

## 🎯 PARTES DETALLADAS

### PARTE 1: Models + Validators (1h)
```yaml
Input:
  - apps/users/models.py (existente)
  - apps/users/managers.py (existente)

Output:
  - apps/users/validators.py (nuevo)
  - apps/users/constants.py (nuevo)
  - Models revisados y actualizados

Tareas:
  1. Revisar CustomUser
  2. Revisar UserProfile
  3. Crear validators
  4. Definir constants
```

### PARTE 2: UserService (1.5h)
```yaml
Input:
  - apps/core/services/base.py

Output:
  - apps/users/services/user_service.py (300+ líneas)
  - apps/users/exceptions.py (150+ líneas)

Métodos:
  - create_user()
  - update_user()
  - delete_user() # soft delete
  - activate_user()
  - deactivate_user()
  - list_users()
```

### PARTE 3: Profile + Avatar Services (1h)
```yaml
Output:
  - apps/users/services/profile_service.py (200+ líneas)
  - apps/users/services/avatar_service.py (180+ líneas)

Features:
  - Actualizar perfil
  - Upload avatar (validación)
  - Resize automático
  - Delete avatar
```

### PARTE 4: Serializers (1.5h)
```yaml
Output:
  - apps/users/serializers/user.py (400+ líneas)
  - apps/users/serializers/profile.py (200+ líneas)
  - apps/users/serializers/avatar.py (100+ líneas)

Total: 11 serializers
```

### PARTE 5: ViewSets + Permissions (2h)
```yaml
Output:
  - apps/users/views.py (500+ líneas)
  - apps/users/permissions.py (150+ líneas)
  - apps/users/urls.py (50+ líneas)

ViewSets:
  - UserViewSet (11 acciones)
  - ProfileViewSet (4 acciones)

Endpoints: 15+
```

### PARTE 6: Tests Unitarios (2h)
```yaml
Output:
  - tests/unit/users/test_models.py (actualizar)
  - tests/unit/users/test_services.py (400+ líneas)
  - tests/factories/user_factory.py (actualizar)

Tests: ~40
```

### PARTE 7: Tests Integración + Docs (1.5h)
```yaml
Output:
  - tests/integration/users/test_user_crud_flow.py
  - tests/integration/users/test_profile_flow.py
  - tests/integration/users/test_role_assignment_flow.py
  - docs/USER_MANAGEMENT_GUIDE.md (800+ líneas)
  - docs/API_REFERENCE.md (600+ líneas)

Tests: ~30
Tag: fase2-v1.0.0
```

---

## 🔧 CONFIGURACIÓN PREVIA

### 1. Settings.py
```python
# config/settings.py

# Media files (para avatares)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Pillow settings
AVATAR_MAX_SIZE = 5 * 1024 * 1024  # 5MB
AVATAR_ALLOWED_FORMATS = ['JPEG', 'PNG', 'GIF']
AVATAR_SIZE = (300, 300)  # Resize automático
```

### 2. URLs root
```python
# config/urls.py

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... existing urls ...
    path('api/v1/users/', include('apps.users.urls')),
]

# Servir media files en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 3. Instalar dependencias
```bash
pip install Pillow django-filter
```

---

## 📊 ENDPOINTS PREVIEW

```http
# Users
GET    /api/v1/users/                       # Listar (filtros, search)
POST   /api/v1/users/                       # Crear
GET    /api/v1/users/{id}/                  # Detalle
PUT    /api/v1/users/{id}/                  # Actualizar
PATCH  /api/v1/users/{id}/                  # Parcial
DELETE /api/v1/users/{id}/                  # Soft delete
POST   /api/v1/users/{id}/activate/         # Activar
POST   /api/v1/users/{id}/deactivate/       # Desactivar
POST   /api/v1/users/{id}/reset-password/   # Reset
POST   /api/v1/users/{id}/assign-role/      # Asignar rol
POST   /api/v1/users/{id}/remove-role/      # Remover rol

# Profile
GET    /api/v1/profile/                     # Ver perfil propio
PUT    /api/v1/profile/                     # Actualizar
POST   /api/v1/profile/avatar/              # Upload avatar
DELETE /api/v1/profile/avatar/              # Delete avatar
GET    /api/v1/users/{id}/profile/          # Ver perfil usuario
```

---

## ✅ CHECKLIST DE INICIO

```yaml
Pre-requisitos:
  ✅ FASE 1 completada
  ✅ Tag fase1-v1.0.0 creado
  ✅ Migraciones FASE 1 aplicadas
  ✅ Tests FASE 1 pasando (54 tests)
  ✅ PostgreSQL corriendo
  ❌ NO Redis (prohibido CNST-010)

Ambiente:
  □ Pillow instalado
  □ django-filter instalado
  □ MEDIA_ROOT configurado
  □ MEDIA_URL configurado

Git:
  □ Branch feature/user-management creado
  □ Working directory limpio
  □ .gitignore incluye /media/

Verificación:
  □ python manage.py check (sin errores)
  □ pytest tests/unit/ -v (todos pasando)
  □ Revisar apps/users/ existente
```

---

## 🚀 COMANDO INICIAL

```bash
# Setup completo
cd /tmp/iact-real/callcentersite

# Verificar FASE 1
git log --oneline -1  # Debe ser PARTE 7
git tag -l "fase1*"   # Debe existir fase1-v1.0.0
pytest tests/unit/authentication/ tests/integration/authentication/ -v  # 54 tests

# Crear branch FASE 2
git checkout -b feature/user-management

# Revisar código existente
cat apps/users/models.py | head -50
cat apps/users/managers.py
ls -la tests/unit/users/

# Instalar dependencias
pip install Pillow django-filter

# Verificar ambiente
python manage.py check

# ✅ Listo para PARTE 1
```

---

## 💡 TIPS

### Para cada PARTE:

1. **Leer el plan primero**
   ```bash
   cat docs/plans/PLAN_FASE_2_v1.0.0.md | grep "PARTE X" -A 50
   ```

2. **Verificar sintaxis antes de commit**
   ```bash
   python -m py_compile archivo.py
   ```

3. **Ejecutar tests relevantes**
   ```bash
   pytest tests/unit/users/test_services.py -v
   ```

4. **Commit descriptivo**
   ```bash
   git commit -m "FASE 2 v1.0.0 - PARTE X: Descripción"
   ```

5. **Documentar progreso**
   ```bash
   # Crear docs/compliance/FASE_2_PARTE_X_IMPLEMENTADA.md
   ```

---

## 🎯 CRITERIOS DE ÉXITO

```yaml
FASE 2 exitosa si:
  ✅ 70 tests pasando
  ✅ 15+ endpoints funcionando
  ✅ Upload/Delete avatares funcional
  ✅ CRUD usuarios completo
  ✅ Soft delete implementado
  ✅ Coverage >90%
  ✅ Documentación completa
  ✅ Tag fase2-v1.0.0 creado
```

---

## 📚 RECURSOS

```yaml
Documentos:
  - docs/plans/PLAN_FASE_2_v1.0.0.md (Plan completo)
  - docs/plans/FASE_1_vs_FASE_2_COMPARISON.md (Comparación)
  - docs/INTEGRATION_GUIDE.md (FASE 1, referencia)

Código Referencia:
  - apps/authentication/ (Patrón de services)
  - tests/unit/authentication/ (Patrón de tests)
  - tests/integration/authentication/ (Patrón integración)

Factories:
  - tests/factories/user_factory.py (Actualizar)
  - tests/factories/authentication_factories.py (Referencia)
```

---

## 🎓 LECCIONES DE FASE 1

```yaml
Aplicar:
  ✅ Factories desde el inicio
  ✅ Tests unit antes de integration
  ✅ Commits atómicos descriptivos
  ✅ Verificar sintaxis siempre
  ✅ Documentar cada PARTE
  ✅ Guías detalladas al final
  ✅ Tag anotado completo
```

---

## ⏭️ SIGUIENTE PASO

```bash
# ¿Listo para comenzar?
# 1. Revisar checklist arriba
# 2. Crear branch
# 3. Abrir plan PARTE 1

cat docs/plans/PLAN_FASE_2_v1.0.0.md | grep "PARTE 1" -A 100
```

---

**Guía:** Inicio Rápido FASE 2  
**Versión:** 1.0  
**Duración:** 11h (7 partes)  
**Output:** 5,580 líneas, 70 tests, 15+ endpoints  
**Estado:** 📋 READY TO START

---

## 🚀 ¿COMENZAMOS?

Cuando estés listo, di: **"Vamos con PARTE 1"** 🎯
