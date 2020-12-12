from rest_framework import serializers

from .models import Event, EventPosition, EventPositionRequest


class EventPositionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPositionRequest
        fields = ['user']


class EventPositionSerializer(serializers.ModelSerializer):
    requests = EventPositionRequestSerializer(many=True, read_only=True)

    class Meta:
        model = EventPosition
        fields = ['callsign', 'requests']


class EventWithPositionsSerializer(serializers.ModelSerializer):
    positions = EventPositionSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'banner', 'start', 'end', 'host', 'description', 'hidden', 'positions']


class EventSerializer(serializers.ModelSerializer):
    archived = serializers.BooleanField(read_only=True, source='is_archived')

    class Meta:
        model = Event
        fields = ['id', 'name', 'banner', 'start', 'end', 'host', 'description', 'hidden', 'archived']
