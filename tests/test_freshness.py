import pytest
from datetime import datetime, timezone, timedelta
from apps.classification.services.date_extractor import DateExtractionService
from apps.opportunities.models import Opportunity, OpportunityStatus, GeographyStatus

@pytest.mark.django_db
class TestMandatoryFreshnessRequirements:
    """
    Mandatory test cases specified in Section 41 of instruction.md.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.extractor = DateExtractionService()
        self.now = datetime.now(timezone.utc)

    def test_case_1_posted_1_hour_ago(self):
        """Case 1: posted 1 hour ago -> include"""
        text = "Seeking participants for paid psychology survey. Posted 1 hour ago. Compensation: $20."
        res = self.extractor.extract_date(text_content=text, reference_time=self.now)
        assert res.published_at is not None
        assert res.confidence >= 0.70

        opp = Opportunity(
            title="Psychology Survey",
            published_at=res.published_at,
            date_confidence=res.confidence,
            participant_geo_confidence=0.95,
            geography_status=GeographyStatus.US_ELIGIBLE,
            status=OpportunityStatus.VERIFIED
        )
        assert opp.is_fresh is True
        assert opp.is_eligible_for_alert is True

    def test_case_2_posted_1_day_ago(self):
        """Case 2: posted 1 day ago -> include"""
        text = "Participants needed for user research. Posted 1 day ago."
        res = self.extractor.extract_date(text_content=text, reference_time=self.now)
        assert res.published_at is not None

        opp = Opportunity(
            title="User Research",
            published_at=res.published_at,
            date_confidence=res.confidence,
            participant_geo_confidence=0.95,
            geography_status=GeographyStatus.CA_ELIGIBLE,
            status=OpportunityStatus.VERIFIED
        )
        assert opp.is_fresh is True
        assert opp.is_eligible_for_alert is True

    def test_case_3_posted_6_days_ago(self):
        """Case 3: posted 6 days ago -> include"""
        text = "Paid study on sleep habits. Posted 6 days ago."
        res = self.extractor.extract_date(text_content=text, reference_time=self.now)
        assert res.published_at is not None

        opp = Opportunity(
            title="Sleep Habits Study",
            published_at=res.published_at,
            date_confidence=res.confidence,
            participant_geo_confidence=0.95,
            geography_status=GeographyStatus.US_ELIGIBLE,
            status=OpportunityStatus.VERIFIED
        )
        assert opp.is_fresh is True
        assert opp.is_eligible_for_alert is True

    def test_case_4_posted_exactly_7_days_ago(self):
        """Case 4: posted exactly 7 days ago -> handle boundary correctly"""
        dt_7d_ago = datetime.now(timezone.utc) - timedelta(days=7)
        opp = Opportunity(
            title="Boundary Study",
            published_at=dt_7d_ago,
            date_confidence=0.95,
            participant_geo_confidence=0.95,
            geography_status=GeographyStatus.US_ELIGIBLE,
            status=OpportunityStatus.VERIFIED
        )
        # Should be fresh on boundary
        assert opp.is_fresh is True

    def test_case_5_posted_8_days_ago(self):
        """Case 5: posted 8 days ago -> exclude"""
        text = "Academic survey on decision making. Posted 8 days ago."
        res = self.extractor.extract_date(text_content=text, reference_time=self.now)
        opp = Opportunity(
            title="Decision Making Survey",
            published_at=res.published_at,
            date_confidence=res.confidence,
            participant_geo_confidence=0.95,
            geography_status=GeographyStatus.US_ELIGIBLE,
            status=OpportunityStatus.VERIFIED
        )
        assert opp.is_fresh is False
        assert opp.is_eligible_for_alert is False

    def test_case_6_posted_30_days_ago(self):
        """Case 6: posted 30 days ago -> exclude"""
        old_date = self.now - timedelta(days=30)
        opp = Opportunity(
            title="Old Survey",
            published_at=old_date,
            date_confidence=0.95,
            participant_geo_confidence=0.95,
            geography_status=GeographyStatus.US_ELIGIBLE,
            status=OpportunityStatus.VERIFIED
        )
        assert opp.is_fresh is False
        assert opp.is_eligible_for_alert is False

    def test_case_7_unknown_publication_date(self):
        """Case 7: unknown publication date -> no alert"""
        text = "Random research study text with no timestamp or date whatsoever."
        res = self.extractor.extract_date(text_content=text, reference_time=self.now)
        assert res.published_at is None
        assert res.confidence == 0.0

        opp = Opportunity(
            title="Undated Study",
            published_at=None,
            date_confidence=0.0,
            participant_geo_confidence=0.95,
            geography_status=GeographyStatus.US_ELIGIBLE,
            status=OpportunityStatus.VERIFIED
        )
        assert opp.is_fresh is False
        assert opp.is_eligible_for_alert is False

    def test_case_8_deadline_recent_but_post_is_old(self):
        """Case 8: deadline is recent but post is old -> exclude (Section 3: do NOT use deadline)"""
        # Study posted 20 days ago with deadline in 2 days
        old_posted = self.now - timedelta(days=20)
        meta = {'article:published_time': old_posted.isoformat()}
        text = "Deadline: Closes tomorrow! Join our study."

        res = self.extractor.extract_date(text_content=text, meta_tags=meta, reference_time=self.now)
        opp = Opportunity(
            title="Old Study with Upcoming Deadline",
            published_at=res.published_at,
            date_confidence=res.confidence,
            participant_geo_confidence=0.95,
            geography_status=GeographyStatus.US_ELIGIBLE,
            status=OpportunityStatus.VERIFIED
        )
        assert opp.is_fresh is False
        assert opp.is_eligible_for_alert is False

    def test_case_9_repost_detection_preserves_original_date(self):
        """Case 9: old original study reposted recently -> detect repost and do not treat as fresh"""
        from apps.opportunities.services.deduplicator import DeduplicationService
        from apps.sources.models import Source

        source = Source.objects.create(name="Source 1", slug="src-1", base_url="https://source1.com")
        dedup = DeduplicationService()

        # Original post 25 days ago
        old_date = self.now - timedelta(days=25)
        opp, is_new, _ = dedup.record_opportunity(
            opportunity_data={
                'title': 'Original Cancer Biomarker Study',
                'source_url': 'https://source1.com/study-101',
                'content_hash': 'hash101',
                'published_at': old_date,
            },
            source=source
        )
        assert is_new is True
        assert opp.is_fresh is False

        # Another site reposts it today with new URL but same title / content
        source2 = Source.objects.create(name="Source 2", slug="src-2", base_url="https://source2.com")
        opp2, is_new2, reason = dedup.record_opportunity(
            opportunity_data={
                'title': 'Original Cancer Biomarker Study',
                'source_url': 'https://source2.com/repost-101',
                'content_hash': 'hash101',
                'published_at': self.now,
            },
            source=source2
        )
        # Sighting should be deduplicated
        assert is_new2 is False
        opp.refresh_from_db()
        assert opp.repost_detected is True
        assert opp.original_published_at == old_date

    def test_case_10_new_recruitment_round(self):
        """Case 10: new recruitment round with verified new posting -> alert if fresh"""
        opp = Opportunity(
            title="Cognitive Aging Study - Fall 2026 Cohort Round 2",
            published_at=self.now - timedelta(hours=5),
            date_confidence=0.95,
            participant_geo_confidence=0.95,
            geography_status=GeographyStatus.US_ELIGIBLE,
            status=OpportunityStatus.VERIFIED
        )
        assert opp.is_fresh is True
        assert opp.is_eligible_for_alert is True
