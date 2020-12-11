from django.db import models

from ..users.models import User
from ..events.models import Event


class Feedback(models.Model):
    class Meta:
        verbose_name_plural = 'Feedback'

    controller = models.ForeignKey(User, models.CASCADE, related_name='controller_feedback')
    callsign = models.CharField(max_length=16)
    rating = models.IntegerField()
    comments = models.TextField()
    event = models.ForeignKey(Event, models.SET_NULL, null=True, blank=True, related_name='feedback')
    pilot_cid = models.IntegerField()
    pilot_name = models.CharField(max_length=64, null=True, blank=True)
    pilot_email = models.EmailField(null=True, blank=True)
    pilot_callsign = models.CharField(max_length=16, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.controller.full_name} @ {self.created.strftime("%b %d, %Y %H%Mz")}'
