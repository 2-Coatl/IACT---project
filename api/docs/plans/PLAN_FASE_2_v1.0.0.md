# 📋 PLAN FASE 2 v1.0.0 - Sistema de Gestión de Usuarios

## 🎯 OBJETIVO

Implementar un **sistema completo de gestión de usuarios** que integre con el sistema de autenticación (FASE 1) y proporcione CRUD completo, gestión de perfiles, avatares, y asignación de roles/permisos.

---

## 📊 CONTEXTO

### ✅ Ya Implementado (FASE 1)
```yaml
Sistema de Autenticación:
  - Login/Logout
  - Recuperación de contraseña
  - Gestión de sesiones
  - Bloqueo de cuentas
  - 11 endpoints REST
  - 54 tests
```

### 🎯 Por Implementar (FASE 2)
```yaml
Sistema de Gestión de Usuarios:
  - CRUD completo de usuarios
  - Gestión de perfiles
  - Gestión de avatares
  - Asignación de roles/permisos
  - Activación/Desactivación
  - Auditoría de cambios
```

---

## 📁 ESTRUCTURA ACTUAL

### apps/users/ (Existente)
```
apps/users/
├── models.py           # CustomUser, UserProfile (YA EXISTE)
├── managers.py         # CustomUserManager (YA EXISTE)
├── serializers/        # Parcialmente implementado
├── viewsets.py         # Parcialmente implementado
├── permissions.py      # Por crear
└── services/           # Por crear
```

### tests/unit/users/ (Existente)
```
tests/unit/users/
├── test_models.py         # Parcial
├── test_serializers.py    # Parcial
├── test_views.py          # Parcial
└── test_profile_api.py    # Parcial
```

---

## 🎯 ALCANCE FASE 2

### Modelos (Revisar/Completar)
- ✅ CustomUser (ya existe, revisar)
- ✅ UserProfile (ya existe, revisar)
- 📝 Agregar campos faltantes si necesario

### Services (Crear)
- 📝 UserService (CRUD completo)
- 📝 ProfileService (gestión perfiles)
- 📝 AvatarService (gestión avatares)
- 📝 RoleAssignmentService (asignar roles)

### Serializers (Completar)
- 📝 UserCreateSerializer
- 📝 UserUpdateSerializer
- 📝 UserListSerializer
- 📝 UserDetailSerializer
- 📝 ProfileSerializer
- 📝 AvatarSerializer
- 📝 PasswordChangeSerializer
- 📝 UserActivationSerializer

### ViewSets (Completar)
- 📝 UserViewSet (CRUD + acciones)
- 📝 ProfileViewSet (gestión perfil)

### Endpoints (Crear)
- 📝 15+ endpoints REST

### Tests (Completar)
- 📝 Tests unitarios (models, services)
- 📝 Tests integración (flujos completos)
- 📝 Factories actualizadas
- 📝 Fixtures pytest

---

## 📋 DIVISIÓN EN PARTES (7 PARTES)

### PARTE 1: Models + Managers + Validators (1h)
**Objetivo:** Revisar y completar modelos existentes

**Tareas:**
1. Revisar CustomUser model
   - Verificar campos existentes
   - Agregar campos faltantes si necesario
   - Verificar herencia de AbstractBaseUser
   - Verificar soft delete

2. Revisar UserProfile model
   - Verificar relación OneToOne con User
   - Campos: phone, position, employee_id, department
   - Avatar field
   - Bio/Notes

3. Revisar CustomUserManager
   - create_user()
   - create_superuser()
   - active() queryset

4. Crear validators.py
   - validate_phone_number()
   - validate_employee_id()
   - validate_username()
   - validate_email()

5. Actualizar constants.py
   - USER_STATUS choices
   - DEPARTMENT choices
   - POSITION choices

**Archivos:**
- apps/users/models.py (revisar/actualizar)
- apps/users/managers.py (revisar)
- apps/users/validators.py (crear)
- apps/users/constants.py (crear)

**Output:** Modelos completos y validados

---

### PARTE 2: Services Base + UserService (1.5h)
**Objetivo:** Implementar servicios para gestión de usuarios

**Tareas:**
1. Crear UserService
   - Hereda de BaseService
   - create_user() - Crear usuario con validaciones
   - update_user() - Actualizar con auditoría
   - delete_user() - Soft delete
   - activate_user() - Activar cuenta
   - deactivate_user() - Desactivar cuenta
   - get_user_by_id()
   - get_user_by_username()
   - get_user_by_email()
   - list_users() - Con filtros

2. Crear excepciones específicas
   - UserAlreadyExistsError
   - UserNotFoundError
   - InvalidUserDataError
   - UserInactiveError
   - EmailAlreadyExistsError

**Archivos:**
- apps/users/services/__init__.py
- apps/users/services/user_service.py (300+ líneas)
- apps/users/exceptions.py (150+ líneas)

**Output:** UserService completo con todas las operaciones CRUD

---

### PARTE 3: ProfileService + AvatarService (1h)
**Objetivo:** Servicios para perfiles y avatares

**Tareas:**
1. ProfileService
   - get_profile() - Obtener perfil de usuario
   - update_profile() - Actualizar información personal
   - complete_profile() - Marcar perfil como completo
   - validate_profile_data()

2. AvatarService
   - upload_avatar() - Subir avatar con validaciones
   - delete_avatar() - Eliminar avatar
   - get_avatar_url()
   - validate_image() - Validar tipo, tamaño
   - resize_image() - Redimensionar automático

3. Agregar helpers para imágenes
   - generate_thumbnail()
   - allowed_image_formats()
   - max_file_size validation

**Archivos:**
- apps/users/services/profile_service.py (200+ líneas)
- apps/users/services/avatar_service.py (180+ líneas)

**Output:** Servicios para gestión de perfiles y avatares

---

### PARTE 4: Serializers Completos (1.5h)
**Objetivo:** Serializers para todas las operaciones

**Tareas:**
1. User Serializers (6)
   - UserCreateSerializer - Crear usuario (POST)
   - UserUpdateSerializer - Actualizar usuario (PUT/PATCH)
   - UserListSerializer - Listado (GET list)
   - UserDetailSerializer - Detalle (GET detail)
   - UserActivationSerializer - Activar/Desactivar
   - ChangePasswordSerializer - Cambiar password

2. Profile Serializers (2)
   - ProfileSerializer - Gestión perfil
   - ProfileUpdateSerializer - Actualizar perfil

3. Avatar Serializers (1)
   - AvatarSerializer - Upload/Delete avatar

4. Role Assignment Serializers (2)
   - UserRoleAssignmentSerializer
   - UserPermissionSerializer

**Archivos:**
- apps/users/serializers/__init__.py
- apps/users/serializers/user.py (400+ líneas)
- apps/users/serializers/profile.py (200+ líneas)
- apps/users/serializers/avatar.py (100+ líneas)

**Output:** 11 serializers completos

---

### PARTE 5: ViewSets + Permissions + URLs (2h)
**Objetivo:** ViewSets con todas las acciones y permisos

**Tareas:**
1. UserViewSet
   - list() - Listar usuarios (filtros, búsqueda, paginación)
   - create() - Crear usuario
   - retrieve() - Detalle usuario
   - update() - Actualizar usuario
   - partial_update() - Actualización parcial
   - destroy() - Soft delete
   - activate() - Activar usuario (acción custom)
   - deactivate() - Desactivar usuario (acción custom)
   - assign_role() - Asignar rol (acción custom)
   - remove_role() - Remover rol (acción custom)
   - reset_password() - Reset password (acción custom)

2. ProfileViewSet
   - retrieve() - Ver perfil actual
   - update() - Actualizar perfil
   - upload_avatar() - Subir avatar (acción custom)
   - delete_avatar() - Eliminar avatar (acción custom)

3. Permissions personalizados
   - IsOwnerOrAdmin - Solo dueño o admin
   - CanManageUsers - Permiso gestión usuarios
   - CanAssignRoles - Permiso asignar roles

4. URLs configuration
   - Router para UserViewSet
   - Router para ProfileViewSet
   - Nested routes si necesario

**Archivos:**
- apps/users/viewsets.py (500+ líneas)
- apps/users/permissions.py (150+ líneas)
- apps/users/urls.py (50+ líneas)
- config/urls.py (actualizar)

**Output:** 2 ViewSets, 3 Permissions, 15+ endpoints

---

### PARTE 6: Tests Unitarios + Factories (2h)
**Objetivo:** Tests completos para models y services

**Tareas:**
1. Factories (actualizar/crear)
   - CustomUserFactory - Ya existe, actualizar
   - UserProfileFactory - Crear
   - AdminUserFactory - Ya existe, verificar

2. Fixtures pytest
   - users.py - Fixtures reutilizables
   - profiles.py - Fixtures de perfiles

3. Tests Models
   - TestCustomUser (5-7 tests)
   - TestUserProfile (5-7 tests)
   - TestCustomUserManager (3-5 tests)

4. Tests Services
   - TestUserService (10-12 tests)
   - TestProfileService (6-8 tests)
   - TestAvatarService (5-7 tests)

**Archivos:**
- tests/factories/user_factory.py (actualizar)
- tests/fixtures/users.py (actualizar)
- tests/unit/users/test_models.py (actualizar)
- tests/unit/users/test_services.py (crear, 400+ líneas)

**Output:** ~40 tests unitarios

---

### PARTE 7: Tests Integración + Documentación (1.5h)
**Objetivo:** Tests end-to-end y documentación completa

**Tareas:**
1. Tests de Integración
   - test_user_crud_flow.py
     * Crear usuario → Actualizar → Desactivar → Activar
   - test_profile_flow.py
     * Actualizar perfil → Subir avatar → Eliminar avatar
   - test_role_assignment_flow.py
     * Asignar rol → Verificar permisos → Remover rol
   - test_user_lifecycle.py
     * Crear → Login → Cambiar password → Soft delete

2. Fixtures de datos
   - users.json - Usuarios de ejemplo
   - profiles.json - Perfiles de ejemplo

3. Documentación
   - USER_MANAGEMENT_GUIDE.md
     * Pre-requisitos
     * Endpoints documentados (15+)
     * Ejemplos de uso
     * Troubleshooting
   - API_REFERENCE.md
     * Referencia completa de endpoints
     * Request/Response examples

4. Tag final
   - fase2-v1.0.0

**Archivos:**
- tests/integration/users/test_user_crud_flow.py (300+ líneas)
- tests/integration/users/test_profile_flow.py (250+ líneas)
- tests/integration/users/test_role_assignment_flow.py (200+ líneas)
- tests/integration/users/test_user_lifecycle.py (200+ líneas)
- docs/USER_MANAGEMENT_GUIDE.md (800+ líneas)
- docs/API_REFERENCE.md (600+ líneas)

**Output:** ~30 tests integración, documentación completa

---

## 📊 RESUMEN ESTIMACIONES

```yaml
PARTE 1: Models + Managers + Validators
  Tiempo: 1h
  Archivos: 3
  Líneas: ~400

PARTE 2: Services Base + UserService
  Tiempo: 1.5h
  Archivos: 3
  Líneas: ~450

PARTE 3: ProfileService + AvatarService
  Tiempo: 1h
  Archivos: 2
  Líneas: ~380

PARTE 4: Serializers Completos
  Tiempo: 1.5h
  Archivos: 4
  Líneas: ~700

PARTE 5: ViewSets + Permissions + URLs
  Tiempo: 2h
  Archivos: 4
  Líneas: ~700

PARTE 6: Tests Unitarios + Factories
  Tiempo: 2h
  Archivos: 4
  Líneas: ~800

PARTE 7: Tests Integración + Docs
  Tiempo: 1.5h
  Archivos: 6
  Líneas: ~2,150

---
TOTAL FASE 2:
  Tiempo: 11h
  Archivos: 26
  Líneas: ~5,580
  Tests: ~70 (40 unit + 30 integration)
  Endpoints: 15+
```

---

## 🎯 ENDPOINTS ESPERADOS (15+)

### User Management
```http
1.  GET    /api/v1/users/                    # Listar usuarios
2.  POST   /api/v1/users/                    # Crear usuario
3.  GET    /api/v1/users/{id}/               # Detalle usuario
4.  PUT    /api/v1/users/{id}/               # Actualizar usuario
5.  PATCH  /api/v1/users/{id}/               # Actualización parcial
6.  DELETE /api/v1/users/{id}/               # Soft delete
7.  POST   /api/v1/users/{id}/activate/      # Activar usuario
8.  POST   /api/v1/users/{id}/deactivate/    # Desactivar usuario
9.  POST   /api/v1/users/{id}/reset-password/ # Reset password
10. POST   /api/v1/users/{id}/assign-role/   # Asignar rol
11. POST   /api/v1/users/{id}/remove-role/   # Remover rol
```

### Profile Management
```http
12. GET    /api/v1/profile/                  # Ver perfil actual
13. PUT    /api/v1/profile/                  # Actualizar perfil
14. POST   /api/v1/profile/avatar/           # Subir avatar
15. DELETE /api/v1/profile/avatar/           # Eliminar avatar
16. GET    /api/v1/users/{id}/profile/       # Ver perfil de usuario
```

---

## 🔗 INTEGRACIÓN CON FASE 1

```yaml
Autenticación (FASE 1):
  - Login → Retorna user data
  - Cambio password → UserService
  - Session → Vinculado a User

Usuarios (FASE 2):
  - Crear usuario → Configurar security answers
  - Activar usuario → Habilitar login
  - Soft delete → Invalidar sesiones
  - Cambio datos → Auditoría
```

---

## 🔒 PERMISOS REQUERIDOS

```yaml
RBAC Functions (apps/access):
  - users.view_users
  - users.add_user
  - users.change_user
  - users.delete_user
  - users.activate_user
  - users.deactivate_user
  - users.assign_roles
  - users.reset_password
  - users.view_profile
  - users.change_profile
```

---

## ✅ CRITERIOS DE ACEPTACIÓN

```yaml
Funcionalidad:
  ✅ CRUD completo de usuarios
  ✅ Soft delete implementado
  ✅ Activación/Desactivación
  ✅ Gestión de perfiles completa
  ✅ Upload/Delete avatares
  ✅ Asignación de roles
  ✅ Cambio de contraseña
  ✅ Validaciones en todos los campos

Calidad:
  ✅ Tests unitarios >90% coverage
  ✅ Tests integración end-to-end
  ✅ Documentación completa
  ✅ python manage.py check sin errores
  ✅ Factories para todos los models
  ✅ Fixtures pytest reutilizables

Seguridad:
  ✅ Permisos en todos los endpoints
  ✅ Validación de ownership
  ✅ Sanitización de inputs
  ✅ Auditoría de cambios
  ✅ Soft delete (no hard delete)

Performance:
  ✅ Paginación en listados
  ✅ Filtros eficientes
  ✅ Select related/prefetch related
  ✅ Optimización de queries
```

---

## 📚 DEPENDENCIAS

### Django Packages
```python
# Ya instalados
djangorestframework
django-filter  # Para filtros avanzados
Pillow  # Para manejo de imágenes
```

### Apps Dependientes
```yaml
apps/core:
  - BaseService
  - SoftDeleteMixin
  - AuditedModel
  - RequiresFunctionPermission

apps/authentication:
  - Token authentication
  - SessionLog

apps/access:
  - RBAC (Roles, Functions)
  - Permission checking
```

---

## 🚀 ORDEN DE EJECUCIÓN

```mermaid
PARTE 1 → PARTE 2 → PARTE 3
   ↓         ↓         ↓
PARTE 4 ← PARTE 5 ← PARTE 6
   ↓
PARTE 7 (Final)
```

**Dependencias:**
- PARTE 4 requiere PARTE 2-3 (services)
- PARTE 5 requiere PARTE 4 (serializers)
- PARTE 6 requiere PARTE 1-3 (models, services)
- PARTE 7 requiere PARTE 5 (endpoints)

---

## 📋 CHECKLIST PRE-INICIO

```yaml
Antes de comenzar FASE 2:
  ✅ FASE 1 completada al 100%
  ✅ Tag fase1-v1.0.0 creado
  ✅ Migraciones FASE 1 aplicadas
  ✅ Tests FASE 1 pasando
  ✅ Branch feature/user-management creado
  📝 Revisar apps/users/ actual
  📝 Revisar tests/unit/users/ actual
  📝 Listar campos faltantes en models
```

---

## 🎯 ENTREGABLES FASE 2

```yaml
Código:
  - 4 Services (User, Profile, Avatar, RoleAssignment)
  - 11 Serializers
  - 2 ViewSets
  - 3 Permissions
  - 15+ endpoints REST
  - Validators personalizados

Tests:
  - 40 tests unitarios
  - 30 tests integración
  - Factories actualizadas
  - Fixtures pytest

Documentación:
  - USER_MANAGEMENT_GUIDE.md
  - API_REFERENCE.md
  - 7 compliance docs (PARTE_X_IMPLEMENTADA.md)

Tag:
  - fase2-v1.0.0
```

---

## 🔄 WORKFLOW

```bash
# 1. Crear branch
git checkout -b feature/user-management

# 2. Ejecutar PARTE 1
# ... implementar ...
git commit -m "FASE 2 v1.0.0 - PARTE 1: Models + Validators"

# 3. Ejecutar PARTE 2-6
# ... repetir proceso ...

# 4. PARTE 7 (Final)
git commit -m "FASE 2 v1.0.0 - PARTE 7: Tests + Docs"
git tag -a fase2-v1.0.0 -m "Sistema Gestión Usuarios Completo"

# 5. Merge a develop
git checkout develop
git merge feature/user-management
```

---

## 📊 MÉTRICAS ESPERADAS

```yaml
Coverage:
  - Models: >95%
  - Services: >90%
  - Serializers: >85%
  - ViewSets: >90%
  - Total: >90%

Performance:
  - Listado usuarios: <200ms
  - CRUD operations: <100ms
  - Upload avatar: <500ms
  - Filtros: <150ms

Calidad:
  - Complejidad ciclomática: <10
  - Líneas por función: <50
  - Docstrings: 100%
  - Type hints: 100%
```

---

## 🎓 LECCIONES DE FASE 1

```yaml
Aplicar en FASE 2:
  ✅ Usar factories desde el inicio
  ✅ Tests unitarios antes de integración
  ✅ Documentar cada PARTE
  ✅ Verificar sintaxis antes de commit
  ✅ Commits descriptivos
  ✅ Tag anotado al final
  ✅ Guía de integración completa
  ✅ Troubleshooting documentado
```

---

## 🚀 PRÓXIMOS PASOS

```bash
# 1. Revisar este plan
¿Aprobado? → Continuar

# 2. Crear branch
git checkout -b feature/user-management

# 3. Comenzar PARTE 1
Revisar models actuales → Actualizar → Crear validators
```

---

**Plan:** FASE 2 v1.0.0  
**Objetivo:** Sistema de Gestión de Usuarios Completo  
**Duración:** 11 horas  
**Archivos:** 26  
**Líneas:** ~5,580  
**Tests:** ~70  
**Estado:** 📋 PLANIFICADO - Esperando aprobación
