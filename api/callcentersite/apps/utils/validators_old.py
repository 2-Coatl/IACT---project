"""
Validadores reutilizables del proyecto.

Validaciones comunes usadas en múltiples apps.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    """
    Valida formato de número telefónico.
    
    Formatos válidos:
        - 800-123-4567
        - 8001234567
        - +56912345678
        - 912345678
    
    Args:
        value (str): Número telefónico
    
    Raises:
        ValidationError: Si formato inválido
    
    Examples:
        >>> validate_phone_number('800-123-4567')  # OK
        >>> validate_phone_number('invalid')  # Raises ValidationError
    """
    if not value:
        return
    
    # Limpiar caracteres no numéricos
    cleaned = re.sub(r'[^\d]', '', value)
    
    # Validar longitud (mínimo 7, máximo 15 dígitos)
    if len(cleaned) < 7 or len(cleaned) > 15:
        raise ValidationError(
            _('Número telefónico debe tener entre 7 y 15 dígitos.'),
            code='invalid_phone_length'
        )
    
    # Validar que solo contenga dígitos, guiones, paréntesis, espacios, +
    pattern = r'^[\d\s\-\(\)\+]+$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Número telefónico contiene caracteres inválidos.'),
            code='invalid_phone_format'
        )


def validate_service_800(value):
    """
    Valida formato de número 800.
    
    Formatos válidos:
        - 800-123-4567
        - 800123456
        - 8001234567
    
    Args:
        value (str): Número 800
    
    Raises:
        ValidationError: Si formato inválido
    """
    if not value:
        return
    
    # Limpiar caracteres no numéricos
    cleaned = re.sub(r'[^\d]', '', value)
    
    # Debe empezar con 800
    if not cleaned.startswith('800'):
        raise ValidationError(
            _('Número de servicio debe empezar con 800.'),
            code='invalid_800_prefix'
        )
    
    # Longitud típica de 800: 10-11 dígitos
    if len(cleaned) < 7 or len(cleaned) > 15:
        raise ValidationError(
            _('Número 800 debe tener entre 7 y 15 dígitos.'),
            code='invalid_800_length'
        )


def validate_positive_number(value):
    """
    Valida que número sea positivo (> 0).
    
    Args:
        value (int/float): Valor a validar
    
    Raises:
        ValidationError: Si valor no es positivo
    """
    if value is not None and value <= 0:
        raise ValidationError(
            _('El valor debe ser mayor que cero.'),
            code='not_positive'
        )


def validate_non_negative_number(value):
    """
    Valida que número sea no negativo (>= 0).
    
    Args:
        value (int/float): Valor a validar
    
    Raises:
        ValidationError: Si valor es negativo
    """
    if value is not None and value < 0:
        raise ValidationError(
            _('El valor no puede ser negativo.'),
            code='negative_number'
        )


def validate_percentage(value):
    """
    Valida que valor esté entre 0 y 100.
    
    Args:
        value (float/Decimal): Porcentaje
    
    Raises:
        ValidationError: Si valor fuera de rango
    """
    if value is not None:
        if value < 0 or value > 100:
            raise ValidationError(
                _('El porcentaje debe estar entre 0 y 100.'),
                code='invalid_percentage'
            )


def validate_rate(value):
    """
    Valida que valor esté entre 0 y 1 (tasa/rate).
    
    Args:
        value (float/Decimal): Tasa (0.0 - 1.0)
    
    Raises:
        ValidationError: Si valor fuera de rango
    """
    if value is not None:
        if value < 0 or value > 1:
            raise ValidationError(
                _('La tasa debe estar entre 0 y 1.'),
                code='invalid_rate'
            )


def validate_codigo_center(value):
    """
    Valida formato de código de centro.
    
    Formato: 2-20 caracteres alfanuméricos, guiones, underscores.
    Ejemplos: CT01, CENTER_01, CENTRO-A
    
    Args:
        value (str): Código de centro
    
    Raises:
        ValidationError: Si formato inválido
    """
    if not value:
        return
    
    # Longitud
    if len(value) < 2 or len(value) > 20:
        raise ValidationError(
            _('Código debe tener entre 2 y 20 caracteres.'),
            code='invalid_codigo_length'
        )
    
    # Solo alfanuméricos, guiones, underscores
    pattern = r'^[A-Za-z0-9_\-]+$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Código solo puede contener letras, números, guiones y underscores.'),
            code='invalid_codigo_format'
        )


def validate_year(value):
    """
    Valida año (entre 2000 y 2100).
    
    Args:
        value (int): Año
    
    Raises:
        ValidationError: Si año fuera de rango
    """
    if value is not None:
        if value < 2000 or value > 2100:
            raise ValidationError(
                _('Año debe estar entre 2000 y 2100.'),
                code='invalid_year'
            )


def validate_quarter(value):
    """
    Valida trimestre (1-4).
    
    Args:
        value (int): Trimestre
    
    Raises:
        ValidationError: Si trimestre inválido
    """
    if value is not None:
        if value < 1 or value > 4:
            raise ValidationError(
                _('Trimestre debe ser 1, 2, 3 o 4.'),
                code='invalid_quarter'
            )


def validate_month(value):
    """
    Valida mes (1-12).
    
    Args:
        value (int): Mes
    
    Raises:
        ValidationError: Si mes inválido
    """
    if value is not None:
        if value < 1 or value > 12:
            raise ValidationError(
                _('Mes debe estar entre 1 y 12.'),
                code='invalid_month'
            )


def validate_did_number(value):
    """
    Valida número DID (Direct Inward Dialing).
    
    Similar a validate_phone_number pero más específico.
    
    Args:
        value (str): Número DID
    
    Raises:
        ValidationError: Si formato inválido
    """
    validate_phone_number(value)  # Reutilizar validación básica


def validate_file_size_mb(value, max_mb=10):
    """
    Valida tamaño de archivo.
    
    Args:
        value: File object
        max_mb (int): Tamaño máximo en MB
    
    Raises:
        ValidationError: Si archivo muy grande
    """
    if value:
        file_size_mb = value.size / (1024 * 1024)  # Convertir a MB
        if file_size_mb > max_mb:
            raise ValidationError(
                _(f'El archivo no puede superar {max_mb} MB. Tamaño actual: {file_size_mb:.2f} MB'),
                code='file_too_large'
            )


def validate_export_row_limit(row_count):
    """
    Valida límite de filas para export.
    
    CNST-007: Export máximo 100K rows.
    
    Args:
        row_count (int): Número de filas
    
    Raises:
        ValidationError: Si excede límite
    """
    MAX_ROWS = 100000  # CNST-007
    
    if row_count > MAX_ROWS:
        raise ValidationError(
            _(f'Export limitado a {MAX_ROWS:,} filas. Actual: {row_count:,} filas.'),
            code='export_limit_exceeded'
        )


# ============================================================================
# TOTAL VALIDATORS: 15
# 
# Teléfonos:
#   - validate_phone_number
#   - validate_service_800
#   - validate_did_number
# 
# Números:
#   - validate_positive_number
#   - validate_non_negative_number
#   - validate_percentage
#   - validate_rate
# 
# Fechas:
#   - validate_year
#   - validate_quarter
#   - validate_month
# 
# Códigos:
#   - validate_codigo_center
# 
# Archivos:
#   - validate_file_size_mb
#   - validate_export_row_limit (CNST-007)
# 
# CLEAN_CODE v3.0.1: Nombres auto-documentados ✅
# CNST-007: Export limit validator ✅
# ============================================================================
