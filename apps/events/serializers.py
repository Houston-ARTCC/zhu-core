from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Event, EventPosition, PositionShift, ShiftRequest, SupportRequest, PositionPreset
from ..users.models import User
from ..users.serializers import BasicUserSerializer, AuthenticatedBasicUserSerializer, EventScoreUserSerializer


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
    # user = EventScoreUserSerializer()
    user = BasicUserSerializer()

    class Meta:
        model = ShiftRequest
        exclude = ['shift']


class BaseShiftSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    class Meta:
        model = PositionShift
        fields = '__all__'


class ShiftSerializer(serializers.ModelSerializer):
    requests = ShiftRequestSerializer(many=True, read_only=True)
    user = BasicUserSerializer()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

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
    shifts = ShiftSerializer(many=True, read_only=True)

    class Meta:
        model = EventPosition
        exclude = ['event']


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

    def validate(self, data):
        if data.get('end') < data.get('start'):
            raise serializers.ValidationError('The end time cannot be before the start time!')

        return data


class BaseSupportRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = SupportRequest
        fields = '__all__'


class SupportRequestSerializer(BaseSupportRequestSerializer):
    user = AuthenticatedBasicUserSerializer()


class PositionPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionPreset
        fields = '__all__'
