from auditlog.registry import auditlog
from django.db import models

from apps.users.models import User


class Type(models.IntegerChoices):
    CLASSROOM = 0, "Classroom"
    SWEATBOX = 1, "Sweatbox"
    ONLINE = 2, "Online"
    OTS = 3, "OTS"


class Level(models.IntegerChoices):
    GROUND = 0, "Ground"
    GROUND_T1 = 1, "Ground (T1)"
    TOWER = 2, "Tower"
    TOWER_T1 = 3, "Tower (T1)"
    APPROACH = 4, "Approach"
    APPROACH_T1 = 5, "Approach (T1)"
    CENTER = 6, "Center (T2)"


class Status(models.IntegerChoices):
    SCHEDULED = 0, "Scheduled"
    COMPLETED = 1, "Completed"
    CANCELLED = 2, "Cancelled"
    NO_SHOW = 3, "No-Show"


class OTSStatus(models.IntegerChoices):
    NON_OTS = 0, "Non-OTS"
    PASSED = 1, "Passed"
    FAILED = 2, "Failed"
    RECOMMENDED = 3, "Recommended"


class DayOfWeek(models.IntegerChoices):
    SUNDAY = 0, "Sunday"
    MONDAY = 1, "Monday"
    TUESDAY = 2, "Tuesday"
    WEDNESDAY = 3, "Wednesday"
    THURSDAY = 4, "Thursday"
    FRIDAY = 5, "Friday"
    SATURDAY = 6, "Saturday"


class TrainingSession(models.Model):
    class Meta:
        verbose_name = "Training session"

    student = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name="student_sessions")
    instructor = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name="instructor_sessions")
    start = models.DateTimeField()
    end = models.DateTimeField()
    movements = models.IntegerField(default=0)
    progress = models.IntegerField(default=3)
    position = models.CharField(max_length=16, null=True, blank=True)
    type = models.IntegerField(choices=Type.choices)  # noqa: A003
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
        return self.student.full_name


class TrainingRequest(models.Model):
    class Meta:
        verbose_name = "Training request"

    user = models.ForeignKey(User, models.CASCADE, related_name="training_requests")
    start = models.DateTimeField()
    end = models.DateTimeField()
    type = models.IntegerField(choices=Type.choices)  # noqa: A003
    level = models.IntegerField(choices=Level.choices)
    remarks = models.TextField(null=True, blank=True)

    @property
    def duration(self):
        return self.end - self.start

    def __str__(self):
        return self.user.full_name


class MentorAvailability(models.Model):
    class Meta:
        verbose_name = "Mentor availability"
        unique_together = ("user", "day")

    user = models.ForeignKey(User, models.CASCADE, related_name="available_days")
    day = models.IntegerField(choices=DayOfWeek.choices)
    start = models.TimeField()
    end = models.TimeField()


auditlog.register(TrainingSession)
