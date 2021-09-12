import os
import pytz
from datetime import datetime
from django.core.management.base import BaseCommand

from zhu_core.utils import get_vatsim_data
from apps.connections.models import OnlineController
from apps.users.models import User


class Command(BaseCommand):
    help = 'Pulls all connections from the VATSIM data API.'

    def handle(self, *args, **options):
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

        print(f'{datetime.now()} :: update_online_controllers :: SUCCESS')
