import os
from datetime import date

import requests
from auditlog.registry import auditlog
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.mailer.models import Email
from zhu_core.utils import OverwriteStorage, base26decode, base26encode, rating_int_to_short


def create_profile_path(instance, filename):
    return f"profile/{filename}"


def default_endorsements():
    return {
        "gnd": False,
        "hou_gnd": False,
        "iah_gnd": False,
        "twr": False,
        "hou_twr": False,
        "iah_twr": False,
        "app": False,
        "i90": False,
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
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    profile = models.ImageField(upload_to=create_profile_path, null=True, blank=True, storage=OverwriteStorage())
    biography = models.TextField(null=True, blank=True)

    # VATSIM Details
    rating = models.CharField(max_length=3, choices=Rating.choices)
    home_facility = models.CharField(max_length=16)

    # ARTCC Details
    roles = models.ManyToManyField(Role, related_name="users", blank=True)
    status = models.IntegerField(default=Status.NON_MEMBER, choices=Status.choices)
    initials = models.CharField(max_length=2, null=True, blank=True)
    joined = models.DateTimeField(null=True, blank=True)
    endorsements = models.JSONField(null=True)

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
    def is_admin(self):
        return self.roles.filter(short__in=["ATM", "DATM"]).exists() or self.is_superuser

    @property
    def visiting_eligibility(self):
        """Check if authenticated user is eligible to apply as a visiting controller."""
        # Imported in here to avoid a circular dependency
        from apps.visit.models import VisitingApplication

        vatusa_checklist = requests.get(
            f"https://api.vatusa.net/v2/user/{self.cid}/transfer/checklist",
            params={"apikey": os.getenv("VATUSA_API_TOKEN")},
        ).json()

        membership_check = not self.is_member
        pending_application_check = not VisitingApplication.objects.filter(user=self).exists()

        return {
            "has_home_facility": vatusa_checklist["data"]["hasHome"],
            "rce_completed": vatusa_checklist["data"]["needbasic"],
            "has_s3_rating": vatusa_checklist["data"]["hasRating"],
            "time_since_visit": vatusa_checklist["data"]["60days"],
            "time_since_promo": vatusa_checklist["data"]["promo"],
            "controlling_time": vatusa_checklist["data"]["50hrs"],
            "membership_check": membership_check,
            "pending_application_check": pending_application_check,
            "is_eligible": vatusa_checklist["data"]["visiting"] and membership_check and pending_application_check,
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

    def set_membership(self, short):
        """Sets the user to home, visiting, or non-member.

        Automatically removes any other membership roles.
        Automatically assigns initials and sets join date if new member.
        """
        assert short in ["HC", "VC", None]

        if self.roles.filter(short=short).exists():
            return

        if short is None:
            self.roles.clear()

            self.status = Status.NON_MEMBER
            self.endorsements = None
        else:
            self.roles.remove(*self.roles.filter(short__in=["HC", "VC"]))
            self.add_role(short)

            if self.status == Status.NON_MEMBER:
                self.status = Status.ACTIVE
                self.endorsements = default_endorsements()
                self.initials = self.get_initials()
                self.joined = timezone.now()

            if short == "HC":
                self.home_facility = "ZHU"
            elif short == "VC":
                requests.post(
                    f"https://api.vatusa.net/v2/facility/ZHU/roster/manageVisitor/{self.cid}/",
                    params={"apikey": os.getenv("VATUSA_API_TOKEN")},
                )

        self.save()

    def update_loa_status(self):
        loa_filter = self.loas.filter(start__lt=date.today(), approved=True)

        if loa_filter.filter(end__gte=date.today()).exists() and self.status == Status.ACTIVE:
            self.status = Status.LOA

            Email.objects.queue(
                to=self,
                subject="See you soon!",
                from_email="management@houston.center",
                template="loa_activated",
                context={"loa": loa_filter.first()},
            )
        elif loa_filter.filter(end__lt=date.today()).exists() and self.status == Status.LOA:
            self.status = Status.ACTIVE

            Email.objects.queue(
                to=self,
                subject="Welcome back!",
                from_email="management@houston.center",
                template="loa_deactivated",
            )

        self.save()

    def update_rating(self):
        vatsim_data = requests.get(f"https://api.vatsim.net/api/ratings/{self.cid}").json()

        if rating_short := rating_int_to_short(vatsim_data.get("rating")):
            self.rating = rating_short
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
