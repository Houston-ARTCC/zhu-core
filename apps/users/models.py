import os
import pytz
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta, datetime
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, Group
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

from zhu_core.utils import base26decode, base26encode, OverwriteStorage


def create_profile_path(instance, filename):
    return f'profile/{instance.cid}.png'


class Rating(models.TextChoices):
    UNK = '', 'Unknown'
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
    class Meta:
        verbose_name = 'User'

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
    roles = models.ManyToManyField(Role, related_name='roles', blank=True)
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

    # Flags
    prevent_event_signup = models.BooleanField(default=False)
    cic_endorsed = models.BooleanField(default=False)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def membership(self):
        return self.roles.filter(short__in=['HC', 'VC', 'MC']).first().short

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
        return self.roles.filter(short__in=['ATM', 'DATM']).exists()

    @property
    def training_staff_role(self):
        return self.roles.filter(short__in=['INS', 'MTR']).first()

    @property
    def staff_role(self):
        return self.roles.filter(short__in=['ATM', 'DATM', 'TA', 'ATA', 'FE', 'AFE', 'EC', 'AEC', 'WM', 'AWM']).first()

    @property
    def activity_requirement(self):
        if self.del_cert == Certification.NONE:
            return timedelta(hours=0)
        elif self.is_staff:
            return timedelta(hours=5)
        elif self.membership == 'HC':
            return timedelta(hours=2)
        else:
            return timedelta(hours=1)

    @property
    def visiting_eligibility(self):
        """
        Check if authenticated user is eligible to apply as a visiting controller.
        """
        from ..visit.models import VisitingApplication

        rating_check = self.rating not in [Rating.UNK, Rating.OBS, Rating.S1]

        rating_time = requests.get('https://api.vatsim.net/api/ratings/' + str(self.cid) + '/').json()
        last_rating_change = pytz.utc.localize(
            datetime.strptime(rating_time.get('lastratingchange'), '%Y-%m-%dT%H:%M:%S')
        )
        rating_time_check = timezone.now() - last_rating_change >= timedelta(days=90)

        rating_hours = requests.get('https://api.vatsim.net/api/ratings/' + str(self.cid) + '/rating_times/').json()
        rating_hours_check = rating_hours.get(self.rating.lower()) > 50

        membership_check = not self.is_member

        pending_application_check = not VisitingApplication.objects.filter(user=self).exists()

        return {
            'rating_check': rating_check,
            'rating_time_check': rating_time_check,
            'rating_hours_check': rating_hours_check,
            'membership_check': membership_check,
            'pending_application_check': pending_application_check,
            'is_eligible': rating_check and rating_time_check and rating_hours_check and
                           membership_check and pending_application_check,
        }

    @property
    def event_score(self):
        return self.get_event_scores().get('event_score')

    def get_event_scores(self):
        """
        Calculates an averaged percentage to represent the user's
        actual vs anticipated participation in all events.
        Also factors in feedback for the event.
        """
        from apps.events.models import Event
        from apps.events.serializers import BasicEventSerializer
        from apps.feedback.models import Feedback
        from apps.feedback.serializers import EventFeedbackSerializer

        individual_scores = [
            {
                'event': None,
                'score': 100 if self.membership == 'HC' else 85,
            },
        ]

        events = Event.objects.filter(end__lt=timezone.now(), positions__shifts__user=self).distinct()
        for event in events:
            # Get target controlling duration for event
            shifts = self.event_shifts.filter(position__event=event)
            target_duration = round(sum([(shift.end - shift.start).total_seconds() for shift in shifts]))

            # Get actual controlling duration for event
            sessions = [session for session in self.controller_sessions.filter(
                start__gt=event.start - timedelta(hours=1),
                start__lt=event.end
            )]
            actual_duration = round(sum([session.duration.total_seconds() for session in sessions]))

            # Calculate feedback adjustment
            adjustment = 1
            event_feedback = Feedback.objects.filter(controller=self, event=event, approved=True)
            for feedback in event_feedback:
                adjustment += (feedback.rating - 3) * 0.05

            # Calculate final score for event and append to list
            individual_scores.append({
                'event': BasicEventSerializer(event).data,
                'score': round(actual_duration * 100 * adjustment / target_duration),
                'target_duration': target_duration,
                'actual_duration': actual_duration,
                'feedback': EventFeedbackSerializer(event_feedback, many=True).data,
            })

        scores = list(map(lambda x: x.get('score'), individual_scores))

        return {
            'event_score': round(sum(scores) / len(scores)),
            'scores': individual_scores,
        }

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

    def generate_profile(self):
        """
        Generates a profile picture with the user's
        initials and saves it to database.
        """
        profile = Image.new('RGB', (500, 500), color=(194, 207, 224))
        font = ImageFont.truetype(str(settings.STATIC_ROOT) + '/fonts/CeraPro-Medium.ttf', 225)

        text_layer = ImageDraw.Draw(profile)
        text_width, text_height = text_layer.textsize(self.initials, font=font)
        text_layer.text(((500 - text_width) / 2, (500 - text_height) / 2), self.initials, font=font, fill=(51, 77, 110))

        profile_io = BytesIO()
        profile.save(profile_io, 'PNG')

        self.profile = File(profile_io, name=str(self.cid) + '.png')
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

                if os.getenv('DEV_ENV') == 'False':
                    self.send_welcome_mail()

            if short == 'HC':
                self.home_facility = 'ZHU'

            self.status = Status.ACTIVE
            self.add_role(short)
        self.save()

    def send_welcome_mail(self):
        context = {'user': self}
        EmailMultiAlternatives(
            subject=f'Welcome to {os.getenv("FACILITY_NAME")}!',
            to=[self.email],
            from_email=os.getenv('EMAIL_ADDRESS'),
            body=render_to_string('welcome_email.txt', context=context),
            alternatives=[(render_to_string('welcome_email.html', context=context), 'text/html')],
        ).send()

    def add_role(self, short):
        self.roles.add(Role.objects.get(short=short))

    def remove_role(self, short):
        self.roles.remove(*self.roles.filter(short=short))

    def __str__(self):
        return self.full_name


auditlog.register(User, exclude_fields=['last_login'])
