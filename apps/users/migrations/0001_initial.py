# Generated by Django 3.1.4 on 2020-12-24 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('long', models.CharField(max_length=32)),
                ('short', models.CharField(max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('cid', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('first_name', models.CharField(max_length=16)),
                ('last_name', models.CharField(max_length=16)),
                ('rating', models.CharField(choices=[('OBS', 'Observer'), ('S1', 'Student 1'), ('S2', 'Student 2'), ('S3', 'Student 3'), ('C1', 'Controller'), ('C3', 'Senior Controller'), ('I1', 'Instructor'), ('I3', 'Senior Instructor'), ('SUP', 'Supervisor'), ('ADM', 'Administrator')], max_length=3)),
                ('home_facility', models.CharField(max_length=8)),
                ('status', models.IntegerField(choices=[(0, 'Active'), (1, 'Loa'), (2, 'Non Member')], default=2)),
                ('initials', models.CharField(blank=True, max_length=2, null=True)),
                ('del_cert', models.IntegerField(choices=[(0, 'No Certification'), (1, 'Minor Certification'), (2, 'Major Certification'), (3, 'Solo Certification')], default=0)),
                ('gnd_cert', models.IntegerField(choices=[(0, 'No Certification'), (1, 'Minor Certification'), (2, 'Major Certification'), (3, 'Solo Certification')], default=0)),
                ('twr_cert', models.IntegerField(choices=[(0, 'No Certification'), (1, 'Minor Certification'), (2, 'Major Certification'), (3, 'Solo Certification')], default=0)),
                ('app_cert', models.IntegerField(choices=[(0, 'No Certification'), (1, 'Minor Certification'), (2, 'Major Certification'), (3, 'Solo Certification')], default=0)),
                ('ctr_cert', models.IntegerField(choices=[(0, 'No Certification'), (1, 'Minor Certification'), (2, 'Major Certification'), (3, 'Solo Certification')], default=0)),
                ('ocn_cert', models.IntegerField(choices=[(0, 'No Certification'), (1, 'Minor Certification'), (2, 'Major Certification'), (3, 'Solo Certification')], default=0)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('roles', models.ManyToManyField(related_name='roles', to='users.Role')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
