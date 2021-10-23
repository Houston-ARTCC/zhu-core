import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from apps.connections.statistics import get_user_hours
from apps.mailer.models import Email
from apps.users.models import Status


class Command(BaseCommand):
    help = 'Sends notification to controllers who have not fulfilled their activity requirements for the month.'

    def handle(self, *args, **options):
        if os.getenv('DEV_ENV') == 'True':
            return

        hours = get_user_hours()
        month_name = datetime.now().strftime('%B')

        for user in hours.filter(status=Status.ACTIVE, roles__short__in=['HC', 'VC']):
            if user.curr_hours < user.activity_requirement:
                context = {
                    'user': user,
                    'month': month_name,
                }
                Email(
                    subject='Controller Activity Reminder',
                    html_body=render_to_string('activity_reminder.html', context=context),
                    text_body=render_to_string('activity_reminder.txt', context=context),
                    to_email=user.email,
                ).save()

        print(f'{datetime.now()} :: notify_inactive_controllers :: SUCCESS')
