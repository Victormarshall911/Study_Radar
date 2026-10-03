import uuid
from django.db import models
from apps.opportunities.models import Opportunity

class DeliveryChannel(models.TextChoices):
    TELEGRAM = 'telegram', 'Telegram'
    EMAIL = 'email', 'Email'
    LOCAL_LOG = 'local_log', 'Local Audit Log'

class DeliveryStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'

class AlertRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, default="Standard US/Canada Fresh Research Alert")
    is_active = models.BooleanField(default=True)
    freshness_max_days = models.IntegerField(default=7)
    require_us_or_ca = models.BooleanField(default=True)
    min_date_confidence = models.FloatField(default=0.70)
    min_geo_confidence = models.FloatField(default=0.70)
    min_classification_confidence = models.FloatField(default=0.70)
    notify_telegram = models.BooleanField(default=True)
    notify_email = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} [{'Active' if self.is_active else 'Disabled'}]"

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='notifications')
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for: {self.opportunity.title[:50]}"

class NotificationDelivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='deliveries')
    channel = models.CharField(max_length=20, choices=DeliveryChannel.choices)
    recipient = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING)
    error_message = models.TextField(blank=True, default='')
    response_payload = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Delivery [{self.channel}] -> {self.recipient} ({self.status})"
