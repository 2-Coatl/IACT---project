"""
Django Admin para apps/users/.

NOTA: Admin completo se implementará en fases posteriores.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from apps.users.models import UserProfile, SessionHistory, UserSettings

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin para User."""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('employee_id', 'phone', 'position', 'avatar')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para UserProfile."""
    
    list_display = ['user', 'department', 'created_at']
    search_fields = ['user__username', 'department']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SessionHistory)
class SessionHistoryAdmin(admin.ModelAdmin):
    """Admin para SessionHistory."""
    
    list_display = ['user', 'ip_address', 'login_at', 'logout_at', 'is_active']
    list_filter = ['is_active', 'login_at']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['login_at', 'created_at', 'updated_at']


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """Admin para UserSettings."""
    
    list_display = ['user', 'language', 'theme', 'notifications_enabled']
    search_fields = ['user__username']
    list_filter = ['language', 'theme', 'notifications_enabled']
