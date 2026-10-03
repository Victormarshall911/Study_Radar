"""
Root URL configuration for Study Radar.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

@api_view(['GET'])
def health_check(request):
    """System health check endpoint."""
    return Response({
        'status': 'healthy',
        'service': 'studyradar-backend',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/opportunities/', include('apps.opportunities.urls')),
    path('api/sources/', include('apps.sources.urls')),
    path('api/geographies/', include('apps.geography.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/stats/', include('apps.analytics.urls')),
    path('api/ingest/', include('apps.crawling.urls')),
]
