import json
from datetime import timedelta
from auditlog.models import LogEntry
from django.db.models.signals import m2m_changed
from django.utils import timezone

from .models import User, Role


def user_roles_changed(instance, action, pk_set, **kwargs):
    """
    Manually creates audit log entries for changes in use roles.
    ManyToMany fields are not supported by django-auditlog so we
    must do it manually through signals.

    This function works for two signals: before adding a role (pre_add)
    and before removing a role (pre_remove). To consolidate them into one
    log entry, we check if there has been a log entry for the same model
    in the last second, and update that in lieu of creating a new log entry.
    """
    if instance.cid is not None and action in ['pre_add', 'pre_remove']:
        delta_roles = [Role.objects.get(id=id).long for id in pk_set]
        before = [role.long for role in instance.roles.all()]

        if action == 'pre_add':
            after = before + delta_roles
        else:
            after = [item for item in before if item not in delta_roles]

        before.sort()
        after.sort()

        # Checking for the log entry from pre_add
        entry_filter = LogEntry.objects.filter(object_id=instance.cid, timestamp__gt=timezone.now() - timedelta(seconds=1))
        if entry_filter.exists():
            entry = entry_filter.first()
            old_changes = entry.changes_dict
            old_changes['roles'][1] = str(after)
            entry.changes = json.dumps(old_changes)
            entry.save()
        else:
            LogEntry.objects.log_create(
                instance=instance,
                action=LogEntry.Action.UPDATE,
                changes=json.dumps({
                    'roles': [
                        str(before),
                        str(after),
                    ]
                })
            )


m2m_changed.connect(user_roles_changed, sender=User.roles.through)
