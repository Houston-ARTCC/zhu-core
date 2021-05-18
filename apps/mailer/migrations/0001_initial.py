# Generated by Django 3.1.7 on 2021-05-13 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('html_body', models.TextField()),
                ('text_body', models.TextField()),
                ('from_email', models.EmailField(max_length=254, null=True)),
                ('to_email', models.TextField()),
                ('cc_email', models.TextField(null=True)),
                ('bcc_email', models.TextField(null=True)),
                ('status', models.IntegerField(choices=[(0, 'Pending'), (1, 'Failed'), (2, 'Sent')], default=0)),
                ('last_attempt', models.DateTimeField(null=True)),
            ],
        ),
    ]