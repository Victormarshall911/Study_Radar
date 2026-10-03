import uuid
from django.db import models

class SourceType(models.TextChoices):
    RSS = 'rss', 'RSS / Atom Feed'
    API = 'api', 'Public / Official API'
    WEBSITE = 'website', 'Permitted Website'
    UNIVERSITY = 'university', 'University Research Directory'
    RESEARCH_PLATFORM = 'research_platform', 'Public Research Board'
    CUSTOM = 'custom', 'Custom Connector'

class SourceStatus(models.TextChoices):
    IDLE = 'idle', 'Idle'
    RUNNING = 'running', 'Running'
    FAILING = 'failing', 'Failing'
    DISABLED = 'disabled', 'Disabled'

class Source(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    source_type = models.CharField(max_length=30, choices=SourceType.choices, default=SourceType.RSS)
    base_url = models.URLField(max_length=500)
    feed_or_api_url = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    crawl_interval_seconds = models.IntegerField(default=3600, help_text="Interval in seconds between discovery runs")
    rate_limit_rps = models.FloatField(default=1.0, help_text="Max requests per second")
    compliance_notes = models.TextField(blank=True, default="Respects public robots.txt, public API terms, and reasonable request delays.")
    last_run_at = models.DateTimeField(blank=True, null=True)
    last_success_at = models.DateTimeField(blank=True, null=True)
    failure_count = models.IntegerField(default=0)
    avg_response_time_ms = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=SourceStatus.choices, default=SourceStatus.IDLE)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.source_type})"

class SourceRunStatus(models.TextChoices):
    RUNNING = 'running', 'Running'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'
    PARTIAL = 'partial', 'Partial'

class SourceRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='runs')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=SourceRunStatus.choices, default=SourceRunStatus.RUNNING, db_index=True)
    items_fetched = models.IntegerField(default=0)
    items_parsed = models.IntegerField(default=0)
    items_rejected = models.IntegerField(default=0)
    items_accepted = models.IntegerField(default=0)
    duplicate_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, default='')
    response_time_ms = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.source.name} run @ {self.started_at.strftime('%Y-%m-%d %H:%M')} [{self.status}]"

class DiscoveryQuery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query_text = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100, blank=True, default='general')
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query_text

class CrawlFailure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True, related_name='failures')
    source_run = models.ForeignKey(SourceRun, on_delete=models.SET_NULL, null=True, blank=True, related_name='failures')
    url = models.CharField(max_length=1000)
    status_code = models.IntegerField(blank=True, null=True)
    failure_reason = models.CharField(max_length=255)
    stack_trace = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Failure on {self.url[:50]} ({self.failure_reason})"
