from datetime import date

from .models import LOA
from ..users.models import Status, User


def update_loa_status():
    """
    This job updates users who should be or are
    longer on a leave of absence.
    """
    for user in User.objects.filter(status=Status.ACTIVE):
        if LOA.objects.filter(user=user, start__lte=date.today(), end__gt=date.today()).exists():
            user.status = Status.LOA
            user.save()
            # TODO: Send email on LOA activation

    for user in User.objects.filter(status=Status.LOA):
        if not LOA.objects.filter(user=user, start__lte=date.today(), end__gt=date.today()).exists():
            user.status = Status.ACTIVE
            user.save()
            # TODO: Send email on LOA deactivation
