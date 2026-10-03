import pytest
from apps.opportunities.services.deduplicator import DeduplicationService
from apps.sources.models import Source
from apps.opportunities.models import Opportunity

@pytest.mark.django_db
class TestDeduplicationService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.dedup = DeduplicationService()
        self.source1 = Source.objects.create(name="Reddit Paid Studies", slug="reddit-src", base_url="https://reddit.com")
        self.source2 = Source.objects.create(name="University Portal", slug="univ-src", base_url="https://univ.edu")

    def test_url_normalization(self):
        url1 = "https://example.com/study?utm_source=twitter&utm_medium=social&id=123"
        url2 = "HTTPS://example.com/study/?id=123&utm_campaign=spring"
        assert self.dedup.normalize_url(url1) == self.dedup.normalize_url(url2)

    def test_multi_source_deduplication(self):
        # First discovery
        opp1, is_new1, _ = self.dedup.record_opportunity(
            opportunity_data={
                'title': 'Autonomous Vehicle User Study',
                'source_url': 'https://reddit.com/r/PaidStudies/comments/12345',
                'canonical_url': 'https://research-lab.org/study-av',
                'content_hash': 'av_study_hash_1',
            },
            source=self.source1
        )
        assert is_new1 is True

        # Second discovery from another source with same canonical URL
        opp2, is_new2, reason = self.dedup.record_opportunity(
            opportunity_data={
                'title': 'Autonomous Vehicle User Study',
                'source_url': 'https://univ.edu/board/post/999',
                'canonical_url': 'https://research-lab.org/study-av?utm_source=univ',
                'content_hash': 'different_hash_on_different_page',
            },
            source=self.source2
        )
        assert is_new2 is False
        assert opp1.id == opp2.id
        assert opp1.sources.count() == 2
        assert "canonical_url_match" in reason

    def test_title_and_organization_deduplication(self):
        opp1, is_new1, _ = self.dedup.record_opportunity(
            opportunity_data={
                'title': 'Longitudinal Sleep Study for College Students',
                'source_url': 'https://source-a.com/page1',
                'organization': 'Stanford University',
                'content_hash': 'hash_aaa',
            },
            source=self.source1
        )
        assert is_new1 is True

        opp2, is_new2, reason = self.dedup.record_opportunity(
            opportunity_data={
                'title': 'Longitudinal Sleep Study for College Students!',
                'source_url': 'https://source-b.com/page2',
                'organization': 'Stanford University',
                'content_hash': 'hash_bbb',
            },
            source=self.source2
        )
        assert is_new2 is False
        assert opp1.id == opp2.id
