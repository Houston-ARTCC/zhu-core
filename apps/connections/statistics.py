from django.db.models import Sum, Q
from django.utils import timezone

from .models import ControllerSession
from ..users.models import User, Status


def get_user_hours():
    MONTH_NOW = timezone.now().month
    YEAR_NOW = timezone.now().year

    CURR_MONTH = (Q(controller_sessions__start__month=MONTH_NOW)
                  & Q(controller_sessions__start__year=YEAR_NOW))
    PREV_MONTH = (Q(controller_sessions__start__month=MONTH_NOW - 1 if MONTH_NOW > 1 else 12)
                  & Q(controller_sessions__start__year=YEAR_NOW if MONTH_NOW > 1 else YEAR_NOW - 1))
    PREV_PREV_MONTH = (Q(controller_sessions__start__month=MONTH_NOW - 2 if MONTH_NOW > 2 else 12 if MONTH_NOW > 1 else 11)
                       & Q(controller_sessions__start__year=YEAR_NOW if MONTH_NOW > 2 else YEAR_NOW - 1))

    users = User.objects.exclude(status=Status.NON_MEMBER)
    users = users.annotate(
        curr_hours=Sum('controller_sessions__duration', filter=CURR_MONTH),
        prev_hours=Sum('controller_sessions__duration', filter=PREV_MONTH),
        prev_prev_hours=Sum('controller_sessions__duration', filter=PREV_PREV_MONTH),
    )

    return users


def get_top_controllers():
    SAME_MONTH = Q(controller_sessions__start__month=timezone.now().month)
    SAME_YEAR = Q(controller_sessions__start__year=timezone.now().year)

    users = User.objects.filter(status=Status.ACTIVE)
    users = users.annotate(hours=Sum('controller_sessions__duration', filter=SAME_MONTH & SAME_YEAR))

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

