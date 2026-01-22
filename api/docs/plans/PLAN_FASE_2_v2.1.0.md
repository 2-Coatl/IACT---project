# 📋 PLAN FASE 2 v2.1.0 - User Management

**Versión:** 2.1.0  
**Fecha:** 2026-01-21  
**País:** México 🇲🇽  
**Branch:** feature/user-management

---

## 🔍 CAMBIOS vs v2.0.0

```yaml
❌ ELIMINAR UserServiceAccess:
  - Control de acceso SOLO por Módulos y Funciones
  - No relación directa User -> Service
  
✅ SOLO MÉXICO:
  - Formato teléfono: México (10 dígitos)
  - Timezone sistema: America/Mexico_City
  - Sin referencias a Chile u otros países
```

---

## 🏗️ ARQUITECTURA - CONTROL DE ACCESO

### ✅ SOLO 2 MECANISMOS RBAC

```
User
 ├── function_assignments (M:N) → Function
 │    └── Funciones atómicas (USR_VIEW, RPT_EXPORT, etc)
 │
 └── module_accesses (M:N) → Module  
      └── Módulos jerárquicos (MOD_Users, MOD_Reports, etc)
      
❌ NO UserServiceAccess (obsoleto)
```

### Ejemplo de uso

```yaml
Usuario "juan":
  Funciones:
    - USR_VIEW (ver usuarios)
    - RPT_EXPORT (exportar reportes)
  
  Módulos:
    - MOD_Dashboard (con hijos automáticos)
    - MOD_Reports (con hijos automáticos)
    
Acceso a Services 800:
  - Se controla vía módulo MOD_Pipeline
  - O función específica PIPE_SERVICE_VIEW
  - NO mediante UserServiceAccess
```

---

## 📋 MODELOS - CORRECCIONES REQUERIDAS

### User

```python
# QUITAR:
❌ employee_id

# MANTENER:
✅ phone (validator México)
✅ avatar
✅ position
✅ Relaciones RBAC: function_assignments, module_accesses
```

### UserSettings

```python
# QUITAR:
❌ theme (config del sistema)
❌ timezone (config del sistema, México)
❌ email_notifications (sistema alertas)

# MANTENER:
✅ language (es, en)
✅ notifications_enabled (alertas internas)
```

---

## 📋 PARTES (5 TOTAL)

### ✅ PARTE 1: Models + Validators - COMPLETADA

```yaml
Duración: 1h
Estado: ✅ COMPLETADA
Output:
  - CustomUserManager
  - 4 validators específicos
  - POSITION_CHOICES, DEPARTMENT_CHOICES
```

---

### ⏳ PARTE 2: Correcciones (30 min)

**Objetivo:** Limpiar modelos de campos obsoletos

**Tareas:**

1. **Actualizar User:**
   ```python
   # apps/users/models.py
   - Quitar employee_id
   - Quitar import validate_employee_id
   ```

2. **Actualizar UserSettings:**
   ```python
   # apps/users/models.py
   class UserSettings(TimeStampedModel):
       user = OneToOneField(...)
       language = CharField(...)  # ✅ Mantener
       notifications_enabled = BooleanField(...)  # ✅ Mantener
       # ❌ Quitar: theme, timezone, email_notifications
   ```

3. **Actualizar validators.py:**
   ```python
   # apps/users/validators.py
   # Quedan solo 3:
   - validate_username()
   - validate_avatar_file()
   - validate_password_strength()
   
   # ❌ Quitar validate_employee_id
   ```

4. **Migración:**
   ```python
   # 000X_remove_obsolete_fields.py
   operations = [
       RemoveField('user', 'employee_id'),
       RemoveField('usersettings', 'theme'),
       RemoveField('usersettings', 'timezone'),
       RemoveField('usersettings', 'email_notifications'),
   ]
   ```

5. **Marcar UserServiceAccess obsoleto:**
   ```python
   # apps/access/models.py
   class UserServiceAccess(...):
       """
       OBSOLETO - No usar.
       Control de acceso por Módulos y Funciones únicamente.
       """
   ```

---

### ❌ PARTE 3: Services - OMITIDA

```yaml
Razón: YA EXISTEN (1,511 líneas)
  - UserService (487 líneas)
  - ProfileService (307 líneas)
  - PasswordService (376 líneas)
  - AuthenticationService (341 líneas)
```

---

### ⏳ PARTE 4: Serializers (1.5h)

**11 Serializers:**

1. **UserSerializer** - Con functions y modules
2. **UserCreateSerializer**
3. **UserUpdateSerializer**
4. **UserListSerializer**
5. **UserDetailSerializer** - Full RBAC info
6. **ProfileSerializer**
7. **UserSettingsSerializer** - Solo language y notifications_enabled
8. **AvatarUploadSerializer**
9. **PasswordChangeSerializer**
10. **UserActivationSerializer**
11. **RBAC Serializers** - Function/Module assignments (read-only)

**Ejemplo UserSerializer:**

```python
class UserSerializer(serializers.ModelSerializer):
    functions = SerializerMethodField()  # ✅ Funciones RBAC
    modules = SerializerMethodField()    # ✅ Módulos RBAC
    
    def get_functions(self, obj):
        """Códigos de funciones: ['USR_VIEW', 'RPT_EXPORT']"""
        return [a.function.code for a in 
                obj.function_assignments.filter(is_active=True)]
    
    def get_modules(self, obj):
        """Códigos de módulos: ['MOD_Dashboard', 'MOD_Users']"""
        return [a.module.code for a in 
                obj.module_accesses.filter(is_active=True)]
```

---

### ⏳ PARTE 5: ViewSets (2h)

**Endpoints con RBAC:**

```
/api/users/
  GET    - Listar (USR_VIEW)
  POST   - Crear (USR_CREATE)

/api/users/{id}/
  GET    - Detalle (USR_VIEW)
  PUT    - Actualizar (USR_EDIT)
  DELETE - Soft delete (USR_DELETE)

/api/users/{id}/functions/
  GET  - Ver funciones (USR_VIEW)
  POST - Asignar función (USR_PERMS)

/api/users/{id}/modules/
  GET  - Ver módulos (USR_VIEW)
  POST - Otorgar módulo (USR_PERMS)

/api/profile/me/
  GET/PUT - Perfil propio

/api/profile/me/avatar/
  POST/DELETE - Avatar
```

**Permission: HasFunction**

```python
class HasFunction(BasePermission):
    """Verifica función RBAC."""
    def __init__(self, function_code):
        self.function_code = function_code
    
    def has_permission(self, request, view):
        return UserFunctionAssignment.objects.filter(
            user=request.user,
            function__code=self.function_code,
            is_active=True
        ).exists()
```

---

### ⏳ PARTE 6: Tests Unit (2h)

```yaml
Cobertura: 90%+
Archivos:
  - test_models.py
  - test_validators.py
  - test_managers.py
  - test_services.py
  - test_serializers.py
```

---

### ⏳ PARTE 7: Tests Int + Docs (1.5h)

```yaml
Archivos:
  - test_user_api.py
  - test_rbac_flow.py
  - API_USERS.md
  - RBAC_GUIDE.md
```

---

## 📊 RESUMEN

```yaml
Partes: 5 (reducido de 7)
Duración: 9.5h
Progreso: 20% (1/5)

Control RBAC:
  ✅ Function (funciones atómicas)
  ✅ Module (módulos jerárquicos)
  ❌ UserServiceAccess (obsoleto)

Regional:
  ✅ México únicamente
  ✅ America/Mexico_City
  ✅ Teléfono 10 dígitos

Próximo: PARTE 2 - Correcciones (30 min)
```

---

## 🎯 DEPENDENCIAS

```
PARTE 1 (✅) → PARTE 2 → PARTE 4 → PARTE 5 → PARTE 7
                        ↓
                     PARTE 6 (paralelo)
```

---

**Versión:** 2.1.0  
**Estado:** Corregido  
**Fecha:** 2026-01-21
