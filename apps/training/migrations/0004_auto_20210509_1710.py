# Generated by Django 3.1.7 on 2021-05-09 21:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0003_auto_20210319_1800'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trainingrequest',
            options={'verbose_name': 'Training request'},
        ),
        migrations.AlterModelOptions(
            name='trainingsession',
            options={'verbose_name': 'Training session'},
        ),
    ]