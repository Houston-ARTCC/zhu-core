# Generated by Django 3.1.4 on 2020-12-24 21:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('connections', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlinecontroller',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='controller_online', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='controllersession',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL),
        ),
    ]
