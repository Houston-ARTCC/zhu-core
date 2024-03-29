# Generated by Django 5.0.3 on 2024-03-08 05:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='eventscore',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_scores', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='positionshift',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shifts', to='events.eventposition'),
        ),
        migrations.AddField(
            model_name='positionshift',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_shifts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shiftrequest',
            name='shift',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='events.positionshift'),
        ),
        migrations.AddField(
            model_name='shiftrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='supportrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]
