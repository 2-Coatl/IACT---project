# INTEGRATION GUIDE - apps/core/

**Versión:** 1.0.0  
**Fecha:** 2026-01-21  
**Audiencia:** Developers  

---

## 📋 ÍNDICE

1. [Introducción](#introducción)
2. [Abstract Models](#abstract-models)
3. [DRF Permissions](#drf-permissions)
4. [Flujo RBAC Completo](#flujo-rbac-completo)
5. [Middleware](#middleware)
6. [Mixins](#mixins)
7. [Integración entre Apps](#integración-entre-apps)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## 📖 INTRODUCCIÓN

Esta guía explica cómo integrar y usar los componentes de `apps/core/` en tus apps.

### Principios

```yaml
apps/core/:
  - Infraestructura compartida
  - Reutilizable por todos
  - Sin lógica de negocio
  - Bien testeado (90%+ coverage)
```

---

## 🧱 ABSTRACT MODELS

### TimeStampedModel

#### Cuándo Usar

```yaml
✅ Usar cuando:
  - Necesitas created_at / updated_at
  - Cualquier modelo que requiera timestamps
  - Auditoría básica de fechas

❌ No usar cuando:
  - Modelo es puramente lookup (no cambia)
  - Rendimiento es crítico (extra fields)
```

#### Implementación

**1. Heredar en tu modelo:**

```python
# apps/reports/models.py
from django.db import models
from apps.core.models import TimeStampedModel

class Report(TimeStampedModel):
    """
    Report model con timestamps automáticos.
    
    Hereda:
    - created_at (auto-set on create)
    - updated_at (auto-update on save)
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']  # Más recientes primero
```

**2. Uso en código:**

```python
# Crear
report = Report.objects.create(
    title='Q4 Sales',
    content='...'
)
print(report.created_at)  # → 2024-01-21 10:30:00
print(report.updated_at)  # → 2024-01-21 10:30:00

# Actualizar
report.title = 'Q4 Sales Updated'
report.save()
print(report.created_at)  # → 2024-01-21 10:30:00 (sin cambios)
print(report.updated_at)  # → 2024-01-21 11:45:00 (actualizado)
```

**3. Queries:**

```python
# Filtrar por fecha
recent = Report.objects.filter(
    created_at__gte=date.today() - timedelta(days=7)
)

# Ordenar
latest = Report.objects.order_by('-created_at').first()
```

#### Importante

```yaml
⚠️ QuerySet.update() NO actualiza updated_at:
  
# ❌ NO actualiza updated_at
Report.objects.filter(id=1).update(title='New')

# ✅ SÍ actualiza updated_at
report = Report.objects.get(id=1)
report.title = 'New'
report.save()
```

---

### SoftDeleteMixin

#### Cuándo Usar

```yaml
✅ Usar cuando:
  - Necesitas recuperar eliminados
  - Auditoría requiere histórico
  - Eliminación debe ser reversible
  - Referencias FK no deben romperse

❌ No usar cuando:
  - Eliminación definitiva (GDPR)
  - Datos sensibles
  - Performance crítico (extra queries)
```

#### Implementación

**1. Heredar y configurar manager:**

```python
# apps/access/models.py
from django.db import models
from apps.core.models import SoftDeleteMixin, SoftDeleteManager

class Function(SoftDeleteMixin, models.Model):
    """
    Function con soft delete.
    
    Hereda:
    - is_deleted (BooleanField)
    - deleted_at (DateTimeField)
    - delete(), restore(), hard_delete()
    """
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    
    # IMPORTANTE: Usar SoftDeleteManager
    objects = SoftDeleteManager()
    
    class Meta:
        db_table = 'access_functions'
```

**2. Operaciones:**

```python
# Crear
func = Function.objects.create(code='USERS_VIEW', name='View Users')

# Soft delete
func.delete()
print(func.is_deleted)    # → True
print(func.deleted_at)    # → 2024-01-21 10:30:00

# Restaurar
func.restore()
print(func.is_deleted)    # → False
print(func.deleted_at)    # → None

# Hard delete (físico)
func.hard_delete()  # Elimina de DB permanentemente
```

**3. Queries con Manager:**

```python
# all() - Solo activos (is_deleted=False)
active_funcs = Function.objects.all()

# deleted() - Solo eliminados
deleted_funcs = Function.objects.deleted()

# with_deleted() - Todos (activos + eliminados)
all_funcs = Function.objects.with_deleted()

# active() - Alias de all()
active = Function.objects.active()

# Filtros combinables
admin_funcs = Function.objects.filter(code__startswith='ADMIN')
deleted_admin = Function.objects.deleted().filter(code__startswith='ADMIN')
```

**4. En ViewSets con Mixin:**

```python
from apps.core.mixins import SoftDeleteViewSetMixin

class FunctionViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    queryset = Function.objects.all()  # Solo activos
    
    # Endpoints agregados automáticamente:
    # POST /api/functions/1/restore/
    # DELETE /api/functions/1/hard-delete/
```

---

## 🔐 DRF PERMISSIONS

### RequiresFunctionPermission (CRÍTICO)

#### Arquitectura RBAC

```
apps/access/models.py:
  - Function: Funciones del sistema
  - Module: Módulos/secciones
  - UserFunctionAssignment: User ↔ Function

apps/users/models.py:
  - User.has_function(code): Verifica si user tiene función

apps/core/permissions.py:
  - RequiresFunctionPermission: DRF permission

apps/authentication/, apps/users/, apps/pipeline/:
  - Usan RequiresFunctionPermission en ViewSets
```

#### Flujo Completo

```
1. Frontend hace request:
   POST /api/auth/change-password/
   Headers: Authorization: Token abc123

2. DRF ViewSet (apps/authentication/viewsets.py):
   class AuthViewSet(viewsets.ViewSet):
       permission_classes = [IsAuthenticated, RequiresFunctionPermission]
       
       function_map = {
           'change_password': 'authentication.change_password',
       }
       
       @action(detail=False, methods=['post'])
       def change_password(self, request):
           pass

3. RequiresFunctionPermission (apps/core/permissions.py):
   def has_permission(self, request, view):
       # a) Usuario autenticado?
       if not request.user.is_authenticated:
           return False  # → 401
       
       # b) Superuser?
       if request.user.is_superuser:
           return True   # → Bypass
       
       # c) Obtener action
       action = view.action  # 'change_password'
       
       # d) Obtener function_map
       function_map = view.function_map
       # {'change_password': 'authentication.change_password'}
       
       # e) Action en map?
       if action not in function_map:
           return False  # → 403
       
       # f) Obtener function_id
       function_id = function_map[action]
       # 'authentication.change_password'
       
       # g) Verificar RBAC
       return request.user.has_function(function_id)

4. User.has_function() (apps/users/models.py):
   def has_function(self, function_id):
       # Import lazy para evitar circular
       from apps.access.models import UserFunctionAssignment
       
       return UserFunctionAssignment.objects.filter(
           user=self,
           function__code=function_id,
           is_active=True
       ).exists()

5. UserFunctionAssignment (apps/access/models.py):
   - Query a DB:
     SELECT 1 FROM access_user_function_assignments
     WHERE user_id = 123
       AND function__code = 'authentication.change_password'
       AND is_active = True
     LIMIT 1
   
6. Response:
   - True → 200 OK (ejecuta change_password)
   - False → 403 Forbidden
```

#### Implementación en tu App

**1. Define Functions en DB:**

```python
# Script o migration
from apps.access.models import Function, Module

# Módulo
reports_module = Module.objects.create(
    code='REPORTS',
    name='Reportes'
)

# Functions
Function.objects.create(
    code='reports.view',
    name='Ver Reportes',
    module=reports_module
)
Function.objects.create(
    code='reports.create',
    name='Crear Reportes',
    module=reports_module
)
Function.objects.create(
    code='reports.export',
    name='Exportar Reportes',
    module=reports_module
)
```

**2. Asigna Functions a Users:**

```python
from apps.access.models import UserFunctionAssignment

UserFunctionAssignment.objects.create(
    user=user,
    function=function,
    assigned_by=admin_user
)
```

**3. Usa en ViewSet:**

```python
# apps/reports/viewsets.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from apps.core.permissions import RequiresFunctionPermission

class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet de reportes con RBAC.
    """
    permission_classes = [IsAuthenticated, RequiresFunctionPermission]
    
    # IMPORTANTE: Mapear actions a function codes
    function_map = {
        'list': 'reports.view',
        'retrieve': 'reports.view',
        'create': 'reports.create',
        'update': 'reports.edit',
        'partial_update': 'reports.edit',
        'destroy': 'reports.delete',
        'export': 'reports.export',  # Custom action
    }
    
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    
    @action(detail=False, methods=['post'])
    def export(self, request):
        """
        Exportar reportes.
        
        Requiere: reports.export
        """
        # Permission ya verificado por RequiresFunctionPermission
        pass
```

**4. Testing:**

```python
import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from apps.users.models import User

@pytest.mark.django_db
class TestReportViewSet:
    
    def test_list_with_permission(self):
        """Test: Usuario con permission puede listar."""
        client = APIClient()
        user = User.objects.create_user(username='test')
        client.force_authenticate(user=user)
        
        # Mock has_function para retornar True
        with patch.object(User, 'has_function', return_value=True):
            response = client.get('/api/reports/')
        
        assert response.status_code == 200
    
    def test_list_without_permission(self):
        """Test: Usuario sin permission → 403."""
        client = APIClient()
        user = User.objects.create_user(username='test')
        client.force_authenticate(user=user)
        
        # Mock has_function para retornar False
        with patch.object(User, 'has_function', return_value=False):
            response = client.get('/api/reports/')
        
        assert response.status_code == 403
```

---

### Otras Permissions

#### IsOwnerOrReadOnly

**Uso:**

```python
from apps.core.permissions import IsOwnerOrReadOnly

class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
# Requisito: Model debe tener created_by field
class Document(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
```

#### Combining Permissions

```python
class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,           # Debe estar autenticado
        RequiresFunctionPermission, # Debe tener función RBAC
        IsOwnerOrReadOnly,         # Solo owner puede editar
    ]
```

---

## 🔧 MIDDLEWARE

### HealthCheckMiddleware

**Configuración:**

```python
# settings/base.py
MIDDLEWARE = [
    'apps.core.middleware.HealthCheckMiddleware',  # Primero
    'django.middleware.security.SecurityMiddleware',
    # ...
]
```

**Uso:**

```bash
# Monitoring
curl https://api.example.com/health/
# → {"status": "healthy", "timestamp": "2024-01-21T10:30:00Z"}
```

---

### LoggingMiddleware

**Configuración:**

```python
MIDDLEWARE = [
    # ...
    'apps.core.middleware.LoggingMiddleware',
    # ...
]

LOGGING = {
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/requests.log',
        },
    },
    'loggers': {
        'apps.core.middleware.logging': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

**Logs generados:**

```
[2024-01-21 10:30:00] INFO Request: GET /api/reports/ user=john
[2024-01-21 10:30:01] INFO Response: 200 OK (1.2s)
```

---

## 🎨 MIXINS

### SoftDeleteViewSetMixin

**Implementación:**

```python
from apps.core.mixins import SoftDeleteViewSetMixin

class ReportViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
```

**Endpoints agregados:**

```bash
# Restaurar eliminado
POST /api/reports/1/restore/
# → 200 OK {report_data}

# Eliminar físicamente
DELETE /api/reports/1/hard-delete/
# → 204 No Content
```

---

### AuditMixin

**Implementación:**

```python
from apps.core.mixins import AuditMixin

class UserViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
```

**Efecto:** Loggea automáticamente en perform_create/perform_update.

---

## 🔗 INTEGRACIÓN ENTRE APPS

### apps/users/ → apps/core/

```python
# apps/users/models.py
from apps.core.models import TimeStampedModel, SoftDeleteMixin

class User(AbstractUser, SoftDeleteMixin):
    pass

class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
```

---

### apps/authentication/ → apps/core/ → apps/access/

```python
# apps/authentication/viewsets.py
from apps.core.permissions import RequiresFunctionPermission

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [RequiresFunctionPermission]
    
    function_map = {
        'change_password': 'authentication.change_password',
    }
```

**Flujo:**
```
AuthViewSet → RequiresFunctionPermission → User.has_function() → UserFunctionAssignment
```

---

## 💡 BEST PRACTICES

### DO (✅)

```python
# 1. Usar abstract models apropiadamente
class MyModel(TimeStampedModel, SoftDeleteMixin):
    objects = SoftDeleteManager()  # IMPORTANTE

# 2. Definir function_map completo
class MyViewSet(viewsets.ModelViewSet):
    function_map = {
        'list': 'my.view',
        'create': 'my.create',
        'update': 'my.edit',
        'destroy': 'my.delete',
        'custom': 'my.custom',
    }

# 3. Combinar permissions lógicamente
permission_classes = [
    IsAuthenticated,
    RequiresFunctionPermission,
]
```

### DON'T (❌)

```python
# 1. NO olvidar SoftDeleteManager
class MyModel(SoftDeleteMixin, models.Model):
    # ❌ Falta: objects = SoftDeleteManager()
    pass

# 2. NO usar update() con TimeStampedModel
MyModel.objects.filter(id=1).update(field='value')  # ❌ No actualiza updated_at

# 3. NO omitir actions en function_map
class MyViewSet(viewsets.ModelViewSet):
    function_map = {
        'list': 'my.view',
        # ❌ Falta 'create', 'update', etc
    }
```

---

## 🐛 TROUBLESHOOTING

### Permission Denied (403)

```yaml
Síntoma: 403 Forbidden aunque user tiene función

Diagnóstico:
1. ¿action en function_map?
   print(view.function_map)
   
2. ¿User tiene función?
   print(user.has_function('code'))
   
3. ¿UserFunctionAssignment existe?
   UserFunctionAssignment.objects.filter(
       user=user,
       function__code='code'
   ).exists()
   
4. ¿Function activa?
   Function.objects.get(code='code').is_active

Solución:
  - Agregar action a function_map
  - Crear UserFunctionAssignment
  - Activar Function
```

### SoftDelete No Funciona

```yaml
Síntoma: delete() elimina físicamente

Diagnóstico:
1. ¿Hereda SoftDeleteMixin?
   isinstance(obj, SoftDeleteMixin)
   
2. ¿Tiene SoftDeleteManager?
   type(MyModel.objects)
   
Solución:
  class MyModel(SoftDeleteMixin, models.Model):
      objects = SoftDeleteManager()  # ← Agregar
```

### Timestamps No Se Actualizan

```yaml
Síntoma: updated_at no cambia

Diagnóstico:
1. ¿Usa .save()?
   obj.save()  # ✅
   MyModel.objects.update()  # ❌

Solución:
  # En vez de update()
  obj = MyModel.objects.get(id=1)
  obj.field = 'new'
  obj.save()  # Actualiza updated_at
```

---

## 📚 RECURSOS

### Documentación

- [apps/core/README.md](../../callcentersite/apps/core/README.md)
- [apps/utils/README.md](../../callcentersite/apps/utils/README.md)
- [ANALISIS_RELACIONES_Y_SRP_v1.1.0.md](../architecture/ANALISIS_RELACIONES_Y_SRP_v1.1.0.md)

### Tests

```bash
# Ver ejemplos de uso
cat tests/unit/core/test_permissions.py
cat tests/unit/core/test_abstract_models.py
cat tests/unit/core/test_mixins.py
```

---

**Mantenido por:** IACT Development Team  
**Última actualización:** 2026-01-21 (FASE 3 PARTE 4)  
**Feedback:** Abrir issue en deuda técnica
