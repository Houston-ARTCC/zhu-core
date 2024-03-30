from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Case, Exists, ExpressionWrapper, F, Func, OuterRef, Q, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce
from django.db.models.lookups import GreaterThanOrEqual
from django.db.models.query import QuerySet
from django.utils import timezone

from apps.training.models import Status as TrainingStatus
from apps.training.models import TrainingSession
from apps.users.models import Role, User
from apps.users.models import Status as UserStatus

from .models import ControllerSession


def aggregate_quarterly_hours(queryset: QuerySet[User]):
    """Performs several aggregates on each active user's controlling sessions."""
    now = timezone.now()
    quarter = (now.month - 1) // 3  # zero indexed (e.g. 0: Jan - Mar, 1: Apr - Jun, etc.)

    month_1_start = date(now.year, quarter * 3 + 1, 1)
    month_1_end = month_1_start + relativedelta(day=31)

    month_2_start = month_1_start + relativedelta(months=1)
    month_2_end = month_2_start + relativedelta(day=31)

    month_3_start = month_2_start + relativedelta(months=1)
    month_3_end = month_3_start + relativedelta(day=31)

    return queryset.annotate(
        month_1_hours=Sum(
            "sessions__duration",
            filter=Q(sessions__start__date__range=[month_1_start, month_1_end]),
        ),
        month_2_hours=Sum(
            "sessions__duration",
            filter=Q(sessions__start__date__range=[month_2_start, month_2_end]),
        ),
        month_3_hours=Sum(
            "sessions__duration",
            filter=Q(sessions__start__date__range=[month_3_start, month_3_end]),
        ),
        quarter_hours=Sum(
            "sessions__duration",
            filter=Q(sessions__start__date__range=[month_1_start, month_3_end]),
        ),
        quarter_quota=Case(
            # Controllers with a staff role are expected to complete at least 6 controlling hours as per P001 [3-2]
            When(
                Exists(
                    Role.objects.filter(
                        users__cid=OuterRef("cid"),
                        short__in=["ATM", "DATM", "TA", "ATA", "FE", "AFE", "EC", "AEC", "WM", "AWM"],
                    )
                ),
                then=Value(timedelta(hours=6)),
            ),
            # All other controllers are expected to complete at least 3 controlling hours as per P001 [3-3-1]
            default=timedelta(hours=3),
        ),
        quarter_active=Coalesce(
            GreaterThanOrEqual(F("quarter_hours"), F("quarter_quota")),
            Value(False),
        ),
        hou_gnd_hours=Sum(
            "sessions__duration",
            filter=(
                Q(sessions__callsign__iregex=r"^HOU(_\w+)?_GND$")
                & Q(sessions__start__date__range=[month_1_start, month_3_end])
            ),
        ),
        hou_twr_hours=Sum(
            "sessions__duration",
            filter=(
                Q(sessions__callsign__iregex=r"^HOU(_\w+)?_TWR$")
                & Q(sessions__start__date__range=[month_1_start, month_3_end])
            ),
        ),
        hou_hours=Case(
            When(endorsements__hou_twr=True, then=F("hou_twr_hours")),
            When(endorsements__hou_gnd=True, then=F("hou_gnd_hours")),
        ),
        iah_gnd_hours=Sum(
            "sessions__duration",
            filter=(
                Q(sessions__callsign__iregex=r"^IAH(_\w+)?_GND$")
                & Q(sessions__start__date__range=[month_1_start, month_3_end])
            ),
        ),
        iah_twr_hours=Sum(
            "sessions__duration",
            filter=(
                Q(sessions__callsign__iregex=r"^IAH(_\w+)?_TWR$")
                & Q(sessions__start__date__range=[month_1_start, month_3_end])
            ),
        ),
        iah_hours=Case(
            When(endorsements__iah_twr=True, then=F("iah_twr_hours")),
            When(endorsements__iah_gnd=True, then=F("iah_gnd_hours")),
        ),
        i90_hours=Sum(
            "sessions__duration",
            filter=(
                Q(sessions__callsign__iregex=r"^I90(_\w+)?_APP$")
                & Q(sessions__start__date__range=[month_1_start, month_3_end])
            ),
        ),
        zhu_hours=Sum(
            "sessions__duration",
            filter=(
                Q(sessions__callsign__iregex=r"^HOU(_\w+)?_CTR$")
                & Q(sessions__start__date__range=[month_1_start, month_3_end])
            ),
        ),
        t1_hours=Case(
            When(endorsements__zhu=True, then=F("zhu_hours") + F("i90_hours")),
            When(endorsements__i90=True, then=F("i90_hours")),
            When(
                (Q(endorsements__iah_twr=True) | Q(endorsements__iah_gnd=True))
                & (Q(endorsements__hou_twr=True) | Q(endorsements__hou_gnd=True)),
                then=Coalesce(
                    F("iah_hours") + F("hou_hours"),
                    F("iah_hours"),
                    F("hou_hours"),
                ),
            ),
            When(endorsements__iah_twr=True, then=F("iah_twr_hours")),
            When(endorsements__iah_gnd=True, then=F("iah_gnd_hours")),
            When(endorsements__hou_twr=True, then=F("hou_twr_hours")),
            When(endorsements__hou_gnd=True, then=F("hou_gnd_hours")),
        ),
        t1_active=ExpressionWrapper(
            Coalesce(
                GreaterThanOrEqual(F("t1_hours"), timedelta(hours=3)),
                False,
            )
            & Case(
                When(
                    Q(endorsements__zhu=False)
                    & Q(endorsements__i90=False)
                    & (Q(endorsements__iah_twr=True) | Q(endorsements__iah_gnd=True))
                    & (Q(endorsements__hou_twr=True) | Q(endorsements__hou_gnd=True)),
                    then=ExpressionWrapper(
                        GreaterThanOrEqual(F("iah_hours"), timedelta(hours=1))
                        & GreaterThanOrEqual(F("hou_hours"), timedelta(hours=1)),
                        output_field=models.BooleanField(),
                    ),
                ),
                default=True,
            ),
            output_field=models.BooleanField(),
        ),
        training_hours=Subquery(
            TrainingSession.objects.filter(
                student_id=OuterRef("cid"),
                status=TrainingStatus.COMPLETED,
                start__date__range=[month_1_start, month_3_end],
            )
            .annotate(duration=F("end") - F("start"))
            .values("student")
            .annotate(total=Sum("duration"))
            .values("total"),
            output_field=models.DurationField(),
        ),
        # Controllers with an OBS rating are expected to complete at least three training hours as per P001 [3-3-2]
        training_active=Coalesce(
            GreaterThanOrEqual(F("training_hours"), timedelta(hours=3)),
            False,
        ),
    )


def get_annotated_statistics(*, admin: bool = False):
    values = [
        "cid",
        "first_name",
        "last_name",
        "initials",
        "rating",
        "month_1_hours",
        "month_2_hours",
        "month_3_hours",
        "quarter_hours",
        "quarter_active",
    ]

    if admin:
        values.extend(
            [
                "hou_gnd_hours",
                "hou_twr_hours",
                "iah_gnd_hours",
                "iah_twr_hours",
                "i90_hours",
                "zhu_hours",
                "t1_hours",
                "t1_active",
                "training_hours",
                "training_active",
            ]
        )

    return aggregate_quarterly_hours().values(*values)


def get_top_controllers():
    """
    Returns query set of active users annotated with controlling
    hour sums for the current month (hours) sorted by most
    controlling hours (controllers with no hours are not included).
    """
    now = timezone.now()

    month_start = date(now.year, now.month, 1)
    month_end = month_start + relativedelta(day=31)

    return (
        User.objects.exclude(status=UserStatus.NON_MEMBER)
        .annotate(
            hours=Sum(
                "sessions__duration",
                filter=Q(sessions__start__date__range=[month_start, month_end]),
            )
        )
        .exclude(hours__isnull=True)
        .order_by("-hours")
    )


def get_top_positions():
    """
    Returns query set of normalized position name (no infix) annotated with controlling
    hour sums for the current month (hours) sorted by most controlling hours.
    """
    now = timezone.now()

    month_start = date(now.year, now.month, 1)
    month_end = month_start + relativedelta(day=31)

    return (
        ControllerSession.objects.filter(start__date__range=[month_start, month_end])
        .annotate(
            position=Func(
                F("callsign"),
                Value(r"_\w+_"),
                Value("_"),
                function="REGEXP_REPLACE",
            )
        )
        .values("position")
        .annotate(hours=Sum("duration"))
        .order_by("-hours")
    )


def get_daily_statistics(year, user=None):
    """
    Returns a query dictionary of every day of the given year
    annotated with the controlling hours for that day.
    """
    sessions = ControllerSession.objects.filter(start__year=year)
    if user:
        sessions = sessions.filter(user=user)
    return sessions.extra({"date": "date(start)"}).values("date").annotate(value=Sum("duration"))
