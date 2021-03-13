from rest_framework import serializers

from .models import TrainingSession, TrainingRequest
from ..users.models import User
from ..users.serializers import BaseUserSerializer


class TrainingSessionSerializer(serializers.ModelSerializer):
    instructor = BaseUserSerializer()

    class Meta:
        model = TrainingSession
        fields = '__all__'


class TrainingRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    class Meta:
        model = TrainingRequest
        fields = ['id', 'user', 'start', 'end', 'type', 'level', 'remarks']
