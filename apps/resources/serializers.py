from django.template.defaultfilters import filesizeformat
from rest_framework import serializers

from .models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    extension = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = "__all__"

    def get_extension(self, resource):
        return resource.extension

    def get_size(self, resource):
        return filesizeformat(resource.size)
