from rest_framework import serializers

from apps.users.models import User
from apps.users.serializers import BasicUserSerializer
from zhu_core.utils import CustomDurationField

from .models import ControllerSession, OnlineController


class ControllerSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControllerSession
        exclude = ["user"]


class OnlineControllerSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = OnlineController
        fields = "__all__"


class StatisticsSerializer(serializers.ModelSerializer):
    curr_hours = CustomDurationField()
    prev_hours = CustomDurationField()
    prev_prev_hours = CustomDurationField()
    activity_requirement = CustomDurationField()

    class Meta:
        model = User
        fields = [
            "cid",
            "first_name",
            "last_name",
            "rating",
            "curr_hours",
            "initials",
            "is_staff",
            "prev_hours",
            "prev_prev_hours",
            "activity_requirement",
        ]


class TopControllersSerializer(serializers.ModelSerializer):
    hours = CustomDurationField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "hours"]


class TopPositionsSerializer(serializers.Serializer):
    position = serializers.CharField()
    hours = CustomDurationField()


class DailyConnectionsSerializer(serializers.Serializer):
    date = serializers.DateField()
    count = serializers.SerializerMethodField()

    def get_count(self, obj):
        return obj.get("value").total_seconds() / 3600
