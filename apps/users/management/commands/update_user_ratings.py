from datetime import datetime

from django.core.management.base import BaseCommand

from apps.users.models import Status, User


class Command(BaseCommand):
    help = "Updates ratings for all active controllers"  # noqa: A003

    def handle(self, *args, **options):
        failures = 0
        for user in User.objects.exclude(status=Status.NON_MEMBER):
            try:
                user.update_rating()
            except Exception as err:
                failures += 1
                print(f"update_user_ratings :: failed for cid={user.cid}: {err!r}")

        status = "PARTIAL" if failures else "SUCCESS"
        print(f"{datetime.now()} :: update_user_ratings :: {status} (failures={failures})")
