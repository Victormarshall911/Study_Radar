from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.opportunities.models import Opportunity, OpportunityStatus, GeographyStatus
from apps.sources.models import Source, SourceRun, SourceRunStatus

class DashboardMetricsView(APIView):
    """
    Returns aggregated metrics matching Section 59 of instruction.md for the dashboard home.
    """
    def get(self, request):
        now = timezone.now()
        h24_ago = now - timedelta(hours=24)
        d7_ago = now - timedelta(days=7)

        # Base queryset of verified/eligible opportunities
        valid_opps = Opportunity.objects.exclude(status__in=[OpportunityStatus.EXCLUDED, OpportunityStatus.FAILED])

        new_24h = valid_opps.filter(published_at__gte=h24_ago).count()
        new_7d = valid_opps.filter(published_at__gte=d7_ago).count()

        us_opportunities = valid_opps.filter(geography_status__in=[GeographyStatus.US_ELIGIBLE, GeographyStatus.US_CA_ELIGIBLE]).count()
        canada_opportunities = valid_opps.filter(geography_status__in=[GeographyStatus.CA_ELIGIBLE, GeographyStatus.US_CA_ELIGIBLE]).count()

        paid_opportunities = valid_opps.filter(is_paid=True).count()
        unpaid_opportunities = valid_opps.filter(is_paid=False).count()

        sources_monitored = Source.objects.filter(is_active=True).count()
        successful_runs = SourceRun.objects.filter(status=SourceRunStatus.SUCCESS).count()
        failed_runs = SourceRun.objects.filter(status=SourceRunStatus.FAILED).count()

        total_duplicates = Opportunity.objects.filter(status=OpportunityStatus.DUPLICATE).count()
        # Also sum duplicate_count from source runs
        run_duplicates = sum(SourceRun.objects.values_list('duplicate_count', flat=True)) or 0
        duplicates_removed = max(total_duplicates, run_duplicates)

        total_discovered = Opportunity.objects.count()

        return Response({
            'new_24h': new_24h,
            'new_7d': new_7d,
            'us_opportunities': us_opportunities,
            'canada_opportunities': canada_opportunities,
            'paid_opportunities': paid_opportunities,
            'unpaid_opportunities': unpaid_opportunities,
            'sources_monitored': sources_monitored,
            'successful_source_runs': successful_runs,
            'failed_source_runs': failed_runs,
            'duplicates_removed': duplicates_removed,
            'total_discovered': total_discovered,
            'server_time': now.isoformat(),
        })
