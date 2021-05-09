import json
from auditlog.models import LogEntry
from rest_framework import serializers

from ..users.serializers import BaseUserSerializer


class LogEntrySerializer(serializers.ModelSerializer):
    actor = BaseUserSerializer()
    changes = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = ['id', 'action', 'actor', 'changes', 'content_type', 'object_id', 'object_repr', 'timestamp']

    def get_changes(self, obj):
        return json.loads(obj.changes)

    def get_content_type(self, obj):
        return obj.content_type.name
