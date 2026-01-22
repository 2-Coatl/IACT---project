"""
Excepciones base para IACT.

CLEAN_CODE v3.0.1: Nombres auto-documentados.
"""


class IACTBaseException(Exception):
    """
    Excepción base para IACT.
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    
    Todas las excepciones custom heredan de esta.
    
    Uso:
        raise IACTBaseException("Error general")
    """
    pass


class ValidationError(IACTBaseException):
    """
    Error de validación de datos.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    
    Se lanza cuando datos no cumplen reglas de validación.
    
    Uso:
        if not is_valid_phone(phone):
            raise ValidationError(f"Teléfono inválido: {phone}")
    """
    pass


class BusinessRuleError(IACTBaseException):
    """
    Error de regla de negocio.
    
    CLEAN_CODE v3.0.1: Nombre auto-documentado.
    
    Se lanza cuando se viola una regla de negocio.
    
    Ejemplo:
        # No se puede eliminar un centro con servicios activos
        if center.services.filter(activo=True).exists():
            raise BusinessRuleError(
                "No se puede eliminar centro con servicios activos"
            )
    """
    pass


class PermissionDeniedError(IACTBaseException):
    """
    Error de permisos insuficientes.
    
    CLEAN_CODE v3.0.1: Nombre que revela intención.
    
    Se lanza cuando usuario no tiene permisos.
    
    Uso:
        from apps.access.services import AccessService
        
        if not AccessService.user_has_function(user, 'reports.delete'):
            raise PermissionDeniedError(
                "No tiene permiso para eliminar reportes"
            )
    """
    pass


class ResourceNotFoundError(IACTBaseException):
    """
    Error de recurso no encontrado.
    
    CLEAN_CODE v3.0.1: Nombre descriptivo.
    
    Se lanza cuando recurso solicitado no existe.
    
    Uso:
        try:
            center = Center.objects.get(codigo='CT999')
        except Center.DoesNotExist:
            raise ResourceNotFoundError(
                f"Centro con código CT999 no existe"
            )
    """
    pass


class ETLError(IACTBaseException):
    """
    Error en proceso ETL.
    
    CLEAN_CODE v3.0.1: Nombre auto-documentado.
    
    Se lanza cuando falla extracción, transformación o carga.
    
    Uso:
        try:
            records = extract_from_ivr(date)
        except Exception as e:
            raise ETLError(f"Error extrayendo de IVR: {e}")
    """
    pass


# ============================================================================
# RESUMEN EXCEPTIONS
# 
# Total: 6 excepciones
# 
# Excepciones:
#   ✅ IACTBaseException (base)
#   ✅ ValidationError (validación)
#   ✅ BusinessRuleError (reglas negocio)
#   ✅ PermissionDeniedError (permisos)
#   ✅ ResourceNotFoundError (404)
#   ✅ ETLError (proceso ETL)
# 
# CLEAN_CODE v3.0.1:
#   ✅ Nombres auto-documentados
#   ✅ Docstrings Google Style
#   ✅ Ejemplos de uso
# ============================================================================
