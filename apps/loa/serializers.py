from datetime import timedelta

from rest_framework import serializers

from apps.users.models import User
from apps.users.serializers import BasicUserSerializer

from .models import LOA


class BaseLOASerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = LOA
        fields = "__all__"

    def validate(self, data):
        if data.get("end") < data.get("start"):
            raise serializers.ValidationError("The end time cannot be before the start time")

        if data.get("end") - data.get("start") < timedelta(days=30):
            raise serializers.ValidationError("The LOA must last at least 30 days")

        return data


class LOASerializer(BaseLOASerializer):
    user = BasicUserSerializer()
