from rest_framework import serializers

from apps.events.models import Event
from apps.training.models import TrainingSession
from apps.users.serializers import BaseUserSerializer


class EventCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'host', 'start', 'end']


class TrainingCalendarSerializer(serializers.ModelSerializer):
    student = BaseUserSerializer()

    class Meta:
        model = TrainingSession
        fields = ['id', 'student', 'level', 'type', 'position', 'start', 'end']
