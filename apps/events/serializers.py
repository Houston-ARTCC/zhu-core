from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Event, EventPosition, EventPositionRequest
from ..users.models import User


class EventPositionRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    class Meta:
        model = EventPositionRequest
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=EventPositionRequest.objects.all(),
                fields=['position', 'user'],
                message='Position already requested.'
            )
        ]


class EventPositionSerializer(serializers.ModelSerializer):
    requests = EventPositionRequestSerializer(many=True, read_only=True)

    class Meta:
        model = EventPosition
        fields = ['event', 'user', 'callsign', 'requests']


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
