from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.users.models import User
from apps.users.serializers import BasicUserSerializer

from .models import MentorAvailability, TrainingRequest, TrainingSession


class BaseTrainingSessionSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    instructor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = TrainingSession
        fields = "__all__"

    def validate(self, data):
        if data.get("start") and data.get("end") and data.get("end") < data.get("start"):
            raise serializers.ValidationError("The end time cannot be before the start time!")

        return data


class TrainingSessionSerializer(BaseTrainingSessionSerializer):
    instructor = BasicUserSerializer()
    student = BasicUserSerializer()


class BaseTrainingRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    class Meta:
        model = TrainingRequest
        fields = ["id", "user", "start", "end", "type", "level", "remarks"]

    def validate(self, data):
        if data.get("user").training_requests.filter(end__gt=timezone.now()).count() >= 7:
            raise serializers.ValidationError("You may not have more than 7 active requests!")

        if data.get("end") < data.get("start"):
            raise serializers.ValidationError("The end time cannot be before the start time!")

        if data.get("start") > timezone.now() + timedelta(days=30):
            raise serializers.ValidationError("The start time must be within the next 30 days!")

        return data


class BasicMentorAvailabilitySerializer(serializers.ModelSerializer):
    start = serializers.TimeField(format="%H:%M")
    end = serializers.TimeField(format="%H:%M")

    class Meta:
        model = MentorAvailability
        fields = ["start", "end"]


class MentorAvailabilitySerializer(serializers.ModelSerializer):
    user = BasicUserSerializer()
    start = serializers.TimeField(format="%H:%M")
    end = serializers.TimeField(format="%H:%M")

    class Meta:
        model = MentorAvailability
        fields = "__all__"
