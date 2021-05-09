from auditlog.registry import auditlog
from django.db import models

from ..users.models import User


class VisitingApplication(models.Model):
    class Meta:
        verbose_name = 'Vistiting application'

    user = models.OneToOneField(User, models.CASCADE, related_name='visiting_application', unique=True)
    reason = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.full_name


auditlog.register(VisitingApplication)
