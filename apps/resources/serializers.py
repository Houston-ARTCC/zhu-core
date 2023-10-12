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
    poly = serializers.SerializerMethodField()
    proc = serializers.SerializerMethodField()
    loa = serializers.SerializerMethodField()
    vatis = serializers.SerializerMethodField()
    rvm = serializers.SerializerMethodField()
    ref = serializers.SerializerMethodField()

    def _build_resource_list(self, category):
        resources = Resource.objects.filter(category=category)
        serializer = ResourceSerializer(resources, many=True)
        return serializer.data

    def get_poly(self, obj):
        return self._build_resource_list(Category.POLY)

    def get_proc(self, obj):
        return self._build_resource_list(Category.PROC)

    def get_loa(self, obj):
        return self._build_resource_list(Category.LOA)

    def get_vatis(self, obj):
        return self._build_resource_list(Category.vATIS)

    def get_rvm(self, obj):
        return self._build_resource_list(Category.RVM)

    def get_ref(self, obj):
        return self._build_resource_list(Category.REF)

    class Meta:
        model = Resource
        fields = ['poly', 'proc', 'loa', 'vatis', 'rvm', 'ref']
