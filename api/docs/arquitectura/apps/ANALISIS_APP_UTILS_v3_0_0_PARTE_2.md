---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Utils PARTE 2/3
categoria: arquitectura/apps
tema: apps/utils/ - Date Utils, String Utils, Number Utils y Decorators
autor: Claude Technical Analysis
tags: [utils, date-utils, string-utils, decorators]
estado: definitivo
parte: 2 de 3
relacionado:
  - ANALISIS_APP_UTILS_v3_0_0_PARTE_1.md
  - ANALISIS_APP_UTILS_v3_0_0_PARTE_3.md
replaces: []
---

# ANÁLISIS DE apps/utils/ v3.0.0 - PARTE 2/3
## DATE UTILS, STRING UTILS, NUMBER UTILS Y DECORATORS

---

## 1. DATE UTILITIES

### 1.1 date_utils.py

```python
"""
Date utilities para apps/utils/.

CLEAN_CODE v3.0.1: Funciones auto-documentadas.
"""

from datetime import datetime, date, timedelta
from typing import Tuple, Optional


def get_quarter_from_date(dt: date) -> int:
    """
    Obtiene trimestre desde fecha.
    
    Args:
        dt: Fecha
    
    Returns:
        int: Trimestre (1-4)
    
    Examples:
        >>> get_quarter_from_date(date(2025, 3, 15))
        1
        >>> get_quarter_from_date(date(2025, 7, 1))
        3
    """
    return (dt.month - 1) // 3 + 1


def get_quarter_date_range(year: int, quarter: int) -> Tuple[date, date]:
    """
    Obtiene rango de fechas de un trimestre.
    
    Args:
        year: Año
        quarter: Trimestre (1-4)
    
    Returns:
        Tuple[date, date]: (fecha_inicio, fecha_fin)
    
    Examples:
        >>> get_quarter_date_range(2025, 1)
        (date(2025, 1, 1), date(2025, 3, 31))
    """
    if quarter not in [1, 2, 3, 4]:
        raise ValueError("Quarter must be 1-4")
    
    # Mapeo trimestre → meses
    quarter_months = {
        1: (1, 3),
        2: (4, 6),
        3: (7, 9),
        4: (10, 12)
    }
    
    start_month, end_month = quarter_months[quarter]
    
    # Fecha inicio: primer día del mes inicial
    start_date = date(year, start_month, 1)
    
    # Fecha fin: último día del mes final
    if end_month == 12:
        # Diciembre → 31
        end_date = date(year, 12, 31)
    else:
        # Primer día del siguiente mes - 1 día
        next_month_first = date(year, end_month + 1, 1)
        end_date = next_month_first - timedelta(days=1)
    
    return start_date, end_date


def format_datetime_cl(dt: datetime) -> str:
    """
    Formatea datetime para Chile.
    
    Args:
        dt: Datetime
    
    Returns:
        str: Fecha formateada
    
    Examples:
        >>> format_datetime_cl(datetime(2025, 1, 15, 14, 30))
        '15/01/2025 14:30'
    """
    return dt.strftime('%d/%m/%Y %H:%M')


def format_date_cl(dt: date) -> str:
    """
    Formatea date para Chile.
    
    Args:
        dt: Date
    
    Returns:
        str: Fecha formateada
    
    Examples:
        >>> format_date_cl(date(2025, 1, 15))
        '15/01/2025'
    """
    return dt.strftime('%d/%m/%Y')


def parse_date_flexible(date_str: str) -> Optional[date]:
    """
    Parse fecha desde múltiples formatos.
    
    Args:
        date_str: Fecha como string
    
    Returns:
        date o None si inválido
    
    Examples:
        >>> parse_date_flexible('2025-01-15')
        date(2025, 1, 15)
        >>> parse_date_flexible('15/01/2025')
        date(2025, 1, 15)
    """
    if not date_str:
        return None
    
    # Formatos a intentar
    formats = [
        '%Y-%m-%d',          # ISO: 2025-01-15
        '%d/%m/%Y',          # CL: 15/01/2025
        '%d-%m-%Y',          # CL: 15-01-2025
        '%Y/%m/%d',          # US: 2025/01/15
        '%m/%d/%Y',          # US: 01/15/2025
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.date()
        except ValueError:
            continue
    
    return None


def get_days_between(start: date, end: date) -> int:
    """
    Obtiene días entre dos fechas.
    
    Args:
        start: Fecha inicio
        end: Fecha fin
    
    Returns:
        int: Días entre fechas
    """
    delta = end - start
    return delta.days


def add_business_days(start: date, days: int) -> date:
    """
    Suma días hábiles (lunes-viernes).
    
    Args:
        start: Fecha inicio
        days: Días hábiles a sumar
    
    Returns:
        date: Fecha resultante
    """
    current = start
    days_added = 0
    
    while days_added < days:
        current += timedelta(days=1)
        # weekday: 0=Monday, 6=Sunday
        if current.weekday() < 5:  # Lunes-Viernes
            days_added += 1
    
    return current


def get_month_name_es(month: int) -> str:
    """
    Obtiene nombre de mes en español.
    
    Args:
        month: Mes (1-12)
    
    Returns:
        str: Nombre del mes
    
    Examples:
        >>> get_month_name_es(1)
        'Enero'
    """
    months = [
        '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    
    if 1 <= month <= 12:
        return months[month]
    return ''


def get_quarter_name(quarter: int) -> str:
    """
    Obtiene nombre de trimestre.
    
    Args:
        quarter: Trimestre (1-4)
    
    Returns:
        str: Nombre (Q1, Q2, Q3, Q4)
    """
    return f"Q{quarter}" if 1 <= quarter <= 4 else ''
```

---

## 2. STRING UTILITIES

### 2.1 string_utils.py

```python
"""
String utilities para apps/utils/.

CLEAN_CODE v3.0.1: Funciones auto-documentadas.
"""

import re
import unicodedata


def slugify(text: str) -> str:
    """
    Convierte texto a slug.
    
    Args:
        text: Texto a convertir
    
    Returns:
        str: Slug
    
    Examples:
        >>> slugify('Hola Mundo 123')
        'hola-mundo-123'
        >>> slugify('¿Qué tal?')
        'que-tal'
    """
    # Normalizar unicode (quitar tildes)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Lowercase
    text = text.lower()
    
    # Remover caracteres no alfanuméricos
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    
    # Espacios → guiones
    text = re.sub(r'[\s]+', '-', text)
    
    # Múltiples guiones → uno solo
    text = re.sub(r'-+', '-', text)
    
    # Trim guiones
    text = text.strip('-')
    
    return text


def normalize_text(text: str) -> str:
    """
    Normaliza texto (lowercase, sin tildes, sin espacios extra).
    
    Args:
        text: Texto
    
    Returns:
        str: Texto normalizado
    """
    if not text:
        return ''
    
    # Remover tildes
    text = remove_accents(text)
    
    # Lowercase
    text = text.lower()
    
    # Espacios extra → un espacio
    text = re.sub(r'\s+', ' ', text)
    
    # Trim
    text = text.strip()
    
    return text


def remove_accents(text: str) -> str:
    """
    Remueve tildes y acentos.
    
    Args:
        text: Texto
    
    Returns:
        str: Texto sin tildes
    
    Examples:
        >>> remove_accents('José García')
        'Jose Garcia'
    """
    if not text:
        return ''
    
    # Normalizar unicode
    nfkd = unicodedata.normalize('NFKD', text)
    
    # Remover diacríticos
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])


def truncate(text: str, max_length: int, suffix: str = '...') -> str:
    """
    Trunca texto.
    
    Args:
        text: Texto
        max_length: Longitud máxima
        suffix: Sufijo (default: '...')
    
    Returns:
        str: Texto truncado
    
    Examples:
        >>> truncate('Hello World', 8)
        'Hello...'
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def capitalize_words(text: str) -> str:
    """
    Capitaliza cada palabra.
    
    Args:
        text: Texto
    
    Returns:
        str: Texto capitalizado
    
    Examples:
        >>> capitalize_words('juan pérez')
        'Juan Pérez'
    """
    if not text:
        return ''
    
    return ' '.join(word.capitalize() for word in text.split())


def remove_whitespace(text: str) -> str:
    """
    Remueve todos los espacios.
    
    Args:
        text: Texto
    
    Returns:
        str: Texto sin espacios
    """
    return re.sub(r'\s+', '', text) if text else ''


def extract_numbers(text: str) -> str:
    """
    Extrae solo números de texto.
    
    Args:
        text: Texto
    
    Returns:
        str: Solo números
    
    Examples:
        >>> extract_numbers('Phone: +56 9 1234 5678')
        '5691234567'
    """
    return re.sub(r'\D', '', text) if text else ''
```

---

## 3. NUMBER UTILITIES

### 3.1 number_utils.py

```python
"""
Number utilities para apps/utils/.

CLEAN_CODE v3.0.1: Funciones auto-documentadas.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union


def round_decimal(value: Union[float, Decimal], decimals: int = 2) -> Decimal:
    """
    Redondea decimal correctamente.
    
    Args:
        value: Valor a redondear
        decimals: Decimales
    
    Returns:
        Decimal: Valor redondeado
    
    Examples:
        >>> round_decimal(1.235, 2)
        Decimal('1.24')
    """
    if isinstance(value, float):
        value = Decimal(str(value))
    
    quantize_str = '0.' + '0' * decimals if decimals > 0 else '1'
    
    return value.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)


def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """
    Formatea número con separadores de miles.
    
    Args:
        value: Número
        decimals: Decimales a mostrar
    
    Returns:
        str: Número formateado
    
    Examples:
        >>> format_number(1234567.89, 2)
        '1.234.567,89'
    """
    if decimals > 0:
        # Con decimales
        formatted = f"{value:,.{decimals}f}"
        # Cambiar separadores: , → . y . → ,
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    else:
        # Sin decimales
        formatted = f"{int(value):,}".replace(',', '.')
    
    return formatted


def percentage(part: Union[int, float], total: Union[int, float]) -> float:
    """
    Calcula porcentaje.
    
    Args:
        part: Parte
        total: Total
    
    Returns:
        float: Porcentaje (0-100)
    
    Examples:
        >>> percentage(25, 100)
        25.0
        >>> percentage(3, 10)
        30.0
    """
    if total == 0:
        return 0.0
    
    return (part / total) * 100


def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """
    Limita valor entre mín y máx.
    
    Args:
        value: Valor
        min_val: Mínimo
        max_val: Máximo
    
    Returns:
        Valor limitado
    
    Examples:
        >>> clamp(5, 0, 10)
        5
        >>> clamp(15, 0, 10)
        10
        >>> clamp(-5, 0, 10)
        0
    """
    return max(min_val, min(value, max_val))


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
    """
    División segura (evita división por cero).
    
    Args:
        numerator: Numerador
        denominator: Denominador
        default: Valor por defecto si división por cero
    
    Returns:
        float: Resultado
    """
    if denominator == 0:
        return default
    
    return numerator / denominator
```

---

## 4. FILE UTILITIES

### 4.1 file_utils.py

```python
"""
File utilities para apps/utils/.

CLEAN_CODE v3.0.1: Funciones auto-documentadas.
"""

import os
from typing import List


def get_file_extension(filename: str) -> str:
    """
    Obtiene extensión de archivo.
    
    Args:
        filename: Nombre de archivo
    
    Returns:
        str: Extensión (sin punto)
    
    Examples:
        >>> get_file_extension('report.xlsx')
        'xlsx'
        >>> get_file_extension('document.tar.gz')
        'gz'
    """
    if not filename or '.' not in filename:
        return ''
    
    return filename.rsplit('.', 1)[1].lower()


def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Valida tipo de archivo.
    
    Args:
        filename: Nombre de archivo
        allowed_extensions: Extensiones permitidas
    
    Returns:
        bool: True si permitido
    
    Examples:
        >>> validate_file_type('report.xlsx', ['xlsx', 'csv'])
        True
        >>> validate_file_type('script.py', ['xlsx', 'csv'])
        False
    """
    extension = get_file_extension(filename)
    return extension in [ext.lower() for ext in allowed_extensions]


def format_file_size(bytes_size: int) -> str:
    """
    Formatea tamaño de archivo.
    
    Args:
        bytes_size: Tamaño en bytes
    
    Returns:
        str: Tamaño formateado
    """
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 ** 2:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 ** 3:
        return f"{bytes_size / (1024 ** 2):.2f} MB"
    else:
        return f"{bytes_size / (1024 ** 3):.2f} GB"


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nombre de archivo.
    
    Args:
        filename: Nombre de archivo
    
    Returns:
        str: Nombre sanitizado
    
    Examples:
        >>> sanitize_filename('My File: Report (2025).xlsx')
        'My_File_Report_2025.xlsx'
    """
    if not filename:
        return ''
    
    # Remover caracteres peligrosos
    safe = re.sub(r'[^\w\s.-]', '', filename)
    
    # Espacios → underscore
    safe = re.sub(r'\s+', '_', safe)
    
    # Múltiples underscores → uno solo
    safe = re.sub(r'_+', '_', safe)
    
    return safe.strip('_')
```

---

## 5. DECORATORS

### 5.1 decorators.py

```python
"""
Decorators para apps/utils/.

CLEAN_CODE v3.0.1: Decorators reutilizables.
"""

import functools
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)


def cache_result(ttl_seconds: int = 300):
    """
    Decorator para cachear resultado de función.
    
    Args:
        ttl_seconds: TTL del cache (segundos)
    
    Examples:
        @cache_result(ttl_seconds=60)
        def expensive_query():
            # ...
            pass
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Crear cache key
            cache_key = str(args) + str(kwargs)
            
            # Check cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    return result
            
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Guardar en cache
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator


def log_execution(func: Callable) -> Callable:
    """
    Decorator para loggear ejecución.
    
    Examples:
        @log_execution
        def process_data():
            # ...
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"[START] {func.__name__}")
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"[END] {func.__name__} - {elapsed:.2f}s")
            return result
        
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[ERROR] {func.__name__} - {elapsed:.2f}s - {e}")
            raise
    
    return wrapper


def retry_on_failure(max_retries: int = 3, delay_seconds: float = 1.0):
    """
    Decorator para reintentar en caso de fallo.
    
    Args:
        max_retries: Máximo de reintentos
        delay_seconds: Delay entre reintentos
    
    Examples:
        @retry_on_failure(max_retries=3, delay_seconds=2.0)
        def unstable_api_call():
            # ...
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"[RETRY] {func.__name__} - Attempt {attempt + 1}/{max_retries} failed: {e}"
                    )
                    
                    if attempt < max_retries - 1:
                        time.sleep(delay_seconds)
            
            # Todos los intentos fallaron
            logger.error(f"[FAILED] {func.__name__} - All {max_retries} attempts failed")
            raise last_exception
        
        return wrapper
    return decorator
```

---

## 6. RESUMEN PARTE 2

```yaml
Date Utils (10 funciones):
  ✅ get_quarter_from_date()
  ✅ get_quarter_date_range()
  ✅ format_datetime_cl()
  ✅ format_date_cl()
  ✅ parse_date_flexible()
  ✅ get_days_between()
  ✅ add_business_days()
  ✅ get_month_name_es()
  ✅ get_quarter_name()

String Utils (8 funciones):
  ✅ slugify()
  ✅ normalize_text()
  ✅ remove_accents()
  ✅ truncate()
  ✅ capitalize_words()
  ✅ remove_whitespace()
  ✅ extract_numbers()

Number Utils (5 funciones):
  ✅ round_decimal()
  ✅ format_number()
  ✅ percentage()
  ✅ clamp()
  ✅ safe_divide()

File Utils (4 funciones):
  ✅ get_file_extension()
  ✅ validate_file_type()
  ✅ format_file_size()
  ✅ sanitize_filename()

Decorators (3):
  ✅ @cache_result
  ✅ @log_execution
  ✅ @retry_on_failure

Total: ~500 líneas Python
```

---

## PRÓXIMA PARTE

**PARTE 3/3: Testing y Resumen Final**

Contenido:
- ✅ Tests (40 tests)
  - test_validators.py
  - test_formatters.py
  - test_date_utils.py
  - test_string_utils.py
  - test_number_utils.py
- ✅ Usage examples en otras apps
- ✅ Resumen ejecutivo final

**Estimado:** ~300 líneas

---

**Fin de PARTE 2/3**
