import os
from datetime import date

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import LOA
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

            try:
                context = {'user': user, 'loa': loa_filter.first()}
                EmailMultiAlternatives(
                    subject='You have been placed on a leave of absence',
                    to=[user.email],
                    from_email=os.getenv('EMAIL_ADDRESS'),
                    body=render_to_string('loa_activated.txt', context=context),
                    alternatives=[(render_to_string('loa_activated.html', context=context), 'text/html')],
                ).send()
            except:
                pass

    for user in User.objects.filter(status=Status.LOA):
        if not LOA.objects.filter(user=user, start__lte=date.today(), end__gt=date.today()).exists():
            user.status = Status.ACTIVE
            user.save()

            try:
                context = {'user': user}
                EmailMultiAlternatives(
                    subject='Welcome back to Houston!',
                    to=[user.email],
                    from_email=os.getenv('EMAIL_ADDRESS'),
                    body=render_to_string('loa_deactivated.txt', context=context),
                    alternatives=[(render_to_string('loa_deactivated.html', context=context), 'text/html')],
                ).send()
            except:
                pass
