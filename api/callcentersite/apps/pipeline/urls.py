from django.urls import path
from apps.pipeline.views import etl_status

app_name = 'pipeline'

urlpatterns = [
    path('status/', etl_status, name='etl_status'),
]
