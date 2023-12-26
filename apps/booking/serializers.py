from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from apps.users.models import User
from apps.users.serializers import BasicUserSerializer

from .models import Booking


class BaseBookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    class Meta:
        model = Booking
        fields = "__all__"

    def validate(self, data):
        date_range = [data.get("start"), data.get("end")]
        range_filter = Q(start__range=date_range) | Q(end__range=date_range)

        filter_position = Booking.objects.filter(callsign=data.get("callsign")).filter(range_filter)
        if filter_position.exists():
            raise serializers.ValidationError("Position is already booked!")

        filter_user = Booking.objects.filter(user=data.get("user")).filter(range_filter)
        if filter_user.exists():
            raise serializers.ValidationError("You are already booked for this time!")

        if data.get("end") < data.get("start"):
            raise serializers.ValidationError("The end time cannot be before the start time!")

        return data

    def validate_start(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Start time must be after the current time!")

        return value

    def validate_end(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("End time must be after the current time!")

        return value


class BookingSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = Booking
        fields = "__all__"
