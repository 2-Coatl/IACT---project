from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import (
    UserViewSet,
    upload_avatar_view,
    delete_avatar_view,
    get_user_profile_view,
    update_user_profile_view,
)

app_name = 'users'

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Avatar management
    path('upload-avatar/', upload_avatar_view, name='upload-avatar'),
    path('delete-avatar/', delete_avatar_view, name='delete-avatar'),
    
    # Profile management
    path('profile/', get_user_profile_view, name='user-profile'),
    path('profile/update/', update_user_profile_view, name='update-profile'),
]
