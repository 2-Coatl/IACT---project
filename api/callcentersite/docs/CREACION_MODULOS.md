# Guia de Creacion de Modulos - IACT Call Center System

## Resumen

Esta guia explica como crear y gestionar la estructura de modulos del sistema IACT, que controla el acceso y permisos de usuarios.

## Modelo Module

El modelo `Module` (en `apps.access.models`) representa la estructura jerarquica de modulos del sistema.

### Campos

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `code` | VARCHAR(50) | Codigo unico del modulo (ej: MOD_REPORTES) |
| `name` | VARCHAR(200) | Nombre para mostrar al usuario |
| `description` | TEXT | Descripcion detallada del modulo |
| `parent` | FK(Module) | Modulo padre (null para modulos raiz) |
| `order` | INT | Orden de visualizacion |
| `icon` | VARCHAR(50) | Nombre del icono (opcional) |
| `url_path` | VARCHAR(200) | Ruta URL del modulo |
| `is_active` | BOOLEAN | Indica si el modulo esta activo |
| `is_deleted` | BOOLEAN | Soft delete (historico) |
| `created_at` | TIMESTAMP | Fecha de creacion |
| `updated_at` | TIMESTAMP | Fecha de ultima actualizacion |

### Metodos

- `get_level()`: Calcula el nivel del modulo en la jerarquia
- `get_ancestors()`: Retorna lista de modulos ancestros
- `get_descendants()`: Retorna lista de modulos descendientes

## Metodos de Creacion

### Opcion 1: Management Command (Recomendado)

```bash
# Simular creacion (no guarda cambios)
python manage.py create_modules --dry-run

# Ejecutar creacion
python manage.py create_modules

# Limpiar y crear (elimina modulos existentes)
python manage.py create_modules --clear
```

**Ventajas:**
- Facil de usar
- Modo dry-run para verificar
- Muestra arbol jerarquico
- Maneja dependencias automaticamente

### Opcion 2: Fixtures JSON

```bash
# Cargar fixtures
python manage.py loaddata initial_modules

# O especificamente
python manage.py loaddata apps/access/fixtures/initial_modules.json
```

**Ventajas:**
- Reproducible
- Versionable en Git
- Facil de compartir

### Opcion 3: Script Python

```bash
# Ejecutar script directamente
python manage.py shell < scripts/create_modules.py
```

**Ventajas:**
- Maxima flexibilidad
- Facil de customizar

### Opcion 4: Django ORM Directamente

```python
from apps.access.models import Module

# Crear modulo padre
reportes = Module.objects.create(
    code='MOD_REPORTES',
    name='Reportes',
    description='Modulo principal de reportes',
    parent=None,
    order=1,
    url_path='/reportes',
    is_active=True,
)

# Crear submodulo
Module.objects.create(
    code='MOD_REPORTES_DIARIO',
    name='Reporte Diario',
    description='Reporte de actividad diaria',
    parent=reportes,  # Referencia al objeto padre
    order=1,
    url_path='/reportes/diario',
    is_active=True,
)
```

## Ejemplo de Flujo Completo

### Paso 1: Crear modulo padre

```python
from apps.access.models import Module

# Modulo raiz
reportes = Module.objects.create(
    code='MOD_REPORTES',
    name='Reportes',
    description='Modulo principal de reportes del sistema',
    parent=None,
    order=1,
    url_path='/reportes',
    is_active=True,
)
```

### Paso 2: Crear submodulos

```python
# Primer submodulo
reporte_diario = Module.objects.create(
    code='MOD_REPORTES_DIARIO',
    name='Reporte Diario',
    parent=reportes,  # Mismo padre
    order=1,
    url_path='/reportes/diario',
    is_active=True,
)

# Segundo submodulo
reporte_acumulado = Module.objects.create(
    code='MOD_REPORTES_ACUMULADO',
    name='Reporte Acumulado',
    parent=reportes,  # Mismo padre
    order=2,
    url_path='/reportes/acumulado',
    is_active=True,
)
```

### Paso 3: Verificar jerarquia

```python
# Ver todos los modulos
Module.objects.all()

# Ver jerarquia
for root in Module.objects.filter(parent__isnull=True):
    print(f"{root.code} - {root.name}")
    for child in root.children.all():
        print(f"  - {child.code} - {child.name}")

# Verificar niveles
module = Module.objects.get(code='MOD_REPORTES_DIARIO')
print(f"Nivel: {module.get_level()}")  # Debe ser 1
```

## Estructura Resultante

```
[MOD_REPORTES] Reportes
   URL: /reportes
   - [MOD_REPORTES_DIARIO] Reporte Diario
      URL: /reportes/diario
   - [MOD_REPORTES_ACUMULADO] Reporte Acumulado
      URL: /reportes/acumulado

[MOD_ONBOARDING] OnBoarding
   URL: /onboarding
   - [MOD_ONBOARDING_MATRIZ] Matriz de Asesores
      URL: /onboarding/matriz-asesores
```

## Verificacion

### Via API

```bash
# Obtener arbol de modulos
curl http://localhost:8000/api/v1/access/modules/tree/

# Obtener modulos del usuario
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/access/my-modules/
```

### Via Shell

```python
python manage.py shell

from apps.access.models import Module

# Ver todos los modulos
Module.objects.all()

# Ver jerarquia
for root in Module.objects.filter(parent__isnull=True):
    print(f"\n{root.code} - {root.name}")
    for child in root.children.all():
        print(f"  - {child.code} - {child.name}")

# Verificar niveles
module = Module.objects.get(code='MOD_REPORTES_DIARIO')
print(f"Nivel: {module.get_level()}")
print(f"Ancestros: {module.get_ancestors()}")
```

### Via Admin

```bash
# Abrir Django Admin
http://localhost:8000/admin/access/module/
```

## Asignacion de Modulos a Usuarios

```python
from apps.access.models import Module, UserModuleAccess
from apps.users.models import User

# Obtener usuario
user = User.objects.get(username='juan')

# Obtener modulo
module = Module.objects.get(code='MOD_REPORTES')

# Asignar acceso
UserModuleAccess.objects.create(
    user=user,
    module=module,
    granted_by=admin_user,
    reason='Acceso a reportes del sistema',
)

# Usuario ahora puede acceder a:
# - MOD_REPORTES (asignado directamente)
# - MOD_REPORTES_DIARIO (hijo automatico)
# - MOD_REPORTES_ACUMULADO (hijo automatico)
```

## Convencion de Nombres

### Codigos de Modulos

- Prefijo: `MOD_`
- Estructura: `MOD_<AREA>_<FUNCIONALIDAD>`
- Ejemplos:
  - `MOD_REPORTES`
  - `MOD_REPORTES_DIARIO`
  - `MOD_ONBOARDING_MATRIZ`

### URLs

- Rutas modernas con `/`
- Minusculas y separadas por guiones
- Ejemplos:
  - `/reportes`
  - `/reportes/diario`
  - `/onboarding/matriz-asesores`

## Personalizacion

### Agregar nuevos modulos

Editar `apps/access/management/commands/create_modules.py`:

```python
modules = [
    # ... modulos existentes ...
    
    # Nuevo modulo
    {
        'code': 'MOD_TU_MODULO',
        'name': 'Tu Modulo',
        'description': 'Descripcion del modulo',
        'parent_code': None,  # o codigo del padre
        'order': 3,
        'icon': None,
        'url_path': '/tu/ruta',
    },
]
```

## Consideraciones

### IDs Auto-incrementales

Django genera IDs automaticamente. No se deben especificar manualmente a menos que uses fixtures JSON.

### Referencias Padre

En lugar de IDs, usar objetos: `parent=modulo_padre` en vez de `parent_id=123`.

### Nivel Jerarquico

No se almacena explicitamente. Se calcula dinamicamente con `module.get_level()`.

### SoftDelete

Los modulos nunca se eliminan permanentemente. Usar `is_deleted=True` para marcarlos como eliminados.

## Ejemplos de Fixtures JSON

### Modulo Raiz

```json
{
    "model": "access.module",
    "pk": 1,
    "fields": {
        "code": "MOD_REPORTES",
        "name": "Reportes",
        "parent": null,
        "order": 1,
        "url_path": "/reportes",
        "is_active": true
    }
}
```

### Submodulo

```json
{
    "model": "access.module",
    "pk": 2,
    "fields": {
        "code": "MOD_REPORTES_DIARIO",
        "name": "Reporte Diario",
        "parent": 1,
        "order": 1,
        "url_path": "/reportes/diario",
        "is_active": true
    }
}
```

## Recursos

- Modelo Module: `apps/access/models.py`
- Fixtures: `apps/access/fixtures/initial_modules.json`
- Management Command: `apps/access/management/commands/create_modules.py`
- Script: `scripts/create_modules.py`
- API: `/api/v1/access/modules/`
- Tests: `tests/api/test_access_api.py`

## Comandos Utiles

```bash
# Crear modulos
python manage.py create_modules

# Ver modulos en shell
python manage.py shell -c "from apps.access.models import Module; print(Module.objects.all())"

# Cargar fixtures
python manage.py loaddata initial_modules

# Ver arbol via API
curl http://localhost:8000/api/v1/access/modules/tree/

# Ejecutar tests
pytest tests/api/test_access_api.py
```

---

Ultima actualizacion: 2024 - Remediacion Post Sprint 3
