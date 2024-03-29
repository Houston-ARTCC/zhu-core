# Generated by Django 5.0.3 on 2024-03-08 05:37

import django.db.models.deletion
from django.db import migrations, models


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
                ('host', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True, null=True)),
                ('hidden', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Event',
            },
        ),
        migrations.CreateModel(
            name='PositionPreset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('positions', models.JSONField(default=list)),
            ],
            options={
                'verbose_name': 'Position preset',
            },
        ),
        migrations.CreateModel(
            name='PositionShift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Position shift',
            },
        ),
        migrations.CreateModel(
            name='ShiftRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Shift request',
            },
        ),
        migrations.CreateModel(
            name='SupportRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('banner', models.URLField(blank=True, null=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('host', models.CharField(max_length=32)),
                ('requested_fields', models.JSONField(blank=True, default=list)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Event support request',
            },
        ),
        migrations.CreateModel(
            name='EventPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('callsign', models.CharField(max_length=16)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='events.event')),
            ],
            options={
                'verbose_name': 'Event position',
            },
        ),
        migrations.CreateModel(
            name='EventScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField()),
                ('notes', models.JSONField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='events.event')),
            ],
            options={
                'verbose_name': 'Event score',
            },
        ),
    ]
