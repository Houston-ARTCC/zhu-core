# Generated by Django 3.1.7 on 2021-03-19 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0002_auto_20201224_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingsession',
            name='position',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
