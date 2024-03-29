from auditlog.registry import auditlog
from django.db import models

from apps.events.models import Event
from apps.users.models import User


class Feedback(models.Model):
    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    controller = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name="feedback")
    controller_callsign = models.CharField(max_length=16, null=True, blank=True)
    pilot = models.ForeignKey(User, models.SET_NULL, null=True, related_name="feedback_given")
    pilot_callsign = models.CharField(max_length=16, null=True, blank=True)
    rating = models.IntegerField()
    comments = models.TextField()
    event = models.ForeignKey(Event, models.SET_NULL, null=True, blank=True, related_name="feedback")
    created = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        if self.controller is None:
            return "General ARTCC Feedback"
        else:
            return self.controller.full_name


auditlog.register(Feedback, exclude_fields=["created"])
