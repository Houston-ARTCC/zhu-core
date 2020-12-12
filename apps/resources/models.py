from django.db import models


class Category(models.TextChoices):
    VRC = 'VRC', 'VRC'
    VSTARS = 'vSTARS', 'vSTARS'
    VERAM = 'vERAM', 'vERAM'
    VATIS = 'vATIS', 'vATIS'
    SOP = 'SOP', 'SOP'
    LOA = 'LOA', 'LOA'
    MAVP = 'MAVP', 'MAVP'
    MISC = 'Misc', 'Misc'


class Resource(models.Model):
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=16, choices=Category.choices)
    path = models.FileField(upload_to='resources/')
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
