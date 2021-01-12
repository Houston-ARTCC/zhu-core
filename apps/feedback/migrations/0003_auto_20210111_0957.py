# Generated by Django 3.1.4 on 2021-01-11 14:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('feedback', '0002_auto_20201224_1619'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feedback',
            old_name='callsign',
            new_name='controller_callsign',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='pilot_cid',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='pilot_email',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='pilot_name',
        ),
        migrations.AddField(
            model_name='feedback',
            name='pilot',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feedback_given', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='controller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to=settings.AUTH_USER_MODEL),
        ),
    ]
