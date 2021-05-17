from django.db.models import Sum, Q
from django.utils import timezone

from .models import ControllerSession
from ..users.models import User, Status


def annotate_hours(query):
    """
    Annotates given QuerySet with controlling hours for the
    current (curr_hours), previous (prev_hours), and
    penultimate (prev_prev_hours) months.
    """
    MONTH_NOW = timezone.now().month
    YEAR_NOW = timezone.now().year
    CURR_MONTH = (Q(sessions__start__month=MONTH_NOW)
                  & Q(sessions__start__year=YEAR_NOW))
    PREV_MONTH = (Q(sessions__start__month=MONTH_NOW - 1 if MONTH_NOW > 1 else 12)
                  & Q(sessions__start__year=YEAR_NOW if MONTH_NOW > 1 else YEAR_NOW - 1))
    PREV_PREV_MONTH = (Q(sessions__start__month=MONTH_NOW - 2 if MONTH_NOW > 2 else 12 if MONTH_NOW > 1 else 11)
                       & Q(sessions__start__year=YEAR_NOW if MONTH_NOW > 2 else YEAR_NOW - 1))

    return query.annotate(
        curr_hours=Sum('sessions__duration', filter=CURR_MONTH),
        prev_hours=Sum('sessions__duration', filter=PREV_MONTH),
        prev_prev_hours=Sum('sessions__duration', filter=PREV_PREV_MONTH),
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
    SAME_MONTH = Q(sessions__start__month=timezone.now().month)
    SAME_YEAR = Q(sessions__start__year=timezone.now().year)

    users = User.objects.exclude(status=Status.NON_MEMBER)
    users = users.annotate(hours=Sum('sessions__duration', filter=SAME_MONTH & SAME_YEAR))

    return users.exclude(hours__isnull=True).order_by('-hours')


def get_top_positions():
    SAME_MONTH = Q(start__month=timezone.now().month)
    SAME_YEAR = Q(start__year=timezone.now().year)

    sessions = ControllerSession.objects.filter(SAME_MONTH & SAME_YEAR)
    position_durations = {}

    for session in sessions:
        position = session.facility + '_' + session.level
        if position in position_durations:
            position_durations[position] += session.duration
        else:
            position_durations[position] = session.duration

    sorted_positions = sorted(position_durations, key=position_durations.get, reverse=True)
    return [{'position': position, 'hours': position_durations[position]} for position in sorted_positions]


def get_daily_statistics(year, user=None):
    """
    Returns a query dictionary of every day of the
    given year annotated with the controlling hours
    for that day.
    """
    sessions = ControllerSession.objects.filter(start__year=year)
    if user:
        sessions = sessions.filter(user=user)
    return sessions.extra({'day': 'date(start)'}).values('day').annotate(value=Sum('duration'))
