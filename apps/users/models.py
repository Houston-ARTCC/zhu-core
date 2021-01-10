from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, Group
from django.core.files import File
from django.db import models
from django.utils import timezone

from zhu_core.utils import base26decode, base26encode, OverwriteStorage


def create_profile_path(instance, filename):
    return f'profile/{instance.cid}.png'


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


class Status(models.IntegerChoices):
    ACTIVE = 0
    LOA = 1
    NON_MEMBER = 2


class Certification(models.IntegerChoices):
    NONE = 0, 'No Certification'
    MINOR = 1, 'Minor Certification'
    MAJOR = 2, 'Major Certification'
    SOLO = 3, 'Solo Certification'


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


class User(AbstractBaseUser, PermissionsMixin):
    # Django Auth Fields
    objects = UserManager()
    USERNAME_FIELD = 'cid'
    is_superuser = models.BooleanField(default=False)

    # Personal Info
    cid = models.IntegerField(primary_key=True, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    profile = models.ImageField(upload_to=create_profile_path, null=True, blank=True, storage=OverwriteStorage())
    biography = models.TextField(null=True, blank=True)

    # VATSIM Details
    rating = models.CharField(max_length=3, choices=Rating.choices)
    home_facility = models.CharField(max_length=8)

    # ARTCC Details
    roles = models.ManyToManyField(Role, related_name='roles')
    status = models.IntegerField(default=Status.NON_MEMBER, choices=Status.choices)
    initials = models.CharField(max_length=2, null=True, blank=True)
    joined = models.DateTimeField(null=True, blank=True)

    # Certifications
    del_cert = models.IntegerField(default=Certification.NONE, choices=Certification.choices)
    gnd_cert = models.IntegerField(default=Certification.NONE, choices=Certification.choices)
    twr_cert = models.IntegerField(default=Certification.NONE, choices=Certification.choices)
    app_cert = models.IntegerField(default=Certification.NONE, choices=Certification.choices)
    ctr_cert = models.IntegerField(default=Certification.NONE, choices=Certification.choices)
    ocn_cert = models.IntegerField(default=Certification.NONE, choices=Certification.choices)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_member(self):
        return self.status != Status.NON_MEMBER

    @property
    def is_training_staff(self):
        return self.roles.filter(short__in=['INS', 'MTR']).exists()

    @property
    def is_staff(self):
        return self.roles.filter(short__in=['ATM', 'DATM', 'TA', 'ATA', 'FE', 'AFE', 'EC', 'AEC', 'WM', 'AWM']).exists()

    @property
    def is_senior_staff(self):
        return self.roles.filter(short__in=['ATM', 'DATM', 'TA']).exists()

    @property
    def is_admin(self):
        return self.roles.filter(short__in=['ATM', 'DATM', 'WM']).exists()

    def assign_initials(self):
        """
        Assigns operating initials to the user. If the user's initials are taken
        the letters are cycled through until an available one is found.
        """
        initials = (self.first_name[0] + self.last_name[0]).upper()
        users = User.objects.exclude(status=Status.NON_MEMBER).exclude(cid=self.cid)
        while users.filter(initials=initials).exists():
            new_initials = base26decode(initials) + 1
            initials = base26encode(new_initials if new_initials <= 675 else 0)
        self.initials = initials.rjust(2, 'A')
        self.save()

    def set_membership(self, short):
        """
        Sets the user to home, visiting, MAVP, or non-member.
        Automatically removes any other membership roles.
        Automatically assigns initials and sets join date if new member.
        """
        assert short in ['HC', 'VC', 'MC', None]
        self.roles.remove(*self.roles.filter(short__in=['HC', 'VC', 'MC']))
        if short is None:
            self.status = Status.NON_MEMBER
        else:
            if self.status == Status.NON_MEMBER:
                self.assign_initials()
                self.generate_profile()
                self.joined = timezone.now()
            if short == 'HC':
                self.home_facility = 'ZHU'
            self.status = Status.ACTIVE
            self.add_role(short)
        self.save()

    def add_role(self, short):
        self.roles.add(Role.objects.get(short=short))

    def remove_role(self, short):
        self.roles.remove(*self.roles.filter(short=short))

    def generate_profile(self):
        """
        Generates a profile picture with the user's
        initials and saves it to database.
        """
        profile = Image.new('RGB', (500, 500), color=(194, 207, 224))
        font = ImageFont.truetype('C:/Users/miker/Documents/Web Fonts/CeraPro/CeraPro-Medium.ttf', 225)

        text_layer = ImageDraw.Draw(profile)
        text_width, text_height = text_layer.textsize(self.initials, font=font)
        text_layer.text(((500 - text_width) / 2, (500 - text_height) / 2), self.initials, font=font, fill=(51, 77, 110))

        profile_io = BytesIO()
        profile.save(profile_io, 'PNG')

        self.profile = File(profile_io, name=str(self.cid) + '.png')
        self.save()

    def __str__(self):
        return self.full_name
