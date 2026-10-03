from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GeographyViewSet

router = DefaultRouter()
router.register(r'', GeographyViewSet, basename='geography')

urlpatterns = [
    path('', include(router.urls)),
]
