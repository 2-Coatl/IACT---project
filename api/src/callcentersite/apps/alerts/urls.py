"""URLs para buzon interno."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InternalMessageViewSet

router = DefaultRouter()
router.register(r"messages", InternalMessageViewSet, basename="internal-message")

urlpatterns = [
    path("", include(router.urls)),
]
