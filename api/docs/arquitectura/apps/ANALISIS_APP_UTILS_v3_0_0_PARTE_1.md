---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Utils PARTE 1/3
categoria: arquitectura/apps
tema: apps/utils/ - Fundamentos y Helper Functions Core
autor: Claude Technical Analysis
tags: [utils, helpers, validators, formatters, clean-code]
documentos_base:
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md (5 partes) ⭐ APLICADO
estado: definitivo
parte: 1 de 3
relacionado:
  - ANALISIS_APP_UTILS_v3_0_0_PARTE_2.md
  - ANALISIS_APP_UTILS_v3_0_0_PARTE_3.md
replaces: []
---

# ANÁLISIS DE apps/utils/ v3.0.0 - PARTE 1/3
## FUNDAMENTOS Y HELPER FUNCTIONS CORE

**BASADO EN: CLEAN_CODE_NAMING_PRINCIPLES v3.0.1 (5 partes)**

---

## 1. RESUMEN EJECUTIVO

### 1.1 Información General

```yaml
App: apps/utils/
Tipo: SIMPLE (3 partes - SOLO funciones helper)
Líneas estimadas: ~1,200 líneas código
Propósito: Funciones utilitarias reutilizables
Funciones RBAC: 0 (NO tiene permisos, es helper)
Dependencias:
  - Ninguna app específica
  - Usada por TODAS las apps
Tests: 40 tests estimados
Coverage objetivo: >95%
Clean Code: v3.0.1 aplicado ✅
```

### 1.2 Responsabilidades Core

```yaml
Helper Functions:
  ✅ Validators (email, phone, RUT, etc)
  ✅ Formatters (dates, numbers, strings)
  ✅ Date utilities (quarters, ranges)
  ✅ String utilities (slugify, normalize)
  ✅ Number utilities (round, format)
  ✅ File utilities (size, extension)

Restricciones (CLEAN_CODE v3.0.1):
  ❌ NO modelos Django
  ❌ NO views
  ❌ NO serializers
  ❌ NO ViewSets
  ✅ SÍ solo funciones Python puras
  ✅ SÍ decorators
  ✅ SÍ exceptions custom
```

### 1.3 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                apps/utils/                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  SOLO FUNCIONES (NO models, NO views):             │
│                                                     │
│  validators.py:                                     │
│  ├─ validate_email()                               │
│  ├─ validate_phone_cl()                            │
│  ├─ validate_rut()                                 │
│  └─ validate_date_range()                          │
│                                                     │
│  formatters.py:                                     │
│  ├─ format_phone_cl()                              │
│  ├─ format_rut()                                   │
│  ├─ format_currency()                              │
│  └─ format_percentage()                            │
│                                                     │
│  date_utils.py:                                     │
│  ├─ get_quarter_from_date()                        │
│  ├─ get_quarter_date_range()                       │
│  ├─ format_datetime_cl()                           │
│  └─ parse_date_flexible()                          │
│                                                     │
│  string_utils.py:                                   │
│  ├─ slugify()                                      │
│  ├─ normalize_text()                               │
│  ├─ truncate()                                     │
│  └─ remove_accents()                               │
│                                                     │
│  number_utils.py:                                   │
│  ├─ round_decimal()                                │
│  ├─ format_number()                                │
│  └─ percentage()                                   │
│                                                     │
│  file_utils.py:                                     │
│  ├─ get_file_extension()                           │
│  ├─ format_file_size()                             │
│  └─ validate_file_type()                           │
│                                                     │
│  decorators.py:                                     │
│  ├─ @cache_result                                  │
│  ├─ @log_execution                                 │
│  └─ @retry_on_failure                              │
│                                                     │
│  exceptions.py:                                     │
│  ├─ ValidationError                                │
│  └─ FormattingError                                │
│                                                     │
└─────────────────────────────────────────────────────┘

USADO POR TODAS LAS APPS:
  - apps/users/ → validate_email, validate_phone_cl
  - apps/reports/ → format_currency, get_quarter_from_date
  - apps/authentication/ → validate_rut
  - apps/ivr/ → get_quarter_date_range
  - etc.
```

---

## 2. CLEAN CODE v3.0.1 APLICADO

### 2.1 Principio: Nombres que Revelan Intenciones

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 1, Sección 1
# ============================================================================

# ❌ INCORRECTO
def val_email(e):  # ❌ Nombre corto, no claro
    pass

def check(value):  # ❌ ¿Check de qué?
    pass

# ✅ CORRECTO (CLEAN_CODE v3.0.1)
def validate_email(email: str) -> bool:
    """
    Valida formato de email.
    
    Args:
        email: Email a validar (str)
    
    Returns:
        bool: True si válido
    
    Examples:
        >>> validate_email('user@example.com')
        True
        >>> validate_email('invalid')
        False
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone_cl(phone: str) -> bool:
    """
    Valida teléfono chileno.
    
    Args:
        phone: Teléfono (str)
    
    Returns:
        bool: True si válido
    
    Formats válidos:
        - +56912345678
        - 912345678
        - 221234567 (fijo Santiago)
    """
    import re
    # Móvil: 9 dígitos empezando con 9
    # Fijo: 8 dígitos (código área + número)
    pattern = r'^(\+?56)?([2-9]\d{7,8})$'
    return bool(re.match(pattern, phone))
```

### 2.2 Principio: Funciones Pequeñas

```python
# ============================================================================
# CLEAN_CODE v3.0.1 - PARTE 2, Sección 13: Funciones pequeñas
# ============================================================================

# ✅ CORRECTO - Funciones pequeñas, una responsabilidad
def validate_rut(rut: str) -> bool:
    """
    Valida RUT chileno.
    
    Args:
        rut: RUT (str) - formato: 12345678-9
    
    Returns:
        bool: True si válido
    """
    if not rut:
        return False
    
    # Limpiar
    clean_rut = _clean_rut(rut)
    
    # Validar formato
    if not _has_valid_rut_format(clean_rut):
        return False
    
    # Validar dígito verificador
    return _validate_rut_checksum(clean_rut)


def _clean_rut(rut: str) -> str:
    """Limpia RUT (helper privada)."""
    return rut.replace('.', '').replace('-', '').upper()


def _has_valid_rut_format(rut: str) -> bool:
    """Valida formato RUT (helper privada)."""
    import re
    return bool(re.match(r'^\d{7,8}[0-9K]$', rut))


def _validate_rut_checksum(rut: str) -> bool:
    """Valida dígito verificador (helper privada)."""
    body = rut[:-1]
    dv = rut[-1]
    
    calculated_dv = _calculate_rut_dv(body)
    
    return calculated_dv == dv


def _calculate_rut_dv(rut_body: str) -> str:
    """Calcula dígito verificador."""
    reversed_digits = map(int, reversed(rut_body))
    factors = [2, 3, 4, 5, 6, 7]
    
    s = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
    remainder = 11 - (s % 11)
    
    if remainder == 11:
        return '0'
    elif remainder == 10:
        return 'K'
    else:
        return str(remainder)
```

---

## 3. VALIDATORS

### 3.1 validators.py

```python
"""
Validators para apps/utils/.

CLEAN_CODE v3.0.1: Funciones auto-documentadas.
"""

import re
from datetime import datetime
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Valida formato de email.
    
    Args:
        email: Email a validar
    
    Returns:
        bool: True si válido
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone_cl(phone: str) -> bool:
    """
    Valida teléfono chileno.
    
    Acepta:
    - Móviles: 9 dígitos empezando con 9
    - Fijos: 8 dígitos (código área + número)
    - Con/sin +56
    
    Args:
        phone: Teléfono
    
    Returns:
        bool: True si válido
    """
    if not phone:
        return False
    
    # Limpiar
    clean_phone = phone.replace(' ', '').replace('-', '').replace('+', '')
    
    # Remover código país si existe
    if clean_phone.startswith('56'):
        clean_phone = clean_phone[2:]
    
    # Validar móvil (9 dígitos, empieza con 9)
    if re.match(r'^9\d{8}$', clean_phone):
        return True
    
    # Validar fijo (8 dígitos, empieza con 2-9)
    if re.match(r'^[2-9]\d{7}$', clean_phone):
        return True
    
    return False


def validate_rut(rut: str) -> bool:
    """
    Valida RUT chileno.
    
    Args:
        rut: RUT - formato: 12345678-9 o 12.345.678-9
    
    Returns:
        bool: True si válido
    """
    if not rut:
        return False
    
    # Limpiar
    clean_rut = _clean_rut(rut)
    
    # Validar formato
    if not _has_valid_rut_format(clean_rut):
        return False
    
    # Validar dígito verificador
    return _validate_rut_checksum(clean_rut)


def _clean_rut(rut: str) -> str:
    """Limpia RUT."""
    return rut.replace('.', '').replace('-', '').replace(' ', '').upper()


def _has_valid_rut_format(rut: str) -> bool:
    """Valida formato RUT."""
    return bool(re.match(r'^\d{7,8}[0-9K]$', rut))


def _validate_rut_checksum(rut: str) -> bool:
    """Valida dígito verificador RUT."""
    body = rut[:-1]
    dv = rut[-1]
    
    calculated_dv = _calculate_rut_dv(body)
    
    return calculated_dv == dv


def _calculate_rut_dv(rut_body: str) -> str:
    """Calcula dígito verificador RUT."""
    reversed_digits = map(int, reversed(rut_body))
    factors = [2, 3, 4, 5, 6, 7]
    
    s = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
    remainder = 11 - (s % 11)
    
    if remainder == 11:
        return '0'
    elif remainder == 10:
        return 'K'
    else:
        return str(remainder)


def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    max_days: Optional[int] = None
) -> bool:
    """
    Valida rango de fechas.
    
    Args:
        start_date: Fecha inicio
        end_date: Fecha fin
        max_days: Máximo de días permitidos (opcional)
    
    Returns:
        bool: True si válido
    """
    if not start_date or not end_date:
        return False
    
    # end_date debe ser >= start_date
    if end_date < start_date:
        return False
    
    # Validar max_days si se especificó
    if max_days:
        delta = (end_date - start_date).days
        if delta > max_days:
            return False
    
    return True


def validate_quarter(quarter: int) -> bool:
    """
    Valida trimestre.
    
    Args:
        quarter: Trimestre (1-4)
    
    Returns:
        bool: True si válido
    """
    return quarter in [1, 2, 3, 4]


def validate_year(year: int) -> bool:
    """
    Valida año.
    
    Args:
        year: Año (int)
    
    Returns:
        bool: True si válido (1900-2100)
    """
    return 1900 <= year <= 2100
```

---

## 4. FORMATTERS

### 4.1 formatters.py

```python
"""
Formatters para apps/utils/.

CLEAN_CODE v3.0.1: Funciones auto-documentadas.
"""


def format_phone_cl(phone: str) -> str:
    """
    Formatea teléfono chileno.
    
    Args:
        phone: Teléfono sin formato
    
    Returns:
        str: Teléfono formateado
    
    Examples:
        >>> format_phone_cl('912345678')
        '+56 9 1234 5678'
        >>> format_phone_cl('221234567')
        '+56 2 2123 4567'
    """
    if not phone:
        return ''
    
    # Limpiar
    clean = phone.replace(' ', '').replace('-', '').replace('+', '')
    
    # Remover código país si existe
    if clean.startswith('56'):
        clean = clean[2:]
    
    # Formatear móvil
    if clean.startswith('9') and len(clean) == 9:
        return f"+56 9 {clean[1:5]} {clean[5:]}"
    
    # Formatear fijo
    if len(clean) == 8 or len(clean) == 9:
        area = clean[0]
        number = clean[1:]
        return f"+56 {area} {number[:4]} {number[4:]}"
    
    return phone  # Retornar sin cambios si no coincide


def format_rut(rut: str) -> str:
    """
    Formatea RUT chileno.
    
    Args:
        rut: RUT sin formato
    
    Returns:
        str: RUT formateado
    
    Examples:
        >>> format_rut('123456789')
        '12.345.678-9'
    """
    if not rut:
        return ''
    
    # Limpiar
    clean = rut.replace('.', '').replace('-', '').upper()
    
    if len(clean) < 2:
        return rut
    
    # Separar cuerpo y DV
    body = clean[:-1]
    dv = clean[-1]
    
    # Formatear cuerpo con puntos
    formatted_body = ''
    for i, digit in enumerate(reversed(body)):
        if i > 0 and i % 3 == 0:
            formatted_body = '.' + formatted_body
        formatted_body = digit + formatted_body
    
    return f"{formatted_body}-{dv}"


def format_currency(amount: float, currency: str = 'CLP') -> str:
    """
    Formatea moneda.
    
    Args:
        amount: Monto
        currency: Moneda (CLP, USD, EUR)
    
    Returns:
        str: Monto formateado
    
    Examples:
        >>> format_currency(1234567.89, 'CLP')
        '$1.234.568'
        >>> format_currency(1234.56, 'USD')
        'US$1,234.56'
    """
    if currency == 'CLP':
        # Pesos chilenos (sin decimales)
        rounded = int(round(amount))
        formatted = f"{rounded:,}".replace(',', '.')
        return f"${formatted}"
    
    elif currency == 'USD':
        formatted = f"{amount:,.2f}"
        return f"US${formatted}"
    
    elif currency == 'EUR':
        formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"€{formatted}"
    
    else:
        return f"{amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Formatea porcentaje.
    
    Args:
        value: Valor (0.15 = 15%)
        decimals: Decimales a mostrar
    
    Returns:
        str: Porcentaje formateado
    
    Examples:
        >>> format_percentage(0.1534, 2)
        '15.34%'
        >>> format_percentage(0.5, 0)
        '50%'
    """
    percentage = value * 100
    return f"{percentage:.{decimals}f}%"


def format_file_size(bytes_size: int) -> str:
    """
    Formatea tamaño de archivo.
    
    Args:
        bytes_size: Tamaño en bytes
    
    Returns:
        str: Tamaño formateado
    
    Examples:
        >>> format_file_size(1024)
        '1.00 KB'
        >>> format_file_size(1536000)
        '1.46 MB'
    """
    if bytes_size < 1024:
        return f"{bytes_size} B"
    
    elif bytes_size < 1024 ** 2:
        kb = bytes_size / 1024
        return f"{kb:.2f} KB"
    
    elif bytes_size < 1024 ** 3:
        mb = bytes_size / (1024 ** 2)
        return f"{mb:.2f} MB"
    
    else:
        gb = bytes_size / (1024 ** 3)
        return f"{gb:.2f} GB"
```

---

## 5. EXCEPTIONS

```python
"""
Custom exceptions para utils.

CLEAN_CODE v3.0.1: Nombres descriptivos.
"""


class UtilsBaseException(Exception):
    """Base exception para utils."""
    pass


class ValidationError(UtilsBaseException):
    """Error de validación."""
    pass


class FormattingError(UtilsBaseException):
    """Error de formateo."""
    pass


class DateRangeError(UtilsBaseException):
    """Error en rango de fechas."""
    pass
```

---

## 6. RESUMEN PARTE 1

```yaml
Validators (6 funciones):
  ✅ validate_email()
  ✅ validate_phone_cl()
  ✅ validate_rut() (+ 4 helpers privadas)
  ✅ validate_date_range()
  ✅ validate_quarter()
  ✅ validate_year()

Formatters (5 funciones):
  ✅ format_phone_cl()
  ✅ format_rut()
  ✅ format_currency()
  ✅ format_percentage()
  ✅ format_file_size()

Exceptions (3):
  ✅ ValidationError
  ✅ FormattingError
  ✅ DateRangeError

Clean Code Aplicado:
  ✅ v3.0.1 PARTE 1: Nombres auto-documentados
  ✅ v3.0.1 PARTE 2: Funciones pequeñas
  ✅ v3.0.1 PARTE 3: Docstrings Google Style
  ✅ v3.0.1: Helpers privadas (_prefijo)

Restricciones:
  ✅ NO modelos Django
  ✅ NO views
  ✅ SOLO funciones Python puras

Total: ~400 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 2/3: Date Utils, String Utils y Decorators**

Contenido:
- ✅ date_utils.py (10 funciones)
- ✅ string_utils.py (8 funciones)
- ✅ number_utils.py (5 funciones)
- ✅ file_utils.py (6 funciones)
- ✅ decorators.py (3 decorators)

**Estimado:** ~500 líneas, 2 horas

---

**Fin de PARTE 1/3 - v3.0.0 con CLEAN_CODE v3.0.1 aplicado ✅**
