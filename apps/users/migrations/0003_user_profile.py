# Generated by Django 3.1.4 on 2021-01-04 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile',
            field=models.ImageField(blank=True, null=True, upload_to='profile/'),
        ),
    ]