from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from apps.connections.statistics import get_user_hours
from apps.mailer.models import Email
from apps.users.models import Status


class Command(BaseCommand):
    help = "Sends notification to controllers who have not fulfilled their activity requirements for the month"  # noqa: A003

    def handle(self, *args, **options):
        if settings.DEV_ENV:
            return

        hours = get_user_hours()
        curr_date = datetime.today()
        current_quarter = (curr_date.month - 1) // 3 + 1

        for user in hours.filter(status=Status.ACTIVE, roles__short__in=["HC", "VC"]):
            if getattr(user, f"q{current_quarter}") < user.activity_requirement:
                context = {
                    "user": user,
                    "quarter": current_quarter,
                    "year": curr_date.year,
                }
                Email(
                    subject="Controller Activity Reminder",
                    html_body=render_to_string("activity_reminder.html", context=context),
                    text_body=render_to_string("activity_reminder.txt", context=context),
                    to_email=user.email,
                ).save()

        print(f"{datetime.now()} :: notify_inactive_controllers :: SUCCESS")
