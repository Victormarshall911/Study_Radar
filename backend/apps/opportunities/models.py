import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.sources.models import Source
from apps.geography.models import Geography, GeographyScope
from apps.crawling.models import RawDocument

class OpportunityStatus(models.TextChoices):
    DISCOVERED = 'discovered', 'Discovered'
    PROCESSING = 'processing', 'Processing'
    VERIFIED = 'verified', 'Verified'
    ELIGIBLE = 'eligible', 'Eligible'
    EXCLUDED = 'excluded', 'Excluded'
    DUPLICATE = 'duplicate', 'Duplicate'
    UNCERTAIN = 'uncertain', 'Uncertain'
    EXPIRED = 'expired', 'Expired'
    FAILED = 'failed', 'Failed'

class StudyType(models.TextChoices):
    PAID_SURVEY = 'paid_survey', 'Paid Survey'
    UNPAID_SURVEY = 'unpaid_survey', 'Unpaid Survey'
    ACADEMIC_SURVEY = 'academic_survey', 'Academic Survey'
    MARKET_RESEARCH = 'market_research', 'Market Research'
    CONSUMER_RESEARCH = 'consumer_research', 'Consumer Research'
    RESEARCH_STUDY = 'research_study', 'Research Study'
    PARTICIPANT_RECRUITMENT = 'participant_recruitment', 'Participant Recruitment'
    FOCUS_GROUP = 'focus_group', 'Focus Group'
    USER_INTERVIEW = 'user_interview', 'User Interview'
    UX_RESEARCH = 'ux_research', 'UX Research'
    USABILITY_TEST = 'usability_test', 'Usability Test'
    PRODUCT_RESEARCH = 'product_research', 'Product Research'
    DIARY_STUDY = 'diary_study', 'Diary Study'
    REMOTE_STUDY = 'remote_study', 'Remote Study'
    IN_PERSON_STUDY = 'in_person_study', 'In-Person Study'
    OTHER = 'other', 'Other Research Study'

class DatePrecision(models.TextChoices):
    EXACT_DATETIME = 'exact_datetime', 'Exact Datetime'
    EXACT_DATE = 'exact_date', 'Exact Date'
    RELATIVE_DATETIME = 'relative_datetime', 'Relative Datetime'
    RELATIVE_DATE = 'relative_date', 'Relative Date'
    APPROXIMATE = 'approximate', 'Approximate'
    UNKNOWN = 'unknown', 'Unknown'

class GeographyStatus(models.TextChoices):
    US_ELIGIBLE = 'us_eligible', 'United States'
    CA_ELIGIBLE = 'ca_eligible', 'Canada'
    US_CA_ELIGIBLE = 'us_ca_eligible', 'US and Canada'
    OUTSIDE_TARGET = 'outside_target', 'Outside US/Canada'
    UNKNOWN = 'unknown', 'Unknown Geography'

class Opportunity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    normalized_title = models.CharField(max_length=500, db_index=True)
    description = models.TextField(blank=True, default='')
    study_type = models.CharField(max_length=40, choices=StudyType.choices, default=StudyType.RESEARCH_STUDY, db_index=True)

    source_url = models.CharField(max_length=1000)
    canonical_url = models.CharField(max_length=1000, blank=True, default='', db_index=True)
    application_url = models.CharField(max_length=1000, blank=True, default='')
    organization = models.CharField(max_length=255, blank=True, default='', db_index=True)
    researcher_location = models.CharField(max_length=255, blank=True, default='', help_text="Location of researcher/org, separated from participant eligibility")

    # Publication Date
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    published_at_timezone = models.CharField(max_length=50, blank=True, default='UTC')
    published_date_precision = models.CharField(max_length=30, choices=DatePrecision.choices, default=DatePrecision.UNKNOWN)
    date_source = models.CharField(max_length=100, blank=True, default='unknown')
    date_confidence = models.FloatField(default=0.0)
    original_published_at = models.DateTimeField(null=True, blank=True)
    repost_detected = models.BooleanField(default=False)

    discovered_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    # Reward & Duration
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reward_currency = models.CharField(max_length=10, default='USD')
    reward_text = models.CharField(max_length=255, blank=True, default='')
    reward_type = models.CharField(max_length=50, blank=True, default='')
    is_paid = models.BooleanField(default=False, db_index=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    duration_text = models.CharField(max_length=100, blank=True, default='')

    # Eligibility & Geography
    eligibility_text = models.TextField(blank=True, default='')
    geography_status = models.CharField(max_length=30, choices=GeographyStatus.choices, default=GeographyStatus.UNKNOWN, db_index=True)
    participant_geo_confidence = models.FloatField(default=0.0)

    # Status & Deduplication
    status = models.CharField(max_length=30, choices=OpportunityStatus.choices, default=OpportunityStatus.DISCOVERED, db_index=True)
    exclusion_reason = models.CharField(max_length=255, blank=True, default='')
    content_hash = models.CharField(max_length=64, db_index=True)
    canonical_opportunity = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='duplicates')

    # Notification tracking
    has_been_notified = models.BooleanField(default=False, db_index=True)
    notification_count = models.IntegerField(default=0)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    notified_channels = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name_plural = 'Opportunities'
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['geography_status', 'is_paid']),
            models.Index(fields=['has_been_notified', 'status']),
            models.Index(fields=['content_hash']),
        ]

    def __str__(self):
        return f"{self.title[:60]} [{self.get_geography_status_display()}]"

    @property
    def is_fresh(self) -> bool:
        """Determines if the publication date is strictly within the 7-day window."""
        if not self.published_at:
            return False
        # Allow 60-second clock skew buffer for exact 7-day boundary evaluations
        cutoff = timezone.now() - timedelta(days=settings.FRESHNESS_WINDOW_DAYS, seconds=60)
        return self.published_at >= cutoff

    @property
    def is_eligible_for_alert(self) -> bool:
        """Central rule evaluator for alerting."""
        if self.has_been_notified:
            return False
        if self.status not in (OpportunityStatus.VERIFIED, OpportunityStatus.ELIGIBLE):
            return False
        if not self.is_fresh:
            return False
        if self.geography_status not in (GeographyStatus.US_ELIGIBLE, GeographyStatus.CA_ELIGIBLE, GeographyStatus.US_CA_ELIGIBLE):
            return False
        if self.date_confidence < settings.CONFIDENCE_THRESHOLD_DATE:
            return False
        if self.participant_geo_confidence < settings.CONFIDENCE_THRESHOLD_GEO:
            return False
        return True

class OpportunitySource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='sources')
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='opportunity_sources')
    source_url = models.CharField(max_length=1000)
    raw_document = models.ForeignKey(RawDocument, on_delete=models.SET_NULL, null=True, blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('opportunity', 'source_url')

    def __str__(self):
        return f"{self.source.name} -> {self.opportunity.title[:40]}"

class OpportunityGeography(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='geographies')
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE, related_name='opportunity_geographies')
    scope = models.CharField(max_length=30, choices=GeographyScope.choices, default=GeographyScope.UNKNOWN)
    is_explicit = models.BooleanField(default=True)
    confidence = models.FloatField(default=1.0)

    class Meta:
        verbose_name_plural = 'Opportunity Geographies'

    def __str__(self):
        return f"{self.opportunity.title[:30]} in {self.geography}"
