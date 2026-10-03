import uuid
from django.db import models
from apps.crawling.models import RawDocument
from apps.opportunities.models import Opportunity

class AIExtraction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raw_document = models.ForeignKey(RawDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_extractions')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_extractions')
    provider = models.CharField(max_length=50, default='mock')
    model = models.CharField(max_length=100, default='gpt-4o-mini')
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    latency_ms = models.FloatField(default=0.0)
    raw_response = models.TextField(blank=True, default='')
    parsed_output = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"AIExtraction ({self.provider}/{self.model}) @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"
