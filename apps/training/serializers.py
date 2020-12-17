from rest_framework import serializers

from .models import TrainingSession, TrainingRequest
from ..users.models import User


class TrainingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = '__all__'


class TrainingRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    class Meta:
        model = TrainingRequest
        fields = ['user', 'start', 'end', 'type', 'level', 'remarks']
