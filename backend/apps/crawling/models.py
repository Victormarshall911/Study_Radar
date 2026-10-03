import uuid
from django.db import models
from apps.sources.models import Source, SourceRun

class RawDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    source_run = models.ForeignKey(SourceRun, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    url = models.CharField(max_length=1000, db_index=True)
    canonical_url = models.CharField(max_length=1000, blank=True, default='')
    content_type = models.CharField(max_length=100, default='text/html')
    http_status = models.IntegerField(default=200)
    text_content = models.TextField(blank=True, default='', help_text="Sanitized visible text content")
    raw_html_snippet = models.TextField(blank=True, default='', help_text="Sanitized snippet or structured markup, not giant blobs")
    metadata_json = models.JSONField(default=dict, blank=True, help_text="Extracted JSON-LD, OpenGraph, or meta tags")
    content_hash = models.CharField(max_length=64, db_index=True)
    fetched_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-fetched_at']
        indexes = [
            models.Index(fields=['content_hash']),
            models.Index(fields=['url']),
        ]

    def __str__(self):
        return f"RawDoc: {self.url[:60]} ({self.fetched_at.strftime('%Y-%m-%d %H:%M')})"
