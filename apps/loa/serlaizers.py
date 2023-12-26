from rest_framework import serializers

from apps.users.models import User
from apps.users.serializers import BasicUserSerializer

from .models import LOA


class BaseLOASerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    class Meta:
        model = LOA
        fields = "__all__"


class LOASerializer(BaseLOASerializer):
    user = BasicUserSerializer()
