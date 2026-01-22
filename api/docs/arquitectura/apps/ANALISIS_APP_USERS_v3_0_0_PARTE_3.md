---
version: 3.0.0
date: 2026-01-20
project: IACT Call Center System
type: Análisis de Arquitectura - App Users PARTE 3/4
categoria: arquitectura/apps
tema: apps/users/ - API REST y Serializers
autor: Claude Technical Analysis
tags: [users, api, rest, serializers, viewsets, clean-code]
estado: definitivo
parte: 3 de 4
relacionado:
  - ANALISIS_APP_USERS_v3_0_0_PARTE_1.md
  - ANALISIS_APP_USERS_v3_0_0_PARTE_2.md
  - ANALISIS_APP_USERS_v3_0_0_PARTE_4.md
replaces: []
---

# ANÁLISIS DE apps/users/ v3.0.0 - PARTE 3/4
## API REST Y SERIALIZERS

---

## TABLA DE CONTENIDOS

1. [Resumen Parte 3](#resumen)
2. [Serializers](#serializers)
3. [ViewSets](#viewsets)
4. [URLs](#urls)

---

<a name="resumen"></a>
## 1. RESUMEN PARTE 3

```yaml
Componentes:
  ✅ Serializers DRF (8 serializers)
  ✅ ViewSets REST (4 viewsets)
  ✅ URLs configuration
  ✅ 18 endpoints REST

Líneas código: ~1,200 líneas Python
Endpoints: 18 REST endpoints
```

---

<a name="serializers"></a>
## 2. SERIALIZERS

### 2.1 Archivo: apps/users/serializers.py

```python
"""
Serializers DRF para users.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.users.models import UserProfile, UserSettings, SessionHistory

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para UserProfile."""
    
    avatar_url = serializers.CharField(source='avatar_url', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'avatar_url', 'phone_number',
            'position', 'department', 'bio',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer para UserSettings."""
    
    class Meta:
        model = UserSettings
        fields = [
            'language', 'theme', 'timezone',
            'notifications_enabled', 'email_notifications'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer principal para User.
    """
    
    profile = UserProfileSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)
    full_name = serializers.CharField(source='full_name', read_only=True)
    functions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'employee_id', 'is_active', 'is_staff',
            'date_joined', 'last_login', 'profile', 'settings',
            'functions'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'is_staff'
        ]
    
    def get_functions(self, obj):
        """Get user RBAC functions."""
        if self.context.get('include_functions'):
            return sorted(list(obj.get_functions()))
        return []


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuario."""
    
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'employee_id'
        ]
    
    def validate(self, data):
        """Validate passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Las contraseñas no coinciden'}
            )
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña."""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate passwords match."""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Las contraseñas no coinciden'}
            )
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer para solicitar reset."""
    
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer para confirmar reset."""
    
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate passwords match."""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Las contraseñas no coinciden'}
            )
        return data


class SessionHistorySerializer(serializers.ModelSerializer):
    """Serializer para SessionHistory."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    duration = serializers.CharField(source='duration', read_only=True)
    
    class Meta:
        model = SessionHistory
        fields = [
            'id', 'user', 'username', 'ip_address', 'user_agent',
            'login_at', 'logout_at', 'is_active', 'duration'
        ]
        read_only_fields = '__all__'
```

---

<a name="viewsets"></a>
## 3. VIEWSETS

### 3.1 Archivo: apps/users/views.py

```python
"""
ViewSets DRF para users.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.access.permissions import DynamicFunctionPermission
from apps.users.models import User, SessionHistory
from apps.users.serializers import (
    UserSerializer, UserCreateSerializer,
    UserProfileSerializer, UserSettingsSerializer,
    LoginSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    SessionHistorySerializer
)
from apps.users.services import (
    UserService, AuthenticationService,
    ProfileService, PasswordService
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para User.
    
    Endpoints:
    - GET    /api/v1/users/
    - POST   /api/v1/users/
    - GET    /api/v1/users/{id}/
    - PUT    /api/v1/users/{id}/
    - DELETE /api/v1/users/{id}/
    - POST   /api/v1/users/{id}/activate/
    - POST   /api/v1/users/{id}/deactivate/
    - GET    /api/v1/users/search/?q=
    
    RBAC: USR_VIEW, USR_EDIT, USR_DELETE
    """
    
    queryset = User.objects.select_related('profile', 'settings').all()
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'list': 'user.view',
        'retrieve': 'user.view',
        'create': 'user.edit',
        'update': 'user.edit',
        'partial_update': 'user.edit',
        'destroy': 'user.delete',
        'activate': 'user.edit',
        'deactivate': 'user.edit',
        'search': 'user.view',
    }
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Optimize queryset with filters."""
        queryset = super().get_queryset()
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_staff = self.request.query_params.get('is_staff')
        if is_staff is not None:
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')
        
        return queryset.order_by('username')
    
    def perform_destroy(self, instance):
        """Soft delete (is_active=False)."""
        user_service = UserService()
        user_service.delete_user(instance.id)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate user."""
        user_service = UserService()
        user = user_service.activate_user(int(pk))
        
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate user."""
        user_service = UserService()
        user = user_service.deactivate_user(int(pk))
        
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users by query."""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'error': 'Query parameter "q" required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_service = UserService()
        users = user_service.search_users(query)
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ViewSet):
    """
    ViewSet para Profile.
    
    Endpoints:
    - GET    /api/v1/users/profile/me/
    - PUT    /api/v1/users/profile/me/
    - POST   /api/v1/users/profile/me/upload-avatar/
    - DELETE /api/v1/users/profile/me/delete-avatar/
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        """Get or update current user profile."""
        profile_service = ProfileService()
        profile = profile_service.get_profile(request.user)
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            profile = profile_service.update_profile(
                request.user,
                serializer.validated_data
            )
            
            return Response(UserProfileSerializer(profile).data)
    
    @action(detail=False, methods=['post'])
    def upload_avatar(self, request):
        """Upload avatar."""
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile_service = ProfileService()
        profile = profile_service.upload_avatar(request.user, request.FILES['avatar'])
        
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def delete_avatar(self, request):
        """Delete avatar."""
        profile_service = ProfileService()
        profile = profile_service.delete_avatar(request.user)
        
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet para autenticación.
    
    Endpoints:
    - POST /api/v1/users/auth/login/
    - POST /api/v1/users/auth/logout/
    - POST /api/v1/users/auth/change-password/
    - POST /api/v1/users/auth/request-reset/
    - POST /api/v1/users/auth/confirm-reset/
    """
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login user."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        auth_service = AuthenticationService()
        user = auth_service.login_user(
            request,
            serializer.validated_data['username'],
            serializer.validated_data['password']
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout user."""
        auth_service = AuthenticationService()
        auth_service.logout_user(request)
        
        return Response({'message': 'Logout successful'})
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change password."""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        password_service = PasswordService()
        password_service.change_password(
            request.user,
            serializer.validated_data['old_password'],
            serializer.validated_data['new_password']
        )
        
        return Response({'message': 'Password changed successfully'})
    
    @action(detail=False, methods=['post'])
    def request_reset(self, request):
        """Request password reset."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        auth_service = AuthenticationService()
        auth_service.generate_password_reset_token(
            serializer.validated_data['email']
        )
        
        return Response({'message': 'Password reset email sent'})
    
    @action(detail=False, methods=['post'])
    def confirm_reset(self, request):
        """Confirm password reset."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        auth_service = AuthenticationService()
        success = auth_service.reset_password(
            serializer.validated_data['uidb64'],
            serializer.validated_data['token'],
            serializer.validated_data['new_password']
        )
        
        if success:
            return Response({'message': 'Password reset successful'})
        else:
            return Response(
                {'error': 'Invalid token or user'},
                status=status.HTTP_400_BAD_REQUEST
            )


class SessionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para SessionHistory.
    
    Endpoints:
    - GET /api/v1/users/sessions/
    - GET /api/v1/users/sessions/{id}/
    - GET /api/v1/users/sessions/my-sessions/
    
    RBAC: AUD_VIEW (auditoría)
    """
    
    queryset = SessionHistory.objects.select_related('user').all()
    serializer_class = SessionHistorySerializer
    permission_classes = [IsAuthenticated, DynamicFunctionPermission]
    
    function_map = {
        'list': 'audit.view',
        'retrieve': 'audit.view',
        'my_sessions': None,  # Siempre permitido (propias sesiones)
    }
    
    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """Get current user sessions."""
        sessions = SessionHistory.objects.filter(
            user=request.user
        ).order_by('-login_at')[:10]
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)
```

---

<a name="urls"></a>
## 4. URLS

### 4.1 Archivo: apps/users/urls.py

```python
"""
URL configuration para users.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    UserViewSet, ProfileViewSet, AuthViewSet, SessionHistoryViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'sessions', SessionHistoryViewSet, basename='session')

app_name = 'users'

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
```

### 4.2 Tabla de Endpoints

```yaml
USERS ENDPOINTS (18 total):

Users (8):
  GET    /api/v1/users/
  POST   /api/v1/users/
  GET    /api/v1/users/{id}/
  PUT    /api/v1/users/{id}/
  DELETE /api/v1/users/{id}/
  POST   /api/v1/users/{id}/activate/
  POST   /api/v1/users/{id}/deactivate/
  GET    /api/v1/users/search/?q=

Profile (4):
  GET    /api/v1/profile/me/
  PUT    /api/v1/profile/me/
  POST   /api/v1/profile/me/upload-avatar/
  DELETE /api/v1/profile/me/delete-avatar/

Auth (5):
  POST /api/v1/auth/login/
  POST /api/v1/auth/logout/
  POST /api/v1/auth/change-password/
  POST /api/v1/auth/request-reset/
  POST /api/v1/auth/confirm-reset/

Sessions (3):
  GET /api/v1/sessions/
  GET /api/v1/sessions/{id}/
  GET /api/v1/sessions/my-sessions/
```

---

## 5. RESUMEN PARTE 3

```yaml
Serializers (8):
  ✅ UserSerializer
  ✅ UserCreateSerializer
  ✅ UserProfileSerializer
  ✅ UserSettingsSerializer
  ✅ LoginSerializer
  ✅ ChangePasswordSerializer
  ✅ PasswordResetRequestSerializer
  ✅ SessionHistorySerializer

ViewSets (4):
  ✅ UserViewSet (8 endpoints)
  ✅ ProfileViewSet (4 endpoints)
  ✅ AuthViewSet (5 endpoints)
  ✅ SessionHistoryViewSet (3 endpoints)

Total: ~1,000 líneas, 18 endpoints REST
```

---

## PRÓXIMA PARTE

**PARTE 4/4: Testing y Deployment (FINAL)**

Contenido:
- ✅ Unit tests (20 tests)
- ✅ API tests (15 tests)
- ✅ Integration tests (10 tests)
- ✅ Deployment checklist

**Estimado:** ~900 líneas, 2.5 horas

---

**Fin de PARTE 3/4**
