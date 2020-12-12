from django.db import models

from ..users.models import User


class Type(models.IntegerChoices):
    CLASSROOM = 0, 'Classroom'
    SWEATBOX = 1, 'Sweatbox'
    ONLINE = 2, 'Online'
    OTS = 3, 'OTS'


class Level(models.IntegerChoices):
    MINOR_GROUND = 0, 'Minor Ground'
    MAJOR_GROUND = 1, 'Major Ground'
    MINOR_TOWER = 2, 'Minor Tower'
    MAJOR_TOWER = 3, 'Major Tower'
    MINOR_APPROACH = 4, 'Minor Approach'
    MAJOR_APPROACH = 5, 'Major Approach'
    CENTER = 6, 'Center'
    OCEANIC = 7, 'Oceanic'


class Status(models.IntegerChoices):
    SCHEDULED = 0, 'Scheduled'
    COMPLETED = 1, 'Completed'
    CANCELLED = 2, 'Cancelled'
    NO_SHOW = 3, 'No-Show'


class OTSStatus(models.IntegerChoices):
    NON_OTS = 0, 'Non-OTS'
    PASSED = 1, 'Passed'
    FAILED = 2, 'Failed'
    RECOMMENDED = 3, 'Recommended'


class TrainingSession(models.Model):
    class Meta:
        verbose_name_plural = 'Training Sessions'

    student = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='student_sessions')
    instructor = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='instructor_sessions')
    start = models.DateTimeField()
    end = models.DateTimeField()
    movements = models.IntegerField(default=0)
    progress = models.IntegerField(default=3)
    position = models.CharField(max_length=16)
    type = models.IntegerField(choices=Type.choices)
    level = models.IntegerField(choices=Level.choices)
    status = models.IntegerField(default=0, choices=Status.choices)
    ots_status = models.IntegerField(default=0, choices=OTSStatus.choices)
    ctrs_id = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    solo_granted = models.BooleanField(default=False)

    @property
    def duration(self):
        return self.end - self.start

    def __str__(self):
        return f'{self.student.full_name} {self.get_level_display()} {self.get_type_display()} @ {self.start}'


class TrainingRequest(models.Model):
    class Meta:
        verbose_name_plural = 'Training Requests'

    student = models.ForeignKey(User, models.CASCADE, related_name='training_requests')
    start = models.DateTimeField()
    end = models.DateTimeField()
    type = models.IntegerField(choices=Type.choices)
    level = models.IntegerField(choices=Level.choices)
    remarks = models.TextField(null=True, blank=True)

    @property
    def duration(self):
        return self.end - self.start

    def __str__(self):
        return f'{self.student.full_name} {self.get_level_display()} {self.get_type_display()}'
