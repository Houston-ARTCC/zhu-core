# Generated by Django 3.2.4 on 2024-01-06 00:30

import apps.users.models
from apps.users.models import Certification
from django.db import migrations, models


def migrate_certifications(apps, schema_editor):
    User = apps.get_model("users", "User")

    for user in User.objects.all():
        user.endorsements = {
            "del": user.del_cert in [Certification.MINOR, Certification.MAJOR],
            "gnd": user.gnd_cert in [Certification.MINOR, Certification.MAJOR],
            "hou_gnd": user.gnd_cert in [Certification.MINOR, Certification.MAJOR],
            "iah_gnd": user.gnd_cert == Certification.MAJOR,
            "twr": user.twr_cert in [Certification.MINOR, Certification.MAJOR],
            "hou_twr": user.twr_cert in [Certification.MINOR, Certification.MAJOR],
            "iah_twr": user.twr_cert == Certification.MAJOR,
            "app": user.app_cert in [Certification.MINOR, Certification.MAJOR],
            "i90_app": user.app_cert == Certification.MAJOR,
            "zhu": user.ctr_cert in [Certification.MINOR, Certification.MAJOR],
        }

        if user.del_cert == Certification.SOLO:
            user.endorsements["del"] = user.solo_facility
        if user.gnd_cert == Certification.SOLO:
            user.endorsements["gnd"] = user.solo_facility
        if user.twr_cert == Certification.SOLO:
            user.endorsements["twr"] = user.solo_facility
        if user.app_cert == Certification.SOLO:
            user.endorsements["app"] = user.solo_facility

        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20231017_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='endorsements',
            field=models.JSONField(default=apps.users.models.default_endorsements),
        ),
        migrations.RunPython(migrate_certifications),
        migrations.RemoveField(
            model_name='user',
            name='app_cert',
        ),
        migrations.RemoveField(
            model_name='user',
            name='ctr_cert',
        ),
        migrations.RemoveField(
            model_name='user',
            name='del_cert',
        ),
        migrations.RemoveField(
            model_name='user',
            name='gnd_cert',
        ),
        migrations.RemoveField(
            model_name='user',
            name='solo_facility',
        ),
        migrations.RemoveField(
            model_name='user',
            name='twr_cert',
        ),
    ]