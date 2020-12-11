from django.db import models


CATEGORIES = (
    ('VRC', 'VRC'),
    ('vSTARS', 'vSTARS'),
    ('vERAM', 'vERAM'),
    ('vATIS', 'vATIS'),
    ('SOP', 'SOP'),
    ('LOA', 'LOA'),
    ('MAVP', 'MAVP'),
    ('Misc', 'Misc')
)


class Resource(models.Model):
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=16, choices=CATEGORIES)
    path = models.FileField(upload_to='resources/')
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
