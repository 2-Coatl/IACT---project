"""
Custom permissions para access app.
"""
from .module_permissions import (
    HasModuleAccess,
    HasAnyModuleAccess,
    HasAllModuleAccess,
)

__all__ = [
    'HasModuleAccess',
    'HasAnyModuleAccess',
    'HasAllModuleAccess',
]
