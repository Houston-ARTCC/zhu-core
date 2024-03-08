from datetime import datetime

from django.core.management.base import BaseCommand

from apps.users.models import Status, User


class Command(BaseCommand):
    help = "Updates users who should be or are no longer on leave of absence"  # noqa: A003

    def handle(self, *args, **options):
        for user in User.objects.filter(status__in=[Status.ACTIVE, Status.LOA]).prefetch_related("loas"):
            user.update_loa_status()

        print(f"{datetime.now()} :: update_loa_status :: SUCCESS")
