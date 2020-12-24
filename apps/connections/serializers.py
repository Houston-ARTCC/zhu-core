from rest_framework import serializers

from .models import OnlineController, ControllerSession


class OnlineControllerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineController
        fields = '__all__'


class ControllerSessionSerializer(serializers.ModelSerializer):
    class TMUNotice:
        model = ControllerSession
        fields = '__all__'
