from rest_framework import serializers

from .models import OnlineController, ControllerSession
from ..users.models import User


class ControllerSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControllerSession
        exclude = ['user']


class OnlineControllerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineController
        fields = '__all__'


class StatisticsSerializer(serializers.ModelSerializer):
    curr_hours = serializers.DurationField()
    prev_hours = serializers.DurationField()
    prev_prev_hours = serializers.DurationField()

    class Meta:
        model = User
        fields = ['cid', 'first_name', 'last_name', 'rating', 'curr_hours', 'prev_hours', 'prev_prev_hours']


class TopControllersSerializer(serializers.ModelSerializer):
    hours = serializers.DurationField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'hours']


class TopPositionsSerializer(serializers.Serializer):
    position = serializers.CharField()
    hours = serializers.DurationField()
