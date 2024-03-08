from django.db import models

from apps.users.models import User


class OnlineController(models.Model):
    class Meta:
        verbose_name = "Online controller"

    user = models.ForeignKey(User, models.CASCADE, related_name="controller_online")
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
        return f"{self.user.full_name} on {self.callsign}"


class ControllerSession(models.Model):
    class Meta:
        verbose_name = "Controller session"

    user = models.ForeignKey(User, models.CASCADE, related_name="sessions")
    callsign = models.CharField(max_length=16)
    start = models.DateTimeField()
    duration = models.DurationField()

    @property
    def end(self):
        return self.start + self.duration

    @property
    def facility(self):
        return self.callsign.split("_")[0]

    @property
    def level(self):
        return self.callsign.split("_")[-1]

    def __str__(self):
        return f"{self.start} | {self.user.full_name} on {self.callsign}"
