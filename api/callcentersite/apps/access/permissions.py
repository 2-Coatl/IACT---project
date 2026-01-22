from rest_framework.permissions import BasePermission
from apps.access.models import UserFunctionAssignment


class HasFunction(BasePermission):
    """
    Permission que verifica funcion RBAC.
    
    La view debe definir el atributo: required_function
    
    Uso:
        class MyView(APIView):
            permission_classes = [HasFunction]
            required_function = 've_reportes'
            
            def get(self, request):
                # Solo usuarios con funcion 've_reportes' pueden acceder
                ...
    """
    
    def has_permission(self, request, view):
        """
        Verificar si usuario tiene la funcion requerida.
        
        Args:
            request: HttpRequest
            view: View que requiere el permiso
            
        Returns:
            bool: True si tiene permiso, False si no
        """
        # Usuario debe estar autenticado
        if not request.user.is_authenticated:
            return False
        
        # Superuser siempre tiene permiso
        if request.user.is_superuser:
            return True
        
        # Obtener funcion requerida de la view
        required_function = getattr(view, 'required_function', None)
        
        # Si no se especifica funcion, denegar
        if not required_function:
            return False
        
        # Verificar si usuario tiene la funcion
        has_func = UserFunctionAssignment.objects.filter(
            user=request.user,
            function__code=required_function,
            is_active=True,
        ).exists()
        
        return has_func
