from rest_framework import serializers

from .models import Announcement
from ..users.models import User
from ..users.serializers import BasicUserSerializer


class BaseAnnouncementSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Announcement
        fields = '__all__'


class AnnouncementSerializer(BaseAnnouncementSerializer):
    author = BasicUserSerializer()
