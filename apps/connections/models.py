from django.db import models

from ..users.models import User


class OnlineController(models.Model):
    class Meta:
        verbose_name_plural = 'Online Controllers'

    user = models.ForeignKey(User, models.CASCADE, related_name='controller_online')
    callsign = models.CharField(max_length=16)
    online_since = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True)

    def convert_to_session(self):
        ControllerSession(
            user=self.user,
            callsign=self.callsign,
            start=self.online_since,
            duration=self.duration,
        ).save()

    @property
    def duration(self):
        return self.last_updated - self.online_since

    def __str__(self):
        return f'{self.user.full_name} on {self.callsign}'


class ControllerSession(models.Model):
    class Meta:
        verbose_name_plural = 'Controller Sessions'

    user = models.ForeignKey(User, models.CASCADE, related_name='controller_sessions')
    callsign = models.CharField(max_length=16)
    start = models.DateTimeField()
    duration = models.DurationField()

    @property
    def end(self):
        return self.start + self.duration

    def __str__(self):
        return f'{self.start} | {self.user.full_name} on {self.callsign}'
