import pytest
from apps.classification.services.classifier import StudyClassifier
from apps.opportunities.models import StudyType

class TestStudyClassifier:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.classifier = StudyClassifier()

    def test_positive_paid_survey(self):
        title = "Paid Survey on Consumer Electronics"
        text = "Complete our online paid survey about smart TVs. Compensation: $25 Amazon gift card. Takes 15 minutes."
        res = self.classifier.classify(title, text)
        assert res.is_research_opportunity is True
        assert res.study_type in (StudyType.PAID_SURVEY, StudyType.RESEARCH_STUDY)
        assert res.is_paid is True
        assert res.reward_amount == 25
        assert res.duration_minutes == 15

    def test_positive_focus_group(self):
        title = "Virtual Focus Group for Mobile Developers"
        text = "Seeking participants for a 90 minutes focus group discussion. Reward: $150."
        res = self.classifier.classify(title, text)
        assert res.is_research_opportunity is True
        assert res.study_type == StudyType.FOCUS_GROUP
        assert res.is_paid is True
        assert res.duration_minutes == 90

    def test_negative_normal_job_posting(self):
        title = "Senior Python Backend Engineer"
        text = "Job opening: We are hiring a Senior Software Engineer. Responsibilities: manage team and build microservices. Salary: $150k."
        res = self.classifier.classify(title, text)
        assert res.is_research_opportunity is False
        assert "Non-research match" in res.exclusion_reason

    def test_negative_academic_paper_without_recruitment(self):
        title = "Neural Networks for Sentiment Analysis"
        text = "Journal article published in IEEE Transactions. Abstract: In this paper we present an empirical study of transformers. DOI: 10.1109/..."
        res = self.classifier.classify(title, text)
        assert res.is_research_opportunity is False
