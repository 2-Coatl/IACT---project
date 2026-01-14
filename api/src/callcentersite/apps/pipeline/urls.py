"""URLs para ETL."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ETLJobViewSet, ETLValidationErrorViewSet

router = DefaultRouter()
router.register(r"jobs", ETLJobViewSet, basename="etl-job")
router.register(r"errors", ETLValidationErrorViewSet, basename="etl-validation-error")

urlpatterns = [
    path("", include(router.urls)),
]
