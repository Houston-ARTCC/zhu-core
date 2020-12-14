from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import VisitingApplication
from ..users.models import User


class VisitingApplicationSerializer(serializers.ModelSerializer):
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
        fields = ['user', 'reason']

# TODO: UniqueValidator on user field not running and an IntegrityError is raised.
