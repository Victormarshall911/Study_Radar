import pytest
from apps.geography.services.resolver import GeographyResolver
from apps.opportunities.models import GeographyStatus
from apps.geography.models import GeographyScope

class TestMandatoryGeographyRequirements:
    """
    Mandatory test cases specified in Section 41 of instruction.md.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.resolver = GeographyResolver()

    def test_geo_1_united_states_explicit(self):
        """1. United States -> include"""
        res = self.resolver.resolve(
            title="Health Survey",
            text_content="We are seeking adults living across the United States to participate in a health study."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.US_ELIGIBLE

    def test_geo_2_canada_explicit(self):
        """2. Canada -> include"""
        res = self.resolver.resolve(
            title="Consumer Survey",
            text_content="Canadian residents wanted for online research about retail shopping."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.CA_ELIGIBLE

    def test_geo_3_arizona_state(self):
        """3. Arizona -> include"""
        res = self.resolver.resolve(
            title="Sunlight Exposure Study",
            text_content="Looking for Arizona residents to participate in a 2-week research project."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.US_ELIGIBLE
        assert any(m.state_province == 'Arizona' for m in res.matches)

    def test_geo_4_ontario_province(self):
        """4. Ontario -> include"""
        res = self.resolver.resolve(
            title="Public Transit Research",
            text_content="Open to residents of Ontario who commute by train or bus."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.CA_ELIGIBLE
        assert any(m.state_province == 'Ontario' for m in res.matches)

    def test_geo_5_phoenix_city(self):
        """5. Phoenix -> include"""
        res = self.resolver.resolve(
            title="Local Focus Group",
            text_content="Participants needed in Phoenix for in-person discussion on clean energy."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.US_ELIGIBLE
        assert any(m.city == 'Phoenix' for m in res.matches)

    def test_geo_6_toronto_city(self):
        """6. Toronto -> include"""
        res = self.resolver.resolve(
            title="Tech Usability Test",
            text_content="Participants from Toronto needed for a 45-minute mobile app usability test."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.CA_ELIGIBLE
        assert any(m.city == 'Toronto' for m in res.matches)

    def test_geo_7_multi_state_us(self):
        """7. California + Texas -> include"""
        res = self.resolver.resolve(
            title="Regional Energy Study",
            text_content="Seeking participants from Texas and California for grid resilience study."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.US_ELIGIBLE
        states = {m.state_province for m in res.matches if m.state_province}
        assert 'Texas' in states
        assert 'California' in states

    def test_geo_8_multi_province_canada(self):
        """8. Quebec + Ontario -> include"""
        res = self.resolver.resolve(
            title="Bilingual Communication Study",
            text_content="Open to people living in Quebec and Ontario."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.CA_ELIGIBLE
        provs = {m.state_province for m in res.matches if m.state_province}
        assert 'Quebec' in provs
        assert 'Ontario' in provs

    def test_geo_9_us_nationwide(self):
        """9. US nationwide -> include"""
        res = self.resolver.resolve(
            title="National Consumer Study",
            text_content="Open to adults across the United States."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.US_ELIGIBLE

    def test_geo_10_canadian_nationwide(self):
        """10. Canadian nationwide -> include"""
        res = self.resolver.resolve(
            title="Canada-wide Survey",
            text_content="Adults living anywhere in Canada are invited to participate."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.CA_ELIGIBLE

    def test_geo_11_global_study_allowing_us_ca(self):
        """11. global study explicitly allowing US/Canada -> include"""
        res = self.resolver.resolve(
            title="Global Developer Study",
            text_content="Worldwide research study. Open to participants in the United States and Canada."
        )
        assert res.is_eligible_us_or_ca is True
        assert res.geography_status == GeographyStatus.US_CA_ELIGIBLE

    def test_geo_12_uk_only(self):
        """12. UK only -> exclude"""
        res = self.resolver.resolve(
            title="NHS Healthcare Study",
            text_content="United Kingdom only. Must be registered with a GP in the UK."
        )
        assert res.is_eligible_us_or_ca is False
        assert res.geography_status == GeographyStatus.OUTSIDE_TARGET

    def test_geo_13_australia_only(self):
        """13. Australia only -> exclude"""
        res = self.resolver.resolve(
            title="Australian Climate Survey",
            text_content="Open only to Australia residents. Compensation AUD $40."
        )
        assert res.is_eligible_us_or_ca is False
        assert res.geography_status == GeographyStatus.OUTSIDE_TARGET

    def test_geo_14_us_researcher_participants_abroad(self):
        """14. US researcher but participants in Europe -> exclude"""
        res = self.resolver.resolve(
            title="Cross-Cultural Research",
            text_content="Conducted by Harvard University Department of Psychology. Eligibility: Germany only."
        )
        assert res.is_eligible_us_or_ca is False
        assert res.geography_status == GeographyStatus.OUTSIDE_TARGET

    def test_geo_15_canada_researcher_participants_worldwide_no_explicit_eligibility(self):
        """15. Canada researcher but participants worldwide -> include ONLY if US/Canada eligibility is explicit"""
        res = self.resolver.resolve(
            title="University of Toronto International Project",
            text_content="Conducted by researchers at University of Toronto. Open to participants worldwide."
        )
        # Without explicit US or Canadian participant eligibility, global is NOT assumed US/CA
        assert res.is_eligible_us_or_ca is False

    def test_geo_16_remote_without_geography(self):
        """16. 'remote' without geography -> do NOT assume eligibility"""
        res = self.resolver.resolve(
            title="Remote Usability Study",
            text_content="Join our online remote usability test from your computer. Takes 30 minutes."
        )
        assert res.is_eligible_us_or_ca is False
        assert res.geography_status == GeographyStatus.UNKNOWN

    def test_geo_17_researcher_location_us_participant_unknown(self):
        """17. researcher location is US but participant geography unknown -> do NOT assume US eligibility"""
        res = self.resolver.resolve(
            title="Lab Research Study",
            text_content="Conducted by researchers at University of Michigan. Fill out the questionnaire."
        )
        assert res.is_eligible_us_or_ca is False
        assert res.geography_status == GeographyStatus.UNKNOWN
