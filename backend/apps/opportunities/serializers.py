from rest_framework import serializers
from .models import Opportunity, OpportunitySource, OpportunityGeography
from apps.geography.serializers import GeographySerializer

class OpportunitySourceSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_type = serializers.CharField(source='source.source_type', read_only=True)

    class Meta:
        model = OpportunitySource
        fields = ['id', 'source', 'source_name', 'source_type', 'source_url', 'discovered_at']

class OpportunityGeographySerializer(serializers.ModelSerializer):
    geography = GeographySerializer(read_only=True)

    class Meta:
        model = OpportunityGeography
        fields = ['id', 'geography', 'scope', 'is_explicit', 'confidence']

class OpportunityListSerializer(serializers.ModelSerializer):
    geographies = OpportunityGeographySerializer(many=True, read_only=True)
    is_fresh = serializers.BooleanField(read_only=True)
    is_eligible_for_alert = serializers.BooleanField(read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id',
            'title',
            'study_type',
            'organization',
            'researcher_location',
            'source_url',
            'canonical_url',
            'application_url',
            'published_at',
            'published_at_timezone',
            'published_date_precision',
            'date_confidence',
            'reward_amount',
            'reward_currency',
            'reward_text',
            'reward_type',
            'is_paid',
            'duration_minutes',
            'duration_text',
            'eligibility_text',
            'geography_status',
            'participant_geo_confidence',
            'status',
            'has_been_notified',
            'discovered_at',
            'geographies',
            'is_fresh',
            'is_eligible_for_alert',
        ]

class OpportunityDetailSerializer(serializers.ModelSerializer):
    sources = OpportunitySourceSerializer(many=True, read_only=True)
    geographies = OpportunityGeographySerializer(many=True, read_only=True)
    duplicate_count = serializers.IntegerField(source='duplicates.count', read_only=True)
    is_fresh = serializers.BooleanField(read_only=True)
    is_eligible_for_alert = serializers.BooleanField(read_only=True)

    class Meta:
        model = Opportunity
        fields = '__all__'
