from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, cid, email, first_name, last_name, **extra_fields):
        user = self.model(
            cid=int(cid),
            email=self.normalize_email(email),
            first_name=first_name.capitalize(),
            last_name=last_name.capitalize(),
            **extra_fields,
        )
        user.set_unusable_password()
        user.save()

        return user

    def create_superuser(self, cid, email, first_name, last_name, password, **extra_fields):
        user = self.create_user(cid, email, first_name, last_name, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Django Auth Fields
    objects = UserManager()
    USERNAME_FIELD = 'cid'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Personal Info
    cid = models.IntegerField(primary_key=True, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
