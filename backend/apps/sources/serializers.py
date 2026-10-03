from rest_framework import serializers
from .models import Source, SourceRun, DiscoveryQuery, CrawlFailure

class SourceSerializer(serializers.ModelSerializer):
    run_count = serializers.IntegerField(source='runs.count', read_only=True)

    class Meta:
        model = Source
        fields = '__all__'

class SourceRunSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)

    class Meta:
        model = SourceRun
        fields = '__all__'

class DiscoveryQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscoveryQuery
        fields = '__all__'

class CrawlFailureSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)

    class Meta:
        model = CrawlFailure
        fields = '__all__'
