from datetime import date
from django.template.loader import render_to_string

from .models import LOA
from ..mailer.models import Email
from ..users.models import Status, User


def update_loa_status():
    """
    This job updates users who should be or are
    longer on a leave of absence.
    """
    for user in User.objects.filter(status=Status.ACTIVE):
        loa_filter = LOA.objects.filter(user=user, start__lte=date.today(), end__gt=date.today())
        if loa_filter.exists():
            user.status = Status.LOA
            user.save()

            context = {'user': user, 'loa': loa_filter.first()}
            Email(
                subject='You have been placed on a leave of absence',
                html_body=render_to_string('loa_activated.html', context=context),
                text_body=render_to_string('loa_activated.txt', context=context),
                to_email=user.email,
            ).save()

    for user in User.objects.filter(status=Status.LOA):
        if not LOA.objects.filter(user=user, start__lte=date.today(), end__gt=date.today()).exists():
            user.status = Status.ACTIVE
            user.save()

            context = {'user': user}
            Email(
                subject='Welcome back to Houston!',
                html_body=render_to_string('loa_deactivated.html', context=context),
                text_body=render_to_string('loa_deactivated.txt', context=context),
                to_email=user.email,
            ).save()
