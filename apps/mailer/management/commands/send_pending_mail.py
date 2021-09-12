from datetime import datetime
from django.core.management.base import BaseCommand

from apps.mailer.models import Email, Status


class Command(BaseCommand):
    help = 'Sends pending emails in the queue.'

    def handle(self, *args, **options):
        for mail in Email.objects.exclude(status=Status.SENT):
            mail.send()

        print(f'{datetime.now()} :: send_pending_mail :: SUCCESS')
