from datetime import datetime

from django.core.management.base import BaseCommand

from apps.users.models import Status, User


class Command(BaseCommand):
    help = "Updates ratings for all active controllers"  # noqa: A003

    def handle(self, *args, **options):
        for user in User.objects.exclude(status=Status.NON_MEMBER):
            user.update_rating()

        print(f"{datetime.now()} :: update_user_ratings :: SUCCESS")
