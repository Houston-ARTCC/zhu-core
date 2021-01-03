from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Event, EventPosition, EventPositionRequest, SupportRequest
from ..users.models import User
from ..users.serializers import BasicUserSerializer


class BasePositionRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = EventPositionRequest
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=EventPositionRequest.objects.all(),
                fields=['position', 'user'],
                message='Position already requested.'
            )
        ]


class PositionRequestSerializer(BasePositionRequestSerializer):
    user = BasicUserSerializer()


class BasePositionSerializer(serializers.ModelSerializer):
    requests = PositionRequestSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True)

    class Meta:
        model = EventPosition
        fields = '__all__'


class PositionSerializer(BasePositionSerializer):
    user = BasicUserSerializer()


class EventSerializer(serializers.ModelSerializer):
    archived = serializers.BooleanField(read_only=True, source='is_archived')
    positions = PositionSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'banner', 'start', 'end', 'host', 'description', 'hidden', 'archived', 'positions']


class SupportSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    class Meta:
        model = SupportRequest
        fields = '__all__'
