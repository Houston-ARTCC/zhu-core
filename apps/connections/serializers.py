import math

from rest_framework import serializers

from zhu_core.utils import CustomDurationField
from .models import OnlineController, ControllerSession
from ..users.models import User
from ..users.serializers import BaseUserSerializer


class ControllerSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControllerSession
        exclude = ['user']


class OnlineControllerSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer()

    class Meta:
        model = OnlineController
        fields = '__all__'


class StatisticsSerializer(serializers.ModelSerializer):
    curr_hours = CustomDurationField()
    prev_hours = CustomDurationField()
    prev_prev_hours = CustomDurationField()
    activity_requirement = CustomDurationField()

    class Meta:
        model = User
        fields = ['cid', 'first_name', 'last_name', 'rating', 'curr_hours', 'initials',
                  'prev_hours', 'prev_prev_hours', 'activity_requirement']


class TopControllersSerializer(serializers.ModelSerializer):
    hours = CustomDurationField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'hours']


class TopPositionsSerializer(serializers.Serializer):
    position = serializers.CharField()
    hours = CustomDurationField()


class DailyConnectionsSerializer(serializers.Serializer):
    day = serializers.DateField()
    value = serializers.SerializerMethodField()

    def get_value(self, obj):
        return obj.get('value').total_seconds() / 3600
