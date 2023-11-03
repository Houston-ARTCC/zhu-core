from datetime import timedelta

from django.db.models import DurationField, Q, Sum
from django.db.models.functions import Cast, Coalesce
from django.utils import timezone

from apps.users.models import Status, User

from .models import ControllerSession


def annotate_hours(query):
    """
    Annotates given QuerySet with controlling hours for the
    current (curr_hours), previous (prev_hours), and
    penultimate (prev_prev_hours) months.
    """
    is_curr_year = Q(sessions__start__year=timezone.now().year)

    return query.annotate(
        q1=Coalesce(Sum('sessions__duration', filter=Q(sessions__start__quarter=1) & is_curr_year), Cast(timedelta(), DurationField())),
        q2=Coalesce(Sum('sessions__duration', filter=Q(sessions__start__quarter=2) & is_curr_year), Cast(timedelta(), DurationField())),
        q3=Coalesce(Sum('sessions__duration', filter=Q(sessions__start__quarter=3) & is_curr_year), Cast(timedelta(), DurationField())),
        q4=Coalesce(Sum('sessions__duration', filter=Q(sessions__start__quarter=4) & is_curr_year), Cast(timedelta(), DurationField())),
    )


def get_user_hours():
    """
    Returns query set of active users annotated with controlling
    hours for the current (curr_hours), previous (prev_hours),
    and penultimate (prev_prev_hours) months.
    """
    return annotate_hours(User.objects.exclude(status=Status.NON_MEMBER))


def get_top_controllers():
    """
    Returns query set of active users annotated with controlling
    hour sums for the current month (hours) sorted by most
    controlling hours (controllers with no hours are not included).
    """
    curr_time = timezone.now()

    return (
        User.objects
        .exclude(status=Status.NON_MEMBER)
        .annotate(
            hours=Sum(
                'sessions__duration',
                filter=Q(sessions__start__month=curr_time.month) & Q(sessions__start__year=curr_time.year)
            )
        )
        .exclude(hours__isnull=True)
        .order_by('-hours')
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
