# ANÁLISIS PROFUNDO DEL PROYECTO - PARTE 5 DE 5
## PLAN DE ACCIÓN DIVIDIDO EN SPRINTS

**Proyecto:** IACT Call Center System  
**Fecha Análisis:** 16 de enero de 2026  
**Duración Total:** 8-9 días (65-70 horas)

---

## SPRINT 0: PREPARACIÓN (DÍA 0 - 0.5 días)

### Objetivo: Ambiente listo para desarrollo

### Tareas:

#### 1. Verificar dependencias (30 min)
```bash
cd /tmp/iact-project/callcentersite

# Verificar instaladas
pip list | grep -E "(Django|Pillow|openpyxl|reportlab|pytest|mysqlclient)"

# Instalar faltantes
pip install Pillow openpyxl pandas reportlab mysqlclient pytest-cov factory-boy

# NO instalar:
# celery (no se usa)
# redis (no se usa)

# Actualizar requirements.txt
pip freeze > requirements.txt
```

#### 2. Crear backup (15 min)
```bash
# Backup del proyecto actual
cp -r /tmp/iact-project /tmp/iact-project-backup-$(date +%Y%m%d)

# Backup de modelos antes de migraciones
cp apps/users/models.py apps/users/models.py.backup.$(date +%Y%m%d)
cp apps/access/models.py apps/access/models.py.backup.$(date +%Y%m%d)
```

#### 3. Configurar base de datos (15 min)
```bash
# Verificar PostgreSQL corriendo
# Crear base de datos si no existe
# Verificar config/settings/base.py DATABASES
```

#### 4. Verificar tests actuales (30 min)
```bash
# Ejecutar tests existentes
pytest tests/unit/ -v

# Verificar que pasan
# Documentar fallos si existen
```

**Checklist Sprint 0:**
- [ ] Dependencias instaladas
- [ ] Backups creados
- [ ] BD configurada
- [ ] Tests existentes pasan

**Duración:** 4 horas  
**Entregable:** Ambiente listo

---

## SPRINT 1: FUNDACIÓN CRÍTICA (DÍAS 1-2)

### Objetivo: Sistema funciona básico (BD + RBAC básico)

### DÍA 1 - MAÑANA (4h)

#### Tarea 1.1: Crear migraciones (2h)
```bash
cd /tmp/iact-project/callcentersite

# Orden importa por dependencias
python manage.py makemigrations users
python manage.py makemigrations access
python manage.py makemigrations core
python manage.py makemigrations authentication
python manage.py makemigrations audit
python manage.py makemigrations pipeline

# Revisar archivos de migración generados
ls apps/*/migrations/0001_initial.py
```

**Verificación:**
- [ ] Archivos 0001_initial.py creados
- [ ] No hay errores de sintaxis
- [ ] Revisar dependencias entre migraciones

#### Tarea 1.2: Aplicar migraciones (0.5h)
```bash
# Aplicar migraciones
python manage.py migrate

# Verificar tablas creadas
python manage.py dbshell
\dt  # PostgreSQL
# Verificar tablas: users, functions, modules, etc.
\q
```

**Verificación:**
- [ ] Migraciones aplicadas sin errores
- [ ] Tablas existen en BD
- [ ] Campos avatar, phone, position, employee_id en tabla users

#### Tarea 1.3: Test de migración (0.5h)
```bash
# Crear usuario de prueba
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.create_user(
...     username='test',
...     password='test123',
...     phone='+56912345678',
...     position='Developer'
... )
>>> print(user.phone)
>>> exit()
```

**Verificación:**
- [ ] Usuario se crea sin errores
- [ ] Campos nuevos funcionan
- [ ] Queries funcionan

#### Tarea 1.4: Actualizar tests existentes (1h)
```bash
# Ejecutar tests para ver fallos
pytest tests/unit/users/test_user_model.py -v

# Ajustar si fallan por migraciones
# Ejecutar todos los tests
pytest tests/unit/ -v
```

**Checklist Día 1 Mañana:**
- [ ] Migraciones creadas
- [ ] Migraciones aplicadas
- [ ] BD funcional
- [ ] Tests pasan

---

### DÍA 1 - TARDE (4h)

#### Tarea 1.5: Command populate_functions (2h)
```python
# Crear: apps/access/management/commands/populate_functions.py

from django.core.management.base import BaseCommand
from apps.access.models import Function

class Command(BaseCommand):
    help = 'Pobla las 44 funciones RBAC del sistema'
    
    def handle(self, *args, **options):
        functions = [
            # Authentication
            {'code': 'AUTH-001', 'module': 'MOD_Authentication', 'name': 'Login al sistema'},
            {'code': 'AUTH-002', 'module': 'MOD_Authentication', 'name': 'Cambiar contraseña'},
            
            # Users
            {'code': 'USR-001', 'module': 'MOD_Users', 'name': 'Ver usuarios'},
            {'code': 'USR-002', 'module': 'MOD_Users', 'name': 'Crear usuarios'},
            {'code': 'USR-003', 'module': 'MOD_Users', 'name': 'Editar usuarios'},
            {'code': 'USR-004', 'module': 'MOD_Users', 'name': 'Eliminar usuarios'},
            
            # Access
            {'code': 'ACC-001', 'module': 'MOD_Access', 'name': 'Ver funciones'},
            {'code': 'ACC-002', 'module': 'MOD_Access', 'name': 'Asignar funciones'},
            {'code': 'ACC-003', 'module': 'MOD_Access', 'name': 'Revocar funciones'},
            
            # Reports
            {'code': 'RPT-001', 'module': 'MOD_Reports', 'name': 'Ver reportes'},
            {'code': 'RPT-002', 'module': 'MOD_Reports', 'name': 'Ver dashboard'},
            {'code': 'RPT-003', 'module': 'MOD_Reports', 'name': 'Generar reportes'},
            {'code': 'RPT-004', 'module': 'MOD_Reports', 'name': 'Exportar CSV'},
            {'code': 'RPT-005', 'module': 'MOD_Reports', 'name': 'Exportar Excel'},
            {'code': 'RPT-006', 'module': 'MOD_Reports', 'name': 'Exportar PDF'},
            
            # ... completar las 44 funciones
        ]
        
        for func_data in functions:
            Function.objects.get_or_create(
                code=func_data['code'],
                defaults={
                    'module': func_data['module'],
                    'name': func_data['name'],
                    'is_active': True
                }
            )
            
        self.stdout.write(
            self.style.SUCCESS(f' Pobladas {len(functions)} funciones')
        )
```

```bash
# Ejecutar
python manage.py populate_functions
```

**Verificación:**
- [ ] Command creado
- [ ] 44 funciones en BD
- [ ] Sin duplicados

#### Tarea 1.6: Command populate_modules (1.5h)
```python
# Crear: apps/access/management/commands/populate_modules.py

from django.core.management.base import BaseCommand
from apps.access.models import Module
import json
from pathlib import Path

class Command(BaseCommand):
    help = 'Pobla módulos desde metadata JSON'
    
    def handle(self, *args, **options):
        # Leer metadata de navigation
        apps_with_metadata = [
            'access', 'audit', 'authentication', 
            'reports', 'users'
        ]
        
        for app_name in apps_with_metadata:
            metadata_path = Path(f'apps/{app_name}/navigation/menu_metadata.json')
            if metadata_path.exists():
                with open(metadata_path) as f:
                    data = json.load(f)
                    
                # Crear módulos desde metadata
                for menu in data.get('menu_tree', []):
                    Module.objects.get_or_create(
                        code=f"MOD_{menu['des_name'].replace(' ', '_')}",
                        defaults={
                            'name': menu['des_name'],
                            'order': menu.get('orden', 0),
                            'icon': menu.get('icon', ''),
                            'is_active': True
                        }
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f' Módulos poblados')
        )
```

```bash
# Ejecutar
python manage.py populate_modules
```

#### Tarea 1.7: Crear superuser con funciones (0.5h)
```bash
# Crear superuser
python manage.py createsuperuser
# Username: admin
# Email: admin@iact.com
# Password: admin123

# Asignar todas las funciones en shell
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from apps.access.models import Function, UserFunctionAssignment
>>> User = get_user_model()
>>> admin = User.objects.get(username='admin')
>>> functions = Function.objects.all()
>>> for func in functions:
...     UserFunctionAssignment.objects.get_or_create(
...         user=admin,
...         function=func,
...         defaults={'reason': 'Superuser inicial', 'assigned_by': admin}
...     )
>>> exit()
```

**Checklist Día 1 Tarde:**
- [ ] 44 funciones en BD
- [ ] Módulos poblados
- [ ] Superuser creado
- [ ] Superuser tiene funciones

**Entregable Día 1:** BD completa y poblada

---

### DÍA 2 - APIS RBAC (8h)

#### Tarea 2.1: FunctionViewSet completo (2h)
```python
# Actualizar: apps/access/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Function
from .serializers import FunctionSerializer

class FunctionViewSet(viewsets.ModelViewSet):
    """CRUD completo de funciones."""
    queryset = Function.objects.all()
    serializer_class = FunctionSerializer
    permission_classes = []  # TODO: Agregar permisos RBAC
    
    @action(detail=False, methods=['get'])
    def by_module(self, request):
        """Listar funciones por módulo."""
        module = request.query_params.get('module')
        if module:
            functions = self.queryset.filter(module=module)
            serializer = self.get_serializer(functions, many=True)
            return Response(serializer.data)
        return Response({'error': 'Module required'}, status=400)
```

```python
# Actualizar: apps/access/serializers.py

class FunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Function
        fields = [
            'id', 'code', 'module', 'name', 
            'description', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
```

```python
# Actualizar: apps/access/urls.py

from rest_framework.routers import DefaultRouter
from .views import FunctionViewSet

router = DefaultRouter()
router.register('functions', FunctionViewSet, basename='function')

urlpatterns = router.urls
```

**Tests:**
```python
# tests/unit/access/test_function_api.py

def test_list_functions(api_client):
    response = api_client.get('/api/v1/access/functions/')
    assert response.status_code == 200
    
def test_get_functions_by_module(api_client):
    response = api_client.get('/api/v1/access/functions/by_module/?module=MOD_Users')
    assert response.status_code == 200
```

#### Tarea 2.2: UserFunctionAssignment API (3h)
```python
# Agregar a apps/access/views.py

class UserFunctionViewSet(viewsets.ViewSet):
    """Gestión de funciones de usuario."""
    
    @action(detail=False, methods=['post'])
    def assign(self, request):
        """Asignar función a usuario."""
        user_id = request.data.get('user_id')
        function_id = request.data.get('function_id')
        reason = request.data.get('reason', '')
        
        # Validar
        # Crear asignación
        # Retornar resultado
        
    @action(detail=False, methods=['post'])
    def revoke(self, request):
        """Revocar función de usuario."""
        # Implementar
        
    @action(detail=False, methods=['get'])
    def user_functions(self, request):
        """Listar funciones de un usuario."""
        user_id = request.query_params.get('user_id')
        # Implementar
```

#### Tarea 2.3: Integración con User.get_functions() (1h)
```python
# Actualizar apps/users/models.py

def get_functions(self):
    """Obtener funciones activas del usuario."""
    from apps.access.models import UserFunctionAssignment
    
    assignments = UserFunctionAssignment.objects.filter(
        user=self,
        is_active=True,
        function__is_active=True
    ).select_related('function')
    
    return [
        f"{a.function.code}: {a.function.name}" 
        for a in assignments
    ]
```

#### Tarea 2.4: Tests RBAC (2h)
```python
# tests/unit/access/test_rbac_integration.py

@pytest.mark.django_db
class TestRBACIntegration:
    def test_assign_function_to_user(self, api_client, sample_user):
        # Test completo de asignación
        pass
        
    def test_user_has_function(self, sample_user):
        # Test de verificación
        pass
        
    def test_revoke_function(self, api_client):
        # Test de revocación
        pass
```

**Checklist Día 2:**
- [ ] CRUD Functions completo
- [ ] Assign/Revoke implementado
- [ ] User.get_functions() conectado
- [ ] Tests RBAC pasan
- [ ] APIs documentadas

**Entregable Día 2:** RBAC funcional completo

---

## SPRINT 2: CRUD COMPLETO (DÍAS 3-4)

### DÍA 3 - USERS & CORE (8h)

#### Tarea 3.1: APIs Users faltantes (3h)
```python
# apps/users/views.py - agregar

@action(detail=True, methods=['post'])
def change_password(self, request, pk=None):
    """Cambiar contraseña."""
    user = self.get_object()
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not user.check_password(old_password):
        return Response({'error': 'Contraseña incorrecta'}, status=400)
    
    user.set_password(new_password)
    user.save()
    
    return Response({'success': True})

@action(detail=False, methods=['post'])
def reset_password(self, request):
    """Reset contraseña (admin)."""
    # Implementar
```

#### Tarea 3.2: APIs Core CRUD (3h)
```python
# apps/core/views.py - convertir ReadOnly a ModelViewSet

class CenterViewSet(viewsets.ModelViewSet):  # Cambiar de ReadOnlyModelViewSet
    queryset = Center.objects.all()
    serializer_class = CenterSerializer
    # Agregar permisos RBAC
    
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
```

#### Tarea 3.3: Tests (2h)
```python
# tests/unit/users/test_password_api.py
# tests/unit/core/test_centers_crud.py
# tests/unit/core/test_services_crud.py
```

**Checklist Día 3:**
- [ ] Change password
- [ ] Reset password
- [ ] Centers CRUD
- [ ] Services CRUD
- [ ] Tests pasan

---

### DÍA 4 - MODELOS REPORTS (8h)

#### Tarea 4.1: Crear modelos Reports (4h)
```python
# Crear archivo completo: apps/reports/models.py
# Ver especificación en Parte 3
```

#### Tarea 4.2: Crear serializers (2h)
```python
# Crear archivo completo: apps/reports/serializers.py
```

#### Tarea 4.3: Migraciones (1h)
```bash
python manage.py makemigrations reports
python manage.py migrate
```

#### Tarea 4.4: Tests modelos (1h)
```python
# tests/unit/reports/test_models.py
```

**Checklist Día 4:**
- [ ] Modelos Reports creados
- [ ] Serializers creados
- [ ] Migraciones aplicadas
- [ ] Tests modelos pasan

**Entregable Sprint 2:** CRUD completo + Modelos Reports

---

## SPRINT 3: REPORTS FUNCIONALES (DÍAS 5-6)  CORREGIDO

### DÍA 5: APIs Reports generación manual (6h)
- POST /api/v1/reports/generate/ (generación síncrona)
- GET /api/v1/reports/ (listar)
- GET /api/v1/reports/{id}/download/ (descarga)
- Exportación directa CSV/Excel/PDF

### DÍA 6: Dashboards (4h)
- APIs Dashboards CRUD
- API datos widgets (consultas en vivo)
- Tests Reports

**Entregable Sprint 3:** Reports funcionales (sin scheduling, sin emails)

---

## SPRINT 4: CALIDAD & DEPLOY (DÍAS 7-8)  CORREGIDO

### DÍA 7: Tests & Coverage (6h)
- Integration tests
- Coverage > 80%

### DÍA 8: Infra & Docs (6h)
- Docker
- CI/CD
- Documentación

**Entregable Sprint 4:** Proyecto production-ready

---

## RESUMEN PLAN COMPLETO

### CRONOGRAMA:

```
Sprint 0:  0.5 días  (Preparación)
Sprint 1:  2   días  (Fundación)
Sprint 2:  2   días  (CRUD)
Sprint 3:  2   días  (Reports - SIN scheduling)  CORREGIDO
Sprint 4:  2   días  (Calidad)  CORREGIDO
────────────────────
TOTAL:     8.5 días   CORREGIDO
```

### HITOS:

```
✓ Día 0:   Ambiente listo
✓ Día 1:   BD funcional, datos poblados
✓ Día 2:   RBAC completo
✓ Día 3:   Users & Core CRUD
✓ Día 4:   Modelos Reports
✓ Día 6:   Reports funcionales (manual)  CORREGIDO
✓ Día 8:   Production ready  CORREGIDO
```

### MÉTRICAS DE ÉXITO:

```
Migraciones:     100% aplicadas
Funciones RBAC:  44 pobladas
APIs:            40+ endpoints
Tests:           >150 tests
Coverage:        >80%
Documentación:   Completa
Deploy:          Automatizado
```

---

**FIN DEL ANÁLISIS PROFUNDO**

**Próximo paso:** Ejecutar Sprint 0 y comenzar implementación
