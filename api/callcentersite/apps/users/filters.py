"""
Filtros para apps/users/.

Django-filter filtros para UserViewSet.
"""

import django_filters
from apps.users.models import User


class UserFilter(django_filters.FilterSet):
    """
    Filtros para User.
    
    Filtros disponibles:
    - username (icontains)
    - email (icontains)
    - is_active (exact)
    - is_staff (exact)
    - date_joined (gte, lte)
    """
    
    username = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = User
        fields = {
            'is_active': ['exact'],
            'is_staff': ['exact'],
            'date_joined': ['gte', 'lte'],
        }
