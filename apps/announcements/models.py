from django.db import models

from ..users.models import User


class Announcement(models.Model):
    title = models.CharField(max_length=128)
    body = models.TextField()
    author = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='announcements')
    posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
