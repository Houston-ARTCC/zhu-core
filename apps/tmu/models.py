from django.db import models


class ATIS(models.Model):
    class Meta:
        verbose_name_plural = 'ATIS'

    facility = models.CharField(max_length=4)
    config_profile = models.CharField(max_length=16)
    atis_letter = models.CharField(max_length=1)
    airport_conditions = models.TextField()
    notams = models.TextField()
    updated = models.DateTimeField(auto_now=True)


class TMUNotice(models.Model):
    class Meta:
        verbose_name_plural = 'TMU Notices'

    info = models.TextField()
    time_issued = models.DateTimeField(auto_now_add=True)
    time_expires = models.DateTimeField()


class METAR(models.Model):
    class Meta:
        verbose_name_plural = 'METARs'

    station = models.CharField(max_length=4)
    raw = models.TextField()
    flight_rules = models.CharField(max_length=4)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f'{self.station} @ {self.timestamp}'
