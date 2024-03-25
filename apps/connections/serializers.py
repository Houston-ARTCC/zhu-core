from rest_framework import serializers
from rest_framework.fields import BooleanField

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
    month_1_hours = CustomDurationField()
    month_2_hours = CustomDurationField()
    month_3_hours = CustomDurationField()

    quarter_hours = CustomDurationField()
    quarter_active = BooleanField()

    class Meta:
        model = User
        fields = [
            "cid",
            "first_name",
            "last_name",
            "initials",
            "rating",
            "month_1_hours",
            "month_2_hours",
            "month_3_hours",
            "quarter_hours",
            "quarter_active",
        ]


class AdminStatisticsSerializer(StatisticsSerializer):
    t1_hours = CustomDurationField()
    t1_active = BooleanField()

    training_hours = CustomDurationField()
    training_active = BooleanField()

    class Meta:
        model = User
        fields = [
            *StatisticsSerializer.Meta.fields,
            "t1_hours",
            "t1_active",
            "training_hours",
            "training_active",
        ]


class StatusStatisticsSerializer(AdminStatisticsSerializer):
    endorsements = serializers.JSONField()
    quarter_quota = CustomDurationField()

    hou_gnd_hours = CustomDurationField()
    hou_twr_hours = CustomDurationField()
    iah_gnd_hours = CustomDurationField()
    iah_twr_hours = CustomDurationField()
    i90_hours = CustomDurationField()
    zhu_hours = CustomDurationField()

    class Meta:
        model = User
        fields = [
            *AdminStatisticsSerializer.Meta.fields,
            "endorsements",
            "quarter_quota",
            "hou_gnd_hours",
            "hou_twr_hours",
            "iah_gnd_hours",
            "iah_twr_hours",
            "i90_hours",
            "zhu_hours",
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
