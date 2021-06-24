from rest_framework import serializers

from .models import Feedback
from ..events.serializers import BasicEventSerializer
from ..users.models import User
from ..users.serializers import AuthenticatedBasicUserSerializer


class BaseFeedbackSerializer(serializers.ModelSerializer):
    pilot = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Feedback
        fields = '__all__'


class FeedbackSerializer(BaseFeedbackSerializer):
    controller = AuthenticatedBasicUserSerializer()
    pilot = AuthenticatedBasicUserSerializer()
    event = BasicEventSerializer()


class BasicFeedbackSerializer(serializers.ModelSerializer):
    event = BasicEventSerializer()

    class Meta:
        model = Feedback
        fields = ['id', 'controller_callsign', 'pilot_callsign', 'rating', 'comments', 'event', 'created']


class EventFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'rating']
