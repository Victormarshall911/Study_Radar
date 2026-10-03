from rest_framework import serializers
from .models import RawDocument

class RawDocumentSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)

    class Meta:
        model = RawDocument
        fields = '__all__'

class ManualIngestRequestSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    save_to_database = serializers.BooleanField(default=False)
