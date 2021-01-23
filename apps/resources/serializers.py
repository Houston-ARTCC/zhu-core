from django.template.defaultfilters import filesizeformat
from rest_framework import serializers

from .models import Category, Resource


class ResourceSerializer(serializers.ModelSerializer):
    extension = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = '__all__'

    def get_extension(self, resource):
        return resource.extension

    def get_size(self, resource):
        return filesizeformat(resource.size)


class ResourceGroupedSerializer(serializers.ModelSerializer):
    vrc = serializers.SerializerMethodField()
    vstars = serializers.SerializerMethodField()
    veram = serializers.SerializerMethodField()
    vatis = serializers.SerializerMethodField()
    sop = serializers.SerializerMethodField()
    loa = serializers.SerializerMethodField()
    mavp = serializers.SerializerMethodField()
    misc = serializers.SerializerMethodField()

    def _build_resource_list(self, category):
        resources = Resource.objects.filter(category=category)
        serializer = ResourceSerializer(resources, many=True)
        return serializer.data

    def get_vrc(self, obj):
        return self._build_resource_list(Category.VRC)

    def get_vstars(self, obj):
        return self._build_resource_list(Category.VSTARS)

    def get_veram(self, obj):
        return self._build_resource_list(Category.VERAM)

    def get_vatis(self, obj):
        return self._build_resource_list(Category.VATIS)

    def get_sop(self, obj):
        return self._build_resource_list(Category.SOP)

    def get_loa(self, obj):
        return self._build_resource_list(Category.LOA)

    def get_mavp(self, obj):
        return self._build_resource_list(Category.MAVP)

    def get_misc(self, obj):
        return self._build_resource_list(Category.MISC)

    class Meta:
        model = Resource
        fields = ['vrc', 'vstars', 'veram', 'vatis', 'sop', 'loa', 'mavp', 'misc']
