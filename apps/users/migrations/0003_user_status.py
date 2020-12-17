# Generated by Django 3.1.4 on 2020-12-12 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_user_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='status',
            field=models.IntegerField(choices=[(0, 'Active'), (1, 'Loa'), (2, 'Inactive')], default=0),
        ),
    ]