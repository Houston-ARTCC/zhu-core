from rest_framework import serializers

from .models import Feedback
from ..users.models import User


class FeedbackSerializer(serializers.ModelSerializer):
    pilot = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Feedback
        fields = '__all__'
