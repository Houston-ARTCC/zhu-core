# Generated by Django 3.2.4 on 2021-06-10 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20210509_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='solo_facility',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]