# Generated by Django 3.1.4 on 2020-12-14 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='home_facility',
            field=models.CharField(default='ZHU', max_length=8),
            preserve_default=False,
        ),
    ]