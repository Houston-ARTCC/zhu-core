from rest_framework import serializers

from .models import ATIS, TMUNotice


class ATISSerializer(serializers.ModelSerializer):
    class Meta:
        model = ATIS
        fields = '__all__'


class TMUNoticeSerializer(serializers.ModelSerializer):
    class TMUNotice:
        model = TMUNotice
        fields = '__all__'
