from datetime import datetime

from django.core.management.base import BaseCommand

from apps.connections.statistics import aggregate_quarterly_hours
from apps.mailer.models import Email
from apps.users.models import Status, User


class Command(BaseCommand):
    help = "Sends notification to controllers who have not fulfilled their activity requirements for the month"  # noqa: A003

    def handle(self, *args, **options):
        users = User.objects.filter(status=Status.ACTIVE)
        statistics = aggregate_quarterly_hours(users)

        for user in statistics.filter(active=False):
            Email.objects.queue(
                to=user,
                subject="Quarterly activity reminder",
                from_email="management@houston.center",
                template="activity_reminder",
            )

        print(f"{datetime.now()} :: notify_inactive_controllers :: SUCCESS")
