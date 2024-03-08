from rest_framework import serializers

from apps.users.models import User
from apps.users.serializers import BasicUserSerializer

from .models import Announcement


class BaseAnnouncementSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    class Meta:
        model = Announcement
        fields = "__all__"


class AnnouncementSerializer(BaseAnnouncementSerializer):
    author = BasicUserSerializer()
