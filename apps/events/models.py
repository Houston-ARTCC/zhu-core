from datetime import timedelta
from auditlog.registry import auditlog
from django.db import models
from django.utils import timezone

from apps.users.models import User


class Event(models.Model):
    class Meta:
        verbose_name = 'Event'

    name = models.CharField(max_length=128)
    banner = models.URLField(null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    host = models.CharField(max_length=32)
    description = models.TextField(null=True, blank=True)
    hidden = models.BooleanField(default=False)

    @property
    def duration(self):
        return self.end - self.start
    
    @property
    def is_archived(self):
        return self.end < timezone.now()

    def __str__(self):
        return self.name


class EventPosition(models.Model):
    class Meta:
        verbose_name = 'Event position'

    event = models.ForeignKey(Event, models.CASCADE, related_name='positions')
    callsign = models.CharField(max_length=16)

    @property
    def shift_duration(self):
        return timedelta(seconds=self.event.duration.total_seconds() / self.shifts.count())

    def __str__(self):
        return f'{self.event} | {self.callsign}'


class PositionShift(models.Model):
    class Meta:
        verbose_name = 'Position shift'

    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True, related_name='event_shifts')
    position = models.ForeignKey(EventPosition, models.CASCADE, related_name='shifts')

    @property
    def start(self):
        return self.position.event.start + (list(self.position.shifts.all()).index(self) + 1) * self.position.shift_duration

    @property
    def end(self):
        return self.start + self.position.shift_duration

    def assign_user(self, user):
        self.user = user
        self.save()

    def __str__(self):
        return f'{self.position} ({self.start.strftime("%H:%M")}z - {self.end.strftime("%H:%M")}z)'


class ShiftRequest(models.Model):
    class Meta:
        verbose_name = 'Shift request'

    shift = models.ForeignKey(PositionShift, models.CASCADE, related_name='requests')
    user = models.ForeignKey(User, models.CASCADE, related_name='shift_requests')

    def accept_request(self):
        self.shift.assign_user(self.user)

    def __str__(self):
        return f'{self.user.full_name} for {self.shift}'


class SupportRequest(models.Model):
    class Meta:
        verbose_name = 'Event support request'

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


class PositionPreset(models.Model):
    class Meta:
        verbose_name = 'Position preset'

    name = models.CharField(max_length=64)
    positions = models.JSONField(default=list)
    
    def apply_to_event(self, event):
        for preset_position in self.positions:
            # Create Position
            position = EventPosition(event=event, callsign=preset_position.get('callsign'))
            position.save()

            # Create Shifts
            for _ in range(preset_position.get('shifts')):
                PositionShift(position=position).save()

    def __str__(self):
        return self.name


# TODO: Add requested fields to SupportRequest model


auditlog.register(Event, exclude_fields=['feedback', 'positions'])
auditlog.register(SupportRequest)
auditlog.register(PositionPreset)
