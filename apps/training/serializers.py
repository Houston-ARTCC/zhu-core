from rest_framework import serializers

from .models import TrainingSession, TrainingRequest
from ..users.models import User
from ..users.serializers import BaseUserSerializer


class BaseTrainingSessionSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    instructor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = TrainingSession
        fields = '__all__'

    def validate(self, data):
        if data.get('start') and data.get('end') and data.get('end') < data.get('start'):
            raise serializers.ValidationError('The end time cannot be before the start time!')

        return data


class TrainingSessionSerializer(BaseTrainingSessionSerializer):
    instructor = BaseUserSerializer()
    student = BaseUserSerializer()


class BaseTrainingRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = TrainingRequest
        fields = ['id', 'user', 'start', 'end', 'type', 'level', 'remarks']

    def validate(self, data):
        if data.get('end') < data.get('start'):
            raise serializers.ValidationError('The end time cannot be before the start time!')

        return data


class TrainingRequestSerializer(BaseTrainingRequestSerializer):
    user = BaseUserSerializer()
