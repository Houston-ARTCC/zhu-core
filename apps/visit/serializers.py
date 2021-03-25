from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import VisitingApplication
from ..users.models import User
from ..users.serializers import AuthenticatedUserSerializer


class BaseVisitingApplicationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Visiting application already submitted.'
            )
        ]
    )

    class Meta:
        model = VisitingApplication
        fields = ['id', 'user', 'reason']


class VisitingApplicationSerializer(BaseVisitingApplicationSerializer):
    user = AuthenticatedUserSerializer()

# TODO: UniqueValidator on user field not running and an IntegrityError is raised.
