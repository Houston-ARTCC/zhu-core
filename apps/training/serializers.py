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


class TrainingSessionSerializer(BaseTrainingSessionSerializer):
    instructor = BaseUserSerializer()
    student = BaseUserSerializer()


class BaseTrainingRequestSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer()

    class Meta:
        model = TrainingRequest
        fields = ['id', 'user', 'start', 'end', 'type', 'level', 'remarks']


class TrainingRequestSerializer(BaseTrainingRequestSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
