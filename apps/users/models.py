import os
from datetime import date, datetime, timedelta

import pytz
import requests
from auditlog.registry import auditlog
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

from apps.mailer.models import Email
from apps.visit.models import VisitingApplication
from zhu_core.utils import OverwriteStorage, base26decode, base26encode


def create_profile_path(instance, filename):
    return f"profile/{filename}"


def default_endorsements():
    return {
        "del": False,
        "gnd": False,
        "hou_gnd": False,
        "iah_gnd": False,
        "twr": False,
        "hou_twr": False,
        "iah_twr": False,
        "app": False,
        "i90_app": False,
        "zhu": False,
    }


class Rating(models.TextChoices):
    UNK = "", "Unknown"
    OBS = "OBS", "Observer"
    S1 = "S1", "Student 1"
    S2 = "S2", "Student 2"
    S3 = "S3", "Student 3"
    C1 = "C1", "Controller"
    C3 = "C3", "Senior Controller"
    I1 = "I1", "Instructor"
    I3 = "I3", "Senior Instructor"
    SUP = "SUP", "Supervisor"
    ADM = "ADM", "Administrator"


class Status(models.IntegerChoices):
    ACTIVE = 0
    LOA = 1
    NON_MEMBER = 2


class Certification(models.IntegerChoices):
    NONE = 0, "No Certification"
    MINOR = 1, "Minor Certification"
    MAJOR = 2, "Major Certification"
    SOLO = 3, "Solo Certification"


class Role(models.Model):
    long = models.CharField(max_length=32)
    short = models.CharField(max_length=8)

    def __str__(self):
        return self.long


class UserManager(BaseUserManager):
    def create_user(self, cid, email, first_name, last_name, rating, save=True, **extra_fields):
        user = self.model(
            cid=int(cid),
            email=self.normalize_email(email),
            first_name=first_name.capitalize(),
            last_name=last_name.capitalize(),
            rating=rating,
            **extra_fields,
        )
        user.set_unusable_password()

        if save:
            user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = "User"

    # Django Auth Fields
    objects = UserManager()
    USERNAME_FIELD = "cid"
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
    roles = models.ManyToManyField(Role, related_name="users", blank=True)
    status = models.IntegerField(default=Status.NON_MEMBER, choices=Status.choices)
    initials = models.CharField(max_length=2, null=True, blank=True)
    joined = models.DateTimeField(null=True, blank=True)
    endorsements = models.JSONField(default=default_endorsements)

    # Flags
    prevent_event_signup = models.BooleanField(default=False)
    cic_endorsed = models.BooleanField(default=False)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def membership(self):
        return self.roles.filter(short__in=["HC", "VC"]).first().short

    @property
    def is_member(self):
        return self.status != Status.NON_MEMBER

    @property
    def is_training_staff(self):
        return self.roles.filter(short__in=["INS", "MTR"]).exists() or self.is_superuser

    @property
    def is_staff(self):
        return (
            self.roles.filter(short__in=["ATM", "DATM", "TA", "ATA", "FE", "AFE", "EC", "AEC", "WM", "AWM"]).exists()
            or self.is_superuser
        )

    @property
    def is_senior_staff(self):
        return self.roles.filter(short__in=["ATM", "DATM", "TA", "FE"]).exists() or self.is_superuser

    @property
    def is_admin(self):
        return self.roles.filter(short__in=["ATM", "DATM"]).exists() or self.is_superuser

    @property
    def training_staff_role(self):
        return self.roles.filter(short__in=["INS", "MTR"]).first()

    @property
    def staff_role(self):
        return self.roles.filter(short__in=["ATM", "DATM", "TA", "ATA", "FE", "AFE", "EC", "AEC", "WM", "AWM"]).first()

    @property
    def visiting_eligibility(self):
        """Check if authenticated user is eligible to apply as a visiting controller."""
        rating_check = self.rating not in [Rating.UNK, Rating.OBS, Rating.S1]

        rating_time = requests.get(f"https://api.vatsim.net/api/ratings/{self.cid}/").json()
        if rating_time.get("lastratingchange") is not None:
            last_rating_change = pytz.utc.localize(
                datetime.strptime(rating_time.get("lastratingchange"), "%Y-%m-%dT%H:%M:%S")
            )
            rating_time_check = timezone.now() - last_rating_change >= timedelta(days=90)
        else:
            rating_time_check = True

        rating_hours = requests.get(f"https://api.vatsim.net/api/ratings/{self.cid}/rating_times/").json()
        if rating_hours.get(self.rating.lower()) is not None:
            rating_hours_check = rating_hours.get(self.rating.lower()) > 50
        else:
            rating_hours_check = False

        membership_check = not self.is_member

        pending_application_check = not VisitingApplication.objects.filter(user=self).exists()

        return {
            "rating_check": rating_check,
            "rating_time_check": rating_time_check,
            "rating_hours_check": rating_hours_check,
            "membership_check": membership_check,
            "pending_application_check": pending_application_check,
            "is_eligible": rating_check
            and rating_time_check
            and rating_hours_check
            and membership_check
            and pending_application_check,
        }

    def get_initials(self):
        """Assigns operating initials to user.

        If the user's initials are taken, the letters are cycled through until an available one is found.
        """
        initials = (self.first_name[0] + self.last_name[0]).upper()

        users = User.objects.exclude(status=Status.NON_MEMBER).exclude(cid=self.cid)
        while users.filter(initials=initials).exists():
            new_initials = base26decode(initials) + 1
            initials = base26encode(new_initials if new_initials <= 675 else 0)

        return initials.rjust(2, "A")

    def set_membership(self, short, override=True):
        """Sets the user to home, visiting, or non-member.

        Automatically removes any other membership roles.
        Automatically assigns initials and sets join date if new member.
        """
        assert short in ["HC", "VC", None]

        if self.roles.filter(short=short).exists():
            return

        if short is None:
            self.status = Status.NON_MEMBER
        else:
            if self.status == Status.NON_MEMBER:
                if override:
                    self.initials = self.get_initials()
                    self.joined = timezone.now()

                if not settings.DEV_ENV:
                    self.send_welcome_mail()

            if short == "HC":
                self.home_facility = "ZHU"

            if short == "VC":
                requests.post(
                    f"https://api.vatusa.net/v2/facility/ZHU/roster/manageVisitor/{self.cid}/",
                    params={"apikey": os.getenv("VATUSA_API_TOKEN")},
                )

            self.status = Status.ACTIVE

        self.save()

        self.roles.remove(*self.roles.filter(short__in=["HC", "VC"]))
        self.add_role(short)

    def send_welcome_mail(self):
        context = {
            "user": self,
            "staff": {
                "atm": User.objects.filter(roles__short="ATM").first(),
                "datm": User.objects.filter(roles__short="DATM").first(),
                "ta": User.objects.filter(roles__short="TA").first(),
            },
        }
        Email(
            subject="Welcome to Houston ARTCC!",
            html_body=render_to_string("welcome_email.html", context=context),
            text_body=render_to_string("welcome_email.txt", context=context),
            to_email=self.email,
        ).save()

    def update_loa_status(self):
        loa_filter = self.loas.filter(start__lt=date.today(), end__gt=date.today(), approved=True)

        if loa_filter.exists() and self.status == Status.ACTIVE:
            self.status = Status.LOA

            context = {"user": self, "loa": loa_filter.first()}
            Email(
                subject="You have been placed on a leave of absence",
                html_body=render_to_string("loa_activated.html", context=context),
                text_body=render_to_string("loa_activated.txt", context=context),
                to_email=self.email,
            ).save()
        elif self.status == Status.LOA:
            self.status = Status.ACTIVE

            context = {"user": self}
            Email(
                subject="Welcome back to Houston!",
                html_body=render_to_string("loa_deactivated.html", context=context),
                text_body=render_to_string("loa_deactivated.txt", context=context),
                to_email=self.email,
            ).save()

        self.save()

    def add_role(self, short):
        self.roles.add(*Role.objects.filter(short=short))

    def remove_role(self, short):
        self.roles.remove(*self.roles.filter(short=short))

    def __str__(self):
        return self.full_name


auditlog.register(
    User,
    include_fields=[
        "cid",
        "email",
        "first_name",
        "last_name",
        "biography",
        "rating",
        "home_facility",
        "roles",
        "status",
        "initials",
        "joined",
        "prevent_event_signup",
        "cic_endorsed",
        "endorsements",
    ],
)
