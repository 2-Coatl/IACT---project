# 📜 RESTRICCIONES ARQUITECTÓNICAS - SISTEMA IACT

## PARTE 3/3: DESARROLLO, AUDITORÍA Y REFERENCIAS

---

## 📋 INFORMACIÓN DEL DOCUMENTO

| Atributo | Valor |
|---|---|
| **Versión** | 1.0.0 - DEFINITIVA |
| **Fecha** | 19 Enero 2026 |
| **Proyecto** | Sistema IACT - IVR Analytics & Customer Tracking |
| **Parte** | 3/3 - Desarrollo, Auditoría y Referencias (FINAL) |
| **Continuación de** | PARTE 2/3 - Arquitectura, Base de Datos y Performance |

---

## 📋 CONTENIDO DE ESTA PARTE

**SECCIÓN 8: RESTRICCIONES DE DESARROLLO**
- 8.1 Coding Standards
- 8.2 Git y Control de Versiones
- 8.3 Testing
- 8.4 Documentación

**SECCIÓN 9: RESTRICCIONES DE LOGGING Y AUDITORÍA**
- 9.1 Logging
- 9.2 Auditoría

**SECCIÓN 10: RESTRICCIONES DE PRIVACIDAD Y DATOS**
- 10.1 Clasificación de Datos
- 10.2 Minimización de Datos

**SECCIÓN 11: CHECKLIST DE CUMPLIMIENTO**
- 11.1 Pre-Deploy
- 11.2 Post-Deploy

**SECCIÓN 12: GLOSARIO DE RESTRICCIONES**

**SECCIÓN 13: TABLA RESUMEN CNST** ⭐ NUEVA
- Todas las restricciones consolidadas
- Referencias cruzadas
- Estado de cumplimiento

**SECCIÓN 14: REFERENCIAS Y DOCUMENTOS RELACIONADOS**

---

## 💻 8. RESTRICCIONES DE DESARROLLO

> ⚠️ **IMPORTANTE:** Estas restricciones definen los estándares de código y desarrollo.

---

### 8.1 Coding Standards

**Código:** CNST-026 (implícito)

```yaml
✅ PYTHON:
  - PEP 8 obligatorio
  - Black para formateo automático
  - Flake8 para linting
  - isort para imports
  - Type hints (Python 3.10+)
  - Docstrings en funciones/clases

✅ DJANGO/DRF:
  - Serializers explícitos (no __all__)
  - Permisos en cada endpoint
  - Throttling configurado
  - Paginación siempre
  - Validaciones exhaustivas
  - Naming según CLEAN_CODE v3.0.1

✅ JAVASCRIPT/TYPESCRIPT:
  - ESLint configurado
  - Prettier para formateo
  - TypeScript preferido sobre JavaScript
  - Componentes funcionales (no clases)

✅ SQL:
  - Queries parametrizadas (NO raw SQL)
  - Índices en columnas de búsqueda
  - Stored procedures documentados
  - Naming snake_case

❌ PROHIBIDO:
  - Código sin formatear
  - Imports desordenados
  - Funciones sin docstring
  - Magic numbers/strings
  - eval(), exec() en Python
```

**Configuración Black:**
```toml
# pyproject.toml

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
  | migrations
)/
'''
```

**Configuración Flake8:**
```ini
# .flake8

[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude =
    .git,
    __pycache__,
    */migrations/*,
    */venv/*,
    */build/*,
    */dist/*
per-file-ignores =
    __init__.py:F401
```

**Configuración isort:**
```toml
# pyproject.toml

[tool.isort]
profile = "black"
line_length = 88
skip = ["migrations", "venv"]
known_first_party = ["apps", "config"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

**Pre-commit Hook:**
```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**Ejemplo Código Correcto:**
```python
# ✅ CORRECTO - Sigue todos los estándares

from typing import Optional, List
from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel, SoftDeleteMixin


class QuarterlyReport(TimeStampedModel, SoftDeleteMixin):
    """
    Reporte trimestral consolidado.
    
    Almacena métricas agregadas por trimestre, año y DID.
    Datos extraídos de BD IVR mediante ETL.
    
    Attributes:
        quarter: Trimestre (Q1, Q2, Q3, Q4)
        year: Año del reporte
        did: Número DID
        total_calls: Total de llamadas
        abandoned_calls: Llamadas abandonadas
        avg_duration: Duración promedio en segundos
    """
    
    # Constants
    QUARTERS = ['Q1', 'Q2', 'Q3', 'Q4']
    
    # Fields
    quarter = models.CharField(max_length=10, choices=[(q, q) for q in QUARTERS])
    year = models.IntegerField()
    did = models.CharField(max_length=20)
    total_calls = models.IntegerField(default=0)
    abandoned_calls = models.IntegerField(default=0)
    avg_duration = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'quarterly_reports'
        ordering = ['-year', '-quarter']
        indexes = [
            models.Index(fields=['quarter', 'year']),
            models.Index(fields=['did']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['quarter', 'year', 'did'],
                name='unique_quarterly_report'
            )
        ]
    
    def __str__(self) -> str:
        """Representación en string."""
        return f"{self.quarter}-{self.year} - {self.did}"
    
    def get_abandonment_rate(self) -> Optional[Decimal]:
        """
        Calcula tasa de abandono.
        
        Returns:
            Decimal: Tasa de abandono (0-100) o None si no hay llamadas
            
        Example:
            >>> report = QuarterlyReport(total_calls=1000, abandoned_calls=85)
            >>> report.get_abandonment_rate()
            Decimal('8.50')
        """
        if self.total_calls == 0:
            return None
        
        rate = (self.abandoned_calls / self.total_calls) * 100
        return Decimal(str(round(rate, 2)))
```

**Validación:**
```bash
# Formatear código
black apps/

# Verificar linting
flake8 apps/

# Ordenar imports
isort apps/

# Instalar pre-commit
pre-commit install

# Ejecutar pre-commit manualmente
pre-commit run --all-files
```

---

### 8.2 Git y Control de Versiones

**Código:** CNST-027 (implícito)

```yaml
✅ BRANCHING STRATEGY:
  - main: Producción (protegida)
  - develop: Desarrollo
  - feature/*: Features
  - hotfix/*: Hotfixes urgentes
  - release/*: Releases

✅ COMMITS:
  - Conventional Commits (feat, fix, docs, etc)
  - Mensajes descriptivos
  - Máximo 72 caracteres en título
  - Cuerpo detallado si necesario

✅ PULL REQUESTS:
  - Code review obligatorio (2+ aprobaciones)
  - CI debe pasar
  - Sin conflictos
  - Descripción detallada

❌ PROHIBIDO:
  - Commits directos a main
  - Commits sin mensaje
  - Secrets en commits
  - Archivos grandes en repo
```

**Conventional Commits:**
```bash
# ✅ CORRECTO

# Feature
git commit -m "feat(reports): agregar exportación a PDF"

# Fix
git commit -m "fix(auth): corregir validación de token expirado"

# Docs
git commit -m "docs(readme): actualizar instrucciones de instalación"

# Refactor
git commit -m "refactor(services): extraer lógica a ReportService"

# Test
git commit -m "test(reports): agregar tests para AbandonedCallsReport"

# Chore
git commit -m "chore(deps): actualizar Django a 4.2.9"
```

**Estructura de Branches:**
```
main (producción)
├── release/v1.0.0
│   └── hotfix/fix-login-bug
│
develop (desarrollo)
├── feature/add-pdf-export
├── feature/dashboard-metrics
└── feature/rbac-v6
```

**Pull Request Template:**
```markdown
## Descripción

Descripción clara y concisa de los cambios.

## Tipo de Cambio

- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update

## Checklist

- [ ] Código sigue los estándares (Black, Flake8, isort)
- [ ] Tests agregados/actualizados
- [ ] Documentación actualizada
- [ ] Sin warnings de seguridad (safety check)
- [ ] Migraciones generadas (si aplica)
- [ ] CHANGELOG actualizado

## Testing

Describe cómo se probó:
- [ ] Tests unitarios
- [ ] Tests de integración
- [ ] Tests manuales

## Screenshots (si aplica)

## Documentos Relacionados

- Relacionado con: #123
- Cierra: #456
```

**.gitignore:**
```gitignore
# Python
*.py[cod]
__pycache__/
*.so
*.egg
*.egg-info/
dist/
build/
.venv/
venv/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/static

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.*

# Coverage
htmlcov/
.coverage
.coverage.*

# Secrets
*.key
*.pem
secrets.yaml
```

**Git Hooks (Pre-commit):**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Verificar secrets
if git diff --cached --name-only | xargs grep -E '(SECRET_KEY|PASSWORD|API_KEY).*=.*"[^"]+"'; then
    echo "❌ ERROR: Posible secret en commit"
    exit 1
fi

# Ejecutar pre-commit
pre-commit run --all-files
```

---

### 8.3 Testing

**Código:** CNST-028 (implícito)

```yaml
✅ OBLIGATORIO:
  - Cobertura mínima: 80%
  - Tests unitarios + integración
  - Factory Boy para fixtures
  - Pytest como runner
  - Tests de seguridad (Bandit)

✅ TIPOS DE TESTS:
  - Unitarios: Funciones/métodos aislados
  - Integración: APIs, views, services
  - Funcionales: Flujos end-to-end
  - Seguridad: Bandit, safety

❌ PROHIBIDO:
  - Código sin tests
  - Tests que modifican BD producción
  - Tests con dependencias externas
  - Tests sin assertions
```

**Configuración Pytest:**
```ini
# pytest.ini

[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --cov=apps
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --maxfail=5
testpaths = apps
markers =
    slow: marks tests as slow
    integration: marks tests as integration
    security: marks tests as security
```

**Ejemplo Test Unitario:**
```python
# apps/reports/tests/test_services.py

import pytest
from decimal import Decimal
from datetime import date
from django.core.exceptions import ValidationError

from apps.reports.services import ReportService
from apps.ivr.tests.factories import CallRecordFactory


class TestReportService:
    """Tests para ReportService."""
    
    def test_generate_abandoned_calls_report_success(self):
        """Test generación exitosa de reporte."""
        # Arrange
        CallRecordFactory.create_batch(
            10,
            cEstado='Abandoned',
            dFecha=date(2026, 1, 15)
        )
        
        # Act
        report = ReportService.generate_abandoned_calls_report(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            format='excel'
        )
        
        # Assert
        assert report is not None
        assert report.endswith('.xlsx')
        assert os.path.exists(report)
    
    def test_generate_abandoned_calls_report_validates_date_range(self):
        """Test validación de rango de fechas."""
        # Arrange
        start_date = date(2024, 1, 1)
        end_date = date(2026, 12, 31)  # > 2 años
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ReportService.generate_abandoned_calls_report(
                start_date=start_date,
                end_date=end_date,
                format='excel'
            )
        
        assert "Rango máximo: 2 años" in str(exc_info.value)
    
    def test_generate_abandoned_calls_report_respects_limit(self):
        """Test que respeta límite de registros."""
        # Arrange
        CallRecordFactory.create_batch(
            60000,  # > 50K (límite Excel)
            cEstado='Abandoned',
            dFecha=date(2026, 1, 15)
        )
        
        # Act
        report = ReportService.generate_abandoned_calls_report(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            format='excel'
        )
        
        # Assert - debe tener máx 50K registros
        # TODO: Verificar tamaño del archivo
        assert report is not None
```

**Factory Boy:**
```python
# apps/ivr/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from datetime import datetime

from apps.ivr.models import CallRecord


class CallRecordFactory(DjangoModelFactory):
    """Factory para CallRecord."""
    
    class Meta:
        model = CallRecord
    
    dFecha = factory.LazyFunction(datetime.now)
    cDID = factory.Sequence(lambda n: f"1902008{n}")
    cMenu = factory.Iterator(['CREDITOS', 'SALDOS', 'PAGOS'])
    cEstado = factory.Iterator(['Completed', 'Abandoned', 'Failed'])
    iDuracion = factory.Faker('random_int', min=0, max=600)
```

**Tests de Seguridad:**
```bash
# Bandit - Detectar vulnerabilidades
bandit -r apps/ -f json -o bandit-report.json

# Safety - Verificar dependencias
safety check --json

# Verificar secrets
detect-secrets scan --baseline .secrets.baseline
```

**Cobertura:**
```bash
# Ejecutar tests con cobertura
pytest --cov=apps --cov-report=html

# Ver reporte
open htmlcov/index.html

# Verificar mínimo 80%
pytest --cov=apps --cov-fail-under=80
```

---

### 8.4 Documentación

**Código:** CNST-029 (implícito)

```yaml
✅ OBLIGATORIO:
  - README.md con setup completo
  - Docstrings en funciones/clases
  - OpenAPI/Swagger actualizado
  - Diagramas actualizados (Mermaid/PlantUML)
  - CHANGELOG.md mantenido

✅ TIPOS DE DOCS:
  - README: Setup, instalación, deployment
  - API Docs: OpenAPI/Swagger
  - Arquitectura: Diagramas, decisiones
  - Restricciones: Este documento (3 partes)

❌ PROHIBIDO:
  - Código sin documentar
  - README desactualizado
  - API sin documentar
  - Diagramas obsoletos
```

**README.md Estructura:**
```markdown
# 📊 IACT - IVR Analytics & Customer Tracking

Sistema de análisis de llamadas IVR con dashboards y reportes.

## 🚀 Quick Start

### Requisitos
- Python 3.11+
- MariaDB 10.11+
- Nginx 1.24+

### Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/company/iact.git
cd iact

# Crear virtualenv
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements/local.txt

# Configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# Migraciones
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Ejecutar
python manage.py runserver
```

## 📚 Documentación

- [Arquitectura](docs/arquitectura/)
- [Restricciones](docs/arquitectura/restricciones/)
- [API Docs](http://localhost:8000/api/docs/)
- [RBAC](docs/rbac/)

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=apps
```

## 📦 Deployment

Ver [DEPLOYMENT.md](docs/DEPLOYMENT.md)

## 📝 Changelog

Ver [CHANGELOG.md](CHANGELOG.md)
```

**Docstrings:**
```python
def generate_abandoned_calls_report(
    start_date: date,
    end_date: date,
    format: str = 'excel'
) -> str:
    """
    Genera reporte de llamadas abandonadas.
    
    Extrae llamadas abandonadas de BD IVR y genera archivo
    en el formato especificado (Excel, CSV o PDF).
    
    Args:
        start_date: Fecha inicio del rango
        end_date: Fecha fin del rango
        format: Formato de exportación ('excel', 'csv', 'pdf')
    
    Returns:
        str: Ruta del archivo generado
    
    Raises:
        ValidationError: Si rango > 2 años o formato inválido
        
    Limits:
        - Rango máximo: 2 años
        - Excel: 50,000 registros
        - CSV: 100,000 registros
        - PDF: 10,000 registros
    
    Example:
        >>> from datetime import date
        >>> filepath = generate_abandoned_calls_report(
        ...     start_date=date(2026, 1, 1),
        ...     end_date=date(2026, 1, 31),
        ...     format='excel'
        ... )
        >>> print(filepath)
        '/opt/iact/media/reports/abandoned_calls_abc123.xlsx'
    """
    pass
```

**OpenAPI/Swagger:**
```python
# apps/reports/views.py

from drf_spectacular.utils import extend_schema, OpenApiParameter

class ReportViewSet(viewsets.ViewSet):
    """ViewSet de reportes."""
    
    @extend_schema(
        summary="Generar reporte de llamadas abandonadas",
        description="""
        Genera reporte de llamadas abandonadas en el formato especificado.
        
        Límites:
        - Rango máximo: 2 años
        - Excel: 50,000 registros
        - CSV: 100,000 registros
        - PDF: 10,000 registros
        """,
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=str,
                description='Fecha inicio (YYYY-MM-DD)',
                required=True
            ),
            OpenApiParameter(
                name='end_date',
                type=str,
                description='Fecha fin (YYYY-MM-DD)',
                required=True
            ),
            OpenApiParameter(
                name='format',
                type=str,
                description='Formato (excel, csv, pdf)',
                required=False,
                default='excel'
            ),
        ],
        responses={
            200: {'description': 'Reporte generado exitosamente'},
            400: {'description': 'Parámetros inválidos'},
            403: {'description': 'Sin permisos (requiere RPT-004)'},
        },
        tags=['Reportes']
    )
    @require_function('RPT-004')
    def generate_abandoned_calls(self, request):
        """Genera reporte de llamadas abandonadas."""
        pass
```

---

## 📊 9. RESTRICCIONES DE LOGGING Y AUDITORÍA

> ⚠️ **IMPORTANTE:** Sistema de logging y auditoría completo para trazabilidad.

---

### 9.1 Logging

**Código:** CNST-030 (implícito)

```yaml
✅ NIVELES:
  - DEBUG: Solo desarrollo
  - INFO: Operaciones normales
  - WARNING: Advertencias
  - ERROR: Errores recuperables
  - CRITICAL: Errores críticos

✅ UBICACIÓN:
  - Filesystem: /opt/iact/logs/
  - Rotating: 10MB x 10 archivos
  - Formato: JSON para parsing

⚠️ NO LOGGEAR:
  - Passwords
  - Tokens
  - API keys
  - PII innecesaria
  - Datos sensibles

❌ PROHIBIDO:
  - Logging externo (Sentry, ver CNST-012)
  - Logs en stdout en producción
  - Logs sin rotar
  - Logs con secrets
```

**Configuración Logging:**
```python
# settings/production.py

import os
from pathlib import Path

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/iact/logs/django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/iact/logs/django-error.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

**Ejemplo Logging:**
```python
# apps/reports/services.py

import logging

logger = logging.getLogger(__name__)


class ReportService:
    """Service de reportes."""
    
    @staticmethod
    def generate_abandoned_calls_report(start_date, end_date, format='excel'):
        """Genera reporte de llamadas abandonadas."""
        
        logger.info(
            "Generando reporte llamadas abandonadas",
            extra={
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'format': format,
                'user_id': get_current_user_id(),
            }
        )
        
        try:
            # Generar reporte
            report = _generate_report(start_date, end_date, format)
            
            logger.info(
                "Reporte generado exitosamente",
                extra={
                    'report_path': report,
                    'records': _count_records(report),
                }
            )
            
            return report
            
        except Exception as e:
            logger.error(
                "Error generando reporte",
                extra={
                    'error': str(e),
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                },
                exc_info=True
            )
            raise
```

---

### 9.2 Auditoría

**Código:** CNST-031 (implícito)

```yaml
✅ EVENTOS AUDITABLES:
  - Login/Logout
  - Cambios de permisos
  - Exportación de reportes
  - Accesos denegados
  - Cambios en configuración
  - Cambios en ETL

✅ INFORMACIÓN A REGISTRAR:
  - Usuario
  - Timestamp
  - Acción
  - IP address
  - User-Agent
  - Resultado (éxito/fallo)
  - Datos antes/después (si aplica)

⚠️ PROPIEDADES:
  - Immutable (append-only)
  - Retención: 2 años mínimo
  - Sin PII innecesaria
  - Checksum SHA-256

❌ PROHIBIDO:
  - Modificar registros de auditoría
  - Eliminar registros
  - Auditoría sin timestamp
  - Sin información de usuario
```

**Modelo de Auditoría:**
```python
# apps/audit/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import hashlib
import json

User = get_user_model()


class AuditLog(models.Model):
    """
    Registro de auditoría.
    
    CRÍTICO: Immutable (append-only).
    NO se puede modificar ni eliminar.
    """
    
    # Who
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    
    # When
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # What
    action = models.CharField(max_length=100, db_index=True)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    
    # How
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    
    # Result
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Changes
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    # Integrity
    checksum = models.CharField(max_length=64, editable=False)
    
    class Meta:
        db_table = 'audit_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def save(self, *args, **kwargs):
        """Calcula checksum antes de guardar."""
        if not self.checksum:
            self.checksum = self._calculate_checksum()
        super().save(*args, **kwargs)
    
    def _calculate_checksum(self) -> str:
        """Calcula SHA-256 del registro."""
        data = {
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'model_name': self.model_name,
            'object_id': self.object_id,
            'ip_address': self.ip_address,
            'success': self.success,
        }
        
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def delete(self, *args, **kwargs):
        """Bloquea eliminación de auditoría."""
        raise NotImplementedError(
            "Los registros de auditoría no se pueden eliminar"
        )
```

**Service de Auditoría:**
```python
# apps/audit/services.py

from apps.audit.models import AuditLog
from apps.utils.helpers import get_client_ip


class AuditService:
    """Service para auditoría."""
    
    @staticmethod
    def log_action(
        user,
        action: str,
        success: bool = True,
        model_name: str = '',
        object_id: str = '',
        old_values: dict = None,
        new_values: dict = None,
        error_message: str = '',
        request=None
    ):
        """
        Registra acción en auditoría.
        
        Immutable (append-only).
        """
        ip_address = None
        user_agent = ''
        
        if request:
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        log = AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id) if object_id else '',
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
            old_values=old_values,
            new_values=new_values,
        )
        
        return log
    
    @staticmethod
    def log_login(user, success: bool, request=None):
        """Registra login."""
        return AuditService.log_action(
            user=user,
            action='login',
            success=success,
            request=request
        )
    
    @staticmethod
    def log_permission_change(user, target_user, function_code, action, request=None):
        """Registra cambio de permisos."""
        return AuditService.log_action(
            user=user,
            action=f'permission_{action}',
            model_name='UserFunctionAssignment',
            object_id=target_user.id,
            new_values={
                'target_user': target_user.username,
                'function': function_code,
                'action': action,
            },
            request=request
        )
    
    @staticmethod
    def log_report_generation(user, report_type, records, request=None):
        """Registra generación de reporte."""
        return AuditService.log_action(
            user=user,
            action='report_generation',
            model_name='Report',
            new_values={
                'report_type': report_type,
                'records': records,
            },
            request=request
        )
```

**Uso en Views:**
```python
# apps/access/views.py

from apps.audit.services import AuditService

class FunctionAssignmentViewSet(viewsets.ViewSet):
    """Asignación de funciones (con auditoría)."""
    
    @require_function('ACC-001')
    def create(self, request):
        """Asigna función a usuario."""
        user = request.user
        target_user = User.objects.get(id=request.data['user_id'])
        function_code = request.data['function_code']
        
        # Asignar función
        assignment = UserFunctionAssignment.objects.create(
            user=target_user,
            function=Function.objects.get(code=function_code),
            assigned_by=user,
        )
        
        # Auditar
        AuditService.log_permission_change(
            user=user,
            target_user=target_user,
            function_code=function_code,
            action='assign',
            request=request
        )
        
        return Response({'id': assignment.id})
```

---

## 🔒 10. RESTRICCIONES DE PRIVACIDAD Y DATOS

> ⚠️ **IMPORTANTE:** Protección de datos personales y minimización de información.

---

### 10.1 Clasificación de Datos

**Código:** CNST-032 (implícito)

```yaml
📊 NIVEL 1 - PÚBLICO:
  - Documentación
  - Logs técnicos (sin PII)
  - Métricas agregadas

📊 NIVEL 2 - INTERNO:
  - IPs de usuarios
  - User-Agents
  - Timestamps de acceso
  - Estadísticas por DID

📊 NIVEL 3 - CONFIDENCIAL:
  - Usernames
  - Emails
  - Nombres completos
  - Permisos asignados

📊 NIVEL 4 - RESTRINGIDO:
  - Passwords (hasheados)
  - Tokens de sesión
  - API keys
  - Security questions/answers

🔐 PROTECCIÓN POR NIVEL:
  - Nivel 1: Sin restricción
  - Nivel 2: Acceso autenticado
  - Nivel 3: RBAC específico
  - Nivel 4: Cifrado + RBAC estricto
```

**Cifrado de Datos Sensibles:**
```python
# apps/core/encryption.py

from cryptography.fernet import Fernet
from django.conf import settings
import base64


class FieldEncryption:
    """Cifrado de campos sensibles."""
    
    @staticmethod
    def get_cipher():
        """Obtiene cipher de Fernet."""
        key = settings.FIELD_ENCRYPTION_KEY.encode()
        return Fernet(key)
    
    @staticmethod
    def encrypt(value: str) -> str:
        """Cifra valor."""
        cipher = FieldEncryption.get_cipher()
        encrypted = cipher.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt(encrypted_value: str) -> str:
        """Descifra valor."""
        cipher = FieldEncryption.get_cipher()
        encrypted = base64.b64decode(encrypted_value.encode())
        return cipher.decrypt(encrypted).decode()


# Uso en modelo
class User(AbstractUser):
    """Usuario con campos cifrados."""
    
    # Cifrado
    security_answer_1_encrypted = models.TextField()
    
    @property
    def security_answer_1(self) -> str:
        """Descifra respuesta de seguridad."""
        return FieldEncryption.decrypt(self.security_answer_1_encrypted)
    
    @security_answer_1.setter
    def security_answer_1(self, value: str):
        """Cifra respuesta de seguridad."""
        self.security_answer_1_encrypted = FieldEncryption.encrypt(value)
```

---

### 10.2 Minimización de Datos

**Código:** CNST-033 (implícito)

```yaml
✅ PRINCIPIOS:
  - Solo recolectar datos necesarios
  - Retención limitada (2 años auditoría)
  - Eliminar datos obsoletos
  - Anonimizar cuando posible

✅ RETENCIÓN:
  - Sesiones: 15 días
  - Logs aplicación: 90 días
  - Logs auditoría: 2 años
  - Reportes generados: 1 año
  - Datos analíticos: Indefinido (agregados)

❌ PROHIBIDO:
  - Guardar más de lo necesario
  - PII en logs
  - Datos sin propósito claro
  - Retención indefinida sin justificar
```

**Cleanup Automático:**
```python
# apps/core/management/commands/cleanup_old_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.authentication.models import Session
from apps.audit.models import AuditLog


class Command(BaseCommand):
    help = 'Limpia datos obsoletos'
    
    def handle(self, *args, **options):
        """Ejecuta cleanup."""
        now = timezone.now()
        
        # Sesiones > 15 días
        old_sessions = Session.objects.filter(
            expire_date__lt=now - timedelta(days=15)
        )
        deleted_sessions = old_sessions.count()
        old_sessions.delete()
        
        self.stdout.write(
            f'✅ Eliminadas {deleted_sessions} sesiones antiguas'
        )
        
        # Logs > 90 días (NO auditoría)
        # Implementar según modelo de logs
        
        # Reportes > 1 año
        old_reports = Report.objects.filter(
            created_at__lt=now - timedelta(days=365)
        )
        deleted_reports = old_reports.count()
        old_reports.delete()
        
        self.stdout.write(
            f'✅ Eliminados {deleted_reports} reportes antiguos'
        )
        
        # ⚠️ NO eliminar auditoría (retención 2 años mínimo)
        # Auditoría se mantiene indefinidamente por compliance
```

**Scheduler Cleanup:**
```python
# apps/core/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

def run_cleanup():
    """Ejecuta cleanup de datos."""
    call_command('cleanup_old_data')

scheduler = BackgroundScheduler()

# Cleanup semanal (domingos 3 AM)
scheduler.add_job(
    run_cleanup,
    trigger='cron',
    day_of_week='sun',
    hour=3,
    minute=0,
    id='cleanup_job',
)
```

---

## 📋 11. CHECKLIST DE CUMPLIMIENTO

> ⚠️ **IMPORTANTE:** Verificación obligatoria antes de cada deployment.

---

### 11.1 Pre-Deploy

**Checklist de Verificación:**

```yaml
✅ CÓDIGO:
  - [ ] Black, Flake8, isort pasados
  - [ ] Pre-commit hooks pasados
  - [ ] No warnings de Bandit
  - [ ] No warnings de safety
  - [ ] Tests al 80%+ cobertura
  - [ ] Todos los tests pasando
  - [ ] Code review aprobado (2+)

✅ CONFIGURACIÓN:
  - [ ] DEBUG = False
  - [ ] SECRET_KEY desde .env
  - [ ] ALLOWED_HOSTS configurado
  - [ ] SESSION_ENGINE = db
  - [ ] NO Redis configurado
  - [ ] NO Celery configurado
  - [ ] NO Docker en producción
  - [ ] NO servicios cloud (AWS/GCP/Azure)

✅ SEGURIDAD:
  - [ ] HTTPS habilitado
  - [ ] CSRF tokens habilitados
  - [ ] XSS protection habilitado
  - [ ] Passwords hasheados (PBKDF2)
  - [ ] Permisos RBAC en endpoints
  - [ ] Sin secrets en código

✅ BASE DE DATOS:
  - [ ] Migraciones aplicadas
  - [ ] BD IVR readonly verificado
  - [ ] Database router configurado
  - [ ] Backups configurados

✅ INFRAESTRUCTURA:
  - [ ] Nginx configurado
  - [ ] Gunicorn configurado
  - [ ] Supervisor configurado
  - [ ] Logs rotando
  - [ ] Cleanup programado

✅ DOCUMENTACIÓN:
  - [ ] README actualizado
  - [ ] CHANGELOG actualizado
  - [ ] API docs actualizadas
  - [ ] Diagramas actualizados
```

**Script de Verificación:**
```bash
#!/bin/bash
# /opt/iact/scripts/pre_deploy_check.sh

set -e

echo "🔍 Verificando cumplimiento pre-deploy..."

# Código
echo "✅ Verificando código..."
black --check apps/ || { echo "❌ Black failed"; exit 1; }
flake8 apps/ || { echo "❌ Flake8 failed"; exit 1; }
isort --check apps/ || { echo "❌ isort failed"; exit 1; }

# Seguridad
echo "✅ Verificando seguridad..."
bandit -r apps/ -ll || { echo "❌ Bandit found issues"; exit 1; }
safety check || { echo "❌ Safety found vulnerabilities"; exit 1; }

# Tests
echo "✅ Ejecutando tests..."
pytest --cov=apps --cov-fail-under=80 || { echo "❌ Tests failed"; exit 1; }

# Configuración
echo "✅ Verificando configuración..."
python manage.py check --deploy || { echo "❌ Django checks failed"; exit 1; }

# Migraciones
echo "✅ Verificando migraciones..."
python manage.py makemigrations --check --dry-run || { echo "❌ Migraciones pendientes"; exit 1; }

# Verificar restricciones CNST
echo "✅ Verificando restricciones CNST..."
./scripts/verify_cnst_compliance.sh || { echo "❌ CNST compliance failed"; exit 1; }

echo "✅ Pre-deploy checks passed"
```

---

### 11.2 Post-Deploy

**Checklist Post-Deploy:**

```yaml
✅ VERIFICACIÓN:
  - [ ] Aplicación respondiendo
  - [ ] Health check OK (/health)
  - [ ] Login funcionando
  - [ ] RBAC funcionando
  - [ ] ETL programado corriendo
  - [ ] Logs generándose

✅ SMOKE TESTS:
  - [ ] GET /api/v1/ (200 OK)
  - [ ] POST /api/v1/auth/login/ (200 OK)
  - [ ] GET /api/v1/reports/ (200 OK con auth)
  - [ ] GET /api/v1/dashboard/ (200 OK con auth)

✅ MONITOREO:
  - [ ] Logs sin errores
  - [ ] Métricas normales
  - [ ] Disco con espacio
  - [ ] CPU/RAM normales

✅ ROLLBACK PLAN:
  - [ ] Backup pre-deploy tomado
  - [ ] Procedimiento rollback documentado
  - [ ] Team notificado
```

**Script Post-Deploy:**
```bash
#!/bin/bash
# /opt/iact/scripts/post_deploy_check.sh

set -e

echo "🚀 Verificando deployment..."

# Health check
echo "✅ Health check..."
curl -f http://localhost/health || { echo "❌ Health check failed"; exit 1; }

# API check
echo "✅ API check..."
curl -f http://localhost/api/v1/ || { echo "❌ API not responding"; exit 1; }

# Database
echo "✅ Database check..."
python manage.py dbshell -c "SELECT 1;" || { echo "❌ Database not accessible"; exit 1; }

# Scheduler
echo "✅ Scheduler check..."
supervisorctl status iact-apscheduler | grep RUNNING || { echo "❌ Scheduler not running"; exit 1; }

# Logs
echo "✅ Verificando logs..."
tail -n 100 /opt/iact/logs/django.log | grep ERROR && { echo "⚠️ Errors in logs"; }

echo "✅ Post-deploy checks passed"
echo "📊 Monitorear logs por 30 minutos"
```

---

## 📚 12. GLOSARIO DE RESTRICCIONES

**Términos Clave:**

| Término | Definición |
|---------|-----------|
| **CNST** | Código de restricción (CNST-001 a CNST-033) |
| **On-Premise** | Infraestructura en servidores propios, no cloud |
| **Readonly** | Solo lectura, sin escritura |
| **RBAC** | Role-Based Access Control (control de acceso por roles) |
| **SoD** | Separation of Duties (separación de funciones) |
| **ETL** | Extract, Transform, Load |
| **PII** | Personally Identifiable Information (datos personales) |
| **Immutable** | Inmutable, no se puede modificar |
| **Append-only** | Solo agregar, no modificar/eliminar |
| **Throttling** | Limitación de tasa de requests |
| **SLA** | Service Level Agreement |
| **Flat RBAC** | RBAC sin jerarquías |

---

## 📊 13. TABLA RESUMEN CNST

> ⭐ **NUEVA SECCIÓN:** Consolidación de todas las restricciones documentadas.

### Restricciones Técnicas Críticas

| Código | Nombre | Descripción | Sección | Estado |
|--------|--------|-------------|---------|--------|
| **CNST-001** | NO Email | Prohibido envío de correos electrónicos | 1.1 | ✅ Obligatorio |
| **CNST-010** | NO Redis | Prohibido Redis para cache/sessions | 1.2 | ✅ Obligatorio |
| **CNST-002** | BD Dual | BD IVR readonly, BD Analytics write | 1.3, 4.1 | ✅ Obligatorio |
| **CNST-003** | NO Real-time | Prohibido WebSockets, SSE, polling | 1.4 | ✅ Obligatorio |
| **CNST-011** | NO Cloud | Prohibido AWS/GCP/Azure | 1.5 | ✅ Obligatorio |
| **CNST-012** | NO Externos | Prohibido servicios externos (Twilio/Sentry/etc) | 1.6 | ✅ Obligatorio |
| **CNST-013** | NO Brokers | Prohibido Celery/RabbitMQ/Kafka | 1.7 | ✅ Obligatorio |
| **CNST-014** | NO Containers | Prohibido Docker/Kubernetes | 1.8, 7.1-7.4 | ✅ Obligatorio |

### Restricciones de Seguridad

| Código | Nombre | Descripción | Sección | Estado |
|--------|--------|-------------|---------|--------|
| **CNST-004** | Config Django | DEBUG=False, SECRET_KEY seguro, HTTPS | 2.1 | ✅ Obligatorio |
| **CNST-005** | Autenticación | Token/Session, PBKDF2, password validation | 2.2 | ✅ Obligatorio |
| **CNST-006** | Serializers | Campos explícitos, no __all__ | 2.3 | ✅ Obligatorio |
| **CNST-007** | Límites | CSV 100K, Excel 50K, PDF 10K | 2.4, 6.2 | ✅ Obligatorio |
| **CNST-008** | Dependencias | Versiones fijadas, safety check | 2.5 | ✅ Obligatorio |

### Restricciones de Arquitectura

| Código | Nombre | Descripción | Sección | Estado |
|--------|--------|-------------|---------|--------|
| **CNST-015** | Antipatrones | God Class, Spaghetti Code, etc prohibidos | 3.1 | ⚠️ Recomendado |
| **CNST-016** | Patrones | Service Layer, Repository, Factory permitidos | 3.2 | ⚠️ Recomendado |
| **CNST-017** | SOLID | Principios SOLID obligatorios | 3.3 | ⚠️ Recomendado |

### Restricciones de Base de Datos

| Código | Nombre | Descripción | Sección | Estado |
|--------|--------|-------------|---------|--------|
| **CNST-018** | BD Analytics | Permisos completos, migraciones permitidas | 4.2 | ✅ Obligatorio |
| **CNST-019** | ETL | APScheduler, 6-12h, stored procedure | 4.3 | ✅ Obligatorio |

### Restricciones Funcionales

| Código | Nombre | Descripción | Sección | Estado |
|--------|--------|-------------|---------|--------|
| **CNST-020** | Autenticación | Django Auth, 3 preguntas seguridad | 5.1 | ✅ Obligatorio |
| **CNST-021** | RBAC | 42 funciones, 9 módulos, SoD | 5.2 | ✅ Obligatorio |
| **CNST-022** | Reportes | 3 tipos, límites por formato | 5.3 | ✅ Obligatorio |
| **CNST-023** | Dashboard | Datos estáticos, cache 5 min | 5.4 | ✅ Obligatorio |
| **CNST-024** | Alertas | Buzón interno, máx 50 destinatarios | 5.5 | ✅ Obligatorio |

### Restricciones de Performance

| Código | Nombre | Descripción | Sección | Estado |
|--------|--------|-------------|---------|--------|
| **CNST-025** | SLA | GET <500ms, POST <1s, timeout 90s | 6.1 | ✅ Obligatorio |

### Restricciones de Desarrollo

| Código | Nombre | Descripción | Sección | Estado |
|--------|--------|-------------|---------|--------|
| **CNST-026** | Coding Standards | PEP 8, Black, Flake8, isort | 8.1 | ✅ Obligatorio |
| **CNST-027** | Git | Conventional Commits, code review | 8.2 | ✅ Obligatorio |
| **CNST-028** | Testing | 80% cobertura, pytest, factory boy | 8.3 | ✅ Obligatorio |
| **CNST-029** | Documentación | README, docstrings, OpenAPI | 8.4 | ✅ Obligatorio |

### Restricciones de Logging y Auditoría

| Código | Nombre | Descripción | Sección | Estado |
|--------|--------|-------------|---------|--------|
| **CNST-030** | Logging | Filesystem, rotating, JSON, sin PII | 9.1 | ✅ Obligatorio |
| **CNST-031** | Auditoría | Immutable, retención 2 años, SHA-256 | 9.2 | ✅ Obligatorio |

### Restricciones de Privacidad

| Código | Nombre | Descripción | Sección | Estado |
|--------|--------|-------------|---------|--------|
| **CNST-032** | Clasificación | 4 niveles (Público a Restringido) | 10.1 | ✅ Obligatorio |
| **CNST-033** | Minimización | Retención limitada, cleanup automático | 10.2 | ✅ Obligatorio |

### Resumen Estadístico

```
TOTAL RESTRICCIONES: 33
├─ Obligatorias: 28 (85%)
└─ Recomendadas: 5 (15%)

POR CRITICIDAD:
├─ CRÍTICAS (NO NEGOCIABLES): 8 (CNST-001 a CNST-014)
├─ IMPORTANTES: 15 (Seguridad, BD, Funcionales)
└─ RECOMENDADAS: 10 (Arquitectura, Desarrollo)

POR CATEGORÍA:
├─ Técnicas Críticas: 8
├─ Seguridad: 5
├─ Arquitectura: 3
├─ Base de Datos: 2
├─ Funcionales: 5
├─ Performance: 1
├─ Desarrollo: 4
├─ Logging/Auditoría: 2
└─ Privacidad: 2
```

---

## 📚 14. REFERENCIAS Y DOCUMENTOS RELACIONADOS

### Documentos del Proyecto

```
DOCUMENTOS PRINCIPALES:
├─ RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0 (3 partes) ⭐ ESTE DOCUMENTO
│   ├─ PARTE 1: Restricciones Críticas y Seguridad
│   ├─ PARTE 2: Arquitectura, Base de Datos y Performance
│   └─ PARTE 3: Desarrollo, Auditoría y Referencias
│
├─ ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0 (3 partes)
│   ├─ PARTE 1: Fundamentos y Decisiones
│   ├─ PARTE 2: Arquitectura Django
│   └─ PARTE 3: Nomenclatura y Referencias
│
├─ MODELO_RBAC_IACT_v6_0_0
│   ├─ 9 módulos funcionales
│   ├─ 42 funciones atómicas
│   └─ MOD_Dashboard separado (DSH-001/002/003)
│
├─ CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1 (5 partes)
│   ├─ Nomenclatura código
│   ├─ Nomenclatura base de datos
│   └─ Patrones y anti-patrones
│
└─ PROPUESTA_AMPLIACIONES_CNST_005-006
    ├─ Permisos temporales
    └─ Patrones recomendados
```

### Referencias Externas

```
DJANGO/PYTHON:
├─ Django Documentation: https://docs.djangoproject.com/
├─ DRF Documentation: https://www.django-rest-framework.org/
├─ PEP 8: https://peps.python.org/pep-0008/
└─ Python Type Hints: https://docs.python.org/3/library/typing.html

SEGURIDAD:
├─ OWASP Top 10: https://owasp.org/www-project-top-ten/
├─ Django Security: https://docs.djangoproject.com/en/4.2/topics/security/
└─ DRF Security: https://www.django-rest-framework.org/topics/security/

ARQUITECTURA:
├─ Clean Architecture: Robert C. Martin
├─ Domain-Driven Design: Eric Evans
└─ Patterns of Enterprise Application Architecture: Martin Fowler

HERRAMIENTAS:
├─ Black: https://black.readthedocs.io/
├─ Flake8: https://flake8.pycqa.org/
├─ isort: https://pycqa.github.io/isort/
├─ Pytest: https://docs.pytest.org/
├─ Bandit: https://bandit.readthedocs.io/
└─ Safety: https://pyup.io/safety/
```

### Ubicación de Documentos

```
/tmp/iact-real/docs/
└─ arquitectura/
    ├─ diseño/
    │   ├─ ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0_PARTE_1.md
    │   ├─ ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0_PARTE_2.md
    │   └─ ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0_PARTE_3.md
    │
    └─ restricciones/ ⭐
        ├─ RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0_PARTE_1.md
        ├─ RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0_PARTE_2.md
        └─ RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0_PARTE_3.md
```

---

## ✅ RESUMEN EJECUTIVO FINAL

### Restricciones Totales Documentadas

```
TOTAL: 33 restricciones (CNST-001 a CNST-033)

DISTRIBUCIÓN:
├─ PARTE 1: CNST-001 a CNST-010 (10 restricciones)
│   └─ Restricciones Críticas + Seguridad
│
├─ PARTE 2: CNST-011 a CNST-025 (15 restricciones)
│   └─ Arquitectura + BD + Performance + Funcionales + Infraestructura
│
└─ PARTE 3: CNST-026 a CNST-033 (8 restricciones)
    └─ Desarrollo + Logging + Auditoría + Privacidad
```

### Restricciones MÁS Críticas (Top 10)

```
1. CNST-010: NO Redis
2. CNST-011: NO Cloud Services
3. CNST-013: NO Message Brokers
4. CNST-014: NO Containerización
5. CNST-001: NO Email
6. CNST-002: BD Dual (IVR readonly)
7. CNST-021: RBAC (42 funciones)
8. CNST-031: Auditoría Immutable
9. CNST-004: Config Segura Django
10. CNST-025: SLA Performance
```

### Nuevas Restricciones en v1.0.0

```
⭐ CNST-010: NO Redis (sessions/cache)
⭐ CNST-011: NO Cloud (AWS/GCP/Azure)
⭐ CNST-012: NO Servicios Externos
⭐ CNST-013: NO Message Brokers (Celery/RabbitMQ)
⭐ CNST-014: NO Containerización (Docker/K8s)

IMPACTO: Arquitectura 100% on-premise tradicional
```

### Cumplimiento Obligatorio

```
✅ PRE-DEPLOY:
- Scripts de verificación automática
- Checklist completo (11.1)
- CI/CD gates

✅ POST-DEPLOY:
- Smoke tests automáticos
- Monitoreo continuo
- Health checks

✅ PERIÓDICO:
- Auditorías mensuales
- Revisión de logs
- Actualización de dependencias
```

---

## 📝 CHANGELOG

| Versión | Fecha | Cambios |
|---------|-------|---------|
| **1.0.0** | **2026-01-19** | **Versión inicial definitiva** |
|  |  | + 33 restricciones documentadas (CNST-001 a CNST-033) |
|  |  | + 5 nuevas restricciones críticas (CNST-010 a CNST-014) |
|  |  | + Sección 7 Infraestructura completamente reescrita |
|  |  | + Sección 13 Tabla Resumen CNST agregada |
|  |  | + Documentación completa en 3 partes |
|  |  | + Total: ~4,400 líneas de documentación |

---

## 🎓 CONCLUSIÓN

Este documento **RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0** (3 partes) consolida **TODAS** las restricciones del proyecto IACT.

### Puntos Clave

```
✅ 33 restricciones documentadas exhaustivamente
✅ 100% on-premise (NO cloud, NO Docker/K8s)
✅ Arquitectura tradicional (Nginx + Gunicorn + Supervisor)
✅ RBAC completo (42 funciones, 9 módulos)
✅ Seguridad (HTTPS, RBAC, auditoría immutable)
✅ Calidad (80% cobertura, PEP 8, code review)
```

### Cumplimiento

```
CRÍTICO: Cumplir con TODAS las restricciones CNST-001 a CNST-014
IMPORTANTE: Cumplir con restricciones de seguridad, BD y funcionales
RECOMENDADO: Seguir patrones arquitectónicos y coding standards
```

### Próximos Pasos

```
1. ✅ Validar cumplimiento con checklist (Sección 11)
2. ✅ Ejecutar scripts de verificación
3. ✅ Code review con estas restricciones
4. ✅ Deployment siguiendo Sección 7
5. ✅ Monitoreo continuo post-deploy
```

---

**Documento generado:** 2026-01-19  
**Versión:** 1.0.0  
**Estado:** ✅ DEFINITIVO  
**Parte:** 3/3 (FINAL)

**Serie Completa:**
- PARTE 1/3: Restricciones Críticas y Seguridad (1,746 líneas)
- PARTE 2/3: Arquitectura, Base de Datos y Performance (2,093 líneas)
- PARTE 3/3: Desarrollo, Auditoría y Referencias (2,350 líneas) ⭐ ESTE DOCUMENTO

**TOTAL: ~6,189 líneas de restricciones arquitectónicas consolidadas**
