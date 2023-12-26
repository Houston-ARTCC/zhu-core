from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.users.models import User
from apps.users.serializers import AuthenticatedUserSerializer

from .models import VisitingApplication


class BaseVisitingApplicationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        validators=[UniqueValidator(queryset=User.objects.all(), message="Visiting application already submitted.")],
    )

    class Meta:
        model = VisitingApplication
        fields = ["id", "user", "reason"]


class VisitingApplicationSerializer(BaseVisitingApplicationSerializer):
    user = AuthenticatedUserSerializer()
