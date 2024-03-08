from auditlog.registry import auditlog
from django.db import models

from apps.users.models import User


class Announcement(models.Model):
    class Meta:
        verbose_name = "Announcement"

    title = models.CharField(max_length=128)
    body = models.TextField()
    author = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name="announcements")
    posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


auditlog.register(Announcement)
