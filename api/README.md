# IACT Call Center System

Sistema Analytics Call Center con Django REST Framework.

## Compliance CNST v2.2.1

 **100% Compliant**
- CNST-001: NO email
- CNST-002: SESSION_ENGINE='db'
- CNST-003: Dual database (READ-ONLY ivr_legacy)
- CNST-004: NO Celery, NO Channels
- CNST-005: Throttling + MAX_PAGE_SIZE
- CNST_TECNICAS: NO Sentry, NO Redis

## Stack Tecnológico

- Python 3.11+
- Django 5.0+
- Django REST Framework 3.14+
- PostgreSQL 16 (analytics)
- MariaDB 11.4 (ivr_legacy READ-ONLY)
- pytest + FactoryBoy

## Setup

```bash
# 1. Crear virtualenv
cd callcentersite
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r ../requirements/development.txt

# 3. Configurar .env
cp .env.example .env
# Editar .env con configuración

# 4. Migrations
python manage.py migrate

# 5. Crear superuser
python manage.py createsuperuser

# 6. Runserver
python manage.py runserver
```

## Tests

```bash
# Todos los tests
pytest

# Solo unit tests
pytest -m unit

# Con coverage
pytest --cov
```

## Documentación

Ver `docs/` para:
- Arquitectura
- API Reference
- Casos de Uso
- Planning

## Estructura

```
iact-project/
├── callcentersite/       # Proyecto Django
│   ├── apps/             # Apps Django
│   ├── config/           # Settings
│   ├── tests/            # Tests
│   └── venv/             # Virtualenv
├── deployment/           # Scripts deployment
├── docs/                 # Documentación
└── requirements/         # Dependencies
```

## License

Proprietary - IACT © 2024
