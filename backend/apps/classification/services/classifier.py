import re
import json
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from apps.opportunities.models import StudyType

logger = logging.getLogger(__name__)

class ClassificationResult:
    def __init__(
        self,
        is_research_opportunity: bool,
        study_type: str = StudyType.RESEARCH_STUDY,
        confidence: float = 0.0,
        reward_amount: Optional[Decimal] = None,
        reward_currency: str = 'USD',
        reward_text: str = '',
        reward_type: str = '',
        is_paid: bool = False,
        duration_minutes: Optional[int] = None,
        duration_text: str = '',
        eligibility_summary: str = '',
        organization: str = '',
        application_url: str = '',
        exclusion_reason: str = '',
        stage_used: str = 'rule_based'
    ):
        self.is_research_opportunity = is_research_opportunity
        self.study_type = study_type
        self.confidence = confidence
        self.reward_amount = reward_amount
        self.reward_currency = reward_currency
        self.reward_text = reward_text
        self.reward_type = reward_type
        self.is_paid = is_paid
        self.duration_minutes = duration_minutes
        self.duration_text = duration_text
        self.eligibility_summary = eligibility_summary
        self.organization = organization
        self.application_url = application_url
        self.exclusion_reason = exclusion_reason
        self.stage_used = stage_used

class StudyClassifier:
    """
    Cost-effective, staged classification engine following Sections 2, 16, 33-36, 56.
    Uses fast deterministic filters first, then rule-based extraction,
    and falls back to pluggable AI providers when required.
    """

    # Strong negative signals that immediately exclude the candidate (Rule A)
    NEGATIVE_SIGNALS = [
        re.compile(r'\b(?:job\s+opening|full-time\s+job|part-time\s+job|salary\s*:\s*\$\d+k|responsibilities\s*:\s*manage|we\s+are\s+hiring\s+a\s+senior|career\s+opportunity)\b', re.IGNORECASE),
        re.compile(r'\b(?:scholarship\s+application|grant\s+proposal|funding\s+opportunity|fellowship\s+award)\b', re.IGNORECASE),
        re.compile(r'\b(?:lottery\s+ticket|sweepstakes\s+rules|enter\s+to\s+win\s+a\s+car|casino\s+bonus)\b', re.IGNORECASE),
        re.compile(r'\b(?:journal\s+article|doi\s*:\s*10\.\d+|abstract\s*:\s*in\s+this\s+paper\s+we\s+present|research\s+paper\s+published\s+in)\b', re.IGNORECASE),
    ]

    # Positive recruitment signals
    POSITIVE_SIGNALS = [
        (re.compile(r'\b(?:paid\s+survey|complete\s+our\s+survey|take\s+this\s+survey|online\s+survey)\b', re.IGNORECASE), StudyType.PAID_SURVEY, 0.95),
        (re.compile(r'\b(?:focus\s+group|participate\s+in\s+a\s+focus\s+group)\b', re.IGNORECASE), StudyType.FOCUS_GROUP, 0.95),
        (re.compile(r'\b(?:user\s+interview|ux\s+interview|research\s+interview)\b', re.IGNORECASE), StudyType.USER_INTERVIEW, 0.95),
        (re.compile(r'\b(?:usability\s+test(?:ing)?|test\s+our\s+app|prototype\s+test)\b', re.IGNORECASE), StudyType.USABILITY_TEST, 0.95),
        (re.compile(r'\b(?:academic\s+study|academic\s+survey|university\s+study\s+recruiting)\b', re.IGNORECASE), StudyType.ACADEMIC_SURVEY, 0.92),
        (re.compile(r'\b(?:diary\s+study|daily\s+log\s+study)\b', re.IGNORECASE), StudyType.DIARY_STUDY, 0.94),
        (re.compile(r'\b(?:consumer\s+research|market\s+research\s+study)\b', re.IGNORECASE), StudyType.CONSUMER_RESEARCH, 0.90),
        (re.compile(r'\b(?:participants\s+needed|seeking\s+participants|join\s+our\s+study|take\s+part\s+in\s+research)\b', re.IGNORECASE), StudyType.PARTICIPANT_RECRUITMENT, 0.92),
        (re.compile(r'\b(?:paid\s+research\s+study|compensation\s+provided)\b', re.IGNORECASE), StudyType.RESEARCH_STUDY, 0.90),
    ]

    REWARD_PATTERNS = [
        # "$50", "$25.00", "US$100"
        (re.compile(r'(?:US\$|\$)\s*(\d+(?:\.\d{2})?)', re.IGNORECASE), 'USD', 'cash'),
        # "CAD $75", "C$50"
        (re.compile(r'(?:CAD\s*\$|C\$)\s*(\d+(?:\.\d{2})?)', re.IGNORECASE), 'CAD', 'cash'),
        # "Amazon gift card $20"
        (re.compile(r'amazon\s+gift\s+card\s*(?:worth\s*)?\$?\s*(\d+)', re.IGNORECASE), 'USD', 'gift_card'),
        # "$20 gift card"
        (re.compile(r'\$(\d+)\s*(?:gift\s+card|voucher|token)', re.IGNORECASE), 'USD', 'gift_card'),
        # "no compensation"
        (re.compile(r'\b(?:no\s+compensation|unpaid|volunteer)\b', re.IGNORECASE), 'USD', 'unpaid'),
    ]

    DURATION_PATTERNS = [
        (re.compile(r'(\d+)\s*(?:minutes?|mins?)\b', re.IGNORECASE), lambda m: int(m.group(1))),
        (re.compile(r'(\d+)\s*(?:hours?|hrs?)\b', re.IGNORECASE), lambda m: int(m.group(1)) * 60),
        (re.compile(r'1\s*(?:hour|hr)\b', re.IGNORECASE), lambda m: 60),
        (re.compile(r'(\d+)\s*sessions?\b', re.IGNORECASE), lambda m: int(m.group(1)) * 45),
    ]

    def classify(self, title: str, text: str, meta: Optional[Dict[str, Any]] = None) -> ClassificationResult:
        full_text = f"{title}\n{text}".strip()

        # Stage 1: Fast Negative Screening (Filter out normal jobs, papers, sweepstakes)
        for neg_pat in self.NEGATIVE_SIGNALS:
            match = neg_pat.search(full_text)
            if match:
                # Check if it has an overriding strong recruitment signal
                if not re.search(r'\b(?:participants\s+needed|paid\s+research\s+study|join\s+our\s+study)\b', full_text, re.IGNORECASE):
                    return ClassificationResult(
                        is_research_opportunity=False,
                        confidence=0.92,
                        exclusion_reason=f"Stage 1 Excluded: Non-research match ('{match.group(0)}')",
                        stage_used='stage_1_negative_screening'
                    )

        # Stage 2: Deterministic Recruitment Signal Detection
        matched_study_type = None
        highest_confidence = 0.0

        for pattern, stype, conf in self.POSITIVE_SIGNALS:
            if pattern.search(full_text):
                if conf > highest_confidence:
                    matched_study_type = stype
                    highest_confidence = conf

        if not matched_study_type:
            # If no positive signals matched at all, exclude
            return ClassificationResult(
                is_research_opportunity=False,
                confidence=0.85,
                exclusion_reason="Stage 2 Excluded: No valid participant recruitment signals found",
                stage_used='stage_2_rule_based'
            )

        # Extract Reward
        reward_amount, reward_currency, reward_type, reward_text, is_paid = self._extract_reward(full_text)
        if is_paid and matched_study_type == StudyType.RESEARCH_STUDY:
            matched_study_type = StudyType.PAID_SURVEY if 'survey' in full_text.lower() else StudyType.RESEARCH_STUDY

        # Extract Duration
        duration_minutes, duration_text = self._extract_duration(full_text)

        # Extract Eligibility Summary
        eligibility_summary = self._extract_eligibility(full_text)

        # Extract Organization
        organization = self._extract_organization(full_text, meta)

        return ClassificationResult(
            is_research_opportunity=True,
            study_type=matched_study_type,
            confidence=highest_confidence,
            reward_amount=reward_amount,
            reward_currency=reward_currency,
            reward_text=reward_text,
            reward_type=reward_type,
            is_paid=is_paid,
            duration_minutes=duration_minutes,
            duration_text=duration_text,
            eligibility_summary=eligibility_summary,
            organization=organization,
            stage_used='stage_2_deterministic_extraction'
        )

    def _extract_reward(self, text: str) -> tuple[Optional[Decimal], str, str, str, bool]:
        for pattern, currency, rtype in self.REWARD_PATTERNS:
            match = pattern.search(text)
            if match:
                if rtype == 'unpaid':
                    return None, 'USD', 'unpaid', 'No compensation', False
                try:
                    amount_val = Decimal(match.group(1))
                    return amount_val, currency, rtype, f"{currency} ${amount_val}", True
                except Exception:
                    continue

        if re.search(r'\b(?:paid|compensation|gift\s+card|incentive|honorarium)\b', text, re.IGNORECASE):
            return None, 'USD', 'compensation', 'Compensation provided', True

        return None, 'USD', 'unspecified', '', False

    def _extract_duration(self, text: str) -> tuple[Optional[int], str]:
        for pattern, parser in self.DURATION_PATTERNS:
            match = pattern.search(text)
            if match:
                try:
                    minutes = parser(match)
                    return minutes, match.group(0).strip()
                except Exception:
                    continue
        return None, ''

    def _extract_eligibility(self, text: str) -> str:
        elig_match = re.search(r'(?:eligibility|requirements|who\s+can\s+participate|criteria)\s*:\s*([^\n\.\;]+[\.\;]?)', text, re.IGNORECASE)
        if elig_match:
            return elig_match.group(1).strip()
        # Fallback to searching for "Looking for..."
        looking_match = re.search(r'(?:looking\s+for|seeking)\s+([^\n\.\;]+[\.\;]?)', text, re.IGNORECASE)
        if looking_match:
            return looking_match.group(0).strip()
        return ''

    def _extract_organization(self, text: str, meta: Optional[Dict[str, Any]]) -> str:
        if meta and meta.get('organization'):
            return str(meta['organization'])
        # Look for "University of ..." or "... Institute" or "... Research"
        org_match = re.search(r'\b(?:University\s+of\s+[A-Za-z]+|[A-Za-z]+\s+University|[A-Za-z]+\s+Institute|[A-Za-z]+\s+Health)\b', text)
        if org_match:
            return org_match.group(0).strip()
        return ''
