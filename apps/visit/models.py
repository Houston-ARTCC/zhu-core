from django.db import models

from ..users.models import User


class VisitingApplication(models.Model):
    class Meta:
        verbose_name_plural = 'Vistiting Applications'

    user = models.OneToOneField(User, models.CASCADE, related_name='visiting_application', unique=True)
    reason = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.full_name} @ {self.submitted.strftime("%b %d, %Y %H%Mz")}'
