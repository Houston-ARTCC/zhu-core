from rest_framework import serializers

from apps.events.models import Event
from apps.training.models import TrainingSession
from apps.users.serializers import BasicUserSerializer


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'host', 'start', 'end']


class CalendarTrainingSerializer(serializers.ModelSerializer):
    student = BasicUserSerializer()

    class Meta:
        model = TrainingSession
        fields = ['id', 'student', 'level', 'type', 'position', 'start', 'end']
