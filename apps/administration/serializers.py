from auditlog.models import LogEntry
from django.core.exceptions import FieldDoesNotExist
from rest_framework import serializers

from apps.users.serializers import BasicUserSerializer


class LogEntrySerializer(serializers.ModelSerializer):
    actor = BasicUserSerializer()
    changes = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = ["id", "action", "actor", "changes", "content_type", "object_id", "object_repr", "timestamp"]

    def get_changes(self, obj):
        """
        The LogEntry attribute 'changes_display_dict' does not work for ManyToMany
        related fields. This is a workaround that manually replaces choices with
        their representations.
        """
        changes = obj.changes_dict
        model = obj.content_type.model_class()

        for field in changes:
            try:
                field_class = model._meta.get_field(field)
            except FieldDoesNotExist:
                # This can happen if a field gets deleted. We'll just ignore it.
                continue

            if getattr(field_class, "choices", None):
                choices = {str(key): value for key, value in field_class.choices}
                for i in range(2):
                    changes[field][i] = choices.get(changes.get(field)[i])

        return changes

    def get_content_type(self, obj):
        return obj.content_type.name
