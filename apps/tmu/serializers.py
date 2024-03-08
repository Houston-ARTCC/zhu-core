from rest_framework import serializers

from .models import ATIS, METAR, TMUNotice


class ATISSerializer(serializers.ModelSerializer):
    class Meta:
        model = ATIS
        fields = "__all__"


class TMUNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMUNotice
        fields = "__all__"


class METARSerializer(serializers.ModelSerializer):
    class Meta:
        model = METAR
        exclude = ["id"]
