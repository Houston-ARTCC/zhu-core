from auditlog.registry import auditlog
from django.db import models

from ..users.models import User


class LOA(models.Model):
    class Meta:
        verbose_name = 'LOA'

    user = models.ForeignKey(User, models.CASCADE, related_name='loa_requests')
    start = models.DateField()
    end = models.DateField()
    remarks = models.TextField()
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name


auditlog.register(LOA)
