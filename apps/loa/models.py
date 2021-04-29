from django.db import models

from ..users.models import User


class LOA(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='loa_requests')
    start = models.DateField()
    end = models.DateField()
    remarks = models.TextField()
    approved = models.BooleanField(default=False)
