from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from apps.users.serializers import UserSerializer, UserCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestion usuarios.
    
    CRUD completo:
    - list: Listar usuarios
    - create: Crear usuario
    - retrieve: Detalle usuario
    - update: Actualizar usuario
    - destroy: Eliminar usuario
    
    CNST-005: Permisos IsAuthenticated.
    """
    
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Seleccionar serializer segun accion.
        
        - create: UserCreateSerializer (con password)
        - otros: UserSerializer (sin password)
        
        Returns:
            Serializer class
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
