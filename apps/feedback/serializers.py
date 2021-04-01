from rest_framework import serializers

from .models import Feedback
from ..events.serializers import BasicEventSerializer
from ..users.models import User
from ..users.serializers import AuthenticatedBaseUserSerializer


class BaseFeedbackSerializer(serializers.ModelSerializer):
    pilot = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Feedback
        fields = '__all__'


class FeedbackSerializer(BaseFeedbackSerializer):
    controller = AuthenticatedBaseUserSerializer()
    pilot = AuthenticatedBaseUserSerializer()
    event = BasicEventSerializer()


class SimplifiedFeedbackSerializer(serializers.ModelSerializer):
    event = BasicEventSerializer()

    class Meta:
        model = Feedback
        fields = ['id', 'controller_callsign', 'pilot_callsign', 'rating', 'comments', 'event', 'created']
