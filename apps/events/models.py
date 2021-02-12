from django.db import models
from django.utils import timezone

from apps.users.models import User


class Event(models.Model):
    name = models.CharField(max_length=128)
    banner = models.URLField(null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    host = models.CharField(max_length=32)
    description = models.TextField(null=True, blank=True)
    hidden = models.BooleanField(default=False)
    
    @property
    def is_archived(self):
        return self.end < timezone.now()

    def __str__(self):
        return self.name


class EventPosition(models.Model):
    class Meta:
        verbose_name_plural = 'Event Positions'

    event = models.ForeignKey(Event, models.CASCADE, related_name='positions')
    callsign = models.CharField(max_length=16)

    def __str__(self):
        return f'{self.event} | {self.callsign}'


class PositionShift(models.Model):
    class Meta:
        verbose_name_plural = 'Position Shifts'

    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True, related_name='event_positions')
    position = models.ForeignKey(EventPosition, models.CASCADE, related_name='shifts')
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return f'{self.position} ({self.start.strftime("%H:%M")}z - {self.end.strftime("%H:%M")}z)'


class ShiftRequest(models.Model):
    class Meta:
        verbose_name_plural = 'Shift Requests'

    shift = models.ForeignKey(PositionShift, models.CASCADE, related_name='requests')
    user = models.ForeignKey(User, models.CASCADE, related_name='shift_requests')

    def accept_request(self):
        self.shift.user = self.shift
        self.shift.save()

    def __str__(self):
        return f'{self.user.full_name} for {self.shift}'


class SupportRequest(models.Model):
    class Meta:
        verbose_name_plural = 'Event Support Requests'

    user = models.ForeignKey(User, models.CASCADE, related_name='support_requests')
    name = models.CharField(max_length=128)
    banner = models.URLField(null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    host = models.CharField(max_length=32)
    description = models.TextField(null=True, blank=True)

    def convert_to_event(self):
        Event(
            name=self.name,
            banner=self.banner,
            start=self.start,
            end=self.end,
            host=self.host,
            description=self.description,
            hidden=True,
        ).save()

    def __str__(self):
        return f'{self.name} by {self.host}'

# TODO: Add requested fields to SupportRequest model
