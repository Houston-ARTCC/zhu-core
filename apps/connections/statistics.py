from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import (
    Case,
    Exists,
    ExpressionWrapper,
    F,
    OuterRef,
    Q,
    Subquery,
    Sum,
    When, Value,
)
from django.utils import timezone

from apps.training.models import Status as TrainingStatus
from apps.training.models import TrainingSession
from apps.users.models import Rating, Role, User
from apps.users.models import Status as UserStatus

from .models import ControllerSession


def aggregate_quarterly_hours():
    """Performs several aggregates on each active user's controlling sessions.

    - `month_1_hours`, `month_2_hours`, and `month_3_hours` are the collective hours spent controlling any
      ZHU position within the first, second, and third months of the current quarter, respectively.

    - `quarter_hours` is the sum of all three month-wise aggregates.
    - `quarter_active` is a boolean flag indicating whether a user has met currency requirements.
      This requirement is 6 hours for staff members and 3 hours for everybody else.

    """
    now = timezone.now().replace(year=2023)  # TODO: Remove year override used for testing
    quarter = (now.month - 1) // 3  # zero indexed (e.g. 0: Jan - Mar, 1: Apr - Jun, etc.)

    month_1_start = date(now.year, quarter * 3 + 1, 1)
    month_1_end = month_1_start + relativedelta(day=31)

    month_2_start = month_1_start + relativedelta(months=1)
    month_2_end = month_2_start + relativedelta(day=31)

    month_3_start = month_2_start + relativedelta(months=1)
    month_3_end = month_3_start + relativedelta(day=31)

    return (
        User.objects.exclude(status=UserStatus.NON_MEMBER)
        .values("cid")  # Forces the aggregate functions to "GROUP BY" cid only
        .annotate(
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
            quarter_active=Case(
                # Controllers with a staff role are expected to complete at least 6 controlling hours as per P001 [3-2]
                When(
                    Exists(
                        Role.objects.filter(
                            users__cid=OuterRef("cid"),
                            short__in=["ATM", "DATM", "TA", "ATA", "FE", "AFE", "EC", "AEC", "WM", "AWM"],
                        )
                    ),
                    then=ExpressionWrapper(
                        Q(quarter_hours__gte=timedelta(hours=6)),
                        output_field=models.BooleanField(),
                    ),
                ),
                # All other controllers are expected to complete at least 3 controlling hours as per P001 [3-3-1]
                default=ExpressionWrapper(
                    Q(quarter_hours__gte=timedelta(hours=3)),
                    output_field=models.BooleanField(),
                ),
                output_field=models.BooleanField(),
            ),
            quarter_hou_t1_hours=Case(
                When(
                    endorsements__hou_twr=True,
                    then=Sum(
                        "sessions__duration",
                        filter=(
                            Q(sessions__callsign__iregex=r"^HOU(_\w+)?_TWR$")
                            & Q(sessions__start__date__range=[month_1_start, month_3_end])
                        ),
                    ),
                ),
                When(
                    endorsements__hou_gnd=True,
                    then=Sum(
                        "sessions__duration",
                        filter=(
                            Q(sessions__callsign__iregex=r"^HOU(_\w+)?_GND$")
                            & Q(sessions__start__date__range=[month_1_start, month_3_end])
                        ),
                    ),
                ),
            ),
            quarter_iah_t1_hours=Case(
                When(
                    endorsements__iah_twr=True,
                    then=Sum(
                        "sessions__duration",
                        filter=(
                            Q(sessions__callsign__iregex=r"^IAH(_\w+)?_TWR$")
                            & Q(sessions__start__date__range=[month_1_start, month_3_end])
                        ),
                    ),
                ),
                When(
                    endorsements__iah_gnd=True,
                    then=Sum(
                        "sessions__duration",
                        filter=(
                            Q(sessions__callsign__iregex=r"^IAH(_\w+)?_GND$")
                            & Q(sessions__start__date__range=[month_1_start, month_3_end])
                        ),
                    ),
                ),
            ),
            quarter_i90_t1_hours=Case(
                When(
                    endorsements__i90_app=True,
                    then=Sum(
                        "sessions__duration",
                        filter=(
                            Q(sessions__callsign__iregex=r"^I90(_\w+)?_APP$")
                            & Q(sessions__start__date__range=[month_1_start, month_3_end])
                        ),
                    ),
                ),
            ),
            quarter_t1_hours=Value(timedelta(0)),     # TODO
            quarter_t1_active=Value(False),           # TODO
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
            training_active=Q(rating=Rating.OBS) & Q(training_hours__gte=timedelta(hours=3)),
        )
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
                "quarter_hou_t1_hours",
                "quarter_iah_t1_hours",
                "quarter_i90_t1_hours",
                "quarter_t1_hours",
                "quarter_t1_active",
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
    curr_time = timezone.now()

    return (
        User.objects.exclude(status=UserStatus.NON_MEMBER)
        .annotate(
            hours=Sum(
                "sessions__duration",
                filter=Q(sessions__start__month=curr_time.month) & Q(sessions__start__year=curr_time.year),
            )
        )
        .exclude(hours__isnull=True)
        .order_by("-hours")
    )


def get_top_positions():
    curr_time = timezone.now()

    sessions = ControllerSession.objects.filter(start__month=curr_time.month, start__year=curr_time.year)
    position_durations = {}

    for session in sessions:
        position = session.facility + "_" + session.level
        if position in position_durations:
            position_durations[position] += session.duration
        else:
            position_durations[position] = session.duration

    sorted_positions = sorted(position_durations, key=position_durations.get, reverse=True)
    return [{"position": position, "hours": position_durations[position]} for position in sorted_positions]


def get_daily_statistics(year, user=None):
    """
    Returns a query dictionary of every day of the
    given year annotated with the controlling hours
    for that day.
    """
    sessions = ControllerSession.objects.filter(start__year=year)
    if user:
        sessions = sessions.filter(user=user)
    return sessions.extra({"date": "date(start)"}).values("date").annotate(value=Sum("duration"))
