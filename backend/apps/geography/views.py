from rest_framework import viewsets, filters
from .models import Geography
from .serializers import GeographySerializer

class GeographyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Geography.objects.all().order_by('country', 'state_province', 'city')
    serializer_class = GeographySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['state_province', 'state_code', 'city', 'region', 'aliases']

    def get_queryset(self):
        qs = super().get_queryset()
        country = self.request.query_params.get('country')
        scope = self.request.query_params.get('scope')
        if country:
            qs = qs.filter(country__iexact=country)
        if scope:
            qs = qs.filter(scope=scope)
        return qs
