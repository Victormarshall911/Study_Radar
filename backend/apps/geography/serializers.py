from rest_framework import serializers
from .models import Geography

class GeographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Geography
        fields = '__all__'
