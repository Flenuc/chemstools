from rest_framework import serializers
from .models import TelemetryEvent

class TelemetryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryEvent
        fields = ['event_name', 'details', 'session_id']
