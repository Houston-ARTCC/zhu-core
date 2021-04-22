from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Event, EventPosition, PositionShift, ShiftRequest, SupportRequest
from ..users.models import User
from ..users.serializers import BaseUserSerializer, AuthenticatedBaseUserSerializer, EventScoreUserSerializer


class BaseShiftRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = ShiftRequest
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShiftRequest.objects.all(),
                fields=['shift', 'user'],
                message='Shift already requested.'
            )
        ]


class ShiftRequestSerializer(serializers.ModelSerializer):
    user = EventScoreUserSerializer()

    class Meta:
        model = ShiftRequest
        exclude = ['shift']


class BaseShiftSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    start = serializers.DateTimeField()
    end= serializers.DateTimeField()

    class Meta:
        model = PositionShift
        fields = '__all__'


class ShiftSerializer(serializers.ModelSerializer):
    requests = ShiftRequestSerializer(many=True, read_only=True)
    user = BaseUserSerializer()
    start = serializers.DateTimeField()
    end= serializers.DateTimeField()

    class Meta:
        model = PositionShift
        exclude = ['position']


class BasePositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPosition
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=EventPosition.objects.all(),
                fields=['event', 'callsign'],
                message='Position with this name already exists.'
            )
        ]


class PositionSerializer(serializers.ModelSerializer):
    shifts = serializers.SerializerMethodField()

    class Meta:
        model = EventPosition
        exclude = ['event']

    def get_shifts(self, instance):
        shifts = instance.shifts.all()
        return ShiftSerializer(shifts, many=True, read_only=True).data


class BasicEventSerializer(serializers.ModelSerializer):
    archived = serializers.BooleanField(read_only=True, source='is_archived')
    available_shifts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'banner', 'start', 'end', 'host', 'hidden', 'archived', 'available_shifts']

    def get_available_shifts(self, obj):
        return PositionShift.objects.filter(position__event=obj, user__isnull=True).count()


class EventSerializer(serializers.ModelSerializer):
    archived = serializers.BooleanField(read_only=True, source='is_archived')
    positions = PositionSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'banner', 'start', 'end', 'host', 'description', 'hidden', 'archived', 'positions']


class BaseSupportRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = SupportRequest
        fields = '__all__'


class SupportRequestSerializer(BaseSupportRequestSerializer):
    user = AuthenticatedBaseUserSerializer()
