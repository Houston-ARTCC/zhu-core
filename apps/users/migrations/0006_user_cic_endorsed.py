# Generated by Django 3.1.4 on 2021-02-15 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210215_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cic_endorsed',
            field=models.BooleanField(default=False),
        ),
    ]