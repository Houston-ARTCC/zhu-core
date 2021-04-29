from rest_framework import serializers

from .models import LOA
from ..users.models import User
from ..users.serializers import BaseUserSerializer


class BaseLOASerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = LOA
        fields = '__all__'


class LOASerializer(BaseLOASerializer):
    user = BaseUserSerializer()
