from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SourceViewSet, SourceRunViewSet, DiscoveryQueryViewSet, CrawlFailureViewSet

router = DefaultRouter()
router.register(r'runs', SourceRunViewSet, basename='source-runs')
router.register(r'queries', DiscoveryQueryViewSet, basename='discovery-queries')
router.register(r'failures', CrawlFailureViewSet, basename='crawl-failures')
router.register(r'', SourceViewSet, basename='sources')

urlpatterns = [
    path('', include(router.urls)),
]
