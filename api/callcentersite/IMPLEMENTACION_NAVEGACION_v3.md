# SISTEMA DE NAVEGACION IMPLEMENTADO v3.0.0

**Fecha:** 16 de enero de 2026  
**Ubicacion:** /tmp/iact-project/callcentersite  
**Estado:** IMPLEMENTADO Y LISTO PARA PRUEBAS

---

## QUE SE IMPLEMENTO

### 1. Management Command (create_modules)

**Ubicacion:**
```
apps/core/management/commands/create_modules.py
```

**Como usar:**
```bash
# Dry-run (ver que haria)
python manage.py create_modules --dry-run --verbose

# Generar estructura completa
python manage.py create_modules --verbose

# Generar solo un modulo
python manage.py create_modules --module=reports --verbose
```

**Que genera:**
- Estructura de modulos en `modules/`
- Metadata de navegacion con IDs numericos
- Archivos __init__.py y README.md
- Archivos metadata.json por caso de uso

---

### 2. Menu Builder

**Ubicacion:**
```
apps/core/navigation/builders.py
```

**Clases:**
- `MenuBuilder`: Construye menus personalizados
- `MenuSerializer`: Serializa para API
- `MenuValidator`: Valida IDs numericos

**Caracteristicas:**
- Filtra por permisos RBAC
- Valida iconos fisicos
- Personaliza con datos del usuario
- Valida IDs numericos

---

### 3. API Navigation

**Ubicacion:**
```
apps/core/navigation/views.py
apps/core/navigation/urls.py
```

**Endpoint:**
```
GET /api/v1/navigation/menu/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "menu": [
    {
      "id_menu": 5,
      "des_name": "Reportes",
      "icon": "/static/icons/menu/reports.png",
      "nivel": 1,
      "orden": 50,
      "submenus": [
        {
          "id_menu": 501,
          "des_name": "Reporte Trimestral",
          "endpoint": {
            "url": "/api/reports/quarterly/",
            "method": "GET"
          }
        }
      ]
    }
  ]
}
```

---

### 4. Modelo User Extendido

**Ubicacion:**
```
apps/users/models.py
```

**Nuevos campos:**
- `avatar`: ImageField para foto de perfil
- `phone`: CharField para telefono
- `position`: CharField para cargo
- `employee_id`: CharField para ID de empleado

**Nuevos metodos:**
- `get_avatar_url()`: Retorna URL del avatar o default
- `get_functions()`: Retorna funciones RBAC del usuario
- `has_function(name)`: Verifica si tiene una funcion
- `has_any_function(names)`: Verifica si tiene alguna funcion
- `has_all_functions(names)`: Verifica si tiene todas las funciones
- `delete_avatar()`: Elimina archivo fisico del avatar

---

### 5. API Avatar y Perfil

**Ubicacion:**
```
apps/users/views.py
apps/users/urls.py
```

**Endpoints:**

**POST /api/v1/users/upload-avatar/**
```bash
# Upload avatar
curl -X POST http://localhost:8000/api/v1/users/upload-avatar/ \
  -H "Authorization: Bearer {token}" \
  -F "avatar=@avatar.jpg"
```

**DELETE /api/v1/users/delete-avatar/**
```bash
# Delete avatar
curl -X DELETE http://localhost:8000/api/v1/users/delete-avatar/ \
  -H "Authorization: Bearer {token}"
```

**GET /api/v1/users/profile/**
```bash
# Get profile
curl http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer {token}"
```

**PUT /api/v1/users/profile/update/**
```bash
# Update profile
curl -X PUT http://localhost:8000/api/v1/users/profile/update/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Juan", "last_name": "Perez"}'
```

---

### 6. Estructura de Archivos

**Directorios creados:**
```
callcentersite/
├── apps/
│   ├── core/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── create_modules.py
│   │   └── navigation/
│   │       ├── __init__.py
│   │       ├── builders.py
│   │       ├── views.py
│   │       └── urls.py
│   └── users/
│       ├── models.py (ACTUALIZADO)
│       ├── views.py (ACTUALIZADO)
│       └── urls.py (ACTUALIZADO)
│
├── static/icons/
│   ├── menu/
│   │   └── .gitkeep
│   ├── submenu/
│   │   └── .gitkeep
│   └── defaults/
│       └── .gitkeep
│
├── media/profiles/
│   └── .gitkeep
│
└── modules/
    └── (se genera con create_modules)
```

---

### 7. Configuracion (settings)

**Agregado a config/settings/base.py:**
```python
# Avatar settings
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
```

**Agregado a config/urls.py:**
```python
path('api/v1/navigation/', include('apps.core.navigation.urls')),
```

---

## SIGUIENTES PASOS

### 1. Crear migraciones

```bash
cd /tmp/iact-project/callcentersite
python manage.py makemigrations users
```

Deberia crear una migracion para los nuevos campos:
- avatar
- phone
- position
- employee_id

### 2. Aplicar migraciones

```bash
python manage.py migrate
```

### 3. Generar modulos

```bash
python manage.py create_modules --verbose
```

Esto creara:
```
modules/
├── MODULES_METADATA.json
├── auth/
├── users/
├── access/
├── pipeline/
├── reports/
├── alerts/
├── audit/
└── logs/
```

### 4. Crear metadata de navegacion

Para cada app, crear:
```
apps/{app}/navigation/menu_metadata.json
```

**Ejemplo para reports:**
```json
{
  "module": "MOD_Reports",
  "app": "reports",
  "menu_tree": [
    {
      "nivel": 1,
      "id_menu": 5,
      "des_name": "Reportes",
      "icon": "/static/icons/menu/reports.png",
      "orden": 50,
      "required_functions": [],
      "submenus": [
        {
          "id_menu": 501,
          "des_name": "Reporte Trimestral",
          "icon": "/static/icons/submenu/quarterly_report.png",
          "endpoint": "/api/reports/quarterly/",
          "method": "GET",
          "orden": 1,
          "required_functions": ["RPT-001: view_reports"]
        }
      ]
    }
  ]
}
```

### 5. Poblar iconos

Copiar imagenes a:
```
static/icons/menu/*.png
static/icons/submenu/*.png
static/icons/defaults/avatar_default.png
```

### 6. Probar endpoints

**a) Crear superusuario:**
```bash
python manage.py createsuperuser
```

**b) Obtener token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

**c) Probar menu:**
```bash
curl http://localhost:8000/api/v1/navigation/menu/ \
  -H "Authorization: Bearer {token}"
```

**d) Probar perfil:**
```bash
curl http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer {token}"
```

**e) Subir avatar:**
```bash
curl -X POST http://localhost:8000/api/v1/users/upload-avatar/ \
  -H "Authorization: Bearer {token}" \
  -F "avatar=@test.jpg"
```

---

## ESQUEMA DE IDs NUMERICOS

### Nivel 1 (Menus): 1-99
```
1 - Autenticacion
2 - Usuarios
3 - Permisos
4 - ETL Pipeline
5 - Reportes
6 - Alertas
7 - Auditoria
8 - Logs del Sistema
```

### Nivel 2 (Submenus): 100-999
```
101-199: Autenticacion
201-299: Usuarios
301-399: Permisos
401-499: ETL Pipeline
501-599: Reportes
601-699: Alertas
701-799: Auditoria
801-899: Logs del Sistema
```

---

## ARCHIVOS MODIFICADOS

### Nuevos archivos:
- apps/core/management/__init__.py
- apps/core/management/commands/__init__.py
- apps/core/management/commands/create_modules.py
- apps/core/navigation/__init__.py
- apps/core/navigation/builders.py
- apps/core/navigation/views.py
- apps/core/navigation/urls.py

### Archivos modificados:
- apps/users/models.py (backup en models.py.backup)
- apps/users/views.py
- apps/users/urls.py
- config/urls.py
- config/settings/base.py

### Directorios creados:
- static/icons/menu/
- static/icons/submenu/
- static/icons/defaults/
- media/profiles/
- modules/

---

## VALIDACIONES

### 1. Verificar estructura
```bash
tree apps/core/navigation/
tree static/icons/
tree media/profiles/
```

### 2. Verificar imports
```bash
python manage.py check
```

### 3. Verificar migraciones
```bash
python manage.py makemigrations --dry-run
python manage.py migrate --plan
```

---

## TROUBLESHOOTING

### Error: No module named 'PIL'

**Solucion:**
```bash
pip install Pillow
```

### Error: MEDIA_ROOT not configured

**Verificar en settings/base.py:**
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Error: Menu vacio

**Causa:** Usuario no tiene funciones RBAC.

**Solucion:**
```python
from django.contrib.auth import get_user_model
from apps.access.models import Function

User = get_user_model()
user = User.objects.get(username='admin')
func = Function.objects.get(name='view_reports')
# Asignar funcion al usuario
```

---

## DOCUMENTACION COMPLETA

Ver archivos en /mnt/user-data/outputs/:
- README_SISTEMA_COMPLETO_v3.md
- RESUMEN_FINAL_SISTEMA_v3.md

---

**Implementado por:** Claude  
**Version:** 3.0.0  
**Estado:** LISTO PARA PRUEBAS
