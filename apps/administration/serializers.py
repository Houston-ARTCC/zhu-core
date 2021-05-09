import json
from auditlog.models import LogEntry
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from ..users.serializers import BaseUserSerializer


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'


class LogEntrySerializer(serializers.ModelSerializer):
    actor = BaseUserSerializer()
    changes = serializers.SerializerMethodField()
    content_type = ContentTypeSerializer()

    class Meta:
        model = LogEntry
        fields = ['id', 'action', 'actor', 'changes', 'content_type', 'object_repr', 'timestamp']

    def get_changes(self, obj):
        return json.loads(obj.changes)
