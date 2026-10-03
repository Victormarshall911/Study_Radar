from django.urls import path
from .views import ManualIngestionView

urlpatterns = [
    path('', ManualIngestionView.as_view(), name='manual-ingest'),
]
