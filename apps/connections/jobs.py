import os
import pytz
from datetime import datetime
from django.template.loader import render_to_string

from zhu_core.utils import get_vatsim_data
from .models import OnlineController
from .statistics import get_user_hours
from ..mailer.models import Email
from ..users.models import User, Status


def update_online_controllers():
    """
    This job pulls all connections from the VATSIM data API
    and updates all current controlling sessions and creates
    new ones as needed.
    """
    position_prefixes = os.getenv('POSITION_PREFIXES').split(',')
    connections = {connection.get('callsign'): connection for connection in get_vatsim_data().get('controllers')}

    # Updates all controllers currently online.
    for online in OnlineController.objects.all():
        if online.callsign in connections and connections.get(online.callsign).get('cid') == online.user.cid:
            online.save()
        else:
            online.convert_to_session()
            online.delete()

    # Checks for new connections.
    for callsign, connection in connections.items():
        user = User.objects.filter(cid=connection.get('cid'))
        if user.exists() and not OnlineController.objects.filter(callsign=callsign, user=user.first()).exists():
            if callsign.split('_')[0] in position_prefixes and callsign.split('_')[-1] not in ['SUP', 'OBS']:
                OnlineController(
                    user=user.first(),
                    callsign=callsign,
                    online_since=pytz.utc.localize(
                        datetime.strptime(connection.get('logon_time')[:-2], '%Y-%m-%dT%H:%M:%S.%f')
                    )
                ).save()


def notify_inactive_controllers():
    """
    This job goes through all controllers and sends a notification
    email to those who have not yet fulfilled their activity
    requirements for the month.
    """
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
