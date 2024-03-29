# Generated by Django 5.0.3 on 2024-03-08 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LOA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('remarks', models.TextField()),
                ('approved', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'LOA',
            },
        ),
    ]
