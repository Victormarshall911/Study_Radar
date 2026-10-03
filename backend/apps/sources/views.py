from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Source, SourceRun, DiscoveryQuery, CrawlFailure
from .serializers import SourceSerializer, SourceRunSerializer, DiscoveryQuerySerializer, CrawlFailureSerializer

class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all().order_by('name')
    serializer_class = SourceSerializer

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        source = self.get_object()
        source.is_active = not source.is_active
        source.save(update_fields=['is_active'])
        return Response({'id': source.id, 'name': source.name, 'is_active': source.is_active})

    @action(detail=True, methods=['post'])
    def trigger_run(self, request, pk=None):
        source = self.get_object()
        from apps.tasks.tasks import crawl_single_source_task
        task = crawl_single_source_task.delay(str(source.id))
        return Response({
            'message': f"Discovery run initiated for {source.name}",
            'source_id': source.id,
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)

class SourceRunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SourceRun.objects.all().select_related('source').order_by('-started_at')
    serializer_class = SourceRunSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        source_id = self.request.query_params.get('source_id')
        status_param = self.request.query_params.get('status')
        if source_id:
            qs = qs.filter(source_id=source_id)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

class DiscoveryQueryViewSet(viewsets.ModelViewSet):
    queryset = DiscoveryQuery.objects.all().order_by('-created_at')
    serializer_class = DiscoveryQuerySerializer

class CrawlFailureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CrawlFailure.objects.all().select_related('source').order_by('-created_at')
    serializer_class = CrawlFailureSerializer
