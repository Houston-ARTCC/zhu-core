import os

from auditlog.registry import auditlog
from django.db import models


class Category(models.TextChoices):
    POLY = "POLY", "Policy"
    PROC = "PROC", "Procedure"
    LOA = "LOA", "LOA"
    VATIS = "vATIS", "vATIS Profile"
    RVM = "RVM", "RVM List"
    REF = "REF", "Reference"


class Resource(models.Model):
    class Meta:
        verbose_name = "Resource"

    name = models.CharField(max_length=128)
    category = models.CharField(max_length=16, choices=Category.choices)
    path = models.FileField(upload_to="resources/")
    updated = models.DateTimeField(auto_now=True)

    @property
    def extension(self):
        name, extension = os.path.splitext(self.path.name)
        return extension

    @property
    def size(self):
        return os.path.getsize(self.path.path)

    def __str__(self):
        return self.name


auditlog.register(Resource, exclude_fields=["updated"])
