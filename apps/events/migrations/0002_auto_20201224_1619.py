# Generated by Django 3.1.4 on 2020-12-24 21:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='eventpositionrequest',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='events.eventposition'),
        ),
        migrations.AddField(
            model_name='eventpositionrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_position_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='eventposition',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='events.event'),
        ),
        migrations.AddField(
            model_name='eventposition',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_positions', to=settings.AUTH_USER_MODEL),
        ),
    ]
