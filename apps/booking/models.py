from django.db import models

from ..users.models import User


class Booking(models.Model):
    class Meta:
        verbose_name = 'Booking'

    user = models.ForeignKey(User, models.CASCADE, related_name='bookings')
    callsign = models.CharField(max_length=16)
    start = models.DateTimeField()
    end = models.DateTimeField()
