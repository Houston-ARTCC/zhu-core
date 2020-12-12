from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, Group
from django.db import models


class Rating(models.TextChoices):
    OBS = 'OBS', 'Observer'
    S1 = 'S1', 'Student 1'
    S2 = 'S2', 'Student 2'
    S3 = 'S3', 'Student 3'
    C1 = 'C1', 'Controller'
    C3 = 'C3', 'Senior Controller'
    I1 = 'I1', 'Instructor'
    I3 = 'I3', 'Senior Instructor'
    SUP = 'SUP', 'Supervisor'
    ADM = 'ADM', 'Administrator'


class Role(models.Model):
    long = models.CharField(max_length=32)
    short = models.CharField(max_length=8)

    def __str__(self):
        return self.long


class UserManager(BaseUserManager):
    def create_user(self, cid, email, first_name, last_name, rating, **extra_fields):
        user = self.model(
            cid=int(cid),
            email=self.normalize_email(email),
            first_name=first_name.capitalize(),
            last_name=last_name.capitalize(),
            rating=rating,
            **extra_fields,
        )
        user.set_unusable_password()
        user.save()

        return user

    def create_superuser(self, cid, email, first_name, last_name, password, rating, **extra_fields):
        user = self.create_user(cid, email, first_name, last_name, rating, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Django Auth Fields
    objects = UserManager()
    USERNAME_FIELD = 'cid'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'rating']
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Personal Info
    cid = models.IntegerField(primary_key=True, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    rating = models.CharField(max_length=3, choices=Rating.choices)
    roles = models.ManyToManyField(Role, related_name='roles')

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
