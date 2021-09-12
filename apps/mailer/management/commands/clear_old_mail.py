from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.mailer.models import Email, Status


class Command(BaseCommand):
    help = 'Removes old emails from database.'

    def handle(self, *args, **options):
        week_ago = timezone.now() - timedelta(weeks=1)
        Email.objects.filter(last_attempt__lte=week_ago).exclude(status=Status.PENDING).delete()

        print(f'{datetime.now()} :: clear_old_mail :: SUCCESS')
