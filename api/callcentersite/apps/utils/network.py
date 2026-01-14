"""
Network utilities - IACT Call Center System.

Funciones para obtener informacion cliente HTTP.

CNST-002: Funciones necesarias para audit logging.
"""


def get_client_ip(request):
    """
    Obtener IP cliente desde request.
    
    Maneja proxies (X-Forwarded-For, X-Real-IP).
    
    Args:
        request: Django HttpRequest
    
    Returns:
        str: IP cliente
    
    Examples:
        >>> get_client_ip(request)
        '192.168.1.100'
    """
    # Intentar obtener de headers proxy
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Primer IP en la cadena es el cliente original
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    # Intentar X-Real-IP
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip.strip()
    
    # Fallback a REMOTE_ADDR
    remote_addr = request.META.get('REMOTE_ADDR', '')
    return remote_addr


def get_user_agent(request):
    """
    Obtener User-Agent desde request.
    
    Args:
        request: Django HttpRequest
    
    Returns:
        str: User-Agent string
    
    Examples:
        >>> get_user_agent(request)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    return user_agent


def get_request_metadata(request):
    """
    Obtener metadata completo request.
    
    Util para audit logging (CNST-002).
    
    Args:
        request: Django HttpRequest
    
    Returns:
        dict: Metadata request
    
    Examples:
        >>> get_request_metadata(request)
        {
            'ip': '192.168.1.100',
            'user_agent': 'Mozilla/5.0...',
            'method': 'GET',
            'path': '/api/v1/calls/',
        }
    """
    return {
        'ip': get_client_ip(request),
        'user_agent': get_user_agent(request),
        'method': request.method,
        'path': request.path,
        'query_string': request.META.get('QUERY_STRING', ''),
    }
