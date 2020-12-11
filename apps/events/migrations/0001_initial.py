# Generated by Django 3.1.4 on 2020-12-11 05:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('banner', models.URLField(blank=True, null=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('host', models.CharField(max_length=32)),
                ('description', models.TextField(blank=True, null=True)),
                ('hidden', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='EventPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('callsign', models.CharField(max_length=16)),
            ],
            options={
                'verbose_name_plural': 'Event Positions',
            },
        ),
        migrations.CreateModel(
            name='EventPositionRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='events.eventposition')),
            ],
            options={
                'verbose_name_plural': 'Event Position Requests',
            },
        ),
    ]
