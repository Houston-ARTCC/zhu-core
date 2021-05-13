from datetime import timedelta
from django.utils import timezone

from apps.mailer.models import Status, Email


def send_pending_mail():
    """
    This job goes through pending emails in the queue
    and sends them.
    """
    for mail in Email.objects.exclude(status=Status.SENT):
        mail.send()


def clear_old_mail():
    """
    This job removes emails older than one week from the database.
    """
    Email.objects.filter(last_attempt__lte=timezone.now() - timedelta(weeks=1)).exclude(status=Status.PENDING).delete()
