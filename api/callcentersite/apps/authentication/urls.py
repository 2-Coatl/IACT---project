from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.authentication.views import (
    CustomTokenObtainPairView,
    password_reset_request,
)

app_name = 'authentication'

urlpatterns = [
    # JWT Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password Reset (sin email)
    path('password-reset/', password_reset_request, name='password_reset'),
]
