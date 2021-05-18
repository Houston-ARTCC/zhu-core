# Generated by Django 3.1.7 on 2021-05-13 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='error',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='email',
            name='bcc_email',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='email',
            name='cc_email',
            field=models.CharField(max_length=255, null=True),
        ),
    ]