import uuid
from django.db import models

class GeographyScope(models.TextChoices):
    NATIONWIDE = 'nationwide', 'Nationwide'
    STATE = 'state', 'State'
    PROVINCE = 'province', 'Province'
    TERRITORY = 'territory', 'Territory'
    REGION = 'region', 'Region'
    CITY = 'city', 'City'
    COUNTY = 'county', 'County'
    METRO_AREA = 'metro_area', 'Metropolitan Area'
    MULTI_STATE = 'multi_state', 'Multi-State'
    MULTI_PROVINCE = 'multi_province', 'Multi-Province'
    REMOTE = 'remote', 'Remote'
    UNKNOWN = 'unknown', 'Unknown'

class Geography(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=2, help_text="ISO 2-letter country code: US or CA")
    state_province = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    state_code = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    city = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    metro_area = models.CharField(max_length=150, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    scope = models.CharField(max_length=30, choices=GeographyScope.choices, default=GeographyScope.UNKNOWN, db_index=True)
    is_us = models.BooleanField(default=False, db_index=True)
    is_ca = models.BooleanField(default=False, db_index=True)
    aliases = models.JSONField(default=list, blank=True, help_text="List of alternate names or regex keywords")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Geography'
        verbose_name_plural = 'Geographies'
        indexes = [
            models.Index(fields=['country', 'state_code']),
            models.Index(fields=['country', 'city']),
            models.Index(fields=['scope', 'country']),
        ]

    def __str__(self):
        parts = []
        if self.city:
            parts.append(self.city)
        if self.state_code:
            parts.append(self.state_code)
        elif self.state_province:
            parts.append(self.state_province)
        parts.append(self.country)
        return ", ".join(parts) + f" [{self.scope}]"
