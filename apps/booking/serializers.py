from rest_framework import serializers

from .models import Booking
from ..users.models import User
from ..users.serializers import BaseUserSerializer


class BaseBookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Booking
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer()

    class Meta:
        model = Booking
        fields = '__all__'
