from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Opportunity, OpportunityStatus, GeographyStatus
from .serializers import OpportunityListSerializer, OpportunityDetailSerializer

class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all().prefetch_related('geographies__geography', 'sources__source').order_by('-published_at', '-created_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'organization', 'eligibility_text', 'reward_text']
    ordering_fields = ['published_at', 'reward_amount', 'duration_minutes', 'discovered_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OpportunityDetailSerializer
        return OpportunityListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        # Country filter: US, CA
        country = params.get('country')
        if country:
            if country.upper() == 'US':
                qs = qs.filter(geography_status__in=[GeographyStatus.US_ELIGIBLE, GeographyStatus.US_CA_ELIGIBLE])
            elif country.upper() == 'CA':
                qs = qs.filter(geography_status__in=[GeographyStatus.CA_ELIGIBLE, GeographyStatus.US_CA_ELIGIBLE])

        # State / Province filter
        state = params.get('state') or params.get('province')
        if state:
            qs = qs.filter(
                Q(geographies__geography__state_province__iexact=state) |
                Q(geographies__geography__state_code__iexact=state) |
                Q(eligibility_text__icontains=state)
            ).distinct()

        # City filter
        city = params.get('city')
        if city:
            qs = qs.filter(
                Q(geographies__geography__city__iexact=city) |
                Q(eligibility_text__icontains=city)
            ).distinct()

        # Study type filter
        study_type = params.get('study_type')
        if study_type:
            qs = qs.filter(study_type=study_type)

        # Paid / Unpaid filter
        paid = params.get('paid')
        if paid is not None:
            if paid.lower() in ('true', '1'):
                qs = qs.filter(is_paid=True)
            elif paid.lower() in ('false', '0'):
                qs = qs.filter(is_paid=False)

        # Freshness / Posted within filter
        posted_within = params.get('posted_within')
        now = timezone.now()
        if posted_within == '24h':
            qs = qs.filter(published_at__gte=now - timedelta(hours=24))
        elif posted_within == '3d':
            qs = qs.filter(published_at__gte=now - timedelta(days=3))
        elif posted_within == '7d' or params.get('fresh_only', 'false').lower() in ('true', '1'):
            qs = qs.filter(published_at__gte=now - timedelta(days=7))

        # Status filter
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        elif self.action == 'list' and not params.get('include_all'):
            # Default to showing active/valid opportunities
            qs = qs.exclude(status__in=[OpportunityStatus.EXCLUDED, OpportunityStatus.FAILED])

        return qs

    @action(detail=True, methods=['post'])
    def trigger_notification(self, request, pk=None):
        """Manually trigger alert dispatch for this opportunity."""
        opportunity = self.get_object()
        from apps.notifications.services import NotificationDispatcher
        dispatcher = NotificationDispatcher()
        deliveries = dispatcher.dispatch_for_opportunity(opportunity, force=True)
        return Response({
            'message': f"Alert dispatched for opportunity: {opportunity.title}",
            'deliveries': len(deliveries),
            'has_been_notified': opportunity.has_been_notified
        })
