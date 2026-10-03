import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from apps.opportunities.models import Opportunity, OpportunityStatus, GeographyStatus
from apps.sources.models import Source

@pytest.mark.django_db
class TestStudyRadarAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.source = Source.objects.create(name="Public Lab Feed", slug="lab-feed", base_url="https://lab.org")

    def test_health_check_endpoint(self):
        response = self.client.get('/api/health/')
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'

    def test_dashboard_stats_endpoint(self):
        # Create fresh study
        Opportunity.objects.create(
            title="Fresh US Study",
            source_url="https://lab.org/1",
            published_at=timezone.now() - timedelta(hours=2),
            geography_status=GeographyStatus.US_ELIGIBLE,
            is_paid=True,
            status=OpportunityStatus.ELIGIBLE
        )
        response = self.client.get('/api/stats/')
        assert response.status_code == 200
        data = response.json()
        assert data['new_24h'] >= 1
        assert data['new_7d'] >= 1
        assert data['us_opportunities'] >= 1
        assert data['paid_opportunities'] >= 1

    def test_opportunities_list_and_filters(self):
        Opportunity.objects.create(
            title="Toronto Mobile UX Test",
            source_url="https://lab.org/ca-1",
            published_at=timezone.now() - timedelta(days=1),
            geography_status=GeographyStatus.CA_ELIGIBLE,
            is_paid=True,
            status=OpportunityStatus.ELIGIBLE
        )
        Opportunity.objects.create(
            title="Phoenix Sleep Research",
            source_url="https://lab.org/us-1",
            published_at=timezone.now() - timedelta(days=2),
            geography_status=GeographyStatus.US_ELIGIBLE,
            is_paid=False,
            status=OpportunityStatus.ELIGIBLE
        )

        # Filter by Canada
        res_ca = self.client.get('/api/opportunities/?country=CA')
        assert res_ca.status_code == 200
        results_ca = res_ca.json()['results']
        assert len(results_ca) >= 1
        assert all(r['geography_status'] in ('ca_eligible', 'us_ca_eligible') for r in results_ca)

        # Filter by US
        res_us = self.client.get('/api/opportunities/?country=US')
        assert res_us.status_code == 200
        results_us = res_us.json()['results']
        assert len(results_us) >= 1
        assert all(r['geography_status'] in ('us_eligible', 'us_ca_eligible') for r in results_us)

        # Filter by paid
        res_paid = self.client.get('/api/opportunities/?paid=true')
        assert res_paid.status_code == 200
        assert all(r['is_paid'] is True for r in res_paid.json()['results'])

    def test_notification_test_endpoint(self):
        payload = {'channel': 'local_log'}
        response = self.client.post('/api/notifications/test/', payload, format='json')
        assert response.status_code == 200
        assert response.json()['status'] == 'test_dispatched'
